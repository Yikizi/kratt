#!/usr/bin/env python3
"""Compare wake word models on identical test sets.

Usage:
    python compare_models.py              # all models
    python compare_models.py v6 v7        # specific models
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

from microwakeword.inference import Model

STEP_MS = 10
MA_WINDOW = 5
LIMIT = 250

# ANSI colors
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_RED = "\033[31m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_CYAN = "\033[36m"
C_BG_RED = "\033[41m"
C_BG_GREEN = "\033[42m"


def load_audio_16k(path: Path) -> np.ndarray:
    audio, sr = sf.read(str(path), always_2d=False)
    if audio.ndim > 1:
        audio = audio[:, 0]
    audio = audio.astype(np.float32)
    if sr != 16000:
        import torchaudio
        import torch
        tensor = torch.from_numpy(audio).float().unsqueeze(0)
        tensor = torchaudio.functional.resample(tensor, sr, 16000)
        audio = tensor.squeeze(0).numpy()
    return (np.clip(audio, -1.0, 1.0) * 32767.0).astype(np.int16)


def moving_average(values: np.ndarray, window: int) -> np.ndarray:
    if window <= 1 or values.size == 0:
        return values
    kernel = np.ones(window, dtype=np.float32) / float(window)
    return np.convolve(values, kernel, mode="valid")


def score_files(model: Model, wav_dir: Path, limit: int = LIMIT) -> list[float]:
    files = sorted(wav_dir.glob("*.wav"))[:limit]
    scores = []
    for f in files:
        pcm = load_audio_16k(f)
        raw = np.array(model.predict_clip(pcm, step_ms=STEP_MS), dtype=np.float32)
        if raw.size == 0:
            scores.append(0.0)
            continue
        ma = moving_average(raw, MA_WINDOW)
        scores.append(float(ma.max()) if ma.size else float(raw.max()))
    return scores


def compute_metrics(scores: list[float], is_positive: bool, threshold: float) -> dict:
    if not scores:
        return {}
    arr = np.array(scores)
    detected = arr >= threshold

    metrics = {
        "mean_score": float(arr.mean()),
        "median_score": float(np.median(arr)),
        "std_score": float(arr.std()),
        "min_score": float(arr.min()),
        "max_score": float(arr.max()),
        "p5_score": float(np.percentile(arr, 5)),
        "p95_score": float(np.percentile(arr, 95)),
        "n_clips": len(scores),
    }

    if is_positive:
        metrics["recall"] = float(detected.sum()) / len(scores)
        metrics["miss_rate"] = 1.0 - metrics["recall"]
    else:
        metrics["fpr"] = float(detected.sum()) / len(scores)
        metrics["tnr"] = 1.0 - metrics["fpr"]

    return metrics


def color_val(val: float, is_positive: bool, metric: str) -> str:
    """Color a metric value: green=good, red=bad."""
    s = f"{val:7.1%}"
    if metric == "recall":
        if val >= 0.99:
            return f"{C_GREEN}{s}{C_RESET}"
        elif val >= 0.95:
            return f"{C_YELLOW}{s}{C_RESET}"
        else:
            return f"{C_RED}{s}{C_RESET}"
    elif metric == "fpr":
        if val <= 0.01:
            return f"{C_GREEN}{s}{C_RESET}"
        elif val <= 0.05:
            return f"{C_YELLOW}{s}{C_RESET}"
        elif val >= 0.5:
            return f"{C_BG_RED}{s}{C_RESET}"
        else:
            return f"{C_RED}{s}{C_RESET}"
    return s


def color_score(val: float) -> str:
    s = f"{val:6.3f}"
    if val >= 0.9:
        return f"{C_GREEN}{s}{C_RESET}"
    elif val >= 0.5:
        return f"{C_YELLOW}{s}{C_RESET}"
    else:
        return f"{C_DIM}{s}{C_RESET}"


def delta_str(curr: float, prev: float, lower_is_better: bool = False) -> str:
    diff = curr - prev
    if abs(diff) < 0.001:
        return f"{C_DIM}   ={C_RESET}"
    if lower_is_better:
        color = C_GREEN if diff < 0 else C_RED
    else:
        color = C_GREEN if diff > 0 else C_RED
    sign = "+" if diff > 0 else ""
    return f"{color}{sign}{diff:+.1%}{C_RESET}"


def discover_models(base: Path, selected: list[str] | None = None) -> dict[str, Path]:
    models = {}
    for d in sorted(base.glob("models/kuule-kratt-v*")):
        version = d.name.replace("kuule-kratt-", "")
        tflite = d / f"kuule_kratt_{version}.tflite"
        if tflite.exists():
            if selected is None or version in selected:
                models[version] = tflite
    return models


def discover_test_sets(base: Path) -> dict[str, Path]:
    sets = {}
    pos_mic1 = base / "data" / "processed" / "positive" / "mattias_mic1"
    pos_mic2 = base / "data" / "processed" / "positive" / "mattias_mic2"
    neg_korvo2 = base / "data" / "processed" / "negative_korvo2"

    cv_neg_dir = base / "data" / "processed" / "negative_samples"
    if not cv_neg_dir.exists():
        for d in sorted((base / "data" / "processed" / "experiments").glob("*")):
            if d.is_dir() and (d / "negative_samples").exists():
                cv_neg_dir = d / "negative_samples"
                break

    if pos_mic1.exists():
        sets["pos_mic1"] = pos_mic1
    if pos_mic2.exists():
        sets["pos_mic2"] = pos_mic2
    if cv_neg_dir.exists():
        sets["neg_cv"] = cv_neg_dir
    if neg_korvo2.exists():
        sets["neg_korvo2"] = neg_korvo2
    return sets


def print_header(text: str):
    w = 70
    print(f"\n{C_CYAN}{'=' * w}{C_RESET}")
    print(f"{C_BOLD}{C_CYAN}  {text}{C_RESET}")
    print(f"{C_CYAN}{'=' * w}{C_RESET}")


def print_section(text: str):
    print(f"\n{C_BOLD}{text}{C_RESET}")
    print(f"{C_DIM}{'─' * 70}{C_RESET}")


def main():
    parser = argparse.ArgumentParser(description="Compare wake word models")
    parser.add_argument("models", nargs="*", help="Model versions to compare (e.g. v6 v7). Empty = all.")
    parser.add_argument("--threshold", "-t", type=float, default=0.9, help="Primary threshold (default: 0.9)")
    parser.add_argument("--csv", type=str, help="Save detailed CSV to path")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent.parent
    selected = args.models if args.models else None
    models = discover_models(base, selected)
    test_sets = discover_test_sets(base)

    if not models:
        print("No models found.")
        sys.exit(1)

    model_names = list(models.keys())

    # Header
    print_header("Kuule Kratt Model Comparison")
    print(f"  Models:    {', '.join(model_names)}")
    print(f"  Threshold: {args.threshold}")
    print(f"  Limit:     {LIMIT} clips per set")

    # Test sets
    print_section("Test Sets")
    for name, path in test_sets.items():
        count = len(list(path.glob("*.wav")))
        label = "positive" if name.startswith("pos") else "negative"
        print(f"  {name:15s}  {count:4d} clips  ({label})")

    # Score all models
    all_scores: dict[str, dict[str, list[float]]] = {}
    for mn, mp in models.items():
        print(f"\n  Scoring {C_BOLD}{mn}{C_RESET}...", end=" ", flush=True)
        model = Model(str(base / mp))
        all_scores[mn] = {}
        for sn, sp in test_sets.items():
            all_scores[mn][sn] = score_files(model, sp)
        print("done")

    # === Main comparison table ===
    threshold = args.threshold
    print_section(f"Recall & FPR (threshold = {threshold})")

    # Header row
    hdr = f"  {'Test Set':15s}"
    for mn in model_names:
        hdr += f"  {C_BOLD}{mn:>8s}{C_RESET}"
    if len(model_names) >= 2:
        hdr += f"  {C_DIM}{'delta':>8s}{C_RESET}"
    print(hdr)

    for sn in test_sets:
        is_pos = sn.startswith("pos_")
        metric = "recall" if is_pos else "fpr"
        row = f"  {sn:15s}"
        vals = []
        for mn in model_names:
            m = compute_metrics(all_scores[mn][sn], is_pos, threshold)
            v = m.get(metric, 0.0)
            vals.append(v)
            row += f"  {color_val(v, is_pos, metric)}"
        if len(vals) >= 2:
            row += f"  {delta_str(vals[-1], vals[-2], lower_is_better=(metric == 'fpr'))}"
        label = f"{C_DIM}({metric}){C_RESET}"
        print(f"{row}  {label}")

    # === Score distribution ===
    print_section("Score Distribution (max moving-avg per clip)")

    hdr = f"  {'':15s}"
    for mn in model_names:
        hdr += f"  {C_BOLD}{mn:>8s}{C_RESET}"
    print(hdr)

    for sn in test_sets:
        is_pos = sn.startswith("pos_")
        for stat_name, stat_key in [("mean", "mean_score"), ("p5", "p5_score"), ("p95", "p95_score")]:
            row = f"  {sn + '/' + stat_name:15s}"
            for mn in model_names:
                m = compute_metrics(all_scores[mn][sn], is_pos, threshold)
                v = m.get(stat_key, 0.0)
                row += f"  {color_score(v)}"
            print(row)

    # === Multi-threshold overview ===
    print_section("Multi-threshold Overview")
    for t in [0.5, 0.7, 0.9, 0.95, 0.99]:
        marker = " <<<" if t == threshold else ""
        row = f"  {C_BOLD}@{t:<5.2f}{C_RESET}"
        for sn in test_sets:
            is_pos = sn.startswith("pos_")
            metric = "recall" if is_pos else "fpr"
            # Show last model only for compact view
            mn = model_names[-1]
            m = compute_metrics(all_scores[mn][sn], is_pos, t)
            v = m.get(metric, 0.0)
            row += f"  {color_val(v, is_pos, metric)}"
        row += f"  {C_DIM}{model_names[-1]}{marker}{C_RESET}"
        print(row)

    labels = "       "
    for sn in test_sets:
        is_pos = sn.startswith("pos_")
        metric = "recall" if is_pos else "fpr"
        labels += f"  {C_DIM}{sn[:7]:>7s}{C_RESET}"
    print(labels)

    # === Model size ===
    print_section("Model Info")
    for mn in model_names:
        p = base / models[mn]
        size_kb = p.stat().st_size / 1024
        print(f"  {C_BOLD}{mn:6s}{C_RESET}  {size_kb:6.1f} KB  {p.name}")

    # === Summary ===
    if len(model_names) >= 2:
        last = model_names[-1]
        prev = model_names[-2]
        print_section(f"Summary: {prev} -> {last}")

        improvements = []
        regressions = []
        for sn in test_sets:
            is_pos = sn.startswith("pos_")
            metric = "recall" if is_pos else "fpr"
            m_last = compute_metrics(all_scores[last][sn], is_pos, threshold)
            m_prev = compute_metrics(all_scores[prev][sn], is_pos, threshold)
            v_last = m_last.get(metric, 0.0)
            v_prev = m_prev.get(metric, 0.0)
            diff = v_last - v_prev

            if metric == "fpr":
                if diff < -0.005:
                    improvements.append(f"{sn} FPR: {v_prev:.1%} -> {v_last:.1%}")
                elif diff > 0.005:
                    regressions.append(f"{sn} FPR: {v_prev:.1%} -> {v_last:.1%}")
            else:
                if diff > 0.005:
                    improvements.append(f"{sn} recall: {v_prev:.1%} -> {v_last:.1%}")
                elif diff < -0.005:
                    regressions.append(f"{sn} recall: {v_prev:.1%} -> {v_last:.1%}")

        if improvements:
            for line in improvements:
                print(f"  {C_GREEN}+{C_RESET} {line}")
        if regressions:
            for line in regressions:
                print(f"  {C_RED}-{C_RESET} {line}")
        if not improvements and not regressions:
            print(f"  {C_DIM}No significant changes at threshold {threshold}{C_RESET}")

    # CSV export
    csv_path = args.csv or str(base / "evaluation" / "model_comparison.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["model", "test_set", "threshold", "metric", "value",
                         "mean_score", "median_score", "std_score", "p5", "p95", "n_clips"])
        for t in [0.5, 0.7, 0.9, 0.95, 0.99]:
            for mn in model_names:
                for sn in test_sets:
                    is_pos = sn.startswith("pos_")
                    metric = "recall" if is_pos else "fpr"
                    m = compute_metrics(all_scores[mn][sn], is_pos, t)
                    writer.writerow([
                        mn, sn, t, metric,
                        f"{m.get(metric, 0):.4f}",
                        f"{m.get('mean_score', 0):.4f}",
                        f"{m.get('median_score', 0):.4f}",
                        f"{m.get('std_score', 0):.4f}",
                        f"{m.get('p5_score', 0):.4f}",
                        f"{m.get('p95_score', 0):.4f}",
                        m.get("n_clips", 0),
                    ])
    print(f"\n{C_DIM}CSV: {csv_path}{C_RESET}")


if __name__ == "__main__":
    main()
