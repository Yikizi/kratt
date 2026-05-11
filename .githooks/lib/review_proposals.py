#!/usr/bin/env python3
"""Tier 2: pre-push batch review.

Collects proposals for commits in the push range, summarizes by issue,
flags missing entries, writes ~/.kratt-time-log/review-pending.md.

Pre-push stdin format (one line per ref):
    <local_ref> <local_sha> <remote_ref> <remote_sha>
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR = Path.home() / ".kratt-time-log"
PROPOSALS_DIR = LOG_DIR / "proposals"
REVIEW_FILE = LOG_DIR / "review-pending.md"
LOGS_DIR = LOG_DIR / "logs"
ERR_LOG = LOGS_DIR / "review-errors.log"

ZERO = "0" * 40
DEFAULT_AGENT = os.environ.get("KRATT_TIME_AGENT_DEEP", "claude --print")
TIMEOUT_SEC = int(os.environ.get("KRATT_TIME_REVIEW_TIMEOUT", "240"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def log_err(msg: str) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with ERR_LOG.open("a") as f:
        f.write(f"{datetime.now().isoformat()} {msg}\n")


def collect_push_hashes() -> set[str]:
    hashes: set[str] = set()
    for raw in sys.stdin:
        parts = raw.split()
        if len(parts) < 4:
            continue
        _, local_sha, _, remote_sha = parts[0], parts[1], parts[2], parts[3]
        if local_sha == ZERO:
            continue  # branch deletion
        try:
            if remote_sha == ZERO:
                # New branch — ancestors not on any other ref
                out = git(
                    "rev-list",
                    local_sha,
                    "--not",
                    "--branches=*",
                    "--remotes=*",
                )
            else:
                out = git("rev-list", f"{remote_sha}..{local_sha}")
            for h in out.splitlines():
                if h.strip():
                    hashes.add(h.strip())
        except subprocess.CalledProcessError as e:
            log_err(f"rev-list failed: {e}")
    return hashes


def collect_proposals(hashes: set[str]) -> list[dict]:
    proposals: list[dict] = []
    if not PROPOSALS_DIR.exists():
        return proposals
    for f in sorted(PROPOSALS_DIR.glob("*.jsonl")):
        with f.open() as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("hash") in hashes:
                    proposals.append(rec)
    return proposals


def maybe_call_agent(proposals: list[dict]) -> str | None:
    """Optional: ask deep agent to dedupe/aggregate same-issue blocks.

    For MVP we skip this and just summarize with shell logic. Returning None
    means use default summary path. Plumbed for future use.
    """
    return None


def write_review(hashes: set[str], proposals: list[dict]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    found_hashes = {p["hash"] for p in proposals}
    missing = sorted(hashes - found_hashes)

    by_issue: dict[str, list[dict]] = {}
    for p in proposals:
        by_issue.setdefault(p.get("issue", "?"), []).append(p)

    lines: list[str] = []
    now = datetime.now().isoformat(timespec="seconds")
    lines.append(f"# Pre-push time-tracking review — {now}")
    lines.append("")
    lines.append(f"- Commits in push: **{len(hashes)}**")
    lines.append(f"- Proposals found: **{len(proposals)}**")
    lines.append(f"- Missing proposals: **{len(missing)}**")
    total_min = sum(p.get("duration_min", 0) for p in proposals)
    applied_min = sum(p.get("duration_min", 0) for p in proposals if p.get("applied"))
    skipped_min = sum(p.get("duration_min", 0) for p in proposals if p.get("skipped"))
    pending_min = sum(p.get("duration_min", 0) for p in proposals if not p.get("applied") and not p.get("skipped"))
    lines.append(f"- Total proposed duration: **{total_min // 60}h {total_min % 60}m**")
    lines.append(f"- Applied/skipped/pending: **{applied_min // 60}h {applied_min % 60}m** / **{skipped_min // 60}h {skipped_min % 60}m** / **{pending_min // 60}h {pending_min % 60}m**")
    lines.append("")

    lines.append("## Summary by issue")
    if not by_issue:
        lines.append("_(no proposals)_")
    for issue, items in sorted(by_issue.items()):
        total = sum(p.get("duration_min", 0) for p in items)
        lines.append(
            f"- **{issue}** — {total // 60}h {total % 60}m ({len(items)} commit"
            f"{'s' if len(items) != 1 else ''})"
        )
    lines.append("")

    if missing:
        lines.append("## ⚠️ Missing proposals")
        for h in missing:
            try:
                msg = git("log", "-1", "--format=%s", h)
            except subprocess.CalledProcessError:
                msg = "?"
            lines.append(f"- `{h[:8]}` {msg}")
        lines.append("")

    lines.append("## Detail")
    for p in proposals:
        status = "applied" if p.get("applied") else "skipped" if p.get("skipped") else "pending"
        extra = f" ({p.get('skip_reason')})" if p.get("skipped") and p.get("skip_reason") else ""
        lines.append(
            f"- `{p.get('hash','?')[:8]}` {p.get('issue','?')} · "
            f"{p.get('duration_min',0)}min · "
            f"_{p.get('confidence','?')}_ · "
            f"**{status}**{extra} · "
            f"{p.get('description','')}"
        )
    lines.append("")
    lines.append("---")
    lines.append("Medium/high-confidence proposals auto-apply; inspect pending rows with `kratt time-apply --dry-run`.")

    REVIEW_FILE.write_text("\n".join(lines) + "\n")


def main() -> int:
    hashes = collect_push_hashes()
    if not hashes:
        return 0
    proposals = collect_proposals(hashes)
    write_review(hashes, proposals)

    total_min = sum(p.get("duration_min", 0) for p in proposals)
    applied_min = sum(p.get("duration_min", 0) for p in proposals if p.get("applied"))
    pending_min = sum(p.get("duration_min", 0) for p in proposals if not p.get("applied") and not p.get("skipped"))
    missing = len(hashes) - len({p["hash"] for p in proposals})

    sys.stderr.write("\n=== Pre-push time-tracking review ===\n")
    sys.stderr.write(f"  Commits: {len(hashes)} | Proposals: {len(proposals)}")
    sys.stderr.write(f" | Total: {total_min // 60}h {total_min % 60}m")
    sys.stderr.write(f" | Applied: {applied_min // 60}h {applied_min % 60}m")
    sys.stderr.write(f" | Pending: {pending_min // 60}h {pending_min % 60}m\n")
    if missing:
        sys.stderr.write(f"  ⚠️  {missing} commit(s) without proposal\n")
    sys.stderr.write(f"  Review: {REVIEW_FILE}\n\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        log_err(f"unhandled: {e!r}")
        sys.exit(0)
