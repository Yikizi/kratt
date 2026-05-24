#!/usr/bin/env python3
"""Live microphone test for a microWakeWord TFLite model.

Usage:
    python live_test_tflite.py --model path/to/model.tflite [--threshold 0.5]

Press Ctrl+C to stop.
"""

import argparse
import contextlib
import json
import os
import select
import subprocess
import sys
import termios
import threading
import time
import tty
import wave
import warnings
from datetime import datetime
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
warnings.filterwarnings("ignore", message=r".*tf\.lite\.Interpreter is deprecated.*")

import numpy as np

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    import tensorflow.lite as tflite


def make_interpreter(model_path: str):
    interp = tflite.Interpreter(model_path=model_path)
    interp.allocate_tensors()
    return interp


def main():
    parser = argparse.ArgumentParser(description="Live wake-word test")
    parser.add_argument("--model", required=True, help="Path to .tflite model")
    parser.add_argument("--threshold", type=float, default=0.5, help="Detection threshold")
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--device", type=int, default=None, help="Input device ID for sounddevice")
    parser.add_argument("--frame-ms", type=int, default=10, help="Frame size in ms (match model step_ms)")
    parser.add_argument("--cooldown", type=float, default=2.0, help="Seconds to suppress after a detection")
    parser.add_argument("--name", default=None, help="Wake word name for display (auto-detected from model path)")
    parser.add_argument("--capture-dir", default=None, help="Directory to save detection audio snippets (disabled when unset)")
    parser.add_argument("--mining-dir", default=None, help="Directory for live mining. Detections default to false-positive; press SPACE within --label-window-seconds to mark true-positive. SPACE without a pending detection saves missed-positive audio from the rolling buffer.")
    parser.add_argument("--label-window-seconds", type=float, default=2.0, help="Seconds after a detection to allow SPACE=true-positive labeling in --mining-dir mode")
    parser.add_argument("--duration-hours", type=float, default=0.0, help="Stop after N hours (default: 0 = until Ctrl+C)")
    parser.add_argument("--pre-roll-seconds", type=float, default=5.0, help="Seconds of audio before detection to keep in RAM")
    parser.add_argument("--post-roll-seconds", type=float, default=1.0, help="Seconds of audio after detection to include in saved snippet")
    parser.add_argument("--alert-sound", default="", help="Sound alias (ping|pop|tink|none) or path to .wav/.aiff/.m4a to play on detection")
    parser.add_argument("--verbose", action="store_true", help="Print model path and tensor details")
    args = parser.parse_args()

    alert_sound = (args.alert_sound or "").strip().lower()
    if alert_sound == "none":
        alert_sound = ""

    if args.pre_roll_seconds < 0:
        parser.error("--pre-roll-seconds must be >= 0")
    if args.post_roll_seconds < 0:
        parser.error("--post-roll-seconds must be >= 0")
    if args.label_window_seconds < 0:
        parser.error("--label-window-seconds must be >= 0")
    if args.duration_hours < 0:
        parser.error("--duration-hours must be >= 0")

    if args.name is None:
        args.name = Path(args.model).stem.replace("_", " ")

    try:
        import sounddevice as sd
    except ImportError:
        print("Install sounddevice: pip install sounddevice")
        sys.exit(1)

    try:
        from pymicro_features import MicroFrontend
    except ImportError:
        print("Install pymicro-features: pip install 'git+https://github.com/puddly/pymicro-features@puddly/minimum-cpp-version'")
        sys.exit(1)

    interpreter = make_interpreter(args.model)
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    pre_roll_samples = int(args.pre_roll_seconds * args.sample_rate)
    post_roll_samples = int(args.post_roll_seconds * args.sample_rate)
    rolling_buffer = np.zeros(max(pre_roll_samples, 1), dtype=np.int16)
    rolling_len = 0
    rolling_pos = 0

    mining_dir = Path(args.mining_dir).expanduser().resolve() if args.mining_dir else None
    capture_dir = Path(args.capture_dir).expanduser().resolve() if args.capture_dir else mining_dir
    pending_capture = None

    audio_buffer = bytearray()
    audio_lock = threading.Lock()

    def append_to_rolling_locked(samples: np.ndarray):
        nonlocal rolling_len, rolling_pos
        if samples.size == 0:
            return

        cap = rolling_buffer.size
        n = samples.size

        if n >= cap:
            rolling_buffer[:] = samples[-cap:]
            rolling_len = cap
            rolling_pos = 0
            return

        first = min(cap - rolling_pos, n)
        rolling_buffer[rolling_pos:rolling_pos + first] = samples[:first]
        second = n - first
        if second > 0:
            rolling_buffer[:second] = samples[first:]

        rolling_pos = (rolling_pos + n) % cap
        rolling_len = min(cap, rolling_len + n)

    def read_rolling_locked() -> np.ndarray:
        if pre_roll_samples <= 0 or rolling_len <= 0:
            return np.array([], dtype=np.int16)

        cap = rolling_buffer.size
        if rolling_len < cap:
            return rolling_buffer[:rolling_len].copy()
        if rolling_pos == 0:
            return rolling_buffer.copy()
        return np.concatenate((rolling_buffer[rolling_pos:], rolling_buffer[:rolling_pos]))

    def write_wav(path: Path, pcm: np.ndarray):
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(args.sample_rate)
            wf.writeframes(pcm.astype(np.int16, copy=False).tobytes())

    def append_mining_event(event: dict):
        if mining_dir is None:
            return
        mining_dir.mkdir(parents=True, exist_ok=True)
        event = {"time": datetime.now().isoformat(timespec="seconds"), **event}
        with (mining_dir / "events.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def finalize_capture(capture_state):
        if capture_dir is None:
            return

        label = capture_state.get("label", "capture")
        out_root = capture_dir / label if mining_dir is not None else capture_dir
        out_root.mkdir(parents=True, exist_ok=True)

        pre = capture_state["pre"]
        post_parts = capture_state["post"]
        post = np.concatenate(post_parts) if post_parts else np.array([], dtype=np.int16)

        if pre.size and post.size:
            pcm = np.concatenate([pre, post])
        elif pre.size:
            pcm = pre
        else:
            pcm = post

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_name = args.name.replace(" ", "_")
        out_path = out_root / f"{stamp}_{safe_name}_p{capture_state['prob']:.3f}_c{capture_state['count']}.wav"
        write_wav(out_path, pcm)
        print(f"  [saved:{label}] {out_path}")
        append_mining_event(
            {
                "event": "capture_saved",
                "label": label,
                "path": str(out_path),
                "prob": float(capture_state.get("prob", 0.0)),
                "count": int(capture_state.get("count", 0)),
                "samples": int(pcm.size),
                "duration_s": float(pcm.size / args.sample_rate),
                "manual": bool(capture_state.get("manual", False)),
            }
        )

    def pop_completed_capture_locked():
        nonlocal pending_capture
        if pending_capture is not None and pending_capture["remaining"] <= 0:
            deadline = pending_capture.get("label_deadline")
            if deadline is not None and time.monotonic() < deadline:
                return None
            done = pending_capture
            pending_capture = None
            return done
        return None

    def pop_pending_capture_locked():
        nonlocal pending_capture
        if pending_capture is None:
            return None
        done = pending_capture
        pending_capture = None
        return done

    def maybe_finalize_capture_now():
        if capture_dir is None:
            return
        with audio_lock:
            done = pop_completed_capture_locked()
        if done is not None:
            finalize_capture(done)

    def flush_pending_capture():
        if capture_dir is None:
            return
        with audio_lock:
            done = pop_pending_capture_locked()
        if done is not None:
            finalize_capture(done)

    class NonBlockingKeyReader:
        def __init__(self):
            self.enabled = sys.stdin.isatty()
            self.fd = sys.stdin.fileno() if self.enabled else None
            self.old_settings = None

        def __enter__(self):
            if self.enabled and self.fd is not None:
                self.old_settings = termios.tcgetattr(self.fd)
                tty.setcbreak(self.fd)
            return self

        def __exit__(self, exc_type, exc, tb):
            if self.enabled and self.old_settings is not None and self.fd is not None:
                with contextlib.suppress(Exception):
                    termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

        def read_key(self) -> str | None:
            if not self.enabled:
                return None
            ready, _, _ = select.select([sys.stdin], [], [], 0)
            if not ready:
                return None
            return sys.stdin.read(1)

    def handle_key(key: str, current_count: int):
        nonlocal pending_capture
        if mining_dir is None or key not in {" ", "p", "P", "f", "F"}:
            return
        with audio_lock:
            if pending_capture is not None:
                if key in {" ", "p", "P"}:
                    pending_capture["label"] = "true-positive"
                    pending_capture["label_deadline"] = time.monotonic()
                    print("  [label] pending capture marked true-positive")
                    append_mining_event({"event": "capture_labeled", "label": "true-positive", "count": pending_capture.get("count", 0)})
                elif key in {"f", "F"}:
                    pending_capture["label"] = "false-positive"
                    pending_capture["label_deadline"] = time.monotonic()
                    print("  [label] pending capture kept false-positive")
                    append_mining_event({"event": "capture_labeled", "label": "false-positive", "count": pending_capture.get("count", 0)})
                return
            if key in {" ", "p", "P"}:
                pre = read_rolling_locked()
            else:
                return
        if pre.size:
            finalize_capture(
                {
                    "prob": 0.0,
                    "count": current_count,
                    "pre": pre,
                    "post": [],
                    "remaining": 0,
                    "label": "missed-positive",
                    "manual": True,
                }
            )
            print("  [label] no pending detection; saved rolling buffer as missed-positive")

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

    def audio_callback(indata, frames, time_info, status):
        if status:
            print(f"  [audio status: {status}]", file=sys.stderr)

        int16_data = (indata[:, 0] * 32768).clip(-32768, 32767).astype(np.int16)

        with audio_lock:
            audio_buffer.extend(int16_data.tobytes())
            append_to_rolling_locked(int16_data)

            if pending_capture is not None and pending_capture["remaining"] > 0:
                take = min(pending_capture["remaining"], int16_data.size)
                if take > 0:
                    pending_capture["post"].append(int16_data[:take].copy())
                    pending_capture["remaining"] -= take

    # Print model info. Keep normal CLI output concise; use --verbose for tensor/debug details.
    if mining_dir is not None:
        print(f"Mining: enabled at {mining_dir}")
        print(
            "Mining keys: SPACE/p marks pending detection true-positive; "
            "SPACE with no pending detection saves missed-positive; f keeps false-positive."
        )
    if capture_dir is not None:
        print(f"Capture: enabled (pre={args.pre_roll_seconds:.1f}s, post={args.post_roll_seconds:.1f}s)")
    else:
        print("Capture: disabled")

    print(f"Alert: {alert_sound if alert_sound else 'disabled'}")
    print(f"Label: {args.name}")
    print(f"Threshold: {args.threshold}")

    if args.verbose:
        print(f"Model path: {args.model}")
        print(f"Rolling buffer RAM: {rolling_buffer.nbytes / 1024:.1f} KiB")
        print(f"Inputs: {len(input_details)}")
        for i, d in enumerate(input_details):
            print(f"  [{i}] {d['name']}: shape={d['shape']} dtype={d['dtype']}")
        print(f"Outputs: {len(output_details)}")
        for i, d in enumerate(output_details):
            print(f"  [{i}] {d['name']}: shape={d['shape']} dtype={d['dtype']}")
    print()

    # The streaming TFLite model expects one spectrogram frame at a time.
    # Each frame = 1 x num_features (typically 1 x 40).
    # State tensors are carried between invocations.
    frontend = MicroFrontend()
    process_fn = getattr(frontend, "process_samples", None) or getattr(frontend, "ProcessSamples", None)

    frame_samples = int(args.sample_rate * args.frame_ms / 1000)  # 160 samples per 10ms
    frame_bytes = frame_samples * 2  # int16

    # Identify input: the audio feature input vs state inputs
    audio_input_idx = 0  # typically index 0

    # Initialize state tensors
    for detail in input_details:
        interpreter.set_tensor(detail["index"], np.zeros(detail["shape"], dtype=detail["dtype"]))

    print(f"Listening... say {args.name}! (threshold={args.threshold})")
    print("=" * 50)

    detection_count = 0
    last_detection_time = 0.0
    frame_count = 0
    warmup_frames = 50  # ignore first ~0.5s while model state stabilizes

    stream_kwargs = dict(
        samplerate=args.sample_rate,
        channels=1,
        dtype="float32",
        blocksize=frame_samples,
        callback=audio_callback,
    )
    if args.device is not None:
        stream_kwargs["device"] = args.device

    started_at = time.monotonic()
    stop_after_s = args.duration_hours * 3600.0 if args.duration_hours > 0 else 0.0

    with sd.InputStream(**stream_kwargs), NonBlockingKeyReader() as key_reader:
        try:
            while True:
                if stop_after_s and (time.monotonic() - started_at) >= stop_after_s:
                    flush_pending_capture()
                    print(f"\n\nStopped after {args.duration_hours:.3f}h. Total detections: {detection_count}")
                    return
                key = key_reader.read_key()
                if key is not None:
                    handle_key(key, detection_count)
                while True:
                    with audio_lock:
                        if len(audio_buffer) < frame_bytes:
                            chunk = None
                        else:
                            chunk = bytes(audio_buffer[:frame_bytes])
                            del audio_buffer[:frame_bytes]

                    if chunk is None:
                        break

                    result = process_fn(chunk)
                    if not result.features:
                        continue

                    features = np.array(result.features, dtype=np.float32)
                    expected_shape = input_details[audio_input_idx]["shape"]
                    features = features.reshape(expected_shape)

                    inp_dtype = input_details[audio_input_idx]["dtype"]
                    if inp_dtype == np.int8:
                        scale, zero_point = input_details[audio_input_idx]["quantization"]
                        features = (features / scale + zero_point).clip(-128, 127).astype(np.int8)

                    interpreter.set_tensor(input_details[audio_input_idx]["index"], features)
                    interpreter.invoke()
                    frame_count += 1

                    if frame_count <= warmup_frames:
                        continue

                    output = interpreter.get_tensor(output_details[0]["index"])
                    out_dtype = output_details[0]["dtype"]
                    if out_dtype in (np.int8, np.uint8):
                        scale, zero_point = output_details[0]["quantization"]
                        prob_val = float(((output.astype(np.float32) - zero_point) * scale).flat[0])
                    else:
                        prob_val = float(output.flatten()[0])

                    maybe_finalize_capture_now()
                    key = key_reader.read_key()
                    if key is not None:
                        handle_key(key, detection_count)

                    now = time.monotonic()
                    in_cooldown = (now - last_detection_time) < args.cooldown

                    if prob_val > args.threshold and not in_cooldown:
                        detection_count += 1
                        last_detection_time = now
                        print(f"  >>> DETECTED {args.name}! (prob={prob_val:.3f}, count={detection_count}) <<<")
                        play_alert()

                        if capture_dir is not None:
                            with audio_lock:
                                previous = pop_pending_capture_locked()
                                pending_capture = {
                                    "prob": prob_val,
                                    "count": detection_count,
                                    "pre": read_rolling_locked(),
                                    "post": [],
                                    "remaining": post_roll_samples,
                                    "label": "false-positive" if mining_dir is not None else "capture",
                                    "label_deadline": (time.monotonic() + args.label_window_seconds) if mining_dir is not None else None,
                                }
                                immediate = pending_capture if post_roll_samples == 0 else None
                                if post_roll_samples == 0:
                                    pending_capture = None
                            if previous is not None:
                                finalize_capture(previous)
                            if immediate is not None:
                                finalize_capture(immediate)
                            if mining_dir is not None:
                                print(f"  [mine] press SPACE within {args.label_window_seconds:.1f}s if this was a real wake phrase")

                    elif prob_val > 0.1 and not in_cooldown:
                        bar = "█" * int(prob_val * 30)
                        print(f"  {prob_val:.3f} {bar}", end="\r")

                time.sleep(0.005)

        except KeyboardInterrupt:
            flush_pending_capture()
            print(f"\n\nStopped. Total detections: {detection_count}")


if __name__ == "__main__":
    main()
