#!/usr/bin/env python3
"""Unified recording tool for wake word data collection.

Modes:
  pos    — Record "Kuule Kratt" samples (short clips, ENTER between each)
  neg    — Record continuous negative speech (one long recording, Ctrl+C to stop)
  hneg   — Record hard negatives (prompted phrases, short clips)

Usage:
    python record_session.py pos --name mattias --output ../raw/mattias/positive
    python record_session.py neg --name mattias --output ../raw/mattias/negative
    python record_session.py hneg --name mattias --output ../raw/mattias/hard_negative
"""

from __future__ import annotations

import argparse
import json
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

# Import hard negative phrases
sys.path.insert(0, str(Path(__file__).parent))
from hard_negative_phrases import (
    ALL_PHRASES,
    KUULE_KR,
    KUULE_RHYME,
    KUULE_OTHER,
    KUULE_K,
)

PHRASE = "Kuule Kratt"

# Hard negatives prioritized: closest confusables first
HNEG_PHRASES = KUULE_KR + KUULE_RHYME + KUULE_OTHER[:10] + KUULE_K[:10]


def rms_db(audio: np.ndarray) -> float:
    rms = float(np.sqrt(np.mean(audio.astype(np.float32) ** 2)))
    return 20 * np.log10(rms + 1e-10)


def record_clip(duration: float, sr: int, device: int | None = None) -> np.ndarray:
    """Record a fixed-length clip."""
    audio = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype="int16", device=device)
    sd.wait()
    return audio


def save_wav(audio: np.ndarray, path: Path, sr: int):
    sf.write(str(path), audio, sr)


def mode_pos(args):
    """Record wake word positive samples."""
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    print(f"\n  Salvestan '{PHRASE}' samplid")
    print(f"  Väljund:  {output}")
    print(f"  Pikkus:   {args.duration}s per klipp")
    print(f"  Mikrofon: {_device_name(args.device)}")
    print()
    print("  Nipid: muuda kaugust, kiirust, emotsiooni, häälekõrgust")
    print("  Ctrl+C lõpetamiseks\n")

    i = 0
    try:
        while True:
            input(f"  [{i+1}] ENTER → ütle \"{PHRASE}\" ")
            print("  🎤 ...", end="", flush=True)
            audio = record_clip(args.duration, args.sr, args.device)
            db = rms_db(audio)

            if db < -45:
                print(f"\r  ⚠️  Liiga vaikne ({db:.0f} dB) — proovi uuesti")
                continue

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = output / f"{args.name}_pos_{i:04d}_{ts}.wav"
            save_wav(audio, path, args.sr)
            print(f"\r  ✅ {path.name} ({db:.0f} dB)")
            i += 1
    except KeyboardInterrupt:
        print(f"\n\n  Valmis! {i} klippi salvestatud → {output}")


def mode_neg(args):
    """Record continuous negative speech (one long recording)."""
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    print(f"\n  Pidev salvestus — räägi eesti keeles vabalt")
    print(f"  ÄRA ütle \"{PHRASE}\"!")
    print(f"  Väljund:  {output}")
    print(f"  Mikrofon: {_device_name(args.device)}")
    print()
    print("  Ctrl+C kui valmis (soovitatav 1-3 min)")
    input("  ENTER alustamiseks... ")

    # Use streaming recording so Ctrl+C stops cleanly
    chunks: list[np.ndarray] = []
    sr = args.sr
    chunk_s = 1.0  # 1 second chunks
    chunk_frames = int(chunk_s * sr)

    print("  🎤 SALVESTAN... (Ctrl+C lõpetamiseks)\n")
    start = time.time()

    try:
        while True:
            chunk = sd.rec(chunk_frames, samplerate=sr, channels=1, dtype="int16", device=args.device)
            sd.wait()
            chunks.append(chunk)
            elapsed = time.time() - start
            db = rms_db(chunk)
            bar = "█" * max(0, int((db + 50) / 2)) if db > -50 else ""
            print(f"\r  {elapsed:5.0f}s  {db:5.0f} dB  {bar:<25}", end="", flush=True)
    except KeyboardInterrupt:
        pass

    if not chunks:
        print("\n  Midagi ei salvestatud.")
        return

    audio = np.concatenate(chunks)
    elapsed = len(audio) / sr
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = output / f"{args.name}_neg_{ts}_{elapsed:.0f}s.wav"
    save_wav(audio, path, sr)
    print(f"\n\n  ✅ {path.name} ({elapsed:.0f}s, {rms_db(audio):.0f} dB)")


def mode_hneg(args):
    """Record hard negative phrases (prompted, short clips)."""
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    phrases = HNEG_PHRASES
    print(f"\n  Hard negatives — foneetiliselt sarnased fraasid")
    print(f"  {len(phrases)} fraasi, {args.duration}s per klipp")
    print(f"  Väljund:  {output}")
    print(f"  Mikrofon: {_device_name(args.device)}")
    print()
    print("  Loe ette täpselt mis ekraanil näed")
    print("  [s]kip fraasi vahele jätmiseks, Ctrl+C lõpetamiseks\n")

    saved = 0
    try:
        for i, phrase in enumerate(phrases):
            resp = input(f"  [{i+1}/{len(phrases)}]  \"{phrase}\"  — ENTER / [s]kip ")
            if resp.strip().lower() == "s":
                continue

            print("  🎤 ...", end="", flush=True)
            audio = record_clip(args.duration, args.sr, args.device)
            db = rms_db(audio)

            if db < -45:
                print(f"\r  ⚠️  Liiga vaikne ({db:.0f} dB) — vahele jäetud")
                continue

            safe = phrase.replace(" ", "_").replace(",", "").replace("!", "").replace("?", "")
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = output / f"{args.name}_hneg_{i:04d}_{safe}_{ts}.wav"
            save_wav(audio, path, args.sr)
            print(f"\r  ✅ {path.name} ({db:.0f} dB)")
            saved += 1
    except KeyboardInterrupt:
        pass

    print(f"\n\n  Valmis! {saved} hard negative klippi → {output}")


def _device_name(device_id: int | None) -> str:
    if device_id is not None:
        return sd.query_devices(device_id)["name"]
    return sd.query_devices(sd.default.device[0])["name"]


def main():
    p = argparse.ArgumentParser(description="Kratt recording session")
    p.add_argument("mode", choices=["pos", "train", "neg", "hneg"], help="Recording mode")
    p.add_argument("-n", "--name", required=True, help="Speaker name")
    p.add_argument("-o", "--output", required=True, help="Output directory")
    p.add_argument("-d", "--duration", type=float, default=2.5, help="Clip duration (pos/hneg, default 2.5s)")
    p.add_argument("--sr", type=int, default=16000, help="Sample rate (default 16000)")
    p.add_argument("--device", type=int, default=None, help="Mic device ID")
    args = parser = p.parse_args()

    # train is alias for pos
    if args.mode == "train":
        args.mode = "pos"

    {"pos": mode_pos, "neg": mode_neg, "hneg": mode_hneg}[args.mode](args)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n  ❌ {e}")
        sys.exit(1)
