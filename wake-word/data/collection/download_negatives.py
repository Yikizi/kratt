#!/usr/bin/env python3
"""
Laadib alla negative samples wake word treenimiseks.
Kasutab Google Speech Commands Dataset ja Common Voice.
"""

import argparse
import urllib.request
import tarfile
import zipfile
from pathlib import Path
import shutil
import random

def download_file(url, destination):
    """Laadi fail alla progress bar'iga."""
    last_percent = {"value": -1}
    def reporthook(count, block_size, total_size):
        if total_size <= 0:
            return
        percent = int(count * block_size * 100 / total_size)
        # Avoid extremely spammy output; only print when the integer percent changes.
        if percent != last_percent["value"]:
            last_percent["value"] = percent
            print(f"\r📥 Laadimine: {percent}%", end='', flush=True)

    print(f"📡 Laadimine: {url}")
    urllib.request.urlretrieve(url, destination, reporthook=reporthook)
    print("\n✅ Valmis!")

def download_speech_commands(output_dir):
    """Laadi Google Speech Commands Dataset v2."""
    print("\n🎯 Laadimine: Google Speech Commands Dataset v2")
    print("   ~2.4GB, ~105,000 audio faili")

    url = "http://download.tensorflow.org/data/speech_commands_v0.02.tar.gz"
    archive_path = output_dir / "speech_commands_v0.02.tar.gz"
    extract_dir = output_dir / "speech_commands"

    # Laadi alla
    if archive_path.exists():
        print(f"⏭️  Juba olemas: {archive_path}")
    else:
        download_file(url, archive_path)

    # Ekstrakti
    if not extract_dir.exists():
        print("📦 Ekstraktimine...")
        extract_dir.mkdir(parents=True, exist_ok=True)
        try:
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(extract_dir)
        except Exception as e:
            # If the archive is partial/corrupt, keep it for debugging and force re-download.
            print(f"\n❌ Ekstraktimine ebaõnnestus: {e}")
            corrupt_path = archive_path.with_suffix(archive_path.suffix + ".corrupt")
            print(f"↪️  Nimetan arhive ümber: {archive_path.name} -> {corrupt_path.name}")
            archive_path.rename(corrupt_path)
            print("🔁 Proovin uuesti alla laadida...")
            download_file(url, archive_path)
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(extract_dir)
        print("✅ Ekstraktitud!")
    else:
        print(f"⏭️  Juba ekstraktitud: {extract_dir}")

    # Kustuta kaustad, mis võiksid olla wake word'id
    # (jätame need välja, et vältida konflikti)
    wake_word_folders = ['yes', 'no', 'stop', 'go', 'up', 'down', 'left', 'right']
    for folder in wake_word_folders:
        folder_path = extract_dir / folder
        if folder_path.exists():
            print(f"🗑️  Kustutan võimaliku wake word kausta: {folder}")
            shutil.rmtree(folder_path)

    # Kopeeri failid negative kausta
    negative_dir = output_dir / "negative_samples"
    negative_dir.mkdir(parents=True, exist_ok=True)

    file_count = 0
    for audio_file in extract_dir.rglob("*.wav"):
        if file_count >= 5000:  # Piira 5000 failiga
            break
        shutil.copy2(audio_file, negative_dir / f"speech_cmd_{file_count:05d}.wav")
        file_count += 1

    print(f"✅ Kopeeritud {file_count} negative samples")

    # Cleanup
    if archive_path.exists():
        print("🧹 Kustutan archive...")
        archive_path.unlink()

    return negative_dir

def add_noise_samples(output_dir):
    """Genereeri müra ja vaikusejärgused negative näited."""
    print("\n🔊 Genereerin müra ja vaikusejärgused...")

    import numpy as np
    import soundfile as sf

    negative_dir = output_dir / "negative_samples"
    negative_dir.mkdir(parents=True, exist_ok=True)

    sample_rate = 16000
    duration = 1.0

    noise_types = {
        'white_noise': lambda: np.random.normal(0, 0.1, int(sample_rate * duration)),
        'pink_noise': lambda: np.cumsum(np.random.normal(0, 0.1, int(sample_rate * duration))),
        'silence': lambda: np.zeros(int(sample_rate * duration)),
        'low_noise': lambda: np.random.normal(0, 0.01, int(sample_rate * duration)),
    }

    for noise_name, noise_func in noise_types.items():
        for i in range(250):  # 250 näidet iga tüübi kohta
            audio = noise_func()
            # Normaliseeri
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio)) * 0.5
            filename = negative_dir / f"{noise_name}_{i:03d}.wav"
            sf.write(filename, audio.astype(np.float32), sample_rate)

    print("✅ Genereeritud 1000 müra/vaikusejärgused")

def generate_background_sounds(output_dir):
    """Juhised background soundide lisamiseks."""
    print("\n🎵 SOOVITUS: Lisa ka tausta helisid!")
    print("\n💡 Soovitused:")
    print("   1. Salvesta 10-20 minutit:")
    print("      - Muusikat (erinevad žanrid)")
    print("      - Telerit/raadiot")
    print("      - Kodu helisid (nõudepesumasin, tolmuimeja, ventilaator)")
    print("      - Vestlust (ilma wake word'ita)")
    print("      - Välis helisid (liiklus, linnud)")
    print("\n   2. Tükelda 1-2 sekundiseks:")
    print("      ffmpeg -i background.wav -f segment -segment_time 2 bg_%03d.wav")
    print("\n   3. Kopeeri data/negative kausta")

def main():
    parser = argparse.ArgumentParser(description='Laadi negative samples')
    parser.add_argument('--output-dir', type=str, default='data',
                       help='Väljundi kataloog')
    parser.add_argument('--skip-download', action='store_true',
                       help='Jäta alla laadimime vahele (kasuta olemasolevaid)')

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*60)
    print("🎯 NEGATIVE SAMPLES DOWNLOAD")
    print("="*60)

    # 1. Download Speech Commands
    if not args.skip_download:
        negative_dir = download_speech_commands(output_dir)
    else:
        negative_dir = output_dir / "negative_samples"
        print("⏭️  Jätan alla laadimise vahele")

    # 2. Generate noise
    add_noise_samples(output_dir)

    # 3. Background sounds juhised
    generate_background_sounds(output_dir)

    # Stats
    total_negatives = len(list((output_dir / "negative_samples").glob("*.wav")))

    print("\n" + "="*60)
    print("🎉 VALMIS!")
    print("="*60)
    print(f"📊 Kokku negative samples: {total_negatives}")
    print(f"📁 Asukoht: {output_dir / 'negative_samples'}")
    print("\n📝 Järgmised sammud:")
    print("   1. Lisa background sounds (vaata juhiseid ülalpool)")
    print("   2. Salvesta positive samples: python record_samples.py --phrase 'tere kodu' --count 100")
    print("   3. Treeni mudel: python train_model.py")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Allalaadimine katkestatud")
    except Exception as e:
        print(f"\n\n❌ Viga: {e}")
        import traceback
        traceback.print_exc()
