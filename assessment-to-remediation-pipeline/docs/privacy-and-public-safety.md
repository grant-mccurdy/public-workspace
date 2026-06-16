# Privacy and Public Safety

## Public-Safe Boundary

This project is intended for public portfolio use. It must be safe to publish, clone, inspect, and run without access to private systems.

## Required Constraints

- Synthetic students only.
- No real names.
- No real school records.
- No real grades.
- No internal school exports.
- No private Canvas exports.
- No parent, student, personnel, or teacher-private data.
- No credentials, tokens, OAuth files, or API keys.
- No hidden `.env` dependency.
- No copied assessment items from SAT, ACT, AP, state exams, commercial publishers, or school-private materials.
- No claim that the diagnostic is validated unless future work demonstrates validation evidence.
- No live Canvas course IDs, assignment IDs, user IDs, URLs, or access tokens in public files.

## Permitted Data

- Generated synthetic student identifiers.
- Generated synthetic response data.
- Original math items written for this demo.
- Public skill-domain descriptions.
- Official-source research summaries with citations.
- Offline Canvas payload shapes without credentials or live identifiers.
- Aggregate synthetic summaries.
- Public-safe Markdown, CSV, JSON, and static report outputs.

## Language Rules

Use:

- standards-aligned diagnostic,
- internal math readiness diagnostic,
- predictive-validity prototype,
- assessment-to-remediation pipeline,
- learning evidence to instructional action workflow.

Avoid:

- validated standardized test,
- official placement test,
- proprietary benchmark,
- automatic teacher replacement,
- unsupported claims of predictive accuracy.

## Release Review Checklist

Before any commit, PR, or publication:

- Run `git status --short --branch`.
- Review changed files by category.
- Run the project validation command once it exists.
- Search for credential terms.
- Search for private-path and student-data terms.
- Confirm every dataset is synthetic.
- Confirm generated reports do not contain private names, emails, IDs, or school-private references.
- Confirm assessment items are original.
- Confirm public-facing claims match evidence.

## Later AI-Assisted Layer

If a future version uses AI to draft feedback or remediation text, it must remain public-safe, reviewable, and clearly labeled as AI-assisted. The default MVP workflow should not require live AI calls; optional API-backed review gates must keep credentials outside Git.
