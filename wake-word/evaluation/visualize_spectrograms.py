#!/usr/bin/env python3
"""Generate thesis-quality mel spectrogram comparison grids.

Usage examples:

  # Positive vs Hard Negative (why the model is confused)
  python visualize_spectrograms.py \
    --title "Positive vs Confusable" \
    --row "Positiivne (Mattias Mac)" data/raw/mattias-short/positive 4 \
    --row "Hard neg (Mattias Mac)"   data/augmented/hard_neg_mattias_mac_train 4 \
    --row "Hard neg (Isa XTTS)"      data/processed/test_hard_neg_xtts_isa 4 \
    -o figures/pos_vs_hardneg.png

  # Speaker diversity (same phrase, different voices)
  python visualize_spectrograms.py \
    --title "Kõnelejate võrdlus" \
    --row "Mattias (Mac)"   data/raw/mattias-short/positive 4 \
    --row "Sõber (iPhone)"  data/raw/friend1_20260414 4 \
    --row "Õde (reaalne)"   data/raw/ode_kuule_kratt 4 \
    --row "Isa (XTTS)"      data/processed/test_pos_xtts_isa 4 \
    -o figures/speaker_diversity.png

  # Device / mic comparison
  python visualize_spectrograms.py \
    --title "Mikrofonide spektraalne erinevus" \
    --row "MacBook Pro mic"    data/raw/mattias-short/positive 4 \
    --row "iPhone (AirDrop)"   data/raw/friend1_20260414 4 \
    --row "CV ET (crowdsourced)" data/processed/faph_test_cv_et 4 \
    -o figures/mic_comparison.png

All panels share identical axes: mel frequency (y), time (x), and a fixed
dB colorscale so any two sub-plots are directly comparable.
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

import librosa
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")

# ── Audio & spectrogram constants (match microWakeWord pipeline) ─────────
SR = 16_000          # target sample rate
N_FFT = 512          # 32 ms window @ 16 kHz
HOP = 160            # 10 ms hop  (= microWakeWord window_step_ms)
N_MELS = 40          # mel bands
FMIN = 60            # Hz
FMAX = 7800          # Hz
REF_DB = 0.0         # fixed top of colorscale
FLOOR_DB = -80.0     # fixed bottom of colorscale


def load_mel(path: Path) -> np.ndarray:
    """Load a WAV, resample to 16 kHz, return log-mel spectrogram in dB."""
    y, _ = librosa.load(str(path), sr=SR, mono=True)
    S = librosa.feature.melspectrogram(
        y=y, sr=SR, n_fft=N_FFT, hop_length=HOP,
        n_mels=N_MELS, fmin=FMIN, fmax=FMAX,
    )
    S_db = librosa.power_to_db(S, ref=np.max)
    return S_db


def pick_clips(directory: Path, n: int, seed: int = 42) -> list[Path]:
    """Pick up to n random WAV clips from a directory."""
    wavs = sorted(directory.glob("*.wav"))
    if not wavs:
        print(f"WARNING: no .wav files in {directory}", file=sys.stderr)
        return []
    rng = random.Random(seed)
    return rng.sample(wavs, min(n, len(wavs)))


def make_grid(
    rows: list[tuple[str, Path, int]],
    title: str,
    out_path: Path,
    seed: int = 42,
    dpi: int = 300,
    figscale: float = 1.0,
) -> None:
    """Generate a grid of mel spectrograms and save to PNG.

    rows: list of (label, directory, n_clips)
    """
    # Resolve how many columns (= max clips per row)
    n_cols = max(n for _, _, n in rows)
    n_rows = len(rows)

    fig_w = 3.2 * n_cols * figscale + 1.6  # extra for colorbar + labels
    fig_h = 2.0 * n_rows * figscale + 1.2  # extra for title

    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(fig_w, fig_h),
        squeeze=False,
        constrained_layout=True,
    )

    mel_images = []

    for r, (label, directory, n_clips) in enumerate(rows):
        clips = pick_clips(directory, n_clips, seed=seed)
        for c in range(n_cols):
            ax = axes[r][c]
            if c < len(clips):
                S_db = load_mel(clips[c])
                # Time axis in seconds
                t_max = S_db.shape[1] * HOP / SR
                extent = [0, t_max, 0, N_MELS]
                im = ax.imshow(
                    S_db,
                    aspect="auto",
                    origin="lower",
                    extent=extent,
                    cmap="magma",
                    vmin=FLOOR_DB,
                    vmax=REF_DB,
                    interpolation="nearest",
                )
                mel_images.append(im)
                # Clip name as subtitle
                ax.set_title(clips[c].stem, fontsize=6, pad=2)
            else:
                ax.axis("off")

            # Y-axis: only leftmost column
            if c == 0:
                ax.set_ylabel(label, fontsize=8, fontweight="bold")
                mel_ticks = [0, 10, 20, 30, 40]
                mel_freqs = librosa.mel_frequencies(n_mels=N_MELS + 1, fmin=FMIN, fmax=FMAX)
                freq_labels = [f"{int(mel_freqs[t])}" for t in mel_ticks]
                ax.set_yticks(mel_ticks)
                ax.set_yticklabels(freq_labels, fontsize=6)
            else:
                ax.set_yticks([])

            # X-axis: only bottom row
            if r == n_rows - 1:
                ax.set_xlabel("Aeg (s)", fontsize=7)
                ax.tick_params(axis="x", labelsize=6)
            else:
                ax.set_xticklabels([])

    # Shared colorbar
    if mel_images:
        cbar = fig.colorbar(
            mel_images[0], ax=axes, location="right",
            fraction=0.02, pad=0.01, label="dB",
        )
        cbar.ax.tick_params(labelsize=6)

    fig.suptitle(title, fontsize=12, fontweight="bold")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out_path), dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out_path}  ({n_rows} rows × {n_cols} cols)")


def main():
    parser = argparse.ArgumentParser(
        description="Mel spectrogram comparison grid generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--title", default="Mel Spectrogram Comparison")
    parser.add_argument(
        "--row", nargs=3, action="append", required=True,
        metavar=("LABEL", "DIR", "N"),
        help='Row: "Label" path/to/clips N',
    )
    parser.add_argument("-o", "--output", required=True, help="Output PNG path")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--scale", type=float, default=1.0, help="Figure scale multiplier")
    args = parser.parse_args()

    base = Path(__file__).resolve().parents[1]  # wake-word/

    rows = []
    for label, dir_str, n_str in args.row:
        d = Path(dir_str)
        if not d.is_absolute():
            d = base / d
        rows.append((label, d, int(n_str)))

    out = Path(args.output)
    if not out.is_absolute():
        out = base / out

    make_grid(rows, title=args.title, out_path=out, seed=args.seed, dpi=args.dpi, figscale=args.scale)


if __name__ == "__main__":
    main()
