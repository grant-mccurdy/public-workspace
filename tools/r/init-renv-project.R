args <- commandArgs(trailingOnly = TRUE)
project <- if (length(args)) args[[1]] else getwd()
project <- normalizePath(project, mustWork = TRUE)
source_libraries <- unique(c(
  path.expand(Sys.getenv("R_LIBS_USER")),
  .libPaths()
))
source_libraries <- normalizePath(
  source_libraries[nzchar(source_libraries) & dir.exists(source_libraries)],
  mustWork = TRUE
)

repos <- getOption("repos")
if (is.null(repos) || identical(unname(repos["CRAN"]), "@CRAN@")) {
  options(repos = c(CRAN = "https://cloud.r-project.org"))
}

if (!requireNamespace("renv", quietly = TRUE)) {
  install.packages(
    "renv",
    repos = "https://cloud.r-project.org",
    dependencies = c("Depends", "Imports", "LinkingTo")
  )
}

setwd(project)

renv::init(project = project, bare = TRUE, force = FALSE, load = FALSE, restart = FALSE)

parse_package_entries <- function(value) {
  packages <- unlist(strsplit(paste(value, collapse = ","), ","))
  packages <- trimws(gsub("\\s*\\(.*\\)", "", packages))
  setdiff(packages, c("", "R"))
}

read_requirements_packages <- function(path) {
  if (!file.exists(path)) {
    return(character())
  }

  expressions <- parse(path)
  for (expression in expressions) {
    if (
      is.call(expression) &&
        identical(expression[[1]], as.name("<-")) &&
        identical(expression[[2]], as.name("packages"))
    ) {
      return(as.character(eval(expression[[3]], envir = baseenv())))
    }
  }

  character()
}

read_description_dependencies <- function(path) {
  if (!file.exists(path)) {
    return(character())
  }

  fields <- read.dcf(path)
  dependency_fields <- intersect(c("Depends", "Imports"), colnames(fields))
  if (!length(dependency_fields)) {
    return(character())
  }

  parse_package_entries(fields[1, dependency_fields])
}

dependency_closure <- function(packages, library_paths) {
  installed <- installed.packages(
    lib.loc = library_paths,
    fields = c("Depends", "Imports", "LinkingTo", "Priority", "Repository")
  )

  closure <- character()
  queue <- sort(unique(packages))

  while (length(queue)) {
    package <- queue[[1]]
    queue <- queue[-1]

    if (package %in% closure || !(package %in% rownames(installed))) {
      next
    }

    priority <- unname(installed[package, "Priority"])
    if (identical(priority, "base")) {
      next
    }

    closure <- c(closure, package)

    dependency_fields <- installed[package, c("Depends", "Imports", "LinkingTo")]
    dependencies <- parse_package_entries(dependency_fields[!is.na(dependency_fields)])
    dependencies <- setdiff(dependencies, closure)
    queue <- sort(unique(c(queue, dependencies)))
  }

  sort(closure)
}

description_packages <- read_description_dependencies("DESCRIPTION")
requirements_packages <- read_requirements_packages("requirements.R")
declared_packages <- if (length(description_packages)) {
  sort(unique(description_packages))
} else {
  sort(unique(requirements_packages))
}

if (!length(declared_packages)) {
  stop("No R dependencies found in requirements.R or DESCRIPTION.")
}

installed <- installed.packages(lib.loc = source_libraries)
missing <- setdiff(declared_packages, rownames(installed))
if (length(missing)) {
  stop(
    "Declared packages are missing from the shared R libraries: ",
    paste(missing, collapse = ", "),
    ". Run tools/r/bootstrap-workspace.R first."
  )
}

packages <- dependency_closure(declared_packages, source_libraries)
project_library <- renv::paths$library(project = project)
dir.create(project_library, recursive = TRUE, showWarnings = FALSE)

source_libraries <- setdiff(normalizePath(source_libraries, mustWork = TRUE), project_library)

renv::hydrate(
  packages = packages,
  library = project_library,
  sources = source_libraries,
  update = "all",
  prompt = FALSE,
  report = TRUE,
  project = project
)

available_libraries <- unique(c(project_library, source_libraries))
available_packages <- rownames(installed.packages(lib.loc = available_libraries))
missing_after_hydrate <- setdiff(packages, available_packages)
if (length(missing_after_hydrate)) {
  stop(
    "Failed to hydrate packages from shared libraries: ",
    paste(missing_after_hydrate, collapse = ", ")
  )
}

renv::snapshot(
  project = project,
  library = available_libraries,
  type = "implicit",
  prompt = FALSE,
  force = TRUE
)

message("renv initialized and snapshotted for: ", project)
