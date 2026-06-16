#!/usr/bin/env python3
"""Render static student and instructor previews for the diagnostic form."""

from __future__ import annotations

import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "data" / "synthetic" / "assessment_form_spec.json"
ITEM_BANK_PATH = ROOT / "data" / "synthetic" / "item_bank.json"
PREVIEW_DIR = ROOT / "previews"


STYLE = """
:root {
  --border: #d9e2ec;
  --ink: #1f2933;
  --muted: #52606d;
  --panel: #f8fafc;
  --blue: #243b53;
  --blue-soft: #eef2ff;
  --green-soft: #f0fdf4;
  --green-border: #bbf7d0;
  --orange-soft: #fff7ed;
  --orange-border: #fed7aa;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  font-family: Aptos, "Segoe UI", sans-serif;
  line-height: 1.5;
  margin: 0;
  color: var(--ink);
  background:
    linear-gradient(180deg, #f8fafc 0, #ffffff 22rem),
    repeating-linear-gradient(135deg, rgba(36, 59, 83, 0.035) 0 1px, transparent 1px 18px);
}
main { max-width: 1040px; margin: 0 auto; padding: 28px 24px 48px; }
h1, h2, h3, h4 {
  font-family: Charter, "Iowan Old Style", Georgia, serif;
  line-height: 1.2;
  margin-top: 0;
}
h1 { font-size: 2rem; margin-bottom: 0.75rem; }
h2 { font-size: 1.45rem; }
h3 { font-size: 1.05rem; }
.notice, .instructions, .summary-panel {
  border: 1px solid #c7d2fe;
  background: var(--blue-soft);
  padding: 0.9rem;
  border-radius: 6px;
  margin: 0.85rem 0;
}
.draft-banner {
  border: 1px solid #cbd5e1;
  background: #f8fafc;
  color: #334155;
  padding: 0.65rem 0.8rem;
  border-radius: 6px;
  font-weight: 700;
}
.module-nav, .item-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin: 1rem 0;
}
.module-nav {
  position: sticky;
  top: 0;
  z-index: 5;
  padding: 0.55rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 8px 24px rgba(16, 42, 67, 0.08);
}
.module-nav a, .item-nav a {
  color: #102a43;
  border: 1px solid #bcccdc;
  background: #ffffff;
  padding: 0.35rem 0.55rem;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.9rem;
}
.progress-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.7rem;
  margin: 1rem 0;
}
.progress-stat {
  border: 1px solid var(--border);
  border-radius: 6px;
  background: #ffffff;
  padding: 0.75rem;
}
.progress-stat strong {
  display: block;
  font-size: 1.35rem;
}
.module-back {
  color: #102a43;
  font-size: 0.88rem;
}
.module {
  border-top: 2px solid var(--blue);
  margin-top: 2rem;
  padding-top: 1rem;
}
.module-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}
.module-meta {
  color: var(--muted);
  margin: 0;
  font-size: 0.95rem;
}
.item {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1rem;
  margin: 1rem 0;
  background: #ffffff;
}
.item-header {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: flex-start;
  margin-bottom: 0.65rem;
}
.meta { color: var(--muted); font-size: 0.9rem; margin: 0; }
.item-id { color: var(--muted); font-size: 0.85rem; white-space: nowrap; }
.choices { border: 0; margin: 0.8rem 0 0; padding: 0; }
.choice {
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: start;
  gap: 0.65rem;
  border: 1px solid var(--border);
  border-radius: 5px;
  padding: 0.6rem;
  margin: 0.5rem 0;
  background: #ffffff;
}
.choice input { margin-top: 0.2rem; }
.choice-label {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.6rem;
  height: 1.6rem;
  border: 1px solid #9fb3c8;
  border-radius: 50%;
  margin-right: 0.45rem;
  font-weight: 700;
  font-size: 0.85rem;
}
.choice-text { display: inline; }
.numeric-guidance { color: var(--muted); font-size: 0.9rem; margin-bottom: 0.45rem; }
.answer-box {
  border: 1px solid #9fb3c8;
  border-radius: 5px;
  height: 2.7rem;
  width: min(100%, 26rem);
  background: #ffffff;
}
.math-expr, .frac, .math-radical { white-space: nowrap; }
.frac {
  display: inline-grid;
  grid-template-rows: auto auto;
  vertical-align: middle;
  text-align: center;
  line-height: 1;
  min-width: 1.1em;
}
.frac span:first-child {
  border-bottom: 1px solid currentColor;
  padding: 0 0.08em 0.05em;
}
.frac span:last-child { padding-top: 0.05em; }
.key {
  background: var(--green-soft);
  border: 1px solid var(--green-border);
  padding: 0.75rem;
  border-radius: 6px;
  margin-top: 0.75rem;
}
.feedback {
  background: var(--orange-soft);
  border: 1px solid var(--orange-border);
  padding: 0.75rem;
  border-radius: 6px;
  margin-top: 0.75rem;
}
.review-detail {
  border: 1px solid var(--border);
  border-radius: 6px;
  margin-top: 0.85rem;
  background: #ffffff;
}
.review-detail summary {
  cursor: pointer;
  padding: 0.75rem;
  font-weight: 700;
}
.review-detail summary span {
  color: var(--muted);
  display: inline-block;
  font-weight: 500;
  margin-left: 0.5rem;
}
.review-detail[open] summary { border-bottom: 1px solid var(--border); }
.review-detail .key, .review-detail .feedback {
  border-radius: 0;
  border-left: 0;
  border-right: 0;
  margin: 0;
}
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.8rem;
}
.summary-card {
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0.75rem;
}
.summary-card h3 { margin-bottom: 0.4rem; }
.summary-card ul { margin: 0; padding-left: 1.1rem; }
table { width: 100%; border-collapse: collapse; margin: 0.8rem 0; }
th, td { border: 1px solid var(--border); padding: 0.45rem; text-align: left; vertical-align: top; }
th { background: #f1f5f9; }
code { background: #f3f4f6; padding: 0.1rem 0.25rem; border-radius: 3px; }
@media (max-width: 560px) {
  main { padding: 18px 12px 36px; }
  h1 { font-size: 1.45rem; }
  .module-nav { top: 0; }
  .module-nav a, .item-nav a { min-height: 2.25rem; display: inline-flex; align-items: center; }
  .module-header, .item-header { display: block; }
  .item { padding: 0.85rem; }
  .choice { grid-template-columns: 1fr; gap: 0.35rem; }
  .choice input { display: none; }
  .choice-label { margin-right: 0.35rem; }
  th, td { font-size: 0.9rem; }
}
"""


def load_data() -> tuple[dict, list[dict]]:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    items = json.loads(ITEM_BANK_PATH.read_text(encoding="utf-8"))["items"]
    return spec, sorted(items, key=lambda item: (item["module"], item["position"]))


def page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>{STYLE}</style>
</head>
<body>
<main>
{body}
</main>
</body>
</html>
"""


def group_by_module(items: list[dict]) -> dict[int, list[dict]]:
    grouped: dict[int, list[dict]] = defaultdict(list)
    for item in items:
        grouped[item["module"]].append(item)
    return grouped


def item_anchor(item: dict) -> str:
    return f"module-{item['module']}-item-{item['position']}"


def format_math_text(value: str) -> str:
    escaped = html.escape(html.unescape(value))
    escaped = escaped.replace("&lt;=", "&le;").replace("&gt;=", "&ge;")
    escaped = re.sub(r"([A-Za-z0-9\)])\^\(([^)]+)\)", r"\1<sup>\2</sup>", escaped)
    escaped = re.sub(r"([A-Za-z0-9\)])\^([A-Za-z0-9]+)", r"\1<sup>\2</sup>", escaped)
    escaped = re.sub(r"sqrt\(([^()]*)\)", r'<span class="math-radical">&radic;(\1)</span>', escaped)
    escaped = re.sub(
        r"(?<![\w>])(-?\d+)/(\d+)(?![\w<])",
        r'<span class="frac"><span>\1</span><span>\2</span></span>',
        escaped,
    )
    escaped = escaped.replace("theta", '<span class="math-expr">&theta;</span>')
    return escaped


def format_stem_html(value: str) -> str:
    match = re.fullmatch(r"<p>(.*)</p>", value.strip(), flags=re.DOTALL)
    if not match:
        return format_math_text(value)
    return f"<p>{format_math_text(match.group(1))}</p>"


def render_choice(choice: dict, item: dict) -> str:
    choice_id = html.escape(choice["choice_id"])
    input_id = f"{item['item_id']}-{choice_id}"
    return f"""
<label class="choice" for="{html.escape(input_id)}">
  <input id="{html.escape(input_id)}" name="{html.escape(item['item_id'])}" type="radio" disabled>
  <span><span class="choice-label">{choice_id}</span><span class="choice-text">{format_math_text(choice['html'])}</span></span>
</label>
"""


def render_student_item(item: dict, module_item_count: int = 18) -> str:
    choices = ""
    if item["item_type"] == "multiple_choice":
        choices = "<fieldset class=\"choices\"><legend class=\"meta\">Select one answer.</legend>"
        for choice in item["choices"]:
            choices += render_choice(choice, item)
        choices += "</fieldset>"
    else:
        choices = (
            "<p class=\"numeric-guidance\"><strong>Response:</strong> Enter a numeric value. "
            "Equivalent fractions or decimals may be accepted when mathematically equal.</p>"
            "<div class=\"answer-box\" aria-label=\"Numeric response box\"></div>"
        )

    return f"""
<section class="item" id="{item_anchor(item)}">
  <div class="item-header">
    <p class="meta">Module {item['module']} | Question {item['position']} of {module_item_count} | {html.escape(item['domain'])}</p>
    <p class="item-id">{html.escape(item['item_id'])}</p>
  </div>
  {format_stem_html(item['stem_html'])}
  {choices}
</section>
"""


def render_instructor_item(item: dict, module_item_count: int = 18) -> str:
    student_item = render_student_item(item, module_item_count)
    if item["item_type"] == "multiple_choice":
        feedback = "<ul>"
        for choice_id, text in item["distractor_feedback"].items():
            feedback += f"<li><strong>{html.escape(choice_id)}:</strong> {format_math_text(text)}</li>"
        feedback += "</ul>"
        answer_detail = f"<p><strong>Correct answer:</strong> {html.escape(item['correct_answer'])}</p>"
    else:
        rules = ", ".join(
            f"{rule['type']}={rule['value']}" for rule in item["accepted_answer_rules"]
        )
        feedback = f"<p><strong>Accepted answer rules:</strong> {html.escape(rules)}</p>"
        answer_detail = f"<p><strong>Correct answer:</strong> {html.escape(item['correct_answer'])}</p>"

    metadata = f"""
<details class="review-detail">
<summary>Instructor Review Details <span>Answer {html.escape(item['correct_answer'])} | Review status {html.escape(item['review_status'])} | Answer Feedback | {html.escape(item['difficulty_band'])}</span></summary>
<div class="key">
  {answer_detail}
  <p><strong>Explanation:</strong> {format_math_text(item['general_feedback'])}</p>
  <p><strong>Subdomain:</strong> {html.escape(item['subdomain'])}</p>
  <p><strong>Difficulty:</strong> {html.escape(item['difficulty_band'])}</p>
  <p><strong>Review status:</strong> <code>{html.escape(item['review_status'])}</code></p>
  <p><strong>Misconception tags:</strong> {html.escape(', '.join(item['misconception_tags']))}</p>
  <p><strong>Remediation tag:</strong> <code>{html.escape(item['remediation_tag'])}</code></p>
</div>
<div class="feedback">
  <h4>Answer Feedback</h4>
  {feedback}
</div>
</details>
"""
    return student_item.replace("</section>", metadata + "\n</section>")


def render_student_preview(spec: dict, items: list[dict]) -> str:
    grouped = group_by_module(items)
    body = f"""
<h1>{html.escape(spec['title'])}</h1>
<p class="notice">Public-safe student preview. This artifact contains original draft items only and does not include answer keys, student data, LMS identifiers, or live API calls.</p>
<p class="draft-banner">Draft preview for review only. This is the 60-minute scaled MVP form, not a validated standardized test or live Canvas quiz.</p>
<section class="instructions" aria-labelledby="student-instructions">
  <h2 id="student-instructions">Instructions</h2>
  <p>Total time: {spec['timing']['total_minutes']} minutes. Complete Module 1 and Module 2 as separate 30-minute sections unless a reviewer gives different local directions.</p>
  <p>Multiple-choice questions show four labeled choices. Numeric response questions ask for a number; enter exact values unless the question indicates rounding.</p>
  <p>Calculator policy for this static prototype is calculator-permitted by default. Future item metadata may flag local no-calculator review items.</p>
</section>
<section class="progress-strip" aria-label="Form overview">
  <div class="progress-stat"><strong>{len(items)}</strong><span>Total items</span></div>
  <div class="progress-stat"><strong>{spec['timing']['total_minutes']}</strong><span>Minutes</span></div>
  <div class="progress-stat"><strong>{spec['item_type_counts']['multiple_choice']}</strong><span>Multiple choice</span></div>
  <div class="progress-stat"><strong>{spec['item_type_counts']['numeric_student_produced_response']}</strong><span>Numeric response</span></div>
</section>
<nav class="module-nav" aria-label="Module navigation">
  <a href="#student-instructions">Overview</a>
  <a href="#module-1">Module 1</a>
  <a href="#module-2">Module 2</a>
</nav>
"""
    for module_id in sorted(grouped):
        module_items = grouped[module_id]
        body += (
            f"<section class=\"module\" id=\"module-{module_id}\">"
            f"<div class=\"module-header\"><div><h2>Module {module_id}</h2>"
            f"<p class=\"module-meta\">Time: 30 minutes. Items: {len(module_items)}.</p></div>"
            f"<p class=\"module-meta\"><a class=\"module-back\" href=\"#student-instructions\">Back to overview</a></p></div>"
        )
        for item in module_items:
            body += render_student_item(item, len(module_items))
        body += "</section>"
    return page(f"{spec['title']} Student Preview", body)


def count_list(counter: Counter) -> str:
    return "".join(f"<li>{html.escape(str(key))}: {count}</li>" for key, count in sorted(counter.items()))


def render_instructor_summary(items: list[dict], grouped: dict[int, list[dict]]) -> str:
    domain_counts = Counter(item["domain"] for item in items)
    type_counts = Counter(item["item_type"] for item in items)
    difficulty_counts = Counter(item["difficulty_band"] for item in items)
    status_counts = Counter(item["review_status"] for item in items)
    nav = ""
    for module_id in sorted(grouped):
        nav += f"<h3>Module {module_id}</h3><div class=\"item-nav\">"
        for item in grouped[module_id]:
            nav += f"<a href=\"#{item_anchor(item)}\">{html.escape(item['item_id'])}</a>"
        nav += "</div>"
    return f"""
<section class="summary-panel" aria-labelledby="review-dashboard">
  <h2 id="review-dashboard">Review Dashboard</h2>
  <p>This instructor preview is offline-only. It supports content review, answer-key checks, distractor feedback review, and public-safety review before any Canvas export.</p>
  <div class="summary-grid">
    <section class="summary-card"><h3>Domains</h3><ul>{count_list(domain_counts)}</ul></section>
    <section class="summary-card"><h3>Item Types</h3><ul>{count_list(type_counts)}</ul></section>
    <section class="summary-card"><h3>Difficulty</h3><ul>{count_list(difficulty_counts)}</ul></section>
    <section class="summary-card"><h3>Review Status</h3><ul>{count_list(status_counts)}</ul></section>
  </div>
  <h2>Item Navigation</h2>
  {nav}
</section>
"""


def render_instructor_preview(spec: dict, items: list[dict]) -> str:
    grouped = group_by_module(items)
    draft_count = sum(1 for item in items if item["review_status"] == "draft")
    body = f"""
<h1>{html.escape(spec['title'])} Instructor Review</h1>
<p class="notice">Instructor review preview. Items are eligible for offline Canvas payload export only when deterministic checks, GPT-5.5 item review, and GPT-5.5 visual review gates pass. Current draft source item count: {draft_count}.</p>
<p class="draft-banner">Offline review artifact only. No Canvas upload, LMS mutation, scoring action, or source item status change happens from this page.</p>
<p>Source policy: official-source research, original items only, offline Canvas payloads only. Timing note: this preview is the 60-minute scaled MVP form based on a 70-minute target assessment structure.</p>
{render_instructor_summary(items, grouped)}
"""
    for module_id in sorted(grouped):
        module_items = grouped[module_id]
        body += (
            f"<section class=\"module\" id=\"module-{module_id}\">"
            f"<div class=\"module-header\"><div><h2>Module {module_id}</h2>"
            f"<p class=\"module-meta\">Time: 30 minutes. Items: {len(module_items)}.</p></div>"
            f"<p class=\"module-meta\">Draft review status shown per item.</p></div>"
        )
        for item in module_items:
            body += render_instructor_item(item, len(module_items))
        body += "</section>"
    return page(f"{spec['title']} Instructor Review", body)


def main() -> None:
    spec, items = load_data()
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    (PREVIEW_DIR / "student_form.html").write_text(render_student_preview(spec, items), encoding="utf-8")
    (PREVIEW_DIR / "instructor_review.html").write_text(
        render_instructor_preview(spec, items),
        encoding="utf-8",
    )
    print("wrote previews/student_form.html")
    print("wrote previews/instructor_review.html")


if __name__ == "__main__":
    main()
