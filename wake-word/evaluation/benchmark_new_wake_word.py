#!/usr/bin/env python3
"""Benchmark a local new-wake-word TFLite model.

Reports three practical smoke metrics:
- recall on the wizard's eval-smoke clips, or positive-real if no eval split exists;
- false-positive rate on generated confusable negative audio and/or an extra negative dir;
- streaming FAPH on a long negative speech directory.

This is a local iteration benchmark, not a controlled thesis benchmark. It is
meant to answer: "does my freshly trained phrase model react to my phrase, and
how noisy is it?"
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Iterable

import numpy as np
import soundfile as sf

from microwakeword.inference import Model
from microwakeword.test import compute_false_accepts_per_hour

WAKE_WORD_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = WAKE_WORD_ROOT.parent
DEFAULT_FAPH_DIR = WAKE_WORD_ROOT / "data" / "processed" / "faph_test_cv_et"
AUDIO_EXTS = {".wav", ".flac"}
STEP_MS = 10
MA_WINDOW = 5
COOLDOWN_SLICES = 25


def now_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", required=True, help="Path to new-wake-word manifest.json")
    p.add_argument("--model", required=True, help="TFLite model path")
    p.add_argument("--thresholds", type=float, nargs="+", default=[0.5, 0.7, 0.9, 0.95, 0.97, 0.99, 0.995])
    p.add_argument("--negative-dir", default="", help="Extra negative/confusable WAV directory")
    p.add_argument("--faph-dir", default=str(DEFAULT_FAPH_DIR), help="Long negative stream directory")
    p.add_argument("--faph-limit", type=int, default=0, help="Optional cap on FAPH files")
    p.add_argument("--no-faph", action="store_true", help="Skip streaming FAPH")
    p.add_argument("--output-dir", default="", help="Report dir; default output-root/reports")
    p.add_argument("--per-clip", action="store_true", help="Print per-clip scores")
    return p.parse_args()


def main_checkout_root() -> Path | None:
    marker = "/.claude/worktrees/"
    root_s = str(PROJECT_ROOT)
    if marker not in root_s:
        return None
    return Path(root_s.split(marker, 1)[0])


def mapped_main_checkout_path(path: Path) -> Path | None:
    main_root = main_checkout_root()
    if main_root is None:
        return None
    try:
        rel = path.resolve(strict=False).relative_to(PROJECT_ROOT.resolve(strict=False))
    except ValueError:
        return None
    candidate = main_root / rel
    return candidate if candidate.exists() else None


def resolve_path(raw: str | Path, *, base: Path | None = None) -> Path:
    p = Path(raw).expanduser()
    if p.is_absolute():
        if p.exists():
            return p.resolve()
        mapped = mapped_main_checkout_path(p)
        if mapped is not None:
            return mapped.resolve()
        return p
    candidates = []
    if base is not None:
        candidates.append(base / p)
    candidates.extend([Path.cwd() / p, PROJECT_ROOT / p, WAKE_WORD_ROOT / p])
    main_root = main_checkout_root()
    if main_root is not None:
        candidates.extend([main_root / p, main_root / "wake-word" / p])
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return candidates[0].resolve()


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Manifest not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid manifest JSON: {path}: {exc}")


def audio_files(root: Path, recursive: bool = True) -> list[Path]:
    if not root.exists():
        return []
    it = root.rglob("*") if recursive else root.glob("*")
    return sorted(p for p in it if p.is_file() and p.suffix.lower() in AUDIO_EXTS)


def dedupe(paths: Iterable[Path]) -> list[Path]:
    seen: set[Path] = set()
    out: list[Path] = []
    for p in paths:
        key = p.resolve(strict=False)
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def load_16k(path: Path) -> np.ndarray:
    audio, sr = sf.read(str(path), always_2d=False)
    if getattr(audio, "ndim", 1) > 1:
        audio = audio[:, 0]
    audio = audio.astype(np.float32, copy=False)
    if sr != 16000:
        import librosa

        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000).astype(np.float32, copy=False)
    return (np.clip(audio, -1.0, 1.0) * 32767.0).astype(np.int16)


def moving_average(values: np.ndarray, window: int = MA_WINDOW) -> np.ndarray:
    if window <= 1 or values.size < window:
        return values
    return np.convolve(values, np.ones(window, dtype=np.float32) / window, mode="valid")


def reset(model: Model) -> None:
    try:
        model.reset_states()
    except Exception:
        pass


def score_clips(model: Model, files: list[Path]) -> list[dict]:
    rows: list[dict] = []
    for index, wav in enumerate(files, start=1):
        pcm = load_16k(wav)
        raw = np.array(model.predict_clip(pcm, step_ms=STEP_MS), dtype=np.float32)
        smoothed = moving_average(raw)
        max_raw = float(raw.max()) if raw.size else 0.0
        max_ma = float(smoothed.max()) if smoothed.size else max_raw
        reset(model)
        rows.append(
            {
                "index": index,
                "path": str(wav),
                "duration_s": len(pcm) / 16000.0,
                "max_score_ma": max_ma,
                "max_score_raw": max_raw,
            }
        )
    return rows


def summarize_clip_metric(rows: list[dict], thresholds: list[float], *, positive: bool) -> list[dict]:
    scores = np.array([r["max_score_ma"] for r in rows], dtype=np.float32)
    out: list[dict] = []
    for threshold in thresholds:
        hits = int((scores >= threshold).sum()) if scores.size else 0
        value = (hits / len(rows)) if rows else 0.0
        out.append(
            {
                "threshold": threshold,
                "hits": hits,
                "count": len(rows),
                "value": value,
                "percent": 100.0 * value,
                "meaning": "recall" if positive else "false_positive_rate",
            }
        )
    return out


def build_track(files: list[Path], inter_clip_silence_ms: int = 300) -> np.ndarray:
    silence = np.zeros((inter_clip_silence_ms * 16000) // 1000, dtype=np.int16)
    parts: list[np.ndarray] = []
    for index, f in enumerate(files):
        if index > 0:
            parts.append(silence)
        parts.append(load_16k(f))
    return np.concatenate(parts) if parts else np.zeros(0, dtype=np.int16)


def run_faph(model: Model, files: list[Path], thresholds: list[float]) -> dict:
    track = build_track(files)
    hours = (len(track) / 16000.0) / 3600.0
    raw = np.array(model.predict_clip(track, step_ms=STEP_MS), dtype=np.float32)
    smoothed = moving_average(raw)
    faph_values = compute_false_accepts_per_hour(
        [smoothed],
        cutoffs=np.array(thresholds, dtype=np.float32),
        ignore_slices_after_accept=COOLDOWN_SLICES,
        stride=1,
        step_s=STEP_MS / 1000.0,
    )
    reset(model)
    return {
        "files": len(files),
        "hours": hours,
        "thresholds": [
            {
                "threshold": float(t),
                "faph": float(f),
                "activations_estimated": int(round(float(f) * hours)),
            }
            for t, f in zip(thresholds, faph_values)
        ],
    }


def write_clip_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["index", "path", "duration_s", "max_score_ma", "max_score_raw"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary_csv(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for item in report.get("positive_summary", []):
        rows.append({"set": report.get("positive_set"), "metric": "recall", **item})
    for item in report.get("negative_summary", []):
        rows.append({"set": report.get("negative_set"), "metric": "confusable_fpr", **item})
    for item in report.get("faph", {}).get("thresholds", []):
        rows.append(
            {
                "set": report.get("faph_set"),
                "metric": "faph",
                "threshold": item["threshold"],
                "hits": item["activations_estimated"],
                "count": report.get("faph", {}).get("files", 0),
                "value": item["faph"],
                "percent": "",
                "meaning": "false_accepts_per_hour",
            }
        )
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        fieldnames = ["set", "metric", "threshold", "hits", "count", "value", "percent", "meaning"]
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def print_clip_summary(title: str, rows: list[dict], summaries: list[dict]) -> None:
    print(f"\n{title}")
    if not rows:
        print("  no clips")
        return
    scores = [r["max_score_ma"] for r in rows]
    arr = np.array(scores, dtype=np.float32)
    print(f"  clips={len(rows)} mean={mean(scores):.3f} min={arr.min():.3f} median={np.median(arr):.3f} max={arr.max():.3f}")
    for s in summaries:
        print(f"  >= {s['threshold']:g}: {s['hits']}/{s['count']} = {s['percent']:.1f}% ({s['meaning']})")


def main() -> int:
    args = parse_args()
    manifest_path = resolve_path(args.manifest)
    model_path = resolve_path(args.model)
    if not model_path.exists():
        raise SystemExit(f"Model not found: {model_path}")

    manifest = load_json(manifest_path)
    output_root = manifest_path.parent
    phrase = manifest.get("wizard", {}).get("phrase") or manifest.get("prompts", {}).get("target") or "wake word"
    slug = manifest.get("wizard", {}).get("slug") or output_root.name

    positive_dir = output_root / "audio" / "eval-smoke"
    positive_set = "eval-smoke"
    positives = audio_files(positive_dir)
    notes = ["Local benchmark: use for quick iteration, not for thesis-grade claims."]
    if not positives:
        positive_dir = output_root / "audio" / "positive-real"
        positives = audio_files(positive_dir)
        positive_set = "positive-real-not-held-out"
        notes.append("No eval-smoke clips found; scoring positive-real, which may overlap training.")

    negative_dirs = [output_root / "audio" / "negative-confusable-tts"]
    if args.negative_dir:
        negative_dirs.append(resolve_path(args.negative_dir))
    negatives = dedupe([p for d in negative_dirs for p in audio_files(d)])

    faph_dir = resolve_path(args.faph_dir)
    faph_files = audio_files(faph_dir)
    if args.faph_limit > 0:
        faph_files = faph_files[: args.faph_limit]

    report_dir = resolve_path(args.output_dir, base=output_root) if args.output_dir else output_root / "reports"
    report_tag = f"benchmark-{model_path.stem}-{now_tag()}"
    report_json = report_dir / f"{report_tag}.json"
    summary_csv = report_dir / f"{report_tag}.csv"
    positive_csv = report_dir / f"{report_tag}-positive-clips.csv"
    negative_csv = report_dir / f"{report_tag}-negative-clips.csv"

    print("=== Benchmark local new wake-word model ===")
    print(f"Phrase:   {phrase}")
    print(f"Slug:     {slug}")
    print(f"Manifest: {manifest_path}")
    print(f"Model:    {model_path}")

    model = Model(str(model_path))

    positive_rows = score_clips(model, positives) if positives else []
    positive_summary = summarize_clip_metric(positive_rows, args.thresholds, positive=True)
    print_clip_summary(f"Positive set: {positive_set}", positive_rows, positive_summary)

    negative_rows = score_clips(model, negatives) if negatives else []
    negative_summary = summarize_clip_metric(negative_rows, args.thresholds, positive=False)
    print_clip_summary("Confusable negative set", negative_rows, negative_summary)

    faph_result: dict = {}
    if args.no_faph:
        notes.append("FAPH skipped via --no-faph.")
    elif faph_files:
        print(f"\nFAPH set: {faph_dir} ({len(faph_files)} files)")
        faph_result = run_faph(model, faph_files, args.thresholds)
        print(f"  duration={faph_result['hours']:.3f}h")
        for row in faph_result["thresholds"]:
            print(f"  >= {row['threshold']:g}: FAPH={row['faph']:.2f}, activations≈{row['activations_estimated']}")
    else:
        notes.append(f"No FAPH files found under {faph_dir}.")

    if args.per_clip:
        print("\nPer-clip positive scores")
        for row in positive_rows:
            print(f"  {row['max_score_ma']:.6f}  {row['path']}")
        print("\nPer-clip negative scores")
        for row in negative_rows:
            print(f"  {row['max_score_ma']:.6f}  {row['path']}")

    report = {
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "phrase": phrase,
        "slug": slug,
        "manifest": str(manifest_path),
        "model": str(model_path),
        "thresholds": args.thresholds,
        "notes": notes,
        "positive_set": positive_set,
        "positive_dir": str(positive_dir),
        "positive_clips": len(positive_rows),
        "positive_summary": positive_summary,
        "negative_set": ",".join(str(d) for d in negative_dirs),
        "negative_clips": len(negative_rows),
        "negative_summary": negative_summary,
        "faph_set": str(faph_dir),
        "faph": faph_result,
    }

    report_dir.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_summary_csv(summary_csv, report)
    write_clip_csv(positive_csv, positive_rows)
    write_clip_csv(negative_csv, negative_rows)

    print("\nReports:")
    print(f"  {report_json}")
    print(f"  {summary_csv}")
    if positive_rows:
        print(f"  {positive_csv}")
    if negative_rows:
        print(f"  {negative_csv}")
    for note in notes:
        print(f"Note: {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
