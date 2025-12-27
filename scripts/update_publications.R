#!/usr/bin/env Rscript

# =============================================================================
# Update Publications from Google Scholar
# =============================================================================
# This script fetches publications from Google Scholar and categorizes them
# into journal articles, working papers, and conference posters.
#
# Requirements: scholar package
# Usage: Rscript scripts/update_publications.R
# =============================================================================

#' Fetch publications from Google Scholar
#'
#' @param scholar_id Character string with Google Scholar ID
#' @return Data frame with publication data
#' @export
fetch_publications <- function(scholar_id) {
  cat("Fetching publications from Google Scholar...\n")
  cat("Scholar ID:", scholar_id, "\n")
  
  pubs <- scholar::get_publications(scholar_id)
  cat("Retrieved", nrow(pubs), "publications\n")
  
  return(pubs)
}

#' Clean and normalize publication data
#'
#' @param pubs Data frame with raw publication data
#' @return Data frame with cleaned publication data
#' @export
clean_publications <- function(pubs) {
  cat("\nCleaning publication data...\n")
  
  pubs_clean <- pubs |>
    # Remove duplicates based on title
    dplyr::distinct(title, .keep_all = TRUE) |>
    # Clean up titles (remove extra whitespace, newlines)
    dplyr::mutate(
      title = stringr::str_squish(stringr::str_replace_all(title, "[\n\r]+", " ")),
      journal = stringr::str_squish(journal),
      author = stringr::str_squish(author)
    ) |>
    # Categorize publications
    dplyr::mutate(
      pub_type = dplyr::case_when(
        # Posters: look for "poster" in title or journal field
        stringr::str_detect(stringr::str_to_lower(title), "poster") |
          stringr::str_detect(stringr::str_to_lower(journal), "poster") ~ "poster",
        # Journal articles: have a journal name
        !is.na(journal) & journal != "" ~ "article",
        # Everything else is a working paper
        TRUE ~ "working-paper"
      )
    ) |>
    # Create stable citation keys
    dplyr::mutate(
      first_author = stringr::str_extract(author, "^[A-Za-z]+"),
      first_word = stringr::str_extract(title, "^[A-Za-z]+"),
      citekey = paste0(
        tolower(first_author), 
        year, 
        tolower(first_word)
      )
    ) |>
    # Ensure unique citation keys
    dplyr::group_by(citekey) |>
    dplyr::mutate(
      citekey = dplyr::if_else(
        dplyr::n() > 1,
        paste0(citekey, "_", dplyr::row_number()),
        citekey
      )
    ) |>
    dplyr::ungroup() |>
    # Sort by year (descending) and citations
    dplyr::arrange(dplyr::desc(year), dplyr::desc(cites))
  
  cat("Cleaned", nrow(pubs_clean), "unique publications\n")
  cat("  - Articles:", sum(pubs_clean$pub_type == "article"), "\n")
  cat("  - Working papers:", sum(pubs_clean$pub_type == "working-paper"), "\n")
  cat("  - Posters:", sum(pubs_clean$pub_type == "poster"), "\n")
  
  return(pubs_clean)
}

#' Create a BibTeX entry for a publication
#'
#' @param row Single row data frame with publication data
#' @return Character string with BibTeX entry
#' @export
create_bibtex_entry <- function(row) {
  # Determine entry type based on pub_type
  entry_type <- dplyr::case_when(
    row$pub_type == "article" ~ "article",
    row$pub_type == "poster" ~ "misc",
    !is.na(row$booktitle) & row$booktitle != "" ~ "inproceedings",
    TRUE ~ "misc"
  )
  
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
  
  # Add keywords for filtering by publication type
  entry <- paste0(entry, "  keywords = {", row$pub_type, "},\n")
  
  entry <- paste0(entry, "}\n")
  return(entry)
}

#' Write publications to BibTeX file
#'
#' @param pubs_clean Data frame with cleaned publication data
#' @param output_file Path to output BibTeX file
#' @return NULL (writes to file)
#' @export
write_bibtex <- function(pubs_clean, output_file) {
  cat("\nConverting to BibTeX format...\n")
  
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
  cat("Writing to", output_file, "...\n")
  writeLines(bibtex_content, output_file)
  
  # Verify the file
  if (file.exists(output_file)) {
    file_size <- file.info(output_file)$size
    cat("Successfully wrote", file_size, "bytes to", output_file, "\n")
    
    # Count entries
    bib_lines <- readLines(output_file)
    n_entries <- sum(stringr::str_detect(bib_lines, "^@"))
    cat("BibTeX file contains", n_entries, "entries\n")
  } else {
    cat("ERROR: Failed to create output file\n")
    quit(status = 1)
  }
}

# =============================================================================
# Main execution
# =============================================================================

main <- function() {
  # Configuration
  SCHOLAR_ID <- "QbPv1H0AAAAJ"  # Lorenzo Fabbri's Google Scholar ID
  OUTPUT_FILE <- "references.bib"
  
  cat("Starting publication update...\n")
  
  # Fetch publications
  tryCatch({
    pubs <- fetch_publications(SCHOLAR_ID)
  }, error = function(e) {
    cat("Error fetching publications:", e$message, "\n")
    cat("Cannot continue without publication data.\n")
    quit(status = 1)
  })
  
  # Clean and categorize publications
  pubs_clean <- clean_publications(pubs)
  
  # Display basic info
  cat("\nPublications summary:\n")
  print(head(pubs_clean[, c("title", "year", "journal", "pub_type")], 10))
  
  # Write to BibTeX file
  write_bibtex(pubs_clean, OUTPUT_FILE)
  
  cat("\n=== Publication update complete! ===\n")
  cat("Next steps:\n")
  cat("1. Review", OUTPUT_FILE, "for accuracy\n")
  cat("2. Commit changes to git\n")
  cat("3. Publications will appear on the Research page\n")
}

# Run main function
main()
