#!/usr/bin/env python3
"""Benchmark an openWakeWord ONNX model on Kratt test sets.

Outputs CSV rows compatible with the microWakeWord benchmark schema:
  timestamp,model,test_set,kind,threshold,metric,value,n,duration_h,combo
"""
from __future__ import annotations

import argparse
import csv
import math
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import soundfile as sf

try:
    import librosa
except Exception:  # pragma: no cover
    librosa = None

from openwakeword import Model as OpenWakeWordModel

BASE = Path(__file__).resolve().parent.parent
DATA_ROOT = Path(os.environ.get("KRATT_DATA", BASE / "data"))
FRAME = 1280  # 80 ms at 16 kHz
SILENCE_MS = 300
COOLDOWN_SECONDS = 0.25

CLIP_SETS: dict[str, dict] = {
    "pos_isa_xtts": {
        "path": DATA_ROOT / "processed/test_pos_xtts_isa",
        "kind": "positive",
        "metric": "recall",
    },
    "pos_ode": {
        "path": DATA_ROOT / "raw/ode_kuule_kratt",
        "kind": "positive",
        "metric": "recall",
    },
    "pos_mattias_short": {
        "path": DATA_ROOT / "raw/mattias-short/positive",
        "kind": "positive",
        "metric": "recall",
    },
    "pos_friend1": {
        "path": DATA_ROOT / "raw/friend1_20260414",
        "kind": "positive",
        "metric": "recall",
    },
    "hard_neg_mac_holdout": {
        "path": DATA_ROOT / "processed/hard_neg_test",
        "kind": "hard_negative",
        "metric": "fpr",
    },
    "hard_neg_isa_xtts": {
        "path": DATA_ROOT / "processed/test_hard_neg_xtts_isa",
        "kind": "hard_negative",
        "metric": "fpr",
    },
    "hard_neg_canary": {
        "path": DATA_ROOT / "processed/test_neg_false_accepts_v10_canary",
        "kind": "hard_negative",
        "metric": "fpr",
    },
    "neg_prefix_only_mattias_short": {
        "path": DATA_ROOT / "processed/prefix_regression_test/prefix_only_mattias_short_lt0p80",
        "kind": "hard_negative",
        "metric": "fpr",
    },
    "neg_single_kratt_neurokone": {
        "path": DATA_ROOT / "processed/prefix_regression_test/single_kratt_neurokone_phase1",
        "kind": "hard_negative",
        "metric": "fpr",
    },
    "neg_reversed_kratt_kuule": {
        "path": DATA_ROOT / "processed/prefix_regression_test/reversed_kratt_kuule_phase1",
        "kind": "hard_negative",
        "metric": "fpr",
    },
    "neg_kuule_kule_confusables": {
        "path": DATA_ROOT / "processed/prefix_regression_test/kuule_kule_confusables_neurokone_hard_neg_v2",
        "kind": "hard_negative",
        "metric": "fpr",
    },
}

FAPH_SETS: dict[str, Path] = {
    "faph_cv_et": DATA_ROOT / "processed/faph_test_cv_et",
    "faph_librispeech": DATA_ROOT / "processed/benchmarks/librispeech-test-clean",
    "faph_macbook_bg": DATA_ROOT / "raw/macbook_negatives",
    "faph_dipco": DATA_ROOT / "processed/benchmarks/dipco",
}


def audio_files(path: Path) -> list[Path]:
    files: list[Path] = []
    if path.exists():
        for ext in ("*.wav", "*.flac"):
            files.extend(path.rglob(ext))
    return sorted(files)


def load_16k(path: Path) -> np.ndarray:
    audio, sr = sf.read(str(path), always_2d=False)
    if audio.ndim > 1:
        audio = audio[:, 0]
    audio = audio.astype(np.float32)
    if sr != 16000:
        if librosa is None:
            raise RuntimeError("librosa is required for resampling non-16k audio")
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
    if np.issubdtype(audio.dtype, np.floating):
        audio = np.clip(audio, -1.0, 1.0) * 32767.0
    return audio.astype(np.int16)


def chunks(audio: np.ndarray, pad_final: bool = True):
    for start in range(0, len(audio), FRAME):
        chunk = audio[start:start + FRAME]
        if len(chunk) < FRAME:
            if not pad_final:
                break
            chunk = np.pad(chunk, (0, FRAME - len(chunk)))
        yield chunk


def model_key(model: OpenWakeWordModel, model_path: Path) -> str:
    # Avoid calling Model.predict here: custom long-window models can have fewer
    # than the required feature frames during cold start, which makes upstream
    # openWakeWord call ONNX with the wrong input shape.
    stem = model_path.stem
    keys = list(model.models.keys())
    if stem in keys:
        return stem
    return keys[0] if keys else stem


def predict_safe(model: OpenWakeWordModel, key: str, chunk: np.ndarray) -> float:
    """Run one streaming step, tolerating long custom model windows.

    openWakeWord's stock Model.predict assumes that get_features(n) always
    returns n frames. For this trained model n=72, but cold-start buffers can be
    shorter. We call the preprocessor ourselves and only run ONNX once enough
    embedding frames exist.
    """
    model.preprocessor(chunk)
    n_frames = int(model.model_inputs[key])
    if model.preprocessor.feature_buffer.shape[0] < n_frames:
        return 0.0
    x = model.preprocessor.get_features(n_frames)
    sess = model.models[key]
    y = sess.run(None, {sess.get_inputs()[0].name: x})[0]
    return float(np.asarray(y).reshape(-1)[0])


def clip_peak(model: OpenWakeWordModel, key: str, path: Path) -> float:
    model.reset()
    peak = 0.0
    # Warm with enough silence to fill melspec/embedding context. This mirrors a
    # real continuously running detector and avoids penalizing short clips for
    # cold start only.
    warm = np.zeros(max(16000 * 7, FRAME * (int(model.model_inputs[key]) + 10)), dtype=np.int16)
    for chunk in chunks(warm):
        predict_safe(model, key, chunk)
    for chunk in chunks(load_16k(path)):
        peak = max(peak, predict_safe(model, key, chunk))
    model.reset()
    return peak


def stream_peaks(model: OpenWakeWordModel, key: str, files: list[Path], label: str = "stream") -> tuple[np.ndarray, float]:
    model.reset()
    scores: list[float] = []
    total_samples = 0
    silence = np.zeros((SILENCE_MS * 16000) // 1000, dtype=np.int16)
    for i, path in enumerate(files, start=1):
        if i > 1:
            total_samples += len(silence)
            for chunk in chunks(silence):
                scores.append(predict_safe(model, key, chunk))
        audio = load_16k(path)
        total_samples += len(audio)
        for chunk in chunks(audio):
            scores.append(predict_safe(model, key, chunk))
        if i == 1 or i % 50 == 0 or i == len(files):
            hours = total_samples / 16000.0 / 3600.0
            print(f"    {label}: {i}/{len(files)} ({hours:.2f}h simulated)", flush=True)
    model.reset()
    return np.array(scores, dtype=np.float32), total_samples / 16000.0 / 3600.0


def count_detections(scores: np.ndarray, threshold: float) -> int:
    cooldown_frames = max(1, int(math.ceil(COOLDOWN_SECONDS / (FRAME / 16000.0))))
    count = 0
    cooldown = 0
    for score in scores:
        if cooldown > 0:
            cooldown -= 1
            continue
        if score >= threshold:
            count += 1
            cooldown = cooldown_frames
    return count


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", required=True, type=Path)
    ap.add_argument("--name", default=None)
    ap.add_argument("--output", "-o", default=None)
    ap.add_argument("--thresholds", type=float, nargs="+", default=[0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99])
    ap.add_argument(
        "--include-mattias-short",
        action="store_true",
        help="Include pos_mattias_short recall set. Off by default because recall-cv/openWakeWord runs may train on this source.",
    )
    args = ap.parse_args()

    if not args.include_mattias_short:
        CLIP_SETS.pop("pos_mattias_short", None)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_tag = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    out = Path(args.output) if args.output else BASE / "evaluation" / f"benchmark_openwakeword_{date_tag}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)

    model_name = args.name or args.model.stem
    print(f"Loading openWakeWord model: {args.model}")
    model = OpenWakeWordModel(wakeword_models=[str(args.model)])
    key = model_key(model, args.model)
    print(f"Prediction key: {key}")

    rows: list[dict] = []

    print("\nClip-level scoring...")
    for set_name, info in CLIP_SETS.items():
        files = audio_files(info["path"])
        if not files:
            print(f"  SKIP {set_name}: no files")
            continue
        print(f"  {set_name}: {len(files)} clips", flush=True)
        peaks_list: list[float] = []
        for i, path in enumerate(files, start=1):
            peaks_list.append(clip_peak(model, key, path))
            if i == 1 or i % 10 == 0 or i == len(files):
                print(f"    {set_name}: {i}/{len(files)}", flush=True)
        peaks = np.array(peaks_list, dtype=np.float32)
        for threshold in args.thresholds:
            hits = int((peaks >= threshold).sum())
            if info["metric"] == "recall":
                value = hits / len(files)
            else:
                value = hits / len(files)
            rows.append({
                "timestamp": timestamp,
                "model": model_name,
                "test_set": set_name,
                "kind": info["kind"],
                "threshold": threshold,
                "metric": info["metric"],
                "value": value,
                "n": len(files),
                "duration_h": "",
                "combo": "",
            })
        print(f"    peak range: min={peaks.min():.4f} p50={np.median(peaks):.4f} max={peaks.max():.4f}", flush=True)

    print("\nStreaming FAPH...")
    for set_name, path in FAPH_SETS.items():
        files = audio_files(path)
        if not files:
            print(f"  SKIP {set_name}: no files")
            continue
        print(f"  {set_name}: {len(files)} files", flush=True)
        scores, hours = stream_peaks(model, key, files, set_name)
        for threshold in args.thresholds:
            detections = count_detections(scores, threshold)
            faph = detections / hours if hours > 0 else 0.0
            rows.append({
                "timestamp": timestamp,
                "model": model_name,
                "test_set": set_name,
                "kind": "ambient",
                "threshold": threshold,
                "metric": "faph",
                "value": faph,
                "n": len(files),
                "duration_h": round(hours, 4),
                "combo": "",
            })
        print(f"    hours={hours:.2f} score range: min={scores.min():.4f} p99={np.quantile(scores, 0.99):.4f} max={scores.max():.4f}", flush=True)

    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "model", "test_set", "kind", "threshold", "metric", "value", "n", "duration_h", "combo"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
