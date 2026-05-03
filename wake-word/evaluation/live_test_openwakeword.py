#!/usr/bin/env python3
"""Live microphone test for a custom openWakeWord ONNX model.

This bypasses openWakeWord.Model.predict() for long-window custom models where
cold-start feature buffers may be shorter than the ONNX input shape.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import threading
import time
import wave
from datetime import datetime
from pathlib import Path

import numpy as np
from openwakeword import Model as OpenWakeWordModel

FRAME = 1280  # openWakeWord frame: 80 ms at 16 kHz


def chunks(audio: np.ndarray):
    for start in range(0, len(audio), FRAME):
        chunk = audio[start:start + FRAME]
        if len(chunk) < FRAME:
            chunk = np.pad(chunk, (0, FRAME - len(chunk)))
        yield chunk


def model_key(model: OpenWakeWordModel, model_path: Path) -> str:
    stem = model_path.stem
    keys = list(model.models.keys())
    if stem in keys:
        return stem
    return keys[0] if keys else stem


def predict_safe(model: OpenWakeWordModel, key: str, chunk: np.ndarray) -> float:
    model.preprocessor(chunk)
    n_frames = int(model.model_inputs[key])
    if model.preprocessor.feature_buffer.shape[0] < n_frames:
        return 0.0
    x = model.preprocessor.get_features(n_frames)
    sess = model.models[key]
    y = sess.run(None, {sess.get_inputs()[0].name: x})[0]
    return float(np.asarray(y).reshape(-1)[0])


def write_wav(path: Path, pcm: np.ndarray, sample_rate: int = 16000) -> None:
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.astype(np.int16, copy=False).tobytes())


def main() -> None:
    parser = argparse.ArgumentParser(description="Live openWakeWord ONNX wake-word test")
    parser.add_argument("--model", required=True, type=Path, help="Path to custom .onnx model")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--cooldown", type=float, default=2.0)
    parser.add_argument("--device", default=None)
    parser.add_argument("--name", default=None)
    parser.add_argument("--capture-dir", default=None)
    parser.add_argument("--pre-roll-seconds", type=float, default=5.0)
    parser.add_argument("--post-roll-seconds", type=float, default=1.0)
    parser.add_argument("--alert-sound", default="ping")
    args = parser.parse_args()

    try:
        import sounddevice as sd
    except ImportError:
        print("Install sounddevice: pip install sounddevice", file=sys.stderr)
        raise

    name = args.name or args.model.stem
    print(f"Loading openWakeWord ONNX: {args.model}")
    model = OpenWakeWordModel(wakeword_models=[str(args.model)])
    key = model_key(model, args.model)
    n_frames = int(model.model_inputs[key])
    warm_seconds = max(7.0, (n_frames + 10) * FRAME / args.sample_rate)
    print(f"Prediction key: {key}; input frames={n_frames}; warm-up={warm_seconds:.1f}s")

    # Warm context with silence so short spoken phrases are not penalized by cold start.
    for chunk in chunks(np.zeros(int(warm_seconds * args.sample_rate), dtype=np.int16)):
        predict_safe(model, key, chunk)

    pre_roll_samples = int(args.pre_roll_seconds * args.sample_rate)
    post_roll_samples = int(args.post_roll_seconds * args.sample_rate)
    rolling = np.zeros(max(pre_roll_samples, 1), dtype=np.int16)
    rolling_len = 0
    rolling_pos = 0
    pending_capture = None
    capture_dir = Path(args.capture_dir).expanduser().resolve() if args.capture_dir else None

    audio_buffer = bytearray()
    lock = threading.Lock()

    def append_rolling(samples: np.ndarray) -> None:
        nonlocal rolling_len, rolling_pos
        if samples.size == 0:
            return
        cap = rolling.size
        if samples.size >= cap:
            rolling[:] = samples[-cap:]
            rolling_len = cap
            rolling_pos = 0
            return
        first = min(cap - rolling_pos, samples.size)
        rolling[rolling_pos:rolling_pos + first] = samples[:first]
        second = samples.size - first
        if second:
            rolling[:second] = samples[first:]
        rolling_pos = (rolling_pos + samples.size) % cap
        rolling_len = min(cap, rolling_len + samples.size)

    def read_rolling() -> np.ndarray:
        if rolling_len <= 0 or pre_roll_samples <= 0:
            return np.array([], dtype=np.int16)
        if rolling_len < rolling.size:
            return rolling[:rolling_len].copy()
        if rolling_pos == 0:
            return rolling.copy()
        return np.concatenate((rolling[rolling_pos:], rolling[:rolling_pos]))

    def finalize_capture(state: dict) -> None:
        if capture_dir is None:
            return
        capture_dir.mkdir(parents=True, exist_ok=True)
        post = np.concatenate(state["post"]) if state["post"] else np.array([], dtype=np.int16)
        pcm = np.concatenate([state["pre"], post]) if state["pre"].size else post
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe = name.replace(" ", "_")
        out = capture_dir / f"{stamp}_{safe}_p{state['prob']:.3f}_c{state['count']}.wav"
        write_wav(out, pcm, args.sample_rate)
        print(f"  [saved] {out}")

    def play_alert() -> None:
        sound = (args.alert_sound or "").strip().lower()
        if not sound or sound == "none":
            return
        aliases = {
            "ping": "/System/Library/Sounds/Ping.aiff",
            "pop": "/System/Library/Sounds/Pop.aiff",
            "tink": "/System/Library/Sounds/Tink.aiff",
        }
        try:
            subprocess.Popen(["/usr/bin/afplay", aliases.get(sound, args.alert_sound)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def callback(indata, frames, time_info, status):
        nonlocal pending_capture
        if status:
            print(f"  [audio status: {status}]", file=sys.stderr)
        pcm = (indata[:, 0] * 32768).clip(-32768, 32767).astype(np.int16)
        with lock:
            audio_buffer.extend(pcm.tobytes())
            append_rolling(pcm)
            if pending_capture is not None and pending_capture["remaining"] > 0:
                take = min(pending_capture["remaining"], pcm.size)
                if take:
                    pending_capture["post"].append(pcm[:take].copy())
                    pending_capture["remaining"] -= take

    blocksize = FRAME
    stream_kwargs = {
        "samplerate": args.sample_rate,
        "channels": 1,
        "dtype": "float32",
        "blocksize": blocksize,
        "callback": callback,
    }
    if args.device is not None:
        stream_kwargs["device"] = int(args.device) if str(args.device).isdigit() else args.device

    print(f"Model: {name}, threshold={args.threshold}, cooldown={args.cooldown}s")
    if capture_dir:
        print(f"Capture dir: {capture_dir}")
    print("Listening... Ctrl+C to stop")

    last_detection = 0.0
    detection_count = 0
    frame_count = 0
    started = time.time()

    try:
        with sd.InputStream(**stream_kwargs):
            while True:
                with lock:
                    n = len(audio_buffer) // 2
                    if n >= FRAME:
                        raw = audio_buffer[:FRAME * 2]
                        del audio_buffer[:FRAME * 2]
                        done = None
                        if pending_capture is not None and pending_capture["remaining"] <= 0:
                            done = pending_capture
                            pending_capture = None
                    else:
                        raw = None
                        done = None
                if done is not None:
                    finalize_capture(done)
                if raw is None:
                    time.sleep(0.005)
                    continue
                chunk = np.frombuffer(raw, dtype=np.int16).copy()
                prob = predict_safe(model, key, chunk)
                frame_count += 1
                now = time.time()
                if frame_count % 10 == 0:
                    print(f"\rprob={prob:.4f} max? listening {now-started:.0f}s", end="", flush=True)
                if prob >= args.threshold and (now - last_detection) >= args.cooldown:
                    detection_count += 1
                    last_detection = now
                    elapsed_h = max((now - started) / 3600.0, 1e-9)
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] DETECT #{detection_count}: {prob:.4f} FAPH~{detection_count/elapsed_h:.1f}")
                    play_alert()
                    if capture_dir is not None:
                        with lock:
                            pending_capture = {
                                "pre": read_rolling(),
                                "post": [],
                                "remaining": post_roll_samples,
                                "prob": prob,
                                "count": detection_count,
                            }
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
