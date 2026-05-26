# Makefile — targets wired in Story 1.5.
# Requires: pip install -r requirements.txt
#
# Breakpoints for understanding this file:
#   LEARNER build   → site/               (instructor content excluded)
#   INSTRUCTOR build → site-instructor/   (all content included, INSTRUCTOR=1 set)
#   PDF             → scripts/pdf_build.py (print-site HTML + Chromium; WeasyPrint fallback) → dist/
#   SERVE           → mkdocs serve with live reload (learner variant, port 8000)
#   SERVE-INSTRUCTOR → mkdocs serve with INSTRUCTOR=1 (port 8001; Story 5.2)
#   BUILD-ALL       → build-learner + build-instructor (Story 5.2)
#   LINT            → authoring lint stub (rules land in Epic 2; exits 0 if none installed)

PYTHON      ?= python3
NSO_VERSION := $(shell $(PYTHON) scripts/read_nso_version.py 2>/dev/null || echo unknown)

LEARNER_SITE    := site
INSTRUCTOR_SITE := site-instructor
# Story 6.2 — canonical learner PDF artifact (FR20/FR22)
DIST_PDF        := dist/cisco-nso-hands-on-training-workbook-$(NSO_VERSION).pdf
DIST_PDF_INSTR  := dist/cisco-nso-hands-on-training-workbook-$(NSO_VERSION)-instructor.pdf
SERVE_LEARNER_ADDR    ?= 127.0.0.1:8000
SERVE_INSTRUCTOR_ADDR ?= 127.0.0.1:8001

.DEFAULT_GOAL := help

.PHONY: help build-learner build-instructor build-all check-instructor-leak pdf pdf-test pdf-learner pdf-instructor serve serve-instructor lint lint-fail-all clean pre-render-mermaid optimize-images rollback-lab ci-quality-gates

## help: Print this help summary
help:
	@echo ""
	@echo "Cisco NSO Workbook — available make targets:"
	@echo ""
	@printf "  %-22s %s\n" "build-learner"    "Build learner site → $(LEARNER_SITE)/"
	@printf "  %-22s %s\n" "build-instructor" "Build instructor site → $(INSTRUCTOR_SITE)/"
	@printf "  %-22s %s\n" "build-all"        "Build learner + instructor sites + dual-audience smoke + FR37 leak check (5.2–5.6)"
	@printf "  %-22s %s\n" "check-instructor-leak" "Scan learner site/ for instructor-only markers (FR37, Story 5.6)"
	@printf "  %-22s %s\n" "pdf"              "Learner PDF (print-site + Chromium) → $(DIST_PDF) (Story 6.2)"
	@printf "  %-22s %s\n" "pdf-test"         "Spike corpus PDF vs acceptance baseline page count (6.2 AC4)"
	@printf "  %-22s %s\n" "pdf-learner"      "Alias for pdf"
	@printf "  %-22s %s\n" "pdf-instructor"   "Instructor PDF → $(DIST_PDF_INSTR)"
	@printf "  %-22s %s\n" "serve"            "Live-reload dev server (learner, $(SERVE_LEARNER_ADDR))"
	@printf "  %-22s %s\n" "serve-instructor" "Live-reload dev server (INSTRUCTOR=1, $(SERVE_INSTRUCTOR_ADDR))"
	@printf "  %-22s %s\n" "lint"             "Run authoring lint (warn mode default)"
	@printf "  %-22s %s\n" "lint-fail-all"    "Lint with all rule groups in fail mode (Epic 4 / dry run)"
	@printf "  %-22s %s\n" "pre-render-mermaid" "Mermaid .mmd → SVG/PNG under docs/assets/images/mermaid/ (Story 3.5)"
	@printf "  %-22s %s\n" "optimize-images"  "oxipng on PNGs in docs/assets/images/ (optional; Story 3.5)"
	@printf "  %-22s %s\n" "rollback-lab"      "Print rollback hints for LAB=1..9 (Story 3.9)"
	@printf "  %-22s %s\n" "ci-quality-gates" "Story 3.11 — npm ci + perf budget, links, Lighthouse, axe (needs Chromium on PATH)"
	@printf "  %-22s %s\n" "clean"            "Remove built site directories"
	@echo ""

## build-learner: Build the learner site into site/ (instructor content excluded)
build-learner:
	@echo "Building learner site…"
	@mkdocs build --strict --site-dir $(LEARNER_SITE)
	@echo "✓ Learner site built → $(LEARNER_SITE)/"

## build-instructor: Build the instructor site into site-instructor/ (all content, INSTRUCTOR=1)
build-instructor:
	@echo "Building instructor site…"
	@INSTRUCTOR=1 mkdocs build --strict --site-dir $(INSTRUCTOR_SITE)
	@echo "✓ Instructor site built → $(INSTRUCTOR_SITE)/"

## build-all: Build learner site then instructor site (Story 5.2)
build-all: build-learner build-instructor
	@echo "✓ build-all complete → $(LEARNER_SITE)/ and $(INSTRUCTOR_SITE)/"
	@echo "Checking dual-audience smoke (Story 5.3: instructor_block)…"
	@LEAK=$$(find $(LEARNER_SITE) \( -path '*_test-fixtures*' -o -path '*/0[0-9]-*' \) -name '*.html' -exec grep -l 'data-instructor-block' {} \; 2>/dev/null); \
	if [ -n "$$LEAK" ]; then echo "ERROR: learner HTML leaks instructor macro (data-instructor-block): $$LEAK"; exit 1; fi
	@HIT=$$(find $(INSTRUCTOR_SITE)/_test-fixtures -name '*.html' -exec grep -l 'data-instructor-block' {} \; 2>/dev/null); \
	if [ -z "$$HIT" ]; then echo "ERROR: instructor site missing instructor_block fixture output under _test-fixtures/"; exit 1; fi
	@echo "✓ Dual-audience smoke OK (learner lab + fixture paths have no macro marker; instructor fixture renders)"
	@echo "Checking FR37 instructor leakage guard (Story 5.6)…"
	@$(PYTHON) scripts/check_instructor_leak.py $(LEARNER_SITE)
	@echo "✓ FR37 leakage check OK ($(LEARNER_SITE)/)"

## check-instructor-leak: Scan built learner site for instructor-only HTML markers (FR37)
check-instructor-leak:
	@$(PYTHON) scripts/check_instructor_leak.py $(LEARNER_SITE)

## pdf: Learner PDF from mkdocs-print-site + Chromium (Story 6.2; WeasyPrint optional fallback)
pdf:
	@$(PYTHON) scripts/pdf_build.py

## pdf-test: Acceptance baseline check (spike corpus page count)
pdf-test:
	@$(PYTHON) scripts/pdf_acceptance_test.py

## pdf-learner: Alias for pdf (kept for muscle memory / docs)
pdf-learner: pdf

## pdf-instructor: Full instructor site → print-site PDF (facilitator content included)
pdf-instructor:
	@$(PYTHON) scripts/pdf_build.py --instructor

## serve: Start live-reload dev server (learner variant — facilitator paths omitted)
serve:
	@echo "Starting learner live-reload at http://$(SERVE_LEARNER_ADDR) (Ctrl-C to stop)…"
	@mkdocs serve --dev-addr $(SERVE_LEARNER_ADDR)

## serve-instructor: Live-reload with INSTRUCTOR=1 (facilitator content included; Story 5.2)
serve-instructor:
	@echo "Starting instructor live-reload at http://$(SERVE_INSTRUCTOR_ADDR) (INSTRUCTOR=1, Ctrl-C to stop)…"
	@INSTRUCTOR=1 mkdocs serve --dev-addr $(SERVE_INSTRUCTOR_ADDR)

## lint: Run authoring lint (AR13 rules 1–12 + AR15; LINT_RULES_*_MODE=fail to hard-fail)
lint:
	@if [ -f scripts/lint_authoring.py ]; then \
		$(PYTHON) scripts/lint_authoring.py docs/; \
	else \
		echo "✓ scripts/lint_authoring.py missing."; \
	fi

## lint-fail-all: All LINT_RULES_*_MODE=fail — full enforcement dry run (Story 2.7)
lint-fail-all:
	@if [ -f scripts/lint_authoring.py ]; then \
		LINT_RULES_1_3_MODE=fail LINT_RULES_4_7_MODE=fail LINT_RULES_5_6_MODE=fail LINT_RULES_8_11_MODE=fail LINT_RULES_12_MODE=fail \
		$(PYTHON) scripts/lint_authoring.py docs/; \
	else \
		echo "✓ scripts/lint_authoring.py missing."; \
	fi

## pre-render-mermaid: Run scripts/pre_render_mermaid.py (requires Node + @mermaid-js/mermaid-cli)
pre-render-mermaid:
	@$(PYTHON) scripts/pre_render_mermaid.py

## optimize-images: Lossless PNG optimization + optional per-folder size warnings
optimize-images:
	@$(PYTHON) scripts/optimize_images.py --budget-warn

## clean: Remove all built site directories
clean:
	@rm -rf $(LEARNER_SITE) $(INSTRUCTOR_SITE)
	@echo "✓ Cleaned $(LEARNER_SITE)/ and $(INSTRUCTOR_SITE)/"

## ci-quality-gates: Story 3.11 — run scripts/ci/run_quality_gates.sh (requires: npm ci, built site/)
ci-quality-gates: build-learner
	@npm ci
	@bash scripts/ci/run_quality_gates.sh $(LEARNER_SITE)

## rollback-lab: Story 3.9 — print non-destructive rollback hints (requires LAB=1..9)
rollback-lab:
	@if [ -z "$(LAB)" ]; then \
	  echo "Usage: make rollback-lab LAB=N   (N = 1–9)"; \
	  echo "See your instructor for full VM / NSO reset guidance."; \
	  exit 1; \
	fi
	@LAB=$(LAB) $(SHELL) scripts/rollback-lab.sh
