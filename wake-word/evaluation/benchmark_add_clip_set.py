#!/usr/bin/env python3
"""Incrementally add one clip-level test set to an existing benchmark CSV.

Scores all models + consensus combos on a new clip directory (positive or
hard-negative) and appends new rows with the same schema. Much faster than
the full benchmark since it skips FAPH streaming.

Usage:
    python benchmark_add_clip_set.py \
        --csv evaluation/benchmark_results_supervisor.csv \
        --name pos_friend1 \
        --path data/raw/friend1_20260414 \
        --kind positive \
        --metric recall
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import soundfile as sf

from microwakeword.inference import Model

STEP_MS = 10
MA_WINDOW = 5
BASE = Path(__file__).resolve().parent.parent

CONSENSUS_COMBOS = [
    ("ex3a", "expert-a"),
    ("ex3a", "expert-b2"),
    ("ex3a", "expert-a", "expert-b2"),
    ("ex3a", "expert-a", "expert-b"),
    ("ex3a", "expert-b", "expert-b2"),
    ("v6-residual", "expert-a"),
    ("ex3b", "expert-b2"),
    ("v14", "expert-b"),
]


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


def discover_models() -> dict[str, Path]:
    out: dict[str, Path] = {}
    for d in sorted(BASE.glob("models/kuule-kratt-*")):
        version = d.name.replace("kuule-kratt-", "")
        tflite = d / f"kuule_kratt_{version}.tflite"
        if tflite.exists():
            out[version] = tflite
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="existing benchmark CSV")
    ap.add_argument("--name", required=True, help="test set name (e.g. pos_friend1)")
    ap.add_argument("--path", required=True, help="clip directory")
    ap.add_argument("--kind", choices=["positive", "hard_negative"], required=True)
    ap.add_argument("--metric", choices=["recall", "fpr"], required=True)
    ap.add_argument(
        "--thresholds", type=float, nargs="+",
        default=[0.97, 0.99, 0.995, 0.996, 0.999],
    )
    args = ap.parse_args()

    clip_dir = Path(args.path)
    if not clip_dir.is_absolute():
        clip_dir = BASE / clip_dir
    clips = sorted(clip_dir.rglob("*.wav"))
    if not clips:
        raise SystemExit(f"No clips in {clip_dir}")
    print(f"Test set '{args.name}': {len(clips)} clips from {clip_dir}")

    model_map = discover_models()
    print(f"Models: {len(model_map)}")

    # Load models
    models: dict[str, Model] = {}
    for name, path in model_map.items():
        models[name] = Model(str(path))

    # Score every (model, clip) → peak of smoothed probs
    print("Scoring clips...")
    peaks: dict[tuple[str, int], float] = {}
    pcm_cache = [load_16k(c) for c in clips]
    for mn, m in models.items():
        for i, pcm in enumerate(pcm_cache):
            raw = np.array(m.predict_clip(pcm, step_ms=STEP_MS), dtype=np.float32)
            smoothed = ma(raw)
            peaks[(mn, i)] = (
                float(smoothed.max()) if smoothed.size else float(raw.max())
            )
            reset(m)
        print(f"  {mn} done")

    # Build new rows
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    new_rows: list[dict] = []

    def add_row(model_label: str, combo_label: str, threshold: float, value: float) -> None:
        new_rows.append({
            "timestamp": timestamp,
            "model": model_label,
            "test_set": args.name,
            "kind": args.kind,
            "threshold": threshold,
            "metric": args.metric,
            "value": f"{value:.4f}",
            "n": len(clips),
            "duration_h": "",
            "combo": combo_label,
        })

    # Singles
    for mn in models:
        for t in args.thresholds:
            hits = sum(1 for i in range(len(clips)) if peaks[(mn, i)] >= t)
            val = hits / len(clips)
            add_row(mn, "", t, val)

    # Combos (AND consensus on smoothed peaks)
    for combo in CONSENSUS_COMBOS:
        if not all(mn in models for mn in combo):
            continue
        label = " + ".join(combo)
        for t in args.thresholds:
            hits = sum(
                1 for i in range(len(clips))
                if all(peaks[(mn, i)] >= t for mn in combo)
            )
            val = hits / len(clips)
            add_row(label, label, t, val)

    # Read existing CSV (preserve header + prior rows)
    csv_path = Path(args.csv)
    with open(csv_path) as f:
        existing = list(csv.DictReader(f))
        fields = list(existing[0].keys()) if existing else [
            "timestamp", "model", "test_set", "kind", "threshold",
            "metric", "value", "n", "duration_h", "combo",
        ]

    # Replace any previous rows for the same test_set (idempotent re-run)
    existing = [r for r in existing if r["test_set"] != args.name]

    merged = existing + new_rows
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(merged)

    print(f"\nAppended {len(new_rows)} rows for {args.name} to {csv_path}")
    print(f"Total rows now: {len(merged)}")


if __name__ == "__main__":
    main()
