# MVP Scope

## Goal

Create a static, reproducible demo that turns official-source SAT Math correlation research into an original one-hour diagnostic form, then prepares the architecture for later synthetic attempts, LMS-style extracts, feedback, remediation, and mastery evidence.

## Included

- Official-source SAT Math research summary.
- Assessment creation parameters.
- 36-item original math-readiness diagnostic blueprint scaled to one hour.
- Four SAT Math-correlated domains with subdomain skill targets.
- Two 30-minute modules with 18 items each.
- 27 four-option MCQ items and 9 numeric student-produced response items.
- HTML preview and instructor-review artifacts.
- Automated GPT-5.5 item and visual review gate before Canvas export.
- Offline Canvas New Quizzes payload and dry-run manifest.
- Answer key, scoring rules, and domain-level score summaries.
- Item difficulty and discrimination summaries.
- Error-pattern or misconception tags.
- Student-facing feedback report.
- Teacher-facing summary report.
- Targeted remediation plan.
- Sample mastery-check blueprint and sample result.
- Public-safe README, methodology docs, and case-study draft.

## Excluded From MVP

- Real student records.
- Private gradebooks or LMS exports.
- Canvas API integration.
- Live Canvas quiz creation.
- Live OpenAI or other AI API calls.
- Gmail, Google Drive, or Google Calendar APIs.
- Supabase, hosted databases, or OAuth.
- Browser automation or Playwright.
- Claims of standardized-test validation.
- Commercial test item copying or close paraphrasing.

## Suggested Local Workflow

```text
make all
-> validate official-source research docs
-> validate assessment form contract
-> validate item bank metadata
-> render HTML previews
-> validate automated-review flags
-> export Canvas New Quizzes dry-run payloads
-> run public-safety checks
```

## Proposed MVP Files

```text
src/
  validate_architecture_contract.py
  render_assessment_preview.py
  export_canvas_new_quizzes_payload.py
  generate_synthetic_attempts.py
  score_assessment.py
  analyze_results.py
  generate_feedback.py
  generate_remediation.py
  export_reports.py
data/
  synthetic/
  outputs/
reports/
  sample_student_feedback.md
  sample_teacher_summary.md
  sample_remediation_plan.md
tests/
Makefile
```

## Deferred Extensions

- Static dashboard.
- GitHub Pages case-study integration.
- Canvas import/export adapter.
- Live Canvas sandbox loading.
- AI-assisted remediation drafting layer with public-safe review controls.
- Longitudinal mastery evidence across multiple attempts.
- Predictive-validity simulation or validation study using synthetic outcomes.
