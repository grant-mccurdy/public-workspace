# R And VS Code Toolchain

This workspace uses VS Code as the UI and R as the statistical build/runtime
layer. It does not install or run RStudio Server.

There are two supported ways to open the workspace:

- Open `~/repos/public`: uses `public/.devcontainer/`.
- Open `~/repos`: uses `~/repos/.devcontainer/`, which shares the same
  toolchain and runs package setup from
  `public/assessment-intelligence/requirements.R`.

The devcontainer installs:

- R and Rscript
- Pandoc
- LaTeX for PDF knitting
- Quarto CLI
- system libraries needed by common R packages
- VS Code R, Quarto, and Jupyter extensions
- R language server and HTTP graphics support
- IRkernel for notebook work
- renv for project-level dependency snapshots

## Rebuild

In VS Code or Codespaces, rebuild the container after adding `.devcontainer/`.
After rebuild, verify:

```bash
Rscript --version
R --version
pandoc --version
quarto --version
```

If VS Code was already open before the devcontainer was added, use
`Dev Containers: Rebuild and Reopen in Container` from the command palette.

## Package Setup

The devcontainer runs:

```bash
Rscript tools/r/bootstrap-workspace.R
```

You can rerun it manually from the workspace root. This installs the shared
machine-level R package set into the normal user R library. It does not put an R
package library inside `~/repos`.

For durable project-level reproducibility, initialize `renv` in the project:

```bash
Rscript tools/r/init-renv-project.R \
  assessment-intelligence
```

Then commit the project dependency metadata, including `renv.lock`, while
leaving `renv/library/` uncommitted. See `docs/r-dependency-strategy.md`.

## Assessment Commands

From `assessment-intelligence/`:

```bash
make r-check
make r-setup
make toolchain-smoke
make render-report-html
make render-report-pdf
```

`make toolchain-smoke` is the replacement-readiness check for the older
project-specific statistics devcontainer. It verifies:

- R and Rscript are available.
- Pandoc and Quarto are available.
- R Markdown renders to HTML.
- R Markdown renders to PDF through LaTeX.
- Quarto renders an HTML document with embedded R.

If this target passes from a VS Code session opened at `~/repos`, the older
statistics-project devcontainer is redundant unless RStudio Server is still
needed.

Gradebook reconstruction uses a private reference path supplied at runtime:

```bash
export REFERENCE_GRADEBOOK="<private reference gradebook path>"
make gradebook-profile
make synthetic-gradebook
make validate-gradebook
```
