#' Date a page last changed, as "Month YYYY"
#'
#' Reads the date from the file's last commit rather than the render time, so a
#' rebuild that changes nothing (the monthly publication cron, a manual deploy)
#' does not advance the date. An uncommitted edit in the working tree is dated
#' today, since that edit is what the render is about to publish.
#'
#' @param path Path to the file, relative to the project root.
#'
#' @return A character string such as `"August 2026"`.
last_updated <- function(path) {
  git <- function(args) {
    tryCatch(
      suppressWarnings(system2("git", args, stdout = TRUE, stderr = FALSE)),
      error = function(e) character(0)
    )
  }

  uncommitted <- length(git(c("status", "--porcelain", "--", path))) > 0
  committed <- git(c("log", "-1", "--format=%cs", "--", path))

  date <- if (uncommitted || length(committed) == 0 || !nzchar(committed[1])) {
    # No git history for the file: a shallow clone, or a file never committed.
    if (uncommitted || !file.exists(path)) Sys.Date() else as.Date(file.mtime(path))
  } else {
    as.Date(committed[1])
  }

  # month.name rather than format("%B"), which follows the renderer's locale.
  paste(month.name[as.integer(format(date, "%m"))], format(date, "%Y"))
}
