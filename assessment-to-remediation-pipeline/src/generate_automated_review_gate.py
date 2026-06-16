#!/usr/bin/env python3
"""Combine deterministic, item, and visual reviews into one automated export gate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ITEM_BANK_PATH = ROOT / "data" / "synthetic" / "item_bank.json"
DETERMINISTIC_REVIEW_PATH = ROOT / "reports" / "item-review" / "item-review.json"
GPT_ITEM_REVIEW_PATH = ROOT / "reports" / "automated-review" / "gpt-5-5-item-review.json"
GPT_VISUAL_REVIEW_PATH = ROOT / "reports" / "visual-inspection" / "gpt-5-5-visual-review.json"
OUTPUT_DIR = ROOT / "reports" / "automated-review"
JSON_OUT = OUTPUT_DIR / "automated-review.json"
MD_OUT = OUTPUT_DIR / "automated-review.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"missing": True, "path": path.relative_to(ROOT).as_posix()}
    return json.loads(path.read_text(encoding="utf-8"))


def deterministic_by_item(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["item_id"]: item for item in report.get("items", [])}


def gpt_by_item(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    review = report.get("review", {})
    return {item["item_id"]: item for item in review.get("item_reviews", [])}


def visual_gate_reasons(report: dict[str, Any]) -> list[str]:
    if report.get("missing"):
        return [f"GPT-5.5 visual review artifact is missing: {report['path']}"]
    review = report.get("review", {})
    reasons = []
    if not report.get("openai_used"):
        reasons.append("GPT-5.5 visual review API was not used.")
    if review.get("decision") in {"REVISION_REQUIRED", "BLOCKED", None}:
        reasons.append(f"GPT-5.5 visual review decision is {review.get('decision')}.")
    return reasons


def item_review_gate_reasons(report: dict[str, Any]) -> list[str]:
    if report.get("missing"):
        return [f"GPT-5.5 item review artifact is missing: {report['path']}"]
    review = report.get("review", {})
    reasons = []
    if not report.get("openai_used"):
        reasons.append("GPT-5.5 item review API was not used.")
    if review.get("decision") in {"REVISION_REQUIRED", "BLOCKED", None}:
        reasons.append(f"GPT-5.5 item review decision is {review.get('decision')}.")
    return reasons


def main() -> None:
    items = sorted(
        json.loads(ITEM_BANK_PATH.read_text(encoding="utf-8"))["items"],
        key=lambda item: (item["module"], item["position"]),
    )
    deterministic_report = load_json(DETERMINISTIC_REVIEW_PATH)
    gpt_item_report = load_json(GPT_ITEM_REVIEW_PATH)
    gpt_visual_report = load_json(GPT_VISUAL_REVIEW_PATH)
    deterministic_reviews = deterministic_by_item(deterministic_report)
    gpt_item_reviews = gpt_by_item(gpt_item_report)

    form_gate_reasons = []
    form_gate_reasons.extend(item_review_gate_reasons(gpt_item_report))
    form_gate_reasons.extend(visual_gate_reasons(gpt_visual_report))

    item_results = []
    exportable_item_ids = []
    for item in items:
        item_id = item["item_id"]
        item_reasons = []
        deterministic = deterministic_reviews.get(item_id)
        gpt_item = gpt_item_reviews.get(item_id)
        if not deterministic:
            item_reasons.append("Missing deterministic item review.")
        elif deterministic["review_decision"] != "candidate_for_automated_review":
            item_reasons.append(f"Deterministic review decision is {deterministic['review_decision']}.")
        if not gpt_item:
            item_reasons.append("Missing GPT-5.5 item review decision.")
        elif gpt_item["decision"] != "automated_pass":
            item_reasons.append(f"GPT-5.5 item review decision is {gpt_item['decision']}.")
        form_blocked = bool(form_gate_reasons)
        reasons = list(item_reasons)
        if form_blocked:
            reasons.append("Blocked by form-level automated review gate; see form_gate_reasons.")
        if not reasons:
            exportable_item_ids.append(item_id)
        item_results.append(
            {
                "item_id": item_id,
                "module": item["module"],
                "position": item["position"],
                "domain": item["domain"],
                "item_type": item["item_type"],
                "export_allowed": not reasons,
                "item_gate_reasons": item_reasons,
                "exclusion_reasons": reasons,
            }
        )

    export_allowed = not form_gate_reasons and len(exportable_item_ids) == len(items)
    report = {
        "generated_at": "not_recorded_for_reproducible_offline_review",
        "mode": "automated_gpt55_review_gate",
        "export_allowed": export_allowed,
        "gate_status": "PASS" if export_allowed else "BLOCKED",
        "total_item_count": len(items),
        "exportable_item_count": len(exportable_item_ids) if export_allowed else 0,
        "exportable_item_ids": exportable_item_ids if export_allowed else [],
        "form_gate_reasons": form_gate_reasons,
        "dependencies": {
            "deterministic_item_review": DETERMINISTIC_REVIEW_PATH.relative_to(ROOT).as_posix(),
            "gpt55_item_review": GPT_ITEM_REVIEW_PATH.relative_to(ROOT).as_posix(),
            "gpt55_visual_review": GPT_VISUAL_REVIEW_PATH.relative_to(ROOT).as_posix(),
        },
        "item_results": item_results,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    blocked_rows = "\n".join(
        "| {item_id} | M{module} Q{position} | {domain} | {item_type} | {export_allowed} | {reasons} |".format(
            reasons="; ".join(item["exclusion_reasons"]) if item["exclusion_reasons"] else "None",
            **item,
        )
        for item in item_results
    )
    MD_OUT.write_text(
        f"""# Automated Review Gate

Gate status: `{report['gate_status']}`

Export allowed: `{report['export_allowed']}`

Exportable items: `{report['exportable_item_count']}` of `{report['total_item_count']}`

## Form Gate Reasons

{chr(10).join(f'- {reason}' for reason in form_gate_reasons) if form_gate_reasons else '- None'}

## Item Gate Table

| Item | Location | Domain | Type | Export Allowed | Reasons |
| --- | --- | --- | --- | ---: | --- |
{blocked_rows}

## Safety Boundary

This gate combines deterministic checks and GPT-5.5 advisory review artifacts. It does not call Canvas, mutate LMS state, validate the assessment, or use real student data.
""",
        encoding="utf-8",
    )
    print(f"wrote {JSON_OUT.relative_to(ROOT)}")
    print(f"wrote {MD_OUT.relative_to(ROOT)}")
    if not export_allowed:
        print("Automated review gate blocked Canvas item export")


if __name__ == "__main__":
    main()
