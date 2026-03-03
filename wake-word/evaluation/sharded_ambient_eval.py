#!/usr/bin/env python3
"""
Run microWakeWord ambient false-accept evaluation in file-level shards.

This keeps the evaluation logic compatible with microWakeWord's streaming
false-accept-per-hour calculation while allowing parallel execution across
cores or machines.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import soundfile as sf


ROOT_DIR = Path(__file__).resolve().parents[2]
MICRO_WAKE_WORD_DIR = ROOT_DIR / "external-repos" / "microWakeWord"
if str(MICRO_WAKE_WORD_DIR) not in sys.path:
    sys.path.insert(0, str(MICRO_WAKE_WORD_DIR))

from microwakeword.inference import Model  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run-shard")
    run_parser.add_argument("--model", required=True, help="Path to .tflite model")
    run_parser.add_argument("--ambient-dir", required=True, help="Directory of ambient wav files")
    run_parser.add_argument("--output", required=True, help="Shard JSON output path")
    run_parser.add_argument("--num-shards", type=int, required=True)
    run_parser.add_argument("--shard-index", type=int, required=True)
    run_parser.add_argument("--step-ms", type=int, default=10)
    run_parser.add_argument("--stride", type=int, default=1)
    run_parser.add_argument("--ma-window", type=int, default=5)
    run_parser.add_argument("--ignore-slices-after-accept", type=int, default=25)

    aggregate_parser = subparsers.add_parser("aggregate")
    aggregate_parser.add_argument("--input-dir", required=True, help="Directory of shard JSON files")
    aggregate_parser.add_argument("--output", required=True, help="Aggregate JSON output path")

    return parser.parse_args()


def load_audio_16k_mono_int16(path: Path) -> np.ndarray:
    audio, sample_rate = sf.read(str(path), always_2d=False)
    if isinstance(audio, np.ndarray) and audio.ndim > 1:
        audio = audio[:, 0]
    audio = audio.astype(np.float32, copy=False)
    if sample_rate != 16000:
        import librosa

        audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=16000).astype(
            np.float32, copy=False
        )
    audio = np.clip(audio, -1.0, 1.0)
    return (audio * 32767.0).astype(np.int16)


def moving_average(values: np.ndarray, window: int) -> np.ndarray:
    if values.size == 0 or window <= 1:
        return values
    if values.size < window:
        return np.array([], dtype=np.float32)
    kernel = np.ones(window, dtype=np.float32) / float(window)
    return np.convolve(values, kernel, mode="valid")


def assign_files(files: list[Path], num_shards: int, shard_index: int) -> list[Path]:
    return [path for idx, path in enumerate(files) if idx % num_shards == shard_index]


def count_false_accepts(
    probabilities: np.ndarray,
    cutoffs: np.ndarray,
    ignore_slices_after_accept: int,
) -> np.ndarray:
    counts = np.zeros_like(cutoffs, dtype=np.int64)
    cooldown = np.ones_like(cutoffs, dtype=np.int64) * ignore_slices_after_accept
    for probability in probabilities:
        cooldown = np.maximum(cooldown - 1, 0)
        detections = probability > cutoffs
        ready = cooldown == 0
        accepted = detections & ready
        counts[accepted] += 1
        cooldown[accepted] = ignore_slices_after_accept
    return counts


def run_shard(args: argparse.Namespace) -> int:
    ambient_dir = Path(args.ambient_dir).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(ambient_dir.glob("*.wav"))
    shard_files = assign_files(files, args.num_shards, args.shard_index)
    cutoffs = np.arange(0.0, 1.01, 0.01, dtype=np.float32)

    model = Model(str(Path(args.model).expanduser().resolve()), stride=args.stride)
    false_accept_counts = np.zeros_like(cutoffs, dtype=np.int64)
    duration_hours = 0.0
    file_summaries = []

    for path in shard_files:
        audio = load_audio_16k_mono_int16(path)
        duration_s = float(len(audio)) / 16000.0
        duration_hours += duration_s / 3600.0

        probabilities = np.asarray(model.predict_clip(audio, step_ms=args.step_ms), dtype=np.float32)
        ma_probabilities = moving_average(probabilities, args.ma_window)
        false_accept_counts += count_false_accepts(
            ma_probabilities,
            cutoffs=cutoffs,
            ignore_slices_after_accept=args.ignore_slices_after_accept,
        )
        file_summaries.append(
            {
                "file": path.name,
                "duration_s": duration_s,
                "frames": int(probabilities.size),
                "ma_frames": int(ma_probabilities.size),
                "max_score": float(probabilities.max()) if probabilities.size else math.nan,
                "max_ma_score": float(ma_probabilities.max()) if ma_probabilities.size else math.nan,
            }
        )

    payload = {
        "model": str(Path(args.model).expanduser().resolve()),
        "ambient_dir": str(ambient_dir),
        "num_shards": args.num_shards,
        "shard_index": args.shard_index,
        "cutoffs": cutoffs.tolist(),
        "false_accept_counts": false_accept_counts.tolist(),
        "duration_hours": duration_hours,
        "file_count": len(shard_files),
        "files": [path.name for path in shard_files],
        "file_summaries": file_summaries,
        "step_ms": args.step_ms,
        "stride": args.stride,
        "ma_window": args.ma_window,
        "ignore_slices_after_accept": args.ignore_slices_after_accept,
    }
    output_path.write_text(json.dumps(payload, indent=2))
    print(
        json.dumps(
            {
                "output": str(output_path),
                "file_count": len(shard_files),
                "duration_hours": round(duration_hours, 4),
            }
        )
    )
    return 0


def aggregate(args: argparse.Namespace) -> int:
    input_dir = Path(args.input_dir).expanduser().resolve()
    shard_paths = sorted(input_dir.glob("*.json"))
    if not shard_paths:
        raise FileNotFoundError(f"No shard JSON files found in {input_dir}")

    total_counts = None
    total_duration_hours = 0.0
    total_files = 0
    cutoffs = None
    shard_indexes = []

    for path in shard_paths:
        payload = json.loads(path.read_text())
        shard_cutoffs = np.asarray(payload["cutoffs"], dtype=np.float32)
        shard_counts = np.asarray(payload["false_accept_counts"], dtype=np.int64)
        if cutoffs is None:
            cutoffs = shard_cutoffs
            total_counts = np.zeros_like(shard_counts, dtype=np.int64)
        elif not np.allclose(cutoffs, shard_cutoffs):
            raise ValueError(f"Cutoff mismatch in {path}")

        total_counts += shard_counts
        total_duration_hours += float(payload["duration_hours"])
        total_files += int(payload["file_count"])
        shard_indexes.append(int(payload["shard_index"]))

    if total_duration_hours <= 0.0:
        faph = np.zeros_like(cutoffs, dtype=np.float32)
    else:
        faph = total_counts.astype(np.float64) / total_duration_hours

    result = {
        "input_dir": str(input_dir),
        "shards_found": len(shard_paths),
        "shard_indexes": sorted(shard_indexes),
        "file_count": total_files,
        "duration_hours": total_duration_hours,
        "cutoffs": cutoffs.tolist(),
        "false_accept_counts": total_counts.tolist(),
        "faph": faph.tolist(),
    }

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2))
    print(
        json.dumps(
            {
                "output": str(output_path),
                "shards_found": len(shard_paths),
                "file_count": total_files,
                "duration_hours": round(total_duration_hours, 4),
            }
        )
    )
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "run-shard":
        return run_shard(args)
    if args.command == "aggregate":
        return aggregate(args)
    raise ValueError(f"Unsupported command {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
