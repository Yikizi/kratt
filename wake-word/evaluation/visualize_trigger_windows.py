#!/usr/bin/env python3
"""Visualize the EXACT 1.5s sliding window that triggered a false positive.

For each clip, runs microWakeWord inference to find the window with the highest
score, then plots that specific 1.5s slice alongside the positive reference.

Usage:
    python visualize_trigger_windows.py \
        --model models/kuule-kratt-expert-a/kuule_kratt_expert-a.tflite \
        --clips data/mined/ohem_expert_a_top50 \
        --ref-dir data/raw/mattias-short/positive \
        --n 8 \
        -o figures/trigger_windows.png
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path

import librosa
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

matplotlib.use("Agg")

SR = 16_000
N_FFT = 512
HOP = 160         # 10ms = microWakeWord step
N_MELS = 40
FMIN = 60
FMAX = 7800
FLOOR_DB = -80.0
REF_DB = 0.0
CLIP_MS = 1500    # microWakeWord clip_duration_ms


def compute_mel(y: np.ndarray) -> np.ndarray:
    S = librosa.feature.melspectrogram(
        y=y, sr=SR, n_fft=N_FFT, hop_length=HOP,
        n_mels=N_MELS, fmin=FMIN, fmax=FMAX,
    )
    return librosa.power_to_db(S, ref=np.max)


def find_trigger_window(model, wav_path: Path, step_ms: int = 10):
    """Find the 1.5s window with the highest model score.

    Returns (start_sample, end_sample, max_score, all_scores).
    """
    audio, file_sr = sf.read(str(wav_path), dtype="int16")
    if file_sr != SR:
        audio_f = audio.astype(np.float32) / 32768.0
        audio_f = librosa.resample(audio_f, orig_sr=file_sr, target_sr=SR)
        audio = (audio_f * 32768).astype(np.int16)
    if audio.ndim > 1:
        audio = audio[:, 0]

    predictions = model.predict_clip(audio, step_ms=step_ms)
    if not predictions:
        return 0, int(SR * CLIP_MS / 1000), 0.0, [], audio

    # Each prediction corresponds to a window ending at a specific frame
    clip_samples = int(SR * CLIP_MS / 1000)  # 24000 samples = 1.5s
    step_samples = int(SR * step_ms / 1000)

    # Model stride determines how predictions map to time
    # Each prediction i corresponds to audio ending at frame:
    #   end_frame = input_feature_slices + i * stride
    # But we approximate: prediction i ≈ window centered around that position
    n_preds = len(predictions)
    best_idx = int(np.argmax(predictions))
    best_score = float(predictions[best_idx])

    # Approximate start sample of the best window
    # The model processes spectrogram slices; each prediction corresponds
    # to a window of `clip_samples` audio
    total_frames = len(audio) // step_samples
    window_frames = clip_samples // step_samples  # 150 frames for 1.5s

    # Map prediction index to audio position
    if n_preds > 1:
        # Spread predictions evenly across the valid range
        stride_frames = max(1, (total_frames - window_frames) // max(1, n_preds - 1))
        start_frame = best_idx * stride_frames
    else:
        start_frame = 0

    start_sample = start_frame * step_samples
    end_sample = start_sample + clip_samples
    end_sample = min(end_sample, len(audio))
    start_sample = max(0, end_sample - clip_samples)

    return start_sample, end_sample, best_score, predictions, audio


def main():
    parser = argparse.ArgumentParser(description="Visualize exact trigger windows")
    parser.add_argument("--model", required=True)
    parser.add_argument("--clips", required=True, help="Directory of false trigger clips")
    parser.add_argument("--ref-dir", required=True, help="Directory of positive reference clips")
    parser.add_argument("--n", type=int, default=8, help="Number of clips to show")
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()

    from microwakeword.inference import Model
    model = Model(args.model)

    clips_dir = Path(args.clips)
    ref_dir = Path(args.ref_dir)

    wavs = sorted(clips_dir.glob("*.wav"))
    refs = sorted(ref_dir.glob("*.wav"))
    rng = random.Random(args.seed)

    selected = rng.sample(wavs, min(args.n, len(wavs)))
    ref_selected = rng.sample(refs, min(args.n, len(refs)))

    n_cols = min(args.n, 4)
    n_pairs = len(selected)
    # Layout: row pairs — each pair = (positive 1.5s, trigger window 1.5s)
    # Side-by-side same zoom for direct comparison
    n_rows = 2  # row 0 = positive, row 1 = trigger window (both 1.5s)

    fig_w = 3.5 * n_cols + 1.2
    fig_h = 2.2 * n_rows + 1.5

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(fig_w, fig_h),
                             squeeze=False, constrained_layout=True)

    mel_freqs = librosa.mel_frequencies(n_mels=N_MELS + 1, fmin=FMIN, fmax=FMAX)
    mel_ticks = [0, 10, 20, 30, 40]
    freq_labels = [f"{int(mel_freqs[t])}" for t in mel_ticks]

    # Fixed x-axis for both rows: 0 to 1.5s (same zoom)
    clip_sec = CLIP_MS / 1000.0

    for c in range(n_cols):
        # Row 0: positive reference — crop/pad to exactly 1.5s
        ax0 = axes[0][c]
        if c < len(ref_selected):
            y_ref, _ = librosa.load(str(ref_selected[c]), sr=SR, mono=True)
            target_len = int(SR * clip_sec)
            if len(y_ref) > target_len:
                y_ref = y_ref[:target_len]
            elif len(y_ref) < target_len:
                y_ref = np.pad(y_ref, (0, target_len - len(y_ref)))
            S_ref = compute_mel(y_ref)
            ax0.imshow(S_ref, aspect="auto", origin="lower",
                       extent=[0, clip_sec, 0, N_MELS], cmap="magma",
                       vmin=FLOOR_DB, vmax=REF_DB, interpolation="nearest")
            ax0.set_title(ref_selected[c].stem, fontsize=5, pad=2)
            ax0.set_xlim(0, clip_sec)
        else:
            ax0.axis("off")

        # Row 1: trigger window — exactly 1.5s
        if c < len(selected):
            start, end, score, preds, audio_int16 = find_trigger_window(
                model, selected[c]
            )
            audio_f32 = audio_int16.astype(np.float32) / 32768.0
            window_audio = audio_f32[start:end]

            ax1 = axes[1][c]
            if len(window_audio) > 0:
                target_len = int(SR * clip_sec)
                if len(window_audio) > target_len:
                    window_audio = window_audio[:target_len]
                elif len(window_audio) < target_len:
                    window_audio = np.pad(window_audio, (0, target_len - len(window_audio)))
                S_win = compute_mel(window_audio)
                ax1.imshow(S_win, aspect="auto", origin="lower",
                           extent=[0, clip_sec, 0, N_MELS], cmap="magma",
                           vmin=FLOOR_DB, vmax=REF_DB, interpolation="nearest")
                t_start = start / SR
                ax1.set_title(f"{selected[c].stem} @{t_start:.1f}s (score={score:.2f})",
                              fontsize=5, pad=2)
                ax1.set_xlim(0, clip_sec)
        else:
            axes[1][c].axis("off")

        for r in range(n_rows):
            ax = axes[r][c]
            if c == 0:
                labels = ["Positiivne\n'Kuule Kratt' (1.5s)", "False trigger\naken (1.5s)"]
                ax.set_ylabel(labels[r], fontsize=7, fontweight="bold")
                ax.set_yticks(mel_ticks)
                ax.set_yticklabels(freq_labels, fontsize=5)
            else:
                ax.set_yticks([])
            if r == n_rows - 1:
                ax.set_xlabel("Aeg (s)", fontsize=6)
            ax.tick_params(axis="x", labelsize=5)

    fig.suptitle("Positiivne vs False Trigger — mõlemad 1.5s akna tasemel",
                 fontsize=10, fontweight="bold")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out), dpi=args.dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
