#!/usr/bin/env python3
"""Quick recorder - starts immediately, tag after.

Usage:
    python record_quick.py                    # record, tag after
    python record_quick.py --device 0         # specific mic
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 44100
OUTPUT_ROOT = Path(__file__).parent.parent / "raw" / "quick"


def rms_db(audio: np.ndarray) -> float:
    rms = float(np.sqrt(np.mean(audio.astype(np.float32) ** 2)))
    return 20 * np.log10(rms + 1e-10)


def main():
    parser = argparse.ArgumentParser(description="Quick recorder")
    parser.add_argument("--device", type=int, default=None)
    parser.add_argument("--sr", type=int, default=SAMPLE_RATE)
    args = parser.parse_args()

    dev = sd.query_devices(args.device or sd.default.device[0])
    print(f"  🎤 {dev['name']} | {args.sr}Hz | Ctrl+C peatamiseks")
    print()

    chunks: list[np.ndarray] = []
    chunk_s = 0.5
    chunk_frames = int(chunk_s * args.sr)
    start = time.time()

    try:
        while True:
            chunk = sd.rec(chunk_frames, samplerate=args.sr, channels=1, dtype="float32", device=args.device)
            sd.wait()
            chunks.append(chunk)
            elapsed = time.time() - start
            db = rms_db(chunk)
            bar = "█" * max(0, int((db + 50) / 2)) if db > -50 else ""
            print(f"\r  {elapsed:5.1f}s  {db:5.0f} dB  {bar:<25}", end="", flush=True)
    except KeyboardInterrupt:
        pass

    if not chunks:
        print("\n  Tühi salvestus.")
        return

    audio = np.concatenate(chunks)
    elapsed = len(audio) / args.sr
    db = rms_db(audio)

    print(f"\n\n  Salvestatud: {elapsed:.1f}s, {db:.0f} dB")
    print()

    # Playback option
    while True:
        resp = input("  [k]uula / [s]alvesta / [t]ühista? ").strip().lower()
        if resp == "k":
            print("  ▶ ...", end="", flush=True)
            sd.play(audio, samplerate=args.sr)
            sd.wait()
            print("\r       ")
        elif resp == "t":
            print("  Tühistatud.")
            return
        elif resp == "s":
            break

    # Tag
    name = input("  Failinimi (ilma .wav): ").strip()
    if not name:
        name = datetime.now().strftime("quick_%Y%m%d_%H%M%S")

    tags = input("  Sildid (komaga eraldatud, tühi OK): ").strip()
    notes = input("  Märkmed (tühi OK): ").strip()

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}.wav" if not name.endswith(".wav") else name
    filepath = OUTPUT_ROOT / filename

    # Avoid overwrite
    if filepath.exists():
        filepath = OUTPUT_ROOT / f"{Path(filename).stem}_{ts}.wav"

    sf.write(str(filepath), audio, args.sr, subtype="FLOAT")

    meta = {
        "name": name,
        "tags": [t.strip() for t in tags.split(",") if t.strip()] if tags else [],
        "notes": notes or None,
        "duration_s": round(elapsed, 1),
        "db_rms": round(db, 1),
        "sample_rate": args.sr,
        "device": dev["name"],
        "timestamp": ts,
    }
    meta_path = filepath.with_suffix(".wav.json")
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")

    print(f"\n  ✅ {filepath}")
    print(f"     {meta_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n  ❌ {e}")
        sys.exit(1)
