# Public Workspace Commands

Run these from `/home/grant/repos/public` unless a command says otherwise.

## Workspace Status

```bash
bash /home/grant/repos/reports/check-workspace-health.sh
```

For a compact public-only view:

```bash
git status --short --branch

for repo in \
  grant-mccurdy.github.io \
  synthetic-education-data \
  assessment-intelligence \
  instructional-ai-workflows \
  content-intelligence
do
  git -C "$repo" status --short --branch
done
```

## Project Checks

```bash
make -C synthetic-education-data all
make -C content-intelligence all
make -C instructional-ai-workflows all
make -C assessment-intelligence all
make -C grant-mccurdy.github.io check
```

## Public Safety Scans

```bash
rg -n --hidden --glob '!.git/**' -i \
  '(api[_ -]?key|secret|token|password|credential|private key|bearer|sk-[A-Za-z0-9_-]{20,})' .

rg -n --hidden --glob '!.git/**' -i \
  '(/home/grant|/mnt/c|private/data|reference_artifacts|canvas\.instructure|student|gradebook|submission|roster)' .
```

Review any findings manually before committing or pushing public changes. Do not
paste secret values into reports, issues, or commit messages.

## GitHub Pages Visual Check

```bash
make -C grant-mccurdy.github.io visual-smoke
```

If Playwright is not installed locally, install it in the current Node
environment or set `PLAYWRIGHT_MODULE_DIR` to a `node_modules` directory that
contains `playwright`.

In WSL, if `node` is not installed but Windows `node.exe` is visible, pass a
Windows-style `PLAYWRIGHT_MODULE_DIR` path for the visual check.
