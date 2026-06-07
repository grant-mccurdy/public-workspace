# Public Portfolio Workspace

This repository is the public portfolio orchestration workspace. It keeps shared
public-facing documentation and tooling near the independent project repos, but
it does not own those child repo contents.

## Repo Roles

```text
public/
├── grant-mccurdy.github.io/        # GitHub Pages front door
├── synthetic-math-department/      # synthetic education data foundation
├── assessment-intelligence/        # analytics, dashboards, diagnostics, reports
├── instructional-ai-workflows/     # teacher-controlled AI workflow demos
├── content-intelligence-reporting/ # source-grounded corpus/report pipeline
├── docs/                          # shared public release/toolchain guidance
└── tools/                         # shared local helper scripts
```

The child project directories are independently managed Git repositories. This
workspace repo intentionally ignores them so public project history stays
separate.

## Canonical Strategy

Use `/home/grant/repos/reports/PORTFOLIO_ARCHITECTURE_PLAN.md` as the canonical
portfolio strategy document.

Use `docs/public-release-checklist.md` before publishing or moving material into
any public repo.

Legacy planning notes that should not live in the public workspace were moved to:

```text
/home/grant/repos/reports/public-workspace-legacy/
```

## Shared Toolchain

The shared VS Code/R toolchain lives in `.devcontainer/` and `tools/r/`. Durable
R projects should keep their own `renv.lock` files, while package libraries stay
out of Git.

See:

- `docs/r-vscode-toolchain.md`
- `docs/r-dependency-strategy.md`
- `COMMANDS.md`

## Public Safety

Public repos may include synthetic datasets, public-safe screenshots,
reproducible demos, documentation, and sample outputs.

Do not publish student data, grades, submissions, rosters, private Canvas URLs,
API keys, OAuth files, transcripts, LMS links, career/contact trackers,
copyrighted course material, or private institutional records.
