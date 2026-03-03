#!/usr/bin/env python3
"""
Prepare a 'processed' dataset layout from the raw Neurokone phase1 TTS output.

Why:
- microWakeWord/openWakeWord training pipelines expect a clean directory of
  positive/negative samples.
- Raw Neurokone output includes multiple text variants; for a single wake word
  ("Kratt") we usually want the isolated form only.

This script:
1) Creates wake-word/data/processed/positive_samples/ containing symlinks
   to the isolated "Kratt" wavs from wake-word/data/raw/neurokone_phase1/.
2) Optionally downloads negative samples into wake-word/data/processed/negative_samples/
   using download_negatives.py (Google Speech Commands + generated noise).
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


STRICT_ISOLATED_RE = re.compile(r"^[^_]+_\d{4}_Kratt_speed[0-9.]+\.wav$")


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def link_or_copy(src: Path, dst: Path, copy: bool) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        return
    if copy:
        dst.write_bytes(src.read_bytes())
    else:
        dst.symlink_to(src.resolve())


def prepare_positive_samples(
    raw_dir: Path,
    out_dir: Path,
    include_context: bool,
    copy: bool,
) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)

    wavs = list(raw_dir.glob("*/*.wav"))
    if include_context:
        selected = wavs
    else:
        selected = [p for p in wavs if STRICT_ISOLATED_RE.match(p.name)]

    for p in selected:
        link_or_copy(p, out_dir / p.name, copy=copy)

    return len(selected)


def ensure_negative_samples(processed_dir: Path, python_bin: str) -> Path:
    negative_dir = processed_dir / "negative_samples"
    if negative_dir.exists():
        return negative_dir

    script = project_root() / "wake-word" / "data" / "collection" / "download_negatives.py"
    subprocess.check_call(
        [python_bin, str(script), "--output-dir", str(processed_dir)],
    )
    return negative_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw-dir",
        default=str(project_root() / "wake-word" / "data" / "raw" / "neurokone_phase1"),
        help="Path to raw Neurokone dataset (default: wake-word/data/raw/neurokone_phase1)",
    )
    parser.add_argument(
        "--processed-dir",
        default=str(project_root() / "wake-word" / "data" / "processed"),
        help="Path to processed output dir (default: wake-word/data/processed)",
    )
    parser.add_argument(
        "--include-context",
        action="store_true",
        help="Include all Neurokone phrase variants as positive samples (default: only isolated 'Kratt')",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy files instead of symlinking (default: symlink)",
    )
    parser.add_argument(
        "--download-negatives",
        action="store_true",
        help="Download/generate negative samples into processed dir (large download)",
    )
    parser.add_argument(
        "--python",
        default=os.environ.get("PYTHON", ""),
        help="Python interpreter to run download_negatives.py (default: uses this interpreter)",
    )

    args = parser.parse_args()

    raw_dir = Path(args.raw_dir).expanduser().resolve()
    processed_dir = Path(args.processed_dir).expanduser().resolve()
    positive_dir = processed_dir / "positive_samples"

    if not raw_dir.exists():
        raise SystemExit(f"Raw dir not found: {raw_dir}")

    count = prepare_positive_samples(
        raw_dir=raw_dir,
        out_dir=positive_dir,
        include_context=args.include_context,
        copy=args.copy,
    )
    print(f"Prepared positive samples: {count} -> {positive_dir}")

    if args.download_negatives:
        python_bin = args.python or sys.executable
        neg_dir = ensure_negative_samples(
            processed_dir=processed_dir,
            python_bin=python_bin,
        )
        print(f"Prepared negative samples -> {neg_dir}")


if __name__ == "__main__":
    main()
