# Assessment Creation Parameters

## Purpose

This is the authoritative contract for writing original diagnostic items. It converts official SAT Math research into public-safe authoring rules.

## Assessment Shape

| Parameter | Value |
| --- | --- |
| Title | SAT Math Readiness Diagnostic Prototype |
| Time | 60 minutes |
| Modules | 2 |
| Items per module | 18 |
| Total items | 36 |
| MCQ items | 27 |
| Numeric SPR items | 9 |
| Adaptivity | None in v1 |
| Calculator | Permitted by default |

## Domain Counts

| Domain | Items |
| --- | ---: |
| Algebra | 13 |
| Advanced Math | 13 |
| Problem-Solving and Data Analysis | 5 |
| Geometry and Trigonometry | 5 |

## Item Rules

### Multiple Choice

- Exactly 4 answer choices.
- Exactly 1 correct answer.
- Exactly 3 distractors.
- Each distractor must represent a plausible error pattern.
- Each distractor must include feedback that helps the student identify the error.
- The correct answer must include a concise solution explanation.

### Numeric Student-Produced Response

- The item must ask for a numeric answer.
- Accepted answer rules must be explicit.
- Use exact values when possible.
- Allow equivalent fractions/decimals when mathematically appropriate.
- Use tolerance or range only when measurement, estimation, or rounding makes that necessary.

## Required Item Metadata

- `item_id`
- `module`
- `position`
- `domain`
- `subdomain`
- `skill_statement`
- `difficulty_band`
- `item_type`
- `stem_html`
- `choices`
- `correct_answer`
- `accepted_answer_rules`
- `distractor_feedback`
- `general_feedback`
- `misconception_tags`
- `remediation_tag`
- `mastery_check_target`
- `review_status`
- `source_originality_note`

## Review Status Values

- `draft`
- `needs_revision`
- `approved`
- `retired`

The MVP does not rely on changing source item status to permit export. Canvas New Quizzes payload artifacts may include only items allowed by the generated automated review gate.

## Public-Safety Rules

- Item stems must be original.
- Do not copy or closely paraphrase SAT, ACT, AP, state exam, commercial publisher, or school-private items.
- Do not use real school names, student names, teacher names, or private institutional contexts.
- Do not describe this diagnostic as validated unless future validation evidence is added.
