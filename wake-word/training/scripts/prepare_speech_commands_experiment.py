#!/usr/bin/env python3
"""
Prepare a reproducible Speech Commands experiment directory for microWakeWord.

The output structure matches the existing local conventions:
  <output>/
    positive_samples/
    negative_samples/
    ambient_samples/
    manifest.json

By default the script creates symlinks, which keeps the experiment cheap to
reset and makes it obvious that the source of truth is the original dataset.
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-root",
        default="/Users/mattias/kratt/wake-word/data/processed/speech_commands",
        help="Root directory of the Speech Commands dataset.",
    )
    parser.add_argument(
        "--target-word",
        required=True,
        help="Folder name to treat as the positive wake word class.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where the experiment dataset will be created.",
    )
    parser.add_argument(
        "--negative-limit",
        type=int,
        default=12000,
        help="Maximum number of negative samples to include. Use 0 for all.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=10,
        help="Deterministic shuffle seed used when subsampling negatives.",
    )
    parser.add_argument(
        "--link-mode",
        choices=("symlink", "copy"),
        default="symlink",
        help="Whether to symlink or copy source wav files into the experiment.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing output directory.",
    )
    return parser.parse_args()


def list_wavs(path: Path) -> list[Path]:
    return sorted(path.glob("*.wav"))


def write_link(src: Path, dst: Path, link_mode: str) -> None:
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    if link_mode == "symlink":
        dst.symlink_to(src)
    else:
        shutil.copy2(src, dst)


def materialize_files(files: list[Path], output_dir: Path, prefix: str, link_mode: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for index, src in enumerate(files):
        dst = output_dir / f"{prefix}_{index:05d}.wav"
        write_link(src.resolve(), dst, link_mode)


def main() -> None:
    args = parse_args()

    source_root = Path(args.source_root).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    target_dir = source_root / args.target_word
    ambient_dir = source_root / "_background_noise_"

    if not source_root.exists():
        raise SystemExit(f"Speech Commands root not found: {source_root}")
    if not target_dir.exists():
        raise SystemExit(f"Target word folder not found: {target_dir}")
    if not ambient_dir.exists():
        raise SystemExit(f"Ambient folder not found: {ambient_dir}")

    if output_dir.exists():
        if not args.force:
            raise SystemExit(
                f"Output directory already exists: {output_dir} (use --force to replace it)"
            )
        shutil.rmtree(output_dir)

    positive_files = list_wavs(target_dir)
    ambient_files = list_wavs(ambient_dir)

    negative_by_label: dict[str, list[Path]] = {}
    for child in sorted(source_root.iterdir()):
        if not child.is_dir():
            continue
        if child.name in {args.target_word, "_background_noise_"}:
            continue
        negative_by_label[child.name] = list_wavs(child)

    negative_files: list[Path] = []
    for label in sorted(negative_by_label):
        negative_files.extend(negative_by_label[label])

    rnd = random.Random(args.seed)
    rnd.shuffle(negative_files)
    if args.negative_limit > 0:
        negative_files = negative_files[: args.negative_limit]

    materialize_files(
        positive_files,
        output_dir / "positive_samples",
        prefix=f"{args.target_word}_positive",
        link_mode=args.link_mode,
    )
    materialize_files(
        negative_files,
        output_dir / "negative_samples",
        prefix=f"{args.target_word}_negative",
        link_mode=args.link_mode,
    )
    materialize_files(
        ambient_files,
        output_dir / "ambient_samples",
        prefix=f"{args.target_word}_ambient",
        link_mode=args.link_mode,
    )

    manifest = {
        "source_root": str(source_root),
        "target_word": args.target_word,
        "positive_count": len(positive_files),
        "negative_count": len(negative_files),
        "ambient_count": len(ambient_files),
        "negative_labels": sorted(negative_by_label),
        "negative_limit": args.negative_limit,
        "seed": args.seed,
        "link_mode": args.link_mode,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )

    print("Prepared Speech Commands experiment")
    print(f"  target word:    {args.target_word}")
    print(f"  output dir:     {output_dir}")
    print(f"  positive files: {len(positive_files)}")
    print(f"  negative files: {len(negative_files)}")
    print(f"  ambient files:  {len(ambient_files)}")
    print(f"  link mode:      {args.link_mode}")


if __name__ == "__main__":
    main()
