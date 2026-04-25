#!/usr/bin/env python3
"""Quick A/B test: does Neurokõne pronounce "Kule" and "Kuule" differently?

Generates 2 clips per speaker (1× "Kule Kratt", 1× "Kuule Kratt") at
speed=1.0, saves side by side for listening comparison + prints duration delta.
"""
import requests
import sys
from pathlib import Path
import struct

API = "https://api.tartunlp.ai/text-to-speech/v2"
SPEAKERS = ["mari", "tambet", "kalev", "albert"]  # subset for quick test
PAIRS = [
    ("Kuule Kratt", "kuule"),
    ("Kule Kratt", "kule"),
]

def wav_duration(path: Path) -> float:
    with open(path, "rb") as f:
        f.read(4)  # RIFF
        f.read(4)  # size
        f.read(4)  # WAVE
        while True:
            chunk_id = f.read(4)
            if not chunk_id:
                return 0
            chunk_size = struct.unpack("<I", f.read(4))[0]
            if chunk_id == b"fmt ":
                fmt = f.read(chunk_size)
                channels = struct.unpack("<H", fmt[2:4])[0]
                sr = struct.unpack("<I", fmt[4:8])[0]
            elif chunk_id == b"data":
                # assume 16-bit
                return chunk_size / (sr * channels * 2)
            else:
                f.read(chunk_size)

def main():
    out = Path(__file__).parent.parent / "raw" / "kule_vs_kuule_test"
    out.mkdir(parents=True, exist_ok=True)

    print(f"Output: {out}\n")
    print(f"{'Speaker':>10s}  {'Kuule dur':>10s}  {'Kule dur':>10s}  {'Delta ms':>10s}  {'Δ%':>6s}")
    print("-" * 56)

    for speaker in SPEAKERS:
        paths = {}
        for text, label in PAIRS:
            p = out / f"{speaker}_{label}_kratt.wav"
            if not p.exists():
                r = requests.post(API, json={"text": text, "speaker": speaker, "speed": 1.0}, timeout=30)
                if r.status_code != 200:
                    print(f"  ERROR {speaker} {label}: {r.status_code}")
                    continue
                p.write_bytes(r.content)
            paths[label] = p

        if "kuule" in paths and "kule" in paths:
            d_kuule = wav_duration(paths["kuule"])
            d_kule = wav_duration(paths["kule"])
            delta_ms = (d_kuule - d_kule) * 1000
            pct = (d_kuule - d_kule) / d_kuule * 100 if d_kuule else 0
            print(f"{speaker:>10s}  {d_kuule:>9.3f}s  {d_kule:>9.3f}s  {delta_ms:>+9.0f}ms  {pct:>+5.1f}%")

    print(f"\nFiles saved to: {out}")
    print("Listen: compare each speaker's kuule vs kule pair.")
    print("If durations differ by >50ms and vowel sounds shorter, Neurokõne IS differentiating.")

if __name__ == "__main__":
    main()
