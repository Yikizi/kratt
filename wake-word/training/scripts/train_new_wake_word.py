#!/usr/bin/env python3
"""Train a local microWakeWord model from a new-wake-word wizard manifest.

This is an approachable local experiment command, not the thesis-grade Kuule
Kratt training pipeline. It stages a small flat dataset from the wizard output,
calls the existing generic microWakeWord training script, and copies the exported
streaming quantized TFLite model back to the wizard output directory.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
import shutil
import struct
import subprocess
import sys
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[3]
WAKE_WORD_ROOT = PROJECT_ROOT / "wake-word"
TRAIN_SCRIPT = WAKE_WORD_ROOT / "training" / "scripts" / "train_microwakeword_experiment.sh"
RUNS_DIR = WAKE_WORD_ROOT / "training" / "runs"
DEFAULT_NEGATIVE_DIR = WAKE_WORD_ROOT / "data" / "processed" / "negative_samples"
FALLBACK_NEGATIVE_DIR = WAKE_WORD_ROOT / "data" / "processed" / "negative_korvo2"
DEFAULT_AMBIENT_DIR = WAKE_WORD_ROOT / "data" / "processed" / "ambient_korvo2"
AUDIO_EXTS = {".wav", ".flac"}
SYNTHETIC_NEGATIVE_MAX = 300


def sibling_main_project_root() -> Path | None:
    """Return the real repo root when running inside .claude/worktrees/<name>."""
    parts = PROJECT_ROOT.parts
    if ".claude" in parts:
        idx = parts.index(".claude")
        candidate = Path(*parts[:idx])
        if (candidate / "wake-word" / "data").exists():
            return candidate
    return None


def candidate_data_dir(relative: str) -> list[Path]:
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


def first_audio_dir(candidates: list[Path]) -> Path | None:
    for candidate in candidates:
        if candidate.exists() and audio_files(candidate, recursive=True):
            return candidate
    return None


def now_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def safe_tag(raw: str) -> str:
    tag = re.sub(r"[^A-Za-z0-9_.-]+", "-", raw.strip()).strip("-._")
    return tag or f"local-{now_tag()}"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", required=True, help="Path to new-wake-word manifest.json")
    p.add_argument("--tag", default="", help="Model tag; default <slug>-local-<timestamp>")
    p.add_argument("--steps", default="1000,200", help="Training steps CSV (default: 1000,200)")
    p.add_argument("--learning-rates", default="0.001,0.0001", help="Learning rates CSV matching --steps")
    p.add_argument("--negative-class-weight", default="20", help="Penalty weight for negative examples (default: 20)")
    p.add_argument("--spec-augment", dest="spec_augment", action="store_true", default=True, help="Use SpecAugment during local training (default)")
    p.add_argument("--no-spec-augment", dest="spec_augment", action="store_false", help="Disable SpecAugment")
    p.add_argument("--hard-negative-mode", choices=["auto", "mixed", "separate"], default="auto", help="How to stage confusable/mined negatives (default: auto)")
    p.add_argument("--hard-negative-dir", action="append", default=[], help="Extra mined/real hard-negative WAV/FLAC dir; can be repeated")
    p.add_argument("--hard-negative-min-count", type=int, default=20, help="Minimum confusable/mined clips before auto uses separate hard-negative set")
    p.add_argument("--negative-dir", default="", help="Broad negative WAV/FLAC source")
    p.add_argument("--negative-limit", type=int, default=1000, help="Max broad negatives to stage")
    p.add_argument("--ambient-dir", default="", help="Ambient source dir; default ambient_korvo2 if present")
    p.add_argument("--ambient-limit", type=int, default=100, help="Max ambient clips to stage")
    p.add_argument("--clip-duration-ms", type=int, default=2000, help="Training window duration")
    p.add_argument("--target-minimization", default="10.0", help="microWakeWord target_minimization value")
    p.add_argument("--min-positive-count", type=int, default=10, help="Duplicate very small positive sets up to this count")
    p.add_argument("--include-tts-positives", dest="include_tts", action="store_true", default=True)
    p.add_argument("--no-tts-positives", dest="include_tts", action="store_false")
    p.add_argument("--max-tts-positive-ratio", type=float, default=3.0, help="Max TTS positives per real training positive (default: 3.0; 0 disables cap)")
    p.add_argument("--no-ambient", action="store_true", help="Do not stage ambient clips")
    p.add_argument("--dry-run", action="store_true", help="Print plan without staging or training")
    p.add_argument("--force", action="store_true", help="Allow reusing an existing training work dir")
    args = p.parse_args()
    if args.negative_limit < 1:
        raise SystemExit("--negative-limit must be >= 1")
    if args.ambient_limit < 0:
        raise SystemExit("--ambient-limit must be >= 0")
    if args.min_positive_count < 1:
        raise SystemExit("--min-positive-count must be >= 1")
    if args.max_tts_positive_ratio < 0:
        raise SystemExit("--max-tts-positive-ratio must be >= 0")
    if args.hard_negative_min_count < 1:
        raise SystemExit("--hard-negative-min-count must be >= 1")
    try:
        if float(args.negative_class_weight) <= 0:
            raise ValueError
    except ValueError:
        raise SystemExit("--negative-class-weight must be a positive number") from None
    return args


def load_manifest(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Manifest not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON manifest: {path}: {exc}")


def audio_files(root: Path, recursive: bool = True) -> list[Path]:
    if not root.exists():
        return []
    iterator = root.rglob("*") if recursive else root.glob("*")
    return sorted(p for p in iterator if p.is_file() and p.suffix.lower() in AUDIO_EXTS)


def resolve_relative(output_root: Path, raw: str) -> Path:
    p = Path(raw)
    if p.is_absolute():
        return p
    return output_root / p


def round_robin_by_voice(paths: list[Path], limit: int) -> list[Path]:
    if limit <= 0 or len(paths) <= limit:
        return paths[:]
    groups: dict[str, list[Path]] = {}
    order: list[str] = []
    for path in paths:
        key = path.stem.split("_", 1)[0]
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(path)
    selected: list[Path] = []
    while len(selected) < limit:
        progressed = False
        for key in order:
            if groups[key]:
                selected.append(groups[key].pop(0))
                progressed = True
                if len(selected) >= limit:
                    break
        if not progressed:
            break
    return selected


def discover_positive_files(
    manifest: dict,
    output_root: Path,
    include_tts: bool,
    max_tts_positive_ratio: float,
) -> tuple[list[Path], list[str]]:
    notes: list[str] = []
    real_files: list[Path] = []

    train_split = manifest.get("splits", {}).get("positive_real_train") or []
    if train_split:
        for raw in train_split:
            p = resolve_relative(output_root, str(raw))
            if p.exists() and p.suffix.lower() in AUDIO_EXTS:
                real_files.append(p)
        notes.append("Using manifest positive_real_train split; eval-smoke clips stay held out.")
    else:
        for row in manifest.get("real_audio", {}).get("clips", []):
            if row.get("accepted"):
                p = resolve_relative(output_root, str(row.get("path", "")))
                if p.exists() and p.suffix.lower() in AUDIO_EXTS:
                    real_files.append(p)

    if not real_files:
        fallback = audio_files(output_root / "audio" / "positive-real", recursive=True)
        if fallback:
            notes.append(
                "No accepted positives were found in manifest; using all audio/positive-real clips for local training."
            )
            real_files.extend(fallback)

    files = dedupe_paths(real_files)
    if include_tts:
        tts = audio_files(output_root / "audio" / "positive-tts", recursive=True)
        if tts:
            selected_tts = tts
            if files and max_tts_positive_ratio > 0:
                cap = max(1, int(len(files) * max_tts_positive_ratio))
                selected_tts = round_robin_by_voice(tts, cap)
                if len(selected_tts) < len(tts):
                    notes.append(
                        f"Capped TTS positives at {len(selected_tts)}/{len(tts)} "
                        f"(max_tts_positive_ratio={max_tts_positive_ratio:g}) so TTS does not swamp real positives."
                    )
            notes.append(f"Including {len(selected_tts)} TTS positive clips as local augmentation.")
            files.extend(selected_tts)

    return dedupe_paths(files), notes


def discover_confusable_negative_files(output_root: Path) -> list[Path]:
    return audio_files(output_root / "audio" / "negative-confusable-tts", recursive=True)


def dedupe_paths(paths: Iterable[Path]) -> list[Path]:
    seen: set[Path] = set()
    out: list[Path] = []
    for path in paths:
        key = path.resolve(strict=False)
        if key in seen:
            continue
        seen.add(key)
        out.append(path)
    return out


def choose_negative_dir(raw: str) -> Path | None:
    if raw:
        p = Path(raw).expanduser()
        candidate = p if p.is_absolute() else PROJECT_ROOT / p
        return candidate if audio_files(candidate, recursive=True) else None
    return first_audio_dir(
        candidate_data_dir("wake-word/data/processed/negative_samples")
        + candidate_data_dir("wake-word/data/processed/negative_korvo2")
        + candidate_data_dir("wake-word/data/processed/negative_macbook_segmented")
    )


def choose_ambient_dir(raw: str, disabled: bool) -> Path | None:
    if disabled:
        return None
    if raw:
        p = Path(raw).expanduser()
        candidate = p if p.is_absolute() else PROJECT_ROOT / p
        return candidate if audio_files(candidate, recursive=True) else None
    return first_audio_dir(
        candidate_data_dir("wake-word/data/processed/ambient_korvo2")
        + candidate_data_dir("wake-word/data/processed/negative_macbook_segmented")
    )


def link_or_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.symlink(src.resolve(), dst)
    except OSError:
        shutil.copy2(src, dst)


def write_int16_wav(path: Path, samples: list[int], sr: int = 16000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    clipped = [max(-32768, min(32767, int(v))) for v in samples]
    with wave.open(str(path), "wb") as fh:
        fh.setnchannels(1)
        fh.setsampwidth(2)
        fh.setframerate(sr)
        fh.writeframes(struct.pack("<" + "h" * len(clipped), *clipped))


def generate_starter_negatives(out_dir: Path, count: int, clip_duration_ms: int) -> list[Path]:
    """Generate harmless starter negatives when no local corpus is available.

    These are not a substitute for speech negatives, but they keep the public
    workflow from crashing on a fresh checkout and make a playable first model.
    """
    rng = random.Random(20260516)
    sr = 16000
    n = max(1, int(sr * clip_duration_ms / 1000.0))
    out_dir.mkdir(parents=True, exist_ok=True)
    files: list[Path] = []
    for i in range(1, count + 1):
        mode = i % 4
        samples: list[int] = []
        if mode == 0:
            # Very low-level room-noise-like floor.
            amp = rng.randint(80, 350)
            samples = [rng.randint(-amp, amp) for _ in range(n)]
        elif mode == 1:
            # Low-frequency hum + noise.
            freq = rng.uniform(80, 220)
            amp = rng.randint(250, 900)
            noise = rng.randint(40, 200)
            samples = [
                int(amp * math.sin(2 * math.pi * freq * t / sr) + rng.randint(-noise, noise))
                for t in range(n)
            ]
        elif mode == 2:
            # Silence with tiny dither.
            samples = [rng.randint(-25, 25) for _ in range(n)]
        else:
            # Broadband but low amplitude.
            amp = rng.randint(150, 700)
            prev = 0.0
            for _ in range(n):
                prev = 0.92 * prev + 0.08 * rng.uniform(-amp, amp)
                samples.append(int(prev))
        path = out_dir / f"generated_negative_{i:05d}.wav"
        write_int16_wav(path, samples, sr=sr)
        files.append(path)
    return files


def stage_flat(
    files: list[Path],
    dst_dir: Path,
    prefix: str,
    *,
    limit: int | None = None,
    duplicate_to: int = 0,
) -> tuple[int, int]:
    dst_dir.mkdir(parents=True, exist_ok=True)
    selected = files[:limit] if limit else files[:]
    created = 0
    duplicates = 0

    for index, src in enumerate(selected, start=1):
        dst = dst_dir / f"{prefix}_{index:05d}{src.suffix.lower()}"
        link_or_copy(src, dst)
        created += 1

    if selected and duplicate_to > created:
        index = created + 1
        cursor = 0
        while created < duplicate_to:
            src = selected[cursor % len(selected)]
            dst = dst_dir / f"{prefix}_dup_{index:05d}{src.suffix.lower()}"
            link_or_copy(src, dst)
            created += 1
            duplicates += 1
            index += 1
            cursor += 1

    return created, duplicates


def remove_existing(path: Path, force: bool) -> None:
    if not path.exists():
        return
    if not force:
        raise SystemExit(f"Training work dir already exists: {path}\nUse --tag another-tag or --force.")
    shutil.rmtree(path)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tail_text(path: Path, lines: int = 80) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except FileNotFoundError:
        return ""
    return "\n".join(data[-lines:])


def ensure_flock_or_shim(work_dir: Path, env: dict[str, str]) -> None:
    if shutil.which("flock", path=env.get("PATH")):
        return
    shim_dir = work_dir / "bin"
    shim_dir.mkdir(parents=True, exist_ok=True)
    shim = shim_dir / "flock"
    shim.write_text("#!/usr/bin/env bash\n# macOS local-training shim: no-op fd lock\nexit 0\n", encoding="utf-8")
    shim.chmod(0o755)
    env["PATH"] = f"{shim_dir}:{env.get('PATH', '')}"


def run_and_tee(cmd: list[str], log_path: Path) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["KRATT_ROOT"] = str(PROJECT_ROOT)
    ensure_flock_or_shim(log_path.parent, env)
    print(f"Training log: {log_path}")
    print("Training can take a while; full microWakeWord output is written to the log.")
    with log_path.open("w", encoding="utf-8") as log:
        log.write("$ " + " ".join(shlex_quote(x) for x in cmd) + "\n\n")
        log.flush()
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
        )
    if result.returncode != 0:
        print("\nTraining log tail:")
        print(tail_text(log_path, lines=80))
    return result.returncode


def shlex_quote(value: str) -> str:
    import shlex

    return shlex.quote(value)


def find_new_run_dir(experiment_name: str, before: set[Path]) -> Path | None:
    candidates = sorted(
        [p for p in RUNS_DIR.glob(f"{experiment_name}-*") if p.is_dir() and p not in before],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if candidates:
        return candidates[0]
    candidates = sorted(
        [p for p in RUNS_DIR.glob(f"{experiment_name}-*") if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def find_tflite(run_dir: Path) -> Path | None:
    preferred = run_dir / "tflite_stream_state_internal_quant" / "stream_state_internal_quant.tflite"
    if preferred.exists():
        return preferred
    matches = sorted(run_dir.rglob("*.tflite"), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def find_fp32_tflite(run_dir: Path) -> Path | None:
    preferred = run_dir / "tflite_stream_state_internal" / "stream_state_internal.tflite"
    if preferred.exists():
        return preferred
    matches = sorted(
        [p for p in run_dir.rglob("*.tflite") if "quant" not in str(p).lower()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return matches[0] if matches else None


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest).expanduser()
    if not manifest_path.is_absolute():
        manifest_path = (Path.cwd() / manifest_path).resolve()
    manifest = load_manifest(manifest_path)

    output_root = manifest_path.parent
    phrase = manifest.get("wizard", {}).get("phrase") or manifest.get("prompts", {}).get("target") or "wake word"
    slug = safe_tag(str(manifest.get("wizard", {}).get("slug") or output_root.name))
    tag = safe_tag(args.tag or f"{slug}-local-{now_tag()}")
    experiment_name = safe_tag(f"microwakeword-{tag}")

    positives, positive_notes = discover_positive_files(
        manifest,
        output_root,
        args.include_tts,
        args.max_tts_positive_ratio,
    )
    if not positives:
        raise SystemExit(
            "No positive WAV/FLAC files found. Run `kratt new-wake-word --phrase ... --count 10` "
            "or pass fixture audio first."
        )

    negative_source = choose_negative_dir(args.negative_dir)
    negatives = audio_files(negative_source, recursive=True) if negative_source else []
    confusable_negatives = discover_confusable_negative_files(output_root)
    for raw_hard_dir in args.hard_negative_dir:
        hard_dir = Path(raw_hard_dir).expanduser()
        if not hard_dir.is_absolute():
            hard_dir = (PROJECT_ROOT / hard_dir).resolve()
        extra_hard = audio_files(hard_dir, recursive=True)
        if extra_hard:
            confusable_negatives.extend(extra_hard)
            positive_notes.append(f"Including {len(extra_hard)} extra hard negatives from {hard_dir}.")
        else:
            positive_notes.append(f"Extra hard-negative dir had no audio files: {hard_dir}.")
    confusable_negatives = dedupe_paths(confusable_negatives)

    ambient_source = choose_ambient_dir(args.ambient_dir, args.no_ambient)
    ambient = audio_files(ambient_source, recursive=True) if ambient_source and args.ambient_limit > 0 else []

    use_separate_hard_negatives = bool(confusable_negatives) and (
        args.hard_negative_mode == "separate"
        or (args.hard_negative_mode == "auto" and len(confusable_negatives) >= args.hard_negative_min_count)
    )
    effective_hard_negative_mode = "separate" if use_separate_hard_negatives else "mixed"
    if confusable_negatives and use_separate_hard_negatives:
        positive_notes.append(
            f"Staging {len(confusable_negatives)} confusable negatives as a separate hard-negative set."
        )
    elif confusable_negatives:
        positive_notes.append(
            f"Mixing {len(confusable_negatives)} confusable negatives into the broad negative set."
        )

    work_dir = output_root / "training" / "local-runs" / tag
    pos_dir = work_dir / "positive"
    neg_dir = work_dir / "negative"
    amb_dir = work_dir / "ambient"
    hard_neg_dir = work_dir / "hard-negative"
    models_dir = output_root / "models"
    model_out = models_dir / f"{tag}.tflite"
    fp32_model_out = models_dir / f"{tag}.fp32.tflite"
    report_out = output_root / "reports" / f"train-{tag}.json"
    log_out = work_dir / "train.log"

    if not negatives:
        generated_count = min(args.negative_limit, SYNTHETIC_NEGATIVE_MAX)
        if generated_count < args.negative_limit:
            generated_count = max(generated_count, min(args.negative_limit, 50))
        generated_dir = output_root / "training" / "generated-negatives" / tag
        negatives = generate_starter_negatives(generated_dir, generated_count, args.clip_duration_ms)
        negative_source = generated_dir
        positive_notes.append(
            f"No broad negative corpus was found; generated {len(negatives)} starter non-speech negatives. "
            "For better models, pass --negative-dir with real speech/background negatives."
        )

    command = [
        "bash",
        str(TRAIN_SCRIPT),
        "--experiment-name",
        experiment_name,
        "--positive-dir",
        str(pos_dir),
        "--negative-dir",
        str(neg_dir),
        "--training-steps",
        args.steps,
        "--learning-rates",
        args.learning_rates,
        "--clip-duration-ms",
        str(args.clip_duration_ms),
        "--target-minimization",
        str(args.target_minimization),
        "--neg-class-weight",
        str(args.negative_class_weight),
        "--aug-profile",
        "moderate",
    ]
    if args.spec_augment:
        command.append("--spec-augment")
    if ambient:
        command.extend(["--ambient-dir", str(amb_dir)])
    if use_separate_hard_negatives:
        command.extend(["--hard-negative-dir", str(hard_neg_dir)])

    planned = {
        "tag": tag,
        "phrase": phrase,
        "manifest": str(manifest_path),
        "output_model": str(model_out),
        "output_model_fp32": str(fp32_model_out),
        "work_dir": str(work_dir),
        "experiment_name": experiment_name,
        "positive_source_count": len(positives),
        "include_tts_positives": bool(args.include_tts),
        "max_tts_positive_ratio": args.max_tts_positive_ratio,
        "negative_source": str(negative_source),
        "negative_source_count": len(negatives),
        "negative_limit": args.negative_limit,
        "negative_class_weight": args.negative_class_weight,
        "spec_augment": bool(args.spec_augment),
        "confusable_negative_count": len(confusable_negatives),
        "extra_hard_negative_dirs": [str(Path(p).expanduser()) for p in args.hard_negative_dir],
        "hard_negative_mode": effective_hard_negative_mode,
        "hard_negative_min_count": args.hard_negative_min_count,
        "ambient_source": str(ambient_source) if ambient_source else None,
        "ambient_source_count": len(audio_files(ambient_source, recursive=True)) if ambient_source else 0,
        "ambient_limit": args.ambient_limit,
        "duplicate_tiny_positives_to": args.min_positive_count,
        "notes": positive_notes + [
            "Local starter mode: small datasets can overfit and benchmarks may not be held out.",
            "The command exports a playable TFLite, not a production-quality model.",
        ],
        "command": command,
    }

    print("=== Train local new wake-word model ===")
    print(f"Phrase:      {phrase}")
    print(f"Tag:         {tag}")
    print(f"Manifest:    {manifest_path}")
    print(f"Positives:   {len(positives)}")
    print(f"Negatives:   {min(len(negatives), args.negative_limit)} + confusable {len(confusable_negatives)} ({effective_hard_negative_mode})")
    print(f"Negative source: {negative_source}")
    print(f"Neg class w: {args.negative_class_weight}; SpecAugment: {bool(args.spec_augment)}")
    print(f"Ambient:     {min(len(ambient), args.ambient_limit) if ambient else 0}")
    if ambient:
        print(f"Ambient source:  {ambient_source}")
    print(f"Output:      {model_out}")
    for note in planned["notes"]:
        print(f"Note:        {note}")

    if args.dry_run:
        print("\nDry-run command:")
        print(" ".join(shlex_quote(x) for x in command))
        print("\nDry-run complete: no files staged and no training started.")
        return 0

    remove_existing(work_dir, args.force)
    work_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    pos_created, pos_dups = stage_flat(
        positives,
        pos_dir,
        "positive",
        duplicate_to=max(args.min_positive_count, len(positives)),
    )
    neg_selected = negatives[: args.negative_limit]
    if not use_separate_hard_negatives:
        neg_selected = neg_selected + confusable_negatives
    neg_created, _ = stage_flat(neg_selected, neg_dir, "negative")
    hard_neg_created = 0
    if use_separate_hard_negatives:
        hard_neg_created, _ = stage_flat(confusable_negatives, hard_neg_dir, "hard_negative")
    amb_created = 0
    if ambient:
        amb_created, _ = stage_flat(ambient[: args.ambient_limit], amb_dir, "ambient")

    planned.update(
        {
            "staged_positive_count": pos_created,
            "staged_positive_duplicates": pos_dups,
            "staged_negative_count": neg_created,
            "staged_hard_negative_count": hard_neg_created,
            "staged_ambient_count": amb_created,
            "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
    )
    write_json(work_dir / "plan.json", planned)

    before = {p for p in RUNS_DIR.glob(f"{experiment_name}-*") if p.is_dir()}
    rc = run_and_tee(command, log_out)
    planned["return_code"] = rc
    planned["finished_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    planned["log"] = str(log_out)

    if rc != 0:
        write_json(report_out, planned)
        print(f"\nTraining failed with exit code {rc}. Log: {log_out}", file=sys.stderr)
        return rc

    run_dir = find_new_run_dir(experiment_name, before)
    if run_dir is None:
        planned["error"] = "training completed but run directory was not found"
        write_json(report_out, planned)
        raise SystemExit("Training completed but run directory was not found")

    tflite = find_tflite(run_dir)
    if tflite is None:
        planned["run_dir"] = str(run_dir)
        planned["error"] = "training completed but no .tflite was found"
        write_json(report_out, planned)
        raise SystemExit(f"Training completed but no .tflite was found under {run_dir}")

    shutil.copy2(tflite, model_out)
    planned.update({"run_dir": str(run_dir), "source_tflite": str(tflite), "output_tflite": str(model_out)})

    fp32_tflite = find_fp32_tflite(run_dir)
    if fp32_tflite is not None:
        shutil.copy2(fp32_tflite, fp32_model_out)
        planned.update({"source_tflite_fp32": str(fp32_tflite), "output_tflite_fp32": str(fp32_model_out)})
    else:
        planned.setdefault("notes", []).append("FP32 streaming TFLite export was not found.")

    write_json(report_out, planned)

    print("\n=== Done ===")
    print(f"TFLite: {model_out}")
    if fp32_tflite is not None:
        print(f"FP32:   {fp32_model_out}")
    print(f"Run:    {run_dir}")
    print(f"Report: {report_out}")
    print("\nNext:")
    print(f"  ./cli/kratt new-wake-word --manifest {manifest_path} --benchmark --model {model_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
