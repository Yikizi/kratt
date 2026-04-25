#!/usr/bin/env python3
"""Build a correlated wav↔event index after a kratt android pull.

Given a pull directory containing .wav files + events.jsonl, produces
index.jsonl — one flat record per wav combining:
  - local_wav (absolute path on this machine)
  - wav_basename
  - event_ts (ISO)
  - trigger_model, trigger_score
  - scores (map of all co-running models' scores at that frame)
  - session_threshold, session_duration_s
  - label (initial: "unlabeled", for later labelling)
  - transcript (initial: null, for later STT labelling)

Also prints orphan counts:
  - wavs with no matching event (event log truncated or wav sneaked in)
  - events with no matching wav (wav save failed or session still writing)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime


def parse_ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pull_dir", type=Path, help="Directory from kratt android pull")
    ap.add_argument("--out", type=Path, default=None,
                    help="Output path (default: <pull_dir>/index.jsonl)")
    args = ap.parse_args()

    pull = args.pull_dir
    if not pull.is_dir():
        sys.exit(f"Not a directory: {pull}")

    events_path = pull / "events.jsonl"
    if not events_path.exists():
        sys.exit(f"No events.jsonl in {pull}")

    out_path = args.out or (pull / "index.jsonl")

    # Index events by wav basename
    event_by_basename: dict[str, dict] = {}
    session_boundary_ts: list[tuple[datetime, dict]] = []  # (start_ts, header)
    current_session: dict | None = None

    with events_path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("session_start"):
                current_session = rec
                session_boundary_ts.append((parse_ts(rec["ts"]), rec))
                continue
            if rec.get("session_end"):
                continue
            if "wav" not in rec:
                continue
            basename = Path(rec["wav"]).name
            # Attach session context to each event
            if current_session is not None:
                rec["_session_threshold"] = current_session.get("threshold")
                rec["_session_models"] = current_session.get("models") or [
                    current_session.get("model")
                ]
            event_by_basename[basename] = rec

    # Walk local wavs
    wavs = sorted(pull.rglob("*.wav"))
    merged = []
    orphan_wavs = []
    for w in wavs:
        evt = event_by_basename.get(w.name)
        if evt is None:
            orphan_wavs.append(w.name)
            continue
        merged.append({
            "local_wav": str(w),
            "wav_basename": w.name,
            "event_ts": evt.get("ts"),
            "trigger_model": evt.get("trigger_model") or evt.get("model"),
            "trigger_score": evt.get("trigger_score") or evt.get("score"),
            "scores": evt.get("scores", {}),
            "session_threshold": evt.get("_session_threshold"),
            "session_models": evt.get("_session_models", []),
            "cooldown_sec": evt.get("cooldown_sec"),
            "pre_roll_sec": evt.get("pre_roll_sec"),
            "post_roll_sec": evt.get("post_roll_sec"),
            "label": "unlabeled",
            "transcript": None,
        })

    wav_basenames = {w.name for w in wavs}
    orphan_events = [b for b in event_by_basename if b not in wav_basenames]

    out_path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in merged) + "\n")

    # Summary
    print(f"→ Indexed {len(merged)} wav↔event records → {out_path}")
    if orphan_wavs:
        print(f"  ⚠ {len(orphan_wavs)} wavs have NO matching event")
        for w in orphan_wavs[:3]:
            print(f"    {w}")
        if len(orphan_wavs) > 3:
            print(f"    ... (+{len(orphan_wavs) - 3} more)")
    if orphan_events:
        print(f"  ⚠ {len(orphan_events)} events have NO matching wav (wav save may have failed)")
        for b in orphan_events[:3]:
            print(f"    {b}")
        if len(orphan_events) > 3:
            print(f"    ... (+{len(orphan_events) - 3} more)")


if __name__ == "__main__":
    main()
