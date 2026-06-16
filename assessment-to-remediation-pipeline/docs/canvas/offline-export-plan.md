# Canvas Offline Export Plan

## Purpose

Generate Canvas New Quizzes-compatible payload artifacts without touching a live LMS.

## MVP Outputs

```text
data/outputs/canvas_new_quiz_payload.json
data/outputs/canvas_upload_manifest.json
```

## Payload Scope

The payload should model:

- New Quiz settings,
- item order,
- `choice` items,
- `numeric` items,
- points possible,
- correct answer and scoring data,
- answer-specific feedback for MCQ items,
- general feedback for all items.

## Dry-Run Manifest

The manifest should include:

- export timestamp,
- assessment version,
- item count,
- domain counts,
- item-type counts,
- excluded item count,
- exclusion reasons,
- public-safety status,
- live upload status set to `not_attempted`.

## Live Adapter Boundary

The MVP must not contain live upload code that executes by default. A later adapter can add:

- local credential discovery outside Git,
- sandbox course targeting,
- explicit dry-run and live modes,
- confirmation prompts before mutation,
- Canvas API response capture with private IDs excluded from public artifacts.
