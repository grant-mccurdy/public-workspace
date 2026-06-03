# Public Release Checklist

Use this checklist before committing or publishing portfolio material from this repository.

## Content Boundary

- Use synthetic, public-domain, public-license, or permission-safe source material.
- Exclude student records, grades, submissions, rosters, parent data, personnel data, and private correspondence.
- Exclude private LMS links, course shell identifiers, internal school documents, and private screenshots.
- Exclude recruiter/contact trackers, application trackers, outreach drafts, and confidential employer material.

## Credential Boundary

- Do not commit API keys, access tokens, OAuth files, credential JSON, `.env` files, or local secret paths.
- Keep examples limited to placeholders such as `.env.example`.
- Read runtime credentials from environment variables only.

## Synthetic Data Checks

- Use fake identifiers that are clearly generated.
- Avoid names, emails, real IDs, URLs, local private paths, and private system references.
- Keep displayed aggregate groups large enough to avoid accidental re-identification.
- Document how synthetic data was generated and what private data, if any, was used only for calibration.

## Artifact Checks

- Review screenshots manually for names, emails, IDs, URLs, school names, grades, and LMS navigation context.
- Clear notebook outputs before publishing notebooks.
- Keep generated reports tied to synthetic or permission-safe data.
- Prefer reproducible scripts over manually edited output files when practical.

## Pre-Commit Commands

```bash
git status --short --untracked-files=all
rg -n --hidden --glob '!.git/**' -i '(api[_ -]?key|secret|token|password|credential|private key|bearer|sk-[A-Za-z0-9_-]{20,})' .
```

For assessment dashboard data, run:

```bash
python3 assessment-intelligence/scripts/validate_synthetic_privacy.py \
  --input path/to/assessment-dashboard.json \
  --report /tmp/synthetic-data-validation-report.md
```
