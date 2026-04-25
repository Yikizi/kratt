#!/usr/bin/env python3
"""Analyze Android events.jsonl → per-model FAPH and co-trigger analysis.

The Android logger records one JSONL event per fired detection (any model
above threshold). Each event includes the trigger model's name, score,
and the scores of ALL co-running models at that frame — so we can compute
per-model FAPH at or above the operating threshold that was running, plus
see which models frequently trigger together (important for consensus
strategies).

Limitations:
- We only see frames where SOME model crossed the operating threshold.
- We CANNOT compute FAPH at thresholds below the one that was running
  (need to re-run inference on audio for that).
- Session duration estimated from first/last event ts per session.

Usage:
    python analyze_android_events.py path/to/events.jsonl
    python analyze_android_events.py path/to/events.jsonl --since 2026-04-14
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Session:
    start_ts: datetime
    end_ts: datetime
    threshold: float
    models: list[str] = field(default_factory=list)
    app_version: str = ""
    events: list[dict] = field(default_factory=list)

    @property
    def duration_s(self) -> float:
        return (self.end_ts - self.start_ts).total_seconds()

    @property
    def duration_h(self) -> float:
        return self.duration_s / 3600.0


def parse_ts(s: str) -> datetime:
    # Handles e.g. "2026-04-14T08:11:13.786Z"
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def load_sessions(path: Path) -> list[Session]:
    """Parse events.jsonl into per-session structures.

    A session starts at `session_start: true` and runs until either an
    explicit `session_end: true` (v0.3.0+) or the next session_start /
    EOF (fallback for older app versions).
    """
    sessions: list[Session] = []
    cur: Session | None = None

    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            ts = parse_ts(rec["ts"])

            if rec.get("session_start"):
                if cur is not None:
                    sessions.append(cur)
                models = rec.get("models", [rec.get("model", "unknown")])
                cur = Session(
                    start_ts=ts,
                    end_ts=ts,
                    threshold=float(rec.get("threshold", 0.85)),
                    models=list(models),
                    app_version=rec.get("app_version", ""),
                )
            elif rec.get("session_end"):
                if cur is not None:
                    # Use explicit duration if available (most accurate —
                    # includes tail silence after the last trigger).
                    dur = rec.get("duration_s")
                    if dur is not None:
                        cur.end_ts = cur.start_ts + __import__("datetime").timedelta(seconds=float(dur))
                    else:
                        cur.end_ts = ts
                    sessions.append(cur)
                    cur = None
            else:
                if cur is None:
                    continue
                cur.end_ts = ts
                cur.events.append(rec)

    if cur is not None:
        sessions.append(cur)

    return sessions


def analyze_session(s: Session) -> dict:
    """Return per-model FAPH at the operating threshold + co-trigger matrix."""
    trigger_counts: dict[str, int] = defaultdict(int)
    above_thresh_counts: dict[str, int] = defaultdict(int)
    cotrigger: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for evt in s.events:
        trig = evt.get("trigger_model", "unknown")
        trigger_counts[trig] += 1

        scores = evt.get("scores", {})
        # Count per model: how often was its score above the session threshold?
        above = [m for m, sc in scores.items() if sc >= s.threshold]
        for m in above:
            above_thresh_counts[m] += 1
        # Co-trigger: for every pair of models above threshold, increment
        for i, m1 in enumerate(above):
            for m2 in above:
                if m1 != m2:
                    cotrigger[m1][m2] += 1

    return {
        "trigger_counts": dict(trigger_counts),
        "above_thresh_counts": dict(above_thresh_counts),
        "cotrigger": {k: dict(v) for k, v in cotrigger.items()},
    }


def short(name: str) -> str:
    return name.removesuffix(".tflite").removeprefix("kuule_kratt_")


def format_session(idx: int, s: Session, stats: dict) -> str:
    out: list[str] = []
    out.append(f"\n── Session {idx}: {s.start_ts.isoformat(timespec='seconds')} "
               f"({s.duration_h:.2f}h, threshold {s.threshold:.2f}, v{s.app_version}) ──")
    out.append(f"   Models running ({len(s.models)}): "
               f"{', '.join(short(m) for m in s.models)}")
    out.append(f"   Total trigger events: {len(s.events)}")

    if s.duration_h < 0.01:
        out.append("   (duration < 36s — FAPH meaningless)")
        return "\n".join(out)

    # Sort by FAPH descending
    if stats["above_thresh_counts"]:
        out.append(f"\n   {'Model':20s} {'Triggers':>10s} {'Above thresh':>14s} {'FAPH':>10s}")
        rows = []
        for m in s.models:
            t = stats["trigger_counts"].get(m, 0)
            a = stats["above_thresh_counts"].get(m, 0)
            faph = a / s.duration_h
            rows.append((faph, m, t, a))
        rows.sort(reverse=True)
        for faph, m, t, a in rows:
            flag = " ← SILENT" if a == 0 else ""
            out.append(f"   {short(m):20s} {t:>10d} {a:>14d} {faph:>10.2f}{flag}")

    return "\n".join(out)


def format_cotrigger(sessions: list[Session]) -> str:
    """Cross-session co-trigger matrix showing model agreement."""
    totals: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    model_totals: dict[str, int] = defaultdict(int)

    for s in sessions:
        stats = analyze_session(s)
        for m1, d in stats["cotrigger"].items():
            for m2, c in d.items():
                totals[m1][m2] += c
        for m, c in stats["above_thresh_counts"].items():
            model_totals[m] += c

    models = sorted(model_totals.keys(), key=lambda m: -model_totals[m])
    if not models:
        return "\n(no co-triggers recorded)"

    out = ["\n── Co-trigger agreement (across all sessions) ──"]
    out.append("   When row model fires, % of the time col model also fires:")
    out.append("")
    hdr = "   " + " " * 20 + " ".join(f"{short(m)[:6]:>7s}" for m in models)
    out.append(hdr)
    for m1 in models:
        row_total = model_totals[m1]
        if row_total == 0:
            continue
        cells = []
        for m2 in models:
            if m1 == m2:
                cells.append("    —  ")
            else:
                pct = 100.0 * totals[m1].get(m2, 0) / row_total
                cells.append(f"{pct:>6.0f}%")
        out.append(f"   {short(m1):20s} " + " ".join(cells))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("events_jsonl", type=Path)
    ap.add_argument("--since", type=str, help="ISO date, only sessions on/after")
    ap.add_argument("--cotrigger", action="store_true",
                    help="Also print co-trigger agreement matrix")
    args = ap.parse_args()

    sessions = load_sessions(args.events_jsonl)

    if args.since:
        cutoff = parse_ts(args.since + "T00:00:00+00:00" if "T" not in args.since else args.since)
        sessions = [s for s in sessions if s.start_ts >= cutoff]

    if not sessions:
        sys.exit("No sessions found.")

    total_h = sum(s.duration_h for s in sessions)
    total_events = sum(len(s.events) for s in sessions)
    print(f"{len(sessions)} sessions, {total_h:.2f}h total listening, {total_events} trigger events")

    for i, s in enumerate(sessions, 1):
        stats = analyze_session(s)
        print(format_session(i, s, stats))

    if args.cotrigger:
        print(format_cotrigger(sessions))


if __name__ == "__main__":
    main()
