#!/usr/bin/env python3
"""Record labelled 10-minute Kratt user-test trials.

This is intentionally a small terminal-based harness. It does not run model
inference. Its job is to create the missing scientific artifact for user tests:
one labelled WAV per trial plus a machine-readable trials.jsonl manifest. The
same audio can then be replayed through all wake-word models offline.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16_000
CHANNELS = 1


@dataclass(frozen=True)
class TrialSpec:
    trial_id: str
    trial_type: str
    prompt: str
    expected_text: str
    expected_wake: bool
    expected_intent: str | None = None
    attempt_number: int = 1
    duration_s: float = 4.0


def default_trials() -> list[TrialSpec]:
    return [
        # Clean positives
        TrialSpec("POS_01", "positive_wake", "Ütle: Kuule Kratt", "Kuule Kratt", True, duration_s=3.0),
        TrialSpec("POS_02", "positive_wake", "Ütle: Kuule Kratt", "Kuule Kratt", True, duration_s=3.0),
        TrialSpec("POS_03", "positive_wake", "Ütle: Kuule Kratt", "Kuule Kratt", True, duration_s=3.0),
        TrialSpec("POS_04", "positive_wake", "Ütle: Kuule Kratt, pane tuli põlema", "Kuule Kratt, pane tuli põlema", True, "turn_on", duration_s=4.0),
        TrialSpec("POS_05", "positive_wake", "Ütle: Kuule Kratt, muuda tuli siniseks", "Kuule Kratt, muuda tuli siniseks", True, "set_color_blue", duration_s=4.0),
        # Hard negatives
        TrialSpec("HN_01", "hard_negative", "Loe: Kuule rott", "Kuule rott", False, duration_s=3.0),
        TrialSpec("HN_02", "hard_negative", "Loe: Tere Kratt", "Tere Kratt", False, duration_s=3.0),
        TrialSpec("HN_03", "hard_negative", "Loe: Kratt kuule", "Kratt kuule", False, duration_s=3.0),
        TrialSpec("HN_04", "hard_negative", "Loe: Kuule robot", "Kuule robot", False, duration_s=3.0),
        TrialSpec("HN_05", "hard_negative", "Loe: Kuule, kas sa kuuled?", "Kuule, kas sa kuuled?", False, duration_s=4.0),
        # Scripted bulb commands
        TrialSpec("CMD_ON", "scripted_command", "Juhi lampi: Kuule Kratt, pane tuli põlema.", "Kuule Kratt, pane tuli põlema.", True, "turn_on", duration_s=5.0),
        TrialSpec("CMD_RED", "scripted_command", "Juhi lampi: Kuule Kratt, pane tuli punaseks.", "Kuule Kratt, pane tuli punaseks.", True, "set_color_red", duration_s=5.0),
        TrialSpec("CMD_BLUE", "scripted_command", "Juhi lampi: Kuule Kratt, muuda tuli siniseks.", "Kuule Kratt, muuda tuli siniseks.", True, "set_color_blue", duration_s=5.0),
        TrialSpec("CMD_DIM", "scripted_command", "Juhi lampi: Kuule Kratt, vähenda heledust.", "Kuule Kratt, vähenda heledust.", True, "set_brightness_down", duration_s=5.0),
        TrialSpec("CMD_WHITE", "scripted_command", "Juhi lampi: Kuule Kratt, pane tuli valgeks.", "Kuule Kratt, pane tuli valgeks.", True, "set_color_white", duration_s=5.0),
        TrialSpec("CMD_OFF", "scripted_command", "Juhi lampi: Kuule Kratt, pane tuli kustu.", "Kuule Kratt, pane tuli kustu.", True, "turn_off", duration_s=5.0),
        # Natural/free form
        TrialSpec(
            "FREE_FILM_01",
            "free_form_command",
            "Oma sõnadega: tee valgus selliseks, nagu tahaksid õhtul filmi vaadata.",
            "<free-form film-evening lighting command>",
            True,
            "free_form_lighting_mood",
            duration_s=8.0,
        ),
    ]


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def sanitize_participant_id(value: str) -> str:
    cleaned = "".join(ch for ch in value.strip() if ch.isalnum() or ch in "_-.")
    if not cleaned:
        raise SystemExit("participant_id became empty after sanitization")
    return cleaned


def list_devices() -> None:
    print(sd.query_devices())


def record_audio(duration_s: float, device: int | None, dry_run: bool) -> np.ndarray:
    frames = int(round(duration_s * SAMPLE_RATE))
    if dry_run:
        return np.zeros((frames,), dtype=np.float32)

    audio = sd.rec(
        frames,
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
        device=device,
    )
    sd.wait()
    return audio.reshape(-1)


def run_session(args: argparse.Namespace) -> Path:
    participant_id = sanitize_participant_id(args.participant_id)
    session_id = args.session_id or uuid.uuid4().hex[:8]
    started = datetime.now().strftime("%Y%m%d-%H%M%S")

    base_dir = Path(args.output_dir).expanduser().resolve() / participant_id
    if args.new_session_subdir:
        base_dir = base_dir / f"{started}_{session_id}"
    audio_dir = base_dir / "audio"
    trials_path = base_dir / "trials.jsonl"
    session_path = base_dir / "session.json"

    if base_dir.exists() and any(base_dir.iterdir()) and not args.allow_existing:
        raise SystemExit(
            f"Output directory already exists and is not empty: {base_dir}\n"
            "Use --allow-existing or --new-session-subdir."
        )

    audio_dir.mkdir(parents=True, exist_ok=True)

    session_record = {
        "type": "session_start",
        "session_id": session_id,
        "participant_id": participant_id,
        "created_at": iso_now(),
        "protocol": "10-minute-shadow-demo-v1",
        "active_model": args.active_model,
        "audio_consent": args.audio_consent,
        "sample_rate": SAMPLE_RATE,
        "device": args.device,
        "dry_run": args.dry_run,
        "operator": args.operator,
        "notes": args.notes,
    }
    write_json(session_path, session_record)

    print("\nKratt 10-minute user-test recorder")
    print("=" * 44)
    print(f"Participant: {participant_id}")
    print(f"Session:     {session_id}")
    print(f"Output:      {base_dir}")
    print(f"Active:      {args.active_model}")
    print(f"Audio:       {'DRY RUN silence' if args.dry_run else 'microphone'}")
    print("\nControls: Enter = record next trial, q + Enter = stop.\n")

    trials = default_trials()
    total = len(trials)

    for idx, trial in enumerate(trials, start=1):
        print("-" * 72)
        print(f"[{idx:02d}/{total}] {trial.trial_id} ({trial.trial_type})")
        print(trial.prompt)
        print(f"Recording duration: {trial.duration_s:.1f}s")
        cmd = input("Press Enter to record, or q to quit: ").strip().lower()
        if cmd == "q":
            append_jsonl(
                trials_path,
                {
                    "type": "session_aborted",
                    "participant_id": participant_id,
                    "session_id": session_id,
                    "timestamp": iso_now(),
                    "next_trial_id": trial.trial_id,
                },
            )
            break

        print("Recording in 0.5s...")
        time.sleep(0.5)
        print("● recording")
        t_start = iso_now()
        monotonic_start = time.monotonic()
        audio = record_audio(trial.duration_s, args.device, args.dry_run)
        monotonic_end = time.monotonic()
        t_end = iso_now()
        print("✓ done")

        wav_name = f"{participant_id}_{trial.trial_id}_attempt{trial.attempt_number}.wav"
        wav_path = audio_dir / wav_name
        if args.audio_consent == "yes":
            sf.write(wav_path, audio, SAMPLE_RATE, subtype="PCM_16")
            audio_rel = str(wav_path.relative_to(base_dir))
        else:
            # Respect no-audio mode: write no WAV, only metadata row.
            audio_rel = None

        peak = float(np.max(np.abs(audio))) if audio.size else 0.0
        rms = float(np.sqrt(np.mean(np.square(audio)))) if audio.size else 0.0

        record = {
            "type": "trial",
            "participant_id": participant_id,
            "session_id": session_id,
            "trial_index": idx,
            **asdict(trial),
            "active_model": args.active_model,
            "audio_file": audio_rel,
            "sample_rate": SAMPLE_RATE,
            "channels": CHANNELS,
            "timestamp_start": t_start,
            "timestamp_end": t_end,
            "record_wall_duration_s": round(monotonic_end - monotonic_start, 3),
            "audio_peak_abs": round(peak, 6),
            "audio_rms": round(rms, 6),
            "audio_consent": args.audio_consent,
        }
        append_jsonl(trials_path, record)

    end_record = {
        "type": "session_end",
        "session_id": session_id,
        "participant_id": participant_id,
        "timestamp": iso_now(),
    }
    append_jsonl(trials_path, end_record)

    print("\nSession saved")
    print(f"  {session_path}")
    print(f"  {trials_path}")
    if args.audio_consent == "yes":
        print(f"  {audio_dir}")
    return base_dir


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record labelled Kratt user-test trials")
    parser.add_argument("participant_id", nargs="?", help="Participant ID, e.g. P01")
    parser.add_argument("--output-dir", default="output/user-tests", help="Base output dir")
    parser.add_argument("--active-model", default="v16c", help="User-visible active model tag")
    parser.add_argument("--audio-consent", choices=["yes", "no"], default="yes")
    parser.add_argument("--operator", default=os.environ.get("USER", ""))
    parser.add_argument("--notes", default="", help="Free-text session note stored in session.json")
    parser.add_argument("--session-id", default=None)
    parser.add_argument("--device", type=int, default=None, help="sounddevice input device id")
    parser.add_argument("--list-devices", action="store_true", help="Print audio devices and exit")
    parser.add_argument("--dry-run", action="store_true", help="Create silent WAVs without using microphone")
    parser.add_argument("--allow-existing", action="store_true", help="Allow writing into a non-empty participant dir")
    parser.add_argument("--new-session-subdir", action="store_true", help="Create participant/timestamp_session subdir")
    args = parser.parse_args(list(argv))

    if args.list_devices:
        list_devices()
        raise SystemExit(0)
    if not args.participant_id:
        parser.error("participant_id is required unless --list-devices is used")
    return args


def main(argv: list[str] | None = None) -> None:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    run_session(args)


if __name__ == "__main__":
    main()
