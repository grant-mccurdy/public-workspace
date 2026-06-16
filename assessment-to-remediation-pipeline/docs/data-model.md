# Data Model

## Principle

Separate assessment design, synthetic attempts, scoring outputs, analysis outputs, and report artifacts. This keeps the pipeline auditable and reduces the risk of mixing source evidence with interpretations.

## Planned Artifacts

### `data/synthetic/assessment_form_spec.json`

Machine-readable one-hour diagnostic contract.

Fields:

- `assessment_id`
- `title`
- `version`
- `source_policy`
- `timing`
- `item_type_counts`
- `content_domain_counts`
- `module_blueprints`
- `canvas_export_boundary`

### `data/synthetic/diagnostic_blueprint.json`

Structured assessment design.

Fields:

- `assessment_id`
- `version`
- `domains`
- `items`
- `remediation_modules`
- `mastery_check_items`

### `data/synthetic/item_bank.json`

Original item authoring source.

Fields:

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
- `review_status`

The source `review_status` remains authoring metadata. MVP Canvas export eligibility is determined by the generated automated review gate artifact, not by silently rewriting source items.

### `previews/student_form.html`

Static student-facing preview of the diagnostic. It must not reveal answer keys or instructor-only metadata.

### `previews/instructor_review.html`

Static instructor review packet. It may include answer keys, distractor feedback, numeric accepted-answer rules, and metadata because it is a local review artifact, but it must still be public-safe.

### `data/outputs/canvas_new_quiz_payload.json`

Offline Canvas New Quizzes payload artifact. It should contain only automated-gate-passing items and no credentials, URLs, course IDs, or live Canvas identifiers.

### `data/outputs/canvas_upload_manifest.json`

Dry-run manifest describing what would be uploaded to Canvas in a future live adapter.

### `reports/automated-review/automated-review.json`

Combined gate report for deterministic item checks, GPT-5.5 item review, and GPT-5.5 visual review.

Fields:

- `gate_status`
- `export_allowed`
- `form_gate_reasons`
- `exportable_item_ids`
- `item_results`

### `data/synthetic/synthetic_students.csv`

Synthetic roster for simulation only.

Fields:

- `synthetic_student_id`
- `readiness_band`
- `synthetic_course_context`
- `domain_profile_seed`

Do not include real names, emails, real school identifiers, demographic attributes, or real grades.

### `data/synthetic/synthetic_attempts.csv`

One row per synthetic student and item attempt.

Fields:

- `attempt_id`
- `synthetic_student_id`
- `assessment_id`
- `item_id`
- `selected_answer`
- `is_omitted`
- `response_time_band`
- `simulated_error_tag`

### `data/outputs/scored_attempts.csv`

Scored item-level results.

Fields:

- `attempt_id`
- `synthetic_student_id`
- `item_id`
- `domain`
- `subdomain`
- `selected_answer`
- `correct_answer`
- `is_correct`
- `score_points`
- `primary_error_tag`

### `data/outputs/domain_summary.csv`

Student-domain summaries.

Fields:

- `synthetic_student_id`
- `domain`
- `items_attempted`
- `items_correct`
- `domain_percent`
- `readiness_level`
- `priority_rank`

### `data/outputs/item_analysis.csv`

Item-level diagnostic summaries.

Fields:

- `item_id`
- `domain`
- `difficulty_band`
- `n_attempted`
- `percent_correct`
- `upper_lower_gap`
- `most_common_error_tag`
- `review_flag`

### `data/outputs/error_patterns.csv`

Misconception summaries.

Fields:

- `synthetic_student_id`
- `error_tag`
- `domain`
- `count`
- `severity`
- `recommended_remediation_module`

## Report Artifacts

- `reports/sample_student_feedback.md`
- `reports/sample_teacher_summary.md`
- `reports/sample_remediation_plan.md`
- `reports/sample_mastery_check.md`

## Identifier Policy

Use generated identifiers such as `SYN-0001`, `ITEM-001`, and `ATT-000001`. Do not use real names, emails, course IDs, Canvas IDs, school IDs, or private source-system identifiers.
