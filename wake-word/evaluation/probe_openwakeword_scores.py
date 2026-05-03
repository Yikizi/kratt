#!/usr/bin/env python3
"""Quick score probe for custom openWakeWord ONNX models.

Runs a small, explicit set of positive/negative/FAPH clips and prints score
summaries plus top-scoring examples. Intended before full benchmark sweeps.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np

from benchmark_openwakeword import audio_files, clip_peak, model_key, stream_peaks
from openwakeword import Model as OpenWakeWordModel

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"

DEFAULT_SETS = {
    "pos_isa_xtts": DATA / "processed/test_pos_xtts_isa",
    "pos_mattias_short": DATA / "raw/mattias-short/positive",
    "pos_friend1": DATA / "raw/friend1_20260414",
    "neg_hard_mac": DATA / "processed/hard_neg_test",
    "neg_isa_xtts": DATA / "processed/test_hard_neg_xtts_isa",
    "neg_canary": DATA / "processed/test_neg_false_accepts_v10_canary",
    "neg_prefix_only": DATA / "processed/prefix_regression_test/prefix_only_mattias_short_lt0p50",
    "neg_confusables": DATA / "processed/prefix_regression_test/kuule_kule_confusables_neurokone_hard_neg_v2",
}

FAPH_SETS = {
    "faph_cv_et_first100": DATA / "processed/faph_test_cv_et",
    "faph_librispeech_first100": DATA / "processed/benchmarks/librispeech-test-clean",
}


def quantiles(xs: np.ndarray) -> str:
    if xs.size == 0:
        return "EMPTY"
    qs = np.quantile(xs, [0, 0.1, 0.5, 0.9, 0.99, 1.0])
    return "min={:.6f} p10={:.6f} p50={:.6f} p90={:.6f} p99={:.6f} max={:.6f}".format(*qs)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, type=Path)
    ap.add_argument("--limit", type=int, default=40, help="clips per set")
    ap.add_argument("--faph-limit", type=int, default=100, help="files per faph mini stream")
    ap.add_argument("--top", type=int, default=5)
    args = ap.parse_args()

    print(f"Loading: {args.model}", flush=True)
    model = OpenWakeWordModel(wakeword_models=[str(args.model)])
    key = model_key(model, args.model)
    print(f"Prediction key: {key}; input_frames={model.model_inputs[key]}", flush=True)

    all_scores: dict[str, np.ndarray] = {}
    for name, path in DEFAULT_SETS.items():
        files = audio_files(path)[:args.limit]
        print(f"\n{name}: {len(files)} clips from {path}", flush=True)
        scored: list[tuple[float, Path]] = []
        for i, f in enumerate(files, start=1):
            s = clip_peak(model, key, f)
            scored.append((s, f))
            if i == 1 or i % 10 == 0 or i == len(files):
                print(f"  {i}/{len(files)}", flush=True)
        arr = np.array([s for s, _ in scored], dtype=np.float32)
        all_scores[name] = arr
        print("  " + quantiles(arr), flush=True)
        for s, f in sorted(scored, reverse=True)[:args.top]:
            print(f"  TOP {s:.6f}  {f.relative_to(BASE)}", flush=True)

    print("\nMini streaming FAPH score distributions:", flush=True)
    for name, path in FAPH_SETS.items():
        files = audio_files(path)[:args.faph_limit]
        print(f"\n{name}: {len(files)} files", flush=True)
        scores, hours = stream_peaks(model, key, files, name)
        print(f"  hours={hours:.4f} frames={len(scores)}", flush=True)
        print("  " + quantiles(scores), flush=True)
        for thr in [0.005, 0.008, 0.010, 0.012, 0.014, 0.016, 0.017, 0.0175, 0.018, 0.0185, 0.019, 0.020, 0.03, 0.05]:
            hits = int((scores >= thr).sum())
            print(f"  frames>= {thr:.4f}: {hits}/{len(scores)} ({hits/max(len(scores),1):.2%})", flush=True)

    print("\nSeparation hints:", flush=True)
    positives = np.concatenate([v for k, v in all_scores.items() if k.startswith("pos_") and v.size]) if any(k.startswith("pos_") and v.size for k, v in all_scores.items()) else np.array([])
    negatives = np.concatenate([v for k, v in all_scores.items() if k.startswith("neg_") and v.size]) if any(k.startswith("neg_") and v.size for k, v in all_scores.items()) else np.array([])
    print(f"  positives: {quantiles(positives)}", flush=True)
    print(f"  negatives: {quantiles(negatives)}", flush=True)
    if positives.size and negatives.size:
        candidates = sorted(set(np.quantile(np.concatenate([positives, negatives]), np.linspace(0, 1, 21))))
        print("  candidate thresholds (clip recall / clip neg-FPR):", flush=True)
        for thr in candidates:
            recall = float((positives >= thr).mean())
            fpr = float((negatives >= thr).mean())
            print(f"    thr={thr:.6f}: recall={recall:.3f} neg_fpr={fpr:.3f}", flush=True)


if __name__ == "__main__":
    main()
