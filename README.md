# Lorenzo Fabbri - Personal Website

My personal academic website built with Quarto and R. The site includes my research, publications, talks, CV, blog posts, and a "Now" page.

**Live site:** [https://lorenzofabbri.github.io/epilorenzo](https://lorenzofabbri.github.io/epilorenzo)

## Building Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/lorenzoFabbri/epilorenzo.git
   cd epilorenzo
   ```

2. Restore R packages with renv:

   ```bash
   R -e "renv::restore()"
   ```

3. Render the website:

   ```bash
   quarto render
   ```

4. Preview locally:

   ```bash
   quarto preview
   ```

The website is built into the `docs/` directory and served via GitHub Pages.

## Publication Management

Publications are managed via `publications.yml`. New journal articles are **automatically discovered** from ORCID weekly (via the [`orcidtr`](https://cran.r-project.org/package=orcidtr) R package), and publication pages are generated using a Python script that fetches metadata from CrossRef (primary) or DOI content negotiation / DataCite (fallback).

When new papers are found, a GitHub Issue is opened listing them so you can add categories and links.

### Directory structure

- `research/articles/` — Published journal articles and conference papers
- `research/posters/` — Conference posters
- `research/working-papers/` — Preprints and works in progress (managed manually)

### Automatic discovery (CI)

Every Monday at 06:00 UTC, a GitHub Actions workflow:

1. Queries ORCID for new `journal-article` works (via `scripts/discover_publications.R`)
2. Appends any new DOIs to `publications.yml` with empty categories
3. Generates/updates all publication pages (via `scripts/generate_publications.py`)
4. Commits changes and opens a GitHub Issue if new papers were added

### Manual usage

```bash
# Discover new ORCID articles locally
Rscript scripts/discover_publications.R

# Generate pages from publications.yml
python scripts/generate_publications.py

# Preview without writing files
python scripts/generate_publications.py --dry-run
```

### Adding a publication manually

Add an entry to `publications.yml` under `articles` or `posters`:

```yaml
articles:
  - doi: 10.xxxx/xxxxx
    slug: fabbri2024title          # optional, auto-generated if omitted
    categories:
      - Epidemiology
    github: https://github.com/lorenzoFabbri/my-paper
    extra_links:
      - name: Preprint
        url: https://...
        icon: fa-solid fa-file-pdf
```

Then run the generation script:

```bash
python scripts/generate_publications.py
```

The page will be written to `research/articles/{slug}/index.qmd` and appear automatically on the Research page.

## Talks

Talks are listed in `talks/talks_2025.yml` and rendered via a custom EJS template. Add new entries directly to the YAML file; the page at `talks.qmd` reads from it automatically.

## Writing Blog Posts

1. Create a folder under `posts/`:

   ```bash
   mkdir -p posts/my-new-post
   ```

2. Create `index.qmd` with frontmatter:

   ```yaml
   ---
   title: "My Post Title"
   description: "Short description"
   author: "Lorenzo Fabbri"
   date: "2025-01-15"
   categories: [research, methods]
   ---
   ```

3. Write content in markdown/Quarto and render:

   ```bash
   quarto render
   ```

## Deployment

The website automatically deploys to GitHub Pages on push to `main` via GitHub Actions. Make sure:

1. GitHub Pages is enabled in repository settings
2. Source is set to "GitHub Actions"
3. The workflow has proper permissions

## Hardcover Integration

The "Now" page fetches currently-reading books from [Hardcover](https://hardcover.app) via the `scripts/hardcover.R` script.

Setup:

1. Get your API token from https://hardcover.app/account/api
2. Create `_hardcover_config.R` with your credentials (see `.gitignore` — this file is not tracked):

   ```r
   HARDCOVER_API_TOKEN <- "your-token-here"
   HARDCOVER_USER_ID <- "your-user-id"
   ```

## License

Content © 2026 Lorenzo Fabbri. Code is MIT licensed.
