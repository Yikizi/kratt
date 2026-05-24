#!/usr/bin/env python3
"""Create a guided starter workflow for a new wake-word phrase.

The wizard creates a self-contained output layout under
``output/new-wake-word/<slug>`` and writes:
- text prompt files
- STT review log
- manifest
- reproducibility documents
- smoke training plan and local checklist

It is intentionally conservative:
- no destructive overwrite of existing directories
- clear dry-run mode
- optional no-stt/no-tts paths
- minimal placeholders when recording / external services are unavailable
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import importlib.util
import json
import os
import re
import shutil
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
import textwrap
import threading
import wave

try:
    import getpass
except Exception:  # pragma: no cover - defensive for odd runtime envs
    getpass = None  # type: ignore

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover - optional for offline environments
    requests = None  # type: ignore

try:
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover - optional when ffmpeg fallback is used
    np = None  # type: ignore

try:
    import sounddevice as sd  # type: ignore
except Exception:  # pragma: no cover - optional when ffmpeg fallback is used
    sd = None  # type: ignore

try:
    import soundfile as sf  # type: ignore
except Exception:  # pragma: no cover - optional when ffmpeg fallback is used
    sf = None  # type: ignore


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output" / "new-wake-word"
WIZARD_VERSION = "0.2.0"
TRAIN_NEW_SCRIPT = PROJECT_ROOT / "wake-word" / "training" / "scripts" / "train_new_wake_word.py"
BENCHMARK_NEW_SCRIPT = PROJECT_ROOT / "wake-word" / "evaluation" / "benchmark_new_wake_word.py"
SETUP_MICROWAKEWORD_ENV_SCRIPT = PROJECT_ROOT / "wake-word" / "training" / "scripts" / "setup_microwakeword_env.sh"
MICROWAKEWORD_ENV_PYTHON = PROJECT_ROOT / "wake-word" / ".venv-microwakeword" / "bin" / "python"

REQUIRED_SAMPLE_RATE = 16000
MIN_DURATION_SECONDS = 0.4
MAX_DURATION_SECONDS = 4.0
MAX_RECORD_SECONDS = 8.0
DEFAULT_RECORD_SECONDS = 2.2

NEUROKONE_API_ENDPOINT = os.environ.get(
    "KRATT_NEUROKONE_API", "https://api.tartunlp.ai/text-to-speech/v2"
)
NEUROKONE_VOICE = os.environ.get("KRATT_NEUROKONE_VOICE", "mari")
DEFAULT_TTS_VOICES = ["albert", "indrek", "kalev", "kylli", "liivika", "mari", "meelis", "peeter", "tambet", "vesta"]
DEFAULT_TTS_SPEEDS = [0.85, 0.95, 1.0, 1.05, 1.15]
# One-shot defaults are intentionally conservative: TTS positives must not swamp
# real positives, while prefix/confusable negatives must be visible to training.
DEFAULT_TTS_POSITIVE_PER_VOICE = 2
DEFAULT_TTS_CONFUSABLE_PER_VOICE = 4
DEFAULT_NEGATIVE_CLASS_WEIGHT = "20"
DEFAULT_TTS_TIMEOUT_SECONDS = 45.0
AUDIO_EXTS = {".wav", ".flac", ".ogg", ".mp3", ".m4a"}


class ServiceStatus:
    """Simple status object for optional service checks."""

    def __init__(self) -> None:
        self.docker_available = False
        self.compose_command: str | None = None
        self.stt_port_open = False
        self.neurokone_port_open = False
        self.neurokone_api_reachable = False
        self.notes: list[str] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "docker_available": self.docker_available,
            "compose_command": self.compose_command,
            "stt_port_open": self.stt_port_open,
            "neurokone_port_open": self.neurokone_port_open,
            "neurokone_api_reachable": self.neurokone_api_reachable,
            "notes": self.notes,
        }


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(text: str) -> str:
    lowered = text.strip().lower()
    lowered = re.sub(r"[^a-z0-9äõöüšž]+", "-", lowered, flags=re.IGNORECASE)
    lowered = re.sub(r"-+", "-", lowered).strip("-")
    return lowered or "wake-word"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a diagnostic starter dataset for a new wake-word phrase.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--manifest", help="Resume an existing wizard manifest for training/benchmarking.")
    parser.add_argument("--phrase", help="Target wake phrase.")
    parser.add_argument("--slug", help="Output slug (default from phrase).")
    parser.add_argument(
        "--speaker",
        default=(os.environ.get("USER") or (getpass.getuser() if getpass else "speaker1")),
        help="Speaker label for recorded clips (default: USER or speaker1).",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of real positive recordings to collect (default: 10).",
    )
    parser.add_argument(
        "--device",
        type=int,
        default=None,
        help="Microphone device id passed to recorder (optional). For ffmpeg on macOS this is the AVFoundation audio index.",
    )
    parser.add_argument("--check", action="store_true", help="Check local onboarding prerequisites and recommended next steps, then exit.")
    parser.add_argument("--list-devices", action="store_true", help="List microphone devices and exit.")
    parser.add_argument(
        "--recorder",
        choices=["auto", "ffmpeg", "sounddevice"],
        default="auto",
        help="Recorder backend. Default: auto (prefer continuous sounddevice, fallback to ffmpeg).",
    )
    parser.add_argument(
        "--record-seconds",
        type=float,
        default=DEFAULT_RECORD_SECONDS,
        help=f"Seconds to record after START. Default: {DEFAULT_RECORD_SECONDS}. Avoids noisy/hacky manual stop.",
    )
    parser.add_argument(
        "--manual-stop",
        action="store_true",
        help="Use old START/STOP style instead of fixed-duration recording.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_DIR / "<slug>"),
        help="Output root directory (default: output/new-wake-word/<slug>).",
    )
    parser.add_argument(
        "--no-docker",
        action="store_true",
        help="Do not check or start docker services.",
    )
    parser.add_argument("--no-stt", action="store_true", help="Skip STT review.")
    parser.add_argument("--no-tts", action="store_true", help="Skip TTS generation.")
    parser.add_argument("--tts-voices", default=",".join(DEFAULT_TTS_VOICES), help="Comma-separated TTS voices for generated positives.")
    parser.add_argument("--tts-per-voice", type=int, default=DEFAULT_TTS_POSITIVE_PER_VOICE, help=f"Positive TTS clips per voice (default: {DEFAULT_TTS_POSITIVE_PER_VOICE}).")
    parser.add_argument("--tts-confusable-per-voice", type=int, default=DEFAULT_TTS_CONFUSABLE_PER_VOICE, help=f"Confusable-negative TTS clips per voice (default: {DEFAULT_TTS_CONFUSABLE_PER_VOICE}).")
    parser.add_argument("--tts-timeout", type=float, default=DEFAULT_TTS_TIMEOUT_SECONDS, help=f"Seconds before one TTS request is skipped (default: {DEFAULT_TTS_TIMEOUT_SECONDS:g}).")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without recording/generating audio.",
    )
    parser.add_argument(
        "--end-to-end",
        action="store_true",
        help="Run the full guided flow: collect data, train a local model, then benchmark it.",
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Train a local model after data collection.",
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Benchmark after training, or benchmark --model if training is skipped.",
    )
    parser.add_argument(
        "--skip-benchmark",
        action="store_true",
        help="When using --end-to-end, train but skip benchmark.",
    )
    parser.add_argument("--model", help="Existing TFLite model to benchmark in this workflow.")
    parser.add_argument("--tag", help="Model tag for local training; default: <slug>-local-<timestamp>.")
    parser.add_argument("--steps", default="1000,200", help="Training steps for local training (default: 1000,200).")
    parser.add_argument("--learning-rates", default="0.001,0.0001", help="Learning rates matching --steps.")
    parser.add_argument("--negative-class-weight", default=DEFAULT_NEGATIVE_CLASS_WEIGHT, help=f"Penalty weight for negative examples (default: {DEFAULT_NEGATIVE_CLASS_WEIGHT}).")
    parser.add_argument("--max-tts-positive-ratio", type=float, default=3.0, help="Max TTS positives per real training positive (default: 3.0; 0 disables cap).")
    parser.add_argument("--no-spec-augment", action="store_true", help="Disable SpecAugment during local one-shot training.")
    parser.add_argument("--hard-negative-mode", choices=["auto", "mixed", "separate"], default="auto", help="How to stage confusable/mined negatives for training (default: auto).")
    parser.add_argument("--hard-negative-dir", action="append", default=[], help="Extra mined/real hard-negative WAV/FLAC dir for training; can be repeated.")
    parser.add_argument("--negative-dir", help="Broad negative WAV/FLAC directory for local training.")
    parser.add_argument("--negative-limit", type=int, default=1000, help="Max broad negatives to stage (default: 1000).")
    parser.add_argument("--ambient-dir", help="Ambient WAV/FLAC directory for local training.")
    parser.add_argument("--ambient-limit", type=int, default=100, help="Max ambient clips to stage (default: 100).")
    parser.add_argument("--faph-dir", default="", help="FAPH/long negative directory for benchmark; default is the project CV ET track.")
    parser.add_argument("--faph-limit", type=int, default=100, help="Max FAPH clips for benchmark in end-to-end mode (default: 100; 0 = all).")
    parser.add_argument("--thresholds", type=float, nargs="+", default=[0.5, 0.7, 0.9, 0.95, 0.97, 0.99, 0.995], help="Benchmark thresholds.")
    parser.add_argument(
        "--local-smoke-train",
        action="store_true",
        help="Deprecated alias for generating local training plan; prefer --train or --end-to-end.",
    )
    parser.add_argument(
        "--hpc-plan",
        action="store_true",
        help="Add HPC follow-up command hints in training commands.",
    )
    parser.add_argument(
        "--fixture-audio",
        default="",
        help="Use existing WAV files as fixture positive-real input instead of live recording.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force creation under requested output (use timestamped safe variant instead of overwriting).",
    )
    parser.add_argument(
        "--force-output",
        action="store_true",
        help="Deprecated alias for --force.",
    )
    parser.add_argument("--_record-sounddevice-child", default="", help=argparse.SUPPRESS)
    parser.add_argument("--_record-child-device", type=int, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--_record-child-seconds", type=float, default=0.0, help=argparse.SUPPRESS)

    args = parser.parse_args()
    if args.count < 0:
        raise SystemExit("--count must be >= 0")
    if args.negative_limit < 1:
        raise SystemExit("--negative-limit must be >= 1")
    if args.ambient_limit < 0:
        raise SystemExit("--ambient-limit must be >= 0")
    if args.faph_limit < 0:
        raise SystemExit("--faph-limit must be >= 0")
    if args.max_tts_positive_ratio < 0:
        raise SystemExit("--max-tts-positive-ratio must be >= 0")
    if args.record_seconds <= 0 or args.record_seconds > MAX_RECORD_SECONDS:
        raise SystemExit(f"--record-seconds must be in (0, {MAX_RECORD_SECONDS}]")
    if args.tts_per_voice < 0 or args.tts_confusable_per_voice < 0:
        raise SystemExit("--tts-per-voice and --tts-confusable-per-voice must be >= 0")
    if args.tts_timeout <= 0:
        raise SystemExit("--tts-timeout must be > 0")
    try:
        if float(args.negative_class_weight) <= 0:
            raise ValueError
    except ValueError:
        raise SystemExit("--negative-class-weight must be a positive number") from None
    return args


def resolve_output_root(raw_output: str, slug: str, force: bool) -> tuple[Path, bool, bool]:
    if "<slug>" in raw_output:
        raw_output = raw_output.replace("<slug>", slug)

    out = Path(raw_output)
    if not out.is_absolute():
        out = PROJECT_ROOT / out

    used_safe = False
    existing = False
    candidate = out

    if candidate.exists():
        existing = True
        if force:
            used_safe = True
            stamped = candidate.with_name(f"{candidate.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
            candidate = stamped
        else:
            # Never overwrite existing output directory in wizard default.
            stamped = candidate.with_name(f"{candidate.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
            print(f"[guard] {candidate} already exists; using safe alternative {stamped}.")
            candidate = stamped
            used_safe = True

    return candidate, existing, used_safe


def ensure_dirs(base: Path, dry_run: bool) -> dict[str, Path]:
    dirs = {
        "base": base,
        "texts": base / "texts",
        "audio": base / "audio",
        "positive_real": base / "audio" / "positive-real",
        "positive_tts": base / "audio" / "positive-tts",
        "negative_confusable_tts": base / "audio" / "negative-confusable-tts",
        "eval_smoke": base / "audio" / "eval-smoke",
        "training": base / "training",
        "reports": base / "reports",
    }

    if not dry_run:
        for path in dirs.values():
            path.mkdir(parents=True, exist_ok=True)

    return dirs


def deduplicate_keep_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        cleaned = item.strip()
        if not cleaned:
            continue
        if cleaned in seen:
            continue
        seen.add(cleaned)
        out.append(cleaned)
    return out


def build_positive_prompts(phrase: str) -> list[str]:
    p = phrase.strip()
    words = p.split()
    variants = [
        p,
        p.lower(),
    ]
    if len(words) >= 2:
        variants.append(f"{words[0]}, {' '.join(words[1:])}")
        variants.append(f"{words[0]} {words[-1]}")
    return deduplicate_keep_order(variants)


def build_confusables(phrase: str) -> list[str]:
    words = [w for w in phrase.strip().split() if w]
    if not words:
        return []

    first = words[0]
    last = words[-1]
    # Order matters because --tts-confusable-per-voice picks the first N prompts
    # per voice. Put prefix-only and near-full-phrase traps first: these are the
    # most common one-shot failure mode for short two-word wake phrases.
    confusables: list[str] = [first, last]

    if len(words) >= 2:
        confusables.append(" ".join(reversed(words)))
        confusables.append(f"{first} Maria")
        if last.lower().endswith("a") and len(last) > 1:
            confusables.append(f"{first} {last[:-1]}ja")
            confusables.append(f"{first} {last[:-1]}ra")
        else:
            confusables.append(f"{first} {last}a")
            confusables.append(f"{first} {last}ra")
        confusables.append(f"{first} {' '.join(words[1:])} palun")
        for prefix in ("kuule", "Kuule", "hei", "Hei", "tere", "Tere"):
            confusables.append(f"{prefix} {last}")

    for template in ("{0} {1} please", "{0} , {1}"):
        confusables.append(template.format(first, last))

    # Strip accidental empties and never label the exact target phrase as a negative.
    target_norm = re.sub(r"\s+", " ", phrase.strip().lower())
    filtered = [
        item
        for item in confusables
        if re.sub(r"\s+", " ", item.strip().lower()) != target_norm
    ]
    return deduplicate_keep_order(filtered)


def write_text_list(path: Path, lines: list[str], dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def recorder_available() -> bool:
    return (sd is not None and sf is not None and np is not None) or ffmpeg_available()


def list_ffmpeg_avfoundation_audio_devices() -> list[tuple[int, str]]:
    """Return macOS AVFoundation audio devices as (index, label)."""
    if sys.platform != "darwin" or not ffmpeg_available():
        return []
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-f", "avfoundation", "-list_devices", "true", "-i", ""],
        capture_output=True,
        text=True,
        timeout=8,
    )
    devices: list[tuple[int, str]] = []
    in_audio = False
    for line in result.stderr.splitlines():
        if "AVFoundation audio devices" in line:
            in_audio = True
            continue
        if "AVFoundation video devices" in line:
            in_audio = False
            continue
        if not in_audio:
            continue
        m = re.search(r"\[(\d+)\]\s+(.+)$", line)
        if m:
            devices.append((int(m.group(1)), m.group(2).strip()))
    return devices


def print_recording_devices() -> None:
    print("Recording devices")
    if sd is not None:
        try:
            print("\nsounddevice / PortAudio:")
            devices = sd.query_devices()
            for idx, info in enumerate(devices):
                if int(info.get("max_input_channels", 0)) > 0:
                    default = " (default)" if idx == sd.default.device[0] else ""
                    print(f"  {idx}: {info.get('name')} — inputs={info.get('max_input_channels')}{default}")
        except Exception as exc:
            print(f"  sounddevice listing failed: {exc}")
    else:
        print("\nsounddevice / PortAudio: unavailable")

    if ffmpeg_available():
        print("\nffmpeg:")
        devices = list_ffmpeg_avfoundation_audio_devices()
        if devices:
            for idx, name in devices:
                print(f"  {idx}: {name}")
        elif sys.platform == "darwin":
            print("  no AVFoundation audio devices found")
        else:
            print("  use default PulseAudio/ALSA input on this platform")
    else:
        print("\nffmpeg: unavailable")


def count_audio_files(root: Path) -> int:
    if not root.exists():
        return 0
    return sum(1 for p in root.rglob("*") if p.is_file() and p.suffix.lower() in AUDIO_EXTS)


def sibling_main_project_root() -> Path | None:
    marker = "/.claude/worktrees/"
    root_s = str(PROJECT_ROOT)
    if marker not in root_s:
        return None
    candidate = Path(root_s.split(marker, 1)[0])
    return candidate if (candidate / "wake-word").exists() else None


def onboarding_data_candidates(relative: str) -> list[Path]:
    roots = [PROJECT_ROOT]
    sibling = sibling_main_project_root()
    if sibling is not None and sibling != PROJECT_ROOT:
        roots.append(sibling)
    env_root = os.environ.get("KRATT_DATA_ROOT") or os.environ.get("KRATT_SOURCE_ROOT")
    if env_root:
        roots.append(Path(env_root).expanduser())
    out: list[Path] = []
    for root in roots:
        candidate = root / relative
        if candidate not in out:
            out.append(candidate)
    return out


def first_audio_candidate(relative: str) -> tuple[Path, int]:
    candidates = onboarding_data_candidates(relative)
    best = candidates[0]
    best_count = 0
    for candidate in candidates:
        count = count_audio_files(candidate)
        if count > 0:
            return candidate, count
        if count > best_count:
            best, best_count = candidate, count
    return best, best_count


def has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def fmt_check(ok: bool | None, label: str, detail: str) -> str:
    if ok is True:
        prefix = "[ok]"
    elif ok is False:
        prefix = "[warn]"
    else:
        prefix = "[info]"
    return f"  {prefix:<6} {label:<28} {detail}"


def print_onboarding_check(args: argparse.Namespace) -> int:
    """Non-mutating environment check for first-time users."""
    print("Kratt new-wake-word onboarding check")
    print(f"Project: {PROJECT_ROOT}")
    print(f"Python:  {sys.executable} ({sys.version.split()[0]})")
    print()

    uv_bin = os.environ.get("UV") if os.environ.get("UV") and Path(os.environ["UV"]).exists() else shutil.which("uv")
    print("Core tools")
    print(fmt_check(bool(uv_bin), "uv", str(uv_bin) if uv_bin else "not on PATH; cli wrapper can install it if curl exists"))
    print(fmt_check(bool(shutil.which("git")), "git", shutil.which("git") or "needed for first microWakeWord setup"))
    print(fmt_check(bool(shutil.which("curl")), "curl", shutil.which("curl") or "needed only if uv must be installed"))
    print(fmt_check(bool(shutil.which("docker")), "docker", shutil.which("docker") or "optional; only for local STT/TTS services"))
    print(fmt_check(ffmpeg_available(), "ffmpeg", shutil.which("ffmpeg") or "optional recorder/playback fallback"))
    print()

    print("Python runtime dependencies loaded by the wrapper")
    for mod in ["numpy", "sounddevice", "soundfile", "requests", "wyoming"]:
        print(fmt_check(has_module(mod), mod, "importable" if has_module(mod) else "missing in current Python env"))
    print()

    print("Recording/playback")
    sd_ok = sd is not None and sf is not None and np is not None
    print(fmt_check(sd_ok, "sounddevice recorder", "available" if sd_ok else "unavailable; will try ffmpeg if installed"))
    print(fmt_check(ffmpeg_available(), "ffmpeg recorder", "available" if ffmpeg_available() else "unavailable"))
    playback = (sys.platform == "darwin" and shutil.which("afplay")) or shutil.which("ffplay")
    print(fmt_check(bool(playback), "clip replay", str(playback) if playback else "no afplay/ffplay found"))
    if sd_ok:
        try:
            inputs = [idx for idx, info in enumerate(sd.query_devices()) if int(info.get("max_input_channels", 0)) > 0]
            print(fmt_check(bool(inputs), "input devices", f"{len(inputs)} found; run --list-devices for names"))
        except Exception as exc:
            print(fmt_check(False, "input devices", f"listing failed: {exc}"))
    print()

    print("Optional local services")
    compose = docker_compose_cmd()
    print(fmt_check(bool(compose), "docker compose", compose or "not available; use --no-docker or remote/API TTS"))
    print(fmt_check(is_port_open("127.0.0.1", 10300), "local STT :10300", "open" if is_port_open("127.0.0.1", 10300) else "closed; STT review can be skipped with --no-stt"))
    print(fmt_check(is_port_open("127.0.0.1", 10301), "local TTS :10301", "open" if is_port_open("127.0.0.1", 10301) else "closed; wizard may use API fallback or --no-tts"))
    print()

    print("Training data available in this checkout")
    data_roots = [
        ("broad negatives", "wake-word/data/processed/negative_samples"),
        ("Korvo negatives", "wake-word/data/processed/negative_korvo2"),
        ("Mac segmented negatives", "wake-word/data/processed/negative_macbook_segmented"),
        ("ambient", "wake-word/data/processed/ambient_korvo2"),
        ("FAPH CV ET", "wake-word/data/processed/faph_test_cv_et"),
    ]
    any_neg = False
    for label, rel in data_roots:
        root, count = first_audio_candidate(rel)
        any_neg = any_neg or ("neg" in label and count > 0)
        print(fmt_check(count > 0, label, f"{count} audio files at {root}" if count else f"missing: {root}"))
    if not any_neg:
        print("  [warn] Fresh checkout has no broad speech/background negatives. Training can still smoke-test with generated non-speech negatives, but good models need --negative-dir or a prepared negative pack.")
    print()

    print("microWakeWord training environment")
    if MICROWAKEWORD_ENV_PYTHON.exists():
        print(fmt_check(True, ".venv-microwakeword", str(MICROWAKEWORD_ENV_PYTHON)))
    else:
        print(fmt_check(None, ".venv-microwakeword", "not created yet; first --train runs setup_microwakeword_env.sh"))
    local_mww = PROJECT_ROOT / "external-repos" / "microWakeWord"
    sibling = sibling_main_project_root()
    sibling_mww = sibling / "external-repos" / "microWakeWord" if sibling is not None else None
    if local_mww.exists():
        mww_detail = str(local_mww)
        mww_ok = True
    elif sibling_mww is not None and sibling_mww.exists():
        mww_detail = f"will reuse sibling checkout: {sibling_mww}"
        mww_ok = True
    else:
        mww_detail = "will be cloned on first training if git/network are available"
        mww_ok = False
    print(fmt_check(mww_ok, "microWakeWord source", mww_detail))
    try:
        usage = shutil.disk_usage(PROJECT_ROOT)
        print(fmt_check(usage.free > 12 * 1024**3, "free disk", f"{usage.free / 1024**3:.1f} GiB free"))
    except Exception as exc:
        print(fmt_check(None, "free disk", f"unknown: {exc}"))
    print()

    print("Recommended first run")
    print("  ./cli/kratt new-wake-word --list-devices")
    print("  ./cli/kratt new-wake-word --phrase \"Hei Toomas\" --count 10 --no-stt --no-tts")
    print("  ./cli/kratt new-wake-word --manifest output/new-wake-word/hei-toomas/manifest.json --train --skip-benchmark")
    print()
    print("For quality close to the current personalized demo, add real speech/background negatives:")
    print("  --negative-dir /path/to/segmented-negative-wavs --negative-limit 10000")
    return 0


def ffmpeg_input_args(device: int | None) -> tuple[list[str], str]:
    """Build ffmpeg input args for the local platform."""
    if sys.platform == "darwin":
        devices = list_ffmpeg_avfoundation_audio_devices()
        chosen = device if device is not None else (devices[0][0] if devices else 0)
        label = next((name for idx, name in devices if idx == chosen), f"avfoundation audio {chosen}")
        return ["-f", "avfoundation", "-i", f":{chosen}"], label
    if sys.platform.startswith("linux"):
        # PulseAudio is common on desktops; ALSA default works on many headless boxes.
        if shutil.which("pactl"):
            return ["-f", "pulse", "-i", "default"], "pulse default"
        return ["-f", "alsa", "-i", "default"], "alsa default"
    raise RuntimeError(f"ffmpeg recording fallback is not configured for platform: {sys.platform}")


def wav_duration_seconds(path: Path) -> float:
    try:
        with wave.open(str(path), "rb") as fh:
            frames = fh.getnframes()
            rate = fh.getframerate()
            return frames / float(rate) if rate else 0.0
    except Exception:
        return 0.0


def record_clip_ffmpeg(
    phrase: str,
    index: int,
    total: int,
    output_path: Path,
    device: int | None,
    record_seconds: float,
    manual_stop: bool,
) -> dict[str, Any]:
    if not ffmpeg_available():
        raise RuntimeError("Recording unavailable: install ffmpeg or Python sounddevice/soundfile/numpy")

    input_args, label = ffmpeg_input_args(device)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(".recording.tmp.wav")
    if tmp_path.exists():
        tmp_path.unlink()

    print(f"\nRecording {index}/{total}. Target phrase: {phrase!r}")
    print(f"  Recorder: ffmpeg ({label})")
    if manual_stop:
        print("  Press ENTER, say the phrase once, then press ENTER to stop...")
    else:
        print(f"  Press ENTER, then say the phrase once. Auto-stops after {record_seconds:.1f}s.")
    try:
        input("  START (ENTER) > ")
    except EOFError:
        raise SystemExit(
            "Interactive recording is unavailable in this environment. "
            "Use --dry-run or --fixture-audio for non-interactive use."
        )

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        *input_args,
        "-vn",
        "-ac",
        "1",
        "-ar",
        str(REQUIRED_SAMPLE_RATE),
        "-t",
        str(MAX_RECORD_SECONDS if manual_stop else record_seconds),
        str(tmp_path),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    try:
        if manual_stop:
            input("  STOP (ENTER) > ")
            if proc.stdin:
                proc.stdin.write("q\n")
                proc.stdin.flush()
            _, err = proc.communicate(timeout=5)
        else:
            print("  Recording...")
            _, err = proc.communicate(timeout=max(10, int(record_seconds) + 5))
            print("  Done.")
    except subprocess.TimeoutExpired:
        proc.terminate()
        _, err = proc.communicate(timeout=5)
    except EOFError:
        proc.terminate()
        _, err = proc.communicate(timeout=5)

    if proc.returncode not in (0, 255) and not tmp_path.exists():
        raise RuntimeError(f"ffmpeg recording failed: {(err or '').strip()}")
    if not tmp_path.exists() or tmp_path.stat().st_size == 0:
        raise RuntimeError(f"ffmpeg did not create audio. Command was: {' '.join(cmd)}. Error: {(err or '').strip()}")
    tmp_path.replace(output_path)

    duration_s = wav_duration_seconds(output_path)
    return {
        "status": "recorded",
        "path": str(output_path),
        "sample_rate": REQUIRED_SAMPLE_RATE,
        "duration_s": round(duration_s, 3),
        "duration_ok": bool(MIN_DURATION_SECONDS <= duration_s <= MAX_DURATION_SECONDS),
        "rms_db": None,
        "source": "mic-ffmpeg",
        "recorder": "ffmpeg",
        "device": label,
    }


def rms_db(audio: "np.ndarray") -> float:
    if audio.size == 0:
        return -120.0
    if np is None:
        return -120.0
    arr = audio.astype("float64")
    arr = arr.reshape(-1)
    rms = float((arr ** 2).mean() ** 0.5)
    return float(20.0 * (0.0 + __import__("math").log10(rms + 1e-10)))


def record_sounddevice_child(output_path: Path, device: int | None, record_seconds: float) -> int:
    """Record one fixed-duration clip in an isolated process.

    PortAudio/CoreAudio can occasionally hang inside native code on macOS; if
    this child blocks, the parent can kill it without losing the whole wizard.
    """
    if sd is None or sf is None or np is None:
        print("sounddevice recorder unavailable (missing sounddevice/soundfile/numpy)", file=sys.stderr)
        return 2
    frames = max(1, int(record_seconds * REQUIRED_SAMPLE_RATE))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    audio = sd.rec(
        frames,
        samplerate=REQUIRED_SAMPLE_RATE,
        channels=1,
        dtype="float32",
        device=device,
    )
    sd.wait()
    sf.write(str(output_path), np.asarray(audio).reshape(-1), REQUIRED_SAMPLE_RATE, subtype="PCM_16")
    return 0


def sounddevice_clip_metadata(output_path: Path) -> dict[str, Any]:
    if sf is None or np is None:
        raise RuntimeError("sounddevice metadata unavailable (missing soundfile/numpy)")
    audio, sr = sf.read(str(output_path), always_2d=False)
    audio_arr = np.asarray(audio, dtype="float32").reshape(-1)
    duration_s = len(audio_arr) / float(sr or REQUIRED_SAMPLE_RATE)
    duration_ok = MIN_DURATION_SECONDS <= duration_s <= MAX_DURATION_SECONDS
    level_db = rms_db(audio_arr)
    return {
        "status": "recorded",
        "path": str(output_path),
        "sample_rate": int(sr),
        "duration_s": round(duration_s, 3),
        "duration_ok": bool(duration_ok),
        "rms_db": round(level_db, 2),
        "source": "mic-sounddevice",
        "recorder": "sounddevice",
    }


def record_clip_sounddevice(
    phrase: str,
    index: int,
    total: int,
    output_path: Path,
    device: int | None,
    record_seconds: float,
    manual_stop: bool,
) -> dict[str, Any]:
    if sd is None or sf is None or np is None:
        raise RuntimeError("sounddevice recorder unavailable (missing sounddevice/soundfile/numpy)")

    print(f"\nRecording {index}/{total}. Target phrase: {phrase!r}")
    print("  Recorder: sounddevice continuous stream")
    if manual_stop:
        print("  Press ENTER, say the phrase once, then press ENTER to stop...")
    else:
        print(f"  Press ENTER, then say the phrase once. Auto-stops after {record_seconds:.1f}s.")
    try:
        input("  START (ENTER) > ")
    except EOFError:
        raise SystemExit(
            "Interactive recording is unavailable in this environment. "
            "Use --dry-run or --fixture-audio for non-interactive use."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not manual_stop:
        tmp_path = output_path.with_name(f".{output_path.stem}.recording{output_path.suffix}")
        if tmp_path.exists():
            tmp_path.unlink()
        cmd = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--_record-sounddevice-child",
            str(tmp_path),
            "--_record-child-seconds",
            str(record_seconds),
        ]
        if device is not None:
            cmd.extend(["--_record-child-device", str(device)])
        print("  Recording...", flush=True)
        timeout_s = max(8.0, record_seconds + 6.0)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
        except subprocess.TimeoutExpired as exc:
            if tmp_path.exists():
                tmp_path.unlink()
            raise RuntimeError(f"sounddevice recording timed out after {timeout_s:.1f}s") from exc
        if result.returncode != 0 or not tmp_path.exists():
            if tmp_path.exists():
                tmp_path.unlink()
            detail = (result.stderr or result.stdout or "unknown sounddevice error").strip()
            raise RuntimeError(f"sounddevice recording failed: {detail}")
        tmp_path.replace(output_path)
        print("  Done.", flush=True)
        return sounddevice_clip_metadata(output_path)

    chunks: list[Any] = []

    def _callback(indata: Any, frames: int, time_info: Any, status: Any) -> None:
        if status:
            # Avoid noisy output for harmless PortAudio status flags, but keep data.
            pass
        chunks.append(indata.copy())

    with sd.InputStream(
        samplerate=REQUIRED_SAMPLE_RATE,
        channels=1,
        dtype="float32",
        device=device,
        callback=_callback,
    ):
        try:
            input("  STOP (ENTER) > ")
        except EOFError:
            pass
    if chunks:
        audio = np.concatenate(chunks, axis=0).reshape(-1)
    else:
        audio = np.empty(0, dtype="float32")

    sf.write(str(output_path), audio, REQUIRED_SAMPLE_RATE, subtype="PCM_16")
    return sounddevice_clip_metadata(output_path)


def record_clip(
    phrase: str,
    index: int,
    total: int,
    output_path: Path,
    device: int | None,
    recorder: str = "auto",
    record_seconds: float = DEFAULT_RECORD_SECONDS,
    manual_stop: bool = False,
) -> dict[str, Any]:
    # Auto now prefers a continuous sounddevice stream. The old implementation
    # opened the mic repeatedly in chunks; this one keeps a single stream open.
    if recorder in {"auto", "sounddevice"}:
        try:
            return record_clip_sounddevice(phrase, index, total, output_path, device, record_seconds, manual_stop)
        except Exception:
            if recorder == "sounddevice":
                raise
            if ffmpeg_available():
                print("  sounddevice recorder failed; falling back to ffmpeg.")
            else:
                raise

    if ffmpeg_available():
        return record_clip_ffmpeg(phrase, index, total, output_path, device, record_seconds, manual_stop)
    raise RuntimeError("No recorder backend available. Install ffmpeg or use uv sounddevice dependencies.")


def collect_fixture_clips(
    fixture_dir: Path,
    speaker: str,
    count: int,
    out_dir: Path,
    dry_run: bool,
) -> tuple[list[dict[str, Any]], list[str]]:
    if not fixture_dir.exists():
        raise SystemExit(f"Fixture path does not exist: {fixture_dir}")

    fixture_files = sorted(
        p
        for p in fixture_dir.glob("**/*")
        if p.is_file() and p.suffix.lower() in {".wav", ".flac", ".ogg", ".mp3", ".m4a"}
    )
    if not fixture_files:
        raise SystemExit(f"No audio files found in fixture path: {fixture_dir}")

    if count == 0:
        return [], []

    rows: list[dict[str, Any]] = []
    notes: list[str] = []
    picks = fixture_files[:count] if count > 0 else []

    for i, src in enumerate(picks, start=1):
        filename = f"{speaker}_{i:04d}{src.suffix.lower()}"
        dst = out_dir / filename
        rel = f"audio/positive-real/{filename}"
        status = "fixture"

        if not dry_run and not dst.exists():
            shutil.copy2(src, dst)
        elif not dry_run and dst.exists():
            notes.append(f"Skipped overwrite due existing fixture target: {dst}")
        else:
            notes.append(f"Planned fixture copy: {src.name}")

        rows.append(
            {
                "status": "fixture",
                "path": rel,
                "sample_rate": REQUIRED_SAMPLE_RATE,
                "duration_s": 0.0,
                "duration_ok": False,
                "rms_db": None,
                "source": "fixture",
                "source_file": str(src),
                "source_hash": None,
            }
        )

    if count > 0 and len(picks) < count:
        notes.append(
            f"Fixture contained {len(picks)} files but {count} requested. Proceeded with available files."
        )

    return rows, notes


def is_port_open(host: str, port: int, timeout: float = 0.6) -> bool:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0


def docker_compose_cmd() -> str | None:
    if shutil.which("docker"):
        return "docker compose"
    if shutil.which("docker-compose"):
        return "docker-compose"
    return None


def run_cmd(cmd: list[str], cwd: Path, timeout: int = 20, check: bool = False) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=check,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return 127, "", "command-not-found"
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except Exception as exc:  # pragma: no cover
        return 1, "", str(exc)


def run_foreground(cmd: list[str], cwd: Path) -> int:
    return subprocess.call(cmd, cwd=str(cwd))


def prompt_yes_no(question: str, default: bool = False) -> bool:
    if not sys.stdin.isatty():
        return default
    suffix = "[Y/n]" if default else "[y/N]"
    answer = input(f"{question} {suffix} ").strip().lower()
    if not answer:
        return default
    return answer in {"y", "yes", "j", "jah"}


def timestamp_tag() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def default_model_tag(slug: str) -> str:
    return f"{slug}-local-{timestamp_tag()}"


def resolve_existing_path(raw: str) -> Path:
    path = Path(raw).expanduser()
    if path.is_absolute():
        return path
    for base in (Path.cwd(), PROJECT_ROOT):
        candidate = base / path
        if candidate.exists():
            return candidate.resolve()
    return (Path.cwd() / path).resolve()


def load_manifest_for_resume(path: Path) -> tuple[dict[str, Any], str, str, Path]:
    if not path.exists():
        raise SystemExit(f"Manifest not found: {path}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid manifest JSON: {path}: {exc}")
    phrase = str(manifest.get("wizard", {}).get("phrase") or manifest.get("prompts", {}).get("target") or "wake word")
    slug = str(manifest.get("wizard", {}).get("slug") or path.parent.name)
    return manifest, phrase, slug, path.parent


def check_services(no_docker: bool, dry_run: bool) -> ServiceStatus:
    status = ServiceStatus()

    status.stt_port_open = is_port_open("127.0.0.1", 10300)
    status.neurokone_port_open = is_port_open("127.0.0.1", 10301)

    if no_docker:
        status.notes.append("docker checks skipped (--no-docker)")
        return status

    compose = docker_compose_cmd()
    if compose is None:
        status.notes.append("docker not available")
        return status
    status.docker_available = True
    status.compose_command = compose

    compose_base: list[str] = compose.split() + [
        "-f",
        str(PROJECT_ROOT / "docker" / "kratt-stack.yml"),
    ]

    rc, _, err = run_cmd([*compose_base, "config"], cwd=PROJECT_ROOT, timeout=40)
    if rc != 0:
        status.notes.append(f"compose config failed: {err.strip()}")
        return status

    if dry_run:
        status.notes.append("compose start skipped (dry-run)")
    else:
        status.notes.append(
            "compose config ok; services were not started automatically. "
            "Start them manually with: docker compose -f docker/kratt-stack.yml "
            "--profile stt --profile neurokone up -d"
        )

    return status


def check_neurokone_api() -> bool:
    if requests is None:
        return False
    try:
        response = requests.post(
            NEUROKONE_API_ENDPOINT,
            json={"text": "ok", "speaker": NEUROKONE_VOICE, "speed": 1.0},
            timeout=6,
        )
        return response.status_code == 200 and bool(response.content)
    except Exception:
        return False


def list_rejection_choices() -> str:
    return "[p]lay / [a]ccept / [r]eject / [u]nsure (default: a)"


def play_review_clip(clip_path: str) -> tuple[bool, str]:
    path = Path(clip_path)
    if not path.exists():
        return False, f"clip not found: {path}"

    if sys.platform == "darwin" and shutil.which("afplay"):
        cmd = ["afplay", str(path)]
    elif shutil.which("ffplay"):
        cmd = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "error", str(path)]
    else:
        return False, "no playback command found (need afplay on macOS or ffplay from ffmpeg)"

    try:
        subprocess.run(cmd, check=False)
        return True, "played"
    except Exception as exc:
        return False, str(exc)


def ask_review(
    clip_path: str,
    phrase: str,
    transcript: str | None,
    dry_run: bool,
) -> tuple[str, bool, str]:
    if dry_run:
        return "accepted", True, "dry-run-accepted"

    if not sys.stdin.isatty():
        return "accepted", True, "auto-accepted-noninteractive"

    print(f"\nReview clip: {clip_path}")
    if transcript:
        print(f"  Transcript: {transcript!r}")
    else:
        print("  Transcript: (not available)")
    print("  Tip: press 'p' to play/replay the clip as many times as needed.")

    while True:
        answer = input(f"  {list_rejection_choices()}: ").strip().lower()
        if answer in {"p", "play", "l", "listen", "replay", "kuula"}:
            ok, message = play_review_clip(clip_path)
            if not ok:
                print(f"  Playback failed: {message}")
            continue
        if answer in {"", "a", "y", "yes"}:
            return "accepted", True, "user-accepted"
        if answer in {"r", "n", "no"}:
            return "rejected", False, "user-rejected"
        if answer in {"u", "?", "q", "skip"}:
            return "uncertain", False, "user-uncertain"
        print("  Invalid input. Use p / a / r / u")


def transcribe_with_placeholder(
    audio_path: str,
    phrase: str,
    stt_disabled: bool,
    services: ServiceStatus,
) -> tuple[str | None, str]:
    if stt_disabled:
        return None, "disabled"

    # Minimal, swappable placeholder. If no Wyoming client is integrated, return None.
    if services.stt_port_open and requests is not None:
        # No public Wyoming HTTP endpoint contract is guaranteed here.
        # Keep this lightweight and non-breaking until a client is wired in.
        return None, "port-open-remote-protocol-not-implemented"

    return None, "unavailable"


def write_stt_review(rows: list[dict[str, Any]], path: Path, dry_run: bool) -> list[dict[str, Any]]:
    if dry_run:
        return rows
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return rows


def make_eval_split(rows: list[dict[str, Any]], keep_for_eval: int = 1) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    accepted = [row for row in rows if row.get("accepted")]
    if len(accepted) < 2:
        return accepted, []
    eval_count = max(1, keep_for_eval)
    eval_rows = accepted[:eval_count]
    train_rows = accepted[eval_count:]
    return train_rows, eval_rows


def copy_eval_smoke(
    train_root: Path,
    eval_root: Path,
    eval_rows: list[dict[str, Any]],
    dry_run: bool,
) -> list[str]:
    copied: list[str] = []
    if dry_run:
        return [str(Path(row["path"]).name) for row in eval_rows]

    eval_root.mkdir(parents=True, exist_ok=True)
    for row in eval_rows:
        src = train_root / row["path"]
        if isinstance(src, Path) and not src.is_absolute():
            src = train_root / src
        dst = eval_root / Path(row["path"]).name
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
            copied.append(str(dst.relative_to(train_root)))
        elif src.exists():
            copied.append(f"skip-existing:{dst.name}")
    return copied

def parse_csv_list(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


async def synthesize_wyoming_once(
    text: str,
    voice: str,
    out_path: Path,
    host: str = "127.0.0.1",
    port: int = 10301,
    timeout_s: float = DEFAULT_TTS_TIMEOUT_SECONDS,
) -> None:
    from wyoming.audio import AudioChunk, AudioStart, AudioStop  # type: ignore
    from wyoming.client import AsyncTcpClient  # type: ignore
    from wyoming.tts import Synthesize, SynthesizeVoice  # type: ignore

    pcm = bytearray()
    rate = 16000
    width = 2
    channels = 1
    async with AsyncTcpClient(host, port) as client:
        await asyncio.wait_for(
            client.write_event(Synthesize(text=text, voice=SynthesizeVoice(name=voice)).event()),
            timeout=min(5.0, timeout_s),
        )
        while True:
            event = await asyncio.wait_for(client.read_event(), timeout=timeout_s)
            if event is None:
                break
            if AudioStart.is_type(event.type):
                start = AudioStart.from_event(event)
                rate, width, channels = start.rate, start.width, start.channels
            elif AudioChunk.is_type(event.type):
                chunk = AudioChunk.from_event(event)
                pcm.extend(chunk.audio)
            elif AudioStop.is_type(event.type):
                break
    if not pcm:
        raise RuntimeError("Wyoming TTS returned empty audio")
    with wave.open(str(out_path), "wb") as fh:
        fh.setnchannels(channels)
        fh.setsampwidth(width)
        fh.setframerate(rate)
        fh.writeframes(bytes(pcm))


def synthesize_tts_once(text: str, voice: str, speed: float, out_path: Path, service_status: ServiceStatus, timeout_s: float) -> tuple[bool, str]:
    if service_status.neurokone_port_open:
        try:
            asyncio.run(synthesize_wyoming_once(text, voice, out_path, timeout_s=timeout_s))
            return True, "wyoming"
        except Exception as exc:
            # Fall through to the public API below when available.
            wyoming_error = str(exc)
    else:
        wyoming_error = "wyoming-port-closed"

    if requests is not None:
        try:
            response = requests.post(
                NEUROKONE_API_ENDPOINT,
                json={"text": text, "speaker": voice, "speed": speed},
                timeout=timeout_s,
            )
            if response.status_code == 200 and response.content:
                out_path.write_bytes(response.content)
                return True, "api"
            return False, f"api-http-{response.status_code}; wyoming={wyoming_error}"
        except Exception as exc:
            return False, f"api-error={exc}; wyoming={wyoming_error}"
    return False, f"requests unavailable; wyoming={wyoming_error}"


def generate_tts_audio(
    phrases: list[str],
    out_dir: Path,
    dry_run: bool,
    voices: list[str],
    per_voice: int,
    service_status: ServiceStatus,
    timeout_s: float,
    label: str = "tts",
) -> tuple[int, int, list[str]]:
    if dry_run or per_voice <= 0 or not voices:
        return 0, 0, []

    out_dir.mkdir(parents=True, exist_ok=True)
    generated = 0
    skipped = 0
    notes: list[str] = []
    source_counts: dict[str, int] = {}
    phrase_pool = deduplicate_keep_order(phrases)
    if not phrase_pool:
        return 0, 0, ["no TTS phrases"]

    total = len(voices) * per_voice
    done = 0
    for voice in voices:
        for idx in range(per_voice):
            done += 1
            text = phrase_pool[idx % len(phrase_pool)]
            speed = DEFAULT_TTS_SPEEDS[idx % len(DEFAULT_TTS_SPEEDS)]
            safe = re.sub(r"[^a-z0-9äõöüšž]+", "-", text.lower(), flags=re.IGNORECASE).strip("-") or "item"
            target = out_dir / f"{voice}_{idx + 1:03d}_{safe}_s{str(speed).replace('.', 'p')}.wav"
            if target.exists():
                skipped += 1
                if done == 1 or done % 10 == 0 or done == total:
                    print(f"  {label}: {done}/{total} (generated={generated}, existing/skipped={skipped})", flush=True)
                continue
            print(f"  {label}: {done}/{total} voice={voice} text={text!r}", flush=True)
            ok, source = synthesize_tts_once(text, voice, speed, target, service_status, timeout_s=timeout_s)
            if ok:
                generated += 1
                source_counts[source] = source_counts.get(source, 0) + 1
            else:
                skipped += 1
                print(f"    skipped: {source}", flush=True)
                if len(notes) < 8:
                    notes.append(f"{voice}:{text}:{source}")
    if generated:
        notes.append("generated_by=" + ",".join(f"{k}:{v}" for k, v in sorted(source_counts.items())))
    return generated, skipped, notes


def write_yaml_config(path: Path, payload: dict[str, Any], dry_run: bool) -> None:
    def _emit_yaml_value(v: Any, level: int = 0) -> str:
        indent = "  " * level
        if isinstance(v, dict):
            lines: list[str] = []
            for key in v:
                lines.append(f"{indent}{key}:")
                lines.append(_emit_yaml_value(v[key], level + 1).rstrip())
            return "\n".join(lines) + "\n"
        if isinstance(v, list):
            if not v:
                return f"{indent}[]\n"
            lines = [f"{indent}- {item}" for item in v]
            return "\n".join(lines) + "\n"
        if isinstance(v, bool):
            return f"{indent}{str(v).lower()}\n"
        if isinstance(v, (int, float)):
            return f"{indent}{v}\n"
        return f"{indent}{json.dumps(v)}\n"

    if dry_run:
        return
    lines = [f"# generated by new-wake-word-wizard v{WIZARD_VERSION}", f"generated_at: {now_iso()}\n"]
    lines.append(_emit_yaml_value(payload).rstrip())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_readme(
    out_root: Path,
    phrase: str,
    slug: str,
    manifest_name: str,
    service_status: ServiceStatus,
    dry_run: bool,
    count: int,
    no_stt: bool,
    no_tts: bool,
) -> None:
    text = f"""# New wake-word wizard output: {slug}

This is a **diagnostic starter dataset** for phrase: **{phrase}**.

Generated by `kratt new-wake-word` (MVP workflow).

## What this gives

- A self-contained dataset skeleton at `{out_root.as_posix()}`
- Real positive recordings (if recording was possible) in `audio/positive-real`
- TTS positives + confusable-negative templates in `audio/positive-tts` and `audio/negative-confusable-tts` (only if TTS generation succeeded)
- Text prompt files in `texts/`
- Split plan with `audio/eval-smoke` separation
- A manifest and reproducibility logs

## Scope and guardrails

This wizard intentionally provides a **starting point**, not a deployment-ready training set.
To avoid common leakage and false-accept risks:

- Exact full-phrase positives only should be used for training.
- Prefix-only/partial positives, reversed order, and command-context tails are *not* positives.
- `audio/eval-smoke` is a held-out smoke split and must stay separate from training until you explicitly train with it.
- Hard/confusable negatives are generated for baseline FPR probing.

## Metrics note

Real deployment quality claims should be reported with all three:

- streaming FAPH,
- real-speaker recall,
- and prefix/confusable false-positive checks (same-session)

## Service notes

- Kiirkirjutaja STT is optional in this MVP.
- Neurokõne in this repo is a Wyoming wrapper over the Tartu Neurokõne API and is not fully offline.

Suggested Docker start command: `docker compose -f docker/kratt-stack.yml --profile stt --profile neurokone up -d`.
The wizard checks Compose configuration and local ports, but does not start Docker services by default.
TTS/STT availability in this run: {json.dumps(service_status.to_dict(), ensure_ascii=False)}

## Output status

- Requested phrase count: {count}
- STT check requested: {'no' if no_stt else 'yes'}
- TTS generation requested: {'no' if no_tts else 'yes'}

## Next steps

1. Review `texts/stt-review.jsonl` and adjust acceptance flags if needed.
2. Fill out negatives (ambient + broad negatives corpus) before any public claim.
3. Run commands from `training/commands.sh`.
4. Keep `training/config.yaml` and `reports/data-summary.json` for reproducibility.

See also: `{manifest_name}`.
"""

    (out_root / "README.md").write_text(textwrap.dedent(text), encoding="utf-8")


def build_commands_script(
    paths: dict[str, Path],
    output_root: Path,
    phrase: str,
    slug: str,
    manifest_path: Path,
    args: argparse.Namespace,
    service_status: ServiceStatus,
    train_rows: list[dict[str, Any]],
    eval_rows: list[dict[str, Any]],
) -> None:
    cmd_path = paths["training"] / "commands.sh"
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        f"# generated-by: new-wake-word-wizard v{WIZARD_VERSION}",
        f"# generated-at: {now_iso()}",
        f"# phrase: {phrase}",
        f"# slug: {slug}",
        f"# manifest: {manifest_path}",
        "",
        "# --- Setup (required/optional) ---",
        f"REPO_ROOT=\"${{KRATT_ROOT:-{PROJECT_ROOT}}}\"",
        f"OUTPUT_ROOT=\"{output_root}\"",
        "cd \"$REPO_ROOT/wake-word\"",
        "",
        "# 1) Smooth end-to-end path for a fresh run:",
        f"# \"$REPO_ROOT/cli/kratt\" new-wake-word --phrase \"{phrase}\" --count 10 --end-to-end --tag \"{slug}-local\"",
        "# Resume this dataset later with the same public command:",
        f"# \"$REPO_ROOT/cli/kratt\" new-wake-word --manifest \"$OUTPUT_ROOT/manifest.json\" --train --benchmark --tag \"{slug}-local\" --steps 1000,200",
        f"# \"$REPO_ROOT/cli/kratt\" new-wake-word --manifest \"$OUTPUT_ROOT/manifest.json\" --benchmark --model \"$OUTPUT_ROOT/models/{slug}-local.tflite\" --faph-limit 100",
        "",
        "# 2) Manual local smoke planning; inspect training config before starting any training",
        f"# - Real positives accepted: {len(train_rows)}",
        f"# - Real positives reserved for eval-smoke: {len(eval_rows)}",
        "",
        "# 3) Existing options for data prep",
        "uv sync",
        "./training/scripts/setup_microwakeword_env.sh",
        "# Copy selected examples into processed layout before any microWakeWord run",
        "mkdir -p data/processed/positive_samples data/processed/negative_samples data/processed/ambient_samples",
        "echo \"cp \\\"${OUTPUT_ROOT}/audio/positive-real/*.wav\\\" data/processed/positive_samples/  # optional\"",
        "echo \"Add negatives/ambient from your standard corpora before training.\"",
        "",
    ]

    if args.local_smoke_train:
        lines.extend(
            [
                "# 3) Optional local smoke (plan only; run only when you are ready):",
                "# ./training/scripts/train_microwakeword.sh",
                "",
            ]
        )

    if args.hpc_plan:
        lines.extend(
            [
                "# 4) HPC follow-up sketch:",
                "# ./cli/kratt train <tag> --dataset-preset recall-cv --dry-run",
                "# and update manifest references in your training config before final submit.",
                "",
            ]
        )

    lines.extend(
        [
            "# Important caveat:",
            "# Neurokõne here is an API-backed Wyoming wrapper, not a fully offline only source.",
            "# Keep generated positives as augmentation only until manually verified.",
            "",
            f"echo 'Prepared smoke workflow for new wake word: {phrase}'",
        ]
    )

    content = "\n".join(lines)
    cmd_path.write_text(content + "\n", encoding="utf-8")
    cmd_path.chmod(0o755)


def build_reproducibility_checklist(
    paths: dict[str, Path],
    output_root: Path,
    phrase: str,
    slug: str,
    args: argparse.Namespace,
    service_status: ServiceStatus,
    counts: dict[str, int],
    dry_run: bool,
) -> None:
    checklist = f"""# Reproducibility checklist

- [x] phrase: {phrase}
- [x] slug: {slug}
- [x] output directory: `{output_root}`
- [x] command-line args captured in manifest
- [x] timestamped output layout created
- [x] requested real-positive count: {args.count}
- [x] real-positive collected count: {counts.get('real_total', 0)}
- [x] accepted real-positive count: {counts.get('real_accepted', 0)}
- [x] positive-eval split kept in `audio/eval-smoke`: {counts.get('eval_count', 0)}
- [x] positive-prompts created: {counts.get('positive_prompt_count', 0)}
- [x] confusable prompts created: {counts.get('confusable_prompt_count', 0)}
- [x] docker/stt/neurokone check ran: {not args.no_docker}
- [x] tts requested: {'no' if args.no_tts else 'yes'}
- [x] dry-run: {'yes' if args.dry_run else 'no'}
- [x] service status: {json.dumps(service_status.to_dict(), ensure_ascii=False)}
- [ ] run local smoke training (optional)
- [ ] add broader negative corpus before any claim
- [ ] run external threshold validation (FAPH + recall + confusable FPR together)

## Files created

- `README.md`
- `manifest.json`
- `texts/target.txt`
- `texts/positive-prompts.txt`
- `texts/confusable-negatives.txt`
- `texts/stt-review.jsonl`
- `training/config.yaml`
- `training/commands.sh`
- `reports/data-summary.json`
- `reports/reproducibility-checklist.md`
"""

    (paths["reports"] / "reproducibility-checklist.md").write_text(checklist, encoding="utf-8")


def summarise_rows(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "count": len(rows),
        "accepted": sum(1 for r in rows if r.get("accepted")),
        "rejected": sum(1 for r in rows if r.get("decision") == "rejected"),
        "uncertain": sum(1 for r in rows if r.get("decision") == "uncertain"),
        "planned": sum(1 for r in rows if r.get("status") == "planned"),
    }


def path_to_relative(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def build_manifest(
    output_root: Path,
    phrase: str,
    slug: str,
    speaker: str,
    args: argparse.Namespace,
    service_status: ServiceStatus,
    real_rows: list[dict[str, Any]],
    train_rows: list[dict[str, Any]],
    eval_rows: list[dict[str, Any]],
    positive_prompts: list[str],
    confusable_prompts: list[str],
    tts_positive_count: int,
    tts_confusable_count: int,
    tts_notes: list[str],
    eval_copies: list[str],
) -> dict[str, Any]:
    return {
        "wizard": {
            "version": WIZARD_VERSION,
            "created_at": now_iso(),
            "dry_run": bool(args.dry_run),
            "phrase": phrase,
            "slug": slug,
            "speaker": speaker,
            "output_root": str(output_root),
            "requested_real_count": int(args.count),
            "requested_services": {
                "no_docker": bool(args.no_docker),
                "no_stt": bool(args.no_stt),
                "no_tts": bool(args.no_tts),
            },
            "service_status": service_status.to_dict(),
            "fixture_audio": bool(args.fixture_audio),
            "local_smoke_train": bool(args.local_smoke_train),
            "hpc_plan": bool(args.hpc_plan),
        },
        "prompts": {
            "target": phrase,
            "positive": positive_prompts,
            "confusable": confusable_prompts,
        },
        "real_audio": {
            "summary": summarise_rows(real_rows),
            "clips": real_rows,
            "train_rows": [path_to_relative(output_root / row["path"], output_root) for row in train_rows],
            "eval_rows": [path_to_relative(output_root / row["path"], output_root) for row in eval_rows],
        },
        "stt": {
            "records": [
                {
                    "path": row["path"],
                    "transcript": row.get("transcript"),
                    "decision": row.get("decision"),
                    "accepted": row.get("accepted"),
                    "reviewed_at": row.get("reviewed_at"),
                }
                for row in real_rows
            ]
        },
        "tts": {
            "positive_count": tts_positive_count,
            "confusable_count": tts_confusable_count,
            "notes": tts_notes,
        },
        "splits": {
            "positive_real_train": [row["path"] for row in train_rows],
            "positive_real_eval_smoke": [row["path"] for row in eval_rows],
            "eval_smoke_copies": eval_copies,
        },
        "guardrails": {
            "exact_phrase_only": True,
            "no_train_with_user_test_mixing": True,
            "confusables_required": True,
            "no_hidden_positives": True,
        },
    }


def build_data_summary(
    manifest: dict[str, Any],
    output_root: Path,
) -> dict[str, Any]:
    return {
        "generated_at": manifest["wizard"]["created_at"],
        "output_root": str(output_root),
        "manifest_path": str(output_root / "manifest.json"),
        "counts": {
            "real_total": manifest["real_audio"]["summary"]["count"],
            "real_accepted": manifest["real_audio"]["summary"]["accepted"],
            "train_real": len(manifest["splits"]["positive_real_train"]),
            "eval_real": len(manifest["splits"]["positive_real_eval_smoke"]),
            "tts_positive": manifest["tts"]["positive_count"],
            "tts_confusable": manifest["tts"]["confusable_count"],
        },
    }


def ensure_tts_for_existing_output(args: argparse.Namespace, output_root: Path) -> None:
    if args.no_tts:
        return
    manifest_path = output_root / "manifest.json"
    if not manifest_path.exists():
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return

    positive_dir = output_root / "audio" / "positive-tts"
    confusable_dir = output_root / "audio" / "negative-confusable-tts"
    existing_positive = len(list(positive_dir.rglob("*.wav"))) if positive_dir.exists() else 0
    existing_confusable = len(list(confusable_dir.rglob("*.wav"))) if confusable_dir.exists() else 0

    phrase = str(manifest.get("wizard", {}).get("phrase") or manifest.get("prompts", {}).get("target") or "")
    positive_prompts = manifest.get("prompts", {}).get("positive") or build_positive_prompts(phrase)
    confusable_prompts = manifest.get("prompts", {}).get("confusable") or build_confusables(phrase)
    voices = parse_csv_list(args.tts_voices)
    desired_positive = len(voices) * args.tts_per_voice
    desired_confusable = len(voices) * args.tts_confusable_per_voice
    if existing_positive >= desired_positive and existing_confusable >= desired_confusable:
        return
    services = check_services(args.no_docker, dry_run=False)
    services.neurokone_api_reachable = check_neurokone_api()

    print("\nGenerating missing TTS clips before training...")
    pos_count, pos_skipped, pos_notes = generate_tts_audio(
        list(positive_prompts),
        positive_dir,
        dry_run=False,
        voices=voices,
        per_voice=args.tts_per_voice,
        service_status=services,
        timeout_s=args.tts_timeout,
        label="positive TTS",
    )
    neg_count = 0
    neg_skipped = 0
    neg_notes: list[str] = []
    if args.tts_confusable_per_voice > 0:
        neg_count, neg_skipped, neg_notes = generate_tts_audio(
            list(confusable_prompts),
            confusable_dir,
            dry_run=False,
            voices=voices,
            per_voice=args.tts_confusable_per_voice,
            service_status=services,
            timeout_s=args.tts_timeout,
            label="confusable TTS",
        )
    print(f"TTS ready: new positives={pos_count}, new confusables={neg_count}")

    manifest.setdefault("tts", {})
    manifest["tts"]["positive_count"] = len(list(positive_dir.rglob("*.wav"))) if positive_dir.exists() else 0
    manifest["tts"]["confusable_count"] = len(list(confusable_dir.rglob("*.wav"))) if confusable_dir.exists() else 0
    notes = list(manifest["tts"].get("notes", []))
    notes.extend(pos_notes)
    notes.extend(neg_notes)
    if pos_skipped or neg_skipped:
        notes.append(f"tts-skipped-on-resume:{pos_skipped + neg_skipped}")
    manifest["tts"]["notes"] = notes[-40:]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_training_and_benchmark_flow(
    args: argparse.Namespace,
    output_root: Path,
    slug: str,
) -> int:
    explicit_train = bool(args.end_to_end or args.train)
    explicit_benchmark = bool(args.benchmark or (args.end_to_end and not args.skip_benchmark))

    train_now = explicit_train
    benchmark_now = explicit_benchmark
    if not explicit_train and not explicit_benchmark and not args.model:
        train_now = prompt_yes_no("Train a local TFLite model now?", default=False)
        if train_now:
            benchmark_now = prompt_yes_no("Benchmark it after training?", default=True)
    elif args.model and not explicit_benchmark:
        benchmark_now = prompt_yes_no("Benchmark the provided model now?", default=True)

    if args.skip_benchmark:
        benchmark_now = False

    if not train_now and not benchmark_now:
        print("\nWorkflow paused after data preparation.")
        print(f"Continue later with: ./cli/kratt new-wake-word --manifest {output_root / 'manifest.json'} --train --benchmark")
        return 0

    manifest_path = output_root / "manifest.json"
    model_path: Path | None = Path(args.model).expanduser() if args.model else None

    if train_now:
        ensure_tts_for_existing_output(args, output_root)
        tag = args.tag or default_model_tag(slug)
        model_path = output_root / "models" / f"{tag}.tflite"
        train_cmd = [
            sys.executable,
            str(TRAIN_NEW_SCRIPT),
            "--manifest",
            str(manifest_path),
            "--tag",
            tag,
            "--steps",
            args.steps,
            "--learning-rates",
            args.learning_rates,
            "--negative-class-weight",
            args.negative_class_weight,
            "--max-tts-positive-ratio",
            str(args.max_tts_positive_ratio),
            "--hard-negative-mode",
            args.hard_negative_mode,
            "--negative-limit",
            str(args.negative_limit),
            "--ambient-limit",
            str(args.ambient_limit),
        ]
        if not args.no_spec_augment:
            train_cmd.append("--spec-augment")
        for hard_dir in args.hard_negative_dir:
            train_cmd.extend(["--hard-negative-dir", hard_dir])
        if args.negative_dir:
            train_cmd.extend(["--negative-dir", args.negative_dir])
        if args.ambient_dir:
            train_cmd.extend(["--ambient-dir", args.ambient_dir])
        print("\n=== Local training ===", flush=True)
        rc = run_foreground(train_cmd, PROJECT_ROOT)
        if rc != 0:
            return rc

    if benchmark_now:
        if model_path is None:
            raise SystemExit("Benchmark requested but no model path is available. Use --model or --train.")
        if not model_path.is_absolute():
            model_path = (Path.cwd() / model_path).resolve()
        if not model_path.exists():
            raise SystemExit(f"Benchmark requested but model does not exist: {model_path}")
        print("Preparing microWakeWord benchmark environment...", flush=True)
        setup_rc = run_foreground(["bash", str(SETUP_MICROWAKEWORD_ENV_SCRIPT)], PROJECT_ROOT)
        if setup_rc != 0:
            return setup_rc
        if not MICROWAKEWORD_ENV_PYTHON.exists():
            raise SystemExit(f"microWakeWord Python not found after setup: {MICROWAKEWORD_ENV_PYTHON}")
        bench_cmd = [str(MICROWAKEWORD_ENV_PYTHON), str(BENCHMARK_NEW_SCRIPT)]
        bench_cwd = PROJECT_ROOT
        bench_cmd.extend(
            [
                "--manifest",
                str(manifest_path),
                "--model",
                str(model_path),
                "--faph-limit",
                str(args.faph_limit),
            ]
        )
        if args.faph_dir:
            bench_cmd.extend(["--faph-dir", args.faph_dir])
        bench_cmd.extend(["--thresholds", *[str(t) for t in args.thresholds]])
        print("\n=== Benchmark ===", flush=True)
        rc = run_foreground(bench_cmd, bench_cwd)
        if rc != 0:
            return rc

    return 0


def collect_real_rows(
    args: argparse.Namespace,
    phrase: str,
    speaker: str,
    paths: dict[str, Path],
    service_status: ServiceStatus,
) -> tuple[list[dict[str, Any]], list[str]]:
    notes: list[str] = []

    if args.count == 0:
        return [], notes

    if args.dry_run:
        rows: list[dict[str, Any]] = []
        for i in range(1, args.count + 1):
            path_rel = f"audio/positive-real/{speaker}_{i:04d}.wav"
            rows.append(
                {
                    "status": "planned",
                    "path": path_rel,
                    "sample_rate": REQUIRED_SAMPLE_RATE,
                    "duration_s": 0.0,
                    "duration_ok": False,
                    "rms_db": None,
                    "source": "planned",
                    "transcript": None,
                    "decision": "planned",
                    "accepted": False,
                    "reviewed_at": now_iso(),
                    "review_note": "dry-run placeholder",
                }
            )
        return rows, notes

    if args.fixture_audio:
        rows, fixture_notes = collect_fixture_clips(
            Path(args.fixture_audio).expanduser(), speaker, args.count, paths["positive_real"], dry_run=False
        )
        notes.extend(fixture_notes)
        return rows, notes

    if not recorder_available():
        if args.count > 0:
            raise SystemExit(
                "Recording tools unavailable: install ffmpeg or let the CLI run via uv "
                "with sounddevice/soundfile/numpy. You can also use --fixture-audio or --dry-run."
            )

    rows = []
    for i in range(1, args.count + 1):
        clip_name = f"{speaker}_{i:04d}.wav"
        target_path = paths["positive_real"] / clip_name

        print(f"\nTarget phrase: {phrase!r}")
        try:
            record = record_clip(
                phrase,
                i,
                args.count,
                target_path,
                args.device,
                args.recorder,
                args.record_seconds,
                args.manual_stop,
            )
        except Exception as exc:
            raise SystemExit(
                f"Recording failed for {clip_name}: {exc}\n"
                "Try `--recorder ffmpeg --device 0`, `--recorder sounddevice`, "
                "or use `--fixture-audio DIR`."
            ) from exc
        row: dict[str, Any] = {
            "status": record["status"],
            "path": f"audio/positive-real/{clip_name}",
            "sample_rate": record["sample_rate"],
            "duration_s": record["duration_s"],
            "duration_ok": record["duration_ok"],
            "rms_db": record["rms_db"],
            "source": record.get("source", "mic"),
            "transcript": None,
            "decision": None,
            "accepted": False,
            "reviewed_at": None,
            "review_note": None,
        }

        transcript, reason = transcribe_with_placeholder(str(target_path), phrase, args.no_stt, service_status)
        if not row["duration_ok"]:
            notes.append(
                f"clip {clip_name}: duration={row['duration_s']} outside [{MIN_DURATION_SECONDS}, {MAX_DURATION_SECONDS}]s"
            )

        decision, accepted, note = ask_review(str(target_path), phrase, transcript, dry_run=False)
        row["transcript"] = transcript
        row["decision"] = decision
        row["accepted"] = accepted
        row["reviewed_at"] = now_iso()
        row["review_note"] = note
        if reason:
            row["review_note"] += f"; stt:{reason}"

        rows.append(row)
        print(f"  Saved audio/positive-real/{clip_name}")

    return rows, notes


def run_wizard(args: argparse.Namespace) -> int:
    if args.list_devices:
        print_recording_devices()
        return 0

    if args.manifest:
        manifest_path = resolve_existing_path(args.manifest)
        _, phrase, slug, output_root = load_manifest_for_resume(manifest_path)
        print("=== New wake-word wizard: resume ===", flush=True)
        print(f"Phrase: {phrase}")
        print(f"Slug: {slug}")
        print(f"Manifest: {manifest_path}")
        print(f"Output: {output_root}")
        if args.dry_run:
            if args.train or args.end_to_end:
                print("Planned local training:")
                print(f"  tag: {args.tag or f'{slug}-local-<timestamp>'}")
                print(f"  steps: {args.steps}")
                print(f"  negative-limit: {args.negative_limit}")
                print(f"  ambient-limit: {args.ambient_limit}")
            if args.benchmark or (args.end_to_end and not args.skip_benchmark):
                print("Planned benchmark:")
                print(f"  model: {args.model or str(output_root / 'models' / ((args.tag or slug + '-local-<timestamp>').replace('<timestamp>', 'TIMESTAMP') + '.tflite'))}")
                print(f"  faph-limit: {args.faph_limit}")
            print("Dry-run resume: no training or benchmark started.")
            return 0
        return run_training_and_benchmark_flow(args, output_root, slug)

    if args.phrase is None:
        args.phrase = input("Target phrase: ").strip()
        if not args.phrase:
            raise SystemExit("Phrase is required")

    phrase = args.phrase.strip()
    slug = (args.slug.strip() if args.slug else slugify(phrase))

    output_root, existed, safe = resolve_output_root(args.output, slug, bool(args.force or args.force_output))

    paths = ensure_dirs(output_root, args.dry_run)

    print("=== New wake-word wizard ===", flush=True)
    print(f"Phrase: {phrase}")
    print(f"Slug: {slug}")
    print(f"Output: {output_root}")
    print(f"Dry-run: {args.dry_run}")
    if existed or safe:
        print("Output guarded: using safe non-overwrite path.")

    service_status = check_services(args.no_docker, args.dry_run)

    positive_prompts = build_positive_prompts(phrase)
    confusable_prompts = build_confusables(phrase)

    if args.dry_run:
        planned_rows, _ = collect_real_rows(args, phrase, args.speaker, paths, service_status)
        print("\nPlanned layout (not created):")
        for key in ("base", "texts", "positive_real", "positive_tts", "negative_confusable_tts", "eval_smoke", "training", "reports"):
            print(f"  {key}: {paths[key]}")
        print("\nPositive prompts:")
        for item in positive_prompts:
            print(f"  - {item}")
        print("\nConfusable negative prompts:")
        for item in confusable_prompts:
            print(f"  - {item}")
        print(f"\nPlanned real-positive recordings: {len(planned_rows)}")
        if args.end_to_end or args.train:
            tag = args.tag or f"{slug}-local-<timestamp>"
            print("\nPlanned local training:")
            print(f"  tag: {tag}")
            print(f"  steps: {args.steps}")
            print(f"  negative-limit: {args.negative_limit}")
            print(f"  ambient-limit: {args.ambient_limit}")
            print(f"  recorder: {args.recorder}, record-seconds: {args.record_seconds}, manual-stop: {args.manual_stop}")
            if args.end_to_end and not args.skip_benchmark:
                print("\nPlanned benchmark:")
                print(f"  model: {paths['base'] / 'models' / (tag.replace('<timestamp>', 'TIMESTAMP') + '.tflite')}")
                print(f"  faph-limit: {args.faph_limit}")
        print("Dry-run complete: no files, directories, media, Docker services, or training jobs were created.")
        return 0

    write_text_list(paths["texts"] / "target.txt", [phrase], args.dry_run)
    write_text_list(paths["texts"] / "positive-prompts.txt", positive_prompts, args.dry_run)
    write_text_list(paths["texts"] / "confusable-negatives.txt", confusable_prompts, args.dry_run)

    if not args.no_stt:
        print("STT review enabled. Service status:", service_status.to_dict())
    else:
        print("STT review disabled via --no-stt")

    if not args.no_tts:
        if not args.dry_run:
            service_status.neurokone_api_reachable = check_neurokone_api()
            if not service_status.neurokone_api_reachable:
                service_status.notes.append("Neurokõne API call probe failed; TTS audio generation may be skipped.")
        else:
            service_status.notes.append("TTS probe skipped in dry-run.")

    real_rows, notes = collect_real_rows(args, phrase, args.speaker, paths, service_status)

    # Fill missing review metadata for dry-run and fixture rows
    for row in real_rows:
        if row.get("decision") is not None:
            continue

        if args.fixture_audio:
            row["decision"], row["accepted"], row["reviewed_at"], row["review_note"] = (
                "accepted",
                True,
                now_iso(),
                "fixture-auto-accepted",
            )
        else:
            row["decision"], row["accepted"], row["reviewed_at"], row["review_note"] = (
                "planned",
                False,
                now_iso(),
                "not-recorded",
            )

    write_stt_review(real_rows, paths["texts"] / "stt-review.jsonl", args.dry_run)

    # Split into train/eval smoke
    train_rows, eval_rows = make_eval_split(real_rows)
    for row in train_rows:
        row["split"] = "train"
    for row in eval_rows:
        row["split"] = "eval-smoke"

    eval_copies: list[str] = copy_eval_smoke(paths["base"], paths["eval_smoke"], eval_rows, args.dry_run)

    # TTS generation (audio only if possible and requested)
    tts_positive_count = 0
    tts_confusable_count = 0
    tts_notes: list[str] = []

    if not args.no_tts:
        if args.dry_run:
            print("Skipping TTS audio generation (dry-run).")
        else:
            voices = parse_csv_list(args.tts_voices)
            print(f"Generating TTS positives ({args.tts_per_voice}/voice, voices={len(voices)})...")
            tts_positive_count, skipped, positive_tts_notes = generate_tts_audio(
                positive_prompts,
                paths["positive_tts"],
                args.dry_run,
                voices=voices,
                per_voice=args.tts_per_voice,
                service_status=service_status,
                timeout_s=args.tts_timeout,
                label="positive TTS",
            )
            if args.tts_confusable_per_voice > 0:
                tts_confusable_count, skipped2, confusable_tts_notes = generate_tts_audio(
                    confusable_prompts,
                    paths["negative_confusable_tts"],
                    args.dry_run,
                    voices=voices,
                    per_voice=args.tts_confusable_per_voice,
                    service_status=service_status,
                    timeout_s=args.tts_timeout,
                    label="confusable TTS",
                )
            else:
                skipped2, confusable_tts_notes = 0, []
            tts_notes.extend(positive_tts_notes)
            tts_notes.extend(confusable_tts_notes)
            skipped = skipped + skipped2
            if skipped:
                tts_notes.append(f"tts-skipped:{skipped}")
            print(f"TTS generation done: positives={tts_positive_count}, confusables={tts_confusable_count}.")

    manifest = build_manifest(
        output_root=output_root,
        phrase=phrase,
        slug=slug,
        speaker=args.speaker,
        args=args,
        service_status=service_status,
        real_rows=real_rows,
        train_rows=train_rows,
        eval_rows=eval_rows,
        positive_prompts=positive_prompts,
        confusable_prompts=confusable_prompts,
        tts_positive_count=tts_positive_count,
        tts_confusable_count=tts_confusable_count,
        tts_notes=tts_notes,
        eval_copies=eval_copies,
    )

    (output_root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    data_summary = build_data_summary(manifest, output_root)
    (paths["reports"] / "data-summary.json").write_text(
        json.dumps(data_summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    write_yaml_config(
        paths["training"] / "config.yaml",
        {
            "project": {
                "phrase": phrase,
                "slug": slug,
                "speaker": args.speaker,
            },
            "paths": {
                "output_root": str(output_root),
                "manifest": "manifest.json",
                "positive_real": "audio/positive-real",
                "positive_tts": "audio/positive-tts",
                "negative_confusable_tts": "audio/negative-confusable-tts",
                "eval_smoke": "audio/eval-smoke",
            },
            "counts": {
                "real_total": manifest["real_audio"]["summary"]["count"],
                "real_accepted": manifest["real_audio"]["summary"]["accepted"],
                "positive_prompts": len(positive_prompts),
                "confusable_prompts": len(confusable_prompts),
            },
            "flags": {
                "no_stt": args.no_stt,
                "no_tts": args.no_tts,
                "dry_run": args.dry_run,
            },
        },
        args.dry_run,
    )

    build_commands_script(
        paths=paths,
        output_root=output_root,
        phrase=phrase,
        slug=slug,
        manifest_path=output_root / "manifest.json",
        args=args,
        service_status=service_status,
        train_rows=train_rows,
        eval_rows=eval_rows,
    )

    build_reproducibility_checklist(
        paths=paths,
        output_root=output_root,
        phrase=phrase,
        slug=slug,
        args=args,
        service_status=service_status,
        counts={
            "real_total": manifest["real_audio"]["summary"]["count"],
            "real_accepted": manifest["real_audio"]["summary"]["accepted"],
            "eval_count": len(eval_rows),
            "positive_prompt_count": len(positive_prompts),
            "confusable_prompt_count": len(confusable_prompts),
        },
        dry_run=args.dry_run,
    )

    build_readme(
        out_root=output_root,
        phrase=phrase,
        slug=slug,
        manifest_name="manifest.json",
        service_status=service_status,
        dry_run=args.dry_run,
        count=args.count,
        no_stt=args.no_stt,
        no_tts=args.no_tts,
    )

    if notes:
        print("\nNotes:")
        for note in notes:
            print(f"  - {note}")

    print("\nPrepared:")
    print(f"  output:    {output_root}")
    print(f"  manifest:  {output_root / 'manifest.json'}")
    print(f"  accepted:  {sum(1 for r in real_rows if r.get('accepted'))}/{len(real_rows)}")
    print(f"  eval-smoke: {len(eval_rows)}")
    if tts_positive_count or tts_confusable_count:
        print(f"  tts:       positives={tts_positive_count}, confusables={tts_confusable_count}")

    return run_training_and_benchmark_flow(args, output_root, slug)


def main() -> int:
    args = parse_args()
    if args._record_sounddevice_child:
        return record_sounddevice_child(
            Path(args._record_sounddevice_child),
            args._record_child_device,
            args._record_child_seconds or args.record_seconds,
        )
    if args.check:
        return print_onboarding_check(args)
    return run_wizard(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit("Interrupted by user")
