#!/usr/bin/env Rscript
# Discover new journal articles from ORCID and append to publications.yml.
# Uses the same orcidtr approach as cv-auto.
#
# Only adds works of type "journal-article". Excludes software, posters,
# preprints, and DOIs already referenced anywhere in publications.yml
# (including extra_links).

library(orcidtr)
library(yaml)
library(data.table)

ORCID_ID <- "0000-0003-3031-322X"
PUBLICATIONS_YML <- here::here("publications.yml")
REPORT_FILE <- here::here("_new_publications.md")

config <- yaml::read_yaml(PUBLICATIONS_YML)

# Collect ALL DOIs referenced anywhere in publications.yml (including extra_links)
collect_all_dois <- function(config) {
  dois <- character(0)
  for (section in c("articles", "posters")) {
    for (pub in config[[section]]) {
      if (!is.null(pub$doi)) dois <- c(dois, pub$doi)
      for (link in pub$extra_links) {
        url <- link$url
        # Extract DOI from URLs like https://doi.org/10.xxxx
        if (grepl("doi.org/", url, fixed = TRUE)) {
          doi <- sub(".*doi\\.org/", "", url)
          dois <- c(dois, doi)
        }
      }
    }
  }
  tolower(dois)
}

known_dois <- collect_all_dois(config)

works <- tryCatch(orcid_works(ORCID_ID), error = function(e) {
  message("Failed to fetch ORCID works: ", e$message)
  data.table()
})

if (nrow(works) == 0) {
  message("No works returned from ORCID.")
  quit(status = 0)
}

works[, doi := tolower(trimws(doi))]
works <- works[!is.na(doi) & doi != ""]

# Only discover journal articles (software, posters, preprints handled separately)
works <- works[type == "journal-article"]

missing <- works[!doi %in% known_dois]

if (nrow(missing) == 0) {
  message("All ORCID journal articles are already in publications.yml.")
  unlink(REPORT_FILE)
  quit(status = 0)
}

message(sprintf("Found %d new journal article(s) from ORCID.", nrow(missing)))

yml_lines <- readLines(PUBLICATIONS_YML)

# Find the line where articles section entries end (before posters: section)
posters_line <- grep("^posters:", yml_lines)
if (length(posters_line) == 0) {
  insert_at <- length(yml_lines)
} else {
  # Insert before the blank line preceding "posters:"
  insert_at <- posters_line[1] - 1
  while (insert_at > 0 && trimws(yml_lines[insert_at]) == "") {
    insert_at <- insert_at - 1
  }
}

new_entries <- vapply(seq_len(nrow(missing)), function(i) {
  row <- missing[i]
  paste0('\n  - doi: "', row$doi, '"\n    categories: []')
}, character(1))

yml_lines <- c(
  yml_lines[seq_len(insert_at)],
  new_entries,
  "",
  if (insert_at < length(yml_lines)) yml_lines[(insert_at + 1):length(yml_lines)]
)

writeLines(yml_lines, PUBLICATIONS_YML)
message(sprintf("Appended %d entry/entries to publications.yml (articles section).", nrow(missing)))

report_lines <- vapply(seq_len(nrow(missing)), function(i) {
  row <- missing[i]
  title <- if (!is.na(row$title)) row$title else "(no title)"
  sprintf("- [ ] [`%s`](https://doi.org/%s) — %s", row$doi, row$doi, title)
}, character(1))

writeLines(report_lines, REPORT_FILE)
message("Wrote report to ", REPORT_FILE)
