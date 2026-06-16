# Assessment-to-Remediation Pipeline

Public-safe prototype for connecting math diagnostic evidence to feedback, remediation, mastery checks, and decision-support reporting.

## Purpose

This project will demonstrate an inspectable instructional loop:

```text
learning objective / benchmark
-> standards-aligned diagnostic assessment
-> synthetic attempt data
-> scoring and item/domain analysis
-> error-pattern analysis
-> individualized feedback
-> targeted remediation artifacts
-> reassessment or mastery evidence
-> reporting for student, teacher, and academic decision support
```

The first version is intentionally local, static, and reproducible. It should use Python, CSV, JSON, and Markdown outputs before adding dashboards, LMS adapters, or live AI services.

## MVP Direction

- Official-source SAT Math correlation research.
- 36 original math-readiness diagnostic items scaled to a one-hour form.
- Two 30-minute modules with 18 items each.
- 27 four-option multiple-choice items and 9 numeric student-produced response items.
- SAT Math domain proportions scaled to Algebra, Advanced Math, Problem-Solving and Data Analysis, and Geometry and Trigonometry.
- Static HTML preview artifacts for automated GPT-5.5 visual review before LMS export.
- Offline Canvas New Quizzes payload generation and dry-run validation.
- Synthetic students and synthetic responses only in later simulation phases.
- Domain/subdomain blueprint with public skill descriptions.
- Scoring, item analysis, domain reporting, and misconception tags after the assessment form passes the automated review gate.
- Student-facing feedback report.
- Teacher-facing summary report.
- Targeted remediation recommendations.
- Sample mastery-check workflow.
- Public-safe portfolio case-study draft.

## Public-Safety Note

This repository must not contain real student data, parent data, school-private records, grades, submissions, rosters, emails, API keys, OAuth tokens, private Canvas exports, employer-confidential material, or copied commercial assessment items.

The diagnostic should be described as a standards-aligned internal math readiness diagnostic or predictive-validity prototype. Do not claim that it is a validated standardized test unless a future version actually demonstrates appropriate validation evidence.

## What To Open First

- [Student preview](previews/student_form.html)
- [Instructor preview](previews/instructor_review.html)
- [Automated review gate](reports/automated-review/automated-review.md)
- [GPT-5.5 item review](reports/automated-review/gpt-5-5-item-review.md)
- [GPT-5.5 visual review](reports/visual-inspection/gpt-5-5-visual-review.md)
- [Portfolio case study draft](docs/portfolio-case-study-draft.md)

## Planning Docs

- [Project brief](docs/project-brief.md)
- [MVP scope](docs/mvp-scope.md)
- [System architecture](docs/system-architecture.md)
- [Assessment blueprint](docs/assessment-blueprint.md)
- [Assessment creation parameters](docs/assessment-creation-parameters.md)
- [Data model](docs/data-model.md)
- [Privacy and public safety](docs/privacy-and-public-safety.md)
- [Validation plan](docs/validation-plan.md)
- [Automated review workflow](docs/automated-review-workflow.md)
- [Portfolio case-study draft](docs/portfolio-case-study-draft.md)
- [SAT Math correlation target](docs/research/sat-math-correlation-target.md)

## Status

Public-safe assessment-authoring MVP implemented. The project now includes:

- a generated 36-item original draft item bank,
- item-bank validation,
- student and instructor HTML previews,
- offline Canvas New Quizzes dry-run payload artifacts,
- deterministic visual inspection screenshots and reports,
- API-backed GPT-5.5 visual review artifacts,
- API-backed GPT-5.5 item review artifacts,
- an automated review gate that currently passes with all 36 items exportable to the offline Canvas payload.

Current review status:

- automated review gate: `PASS`
- item review: `POLISH_RECOMMENDED` with `36/36` items marked `automated_pass`
- visual review: `POLISH_RECOMMENDED` with no presentation blocker
- Canvas dry-run payload: `36` included items, `0` excluded items

The project is public-safe and ready to be tracked in the public repository. It is not a live LMS deployment, validated assessment, or production Canvas integration.

Validate the committed public artifact set without regenerating outputs:

```bash
make validate-public-artifacts
```

Build a fully deterministic local dry-run artifact set with:

```bash
make all
```

Build an API-reviewed public artifact set with:

```bash
OPENAI_ITEM_REVIEW_MODEL=gpt-5.5 OPENAI_VISUAL_REVIEW_MODEL=gpt-5.5 make canvas-export-api
```

`make all` is useful for local deterministic validation, but it regenerates dry-run review reports and blocks Canvas export by design. Use `make validate-public-artifacts` to check the committed public packet, and use `make canvas-export-api` when you want regenerated artifacts to reflect the API-backed review gate.

Run the optional API-backed visual review only after confirming screenshots are public-safe:

```bash
OPENAI_VISUAL_REVIEW_MODEL=gpt-5.5 make visual-review-api
```

Run the optional API-backed automated review gate only after confirming item-bank and preview artifacts are public-safe:

```bash
OPENAI_ITEM_REVIEW_MODEL=gpt-5.5 OPENAI_VISUAL_REVIEW_MODEL=gpt-5.5 make automated-review-gate-api
```
