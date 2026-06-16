# Assessment Blueprint

## Diagnostic Framing

Working title: SAT Math Readiness Diagnostic Prototype

Permitted framing:

- standards-aligned diagnostic,
- math readiness diagnostic,
- predictive-validity prototype,
- assessment-to-remediation pipeline,
- learning evidence to instructional action workflow.

Avoid:

- validated standardized test,
- SAT/ACT/AP replacement,
- official placement test,
- commercial benchmark.

## Design Constraints

- Use original items only.
- Align to public SAT Math skill domains and format patterns, not copied commercial item content.
- Use clear item metadata so scoring and remediation can be audited.
- Include enough domain coverage for diagnostic interpretation, not high-stakes decisions.
- Label all students and attempts as synthetic.
- Use official College Board source pages for target-assessment research.

## MVP Domain Blueprint

The 36-item form scales the current SAT Math structure from 44 questions in 70 minutes to 36 questions in 60 minutes. SAT Math has four public content domains. The MVP preserves the relative weighting while keeping two equal 18-item modules.

| Domain | Items | Evidence Target | Example Subskills | Example Error Tags |
| --- | ---: | --- | --- | --- |
| Algebra | 13 | Analyze, solve, and create linear equations, inequalities, functions, and systems | one-variable equations, two-variable equations, linear functions, systems, inequalities | inverse-operation error, sign error, slope-intercept confusion |
| Advanced Math | 13 | Work with nonlinear expressions, equations, and functions needed for further STEM study | equivalent expressions, quadratics, exponentials, rational/radical equations, nonlinear functions | exponent-rule error, factoring error, function-notation error |
| Problem-Solving and Data Analysis | 5 | Apply quantitative reasoning to rates, percentages, data, probability, and claims | ratios, unit rates, percent change, scatterplots, probability, margin of error | percent-base error, unit-rate error, association-causation confusion |
| Geometry and Trigonometry | 5 | Solve geometry, measurement, triangle, trigonometry, and circle problems | area, volume, lines, angles, triangles, right-triangle trig, circles | formula selection error, scale-factor error, trig-ratio error |

Total: 36 items.

## Form Shape

| Module | Time | Items | MCQ | Numeric SPR |
| --- | ---: | ---: | ---: | ---: |
| Module 1 | 30 minutes | 18 | 14 | 4 |
| Module 2 | 30 minutes | 18 | 13 | 5 |

The MVP is non-adaptive. Each module should contain a broad mix of easy, medium, and hard items ordered from easier to harder.

## Format Rules

- MCQ items must have exactly 4 answer choices.
- MCQ items must have exactly 1 correct answer and 3 distractors.
- Every MCQ distractor must include answer-specific feedback tied to a misconception or error pattern.
- Numeric student-produced response items must include accepted answer rules, such as exact values, equivalent fractions/decimals, ranges, or tolerance.
- Rubric fields are reserved for future constructed-response extensions; they are not required for the v1 SAT-like form.

## Item Metadata Fields

Each item should eventually include:

- `item_id`
- `domain`
- `subdomain`
- `skill_statement`
- `difficulty_band`
- `question_text`
- `item_type`
- `answer_choices`
- `correct_answer`
- `accepted_answer_rules`
- `rationale`
- `distractor_feedback`
- `primary_error_tag`
- `secondary_error_tags`
- `remediation_target`
- `mastery_check_target`
- `review_status`
- `source_originality_note`

## Mastery Evidence

The mastery check should be shorter than the diagnostic and targeted to the highest-priority remediation skills. It should show whether feedback and practice shifted performance on related, original items.
