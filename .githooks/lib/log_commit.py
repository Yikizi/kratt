#!/usr/bin/env python3
"""Tier 0: append commit metadata to ~/.kratt-time-log/commits.jsonl.

Pure-shell-equivalent logger. No LLM, no network. Always succeeds (exit 0).
Stdout: JSON {hash, gap_sec, ts} for orchestrator to pass to Tier 1.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR = Path.home() / ".kratt-time-log"
PROPOSALS_DIR = LOG_DIR / "proposals"
LOGS_DIR = LOG_DIR / "logs"
COMMITS_FILE = LOG_DIR / "commits.jsonl"
GAP_CAP_SEC = 5400  # 90 min — anything longer treated as "new session"


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def parse_shortstat(line: str) -> tuple[int, int, int]:
    files = ins = dels = 0
    for part in line.split(","):
        part = part.strip()
        if not part:
            continue
        n_str, _, kind = part.partition(" ")
        try:
            n = int(n_str)
        except ValueError:
            continue
        if "file" in kind:
            files = n
        elif "insertion" in kind:
            ins = n
        elif "deletion" in kind:
            dels = n
    return files, ins, dels


def previous_repo_ts(repo: str) -> str | None:
    if not COMMITS_FILE.exists():
        return None
    last = None
    with COMMITS_FILE.open() as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("repo") == repo:
                last = rec.get("ts")
    return last


def main() -> int:
    for d in (LOG_DIR, PROPOSALS_DIR, LOGS_DIR):
        d.mkdir(parents=True, exist_ok=True)

    repo = Path(git("rev-parse", "--show-toplevel")).name
    h = git("rev-parse", "HEAD")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    ts = git("log", "-1", "--format=%cI", "HEAD")
    msg = git("log", "-1", "--format=%s", "HEAD")
    author = git("log", "-1", "--format=%an", "HEAD")
    stats_line = subprocess.check_output(
        ["git", "log", "-1", "--shortstat", "--format=", "HEAD"], text=True
    ).strip()
    files_changed, insertions, deletions = parse_shortstat(stats_line)

    gap_sec = 0
    prev_ts = previous_repo_ts(repo)
    if prev_ts:
        try:
            prev = datetime.fromisoformat(prev_ts)
            cur = datetime.fromisoformat(ts)
            gap_sec = max(0, min(int((cur - prev).total_seconds()), GAP_CAP_SEC))
        except ValueError:
            gap_sec = 0

    record = {
        "ts": ts,
        "hash": h,
        "branch": branch,
        "repo": repo,
        "msg": msg,
        "author": author,
        "files_changed": files_changed,
        "insertions": insertions,
        "deletions": deletions,
        "gap_sec": gap_sec,
    }
    with COMMITS_FILE.open("a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(json.dumps({"hash": h, "gap_sec": gap_sec, "ts": ts}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        # Never break a commit. Log to stderr; orchestrator will skip Tier 1.
        sys.stderr.write(f"log_commit failed: {e!r}\n")
        sys.exit(0)
