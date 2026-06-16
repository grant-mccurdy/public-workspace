#!/usr/bin/env python3
"""Validate the committed public artifact set without regenerating outputs."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = ROOT / "reports" / "automated-review" / "automated-review.json"
ITEM_REVIEW_PATH = ROOT / "reports" / "automated-review" / "gpt-5-5-item-review.json"
VISUAL_REVIEW_PATH = ROOT / "reports" / "visual-inspection" / "gpt-5-5-visual-review.json"
PAYLOAD_PATH = ROOT / "data" / "outputs" / "canvas_new_quiz_payload.json"
MANIFEST_PATH = ROOT / "data" / "outputs" / "canvas_upload_manifest.json"
ITEM_BANK_PATH = ROOT / "data" / "synthetic" / "item_bank.json"


def fail(message: str) -> None:
    raise SystemExit(f"public artifact validation failed: {message}")


def load_json(path: Path) -> dict:
    if not path.exists():
        fail(f"missing artifact: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    item_bank = load_json(ITEM_BANK_PATH)
    gate = load_json(GATE_PATH)
    item_review = load_json(ITEM_REVIEW_PATH)
    visual_review = load_json(VISUAL_REVIEW_PATH)
    payload = load_json(PAYLOAD_PATH)
    manifest = load_json(MANIFEST_PATH)

    total_items = len(item_bank.get("items", []))
    if total_items != 36:
        fail(f"expected 36 item-bank items, found {total_items}")

    if gate.get("gate_status") != "PASS" or gate.get("export_allowed") is not True:
        fail("automated review gate is not passing")
    if gate.get("exportable_item_count") != total_items:
        fail("automated review gate does not export all item-bank items")

    item_review_body = item_review.get("review", {})
    if item_review.get("openai_used") is not True:
        fail("GPT-5.5 item review artifact is not API-backed")
    if item_review_body.get("decision") not in {"APPROVED", "POLISH_RECOMMENDED"}:
        fail(f"unexpected item-review decision: {item_review_body.get('decision')}")
    if item_review_body.get("export_allowed") is not True:
        fail("GPT-5.5 item review does not allow export")

    visual_review_body = visual_review.get("review", {})
    if visual_review.get("openai_used") is not True:
        fail("GPT-5.5 visual review artifact is not API-backed")
    if visual_review_body.get("decision") not in {"APPROVED", "POLISH_RECOMMENDED"}:
        fail(f"unexpected visual-review decision: {visual_review_body.get('decision')}")

    payload_items = payload.get("items", [])
    excluded_items = manifest.get("excluded_items", [])
    if len(payload_items) != total_items:
        fail(f"expected {total_items} Canvas payload items, found {len(payload_items)}")
    if excluded_items:
        fail(f"expected 0 excluded items, found {len(excluded_items)}")

    if payload.get("live_api_calls_allowed") is not False:
        fail("Canvas payload does not explicitly block live API calls")
    if manifest.get("live_upload_status") != "not_attempted":
        fail("Canvas upload manifest should remain a dry-run artifact")

    print("public artifact validation passed")
    print(f"- item-bank items: {total_items}")
    print(f"- automated gate: {gate['gate_status']}")
    print(f"- Canvas payload items: {len(payload_items)}")
    print(f"- excluded items: {len(excluded_items)}")


if __name__ == "__main__":
    main()
