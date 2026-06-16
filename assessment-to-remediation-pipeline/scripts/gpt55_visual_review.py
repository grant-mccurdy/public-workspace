#!/usr/bin/env python3
"""Generate an optional GPT-5.5 visual review for assessment preview screenshots."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "reports" / "visual-inspection"
SPEC_PATH = PROJECT_ROOT / "data" / "synthetic" / "assessment_form_spec.json"
ITEM_BANK_PATH = PROJECT_ROOT / "data" / "synthetic" / "item_bank.json"
INSPECTION_PATH = OUTPUT_DIR / "visual-inspection.json"
PROMPT_PATH = OUTPUT_DIR / "gpt-5-5-visual-review-prompt.json"
JSON_PATH = OUTPUT_DIR / "gpt-5-5-visual-review.json"
MD_PATH = OUTPUT_DIR / "gpt-5-5-visual-review.md"
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
    print(f"GPT-5.5 visual review failed: {message}", file=sys.stderr)
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


def summarize_items(items: list[dict[str, Any]]) -> dict[str, Any]:
    domain_counts: dict[str, int] = {}
    type_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    difficulty_counts: dict[str, int] = {}
    for item in items:
        domain_counts[item["domain"]] = domain_counts.get(item["domain"], 0) + 1
        type_counts[item["item_type"]] = type_counts.get(item["item_type"], 0) + 1
        status_counts[item["review_status"]] = status_counts.get(item["review_status"], 0) + 1
        difficulty_counts[item["difficulty_band"]] = difficulty_counts.get(item["difficulty_band"], 0) + 1
    return {
        "item_count": len(items),
        "domain_counts": domain_counts,
        "item_type_counts": type_counts,
        "review_status_counts": status_counts,
        "difficulty_counts": difficulty_counts,
        "first_items": [
            {
                "item_id": item["item_id"],
                "domain": item["domain"],
                "item_type": item["item_type"],
                "difficulty_band": item["difficulty_band"],
                "review_status": item["review_status"],
                "stem_text": re.sub("<[^>]+>", "", item["stem_html"]),
            }
            for item in items[:6]
        ],
    }


def review_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "overall_score",
            "decision",
            "one_sentence_assessment",
            "strengths",
            "visual_issues",
            "assessment_review_issues",
            "student_preview_notes",
            "instructor_preview_notes",
            "improvement_priorities",
            "review_gate_flags",
        ],
        "properties": {
            "overall_score": {"type": "integer", "minimum": 0, "maximum": 100},
            "decision": {
                "type": "string",
                "enum": ["REVIEW_READY", "POLISH_RECOMMENDED", "REVISION_REQUIRED", "BLOCKED"],
            },
            "one_sentence_assessment": {"type": "string"},
            "strengths": {"type": "array", "items": {"type": "string"}},
            "visual_issues": {"type": "array", "items": {"type": "string"}},
            "assessment_review_issues": {"type": "array", "items": {"type": "string"}},
            "student_preview_notes": {"type": "array", "items": {"type": "string"}},
            "instructor_preview_notes": {"type": "array", "items": {"type": "string"}},
            "improvement_priorities": {"type": "array", "items": {"type": "string"}},
            "review_gate_flags": {"type": "array", "items": {"type": "string"}},
        },
    }


def build_prompt(model_label: str) -> dict[str, Any]:
    spec = load_json(SPEC_PATH)
    item_bank = load_json(ITEM_BANK_PATH)
    inspection = load_json(INSPECTION_PATH)
    prompt = {
        "task": "Critique public-safe assessment preview screenshots and inspection results.",
        "model_role": f"{model_label} is acting as an advisory visual and assessment-review critic for an automated portfolio gate.",
        "source_of_truth": [
            "The generated HTML previews and screenshots are the visual evidence.",
            "The form spec and item-bank summary are context for structure and review readiness.",
            "Do not recommend live Canvas upload.",
            "Do not rewrite assessment items unless identifying a concise issue for automated review.",
            "Do not invent validation claims, student outcomes, or private context.",
        ],
        "assessment_context": {
            "title": spec["title"],
            "timing": spec["timing"],
            "item_type_counts": spec["item_type_counts"],
            "content_domain_counts": spec["content_domain_counts"],
            "canvas_boundary": spec["canvas_export_boundary"]["mvp_mode"],
        },
        "item_bank_summary": summarize_items(item_bank["items"]),
        "visual_inspection": inspection,
        "criteria": [
            "student preview readability and test-like usability",
            "instructor preview usefulness for automated review",
            "visual hierarchy and scanability",
            "mobile usability",
            "page density and overflow risk",
            "clarity of public-safety and draft-status language",
            "whether any presentation issue should block the automated review gate",
        ],
        "return_json_only": True,
    }
    prompt_text = json.dumps(prompt, indent=2)
    assert_public_safe_text(prompt_text, "GPT-5.5 visual review prompt")
    return prompt


def image_content(path: Path) -> dict[str, str]:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return {"type": "input_image", "image_url": f"data:image/png;base64,{encoded}"}


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

    inspection = load_json(INSPECTION_PATH)
    screenshot_paths = [
        PROJECT_ROOT / case["screenshot"]
        for case in inspection.get("cases", [])
        if case.get("screenshot")
    ]
    content: list[dict[str, str]] = [{"type": "input_text", "text": json.dumps(prompt, indent=2)}]
    content.extend(image_content(path) for path in screenshot_paths if path.exists())

    payload = {
        "model": args.model,
        "instructions": (
            "You are an advisory visual reviewer for a public-safe math assessment portfolio project. "
            "Return JSON only. Do not create Canvas artifacts, invent facts, or make validation claims."
        ),
        "input": [{"role": "user", "content": content}],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "assessment_visual_review",
                "schema": review_schema(),
                "strict": True,
            }
        },
        "store": False,
    }
    request = urllib.request.Request(
        RESPONSES_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
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
    cases = prompt["visual_inspection"].get("cases", [])
    status = prompt["visual_inspection"].get("status", "UNKNOWN")
    return {
        "overall_score": 0,
        "decision": "BLOCKED",
        "one_sentence_assessment": "GPT-5.5 visual critique was not requested; local inspection artifacts and the review prompt are ready for automated gate review.",
        "strengths": [
            "The assessment previews render from local public-safe artifacts.",
            "The visual inspection report captures desktop and mobile cases.",
        ],
        "visual_issues": [],
        "assessment_review_issues": [
            "All items remain in draft status and are not eligible for Canvas export.",
        ],
        "student_preview_notes": [
            f"{case['label']} deterministic status: {'PASS' if not case.get('failures') else 'FAIL'}"
            for case in cases
            if case["label"].startswith("student")
        ],
        "instructor_preview_notes": [
            f"{case['label']} deterministic status: {'PASS' if not case.get('failures') else 'FAIL'}"
            for case in cases
            if case["label"].startswith("instructor")
        ],
        "improvement_priorities": [
            "Run an API-backed visual review only after confirming screenshots are public-safe.",
            "Use structured item review plus visual review before allowing Canvas payload export.",
        ],
        "review_gate_flags": [
            "No API critique was performed.",
            f"Deterministic visual inspection status: {status}.",
        ],
        "_model": model,
        "_model_label": model_label,
    }


def markdown_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- None"


def render_markdown(review: dict[str, Any], *, model: str, model_label: str, openai_used: bool) -> str:
    return f"""# GPT-5.5 Visual Review

Model: `{model_label}` (`{model}`)

OpenAI used: `{'yes' if openai_used else 'no'}`

Decision: `{review.get('decision')}`

Overall score: `{review.get('overall_score')}/100`

## Assessment

{review.get('one_sentence_assessment', '')}

## Strengths

{markdown_list(review.get('strengths') or [])}

## Visual Issues

{markdown_list(review.get('visual_issues') or [])}

## Assessment Review Issues

{markdown_list(review.get('assessment_review_issues') or [])}

## Student Preview Notes

{markdown_list(review.get('student_preview_notes') or [])}

## Instructor Preview Notes

{markdown_list(review.get('instructor_preview_notes') or [])}

## Improvement Priorities

{markdown_list(review.get('improvement_priorities') or [])}

## Review Gate Flags

{markdown_list(review.get('review_gate_flags') or [])}

## Safety Boundary

This report is advisory evidence for an automated portfolio review gate. It does not change source files, create Canvas quizzes, call Canvas, submit anything, or validate assessment content by itself.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--call-api", action="store_true", help="Call OpenAI. Default is dry-run output only.")
    parser.add_argument(
        "--model",
        default=os.environ.get("OPENAI_VISUAL_REVIEW_MODEL")
        or os.environ.get("OPENAI_MODEL")
        or "gpt-5.5",
    )
    parser.add_argument("--model-label", default="GPT-5.5")
    parser.add_argument("--timeout", type=int, default=120)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prompt = build_prompt(args.model_label)
    PROMPT_PATH.write_text(json.dumps(prompt, indent=2) + "\n", encoding="utf-8")
    review = call_openai(prompt, args) if args.call_api else dry_run_review(prompt, args.model, args.model_label)
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
    print(f"wrote {relative(PROMPT_PATH)}")
    print(f"wrote {relative(JSON_PATH)}")
    print(f"wrote {relative(MD_PATH)}")
    if not args.call_api:
        print("OpenAI not called; dry-run visual review generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
