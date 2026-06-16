#!/usr/bin/env python3
"""Generate deterministic structure and content-risk review packet for the item bank."""

from __future__ import annotations

import csv
import html
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ITEM_BANK_PATH = ROOT / "data" / "synthetic" / "item_bank.json"
SPEC_PATH = ROOT / "data" / "synthetic" / "assessment_form_spec.json"
REPORT_DIR = ROOT / "reports" / "item-review"
JSON_OUT = REPORT_DIR / "item-review.json"
MD_OUT = REPORT_DIR / "item-review.md"
CSV_OUT = REPORT_DIR / "item-review.csv"


CURATED_FINDINGS: dict[str, dict[str, Any]] = {}


FORM_LEVEL_FINDINGS = [
    {
        "severity": "minor",
        "finding": "Problem-Solving and Data Analysis coverage is public-safe and coherent, but the 5-item MVP does not yet include scatterplots, statistical claims, sampling, or margin-of-error style evidence.",
        "recommended_action": "Before Canvas export, consider swapping one direct percent/rate item for a data display or statistical-claim interpretation item.",
    },
    {
        "severity": "info",
        "finding": "Geometry and Trigonometry now includes right-triangle trigonometry, but the 5-item MVP still has no explicit circle item.",
        "recommended_action": "Before a larger release, consider adding a circle problem if preserving the full public SAT Math domain spread is a priority.",
    },
    {
        "severity": "info",
        "finding": "Several stems use plain-text notation such as sqrt(...) and x^2. This is acceptable for a first static preview but should be revisited before polished publication or Canvas export.",
        "recommended_action": "Add a later notation-rendering pass for exponent and radical readability if the item bank is used as a portfolio artifact.",
    },
]


def strip_tags(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()


def load_data() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    item_bank = json.loads(ITEM_BANK_PATH.read_text(encoding="utf-8"))
    return spec, item_bank["items"]


def default_review(item: dict[str, Any]) -> dict[str, Any]:
    findings = []
    recommended_action = "Proceed to automated GPT-5.5 item review; do not export until the automated gate passes."
    severity = "info"
    decision = "candidate_for_automated_review"

    if item["item_type"] == "multiple_choice":
        correct_choices = [choice for choice in item["choices"] if choice["is_correct"]]
        if len(correct_choices) != 1:
            decision = "revise_before_export"
            severity = "major"
            findings.append("Multiple-choice item does not have exactly one correct choice.")
            recommended_action = "Fix the answer-key structure before automated review."
        if set(item["distractor_feedback"]) != {
            choice["choice_id"] for choice in item["choices"] if not choice["is_correct"]
        }:
            decision = "revise_before_export"
            severity = "major"
            findings.append("Distractor feedback does not match the incorrect choices.")
            recommended_action = "Align feedback with every distractor before automated review."
    else:
        if not item["accepted_answer_rules"]:
            decision = "revise_before_export"
            severity = "major"
            findings.append("Numeric item is missing accepted answer rules.")
            recommended_action = "Add exact, equivalent, range, or tolerance-based answer rules."

    if not findings:
        findings.append("No deterministic math/content issue flagged in this review pass.")

    return {
        "item_id": item["item_id"],
        "module": item["module"],
        "position": item["position"],
        "domain": item["domain"],
        "subdomain": item["subdomain"],
        "item_type": item["item_type"],
        "difficulty_band": item["difficulty_band"],
        "review_status": item["review_status"],
        "review_decision": decision,
        "severity": severity,
        "stem_text": strip_tags(item["stem_html"]),
        "correct_answer": item["correct_answer"],
        "findings": findings,
        "recommended_action": recommended_action,
    }


def review_item(item: dict[str, Any]) -> dict[str, Any]:
    review = default_review(item)
    curated = CURATED_FINDINGS.get(item["item_id"])
    if curated:
        review["review_decision"] = curated["review_decision"]
        review["severity"] = curated["severity"]
        review["findings"] = curated["findings"]
        review["recommended_action"] = curated["recommended_action"]
    return review


def render_markdown(spec: dict[str, Any], reviews: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    rows = "\n".join(
        "| {item_id} | M{module} Q{position} | {domain} | {difficulty_band} | {review_decision} | {severity} |".format(
            **review
        )
        for review in reviews
    )
    flagged = [review for review in reviews if review["review_decision"] != "candidate_for_automated_review"]
    flagged_sections = []
    for review in flagged:
        findings = "\n".join(f"- {finding}" for finding in review["findings"])
        flagged_sections.append(
            f"""### {review['item_id']} - {review['review_decision']}

- location: Module {review['module']}, Question {review['position']}
- domain: {review['domain']}
- difficulty: `{review['difficulty_band']}`
- stem: {review['stem_text']}
- correct answer: `{review['correct_answer']}`

Findings:

{findings}

Recommended action: {review['recommended_action']}
"""
        )
    form_findings = "\n".join(
        f"- `{item['severity']}`: {item['finding']} Action: {item['recommended_action']}"
        for item in FORM_LEVEL_FINDINGS
    )
    return f"""# Item Review Packet

Assessment: `{spec['title']}`

Review mode: deterministic structure checks plus conservative math/content risk notes.

Gate boundary: this packet does not approve items. Items require automated GPT-5.5 item review plus visual review before Canvas export.

## Summary

- total items: `{summary['total_items']}`
- candidate for automated review: `{summary['decision_counts'].get('candidate_for_automated_review', 0)}`
- polish before export: `{summary['decision_counts'].get('polish_before_export', 0)}`
- revise before export: `{summary['decision_counts'].get('revise_before_export', 0)}`
- major findings: `{summary['severity_counts'].get('major', 0)}`
- minor findings: `{summary['severity_counts'].get('minor', 0)}`
- current source items marked approved: `{summary['review_status_counts'].get('approved', 0)}`

## Form-Level Findings

{form_findings}

## Item Decision Table

| Item | Location | Domain | Difficulty | Review Decision | Severity |
| --- | --- | --- | --- | --- | --- |
{rows}

## Flagged Items

{chr(10).join(flagged_sections) if flagged_sections else 'No items flagged beyond deterministic review requirements.'}

## Safety Boundary

This report uses original public-safe draft items only. It does not use real student data, Canvas exports, private school records, credentials, or live APIs. It does not allow Canvas export by itself.
"""


def write_csv(reviews: list[dict[str, Any]]) -> None:
    fields = [
        "item_id",
        "module",
        "position",
        "domain",
        "subdomain",
        "item_type",
        "difficulty_band",
        "review_status",
        "review_decision",
        "severity",
        "correct_answer",
        "recommended_action",
    ]
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for review in reviews:
            writer.writerow({field: review[field] for field in fields})


def main() -> None:
    spec, items = load_data()
    reviews = [review_item(item) for item in sorted(items, key=lambda value: (value["module"], value["position"]))]
    summary = {
        "total_items": len(reviews),
        "decision_counts": dict(Counter(review["review_decision"] for review in reviews)),
        "severity_counts": dict(Counter(review["severity"] for review in reviews)),
        "review_status_counts": dict(Counter(review["review_status"] for review in reviews)),
        "form_level_findings": FORM_LEVEL_FINDINGS,
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(
        json.dumps({"assessment_id": spec["assessment_id"], "summary": summary, "items": reviews}, indent=2) + "\n",
        encoding="utf-8",
    )
    MD_OUT.write_text(render_markdown(spec, reviews, summary), encoding="utf-8")
    write_csv(reviews)
    print(f"wrote {MD_OUT.relative_to(ROOT)}")
    print(f"wrote {JSON_OUT.relative_to(ROOT)}")
    print(f"wrote {CSV_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
