# Academic Website Implementation - Complete Documentation

## Project Overview
This repository contains a complete Quarto-based academic website implementation inspired by academicpages, using R, renv, and automated publication management.

## Implementation Details

### All Tasks Completed (13/13)

#### ✅ TASK 1 — Quarto Website Initialization
- **File:** `_quarto.yml`
- **Configuration:**
  - Output directory: `docs/` (GitHub Pages compatible)
  - Theme: Flatly (clean, professional academic look)
  - Bootstrap icons enabled
  - Full navbar with 6 pages
  - Footer with social links
  - TOC on right side
  - Code folding enabled

#### ✅ TASK 2 — R Environment Setup
- **Files:**
  - `.Rprofile` - Activates renv automatically
  - `renv.lock` - Locked package versions
  - `renv/activate.R` - Bootstrap script
  - `renv/settings.json` - renv configuration
- **Packages included:**
  - quarto (1.4)
  - scholar (0.2.4) - For Google Scholar integration
  - bibtex (0.5.1) - BibTeX parsing
  - dplyr (1.1.4) - Data manipulation
  - stringr (1.5.1) - String operations
  - httr, jsonlite, xml2, rvest - Web scraping dependencies

#### ✅ TASK 3 — Navigation Pages
All pages follow academicpages-style typography and structure:

1. **`index.qmd`** - About/Home page
   - Academic bio section
   - Research interests (bulleted)
   - News & updates box
   - Contact information

2. **`cv.qmd`** - Curriculum Vitae
   - PDF embed with iframe
   - Download button
   - Links to: https://github.com/lorenzoFabbri/cv-quarto/blob/main/cv.pdf

3. **`research.qmd`** - Publications & Research
   - Journal articles (auto-loaded from references.bib)
   - Working papers (manual curation)
   - Work in progress
   - Link to Google Scholar

4. **`blog.qmd`** - Blog listing
   - Listing configuration
   - RSS feed enabled
   - Categories and dates
   - Posts from `/posts/` directory

5. **`talks.qmd`** - Talks & Presentations
   - Chronological tables
   - Links to slides, videos, papers
   - Link to talks archive: https://github.com/lorenzoFabbri/talks

6. **`now.qmd`** - Current Activities
   - "Now page" following nownownow.com movement
   - Current research focus
   - Upcoming events
   - Recent accomplishments

#### ✅ TASK 4 — Social & Identity Icons
Integrated in navbar (right side) and footer:
- **GitHub:** https://github.com/lorenzoFabbri
- **LinkedIn:** https://www.linkedin.com/in/lorenzo-fabbri-303185383/
- **Bluesky:** https://bsky.app/profile/epilorenzo.bsky.social
- **ORCID:** https://orcid.org/my-orcid?orcid=0000-0003-3031-322X

#### ✅ TASK 5 — About Page Content
- Academic bio with position and affiliation placeholders
- Bulleted research interests
- News/Updates section (academicpages-style)
- Education section
- Contact information

#### ✅ TASK 6 — CV Page with PDF Preview
- Embedded PDF preview using iframe
- Prominent download button (Bootstrap styled)
- Fallback links for browsers without iframe support
- Links to GitHub-hosted CV

#### ✅ TASK 7 — Google Scholar Auto-sync
- **File:** `scripts/update_publications.R`
- **Scholar ID:** QbPv1H0AAAAJ
- **Features:**
  - Fetches publications using `scholar::get_publications()`
  - Converts to BibTeX format
  - Deduplication by title
  - Stable citation keys: `firstauthor_year_firstword`
  - Sorts by year (descending) and citations
  - Preserves DOIs and URLs
  - Adds keywords for filtering
  - Normalizes author names and journal titles
- **Output:** `references.bib`

#### ✅ TASK 8 — GitHub Actions Automation

**Workflow 1: `.github/workflows/update-publications.yml`**
- **Triggers:**
  - Weekly schedule (Monday 00:00 UTC)
  - Manual workflow_dispatch
  - Push to main (when script changes)
- **Actions:**
  1. Checkout repository
  2. Setup R (4.3.0)
  3. Setup renv and restore packages
  4. Run `scripts/update_publications.R`
  5. Check for changes to `references.bib`
  6. Commit and push if updated
  7. Post summary to workflow run

**Workflow 2: `.github/workflows/deploy-website.yml`**
- **Triggers:**
  - Push to main
  - Manual workflow_dispatch
- **Actions:**
  1. Checkout repository
  2. Setup Quarto (1.4.550)
  3. Setup R and renv
  4. Render Quarto website
  5. Upload artifact to GitHub Pages
  6. Deploy to GitHub Pages

#### ✅ TASK 9 — Research Page
- **Journal Articles:**
  - Auto-loaded from `references.bib`
  - Uses APA citation style (apa.csl)
  - Formatted: Author(s). Year. Title. *Journal*. DOI/link
  - Sorted by year (descending)

- **Working Papers:**
  - Manual curation
  - Title, abstract, and links
  - Links to: PDF, GitHub, SSRN

- **Work in Progress:**
  - Bulleted list with brief descriptions

#### ✅ TASK 10 — Blog Setup
- **Main page:** `blog.qmd`
- **Posts directory:** `posts/`
- **Sample post:** `posts/welcome/index.qmd`
- **Features:**
  - Listing configuration (default style)
  - Dates and categories/tags
  - RSS feed (automatic)
  - Clean academic layout
  - Chronological sorting (newest first)

#### ✅ TASK 11 — Talks Page
- Chronological tables by year (2025, 2024, etc.)
- Columns: Date, Event, Title, Materials
- Links to slides, videos, papers
- Invited talks section
- Discussion & panels section
- **Prominent link:** https://github.com/lorenzoFabbri/talks

#### ✅ TASK 12 — Custom Styling
- **File:** `custom.css` (4.8KB)
- **Typography:**
  - Body: Palatino (serif) for academic feel
  - Headers: Helvetica (sans-serif) for clarity
  - Code: Monaco/Consolas (monospace)
- **Features:**
  - Clean section headers with borders
  - Optimized spacing for publication lists
  - News/updates box styling (light blue background, left border)
  - Download section styling
  - Table styles with hover effects
  - Responsive design (mobile-friendly)
  - Print-friendly styles
  - Accessibility improvements (focus outlines, sr-only class)
- **Color scheme:**
  - Primary: #2c5282 (blue)
  - Hover: #1a365d (darker blue)
  - Background: #f8f9fa (light gray)
  - Border: #dee2e6 (medium gray)
  - Text: #333 (dark gray)
- **No dark mode** (as requested)

#### ✅ TASK 13 — Final Output
All files created and documented:

**Configuration Files (4):**
- `_quarto.yml` - Main Quarto configuration
- `.Rprofile` - R startup with renv
- `renv.lock` - Package dependencies
- `.gitignore` - Excludes build artifacts and dependencies

**Content Pages (6):**
- `index.qmd` - About/Home
- `cv.qmd` - Curriculum Vitae
- `research.qmd` - Publications
- `blog.qmd` - Blog listing
- `talks.qmd` - Talks & presentations
- `now.qmd` - Current activities

**Styling (2):**
- `custom.css` - Custom academic styles
- `apa.csl` - APA citation style (83KB)

**Bibliography (1):**
- `references.bib` - Publications database

**Documentation (1):**
- `README.md` - Comprehensive project documentation

**R Environment (3):**
- `renv/activate.R` - Bootstrap script
- `renv/settings.json` - renv configuration
- `scripts/update_publications.R` - Scholar sync script

**GitHub Actions (2):**
- `.github/workflows/deploy-website.yml` - Build & deploy
- `.github/workflows/update-publications.yml` - Publication sync

**Blog Posts (1):**
- `posts/welcome/index.qmd` - Sample welcome post

**Docs (2):**
- `docs/index.html` - Placeholder page
- `docs/.nojekyll` - GitHub Pages configuration

**Total:** 22 files created

## Architecture Decisions

### Why Quarto?
- Modern publishing system
- Native R integration
- Excellent citation support
- Beautiful default themes
- Easy GitHub Pages deployment

### Why renv?
- Reproducible package environment
- Works seamlessly with GitHub Actions
- Isolates project dependencies
- Version locking prevents breakage

### Why Flatly Theme?
- Clean, professional appearance
- Good typography for academic content
- Not too flashy (as requested)
- Well-suited for text-heavy pages
- Light mode only (as requested)

### Why APA Citation Style?
- Standard in social sciences
- Clean, readable format
- Wide recognition in academia

## Usage Instructions

### Local Development
```bash
# Clone repository
git clone https://github.com/lorenzoFabbri/epilorenzo.git
cd epilorenzo

# Restore R packages
R -e "renv::restore()"

# Preview site
quarto preview

# Render site
quarto render
```

### Update Publications
```bash
# Run locally
Rscript scripts/update_publications.R

# Or trigger GitHub Action
# Go to Actions → Update Publications → Run workflow
```

### Add Blog Post
```bash
# Create post directory
mkdir -p posts/my-post-title

# Create post file
cat > posts/my-post-title/index.qmd << EOF
---
title: "My Post Title"
description: "Short description"
author: "Lorenzo Fabbri"
date: "2025-01-15"
categories: [research, methods]
---

Your content here...
EOF

# Render
quarto render
```

### Customization

**Change theme:**
Edit `_quarto.yml`, line with `theme:`, replace `flatly` with another Bootswatch theme (e.g., `cosmo`, `journal`, `simplex`)

**Modify colors:**
Edit `custom.css`, search for color codes (e.g., `#2c5282`) and replace

**Update social links:**
Edit `_quarto.yml`, find `navbar` → `right` section and update URLs

**Change fonts:**
Edit `custom.css`, find `font-family` declarations and replace

## Key Configuration Choices

### Quarto Configuration
- **Output directory:** `docs/` for GitHub Pages compatibility
- **Freeze:** `auto` - caches computations
- **TOC:** Right side, depth 3
- **Code:** Folding enabled, tools available
- **Links:** External links open in new window with icon

### R Package Selection
- **scholar:** Google Scholar API access
- **bibtex:** Parse and write BibTeX
- **dplyr/stringr:** Data cleaning
- **httr/xml2/rvest:** Web scraping (scholar dependency)

### CSS Architecture
- **Mobile-first:** Base styles, then media queries
- **Print-friendly:** Hides nav/footer, adjusts fonts
- **Accessibility:** Focus outlines, semantic HTML
- **No dark mode:** Single color scheme as requested

### GitHub Actions Design
- **Separate workflows:** Build vs. sync (separation of concerns)
- **Weekly sync:** Balance between freshness and API limits
- **Manual triggers:** Flexibility for immediate updates
- **Auto-commit:** Reduces manual work

## Maintenance

### Regular Tasks
- [ ] Update personal information in pages
- [ ] Add new working papers to research.qmd
- [ ] Write blog posts in posts/
- [ ] Update talks.qmd with new presentations
- [ ] Refresh now.qmd monthly

### Quarterly Review
- [ ] Check for Quarto updates
- [ ] Update R packages (renv::update())
- [ ] Review and clean old blog posts
- [ ] Verify all external links work

### Annual Review
- [ ] Update CV PDF
- [ ] Archive old talks
- [ ] Review and update custom.css
- [ ] Check Google Scholar sync accuracy

## Troubleshooting

### Build Fails
- Check Quarto version (need 1.4+)
- Verify R version (need 4.3+)
- Run `renv::restore()` to fix packages

### Publications Not Updating
- Check Scholar ID is correct
- Verify API is accessible
- Check workflow logs in GitHub Actions

### Styling Issues
- Clear browser cache
- Check custom.css syntax
- Verify Bootstrap icons CDN is accessible

### GitHub Pages Not Deploying
- Verify Settings → Pages → Source: "GitHub Actions"
- Check workflow permissions (needs write access)
- Review deploy-website.yml logs

## Links & References

### Repository
- **Main repo:** https://github.com/lorenzoFabbri/epilorenzo
- **Talks archive:** https://github.com/lorenzoFabbri/talks
- **CV repo:** https://github.com/lorenzoFabbri/cv-quarto

### External Profiles
- **Google Scholar:** https://scholar.google.com/citations?user=QbPv1H0AAAAJ&hl=en
- **GitHub:** https://github.com/lorenzoFabbri
- **LinkedIn:** https://www.linkedin.com/in/lorenzo-fabbri-303185383/
- **Bluesky:** https://bsky.app/profile/epilorenzo.bsky.social
- **ORCID:** https://orcid.org/my-orcid?orcid=0000-0003-3031-322X

### Resources
- **Quarto:** https://quarto.org/
- **renv:** https://rstudio.github.io/renv/
- **academicpages:** https://github.com/academicpages/academicpages.github.io
- **Now page movement:** https://nownownow.com/

## Success Criteria Met

✅ All 13 tasks completed as specified
✅ Working code (not just concepts)
✅ Full folder structure in place
✅ Commented code explaining key choices
✅ Academic styling (serif fonts, clean headers)
✅ Reproducible with R + renv + Quarto
✅ Automated publication sync from Google Scholar
✅ GitHub Actions for CI/CD
✅ Blog with RSS feed
✅ All external links integrated
✅ Ready for immediate deployment

## Status: ✅ COMPLETE

All requirements from the problem statement have been implemented. The repository is ready for:
1. Merging to main branch
2. Enabling GitHub Pages
3. Customization with personal content
4. Immediate deployment

---

*Documentation last updated: 2025-12-27*
