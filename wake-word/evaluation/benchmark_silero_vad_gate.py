#!/usr/bin/env python3
"""Estimate Silero VAD coverage characteristics for wake-word gating.

This script does NOT run a wake-word model. It only answers:
  1) how much speech appears in positive recall sets
  2) how much speech appears in ambient/FAPH sets
  3) what optimistic FAPH reduction looks like if wake-word scoring is gated by VAD

It reads set directories from the canonical registry in ``test_sets.py``.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import soundfile as sf

from test_sets import TEST_SETS, TestSetKind


DEFAULT_MIN_SPEECH_MS = 250
DEFAULT_MIN_SILENCE_MS = 200
DEFAULT_VAD_PAD_MS = 120
DEFAULT_MERGE_GAP_MS = 160
DEFAULT_LATENCY_WARN_MS = 250.0


@dataclass
class FileVadResult:
    path: Path
    speech_ratio: float
    speech_duration_s: float
    duration_s: float
    first_speech_ms: float | None
    segment_count: int


def load_vad_backend():
    try:
        import torch
        from silero_vad import get_speech_timestamps
        from silero_vad import load_silero_vad as _load
    except Exception as exc:  # pragma: no cover - environment specific
        return None, None, False, f"silero_vad unavailable: {exc}"

    torch.set_num_threads(1)
    model = _load()
    return model, get_speech_timestamps, True, "silero_vad"


def load_audio_16k(path: Path) -> tuple[np.ndarray, int]:
    audio, sr = sf.read(str(path), always_2d=False)
    if isinstance(audio, np.ndarray) and audio.ndim > 1:
        audio = audio[:, 0]
    audio = audio.astype(np.float32, copy=False)
    if sr == 16000:
        return np.clip(audio, -1.0, 1.0), sr

    try:
        import librosa
    except Exception as exc:  # pragma: no cover - environment specific
        raise RuntimeError(f"resampling to 16kHz required but librosa missing: {exc}") from exc

    return np.clip(librosa.resample(audio, orig_sr=sr, target_sr=16000), -1.0, 1.0), 16000


def list_audio_files(root: Path, exts: Iterable[str], limit: int | None) -> list[Path]:
    files: list[Path] = []
    for ext in exts:
        files.extend(sorted(root.rglob(ext)))
    if limit and limit > 0:
        files = files[:limit]
    return sorted(set(files), key=lambda p: str(p))


def merge_segments(segments: list[tuple[int, int]], gap_ms: int, sr: int) -> list[tuple[int, int]]:
    if not segments:
        return []

    segments = sorted(segments)
    gap_s = gap_ms / 1000.0
    merged: list[list[int]] = [[segments[0][0], segments[0][1]]]
    for start, end in segments[1:]:
        if start <= merged[-1][1] + int(gap_s * sr):
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [(start, end) for start, end in merged]


def analyze_vad(
    audio: np.ndarray,
    sr: int,
    model,
    get_speech_timestamps,
    *,
    min_speech_ms: int,
    min_silence_ms: int,
    vad_pad_ms: int,
    merge_gap_ms: int,
) -> list[tuple[int, int]]:
    try:
        import torch
    except Exception as exc:  # pragma: no cover - environment specific
        raise RuntimeError(f"torch unavailable for Silero VAD: {exc}") from exc

    if audio.size == 0:
        return []

    model.reset_states()
    tensor = torch.from_numpy(audio).float()
    timestamps = get_speech_timestamps(
        tensor,
        model,
        sampling_rate=sr,
        min_speech_duration_ms=min_speech_ms,
        min_silence_duration_ms=min_silence_ms,
        speech_pad_ms=vad_pad_ms,
    )
    segments = [(int(ts["start"]), int(ts["end"])) for ts in timestamps]
    segments = [seg for seg in segments if seg[1] > seg[0]]
    return merge_segments(segments, merge_gap_ms, sr)


def analyze_file(
    path: Path,
    vad_model,
    get_speech_timestamps,
    *,
    min_speech_ms: int,
    min_silence_ms: int,
    vad_pad_ms: int,
    merge_gap_ms: int,
) -> FileVadResult | None:
    audio, sr = load_audio_16k(path)
    if audio.size == 0:
        return None

    segments = analyze_vad(
        audio,
        sr,
        vad_model,
        get_speech_timestamps,
        min_speech_ms=min_speech_ms,
        min_silence_ms=min_silence_ms,
        vad_pad_ms=vad_pad_ms,
        merge_gap_ms=merge_gap_ms,
    )

    duration_s = len(audio) / sr if sr else 0.0
    speech_samples = sum(end - start for start, end in segments)
    speech_duration_s = speech_samples / sr if sr else 0.0
    speech_ratio = speech_samples / len(audio) if len(audio) else 0.0
    first_speech_ms = (segments[0][0] / sr * 1000.0) if segments else None
    return FileVadResult(
        path=path,
        speech_ratio=float(speech_ratio),
        speech_duration_s=float(speech_duration_s),
        duration_s=float(duration_s),
        first_speech_ms=None if first_speech_ms is None else float(first_speech_ms),
        segment_count=len(segments),
    )


def collect_set_results(
    paths: list[Path],
    vad_model,
    get_speech_timestamps,
    *,
    min_speech_ms: int,
    min_silence_ms: int,
    vad_pad_ms: int,
    merge_gap_ms: int,
) -> tuple[list[FileVadResult], list[tuple[Path, str]]]:
    results: list[FileVadResult] = []
    errors: list[tuple[Path, str]] = []

    for path in paths:
        try:
            item = analyze_file(
                path,
                vad_model,
                get_speech_timestamps,
                min_speech_ms=min_speech_ms,
                min_silence_ms=min_silence_ms,
                vad_pad_ms=vad_pad_ms,
                merge_gap_ms=merge_gap_ms,
            )
            if item is not None:
                results.append(item)
        except Exception as exc:  # pragma: no cover - environment specific
            errors.append((path, str(exc)))
    return results, errors


def summarize_positive(results: list[FileVadResult], latency_warn_ms: float) -> dict:
    n = len(results)
    if n == 0:
        return {"n": 0}

    speech_ratios = [r.speech_ratio for r in results]
    first_ms = [r.first_speech_ms for r in results if r.first_speech_ms is not None]
    no_speech_files = sum(1 for r in results if r.speech_duration_s <= 0.0)
    late_files = sum(1 for r in results if r.first_speech_ms is not None and r.first_speech_ms > latency_warn_ms)

    return {
        "n": n,
        "coverage_mean_pct": float(np.mean(speech_ratios) * 100.0),
        "coverage_median_pct": float(np.median(speech_ratios) * 100.0),
        "coverage_min_pct": float(np.min(speech_ratios) * 100.0),
        "coverage_max_pct": float(np.max(speech_ratios) * 100.0),
        "first_speech_ms_p50": float(np.median(first_ms)) if first_ms else None,
        "first_speech_ms_p95": float(np.percentile(first_ms, 95)) if len(first_ms) > 1 else (first_ms[0] if first_ms else None),
        "no_speech_files": no_speech_files,
        "no_speech_pct": (no_speech_files / n) * 100.0,
        "late_files": late_files,
        "late_files_pct": (late_files / n) * 100.0,
        "latency_warn_ms": float(latency_warn_ms),
        "speech_dur_total_s": float(sum(r.speech_duration_s for r in results)),
        "duration_total_s": float(sum(r.duration_s for r in results)),
    }


def summarize_ambient(results: list[FileVadResult]) -> dict:
    n = len(results)
    if n == 0:
        return {"n": 0}

    speech_dur = sum(r.speech_duration_s for r in results)
    total_dur = sum(r.duration_s for r in results)
    segment_count = sum(r.segment_count for r in results)
    segment_durations = [r.speech_duration_s for r in results if r.segment_count > 0]

    return {
        "n": n,
        "speech_dur_total_s": float(speech_dur),
        "duration_total_s": float(total_dur),
        "speech_duty_cycle": (speech_dur / total_dur) if total_dur > 0 else 0.0,
        "segment_count": segment_count,
        "segment_count_per_hour": (segment_count / (total_dur / 3600.0)) if total_dur > 0 else 0.0,
        "segment_duration_median_s": float(np.median(segment_durations)) if segment_durations else None,
        "segment_duration_p95_s": float(np.percentile(segment_durations, 95)) if len(segment_durations) > 1 else (segment_durations[0] if segment_durations else None),
    }


def read_baseline_faph(csv_path: Path, model_filter: str | None, threshold: float | None) -> dict[str, float]:
    values: dict[str, float] = {}
    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("metric") != "faph":
                continue
            if model_filter and row.get("model") != model_filter:
                continue
            if threshold is not None:
                try:
                    if abs(float(row.get("threshold", "nan")) - threshold) > 1e-6:
                        continue
                except ValueError:
                    continue
            test_set = row.get("test_set")
            if not test_set:
                continue
            try:
                values[test_set] = float(row.get("value", "nan"))
            except ValueError:
                continue
    return values


def print_positive_report(results_by_set: dict[str, dict], latency_warn_ms: float) -> tuple[int, int]:
    total_files = sum(v["n"] for v in results_by_set.values())
    no_speech_files = sum(v.get("no_speech_files", 0) for v in results_by_set.values())
    late_files = sum(v.get("late_files", 0) for v in results_by_set.values())

    print("\nPositive sets (recall):")
    for name, stats in sorted(results_by_set.items()):
        if stats["n"] == 0:
            print(f"  {name:24s}  no files")
            continue
        first_speech = stats["first_speech_ms_p95"]
        first_speech_txt = "n/a" if first_speech is None else f"{first_speech:.1f}ms"
        print(
            f"  {name:24s} n={stats['n']:4d}  coverage={stats['coverage_mean_pct']:5.1f}% (mean),"
            f" {stats['coverage_median_pct']:5.1f}% (median),"
            f" no_speech={stats['no_speech_pct']:5.1f}%"
            f" first_speech_p95={first_speech_txt}"
        )

    risk = (no_speech_files / total_files * 100.0) if total_files else 0.0
    late_risk = (late_files / total_files * 100.0) if total_files else 0.0
    print("  Warning: VAD-gate recall risk")
    print(f"    - {no_speech_files:4d}/{total_files} files have no detected speech ({risk:5.1f}%)")
    print(f"    - {late_files:4d}/{total_files} files have first speech after {latency_warn_ms:.0f}ms ({late_risk:5.1f}%, potential extra miss risk)")
    if no_speech_files:
        print("    - Conservative upper-bound recall loss from VAD-gating:"
              f" {risk:.1f}%")
    return total_files, no_speech_files


def print_ambient_report(results_by_set: dict[str, dict], baseline_faph: dict[str, float] | None, baseline_threshold: float | None) -> None:
    print("\nAmbient/FAPH sets (speech duty):")
    for name, stats in sorted(results_by_set.items()):
        if stats["n"] == 0:
            print(f"  {name:24s}  no files")
            continue

        total_h = stats["duration_total_s"] / 3600.0
        speech_h = stats["speech_dur_total_s"] / 3600.0
        duty = stats["speech_duty_cycle"]
        pct = duty * 100.0
        line = f"  {name:24s} n={stats['n']:4d}  speech={speech_h:6.2f}h / {total_h:6.2f}h  duty={pct:5.1f}%"
        if baseline_faph:
            raw = baseline_faph.get(name)
            if raw is not None and not np.isnan(raw):
                gated = raw * duty
                red = (1.0 - duty) * 100.0
                threshold_txt = f"{baseline_threshold:.3f}" if baseline_threshold is not None else "n/a"
                line += (
                    f"  raw={raw:.2f} @thr={threshold_txt} -> "
                    f"gated_est={gated:.3f} ({red:.1f}% upper-bound reduction)"
                )
                print(line)
                continue
        print(line)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--positive-sets", nargs="*", default=None, help="Positive test set names")
    parser.add_argument("--ambient-sets", nargs="*", default=None, help="Ambient/FAPH set names")
    parser.add_argument("--ext", nargs="+", default=("*.wav", "*.flac"), help="Input extensions")
    parser.add_argument("--max-files-per-set", type=int, default=0, help="Optional per-set cap (0 = all)")
    parser.add_argument("--min-speech-ms", type=int, default=DEFAULT_MIN_SPEECH_MS)
    parser.add_argument("--min-silence-ms", type=int, default=DEFAULT_MIN_SILENCE_MS)
    parser.add_argument("--vad-pad-ms", type=int, default=DEFAULT_VAD_PAD_MS)
    parser.add_argument("--merge-gap-ms", type=int, default=DEFAULT_MERGE_GAP_MS)
    parser.add_argument("--latency-warn-ms", type=float, default=DEFAULT_LATENCY_WARN_MS)

    parser.add_argument("--baseline-faph-csv", type=Path, default=None, help="Optional benchmark CSV with metric=faph")
    parser.add_argument("--baseline-model", type=str, default=None, help="Filter baseline CSV by model")
    parser.add_argument("--baseline-threshold", type=float, default=None, help="Filter baseline CSV by threshold")
    parser.add_argument("--json-out", type=Path, default=None, help="Write summary JSON")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    vad_model, get_speech_timestamps, vad_ok, vad_note = load_vad_backend()
    if not vad_ok:
        raise SystemExit(f"{vad_note}\nInstall dependencies and rerun: pip install torch silero_vad")

    positive_names = args.positive_sets
    ambient_names = args.ambient_sets

    positive_sets = [s for s in TEST_SETS.values() if s.kind == TestSetKind.POSITIVE]
    ambient_sets = [s for s in TEST_SETS.values() if s.kind in (TestSetKind.AMBIENT, TestSetKind.NEGATIVE_GENERAL)]

    if positive_names:
        positive_sets = [s for s in positive_sets if s.name in set(positive_names)]
    if ambient_names:
        ambient_sets = [s for s in ambient_sets if s.name in set(ambient_names)]

    missing_positive = set(positive_names or ()) - {s.name for s in positive_sets}
    missing_ambient = set(ambient_names or ()) - {s.name for s in ambient_sets}
    if missing_positive:
        raise SystemExit(f"Unknown positive sets: {', '.join(sorted(missing_positive))}")
    if missing_ambient:
        raise SystemExit(f"Unknown ambient sets: {', '.join(sorted(missing_ambient))}")

    limit = args.max_files_per_set if args.max_files_per_set > 0 else None

    print(f"[VAD] {vad_note}")

    positive_results: dict[str, dict] = {}
    ambient_results: dict[str, dict] = {}
    errors: list[str] = []

    for test_set in positive_sets:
        paths = list_audio_files(test_set.path, args.ext, limit)
        if not paths:
            positive_results[test_set.name] = {"n": 0}
            continue
        files, file_errors = collect_set_results(
            paths,
            vad_model,
            get_speech_timestamps,
            min_speech_ms=args.min_speech_ms,
            min_silence_ms=args.min_silence_ms,
            vad_pad_ms=args.vad_pad_ms,
            merge_gap_ms=args.merge_gap_ms,
        )
        positive_results[test_set.name] = summarize_positive(files, args.latency_warn_ms)
        for p, e in file_errors:
            errors.append(f"{test_set.name}:{p.name}: {e}")

    for test_set in ambient_sets:
        paths = list_audio_files(test_set.path, args.ext, limit)
        if not paths:
            ambient_results[test_set.name] = {"n": 0}
            continue
        files, file_errors = collect_set_results(
            paths,
            vad_model,
            get_speech_timestamps,
            min_speech_ms=args.min_speech_ms,
            min_silence_ms=args.min_silence_ms,
            vad_pad_ms=args.vad_pad_ms,
            merge_gap_ms=args.merge_gap_ms,
        )
        ambient_results[test_set.name] = summarize_ambient(files)
        for p, e in file_errors:
            errors.append(f"{test_set.name}:{p.name}: {e}")

    baseline_faph = None
    if args.baseline_faph_csv is not None:
        baseline_faph = read_baseline_faph(
            args.baseline_faph_csv,
            args.baseline_model,
            args.baseline_threshold,
        )

    print_positive_report(positive_results, args.latency_warn_ms)
    print_ambient_report(ambient_results, baseline_faph, args.baseline_threshold)

    if errors:
        print("\nFile-level errors:")
        for e in errors:
            print(f"  {e}")

    if args.json_out:
        payload = {
            "positive": positive_results,
            "ambient": ambient_results,
            "baseline_faph": baseline_faph,
            "vad": {
                "min_speech_ms": args.min_speech_ms,
                "min_silence_ms": args.min_silence_ms,
                "vad_pad_ms": args.vad_pad_ms,
                "merge_gap_ms": args.merge_gap_ms,
            },
            "params": {
                "latency_warn_ms": args.latency_warn_ms,
            },
        }
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"\nWrote JSON summary: {args.json_out}")


if __name__ == "__main__":
    main()
