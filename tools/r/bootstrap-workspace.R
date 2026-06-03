workspace_packages <- c(
  "adabag",
  "bookdown",
  "broom",
  "caret",
  "data.table",
  "gbm",
  "ggplot2",
  "httpgd",
  "IRkernel",
  "janitor",
  "jsonlite",
  "knitr",
  "languageserver",
  "lme4",
  "lubridate",
  "nlme",
  "quarto",
  "randomForest",
  "readr",
  "readxl",
  "renv",
  "rmarkdown",
  "ROCR",
  "rpart",
  "tidyverse",
  "xfun"
)

workspace_packages <- sort(unique(workspace_packages))

required_commands <- c("cmake", "pkg-config")
missing_commands <- required_commands[Sys.which(required_commands) == ""]

required_pkg_config <- c(
  "fontconfig",
  "freetype2",
  "fribidi",
  "harfbuzz",
  "libuv"
)

pkg_config_exists <- function(package) {
  status <- system2(
    "pkg-config",
    c("--exists", package),
    stdout = FALSE,
    stderr = FALSE
  )
  identical(status, 0L)
}

missing_pkg_config <- if (Sys.which("pkg-config") == "") {
  required_pkg_config
} else {
  required_pkg_config[!vapply(required_pkg_config, pkg_config_exists, logical(1))]
}

if (length(missing_commands) || length(missing_pkg_config)) {
  message("Missing system prerequisites for the shared R toolchain.")
  if (length(missing_commands)) {
    message("Missing commands: ", paste(missing_commands, collapse = ", "))
  }
  if (length(missing_pkg_config)) {
    message("Missing pkg-config libraries: ", paste(missing_pkg_config, collapse = ", "))
  }
  stop(
    "Install the Ubuntu build dependencies documented in ",
    "docs/r-dependency-strategy.md, then rerun this script."
  )
}

repos <- getOption("repos")
if (is.null(repos) || identical(unname(repos["CRAN"]), "@CRAN@")) {
  options(repos = c(CRAN = "https://cloud.r-project.org"))
}

user_library <- path.expand(Sys.getenv("R_LIBS_USER"))
if (!nzchar(user_library)) {
  stop("R_LIBS_USER is not set; refusing to guess a shared library path.")
}

dir.create(user_library, recursive = TRUE, showWarnings = FALSE)
.libPaths(unique(c(user_library, .libPaths())))

installed <- rownames(installed.packages(lib.loc = .libPaths()))
missing <- setdiff(workspace_packages, installed)

if (length(missing)) {
  message("Installing missing workspace R packages: ", paste(missing, collapse = ", "))
  install.packages(
    missing,
    dependencies = c("Depends", "Imports", "LinkingTo"),
    Ncpus = max(1L, parallel::detectCores() - 1L)
  )
} else {
  message("Workspace R packages already installed.")
}

installed <- rownames(installed.packages(lib.loc = .libPaths()))
remaining <- setdiff(workspace_packages, installed)

if (length(remaining)) {
  stop("Missing workspace R packages after install: ", paste(remaining, collapse = ", "))
}

message("Workspace R package setup complete. Checked ", length(workspace_packages), " packages.")
