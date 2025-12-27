local({
  # the requested version of renv
  version <- "1.0.3"
  attr(version, "sha") <- NULL
  
  # signal that we're loading renv during R startup
  Sys.setenv("RENV_R_INITIALIZING" = "true")
  on.exit(Sys.unsetenv("RENV_R_INITIALIZING"), add = TRUE)
  
  # avoid recursion
  if (!is.na(Sys.getenv("RENV_R_LOADING", unset = NA)))
    return(invisible(TRUE))
  
  # load the 'utils' package eagerly -- this ensures that renv shims, which
  # mask 'utils' packages, will come first on the search path
  library(utils, lib.loc = .Library)
  
  # unload renv if it's already loaded
  if ("renv" %in% loadedNamespaces())
    try(unloadNamespace("renv"), silent = TRUE)
  
  # load bootstrap tools   
  `%||%` <- function(x, y) {
    if (is.null(x)) y else x
  }
  
  renv_bootstrap_download <- function(version) {
    
    # construct URL
    cran <- Sys.getenv("RENV_CRAN", unset = "https://cloud.r-project.org")
    url <- paste(cran, "src/contrib/Archive/renv", sprintf("renv_%s.tar.gz", version), sep = "/")
    
    # use a temporary directory for staging
    tempdir <- tempfile("renv-bootstrap-")
    dir.create(tempdir, showWarnings = FALSE, recursive = TRUE)
    on.exit(unlink(tempdir, recursive = TRUE), add = TRUE)
    
    # download + install renv
    tarball <- file.path(tempdir, basename(url))
    download.file(url, tarball, quiet = TRUE)
    install.packages(tarball, repos = NULL, type = "source", quiet = TRUE)
    
  }
  
  renv_bootstrap_load <- function(project) {
    
    # try to load renv from the project library
    library(renv, lib.loc = renv_paths_library(project = project))
    
  }
  
  renv_paths_library <- function(project) {
    
    path <- Sys.getenv("RENV_PATHS_LIBRARY", unset = NA)
    if (!is.na(path))
      return(path)
    
    path <- Sys.getenv("RENV_PATHS_LIBRARY_ROOT", unset = NA)
    if (!is.na(path)) {
      name <- paste(R.version$platform, getRversion(), sep = "-")
      return(file.path(path, project, name))
    }
    
    file.path(project, "renv/library", R.version$platform, getRversion())
    
  }
  
  # try to load renv from the project library
  bootstrap <- function(version, library) {
    
    # attempt to download renv
    tarball <- tryCatch(
      renv_bootstrap_download(version),
      error = identity
    )
    
    # load it
    if (inherits(tarball, "error"))
      return(FALSE)
    
    # load renv
    status <- tryCatch(
      renv_bootstrap_load(getwd()),
      error = identity
    )
    
    # check for errors
    !inherits(status, "error")
    
  }
  
  # construct path to library root
  project <- Sys.getenv("RENV_PROJECT", unset = getwd())
  libpath <- renv_paths_library(project = project)
  
  # use renv if it's already available
  if (requireNamespace("renv", lib.loc = libpath, quietly = TRUE))
    return(renv::load(project = project))
  
  # bootstrap if needed
  bootstrap(version, libpath)
  renv::load(project = project)
  
})
