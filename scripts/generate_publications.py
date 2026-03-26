#!/usr/bin/env python3
"""
Generate Quarto publication pages from DOI metadata.

Reads publications.yml as the source of truth.
Fetches structured metadata from CrossRef (primary) or DOI content
negotiation / DataCite (fallback) for each DOI.
Writes research/articles/{slug}/index.qmd and research/posters/{slug}/index.qmd.

Usage:
  python scripts/generate_publications.py
  python scripts/generate_publications.py --dry-run       # preview, no writes
  python scripts/generate_publications.py --discover      # report ORCID pubs missing from publications.yml
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path
from typing import Any

import requests
import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLICATIONS_YML = BASE_DIR / "publications.yml"
ARTICLES_DIR = BASE_DIR / "research" / "articles"
POSTERS_DIR = BASE_DIR / "research" / "posters"

# ---------------------------------------------------------------------------
# Unicode → HTML entity / LaTeX mappings (cover common European diacritics)
# ---------------------------------------------------------------------------

_UNICODE_HTML: dict[str, str] = {
    "à": "&agrave;", "á": "&aacute;", "â": "&acirc;", "ã": "&atilde;",
    "ä": "&auml;",   "å": "&aring;",  "æ": "&aelig;", "ç": "&ccedil;",
    "è": "&egrave;", "é": "&eacute;", "ê": "&ecirc;",  "ë": "&euml;",
    "ì": "&igrave;", "í": "&iacute;", "î": "&icirc;",  "ï": "&iuml;",
    "ñ": "&ntilde;", "ò": "&ograve;", "ó": "&oacute;", "ô": "&ocirc;",
    "õ": "&otilde;", "ö": "&ouml;",   "ø": "&oslash;",
    "ù": "&ugrave;", "ú": "&uacute;", "û": "&ucirc;",  "ü": "&uuml;",
    "ý": "&yacute;", "ÿ": "&yuml;",   "ß": "&szlig;",
    "À": "&Agrave;", "Á": "&Aacute;", "Â": "&Acirc;",  "Ã": "&Atilde;",
    "Ä": "&Auml;",   "Å": "&Aring;",  "Æ": "&AElig;",  "Ç": "&Ccedil;",
    "È": "&Egrave;", "É": "&Eacute;",
    "Ì": "&Igrave;", "Í": "&Iacute;",
    "Ñ": "&Ntilde;", "Ó": "&Oacute;", "Ö": "&Ouml;",
    "Ú": "&Uacute;", "Ü": "&Uuml;",
    # Characters lacking named HTML entities → numeric
    "ě": "&#283;", "š": "&#353;", "č": "&#269;", "ž": "&#382;", "ř": "&#345;",
    "Ě": "&#282;", "Š": "&#352;", "Č": "&#268;", "Ž": "&#381;", "Ř": "&#344;",
    "ą": "&#261;", "ę": "&#281;", "ń": "&#324;", "ź": "&#378;", "ż": "&#380;",
    "ł": "&#322;", "Ł": "&#321;",
    "ė": "&#279;", "ū": "&#363;", "ā": "&#257;", "ģ": "&#291;",
}

_UNICODE_LATEX: dict[str, str] = {
    "à": r"{\`a}",  "á": r"{\'a}",  "â": r"{\^a}",  "ã": r"{\~a}",
    "ä": r'{\"a}',  "å": r"{\aa}",  "æ": r"{\ae}",  "ç": r"{\c{c}}",
    "è": r"{\`e}",  "é": r"{\'e}",  "ê": r"{\^e}",  "ë": r'{\"e}',
    "ì": r"{\`i}",  "í": r"{\'i}",  "î": r"{\^i}",  "ï": r'{\"i}',
    "ñ": r"{\~n}",  "ò": r"{\`o}",  "ó": r"{\'o}",  "ô": r"{\^o}",
    "õ": r"{\~o}",  "ö": r'{\"o}',  "ø": r"{\o}",
    "ù": r"{\`u}",  "ú": r"{\'u}",  "û": r"{\^u}",  "ü": r'{\"u}',
    "ý": r"{\'y}",  "ÿ": r'{\"y}',  "ß": r"{\ss}",
    "À": r"{\`A}",  "Á": r"{\'A}",  "Â": r"{\^A}",  "Ã": r"{\~A}",
    "Ä": r'{\"A}',  "Å": r"{\AA}",  "Æ": r"{\AE}",  "Ç": r"{\c{C}}",
    "È": r"{\`E}",  "É": r"{\'E}",
    "Ì": r"{\`I}",  "Í": r"{\'I}",
    "Ñ": r"{\~N}",  "Ó": r"{\'O}",  "Ö": r'{\"O}',
    "Ú": r"{\'U}",  "Ü": r'{\"U}',
    "ě": r"{\v{e}}", "š": r"{\v{s}}", "č": r"{\v{c}}", "ž": r"{\v{z}}", "ř": r"{\v{r}}",
    "Ě": r"{\v{E}}", "Š": r"{\v{S}}", "Č": r"{\v{C}}", "Ž": r"{\v{Z}}", "Ř": r"{\v{R}}",
    "ą": r"{\k{a}}", "ę": r"{\k{e}}", "ń": r"{\'n}",  "ź": r"{\'z}",  "ż": r"{\dot{z}}",
    "ł": r"{\l}",    "Ł": r"{\L}",
    "ė": r"{\.{e}}",  "ū": r"{\=u}",  "ā": r"{\=a}",  "ģ": r"{\c{g}}",
}

_STOPWORDS = frozenset(
    {"a", "an", "the", "of", "in", "and", "or", "for", "to", "with", "on", "at", "by", "from"}
)


def _to_html(s: str) -> str:
    for ch, ent in _UNICODE_HTML.items():
        s = s.replace(ch, ent)
    return s


def _to_latex(s: str) -> str:
    for ch, cmd in _UNICODE_LATEX.items():
        s = s.replace(ch, cmd)
    return s


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def _get(url: str, headers: dict[str, str] | None = None, timeout: int = 30) -> requests.Response | None:
    try:
        resp = requests.get(url, headers=headers or {}, timeout=timeout)
        resp.raise_for_status()
        return resp
    except requests.RequestException as exc:
        print(f"    HTTP error for {url}: {exc}", file=sys.stderr)
        return None


def fetch_crossref(doi: str, email: str) -> dict[str, Any] | None:
    """Return CrossRef work record or None."""
    resp = _get(
        f"https://api.crossref.org/works/{doi}",
        headers={"User-Agent": f"epilorenzo-website/1.0 (mailto:{email})"},
    )
    if resp is not None:
        return resp.json().get("message")
    return None


def fetch_datacite_csl(doi: str) -> dict[str, Any] | None:
    """Return CSL-JSON via DOI content negotiation (works for DataCite / figshare)."""
    resp = _get(
        f"https://doi.org/{doi}",
        headers={"Accept": "application/vnd.citationstyles.csl+json"},
    )
    if resp is not None:
        try:
            return resp.json()
        except ValueError:
            return None
    return None


def fetch_orcid_dois(orcid: str) -> list[str]:
    """Return list of DOIs from an ORCID public record."""
    resp = _get(
        f"https://pub.orcid.org/v3.0/{orcid}/works",
        headers={"Accept": "application/json"},
    )
    if resp is None:
        return []
    dois: list[str] = []
    for group in resp.json().get("group", []):
        for summary in group.get("work-summary", []):
            for ext_id in summary.get("external-ids", {}).get("external-id", []):
                if ext_id.get("external-id-type") == "doi":
                    dois.append(ext_id["external-id-value"].lower())
                    break
    return dois


# ---------------------------------------------------------------------------
# Metadata normalisation
# ---------------------------------------------------------------------------

def _normalise_author(raw: dict[str, Any]) -> dict[str, str]:
    if "family" in raw:
        return {"given": raw.get("given", ""), "family": raw["family"]}
    if "literal" in raw:
        parts = raw["literal"].rsplit(" ", 1)
        return {"given": parts[0], "family": parts[1]} if len(parts) == 2 else {"given": "", "family": raw["literal"]}
    return {"given": "", "family": str(raw)}


def _clean_abstract(text: str) -> str:
    """Strip JATS XML and residual HTML tags from an abstract."""
    text = re.sub(r"</?jats:[^>]*>", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def _extract_year(meta: dict, source: str) -> int:
    if source == "crossref":
        for key in ("published", "published-print", "published-online", "created"):
            parts = meta.get(key, {}).get("date-parts", [[None]])[0]
            if parts and parts[0]:
                return int(parts[0])
    else:
        parts = meta.get("issued", {}).get("date-parts", [[None]])[0]
        if parts and parts[0]:
            return int(parts[0])
    return 0


def _extract_authors(meta: dict) -> list[dict[str, str]]:
    return [_normalise_author(a) for a in meta.get("author", [])]


def _make_slug(authors: list[dict], year: int, title: str) -> str:
    lastname = re.sub(r"[^a-z]", "", authors[0].get("family", "author").lower()) if authors else "author"
    words = re.sub(r"[^a-zA-Z\s]", "", title).lower().split()
    first_word = next((w for w in words if w not in _STOPWORDS), words[0] if words else "pub")
    return f"{lastname}{year}{first_word}"


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

MAX_AUTHORS_DISPLAY = 10


def _fmt_author_html(author: dict[str, str], bold_family: str = "Fabbri") -> str:
    given = author.get("given", "")
    family = author.get("family", "")
    if not family:
        return ""
    initials = "".join(p[0] for p in given.split() if p)
    text = f"{_to_html(family)} {initials}".strip()
    if family == bold_family:
        text = f"<strong>{text}</strong>"
    return text


def _fmt_author_bibtex(author: dict[str, str]) -> str:
    given = _to_latex(author.get("given", ""))
    family = _to_latex(author.get("family", ""))
    if not family:
        return ""
    return f"{family}, {given}" if given else family


def _author_list_html(authors: list[dict]) -> str:
    parts = [_fmt_author_html(a) for a in authors[:MAX_AUTHORS_DISPLAY] if a.get("family")]
    suffix = "et al." if len(authors) > MAX_AUTHORS_DISPLAY else ""
    base = ", ".join(parts)
    return f"{base}, {suffix}" if suffix else base


def _author_list_bibtex(authors: list[dict]) -> str:
    formatted = [_fmt_author_bibtex(a) for a in authors if a.get("family")]
    if len(formatted) > MAX_AUTHORS_DISPLAY:
        return " and ".join(formatted[:MAX_AUTHORS_DISPLAY]) + " and others"
    return " and ".join(formatted)


# ---------------------------------------------------------------------------
# Reference builders
# ---------------------------------------------------------------------------

def _ref_article(authors, year, title, journal, volume, pages, doi) -> str:
    author_str = _author_list_html(authors)
    title_h = _to_html(title)
    journal_h = _to_html(journal) if journal else ""
    # Avoid double period when author_str already ends with "." (e.g. "et al.")
    sep = " " if author_str.endswith(".") else ". "
    parts = [f'{author_str}{sep}"{title_h}."']
    if journal_h:
        loc = f"{volume} ({year}): {pages}" if pages else f"{volume} ({year})" if volume else str(year)
        parts.append(f"<em>{journal_h}</em> {loc},")
    else:
        parts.append(f"({year}),")
    if doi:
        parts.append(f'doi: <a href="https://doi.org/{doi}"><code>{doi}</code></a>')
    return " ".join(parts)


def _ref_poster(authors, year, title, conference, doi=None) -> str:
    author_str = _author_list_html(authors)
    title_h = _to_html(title)
    conf_h = _to_html(conference) if conference else ""
    sep = " " if author_str.endswith(".") else ". "
    ref = f'{author_str}{sep}"{title_h}." Presented at the {conf_h} ({year}).'
    if doi:
        ref += f' doi: <a href="https://doi.org/{doi}"><code>{doi}</code></a>'
    return ref


# ---------------------------------------------------------------------------
# BibTeX builders
# ---------------------------------------------------------------------------

def _bibtex_article(key, title, authors, journal, volume, pages, year, publisher="") -> str:
    lines = [
        f"@article{{{key},",
        f"  title={{{_to_latex(title)}}},",
        f"  author={{{_author_list_bibtex(authors)}}},",
    ]
    if journal:
        lines.append(f"  journal={{{_to_latex(journal)}}},")
    if volume:
        lines.append(f"  volume={{{volume}}},")
    if pages:
        lines.append(f"  pages={{{pages}}},")
    lines.append(f"  year={{{year}}},")
    if publisher:
        lines.append(f"  publisher={{{_to_latex(publisher)}}}")
    else:
        # Remove trailing comma from last real line
        lines[-1] = lines[-1].rstrip(",")
    lines.append("}")
    return "\n".join(lines)


def _bibtex_inproceedings(key, title, authors, booktitle, year, volume=None, number=None) -> str:
    lines = [
        f"@inproceedings{{{key},",
        f"  title={{{_to_latex(title)}}},",
        f"  author={{{_author_list_bibtex(authors)}}},",
    ]
    if booktitle:
        lines.append(f"  booktitle={{{_to_latex(booktitle)}}},")
    if volume:
        lines.append(f"  volume={{{volume}}},")
    if number:
        lines.append(f"  number={{{number}}},")
    lines.append(f"  year={{{year}}}")
    lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# QMD generators
# ---------------------------------------------------------------------------

def _categories_yaml(categories: list[str]) -> str:
    return "\n".join(f"  - {c}" for c in categories) if categories else "  - Research"


def _links_yaml(links: list[dict]) -> str:
    parts = []
    for lnk in links:
        parts.append(
            f"    - name: {lnk['name']}\n"
            f"      url: {lnk['url']}\n"
            f"      icon: {lnk['icon']}"
        )
    return "\n".join(parts)


def generate_article_qmd(pub: dict, meta: dict, source: str) -> tuple[str, str]:
    """Return (qmd_content, slug)."""
    authors = _extract_authors(meta)
    year = _extract_year(meta, source)

    if source == "crossref":
        title     = (meta.get("title") or [""])[0]
        journal   = (meta.get("container-title") or [""])[0]
        volume    = meta.get("volume", "")
        pages     = meta.get("page", "")
        abstract  = _clean_abstract(meta.get("abstract", ""))
        publisher = meta.get("publisher", "")
        doi       = meta.get("DOI", pub.get("doi", ""))
    else:
        raw_title = meta.get("title", "")
        title     = raw_title[0] if isinstance(raw_title, list) else raw_title
        journal   = meta.get("container-title", "")
        volume    = meta.get("volume", "")
        pages     = meta.get("page", "")
        abstract  = ""
        publisher = meta.get("publisher", "")
        doi       = meta.get("DOI", pub.get("doi", ""))

    # Manual overrides from publications.yml take precedence
    doi       = pub.get("doi", doi)
    github    = pub.get("github", "")
    categories = pub.get("categories", [])
    slug      = pub.get("slug") or _make_slug(authors, year, title)

    html_ref  = _ref_article(authors, year, title, journal, volume, pages, doi)

    links = [{"name": "Final version", "url": f"https://doi.org/{doi}", "icon": "fa-solid fa-scroll"}]
    if github:
        links.append({"name": "Code", "url": github, "icon": "fa-brands fa-github"})
    links.append({
        "name": "Add to Zotero",
        "url": f"https://www.zotero.org/save?type=doi&q={doi}",
        "icon": "ai ai-zotero",
    })
    links.extend(pub.get("extra_links", []))

    bibtex = _bibtex_article(slug, title, authors, journal, volume, pages, year, publisher)

    abstract_md = (
        f"## Abstract\n\n{abstract}"
        if abstract
        else f"## Abstract\n\nAvailable at the [journal website](https://doi.org/{doi})."
    )
    imp_links = [f"- [Published version](https://doi.org/{doi})"]
    if github:
        imp_links.append(f"- [Code repository]({github})")

    qmd = (
        f'---\n'
        f'title: "{_escape_yaml(title)}"\n'
        f'date: {year}-01-01\n'
        f'author:\n'
        f'  - name: Lorenzo Fabbri\n'
        f'    orcid: 0000-0003-3031-322X\n'
        f'    affiliation: ISGlobal, Universitat Pompeu Fabra\n'
        f'categories:\n'
        f'{_categories_yaml(categories)}\n'
        f'pub-info:\n'
        f'  reference: >-\n'
        f'    {html_ref}\n'
        f'  links:\n'
        f'{_links_yaml(links)}\n'
        f'doi: {doi}\n'
        f'---\n\n'
        f'{abstract_md}\n\n'
        f'## Important links\n\n'
        + "\n".join(imp_links) + "\n\n"
        f'## BibTeX citation\n\n'
        f'```bibtex\n{bibtex}\n```\n'
    )
    return qmd, slug


def generate_poster_qmd(pub: dict, meta: dict | None, source: str | None) -> tuple[str, str]:
    """Return (qmd_content, slug). Handles both DOI-backed and manual-only posters."""
    manual = pub.get("manual", {})

    if meta is not None and source is not None:
        authors = _extract_authors(meta)
        year    = _extract_year(meta, source)
        raw     = meta.get("title", "")
        title   = raw[0] if isinstance(raw, list) else raw
        doi     = meta.get("DOI", pub.get("doi", ""))
    else:
        authors = [_normalise_author(a) for a in manual.get("authors", [])]
        year    = manual.get("year", 0)
        title   = manual.get("title", "")
        doi     = pub.get("doi", "")

    # Manual overrides from publications.yml always take precedence
    doi        = pub.get("doi", doi)
    if pub.get("year"):
        year = int(pub["year"])
    if pub.get("authors"):
        authors = [_normalise_author(a) for a in pub["authors"]]
    conference = pub.get("conference", manual.get("conference", ""))
    categories = pub.get("categories", [])
    slug       = pub.get("slug") or _make_slug(authors, year, title)
    extra_links = pub.get("extra_links", [])

    html_ref = _ref_poster(authors, year, title, conference, doi or None)

    # For posters, links come entirely from extra_links (e.g. figshare PDF, abstract URL)
    links: list[dict] = []
    if doi and not extra_links:
        links.append({"name": "Abstract", "url": f"https://doi.org/{doi}", "icon": "fa-solid fa-scroll"})
    links.extend(extra_links)
    if doi:
        links.append({
            "name": "Add to Zotero",
            "url": f"https://www.zotero.org/save?type=doi&q={doi}",
            "icon": "ai ai-zotero",
        })

    bibtex = _bibtex_inproceedings(slug, title, authors, conference, year)

    conf_md = f"**Conference:** {conference}" if conference else ""

    doi_line = f"doi: {doi}\n" if doi else ""

    qmd = (
        f'---\n'
        f'title: "{_escape_yaml(title)}"\n'
        f'date: {year}-01-01\n'
        f'author:\n'
        f'  - name: Lorenzo Fabbri\n'
        f'    orcid: 0000-0003-3031-322X\n'
        f'    affiliation: ISGlobal, Universitat Pompeu Fabra\n'
        f'categories:\n'
        f'{_categories_yaml(categories)}\n'
        f'pub-info:\n'
        f'  reference: >-\n'
        f'    {html_ref}\n'
        f'  links:\n'
        f'{_links_yaml(links)}\n'
        f'{doi_line}'
        f'---\n\n'
        + (f"{conf_md}\n\n" if conf_md else "")
        + f'## BibTeX citation\n\n'
        f'```bibtex\n{bibtex}\n```\n'
    )
    return qmd, slug


def _escape_yaml(s: str) -> str:
    """Escape double quotes inside a YAML double-quoted string."""
    return s.replace('"', '\\"')


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

def process_article(pub: dict, email: str, dry_run: bool) -> bool:
    doi = pub.get("doi", "")
    slug = pub.get("slug", "?")
    print(f"  article: {slug} (DOI: {doi})")

    print("    → CrossRef ...", end=" ", flush=True)
    meta = fetch_crossref(doi, email)
    if meta:
        source = "crossref"
        print("ok")
    else:
        print("failed, trying DOI content negotiation ...", end=" ", flush=True)
        meta = fetch_datacite_csl(doi)
        source = "csl"
        if meta:
            print("ok")
        else:
            print("FAILED — skipping")
            return False

    qmd, slug = generate_article_qmd(pub, meta, source)
    out_dir = ARTICLES_DIR / slug
    out_file = out_dir / "index.qmd"

    if dry_run:
        print(f"    [dry-run] would write {out_file.relative_to(BASE_DIR)}")
    else:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file.write_text(qmd, encoding="utf-8")
        print(f"    ✓ wrote {out_file.relative_to(BASE_DIR)}")
    return True


def process_poster(pub: dict, email: str, dry_run: bool) -> bool:
    doi = pub.get("doi", "")
    slug = pub.get("slug", "?")
    print(f"  poster:  {slug}" + (f" (DOI: {doi})" if doi else " (manual)"))

    meta = None
    source = None

    if doi:
        print("    → CrossRef ...", end=" ", flush=True)
        meta = fetch_crossref(doi, email)
        if meta:
            source = "crossref"
            print("ok")
        else:
            print("failed, trying DOI content negotiation ...", end=" ", flush=True)
            meta = fetch_datacite_csl(doi)
            source = "csl"
            if meta:
                print("ok")
            else:
                print("failed — using manual data")

    qmd, slug = generate_poster_qmd(pub, meta, source)
    out_dir = POSTERS_DIR / slug
    out_file = out_dir / "index.qmd"

    if dry_run:
        print(f"    [dry-run] would write {out_file.relative_to(BASE_DIR)}")
    else:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file.write_text(qmd, encoding="utf-8")
        print(f"    ✓ wrote {out_file.relative_to(BASE_DIR)}")
    return True


def discover_missing(config: dict) -> None:
    """Query ORCID and report DOIs not present in publications.yml."""
    orcid = config.get("orcid", "")
    if not orcid:
        print("No ORCID configured — skipping discovery.", file=sys.stderr)
        return

    known_dois = {
        pub["doi"].lower()
        for section in ("articles", "posters")
        for pub in config.get(section, [])
        if "doi" in pub
    }

    print(f"\nQuerying ORCID {orcid} for public works …")
    orcid_dois = fetch_orcid_dois(orcid)
    if not orcid_dois:
        print("  No DOIs returned (ORCID may be private or empty).")
        return

    missing = [d for d in orcid_dois if d not in known_dois]
    if missing:
        print(f"\n  ⚠  {len(missing)} DOI(s) in ORCID but not in publications.yml:")
        for d in missing:
            print(f"    • {d}")
        print("\n  Add them to publications.yml to include on the website.")
    else:
        print("  ✓ All ORCID DOIs are already in publications.yml.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Preview only — do not write files")
    parser.add_argument("--discover", action="store_true", help="Report ORCID publications missing from publications.yml")
    args = parser.parse_args()

    config = yaml.safe_load(PUBLICATIONS_YML.read_text(encoding="utf-8"))
    email = config.get("contact_email", "")

    print("Generating publication pages …\n")

    ok = err = 0
    for pub in config.get("articles", []):
        success = process_article(pub, email, args.dry_run)
        (ok if success else err).__class__  # just counting
        if success:
            ok += 1
        else:
            err += 1
        time.sleep(0.5)  # be polite to APIs

    for pub in config.get("posters", []):
        success = process_poster(pub, email, args.dry_run)
        if success:
            ok += 1
        else:
            err += 1
        time.sleep(0.5)

    print(f"\nDone. {ok} generated, {err} failed.")

    if args.discover:
        discover_missing(config)

    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
