#!/usr/bin/env python3
"""Prepare drift-resistant per-page thesis critique prompts.

The tool does not call any LLM itself. It builds a small, immutable packet from a
single canonical PDF (`main.pdf` by default): manifest, per-page text extracts,
and one prompt per requested page. The prompt includes the exact PDF path,
SHA-256, page count, generated timestamp, and extracted page text, and explicitly
forbids agents from switching to stale sibling PDFs such as `loputoo.pdf`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
THESIS_DIR = REPO_ROOT / "docs" / "thesis" / "thesis-tex-estonian"
DEFAULT_PDF = THESIS_DIR / "main.pdf"
DEFAULT_OUT_ROOT = REPO_ROOT / ".hermes" / "thesis-page-critiques"
SOURCE_SUFFIXES = {".tex", ".bib", ".sty", ".cls", ".png", ".jpg", ".jpeg", ".pdf"}


def run(cmd: list[str], *, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True, check=check)


def require_cmd(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"missing required command: {name}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_page_count(pdf: Path) -> int:
    require_cmd("pdfinfo")
    proc = run(["pdfinfo", str(pdf)])
    for line in proc.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise SystemExit(f"could not parse page count from pdfinfo output for {pdf}")


def extract_page_text(pdf: Path, page: int) -> str:
    require_cmd("pdftotext")
    proc = run(["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(pdf), "-"])
    return proc.stdout.rstrip("\f\n") + "\n"


def parse_pages(spec: str, total: int) -> list[int]:
    if spec.strip().lower() in {"all", "*"}:
        return list(range(1, total + 1))
    pages: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start, end = int(start_s), int(end_s)
            if start > end:
                raise SystemExit(f"invalid page range: {part}")
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    bad = [p for p in sorted(pages) if p < 1 or p > total]
    if bad:
        raise SystemExit(f"page(s) outside 1..{total}: {bad}")
    return sorted(pages)


def source_files(thesis_dir: Path) -> Iterable[Path]:
    for path in thesis_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        # Generated top-level PDFs are intentionally excluded; figure PDFs are
        # source inputs and must be fresh relative to main.pdf.
        if path.suffix.lower() == ".pdf" and path.parent.name != "figures":
            continue
        yield path


def newer_sources(pdf: Path) -> list[Path]:
    if not pdf.exists():
        return []
    pdf_mtime = pdf.stat().st_mtime
    return sorted(path for path in source_files(THESIS_DIR) if path.stat().st_mtime > pdf_mtime)


def build_pdf() -> None:
    require_cmd("latexmk")
    run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=THESIS_DIR)


def sibling_pdfs(canonical_pdf: Path) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(canonical_pdf.parent.glob("*.pdf")):
        if path.resolve() == canonical_pdf.resolve():
            continue
        try:
            pages = pdf_page_count(path)
        except Exception:
            pages = None
        rows.append(
            {
                "path": str(path.relative_to(REPO_ROOT)),
                "bytes": path.stat().st_size,
                "mtime": dt.datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
                "pages": pages,
                "status": "forbidden_for_page_critique_unless_explicitly_requested",
            }
        )
    return rows


def prompt_for_page(*, manifest: dict, page: int, page_text_rel: str, page_text: str) -> str:
    forbidden = manifest.get("sibling_pdfs", [])
    forbidden_text = "\n".join(f"- {row['path']} ({row.get('pages')} pages, mtime {row['mtime']})" for row in forbidden) or "- (none)"
    return f"""# Drift-resistant thesis page critique prompt

You are reviewing exactly one page of Mattias Linholm's Kratt thesis.

## Canonical PDF contract

- Canonical PDF: `{manifest['canonical_pdf']}`
- PDF SHA-256: `{manifest['pdf_sha256']}`
- PDF page count: `{manifest['page_count']}`
- Packet generated: `{manifest['generated_at']}`
- Page to critique: `{page}`
- Page text artifact: `{page_text_rel}`

Forbidden sibling PDFs for this run unless the user explicitly overrides the canonical contract:
{forbidden_text}

## Hard rules

1. Use the canonical PDF contract above. Do **not** discover or read another thesis PDF such as `loputoo.pdf`.
2. Ground the critique in the page text below. You may inspect LaTeX source only after using the page text to identify what page you are critiquing.
3. Do not rely on previous sessions, remembered page layouts, or old PDFs.
4. If the page text is empty, obviously the wrong page, or inconsistent with the requested page number, return `STALE_OR_MISMATCH` and explain the mismatch instead of critiquing.
5. Separate real page-local findings from external-check findings. Mark claims that require TalTech rules, bibliography lookup, or repo context as `needs_external_check`.
6. Output concise Estonian.

## Required output shape

```yaml
page: {page}
pdf_sha256: {manifest['pdf_sha256']}
status: ok | stale_or_mismatch
confidence: high | medium | low
findings:
  - severity: P0 | P1 | P2
    type: factual | methodology | structure | language | formatting | bibliography | external_check
    evidence: "short quote from the page text"
    issue: "what is wrong"
    action: "smallest useful fix"
ignore_or_defer:
  - "feedback not worth acting on now, if any"
```

## Extracted page text

```text
{page_text.rstrip()}
```
"""


def write_runner(out_dir: Path, pages: list[int]) -> None:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "HERE=\"$(cd \"$(dirname \"${BASH_SOURCE[0]}\")\" && pwd)\"",
        "OUT=\"$HERE/responses\"",
        "mkdir -p \"$OUT\"",
        "if ! command -v claude >/dev/null 2>&1; then echo 'missing claude command' >&2; exit 127; fi",
    ]
    for page in pages:
        name = f"page-{page:02d}"
        lines.append(f"claude -p < \"$HERE/prompts/{name}.md\" > \"$OUT/{name}.md\"")
    runner = out_dir / "run-claude.sh"
    runner.write_text("\n".join(lines) + "\n", encoding="utf-8")
    runner.chmod(0o755)


def prepare(args: argparse.Namespace) -> None:
    pdf = Path(args.pdf).expanduser()
    if not pdf.is_absolute():
        pdf = (REPO_ROOT / pdf).resolve()
    if args.build:
        build_pdf()
    if not pdf.exists():
        raise SystemExit(f"canonical PDF does not exist: {pdf}")

    if not args.no_freshness_check:
        stale = newer_sources(pdf)
        if stale:
            examples = "\n".join(f"- {p.relative_to(REPO_ROOT)}" for p in stale[:12])
            more = "" if len(stale) <= 12 else f"\n... and {len(stale) - 12} more"
            raise SystemExit(
                "canonical PDF is older than thesis source files; run with --build or rebuild first.\n"
                + examples
                + more
            )

    total = pdf_page_count(pdf)
    pages = parse_pages(args.pages, total)
    out_dir = Path(args.out).expanduser() if args.out else DEFAULT_OUT_ROOT / dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    if not out_dir.is_absolute():
        out_dir = (REPO_ROOT / out_dir).resolve()
    pages_dir = out_dir / "pages"
    prompts_dir = out_dir / "prompts"
    pages_dir.mkdir(parents=True, exist_ok=True)
    prompts_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "repo_root": str(REPO_ROOT),
        "canonical_pdf": str(pdf.relative_to(REPO_ROOT) if pdf.is_relative_to(REPO_ROOT) else pdf),
        "canonical_pdf_abs": str(pdf),
        "pdf_sha256": sha256(pdf),
        "pdf_mtime": dt.datetime.fromtimestamp(pdf.stat().st_mtime).isoformat(timespec="seconds"),
        "pdf_bytes": pdf.stat().st_size,
        "page_count": total,
        "requested_pages": pages,
        "sibling_pdfs": sibling_pdfs(pdf),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for page in pages:
        page_name = f"page-{page:02d}"
        text = extract_page_text(pdf, page)
        page_rel = f"pages/{page_name}.txt"
        (pages_dir / f"{page_name}.txt").write_text(text, encoding="utf-8")
        (prompts_dir / f"{page_name}.md").write_text(
            prompt_for_page(manifest=manifest, page=page, page_text_rel=page_rel, page_text=text),
            encoding="utf-8",
        )

    readme = f"""# Thesis page critique packet

Generated: `{manifest['generated_at']}`
Canonical PDF: `{manifest['canonical_pdf']}`
SHA-256: `{manifest['pdf_sha256']}`
Pages: `{args.pages}` -> {pages}

Run prompts manually, or execute:

```bash
{shlex.quote(str(out_dir / 'run-claude.sh'))}
```

Guardrail: prompts forbid sibling PDFs and include extracted page text to prevent PDF/page drift.
"""
    (out_dir / "README.md").write_text(readme, encoding="utf-8")
    write_runner(out_dir, pages)

    print(json.dumps({"out_dir": str(out_dir), "pages": pages, "manifest": str(out_dir / "manifest.json")}, ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", default=str(DEFAULT_PDF.relative_to(REPO_ROOT)), help="Canonical thesis PDF (default: docs/thesis/thesis-tex-estonian/main.pdf)")
    parser.add_argument("--pages", default="all", help="Pages to prepare, e.g. all, 47, 1-10,12")
    parser.add_argument("--out", help="Output directory (default: .hermes/thesis-page-critiques/<timestamp>)")
    parser.add_argument("--build", action="store_true", help="Run latexmk before preparing the packet")
    parser.add_argument("--no-freshness-check", action="store_true", help="Allow preparing from a PDF older than thesis source files")
    args = parser.parse_args(argv)
    prepare(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
