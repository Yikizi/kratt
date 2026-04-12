#!/usr/bin/env python3
"""Deterministic false-trigger fuzzer for microWakeWord models.

Purpose:
- Systematically generate non-speech rhythmic/percussive clips (e.g. finger tapping)
- Score them with the SAME frontend + streaming TFLite path as live_test_tflite.py
- Rank clips by wake-word score and export top adversarial triggers

Example:
    python deterministic_trigger_fuzzer.py \
      --model ../models/kuule-kratt-v10/kuule_kratt_v10.tflite \
      --output-dir ./fuzz_runs/v10_taps
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from itertools import product
from pathlib import Path

import numpy as np
import soundfile as sf

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    import tensorflow.lite as tflite

from pymicro_features import MicroFrontend


STEP_MS = 10
SAMPLES_PER_STEP = 160  # 16kHz * 10ms


@dataclass(frozen=True)
class Candidate:
    bpm: int
    subdivision: int
    pulse_kind: str
    carrier_hz: int
    burst_ms: int
    decay_ms: int
    noise_low_hz: int
    noise_high_hz: int
    rms: float


class LiveStyleScorer:
    """Matches live_test_tflite.py style scoring path."""

    def __init__(self, model_path: Path):
        self.interpreter = tflite.Interpreter(model_path=str(model_path))
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.frontend = MicroFrontend()
        self.process_fn = (
            getattr(self.frontend, "process_samples", None)
            or getattr(self.frontend, "ProcessSamples", None)
        )

    def _reset_state(self) -> None:
        for detail in self.input_details:
            self.interpreter.set_tensor(
                detail["index"], np.zeros(detail["shape"], dtype=detail["dtype"])
            )

    def score_clip(self, audio_float32: np.ndarray) -> np.ndarray:
        self._reset_state()

        pcm = (np.clip(audio_float32, -1.0, 1.0) * 32768.0)
        pcm = np.clip(pcm, -32768, 32767).astype(np.int16)

        scores: list[float] = []
        for i in range(0, len(pcm) - SAMPLES_PER_STEP + 1, SAMPLES_PER_STEP):
            chunk = pcm[i : i + SAMPLES_PER_STEP].tobytes()
            result = self.process_fn(chunk)
            if not result.features:
                continue

            features = np.array(result.features, dtype=np.float32)
            expected_shape = self.input_details[0]["shape"]
            features = features.reshape(expected_shape)

            inp_dtype = self.input_details[0]["dtype"]
            if inp_dtype == np.int8:
                scale, zero_point = self.input_details[0]["quantization"]
                features = (features / scale + zero_point).clip(-128, 127).astype(np.int8)
            elif inp_dtype == np.uint8:
                scale, zero_point = self.input_details[0]["quantization"]
                features = (features / scale + zero_point).clip(0, 255).astype(np.uint8)

            self.interpreter.set_tensor(self.input_details[0]["index"], features)
            self.interpreter.invoke()

            output = self.interpreter.get_tensor(self.output_details[0]["index"])
            out_dtype = self.output_details[0]["dtype"]
            if out_dtype in (np.int8, np.uint8):
                scale, zero_point = self.output_details[0]["quantization"]
                prob = float(((output.astype(np.float32) - zero_point) * scale).flat[0])
            else:
                prob = float(output.flatten()[0])
            scores.append(prob)

        return np.array(scores, dtype=np.float32)


def stable_seed(base_seed: int, candidate: Candidate) -> int:
    payload = json.dumps(candidate.__dict__, sort_keys=True)
    digest = hashlib.sha256(f"{base_seed}:{payload}".encode("utf-8")).hexdigest()
    return int(digest[:16], 16) % (2**32)


def band_limited_noise(length: int, sr: int, low_hz: int, high_hz: int, rng: np.random.Generator) -> np.ndarray:
    noise = rng.standard_normal(length).astype(np.float32)
    spec = np.fft.rfft(noise)
    freqs = np.fft.rfftfreq(length, d=1.0 / sr)
    mask = (freqs >= low_hz) & (freqs <= high_hz)
    spec[~mask] = 0
    out = np.fft.irfft(spec, n=length).astype(np.float32)
    peak = float(np.max(np.abs(out)))
    if peak > 1e-9:
        out /= peak
    return out


def synthesize_tapping(candidate: Candidate, *, duration_s: float, sr: int, seed: int) -> np.ndarray:
    """Generate deterministic rhythmic tapping/percussive waveform."""
    total = int(duration_s * sr)
    y = np.zeros(total, dtype=np.float32)

    rng = np.random.default_rng(stable_seed(seed, candidate))

    interval_s = 60.0 / (candidate.bpm * candidate.subdivision)
    start_s = 0.15
    pulse_len = int(max(0.02, (candidate.burst_ms + candidate.decay_ms * 4) / 1000.0) * sr)

    pulse_times = np.arange(start_s, duration_s, interval_s)

    for i, t in enumerate(pulse_times):
        start = int(t * sr)
        if start >= total:
            break

        length = min(pulse_len, total - start)
        n = np.arange(length, dtype=np.float32)

        attack = max(1, int(candidate.burst_ms * sr / 1000.0))
        env = np.exp(-n / max(1.0, candidate.decay_ms * sr / 1000.0)).astype(np.float32)
        env[:attack] *= np.linspace(0.0, 1.0, attack, dtype=np.float32)

        tone = np.sin(2.0 * np.pi * candidate.carrier_hz * n / float(sr)).astype(np.float32)
        noise = band_limited_noise(
            length,
            sr,
            candidate.noise_low_hz,
            candidate.noise_high_hz,
            rng,
        )

        if candidate.pulse_kind == "tone":
            src = tone
        elif candidate.pulse_kind == "noise":
            src = noise
        elif candidate.pulse_kind == "hybrid":
            src = 0.65 * noise + 0.35 * tone
        else:
            raise ValueError(f"Unknown pulse_kind: {candidate.pulse_kind}")

        # Accent every 4th pulse to mimic human tapping pattern
        accent = 1.35 if (i % 4 == 0) else 1.0

        y[start : start + length] += accent * src * env

    # Normalize to target RMS while preserving peaks
    peak = float(np.max(np.abs(y)))
    if peak > 1e-9:
        y /= peak
    rms_now = float(np.sqrt(np.mean(y * y) + 1e-12))
    y *= candidate.rms / max(rms_now, 1e-9)

    # keep in [-1,1]
    y = np.clip(y, -1.0, 1.0)
    return y.astype(np.float32)


def detections_with_cooldown(scores: np.ndarray, threshold: float, cooldown_s: float) -> int:
    count = 0
    last_t = -1e9
    for i, p in enumerate(scores):
        t = i * (STEP_MS / 1000.0)
        if p >= threshold and (t - last_t) >= cooldown_s:
            count += 1
            last_t = t
    return count


def threshold_slug(threshold: float) -> str:
    return str(threshold).replace(".", "p")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", required=True, help="Path to streaming TFLite model")
    p.add_argument("--output-dir", required=True, help="Directory for CSV + top trigger WAVs")

    p.add_argument("--duration-s", type=float, default=6.0)
    p.add_argument("--sample-rate", type=int, default=16000)
    p.add_argument("--thresholds", type=float, nargs="+", default=[0.97, 0.98, 0.99])
    p.add_argument("--cooldown-s", type=float, default=2.0)
    p.add_argument("--seed", type=int, default=42)

    p.add_argument("--bpm", type=int, nargs="+", default=[90, 120, 150, 180])
    p.add_argument("--subdivisions", type=int, nargs="+", default=[1, 2])
    p.add_argument("--pulse-kinds", nargs="+", default=["noise", "hybrid", "tone"], choices=["noise", "hybrid", "tone"])
    p.add_argument("--carrier-hz", type=int, nargs="+", default=[350, 700])
    p.add_argument("--burst-ms", type=int, nargs="+", default=[6, 12])
    p.add_argument("--decay-ms", type=int, nargs="+", default=[25, 60])
    p.add_argument("--noise-low-hz", type=int, nargs="+", default=[900, 1500])
    p.add_argument("--noise-high-hz", type=int, nargs="+", default=[3500, 5500])
    p.add_argument("--rms", type=float, nargs="+", default=[0.01, 0.03])

    p.add_argument("--max-candidates", type=int, default=500, help="0 = evaluate full cartesian grid")
    p.add_argument("--top-k", type=int, default=50, help="How many highest-scoring clips to export as WAV")
    p.add_argument("--save-all-wavs", action="store_true", help="Save every generated clip (large output)")
    return p.parse_args()


def build_candidates(args: argparse.Namespace) -> list[Candidate]:
    out: list[Candidate] = []

    for (
        bpm,
        subdiv,
        kind,
        carrier,
        burst,
        decay,
        low,
        high,
        rms,
    ) in product(
        args.bpm,
        args.subdivisions,
        args.pulse_kinds,
        args.carrier_hz,
        args.burst_ms,
        args.decay_ms,
        args.noise_low_hz,
        args.noise_high_hz,
        args.rms,
    ):
        if low >= high:
            continue
        out.append(
            Candidate(
                bpm=bpm,
                subdivision=subdiv,
                pulse_kind=kind,
                carrier_hz=carrier,
                burst_ms=burst,
                decay_ms=decay,
                noise_low_hz=low,
                noise_high_hz=high,
                rms=rms,
            )
        )

    if args.max_candidates > 0:
        out = out[: args.max_candidates]
    return out


def main() -> None:
    args = parse_args()

    model_path = Path(args.model).expanduser().resolve()
    if not model_path.exists():
        raise SystemExit(f"Model not found: {model_path}")

    output_dir = Path(args.output_dir).expanduser().resolve()
    top_dir = output_dir / "top_triggers"
    all_dir = output_dir / "all_wavs"
    output_dir.mkdir(parents=True, exist_ok=True)
    top_dir.mkdir(parents=True, exist_ok=True)
    if args.save_all_wavs:
        all_dir.mkdir(parents=True, exist_ok=True)

    candidates = build_candidates(args)
    if not candidates:
        raise SystemExit("No valid candidate combinations")

    print(f"Model: {model_path}")
    print(f"Candidates: {len(candidates)}")
    print(f"Thresholds: {args.thresholds}")

    scorer = LiveStyleScorer(model_path)

    rows: list[dict] = []
    wave_cache: dict[int, np.ndarray] = {}

    for idx, cand in enumerate(candidates, 1):
        y = synthesize_tapping(
            cand,
            duration_s=args.duration_s,
            sr=args.sample_rate,
            seed=args.seed,
        )

        scores = scorer.score_clip(y)
        if scores.size == 0:
            continue

        k = int(np.argmax(scores))
        row = {
            "candidate_idx": idx,
            "max_prob": float(scores[k]),
            "t_max_s": k * (STEP_MS / 1000.0),
            "mean_prob": float(scores.mean()),
            "p95_prob": float(np.quantile(scores, 0.95)),
            "frames": int(scores.size),
            **cand.__dict__,
        }

        for th in args.thresholds:
            slug = threshold_slug(th)
            row[f"frames_ge_{slug}"] = int(np.sum(scores >= th))
            row[f"detections_ge_{slug}"] = detections_with_cooldown(
                scores,
                threshold=th,
                cooldown_s=args.cooldown_s,
            )

        rows.append(row)
        wave_cache[idx] = y

        if args.save_all_wavs:
            out_name = f"cand_{idx:04d}_max_{row['max_prob']:.3f}.wav"
            sf.write(str(all_dir / out_name), y, args.sample_rate, subtype="PCM_16")

        if idx % 50 == 0 or idx == len(candidates):
            print(f"  processed {idx}/{len(candidates)}")

    if not rows:
        raise SystemExit("No scored rows produced")

    rows.sort(key=lambda r: r["max_prob"], reverse=True)

    csv_path = output_dir / "fuzzer_results.csv"
    fields = list(rows[0].keys())
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    top_n = min(args.top_k, len(rows))
    top_rows = rows[:top_n]
    for rank, r in enumerate(top_rows, 1):
        idx = int(r["candidate_idx"])
        y = wave_cache[idx]
        out_name = (
            f"rank_{rank:03d}_idx_{idx:04d}_max_{r['max_prob']:.3f}_"
            f"bpm{r['bpm']}_sub{r['subdivision']}_{r['pulse_kind']}.wav"
        )
        sf.write(str(top_dir / out_name), y, args.sample_rate, subtype="PCM_16")

    summary = {
        "model": str(model_path),
        "candidates": len(candidates),
        "thresholds": args.thresholds,
        "cooldown_s": args.cooldown_s,
        "max_prob_best": float(rows[0]["max_prob"]),
        "max_prob_median": float(np.median(np.array([r["max_prob"] for r in rows], dtype=np.float32))),
        "top_k_exported": top_n,
        "csv": str(csv_path),
        "top_dir": str(top_dir),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    print()
    print(f"CSV: {csv_path}")
    print(f"Top triggers: {top_dir}")
    print(f"Best max_prob: {rows[0]['max_prob']:.4f}")


if __name__ == "__main__":
    main()
