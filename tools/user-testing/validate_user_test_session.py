#!/usr/bin/env python3
"""Validate Kratt user-test recorder session artifacts.

Checks that a recorded session has the expected machine-readable files and, when
raw audio consent was granted, one usable WAV per trial. This is intentionally a
small dependency-free guard so pilot sessions can be checked immediately before
any thesis analysis or offline model replay.
"""

from __future__ import annotations

import argparse
import json
import sys
import wave
from collections import Counter
from pathlib import Path
from typing import Iterable, Any

EXPECTED_SAMPLE_RATE = 16_000
EXPECTED_CHANNELS = 1
EXPECTED_TRIAL_COUNT = 17

REQUIRED_TRIAL_FIELDS = {
    "type",
    "participant_id",
    "session_id",
    "trial_index",
    "trial_id",
    "trial_type",
    "prompt",
    "expected_text",
    "expected_wake",
    "attempt_number",
    "duration_s",
    "active_model",
    "audio_file",
    "sample_rate",
    "channels",
    "timestamp_start",
    "timestamp_end",
    "record_wall_duration_s",
    "audio_peak_abs",
    "audio_rms",
    "audio_consent",
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - CLI diagnostic path
        raise ValueError(f"failed to read JSON {path}: {exc}") from exc


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL at {path}:{lineno}: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"JSONL row is not an object at {path}:{lineno}")
            rows.append(row)
    except FileNotFoundError as exc:
        raise ValueError(f"missing trials.jsonl: {path}") from exc
    return rows


def wav_info(path: Path) -> tuple[int, int, float]:
    with wave.open(str(path), "rb") as wav:
        sample_rate = wav.getframerate()
        channels = wav.getnchannels()
        duration_s = wav.getnframes() / sample_rate if sample_rate else 0.0
    return sample_rate, channels, duration_s


def validate_session(
    base_dir: Path,
    *,
    expected_trial_count: int,
    duration_tolerance_s: float,
    min_rms_warning: float,
) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    base_dir = base_dir.expanduser().resolve()

    session_path = base_dir / "session.json"
    trials_path = base_dir / "trials.jsonl"
    audio_dir = base_dir / "audio"

    session: dict[str, Any] = {}
    if not session_path.exists():
        errors.append(f"missing session.json: {session_path}")
    else:
        try:
            session = load_json(session_path)
        except ValueError as exc:
            errors.append(str(exc))

    try:
        rows = load_jsonl(trials_path)
    except ValueError as exc:
        errors.append(str(exc))
        rows = []

    trial_rows = [row for row in rows if row.get("type") == "trial"]
    row_types = Counter(str(row.get("type")) for row in rows)
    trial_types = Counter(str(row.get("trial_type")) for row in trial_rows)

    if expected_trial_count >= 0 and len(trial_rows) != expected_trial_count:
        errors.append(f"expected {expected_trial_count} trial rows, found {len(trial_rows)}")

    if not rows or rows[-1].get("type") != "session_end":
        warnings.append("trials.jsonl does not end with a session_end row")

    seen_trial_keys: set[tuple[str, int]] = set()
    wav_count = len(list(audio_dir.glob("*.wav"))) if audio_dir.exists() else 0
    consent_counts = Counter(str(row.get("audio_consent")) for row in trial_rows)
    audio_source_counts = Counter(str(row.get("audio_source", "legacy_unknown")) for row in trial_rows)

    for idx, row in enumerate(trial_rows, start=1):
        trial_id = str(row.get("trial_id", f"#{idx}"))
        missing = sorted(REQUIRED_TRIAL_FIELDS - set(row))
        if missing:
            errors.append(f"{trial_id}: missing trial fields: {', '.join(missing)}")

        if row.get("trial_index") != idx:
            errors.append(f"{trial_id}: trial_index={row.get('trial_index')} but expected {idx}")

        key = (trial_id, int(row.get("attempt_number", -1)))
        if key in seen_trial_keys:
            errors.append(f"{trial_id}: duplicate trial_id/attempt_number {key}")
        seen_trial_keys.add(key)

        if row.get("sample_rate") != EXPECTED_SAMPLE_RATE:
            errors.append(f"{trial_id}: sample_rate={row.get('sample_rate')} expected {EXPECTED_SAMPLE_RATE}")
        if row.get("channels") != EXPECTED_CHANNELS:
            errors.append(f"{trial_id}: channels={row.get('channels')} expected {EXPECTED_CHANNELS}")

        audio_consent = row.get("audio_consent")
        audio_file = row.get("audio_file")
        if audio_consent == "yes":
            if not audio_file:
                errors.append(f"{trial_id}: audio_consent=yes but audio_file is empty")
                continue
            wav_path = base_dir / str(audio_file)
            if not wav_path.exists():
                errors.append(f"{trial_id}: missing WAV {wav_path}")
                continue
            try:
                sr, channels, wav_duration = wav_info(wav_path)
            except Exception as exc:  # pragma: no cover - CLI diagnostic path
                errors.append(f"{trial_id}: failed to inspect WAV {wav_path}: {exc}")
                continue
            expected_duration = float(row.get("duration_s", 0.0))
            if sr != EXPECTED_SAMPLE_RATE or channels != EXPECTED_CHANNELS:
                errors.append(f"{trial_id}: WAV format {sr}Hz/{channels}ch expected {EXPECTED_SAMPLE_RATE}Hz/{EXPECTED_CHANNELS}ch")
            if abs(wav_duration - expected_duration) > duration_tolerance_s:
                errors.append(
                    f"{trial_id}: WAV duration {wav_duration:.3f}s differs from expected {expected_duration:.3f}s"
                )
            if not bool(session.get("dry_run")) and float(row.get("audio_rms", 0.0)) < min_rms_warning:
                warnings.append(
                    f"{trial_id}: very low audio_rms={float(row.get('audio_rms', 0.0)):.6f}; check mic/device"
                )
        elif audio_consent == "no":
            if audio_file is not None:
                errors.append(f"{trial_id}: audio_consent=no but audio_file={audio_file!r}")
        else:
            errors.append(f"{trial_id}: unexpected audio_consent={audio_consent!r}")

    if trial_rows and all(row.get("audio_consent") == "no" for row in trial_rows) and wav_count:
        errors.append(f"audio_consent=no for all trials, but found {wav_count} WAV files in {audio_dir}")
    if trial_rows and any(row.get("audio_consent") == "yes" for row in trial_rows) and wav_count != sum(
        1 for row in trial_rows if row.get("audio_consent") == "yes"
    ):
        errors.append(
            f"WAV count {wav_count} does not match audio-consented trial count "
            f"{sum(1 for row in trial_rows if row.get('audio_consent') == 'yes')}"
        )

    summary = {
        "session_dir": str(base_dir),
        "participant_id": session.get("participant_id"),
        "session_id": session.get("session_id"),
        "active_model": session.get("active_model"),
        "dry_run": session.get("dry_run"),
        "row_types": dict(row_types),
        "trial_types": dict(trial_types),
        "audio_consent": dict(consent_counts),
        "audio_source": dict(audio_source_counts),
        "audio_fixture_dir": session.get("audio_fixture_dir"),
        "trial_count": len(trial_rows),
        "wav_count": wav_count,
    }
    return errors, warnings, summary


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Kratt user-test session artifacts")
    parser.add_argument("session_dirs", nargs="+", help="Session directories containing session.json + trials.jsonl")
    parser.add_argument("--expected-trials", type=int, default=EXPECTED_TRIAL_COUNT, help="Expected trial row count; use -1 to disable")
    parser.add_argument("--duration-tolerance-s", type=float, default=0.02)
    parser.add_argument("--min-rms-warning", type=float, default=0.0001, help="Warn below this RMS for non-dry-run consented WAVs")
    parser.add_argument("--fail-on-warnings", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON summary")
    return parser.parse_args(list(argv))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    all_results: list[dict[str, Any]] = []
    exit_code = 0

    for session_dir_arg in args.session_dirs:
        session_dir = Path(session_dir_arg)
        errors, warnings, summary = validate_session(
            session_dir,
            expected_trial_count=args.expected_trials,
            duration_tolerance_s=args.duration_tolerance_s,
            min_rms_warning=args.min_rms_warning,
        )
        result = {"summary": summary, "errors": errors, "warnings": warnings}
        all_results.append(result)

        if not args.json:
            print(f"\n{summary['session_dir']}")
            print("-" * min(80, len(summary["session_dir"])))
            print(f"participant:  {summary['participant_id']}")
            print(f"session:      {summary['session_id']}")
            print(f"active model: {summary['active_model']}")
            print(f"dry run:      {summary['dry_run']}")
            print(f"trials:       {summary['trial_count']}  {summary['trial_types']}")
            print(f"audio:        {summary['wav_count']} WAVs  consent={summary['audio_consent']} source={summary['audio_source']}")
            if summary.get("audio_fixture_dir"):
                print(f"fixture dir:  {summary['audio_fixture_dir']}")
            for warning in warnings:
                print(f"WARNING: {warning}")
            for error in errors:
                print(f"ERROR: {error}")
            if not errors and not (args.fail_on_warnings and warnings):
                print("OK")

        if errors or (args.fail_on_warnings and warnings):
            exit_code = 1

    if args.json:
        print(json.dumps(all_results, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
