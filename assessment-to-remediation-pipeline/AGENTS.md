# AGENTS.md

## Project Purpose

This project is a public-safe portfolio capstone showing how assessment design, synthetic education data workflows, statistical analysis, feedback, remediation, and mastery evidence can connect into one instructional workflow.

Position the project as:

- a standards-aligned diagnostic prototype,
- an assessment-to-remediation pipeline,
- a learning-evidence to instructional-action workflow,
- a reproducible education data and reporting demo.

Do not describe it as a validated standardized test.

## Public / Private Boundary

Allowed:

- synthetic students,
- synthetic attempts,
- original math-readiness items,
- public skill-domain descriptions,
- reproducible scoring and analysis scripts,
- Markdown, CSV, JSON, and static report outputs,
- public-safe documentation and screenshots.

Not allowed:

- real student, parent, personnel, or teacher records,
- real names, rosters, emails, grades, submissions, or Canvas exports,
- school-private documents or employer-confidential materials,
- copied commercial test items,
- API keys, OAuth tokens, credentials, or hidden `.env` dependencies,
- claims that the diagnostic is validated without validation evidence.

## Default Workflow

```text
inspect -> plan -> build -> verify -> summarize -> recommend next portfolio-improving action
```

## MVP Technical Rules

- Use Python standard-library scripts first.
- Prefer CSV, JSON, and Markdown artifacts.
- Keep the pipeline runnable locally without Canvas, OpenAI, Google APIs, Supabase, browser automation, or Playwright.
- Treat live Canvas/LMS calls, hosted databases, dashboards, and live AI generation as later adapters.
- Canvas New Quizzes support starts as offline payload/export generation only.
- Keep item content original and aligned to public skill domains only.
- Use official College Board sources for SAT Math correlation research and official Instructure/Canvas sources for Canvas compatibility.

## Documentation Standard

Planning docs should be concise, measurable, and public-safe. Public case-study writing should emphasize the problem solved, system design, tools, outputs, value, and lessons learned without private workplace details or unsupported claims.
