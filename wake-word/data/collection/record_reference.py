#!/usr/bin/env python3
"""Record voice reference audio for TTS voice cloning.

Displays a phonetically balanced Estonian text (IPA standard "Põhjatuul ja Päike"
+ supplementary paragraph) and records high-quality audio for XTTS v2 cloning.

Usage:
    python record_reference.py --name pereema --output ../raw/voice_references
    python record_reference.py --name pereema --device 2   # specific mic
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

# IPA standard phonetically balanced Estonian text (Asu & Teras, JIPA 2009)
# + supplementary paragraph for missing phonemes (š, ž, interrogatives, quantity)
REFERENCE_TEXT = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Loe see tekst ette rahulikult ja loomulikult:

  Ükskord vaidlesid põhjatuul ja päike selle üle, kumb
  neist on tugevam. Just siis tuli mööda teed rändaja,
  seljas soe mantel. Põhjatuul ja päike leppisid kokku,
  et see, kellel esimesena õnnestub sundida rändajat
  mantlit seljast võtma, on teisest tugevam. Põhjatuul
  puhuski kõigest jõust, aga mida rohkem ta puhus, seda
  enam koomale tõmbas rändaja oma mantli hõlmad. Lõpuks
  loobus põhjatuul katsest. Siis hakkas aga päike nii
  soojalt paistma, et rändaja kohe oma mantli seljast
  võttis. Ja nõnda pidigi põhjatuul tunnistama, et päike
  on tast tugevam. Kas sa jõudsid juba šampust tuua või
  žürii seda ei lubanud? Saada mulle sada lehte — ma
  pean need kõik hääletüüpide kaupa läbi vaatama, süües
  samal ajal küpsist ja jõhvikaid.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

SAMPLE_RATE = 44100  # High quality for reference (XTTS resamples internally)
CHANNELS = 1


def list_devices():
    """Print available audio input devices."""
    print("\nSaadaolevad mikrofonid:")
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if d["max_input_channels"] > 0:
            marker = " ←  vaikimisi" if i == sd.default.device[0] else ""
            print(f"  [{i}] {d['name']} ({d['max_input_channels']}ch, {int(d['default_samplerate'])}Hz){marker}")
    print()


def record_until_enter(device: int | None = None) -> np.ndarray:
    """Record continuously until user presses ENTER. Shows live timer."""
    import threading

    chunks: list[np.ndarray] = []
    chunk_s = 0.5
    chunk_frames = int(chunk_s * SAMPLE_RATE)
    stop = threading.Event()

    def wait_for_enter():
        input()
        stop.set()

    t = threading.Thread(target=wait_for_enter, daemon=True)
    t.start()

    start = time.time()
    while not stop.is_set():
        chunk = sd.rec(chunk_frames, samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32", device=device)
        sd.wait()
        chunks.append(chunk)
        elapsed = time.time() - start
        rms = float(np.sqrt(np.mean(chunk**2)))
        db = 20 * np.log10(rms + 1e-10)
        bar = "█" * max(0, int((db + 55) / 2)) if db > -55 else ""
        print(f"\r  ⏱  {elapsed:5.1f}s  {db:5.0f} dB  {bar:<20}  (ENTER lõpetamiseks)", end="", flush=True)

    print()
    return np.concatenate(chunks) if chunks else np.array([], dtype=np.float32)


def audio_stats(audio: np.ndarray) -> dict:
    """Compute audio quality metrics."""
    rms = float(np.sqrt(np.mean(audio**2)))
    peak = float(np.max(np.abs(audio)))
    db_rms = 20 * np.log10(rms + 1e-10)
    db_peak = 20 * np.log10(peak + 1e-10)
    # Detect silence ratio (frames below -50dB)
    frame_energy = np.abs(audio.flatten())
    silence_ratio = float(np.mean(frame_energy < 0.003))
    return {
        "rms": rms,
        "peak": peak,
        "db_rms": db_rms,
        "db_peak": db_peak,
        "silence_ratio": silence_ratio,
        "duration_s": len(audio) / SAMPLE_RATE,
    }


def quality_verdict(stats: dict) -> tuple[str, str]:
    """Return (emoji, message) quality assessment.

    Thresholds calibrated for MacBook/laptop mics at 20-40cm distance.
    Normal speech at this range: RMS -45 to -30 dB, peak -25 to -10 dB.
    """
    if stats["db_peak"] < -35:
        return "❌", "Liiga vaikne — kas mikrofon on õige? Proovi lähemale."
    if stats["db_rms"] > -5:
        return "❌", "Liiga vali / clipping! Mine mikrofonist kaugemale."
    if stats["db_peak"] < -28:
        return "⚠️", "Veidi vaikne, aga kasutatav."
    return "✅", "Hea kvaliteet!"


def play_audio(audio: np.ndarray):
    """Play back recorded audio."""
    sd.play(audio, samplerate=SAMPLE_RATE)
    sd.wait()


def main():
    parser = argparse.ArgumentParser(description="Salvesta voice cloning referentsaudio")
    parser.add_argument("-n", "--name", help="Kõneleja nimi (nt pereema, isa, mattias)")
    parser.add_argument("-o", "--output", default="../raw/voice_references", help="Väljundkaust")
    parser.add_argument("--device", type=int, default=None, help="Mikrofoni device ID (vt --list-devices)")
    parser.add_argument("--list-devices", action="store_true", help="Näita saadaolevaid mikrofone")
    args = parser.parse_args()

    if args.list_devices:
        list_devices()
        return

    if not args.name:
        parser.error("--name on kohustuslik (v.a --list-devices)")

    output_dir = Path(args.output) / args.name
    output_dir.mkdir(parents=True, exist_ok=True)

    print("━" * 60)
    print("  KRATT — Voice Cloning Referentsaudio Salvestamine")
    print("━" * 60)
    print(f"\n  Kõneleja:  {args.name}")
    print(f"  Kvaliteet: {SAMPLE_RATE}Hz, 32-bit float, mono")
    print(f"  Väljund:   {output_dir}/")

    if args.device is not None:
        dev_info = sd.query_devices(args.device)
        print(f"  Mikrofon:  [{args.device}] {dev_info['name']}")
    else:
        dev_info = sd.query_devices(sd.default.device[0])
        print(f"  Mikrofon:  {dev_info['name']} (vaikimisi)")

    print(REFERENCE_TEXT)

    print("  JUHISED:")
    print("  • Loe tekst ette rahulikult ja loomulikult")
    print("  • Ära kiirusta — parem loomuliku tempoga")
    print("  • Mikrofon 20-30cm kaugusele")
    print("  • Kui tekst lõpeb, räägi vabalt edasi (soovitatav 25-40s kokku)")
    print()

    take = 1
    while True:
        input(f"  ENTER alustamiseks (take {take})... ")

        # No countdown - people start speaking immediately
        print("  SALVESTAN - vajuta ENTER kui valmis\n")

        audio = record_until_enter(device=args.device)
        if len(audio) == 0:
            print("  Tühi salvestus, proovi uuesti.")
            continue
        stats = audio_stats(audio)
        emoji, message = quality_verdict(stats)

        print(f"\n  {emoji} {message}")
        print(f"     RMS: {stats['db_rms']:.1f} dB | Peak: {stats['db_peak']:.1f} dB | Vaikus: {stats['silence_ratio']:.0%}")
        print()

        # Options
        while True:
            choice = input("  [k]uula tagasi / [s]alvesta / [u]uesti / [l]oobuge? ").strip().lower()
            if choice == "k":
                print("  ▶ Mängin tagasi...", flush=True)
                play_audio(audio)
                print()
                continue
            elif choice == "s":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{args.name}_ref_take{take:02d}_{timestamp}.wav"
                filepath = output_dir / filename
                sf.write(str(filepath), audio, SAMPLE_RATE, subtype="FLOAT")

                # Save metadata
                meta = {
                    "name": args.name,
                    "take": take,
                    "timestamp": timestamp,
                    "sample_rate": SAMPLE_RATE,
                    "duration_s": stats["duration_s"],
                    "db_rms": round(stats["db_rms"], 1),
                    "db_peak": round(stats["db_peak"], 1),
                    "silence_ratio": round(stats["silence_ratio"], 3),
                    "device": args.device or "default",
                    "device_name": dev_info["name"],
                    "text": "pohjatuul_ja_paike+supplement",
                }
                meta_path = output_dir / f"{filename}.json"
                meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")

                print(f"\n  ✅ Salvestatud: {filepath}")
                print(f"     Metaandmed:  {meta_path}")

                again = input("\n  Kas salvestame veel ühe take? [j/E] ").strip().lower()
                if again == "j":
                    take += 1
                    break
                else:
                    print(f"\n  Valmis! Referentsaudio: {output_dir}/")
                    print(f"  Järgmine samm: kratt tts clone {args.name}")
                    return
            elif choice == "u":
                take += 1
                break
            elif choice == "l":
                print("  Katkestatud.")
                return
            else:
                print("  Sisesta k/s/u/l")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  ⚠️ Katkestatud.")
    except Exception as e:
        print(f"\n  ❌ Viga: {e}")
        print("  Kontrolli: pip install sounddevice soundfile numpy")
        sys.exit(1)
