# SAT Math Correlation Target

## Source Policy

Use official College Board SAT Suite pages for target-assessment research. Do not rely on prep-site summaries as source of truth, and do not copy or paraphrase official SAT items.

Primary sources:

- [How the SAT Is Structured](https://satsuite.collegeboard.org/sat/whats-on-the-test/structure)
- [The Math Section: Overview](https://satsuite.collegeboard.org/sat/whats-on-the-test/math/overview)
- [Types of Math Tested](https://satsuite.collegeboard.org/sat/whats-on-the-test/math/types)
- [Student-Produced Responses](https://satsuite.collegeboard.org/sat/whats-on-the-test/math/student-produced)

## Target Assessment Facts

Current SAT Math uses:

- 70 minutes.
- 44 questions.
- Two equal-length modules.
- Mostly multiple-choice questions.
- Some student-produced response questions.
- Four public content domains:
  - Algebra.
  - Advanced Math.
  - Problem-Solving and Data Analysis.
  - Geometry and Trigonometry.

College Board describes Math domain counts across a full SAT Math section as:

| Domain | Full SAT Math Count |
| --- | ---: |
| Algebra | 13-15 |
| Advanced Math | 13-15 |
| Problem-Solving and Data Analysis | 5-7 |
| Geometry and Trigonometry | 5-7 |

College Board also describes approximately 75% of SAT Math questions as 4-option multiple choice, with the remaining questions using student-produced response format.

## One-Hour Scaling Decision

SAT Math timing ratio:

```text
44 questions / 70 minutes = 0.6286 questions per minute
60 minutes * 0.6286 = 37.7 questions
```

The MVP uses 36 questions instead of 38 to keep:

- two equal 18-item modules,
- a clean 27 MCQ / 9 numeric SPR split,
- slightly more time per item for a diagnostic setting,
- stable domain counts aligned to the official domain hierarchy.

## MVP Form Contract

| Feature | MVP Decision |
| --- | --- |
| Total time | 60 minutes |
| Modules | 2 |
| Module length | 30 minutes |
| Items per module | 18 |
| Total items | 36 |
| Multiple choice | 27 |
| Numeric student-produced response | 9 |
| Adaptivity | Deferred; v1 is non-adaptive |
| Calculator policy | Calculator-permitted by default; item metadata can flag no-calculator intent for local review |

## Language Boundary

Use:

- SAT Math-correlated readiness diagnostic,
- SAT Math readiness diagnostic prototype,
- one-hour internal math readiness diagnostic,
- assessment-to-remediation pipeline.

Avoid:

- SAT clone,
- official SAT practice test,
- validated SAT predictor,
- standardized admissions test.
