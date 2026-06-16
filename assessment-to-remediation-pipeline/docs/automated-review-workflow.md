# Automated Review Workflow

## Purpose

The project should show that assessment content and previews pass an inspectable automated review gate before they become offline LMS payload artifacts.

## Review Sequence

```text
draft item bank
-> validate metadata
-> generate deterministic item review packet
-> render student preview
-> render instructor review preview
-> capture visual inspection screenshots
-> generate GPT-5.5 item-review report
-> generate GPT-5.5 visual-review report
-> combine review artifacts into automated review gate
-> export offline Canvas New Quizzes payload if the gate passes
```

## Review Roles

Deterministic validation checks schema, counts, item types, answer-key shape, and feedback coverage.

GPT-5.5 item review checks math correctness, item clarity, domain alignment, distractor plausibility, feedback specificity, public-safety language, and whether any item should be excluded.

GPT-5.5 visual review checks preview readability, layout, scanability, mobile behavior, draft/public-safety banners, and whether presentation problems should block export.

Computer-vision review alone is not used for math/content review. It is paired with structured item review over the canonical item-bank JSON.

## Student Preview

The student preview should show:

- title and instructions,
- module timing,
- item stems,
- answer choices for MCQ items,
- response boxes for numeric SPR items.

It should not show:

- correct answers,
- distractor feedback,
- misconception tags,
- remediation tags,
- Canvas payload details.

## Instructor Review Preview

The instructor review preview should show:

- all student-facing content,
- correct answers,
- solution explanations,
- distractor feedback,
- accepted numeric answer rules,
- domain and subdomain metadata,
- difficulty bands,
- misconception and remediation tags,
- public-safety checklist flags,
- source review status.

## Automated Gate

Canvas export must include only items that pass the automated review gate.

The gate requires:

- deterministic item review has no blocking item issue,
- API-backed GPT-5.5 item review returns `automated_pass` for the item,
- API-backed GPT-5.5 visual review is not `REVISION_REQUIRED` or `BLOCKED`,
- no public-safety or validation-claim blocker is present.

Dry-run review artifacts intentionally block Canvas item export. They are useful for reproducibility and public-safe inspection, but they are not approval evidence.

## Language Boundary

Use “automated GPT-5.5 advisory review gate” or “automated review gate.” Do not describe the diagnostic as validated, standardized, SAT-equivalent, or professionally psychometrically approved.
