#!/usr/bin/env python3
"""Validate the offline-first assessment architecture contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "data" / "synthetic" / "assessment_form_spec.json"


EXPECTED_DOMAIN_COUNTS = {
    "Algebra": 13,
    "Advanced Math": 13,
    "Problem-Solving and Data Analysis": 5,
    "Geometry and Trigonometry": 5,
}


def fail(message: str) -> None:
    print(f"architecture contract validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))

    timing = spec["timing"]
    item_types = spec["item_type_counts"]
    domains = spec["content_domain_counts"]
    modules = spec["module_blueprints"]
    canvas = spec["canvas_export_boundary"]

    require(timing["total_minutes"] == 60, "total_minutes must be 60")
    require(timing["module_count"] == 2, "module_count must be 2")
    require(timing["minutes_per_module"] == 30, "minutes_per_module must be 30")
    require(timing["mvp_item_count"] == 36, "mvp_item_count must be 36")

    require(item_types["multiple_choice"] == 27, "multiple_choice count must be 27")
    require(
        item_types["numeric_student_produced_response"] == 9,
        "numeric SPR count must be 9",
    )
    require(sum(item_types.values()) == 36, "item type counts must sum to 36")

    require(domains == EXPECTED_DOMAIN_COUNTS, "domain counts do not match contract")
    require(sum(domains.values()) == 36, "domain counts must sum to 36")

    require(len(modules) == 2, "there must be exactly two modules")
    for module in modules:
        label = f"module {module['module']}"
        require(module["minutes"] == 30, f"{label} must be 30 minutes")
        require(module["items"] == 18, f"{label} must contain 18 items")
        require(
            module["multiple_choice"] + module["numeric_student_produced_response"]
            == module["items"],
            f"{label} item-type counts must sum to module item count",
        )
        require(
            sum(module["domain_counts"].values()) == module["items"],
            f"{label} domain counts must sum to module item count",
        )

    require(
        sum(module["multiple_choice"] for module in modules) == 27,
        "module MCQ counts must sum to 27",
    )
    require(
        sum(module["numeric_student_produced_response"] for module in modules) == 9,
        "module numeric SPR counts must sum to 9",
    )
    for domain, expected in EXPECTED_DOMAIN_COUNTS.items():
        actual = sum(module["domain_counts"][domain] for module in modules)
        require(actual == expected, f"module counts for {domain} must sum to {expected}")

    require(
        spec["source_policy"]["research_sources"] == "official_only",
        "research source policy must be official_only",
    )
    require(
        spec["source_policy"]["item_content_policy"] == "original_items_only",
        "item content policy must require original items only",
    )
    require(canvas["mvp_mode"] == "offline_payload_only", "Canvas mode must be offline")
    require(
        canvas["live_api_calls_allowed"] is False,
        "live Canvas API calls must not be allowed in MVP",
    )

    print("architecture contract validation passed")


if __name__ == "__main__":
    main()
