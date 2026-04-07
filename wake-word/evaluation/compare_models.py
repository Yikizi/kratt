#!/usr/bin/env python3
"""Compare wake-word models on TRULY held-out test sets only.

This script uses the central registry in `evaluation/test_sets.py` and
refuses to score against any directory that overlaps with a model's
training pool. For long-form ambient test sets it computes streaming FAPH
(false activations per hour) instead of clip-level FPR.

Usage:
    python compare_models.py                # all models
    python compare_models.py v6 v7 v8       # specific models
    python compare_models.py --threshold 0.97
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

from microwakeword.inference import Model

from test_sets import (
    TEST_SETS,
    TestSet,
    TestSetKind,
    assert_disjoint_from_training,
)

STEP_MS = 10
MA_WINDOW = 5
DEFAULT_THRESHOLD = 0.97
DEFAULT_REFRACTORY_MS = 2000
INTER_CLIP_SILENCE_MS = 300

# ANSI colors
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_RED = "\033[31m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_CYAN = "\033[36m"
C_BG_RED = "\033[41m"


# ─────────────────────────────────────────────────────────────────────────────
# Audio helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_audio_16k(path: Path) -> np.ndarray:
    audio, sr = sf.read(str(path), always_2d=False)
    if audio.ndim > 1:
        audio = audio[:, 0]
    audio = audio.astype(np.float32)
    if sr != 16000:
        import librosa
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
    return (np.clip(audio, -1.0, 1.0) * 32767.0).astype(np.int16)


def moving_average(values: np.ndarray, window: int) -> np.ndarray:
    if window <= 1 or values.size == 0:
        return values
    kernel = np.ones(window, dtype=np.float32) / float(window)
    return np.convolve(values, kernel, mode="valid")


def reset_model_state(model: Model) -> None:
    try:
        model.reset_states()
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Clip-level scoring (positives, hard negatives)
# ─────────────────────────────────────────────────────────────────────────────

def score_clip_max(model: Model, path: Path) -> float:
    pcm = load_audio_16k(path)
    raw = np.array(model.predict_clip(pcm, step_ms=STEP_MS), dtype=np.float32)
    if raw.size == 0:
        return 0.0
    ma = moving_average(raw, MA_WINDOW)
    return float(ma.max()) if ma.size else float(raw.max())


def score_clip_set(model: Model, test_set: TestSet) -> list[float]:
    scores = []
    for f in sorted(test_set.path.glob("*.wav")):
        scores.append(score_clip_max(model, f))
        reset_model_state(model)
    return scores


def clip_metrics(scores: list[float], is_positive: bool, threshold: float) -> dict:
    if not scores:
        return {"n": 0}
    arr = np.array(scores)
    detected = arr >= threshold
    out: dict[str, float | int] = {
        "n": len(scores),
        "mean": float(arr.mean()),
        "p5": float(np.percentile(arr, 5)),
        "p95": float(np.percentile(arr, 95)),
        "max": float(arr.max()),
    }
    if is_positive:
        out["recall"] = float(detected.sum()) / len(scores)
    else:
        out["fpr"] = float(detected.sum()) / len(scores)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Streaming FAPH scoring (long-form ambient)
# ─────────────────────────────────────────────────────────────────────────────

def streaming_faph(
    model: Model,
    test_set: TestSet,
    threshold: float,
    refractory_ms: int = DEFAULT_REFRACTORY_MS,
    silence_ms: int = INTER_CLIP_SILENCE_MS,
) -> dict:
    refractory_frames = max(1, refractory_ms // STEP_MS)
    silence = np.zeros((silence_ms * 16000) // 1000, dtype=np.int16)

    files = sorted(test_set.path.glob("*.wav"))
    if not files:
        return {"n": 0, "duration_s": 0.0, "activations": 0, "faph": 0.0}

    total_samples = 0
    activations = 0
    for f in files:
        pcm = np.concatenate([silence, load_audio_16k(f)])
        total_samples += pcm.size
        raw = np.array(model.predict_clip(pcm, step_ms=STEP_MS), dtype=np.float32)
        smoothed = moving_average(raw, MA_WINDOW)
        cooldown = 0
        for s in smoothed:
            if cooldown > 0:
                cooldown -= 1
                continue
            if s >= threshold:
                activations += 1
                cooldown = refractory_frames
        reset_model_state(model)

    duration_s = total_samples / 16000.0
    duration_h = duration_s / 3600.0
    faph = activations / duration_h if duration_h > 0 else 0.0
    return {
        "n": len(files),
        "duration_s": duration_s,
        "activations": activations,
        "faph": faph,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Pretty printing
# ─────────────────────────────────────────────────────────────────────────────

def color_pct(val: float, *, lower_is_better: bool) -> str:
    s = f"{val * 100:6.1f}%"
    if lower_is_better:
        if val <= 0.01:
            return f"{C_GREEN}{s}{C_RESET}"
        if val <= 0.05:
            return f"{C_YELLOW}{s}{C_RESET}"
        if val >= 0.5:
            return f"{C_BG_RED}{s}{C_RESET}"
        return f"{C_RED}{s}{C_RESET}"
    if val >= 0.99:
        return f"{C_GREEN}{s}{C_RESET}"
    if val >= 0.9:
        return f"{C_YELLOW}{s}{C_RESET}"
    return f"{C_RED}{s}{C_RESET}"


def color_faph(val: float) -> str:
    s = f"{val:7.2f}"
    if val <= 1.0:
        return f"{C_GREEN}{s}{C_RESET}"
    if val <= 5.0:
        return f"{C_YELLOW}{s}{C_RESET}"
    if val >= 100:
        return f"{C_BG_RED}{s}{C_RESET}"
    return f"{C_RED}{s}{C_RESET}"


def header(text: str) -> None:
    w = 78
    print(f"\n{C_CYAN}{'=' * w}{C_RESET}")
    print(f"{C_BOLD}{C_CYAN}  {text}{C_RESET}")
    print(f"{C_CYAN}{'=' * w}{C_RESET}")


def section(text: str) -> None:
    print(f"\n{C_BOLD}{text}{C_RESET}")
    print(f"{C_DIM}{'─' * 78}{C_RESET}")


# ─────────────────────────────────────────────────────────────────────────────
# Model discovery
# ─────────────────────────────────────────────────────────────────────────────

def discover_models(base: Path, selected: list[str] | None) -> dict[str, Path]:
    models: dict[str, Path] = {}
    for d in sorted(base.glob("models/kuule-kratt-v*")):
        version = d.name.replace("kuule-kratt-", "")
        tflite = d / f"kuule_kratt_{version}.tflite"
        if not tflite.exists():
            continue
        if selected is None or version in selected:
            models[version] = tflite
    return models


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("models", nargs="*", help="Model versions to compare (e.g. v6 v7 v8). Empty = all.")
    parser.add_argument("--threshold", "-t", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--csv", type=str, help="Save detailed CSV to path")
    parser.add_argument(
        "--allow-leaked",
        action="store_true",
        help="Allow scoring against test sets that overlap with training data. "
             "Default behavior is to skip leaked (model, test_set) combinations "
             "with a warning.",
    )
    args = parser.parse_args()

    base = Path(__file__).resolve().parent.parent
    models = discover_models(base, args.models or None)
    if not models:
        print("No models found.")
        sys.exit(1)

    model_names = list(models.keys())

    header("Kuule Kratt Model Comparison (held-out test sets only)")
    print(f"  Models:    {', '.join(model_names)}")
    print(f"  Threshold: {args.threshold}")
    print(f"  MA window: {MA_WINDOW} frames")

    section("Test Sets")
    for ts in TEST_SETS.values():
        n = ts.file_count()
        held = "all" if len(ts.held_out_for) == 8 else ", ".join(ts.held_out_for)
        marker = f"{C_DIM}(empty){C_RESET}" if n == 0 else f"{n} files"
        print(f"  {ts.name:24s} {ts.kind.value:14s} {marker:20s} held-out: {held}")

    # ─── Score everything ────────────────────────────────────────────────────
    # results[model][test_set_name] = clip metrics or faph dict
    results: dict[str, dict[str, dict]] = {}
    for mn, mp in models.items():
        print(f"\n  Scoring {C_BOLD}{mn}{C_RESET}...")
        model = Model(str(base / mp))
        results[mn] = {}
        for ts in TEST_SETS.values():
            if ts.file_count() == 0:
                continue
            # Disjointness check
            try:
                assert_disjoint_from_training(ts, mn)
            except AssertionError as e:
                if args.allow_leaked:
                    print(f"    {C_YELLOW}LEAKED{C_RESET} {ts.name}: {e}")
                else:
                    print(f"    {C_RED}SKIP{C_RESET}   {ts.name}: not held out for {mn}")
                    continue
            print(f"    {ts.name}...", end=" ", flush=True)
            if ts.kind == TestSetKind.AMBIENT:
                results[mn][ts.name] = streaming_faph(model, ts, args.threshold)
            else:
                scores = score_clip_set(model, ts)
                is_pos = ts.kind == TestSetKind.POSITIVE
                results[mn][ts.name] = clip_metrics(scores, is_pos, args.threshold)
            print("done")

    # ─── Recall table ────────────────────────────────────────────────────────
    section(f"Recall on held-out positive sets (threshold = {args.threshold})")
    hdr = f"  {'Test set':24s} " + "".join(f"  {C_BOLD}{m:>10s}{C_RESET}" for m in model_names)
    print(hdr)
    for ts in TEST_SETS.values():
        if ts.kind != TestSetKind.POSITIVE:
            continue
        row = f"  {ts.name:24s} "
        any_data = False
        for mn in model_names:
            if ts.name in results.get(mn, {}):
                m = results[mn][ts.name]
                row += f"  {color_pct(m.get('recall', 0.0), lower_is_better=False)}"
                any_data = True
            else:
                row += f"  {C_DIM}{'  -  ':>10s}{C_RESET}"
        if any_data:
            print(row)

    # ─── FPR table (clip-level negatives) ────────────────────────────────────
    section(f"Clip-level FPR on held-out negatives (threshold = {args.threshold})")
    print(hdr)
    for ts in TEST_SETS.values():
        if ts.kind != TestSetKind.NEGATIVE_HARD:
            continue
        row = f"  {ts.name:24s} "
        any_data = False
        for mn in model_names:
            if ts.name in results.get(mn, {}):
                m = results[mn][ts.name]
                row += f"  {color_pct(m.get('fpr', 0.0), lower_is_better=True)}"
                any_data = True
            else:
                row += f"  {C_DIM}{'  -  ':>10s}{C_RESET}"
        if any_data:
            print(row)

    # ─── FAPH table (streaming long-form) ────────────────────────────────────
    section(f"Streaming FAPH on long-form ambient (threshold = {args.threshold})")
    hdr_faph = f"  {'Test set':24s} {'Hours':>7s} " + "".join(
        f"  {C_BOLD}{m:>10s}{C_RESET}" for m in model_names
    )
    print(hdr_faph)
    for ts in TEST_SETS.values():
        if ts.kind != TestSetKind.AMBIENT:
            continue
        any_data = False
        hours = 0.0
        cells: list[str] = []
        for mn in model_names:
            r = results.get(mn, {}).get(ts.name)
            if r is None:
                cells.append(f"  {C_DIM}{'  -  ':>10s}{C_RESET}")
                continue
            any_data = True
            hours = r["duration_s"] / 3600.0
            cells.append(f"  {color_faph(r['faph'])}")
        if any_data:
            print(f"  {ts.name:24s} {hours:7.2f}" + "".join(cells))

    # ─── CSV export ──────────────────────────────────────────────────────────
    csv_path = args.csv or str(base / "evaluation" / "model_comparison_holdout.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "model", "test_set", "kind", "threshold", "metric", "value",
            "n", "duration_s", "mean", "p5", "p95",
        ])
        for mn in model_names:
            for ts in TEST_SETS.values():
                r = results.get(mn, {}).get(ts.name)
                if r is None:
                    continue
                if ts.kind == TestSetKind.AMBIENT:
                    w.writerow([
                        mn, ts.name, ts.kind.value, args.threshold, "faph",
                        f"{r['faph']:.4f}", r["n"], f"{r['duration_s']:.1f}",
                        "", "", "",
                    ])
                else:
                    metric = "recall" if ts.kind == TestSetKind.POSITIVE else "fpr"
                    w.writerow([
                        mn, ts.name, ts.kind.value, args.threshold, metric,
                        f"{r.get(metric, 0):.4f}", r["n"], "",
                        f"{r.get('mean', 0):.4f}",
                        f"{r.get('p5', 0):.4f}",
                        f"{r.get('p95', 0):.4f}",
                    ])
    print(f"\n{C_DIM}CSV: {csv_path}{C_RESET}")


if __name__ == "__main__":
    main()
