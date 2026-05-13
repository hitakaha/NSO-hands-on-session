# Cisco NSO Workbook — Authoring Guide

<!--
  Covers FR42, NFR-M3, NFR-M4, FR41, UX-DR27–29, UX-DR16–17.
  Epic 1 quickstart is preserved below as "Prerequisites & local build".
  Full content contract: lint rules AR13 (Stories 2.3–2.6), instructor model (Epic 5).
-->

This guide is the single canonical reference for **voice**, **structure**, and **lint** for lab chapters.
Use it when writing or reviewing Markdown under `docs/`.

---

## Prerequisites & local build

**Target (NFR-M3):** From `git clone` to `make serve` with a working site in **≤ 30 minutes** on a standard Cisco corporate laptop.

### Tooling

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.12 | See `.python-version`. Use `pyenv` or Cisco-blessed Python. |
| GNU Make | Any | macOS/Linux; Windows use **WSL2** (native PowerShell not supported). |
| Browser | Modern | Chrome, Firefox, or Edge. |
| `git` | Any | For clone and commits. |

**macOS**

```bash
brew install pyenv
pyenv install 3.12
pyenv local 3.12
python --version
make --version
```

**Linux (Ubuntu / Debian)**

```bash
sudo apt-get update && sudo apt-get install -y make python3.12 python3.12-venv
```

**Windows:** use WSL2 and follow Linux steps inside the Ubuntu terminal.

### Clone and install

```bash
git clone https://github.com/daquezad/NSO-hands-on-session.git <YOUR_DIR>
cd <YOUR_DIR>
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`<YOUR_DIR>` is the only placeholder — replace it with your local path.

### Build and serve

| Command | Purpose |
|---------|---------|
| `make serve` | Live reload at [http://localhost:8000](http://localhost:8000) (learner build). |
| `make build-learner` | Static site → `site/`. |
| `make build-instructor` | Instructor site → `site-instructor/` (`INSTRUCTOR=1`). |
| `make lint` | Authoring lint (**AR13 rules 1–11 + AR15**). Default **warn mode** (exit 0). `LINT_RULES_1_3_MODE=fail` / `LINT_RULES_4_7_MODE=fail` / `LINT_RULES_5_6_MODE=fail` / `LINT_RULES_8_11_MODE=fail` hard-fail matching rule groups (rule 8 stays warning-only). |
| `make pdf-learner` / `make pdf-instructor` | PDF via Chromium headless (see Makefile). |
| `make rollback-lab LAB=N` | Story 3.9 — prints non-destructive rollback hints for chapter `N` (1–9). |
| `make ci-quality-gates` | Story 3.11 — `npm ci` then `scripts/ci/run_quality_gates.sh` (perf budget, links, Lighthouse, axe); requires Chromium or Chrome on `PATH`. |

**Learner journey (Story 3.8):** `mkdocs.yml` defines the left **navigation** (all chapters). Material’s **table of contents** follows the current page (`toc.follow` in `mkdocs.yml`). **Search** is the built-in offline index (`plugins: search`) — no network at runtime. After `make build-learner`, run `python3 scripts/check_noindex.py site/` to confirm every generated `.html` includes a `robots` meta with **noindex** and **nofollow** and that `site/sitemap.xml` is absent (CI runs this step on every PR).

**Responsive / touch (Story 3.10):** At **≤768px** width, Material collapses primary nav to the hamburger; a **Contents** pill (in `overrides/main.html`) toggles the same `#__toc` control as the in-page table of contents. **≥44×44px** touch targets are enforced for header actions and code-copy buttons in `extra.css`. The **`time_budget`** legend stacks vertically at **≤600px**; **`journey_table`** uses stacked cards at **≤600px** (see `extra.css`). Record spot-checks in **`docs/responsive-check-log.md`**.

**CI quality gates (Story 3.11 / 6.10):** PR workflow runs **`scripts/check_perf_budget.py`** (≤500 KB HTML+CSS+JS per page, NFR-P5), **`scripts/check_internal_links.py`** (NFR-R4), **`scripts/check_noindex.py`** (NFR-S8), **Lighthouse** performance ≥90 on home + Lab 8 (mobile + simulated throttling, NFR-P7), and **`scripts/check_axe_warn.py`** (axe-core against URLs in **`scripts/ci/axe-pages.yaml`**; default **`AXE_MODE=warn`** with optional **`a11y_baseline.yaml`** ceilings; set **`AXE_MODE=fail`** in CI to block on **serious/critical** — NFR-A8 / FR39). Locally: `make ci-quality-gates` (needs `npm ci` and Chromium/Chrome on `PATH`). See **`docs/_internal/accessibility.md`**.

**Lint cross-reference:** Rules **1–3** — frontmatter, filename, headings (Story 2.3). **Rule 3d** — every `docs/NN-*.md` chapter must call `time_budget(...)` (Story 3.4). **Rule 3f** — `docs/index.md` home cover macros (Story 3.6). Rules **4a–4d, 7** — language tags, *Expected output* pairing, bare commands, `expected_output` landmark (Story 3.3), Jinja allow-list includes `topology`, `home_subtitle`, `home_meta`, `journey_table`. Rules **5–6** — alt text, links (Story 2.5). Rules **8–10** — instructor coherence, versions, classification (Story 2.6). **Rule 11** — lab-safety partial + `LAB_SAFETY_MESSAGE` + `lab_safety` only on index (general) and Lab 8 (intentional_failure) (Story 3.4). Rule **12** — instructor block parity (Story 5.7).

### What you should see

After `make serve`, the home page shows the workbook title, navigation for Labs 1–9, and Material chrome (search, dark mode). If the page is blank, confirm the venv is active and you are in the repo root (directory containing `mkdocs.yml`).

### Timing log (NFR-M3 feedback loop)

If onboarding takes **longer than 30 minutes**, file a GitHub issue titled `onboarding: exceeded 30-minute SLA — <date> — <OS>` and add a row to `docs/onboarding-log.md` with your timings.

---

## Anatomy of a lab chapter

Copy `docs/_template/chapter-template.md` to `docs/NN-your-lab-title.md` where `NN` is a two-digit chapter index (`01`–`99`). Fill **YAML frontmatter** and all **six** mandatory sections.

**Mandatory section order (AR14):**

1. `## Learning Objectives`
2. `## Time Budget`
3. `## Prerequisites`
4. `## Procedure`
5. `## Verification`
6. `## Common Errors`

Machine-readable schema: `docs/_template/schema.yaml`. **Lint rule 1** validates frontmatter against that schema; **lint rule 3** enforces section order, a single H1, and no skipped heading levels (e.g. H1 → H3 without H2).

**Story 3.4 — section macros**

| Macro | Where |
|-------|--------|
| `time_budget(total=N, segments=[[minutes,"label"],...])` | Under `## Time Budget` on every `docs/NN-*.md` lab chapter. Minutes must sum to `N`. Invoke as a Jinja macro call in Markdown (double curly braces around the call). |
| `common_errors_start` … `common_error(symptom, cause, fix)` … `common_errors_end` | Optional, inside `## Common Errors`. |
| `{{ lab_safety(variant="general") }}` | `docs/index.md` only. |
| `{{ lab_safety(variant="intentional_failure") }}` | `08-*.md` (Lab 8) only. |

Do not call `lab_safety` on labs 01–07 or 09. **Lint rules 3d and 11** enforce this.

**Story 3.5 — topology + images**

| Piece | Purpose |
|-------|---------|
| `docs/assets/mermaid-sources/<chapter>/<id>.mmd` | Mermaid source (≤ 8 nodes; names like `xr-1`, `nso-server`, …). |
| `docs/assets/mermaid-sources/<chapter>/<id>.alt.txt` | Long description for accessibility; copied next to renders. |
| `make pre-render-mermaid` | Runs `scripts/pre_render_mermaid.py` → `docs/assets/images/mermaid/<chapter>/<id>.{svg,png,alt.txt}` (requires Node + `@mermaid-js/mermaid-cli`; Chromium must launch). Commit generated SVG/PNG/alt. |
| `topology(diagram_id, chapter, caption)` | Embeds the pre-rendered **SVG** for web (wrap the call in Jinja macro syntax in source). |
| Screenshots | Drop PNGs under `docs/assets/images/` (see subfolders as needed). `make optimize-images` runs **oxipng** when installed. **WebP** variants for PNGs are produced at `mkdocs build` time (not committed) when **cwebp** is on `PATH`. |

**Story 3.6 — home cover (`docs/index.md`)**

| Macro | Role |
|-------|------|
| `home_subtitle(text="…")` | One-line audience line directly under the H1. |
| `home_meta()` | Meta row: total time and lab count (both derived from the journey-data tuple), NSO version from `mkdocs.yml` `extra.nso_version`. |
| `journey_table()` | Accessible `<table>` with caption; Lab 8 row includes an **intentional break** chip with visible text. |

**Order (required):** H1 headline → `home_subtitle` → `home_meta` → `lab_safety(general)` → `topology` → `journey_table`. No generic “welcome to…” copy. **Lint rule 3f** enforces the macros and a single H1.

**Story 3.7 — accessibility baseline**

Skip links (Material “Skip to content” plus **Skip to navigation** and **Skip to verification** on pages that have `## Verification`), Cisco-blue focus rings on Material controls, global copy announcer (`#css-a11y-announcer`), and `docs/a11y-log.md` for spot-check records.

---

## Voice & style (UX-DR27)

Reviewer-gated (not automatically linted). AI-generated content **must** follow this section.

### Second person; present indicative imperatives

**Right**

```markdown
Run `devices sync-from`. Verify the device reaches sync-result `true`.
```

**Wrong**

```markdown
Now you will run `devices sync-from`, and we'll check that sync-result is true.
```

**Lint:** — (reviewer / FR42)

### CLI prompts are literal: `user@ncs>` — never `$` or `>`

**Right**

```markdown
At the `user@ncs>` prompt, run `show devices list`.
```

**Wrong**

```markdown
At `$` run `show devices list`.
```

**Lint:** — (reviewer); **rule 4c** will reject `$` / `>` *inside* command fences when rules 4–7 are enforced.

### Cisco capitalization: NSO, NED, CLI, YANG (all caps); command names in backticks every time

**Right**

```markdown
Use the NSO CLI to commit the YANG-backed change. Run `commit dry-run` first.
```

**Wrong**

```markdown
Use the Nso cli to commit the yang change.
```

**Lint:** — (reviewer)

### Banned: "As you know…" and assumed prior knowledge

**Right**

```markdown
If you have not completed Lab 3, stop and finish it before this step.
```

**Wrong**

```markdown
As you know, NSO stores configuration in CDB.
```

**Lint:** — (reviewer)

---

## Density rules (UX-DR28)

**Limits:** ≤ **3** sentences per paragraph; ≤ **5** paired command/output blocks per `## Procedure` subsection; blank line between paired blocks and the next step or `## Common Errors`.

**Right** (short paragraph; one paired block; blank line before next step)

> Sync devices from NSO. Run `devices sync-from`.  
> Show `result true` in the sync summary before you continue.

**Wrong** (one overloaded paragraph; violates ≤ 3 sentences and hurts scanning)

> Sync is important because it pulls config and you should always sync before commit and if sync fails you need to check the trace and also verify NED versions because mismatches cause errors and then commit might not work.

**Lint:** prose density warnings planned; not in rules 1–3.

---

## Callout scarcity (UX-DR29)

- **Lab-safety banner:** only **home** and **Lab 8** (architecture / UX-DR29).
- **`!!! danger`:** ≤ **1** per lab.
- **`!!! warning`:** ≤ **3** per lab.
- **`!!! note` / `!!! tip`:** allowed without a hard cap (still subject to density).

**Right**

```markdown
!!! warning "Data loss risk"
    This commit cannot be rolled back automatically.
```

**Wrong**

```markdown
!!! danger "Minor note"
    Casual over-use of danger callouts trains learners to ignore them.
```

**Lint:** — (reviewer until rule 11 extended).

---

## Allowed admonition types (UX-DR16)

Only these Material types are allowed in v1.0 (architecture Pattern 1). **Lint rule 11** will enforce the allow-list.

| Type | Use |
|------|-----|
| `!!! note` | Factual clarification |
| `!!! info` | Reference / side detail |
| `!!! tip` | Shortcut or better workflow |
| `!!! warning` | Could cause data loss or break the lab |
| `!!! danger` | Will break the lab or host |
| `!!! example` | Worked example |
| `!!! question` | Reflection question |
| `!!! tip "Instructor"` inside an instructor `if` / `endif` block | Instructor-only hint (≤5 lines) |

**Banned** unless added by PR with semantics: `quote`, `abstract`, `failure`, `success`, `bug`, etc.

**Right**

```markdown
!!! tip "Faster path"
    Use `commit dry-run` before every commit.
```

**Wrong**

```markdown
!!! success "You did it!"
    Great job.
```

**Lint:** **rule 11** (Story 2.6).

---

## Code and expected-output pattern (UX-DR17)

Every command block uses a **language-tagged** fence (`cli`, `bash`, `shell`, …). Immediately after (ignoring blank lines), provide an italic **\*Expected output:\*** label and a `text` or `console` fence — **or** place `<!-- lint-skip: no-output -->` before the block to opt out.

**Right**

```markdown
```cli
show devices list
```

*Expected output:*

```text
NAME    ADDRESS
xr-1    192.0.2.1
```
```

**Wrong**

```markdown
```cli
show devices list
```

(No labelled output fence — learners cannot distinguish input from output.)
```

**Lint:** **rules 4a–4c**, **rule 7** (Story 2.4).

### Paired rendering + landmark hint (Story 3.3)

The build wraps each **command fence → *Expected output:* → output fence** sequence into a **paired** block (shared border, label bar, copy on the command half only). Optionally, on the line **before** *Expected output:*, add:

{% raw %}
`{{ expected_output(landmark="commit complete") }}`
{% endraw %}

Use a short **landmark** string (≤ 60 characters) learners should look for in the output. **Lint rule 4d** requires a non-empty `landmark="..."` whenever `expected_output` is used.

---

## Idempotency and rollback

Frontmatter `idempotent: true|false` (see `docs/_template/schema.yaml`). If `idempotent: false`, the chapter **must** include a rollback admonition (typically under `## Common Errors` or end of `## Procedure`) with the exact commands to restore prior state — **Story 2.6** lint will enforce pairing.

**Right**

```markdown
idempotent: false
```

…and later a `!!! warning "Rollback"` with the `rollback` / `revert` sequence for this lab.

**Wrong**

```markdown
idempotent: false
```

…with no rollback instructions anywhere in the chapter.

**Lint:** extended rule under Story 2.6.

---

## Screenshots and diagrams

**Binding reference:** **`docs/scrub-protocol.md`** (Epic 4 Story 4.1) — scope, identifiers to remove vs permitted lab names and RFC 5737 ranges, scrub tools, worked example assets under `docs/assets/images/scrub-example/`, author self-review, and second-pair review (NFR-S6). Log per-chapter passes under **`docs/scrub-logs/NN.md`**; second-pair sign-off in **`docs/scrub-logs/second-pair-review.md`**.

**Lint:** **rule 5** (Story 2.5) requires alt text and Mermaid/title conventions; rule 5 messages for empty image alt point at the scrub protocol for screenshot hygiene.

---

## Commit conventions

Use **Conventional Commits** (`feat:`, `fix:`, `docs:`, `ci:`, …) and scoped subjects where helpful. Full policy and CI wiring land in **Story 2.7**.

**Right:** `docs: clarify verification steps in Lab 4`  
**Wrong:** `updates`

---

## Instructor-only content (Epic 5)

Dual-audience builds use three mechanisms (AR5):

| Mechanism | Where | Learner `site/` |
|-----------|--------|-----------------|
| **Inline** Jinja instructor gate (`if instructor` … `endif`) | Inside `docs/NN-*.md` | Block omitted when `instructor` is false (macros env) |
| **Companion** `docs/NN-*-instructor-notes.md` | Next to the lab file | File **omitted** from the build (`hooks.py` `on_files`) |
| **Shared facilitator docs** `docs/instructor-artifacts/**` | e.g. `proctor-checklist.md`, `timing-sheet.md` (Stories 5.4–5.5; instructor site only) | **Omitted** from learner builds |

`make build-learner` and default `mkdocs serve` exclude companion paths and `instructor-artifacts/`. **`make build-instructor`** sets `INSTRUCTOR=1` and includes them in `site-instructor/`.

**`instructor_block` macro (UX-DR12, Story 5.3)** — use for pacing, FAQs, and Lab 8 choreography inside a lab chapter. Pass facilitator copy as markdown in the `body` argument (Jinja allows multiline strings). **`variant`** is `generic` (default) or `choreography` (Lab 8 extended script). When `instructor` is false, the macro expands to **nothing** (no empty wrapper, no hidden DOM). Styling lives in `docs/stylesheets/components/instructor-block.css`; the macro output includes a stable data attribute used by `make build-all` smoke checks (lab + `_test-fixtures/` HTML only).

**Right (instructor_block)**

```jinja
{{ instructor_block(variant="generic", body="### FAQs\n- …\n- …\n\n### What breaks\n- …") }}
```

```jinja
{{ instructor_block(variant="choreography", body="### Pause points\n…\n\n### Narrating check-sync\n…") }}
```

**Wrong (instructor_block)**

Putting facilitator-only guidance in plain chapter prose with no gate or macro.

### UX-DR30 minimum content per chapter

**Lint rule 12** (Story 5.7) enforces these minimums in every lab chapter `docs/NN-*.md` (warn-first; see `docs/lint-cutover-plan.md`).

| Requirement | Where | Notes |
|-------------|--------|--------|
| **Expected duration** | Chapter frontmatter (`estimated_duration` / schema) | Already part of the lab contract; not duplicated inside the macro body. |
| **Two learner FAQs** | Inside `instructor_block(variant="generic", …)` | Use a `### FAQs` sub-heading with **at least two** bullet lines (`-` or `*`). |
| **One thing that breaks** | Same generic block | Use `### What breaks` with **at least one** bullet. |
| **Lab 8 only: choreography** | Second macro: `instructor_block(variant="choreography", …)` | Requires `chapter: 8` in frontmatter. Body uses `### Pause points`, `### Narrating check-sync`, and `### Red-to-green flip`, each with facilitator content (bullets recommended). |

**Example — generic block**

```jinja
{{ instructor_block(variant="generic", body="### FAQs\n- Why does sync stall here?\n- Where do I confirm commit-queue depth?\n\n### What breaks\n- Stale template if the service rename is skipped.\n") }}
```

**Example — Lab 8 generic + choreography**

```jinja
{{ instructor_block(variant="generic", body="### FAQs\n- …\n- …\n\n### What breaks\n- …") }}

{{ instructor_block(variant="choreography", body="### Pause points\n- After deploy: pause for questions.\n\n### Narrating check-sync\n- Explain why check-sync may churn while the trace warms up.\n\n### Red-to-green flip\n- Narrate moving from failed commit to green verification.\n") }}
```

**Right (inline `if instructor`)**

{% raw %}
```markdown
{% if instructor %}
!!! tip "Instructor"
    Allow 5 extra minutes if the class hit sync issues in Lab 2.
{% endif %}
```
{% endraw %}

**Wrong**

```markdown
Facilitators: skip this section in a 90-minute session.
```

*(Learner-visible facilitator instruction with no gate.)*

Do not put facilitator-only timing or answers in learner-visible prose without a gate. Details: **AR5**, Epic 5 stories 5.1–5.3, **lint rule 12** (Story 5.7).

---

## Quick reference: run checks locally

```bash
make build-learner
make build-all          # learner + instructor static sites (Story 5.2)
make serve-instructor   # optional: live reload with facilitator paths (default :8001)
make lint
# Full fail-mode dry run (same as CI strict cutover):
make lint-fail-all
```

Cutover sequencing and CI behavior: **`docs/lint-cutover-plan.md`**.

Unit tests for the linter:

```bash
python -m unittest scripts.tests.test_lint_authoring -v
```
