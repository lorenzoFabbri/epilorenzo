# Lorenzo Fabbri - Academic Website

My personal academic website built with Quarto, R, and renv. This site showcases my research, publications, teaching, and blog posts.

🌐 **Live site:** [https://lorenzofabbri.github.io/epilorenzo](https://lorenzofabbri.github.io/epilorenzo)

## Features

- **Academic pages:** About, CV, Research, Talks, Blog, and Now page
- **Automatic publication sync:** Publications are automatically fetched from Google Scholar
- **Blog with RSS:** Write posts in Quarto markdown with full RSS feed support
- **Reproducible:** Uses R's `renv` for package management
- **GitHub Actions:** Automated deployment and publication updates

## Structure

```
.
├── _quarto.yml              # Quarto configuration
├── custom.css               # Custom academic styling
├── index.qmd                # About page
├── cv.qmd                   # CV with PDF preview
├── research.qmd             # Publications and working papers
├── blog.qmd                 # Blog listing page
├── talks.qmd                # Presentations and talks
├── now.qmd                  # Current activities
├── references.bib           # Publications bibliography
├── apa.csl                  # APA citation style
├── renv.lock                # R package dependencies
├── scripts/
│   └── update_publications.R  # Google Scholar sync script
├── posts/                   # Blog posts
│   └── welcome/
│       └── index.qmd
└── .github/workflows/
    ├── deploy-website.yml   # Build and deploy to GitHub Pages
    └── update-publications.yml  # Weekly publication updates
```

## Building Locally

### Prerequisites

- [Quarto](https://quarto.org/docs/get-started/) (version 1.4+)
- [R](https://www.r-project.org/) (version 4.3+)

### Setup

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

The website will be built in the `docs/` directory.

## Publication Management

Publications are automatically synced from Google Scholar weekly via GitHub Actions. To manually update:

```bash
Rscript scripts/update_publications.R
```

This will:
1. Fetch publications from Google Scholar
2. Convert to BibTeX format
3. Update `references.bib`
4. Publications automatically appear on the Research page

## Writing Blog Posts

1. Create a new folder in `posts/`:
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

3. Write your content in markdown/Quarto

4. Render and deploy:
   ```bash
   quarto render
   ```

## Deployment

The website automatically deploys to GitHub Pages on push to `main`. Make sure:

1. GitHub Pages is enabled in repository settings
2. Source is set to "GitHub Actions"
3. The `deploy-website.yml` workflow has proper permissions

## Customization

- **Theme:** Edit `_quarto.yml` to change from Flatly to another Bootswatch theme
- **Styling:** Modify `custom.css` for custom styling
- **Colors:** Update CSS color variables in `custom.css`
- **Social links:** Update in `_quarto.yml` navbar/footer sections

## License

Content © 2025 Lorenzo Fabbri. Code is MIT licensed.

## Acknowledgments

Inspired by the [academicpages](https://github.com/academicpages/academicpages.github.io) template and built with [Quarto](https://quarto.org/).
