# Validation Plan

## Validation Goals

The MVP should prove that the pipeline is reproducible, public-safe, internally coherent, and clear enough for portfolio review.

## MVP Checks

### Reproducibility

- `make all` rebuilds synthetic data, scoring outputs, analysis outputs, and sample reports.
- Outputs are deterministic when a fixed random seed is used.
- Default commands do not require private files, credentials, live APIs, or network access. Browser automation is local-only for preview inspection.

### Architecture Contract

- The form spec contains 36 items.
- The form spec contains 2 modules with 18 items each.
- The form spec contains 27 MCQ items and 9 numeric student-produced response items.
- Domain counts are Algebra 13, Advanced Math 13, Problem-Solving and Data Analysis 5, and Geometry and Trigonometry 5.
- The scaled timing is 60 minutes total.
- The Canvas boundary is offline-first with no live API calls in MVP.

### Data Integrity

- Every attempt references a known synthetic student and item.
- Every item belongs to one blueprint domain and subdomain.
- Scores stay within expected bounds.
- Domain summaries reconcile to item-level scored attempts.
- Error-pattern counts reconcile to incorrect or omitted responses.

### Item Analysis

- Item difficulty is calculated from synthetic attempts.
- Upper/lower performance gap is calculated from synthetic overall score bands.
- Items with extreme synthetic behavior are flagged for review.
- The project avoids making psychometric claims beyond the prototype evidence.

### Public Safety

- No `.env` file is required.
- No credentials, tokens, or API keys are present.
- No real names, emails, rosters, grades, submissions, or Canvas exports are present.
- All data files are synthetic and clearly labeled.
- Assessment content is original.
- Canvas payload artifacts contain no live course IDs, assignment IDs, user IDs, URLs, access tokens, or credentials.

### Report Quality

- Student feedback names strengths, priority skills, and next actions.
- Teacher summary identifies domain patterns and common misconceptions.
- Remediation plan maps evidence to practice modules and mastery checks.
- Public case-study text uses concise, supportable claims.

### Item Review

- Item review packet is generated from the canonical item bank.
- Review packet identifies items that are candidates for automated review, need polish, or need revision before export.
- Review packet does not allow Canvas export by itself.
- Form-level findings call out SAT-correlation coverage gaps without making validation claims.

### Automated GPT-5.5 Review Gate

- GPT-5.5 item review prompt/report generation runs in dry-run mode without network access.
- API-backed GPT-5.5 item review is optional and required only for a passing automated gate.
- GPT-5.5 item review evaluates math correctness, item clarity, distractor plausibility, distractor-feedback specificity, and public-safety concerns.
- Automated gate output identifies exportable and excluded items with explicit reasons.
- Dry-run artifacts intentionally block Canvas item export.

### Visual Inspection

- Static student and instructor previews render locally.
- Desktop and mobile screenshots are captured for each preview.
- Visual inspection verifies headings, expected markers, item count, module count, nonblank body text, and horizontal overflow.
- GPT-5.5 visual-review prompt/report generation runs in dry-run mode without network access.
- API-backed GPT-5.5 visual review is optional and required only for a passing automated gate.

## Suggested Commands

Initial placeholder checks:

```bash
git status --short --branch
find assessment-to-remediation-pipeline -maxdepth 3 -type f | sort
python3 assessment-to-remediation-pipeline/src/validate_architecture_contract.py
python3 assessment-to-remediation-pipeline/src/validate_item_bank.py
python3 assessment-to-remediation-pipeline/scripts/gpt55_item_review.py
python3 assessment-to-remediation-pipeline/src/generate_automated_review_gate.py
rg -n --hidden --glob '!.git/**' -i '(api[_ -]?key|secret|token|password|credential|private key|bearer|sk-[A-Za-z0-9_-]{20,})' assessment-to-remediation-pipeline
```

Future MVP check:

```bash
make all
python -m pytest
```

## Acceptance Criteria For First Implemented Version

- Generates a 36-item blueprint.
- Generates at least 100 synthetic students.
- Scores item and domain performance.
- Produces item analysis and error-pattern summaries.
- Produces at least one student feedback sample, teacher summary, remediation plan, and mastery-check artifact.
- Passes public-safety review.
