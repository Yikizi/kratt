#!/usr/bin/env python3
"""Run multiple wake word models simultaneously on the same mic input.

Consensus modes:
  --mode min       (default) Benchmark-like same-frame consensus: smooth each
                   model probability, then threshold min(model probabilities).
  --mode product   Multiply smoothed per-frame probabilities, then threshold.
  --mode window    (legacy) Each model triggers independently; consensus if
                   all fire within --consensus-window-ms.

Usage:
    python multi_model_live_test.py v14 expert-a
    python multi_model_live_test.py v14 expert-a --threshold 0.995
    python multi_model_live_test.py v14 expert-a --mode min --threshold 0.995
    python multi_model_live_test.py v14 expert-a --mode window --threshold 0.997
    python multi_model_live_test.py --log live.jsonl v14 expert-a
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import warnings
from collections import deque
from datetime import datetime
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
warnings.filterwarnings("ignore", message=r".*tf\.lite\.Interpreter is deprecated.*")

import numpy as np
import sounddevice as sd

try:
    from pymicro_features import MicroFrontend
except ImportError:
    print("pip install 'git+https://github.com/puddly/pymicro-features@puddly/minimum-cpp-version'")
    sys.exit(1)

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    import tensorflow.lite as tflite

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
SAMPLE_RATE = 16000
FRAME_MS = 10
MA_WINDOW = 5

MODEL_ALIASES = {
    "checkpoint-faph": "checkpoint-faph-v18d-clean96-pw96x4",
    "checkpoint-faph10": "checkpoint-faph10-v18d-clean96-pw96x4",
    "checkpoint-faph20": "checkpoint-faph20-v18d-clean96-pw96x4",
}

COLORS = [
    "\033[32m", "\033[33m", "\033[36m", "\033[35m",
    "\033[34m", "\033[91m", "\033[92m", "\033[93m",
]
RESET = "\033[0m"
BOLD = "\033[1m"


def model_path_from_tag(tag: str) -> Path:
    return MODELS_DIR / f"kuule-kratt-{tag}" / f"kuule_kratt_{tag}.tflite"


def natural_key(value: str) -> list[object]:
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", value)]


def available_model_tags() -> list[str]:
    tags = []
    for d in MODELS_DIR.glob("kuule-kratt-*"):
        if not d.is_dir():
            continue
        tag = d.name.removeprefix("kuule-kratt-")
        if model_path_from_tag(tag).exists():
            tags.append(tag)
    return sorted(tags, key=natural_key)


def resolve_model_tag(tag: str) -> tuple[str, Path]:
    tag = tag.removeprefix("kuule-kratt-")
    tag = MODEL_ALIASES.get(tag, tag)

    exact_path = model_path_from_tag(tag)
    if exact_path.exists():
        return tag, exact_path

    matches = [candidate for candidate in available_model_tags() if candidate.startswith(tag)]
    if len(matches) == 1:
        resolved = matches[0]
        return resolved, model_path_from_tag(resolved)

    if len(matches) > 1:
        raise ValueError(
            "Ambiguous model alias "
            f"'{tag}'. Matches: " + ", ".join(matches)
        )

    raise ValueError(f"Model not found: {tag}")


class StreamingModel:
    """Streaming TFLite model that returns a raw probability per frame."""

    def __init__(self, name: str, tflite_path: str, color: str):
        self.name = name
        self.color = color
        self.interpreter = tflite.Interpreter(model_path=tflite_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.audio_input_idx = 0
        self.warmup_frames = 50
        self.frame_count = 0

        for detail in self.input_details:
            self.interpreter.set_tensor(
                detail["index"],
                np.zeros(detail["shape"], dtype=detail["dtype"]),
            )

    def process_features(self, features: np.ndarray) -> float:
        """Feed one spectrogram frame, return raw probability (0-1)."""
        expected_shape = self.input_details[self.audio_input_idx]["shape"]
        features = features.reshape(expected_shape)

        inp_dtype = self.input_details[self.audio_input_idx]["dtype"]
        if inp_dtype == np.int8:
            scale, zp = self.input_details[self.audio_input_idx]["quantization"]
            features = (features / scale + zp).clip(-128, 127).astype(np.int8)

        self.interpreter.set_tensor(
            self.input_details[self.audio_input_idx]["index"], features
        )
        self.interpreter.invoke()
        self.frame_count += 1

        if self.frame_count <= self.warmup_frames:
            return 0.0

        output = self.interpreter.get_tensor(self.output_details[0]["index"])
        out_dtype = self.output_details[0]["dtype"]
        if out_dtype in (np.int8, np.uint8):
            scale, zp = self.output_details[0]["quantization"]
            return float(((output.astype(np.float32) - zp) * scale).flat[0])
        return float(output.flatten()[0])


def main():
    parser = argparse.ArgumentParser(description="Multi-model live wake word test")
    parser.add_argument("models", nargs="+", help="Model tags (e.g. v14 expert-a)")
    parser.add_argument("--threshold", type=float, nargs="+", default=[0.95],
                        help="Combined threshold (product mode) or per-model (window mode)")
    parser.add_argument("--log", type=str, default=None, help="JSONL log file")
    parser.add_argument("--device", type=int, default=None, help="Mic device ID")
    parser.add_argument("--mode", choices=["min", "product", "window"], default="min",
                        help="Consensus mode: min (benchmark-like same-frame consensus, default), "
                             "product (multiply probs), or window (legacy independent triggers)")
    parser.add_argument("--consensus-window-ms", type=int, default=1000,
                        help="Time window for window mode (ms)")
    parser.add_argument("--cooldown", type=float, default=2.0,
                        help="Seconds after detection before next trigger")
    parser.add_argument("--ma-window", type=int, default=MA_WINDOW,
                        help="Moving average window size in frames")
    parser.add_argument("--alert-sound", default="ping", help="Sound alias (ping|pop|tink|none) or path")
    args = parser.parse_args()

    # Resolve all tags before loading any TFLite interpreter; this keeps bad-model
    # errors clean and avoids TensorFlow warnings before the actual error message.
    resolved_models: list[tuple[str, str, Path]] = []
    load_failed = False
    for requested_tag in args.models:
        try:
            tag, tflite_path = resolve_model_tag(requested_tag)
            resolved_models.append((requested_tag, tag, tflite_path))
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            print("\nAvailable models:", file=sys.stderr)
            for candidate in available_model_tags():
                print(f"  {candidate}", file=sys.stderr)
            load_failed = True

    if load_failed:
        sys.exit("Model load failed")

    streaming_models: list[StreamingModel] = []
    for i, (requested_tag, tag, tflite_path) in enumerate(resolved_models):
        color = COLORS[i % len(COLORS)]
        m = StreamingModel(tag, str(tflite_path), color)
        streaming_models.append(m)
        alias_note = f" ← {requested_tag}" if requested_tag != tag else ""
        print(f"  {color}■{RESET} {tag}{alias_note}")

    if not streaming_models:
        sys.exit("No models loaded")

    n_models = len(streaming_models)

    # Threshold setup
    if args.mode in {"min", "product"}:
        combined_threshold = args.threshold[0]
        if len(args.threshold) > 1:
            print(f"  Note: {args.mode} mode uses the first threshold only: {combined_threshold}")
        if args.mode == "min":
            print(f"\n  Mode: {BOLD}min{RESET} (benchmark-like same-frame consensus)")
        else:
            print(f"\n  Mode: {BOLD}product{RESET} (multiply smoothed frame probs)")
        print(f"  Threshold: {combined_threshold}")
        print(f"  MA window: {args.ma_window} frames ({args.ma_window * FRAME_MS}ms)")
    else:
        thresholds = args.threshold
        if len(thresholds) == 1:
            thresholds = thresholds * n_models
        for m, t in zip(streaming_models, thresholds):
            m._threshold = t
            print(f"  {m.name} threshold: {t}")
        print(f"\n  Mode: {BOLD}window{RESET} (independent, {args.consensus_window_ms}ms)")

    # Log file
    log_file = None
    if args.log:
        log_path = Path(args.log)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_file = open(log_path, "a")
        log_file.write(json.dumps({
            "event": "session_start",
            "models": [m.name for m in streaming_models],
            "mode": args.mode,
            "threshold": args.threshold,
            "timestamp": datetime.now().isoformat(),
        }) + "\n")

    # Alert sound helper (reuse same alias semantics as single-model live test).
    alert_sound = (args.alert_sound or "").strip().lower()
    if alert_sound == "none":
        alert_sound = ""

    def play_alert():
        if not alert_sound:
            return

        aliases = {
            "ping": "/System/Library/Sounds/Ping.aiff",
            "pop": "/System/Library/Sounds/Pop.aiff",
            "tink": "/System/Library/Sounds/Tink.aiff",
        }
        sound_path = aliases.get(alert_sound, args.alert_sound)
        try:
            subprocess.Popen(
                ["/usr/bin/afplay", sound_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass

    # Audio setup
    frontend = MicroFrontend()
    process_fn = getattr(frontend, "process_samples", None) or getattr(frontend, "ProcessSamples", None)
    frame_samples = int(SAMPLE_RATE * FRAME_MS / 1000)
    frame_bytes = frame_samples * 2
    audio_buffer = bytearray()

    def audio_callback(indata, frames, time_info, status):
        nonlocal audio_buffer
        int16_data = (indata[:, 0] * 32768).clip(-32768, 32767).astype(np.int16)
        audio_buffer.extend(int16_data.tobytes())

    # Shared state
    detection_count = 0
    last_detection_time = 0.0
    peak_combined = 0.0
    individual_ma: dict[str, deque] = {m.name: deque(maxlen=args.ma_window) for m in streaming_models}

    # State for window mode (legacy)
    recent_detections: dict[str, float] = {}
    individual_counts: dict[str, int] = {m.name: 0 for m in streaming_models}

    print(f"\n{BOLD}Listening... say 'Kuule Kratt'!{RESET}")
    print(f"{'='*60}")

    stream_kwargs: dict = dict(
        samplerate=SAMPLE_RATE, channels=1, dtype="float32",
        blocksize=frame_samples, callback=audio_callback,
    )
    if args.device is not None:
        stream_kwargs["device"] = args.device

    with sd.InputStream(**stream_kwargs):
        try:
            while True:
                while len(audio_buffer) >= frame_bytes:
                    chunk = bytes(audio_buffer[:frame_bytes])
                    del audio_buffer[:frame_bytes]

                    result = process_fn(chunk)
                    if not result.features:
                        continue

                    features = np.array(result.features, dtype=np.float32)
                    now = time.monotonic()

                    # Get raw prob from each model on the SAME frame, then smooth
                    # per model. This mirrors benchmark FAPH combo scoring better
                    # than smoothing a product after the fact.
                    raw_probs = []
                    ma_probs = []
                    for m in streaming_models:
                        p = max(0.0, m.process_features(features.copy()))
                        raw_probs.append(p)
                        individual_ma[m.name].append(p)
                        ma_probs.append(sum(individual_ma[m.name]) / len(individual_ma[m.name]))

                    if args.mode in {"min", "product"}:
                        if args.mode == "min":
                            combined_score = min(ma_probs)
                            joiner = " ∧ "
                        else:
                            combined_score = 1.0
                            for p in ma_probs:
                                combined_score *= p
                            joiner = " × "

                        if combined_score > peak_combined:
                            peak_combined = combined_score

                        if combined_score >= combined_threshold and (now - last_detection_time) >= args.cooldown:
                            detection_count += 1
                            last_detection_time = now
                            ts = datetime.now()
                            probs_str = joiner.join(
                                f"{m.color}{m.name}={p:.3f}{RESET}"
                                for m, p in zip(streaming_models, ma_probs)
                            )
                            model_names = "+".join(m.name for m in streaming_models)
                            print(
                                f"\n  {BOLD}\033[42m >>> CONSENSUS {n_models}/{n_models}: KUULE KRATT! "
                                f"(score={combined_score:.3f}, #{detection_count}) [{model_names}] <<< {RESET}"
                                f"\n  {probs_str}\n"
                            )
                            play_alert()

                            if log_file:
                                log_file.write(json.dumps({
                                    "event": "detection",
                                    "count": detection_count,
                                    "mode": args.mode,
                                    "combined_prob": round(combined_score, 4),
                                    "individual_probs": {
                                        m.name: round(p, 4)
                                        for m, p in zip(streaming_models, ma_probs)
                                    },
                                    "timestamp": ts.isoformat(),
                                }) + "\n")
                                log_file.flush()

                    else:
                        # Legacy window mode
                        for m, ma_p in zip(streaming_models, ma_probs):
                            thr = getattr(m, "_threshold", 0.997)
                            if ma_p >= thr and (now - recent_detections.get(m.name, 0)) >= args.cooldown:
                                individual_counts[m.name] = individual_counts.get(m.name, 0) + 1
                                recent_detections[m.name] = now
                                print(f"  {m.color}>>> {m.name}: prob={ma_p:.3f} (#{individual_counts[m.name]}){RESET}")
                                if log_file:
                                    log_file.write(json.dumps({
                                        "event": "individual_detection",
                                        "model": m.name,
                                        "prob": round(ma_p, 4),
                                        "timestamp": datetime.now().isoformat(),
                                    }) + "\n")
                                    log_file.flush()

                        if (now - last_detection_time) >= args.cooldown:
                            window_s = args.consensus_window_ms / 1000.0
                            agreeing = [
                                name for name, t in recent_detections.items()
                                if (now - t) < window_s
                            ]
                            if len(agreeing) >= n_models:
                                detection_count += 1
                                last_detection_time = now
                                models_str = "+".join(agreeing)
                                print(f"\n  {BOLD}\033[42m >>> CONSENSUS {len(agreeing)}/{n_models}: KUULE KRATT! (#{detection_count}) [{models_str}] <<< {RESET}\n")
                                if log_file:
                                    log_file.write(json.dumps({
                                        "event": "consensus",
                                        "count": detection_count,
                                        "agreeing": agreeing,
                                        "timestamp": datetime.now().isoformat(),
                                    }) + "\n")
                                    log_file.flush()
                                recent_detections.clear()

                time.sleep(0.005)

        except KeyboardInterrupt:
            print(f"\n\n{'='*60}")
            print(f"{BOLD}Results:{RESET}")
            if args.mode in {"min", "product"}:
                print(f"  Mode: {args.mode}")
                print(f"  Peak combined score: {peak_combined:.4f}")
                for m in streaming_models:
                    print(f"  {m.color}■{RESET} {m.name}")
            else:
                for m in streaming_models:
                    print(f"  {m.color}■{RESET} {m.name}: {individual_counts.get(m.name, 0)} individual")
            print(f"  {BOLD}Detections: {detection_count}{RESET}")
            if log_file:
                log_file.write(json.dumps({
                    "event": "session_end",
                    "mode": args.mode,
                    "detections": detection_count,
                    "peak_combined": round(peak_combined, 4) if args.mode in {"min", "product"} else None,
                    "individual": individual_counts if args.mode == "window" else None,
                    "timestamp": datetime.now().isoformat(),
                }) + "\n")
                log_file.close()


if __name__ == "__main__":
    main()
