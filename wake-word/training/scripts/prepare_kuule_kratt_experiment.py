#!/usr/bin/env python3
"""Prepare a 'kuule kratt' experiment directory.

Expects pre-converted WAVs for Common Voice negatives.
Creates symlinks only - fast and reusable.

Usage (v1/v2 - CV negatives only):
    python prepare_kuule_kratt_experiment.py \
        --positive-dirs .../kuule-kratt/positive/mic1 .../kuule-kratt/positive/mic2 \
        --cv-root .../common-voice-et/cv-corpus-24.0-2025-12-05/et \
        --cv-wav-dir .../common-voice-et-wav \
        --ambient-dir .../musan/musan/noise \
        --output-dir .../experiments/kuule_kratt_v1 \
        --negative-limit 5000

Usage (v3 - with same-device negatives and ambient):
    python prepare_kuule_kratt_experiment.py \
        --positive-dirs .../kuule-kratt/positive/mic1 .../kuule-kratt/positive/mic2 \
        --cv-root .../common-voice-et/cv-corpus-24.0-2025-12-05/et \
        --cv-wav-dir .../common-voice-et-wav \
        --ambient-dir .../musan/musan/noise \
        --extra-negative-dirs .../negative_korvo2 \
        --extra-ambient-dirs .../ambient_korvo2 \
        --output-dir .../experiments/kuule_kratt_v3 \
        --negative-limit 5000
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
import shutil


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--positive-dirs", required=True, nargs="+",
                   help="Directories containing positive WAV clips")
    p.add_argument("--cv-root", required=True,
                   help="Common Voice ET root (contains validated.tsv)")
    p.add_argument("--cv-wav-dir", required=True,
                   help="Directory with pre-converted CV WAV files")
    p.add_argument("--ambient-dir", required=True,
                   help="MUSAN noise directory (recursive WAV search)")
    p.add_argument("--extra-negative-dirs", default="",
                   help="Comma-separated list of additional negative WAV directories")
    p.add_argument("--extra-ambient-dirs", default="",
                   help="Comma-separated list of additional ambient WAV directories")
    p.add_argument("--hard-negative-dirs", default="",
                   help="Comma-separated list of HARD negative WAV directories "
                        "(phonetically similar phrases). Symlinked into a separate "
                        "hard_negative_samples/ directory.")
    p.add_argument("--output-dir", required=True)
    p.add_argument("--negative-limit", type=int, default=5000)
    p.add_argument("--test-split", type=float, default=0.15)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--force", action="store_true")
    p.add_argument("--exclude-words", nargs="*", default=["kratt", "kuule"],
                   help="Exclude CV clips whose transcript contains these words")
    return p.parse_args()


def read_cv_validated(cv_root: Path) -> list[dict]:
    """Read validated.tsv and return list of {path, sentence} dicts."""
    tsv_path = cv_root / "validated.tsv"
    rows = []
    with open(tsv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append({"path": row["path"], "sentence": row.get("sentence", "")})
    return rows


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    cv_root = Path(args.cv_root)
    cv_wav_dir = Path(args.cv_wav_dir)
    rnd = random.Random(args.seed)

    if output_dir.exists():
        if not args.force:
            raise SystemExit(f"Output exists: {output_dir} (use --force)")
        shutil.rmtree(output_dir)

    # --- Positive samples ---
    pos_files: list[Path] = []
    for d in args.positive_dirs:
        d = Path(d)
        if not d.exists():
            raise SystemExit(f"Positive dir not found: {d}")
        pos_files.extend(sorted(d.glob("*.wav")))

    if not pos_files:
        raise SystemExit("No positive WAV files found")

    rnd.shuffle(pos_files)
    test_count = max(1, int(len(pos_files) * args.test_split))
    test_files = pos_files[:test_count]
    train_files = pos_files[test_count:]

    pos_out = output_dir / "positive_samples"
    pos_out.mkdir(parents=True)
    for i, src in enumerate(train_files):
        dst = pos_out / f"kuule_kratt_{i:04d}.wav"
        dst.symlink_to(src.resolve())

    test_out = output_dir / "test_positive_samples"
    test_out.mkdir(parents=True)
    for i, src in enumerate(test_files):
        dst = test_out / f"kuule_kratt_test_{i:04d}.wav"
        dst.symlink_to(src.resolve())

    # --- Negative samples (Common Voice ET, pre-converted WAVs) ---
    neg_out = output_dir / "negative_samples"
    neg_out.mkdir(parents=True)
    neg_idx = 0
    filtered: list[Path] = []
    excluded_count = 0

    if args.negative_limit < 0:
        print("CV negatives: SKIPPED (negative_limit < 0)")
    else:
        print("Reading Common Voice validated.tsv...")
        cv_clips = read_cv_validated(cv_root)
        exclude_lower = [w.lower() for w in (args.exclude_words or [])]

        for clip in cv_clips:
            sentence_lower = clip["sentence"].lower()
            if any(w in sentence_lower for w in exclude_lower):
                excluded_count += 1
                continue
            # Check if pre-converted WAV exists
            stem = Path(clip["path"]).stem
            wav_path = cv_wav_dir / f"{stem}.wav"
            if wav_path.exists():
                filtered.append(wav_path)

        print(f"  Total validated: {len(cv_clips)}")
        print(f"  Excluded (contains {exclude_lower}): {excluded_count}")
        print(f"  Available WAVs: {len(filtered)}")

        rnd.shuffle(filtered)
        if args.negative_limit > 0:
            filtered = filtered[:args.negative_limit]

    for src in filtered:
        dst = neg_out / f"cv_negative_{neg_idx:04d}.wav"
        dst.symlink_to(src.resolve())
        neg_idx += 1

    # --- Extra negative samples (e.g. same-device KORVO-2) ---
    extra_neg_count = 0
    extra_neg_dirs = [d.strip() for d in args.extra_negative_dirs.split(",") if d.strip()]
    for extra_dir in extra_neg_dirs:
        extra_dir = Path(extra_dir)
        if not extra_dir.exists():
            raise SystemExit(f"Extra negative dir not found: {extra_dir}")
        extra_wavs = sorted(
            list(extra_dir.glob("*.wav")) + list(extra_dir.glob("*.flac"))
        )
        print(f"  Extra negatives from {extra_dir.name}: {len(extra_wavs)}")
        for src in extra_wavs:
            dst = neg_out / f"extra_negative_{neg_idx:04d}.wav"
            dst.symlink_to(src.resolve())
            neg_idx += 1
            extra_neg_count += 1

    # --- Hard negative samples (phonetically similar phrases) ---
    hard_neg_count = 0
    hard_neg_dirs = [d.strip() for d in args.hard_negative_dirs.split(",") if d.strip()]
    if hard_neg_dirs:
        hard_neg_out = output_dir / "hard_negative_samples"
        hard_neg_out.mkdir(parents=True)
        for extra_dir in hard_neg_dirs:
            extra_dir = Path(extra_dir)
            if not extra_dir.exists():
                raise SystemExit(f"Hard negative dir not found: {extra_dir}")
            extra_wavs = sorted(extra_dir.rglob("*.wav"))
            print(f"  Hard negatives from {extra_dir.name}: {len(extra_wavs)}")
            for src in extra_wavs:
                dst = hard_neg_out / f"hard_negative_{hard_neg_count:05d}.wav"
                dst.symlink_to(src.resolve())
                hard_neg_count += 1

    # --- Ambient samples (MUSAN) ---
    ambient_src = Path(args.ambient_dir)
    ambient_files = sorted(ambient_src.rglob("*.wav"))
    if not ambient_files:
        raise SystemExit(f"No ambient WAVs found in {ambient_src}")

    amb_out = output_dir / "ambient_samples"
    amb_out.mkdir(parents=True)
    amb_idx = 0
    for src in ambient_files:
        dst = amb_out / f"ambient_{amb_idx:04d}.wav"
        dst.symlink_to(src.resolve())
        amb_idx += 1

    # --- Extra ambient samples (e.g. same-device KORVO-2) ---
    extra_amb_count = 0
    extra_amb_dirs = [d.strip() for d in args.extra_ambient_dirs.split(",") if d.strip()]
    for extra_dir in extra_amb_dirs:
        extra_dir = Path(extra_dir)
        if not extra_dir.exists():
            raise SystemExit(f"Extra ambient dir not found: {extra_dir}")
        extra_wavs = sorted(extra_dir.glob("*.wav"))
        print(f"  Extra ambient from {extra_dir.name}: {len(extra_wavs)}")
        for src in extra_wavs:
            dst = amb_out / f"extra_ambient_{amb_idx:04d}.wav"
            dst.symlink_to(src.resolve())
            amb_idx += 1
            extra_amb_count += 1

    # --- Manifest ---
    manifest = {
        "wake_word": "kuule_kratt",
        "positive_train": len(train_files),
        "positive_test": len(test_files),
        "negative_cv_count": len(filtered),
        "negative_extra_count": extra_neg_count,
        "negative_total": len(filtered) + extra_neg_count,
        "negative_source": "common_voice_et_24.0",
        "negative_extra_sources": extra_neg_dirs,
        "negative_limit": args.negative_limit,
        "hard_negative_count": hard_neg_count,
        "hard_negative_sources": hard_neg_dirs,
        "ambient_musan_count": len(ambient_files),
        "ambient_extra_count": extra_amb_count,
        "ambient_total": len(ambient_files) + extra_amb_count,
        "ambient_source": str(ambient_src),
        "ambient_extra_sources": extra_amb_dirs,
        "exclude_words": args.exclude_words,
        "excluded_cv_clips": excluded_count,
        "seed": args.seed,
        "test_split": args.test_split,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )

    print(f"\nExperiment ready: {output_dir}")
    print(f"  Positive (train): {len(train_files)}")
    print(f"  Positive (test):  {len(test_files)}")
    print(f"  Negative (CV):    {len(filtered)}")
    print(f"  Negative (extra): {extra_neg_count}")
    print(f"  Negative (total): {len(filtered) + extra_neg_count}")
    print(f"  Hard negatives:   {hard_neg_count}")
    print(f"  Ambient (MUSAN):  {len(ambient_files)}")
    print(f"  Ambient (extra):  {extra_amb_count}")
    print(f"  Ambient (total):  {len(ambient_files) + extra_amb_count}")


if __name__ == "__main__":
    main()
