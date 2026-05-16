#!/usr/bin/env python3
"""Small final-pass checks for thesis-critical Kratt repo drift.

This intentionally stays narrow. It is not a full CI replacement; it catches
the high-cost mistakes that have already recurred in this repo.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import wave
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FAPH_CV_ET_DIR = REPO_ROOT / "wake-word" / "data" / "processed" / "faph_test_cv_et"
THESIS_TEX_DIR = REPO_ROOT / "docs" / "thesis" / "thesis-tex-estonian"
CANONICAL_THESIS_PDF = THESIS_TEX_DIR / "main.pdf"
FORBIDDEN_THESIS_PDFS = [THESIS_TEX_DIR / "loputoo.pdf"]
INTER_CLIP_SILENCE_S = 0.300


REQUIRED_TEXT = {
    "wake-word/evaluation/test_sets.py": [
        "clips are ~3.65 h",
        "producing a ~3.82 h evaluation track",
    ],
    "wake-word/evaluation/training_data_manifest.md": [
        "3.65h raw; 3.82h canonical streaming track with 300 ms gaps",
    ],
    "docs/research/wake-word-evaluation-methodology.md": [
        "~3.65 hours raw / ~3.82 hours streaming track",
    ],
    "wake-word/evaluation/generate_thesis_figures.py": [
        "3,82 h koos vahedega",
    ],
    "wake-word/evaluation/make_supervisor_table.py": [
        "CV-ET 3.82h track",
    ],
    "wake-word/evaluation/make_html_report.py": [
        "3.65h raw / 3.82h streaming track with 300 ms gaps",
    ],
    "docs/thesis/thesis-tex-estonian/chapters/second_chapter.tex": [
        "3,65\\,h toorheli; 3,82\\,h voogedastusrada",
        "300~ms klipivahedega",
    ],
    "docs/thesis/thesis-tex-estonian/chapters/third_chapter.tex": [
        "3,82\\,h pikkusel Common~Voice ET voogedastusrajal",
    ],
}


FORBIDDEN_TEXT = {
    "docs/thesis/presentation/repo-kokkuvote-ja-esitlusbrief.md": [
        "3,82h peal",
    ],
    "docs/thesis/thesis-tex-estonian/chapters/second_chapter.tex": [
        "(3,82\\,h), recall",
        "($\\sim$3,82\\,tundi). Kasutati",
        "(CV ET, 3,82\\,h)\\,\\emph",
        "Common Voice ET (hold-out) & Eesti & 3,82",
    ],
    "docs/thesis/thesis-tex-estonian/chapters/third_chapter.tex": [
        "0 sündmust 3,82\\,h jooksul",
    ],
    "wake-word/evaluation/generate_thesis_figures.py": [
        "CV ET hold-out, 3,82 h\")",
    ],
    "wake-word/evaluation/make_html_report.py": [
        "3.82h. Primary in-domain FAPH benchmark.",
    ],
    "wake-word/evaluation/make_supervisor_table.py": [
        "\"CV-ET 3.82h\"",
    ],
    "docs/research/wake-word-evaluation-methodology.md": [
        "| **Our `faph_cv_et`** | ~3.65 hours |",
    ],
}


def run_docs_audit(strict: bool) -> int:
    cmd = [sys.executable, str(REPO_ROOT / "scripts" / "docs_freshness_audit.py")]
    if strict:
        cmd.append("--strict")
    print("$ " + " ".join(str(part) for part in cmd), flush=True)
    result = subprocess.run(cmd, cwd=REPO_ROOT, check=False)
    return int(result.returncode)


def read_text(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    if not path.exists():
        raise FileNotFoundError(rel_path)
    return path.read_text(encoding="utf-8")


def check_text_contract() -> list[str]:
    errors: list[str] = []
    for rel_path, snippets in REQUIRED_TEXT.items():
        try:
            text = read_text(rel_path)
        except FileNotFoundError:
            errors.append(f"{rel_path}: missing required file")
            continue
        for snippet in snippets:
            if snippet not in text:
                errors.append(f"{rel_path}: missing expected text: {snippet!r}")

    for rel_path, snippets in FORBIDDEN_TEXT.items():
        try:
            text = read_text(rel_path)
        except FileNotFoundError:
            continue
        for snippet in snippets:
            if snippet in text:
                errors.append(f"{rel_path}: stale/ambiguous text remains: {snippet!r}")
    return errors


def wav_hours(path: Path) -> tuple[int, float] | None:
    if not path.exists():
        return None
    total_seconds = 0.0
    count = 0
    for wav_path in sorted(path.rglob("*.wav")):
        with wave.open(str(wav_path), "rb") as handle:
            total_seconds += handle.getnframes() / handle.getframerate()
        count += 1
    if count == 0:
        return None
    return count, total_seconds / 3600.0


def check_pdf_artifacts() -> list[str]:
    errors: list[str] = []
    if not CANONICAL_THESIS_PDF.exists():
        errors.append(f"missing canonical thesis PDF: {CANONICAL_THESIS_PDF.relative_to(REPO_ROOT)}")
    for path in FORBIDDEN_THESIS_PDFS:
        if path.exists():
            errors.append(
                f"forbidden stale thesis PDF exists: {path.relative_to(REPO_ROOT)}; "
                "use docs/thesis/thesis-tex-estonian/main.pdf as the only thesis review PDF"
            )
    return errors


def check_faph_duration() -> list[str]:
    errors: list[str] = []
    measured = wav_hours(FAPH_CV_ET_DIR)
    if measured is None:
        print(f"WARNING: skipped local duration check; missing WAVs under {FAPH_CV_ET_DIR}")
        return errors

    count, raw_h = measured
    track_h = raw_h + max(0, count - 1) * INTER_CLIP_SILENCE_S / 3600.0
    print(f"faph_cv_et local duration: {count} WAVs, raw={raw_h:.3f}h, streaming_track={track_h:.3f}h")

    if count != 2000:
        errors.append(f"faph_cv_et: expected 2000 WAVs, found {count}")
    if not (3.60 <= raw_h <= 3.70):
        errors.append(f"faph_cv_et: raw duration {raw_h:.3f}h outside expected 3.60..3.70h")
    if not (3.78 <= track_h <= 3.86):
        errors.append(f"faph_cv_et: streaming track duration {track_h:.3f}h outside expected 3.78..3.86h")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run thesis-critical Kratt consistency checks")
    parser.add_argument("--skip-docs-audit", action="store_true", help="Do not run scripts/docs_freshness_audit.py")
    parser.add_argument("--strict-docs", action="store_true", help="Pass --strict to docs_freshness_audit.py")
    args = parser.parse_args(argv)

    exit_code = 0
    if not args.skip_docs_audit:
        exit_code = max(exit_code, run_docs_audit(args.strict_docs))

    errors = check_text_contract()
    errors.extend(check_pdf_artifacts())
    errors.extend(check_faph_duration())

    if errors:
        print("\n# Thesis Final Check Failures")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nThesis final checks passed.")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
