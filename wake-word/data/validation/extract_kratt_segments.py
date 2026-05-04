#!/usr/bin/env python3
"""Extract single-word "Kratt" candidates from clean "Kuule/Kule Kratt" clips.

This is a conservative human-in-the-loop data-prep tool for the v19
`Kratt`-only ablation. It does not assert that automatic boundaries are
perfect. Instead it writes candidate cuts, detailed manifests, confidence
scores, and review folders so suspicious cuts can be listened to before any
training run uses them.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
import random
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

WAKE_WORD_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_DIRS = [WAKE_WORD_ROOT / "data" / "processed" / "positive_strict_kuule_kule"]
DEFAULT_INCLUDE_PATTERNS = [r"(kuule|kule).*kratt"]
DEFAULT_EXCLUDE_PATTERNS = [
    r"ee_kuule_kratt",
    r"no_kuule_kratt",
    r"noh_kuule_kratt",
    r"kratt_kuule",
    r"ssml",
    r"emph",
    r"prosody",
    r"pause",
]


@dataclass(frozen=True)
class BoundaryResult:
    method: str
    confidence: float
    speech_start_s: float
    speech_end_s: float
    boundary_s: float
    kratt_start_s: float
    valley_depth_db: float
    onset_rise_db: float
    position_fraction: float
    flags: list[str]


def resolve_path(text: str | Path) -> Path:
    path = Path(text).expanduser()
    if path.is_absolute():
        return path
    # Support both repo-root style paths (wake-word/data/...) and wake-word-root
    # style paths (data/...), even though the CLI wrapper executes from wake-word/.
    if path.parts and path.parts[0] == WAKE_WORD_ROOT.name:
        return (WAKE_WORD_ROOT.parent / path).resolve()
    if path.parts and path.parts[0] == "data":
        return (WAKE_WORD_ROOT / path).resolve()
    return (Path.cwd() / path).resolve()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def compile_patterns(patterns: list[str]) -> list[re.Pattern[str]]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def matches_any(patterns: list[re.Pattern[str]], text: str) -> bool:
    return any(p.search(text) for p in patterns)


def load_audio(path: Path, target_sr: int) -> tuple[np.ndarray, int, int]:
    audio, sr = sf.read(str(path), always_2d=True, dtype="float32")
    original_sr = int(sr)
    mono = audio.mean(axis=1)
    if original_sr != target_sr:
        gcd = math.gcd(original_sr, target_sr)
        mono = resample_poly(mono, target_sr // gcd, original_sr // gcd).astype(np.float32)
        sr = target_sr
    peak = float(np.max(np.abs(mono))) if mono.size else 0.0
    if peak > 1.0:
        mono = mono / peak
    return mono.astype(np.float32), int(sr), original_sr


def frame_rms(audio: np.ndarray, sr: int, frame_ms: float, hop_ms: float) -> tuple[np.ndarray, int, int]:
    frame_len = max(1, int(round(sr * frame_ms / 1000.0)))
    hop_len = max(1, int(round(sr * hop_ms / 1000.0)))
    if len(audio) < frame_len:
        audio = np.pad(audio, (0, frame_len - len(audio)))
    n_frames = 1 + max(0, (len(audio) - frame_len) // hop_len)
    rms = np.empty(n_frames, dtype=np.float32)
    for i in range(n_frames):
        start = i * hop_len
        frame = audio[start : start + frame_len]
        rms[i] = float(np.sqrt(np.mean(frame * frame) + 1e-12))
    return rms, frame_len, hop_len


def smooth(values: np.ndarray, width: int) -> np.ndarray:
    if width <= 1 or values.size == 0:
        return values
    kernel = np.ones(width, dtype=np.float32) / float(width)
    return np.convolve(values, kernel, mode="same").astype(np.float32)


def frame_center_s(idx: int, frame_len: int, hop_len: int, sr: int) -> float:
    return (idx * hop_len + frame_len / 2.0) / float(sr)


def estimate_boundary(
    audio: np.ndarray,
    sr: int,
    *,
    frame_ms: float,
    hop_ms: float,
    speech_rel_db: float,
    low_confidence_threshold: float,
    search_min_fraction: float,
    search_max_fraction: float,
    boundary_target_fraction: float,
    min_boundary_tail_s: float,
) -> BoundaryResult:
    flags: list[str] = []
    rms, frame_len, hop_len = frame_rms(audio, sr, frame_ms, hop_ms)
    rms_s = smooth(rms, 5)
    max_rms = float(np.max(rms_s)) if rms_s.size else 0.0
    if max_rms <= 1e-8:
        flags.extend(["silent_or_unreadable", "fallback_ratio_used", "low_boundary_confidence"])
        duration_s = len(audio) / float(sr)
        return BoundaryResult(
            method="fallback_ratio",
            confidence=0.0,
            speech_start_s=0.0,
            speech_end_s=duration_s,
            boundary_s=duration_s * 0.50,
            kratt_start_s=duration_s * 0.53,
            valley_depth_db=0.0,
            onset_rise_db=0.0,
            position_fraction=0.60,
            flags=flags,
        )

    rel_db = 20.0 * np.log10(np.maximum(rms_s, 1e-8) / max_rms)
    active = np.flatnonzero(rel_db >= speech_rel_db)
    if active.size == 0:
        flags.extend(["no_speech_region", "fallback_ratio_used"])
        start_i = 0
        end_i = len(rel_db) - 1
    else:
        start_i = max(0, int(active[0]) - 2)
        end_i = min(len(rel_db) - 1, int(active[-1]) + 2)

    if end_i <= start_i + 4:
        flags.extend(["speech_region_too_short", "fallback_ratio_used"])
        start_i = 0
        end_i = len(rel_db) - 1

    speech_start_s = frame_center_s(start_i, frame_len, hop_len, sr)
    speech_end_s = frame_center_s(end_i, frame_len, hop_len, sr)
    span = max(1, end_i - start_i)

    search_start_i = start_i + int(round(span * search_min_fraction))
    search_end_i = start_i + int(round(span * search_max_fraction))
    search_start_i = max(start_i + 1, min(search_start_i, end_i - 2))
    search_end_i = max(search_start_i + 1, min(search_end_i, end_i - 1))

    best: dict[str, Any] | None = None
    post_frames = max(4, int(round(0.22 / (hop_len / float(sr)))))
    pre_frames = max(4, int(round(0.18 / (hop_len / float(sr)))))

    for i in range(search_start_i, search_end_i + 1):
        pre = rel_db[max(start_i, i - pre_frames) : i + 1]
        post = rel_db[i : min(end_i + 1, i + post_frames)]
        if pre.size == 0 or post.size == 0:
            continue
        valley_db = float(rel_db[i])
        pre_peak = float(np.max(pre))
        post_peak = float(np.max(post))
        valley_depth = max(0.0, min(pre_peak, post_peak) - valley_db)
        onset_rise = max(0.0, post_peak - valley_db)

        # First frame after the valley where energy has clearly started rising.
        rise_threshold = valley_db + max(5.0, min(10.0, onset_rise * 0.45))
        onset_i = i
        for j in range(i, min(end_i + 1, i + post_frames)):
            if rel_db[j] >= rise_threshold and rel_db[j] >= -30.0:
                onset_i = j
                break

        frac = (i - start_i) / float(span)
        boundary_s = frame_center_s(i, frame_len, hop_len, sr)
        # Internal closures inside "kratt" (especially the final /t/) also look
        # like an energy valley followed by a burst. Reject late valleys that do
        # not leave enough tail for the whole one-syllable word.
        boundary_tail_s = max(0.0, speech_end_s - boundary_s)
        if boundary_tail_s < min_boundary_tail_s:
            continue
        position_score = max(0.0, 1.0 - abs(frac - boundary_target_fraction) / 0.24)
        depth_score = min(1.0, valley_depth / 16.0)
        rise_score = min(1.0, onset_rise / 14.0)
        if 0.45 <= boundary_tail_s <= 0.95:
            duration_score = 1.0
        elif min_boundary_tail_s <= boundary_tail_s <= 1.15:
            duration_score = 0.55
        else:
            duration_score = 0.10
        score = 0.40 * depth_score + 0.30 * rise_score + 0.20 * position_score + 0.10 * duration_score
        if best is None or score > best["score"]:
            best = {
                "score": score,
                "i": i,
                "onset_i": onset_i,
                "frac": frac,
                "valley_depth": valley_depth,
                "onset_rise": onset_rise,
            }

    if best is None:
        flags.extend(["no_boundary_candidate", "fallback_ratio_used"])
        boundary_i = start_i + int(round(span * boundary_target_fraction))
        onset_i = boundary_i + max(1, int(round(0.03 / (hop_len / float(sr)))))
        confidence = 0.15
        valley_depth = 0.0
        onset_rise = 0.0
        frac = boundary_target_fraction
        method = "fallback_ratio"
    else:
        boundary_i = int(best["i"])
        onset_i = int(best["onset_i"])
        confidence = float(best["score"])
        valley_depth = float(best["valley_depth"])
        onset_rise = float(best["onset_rise"])
        frac = float(best["frac"])
        method = "energy_valley_onset"

    if valley_depth < 6.0:
        flags.append("no_energy_valley")
    if onset_rise < 6.0:
        flags.append("weak_onset_rise")
    if confidence < low_confidence_threshold:
        flags.append("low_boundary_confidence")

    return BoundaryResult(
        method=method,
        confidence=round(confidence, 4),
        speech_start_s=speech_start_s,
        speech_end_s=speech_end_s,
        boundary_s=frame_center_s(boundary_i, frame_len, hop_len, sr),
        kratt_start_s=frame_center_s(onset_i, frame_len, hop_len, sr),
        valley_depth_db=round(valley_depth, 2),
        onset_rise_db=round(onset_rise, 2),
        position_fraction=round(frac, 3),
        flags=flags,
    )


def relative_energy_db(audio: np.ndarray, sr: int, start_s: float, end_s: float, global_peak_rms: float) -> float:
    start = max(0, int(round(start_s * sr)))
    end = min(len(audio), int(round(end_s * sr)))
    if end <= start or global_peak_rms <= 1e-8:
        return -120.0
    segment = audio[start:end]
    rms = float(np.sqrt(np.mean(segment * segment) + 1e-12))
    return 20.0 * math.log10(max(rms, 1e-8) / global_peak_rms)


def analyze_cut_flags(
    audio: np.ndarray,
    sr: int,
    boundary: BoundaryResult,
    crop_start_s: float,
    crop_end_s: float,
    *,
    min_cut_s: float,
    max_cut_s: float,
    suspicious_min_s: float,
    suspicious_max_s: float,
) -> list[str]:
    flags = list(boundary.flags)
    duration = crop_end_s - crop_start_s
    if duration < min_cut_s:
        flags.append("too_short")
    if duration > max_cut_s:
        flags.append("too_long")
    if duration < suspicious_min_s:
        flags.append("suspicious_short")
    if duration > suspicious_max_s:
        flags.append("suspicious_long")

    rms, _, _ = frame_rms(audio, sr, 25.0, 10.0)
    peak_rms = float(np.max(rms)) if rms.size else 0.0
    pre_db = relative_energy_db(audio, sr, crop_start_s - 0.12, crop_start_s - 0.02, peak_rms)
    # We intentionally keep pre-roll to preserve the /k/ closure. Clipped onset
    # means we could not actually keep enough pre-roll (usually because the crop
    # was clamped near the source start), not that the crop starts with energy.
    prefix_overlap_s = boundary.boundary_s - crop_start_s
    kept_preroll_s = boundary.kratt_start_s - crop_start_s
    if prefix_overlap_s > 0.10 and pre_db > -18.0:
        flags.append("possible_prefix_leak")
    if kept_preroll_s < 0.045:
        flags.append("possible_clipped_onset")
    if crop_end_s >= len(audio) / float(sr) - 0.005:
        flags.append("speech_end_uncertain")
    return sorted(set(flags))


def collect_wavs(source_dirs: list[Path], include: list[re.Pattern[str]], exclude: list[re.Pattern[str]]) -> list[Path]:
    wavs: list[Path] = []
    for src in source_dirs:
        if not src.exists():
            print(f"WARN missing source dir: {src}")
            continue
        for wav in sorted(src.rglob("*.wav")):
            rel_text = str(wav.relative_to(src))
            if matches_any(exclude, rel_text):
                continue
            if not matches_any(include, wav.name):
                continue
            wavs.append(wav)
    return sorted(dict.fromkeys(wavs))


def wav_duration_s(path: Path) -> float:
    info = sf.info(str(path))
    return float(info.frames) / float(info.samplerate)


def filter_wavs_by_source_duration(
    wavs: list[Path], min_source_duration_s: float, max_source_duration_s: float
) -> tuple[list[Path], dict[str, int]]:
    counts = {
        "source_wavs_before_duration_filter": len(wavs),
        "skipped_source_too_short": 0,
        "skipped_source_too_long": 0,
        "skipped_source_duration_error": 0,
    }
    if min_source_duration_s <= 0.0 and max_source_duration_s <= 0.0:
        return wavs, counts

    kept: list[Path] = []
    for wav in wavs:
        try:
            duration_s = wav_duration_s(wav)
        except Exception:  # noqa: BLE001 - keep broken metadata visible in the main extraction error path
            counts["skipped_source_duration_error"] += 1
            kept.append(wav)
            continue
        if min_source_duration_s > 0.0 and duration_s < min_source_duration_s:
            counts["skipped_source_too_short"] += 1
            continue
        if max_source_duration_s > 0.0 and duration_s > max_source_duration_s:
            counts["skipped_source_too_long"] += 1
            continue
        kept.append(wav)
    return kept, counts


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def safe_reset_dir(path: Path, force: bool) -> None:
    if path.exists():
        if not force:
            raise SystemExit(f"Output exists: {path} (use --force)")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def symlink_review_item(target: Path, review_dir: Path, name: str) -> None:
    review_dir.mkdir(parents=True, exist_ok=True)
    link = review_dir / name
    if link.exists() or link.is_symlink():
        link.unlink()
    rel_target = Path("..") / ".." / "accepted" / target.name
    link.symlink_to(rel_target)


def build_review_folders(output_dir: Path, rows: list[dict[str, Any]], random_n: int, seed: int) -> None:
    candidates = [r for r in rows if r.get("status") == "candidate" and r.get("output_file")]
    if not candidates:
        return
    rng = random.Random(seed)
    random_rows = candidates[:]
    rng.shuffle(random_rows)

    buckets: dict[str, list[dict[str, Any]]] = {
        "all_by_index": sorted(candidates, key=lambda r: int(r.get("index", 0))),
        "random_sample": random_rows[: min(random_n, len(random_rows))],
        "low_confidence": [r for r in candidates if "low_boundary_confidence" in r.get("flags", [])],
        "suspicious_short": [r for r in candidates if "suspicious_short" in r.get("flags", [])],
        "suspicious_long": [r for r in candidates if "suspicious_long" in r.get("flags", [])],
        "possible_prefix_leak": [r for r in candidates if "possible_prefix_leak" in r.get("flags", [])],
        "possible_clipped_onset": [r for r in candidates if "possible_clipped_onset" in r.get("flags", [])],
        "shortest": sorted(candidates, key=lambda r: r.get("crop_duration_ms", 0))[:20],
        "longest": sorted(candidates, key=lambda r: r.get("crop_duration_ms", 0), reverse=True)[:20],
    }

    accepted_dir = output_dir / "accepted"
    for bucket, bucket_rows in buckets.items():
        for row in bucket_rows:
            target = accepted_dir / Path(row["output_file"]).name
            name = f"{int(row['index']):05d}_{Path(row['output_file']).name}"
            symlink_review_item(target, output_dir / "review" / bucket, name)

    review_csv = output_dir / "review" / "review.csv"
    review_csv.parent.mkdir(parents=True, exist_ok=True)
    seen: set[int] = set()
    review_rows: list[dict[str, Any]] = []
    for bucket_rows in buckets.values():
        for row in bucket_rows:
            idx = int(row["index"])
            if idx in seen:
                continue
            seen.add(idx)
            review_rows.append(row)

    with review_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["index", "output_file", "source_file", "confidence", "flags", "review_status", "notes"],
        )
        writer.writeheader()
        for row in sorted(review_rows, key=lambda r: int(r["index"])):
            writer.writerow(
                {
                    "index": row["index"],
                    "output_file": row["output_file"],
                    "source_file": row["source_file"],
                    "confidence": row["confidence"],
                    "flags": ";".join(row.get("flags", [])),
                    "review_status": "pending",
                    "notes": "",
                }
            )

    seed_marks: dict[int, str] = {}
    seed_labels_path = output_dir / "review" / "terminal-labels.json"
    if seed_labels_path.exists():
        try:
            seed_data = json.loads(seed_labels_path.read_text(encoding="utf-8"))
            for key, value in seed_data.get("labels", {}).items():
                status = value.get("status") if isinstance(value, dict) else value
                if status in {"accept", "reject"}:
                    seed_marks[int(key)] = str(status)
        except Exception:
            seed_marks = {}

    index_html = output_dir / "review" / "index.html"
    with index_html.open("w", encoding="utf-8") as f:
        f.write("""<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<title>Kratt segment review</title>
<style>
body { font-family: system-ui, sans-serif; margin: 2rem; line-height: 1.35; }
.controls { position: sticky; top: 0; z-index: 10; background: #fffdf7; border: 1px solid #e5d28a; padding: 0.75rem; margin-bottom: 1rem; box-shadow: 0 2px 8px #0001; }
table { border-collapse: collapse; width: 100%; margin-bottom: 2rem; }
th, td { border: 1px solid #ccc; padding: 0.35rem; vertical-align: top; }
th { background: #f3f3f3; position: sticky; top: 5.2rem; z-index: 5; }
tr.review-row { cursor: pointer; }
tr.review-row.selected { outline: 3px solid #2563eb; outline-offset: -3px; background: #eff6ff; }
tr.review-row.marked-reject { background: #fee2e2; }
tr.review-row.marked-accept { background: #dcfce7; }
code { white-space: nowrap; }
kbd { border: 1px solid #aaa; border-bottom-width: 2px; border-radius: 3px; padding: 0.05rem 0.3rem; background: #f8f8f8; }
.flag { color: #9a3412; font-weight: 600; }
.small { color: #555; font-size: 0.9rem; }
textarea { width: 100%; min-height: 4rem; font-family: ui-monospace, monospace; }
audio { width: min(320px, 42vw); }
.playButton { margin-right: 0.4rem; }
.audio-slot { display: inline-block; min-width: 320px; min-height: 36px; vertical-align: middle; }
.audio-slot.audio-unloaded { color: #777; font-size: 0.85rem; }
</style>
</head>
<body>
<h1>Kratt segment review</h1>
<div class=\"controls\">
  <strong>Keyboard:</strong>
  <kbd>j</kbd>/<kbd>↓</kbd> next,
  <kbd>k</kbd>/<kbd>↑</kbd> previous,
  <kbd>o</kbd>/<kbd>Enter</kbd>/<kbd>Space</kbd> play current,
  <kbd>r</kbd> mark reject,
  <kbd>a</kbd> mark accept,
  <kbd>u</kbd> unmark,
  <kbd>g</kbd> jump to index.
  <label style=\"margin-left: 1rem;\"><input id=\"autoplay\" type=\"checkbox\" checked> autoplay when moving with j/k</label>
  <span id=\"audioWindowStatus\" class=\"small\" style=\"margin-left: 1rem;\"></span>
  <div class=\"small\">Reject if the cut contains audible <em>kuule/kule/le</em> prefix leakage, clips the /k/ onset/final /t/, or is only <em>tt</em>.</div>
  <details style=\"margin-top: 0.5rem;\" open>
    <summary>Marked rejects export</summary>
    <p class=\"small\">Browser marks are saved in localStorage for this page, but cannot modify repo files directly. Use Copy and paste/send the reject args, or download a CSV.</p>
    <button id=\"copyRejectArgs\" type=\"button\">Copy reject args</button>
    <button id=\"downloadReviewCsv\" type=\"button\">Download review CSV</button>
    <textarea id=\"rejectArgs\" readonly></textarea>
  </details>
</div>
<p>Click any row or use keyboard navigation. The selected row is blue. Rows marked reject are red; accept marks are green.</p>
""")
        for bucket, bucket_rows in buckets.items():
            f.write(f"<h2>{html.escape(bucket)} ({len(bucket_rows)})</h2>\n")
            f.write("<table><thead><tr><th>idx</th><th>audio</th><th>confidence</th><th>duration</th><th>flags</th><th>source</th></tr></thead><tbody>\n")
            for row in bucket_rows:
                rel_audio = html.escape("../" + row["output_file"], quote=True)
                flags = " ".join(f'<span class=\"flag\">{html.escape(flag)}</span>' for flag in row.get("flags", []))
                idx = int(row["index"])
                source_path = Path(row["source_file"])
                seed_mark = seed_marks.get(idx, "")
                mark_class = f" marked-{seed_mark}" if seed_mark in {"accept", "reject"} else ""
                try:
                    source_label = str(source_path.relative_to(WAKE_WORD_ROOT))
                except ValueError:
                    source_label = str(source_path)
                f.write(
                    f"<tr class=\"review-row{mark_class}\" data-index=\"{idx}\" data-audio-src=\"{rel_audio}\">"
                    f"<td>{idx:05d}</td>"
                    f"<td><button class=\"playButton\" type=\"button\" title=\"Play this row\">▶</button><span class=\"audio-slot audio-unloaded\">audio lazy</span><br><code>{html.escape(Path(row['output_file']).name)}</code></td>"
                    f"<td>{float(row['confidence']):.3f}</td>"
                    f"<td>{int(row.get('crop_duration_ms', 0))} ms</td>"
                    f"<td>{flags}</td>"
                    f"<td><code>{html.escape(source_label)}</code></td>"
                    "</tr>\n"
                )
            f.write("</tbody></table>\n")
        f.write("""
<script>
const rows = Array.from(document.querySelectorAll('tr.review-row'));
rows.forEach((row, i) => { row.dataset.rowPos = String(i); });
let current = 0;
let selectedRow = null;
let currentAudio = null;
let playTimer = null;
const mountedAudioRows = new Set();
const autoplay = document.getElementById('autoplay');
const rejectArgs = document.getElementById('rejectArgs');
const copyRejectArgs = document.getElementById('copyRejectArgs');
const downloadReviewCsv = document.getElementById('downloadReviewCsv');
const audioWindowStatus = document.getElementById('audioWindowStatus');
const storageKey = 'kratt-segment-review:' + location.pathname;
const MOVE_PLAY_DELAY_MS = 90;
const AUDIO_WINDOW_BEFORE = 6;
const AUDIO_WINDOW_AFTER = 10;

function rowAudio(row) {
  return row.querySelector('audio');
}

function audioSlot(row) {
  return row.querySelector('.audio-slot');
}

function ensureAudio(row) {
  let audio = rowAudio(row);
  if (audio) return audio;
  const slot = audioSlot(row);
  audio = document.createElement('audio');
  audio.controls = true;
  audio.preload = 'none';
  audio.src = row.dataset.audioSrc;
  if (slot) {
    slot.textContent = '';
    slot.classList.remove('audio-unloaded');
    slot.appendChild(audio);
  }
  return audio;
}

function unloadAudioAt(pos) {
  const row = rows[pos];
  if (!row) return;
  const audio = rowAudio(row);
  if (audio) {
    if (audio === currentAudio) currentAudio = null;
    audio.pause();
    audio.removeAttribute('src');
    audio.load();
    audio.remove();
  }
  const slot = audioSlot(row);
  if (slot) {
    slot.textContent = 'audio lazy';
    slot.classList.add('audio-unloaded');
  }
  mountedAudioRows.delete(pos);
}

function updateAudioWindow() {
  if (!rows.length) return;
  const first = Math.max(0, current - AUDIO_WINDOW_BEFORE);
  const last = Math.min(rows.length - 1, current + AUDIO_WINDOW_AFTER);
  const wanted = new Set();
  for (let pos = first; pos <= last; pos++) {
    wanted.add(pos);
    if (!mountedAudioRows.has(pos)) {
      ensureAudio(rows[pos]);
      mountedAudioRows.add(pos);
    }
  }
  Array.from(mountedAudioRows).forEach(pos => {
    if (!wanted.has(pos)) unloadAudioAt(pos);
  });
  if (audioWindowStatus) {
    audioWindowStatus.textContent = `${mountedAudioRows.size} audio controls mounted (${first + 1}-${last + 1}/${rows.length})`;
  }
}

function pauseCurrentAudio() {
  if (!currentAudio) return;
  currentAudio.pause();
  currentAudio.currentTime = 0;
  currentAudio = null;
}

function playRow(row) {
  const audio = ensureAudio(row);
  if (!audio) return;
  mountedAudioRows.add(Number(row.dataset.rowPos));
  if (currentAudio && currentAudio !== audio) {
    currentAudio.pause();
    currentAudio.currentTime = 0;
  }
  currentAudio = audio;
  audio.currentTime = 0;
  audio.play().catch(() => {});
}

function schedulePlay(row, delayMs = MOVE_PLAY_DELAY_MS) {
  clearTimeout(playTimer);
  if (!row || !autoplay.checked) return;
  pauseCurrentAudio();
  playTimer = setTimeout(() => {
    if (row === selectedRow) playRow(row);
  }, delayMs);
}

function selectRow(i, shouldPlay = false) {
  if (!rows.length) return;
  current = Math.max(0, Math.min(rows.length - 1, i));
  if (selectedRow) selectedRow.classList.remove('selected');
  const row = rows[current];
  selectedRow = row;
  row.classList.add('selected');
  updateAudioWindow();
  row.scrollIntoView({block: 'nearest', behavior: 'auto'});
  if (shouldPlay) schedulePlay(row);
}

function currentMarks() {
  const marks = {};
  rows.forEach(r => {
    if (r.classList.contains('marked-reject')) marks[r.dataset.index] = 'reject';
    else if (r.classList.contains('marked-accept')) marks[r.dataset.index] = 'accept';
  });
  return marks;
}

function saveMarks() {
  localStorage.setItem(storageKey, JSON.stringify(currentMarks()));
}

function loadMarks() {
  try {
    const marks = JSON.parse(localStorage.getItem(storageKey) || '{}');
    rows.forEach(r => {
      const mark = marks[r.dataset.index];
      if (mark === 'reject') r.classList.add('marked-reject');
      if (mark === 'accept') r.classList.add('marked-accept');
    });
  } catch (_) {}
}

function rejectIndices() {
  return Array.from(new Set(
    rows
      .filter(r => r.classList.contains('marked-reject'))
      .map(r => Number(r.dataset.index))
  )).sort((a, b) => a - b);
}

function updateRejectArgs() {
  const indices = rejectIndices();
  rejectArgs.value = indices.map(i => `--reject-index ${i}`).join(' ');
}

function mark(row, cls) {
  const idx = row.dataset.index;
  rows.filter(r => r.dataset.index === idx).forEach(r => {
    r.classList.remove('marked-reject', 'marked-accept');
    if (cls) r.classList.add(cls);
  });
  saveMarks();
  updateRejectArgs();
}

function csvEscape(s) {
  return '"' + String(s).split('"').join('""') + '"';
}

function downloadCsv() {
  const lines = ['index,output_file,source_file,review_status,notes'];
  rows.forEach(r => {
    let status = 'pending';
    if (r.classList.contains('marked-reject')) status = 'reject';
    if (r.classList.contains('marked-accept')) status = 'accept';
    const output = r.querySelector('code')?.textContent || '';
    const source = r.querySelector('td:last-child code')?.textContent || '';
    lines.push([r.dataset.index, output, source, status, ''].map(csvEscape).join(','));
  });
  const blob = new Blob([lines.join('\\n') + '\\n'], {type: 'text/csv'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'kratt_segment_review_export.csv';
  a.click();
  URL.revokeObjectURL(a.href);
}

copyRejectArgs.addEventListener('click', async () => {
  updateRejectArgs();
  try { await navigator.clipboard.writeText(rejectArgs.value); } catch (_) {}
});
downloadReviewCsv.addEventListener('click', downloadCsv);

function rowPositionForSourceIndex(idx) {
  for (let i = 0; i < rows.length; i++) {
    if (Number(rows[i].dataset.index) >= idx) return i;
  }
  return Math.max(0, rows.length - 1);
}

function initialPosition() {
  const match = String(location.hash || '').match(/\\d+/);
  if (!match) return 0;
  return rowPositionForSourceIndex(Number(match[0]));
}

function jumpToIndex() {
  const raw = prompt('Jump to source index, e.g. 472');
  if (raw === null) return;
  const idx = Number(String(raw).trim());
  if (!Number.isFinite(idx)) return;
  location.hash = String(idx);
  selectRow(rowPositionForSourceIndex(idx), true);
}

rows.forEach((row, i) => {
  row.addEventListener('click', (e) => {
    if (e.target.closest('audio,button')) return;
    selectRow(i, false);
  });
  row.querySelector('.playButton')?.addEventListener('click', (e) => {
    e.stopPropagation();
    selectRow(i, false);
    playRow(row);
  });
  row.addEventListener('dblclick', () => playRow(row));
});

document.addEventListener('keydown', (e) => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const key = e.key.toLowerCase();
  if (key === 'j' || e.key === 'ArrowDown') {
    e.preventDefault();
    selectRow(current + 1, true);
  } else if (key === 'k' || e.key === 'ArrowUp') {
    e.preventDefault();
    selectRow(current - 1, true);
  } else if (key === 'o' || e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    clearTimeout(playTimer);
    if (rows[current]) playRow(rows[current]);
  } else if (key === 'r') {
    e.preventDefault();
    if (rows[current]) mark(rows[current], 'marked-reject');
  } else if (key === 'a') {
    e.preventDefault();
    if (rows[current]) mark(rows[current], 'marked-accept');
  } else if (key === 'u') {
    e.preventDefault();
    if (rows[current]) mark(rows[current], null);
  } else if (key === 'g') {
    e.preventDefault();
    jumpToIndex();
  }
}, {capture: true});

loadMarks();
updateRejectArgs();
selectRow(initialPosition(), false);
</script>
</body></html>
""")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", action="append", default=[], help="Source directory; may be repeated")
    ap.add_argument(
        "--output-dir",
        default=str(WAKE_WORD_ROOT / "data" / "processed" / "positive_kratt_only_v19a"),
        help="Output dataset directory",
    )
    ap.add_argument("--force", action="store_true", help="Replace existing output directory")
    ap.add_argument("--dry-run", action="store_true", help="Analyze and write manifests, but do not write WAV cuts")
    ap.add_argument("--limit", type=int, default=0, help="Limit number of input WAVs after filtering")
    ap.add_argument("--sample", type=int, default=0, help="Randomly sample N input WAVs after filtering")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--target-sr", type=int, default=16000)
    ap.add_argument("--frame-ms", type=float, default=25.0)
    ap.add_argument("--hop-ms", type=float, default=10.0)
    ap.add_argument("--speech-rel-db", type=float, default=-35.0)
    ap.add_argument("--pre-roll-ms", type=float, default=110.0)
    ap.add_argument("--post-roll-ms", type=float, default=160.0)
    ap.add_argument(
        "--boundary-pre-roll-ms",
        type=float,
        default=30.0,
        help="Also anchor crop start this many ms before the detected inter-word boundary; prevents late onset-only cuts.",
    )
    ap.add_argument("--min-cut-s", type=float, default=0.30)
    ap.add_argument("--max-cut-s", type=float, default=1.20)
    ap.add_argument(
        "--desired-min-cut-s",
        type=float,
        default=0.60,
        help="If the candidate cut is shorter than this, extend start earlier before flagging/rejecting.",
    )
    ap.add_argument("--suspicious-min-s", type=float, default=0.50)
    ap.add_argument("--suspicious-max-s", type=float, default=1.05)
    ap.add_argument("--low-confidence-threshold", type=float, default=0.55)
    ap.add_argument("--search-min-fraction", type=float, default=0.30)
    ap.add_argument("--search-max-fraction", type=float, default=0.66)
    ap.add_argument("--boundary-target-fraction", type=float, default=0.50)
    ap.add_argument("--min-boundary-tail-s", type=float, default=0.38)
    ap.add_argument(
        "--reject-flag",
        action="append",
        default=[],
        help="If a candidate has this flag, write it to rejected/ instead of accepted/. May repeat.",
    )
    ap.add_argument(
        "--reject-index",
        action="append",
        type=int,
        default=[],
        help="Reject a specific source index from this extraction run. May repeat.",
    )
    ap.add_argument("--include-pattern", action="append", default=[], help="Override/include filename regex; may repeat")
    ap.add_argument("--exclude-pattern", action="append", default=[], help="Additional exclude regex; may repeat")
    ap.add_argument(
        "--min-source-duration-s",
        type=float,
        default=0.0,
        help="Skip source WAVs shorter than this before cutting. Useful for broad positive folders that already contain short crops.",
    )
    ap.add_argument(
        "--max-source-duration-s",
        type=float,
        default=0.0,
        help="Skip source WAVs longer than this before cutting. 0 disables the upper source-duration filter.",
    )
    ap.add_argument("--review-random-n", type=int, default=50)
    args = ap.parse_args()

    source_dirs = [resolve_path(s) for s in args.source_dir] if args.source_dir else DEFAULT_SOURCE_DIRS
    output_dir = resolve_path(args.output_dir)
    include_patterns = args.include_pattern or DEFAULT_INCLUDE_PATTERNS
    exclude_patterns = DEFAULT_EXCLUDE_PATTERNS + args.exclude_pattern
    include = compile_patterns(include_patterns)
    exclude = compile_patterns(exclude_patterns)

    wavs = collect_wavs(source_dirs, include, exclude)
    wavs, source_filter_counts = filter_wavs_by_source_duration(
        wavs, args.min_source_duration_s, args.max_source_duration_s
    )
    if args.sample and args.sample < len(wavs):
        rng = random.Random(args.seed)
        wavs = sorted(rng.sample(wavs, args.sample))
    if args.limit:
        wavs = wavs[: args.limit]
    if not wavs:
        raise SystemExit("No source WAVs matched the source/include/exclude policy")

    safe_reset_dir(output_dir, args.force)
    accepted_dir = output_dir / "accepted"
    rejected_dir = output_dir / "rejected"
    if not args.dry_run:
        accepted_dir.mkdir(parents=True, exist_ok=True)
        rejected_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "review").mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    reject_flags = set(args.reject_flag)
    reject_indices = set(args.reject_index)
    counts: dict[str, int] = {"candidate": 0, "rejected": 0, "error": 0, **source_filter_counts}

    for idx, wav in enumerate(wavs):
        try:
            audio, sr, original_sr = load_audio(wav, args.target_sr)
            duration_s = len(audio) / float(sr)
            boundary = estimate_boundary(
                audio,
                sr,
                frame_ms=args.frame_ms,
                hop_ms=args.hop_ms,
                speech_rel_db=args.speech_rel_db,
                low_confidence_threshold=args.low_confidence_threshold,
                search_min_fraction=args.search_min_fraction,
                search_max_fraction=args.search_max_fraction,
                boundary_target_fraction=args.boundary_target_fraction,
                min_boundary_tail_s=args.min_boundary_tail_s,
            )
            onset_crop_start_s = boundary.kratt_start_s - args.pre_roll_ms / 1000.0
            boundary_crop_start_s = boundary.boundary_s - args.boundary_pre_roll_ms / 1000.0
            crop_start_s = max(0.0, min(onset_crop_start_s, boundary_crop_start_s))
            crop_end_s = min(duration_s, boundary.speech_end_s + args.post_roll_ms / 1000.0)
            if crop_end_s <= crop_start_s:
                crop_end_s = min(duration_s, crop_start_s + args.min_cut_s)
            if crop_end_s - crop_start_s < args.desired_min_cut_s:
                # Short cuts were manually observed to be mostly final "tt".
                # Prefer extending earlier to recover the /kr/ onset; only extend
                # later if we hit the start of the source clip.
                needed_s = args.desired_min_cut_s - (crop_end_s - crop_start_s)
                earlier_start_s = max(0.0, crop_start_s - needed_s)
                recovered_s = crop_start_s - earlier_start_s
                crop_start_s = earlier_start_s
                if recovered_s < needed_s:
                    crop_end_s = min(duration_s, crop_end_s + (needed_s - recovered_s))
            flags = analyze_cut_flags(
                audio,
                sr,
                boundary,
                crop_start_s,
                crop_end_s,
                min_cut_s=args.min_cut_s,
                max_cut_s=args.max_cut_s,
                suspicious_min_s=args.suspicious_min_s,
                suspicious_max_s=args.suspicious_max_s,
            )
            rejected_by_flags = sorted(flag for flag in flags if flag in reject_flags)
            rejected_by_index = idx in reject_indices
            status = "rejected" if rejected_by_flags or rejected_by_index else "candidate"
            output_subdir = "rejected" if status == "rejected" else "accepted"
            output_name = f"kratt_{idx:05d}_{wav.stem}.wav"
            output_file = f"{output_subdir}/{output_name}"
            if not args.dry_run:
                start = int(round(crop_start_s * sr))
                end = int(round(crop_end_s * sr))
                target_dir = rejected_dir if status == "rejected" else accepted_dir
                sf.write(str(target_dir / output_name), audio[start:end], sr, subtype="PCM_16")

            row = {
                "index": idx,
                "status": status,
                "source_file": str(wav),
                "source_sha256": sha256_file(wav),
                "source_duration_ms": round(duration_s * 1000.0),
                "source_sample_rate": original_sr,
                "target_sample_rate": sr,
                "output_file": output_file,
                "speech_start_ms": round(boundary.speech_start_s * 1000.0),
                "speech_end_ms": round(boundary.speech_end_s * 1000.0),
                "boundary_ms": round(boundary.boundary_s * 1000.0),
                "kratt_start_ms": round(boundary.kratt_start_s * 1000.0),
                "crop_start_ms": round(crop_start_s * 1000.0),
                "crop_end_ms": round(crop_end_s * 1000.0),
                "crop_duration_ms": round((crop_end_s - crop_start_s) * 1000.0),
                "method": boundary.method,
                "confidence": boundary.confidence,
                "valley_depth_db": boundary.valley_depth_db,
                "onset_rise_db": boundary.onset_rise_db,
                "position_fraction": boundary.position_fraction,
                "flags": flags,
                "rejected_by_flags": rejected_by_flags,
                "rejected_by_index": rejected_by_index,
                "review_status": "rejected" if status == "rejected" else "pending",
            }
            rows.append(row)
            counts[status] += 1
            for flag in flags:
                counts[f"flag:{flag}"] = counts.get(f"flag:{flag}", 0) + 1
        except Exception as e:  # noqa: BLE001 - data-prep manifest should preserve failures
            rows.append(
                {
                    "index": idx,
                    "status": "error",
                    "source_file": str(wav),
                    "error": f"{e.__class__.__name__}: {e}",
                    "review_status": "rejected",
                }
            )
            counts["error"] += 1

    write_jsonl(output_dir / "manifest.jsonl", rows)
    if not args.dry_run:
        build_review_folders(output_dir, rows, args.review_random_n, args.seed)

    summary = {
        "policy": "Kratt-only candidate extraction from clean Kuule/Kule Kratt clips",
        "source_dirs": [str(s) for s in source_dirs],
        "output_dir": str(output_dir),
        "dry_run": bool(args.dry_run),
        "include_patterns": include_patterns,
        "exclude_patterns": exclude_patterns,
        "parameters": {
            "target_sr": args.target_sr,
            "frame_ms": args.frame_ms,
            "hop_ms": args.hop_ms,
            "speech_rel_db": args.speech_rel_db,
            "pre_roll_ms": args.pre_roll_ms,
            "post_roll_ms": args.post_roll_ms,
            "boundary_pre_roll_ms": args.boundary_pre_roll_ms,
            "min_cut_s": args.min_cut_s,
            "desired_min_cut_s": args.desired_min_cut_s,
            "max_cut_s": args.max_cut_s,
            "suspicious_min_s": args.suspicious_min_s,
            "suspicious_max_s": args.suspicious_max_s,
            "low_confidence_threshold": args.low_confidence_threshold,
            "search_min_fraction": args.search_min_fraction,
            "search_max_fraction": args.search_max_fraction,
            "boundary_target_fraction": args.boundary_target_fraction,
            "min_boundary_tail_s": args.min_boundary_tail_s,
            "reject_flags": sorted(reject_flags),
            "reject_indices": sorted(reject_indices),
            "min_source_duration_s": args.min_source_duration_s,
            "max_source_duration_s": args.max_source_duration_s,
        },
        "counts": counts,
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(f"Kratt segment extraction: {output_dir}")
    before_filter = counts.get("source_wavs_before_duration_filter", len(wavs))
    if before_filter != len(wavs):
        print(f"  source wavs: {len(wavs)} kept / {before_filter} matched before duration filter")
        print(f"  skipped_source_too_short: {counts.get('skipped_source_too_short', 0)}")
        print(f"  skipped_source_too_long: {counts.get('skipped_source_too_long', 0)}")
    else:
        print(f"  source wavs: {len(wavs)}")
    print(f"  candidates: {counts.get('candidate', 0)}")
    print(f"  rejected: {counts.get('rejected', 0)}")
    print(f"  errors: {counts.get('error', 0)}")
    for key in sorted(k for k in counts if k.startswith("flag:")):
        print(f"  {key}: {counts[key]}")
    if args.dry_run:
        print("  dry-run: audio cuts and review symlinks were not written")
    else:
        print(f"  review CSV: {output_dir / 'review' / 'review.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
