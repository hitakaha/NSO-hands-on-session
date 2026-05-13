"""mkdocs-macros — Story 3.1: nso_version; 3.3: expected_output; 3.4–3.6: primitives + home cover; 5.3: instructor_block; 5.5: timing_sheet."""

from __future__ import annotations

import logging
import os
import re
from html import escape
from pathlib import Path

import yaml
from markdown import markdown as _md_fragment

_LOG = logging.getLogger(__name__)

# Story 3.6 — lab journey (minutes align with chapter time_budget ribbons)
_JOURNEY_LABS: tuple[dict[str, object], ...] = (
    {
        "n": 1,
        "file": "01-connect-workstation.md",
        "title": "Connect to the Workstation",
        "min": 10,
        "desc": "Access the lab VM and terminal",
        "intentional": False,
    },
    {
        "n": 2,
        "file": "02-install-nso-neds.md",
        "title": "Install NSO and NEDs",
        "min": 35,
        "desc": "Local NSO install, environment, IOS-XR NED",
        "intentional": False,
    },
    {
        "n": 3,
        "file": "03-register-xrd-routers.md",
        "title": "Register XRd Routers",
        "min": 20,
        "desc": "Device definitions and sync-from",
        "intentional": False,
    },
    {
        "n": 4,
        "file": "04-configure-devices.md",
        "title": "Configure Devices",
        "min": 20,
        "desc": "Push changes via NSO Web UI",
        "intentional": False,
    },
    {
        "n": 5,
        "file": "05-rollbacks.md",
        "title": "Rollbacks",
        "min": 20,
        "desc": "Rollback files and revert commits",
        "intentional": False,
    },
    {
        "n": 6,
        "file": "06-out-of-band-sync.md",
        "title": "Out-of-Band Sync",
        "min": 20,
        "desc": "Detect and reconcile OOB changes",
        "intentional": False,
    },
    {
        "n": 7,
        "file": "07-device-groups-templates.md",
        "title": "Device Groups & Templates",
        "min": 25,
        "desc": "Groups and templates at scale",
        "intentional": False,
    },
    {
        "n": 8,
        "file": "08-create-service.md",
        "title": "Create a Service",
        "min": 30,
        "desc": "Python-and-template service package",
        "intentional": True,
    },
    {
        "n": 9,
        "file": "09-rbac-access-control.md",
        "title": "RBAC Access Control",
        "min": 30,
        "desc": "Users, authgroups, NACM rules",
        "intentional": False,
    },
    {
        "n": 10,
        "file": "10-nso-mcp-setup.md",
        "title": "NSO MCP — Setup and First Client",
        "min": 80,
        "desc": "NSO 6.7 + MCP server, web client, policy permit",
        "intentional": False,
    },
    {
        "n": 11,
        "file": "11-nso-mcp-services-bgp.md",
        "title": "NSO MCP — Service Models and BGP",
        "min": 70,
        "desc": "Load bgpmgr, configure BGP via natural language",
        "intentional": False,
    },
)

_DURATION_RE = re.compile(r"^(\d+)\s*min$")


def _docs_lab_chapter_paths(docs_dir: Path) -> list[Path]:
    """Lab chapters: `NN-*.md` excluding companion `*-instructor-notes.md` (Story 5.5)."""
    out: list[Path] = []
    for p in sorted(docs_dir.glob("[0-9][0-9]-*.md")):
        if p.name.endswith("-instructor-notes.md"):
            continue
        out.append(p)
    return out


def _read_yaml_frontmatter(path: Path) -> dict[str, object]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}
    if not lines or lines[0].strip() != "---":
        return {}
    fm_lines: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        fm_lines.append(line)
    block = "\n".join(fm_lines)
    try:
        data = yaml.safe_load(block)
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def define_env(env):
    """Wire mkdocs.yml `extra` keys; register macros."""
    extra = env.conf.get("extra") or {}
    env.variables["nso_version"] = str(extra.get("nso_version", ""))
    # Dual-audience builds (`make build-instructor` sets INSTRUCTOR=1) — Epic 5 AR5
    env.variables["instructor"] = os.environ.get("INSTRUCTOR", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )

    @env.macro
    def expected_output(landmark: str = "", **kwargs: object) -> str:
        """Landmark marker for paired blocks (Story 3.3)."""
        lm = str(landmark).strip()[:60]
        if not lm:
            return "<!-- expected_output: missing landmark= -->"
        return f'<span class="paired-landmark" data-landmark="{escape(lm, quote=True)}"></span>'

    def _norm_segments(segments: object) -> list[tuple[int, str]]:
        out: list[tuple[int, str]] = []
        if segments is None:
            return out
        if not isinstance(segments, (list, tuple)):
            return out
        for item in segments:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                try:
                    m = int(item[0])
                except (TypeError, ValueError):
                    continue
                label = str(item[1]).strip()
                out.append((m, label))
        return out

    @env.macro
    def time_budget(total: int = 0, segments: object = None, **kwargs: object) -> str:
        """
        Time-budget ribbon (Story 3.4). Use list-of-pairs segments, e.g.:
        {{ time_budget(total=30, segments=[[5,"setup"],[20,"build"],[5,"verify"]]) }}
        """
        segs = _norm_segments(segments if segments is not None else kwargs.get("segments"))
        try:
            t = int(total)
        except (TypeError, ValueError):
            t = 0
        if t <= 0 or not segs:
            return (
                '<p class="css-macro-error"><strong>time_budget</strong>: '
                "need positive <code>total</code> and non-empty <code>segments</code>.</p>"
            )
        ssum = sum(m for m, _ in segs)
        if ssum != t:
            return (
                f'<p class="css-macro-error"><strong>time_budget</strong>: segment minutes sum to '
                f"{ssum}, but <code>total</code> is {t}.</p>"
            )
        parts = [f"{lab} {m} min" for m, lab in segs]
        aria = f"Estimated time: {t} minutes total — " + ", ".join(parts)
        aria_esc = escape(aria, quote=True)
        seg_html: list[str] = []
        legend: list[str] = []
        palette = ("seg--a", "seg--b", "seg--c", "seg--d")
        for i, (mins, lab) in enumerate(segs):
            cls = palette[i % len(palette)]
            seg_html.append(
                f'<div class="css-time-budget__seg {cls}" style="flex:{mins}">'
                f'<span class="css-time-budget__seg-label">{escape(lab)}</span></div>'
            )
            legend.append(
                f'<li><span class="css-time-budget__swatch {cls}"></span>'
                f"{escape(lab)} — {mins} min</li>"
            )
        inner = (
            f'<div class="css-time-budget" role="img" aria-label="{aria_esc}">'
            f'<div class="css-time-budget__ribbon">{"".join(seg_html)}</div>'
            f'<ul class="css-time-budget__legend">{"".join(legend)}</ul>'
            f'<p class="css-time-budget__total"><strong>Total</strong> — {t} min</p></div>'
        )
        return inner

    def _truncate_words(text: str, max_words: int) -> str:
        w = text.split()
        if len(w) <= max_words:
            return text.strip()
        return " ".join(w[:max_words]).rstrip() + "…"

    @env.macro
    def common_errors_start(**kwargs: object) -> str:
        return '<div class="css-common-errors" role="region" aria-label="Common errors">'

    @env.macro
    def common_errors_end(**kwargs: object) -> str:
        return "</div>"

    @env.macro
    def common_error(symptom: str = "", cause: str = "", fix: str = "", **kwargs: object) -> str:
        """One collapsible card; first card opened via common-errors.js (Story 3.4)."""
        sy = _truncate_words(str(symptom), 12)
        ca = _truncate_words(str(cause), 25)
        fx = _truncate_words(str(fix), 40)
        return (
            '<details class="css-common-error">'
            f'<summary class="css-common-error__summary">Symptom: {escape(sy)}</summary>'
            f'<div class="css-common-error__body">'
            f'<p class="css-common-error__cause"><strong>Cause</strong> {escape(ca)}</p>'
            f'<p class="css-common-error__fix"><strong>Fix</strong> {escape(fx)}</p>'
            f"</div></details>"
        )

    @env.macro
    def lab_safety(variant: str = "general", **kwargs: object) -> str:
        """
        In-page lab safety banner (Story 3.4). Content from mkdocs.yml extra.LAB_SAFETY_MESSAGE.
        Placement: index → general; Lab 8 → intentional_failure (enforced by lint rule 11).
        """
        msg = str(extra.get("LAB_SAFETY_MESSAGE") or "").strip()
        if not msg:
            return "<!-- lab_safety: LAB_SAFETY_MESSAGE empty in mkdocs.yml -->"
        v = str(variant).strip().lower()
        if v not in ("general", "intentional_failure"):
            v = "general"
        titles = {
            "general": "Lab safety",
            "intentional_failure": "Intentional failure lab",
        }
        title = titles.get(v, titles["general"])
        mod = f" css-lab-safety--{v}"
        return (
            f'<aside class="css-lab-safety{mod}" role="status" '
            f'aria-label="{escape(title + " — " + msg, quote=True)}">'
            f'<span class="css-lab-safety__glyph" aria-hidden="true">&#9888;</span>'
            f'<div class="css-lab-safety__text">'
            f'<strong class="css-lab-safety__title">{escape(title)}</strong> '
            f'<span class="css-lab-safety__body">{escape(msg)}</span>'
            f"</div></aside>"
        )

    @env.macro
    def topology(
        diagram_id: str = "",
        chapter: str = "index",
        caption: str = "",
        **kwargs: object,
    ) -> str:
        """
        Pre-rendered topology (Story 3.5). Assets under docs/assets/images/mermaid/<chapter>/.
        Alt text: <diagram_id>.alt.txt next to the SVG/PNG outputs.
        """
        did = str(diagram_id).strip()
        ch = str(chapter).strip() or "index"
        if not did:
            return (
                '<p class="css-macro-error"><strong>topology</strong>: '
                "pass <code>diagram_id=\"…\"</code></p>"
            )
        docs_dir = Path(env.conf.get("docs_dir") or ".")
        alt_path = docs_dir / "assets" / "images" / "mermaid" / ch / f"{did}.alt.txt"
        svg_rel = f"assets/images/mermaid/{ch}/{did}.svg"
        alt_text = f"Network topology {did}"
        if alt_path.is_file():
            alt_text = alt_path.read_text(encoding="utf-8").strip().split("\n", 1)[0].strip()
        if len(alt_text) > 500:
            alt_text = alt_text[:497] + "…"
        cap = str(caption).strip() or "Reference topology"
        alt_esc = escape(alt_text, quote=True)
        cap_esc = escape(cap)
        return (
            f'<figure class="css-topology" role="group">'
            f'<img class="css-topology__img" src="{svg_rel}" alt="{alt_esc}" '
            f'loading="lazy" decoding="async" />'
            f'<figcaption class="css-topology__caption">{cap_esc}</figcaption>'
            f"</figure>"
        )

    @env.macro
    def home_subtitle(text: str = "", **kwargs: object) -> str:
        """One-line audience/subtitle under the H1 (Story 3.6)."""
        t = str(text).strip()
        if not t:
            return '<p class="css-macro-error"><strong>home_subtitle</strong>: pass <code>text="…"</code></p>'
        return f'<p class="css-home-subtitle md-typeset">{escape(t)}</p>'

    @env.macro
    def home_meta(**kwargs: object) -> str:
        """Session summary row: total time, lab count, NSO sandbox version (Story 3.6)."""
        total_min = sum(int(r["min"]) for r in _JOURNEY_LABS)
        h = total_min // 60
        m = total_min % 60
        if h and m:
            time_s = f"{h} h {m} min"
        elif h:
            time_s = f"{h} h"
        else:
            time_s = f"{m} min"
        ver = str(extra.get("nso_version") or "").strip() or "—"
        lab_count = len(_JOURNEY_LABS)
        aria = f"About {time_s} total, {lab_count} labs, NSO {ver} sandbox"
        return (
            f'<div class="css-home-meta" role="group" aria-label="{escape(aria, quote=True)}">'
            f'<span class="css-home-meta__item"><strong>Time</strong> ~{escape(time_s)} total</span>'
            f'<span class="css-home-meta__sep" aria-hidden="true">·</span>'
            f'<span class="css-home-meta__item"><strong>Labs</strong> {lab_count} hands-on</span>'
            f'<span class="css-home-meta__sep" aria-hidden="true">·</span>'
            f'<span class="css-home-meta__item"><strong>NSO</strong> {escape(ver)} (sandbox)</span>'
            f"</div>"
        )

    @env.macro
    def journey_table(**kwargs: object) -> str:
        """
        Accessible lab journey table (Story 3.6). Stacked cards on narrow viewports (UX-DR26).
        """
        rows_html: list[str] = []
        for r in _JOURNEY_LABS:
            n = int(r["n"])
            fn = str(r["file"])
            # Built site uses pretty URLs (chapter dir/); not source .md paths
            href = fn[:-3] + "/" if fn.endswith(".md") else fn
            title = str(r["title"])
            mins = int(r["min"])
            desc = str(r["desc"])
            intentional = bool(r["intentional"])
            chip = ""
            if intentional:
                chip = (
                    '<span class="css-journey-chip" title="This lab includes an intentional failure path">'
                    "intentional break</span> "
                )
            row_cls = " css-journey-row--intentional" if intentional else ""
            desc_html = chip + escape(desc)
            rows_html.append(
                f'<tr class="css-journey-tr{row_cls}">'
                f'<th scope="row" data-label="Lab #">{n}</th>'
                f'<td data-label="Title"><a href="{escape(href)}">{escape(title)}</a></td>'
                f'<td data-label="Time">{mins} min</td>'
                f'<td data-label="Description">{desc_html}</td>'
                f"</tr>"
            )
        body = "\n".join(rows_html)
        return (
            '<div class="css-journey-shell">'
            '<table class="css-journey-table">'
            '<caption class="css-journey-caption">Hands-on lab journey</caption>'
            "<thead><tr>"
            '<th scope="col">Lab</th>'
            '<th scope="col">Title</th>'
            '<th scope="col">Time</th>'
            '<th scope="col">Description</th>'
            "</tr></thead>"
            f"<tbody>{body}</tbody>"
            "</table></div>"
        )

    def _instructor_markdown_to_html(fragment: str) -> str:
        """Convert facilitator-authored markdown inside instructor_block (trusted repo content)."""
        return _md_fragment(fragment.strip(), extensions=["markdown.extensions.extra"])

    @env.macro
    def instructor_block(variant: str = "generic", body: str = "") -> str:
        """
        Facilitator-only panel (UX-DR12). Expands to nothing when `instructor` is false (FR28).
        Pass markdown in `body` (multiline string in Jinja is OK).
        """
        if not env.variables.get("instructor"):
            return ""
        text = str(body)
        v = str(variant).strip().lower()
        if v not in ("generic", "choreography"):
            v = "generic"
        if v == "choreography":
            mod = " instructor-notes--choreography"
            aria = "Instructor notes: choreography"
        else:
            mod = " instructor-notes--generic"
            aria = "Instructor notes"
        inner = _instructor_markdown_to_html(text) if text.strip() else ""
        aria_esc = escape(aria, quote=True)
        return (
            f'<div class="instructor-notes{mod}" role="complementary" '
            f'aria-label="{aria_esc}" data-instructor-block="ux-dr-12">'
            '<h3 class="instructor-notes__title md-typeset">👩‍🏫 Instructor notes</h3>'
            f'<div class="instructor-notes__body md-typeset">{inner}</div>'
            f"</div>"
        )

    @env.macro
    def timing_sheet(**kwargs: object) -> str:
        """
        Per-lab timing table from chapter frontmatter (Story 5.5, AR14).
        Used on `instructor-artifacts/timing-sheet.md` (omitted from learner builds).
        """
        docs_dir = Path(env.conf.get("docs_dir") or "docs")
        collected: list[dict[str, object]] = []
        for path in _docs_lab_chapter_paths(docs_dir):
            fm = _read_yaml_frontmatter(path)
            ch = fm.get("chapter")
            try:
                ch_sort = int(ch) if ch is not None else 999
            except (TypeError, ValueError):
                ch_sort = 999
            ch_s = str(int(ch)) if isinstance(ch, int) else (str(ch).strip() if ch is not None else "")
            title = str(fm.get("title") or "").strip()
            ed = fm.get("estimated_duration")
            note_raw = fm.get("instructor_pace_note")
            note_html = "—"
            if isinstance(note_raw, str) and note_raw.strip():
                note_html = escape(note_raw.strip()).replace("\n", "<br/>")

            dur_disp = "—"
            mins: int | None = None
            if isinstance(ed, str):
                m = _DURATION_RE.match(ed.strip())
                if m:
                    mins = int(m.group(1))
                    dur_disp = f"{mins} min"
                else:
                    dur_disp = escape(ed.strip())
            if mins is None:
                if ed is not None:
                    _LOG.warning("timing_sheet: %s has invalid or missing parsed estimated_duration %r", path.name, ed)
                else:
                    _LOG.warning("timing_sheet: %s missing estimated_duration", path.name)

            collected.append(
                {
                    "ch_sort": ch_sort,
                    "ch_s": ch_s,
                    "title": escape(title),
                    "dur_disp": dur_disp,
                    "mins": mins,
                    "note": note_html,
                    "path": path.name,
                }
            )

        collected.sort(key=lambda x: int(x["ch_sort"]) if isinstance(x["ch_sort"], int) else 999)

        cumulative = 0
        body_rows: list[str] = []
        for item in collected:
            mins = item["mins"]
            if isinstance(mins, int):
                cumulative += mins
                run_disp = f"{cumulative} min"
            else:
                run_disp = "—"

            body_rows.append(
                "<tr>"
                f'<th scope="row">{item["ch_s"]}</th>'
                f'<td>{item["title"]}</td>'
                f'<td>{item["dur_disp"]}</td>'
                f"<td>{run_disp}</td>"
                f'<td>{item["note"]}</td>'
                "</tr>"
            )

        grand_total = sum(int(x["mins"]) for x in collected if isinstance(x["mins"], int))
        total_disp = f"{grand_total} min" if grand_total else "—"
        foot = (
            "<tr>"
            '<th scope="row">Total</th>'
            "<td>—</td>"
            f"<td><strong>{total_disp}</strong></td>"
            f"<td><strong>{total_disp}</strong></td>"
            "<td>—</td>"
            "</tr>"
        )

        cap = "Expected durations from each lab chapter frontmatter (AR14); running total is cumulative."
        return (
            '<div class="css-timing-sheet" role="region" '
            f'aria-label="{escape(cap, quote=True)}">'
            '<table class="css-timing-sheet__table">'
            "<thead><tr>"
            '<th scope="col">Chapter</th>'
            '<th scope="col">Title</th>'
            '<th scope="col">Expected duration</th>'
            '<th scope="col">Running total</th>'
            '<th scope="col">Instructor pace notes</th>'
            "</tr></thead>"
            f"<tbody>{''.join(body_rows)}</tbody>"
            f"<tfoot>{foot}</tfoot>"
            "</table></div>"
        )

    return
