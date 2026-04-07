#!/usr/bin/env python3
"""
Prepare a FAPH (False Activations Per Hour) test set from unused Common Voice ET clips.

Uses the same RNG seed and exclusion filter as prepare_kuule_kratt_experiment.py,
then SKIPS the first --skip clips (those that went to training) and converts the
next --limit clips from MP3 to WAV (16kHz mono).

Output: a directory of WAV files that can be fed to a streaming wake-word model
to measure false-activations-per-hour on unseen Estonian speech.
"""

from __future__ import annotations

import argparse
import csv
import random
import subprocess
from pathlib import Path


def read_cv_validated(cv_root: Path) -> list[dict]:
    tsv_path = cv_root / "validated.tsv"
    rows = []
    with open(tsv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append({"path": row["path"], "sentence": row.get("sentence", "")})
    return rows


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--cv-root", required=True,
                   help="Common Voice ET root (contains validated.tsv and clips/)")
    p.add_argument("--out-dir", required=True,
                   help="Output directory for converted WAV files")
    p.add_argument("--skip", type=int, default=5000,
                   help="Number of clips to skip (those that went to training)")
    p.add_argument("--limit", type=int, default=2000,
                   help="Number of new clips to convert")
    p.add_argument("--seed", type=int, default=42,
                   help="RNG seed (must match training seed)")
    p.add_argument("--exclude-words", nargs="*", default=["kratt", "kuule"])
    args = p.parse_args()

    cv_root = Path(args.cv_root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rnd = random.Random(args.seed)

    print(f"Reading {cv_root / 'validated.tsv'}...")
    rows = read_cv_validated(cv_root)
    print(f"  Total validated: {len(rows)}")

    exclude_lower = [w.lower() for w in (args.exclude_words or [])]
    filtered = [
        r for r in rows
        if not any(w in r["sentence"].lower() for w in exclude_lower)
    ]
    print(f"  After excluding {exclude_lower}: {len(filtered)}")

    # Same shuffle as prepare_kuule_kratt_experiment.py
    rnd.shuffle(filtered)

    # Skip the first N (training set) and take the next M
    pool = filtered[args.skip:args.skip + args.limit]
    print(f"  Picking clips {args.skip}..{args.skip + args.limit} ({len(pool)} clips)")

    clips_dir = cv_root / "clips"
    converted = 0
    errors = 0
    skipped = 0

    for i, row in enumerate(pool):
        mp3 = clips_dir / row["path"]
        if not mp3.exists():
            errors += 1
            continue
        out_wav = out_dir / f"faph_{i:05d}.wav"
        if out_wav.exists():
            skipped += 1
            converted += 1
            continue
        try:
            subprocess.run(
                ["sox", str(mp3), "-r", "16000", "-c", "1", "-b", "16", str(out_wav)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            converted += 1
        except subprocess.CalledProcessError:
            errors += 1
        if (i + 1) % 200 == 0:
            print(f"  ...{i + 1} processed (converted={converted}, skipped={skipped}, errors={errors})")

    print(f"Done. Converted {converted}, skipped {skipped}, errors {errors}.")
    print(f"Output: {out_dir}")


if __name__ == "__main__":
    main()
