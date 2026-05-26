#!/usr/bin/env python3
"""
Story 6.2 — Build learner (or instructor) PDF from mkdocs-print-site output + Chromium, with WeasyPrint fallback (AR6).
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_finalize_accessibility():
    import importlib.util

    path = REPO_ROOT / "scripts" / "pdf_finalize_accessibility.py"
    spec = importlib.util.spec_from_file_location("pdf_finalize_accessibility", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.finalize_print_pdf


def read_nso_version() -> str:
    import re

    import yaml

    vf = REPO_ROOT / "_data" / "versions.yaml"
    if vf.is_file():
        data = yaml.safe_load(vf.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("nso_version"):
            return str(data["nso_version"]).strip()
    mk = (REPO_ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    m = re.search(r"nso_version:\s*[\"']?([^\"'\\s]+)", mk)
    if m:
        return m.group(1).strip()
    raise SystemExit("Cannot resolve nso_version from _data/versions.yaml or mkdocs.yml")


def find_chrome() -> str | None:
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        found = shutil.which(name)
        if found:
            return found
    mac = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if mac.is_file():
        return str(mac)
    return None


def run_mkdocs(site_dir: str, *, instructor: bool) -> None:
    env = os.environ.copy()
    if instructor:
        env["INSTRUCTOR"] = "1"
    cmd = [sys.executable, "-m", "mkdocs", "build", "--strict", f"--site-dir={site_dir}"]
    subprocess.run(cmd, cwd=REPO_ROOT, env=env, check=True)


def print_site_html(site_dir: Path) -> Path:
    p = site_dir / "print_page" / "index.html"
    if p.is_file():
        return p
    alt = site_dir / "print_page.html"
    if alt.is_file():
        return alt
    raise FileNotFoundError(f"print-site HTML not found under {site_dir} (expected print_page/index.html)")


def chromium_print(html_path: Path, pdf_out: Path, chrome: str) -> int:
    url = html_path.resolve().as_uri()
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_out}",
        url,
    ]
    r = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr or r.stdout or "chromium: non-zero exit", file=sys.stderr)
    return r.returncode


def weasyprint_pdf(html_path: Path, pdf_out: Path) -> None:
    """Fallback engine (AR6). Prefer standalone CLI when present; else Python API (needs GTK/Pango on some hosts)."""
    cli = shutil.which("weasyprint")
    if cli:
        subprocess.run([cli, str(html_path), str(pdf_out)], cwd=REPO_ROOT, check=True)
        return
    try:
        from weasyprint import HTML
    except ImportError as e:
        raise RuntimeError(
            "WeasyPrint is not available: install `weasyprint` on PATH (recommended on macOS: `brew install weasyprint`) "
            "or `pip install weasyprint` with GTK/Pango — see "
            "https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation (AR6 fallback)."
        ) from e
    try:
        HTML(filename=str(html_path)).write_pdf(str(pdf_out))
    except OSError as e:
        raise RuntimeError(
            "WeasyPrint could not load native libraries (GTK/Pango). Use Chromium primary path, install OS deps for WeasyPrint, "
            "or run the fallback check on Linux CI where `pip install weasyprint` is supported."
        ) from e


def normalize_pdf_metadata(src: Path, dst: Path) -> None:
    """Copy PDF pages and set fixed metadata dates for reproducibility checks (NFR-R1)."""
    reader = PdfReader(str(src))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    fixed = "D:20200101000000+00'00'"
    writer.add_metadata(
        {
            "/Creator": "nso-workbook-pdf-build",
            "/Producer": "nso-workbook-pdf-build",
            "/CreationDate": fixed,
            "/ModDate": fixed,
        }
    )
    with open(dst, "wb") as f:
        writer.write(f)


def sha256_normalized(path: Path) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tpath = Path(tmp.name)
    try:
        normalize_pdf_metadata(path, tpath)
        return hashlib.sha256(tpath.read_bytes()).hexdigest()
    finally:
        tpath.unlink(missing_ok=True)


def run_leak_check_pdf(pdf_path: Path) -> int:
    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "check_instructor_leak.py"), "--pdf", str(pdf_path)],
        cwd=REPO_ROOT,
    )
    return r.returncode


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Build PDF from mkdocs print-site HTML (Story 6.2).")
    p.add_argument("--site-dir", default="site", help="MkDocs output directory (default: site)")
    p.add_argument(
        "--output",
        default="",
        help="Output PDF path (default: dist/cisco-nso-hands-on-training-workbook-{version}.pdf)",
    )
    p.add_argument("--instructor", action="store_true", help="INSTRUCTOR=1 build → site-instructor by default")
    p.add_argument("--skip-build", action="store_true", help="Assume mkdocs build already ran")
    p.add_argument("--skip-leak-check", action="store_true", help="Do not scan PDF text for instructor leakage")
    args = p.parse_args(argv)

    instructor = args.instructor
    site_rel = args.site_dir
    if instructor and args.site_dir == "site":
        site_rel = "site-instructor"

    site_path = REPO_ROOT / site_rel
    ver = read_nso_version()
    if args.output:
        out = Path(args.output)
        if not out.is_absolute():
            out = REPO_ROOT / out
    else:
        suffix = "-instructor" if instructor else ""
        out = REPO_ROOT / "dist" / f"cisco-nso-hands-on-training-workbook-{ver}{suffix}.pdf"

    out.parent.mkdir(parents=True, exist_ok=True)

    if not args.skip_build:
        run_mkdocs(site_rel, instructor=instructor)

    html_path = print_site_html(site_path)
    chrome = find_chrome()
    force_fail = os.environ.get("PDF_ENGINE_FORCE_FAIL", "").strip().lower() in ("1", "true", "yes")

    tmp_pdf = out.with_suffix(".tmp.pdf")
    if tmp_pdf.exists():
        tmp_pdf.unlink()

    used_fallback = False

    try:
        if force_fail:
            print(
                "WARNING: PDF_ENGINE_FORCE_FAIL is set — skipping Chromium and using WeasyPrint fallback.",
                file=sys.stderr,
            )
            weasyprint_pdf(html_path, tmp_pdf)
            used_fallback = True
        elif not chrome:
            print("ERROR: Chromium/Chrome not found on PATH.", file=sys.stderr)
            print("WARNING: Attempting WeasyPrint fallback on print-site HTML…", file=sys.stderr)
            weasyprint_pdf(html_path, tmp_pdf)
            used_fallback = True
        else:
            rc = chromium_print(html_path, tmp_pdf, chrome)
            ok = rc == 0 and tmp_pdf.is_file() and tmp_pdf.stat().st_size > 0
            if not ok:
                print(
                    "WARNING: Chromium print-to-pdf failed or produced empty output; trying WeasyPrint fallback…",
                    file=sys.stderr,
                )
                if tmp_pdf.exists():
                    tmp_pdf.unlink()
                weasyprint_pdf(html_path, tmp_pdf)
                used_fallback = True

        shutil.move(str(tmp_pdf), str(out))
    except Exception:
        if tmp_pdf.exists():
            tmp_pdf.unlink(missing_ok=True)
        raise

    if used_fallback:
        print("WARNING: PDF was generated using the secondary engine (WeasyPrint), not Chromium.", file=sys.stderr)

    if os.environ.get("PDF_SKIP_A11Y", "").strip().lower() not in ("1", "true", "yes"):
        finalize = _load_finalize_accessibility()
        stats = finalize(
            out,
            print_html=html_path,
            mkdocs_yml=REPO_ROOT / "mkdocs.yml",
        )
        print(f"pdf_build: accessibility finalize — {stats}")
    else:
        print("WARNING: PDF_SKIP_A11Y is set — skipping Story 6.4 bookmark/metadata finalize.", file=sys.stderr)

    digest = sha256_normalized(out)
    print(f"pdf_build: wrote {out.relative_to(REPO_ROOT)} (normalized SHA-256: {digest})")

    if not args.skip_leak_check and not instructor:
        code = run_leak_check_pdf(out)
        if code != 0:
            return code

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130) from None
