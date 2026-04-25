#!/usr/bin/env python3
"""Benchmark ALL models on ALL test sets, output to CSV.

Measures recall, hard-negative FPR, and streaming FAPH for every model
in models/kuule-kratt-*/ across all registered test sets. Also evaluates
consensus combos.

Usage:
    python benchmark_all_models.py [--output benchmark_results.csv]
    python benchmark_all_models.py --models ex3a expert-a  # subset
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


def discover_models(selected: list[str] | None = None) -> dict[str, Path]:
    models: dict[str, Path] = {}
    for d in sorted(BASE.glob("models/kuule-kratt-*")):
        version = d.name.replace("kuule-kratt-", "")
        tflite = d / f"kuule_kratt_{version}.tflite"
        if not tflite.exists():
            continue
        if selected is None or version in selected:
            models[version] = tflite
    return models


def build_track(files: list[Path], silence_ms: int = 300) -> np.ndarray:
    silence = np.zeros((silence_ms * 16000) // 1000, dtype=np.int16)
    parts: list[np.ndarray] = []
    for i, f in enumerate(files):
        if i > 0:
            parts.append(silence)
        parts.append(load_16k(f))
    return np.concatenate(parts)


# ── Test set definitions ──

CLIP_SETS: dict[str, dict] = {
    "pos_isa_xtts": {
        "path": BASE / "data/processed/test_pos_xtts_isa",
        "kind": "positive",
        "metric": "recall",
    },
    "pos_ode": {
        "path": BASE / "data/raw/ode_kuule_kratt",
        "kind": "positive",
        "metric": "recall",
    },
    "pos_mattias_short": {
        "path": BASE / "data/raw/mattias-short/positive",
        "kind": "positive",
        "metric": "recall",
    },
    "hard_neg_mac_holdout": {
        "path": BASE / "data/processed/hard_neg_test",
        "kind": "hard_negative",
        "metric": "fpr",
    },
    "hard_neg_isa_xtts": {
        "path": BASE / "data/processed/test_hard_neg_xtts_isa",
        "kind": "hard_negative",
        "metric": "fpr",
    },
    "hard_neg_canary": {
        "path": BASE / "data/processed/test_neg_false_accepts_v10_canary",
        "kind": "hard_negative",
        "metric": "fpr",
    },
}

FAPH_SETS: dict[str, Path] = {
    "faph_cv_et": BASE / "data/processed/faph_test_cv_et",
    "faph_librispeech": BASE / "data/processed/benchmarks/librispeech-test-clean",
    "faph_macbook_bg": BASE / "data/raw/macbook_negatives",
    "faph_dipco": BASE / "data/processed/benchmarks/dipco",
}

CONSENSUS_COMBOS = [
    ("ex3a", "expert-a"),
    ("ex3a", "expert-b2"),
    ("ex3a", "expert-a", "expert-b2"),
    ("ex3a", "expert-a", "expert-b"),
    ("ex3a", "expert-b", "expert-b2"),
    ("v6-residual", "expert-a"),
    ("ex3b", "expert-b2"),
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="*", help="Subset of models to benchmark")
    parser.add_argument("--output", "-o", default=None,
                        help="Output CSV path (default: auto-timestamped)")
    parser.add_argument("--thresholds", type=float, nargs="+",
                        default=[0.97, 0.99, 0.995, 0.996, 0.999])
    args = parser.parse_args()

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_tag = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")

    if args.output:
        csv_path = args.output
    else:
        csv_path = str(BASE / "evaluation" / f"benchmark_results_{date_tag}.csv")

    # Discover models
    model_map = discover_models(args.models)
    if not model_map:
        print("No models found.")
        return

    model_names = list(model_map.keys())
    print(f"Models ({len(model_names)}): {', '.join(model_names)}")

    # Load models
    models: dict[str, Model] = {}
    for mn, mp in model_map.items():
        models[mn] = Model(str(mp))
    print(f"Loaded {len(models)} models")

    # ── Clip-level scoring ──
    print("\nClip-level scoring...")
    clip_peaks: dict[tuple[str, str, int], float] = {}
    for sn, info in CLIP_SETS.items():
        clips = sorted(info["path"].rglob("*.wav")) if info["path"].exists() else []
        if not clips:
            print(f"  SKIP {sn}: no files")
            continue
        print(f"  {sn}: {len(clips)} clips")
        for mn in model_names:
            for i, clip in enumerate(clips):
                pcm = load_16k(clip)
                raw = np.array(
                    models[mn].predict_clip(pcm, step_ms=STEP_MS), dtype=np.float32
                )
                smoothed = ma(raw)
                clip_peaks[(mn, sn, i)] = (
                    float(smoothed.max()) if smoothed.size else float(raw.max())
                )
                reset(models[mn])

    # ── FAPH tracks ──
    print("\nBuilding FAPH tracks...")
    faph_files: dict[str, list[Path]] = {}
    faph_tracks: dict[str, np.ndarray] = {}
    faph_hours: dict[str, float] = {}
    for sn, path in FAPH_SETS.items():
        files = sorted(path.rglob("*.wav")) if path.exists() else []
        if not files:
            print(f"  SKIP {sn}: no files")
            continue
        faph_files[sn] = files
        faph_tracks[sn] = build_track(files)
        faph_hours[sn] = faph_tracks[sn].size / 16000.0 / 3600.0
        print(f"  {sn}: {len(files)} files, {faph_hours[sn]:.2f}h")

    print("\nStreaming inference...")
    stream_probs: dict[tuple[str, str], np.ndarray] = {}
    for mn in model_names:
        for sn, track in faph_tracks.items():
            raw = np.array(
                models[mn].predict_clip(track, step_ms=STEP_MS), dtype=np.float32
            )
            stream_probs[(mn, sn)] = ma(raw)
            reset(models[mn])
        print(f"  {mn} done")

    # ── Build rows ──
    rows: list[dict] = []
    thresholds = args.thresholds
    cutoffs = np.array(thresholds, dtype=np.float32)

    def add_single(mn: str) -> None:
        # Recall / FPR
        for sn, info in CLIP_SETS.items():
            clips = sorted(info["path"].rglob("*.wav")) if info["path"].exists() else []
            if not clips:
                continue
            for t in thresholds:
                hits = sum(
                    1 for i in range(len(clips)) if clip_peaks.get((mn, sn, i), 0) >= t
                )
                val = hits / len(clips)
                rows.append({
                    "timestamp": timestamp, "model": mn, "test_set": sn,
                    "kind": info["kind"], "threshold": t, "metric": info["metric"],
                    "value": f"{val:.4f}", "n": len(clips), "duration_h": "",
                    "combo": "",
                })
        # FAPH
        for sn in faph_tracks:
            faph_vals = compute_false_accepts_per_hour(
                [stream_probs[(mn, sn)]], cutoffs=cutoffs,
                ignore_slices_after_accept=COOLDOWN, stride=1,
                step_s=STEP_MS / 1000.0,
            )
            for i, t in enumerate(thresholds):
                rows.append({
                    "timestamp": timestamp, "model": mn, "test_set": sn,
                    "kind": "ambient", "threshold": t, "metric": "faph",
                    "value": f"{faph_vals[i]:.4f}", "n": len(faph_files[sn]),
                    "duration_h": f"{faph_hours[sn]:.2f}", "combo": "",
                })

    def add_combo(combo: tuple[str, ...]) -> None:
        label = " + ".join(combo)
        # Check all models exist
        if not all(mn in models for mn in combo):
            return
        # Recall / FPR
        for sn, info in CLIP_SETS.items():
            clips = sorted(info["path"].rglob("*.wav")) if info["path"].exists() else []
            if not clips:
                continue
            for t in thresholds:
                hits = sum(
                    1 for i in range(len(clips))
                    if all(clip_peaks.get((mn, sn, i), 0) >= t for mn in combo)
                )
                val = hits / len(clips)
                rows.append({
                    "timestamp": timestamp, "model": label, "test_set": sn,
                    "kind": info["kind"], "threshold": t, "metric": info["metric"],
                    "value": f"{val:.4f}", "n": len(clips), "duration_h": "",
                    "combo": label,
                })
        # FAPH
        for sn in faph_tracks:
            arrs = [stream_probs[(mn, sn)] for mn in combo]
            min_len = min(a.size for a in arrs)
            consensus = np.minimum.reduce([a[:min_len] for a in arrs])
            faph_vals = compute_false_accepts_per_hour(
                [consensus], cutoffs=cutoffs,
                ignore_slices_after_accept=COOLDOWN, stride=1,
                step_s=STEP_MS / 1000.0,
            )
            for i, t in enumerate(thresholds):
                rows.append({
                    "timestamp": timestamp, "model": label, "test_set": sn,
                    "kind": "ambient", "threshold": t, "metric": "faph",
                    "value": f"{faph_vals[i]:.4f}", "n": len(faph_files[sn]),
                    "duration_h": f"{faph_hours[sn]:.2f}", "combo": label,
                })

    print("\nComputing metrics...")
    for mn in model_names:
        add_single(mn)
    for combo in CONSENSUS_COMBOS:
        add_combo(combo)

    # ── Write CSV ──
    fields = [
        "timestamp", "model", "test_set", "kind", "threshold",
        "metric", "value", "n", "duration_h", "combo",
    ]
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {csv_path}")
    print(f"  Models: {len(model_names)} singles + {len(CONSENSUS_COMBOS)} combos")
    n_sets = len(set(r["test_set"] for r in rows))
    print(f"  Test sets: {n_sets}")
    print(f"  Thresholds: {thresholds}")


if __name__ == "__main__":
    main()
