# Canvas New Quizzes Compatibility

## Source Policy

Use official Instructure Canvas LMS API documentation for compatibility decisions:

- [New Quizzes API](https://canvas.instructure.com/doc/api/new_quizzes.html)
- [New Quiz Items API](https://canvas.instructure.com/doc/api/new_quiz_items.html)
- [New Quizzes Reports API](https://canvas.instructure.com/doc/api/new_quizzes_reports.html)

## MVP Boundary

The MVP is offline-first. It should generate local payload artifacts and dry-run manifests only. It must not create, update, publish, or mutate a live Canvas course.

## Supported MVP Item Types

| Diagnostic Format | Canvas New Quiz Item Type |
| --- | --- |
| Four-option MCQ | `choice` |
| Numeric student-produced response | `numeric` |

The New Quiz Items API also supports other question types, including `essay`, but essay-style constructed response is deferred because the SAT Math-correlated MVP uses MCQ and numeric SPR.

## Payload Requirements

New Quiz payload artifacts should include:

- quiz title,
- instructions,
- total points,
- grading type,
- time limit,
- result-view settings,
- item positions,
- item bodies,
- interaction type,
- interaction data,
- scoring data,
- feedback,
- answer feedback for MCQ distractors.

## Prohibited In Public Artifacts

- Canvas base URLs.
- Course IDs.
- Assignment IDs.
- User IDs.
- Access tokens.
- OAuth credentials.
- Real LMS report downloads.
- Private Canvas export files.

## Later Live Adapter

A future live adapter may use local environment variables or local config files outside Git. It must support dry-run mode first and should require an explicit confirmation before creating or updating a quiz.
