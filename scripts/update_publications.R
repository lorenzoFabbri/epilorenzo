#!/usr/bin/env Rscript

# =============================================================================
# Update Publications from Google Scholar
# =============================================================================
# This script fetches publications from Google Scholar and converts them
# to a clean BibTeX file for use in the Quarto website.
#
# Requirements: scholar, dplyr, stringr, bibtex packages
# Usage: Rscript scripts/update_publications.R
# =============================================================================

library(scholar)
library(dplyr)
library(stringr)
library(bibtex)

# Configuration
SCHOLAR_ID <- "QbPv1H0AAAAJ"  # Lorenzo Fabbri's Google Scholar ID
OUTPUT_FILE <- "references.bib"

cat("Starting publication update...\n")
cat("Scholar ID:", SCHOLAR_ID, "\n")

# Fetch publications from Google Scholar
cat("\nFetching publications from Google Scholar...\n")
tryCatch({
  pubs <- get_publications(SCHOLAR_ID)
  cat("Retrieved", nrow(pubs), "publications\n")
}, error = function(e) {
  cat("Error fetching publications:", e$message, "\n")
  cat("Using cached/example data instead.\n")
  quit(status = 1)
})

# Display basic info
cat("\nPublications summary:\n")
print(head(pubs[, c("title", "year", "journal")], 10))

# Data cleaning and normalization
cat("\nCleaning publication data...\n")

# Clean and normalize data
pubs_clean <- pubs %>%
  # Remove duplicates based on title
  distinct(title, .keep_all = TRUE) %>%
  # Sort by year (descending) and citations
  arrange(desc(year), desc(cites)) %>%
  # Clean up titles (remove extra whitespace, newlines)
  mutate(
    title = str_squish(str_replace_all(title, "[\n\r]+", " ")),
    journal = str_squish(journal),
    author = str_squish(author)
  ) %>%
  # Create stable citation keys
  mutate(
    # Create citation key: firstauthor_year_firstword
    first_author = str_extract(author, "^[A-Za-z]+"),
    first_word = str_extract(title, "^[A-Za-z]+"),
    citekey = paste0(
      tolower(first_author), 
      year, 
      tolower(first_word)
    )
  ) %>%
  # Ensure unique citation keys
  group_by(citekey) %>%
  mutate(
    citekey = if_else(
      n() > 1,
      paste0(citekey, "_", row_number()),
      citekey
    )
  ) %>%
  ungroup()

cat("Cleaned", nrow(pubs_clean), "unique publications\n")

# Convert to BibTeX format
cat("\nConverting to BibTeX format...\n")

# Function to create a BibTeX entry
create_bibtex_entry <- function(row) {
  # Determine entry type
  entry_type <- if (!is.na(row$journal) && row$journal != "") {
    "article"
  } else if (!is.na(row$booktitle) && row$booktitle != "") {
    "inproceedings"
  } else {
    "misc"
  }
  
  # Build entry
  entry <- paste0("@", entry_type, "{", row$citekey, ",\n")
  entry <- paste0(entry, "  author = {", row$author, "},\n")
  entry <- paste0(entry, "  title = {{", row$title, "}},\n")
  entry <- paste0(entry, "  year = {", row$year, "},\n")
  
  # Add journal or booktitle
  if (entry_type == "article" && !is.na(row$journal) && row$journal != "") {
    entry <- paste0(entry, "  journal = {", row$journal, "},\n")
    if (!is.na(row$number) && row$number != "") {
      entry <- paste0(entry, "  number = {", row$number, "},\n")
    }
  } else if (entry_type == "inproceedings" && !is.na(row$booktitle) && row$booktitle != "") {
    entry <- paste0(entry, "  booktitle = {", row$booktitle, "},\n")
  }
  
  # Add URL if available (from cid - this is the Google Scholar link)
  if (!is.na(row$cid) && row$cid != "") {
    entry <- paste0(entry, "  url = {https://scholar.google.com/scholar?cluster=", row$cid, "},\n")
  }
  
  # Add pubid if available for stable reference
  if (!is.na(row$pubid) && row$pubid != "") {
    entry <- paste0(entry, "  note = {Google Scholar ID: ", row$pubid, "},\n")
  }
  
  # Add keywords for filtering
  if (!is.na(row$journal) && row$journal != "") {
    entry <- paste0(entry, "  keywords = {journal},\n")
  }
  
  entry <- paste0(entry, "}\n")
  return(entry)
}

# Generate BibTeX content
bibtex_content <- ""
for (i in 1:nrow(pubs_clean)) {
  bibtex_content <- paste0(
    bibtex_content,
    create_bibtex_entry(pubs_clean[i, ]),
    "\n"
  )
}

# Write to file
cat("\nWriting to", OUTPUT_FILE, "...\n")
writeLines(bibtex_content, OUTPUT_FILE)

# Verify the file
if (file.exists(OUTPUT_FILE)) {
  file_size <- file.info(OUTPUT_FILE)$size
  cat("Successfully wrote", file_size, "bytes to", OUTPUT_FILE, "\n")
  
  # Count entries
  bib_lines <- readLines(OUTPUT_FILE)
  n_entries <- sum(str_detect(bib_lines, "^@"))
  cat("BibTeX file contains", n_entries, "entries\n")
} else {
  cat("ERROR: Failed to create output file\n")
  quit(status = 1)
}

cat("\n=== Publication update complete! ===\n")
cat("Next steps:\n")
cat("1. Review", OUTPUT_FILE, "for accuracy\n")
cat("2. Commit changes to git\n")
cat("3. Publications will appear on the Research page\n")
