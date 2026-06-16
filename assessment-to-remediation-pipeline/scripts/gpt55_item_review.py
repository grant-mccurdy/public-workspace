#!/usr/bin/env python3
"""Generate an optional GPT-5.5 assessment item review gate."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "reports" / "automated-review"
SPEC_PATH = PROJECT_ROOT / "data" / "synthetic" / "assessment_form_spec.json"
ITEM_BANK_PATH = PROJECT_ROOT / "data" / "synthetic" / "item_bank.json"
DETERMINISTIC_REVIEW_PATH = PROJECT_ROOT / "reports" / "item-review" / "item-review.json"
PROMPT_PATH = OUTPUT_DIR / "gpt-5-5-item-review-prompt.json"
JSON_PATH = OUTPUT_DIR / "gpt-5-5-item-review.json"
MD_PATH = OUTPUT_DIR / "gpt-5-5-item-review.md"
RESPONSES_URL = "https://api.openai.com/v1/responses"
SECRET_MARKERS = (
    "Bearer ",
    "OPENAI_API_KEY",
    "SUPABASE_ACCESS_TOKEN",
    "SUPABASE_API_KEY",
    "postgres://",
    "postgresql://",
    "sk-",
)
PRIVATE_PATH_PATTERN = re.compile(r"/home/[^\s`'\"]+")


def fail(message: str) -> None:
    print(f"GPT-5.5 item review failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def relative(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT).as_posix()


def assert_public_safe_text(text: str, context: str) -> None:
    for marker in SECRET_MARKERS:
        if marker in text:
            fail(f"refusing to use {context}: found secret marker")
    if PRIVATE_PATH_PATTERN.search(text):
        fail(f"refusing to use {context}: found private local path")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing required input: {relative(path)}")
    text = path.read_text(encoding="utf-8")
    assert_public_safe_text(text, relative(path))
    return json.loads(text)


def strip_tags(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()


def compact_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compacted = []
    for item in items:
        base = {
            "item_id": item["item_id"],
            "module": item["module"],
            "position": item["position"],
            "domain": item["domain"],
            "subdomain": item["subdomain"],
            "skill_statement": item["skill_statement"],
            "difficulty_band": item["difficulty_band"],
            "item_type": item["item_type"],
            "stem_text": strip_tags(item["stem_html"]),
            "correct_answer": item["correct_answer"],
            "general_feedback": item["general_feedback"],
            "misconception_tags": item["misconception_tags"],
            "remediation_tag": item["remediation_tag"],
            "mastery_check_target": item["mastery_check_target"],
            "review_status": item["review_status"],
        }
        if item["item_type"] == "multiple_choice":
            base["choices"] = [
                {
                    "choice_id": choice["choice_id"],
                    "text": strip_tags(choice["html"]),
                    "is_correct": choice["is_correct"],
                }
                for choice in item["choices"]
            ]
            base["distractor_feedback"] = item["distractor_feedback"]
        else:
            base["accepted_answer_rules"] = item["accepted_answer_rules"]
        compacted.append(base)
    return compacted


def review_schema() -> dict[str, Any]:
    item_review = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "item_id",
            "decision",
            "severity",
            "math_content_notes",
            "distractor_feedback_notes",
            "public_safety_notes",
            "recommended_action",
        ],
        "properties": {
            "item_id": {"type": "string"},
            "decision": {"type": "string", "enum": ["automated_pass", "needs_revision", "blocked"]},
            "severity": {"type": "string", "enum": ["info", "minor", "major", "critical"]},
            "math_content_notes": {"type": "array", "items": {"type": "string"}},
            "distractor_feedback_notes": {"type": "array", "items": {"type": "string"}},
            "public_safety_notes": {"type": "array", "items": {"type": "string"}},
            "recommended_action": {"type": "string"},
        },
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "overall_score",
            "decision",
            "export_allowed",
            "one_sentence_assessment",
            "strengths",
            "form_issues",
            "item_reviews",
            "improvement_priorities",
            "review_gate_flags",
        ],
        "properties": {
            "overall_score": {"type": "integer", "minimum": 0, "maximum": 100},
            "decision": {
                "type": "string",
                "enum": ["AUTOMATED_PASS", "POLISH_RECOMMENDED", "REVISION_REQUIRED", "BLOCKED"],
            },
            "export_allowed": {"type": "boolean"},
            "one_sentence_assessment": {"type": "string"},
            "strengths": {"type": "array", "items": {"type": "string"}},
            "form_issues": {"type": "array", "items": {"type": "string"}},
            "item_reviews": {"type": "array", "items": item_review},
            "improvement_priorities": {"type": "array", "items": {"type": "string"}},
            "review_gate_flags": {"type": "array", "items": {"type": "string"}},
        },
    }


def build_prompt(model_label: str) -> dict[str, Any]:
    spec = load_json(SPEC_PATH)
    item_bank = load_json(ITEM_BANK_PATH)
    deterministic_review = load_json(DETERMINISTIC_REVIEW_PATH)
    items = sorted(item_bank["items"], key=lambda value: (value["module"], value["position"]))
    prompt = {
        "task": "Review a public-safe math readiness diagnostic item bank for automated portfolio gate readiness.",
        "model_role": f"{model_label} is acting as an automated assessment-quality reviewer, not as a standardized-test validator.",
        "source_of_truth": [
            "Use the structured item bank, answer keys, feedback, and deterministic review as the evidence.",
            "Do not claim the diagnostic is validated, standardized, predictive, or equivalent to SAT/ACT/AP.",
            "Do not recommend live Canvas upload; this project creates offline payload artifacts only.",
            "For MCQ items, check whether each distractor feedback entry identifies a specific likely mathematical error.",
            "For numeric items, check whether accepted answer rules and general feedback are clear enough for an MVP.",
            "Return a decision for every item_id exactly once.",
        ],
        "assessment_context": {
            "assessment_id": spec["assessment_id"],
            "title": spec["title"],
            "timing": spec["timing"],
            "item_type_counts": spec["item_type_counts"],
            "content_domain_counts": spec["content_domain_counts"],
            "canvas_boundary": spec["canvas_export_boundary"]["mvp_mode"],
        },
        "deterministic_review_summary": deterministic_review["summary"],
        "items": compact_items(items),
        "criteria": [
            "mathematical correctness of stem, answer, rationale, and accepted answer rules",
            "clarity and grade-appropriate precision of item wording",
            "alignment between domain, subdomain, skill statement, difficulty band, and item demand",
            "distractor plausibility and specificity of feedback for each wrong answer",
            "public-safety compliance and absence of copied commercial-test content",
            "whether any issue should block offline Canvas payload inclusion",
        ],
        "return_json_only": True,
    }
    prompt_text = json.dumps(prompt, indent=2)
    assert_public_safe_text(prompt_text, "GPT-5.5 item review prompt")
    return prompt


def output_text(data: dict[str, Any]) -> str:
    text = data.get("output_text")
    if text:
        return text
    chunks: list[str] = []
    for item in data.get("output") or []:
        for content in item.get("content") or []:
            if content.get("type") in {"output_text", "text"}:
                chunks.append(content.get("text", ""))
    return "".join(chunks)


def call_openai(prompt: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        fail("OPENAI_API_KEY is missing. Run without --call-api for dry-run output.")

    payload = {
        "model": args.model,
        "instructions": (
            "You are an automated assessment item reviewer for a public-safe portfolio project. "
            "Return JSON only. Do not invent validation claims, private context, or live LMS actions."
        ),
        "input": [{"role": "user", "content": [{"type": "input_text", "text": json.dumps(prompt, indent=2)}]}],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "assessment_item_review",
                "schema": review_schema(),
                "strict": True,
            }
        },
        "store": False,
    }
    request = urllib.request.Request(
        RESPONSES_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as error:
        fail(str(error))
    text = output_text(data)
    if not text:
        fail("OpenAI response did not include output text")
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        fail(f"OpenAI response was not valid JSON: {error}")


def dry_run_review(prompt: dict[str, Any], model: str, model_label: str) -> dict[str, Any]:
    return {
        "overall_score": 0,
        "decision": "BLOCKED",
        "export_allowed": False,
        "one_sentence_assessment": "API-backed GPT-5.5 item review was not requested; structured review inputs are ready.",
        "strengths": [
            "The item bank is structured and public-safe for automated review.",
            "The deterministic review packet is available as context.",
        ],
        "form_issues": [
            "No API-backed item-quality judgment was performed in dry-run mode.",
        ],
        "item_reviews": [
            {
                "item_id": item["item_id"],
                "decision": "blocked",
                "severity": "info",
                "math_content_notes": ["Dry-run mode does not evaluate math correctness."],
                "distractor_feedback_notes": ["Dry-run mode does not evaluate feedback specificity."],
                "public_safety_notes": ["Inputs passed local public-safety text screening."],
                "recommended_action": "Run automated-item-review-api before allowing offline Canvas item export.",
            }
            for item in prompt["items"]
        ],
        "improvement_priorities": [
            "Run API-backed GPT-5.5 item review after confirming the item bank is public-safe.",
        ],
        "review_gate_flags": [
            "OpenAI was not called.",
            "Dry-run output intentionally blocks Canvas item export.",
        ],
        "_model": model,
        "_model_label": model_label,
    }


def validate_review(review: dict[str, Any], expected_item_ids: set[str]) -> None:
    seen = [item["item_id"] for item in review.get("item_reviews", [])]
    missing = sorted(expected_item_ids - set(seen))
    extra = sorted(set(seen) - expected_item_ids)
    duplicates = sorted({item_id for item_id in seen if seen.count(item_id) > 1})
    if missing or extra or duplicates:
        fail(f"item review ids mismatch; missing={missing}, extra={extra}, duplicates={duplicates}")
    if any(item["decision"] != "automated_pass" for item in review["item_reviews"]):
        review["export_allowed"] = False
    if review["decision"] in {"REVISION_REQUIRED", "BLOCKED"}:
        review["export_allowed"] = False


def markdown_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- None"


def render_markdown(review: dict[str, Any], *, model: str, model_label: str, openai_used: bool) -> str:
    item_rows = "\n".join(
        "| {item_id} | {decision} | {severity} | {recommended_action} |".format(**item)
        for item in review.get("item_reviews", [])
    )
    flagged = [item for item in review.get("item_reviews", []) if item["decision"] != "automated_pass"]
    flagged_sections = []
    for item in flagged:
        flagged_sections.append(
            f"""### {item['item_id']} - {item['decision']}

Math/content notes:

{markdown_list(item['math_content_notes'])}

Distractor-feedback notes:

{markdown_list(item['distractor_feedback_notes'])}

Public-safety notes:

{markdown_list(item['public_safety_notes'])}

Recommended action: {item['recommended_action']}
"""
        )
    return f"""# GPT-5.5 Item Review

Model: `{model_label}` (`{model}`)

OpenAI used: `{'yes' if openai_used else 'no'}`

Decision: `{review.get('decision')}`

Export allowed by item review: `{review.get('export_allowed')}`

Overall score: `{review.get('overall_score')}/100`

## Assessment

{review.get('one_sentence_assessment', '')}

## Strengths

{markdown_list(review.get('strengths') or [])}

## Form Issues

{markdown_list(review.get('form_issues') or [])}

## Improvement Priorities

{markdown_list(review.get('improvement_priorities') or [])}

## Review Gate Flags

{markdown_list(review.get('review_gate_flags') or [])}

## Item Decisions

| Item | Decision | Severity | Recommended Action |
| --- | --- | --- | --- |
{item_rows}

## Flagged Items

{chr(10).join(flagged_sections) if flagged_sections else 'No item-level issues flagged by the automated item review.'}

## Safety Boundary

This report is advisory evidence for an automated portfolio review gate. It does not validate the diagnostic, call Canvas, upload content, or use private student data.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--call-api", action="store_true", help="Call OpenAI. Default is dry-run output only.")
    parser.add_argument(
        "--model",
        default=os.environ.get("OPENAI_ITEM_REVIEW_MODEL") or os.environ.get("OPENAI_MODEL") or "gpt-5.5",
    )
    parser.add_argument("--model-label", default="GPT-5.5")
    parser.add_argument("--timeout", type=int, default=180)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prompt = build_prompt(args.model_label)
    PROMPT_PATH.write_text(json.dumps(prompt, indent=2) + "\n", encoding="utf-8")
    review = call_openai(prompt, args) if args.call_api else dry_run_review(prompt, args.model, args.model_label)
    expected_item_ids = {item["item_id"] for item in prompt["items"]}
    validate_review(review, expected_item_ids)
    report = {
        "generated_at": "not_recorded_for_reproducible_offline_review",
        "model": args.model,
        "model_label": args.model_label,
        "openai_used": args.call_api,
        "review": {key: value for key, value in review.items() if not key.startswith("_")},
    }
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    MD_PATH.write_text(
        render_markdown(report["review"], model=args.model, model_label=args.model_label, openai_used=args.call_api),
        encoding="utf-8",
    )
    print(f"wrote {PROMPT_PATH.relative_to(PROJECT_ROOT)}")
    print(f"wrote {JSON_PATH.relative_to(PROJECT_ROOT)}")
    print(f"wrote {MD_PATH.relative_to(PROJECT_ROOT)}")
    if not args.call_api:
        print("OpenAI not called; dry-run item review generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
