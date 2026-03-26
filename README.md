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

Publications are managed via `publications.yml` and auto-generated using a Python script. The script fetches metadata from CrossRef (primary) or DOI content negotiation / DataCite (fallback).

### Directory structure

- `research/articles/` — Published journal articles and conference papers
- `research/posters/` — Conference posters
- `research/working-papers/` — Preprints and works in progress (managed manually)

### Generating publication pages

```bash
# Install Python dependencies
pip install -r scripts/requirements.txt

# Generate pages from publications.yml
python scripts/generate_publications.py

# Preview without writing files
python scripts/generate_publications.py --dry-run

# Report ORCID publications not yet in publications.yml
python scripts/generate_publications.py --discover
```

### Adding a publication

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
2. Copy `_hardcover_config_example.R` to `_hardcover_config.R`
3. Add your credentials to the config file

## License

Content © 2025 Lorenzo Fabbri. Code is MIT licensed.
