#!/usr/bin/env python3
"""A/B compare two sherpa-onnx STT models on live mic input.

Records N utterances and transcribes each with both models,
printing results side-by-side with timing.

Usage:
    python compare_stt_models.py            # default 5 utterances
    python compare_stt_models.py -n 8       # 8 utterances
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

MODELS = {
    "base": PROJECT_ROOT / "wake-word/models/kiirkirjutaja-int8",
    "large": PROJECT_ROOT / "wake-word/models/kiirkirjutaja-large-int8",
}


def build_recognizer(model_dir: str):
    import sherpa_onnx

    return sherpa_onnx.OnlineRecognizer.from_transducer(
        tokens=f"{model_dir}/tokens.txt",
        encoder=f"{model_dir}/encoder.int8.onnx",
        decoder=f"{model_dir}/decoder.int8.onnx",
        joiner=f"{model_dir}/joiner.int8.onnx",
        num_threads=2,
        sample_rate=SAMPLE_RATE,
        feature_dim=80,
        enable_endpoint_detection=True,
        rule1_min_trailing_silence=2.0,
        rule2_min_trailing_silence=1.0,
        rule3_min_utterance_length=300,
        decoding_method="modified_beam_search",
    )


def transcribe(recognizer, audio: np.ndarray) -> tuple[str, float]:
    tail = np.zeros(int(0.3 * SAMPLE_RATE), dtype=np.float32)
    full = np.concatenate([audio, tail])
    stream = recognizer.create_stream()
    stream.accept_waveform(SAMPLE_RATE, full)
    t0 = time.monotonic()
    while recognizer.is_ready(stream):
        recognizer.decode_stream(stream)
    elapsed = time.monotonic() - t0
    return recognizer.get_result(stream).strip(), elapsed


def record_utterance(duration: float = 5.0) -> np.ndarray:
    print(f"  🎤 Recording {duration:.0f}s... speak now!")
    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )
    sd.wait()
    return audio.flatten()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, default=5, help="Number of utterances")
    parser.add_argument("--duration", type=float, default=5.0, help="Seconds per recording")
    args = parser.parse_args()

    print("Loading models...")
    recognizers = {}
    for name, path in MODELS.items():
        t0 = time.monotonic()
        recognizers[name] = build_recognizer(str(path))
        print(f"  {name}: loaded in {time.monotonic() - t0:.1f}s")

    print(f"\n{'='*70}")
    print(f"A/B STT comparison — {args.n} utterances, {args.duration}s each")
    print(f"{'='*70}\n")

    results = []
    for i in range(1, args.n + 1):
        print(f"--- Utterance {i}/{args.n} ---")
        audio = record_utterance(args.duration)

        row = {"i": i}
        for name, rec in recognizers.items():
            text, elapsed = transcribe(rec, audio)
            row[f"{name}_text"] = text
            row[f"{name}_time"] = elapsed
            print(f"  {name:>5}: ({elapsed:.2f}s) \"{text}\"")

        same = row["base_text"].lower() == row["large_text"].lower()
        print(f"  match: {'YES' if same else 'NO — DIFFERENT'}")
        results.append(row)
        print()

    # Summary
    print(f"{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    matches = sum(1 for r in results if r["base_text"].lower() == r["large_text"].lower())
    print(f"Agreement: {matches}/{len(results)}")

    for name in MODELS:
        times = [r[f"{name}_time"] for r in results]
        avg = sum(times) / len(times)
        print(f"{name:>5} avg decode time: {avg:.3f}s")

    print("\nFull results:")
    for r in results:
        b = r["base_text"] or "(empty)"
        l = r["large_text"] or "(empty)"
        if b.lower() != l.lower():
            print(f"  #{r['i']}: base=\"{b}\" | large=\"{l}\"  <-- DIFF")
        else:
            print(f"  #{r['i']}: \"{b}\"")


if __name__ == "__main__":
    main()
