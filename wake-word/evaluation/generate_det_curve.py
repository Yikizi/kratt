#!/usr/bin/env python3
"""Generate DET curves (FRR vs FA/h) for wake word model comparison.

Sweeps detection threshold and plots FRR (from positive test set) against
FA/h (from negative FAPH test set) for each model. This is the standard
KWS evaluation visualization (Lopez-Espejo et al. 2021, Chen et al. 2014).

Also extracts specific operating points:
  - FRR @ 0.5 FA/h  (microWakeWord/openWakeWord convention)
  - FRR @ 1.0 FA/h  (Google convention)

Usage:
    python generate_det_curve.py v6 v6-residual v10 v14
    python generate_det_curve.py --all
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from microwakeword.inference import Model
from microwakeword.test import compute_false_accepts_per_hour


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
FAPH_TEST_DIR = PROJECT_ROOT / "data" / "processed" / "faph_test_cv_et"
HARD_NEG_DIR = PROJECT_ROOT / "data" / "processed" / "test_hard_neg_xtts_isa"

# All positive test sets — scored individually AND pooled for DET FRR
POS_TEST_SETS: dict[str, Path] = {
    "isa_xtts": PROJECT_ROOT / "data" / "processed" / "test_pos_xtts_isa",
    "ode_real": PROJECT_ROOT / "data" / "raw" / "ode_kuule_kratt",
    "mattias_short": PROJECT_ROOT / "data" / "raw" / "mattias-short" / "positive",
}
# Legacy single-dir default (backward compat for --pos-dir flag)
POS_TEST_DIR = PROJECT_ROOT / "data" / "processed" / "test_pos_xtts_isa"

STEP_MS = 10
SLIDING_WINDOW = 5
COOLDOWN_SLICES = 200  # 2s production convention
TARGET_FAPHS = [0.5, 1.0, 2.0, 5.0]  # operating points to extract


def load_16k_int16(path: Path) -> np.ndarray:
    audio, sr = sf.read(str(path), always_2d=False)
    if audio.ndim > 1:
        audio = audio[:, 0]
    audio = audio.astype(np.float32)
    if sr != 16000:
        import librosa
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
    return (np.clip(audio, -1.0, 1.0) * 32767.0).astype(np.int16)


def sliding_window_average(probs: np.ndarray, window: int) -> np.ndarray:
    if window <= 1 or probs.size < window:
        return probs
    from numpy.lib.stride_tricks import sliding_window_view
    return sliding_window_view(probs, window).mean(axis=-1)


def score_clips(model: Model, wav_dir: Path, limit: int = 500) -> list[float]:
    """Return max smoothed score per clip."""
    files = sorted(wav_dir.glob("*.wav"))[:limit]
    scores = []
    for f in files:
        pcm = load_16k_int16(f)
        raw = np.array(model.predict_clip(pcm, step_ms=STEP_MS), dtype=np.float32)
        if raw.size < SLIDING_WINDOW:
            scores.append(0.0)
            continue
        ma = sliding_window_average(raw, SLIDING_WINDOW)
        scores.append(float(ma.max()))
    return scores


def compute_faph_at_thresholds(
    model: Model, neg_dir: Path, thresholds: np.ndarray
) -> np.ndarray:
    """Run streaming FAPH on concatenated negative audio at multiple thresholds."""
    files = sorted(neg_dir.glob("*.wav"))
    if not files:
        return np.zeros_like(thresholds)

    # Concatenate all audio into single stream
    silence = np.zeros(int(0.3 * 16000), dtype=np.int16)
    parts = []
    for i, f in enumerate(files):
        pcm = load_16k_int16(f)
        if i > 0:
            parts.append(silence)
        parts.append(pcm)
    concatenated = np.concatenate(parts)

    raw = np.array(
        model.predict_clip(concatenated, step_ms=STEP_MS), dtype=np.float32
    )
    smoothed = sliding_window_average(raw, SLIDING_WINDOW)

    return compute_false_accepts_per_hour(
        [smoothed],
        cutoffs=thresholds,
        ignore_slices_after_accept=COOLDOWN_SLICES,
        stride=1,
        step_s=STEP_MS / 1000.0,
    )


def discover_models(selected: list[str] | None = None) -> dict[str, Path]:
    models = {}
    for d in sorted(MODELS_DIR.glob("kuule-kratt-*")):
        tag = d.name.replace("kuule-kratt-", "")
        tflite = d / f"kuule_kratt_{tag}.tflite"
        if tflite.exists():
            if selected is None or tag in selected:
                models[tag] = tflite
    return models


def find_frr_at_faph(frr_values: np.ndarray, faph_values: np.ndarray, target_faph: float) -> float | None:
    """Interpolate FRR at a specific FA/h operating point."""
    # Sort by FAPH descending (threshold ascending)
    order = np.argsort(faph_values)[::-1]
    faph_sorted = faph_values[order]
    frr_sorted = frr_values[order]

    # Find where FAPH crosses target
    for i in range(len(faph_sorted) - 1):
        if faph_sorted[i] >= target_faph >= faph_sorted[i + 1]:
            # Linear interpolation
            if faph_sorted[i] == faph_sorted[i + 1]:
                return float(frr_sorted[i])
            t = (target_faph - faph_sorted[i + 1]) / (faph_sorted[i] - faph_sorted[i + 1])
            return float(frr_sorted[i + 1] + t * (frr_sorted[i] - frr_sorted[i + 1]))

    return None  # Target FAPH outside range


def main():
    parser = argparse.ArgumentParser(description="Generate DET curves for KWS models")
    parser.add_argument("models", nargs="*", help="Model tags (e.g. v6 v10). Empty = use --all")
    parser.add_argument("--all", action="store_true", help="All available models")
    parser.add_argument("--output", default=str(PROJECT_ROOT / "evaluation" / "det_curves.json"))
    parser.add_argument("--pos-dir", default=str(POS_TEST_DIR))
    parser.add_argument("--neg-dir", default=str(FAPH_TEST_DIR))
    parser.add_argument("--hard-neg-dir", default=str(HARD_NEG_DIR))
    args = parser.parse_args()

    selected = args.models if args.models else None
    if args.all:
        selected = None
    models = discover_models(selected)

    if not models:
        raise SystemExit("No models found")

    pos_dir = Path(args.pos_dir)
    neg_dir = Path(args.neg_dir)
    hard_neg_dir = Path(args.hard_neg_dir)

    # Threshold sweep: 0.01 to 1.0 in 0.01 steps
    thresholds = np.arange(0.01, 1.001, 0.01).astype(np.float32)

    results = {}

    # Resolve positive test sets: use --pos-dir if explicitly given, else all POS_TEST_SETS
    use_multi_pos = (args.pos_dir == str(POS_TEST_DIR))  # default = use all
    pos_sets: dict[str, Path] = {}
    if use_multi_pos:
        for name, path in POS_TEST_SETS.items():
            if path.exists() and list(path.rglob("*.wav")):
                pos_sets[name] = path
        counts = ", ".join(
            f"{n}({len(list(p.rglob('*.wav')))}wav)" for n, p in pos_sets.items()
        )
        print(f"\nPositive sets ({len(pos_sets)}): {counts}")
    else:
        pos_sets = {"custom": Path(args.pos_dir)}

    neg_hours_computed = False

    for tag, tflite_path in models.items():
        print(f"\nScoring {tag}...")
        model = Model(str(tflite_path))

        # 1. Score each positive set individually + compute pooled FRR
        per_set_scores: dict[str, list[float]] = {}
        all_pos_scores: list[float] = []
        for ps_name, ps_path in pos_sets.items():
            scores = score_clips(model, ps_path)
            per_set_scores[ps_name] = scores
            all_pos_scores.extend(scores)
            print(f"  Positive {ps_name}: {len(scores)} clips")

        # Pooled FRR across all positive sets
        pooled_arr = np.array(all_pos_scores)
        frr_at_thr = 1.0 - np.array([float((pooled_arr >= t).mean()) for t in thresholds])

        # Per-set FRR for detailed breakdown
        per_set_frr = {}
        for ps_name, scores in per_set_scores.items():
            arr = np.array(scores)
            per_set_frr[ps_name] = (1.0 - np.array([float((arr >= t).mean()) for t in thresholds])).tolist()

        # 2. FAPH at each threshold (streaming on concatenated neg audio)
        print(f"  FAPH ({neg_dir.name})...", end=" ", flush=True)
        faph_at_thr = compute_faph_at_thresholds(model, neg_dir, thresholds)
        print("done")

        # 3. Hard neg FPR at each threshold (clip-level)
        hn_fpr_at_thr = None
        if hard_neg_dir.exists():
            print(f"  Hard neg FPR ({hard_neg_dir.name})...", end=" ", flush=True)
            hn_scores = score_clips(model, hard_neg_dir)
            hn_arr = np.array(hn_scores)
            hn_fpr_at_thr = np.array([float((hn_arr >= t).mean()) for t in thresholds])
            print(f"{len(hn_scores)} clips")

        # 4. Extract operating points (using pooled FRR)
        operating_points = {}
        for target in TARGET_FAPHS:
            frr = find_frr_at_faph(frr_at_thr, faph_at_thr, target)
            if frr is not None:
                operating_points[f"FRR@{target}FA/h"] = round(frr * 100, 2)

        # Per-set operating points
        per_set_operating_points = {}
        for ps_name in per_set_frr:
            ps_frr = np.array(per_set_frr[ps_name])
            ps_ops = {}
            for target in TARGET_FAPHS:
                frr = find_frr_at_faph(ps_frr, faph_at_thr, target)
                if frr is not None:
                    ps_ops[f"FRR@{target}FA/h"] = round(frr * 100, 2)
            per_set_operating_points[ps_name] = ps_ops

        n_neg_hours = None
        if not neg_hours_computed:
            n_neg_hours = round(sum(
                len(load_16k_int16(f)) for f in sorted(neg_dir.glob("*.wav"))
            ) / 16000 / 3600, 2)
            neg_hours_computed = True

        results[tag] = {
            "thresholds": thresholds.tolist(),
            "frr_pooled": frr_at_thr.tolist(),
            "frr_per_set": per_set_frr,
            "faph": faph_at_thr.tolist(),
            "hard_neg_fpr": hn_fpr_at_thr.tolist() if hn_fpr_at_thr is not None else None,
            "operating_points_pooled": operating_points,
            "operating_points_per_set": per_set_operating_points,
            "n_pos_clips_pooled": len(all_pos_scores),
            "n_pos_clips_per_set": {n: len(s) for n, s in per_set_scores.items()},
            "n_neg_hours": n_neg_hours,
        }

        # Print operating points
        print(f"  Operating points (pooled {len(all_pos_scores)} clips):")
        for k, v in operating_points.items():
            print(f"    {k}: {v}%")
        for ps_name, ps_ops in per_set_operating_points.items():
            frr1 = ps_ops.get("FRR@1.0FA/h")
            if frr1 is not None:
                print(f"    [{ps_name}] FRR@1FA/h: {frr1}%")

    # Save JSON
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2) + "\n")
    print(f"\nSaved: {output_path}")

    # Print summary table — pooled FRR
    ps_names = list(pos_sets.keys())
    print(f"\n{'='*100}")
    print(f"{'Model':<20} {'POOLED':>10}", end="")
    for ps in ps_names:
        print(f" {ps[:8]:>10}", end="")
    print("   (all FRR@1FA/h)")
    print("-" * 100)
    for tag in models:
        r = results[tag]
        pooled_val = r["operating_points_pooled"].get("FRR@1.0FA/h")
        print(f"{tag:<20} {pooled_val:>9.2f}%" if pooled_val is not None else f"{tag:<20} {'N/A':>10}", end="")
        for ps in ps_names:
            ps_val = r["operating_points_per_set"].get(ps, {}).get("FRR@1.0FA/h")
            if ps_val is not None:
                print(f" {ps_val:>9.2f}%", end="")
            else:
                print(f" {'N/A':>10}", end="")
        print()
    print("=" * 100)


if __name__ == "__main__":
    main()
