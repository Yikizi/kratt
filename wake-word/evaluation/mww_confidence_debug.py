#!/usr/bin/env python3
"""
microWakeWord confidence debugger (offline + live mic).

Examples:
  python wake-word/evaluation/mww_confidence_debug.py \
    --model /Users/mattias/kratt/hardware/esp32/esphome/models/kratt.tflite \
    --audio ~/Downloads/kratt.m4a

  python wake-word/evaluation/mww_confidence_debug.py \
    --model /Users/mattias/kratt/hardware/esp32/esphome/models/kratt.tflite \
    --live
"""

from __future__ import annotations

import argparse
import collections
import math
import os
import subprocess
import threading
import time
import tempfile
from pathlib import Path

import numpy as np

from microwakeword.inference import Model


def load_audio_16k_mono_int16(path: Path) -> np.ndarray:
    import soundfile as sf
    import librosa

    try:
        audio, sr = sf.read(str(path), always_2d=False)
    except Exception:
        # Fallback for formats unsupported by libsndfile (e.g. many .m4a files).
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_wav = tmp.name
        try:
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(path),
                "-ac",
                "1",
                "-ar",
                "16000",
                "-c:a",
                "pcm_s16le",
                tmp_wav,
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                raise RuntimeError(proc.stderr.strip() or "ffmpeg conversion failed")
            audio, sr = sf.read(tmp_wav, always_2d=False)
        finally:
            if os.path.exists(tmp_wav):
                os.remove(tmp_wav)

    if isinstance(audio, np.ndarray) and audio.ndim > 1:
        audio = audio[:, 0]
    audio = audio.astype(np.float32, copy=False)

    if sr != 16000:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000).astype(np.float32)

    audio = np.clip(audio, -1.0, 1.0)
    return (audio * 32767.0).astype(np.int16)


def moving_average(values: np.ndarray, window: int) -> np.ndarray:
    if window <= 1 or values.size == 0:
        return values
    kernel = np.ones(window, dtype=np.float32) / float(window)
    return np.convolve(values, kernel, mode="valid")


def summarize_scores(scores: np.ndarray, window: int, step_ms: int) -> str:
    if scores.size == 0:
        return "No scores produced (audio too short for model input window)."

    smoothed = moving_average(scores, window)
    max_idx = int(np.argmax(scores))
    max_t_s = (max_idx * step_ms) / 1000.0
    msg = [
        f"scores={scores.size}",
        f"max_raw={scores[max_idx]:.4f} @ {max_t_s:.2f}s",
        f"mean_raw={float(scores.mean()):.4f}",
        f"p95_raw={float(np.quantile(scores, 0.95)):.4f}",
    ]
    if smoothed.size > 0:
        sm_idx = int(np.argmax(smoothed))
        sm_t_s = (sm_idx * step_ms) / 1000.0
        msg.append(f"max_ma{window}={smoothed[sm_idx]:.4f} @ {sm_t_s:.2f}s")
    return " | ".join(msg)


def run_offline(model: Model, audio_path: Path, step_ms: int, ma_window: int) -> int:
    pcm = load_audio_16k_mono_int16(audio_path)
    scores = np.array(model.predict_clip(pcm, step_ms=step_ms), dtype=np.float32)
    print(f"Audio: {audio_path}")
    print(summarize_scores(scores, ma_window, step_ms))
    return 0


def run_live(model: Model, step_ms: int, ma_window: int, buffer_s: float) -> int:
    try:
        import sounddevice as sd
    except ImportError:
        print("Missing dependency: sounddevice")
        print("Install in venv: pip install sounddevice")
        return 2

    max_samples = int(buffer_s * 16000)
    ring = collections.deque(maxlen=max_samples)
    lock = threading.Lock()

    def callback(indata, frames, _time_info, status):
        if status:
            pass
        chunk = indata[:, 0].copy()
        with lock:
            ring.extend(chunk.tolist())

    print("Live mode started. Speak wake word. Press Ctrl+C to stop.")
    with sd.InputStream(
        samplerate=16000,
        channels=1,
        dtype="int16",
        blocksize=1600,
        callback=callback,
    ):
        try:
            while True:
                time.sleep(0.25)
                with lock:
                    if len(ring) < 16000:
                        continue
                    pcm = np.array(ring, dtype=np.int16)

                scores = np.array(model.predict_clip(pcm, step_ms=step_ms), dtype=np.float32)
                if scores.size == 0:
                    continue
                smoothed = moving_average(scores, ma_window)
                raw_now = float(scores[-1])
                ma_now = float(smoothed[-1]) if smoothed.size > 0 else raw_now
                peak = float(scores.max())
                print(f"raw_now={raw_now:.3f} ma{ma_window}_now={ma_now:.3f} peak={peak:.3f}")
        except KeyboardInterrupt:
            print("\nStopped.")
            return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="microWakeWord confidence debugger")
    parser.add_argument("--model", required=True, help="Path to microWakeWord .tflite model")
    parser.add_argument("--audio", help="Path to audio file (wav/m4a/etc readable by soundfile)")
    parser.add_argument("--live", action="store_true", help="Read microphone and print live confidence")
    parser.add_argument("--step-ms", type=int, default=10, help="Feature step size in ms")
    parser.add_argument(
        "--ma-window",
        type=int,
        default=3,
        help="Moving-average window over scores (similar to ESPHome sliding window idea)",
    )
    parser.add_argument(
        "--buffer-s",
        type=float,
        default=2.0,
        help="Live mode ring buffer duration in seconds",
    )

    args = parser.parse_args()
    if not args.audio and not args.live:
        parser.error("Provide at least one of: --audio or --live")

    model_path = Path(args.model).expanduser().resolve()
    if not model_path.exists():
        print(f"Model not found: {model_path}")
        return 2

    model = Model(str(model_path))

    rc = 0
    if args.audio:
        audio_path = Path(args.audio).expanduser().resolve()
        if not audio_path.exists():
            print(f"Audio not found: {audio_path}")
            return 2
        rc = max(rc, run_offline(model, audio_path, args.step_ms, args.ma_window))

    if args.live:
        rc = max(rc, run_live(model, args.step_ms, args.ma_window, args.buffer_s))

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
