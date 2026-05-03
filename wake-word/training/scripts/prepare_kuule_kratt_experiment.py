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
import hashlib
import json
import random
from pathlib import Path
import shutil

import soundfile as sf


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--positive-dirs", required=True, nargs="+",
                   help="Directories containing positive WAV clips")
    p.add_argument("--exclude-positive-wav-dirs", default="",
                   help="Comma-separated WAV dirs to exclude from positives. Used to quarantine known-bad/generated-corrupt sources.")
    p.add_argument("--positive-min-duration-s", type=float, default=0.0,
                   help="Drop positive WAVs shorter than this duration (0 disables).")
    p.add_argument("--positive-max-duration-s", type=float, default=0.0,
                   help="Drop positive WAVs longer than this duration (0 disables).")
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
    p.add_argument("--exclude-words", nargs="*", default=["kratt"],
                   help="Exclude CV clips whose transcript contains these words. Default keeps 'kuule' as ordinary negative speech so the model does not learn prefix-only activation.")
    p.add_argument("--exclude-negative-wav-dirs", default="",
                   help="Comma-separated WAV dirs to exclude from CV/general negatives, "
                        "e.g. held-out FAPH sets. Compared by resolved real path.")
    p.add_argument("--exclude-negative-fingerprints", action="store_true",
                   help="Also exclude exact audio-content matches from --exclude-negative-wav-dirs. "
                        "Slow on large corpora; use as an audit, not default prep.")
    p.add_argument("--exclude-cv-split-skip", type=int, default=None,
                   help="Exclude a deterministic shuffled CV split by source path, e.g. 5000 for faph_cv_et.")
    p.add_argument("--exclude-cv-split-limit", type=int, default=0,
                   help="Number of shuffled CV rows to exclude after --exclude-cv-split-skip.")
    p.add_argument("--exclude-cv-split-exclude-words", nargs="*", default=["kratt", "kuule"],
                   help="Exclude words used when reconstructing the held-out CV split.")
    return p.parse_args()


def list_audio_files(path: Path) -> list[Path]:
    """Return all supported audio files recursively.

    Earlier training prep used top-level glob() for extra negatives, which missed
    nested MUSAN/Riigikogu-style corpora. Use one helper everywhere so v17-style
    runs cannot silently drop data.
    """
    candidates = list(path.rglob("*.wav")) + list(path.rglob("*.flac"))
    # Broken symlinks can happen when local mined clips point to absolute paths
    # not present on HPC. Do not let them enter training manifests.
    return sorted(p for p in candidates if p.exists() and p.is_file())


def audio_fingerprint(path: Path) -> tuple[int, str]:
    """Return a stable fingerprint for copied/renamed audio files.

    The canonical faph_cv_et set contains renamed WAV files, so real-path checks
    are not enough to prevent leakage. Size + SHA1 catches exact audio copies.
    """
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return (path.stat().st_size, h.hexdigest())


def audio_duration_s(path: Path) -> float:
    """Return audio duration in seconds using libsndfile metadata."""
    info = sf.info(str(path))
    return float(info.frames) / float(info.samplerate)


def load_excluded_audio(
    dirs_csv: str,
    *,
    include_fingerprints: bool = False,
) -> tuple[set[Path], set[tuple[int, str]]]:
    excluded_paths: set[Path] = set()
    excluded_fingerprints: set[tuple[int, str]] = set()
    for d in [p.strip() for p in dirs_csv.split(",") if p.strip()]:
        path = Path(d)
        if not path.exists():
            raise SystemExit(f"Exclude audio dir not found: {path}")
        for audio in list_audio_files(path):
            excluded_paths.add(audio.resolve())
            if include_fingerprints:
                excluded_fingerprints.add(audio_fingerprint(audio))
    return excluded_paths, excluded_fingerprints


def reconstruct_excluded_cv_split_paths(
    rows: list[dict],
    *,
    seed: int,
    skip: int | None,
    limit: int,
    exclude_words: list[str],
) -> set[str]:
    """Reconstruct a deterministic held-out CV split by source path.

    This is the fast alternative to hashing renamed FAPH WAV files. For
    faph_cv_et, use the original split recipe: filter with ["kratt", "kuule"],
    shuffle seed=42, skip=5000, limit=2000.
    """
    if skip is None or limit <= 0:
        return set()
    exclude_lower = [w.lower() for w in (exclude_words or [])]
    filtered = [
        r for r in rows
        if not any(w in r["sentence"].lower() for w in exclude_lower)
    ]
    rnd = random.Random(seed)
    rnd.shuffle(filtered)
    split = filtered[skip:skip + limit]
    return {r["path"] for r in split}


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
    excluded_negative_paths, excluded_negative_fingerprints = load_excluded_audio(
        args.exclude_negative_wav_dirs,
        include_fingerprints=args.exclude_negative_fingerprints,
    )
    excluded_positive_paths, _ = load_excluded_audio(
        args.exclude_positive_wav_dirs,
        include_fingerprints=False,
    )

    if output_dir.exists():
        if not args.force:
            raise SystemExit(f"Output exists: {output_dir} (use --force)")
        shutil.rmtree(output_dir)

    # --- Positive samples ---
    pos_files: list[Path] = []
    positive_candidate_count = 0
    positive_excluded_by_path_count = 0
    positive_excluded_by_duration_count = 0
    positive_duration_reject_examples: list[dict[str, str | float]] = []
    for d in args.positive_dirs:
        d = Path(d)
        if not d.exists():
            raise SystemExit(f"Positive dir not found: {d}")
        # Positive sources may be flat (mic recordings) or nested by speaker
        # (Neurokõne/XTTS). Keep this recursive so all raw recordings actually
        # enter the candidate pool. Known-bad sources are excluded by real path
        # before split, and duration gates catch truncated single-word clips or
        # malformed long clips (e.g. literal SSML tags read aloud).
        for p in [p for p in list_audio_files(d) if p.suffix.lower() == ".wav"]:
            positive_candidate_count += 1
            if p.resolve() in excluded_positive_paths:
                positive_excluded_by_path_count += 1
                continue
            if args.positive_min_duration_s > 0 or args.positive_max_duration_s > 0:
                duration_s = audio_duration_s(p)
                too_short = args.positive_min_duration_s > 0 and duration_s < args.positive_min_duration_s
                too_long = args.positive_max_duration_s > 0 and duration_s > args.positive_max_duration_s
                if too_short or too_long:
                    positive_excluded_by_duration_count += 1
                    if len(positive_duration_reject_examples) < 20:
                        positive_duration_reject_examples.append(
                            {"file": str(p), "duration_s": round(duration_s, 3)}
                        )
                    continue
            pos_files.append(p)

    if not pos_files:
        raise SystemExit("No positive WAV files found after quality filters")

    print(f"Positive candidates: {positive_candidate_count}")
    print(f"  Excluded by known-bad path: {positive_excluded_by_path_count}")
    print(f"  Excluded by duration gate: {positive_excluded_by_duration_count}")
    print(f"  Kept positives: {len(pos_files)}")

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
    excluded_by_path_count = 0
    excluded_by_fingerprint_count = 0
    excluded_by_cv_split_count = 0

    if args.negative_limit < 0:
        print("CV negatives: SKIPPED (negative_limit < 0)")
    else:
        print("Reading Common Voice validated.tsv...")
        cv_clips = read_cv_validated(cv_root)
        exclude_lower = [w.lower() for w in (args.exclude_words or [])]
        excluded_cv_source_paths = reconstruct_excluded_cv_split_paths(
            cv_clips,
            seed=args.seed,
            skip=args.exclude_cv_split_skip,
            limit=args.exclude_cv_split_limit,
            exclude_words=args.exclude_cv_split_exclude_words,
        )
        for clip in cv_clips:
            sentence_lower = clip["sentence"].lower()
            if any(w in sentence_lower for w in exclude_lower):
                excluded_count += 1
                continue
            if clip["path"] in excluded_cv_source_paths:
                excluded_by_cv_split_count += 1
                continue
            # Check if pre-converted WAV exists
            stem = Path(clip["path"]).stem
            wav_path = cv_wav_dir / f"{stem}.wav"
            if wav_path.exists():
                if wav_path.resolve() in excluded_negative_paths:
                    excluded_by_path_count += 1
                    continue
                if excluded_negative_fingerprints and audio_fingerprint(wav_path) in excluded_negative_fingerprints:
                    excluded_by_fingerprint_count += 1
                    continue
                filtered.append(wav_path)

        print(f"  Total validated: {len(cv_clips)}")
        print(f"  Excluded (contains {exclude_lower}): {excluded_count}")
        print(f"  Excluded by held-out path: {excluded_by_path_count}")
        print(f"  Excluded by held-out fingerprint: {excluded_by_fingerprint_count}")
        print(f"  Excluded by CV split: {excluded_by_cv_split_count}")
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
            p for p in list_audio_files(extra_dir)
            if p.resolve() not in excluded_negative_paths
            and (not excluded_negative_fingerprints or audio_fingerprint(p) not in excluded_negative_fingerprints)
        )
        skipped_extra = len(list_audio_files(extra_dir)) - len(extra_wavs)
        print(f"  Extra negatives from {extra_dir.name}: {len(extra_wavs)} (excluded by path: {skipped_extra})")
        for src in extra_wavs:
            suffix = src.suffix.lower()
            dst = neg_out / f"extra_negative_{neg_idx:04d}{suffix}"
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
        extra_wavs = [p for p in list_audio_files(extra_dir) if p.suffix.lower() == ".wav"]
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
        "positive_candidate_count": positive_candidate_count,
        "positive_source_dirs": [str(Path(d)) for d in args.positive_dirs],
        "positive_min_duration_s": args.positive_min_duration_s,
        "positive_max_duration_s": args.positive_max_duration_s,
        "positive_excluded_by_path": positive_excluded_by_path_count,
        "positive_excluded_by_duration": positive_excluded_by_duration_count,
        "positive_duration_reject_examples": positive_duration_reject_examples,
        "excluded_positive_wav_dirs": [d.strip() for d in args.exclude_positive_wav_dirs.split(",") if d.strip()],
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
        "excluded_negative_by_path": excluded_by_path_count,
        "excluded_negative_by_fingerprint": excluded_by_fingerprint_count,
        "excluded_negative_by_cv_split": excluded_by_cv_split_count,
        "excluded_negative_wav_dirs": [d.strip() for d in args.exclude_negative_wav_dirs.split(",") if d.strip()],
        "exclude_cv_split_skip": args.exclude_cv_split_skip,
        "exclude_cv_split_limit": args.exclude_cv_split_limit,
        "exclude_cv_split_exclude_words": args.exclude_cv_split_exclude_words,
        "seed": args.seed,
        "test_split": args.test_split,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )

    print(f"\nExperiment ready: {output_dir}")
    print(f"  Positive candidates: {positive_candidate_count}")
    print(f"  Positive excluded by path:     {positive_excluded_by_path_count}")
    print(f"  Positive excluded by duration: {positive_excluded_by_duration_count}")
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
