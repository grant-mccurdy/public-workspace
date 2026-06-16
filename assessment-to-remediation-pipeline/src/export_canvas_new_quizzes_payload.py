#!/usr/bin/env python3
"""Export offline Canvas New Quizzes payload and dry-run manifest artifacts."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "data" / "synthetic" / "assessment_form_spec.json"
ITEM_BANK_PATH = ROOT / "data" / "synthetic" / "item_bank.json"
AUTOMATED_GATE_PATH = ROOT / "reports" / "automated-review" / "automated-review.json"
OUTPUT_DIR = ROOT / "data" / "outputs"
PAYLOAD_PATH = OUTPUT_DIR / "canvas_new_quiz_payload.json"
MANIFEST_PATH = OUTPUT_DIR / "canvas_upload_manifest.json"


def load_data() -> tuple[dict, list[dict]]:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    items = json.loads(ITEM_BANK_PATH.read_text(encoding="utf-8"))["items"]
    return spec, sorted(items, key=lambda item: (item["module"], item["position"]))


def load_gate() -> dict:
    if not AUTOMATED_GATE_PATH.exists():
        return {
            "export_allowed": False,
            "gate_status": "MISSING",
            "exportable_item_ids": [],
            "form_gate_reasons": ["Automated review gate artifact is missing."],
            "item_results": [],
        }
    return json.loads(AUTOMATED_GATE_PATH.read_text(encoding="utf-8"))


def choice_item(item: dict) -> dict:
    return {
        "position": item["position"],
        "points_possible": 1,
        "entry_type": "Item",
        "entry": {
            "title": item["item_id"],
            "item_body": item["stem_html"],
            "interaction_type_slug": "choice",
            "interaction_data": {
                "choices": [
                    {
                        "id": f"{item['item_id']}-{choice['choice_id']}",
                        "position": index + 1,
                        "item_body": choice["html"],
                    }
                    for index, choice in enumerate(item["choices"])
                ]
            },
            "scoring_data": {
                "value": f"{item['item_id']}-{item['correct_answer']}",
            },
            "feedback": {
                "neutral": item["general_feedback"],
                "answer_feedback": {
                    f"{item['item_id']}-{choice_id}": feedback
                    for choice_id, feedback in item["distractor_feedback"].items()
                },
            },
            "properties": {
                "domain": item["domain"],
                "subdomain": item["subdomain"],
                "difficulty_band": item["difficulty_band"],
                "remediation_tag": item["remediation_tag"],
            },
        },
    }


def numeric_item(item: dict) -> dict:
    return {
        "position": item["position"],
        "points_possible": 1,
        "entry_type": "Item",
        "entry": {
            "title": item["item_id"],
            "item_body": item["stem_html"],
            "interaction_type_slug": "numeric",
            "interaction_data": {
                "accepted_answer_rules": item["accepted_answer_rules"],
            },
            "scoring_data": {
                "value": item["correct_answer"],
                "accepted_answer_rules": item["accepted_answer_rules"],
            },
            "feedback": {
                "neutral": item["general_feedback"],
            },
            "properties": {
                "domain": item["domain"],
                "subdomain": item["subdomain"],
                "difficulty_band": item["difficulty_band"],
                "remediation_tag": item["remediation_tag"],
            },
        },
    }


def to_canvas_item(item: dict) -> dict:
    if item["item_type"] == "multiple_choice":
        return choice_item(item)
    if item["item_type"] == "numeric_student_produced_response":
        return numeric_item(item)
    raise ValueError(f"unsupported item type: {item['item_type']}")


def main() -> None:
    spec, items = load_data()
    gate = load_gate()
    item_gate = {item["item_id"]: item for item in gate.get("item_results", [])}
    exportable_ids = set(gate.get("exportable_item_ids", [])) if gate.get("export_allowed") else set()
    exportable_items = [item for item in items if item["item_id"] in exportable_ids]
    excluded_items = []
    for item in items:
        if item["item_id"] in exportable_ids:
            continue
        gate_result = item_gate.get(item["item_id"], {})
        excluded_items.append(
            {
                "item_id": item["item_id"],
                "review_status": item["review_status"],
                "reason": "excluded by automated review gate",
                "gate_reasons": gate_result.get("exclusion_reasons")
                or gate.get("form_gate_reasons")
                or ["Automated review gate did not allow export."],
            }
        )

    payload = {
        "mode": "offline_payload_only",
        "live_api_calls_allowed": False,
        "automated_review_gate": {
            "gate_status": gate.get("gate_status"),
            "export_allowed": gate.get("export_allowed"),
            "source": AUTOMATED_GATE_PATH.relative_to(ROOT).as_posix(),
        },
        "quiz": {
            "title": spec["title"],
            "instructions": (
                "Original SAT Math-correlated readiness diagnostic prototype. "
                "Offline payload artifact only; do not treat as a live Canvas upload."
            ),
            "time_limit": spec["timing"]["total_minutes"],
            "quiz_settings": {
                "shuffle_questions": False,
                "shuffle_answers": False,
                "one_question_at_a_time": False,
            },
        },
        "items": [to_canvas_item(item) for item in exportable_items],
    }

    manifest = {
        "export_timestamp_utc": "not_recorded_for_reproducible_offline_dry_run",
        "assessment_id": spec["assessment_id"],
        "assessment_version": spec["version"],
        "live_upload_status": "not_attempted",
        "public_safety_status": "offline artifact contains no credentials or live Canvas identifiers",
        "automated_gate_status": gate.get("gate_status"),
        "automated_export_allowed": gate.get("export_allowed"),
        "form_gate_reasons": gate.get("form_gate_reasons", []),
        "exportable_item_count": len(exportable_items),
        "excluded_item_count": len(excluded_items),
        "total_item_count": len(items),
        "domain_counts": dict(Counter(item["domain"] for item in items)),
        "item_type_counts": dict(Counter(item["item_type"] for item in items)),
        "excluded_items": excluded_items,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PAYLOAD_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {PAYLOAD_PATH.relative_to(ROOT)}")
    print(f"wrote {MANIFEST_PATH.relative_to(ROOT)}")
    if excluded_items:
        print(f"Canvas item export gated: {len(excluded_items)} items excluded by automated review gate")


if __name__ == "__main__":
    main()
