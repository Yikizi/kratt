#!/usr/bin/env python3
"""
Generate analysis plots and summary tables for a microWakeWord run.

Outputs thesis-friendly artifacts under:
  <run_dir>/analysis/
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import soundfile as sf
import yaml

from microwakeword.inference import Model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True, help="Path to a microWakeWord run dir.")
    parser.add_argument(
        "--model-path",
        help="Override path to the TFLite model. Defaults to the quantized streaming model in run dir.",
    )
    parser.add_argument("--positive-dir", help="Directory of positive wav files for score analysis.")
    parser.add_argument("--negative-dir", help="Directory of negative wav files for score analysis.")
    parser.add_argument(
        "--hard-negative-dir",
        help="Directory of HARD negative wav files (phonetically similar phrases).",
    )
    parser.add_argument(
        "--ambient-dir",
        help="Directory of ambient wav files for dataset summary.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=250,
        help="Maximum number of files to score from positive and negative dirs.",
    )
    parser.add_argument(
        "--step-ms",
        type=int,
        default=10,
        help="Feature step size for inference.",
    )
    parser.add_argument(
        "--ma-window",
        type=int,
        default=5,
        help="Moving-average window applied to streaming scores.",
    )
    return parser.parse_args()


def load_audio_16k_mono_int16(path: Path) -> np.ndarray:
    audio, sr = sf.read(str(path), always_2d=False)
    if isinstance(audio, np.ndarray) and audio.ndim > 1:
        audio = audio[:, 0]
    audio = audio.astype(np.float32, copy=False)
    if sr != 16000:
        import librosa

        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000).astype(
            np.float32, copy=False
        )
    audio = np.clip(audio, -1.0, 1.0)
    return (audio * 32767.0).astype(np.int16)


def moving_average(values: np.ndarray, window: int) -> np.ndarray:
    if window <= 1 or values.size == 0:
        return values
    kernel = np.ones(window, dtype=np.float32) / float(window)
    return np.convolve(values, kernel, mode="valid")


def parse_roc_file(path: Path) -> tuple[float | None, pd.DataFrame]:
    auc_value = None
    rows: list[dict[str, float]] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("AUC "):
            auc_value = float(line.split()[1])
            continue
        if not line.startswith("Cutoff "):
            continue
        left, right = line.split(": ", 1)
        cutoff = float(left.split()[1])
        pieces = dict(part.split("=") for part in right.split("; "))
        rows.append(
            {
                "cutoff": cutoff,
                "frr": float(pieces["frr"]),
                "faph": float(pieces["faph"]),
            }
        )
    return auc_value, pd.DataFrame(rows)


def score_dataset(
    model: Model,
    directory: Path,
    label: str,
    limit: int,
    step_ms: int,
    ma_window: int,
) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    files = sorted(directory.glob("*.wav"))
    if limit > 0:
        files = files[:limit]

    for wav_path in files:
        pcm = load_audio_16k_mono_int16(wav_path)
        raw_scores = np.array(model.predict_clip(pcm, step_ms=step_ms), dtype=np.float32)
        smoothed = moving_average(raw_scores, ma_window)

        if raw_scores.size == 0:
            rows.append(
                {
                    "file": wav_path.name,
                    "label": label,
                    "max_raw": np.nan,
                    "mean_raw": np.nan,
                    "p95_raw": np.nan,
                    "max_ma": np.nan,
                    "duration_s": len(pcm) / 16000.0,
                }
            )
            continue

        rows.append(
            {
                "file": wav_path.name,
                "label": label,
                "max_raw": float(raw_scores.max()),
                "mean_raw": float(raw_scores.mean()),
                "p95_raw": float(np.quantile(raw_scores, 0.95)),
                "max_ma": float(smoothed.max()) if smoothed.size else float(raw_scores.max()),
                "duration_s": len(pcm) / 16000.0,
            }
        )
    return rows


def count_wavs(path: Path | None) -> int:
    if path is None or not path.exists():
        return 0
    return len(list(path.glob("*.wav")))


def sum_duration_s(path: Path | None) -> float:
    if path is None or not path.exists():
        return 0.0
    duration = 0.0
    for wav_path in sorted(path.glob("*.wav")):
        info = sf.info(str(wav_path))
        duration += float(info.frames) / float(info.samplerate)
    return duration


def ensure_analysis_dir(run_dir: Path) -> Path:
    analysis_dir = run_dir / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    return analysis_dir


def save_roc_plot(df: pd.DataFrame, auc_value: float | None, out_path: Path) -> None:
    plt.figure(figsize=(7, 5))
    plt.plot(df["faph"], df["frr"], marker="o", linewidth=1.8)
    plt.xlabel("False Accepts Per Hour (FAPH)")
    plt.ylabel("False Rejection Rate (FRR)")
    title = "microWakeWord Streaming ROC"
    if auc_value is not None:
        title += f" (AUC={auc_value:.4f})"
    plt.title(title)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


def save_score_plot(df: pd.DataFrame, out_path: Path) -> None:
    plt.figure(figsize=(8, 5))
    for label, color in [("positive", "#2a9d8f"), ("negative", "#e76f51")]:
        values = df.loc[df["label"] == label, "max_ma"].dropna()
        if len(values) == 0:
            continue
        plt.hist(values, bins=30, alpha=0.55, label=label, color=color)
    plt.xlabel("Maximum moving-average score")
    plt.ylabel("Clip count")
    plt.title("Score Separation on Evaluation Clips")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


def save_dataset_plot(summary: dict[str, float | int], out_path: Path) -> None:
    labels = ["positive", "negative", "ambient"]
    counts = [summary["positive_count"], summary["negative_count"], summary["ambient_count"]]

    plt.figure(figsize=(7, 5))
    bars = plt.bar(labels, counts, color=["#2a9d8f", "#e76f51", "#457b9d"])
    plt.ylabel("File count")
    plt.title("Experiment Dataset Composition")
    for bar, value in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width() / 2.0, value, str(value), ha="center", va="bottom")
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


def compute_clip_threshold_metrics(
    score_df: pd.DataFrame,
    thresholds: list[float] | None = None,
) -> pd.DataFrame:
    if thresholds is None:
        thresholds = [0.3, 0.5, 0.7, 0.9]

    if score_df.empty:
        return pd.DataFrame(
            columns=["threshold", "recall", "false_positive_rate", "accuracy", "tp", "tn", "fp", "fn"]
        )

    rows: list[dict[str, float | int]] = []
    y_true = (score_df["label"] == "positive").astype(int).to_numpy()
    y_score = score_df["max_ma"].to_numpy()

    for threshold in thresholds:
        y_pred = (y_score >= threshold).astype(int)
        tp = int(np.sum((y_true == 1) & (y_pred == 1)))
        tn = int(np.sum((y_true == 0) & (y_pred == 0)))
        fp = int(np.sum((y_true == 0) & (y_pred == 1)))
        fn = int(np.sum((y_true == 1) & (y_pred == 0)))

        recall = tp / (tp + fn) if (tp + fn) else np.nan
        fpr = fp / (fp + tn) if (fp + tn) else np.nan
        accuracy = (tp + tn) / len(y_true) if len(y_true) else np.nan
        rows.append(
            {
                "threshold": threshold,
                "recall": recall,
                "false_positive_rate": fpr,
                "accuracy": accuracy,
                "tp": tp,
                "tn": tn,
                "fp": fp,
                "fn": fn,
            }
        )

    return pd.DataFrame(rows)


def choose_operating_points(roc_df: pd.DataFrame) -> pd.DataFrame:
    if roc_df.empty:
        return pd.DataFrame(columns=["criterion", "cutoff", "frr", "faph"])

    rows: list[dict[str, float | str]] = []

    min_frr_idx = roc_df["frr"].idxmin()
    rows.append({"criterion": "min_frr", **roc_df.loc[min_frr_idx].to_dict()})

    zero_faph = roc_df.loc[roc_df["faph"] <= 0.0]
    if not zero_faph.empty:
        best_zero = zero_faph.sort_values(["frr", "cutoff"], ascending=[True, False]).iloc[0]
        rows.append({"criterion": "best_zero_faph", **best_zero.to_dict()})

    at_or_below_two = roc_df.loc[roc_df["faph"] <= 2.0]
    if not at_or_below_two.empty:
        best_two = at_or_below_two.sort_values(["frr", "cutoff"], ascending=[True, False]).iloc[0]
        rows.append({"criterion": "best_at_or_below_2_faph", **best_two.to_dict()})

    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    if not run_dir.exists():
        raise SystemExit(f"Run dir not found: {run_dir}")

    analysis_dir = ensure_analysis_dir(run_dir)
    roc_path = run_dir / "tflite_stream_state_internal_quant" / "tflite_streaming_roc.txt"
    if not roc_path.exists():
        raise SystemExit(f"ROC file not found: {roc_path}")

    model_path = (
        Path(args.model_path).expanduser().resolve()
        if args.model_path
        else run_dir / "tflite_stream_state_internal_quant" / "stream_state_internal_quant.tflite"
    )
    if not model_path.exists():
        raise SystemExit(f"Model file not found: {model_path}")

    positive_dir = Path(args.positive_dir).expanduser().resolve() if args.positive_dir else None
    negative_dir = Path(args.negative_dir).expanduser().resolve() if args.negative_dir else None
    hard_negative_dir = (
        Path(args.hard_negative_dir).expanduser().resolve() if args.hard_negative_dir else None
    )
    ambient_dir = Path(args.ambient_dir).expanduser().resolve() if args.ambient_dir else None

    auc_value, roc_df = parse_roc_file(roc_path)
    roc_df.to_csv(analysis_dir / "roc_points.csv", index=False)
    save_roc_plot(roc_df, auc_value, analysis_dir / "roc_faph_vs_frr.png")

    operating_points = choose_operating_points(roc_df)
    operating_points.to_csv(analysis_dir / "recommended_cutoffs.csv", index=False)

    dataset_summary = {
        "positive_count": count_wavs(positive_dir),
        "negative_count": count_wavs(negative_dir),
        "hard_negative_count": count_wavs(hard_negative_dir),
        "ambient_count": count_wavs(ambient_dir),
        "ambient_duration_s": sum_duration_s(ambient_dir),
    }
    (analysis_dir / "dataset_summary.json").write_text(
        json.dumps(dataset_summary, indent=2, sort_keys=True) + "\n"
    )
    save_dataset_plot(dataset_summary, analysis_dir / "dataset_composition.png")

    score_df = pd.DataFrame()
    if positive_dir is not None and negative_dir is not None:
        model = Model(str(model_path))
        score_rows = []
        score_rows.extend(
            score_dataset(model, positive_dir, "positive", args.limit, args.step_ms, args.ma_window)
        )
        score_rows.extend(
            score_dataset(model, negative_dir, "negative", args.limit, args.step_ms, args.ma_window)
        )
        if hard_negative_dir is not None:
            score_rows.extend(
                score_dataset(model, hard_negative_dir, "hard_negative", args.limit, args.step_ms, args.ma_window)
            )
        score_df = pd.DataFrame(score_rows)
        score_df.to_csv(analysis_dir / "clip_scores.csv", index=False, quoting=csv.QUOTE_MINIMAL)
        if not score_df.empty:
            grouped = (
                score_df.groupby("label")[["max_raw", "mean_raw", "p95_raw", "max_ma"]]
                .agg(["mean", "median", "std", "min", "max"])
            )
            grouped.to_csv(analysis_dir / "score_summary_by_label.csv")
            save_score_plot(score_df, analysis_dir / "score_distribution.png")
            compute_clip_threshold_metrics(score_df).to_csv(
                analysis_dir / "clip_threshold_metrics.csv", index=False
            )

    config_path = run_dir / "training_config.yaml"
    if config_path.exists():
        config = yaml.unsafe_load(config_path.read_text())
        (analysis_dir / "training_config_snapshot.json").write_text(
            json.dumps(config, indent=2, sort_keys=True) + "\n"
        )

    print(f"Analysis written to: {analysis_dir}")
    print(f"  ROC points:          {analysis_dir / 'roc_points.csv'}")
    print(f"  ROC plot:            {analysis_dir / 'roc_faph_vs_frr.png'}")
    print(f"  Recommended cutoffs: {analysis_dir / 'recommended_cutoffs.csv'}")
    print(f"  Dataset summary:     {analysis_dir / 'dataset_summary.json'}")
    if not score_df.empty:
        print(f"  Clip scores:         {analysis_dir / 'clip_scores.csv'}")
        print(f"  Score plot:          {analysis_dir / 'score_distribution.png'}")
        print(f"  Threshold metrics:   {analysis_dir / 'clip_threshold_metrics.csv'}")


if __name__ == "__main__":
    main()
