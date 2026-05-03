#!/usr/bin/env python3
"""Materialize disjoint negative/ambient splits for Kratt wake-word training.

The goal is to use large external corpora without leaking final evaluation audio
into training, augmentation, checkpoint selection, or threshold tuning.

Output layout:

    <out-root>/
      train_negatives/        # pass to submit_hpc_kuule_kratt.sh --extra-negative-dirs
      checkpoint_ambient/     # pass to submit_hpc_kuule_kratt.sh --extra-ambient-dirs
      eval/<source>/          # register/benchmark as final or secondary FAPH sets
      manifest.json

Common Voice ET uses the same seeded shuffle policy as the legacy Kratt split:
- indices 5000..6999 are reserved for the frozen final faph_cv_et test set;
- indices 7000..8999 are reserved for dev/checkpoint/threshold selection;
- all remaining converted WAVs can be used for training.

Other corpora are split deterministically by shuffled file list. Podcast-like
sources should preferably be pre-split by episode before using this script; if
only files are available, this script splits by file path and records that caveat
in the manifest.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

AUDIO_EXTS = {".wav", ".flac", ".mp3", ".m4a", ".ogg"}
DIRECT_EXTS = {".wav", ".flac"}


@dataclass
class SplitCounts:
    source: str
    train: int = 0
    checkpoint_ambient: int = 0
    eval: int = 0
    skipped: int = 0
    notes: list[str] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out-root", required=True, help="Output split root")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--force", action="store_true", help="Replace existing out-root")
    p.add_argument("--dry-run", action="store_true", help="Only print/write manifest, no symlinks/conversions")
    p.add_argument("--copy", action="store_true", help="Copy direct WAV/FLAC instead of symlink")
    p.add_argument("--convert-lossy", action="store_true", help="Convert MP3/M4A/OGG sources to 16 kHz WAV with sox/ffmpeg")

    # Common Voice ET
    p.add_argument("--cv-root", help="Common Voice ET root containing validated.tsv")
    p.add_argument("--cv-wav-dir", help="Pre-converted Common Voice ET WAV directory")
    p.add_argument("--cv-exclude-words", nargs="*", default=["kratt"], help="Words excluded from CV negatives")
    p.add_argument("--cv-final-skip", type=int, default=5000)
    p.add_argument("--cv-final-limit", type=int, default=2000)
    p.add_argument("--cv-dev-skip", type=int, default=7000)
    p.add_argument("--cv-dev-limit", type=int, default=2000)
    p.add_argument("--cv-train-limit", type=int, default=0, help="0 = all available train CV clips")

    # Generic corpora. Each path can be absent; absent sources are recorded as skipped.
    p.add_argument("--musan-root", help="MUSAN root containing speech/ music/ noise/")
    p.add_argument("--voices-root", help="VOiCES extracted root")
    p.add_argument("--riigikogu-dir", help="Riigikogu audio directory")
    p.add_argument("--riigikogu-limit", type=int, default=0, help="0 = all Riigikogu files")
    p.add_argument("--podcast-root", help="Directory with normalized podcast/radio audio")

    p.add_argument("--dev-ratio", type=float, default=0.10)
    p.add_argument("--eval-ratio", type=float, default=0.10)
    return p.parse_args()


def read_cv_validated(cv_root: Path) -> list[dict[str, str]]:
    tsv_path = cv_root / "validated.tsv"
    rows: list[dict[str, str]] = []
    with tsv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append({"path": row["path"], "sentence": row.get("sentence", "")})
    return rows


def list_audio(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in AUDIO_EXTS)


def safe_name(source: str, index: int, src: Path, target_ext: str | None = None) -> str:
    digest = hashlib.sha1(str(src).encode("utf-8")).hexdigest()[:10]
    ext = target_ext if target_ext is not None else src.suffix.lower()
    return f"{source}_{index:06d}_{digest}{ext}"


def ensure_clean_dir(path: Path, force: bool) -> None:
    if path.exists():
        if not force:
            raise SystemExit(f"Output already exists: {path} (use --force)")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def convert_to_wav(src: Path, dst: Path) -> None:
    if shutil.which("sox"):
        subprocess.run(
            ["sox", str(src), "-r", "16000", "-c", "1", "-b", "16", str(dst)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return
    if shutil.which("ffmpeg"):
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-ar", "16000", "-ac", "1", str(dst)],
            check=True,
        )
        return
    raise RuntimeError("Neither sox nor ffmpeg found for lossy audio conversion")


def materialize(src: Path, dst_dir: Path, name: str, *, copy: bool, convert_lossy: bool, dry_run: bool) -> bool:
    suffix = src.suffix.lower()
    if suffix in DIRECT_EXTS:
        dst = dst_dir / name
        if dry_run:
            return True
        dst.parent.mkdir(parents=True, exist_ok=True)
        if copy:
            shutil.copy2(src, dst)
        else:
            os.symlink(src.resolve(), dst)
        return True

    if suffix in AUDIO_EXTS and convert_lossy:
        dst = dst_dir / Path(name).with_suffix(".wav").name
        if dry_run:
            return True
        dst.parent.mkdir(parents=True, exist_ok=True)
        convert_to_wav(src, dst)
        return True

    return False


def split_files(files: list[Path], seed: int, dev_ratio: float, eval_ratio: float) -> tuple[list[Path], list[Path], list[Path]]:
    shuffled = files[:]
    random.Random(seed).shuffle(shuffled)
    eval_n = int(len(shuffled) * eval_ratio)
    dev_n = int(len(shuffled) * dev_ratio)
    eval_files = shuffled[:eval_n]
    dev_files = shuffled[eval_n:eval_n + dev_n]
    train_files = shuffled[eval_n + dev_n:]
    return train_files, dev_files, eval_files


def add_files(
    *,
    source: str,
    files: Iterable[Path],
    target_dir: Path,
    copy: bool,
    convert_lossy: bool,
    dry_run: bool,
) -> tuple[int, int]:
    ok = skipped = 0
    for i, src in enumerate(files):
        target_ext = ".wav" if src.suffix.lower() not in DIRECT_EXTS and convert_lossy else None
        name = safe_name(source, i, src, target_ext=target_ext)
        if materialize(src, target_dir, name, copy=copy, convert_lossy=convert_lossy, dry_run=dry_run):
            ok += 1
        else:
            skipped += 1
    return ok, skipped


def process_cv(args: argparse.Namespace, out_root: Path) -> SplitCounts:
    counts = SplitCounts(source="cv_et")
    if not args.cv_root or not args.cv_wav_dir:
        counts.notes.append("CV skipped: --cv-root/--cv-wav-dir not provided")
        return counts

    cv_root = Path(args.cv_root).expanduser().resolve()
    cv_wav_dir = Path(args.cv_wav_dir).expanduser().resolve()
    if not cv_root.exists() or not cv_wav_dir.exists():
        counts.notes.append(f"CV skipped: missing {cv_root} or {cv_wav_dir}")
        return counts

    rows = read_cv_validated(cv_root)
    exclude = [w.lower() for w in (args.cv_exclude_words or [])]
    filtered = [r for r in rows if not any(w in r["sentence"].lower() for w in exclude)]
    random.Random(args.seed).shuffle(filtered)

    final_range = range(args.cv_final_skip, args.cv_final_skip + args.cv_final_limit)
    dev_range = range(args.cv_dev_skip, args.cv_dev_skip + args.cv_dev_limit)

    train: list[Path] = []
    dev: list[Path] = []
    final: list[Path] = []
    for idx, row in enumerate(filtered):
        wav = cv_wav_dir / f"{Path(row['path']).stem}.wav"
        if not wav.exists():
            counts.skipped += 1
            continue
        if idx in final_range:
            final.append(wav)
        elif idx in dev_range:
            dev.append(wav)
        else:
            train.append(wav)

    if args.cv_train_limit > 0:
        train = train[:args.cv_train_limit]

    c, s = add_files(
        source="cv_et_train", files=train, target_dir=out_root / "train_negatives",
        copy=args.copy, convert_lossy=args.convert_lossy, dry_run=args.dry_run,
    )
    counts.train += c; counts.skipped += s
    c, s = add_files(
        source="cv_et_dev", files=dev, target_dir=out_root / "checkpoint_ambient" / "cv_et_dev",
        copy=args.copy, convert_lossy=args.convert_lossy, dry_run=args.dry_run,
    )
    counts.checkpoint_ambient += c; counts.skipped += s
    c, s = add_files(
        source="cv_et_final", files=final, target_dir=out_root / "eval" / "cv_et_final_legacy_range",
        copy=args.copy, convert_lossy=args.convert_lossy, dry_run=args.dry_run,
    )
    counts.eval += c; counts.skipped += s
    counts.notes.append(
        f"CV policy: final indices {args.cv_final_skip}-{args.cv_final_skip + args.cv_final_limit - 1}; "
        f"dev indices {args.cv_dev_skip}-{args.cv_dev_skip + args.cv_dev_limit - 1}; train = rest"
    )
    return counts


def process_generic_source(
    args: argparse.Namespace,
    *,
    source: str,
    root: Path | None,
    out_root: Path,
    subdir: str | None = None,
    limit: int = 0,
) -> SplitCounts:
    counts = SplitCounts(source=source)
    if root is None:
        counts.notes.append(f"{source} skipped: path not provided")
        return counts
    base = (root / subdir) if subdir else root
    if not base.exists():
        counts.notes.append(f"{source} skipped: missing {base}")
        return counts

    files = list_audio(base)
    if limit > 0:
        files = files[:limit]
    if not files:
        counts.notes.append(f"{source} skipped: no supported audio files under {base}")
        return counts

    train, dev, eval_files = split_files(files, args.seed, args.dev_ratio, args.eval_ratio)
    c, s = add_files(source=source, files=train, target_dir=out_root / "train_negatives", copy=args.copy, convert_lossy=args.convert_lossy, dry_run=args.dry_run)
    counts.train += c; counts.skipped += s
    c, s = add_files(source=f"{source}_dev", files=dev, target_dir=out_root / "checkpoint_ambient" / source, copy=args.copy, convert_lossy=args.convert_lossy, dry_run=args.dry_run)
    counts.checkpoint_ambient += c; counts.skipped += s
    c, s = add_files(source=f"{source}_eval", files=eval_files, target_dir=out_root / "eval" / source, copy=args.copy, convert_lossy=args.convert_lossy, dry_run=args.dry_run)
    counts.eval += c; counts.skipped += s
    counts.notes.append(f"Split by deterministic shuffled file list from {base}; use episode-level pre-splits for podcasts if available.")
    return counts


def main() -> None:
    args = parse_args()
    out_root = Path(args.out_root).expanduser().resolve()
    if not args.dry_run:
        ensure_clean_dir(out_root, args.force)
    else:
        out_root.mkdir(parents=True, exist_ok=True)

    counts: list[SplitCounts] = []
    counts.append(process_cv(args, out_root))

    musan_root = Path(args.musan_root).expanduser().resolve() if args.musan_root else None
    counts.append(process_generic_source(args, source="musan_speech", root=musan_root, subdir="speech", out_root=out_root))
    counts.append(process_generic_source(args, source="musan_music", root=musan_root, subdir="music", out_root=out_root))

    voices_root = Path(args.voices_root).expanduser().resolve() if args.voices_root else None
    counts.append(process_generic_source(args, source="voices", root=voices_root, out_root=out_root))

    riigikogu_root = Path(args.riigikogu_dir).expanduser().resolve() if args.riigikogu_dir else None
    counts.append(process_generic_source(args, source="riigikogu", root=riigikogu_root, out_root=out_root, limit=args.riigikogu_limit))

    podcast_root = Path(args.podcast_root).expanduser().resolve() if args.podcast_root else None
    counts.append(process_generic_source(args, source="estonian_podcast", root=podcast_root, out_root=out_root))

    manifest = {
        "created_by": "prepare_negative_data_splits.py",
        "seed": args.seed,
        "out_root": str(out_root),
        "dry_run": args.dry_run,
        "copy": args.copy,
        "convert_lossy": args.convert_lossy,
        "dev_ratio": args.dev_ratio,
        "eval_ratio": args.eval_ratio,
        "counts": [asdict(c) for c in counts],
        "recommended_submit_args": {
            "extra_negative_dirs": str(out_root / "train_negatives"),
            "extra_ambient_dirs": str(out_root / "checkpoint_ambient"),
            "disable_automatic_duplicates": "Use --negative-limit -1 --no-musan --no-riigikogu and pass the split train_negatives dir explicitly.",
        },
        "guardrails": [
            "Do not train on eval/* directories.",
            "Do not use eval/* directories as background-noise or RIR augmentation resources.",
            "Use checkpoint_ambient only for checkpoint/threshold/dev decisions, not final reporting.",
            "Keep existing processed/faph_test_cv_et frozen for historical final comparison.",
        ],
    }
    manifest_path = out_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Output root: {out_root}")
    for c in counts:
        print(f"{c.source:18s} train={c.train:6d} dev={c.checkpoint_ambient:6d} eval={c.eval:6d} skipped={c.skipped:6d}")
        for note in c.notes:
            print(f"  - {note}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
