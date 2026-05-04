#!/usr/bin/env python3
"""Fast terminal reviewer for Kratt-only segment extraction outputs.

Loads an extraction dataset directory containing `manifest.jsonl`, plays clips from
`accepted/`, and persists accept/reject labels under `review/` without relying on
browser localStorage.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

WAKE_WORD_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = WAKE_WORD_ROOT.parent

STATUS_PENDING = "pending"
STATUS_ACCEPT = "accept"
STATUS_REJECT = "reject"


class PreviewAudio:
    """Creates temporary louder preview WAVs without modifying dataset audio."""

    def __init__(self, *, normalize: bool, max_gain_db: float, target_peak: float) -> None:
        self.normalize = normalize
        self.max_gain_db = max_gain_db
        self.target_peak = target_peak
        self._tmpdir = tempfile.TemporaryDirectory(prefix="kratt-review-audio-")
        self._cache: dict[str, Path] = {}

    @property
    def description(self) -> str:
        mode = "norm" if self.normalize else "gain"
        return f"{mode} max+{self.max_gain_db:.0f}dB peak={self.target_peak:.2f}"

    def clear(self) -> None:
        self._cache.clear()
        root = Path(self._tmpdir.name)
        for wav in root.glob("*.wav"):
            try:
                wav.unlink()
            except OSError:
                pass

    def set_gain_db(self, gain_db: float) -> None:
        self.max_gain_db = max(0.0, min(48.0, gain_db))
        self.clear()

    def cleanup(self) -> None:
        self._tmpdir.cleanup()

    def prepare(self, path: Path) -> Path:
        if self.max_gain_db <= 0.01 and not self.normalize:
            return path
        try:
            st = path.stat()
            key_text = f"{path.resolve()}|{st.st_mtime_ns}|{st.st_size}|{self.normalize}|{self.max_gain_db:.2f}|{self.target_peak:.3f}"
            key = hashlib.sha256(key_text.encode("utf-8")).hexdigest()[:24]
            cached = self._cache.get(key)
            if cached and cached.exists():
                return cached

            audio, sr = sf.read(str(path), always_2d=True, dtype="float32")
            if audio.size == 0:
                return path
            peak = float(np.max(np.abs(audio)))
            if peak <= 1e-8:
                return path
            max_gain = 10.0 ** (self.max_gain_db / 20.0)
            if self.normalize:
                scale = 1.0 if peak >= self.target_peak else min(max_gain, self.target_peak / peak)
            else:
                scale = max_gain
            if scale <= 1.01:
                return path
            preview = np.clip(audio * scale, -0.98, 0.98).astype(np.float32)
            out = Path(self._tmpdir.name) / f"preview_{key}.wav"
            sf.write(str(out), preview, sr, subtype="PCM_16")
            self._cache[key] = out
            return out
        except Exception:
            return path


@dataclass
class Player:
    argv_prefix: list[str]
    process: subprocess.Popen[bytes] | None = None

    def stop(self) -> None:
        if self.process is None:
            return
        proc = self.process
        if proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=0.25)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        self.process = None

    def play(self, path: Path) -> None:
        self.stop()
        self.process = subprocess.Popen(
            self.argv_prefix + [str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def resolve_path(text: str | Path) -> Path:
    path = Path(text).expanduser()
    if path.is_absolute():
        return path.resolve()
    if path.parts and path.parts[0] == WAKE_WORD_ROOT.name:
        return (REPO_ROOT / path).resolve()
    if path.parts and path.parts[0] == "data":
        return (WAKE_WORD_ROOT / path).resolve()
    return (Path.cwd() / path).resolve()


def repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_manifest(dataset: Path) -> list[dict[str, Any]]:
    manifest = dataset / "manifest.jsonl"
    if not manifest.exists():
        raise SystemExit(f"Missing manifest: {manifest}")
    rows: list[dict[str, Any]] = []
    with manifest.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("status") == "error":
                continue
            if not row.get("output_file"):
                continue
            rows.append(row)
    return sorted(rows, key=lambda r: int(r.get("index", 0)))


def load_labels(path: Path) -> dict[int, str]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    labels_raw = data.get("labels", {})
    labels: dict[int, str] = {}
    for key, value in labels_raw.items():
        try:
            idx = int(key)
        except ValueError:
            continue
        if isinstance(value, dict):
            status = str(value.get("status", STATUS_PENDING))
        else:
            status = str(value)
        if status in {STATUS_ACCEPT, STATUS_REJECT, STATUS_PENDING}:
            labels[idx] = status
    return labels


def seed_labels_from_manifest(rows: list[dict[str, Any]]) -> dict[int, str]:
    labels: dict[int, str] = {}
    for row in rows:
        idx = int(row["index"])
        status = str(row.get("status", ""))
        review_status = str(row.get("review_status", ""))
        if status == "rejected" or review_status == "rejected":
            labels[idx] = STATUS_REJECT
        elif review_status.startswith("accepted") or review_status == STATUS_ACCEPT:
            labels[idx] = STATUS_ACCEPT
    return labels


def merge_seed_indices(labels: dict[int, str], rejects: list[int], accepts: list[int], unmarks: list[int]) -> None:
    for idx in rejects:
        labels[int(idx)] = STATUS_REJECT
    for idx in accepts:
        labels[int(idx)] = STATUS_ACCEPT
    for idx in unmarks:
        labels.pop(int(idx), None)


def row_status(labels: dict[int, str], row: dict[str, Any]) -> str:
    return labels.get(int(row["index"]), STATUS_PENDING)


def row_audio_path(dataset: Path, row: dict[str, Any]) -> Path:
    return dataset / str(row["output_file"])


def filter_rows(rows: list[dict[str, Any]], only_flags: list[str], only_sources: list[str]) -> list[dict[str, Any]]:
    out = rows
    if only_flags:
        required = set(only_flags)
        out = [r for r in out if required.intersection(set(r.get("flags", [])))]
    if only_sources:
        source_needles = [s.lower() for s in only_sources]
        out = [r for r in out if any(n in str(r.get("source_file", "")).lower() for n in source_needles)]
    return out


def save_outputs(dataset: Path, rows: list[dict[str, Any]], labels: dict[int, str]) -> None:
    review_dir = dataset / "review"
    review_dir.mkdir(parents=True, exist_ok=True)
    labels_path = review_dir / "terminal-labels.json"
    csv_path = review_dir / "terminal-review.csv"
    reject_args_path = review_dir / "reject-args.txt"

    payload = {
        "dataset": str(dataset),
        "updated_at": now_iso(),
        "labels": {
            str(idx): {"status": status, "updated_at": now_iso()}
            for idx, status in sorted(labels.items())
            if status in {STATUS_ACCEPT, STATUS_REJECT}
        },
    }
    tmp = labels_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(labels_path)

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "index",
                "review_status",
                "output_file",
                "source_file",
                "confidence",
                "duration_ms",
                "flags",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "index": int(row["index"]),
                    "review_status": row_status(labels, row),
                    "output_file": row.get("output_file", ""),
                    "source_file": row.get("source_file", ""),
                    "confidence": row.get("confidence", ""),
                    "duration_ms": row.get("crop_duration_ms", ""),
                    "flags": ";".join(row.get("flags", [])),
                }
            )

    rejects = sorted(idx for idx, status in labels.items() if status == STATUS_REJECT)
    reject_args_path.write_text(" ".join(f"--reject-index {idx}" for idx in rejects) + "\n", encoding="utf-8")


def find_start_pos(rows: list[dict[str, Any]], labels: dict[int, str], start_index: int | None, resume: bool) -> int:
    if not rows:
        return 0
    if start_index is not None:
        for pos, row in enumerate(rows):
            if int(row["index"]) >= start_index:
                return pos
        return len(rows) - 1
    if resume:
        for pos, row in enumerate(rows):
            if row_status(labels, row) == STATUS_PENDING:
                return pos
    return 0


def detect_player(player_arg: str | None) -> list[str]:
    if player_arg:
        return shlex.split(player_arg)
    candidates = [
        ("afplay", ["afplay"]),
        ("ffplay", ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"]),
        ("aplay", ["aplay", "-q"]),
        ("paplay", ["paplay"]),
    ]
    for exe, argv in candidates:
        if shutil.which(exe):
            return argv
    raise SystemExit("No audio player found. Install/use afplay, ffplay, aplay, or pass --player 'cmd ...'")


def truncate(text: str, width: int) -> str:
    if width <= 1:
        return ""
    if len(text) <= width:
        return text
    return text[: max(0, width - 1)] + "…"


def status_counts(rows: list[dict[str, Any]], labels: dict[int, str]) -> dict[str, int]:
    counts = {STATUS_PENDING: 0, STATUS_ACCEPT: 0, STATUS_REJECT: 0}
    for row in rows:
        counts[row_status(labels, row)] += 1
    return counts


def terminal_review(
    dataset: Path,
    rows: list[dict[str, Any]],
    export_rows: list[dict[str, Any]],
    labels: dict[int, str],
    *,
    start_pos: int,
    player_argv: list[str],
    autoplay: bool,
    autoplay_delay_ms: int,
    mark_advance: bool,
    preview_audio: PreviewAudio,
) -> None:
    import curses

    player = Player(player_argv)
    current = start_pos
    pending_play_pos: int | None = None
    pending_play_at = 0.0
    dirty = False
    message = ""

    def mark_current(status: str | None) -> None:
        nonlocal current, dirty, message, pending_play_pos, pending_play_at
        row = rows[current]
        idx = int(row["index"])
        if status is None:
            labels.pop(idx, None)
            message = f"unmarked {idx:05d}"
        else:
            labels[idx] = status
            message = f"{status} {idx:05d}"
        dirty = True
        save_outputs(dataset, export_rows, labels)
        if mark_advance and current < len(rows) - 1:
            current += 1
            if autoplay:
                pending_play_pos = current
                pending_play_at = time.monotonic() + autoplay_delay_ms / 1000.0

    def move(delta: int) -> None:
        nonlocal current, pending_play_pos, pending_play_at, message
        new_pos = max(0, min(len(rows) - 1, current + delta))
        if new_pos == current:
            return
        current = new_pos
        message = ""
        if autoplay:
            player.stop()
            pending_play_pos = current
            pending_play_at = time.monotonic() + autoplay_delay_ms / 1000.0

    def jump_prompt(stdscr: Any) -> None:
        nonlocal current, message, pending_play_pos, pending_play_at
        curses.echo()
        h, w = stdscr.getmaxyx()
        prompt = "jump to source index: "
        stdscr.addstr(h - 1, 0, " " * max(0, w - 1))
        stdscr.addstr(h - 1, 0, prompt)
        stdscr.refresh()
        try:
            raw = stdscr.getstr(h - 1, len(prompt), 12).decode("utf-8", errors="replace").strip()
            target = int(raw)
        except Exception:
            message = "jump cancelled"
            curses.noecho()
            return
        curses.noecho()
        current = find_start_pos(rows, labels, target, False)
        message = f"jumped to {int(rows[current]['index']):05d}"
        if autoplay:
            pending_play_pos = current
            pending_play_at = time.monotonic() + autoplay_delay_ms / 1000.0

    def draw(stdscr: Any) -> None:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        row = rows[current]
        idx = int(row["index"])
        counts = status_counts(rows, labels)
        status = row_status(labels, row)
        flags = ",".join(row.get("flags", [])) or "-"
        output = str(row.get("output_file", ""))
        source = repo_relative(Path(str(row.get("source_file", ""))))
        audio_path = row_audio_path(dataset, row)

        header = f"Kratt review | {repo_relative(dataset)} | {current + 1}/{len(rows)} | idx {idx:05d} | {status.upper()}"
        try:
            curses.init_pair(1, curses.COLOR_GREEN, -1)
            curses.init_pair(2, curses.COLOR_RED, -1)
            curses.init_pair(3, curses.COLOR_YELLOW, -1)
            curses.init_pair(4, curses.COLOR_CYAN, -1)
        except Exception:
            pass
        color = curses.color_pair(3)
        if status == STATUS_ACCEPT:
            color = curses.color_pair(1)
        elif status == STATUS_REJECT:
            color = curses.color_pair(2)

        stdscr.addstr(0, 0, truncate(header, w - 1), curses.A_BOLD | color)
        stdscr.addstr(1, 0, truncate(f"pending={counts[STATUS_PENDING]} accept={counts[STATUS_ACCEPT]} reject={counts[STATUS_REJECT]} | autoplay={'on' if autoplay else 'off'} | preview={preview_audio.description} | player={' '.join(player_argv)}", w - 1))
        stdscr.addstr(3, 0, truncate(f"output: {output}", w - 1))
        stdscr.addstr(4, 0, truncate(f"source: {source}", w - 1))
        stdscr.addstr(5, 0, truncate(f"audio : {repo_relative(audio_path)} {'OK' if audio_path.exists() else 'MISSING'}", w - 1))
        stdscr.addstr(6, 0, truncate(f"conf={row.get('confidence', '')} dur={row.get('crop_duration_ms', '')}ms method={row.get('method', '')} flags={flags}", w - 1))
        stdscr.addstr(8, 0, truncate("keys: j/k move | o/space replay | r reject+next | a accept+next | +/- volume | u unmark | g jump | s save | q quit", w - 1), curses.color_pair(4))
        if message:
            stdscr.addstr(9, 0, truncate(message, w - 1), curses.A_BOLD)

        top = max(0, current - 6)
        bottom = min(len(rows), top + max(3, h - 12))
        for line_no, pos in enumerate(range(top, bottom), start=11):
            if line_no >= h - 1:
                break
            r = rows[pos]
            s = row_status(labels, r)
            marker = ">" if pos == current else " "
            stat_char = {STATUS_PENDING: ".", STATUS_ACCEPT: "A", STATUS_REJECT: "R"}[s]
            flag_text = ",".join(r.get("flags", []))
            src_name = Path(str(r.get("source_file", ""))).name
            line = f"{marker} {stat_char} {int(r['index']):05d} {int(r.get('crop_duration_ms', 0)):4d}ms c={float(r.get('confidence', 0.0)):.3f} {src_name} {flag_text}"
            attr = curses.A_REVERSE if pos == current else curses.A_NORMAL
            if s == STATUS_ACCEPT:
                attr |= curses.color_pair(1)
            elif s == STATUS_REJECT:
                attr |= curses.color_pair(2)
            stdscr.addstr(line_no, 0, truncate(line, w - 1), attr)
        stdscr.refresh()

    def loop(stdscr: Any) -> None:
        nonlocal pending_play_pos, dirty, message
        curses.curs_set(0)
        curses.use_default_colors()
        stdscr.timeout(30)
        draw(stdscr)
        while True:
            if pending_play_pos is not None and time.monotonic() >= pending_play_at:
                player.play(preview_audio.prepare(row_audio_path(dataset, rows[pending_play_pos])))
                pending_play_pos = None
                draw(stdscr)
            ch = stdscr.getch()
            if ch == -1:
                continue
            key = chr(ch).lower() if 0 <= ch < 256 else ""
            if key == "q":
                save_outputs(dataset, export_rows, labels)
                message = "saved; quitting"
                draw(stdscr)
                break
            if key == "s":
                save_outputs(dataset, export_rows, labels)
                dirty = False
                message = "saved"
            elif key == "j" or ch == curses.KEY_DOWN:
                move(1)
            elif key == "k" or ch == curses.KEY_UP:
                move(-1)
            elif key == "o" or key == " " or ch in (10, 13):
                pending_play_pos = None
                player.play(preview_audio.prepare(row_audio_path(dataset, rows[current])))
            elif key in {"+", "="}:
                preview_audio.set_gain_db(preview_audio.max_gain_db + 3.0)
                message = f"preview gain max +{preview_audio.max_gain_db:.0f} dB"
            elif key in {"-", "_"}:
                preview_audio.set_gain_db(preview_audio.max_gain_db - 3.0)
                message = f"preview gain max +{preview_audio.max_gain_db:.0f} dB"
            elif key == "r":
                mark_current(STATUS_REJECT)
            elif key == "a":
                mark_current(STATUS_ACCEPT)
            elif key == "u":
                mark_current(None)
            elif key == "g":
                jump_prompt(stdscr)
            draw(stdscr)

    try:
        import curses

        curses.wrapper(loop)
    finally:
        player.stop()
        preview_audio.cleanup()
        if dirty:
            save_outputs(dataset, export_rows, labels)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--dataset",
        "--output-dir",
        default=str(WAKE_WORD_ROOT / "data" / "processed" / "positive_kratt_only_v19a"),
        help="Extraction output directory containing manifest.jsonl",
    )
    ap.add_argument("--start-index", type=int, default=None, help="Start at the first row with source index >= N")
    ap.add_argument("--resume", action="store_true", help="Start at first pending row")
    ap.add_argument("--reject-index", action="append", type=int, default=[], help="Seed/record rejected source index; may repeat")
    ap.add_argument("--accept-index", action="append", type=int, default=[], help="Seed/record accepted source index; may repeat")
    ap.add_argument("--unmark-index", action="append", type=int, default=[], help="Remove a saved label for this source index; may repeat")
    ap.add_argument("--only-flag", action="append", default=[], help="Review only rows with this flag; may repeat")
    ap.add_argument("--only-source", action="append", default=[], help="Review only rows whose source path contains this text; may repeat")
    ap.add_argument("--player", default=None, help="Audio player command prefix. Default auto-detects afplay/ffplay/aplay/paplay")
    ap.add_argument(
        "--preview-gain-db",
        type=float,
        default=24.0,
        help="Maximum temporary preview boost in dB. Does not modify dataset WAVs. Default: 24 dB.",
    )
    ap.add_argument(
        "--preview-target-peak",
        type=float,
        default=0.95,
        help="Target peak for normalized preview WAVs. Default: 0.95.",
    )
    ap.add_argument(
        "--no-normalize-preview",
        action="store_true",
        help="Disable temp preview normalization; use fixed --preview-gain-db boost instead.",
    )
    ap.add_argument("--no-autoplay", action="store_true", help="Do not autoplay after j/k movement")
    ap.add_argument("--autoplay-delay-ms", type=int, default=120, help="Delay playback after movement; helps rapid j/k skipping")
    ap.add_argument("--no-mark-advance", action="store_true", help="Do not advance automatically after r/a")
    ap.add_argument("--export-only", action="store_true", help="Apply seed labels and write review export files without opening curses UI")
    args = ap.parse_args()

    dataset = resolve_path(args.dataset)
    rows_all = load_manifest(dataset)
    if not rows_all:
        raise SystemExit(f"No reviewable rows in {dataset / 'manifest.jsonl'}")

    labels = seed_labels_from_manifest(rows_all)
    labels.update(load_labels(dataset / "review" / "terminal-labels.json"))
    merge_seed_indices(labels, args.reject_index, args.accept_index, args.unmark_index)
    save_outputs(dataset, rows_all, labels)

    rows = filter_rows(rows_all, args.only_flag, args.only_source)
    if not rows:
        raise SystemExit("No rows left after --only-flag/--only-source filters")

    if args.export_only:
        rejects = sorted(idx for idx, status in labels.items() if status == STATUS_REJECT)
        print(f"saved labels for {repo_relative(dataset)}")
        print(f"rows: {len(rows_all)}")
        print(f"rejects: {len(rejects)}")
        print(f"reject args: {dataset / 'review' / 'reject-args.txt'}")
        return 0

    start_pos = find_start_pos(rows, labels, args.start_index, args.resume)
    player_argv = detect_player(args.player)
    preview_audio = PreviewAudio(
        normalize=not args.no_normalize_preview,
        max_gain_db=args.preview_gain_db,
        target_peak=max(0.05, min(0.98, args.preview_target_peak)),
    )
    terminal_review(
        dataset,
        rows,
        rows_all,
        labels,
        start_pos=start_pos,
        player_argv=player_argv,
        autoplay=not args.no_autoplay,
        autoplay_delay_ms=args.autoplay_delay_ms,
        mark_advance=not args.no_mark_advance,
        preview_audio=preview_audio,
    )
    print(f"saved: {dataset / 'review' / 'terminal-labels.json'}")
    print(f"reject args: {dataset / 'review' / 'reject-args.txt'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
