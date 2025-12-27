# Lorenzo Fabbri - Academic Website

My personal academic website built with Quarto and R. This site showcases my research, publications, teaching, and blog posts.

🌐 **Live site:** [https://lorenzofabbri.github.io/epilorenzo](https://lorenzofabbri.github.io/epilorenzo)

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

The website will be built in the `docs/` directory.

## Publication Management

Publications are managed manually by adding `.qmd` files in the appropriate directories under `research/`:

- `research/articles/` - Published journal articles and conference papers
- `research/working-papers/` - Preprints and works in progress
- `research/posters/` - Conference posters and presentations

### Adding a New Publication

1. Create a new folder under the appropriate category:
   ```bash
   mkdir -p research/articles/my-paper-name
   ```

2. Create an `index.qmd` file in the folder with the publication details:
   ```yaml
   ---
   title: "Your Paper Title"
   date: 2024-01-15
   author:
     - name: Your Name
       orcid: 0000-0003-3031-322X
       affiliation: Your University
   categories:
     - Category 1
     - Category 2
   pub-info:
     reference: >-
       <strong>Your Name</strong>, "Paper Title," <em>Journal Name</em>
     links:
       - name: PDF
         url: paper.pdf
         icon: fa-solid fa-file-pdf
         local: true
       - name: DOI
         url: https://doi.org/10.xxxx/xxxxx
         icon: fa-solid fa-scroll
   ---
   
   ## Abstract
   
   Your abstract here...
   ```

3. Add any supporting files (PDFs, images) to the same folder

4. Render the website:
   ```bash
   quarto render
   ```

The publication will automatically appear on the Research page in the appropriate section.

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

The website automatically deploys to GitHub Pages when you push to `main`. Make sure:

1. GitHub Pages is enabled in repository settings
2. Source is set to "GitHub Actions"
3. The workflow has proper permissions

## License

Content © 2025 Lorenzo Fabbri. Code is MIT licensed.

## Acknowledgments

Inspired by the [academicpages](https://github.com/academicpages/academicpages.github.io) template and built with [Quarto](https://quarto.org/).
