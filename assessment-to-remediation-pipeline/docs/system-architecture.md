# System Architecture

## Architecture Principle

Keep the first version deterministic, local, and inspectable. Every generated artifact should be reproducible from repository code and public-safe synthetic inputs.

## Pipeline

```text
docs/research/sat-math-correlation-target.md
-> docs/assessment-creation-parameters.md
-> data/synthetic/assessment_form_spec.json
-> data/synthetic/item_bank.json
-> previews/student_form.html
-> previews/instructor_review.html
-> reports/automated-review/automated-review.json
-> data/outputs/canvas_new_quiz_payload.json
-> data/outputs/canvas_upload_manifest.json
-> data/synthetic/synthetic_attempts.csv
-> data/outputs/scored_attempts.csv
-> data/outputs/domain_summary.csv
-> data/outputs/item_analysis.csv
-> data/outputs/error_patterns.csv
-> reports/sample_student_feedback.md
-> reports/sample_teacher_summary.md
-> reports/sample_remediation_plan.md
```

## Modules

### Research And Parameterization

Documents the SAT Math correlation target from official College Board sources and Canvas compatibility from official Instructure sources. This layer produces the assessment creation parameters and the one-hour form contract.

### Blueprint Generation

Creates a structured representation of domains, subdomains, item metadata, skill targets, correct answers, and misconception tags. Item content must be original and must not copy commercial assessment items.

### Preview And Automated Review

Renders static student and instructor HTML previews. The instructor preview shows item metadata, answer keys, distractor feedback, numeric accepted-answer rules, and public-safety flags. The automated review gate combines deterministic checks, GPT-5.5 item review, and GPT-5.5 visual review. Only gate-passing items are eligible for offline Canvas export.

### Canvas Offline Export

Generates Canvas New Quizzes API payload artifacts and a dry-run upload manifest. The MVP does not call Canvas. Live LMS mutation is a later adapter that must require local credentials outside Git.

### Synthetic Attempt Generation

Creates synthetic student profiles and response patterns. The generator should simulate latent readiness, domain strengths, misconception tendencies, nonresponse behavior, and reassessment improvement without using real records.

### Scoring

Scores each attempt at the item, domain, and overall levels. The scoring layer should keep raw responses, correct answers, item metadata, and score outputs separate enough to audit.

### Analysis

Computes item difficulty, domain performance, discrimination-like summaries, misconception frequencies, and subgroup-free aggregate decision-support views. Any group fields in MVP should be synthetic instructional groupings, not real demographic attributes.

### Feedback Generation

Exports student-facing Markdown that explains strengths, priority skills, likely error patterns, and next remediation actions in concise language.

### Remediation Generation

Maps domain and error-pattern evidence to short practice modules, worked examples, and mastery-check prompts. MVP remediation can be template-driven without live AI calls.

### Reporting

Exports teacher-facing and portfolio-facing summaries that show how evidence moves to instructional action.

## External Dependencies

MVP target: Python standard library only.

Deferred optional dependencies:

- pandas for richer tabular analysis,
- DuckDB for warehouse-style reporting,
- static HTML dashboard tooling,
- live Canvas sandbox adapter,
- AI-assisted artifact drafting with public-safe review controls.

## Public Portfolio Relationship

This project should remain a focused capstone. It can reference sibling portfolio projects as related systems, but the MVP should run independently.
