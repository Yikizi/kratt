#!/usr/bin/env python3
"""Append measurements for a SINGLE consensus combo across ALL test sets.

Loads only the models in the combo, scores clip sets + runs streaming
FAPH on every registered ambient set, then appends rows to the CSV with
model label = "M1 + M2 [+ M3 ...]". Uses same methodology as
benchmark_all_models.py.

Usage:
    python benchmark_add_combo.py --csv evaluation/benchmark_results_supervisor.csv \
        --combo v14 expert-b
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import soundfile as sf

from microwakeword.inference import Model
from microwakeword.test import compute_false_accepts_per_hour

STEP_MS = 10
MA_WINDOW = 5
COOLDOWN = 25
BASE = Path(__file__).resolve().parent.parent

CLIP_SETS: dict[str, dict] = {
    "pos_isa_xtts": {"path": BASE / "data/processed/test_pos_xtts_isa", "kind": "positive", "metric": "recall"},
    "pos_ode": {"path": BASE / "data/raw/ode_kuule_kratt", "kind": "positive", "metric": "recall"},
    "pos_mattias_short": {"path": BASE / "data/raw/mattias-short/positive", "kind": "positive", "metric": "recall"},
    "pos_friend1": {"path": BASE / "data/raw/friend1_20260414", "kind": "positive", "metric": "recall"},
    "hard_neg_mac_holdout": {"path": BASE / "data/processed/hard_neg_test", "kind": "hard_negative", "metric": "fpr"},
    "hard_neg_isa_xtts": {"path": BASE / "data/processed/test_hard_neg_xtts_isa", "kind": "hard_negative", "metric": "fpr"},
    "hard_neg_canary": {"path": BASE / "data/processed/test_neg_false_accepts_v10_canary", "kind": "hard_negative", "metric": "fpr"},
}

FAPH_SETS: dict[str, Path] = {
    "faph_cv_et": BASE / "data/processed/faph_test_cv_et",
    "faph_librispeech": BASE / "data/processed/benchmarks/librispeech-test-clean",
    "faph_macbook_bg": BASE / "data/raw/macbook_negatives",
    "faph_dipco": BASE / "data/processed/benchmarks/dipco",
}


def load_16k(path: Path) -> np.ndarray:
    audio, sr = sf.read(str(path), always_2d=False)
    if audio.ndim > 1:
        audio = audio[:, 0]
    audio = audio.astype(np.float32)
    if sr != 16000:
        import librosa
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
    return (np.clip(audio, -1.0, 1.0) * 32767.0).astype(np.int16)


def ma(v: np.ndarray, w: int = MA_WINDOW) -> np.ndarray:
    if w <= 1 or v.size < w:
        return v
    return np.convolve(v, np.ones(w, dtype=np.float32) / w, mode="valid")


def reset(m: Model) -> None:
    try:
        m.reset_states()
    except Exception:
        pass


def find_model(name: str) -> Path:
    p = BASE / "models" / f"kuule-kratt-{name}" / f"kuule_kratt_{name}.tflite"
    if not p.exists():
        raise SystemExit(f"Model not found: {p}")
    return p


def build_track(files: list[Path], silence_ms: int = 300) -> np.ndarray:
    silence = np.zeros((silence_ms * 16000) // 1000, dtype=np.int16)
    parts: list[np.ndarray] = []
    for i, f in enumerate(files):
        if i > 0:
            parts.append(silence)
        parts.append(load_16k(f))
    return np.concatenate(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--combo", nargs="+", required=True,
                    help="Model names forming the AND consensus combo")
    ap.add_argument("--thresholds", type=float, nargs="+",
                    default=[0.97, 0.99, 0.995, 0.996, 0.999])
    args = ap.parse_args()

    combo = tuple(args.combo)
    label = " + ".join(combo)
    print(f"Combo: {label}")

    # Load models
    models: dict[str, Model] = {}
    for name in combo:
        models[name] = Model(str(find_model(name)))
    print(f"Loaded {len(models)} models")

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    new_rows: list[dict] = []

    def add_row(test_set: str, kind: str, metric: str, threshold: float,
                value: float, n: int, duration_h: float | None) -> None:
        new_rows.append({
            "timestamp": timestamp,
            "model": label,
            "test_set": test_set,
            "kind": kind,
            "threshold": threshold,
            "metric": metric,
            "value": f"{value:.4f}",
            "n": n,
            "duration_h": f"{duration_h:.2f}" if duration_h is not None else "",
            "combo": label,
        })

    # Clip-level scoring (consensus = AND on smoothed peaks)
    print("\nClip-level scoring...")
    for sn, info in CLIP_SETS.items():
        clips = sorted(info["path"].rglob("*.wav")) if info["path"].exists() else []
        if not clips:
            print(f"  SKIP {sn}: no files")
            continue
        print(f"  {sn}: {len(clips)} clips")
        peaks: dict[tuple[str, int], float] = {}
        for mn in combo:
            for i, clip in enumerate(clips):
                pcm = load_16k(clip)
                raw = np.array(models[mn].predict_clip(pcm, step_ms=STEP_MS), dtype=np.float32)
                smoothed = ma(raw)
                peaks[(mn, i)] = float(smoothed.max()) if smoothed.size else float(raw.max())
                reset(models[mn])
        for t in args.thresholds:
            hits = sum(
                1 for i in range(len(clips))
                if all(peaks[(mn, i)] >= t for mn in combo)
            )
            val = hits / len(clips)
            add_row(sn, info["kind"], info["metric"], t, val, len(clips), None)

    # FAPH: stream each model across each long track, then AND on smoothed probs
    print("\nStreaming FAPH tracks...")
    cutoffs = np.array(args.thresholds, dtype=np.float32)
    for sn, path in FAPH_SETS.items():
        files = sorted(path.rglob("*.wav")) if path.exists() else []
        if not files:
            print(f"  SKIP {sn}: no files")
            continue
        track = build_track(files)
        hours = track.size / 16000.0 / 3600.0
        print(f"  {sn}: {len(files)} files, {hours:.2f}h")

        per_model: list[np.ndarray] = []
        for mn in combo:
            raw = np.array(models[mn].predict_clip(track, step_ms=STEP_MS), dtype=np.float32)
            per_model.append(ma(raw))
            reset(models[mn])
        min_len = min(a.size for a in per_model)
        consensus = np.minimum.reduce([a[:min_len] for a in per_model])
        faph_vals = compute_false_accepts_per_hour(
            [consensus], cutoffs=cutoffs,
            ignore_slices_after_accept=COOLDOWN, stride=1,
            step_s=STEP_MS / 1000.0,
        )
        for i, t in enumerate(args.thresholds):
            add_row(sn, "ambient", "faph", t, float(faph_vals[i]), len(files), hours)

    # Merge into CSV
    csv_path = Path(args.csv)
    with open(csv_path) as f:
        existing = list(csv.DictReader(f))
        fields = list(existing[0].keys()) if existing else [
            "timestamp", "model", "test_set", "kind", "threshold",
            "metric", "value", "n", "duration_h", "combo",
        ]
    # Idempotent: replace any previous rows for the same label
    existing = [r for r in existing if r["model"] != label]
    merged = existing + new_rows
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(merged)
    print(f"\nAppended {len(new_rows)} rows for '{label}' to {csv_path}")
    print(f"Total rows now: {len(merged)}")


if __name__ == "__main__":
    main()
