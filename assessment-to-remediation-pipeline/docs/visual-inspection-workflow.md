# Visual Inspection Workflow

## Purpose

This workflow reviews generated assessment previews before any item is included in an offline Canvas export payload. It adapts the existing public visual-smoke pattern and the private GPT-5.5 visual-review pattern into a public-safe assessment workflow.

## Workflow

```text
make all
-> render student and instructor previews
-> capture desktop and mobile screenshots
-> run deterministic visual checks
-> generate GPT-5.5 review prompt/report in dry-run mode
-> optional GPT-5.5 advisory critique with explicit API flag
-> structured GPT-5.5 item review
-> automated review gate
```

## Commands

Run deterministic visual inspection:

```bash
make visual-inspect
```

Generate the GPT-5.5 advisory prompt/report without calling the API:

```bash
make visual-review-dry-run
```

Run the optional API-backed review only after confirming the preview artifacts are public-safe:

```bash
OPENAI_VISUAL_REVIEW_MODEL=gpt-5.5 make visual-review-api
```

The API-backed path is intentionally excluded from `make check`.

## Outputs

```text
reports/visual-inspection/
  visual-inspection.json
  visual-inspection.md
  gpt-5-5-visual-review-prompt.json
  gpt-5-5-visual-review.json
  gpt-5-5-visual-review.md
  screenshots/
    student-desktop.png
    student-mobile.png
    instructor-desktop.png
    instructor-mobile.png
```

## Review Criteria

Deterministic checks confirm:

- both preview pages load from a local server,
- page titles and headings are present,
- expected public-safety language appears,
- item counts match the 36-item contract,
- module headings are present,
- body text is nonblank,
- horizontal overflow is not detected.

GPT-5.5 review, when explicitly run, should assess:

- readability,
- visual hierarchy,
- page density,
- mobile usability,
- instructor review usefulness,
- whether the previews support safe automated review,
- whether any item-format or presentation issue should block the automated gate.

## Safety Boundary

The visual workflow is advisory. It must not:

- validate assessment content by itself,
- create or update Canvas quizzes,
- send or publish anything,
- include real student data,
- include live Canvas IDs, URLs, or credentials,
- use private Career OS job-search artifacts.

Structured GPT-5.5 item review remains required before the automated gate can allow Canvas payload export. Visual review alone is not sufficient for math/content review.
