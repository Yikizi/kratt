#!/usr/bin/env python3
"""
Salvestab wake word näited treenimiseks.
Kasutamine: python record_samples.py --phrase "tere kodu" --count 100
"""

import argparse
import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path
import time
from datetime import datetime

def record_sample(duration=2.0, sample_rate=16000):
    """Salvesta üks audio sample."""
    print("🎤 Salvestan... Ütle oma wake word!")
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='int16'
    )
    sd.wait()
    return recording

def check_audio_level(recording):
    """Kontrolli, kas audio on piisavalt vali."""
    rms = np.sqrt(np.mean(recording.astype(float)**2))
    # Normaliseeritud int16 range: 32768
    normalized_rms = rms / 32768.0
    return normalized_rms

def main():
    parser = argparse.ArgumentParser(description='Salvesta wake word näiteid')
    parser.add_argument('--phrase', type=str, required=True, help='Wake word fraas')
    parser.add_argument('--count', type=int, default=100, help='Mitu näidet salvestada')
    parser.add_argument('--duration', type=float, default=2.0, help='Salvestuse pikkus sekundites')
    parser.add_argument('--output-dir', type=str, default='data/positive', help='Väljundi kataloog')
    parser.add_argument('--min-rms', type=float, default=0.01, help='Minimaalne RMS level')

    args = parser.parse_args()

    # Loo output kataloog
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"🎯 Salvestan {args.count} näidet fraasist: '{args.phrase}'")
    print(f"📁 Salvestan kausta: {output_dir}")
    print(f"⏱️  Salvestuse pikkus: {args.duration}s")
    print(f"📊 Minimaalne RMS: {args.min_rms}")
    print("\n💡 Nipid:")
    print("   - Ütle fraas erinevate häälekõrgustega")
    print("   - Muuda vahemaa mikrofoni ja suu vahel (30cm - 3m)")
    print("   - Ütle erineva kiirusega")
    print("   - Lisa taustahelisid (muusika, TV, vestlus)")
    print("   - Ütle erineva emotsiooniga")
    print("\n" + "="*50 + "\n")

    successful_recordings = 0
    attempt = 0

    while successful_recordings < args.count:
        attempt += 1
        input(f"[{successful_recordings + 1}/{args.count}] Vajuta ENTER ja ütle '{args.phrase}'... ")

        # Salvesta
        recording = record_sample(duration=args.duration)

        # Kontrolli audiot
        rms = check_audio_level(recording)

        if rms < args.min_rms:
            print(f"⚠️  Audio liiga vaikne! RMS: {rms:.4f} (min: {args.min_rms})")
            retry = input("   Kas proovid uuesti? (Y/n): ").strip().lower()
            if retry == 'n':
                continue
            else:
                continue

        # Salvesta fail
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_dir / f"{args.phrase.replace(' ', '_')}_{successful_recordings:03d}_{timestamp}.wav"
        sf.write(filename, recording, 16000)

        successful_recordings += 1
        print(f"✅ Salvestatud: {filename.name} (RMS: {rms:.4f})")

        # Väike paus
        time.sleep(0.3)

    print("\n" + "="*50)
    print(f"🎉 Valmis! Salvestatud {successful_recordings} näidet {attempt} katsega")
    print(f"📈 Edukuse määr: {successful_recordings/attempt*100:.1f}%")
    print(f"📁 Failid: {output_dir}")
    print("\n📝 Järgmised sammud:")
    print(f"   1. Laadi alla negative samples: python download_negatives.py")
    print(f"   2. Treeni mudel: python train_model.py")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Salvestamine katkestatud kasutaja poolt")
    except Exception as e:
        print(f"\n\n❌ Viga: {e}")
        print("\n💡 Kontrolli, et sul on mikrofon ühendatud ja sounddevice paigaldatud:")
        print("   pip install sounddevice soundfile numpy")
