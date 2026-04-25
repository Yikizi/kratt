#!/usr/bin/env python3
"""
Streaming FAPH (False Activations Per Hour) test for microWakeWord models.

Uses the canonical microWakeWord FAPH methodology from
microwakeword.test.compute_false_accepts_per_hour, matching the convention
used by the framework's own tflite streaming evaluation:

  * sliding_window_length = 5  (50 ms moving average @ 10 ms step)
  * ignore_slices_after_accept = 25  (250 ms cooldown)
  * per-track cooldown reset (continuous streaming within a track)

The key methodological point: FAPH must be measured on LONG continuous
audio streams, NOT on thousands of reset-per-clip inferences. In the
default mode this script concatenates every WAV in --input-dir into a
single long track so streaming state and cooldown flow naturally.

Usage:
    python run_faph_test.py \
        --model models/kuule-kratt-v9/kuule_kratt_v9.tflite \
        --input-dir data/processed/faph_test_cv_et \
        --thresholds 0.5 0.7 0.9 0.95 0.97 0.99 0.995
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import soundfile as sf

from microwakeword.inference import Model
from microwakeword.test import compute_false_accepts_per_hour


# Canonical microWakeWord evaluation defaults (see test.test_tflite_model)
DEFAULT_SLIDING_WINDOW = 5       # 50 ms moving average @ 10 ms step
DEFAULT_COOLDOWN_SLICES = 25     # 250 ms refractory period
DEFAULT_STEP_MS = 10             # our training uses window_step_ms = 10


def load_16k_int16(path: Path) -> np.ndarray:
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


def sliding_window_average(probs: np.ndarray, window: int) -> np.ndarray:
    """Match microwakeword.test sliding_window_view + mean semantics."""
    if window <= 1 or probs.size < window:
        return probs
    from numpy.lib.stride_tricks import sliding_window_view
    views = sliding_window_view(probs, window)
    return views.mean(axis=-1)


def build_tracks(
    files: list[Path],
    mode: str,
    inter_clip_silence_ms: int,
    step_ms: int,
) -> list[np.ndarray]:
    """Return a list of int16 PCM tracks.

    mode="single"   - concatenate everything into one long track (closest
                      to real deployment streaming)
    mode="per-file" - one track per input file (legacy behaviour, kept
                      for debugging / A/B comparison)
    """
    if mode not in ("single", "per-file"):
        raise ValueError(f"Unknown mode: {mode}")

    if mode == "per-file":
        return [load_16k_int16(f) for f in files]

    silence_samples = (inter_clip_silence_ms * 16000) // 1000
    silence = np.zeros(silence_samples, dtype=np.int16)

    parts: list[np.ndarray] = []
    for i, f in enumerate(files):
        pcm = load_16k_int16(f)
        if i > 0 and silence_samples > 0:
            parts.append(silence)
        parts.append(pcm)
    return [np.concatenate(parts)]


def main() -> None:
    p = argparse.ArgumentParser(
        description="Streaming FAPH benchmark for microWakeWord models"
    )
    p.add_argument("--model", required=True, help="Path to streaming TFLite model")
    p.add_argument("--input-dir", required=True, help="Directory of WAVs to test on")
    p.add_argument(
        "--thresholds",
        type=float,
        nargs="+",
        default=[0.5, 0.7, 0.9, 0.95, 0.97, 0.99, 0.995],
        help="Cutoff thresholds to report FAPH at",
    )
    p.add_argument(
        "--sliding-window",
        type=int,
        default=DEFAULT_SLIDING_WINDOW,
        help="Sliding window length for moving average (default: 5 slices = 50 ms)",
    )
    p.add_argument(
        "--cooldown-slices",
        type=int,
        default=DEFAULT_COOLDOWN_SLICES,
        help="Refractory period in slices after each activation (default: 25 = 250 ms)",
    )
    p.add_argument(
        "--step-ms",
        type=int,
        default=DEFAULT_STEP_MS,
        help="Spectrogram window step in ms (default: 10, matches training config)",
    )
    p.add_argument(
        "--inter-clip-silence-ms",
        type=int,
        default=300,
        help="Silence to inject between concatenated clips (default: 300)",
    )
    p.add_argument(
        "--mode",
        choices=["single", "per-file"],
        default="single",
        help="single: concatenate all clips into one long track (streaming, default). "
             "per-file: legacy per-clip aggregation (not recommended).",
    )
    p.add_argument("--limit", type=int, default=0, help="Optional cap on number of files")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    files = sorted(Path(args.input_dir).rglob("*.wav"))
    if args.limit > 0:
        files = files[: args.limit]
    if not files:
        raise SystemExit(f"No WAV files in {args.input_dir} (searched recursively)")

    print(f"Loading model: {args.model}")
    model = Model(args.model)

    print(
        f"Building tracks (mode={args.mode}, files={len(files)}, "
        f"silence={args.inter_clip_silence_ms}ms)..."
    )
    tracks_pcm = build_tracks(
        files,
        mode=args.mode,
        inter_clip_silence_ms=args.inter_clip_silence_ms,
        step_ms=args.step_ms,
    )

    total_samples = sum(t.size for t in tracks_pcm)
    total_seconds = total_samples / 16000.0
    total_hours = total_seconds / 3600.0

    print(
        f"  {len(tracks_pcm)} track(s), "
        f"{total_seconds:.0f}s = {total_seconds / 60:.1f}min = {total_hours:.2f}h"
    )

    # Run streaming inference per track, with moving average smoothing
    print("Running streaming inference...")
    smoothed_tracks: list[np.ndarray] = []
    for i, pcm in enumerate(tracks_pcm):
        raw = np.array(
            model.predict_clip(pcm, step_ms=args.step_ms),
            dtype=np.float32,
        )
        smoothed = sliding_window_average(raw, args.sliding_window)
        smoothed_tracks.append(smoothed)
        if args.verbose:
            print(
                f"  track {i}: {len(raw)} slices raw, "
                f"{len(smoothed)} after smoothing, "
                f"max={smoothed.max():.3f}"
            )

    # Use the canonical microWakeWord FAPH function
    cutoffs = np.array(args.thresholds, dtype=np.float32)
    faph_values = compute_false_accepts_per_hour(
        smoothed_tracks,
        cutoffs=cutoffs,
        ignore_slices_after_accept=args.cooldown_slices,
        stride=1,
        step_s=args.step_ms / 1000.0,
    )

    # Report
    print()
    print("=" * 60)
    print(f"Model:            {args.model}")
    print(f"Mode:             {args.mode}")
    print(f"Tracks:           {len(smoothed_tracks)}")
    print(f"Total duration:   {total_seconds:.0f}s = {total_hours:.2f}h")
    print(f"Sliding window:   {args.sliding_window} slices "
          f"({args.sliding_window * args.step_ms}ms MA)")
    print(f"Cooldown:         {args.cooldown_slices} slices "
          f"({args.cooldown_slices * args.step_ms}ms refractory)")
    print("-" * 60)
    print(f"{'Threshold':>10s}  {'FAPH':>10s}  {'Activations':>12s}")
    print("-" * 60)
    for t, faph in zip(args.thresholds, faph_values):
        activations = round(faph * total_hours)
        print(f"{t:>10.4f}  {faph:>10.2f}  {activations:>12d}")
    print("=" * 60)


if __name__ == "__main__":
    main()
