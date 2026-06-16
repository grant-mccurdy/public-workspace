# LMS Extract Contract

## Purpose

Define the future shape of LMS-style assessment extracts without requiring live Canvas data in the MVP.

## Canvas Report Targets

Official Canvas New Quizzes reports support:

- `student_analysis`
- `item_analysis`

The MVP should simulate these report shapes later using synthetic students and attempts.

## Future Student Analysis Fields

- `synthetic_student_id`
- `assessment_id`
- `attempt_id`
- `submitted_at`
- `total_points`
- `total_possible`
- `item_id`
- `student_response`
- `is_correct`
- `points_awarded`
- `response_time_band`

## Future Item Analysis Fields

- `assessment_id`
- `item_id`
- `domain`
- `subdomain`
- `item_type`
- `n_attempted`
- `n_correct`
- `percent_correct`
- `upper_lower_gap`
- `most_common_distractor`
- `most_common_error_tag`

## Public-Safety Boundary

The simulated extract must not contain real Canvas course IDs, assignment IDs, user IDs, names, emails, rosters, grades, or private report downloads.
