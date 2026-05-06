#!/usr/bin/env python3
"""Interactive shadow benchmark for many Kratt wake-word models.

Designed for demos / meetups: keep all candidate models running on one mic input,
then label short windows with one keypress. This measures unseen-speaker recall
without treating every automatic model trigger as a false accept.

Controls:
  Space / t  mark last window as TRUE wake phrase (optional)
  n          mark last window as NEGATIVE / hard-negative phrase (optional)
  f / FALSE  mark oldest pending automatic trigger as FALSE accept
  s          print running summary
  ?          print controls
  q          quit
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import re
import select
import socket
import subprocess
import sys
import termios
import threading
import time
import tty
import warnings
from collections import deque
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
warnings.filterwarnings("ignore", message=r".*tf\.lite\.Interpreter is deprecated.*")

import numpy as np
import sounddevice as sd

try:
    from pymicro_features import MicroFrontend
except ImportError:
    print("Missing pymicro_features. Run through: kratt shadow-benchmark", file=sys.stderr)
    sys.exit(1)

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    import tensorflow.lite as tflite

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
REPO_ROOT = PROJECT_ROOT.parent
SAMPLE_RATE = 16_000
FRAME_MS = 10
DEFAULT_MODELS = ["v16a", "expert-a", "v16c", "ex3a", "v6-residual"]
DEFAULT_CONTROL_SOCKET = "/tmp/kratt-shadow-benchmark.sock"
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
DIM = "\033[2m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def natural_key(value: str) -> list[object]:
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", value)]


def model_path_from_tag(tag: str) -> Path:
    return MODELS_DIR / f"kuule-kratt-{tag}" / f"kuule_kratt_{tag}.tflite"


def available_model_tags() -> list[str]:
    tags: list[str] = []
    for directory in MODELS_DIR.glob("kuule-kratt-*"):
        if not directory.is_dir():
            continue
        tag = directory.name.removeprefix("kuule-kratt-")
        if model_path_from_tag(tag).exists():
            tags.append(tag)
    return sorted(tags, key=natural_key)


def resolve_model_tag(tag: str) -> tuple[str, Path]:
    tag = tag.removeprefix("kuule-kratt-")
    tag = MODEL_ALIASES.get(tag, tag)

    exact = model_path_from_tag(tag)
    if exact.exists():
        return tag, exact

    matches = [candidate for candidate in available_model_tags() if candidate.startswith(tag)]
    if len(matches) == 1:
        resolved = matches[0]
        return resolved, model_path_from_tag(resolved)
    if len(matches) > 1:
        raise ValueError(f"Ambiguous model alias {tag!r}: {', '.join(matches)}")
    raise ValueError(f"Model not found: {tag}")


class StreamingModel:
    def __init__(self, tag: str, tflite_path: Path, threshold: float, color: str):
        self.tag = tag
        self.threshold = threshold
        self.color = color
        self.interpreter = tflite.Interpreter(model_path=str(tflite_path))
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.audio_input_idx = 0
        self.frame_count = 0
        self.warmup_frames = 50

        for detail in self.input_details:
            self.interpreter.set_tensor(
                detail["index"], np.zeros(detail["shape"], dtype=detail["dtype"])
            )

    def process_features(self, features: np.ndarray) -> float:
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


@contextmanager
def raw_terminal(enabled: bool):
    if not enabled or not sys.stdin.isatty():
        yield False
        return
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        yield True
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def read_key() -> str | None:
    if not sys.stdin.isatty():
        return None
    ready, _, _ = select.select([sys.stdin], [], [], 0)
    if not ready:
        return None
    ch = sys.stdin.read(1)
    if ch == "\x03":
        raise KeyboardInterrupt
    return ch


def append_jsonl(path: Path | None, record: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def play_alert(sound: str) -> None:
    sound = (sound or "").strip().lower()
    if not sound or sound == "none":
        return
    aliases = {
        "ping": "/System/Library/Sounds/Ping.aiff",
        "pop": "/System/Library/Sounds/Pop.aiff",
        "tink": "/System/Library/Sounds/Tink.aiff",
    }
    sound_path = aliases.get(sound, sound)
    try:
        subprocess.Popen(
            ["/usr/bin/afplay", sound_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def terminal_width(default: int = 100) -> int:
    try:
        return os.get_terminal_size().columns
    except OSError:
        return default


def print_help() -> None:
    print()
    print(f"{BOLD}Controls{RESET}")
    print("  Space / t  = label last window TRUE wake phrase (optional recall trial)")
    print("  n          = label last window NEGATIVE / hard-negative phrase (optional)")
    print("  f / FALSE  = mark oldest pending automatic trigger as FALSE accept")
    print("  s          = print running summary")
    print("  ?          = help")
    print("  q          = quit")
    print()


def summarize_window(
    frame_ring: deque[dict[str, Any]],
    models: list[StreamingModel],
    now: float,
    window_s: float,
) -> dict[str, dict[str, Any]]:
    start = now - window_s
    frames = [frame for frame in frame_ring if frame["t_mono"] >= start]
    summary: dict[str, dict[str, Any]] = {}
    for model in models:
        vals = [(frame["t_mono"], frame["probs"].get(model.tag, 0.0)) for frame in frames]
        if not vals:
            summary[model.tag] = {
                "peak": 0.0,
                "hit": False,
                "first_hit_age_ms": None,
                "threshold": model.threshold,
            }
            continue
        peak = max(prob for _, prob in vals)
        first_hit = next((t for t, prob in vals if prob >= model.threshold), None)
        summary[model.tag] = {
            "peak": round(float(peak), 4),
            "hit": bool(peak >= model.threshold),
            "first_hit_age_ms": int((first_hit - now) * 1000) if first_hit is not None else None,
            "threshold": model.threshold,
        }
    return summary


def print_trial_table(
    trial_id: int,
    label: str,
    model_summary: dict[str, dict[str, Any]],
    models: list[StreamingModel],
) -> None:
    expected = label == "true_wake"
    title = "TRUE WAKE" if expected else "NEGATIVE"
    color = GREEN if expected else YELLOW
    print()
    print(f"{color}{BOLD}Trial {trial_id:03d}: {title}{RESET}")
    print("┌────────────────────────────────────────────┬────────┬───────┬────────────┐")
    print("│ model                                      │ peak   │ hit   │ hit age    │")
    print("├────────────────────────────────────────────┼────────┼───────┼────────────┤")
    for model in models:
        row = model_summary[model.tag]
        hit = row["hit"]
        if expected:
            status = f"{GREEN}YES{RESET}" if hit else f"{RED}MISS{RESET}"
        else:
            status = f"{RED}FA{RESET}" if hit else f"{GREEN}ok{RESET}"
        age = row["first_hit_age_ms"]
        age_s = "—" if age is None else f"{age / 1000:+.2f}s"
        name = f"{model.color}{model.tag}{RESET}"
        print(f"│ {name:<53} │ {row['peak']:<6.3f} │ {status:<13} │ {age_s:<10} │")
    print("└────────────────────────────────────────────┴────────┴───────┴────────────┘")


def print_summary(stats: dict[str, dict[str, int]], models: list[StreamingModel]) -> None:
    print()
    print(f"{BOLD}Running summary{RESET}")
    print("┌────────────────────────────────────────────┬──────────────┬──────────────┬──────────────┐")
    print("│ model                                      │ recall       │ neg FA       │ manual FA    │")
    print("├────────────────────────────────────────────┼──────────────┼──────────────┼──────────────┤")
    for model in models:
        s = stats[model.tag]
        pos_total = s["pos_total"]
        pos_hit = s["pos_hit"]
        neg_total = s["neg_total"]
        neg_hit = s["neg_hit"]
        manual_fa = s["manual_false_accept"]
        recall = "—" if pos_total == 0 else f"{pos_hit}/{pos_total} ({100 * pos_hit / pos_total:.0f}%)"
        neg = "—" if neg_total == 0 else f"{neg_hit}/{neg_total} ({100 * neg_hit / neg_total:.0f}%)"
        name = f"{model.color}{model.tag}{RESET}"
        print(f"│ {name:<53} │ {recall:<12} │ {neg:<12} │ {manual_fa:<12} │")
    print("└────────────────────────────────────────────┴──────────────┴──────────────┴──────────────┘")
    print()


def update_stats(stats: dict[str, dict[str, int]], label: str, model_summary: dict[str, dict[str, Any]]) -> None:
    for tag, row in model_summary.items():
        if label == "true_wake":
            stats[tag]["pos_total"] += 1
            if row["hit"]:
                stats[tag]["pos_hit"] += 1
        elif label == "negative":
            stats[tag]["neg_total"] += 1
            if row["hit"]:
                stats[tag]["neg_hit"] += 1


def undo_true_stats(stats: dict[str, dict[str, int]], model_summary: dict[str, dict[str, Any]]) -> None:
    for tag, row in model_summary.items():
        if tag not in stats:
            continue
        stats[tag]["pos_total"] = max(0, stats[tag]["pos_total"] - 1)
        if row.get("hit"):
            stats[tag]["pos_hit"] = max(0, stats[tag]["pos_hit"] - 1)


def start_control_socket(path: str, commands: "queue.Queue[str]") -> tuple[socket.socket, Path]:
    """Start a tiny one-command Unix socket: send 'FALSE' to mark false accept."""
    sock_path = Path(path).expanduser()
    sock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        sock_path.unlink()
    except FileNotFoundError:
        pass

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(str(sock_path))
    server.listen(4)
    server.settimeout(0.25)

    def run() -> None:
        while True:
            try:
                conn, _ = server.accept()
            except socket.timeout:
                continue
            except OSError:
                return
            with conn:
                try:
                    data = conn.recv(1024).decode("utf-8", errors="ignore").strip().upper()
                    if data == "FALSE":
                        commands.put("FALSE")
                        conn.sendall(b"OK FALSE\n")
                    else:
                        conn.sendall(b"ERR expected FALSE\n")
                except OSError:
                    pass

    threading.Thread(target=run, daemon=True, name="kratt-shadow-control").start()
    return server, sock_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Live shadow benchmark for Kratt wake-word models")
    parser.add_argument("models", nargs="*", default=DEFAULT_MODELS, help="Model tags. Default: frozen replay set subset")
    parser.add_argument("--threshold", type=float, nargs="+", default=[0.996], help="One threshold for all, or one per model. Default: 0.996")
    parser.add_argument("--window-s", type=float, default=3.0, help="Seconds before keypress to score as one labelled trial. Default: 3.0")
    parser.add_argument("--ma-window", type=int, default=5, help="Moving-average frames. Default: 5")
    parser.add_argument("--cooldown", type=float, default=1.5, help="Per-model auto-trigger cooldown seconds. Default: 1.5")
    parser.add_argument("--device", type=int, default=None, help="sounddevice input device id")
    parser.add_argument("--log", type=str, default=None, help="JSONL log path")
    parser.add_argument("--control-socket", default=DEFAULT_CONTROL_SOCKET, help=f"Unix socket for global false-accept shortcut. Default: {DEFAULT_CONTROL_SOCKET}")
    parser.add_argument("--alert-sound", default="none", help="Sound for automatic triggers: none|ping|pop|tink|path")
    parser.add_argument("--no-keys", action="store_true", help="Disable raw keyboard controls; print only automatic triggers")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    resolved: list[tuple[str, Path]] = []
    for requested in args.models:
        try:
            resolved.append(resolve_model_tag(requested))
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            print("\nAvailable models:", file=sys.stderr)
            for tag in available_model_tags():
                print(f"  {tag}", file=sys.stderr)
            raise SystemExit(2)

    thresholds = list(args.threshold)
    if len(thresholds) == 1:
        thresholds = thresholds * len(resolved)
    if len(thresholds) != len(resolved):
        raise SystemExit(f"{len(thresholds)} thresholds for {len(resolved)} models")

    models: list[StreamingModel] = []
    print(f"{BOLD}Kratt live shadow benchmark{RESET}")
    print("Models:")
    for i, ((tag, path), threshold) in enumerate(zip(resolved, thresholds)):
        color = COLORS[i % len(COLORS)]
        model = StreamingModel(tag, path, threshold, color)
        models.append(model)
        print(f"  {color}■{RESET} {tag:<38} threshold={threshold}")

    log_path = Path(args.log).expanduser().resolve() if args.log else None
    control_queue: queue.Queue[str] = queue.Queue()
    control_server: socket.socket | None = None
    control_socket_path: Path | None = None
    if args.control_socket:
        control_server, control_socket_path = start_control_socket(args.control_socket, control_queue)

    append_jsonl(log_path, {
        "event": "session_start",
        "timestamp": iso_now(),
        "models": [m.tag for m in models],
        "thresholds": {m.tag: m.threshold for m in models},
        "window_s": args.window_s,
        "ma_window": args.ma_window,
        "device": args.device,
        "control_socket": str(control_socket_path) if control_socket_path else None,
    })
    if log_path:
        print(f"Log: {log_path}")
    if control_socket_path:
        print(f"Control socket: {control_socket_path}  {DIM}(send: FALSE){RESET}")

    print_help()
    print(f"{BOLD}Listening continuously.{RESET} Ask someone to say “Kuule Kratt”, then press Space.")

    frontend = MicroFrontend()
    process_fn = getattr(frontend, "process_samples", None) or getattr(frontend, "ProcessSamples", None)
    frame_samples = int(SAMPLE_RATE * FRAME_MS / 1000)
    frame_bytes = frame_samples * 2
    audio_buffer = bytearray()
    max_ring_frames = int(max(args.window_s + 1.0, 5.0) * 1000 / FRAME_MS)
    frame_ring: deque[dict[str, Any]] = deque(maxlen=max_ring_frames)
    ma: dict[str, deque[float]] = {model.tag: deque(maxlen=args.ma_window) for model in models}
    last_model_trigger: dict[str, float] = {model.tag: 0.0 for model in models}
    trigger_seq = 0
    pending_triggers: deque[dict[str, Any]] = deque()
    trial_seq = 0
    stats: dict[str, dict[str, int]] = {
        model.tag: {"pos_total": 0, "pos_hit": 0, "neg_total": 0, "neg_hit": 0, "manual_false_accept": 0}
        for model in models
    }

    def mark_next_false(source: str) -> None:
        if not pending_triggers:
            print(f"\n{YELLOW}FALSE received ({source}), but the pending trigger backlog is empty.{RESET}")
            append_jsonl(log_path, {"event": "false_label_without_trigger", "source": source, "timestamp": iso_now()})
            return
        trigger = pending_triggers.popleft()
        trigger["reviewed"] = True
        trigger["review_label"] = "false_accept"
        trigger["review_source"] = source
        trigger["review_timestamp"] = iso_now()
        undo_true_stats(stats, trigger.get("models", {}))
        for tag in trigger["triggering_models"]:
            if tag in stats:
                stats[tag]["manual_false_accept"] += 1
        append_jsonl(log_path, {"event": "trigger_label", **trigger})
        print(f"\n{RED}{BOLD}Marked auto trigger #{trigger['trigger_id']} as FALSE accept ({source}):{RESET} {', '.join(trigger['triggering_models'])}")
        print(f"{DIM}Pending assumed-true trigger backlog: {len(pending_triggers)}{RESET}")
        print_summary(stats, models)

    def audio_callback(indata, frames, time_info, status):
        nonlocal audio_buffer
        int16 = (indata[:, 0] * 32768).clip(-32768, 32767).astype(np.int16)
        audio_buffer.extend(int16.tobytes())

    stream_kwargs: dict[str, Any] = {
        "samplerate": SAMPLE_RATE,
        "channels": 1,
        "dtype": "float32",
        "blocksize": frame_samples,
        "callback": audio_callback,
    }
    if args.device is not None:
        stream_kwargs["device"] = args.device

    keys_enabled = not args.no_keys and sys.stdin.isatty()
    if not keys_enabled:
        print(f"{YELLOW}Keyboard controls disabled (stdin is not a TTY or --no-keys).{RESET}")

    try:
        with raw_terminal(keys_enabled), sd.InputStream(**stream_kwargs):
            while True:
                # Process all queued audio frames.
                while len(audio_buffer) >= frame_bytes:
                    chunk = bytes(audio_buffer[:frame_bytes])
                    del audio_buffer[:frame_bytes]
                    result = process_fn(chunk)
                    if not result.features:
                        continue
                    features = np.array(result.features, dtype=np.float32)
                    now = time.monotonic()
                    probs: dict[str, float] = {}
                    triggering: list[str] = []
                    for model in models:
                        raw_p = max(0.0, model.process_features(features.copy()))
                        ma[model.tag].append(raw_p)
                        smoothed = sum(ma[model.tag]) / max(len(ma[model.tag]), 1)
                        probs[model.tag] = smoothed
                        if smoothed >= model.threshold and (now - last_model_trigger[model.tag]) >= args.cooldown:
                            triggering.append(model.tag)
                            last_model_trigger[model.tag] = now

                    frame_ring.append({"t_mono": now, "timestamp": iso_now(), "probs": probs})

                    if triggering:
                        trigger_seq += 1
                        trial_seq += 1
                        model_summary = summarize_window(frame_ring, models, now, args.window_s)
                        update_stats(stats, "true_wake", model_summary)
                        confidence = "suspect_single_model" if len(triggering) == 1 else "multi_model"
                        trigger = {
                            "trigger_id": trigger_seq,
                            "trial_id": trial_seq,
                            "timestamp": iso_now(),
                            "t_mono": now,
                            "label": "true_wake",
                            "expected_wake": True,
                            "source": "auto_trigger_assumed_true",
                            "confidence": confidence,
                            "triggering_models": triggering,
                            "probs": {tag: round(probs[tag], 4) for tag in probs},
                            "window_s": args.window_s,
                            "models": model_summary,
                            "reviewed": False,
                        }
                        pending_triggers.append(trigger)
                        append_jsonl(log_path, {"event": "model_trigger_assumed_true", **trigger})
                        append_jsonl(log_path, {"event": "trial", **trigger})
                        model_list = ", ".join(triggering)
                        all_scores = " ".join(
                            f"{model.color}{model.tag}={probs[model.tag]:.3f}{'✓' if probs[model.tag] >= model.threshold else '·'}{RESET}"
                            for model in models
                        )
                        prefix = f"{YELLOW}auto trigger #{trigger_seq} SUSPECT single-model assumed TRUE" if len(triggering) == 1 else f"{GREEN}auto trigger #{trigger_seq} assumed TRUE"
                        print(f"\n{prefix}:{RESET} {model_list}")
                        print(f"  {all_scores}")
                        print(f"{DIM}If fake, send FALSE via Raycast or press f. Pending backlog: {len(pending_triggers)}{RESET}")
                        play_alert(args.alert_sound)

                while True:
                    try:
                        command = control_queue.get_nowait()
                    except queue.Empty:
                        break
                    if command == "FALSE":
                        mark_next_false("socket")

                key = read_key() if keys_enabled else None
                if key:
                    key_lower = key.lower()
                    if key in {" ", "\r", "\n"} or key_lower == "t":
                        trial_seq += 1
                        now = time.monotonic()
                        model_summary = summarize_window(frame_ring, models, now, args.window_s)
                        update_stats(stats, "true_wake", model_summary)
                        record = {
                            "event": "trial",
                            "trial_id": trial_seq,
                            "label": "true_wake",
                            "expected_wake": True,
                            "timestamp": iso_now(),
                            "window_s": args.window_s,
                            "models": model_summary,
                        }
                        append_jsonl(log_path, record)
                        print_trial_table(trial_seq, "true_wake", model_summary, models)
                        print_summary(stats, models)
                    elif key_lower == "n":
                        trial_seq += 1
                        now = time.monotonic()
                        model_summary = summarize_window(frame_ring, models, now, args.window_s)
                        update_stats(stats, "negative", model_summary)
                        record = {
                            "event": "trial",
                            "trial_id": trial_seq,
                            "label": "negative",
                            "expected_wake": False,
                            "timestamp": iso_now(),
                            "window_s": args.window_s,
                            "models": model_summary,
                        }
                        append_jsonl(log_path, record)
                        print_trial_table(trial_seq, "negative", model_summary, models)
                        print_summary(stats, models)
                    elif key_lower == "f":
                        mark_next_false("keyboard")
                    elif key_lower == "s":
                        print_summary(stats, models)
                    elif key_lower == "?":
                        print_help()
                    elif key_lower == "q":
                        raise KeyboardInterrupt

                time.sleep(0.003)
    except KeyboardInterrupt:
        print("\nStopping shadow benchmark.")
    finally:
        append_jsonl(log_path, {
            "event": "session_end",
            "timestamp": iso_now(),
            "trials": trial_seq,
            "auto_triggers": trigger_seq,
            "pending_assumed_true_backlog": len(pending_triggers),
            "summary": stats,
        })
        print_summary(stats, models)
        if control_server is not None:
            control_server.close()
        if control_socket_path is not None:
            try:
                control_socket_path.unlink()
            except FileNotFoundError:
                pass
        if log_path:
            print(f"Saved JSONL: {log_path}")


if __name__ == "__main__":
    main()
