#!/usr/bin/env python3
"""Record background audio from microphone for negative training data.

Records continuously, saving 5-minute WAV chunks. Designed to capture
real-world background audio from different microphone types.

Usage:
    python record_background.py --output data/raw/macbook_negatives --duration 7200
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import soundfile as sf

try:
    import sounddevice as sd
except ImportError:
    print("pip install sounddevice")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Record background audio for negative training")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--duration", type=int, default=7200, help="Total recording duration (seconds)")
    parser.add_argument("--chunk", type=int, default=300, help="Chunk size (seconds, default: 300 = 5min)")
    parser.add_argument("--sr", type=int, default=16000, help="Sample rate")
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    device_name = sd.query_devices(kind='input')['name']
    print(f"Recording from: {device_name}")
    print(f"Output: {out_dir}")
    print(f"Duration: {args.duration}s ({args.duration/3600:.1f}h)")
    print(f"Chunk size: {args.chunk}s")
    print(f"Sample rate: {args.sr}Hz")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print("Recording... (Ctrl+C to stop)")

    chunk_idx = 0
    total_recorded = 0

    try:
        while total_recorded < args.duration:
            remaining = min(args.chunk, args.duration - total_recorded)
            n_samples = remaining * args.sr

            audio = sd.rec(int(n_samples), samplerate=args.sr, channels=1, dtype='float32')
            sd.wait()

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bg_{chunk_idx:04d}_{ts}.wav"
            filepath = out_dir / filename
            sf.write(str(filepath), audio[:, 0], args.sr, subtype='PCM_16')

            total_recorded += remaining
            chunk_idx += 1
            elapsed_min = total_recorded / 60
            print(f"  Saved {filename} ({remaining}s, total: {elapsed_min:.0f}min)")

    except KeyboardInterrupt:
        pass

    print(f"\nDone. {chunk_idx} chunks, {total_recorded/60:.0f} min total")
    print(f"Output: {out_dir}")


if __name__ == "__main__":
    main()
