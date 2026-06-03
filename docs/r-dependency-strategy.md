# R Dependency Strategy

Use three layers for R work under `~/repos`.

## Layer 1: Shared Machine Toolchain

The shared user R library is for day-to-day productivity. It should contain
common analysis, reporting, notebook, language-server, and modeling packages.

On Ubuntu, install the system build dependencies first:

```bash
sudo apt install -y \
  r-base \
  r-base-dev \
  r-recommended \
  make \
  pandoc \
  build-essential \
  curl \
  wget \
  pkg-config \
  cmake \
  libcurl4-openssl-dev \
  libssl-dev \
  libxml2-dev \
  libuv1-dev \
  libfontconfig1-dev \
  libfreetype6-dev \
  libharfbuzz-dev \
  libfribidi-dev \
  libpng-dev \
  libjpeg-dev \
  libtiff-dev \
  libgit2-dev \
  libicu-dev \
  zlib1g-dev
```

Bootstrap it from the public workspace root:

```bash
Rscript tools/r/bootstrap-workspace.R
```

This installs packages into the normal user R library, not into `~/repos`.

## Layer 2: Project Reproducibility

Public or private projects that need stable builds should use `renv`.

From the public workspace root:

```bash
Rscript tools/r/init-renv-project.R \
  assessment-intelligence
```

From any other repo:

```bash
Rscript /home/grant/repos/public/tools/r/init-renv-project.R \
  .
```

Commit project dependency metadata:

```text
.Rprofile
renv.lock
renv/activate.R
renv/settings.json
```

Do not commit project-local package libraries:

```text
renv/library/
renv/staging/
renv/sandbox/
```

## Layer 3: External Executables

Some tools are not R packages and must be installed separately:

- R and Rscript
- Pandoc
- Quarto CLI
- LaTeX or TinyTeX for PDF rendering
- system libraries such as curl, SSL, XML, font, image, and build headers

The R package named `quarto` is not the Quarto CLI. Install the Quarto CLI
separately before expecting `quarto --version` or `.qmd` rendering to work.

Check the local machine:

```bash
Rscript --version
R --version
pandoc --version
quarto --version
```

## Policy

Use the shared library to make exploratory and portfolio work fast. Use `renv`
when a repo becomes a durable artifact, a public demo, a report pipeline, or a
project likely to be revisited after package versions change.
