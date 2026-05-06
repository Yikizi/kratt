#!/usr/bin/env python3
"""Score one or more WAV clips/directories with a microWakeWord TFLite model.

Small manual-testing helper for side experiments: records/fixtures can be scored
with the same `microwakeword.inference.Model.predict_clip` path used by the
benchmark scripts, without running the full benchmark suite.
"""
from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

import numpy as np
import soundfile as sf

from microwakeword.inference import Model

STEP_MS = 10
DEFAULT_MA_WINDOW = 5
BASE = Path(__file__).resolve().parent.parent


def model_path_from_tag(tag: str) -> Path:
    d = BASE / "models" / f"kuule-kratt-{tag}"
    preferred = d / f"kuule_kratt_{tag}.tflite"
    if preferred.exists():
        return preferred
    fallback = d / "model.tflite"
    if fallback.exists():
        return fallback
    return preferred


def resolve_model_tag(input_tag: str) -> tuple[str, Path]:
    tag = input_tag.removeprefix("kuule-kratt-")
    aliases = {
        "checkpoint-faph": "checkpoint-faph-v18d-clean96-pw96x4",
        "checkpoint-faph10": "checkpoint-faph10-v18d-clean96-pw96x4",
        "checkpoint-faph20": "checkpoint-faph20-v18d-clean96-pw96x4",
    }
    tag = aliases.get(tag, tag)

    path = model_path_from_tag(tag)
    if path.exists():
        return tag, path

    matches: list[tuple[str, Path]] = []
    for d in sorted((BASE / "models").glob(f"kuule-kratt-{tag}*")):
        candidate = d.name.removeprefix("kuule-kratt-")
        candidate_path = model_path_from_tag(candidate)
        if candidate_path.exists():
            matches.append((candidate, candidate_path))

    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        msg = "Ambiguous model alias: {}\nMatches:\n{}".format(
            input_tag, "\n".join(f"  {m[0]}" for m in matches)
        )
        raise SystemExit(msg)
    raise SystemExit(f"Model not found: {input_tag}")


def discover_wavs(paths: list[str]) -> list[Path]:
    wavs: list[Path] = []
    for raw in paths:
        p = Path(raw).expanduser()
        if not p.is_absolute():
            # Prefer cwd-relative paths, but allow wake-word-relative paths too.
            p = Path.cwd() / p
            if not p.exists() and (BASE / raw).exists():
                p = BASE / raw
        if p.is_dir():
            wavs.extend(sorted(p.rglob("*.wav")))
        elif p.is_file() and p.suffix.lower() == ".wav":
            wavs.append(p)
        else:
            raise SystemExit(f"No WAV file/dir found: {raw}")
    # De-duplicate while preserving order.
    seen: set[Path] = set()
    out: list[Path] = []
    for wav in wavs:
        key = wav.resolve()
        if key not in seen:
            seen.add(key)
            out.append(wav)
    return out


def load_16k(path: Path) -> np.ndarray:
    audio, sr = sf.read(str(path), always_2d=False)
    if getattr(audio, "ndim", 1) > 1:
        audio = audio[:, 0]
    audio = audio.astype(np.float32)
    if sr != 16000:
        import librosa

        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
    return (np.clip(audio, -1.0, 1.0) * 32767.0).astype(np.int16)


def moving_average(values: np.ndarray, window: int) -> np.ndarray:
    if window <= 1 or values.size < window:
        return values
    return np.convolve(values, np.ones(window, dtype=np.float32) / window, mode="valid")


def reset(model: Model) -> None:
    try:
        model.reset_states()
    except Exception:
        pass


def fmt_score(value: float) -> str:
    return f"{value:.6f}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", help="Model tag/alias, e.g. v19a, v19a-kratt-only, v16c")
    parser.add_argument("paths", nargs="+", help="WAV files or directories to score")
    parser.add_argument("--thresholds", "--threshold", type=float, nargs="+", default=[0.99, 0.996], help="Decision thresholds to summarize")
    parser.add_argument("--ma-window", type=int, default=DEFAULT_MA_WINDOW, help="Moving-average window, benchmark default 5")
    parser.add_argument("--top", type=int, default=8, help="Show N lowest/highest clips")
    parser.add_argument("--per-clip", action="store_true", help="Print every clip score")
    parser.add_argument("--output", type=Path, default=None, help="Optional CSV output path")
    args = parser.parse_args()

    if args.ma_window <= 0:
        raise SystemExit("--ma-window must be positive")

    tag, model_path = resolve_model_tag(args.model)
    wavs = discover_wavs(args.paths)
    if not wavs:
        raise SystemExit("No WAV files found")

    print(f"Model: {tag}")
    print(f"Path:  {model_path}")
    print(f"Clips: {len(wavs)}")
    print(f"MA window: {args.ma_window}")

    model = Model(str(model_path))
    rows: list[dict[str, str]] = []
    scores: list[float] = []
    for index, wav in enumerate(wavs, start=1):
        pcm = load_16k(wav)
        raw = np.array(model.predict_clip(pcm, step_ms=STEP_MS), dtype=np.float32)
        smoothed = moving_average(raw, args.ma_window)
        max_raw = float(raw.max()) if raw.size else 0.0
        max_ma = float(smoothed.max()) if smoothed.size else max_raw
        reset(model)
        scores.append(max_ma)
        rows.append(
            {
                "index": str(index),
                "path": str(wav),
                "model": tag,
                "max_score_ma": fmt_score(max_ma),
                "max_score_raw": fmt_score(max_raw),
                "duration_s": f"{len(pcm) / 16000.0:.3f}",
            }
        )

    arr = np.array(scores, dtype=np.float32)
    print("\nSummary")
    print(f"  mean={mean(scores):.3f} min={arr.min():.3f} median={np.median(arr):.3f} max={arr.max():.3f}")
    qs = np.quantile(arr, [0.10, 0.25, 0.75, 0.90, 0.95])
    print("  q10={:.3f} q25={:.3f} q75={:.3f} q90={:.3f} q95={:.3f}".format(*qs))
    for threshold in args.thresholds:
        hits = int((arr >= threshold).sum())
        print(f"  >= {threshold:g}: {hits}/{len(arr)} = {100.0 * hits / len(arr):.1f}%")

    ordered = sorted(rows, key=lambda r: float(r["max_score_ma"]))
    if args.per_clip:
        print("\nPer clip")
        for r in rows:
            print(f"  {r['max_score_ma']}  {r['path']}")
    else:
        n = max(args.top, 0)
        if n:
            print(f"\nLowest {min(n, len(rows))}")
            for r in ordered[:n]:
                print(f"  {r['max_score_ma']}  {r['path']}")
            print(f"\nHighest {min(n, len(rows))}")
            for r in reversed(ordered[-n:]):
                print(f"  {r['max_score_ma']}  {r['path']}")

    if args.output:
        output = args.output.expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nWrote {output}")
    elif os.environ.get("KRATT_SCORE_WRITE_DEFAULT"):
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output = BASE.parent / "output" / "clip-scores" / f"score_{tag}_{ts}.csv"
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nWrote {output}")


if __name__ == "__main__":
    main()
