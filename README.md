# NSO Hands-On Training Workbook

Cisco Network Services Orchestrator (NSO) — Hands-On Lab Guide built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

Nine self-paced labs walk learners from first connection through service lifecycle and RBAC, all driven from the NSO Web UI and CLI on a hosted XRd lab environment.

| Lab | Topic |
|-----|-------|
| 1 | Connect to the Workstation |
| 2 | Install NSO and NEDs |
| 3 | Register XRd Routers |
| 4 | Configure Devices |
| 5 | Rollbacks |
| 6 | Out-of-Band Sync |
| 7 | Device Groups & Templates |
| 8 | Create a Service |
| 9 | RBAC Access Control |

## Prerequisites

- **Python 3.12+**
- **Node 20+** (only needed for CI quality gates — Lighthouse and axe)
- A terminal on macOS, Linux, or WSL

## Quick Start

```bash
git clone https://github.com/daquezad/NSO-hands-on-session.git
cd NSO-hands-on-session
pip install -r requirements.txt
make serve
```

Open <http://127.0.0.1:8000> in your browser. Changes to any `docs/*.md` file are picked up automatically with live reload.

## Make Targets

Run `make help` for the full list. The most useful ones:

| Target | What it does |
|--------|-------------|
| `make serve` | Live-reload dev server (learner site, port 8000) |
| `make serve-instructor` | Live-reload with facilitator content (`INSTRUCTOR=1`, port 8001) |
| `make build-learner` | Static build to `site/` (instructor content excluded) |
| `make build-instructor` | Static build to `site-instructor/` (all content) |
| `make build-all` | Both builds + dual-audience smoke test + leakage guard |
| `make pdf` | Learner PDF via print-site + Chromium to `dist/` |
| `make pdf-instructor` | Instructor PDF to `dist/` |
| `make lint` | Authoring lint (default: warn mode) |
| `make lint-fail-all` | Authoring lint with all rules in fail mode |
| `make ci-quality-gates` | Lighthouse, axe, perf budget, link checks (needs `npm ci` first) |
| `make clean` | Remove `site/` and `site-instructor/` |

## Updating Content

1. Edit any `.md` file under `docs/`.
2. Preview with `make serve`.
3. Commit, push, and open a PR against `main`.

PR titles must follow **Conventional Commits** (`type(scope): subject`) — see `CONTRIBUTING.md` for details and examples.

## Adding Images

Place images in the appropriate lab folder under `docs/assets/images/` and reference them with a relative path:

```markdown
![Alt text describing the screenshot](assets/images/lab04/webui-example.png)
```

Each lab chapter has its own subfolder (`lab01/`, `lab02/`, etc.).

## Deployment

Pushing to `main` triggers GitHub Actions:

1. **`build.yml`** — full CI (lint, learner + instructor builds, PDF, accessibility, quality gates).
2. **`deploy.yml`** — after a green build on `main`, deploys the versioned site to GitHub Pages via `mike`.
3. **`release.yml`** — on a `v*` tag, creates a GitHub Release with the PDF and changelog.

To cut a release:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Pages are deployed to the `gh-pages` branch using `mike` for versioned documentation. Set **Deploy from a branch** → `gh-pages` → `/(root)` in your repo's Pages settings.

## Repository Layout

```text
docs/                        Markdown source (11 labs + index + support pages)
  assets/images/             Screenshots per lab (lab01/ … lab11/)
  assets/images/mermaid/     Pre-rendered topology diagrams (SVG + PNG)
  assets/mermaid-sources/    Mermaid .mmd sources
  assets/fonts/              Bundled fonts for offline rendering
  stylesheets/extra.css      Cisco-branded design tokens
  _internal/                 Internal docs (not published)
overrides/                   Material theme Jinja2 overrides (banner, footer)
macros/main.py               Jinja2 macros (expected_output, time_budget, etc.)
main.py                      mkdocs-macros shim — loads macros/main.py
hooks.py                     MkDocs build hooks (paired output, image optimization, a11y)
scripts/                     Build helpers (lint, PDF, quality gates, CI checks)
  ci/                        CI-specific scripts (axe, veraPDF, Lighthouse, etc.)
  tests/                     Unit tests for build scripts
.github/workflows/           CI/CD (build, deploy, release)
.github/actions/             Shared setup action (Python, Node, deps)
Makefile                     Developer targets (serve, build, lint, pdf, etc.)
mkdocs.yml                   MkDocs configuration
requirements.txt             Python dependencies (exact-pinned)
package.json                 Node dependencies (Lighthouse, axe-core)
CONTRIBUTING.md              Full contributor guide (make targets, lint, commits, PDF)
```

## License

Cisco Confidential. Internal use only.
