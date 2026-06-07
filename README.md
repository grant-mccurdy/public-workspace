# Public Portfolio Strategy

This workspace stages a public GitHub portfolio around four focused project areas plus a GitHub Pages front door.

The portfolio should present work at the intersection of mathematics, statistics, education, assessment, analytics, AI workflows, and software. It should not read as a private school operations folder or as a Canvas-only developer portfolio.

## Repository Architecture

```text
public/
├── grant-mccurdy.github.io/
├── synthetic-math-department/
├── assessment-intelligence/
├── instructional-ai-workflows/
├── content-intelligence-reporting/
└── docs/
```

The GitHub Pages site is part of the public-facing portfolio surface. It should
present and link to the project work in this workspace.

## Project Areas

### Synthetic Math Department

Privacy-preserving synthetic education data generation and validation for
assessment analytics, dashboard development, and learning-systems prototyping.

### Assessment Intelligence

Public-safe assessment system work: analytics, reproducible processing,
dashboarding, diagnostics, and decision-support reporting for mathematics
programs.

### Instructional AI Workflows

Teacher-controlled instructional workflows: rubric-defined evaluation, structured draft feedback, human review, and student-facing feedback, review, or remediation artifacts.

### Content Intelligence Reporting

Source-grounded content processing: turn unstructured content into a searchable corpus and generate targeted analytical reports with clear source boundaries.

### GitHub Pages Front Door

`grant-mccurdy.github.io` is the presentation layer. It should summarize and link
to the public project areas, not contain all project code.

## Public Safety Boundary

Public repos may include synthetic datasets, public-safe screenshots, reproducible demos, documentation, and sample outputs.

Public repos must not include student data, grades, submissions, private Canvas URLs, API keys, OAuth files, private transcripts, private LMS links, school-private records, career/contact trackers, or copyrighted course materials without permission.

See `docs/public-release-checklist.md` before moving material into any public repo.

## Current Status

This workspace contains public-safe project scaffolding and reproducible demos in
progress. Keep internal planning notes and private audit details outside public
commits.

## R Toolchain

This workspace is configured for VS Code-based R work through `.devcontainer/`.
The parent `~/repos` workspace also has a matching devcontainer, so opening
either `public/` or the full `~/repos` folder can provide the same R toolchain.
It installs R, Pandoc, LaTeX, Quarto, and common R packages without installing
RStudio Server. Shared machine packages are bootstrapped with
`tools/r/bootstrap-workspace.R`; durable R projects should use `renv` lockfiles.
See `docs/r-vscode-toolchain.md` and `docs/r-dependency-strategy.md`.
