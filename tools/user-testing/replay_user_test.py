#!/usr/bin/env python3
"""Replay Kratt user-test WAVs through frozen microWakeWord models.

The recorder intentionally saves labelled WAVs without doing inference. This
script turns those sessions into replayable evidence: identical user utterances
scored across the frozen model set, with one JSONL row per trial/model and a
small recall/FPR summary.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import warnings
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Iterable

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
warnings.filterwarnings("ignore", message=r".*tf\.lite\.Interpreter is deprecated.*")

import numpy as np
import soundfile as sf

try:
    from pymicro_features import MicroFrontend
except ImportError as exc:  # pragma: no cover - environment diagnostic
    raise SystemExit(
        "Missing pymicro_features. Run via `kratt replay-user-test`, which uses "
        "wake-word/.venv-microwakeword."
    ) from exc

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    import tensorflow.lite as tflite  # type: ignore

ROOT = Path(__file__).resolve().parents[2]
WAKE_WORD_DIR = ROOT / "wake-word"
MODELS_DIR = WAKE_WORD_DIR / "models"
SAMPLE_RATE = 16_000
FRAME_MS = 10
WARMUP_FRAMES = 50
DEFAULT_PREPAD_SILENCE_S = WARMUP_FRAMES * FRAME_MS / 1000
DEFAULT_MODELS = ["v16c", "expert-a", "expert-b2", "v6-residual", "v10", "v15"]
DEFAULT_COMBOS = ["expert-a+expert-b2"]
MODEL_ALIASES = {
    "checkpoint-faph": "checkpoint-faph-v18d-clean96-pw96x4",
    "checkpoint-faph10": "checkpoint-faph10-v18d-clean96-pw96x4",
    "checkpoint-faph20": "checkpoint-faph20-v18d-clean96-pw96x4",
}


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
    exact_path = model_path_from_tag(tag)
    if exact_path.exists():
        return tag, exact_path

    matches = [candidate for candidate in available_model_tags() if candidate.startswith(tag)]
    if len(matches) == 1:
        resolved = matches[0]
        return resolved, model_path_from_tag(resolved)
    if len(matches) > 1:
        raise ValueError(f"ambiguous model alias {tag!r}: {', '.join(matches)}")
    raise ValueError(f"model not found: {tag}")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def load_audio_mono(path: Path, target_sr: int = SAMPLE_RATE) -> np.ndarray:
    audio, sr = sf.read(path, dtype="float32", always_2d=False)
    if audio.ndim == 2:
        audio = np.mean(audio, axis=1)
    if sr != target_sr:
        old_x = np.arange(audio.shape[0], dtype=np.float64)
        new_len = int(round(audio.shape[0] * target_sr / sr))
        new_x = np.linspace(0, max(audio.shape[0] - 1, 0), new_len, dtype=np.float64)
        audio = np.interp(new_x, old_x, audio).astype(np.float32)
    return np.asarray(audio, dtype=np.float32)


def audio_to_feature_frames(
    audio: np.ndarray,
    *,
    sample_rate: int = SAMPLE_RATE,
    frame_ms: int = FRAME_MS,
    prepad_silence_s: float = DEFAULT_PREPAD_SILENCE_S,
) -> list[np.ndarray]:
    frame_samples = int(sample_rate * frame_ms / 1000)
    if frame_samples <= 0:
        raise ValueError("frame_samples must be positive")
    if audio.size == 0:
        return []
    prepad_samples = int(round(prepad_silence_s * sample_rate))
    if prepad_samples > 0:
        audio = np.pad(audio, (prepad_samples, 0))
    remainder = audio.size % frame_samples
    if remainder:
        audio = np.pad(audio, (0, frame_samples - remainder))
    pcm = (audio * 32768.0).clip(-32768, 32767).astype(np.int16)

    frontend = MicroFrontend()
    process_fn = getattr(frontend, "process_samples", None) or getattr(frontend, "ProcessSamples", None)
    frames: list[np.ndarray] = []
    for start in range(0, pcm.size, frame_samples):
        chunk = pcm[start:start + frame_samples].tobytes()
        result = process_fn(chunk)
        if result.features:
            frames.append(np.array(result.features, dtype=np.float32))
    return frames


class StreamingModel:
    def __init__(self, tag: str, model_path: Path):
        self.tag = tag
        self.model_path = model_path
        self.interpreter = tflite.Interpreter(model_path=str(model_path))
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.audio_input_idx = 0
        self.frame_count = 0
        self.reset()

    def reset(self) -> None:
        self.frame_count = 0
        reset_all = getattr(self.interpreter, "reset_all_variables", None)
        if callable(reset_all):
            try:
                reset_all()
            except Exception:
                # Some interpreters expose the method even for graphs without variables.
                pass
        for detail in self.input_details:
            self.interpreter.set_tensor(detail["index"], np.zeros(detail["shape"], dtype=detail["dtype"]))

    def process_features(self, features: np.ndarray) -> float:
        expected_shape = self.input_details[self.audio_input_idx]["shape"]
        features = features.reshape(expected_shape)

        inp_dtype = self.input_details[self.audio_input_idx]["dtype"]
        if inp_dtype == np.int8:
            scale, zero_point = self.input_details[self.audio_input_idx]["quantization"]
            features = (features / scale + zero_point).clip(-128, 127).astype(np.int8)

        self.interpreter.set_tensor(self.input_details[self.audio_input_idx]["index"], features)
        self.interpreter.invoke()
        self.frame_count += 1

        if self.frame_count <= WARMUP_FRAMES:
            return 0.0

        output = self.interpreter.get_tensor(self.output_details[0]["index"])
        out_dtype = self.output_details[0]["dtype"]
        if out_dtype in (np.int8, np.uint8):
            scale, zero_point = self.output_details[0]["quantization"]
            return float(((output.astype(np.float32) - zero_point) * scale).flat[0])
        return float(output.flatten()[0])

    def score_frames(self, frames: list[np.ndarray], *, ma_window: int) -> tuple[list[float], list[float]]:
        self.reset()
        raw_scores: list[float] = []
        ma_scores: list[float] = []
        rolling: deque[float] = deque(maxlen=ma_window)
        for features in frames:
            raw = max(0.0, self.process_features(features.copy()))
            raw_scores.append(raw)
            rolling.append(raw)
            ma_scores.append(sum(rolling) / len(rolling))
        return raw_scores, ma_scores


def first_trigger_ms(scores: list[float], threshold: float, *, prepad_frames: int = 0) -> int | None:
    for index, score in enumerate(scores):
        if score >= threshold:
            return max(0, (index - prepad_frames) * FRAME_MS)
    return None


def summarize_scores(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["model_name"])].append(row)

    summary: list[dict[str, Any]] = []
    for model_name, model_rows in sorted(grouped.items(), key=lambda item: natural_key(item[0])):
        positives = [row for row in model_rows if row.get("expected_wake") is True]
        negatives = [row for row in model_rows if row.get("expected_wake") is False]
        pos_hits = sum(1 for row in positives if row.get("triggered"))
        neg_hits = sum(1 for row in negatives if row.get("triggered"))
        summary.append(
            {
                "model_name": model_name,
                "threshold": model_rows[0].get("threshold") if model_rows else None,
                "positive_hits": pos_hits,
                "positive_total": len(positives),
                "positive_recall": pos_hits / len(positives) if positives else None,
                "negative_false_accepts": neg_hits,
                "negative_total": len(negatives),
                "negative_fpr": neg_hits / len(negatives) if negatives else None,
            }
        )
    return summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def replay_session(
    session_dir: Path,
    *,
    models: list[StreamingModel],
    combos: list[tuple[str, list[str]]],
    threshold: float,
    ma_window: int,
    prepad_silence_s: float,
    output_dir: Path,
) -> tuple[Path, Path, list[dict[str, Any]]]:
    session_dir = session_dir.expanduser().resolve()
    session = load_json(session_dir / "session.json")
    trial_rows = [row for row in load_jsonl(session_dir / "trials.jsonl") if row.get("type") == "trial"]

    out_base = output_dir.expanduser().resolve() / session["participant_id"] / session["session_id"]
    out_base.mkdir(parents=True, exist_ok=True)
    scores_path = out_base / "replay_scores.jsonl"
    summary_path = out_base / "replay_summary.csv"

    score_rows: list[dict[str, Any]] = []
    missing_audio = 0
    with scores_path.open("w", encoding="utf-8") as out:
        out.write(json.dumps({
            "type": "replay_start",
            "session_dir": str(session_dir),
            "participant_id": session.get("participant_id"),
            "session_id": session.get("session_id"),
            "models": [model.tag for model in models],
            "combos": [name for name, _ in combos],
            "threshold": threshold,
            "ma_window": ma_window,
            "frame_ms": FRAME_MS,
            "warmup_frames": WARMUP_FRAMES,
            "prepad_silence_s": prepad_silence_s,
        }, ensure_ascii=False) + "\n")

        for trial in trial_rows:
            audio_rel = trial.get("audio_file")
            if not audio_rel:
                missing_audio += 1
                continue
            audio_path = session_dir / str(audio_rel)
            if not audio_path.exists():
                missing_audio += 1
                continue

            audio = load_audio_mono(audio_path)
            frames = audio_to_feature_frames(audio, prepad_silence_s=prepad_silence_s)
            prepad_frames = int(round(prepad_silence_s * 1000 / FRAME_MS))
            per_model: dict[str, dict[str, list[float]]] = {}
            for model in models:
                raw_scores, ma_scores = model.score_frames(frames, ma_window=ma_window)
                per_model[model.tag] = {"raw": raw_scores, "ma": ma_scores}
                trigger_ms = first_trigger_ms(ma_scores, threshold, prepad_frames=prepad_frames)
                row = {
                    "type": "replay_score",
                    "participant_id": session.get("participant_id"),
                    "session_id": session.get("session_id"),
                    "trial_index": trial.get("trial_index"),
                    "trial_id": trial.get("trial_id"),
                    "trial_type": trial.get("trial_type"),
                    "expected_wake": trial.get("expected_wake"),
                    "expected_intent": trial.get("expected_intent"),
                    "audio_file": audio_rel,
                    "audio_source": trial.get("audio_source"),
                    "audio_fixture_file": trial.get("audio_fixture_file"),
                    "session_dry_run": session.get("dry_run"),
                    "session_audio_fixture_dir": session.get("audio_fixture_dir"),
                    "model_name": model.tag,
                    "is_combo": False,
                    "combo_members": None,
                    "threshold": threshold,
                    "prepad_silence_s": prepad_silence_s,
                    "max_score_raw": round(max(raw_scores) if raw_scores else 0.0, 6),
                    "max_score_ma": round(max(ma_scores) if ma_scores else 0.0, 6),
                    "triggered": trigger_ms is not None,
                    "trigger_time_ms": trigger_ms,
                }
                score_rows.append(row)
                out.write(json.dumps(row, ensure_ascii=False) + "\n")

            for combo_name, members in combos:
                if not all(member in per_model for member in members):
                    continue
                lengths = [len(per_model[member]["ma"]) for member in members]
                if not lengths:
                    continue
                n_frames = min(lengths)
                combo_scores = [min(per_model[member]["ma"][i] for member in members) for i in range(n_frames)]
                trigger_ms = first_trigger_ms(combo_scores, threshold, prepad_frames=prepad_frames)
                row = {
                    "type": "replay_score",
                    "participant_id": session.get("participant_id"),
                    "session_id": session.get("session_id"),
                    "trial_index": trial.get("trial_index"),
                    "trial_id": trial.get("trial_id"),
                    "trial_type": trial.get("trial_type"),
                    "expected_wake": trial.get("expected_wake"),
                    "expected_intent": trial.get("expected_intent"),
                    "audio_file": audio_rel,
                    "audio_source": trial.get("audio_source"),
                    "audio_fixture_file": trial.get("audio_fixture_file"),
                    "session_dry_run": session.get("dry_run"),
                    "session_audio_fixture_dir": session.get("audio_fixture_dir"),
                    "model_name": combo_name,
                    "is_combo": True,
                    "combo_members": members,
                    "threshold": threshold,
                    "prepad_silence_s": prepad_silence_s,
                    "max_score_raw": None,
                    "max_score_ma": round(max(combo_scores) if combo_scores else 0.0, 6),
                    "triggered": trigger_ms is not None,
                    "trigger_time_ms": trigger_ms,
                }
                score_rows.append(row)
                out.write(json.dumps(row, ensure_ascii=False) + "\n")

        out.write(json.dumps({"type": "replay_end", "missing_audio_trials": missing_audio}, ensure_ascii=False) + "\n")

    summary_rows = summarize_scores(score_rows)
    write_csv(summary_path, summary_rows)
    return scores_path, summary_path, summary_rows


def parse_combos(values: list[str]) -> list[tuple[str, list[str]]]:
    combos: list[tuple[str, list[str]]] = []
    for value in values:
        members = [part.strip().removeprefix("kuule-kratt-") for part in value.split("+") if part.strip()]
        if len(members) < 2:
            raise ValueError(f"combo must contain at least two models joined by '+': {value!r}")
        resolved_members = [resolve_model_tag(member)[0] for member in members]
        combos.append(("+".join(resolved_members), resolved_members))
    return combos


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay Kratt user-test WAVs through frozen models")
    parser.add_argument("session_dirs", nargs="+", help="Session directories from kratt user-test")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS, help="Model tags to replay")
    parser.add_argument("--combos", nargs="*", default=DEFAULT_COMBOS, help="Consensus combos, e.g. expert-a+expert-b2; use --combos with no values to disable")
    parser.add_argument("--threshold", type=float, default=0.996, help="Frozen replay threshold for model and min-consensus scores")
    parser.add_argument("--ma-window", type=int, default=5, help="Moving average window in frames")
    parser.add_argument("--prepad-silence-s", type=float, default=DEFAULT_PREPAD_SILENCE_S, help="Silence prepended before each clip to warm streaming model state. Default: 0.5")
    parser.add_argument("--output-dir", default="output/user-test-replay", help="Replay output root")
    return parser.parse_args(list(argv))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.ma_window <= 0:
        raise SystemExit("--ma-window must be positive")
    if args.prepad_silence_s < 0:
        raise SystemExit("--prepad-silence-s must be >= 0")

    resolved_models: list[StreamingModel] = []
    for requested in args.models:
        tag, path = resolve_model_tag(requested)
        resolved_models.append(StreamingModel(tag, path))

    combos = parse_combos(args.combos)
    print("Replay models:", ", ".join(model.tag for model in resolved_models))
    if combos:
        print("Combos:", ", ".join(name for name, _ in combos))
    print(f"Threshold: {args.threshold}  MA window: {args.ma_window}  prepad: {args.prepad_silence_s:.2f}s")

    for session_dir_arg in args.session_dirs:
        scores_path, summary_path, summary_rows = replay_session(
            Path(session_dir_arg),
            models=resolved_models,
            combos=combos,
            threshold=args.threshold,
            ma_window=args.ma_window,
            prepad_silence_s=args.prepad_silence_s,
            output_dir=Path(args.output_dir),
        )
        print(f"\n{Path(session_dir_arg).expanduser().resolve()}")
        print(f"  scores:  {scores_path}")
        print(f"  summary: {summary_path}")
        for row in summary_rows:
            recall = row["positive_recall"]
            fpr = row["negative_fpr"]
            recall_s = "n/a" if recall is None else f"{recall * 100:.1f}% ({row['positive_hits']}/{row['positive_total']})"
            fpr_s = "n/a" if fpr is None else f"{fpr * 100:.1f}% ({row['negative_false_accepts']}/{row['negative_total']})"
            print(f"  {row['model_name']:<28} recall={recall_s:<16} hard-neg FPR={fpr_s}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
