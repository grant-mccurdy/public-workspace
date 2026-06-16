.PHONY: all check item-bank item-review automated-item-review-dry-run automated-item-review-api automated-review-gate automated-review-gate-api previews canvas-export canvas-export-api validate-architecture validate-item-bank visual-inspect visual-review-dry-run visual-review-api

all: item-bank validate-architecture validate-item-bank item-review previews visual-inspect visual-review-dry-run automated-item-review-dry-run automated-review-gate canvas-export

check: validate-architecture validate-item-bank item-review previews visual-inspect visual-review-dry-run automated-item-review-dry-run automated-review-gate

item-bank:
	python3 src/generate_initial_item_bank.py

item-review: item-bank validate-item-bank
	python3 src/generate_item_review.py

automated-item-review-dry-run: item-review
	python3 scripts/gpt55_item_review.py

automated-item-review-api: item-review
	python3 scripts/gpt55_item_review.py --call-api

previews: item-bank validate-item-bank
	python3 src/render_assessment_preview.py

canvas-export: automated-review-gate
	python3 src/export_canvas_new_quizzes_payload.py

canvas-export-api: automated-review-gate-api
	python3 src/export_canvas_new_quizzes_payload.py

visual-inspect: previews
	node scripts/visual_inspect.mjs

visual-review-dry-run: visual-inspect
	python3 scripts/gpt55_visual_review.py

visual-review-api: visual-inspect
	python3 scripts/gpt55_visual_review.py --call-api

automated-review-gate: item-review automated-item-review-dry-run visual-review-dry-run
	python3 src/generate_automated_review_gate.py

automated-review-gate-api: item-review automated-item-review-api visual-review-api
	python3 src/generate_automated_review_gate.py

validate-architecture:
	python3 src/validate_architecture_contract.py

validate-item-bank: item-bank
	python3 src/validate_item_bank.py
