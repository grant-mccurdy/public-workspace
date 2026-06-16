#!/usr/bin/env python3
"""Validate the item bank against the assessment form contract."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "data" / "synthetic" / "assessment_form_spec.json"
ITEM_BANK_PATH = ROOT / "data" / "synthetic" / "item_bank.json"

REQUIRED_FIELDS = {
    "item_id",
    "module",
    "position",
    "domain",
    "subdomain",
    "skill_statement",
    "difficulty_band",
    "item_type",
    "stem_html",
    "choices",
    "correct_answer",
    "accepted_answer_rules",
    "distractor_feedback",
    "general_feedback",
    "misconception_tags",
    "remediation_tag",
    "mastery_check_target",
    "review_status",
    "source_originality_note",
}


def fail(message: str) -> None:
    print(f"item bank validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    item_bank = json.loads(ITEM_BANK_PATH.read_text(encoding="utf-8"))
    items = item_bank["items"]

    require(len(items) == spec["timing"]["mvp_item_count"], "item count must match form spec")
    require(
        len({item["item_id"] for item in items}) == len(items),
        "item_id values must be unique",
    )

    domain_counts = Counter(item["domain"] for item in items)
    require(
        dict(domain_counts) == spec["content_domain_counts"],
        f"domain counts must match spec: {domain_counts}",
    )

    item_type_counts = Counter(item["item_type"] for item in items)
    expected_item_types = {
        "multiple_choice": spec["item_type_counts"]["multiple_choice"],
        "numeric_student_produced_response": spec["item_type_counts"][
            "numeric_student_produced_response"
        ],
    }
    require(
        dict(item_type_counts) == expected_item_types,
        f"item type counts must match spec: {item_type_counts}",
    )

    module_domain_counts: dict[int, Counter] = defaultdict(Counter)
    module_type_counts: dict[int, Counter] = defaultdict(Counter)
    module_positions: dict[int, list[int]] = defaultdict(list)

    allowed_statuses = set(spec["review_gate"]["allowed_statuses"])
    for item in items:
        missing = REQUIRED_FIELDS - set(item)
        require(not missing, f"{item.get('item_id', '<unknown>')} missing fields: {sorted(missing)}")
        require(item["review_status"] in allowed_statuses, f"{item['item_id']} has invalid review status")
        require(item["source_originality_note"], f"{item['item_id']} missing originality note")
        require(item["stem_html"].startswith("<p>"), f"{item['item_id']} stem_html should be paragraph HTML")
        require(item["difficulty_band"] in {"easy", "medium", "hard"}, f"{item['item_id']} invalid difficulty")

        module = item["module"]
        module_domain_counts[module][item["domain"]] += 1
        module_type_counts[module][item["item_type"]] += 1
        module_positions[module].append(item["position"])

        if item["item_type"] == "multiple_choice":
            choices = item["choices"]
            require(len(choices) == 4, f"{item['item_id']} must have 4 MCQ choices")
            choice_ids = [choice["choice_id"] for choice in choices]
            require(choice_ids == ["A", "B", "C", "D"], f"{item['item_id']} choices must be A-D")
            correct = [choice for choice in choices if choice["is_correct"]]
            require(len(correct) == 1, f"{item['item_id']} must have exactly 1 correct choice")
            require(correct[0]["choice_id"] == item["correct_answer"], f"{item['item_id']} correct answer mismatch")
            require(not item["accepted_answer_rules"], f"{item['item_id']} MCQ should not have numeric rules")
            wrong_ids = {choice_id for choice_id in choice_ids if choice_id != item["correct_answer"]}
            require(
                set(item["distractor_feedback"]) == wrong_ids,
                f"{item['item_id']} must include feedback for each distractor only",
            )
        elif item["item_type"] == "numeric_student_produced_response":
            require(not item["choices"], f"{item['item_id']} numeric item should not have choices")
            require(item["accepted_answer_rules"], f"{item['item_id']} numeric item needs answer rules")
            require(not item["distractor_feedback"], f"{item['item_id']} numeric item should not have distractor feedback")
        else:
            fail(f"{item['item_id']} has unsupported item_type {item['item_type']}")

    for module in spec["module_blueprints"]:
        module_id = module["module"]
        require(
            sorted(module_positions[module_id]) == list(range(1, module["items"] + 1)),
            f"module {module_id} positions must be contiguous 1-{module['items']}",
        )
        require(
            dict(module_domain_counts[module_id]) == module["domain_counts"],
            f"module {module_id} domain counts must match spec",
        )
        require(
            module_type_counts[module_id]["multiple_choice"] == module["multiple_choice"],
            f"module {module_id} MCQ count must match spec",
        )
        require(
            module_type_counts[module_id]["numeric_student_produced_response"]
            == module["numeric_student_produced_response"],
            f"module {module_id} numeric SPR count must match spec",
        )

    print("item bank validation passed")


if __name__ == "__main__":
    main()
