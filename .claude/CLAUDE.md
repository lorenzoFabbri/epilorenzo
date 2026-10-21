# epilorenzo — working rules

`README.md` covers structure, setup and deployment; read it before changing anything. The rules below are the ones that matter when editing the site.

- Facts about Lorenzo (positions, fellowships, degrees, programmes in progress, software, working papers) follow ORCID (https://orcid.org/0000-0003-3031-322X), the CV in `~/Documents/personal/cv-auto` and `cv-auto/bios.md`. Check those before editing, and when the record itself is wrong, fix the ORCID or CV side first and then bring the site in line.
- The About text in `index.qmd` is the long bio in `cv-auto/bios.md`, and the intro of `research/index.qmd` and the Research line of `now.qmd` restate its first paragraph; change them together, starting from `bios.md`.
- Talks live in `talks/talks_2025.yml`, read by `talks.qmd`.
- Journal articles and posters come from `publications.yml`: `scripts/generate_publications.py` writes `research/articles/{slug}/index.qmd` and `research/posters/{slug}/index.qmd` in the Update Publication Pages workflow (first Monday of the month, and on pushes touching `publications.yml`). Set `slug` and `categories` in `publications.yml`, not in the generated pages, which the next run overwrites.
- Render with `make render`, preview with `make preview`, then check the changed text in the rendered `docs/` pages.
- A push to `main` deploys the public site at https://lorenzofabbri.github.io/epilorenzo, so confirm before pushing.
