#!/usr/bin/env python3
"""Generate "Kule Kratt" SSML mirror of existing "Kuule Kratt" SSML positives.

Mirrors every SSML variation from generate_neurokone_ssml_positives.py but with
"Kule" instead of "Kuule". Deduplicates against existing Kuule clips by SHA-256
hash — if Neurokõne produces identical audio for both spellings (e.g. mari),
the duplicate is removed.

Usage:
    python generate_kule_ssml_mirror.py --output ../raw/neurokone_ssml_kule
    python generate_kule_ssml_mirror.py --output ../raw/neurokone_ssml_kule \
        --kuule-dir ../raw/neurokone_ssml_positives --dedup
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import requests
from tqdm import tqdm

API_ENDPOINT = "https://api.tartunlp.ai/text-to-speech/v2"

ESTONIAN_SPEAKERS = [
    "albert", "indrek", "kalev", "kylli", "lee", "liivika",
    "luukas", "mari", "meelis", "peeter", "tambet", "vesta",
]

# Mirror of SSML_VARIATIONS from generate_neurokone_ssml_positives.py
# Every "Kuule" replaced with "Kule"
KULE_SSML_VARIATIONS = [
    ("pitch_low20", '<speak><prosody pitch="-20%">Kule Kratt</prosody></speak>'),
    ("pitch_low10", '<speak><prosody pitch="-10%">Kule Kratt</prosody></speak>'),
    ("pitch_high10", '<speak><prosody pitch="+10%">Kule Kratt</prosody></speak>'),
    ("pitch_high20", '<speak><prosody pitch="+20%">Kule Kratt</prosody></speak>'),
    ("pitch_high30", '<speak><prosody pitch="+30%">Kule Kratt</prosody></speak>'),
    ("emph_kule", '<speak><emphasis level="strong">Kule</emphasis> Kratt</speak>'),
    ("emph_kule_red", '<speak><emphasis level="reduced">Kule</emphasis> Kratt</speak>'),
    ("emph_kratt", '<speak>Kule <emphasis level="strong">Kratt</emphasis></speak>'),
    ("emph_kratt_red", '<speak>Kule <emphasis level="reduced">Kratt</emphasis></speak>'),
    ("vol_loud", '<speak><prosody volume="loud">Kule Kratt</prosody></speak>'),
    ("vol_soft", '<speak><prosody volume="soft">Kule Kratt</prosody></speak>'),
    ("vol_xloud", '<speak><prosody volume="x-loud">Kule Kratt</prosody></speak>'),
    ("vol_xsoft", '<speak><prosody volume="x-soft">Kule Kratt</prosody></speak>'),
    ("rate_slow", '<speak><prosody rate="slow">Kule Kratt</prosody></speak>'),
    ("rate_fast", '<speak><prosody rate="fast">Kule Kratt</prosody></speak>'),
    ("rate_xslow", '<speak><prosody rate="x-slow">Kule Kratt</prosody></speak>'),
    ("pause_100", '<speak>Kule <break time="100ms"/> Kratt</speak>'),
    ("pause_300", '<speak>Kule <break time="300ms"/> Kratt</speak>'),
    ("pause_500", '<speak>Kule <break time="500ms"/> Kratt</speak>'),
    ("high_emph_kule", '<speak><prosody pitch="+15%"><emphasis level="strong">Kule</emphasis> Kratt</prosody></speak>'),
    ("low_emph_kratt", '<speak><prosody pitch="-15%">Kule <emphasis level="strong">Kratt</emphasis></prosody></speak>'),
    ("loud_fast", '<speak><prosody volume="loud" rate="fast">Kule Kratt</prosody></speak>'),
    ("soft_slow", '<speak><prosody volume="soft" rate="slow">Kule Kratt</prosody></speak>'),
    ("whisper_call", '<speak><prosody volume="x-soft" rate="slow">Kule Kratt</prosody></speak>'),
    ("shout", '<speak><prosody volume="x-loud" pitch="+20%" rate="fast">Kule Kratt</prosody></speak>'),
    ("tired", '<speak><prosody volume="soft" pitch="-15%" rate="slow">Kule Kratt</prosody></speak>'),
    ("excited", '<speak><prosody volume="loud" pitch="+25%" rate="fast">Kule Kratt</prosody></speak>'),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_kuule_hash_index(kuule_dir: Path) -> set[str]:
    """Hash every WAV in the existing Kuule SSML dir for dedup."""
    hashes: set[str] = set()
    if not kuule_dir.exists():
        return hashes
    for f in kuule_dir.rglob("*.wav"):
        hashes.add(sha256(f))
    print(f"Indexed {len(hashes)} unique Kuule hashes from {kuule_dir}")
    return hashes


def generate_sample(ssml: str, speaker: str, speed: float, output_path: Path) -> bool:
    try:
        r = requests.post(
            API_ENDPOINT,
            json={"text": ssml, "speaker": speaker, "speed": speed},
            timeout=30,
        )
        if r.status_code == 200:
            output_path.write_bytes(r.content)
            return True
        print(f"  ERROR {r.status_code}: {r.text[:80]}")
        return False
    except Exception as e:
        print(f"  Exception: {e}")
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="../raw/neurokone_ssml_kule")
    ap.add_argument("--kuule-dir", default="../raw/neurokone_ssml_positives",
                    help="Existing Kuule SSML dir for dedup hash comparison")
    ap.add_argument("--dedup", action="store_true",
                    help="Remove files identical to Kuule versions")
    ap.add_argument("--delay", type=float, default=0.12)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    kuule_hashes: set[str] = set()
    if args.dedup:
        kuule_hashes = build_kuule_hash_index(Path(args.kuule_dir))

    speeds = [0.9, 1.0, 1.1]
    total = len(ESTONIAN_SPEAKERS) * len(KULE_SSML_VARIATIONS) * len(speeds)
    print(f"{len(ESTONIAN_SPEAKERS)} speakers × {len(KULE_SSML_VARIATIONS)} SSML × {len(speeds)} speeds = {total} samples")

    if args.dry_run:
        print("DRY RUN — no API calls")
        return

    stats = {"generated": 0, "skipped_exists": 0, "failed": 0,
             "deduped": 0, "kept": 0, "by_speaker": {}}
    pbar = tqdm(total=total, desc="Generating Kule SSML")

    idx = 0
    for speaker in ESTONIAN_SPEAKERS:
        speaker_dir = output_dir / speaker
        speaker_dir.mkdir(exist_ok=True)
        sp_stats = {"generated": 0, "deduped": 0}

        for label, ssml in KULE_SSML_VARIATIONS:
            for speed in speeds:
                filename = f"{speaker}_{idx:05d}_kule_{label}_speed{speed}.wav"
                filepath = speaker_dir / filename

                if filepath.exists():
                    stats["skipped_exists"] += 1
                    idx += 1
                    pbar.update(1)
                    continue

                ok = generate_sample(ssml, speaker, speed, filepath)
                if not ok:
                    stats["failed"] += 1
                    idx += 1
                    pbar.update(1)
                    time.sleep(args.delay)
                    continue

                stats["generated"] += 1
                sp_stats["generated"] += 1

                # Dedup check
                if args.dedup and kuule_hashes:
                    h = sha256(filepath)
                    if h in kuule_hashes:
                        filepath.unlink()
                        stats["deduped"] += 1
                        sp_stats["deduped"] += 1
                    else:
                        stats["kept"] += 1

                idx += 1
                pbar.update(1)
                time.sleep(args.delay)

        stats["by_speaker"][speaker] = sp_stats

    pbar.close()

    if not args.dedup:
        stats["kept"] = stats["generated"]

    # Summary
    print(f"\n{'='*60}")
    print(f"Generated: {stats['generated']}")
    print(f"Skipped (exists): {stats['skipped_exists']}")
    print(f"Failed: {stats['failed']}")
    if args.dedup:
        print(f"Deduped (identical to Kuule): {stats['deduped']}")
    print(f"Kept (unique Kule clips): {stats['kept']}")

    if args.dedup:
        print(f"\nPer-speaker dedup:")
        for sp, ss in stats["by_speaker"].items():
            pct = ss["deduped"] / ss["generated"] * 100 if ss["generated"] else 0
            print(f"  {sp:>10s}: {ss['generated']:>3d} gen, {ss['deduped']:>3d} deduped ({pct:.0f}%)")

    (output_dir / "generation_stats.json").write_text(
        json.dumps(stats, indent=2) + "\n"
    )
    print(f"\nOutput: {output_dir}")


if __name__ == "__main__":
    main()
