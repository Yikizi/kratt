#!/usr/bin/env python3
"""Build context-aware `Kratt` positive crops for the v19b side branch.

Motivation: v19a used short isolated `Kratt` cuts. During microWakeWord mmap
creation, every <1s positive was left-padded with silence, so the model could
learn `[silence] + Kratt` instead of `Kratt` in natural phrase context. This
builder writes fixed-duration crops where `Kratt` appears at varied offsets and
where the left context may contain `e/le/ule/kuule/kule` speech rather than
artificial silence.

The output is a local data artifact (under wake-word/data/processed by default),
not a training launch.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
import shutil
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

# Reuse the boundary estimator and source filtering from the reviewed v19a
# extractor rather than maintaining two independent boundary heuristics.
from extract_kratt_segments import (  # type: ignore
    DEFAULT_EXCLUDE_PATTERNS,
    DEFAULT_SOURCE_DIRS,
    BoundaryResult,
    collect_wavs,
    compile_patterns,
    estimate_boundary,
    filter_wavs_by_source_duration,
    load_audio,
    resolve_path,
    sha256_file,
    write_jsonl,
)

WAKE_WORD_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = WAKE_WORD_ROOT / "data" / "processed" / "positive_kratt_context_v19b"
DEFAULT_INCLUDE_PATTERNS = [r"kratt"]
DEFAULT_OFFSETS_MS = [40, 160, 280, 400]


@dataclass(frozen=True)
class CropVariant:
    name: str
    requested_offset_ms: int
    actual_offset_ms: int
    crop_start_ms: int
    crop_end_ms: int
    right_pad_ms: int
    flags: list[str]


def safe_reset_dir(path: Path, force: bool) -> None:
    if path.exists():
        if not force:
            raise SystemExit(f"Output exists: {path} (use --force)")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def stable_slug(path: Path) -> str:
    stem = path.stem
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", stem)
    stem = re.sub(r"_+", "_", stem).strip("_")
    return stem[:96] if stem else "clip"


def prefix_variant(path: Path) -> str:
    text = path.name.lower()
    for candidate in ("kuuule", "kuulee", "guule", "gule", "kuule", "kule"):
        if candidate in text:
            return candidate
    return "unknown"


def crop_fixed_window(
    audio: np.ndarray,
    sr: int,
    *,
    kratt_start_s: float,
    offset_ms: int,
    window_ms: int,
) -> tuple[np.ndarray, CropVariant]:
    source_duration_s = len(audio) / float(sr)
    window_samples = int(round(window_ms * sr / 1000.0))
    requested_start_s = kratt_start_s - (offset_ms / 1000.0)
    crop_start_s = max(0.0, requested_start_s)
    start = int(round(crop_start_s * sr))
    end = start + window_samples

    right_pad = max(0, end - len(audio))
    segment = audio[start : min(end, len(audio))]
    if right_pad:
        segment = np.pad(segment, (0, right_pad))
    if segment.size < window_samples:
        segment = np.pad(segment, (0, window_samples - segment.size))
    elif segment.size > window_samples:
        segment = segment[:window_samples]

    actual_offset_ms = int(round((kratt_start_s - crop_start_s) * 1000.0))
    flags: list[str] = []
    if requested_start_s < 0:
        flags.append("left_clamped_to_source_start")
    if right_pad:
        flags.append("right_padded")
    if actual_offset_ms < max(0, offset_ms - 25):
        flags.append("less_left_context_than_requested")
    if actual_offset_ms > window_ms - 420:
        flags.append("limited_tail_after_kratt")
    if crop_start_s <= 0.005:
        flags.append("starts_at_source_start")

    return segment.astype(np.float32), CropVariant(
        name=f"ctx{offset_ms:03d}",
        requested_offset_ms=offset_ms,
        actual_offset_ms=actual_offset_ms,
        crop_start_ms=int(round(crop_start_s * 1000.0)),
        crop_end_ms=int(round((crop_start_s + window_ms / 1000.0) * 1000.0)),
        right_pad_ms=int(round(right_pad / sr * 1000.0)),
        flags=sorted(set(flags)),
    )


def write_wav(path: Path, audio: np.ndarray, sr: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), np.clip(audio, -1.0, 1.0), sr, subtype="PCM_16")


def symlink_relative(target: Path, link: Path) -> None:
    link.parent.mkdir(parents=True, exist_ok=True)
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(Path("../..") / "accepted" / target.name)


def build_review_samples(output_dir: Path, rows: list[dict[str, Any]], *, seed: int, random_n: int) -> None:
    accepted_rows = [row for row in rows if row.get("status") == "accepted"]
    if not accepted_rows:
        return
    rng = random.Random(seed)
    random_rows = accepted_rows[:]
    rng.shuffle(random_rows)

    buckets: dict[str, list[dict[str, Any]]] = {
        "random_sample": random_rows[: min(random_n, len(random_rows))],
        "low_boundary_confidence": [r for r in accepted_rows if "low_boundary_confidence" in r.get("boundary_flags", [])][:random_n],
        "left_clamped": [r for r in accepted_rows if "left_clamped_to_source_start" in r.get("variant_flags", [])][:random_n],
        "right_padded": [r for r in accepted_rows if "right_padded" in r.get("variant_flags", [])][:random_n],
        "ctx040": [r for r in accepted_rows if r.get("variant") == "ctx040"][: min(random_n, len(accepted_rows))],
        "ctx160": [r for r in accepted_rows if r.get("variant") == "ctx160"][: min(random_n, len(accepted_rows))],
        "ctx280": [r for r in accepted_rows if r.get("variant") == "ctx280"][: min(random_n, len(accepted_rows))],
        "ctx400": [r for r in accepted_rows if r.get("variant") == "ctx400"][: min(random_n, len(accepted_rows))],
    }

    for bucket, bucket_rows in buckets.items():
        for row in bucket_rows:
            target = output_dir / row["output_file"]
            link = output_dir / "review" / bucket / f"{int(row['index']):05d}_{target.name}"
            symlink_relative(target, link)

    review_csv = output_dir / "review" / "review-sample.csv"
    review_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "index", "variant", "output_file", "source_file", "prefix_variant",
        "actual_offset_ms", "boundary_confidence", "boundary_flags", "variant_flags",
    ]
    seen: set[tuple[int, str]] = set()
    with review_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for bucket_rows in buckets.values():
            for row in bucket_rows:
                key = (int(row["index"]), str(row["variant"]))
                if key in seen:
                    continue
                seen.add(key)
                writer.writerow({name: row.get(name, "") for name in fieldnames})


def parse_offsets(value: str) -> list[int]:
    offsets: list[int] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        offsets.append(int(part))
    if not offsets:
        raise argparse.ArgumentTypeError("at least one offset is required")
    return offsets


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", action="append", default=[], help="Source directory; may be repeated. Default: positive_strict_kuule_kule")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help=f"Output dataset dir (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--include-pattern", action="append", default=[], help="Regex for source WAV names. Default: kratt")
    parser.add_argument("--exclude-pattern", action="append", default=[], help="Extra source-name regex to exclude")
    parser.add_argument("--window-ms", type=int, default=1000, help="Fixed output crop duration. Default: 1000")
    parser.add_argument("--kratt-offset-ms", type=parse_offsets, default=DEFAULT_OFFSETS_MS, help="Comma-separated target offsets from crop start. Default: 40,160,280,400")
    parser.add_argument("--sample", type=int, default=0, help="Randomly sample N source clips before variants")
    parser.add_argument("--limit", type=int, default=0, help="Limit source clips after sorting/sampling")
    parser.add_argument("--seed", type=int, default=20260506)
    parser.add_argument("--target-sr", type=int, default=16000)
    parser.add_argument("--min-source-duration-s", type=float, default=0.70)
    parser.add_argument("--max-source-duration-s", type=float, default=3.00)
    parser.add_argument("--review-sample", type=int, default=40)
    parser.add_argument("--dry-run", action="store_true", help="Write manifest/summary only, no audio")
    parser.add_argument("--force", action="store_true", help="Replace output dir if it exists")

    # Boundary-estimator knobs copied from extract_kratt_segments defaults used for v19a.
    parser.add_argument("--frame-ms", type=float, default=25.0)
    parser.add_argument("--hop-ms", type=float, default=10.0)
    parser.add_argument("--speech-rel-db", type=float, default=-35.0)
    parser.add_argument("--low-confidence-threshold", type=float, default=0.55)
    parser.add_argument("--search-min-fraction", type=float, default=0.30)
    parser.add_argument("--search-max-fraction", type=float, default=0.66)
    parser.add_argument("--boundary-target-fraction", type=float, default=0.50)
    parser.add_argument("--min-boundary-tail-s", type=float, default=0.38)
    args = parser.parse_args()

    if args.window_ms <= 0:
        raise SystemExit("--window-ms must be positive")
    if any(offset < 0 or offset >= args.window_ms for offset in args.kratt_offset_ms):
        raise SystemExit("all offsets must be in [0, window_ms)")

    source_dirs = [resolve_path(p) for p in args.source_dir] if args.source_dir else DEFAULT_SOURCE_DIRS
    output_dir = resolve_path(args.output_dir)
    include_patterns = compile_patterns(args.include_pattern or DEFAULT_INCLUDE_PATTERNS)
    exclude_patterns = compile_patterns(DEFAULT_EXCLUDE_PATTERNS + args.exclude_pattern)

    wavs = collect_wavs(source_dirs, include_patterns, exclude_patterns)
    wavs, duration_counts = filter_wavs_by_source_duration(
        wavs, args.min_source_duration_s, args.max_source_duration_s
    )
    if args.sample:
        rng = random.Random(args.seed)
        wavs = wavs[:]
        rng.shuffle(wavs)
        wavs = sorted(wavs[: args.sample])
    if args.limit:
        wavs = wavs[: args.limit]
    if not wavs:
        raise SystemExit("No source WAVs matched")

    safe_reset_dir(output_dir, args.force)
    accepted_dir = output_dir / "accepted"
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    variant_counts: Counter[str] = Counter()
    flag_counts: Counter[str] = Counter()
    boundary_flag_counts: Counter[str] = Counter()
    prefix_counts: Counter[str] = Counter()
    offset_values: list[int] = []
    right_pad_values: list[int] = []

    for source_index, wav in enumerate(wavs):
        try:
            audio, sr, original_sr = load_audio(wav, args.target_sr)
            boundary: BoundaryResult = estimate_boundary(
                audio,
                sr,
                frame_ms=args.frame_ms,
                hop_ms=args.hop_ms,
                speech_rel_db=args.speech_rel_db,
                low_confidence_threshold=args.low_confidence_threshold,
                search_min_fraction=args.search_min_fraction,
                search_max_fraction=args.search_max_fraction,
                boundary_target_fraction=args.boundary_target_fraction,
                min_boundary_tail_s=args.min_boundary_tail_s,
            )
            source_hash = sha256_file(wav.resolve())
            source_prefix = prefix_variant(wav)
            prefix_counts[source_prefix] += 1

            for offset_ms in args.kratt_offset_ms:
                crop, variant = crop_fixed_window(
                    audio,
                    sr,
                    kratt_start_s=boundary.kratt_start_s,
                    offset_ms=int(offset_ms),
                    window_ms=args.window_ms,
                )
                filename = f"ctx_{source_index:05d}_{variant.name}_{stable_slug(wav)}.wav"
                rel_output = Path("accepted") / filename
                if not args.dry_run:
                    write_wav(output_dir / rel_output, crop, sr)

                variant_counts[variant.name] += 1
                for flag in variant.flags:
                    flag_counts[flag] += 1
                for flag in boundary.flags:
                    boundary_flag_counts[flag] += 1
                offset_values.append(variant.actual_offset_ms)
                right_pad_values.append(variant.right_pad_ms)

                rows.append(
                    {
                        "status": "accepted",
                        "index": source_index,
                        "variant": variant.name,
                        "output_file": str(rel_output),
                        "source_file": str(wav.resolve()),
                        "source_sha256": source_hash,
                        "source_sample_rate": original_sr,
                        "target_sample_rate": sr,
                        "source_duration_ms": int(round(len(audio) / sr * 1000.0)),
                        "prefix_variant": source_prefix,
                        "window_ms": args.window_ms,
                        "requested_offset_ms": variant.requested_offset_ms,
                        "actual_offset_ms": variant.actual_offset_ms,
                        "crop_start_ms": variant.crop_start_ms,
                        "crop_end_ms": variant.crop_end_ms,
                        "right_pad_ms": variant.right_pad_ms,
                        "boundary_ms": int(round(boundary.boundary_s * 1000.0)),
                        "kratt_start_ms": int(round(boundary.kratt_start_s * 1000.0)),
                        "speech_start_ms": int(round(boundary.speech_start_s * 1000.0)),
                        "speech_end_ms": int(round(boundary.speech_end_s * 1000.0)),
                        "boundary_confidence": boundary.confidence,
                        "boundary_method": boundary.method,
                        "boundary_flags": boundary.flags,
                        "variant_flags": variant.flags,
                    }
                )
        except Exception as exc:  # noqa: BLE001 - data-prep should keep going and report broken sources
            errors.append({"source_file": str(wav), "error": repr(exc)})

    write_jsonl(output_dir / "manifest.jsonl", rows)
    if errors:
        write_jsonl(output_dir / "errors.jsonl", errors)
    if not args.dry_run:
        build_review_samples(output_dir, rows, seed=args.seed, random_n=args.review_sample)

    summary = {
        "dataset": output_dir.name,
        "policy": "Context-aware Kratt positives: fixed-duration crops with varied left speech context, not isolated silence-padded Kratt cuts.",
        "source_dirs": [str(p) for p in source_dirs],
        "source_wavs": len(wavs),
        "accepted_clips": len(rows),
        "errors": len(errors),
        "dry_run": bool(args.dry_run),
        "parameters": {
            "window_ms": args.window_ms,
            "kratt_offset_ms": args.kratt_offset_ms,
            "target_sr": args.target_sr,
            "min_source_duration_s": args.min_source_duration_s,
            "max_source_duration_s": args.max_source_duration_s,
            "include_patterns": args.include_pattern or DEFAULT_INCLUDE_PATTERNS,
            "exclude_patterns": DEFAULT_EXCLUDE_PATTERNS + args.exclude_pattern,
            "boundary": {
                "frame_ms": args.frame_ms,
                "hop_ms": args.hop_ms,
                "speech_rel_db": args.speech_rel_db,
                "low_confidence_threshold": args.low_confidence_threshold,
                "search_min_fraction": args.search_min_fraction,
                "search_max_fraction": args.search_max_fraction,
                "boundary_target_fraction": args.boundary_target_fraction,
                "min_boundary_tail_s": args.min_boundary_tail_s,
            },
        },
        "duration_filter_counts": duration_counts,
        "variant_counts": dict(sorted(variant_counts.items())),
        "prefix_variant_source_counts": dict(sorted(prefix_counts.items())),
        "variant_flag_counts": dict(sorted(flag_counts.items())),
        "boundary_flag_counts_by_clip_variant": dict(sorted(boundary_flag_counts.items())),
        "actual_offset_ms": {
            "min": min(offset_values) if offset_values else None,
            "median": float(np.median(offset_values)) if offset_values else None,
            "max": max(offset_values) if offset_values else None,
        },
        "right_pad_ms": {
            "max": max(right_pad_values) if right_pad_values else None,
            "clips_with_right_pad": int(sum(1 for value in right_pad_values if value > 0)),
        },
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    readme = f"""# {output_dir.name}

Context-aware `Kratt` positive dataset for a possible v19b side experiment.

## Why this exists

v19a used isolated `Kratt` cuts shorter than 1 s. microWakeWord padded those
positives on the **left**, so the model could learn `[silence] + Kratt`. This
dataset instead writes fixed `{args.window_ms}` ms clips where `Kratt` appears at
varied offsets and where the left side may contain `e/le/ule/kuule/kule` speech.

## Counts

- Source WAVs: **{len(wavs)}**
- Accepted clips: **{len(rows)}**
- Variants per source: `{', '.join(str(x) for x in args.kratt_offset_ms)}` ms target offsets
- Errors: **{len(errors)}**

## Training policy

Use this only for a **Kratt-only target-policy ablation**. It is not a two-word
`Kuule/Kule Kratt` exact-phrase dataset. Do not mix it into exact-phrase claims
without a separate manifest and caveat.

Recommended first use, if training is explicitly allowed:

- positive dir: `data/processed/{output_dir.name}/accepted`
- keep `clip_duration_ms` equal to `{args.window_ms}` ms so no new left-padding is introduced;
- add target-free `Kratt`-like hard negatives before making any quality claim.

Review samples are under `review/`.
"""
    (output_dir / "README.md").write_text(readme, encoding="utf-8")

    print(f"Dataset: {output_dir}")
    print(f"Source WAVs: {len(wavs)}")
    print(f"Accepted clips: {len(rows)}")
    print(f"Errors: {len(errors)}")
    print(f"Summary: {output_dir / 'summary.json'}")
    print(f"Manifest: {output_dir / 'manifest.jsonl'}")
    if not args.dry_run:
        print(f"Review: {output_dir / 'review'}")


if __name__ == "__main__":
    main()
