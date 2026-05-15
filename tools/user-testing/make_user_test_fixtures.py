#!/usr/bin/env python3
"""Generate synthetic WAV fixtures for the 10-minute user-test recorder.

These fixtures are for infrastructure smoke tests only. They exercise recorder,
validator, replay, threshold, and consensus plumbing without using microphone or
participant audio. They are not user-study evidence.
"""

from __future__ import annotations

import argparse
import io
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable

import numpy as np
import requests
import soundfile as sf

# Reuse the canonical trial list and duration fitting from the recorder.
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from run_user_test import SAMPLE_RATE, default_trials, fit_duration, resample_linear  # noqa: E402

LOCAL_TTS_URL = "http://127.0.0.1:5380/synthesize"
LOCAL_TTS_SPEAKER = "meelis"


def fixture_text(expected_text: str) -> str:
    if expected_text.startswith("<"):
        return "Kuule Kratt, tuba on liiga hele."
    return expected_text


def read_audio_bytes(data: bytes) -> tuple[np.ndarray, int]:
    audio, sr = sf.read(io.BytesIO(data), dtype="float32", always_2d=False)
    if isinstance(audio, np.ndarray) and audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    return np.asarray(audio, dtype=np.float32), int(sr)


def synthesize_local_tts(text: str, *, url: str, speaker: str, speed: float) -> tuple[np.ndarray, int]:
    response = requests.post(url, json={"text": text, "speaker": speaker, "speed": speed}, timeout=45)
    response.raise_for_status()
    return read_audio_bytes(response.content)


def synthesize_macos_say(text: str, *, voice: str | None) -> tuple[np.ndarray, int]:
    if not shutil.which("say"):
        raise RuntimeError("macOS `say` command not found")
    with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as tmp:
        out_path = Path(tmp.name)
    try:
        cmd = ["say", "-o", str(out_path)]
        if voice:
            cmd.extend(["-v", voice])
        cmd.append(text)
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        audio, sr = sf.read(str(out_path), dtype="float32", always_2d=False)
        if isinstance(audio, np.ndarray) and audio.ndim > 1:
            audio = np.mean(audio, axis=1)
        return np.asarray(audio, dtype=np.float32), int(sr)
    finally:
        out_path.unlink(missing_ok=True)


def local_tts_available(url: str) -> bool:
    try:
        probe_url = url.replace("/synthesize", "/speakers")
        return requests.get(probe_url, timeout=2).status_code == 200
    except Exception:
        return False


def synthesize(text: str, args: argparse.Namespace) -> tuple[np.ndarray, int, str]:
    method = args.method
    if method == "auto":
        method = "local-tts" if local_tts_available(args.url) else "macos-say"

    if method == "local-tts":
        audio, sr = synthesize_local_tts(text, url=args.url, speaker=args.speaker, speed=args.speed)
    elif method == "macos-say":
        audio, sr = synthesize_macos_say(text, voice=args.voice)
    else:  # pragma: no cover - argparse enforces choices
        raise ValueError(method)
    return audio, sr, method


def generate(args: argparse.Namespace) -> int:
    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_rows = []
    used_method = None
    for trial in default_trials():
        text = fixture_text(trial.expected_text)
        audio, sr, method = synthesize(text, args)
        used_method = method
        audio = resample_linear(audio, sr, SAMPLE_RATE)
        audio = fit_duration(audio, trial.duration_s)
        out_path = out_dir / f"{trial.trial_id}.wav"
        sf.write(out_path, audio, SAMPLE_RATE, subtype="PCM_16")
        manifest_rows.append(
            {
                "trial_id": trial.trial_id,
                "trial_type": trial.trial_type,
                "expected_wake": trial.expected_wake,
                "duration_s": trial.duration_s,
                "text": text,
                "audio_file": out_path.name,
            }
        )
        print(f"{trial.trial_id:<12} {out_path.name}  {text}")

    import json

    (out_dir / "fixtures.json").write_text(
        json.dumps(
            {
                "type": "kratt-user-test-fixtures",
                "method": used_method,
                "sample_rate": SAMPLE_RATE,
                "note": "Synthetic smoke-test fixtures only; not user-study evidence.",
                "trials": manifest_rows,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\nWrote fixtures: {out_dir}")
    print("Smoke test:")
    print(f"  ./cli/kratt user-test SYNTH01 --audio-fixture-dir {out_dir} --auto-advance --new-session-subdir")
    return 0


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic WAV fixtures for kratt user-test")
    parser.add_argument("--output-dir", default="output/user-test-fixtures/ten-minute-v1", help="Fixture output dir")
    parser.add_argument("--method", choices=["auto", "local-tts", "macos-say"], default="auto")
    parser.add_argument("--url", default=LOCAL_TTS_URL, help="Local TTS /synthesize URL")
    parser.add_argument("--speaker", default=LOCAL_TTS_SPEAKER, help="Local TTS speaker")
    parser.add_argument("--speed", type=float, default=1.0, help="Local TTS speed")
    parser.add_argument("--voice", default=None, help="macOS say voice name")
    return parser.parse_args(list(argv))


def main(argv: list[str] | None = None) -> int:
    return generate(parse_args(sys.argv[1:] if argv is None else argv))


if __name__ == "__main__":
    raise SystemExit(main())
