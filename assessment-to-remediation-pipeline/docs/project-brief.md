# Project Brief

## Working Name

Assessment-to-Remediation Pipeline

## Portfolio Purpose

This project will serve as a capstone-style public artifact showing how math assessment design, education data workflows, statistical reporting, instructional feedback, remediation planning, and mastery evidence can be connected in one reproducible loop.

The intended audience is hiring teams evaluating capability in assessment analytics, learning systems, education data products, AI-assisted instructional workflows, and public-safe technical execution.

## Core Problem

Schools often collect assessment evidence but struggle to convert it into timely instructional action. A score report alone does not tell a student what to practice, does not tell a teacher which misconceptions are common, and does not create a clear path from diagnosis to remediation to mastery evidence.

## Prototype Solution

Build a static, reproducible workflow that starts with official-source SAT Math correlation research and ends with student, teacher, and decision-support artifacts:

```text
official target research -> assessment creation parameters -> original items
-> HTML preview -> automated GPT-5.5 review gate -> Canvas New Quizzes payloads
-> synthetic attempts -> LMS-style extract -> item/domain analysis
-> misconception tagging -> feedback -> remediation -> mastery check -> reporting
```

## Initial Product Boundary

The MVP is not a live LMS integration, hosted application, live AI product, or validated test. It is a local demonstration that produces inspectable assessment design, preview, and export artifacts before later synthetic attempt simulation.

## Portfolio Positioning

The project should demonstrate:

- mathematics and statistics judgment,
- assessment blueprint design,
- synthetic education data modeling,
- score and item-analysis workflows,
- remediation artifact design,
- public-safe documentation and validation discipline.

## Related Public Portfolio Context

The public workspace already contains adjacent projects:

- `synthetic-education-data`: synthetic education data foundation.
- `assessment-intelligence`: assessment analytics, dashboards, diagnostics, and reporting.
- `instructional-ai-workflows`: teacher-controlled feedback and remediation demos.

This project should connect those themes in a focused instructional-loop prototype rather than merge into any one existing repository.

## Success Criteria

- A reviewer can run the full demo locally.
- All data is synthetic and clearly labeled.
- The diagnostic blueprint is transparent and public-safe.
- The first form is a 36-item, one-hour SAT Math-correlated readiness diagnostic using original items only.
- Canvas support is represented by offline New Quizzes payload artifacts, not live LMS mutation. Item inclusion is controlled by an automated GPT-5.5 advisory review gate.
- Reports connect evidence to instructional action.
- The case study explains the system without private or exaggerated claims.
