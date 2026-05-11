#!/usr/bin/env python3
"""Apply Kratt time-tracking proposals to Clockify and GitLab.

Reads ~/.kratt-time-log/proposals/YYYY-MM-DD.jsonl records created by
propose_commit.py and creates:
- Clockify manual time entries for KRATT_CLOCKIFY_PROJECT_ID
- GitLab issue notes with /spend quick actions

Designed to be safe to re-run: records get per-backend markers and are skipped
once applied/skipped.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

LOG_DIR = Path.home() / ".kratt-time-log"
PROPOSALS_DIR = LOG_DIR / "proposals"
APPLY_LOG = LOG_DIR / "logs" / "apply.log"
DEFAULT_GITLAB_REPO = os.environ.get("KRATT_GITLAB_REPO", "malinh/iaib")
DEFAULT_PROJECT_ID = os.environ.get("KRATT_CLOCKIFY_PROJECT_ID", "")


def log(msg: str) -> None:
    APPLY_LOG.parent.mkdir(parents=True, exist_ok=True)
    with APPLY_LOG.open("a") as f:
        f.write(f"{datetime.now().isoformat(timespec='seconds')} {msg}\n")


def parse_ts(ts: str) -> datetime:
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if dt.tzinfo is not None:
        dt = dt.astimezone()
    return dt.replace(tzinfo=None)


def fmt_clockify(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M")


def fmt_gitlab_duration(minutes: int) -> str:
    hours, mins = divmod(minutes, 60)
    parts: list[str] = []
    if hours:
        parts.append(f"{hours}h")
    if mins or not parts:
        parts.append(f"{mins}m")
    return " ".join(parts)


def commit_patch_id(commit_hash: str) -> str | None:
    """Stable patch-id for duplicate cherry-pick/consolidation detection."""
    if not commit_hash:
        return None
    try:
        patch = subprocess.check_output(
            ["git", "show", commit_hash, "--pretty=format:", "--patch"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        if not patch.strip():
            return None
        result = subprocess.run(
            ["git", "patch-id", "--stable"],
            input=patch,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None
        return result.stdout.split()[0]
    except Exception:
        return None


def load_file(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open() as f:
        for line in f:
            if not line.strip():
                continue
            rows.append(json.loads(line))
    return rows


def write_file(path: Path, rows: list[dict[str, Any]]) -> None:
    backup = path.with_suffix(path.suffix + f".bak-{datetime.now().strftime('%Y%m%d%H%M%S')}")
    if path.exists():
        shutil.copy2(path, backup)
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def should_consider(row: dict[str, Any], include_low: bool) -> tuple[bool, str]:
    if row.get("applied"):
        return False, "already applied"
    if row.get("skipped"):
        return False, "already skipped"
    minutes = int(row.get("duration_min") or 0)
    if minutes <= 0:
        return True, "zero-duration skip"
    if row.get("confidence") == "low" and not include_low:
        return True, "low-confidence skip"
    if not str(row.get("issue", "")).startswith("#"):
        return True, "missing GitLab issue skip"
    return True, "apply"


def apply_clockify(row: dict[str, Any], project_id: str, dry_run: bool) -> tuple[bool, str]:
    if row.get("clockify_id"):
        return True, str(row["clockify_id"])
    minutes = int(row.get("duration_min") or 0)
    start = parse_ts(str(row["ts"]))
    end = start + timedelta(minutes=minutes)
    desc = f"{row.get('description', '').strip()} [{row.get('issue', '?')} {str(row.get('hash', ''))[:8]}]"
    cmd = [
        "clockify-cli",
        "manual",
        "-i=0",
        "-q",
        "-p",
        project_id,
        "--when",
        fmt_clockify(start),
        "--when-to-close",
        fmt_clockify(end),
        "--description",
        desc,
    ]
    if dry_run:
        return True, "DRY-RUN " + " ".join(cmd)
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode != 0:
        return False, (result.stderr or result.stdout).strip()
    return True, result.stdout.strip()


def apply_gitlab(row: dict[str, Any], repo: str, dry_run: bool) -> tuple[bool, str]:
    if row.get("gitlab_applied"):
        return True, "already"
    minutes = int(row.get("duration_min") or 0)
    issue = str(row.get("issue", "")).lstrip("#")
    msg = (
        f"/spend {fmt_gitlab_duration(minutes)}\n\n"
        f"Auto time hook: {row.get('description', '').strip()} "
        f"(`{str(row.get('hash', ''))[:8]}`, `{row.get('branch', '?')}`)."
    )
    cmd = ["glab", "issue", "note", issue, "-R", repo, "-m", msg]
    if dry_run:
        return True, "DRY-RUN " + " ".join(cmd)
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode != 0:
        return False, (result.stderr or result.stdout).strip()
    return True, result.stdout.strip() or "ok"


def apply_row(
    row: dict[str, Any],
    *,
    project_id: str,
    repo: str,
    dry_run: bool,
    include_low: bool,
    skip_clockify: bool,
    skip_gitlab: bool,
    mark_skipped: str | None,
) -> tuple[str, dict[str, Any]]:
    consider, reason = should_consider(row, include_low)
    now = datetime.now().isoformat(timespec="seconds")
    if not consider:
        return "ignored", row

    minutes = int(row.get("duration_min") or 0)
    if mark_skipped:
        row.update({"skipped": True, "skip_reason": mark_skipped, "applied_at": now})
        return "skipped", row
    if reason.endswith("skip") or minutes <= 0:
        row.update({"skipped": True, "skip_reason": reason, "applied_at": now})
        return "skipped", row

    if not project_id and not skip_clockify:
        raise RuntimeError("KRATT_CLOCKIFY_PROJECT_ID is not set")

    ok_clockify = True
    ok_gitlab = True
    if not skip_clockify:
        ok_clockify, clockify_result = apply_clockify(row, project_id, dry_run)
        row["clockify_result"] = clockify_result
        if ok_clockify and not dry_run:
            row["clockify_id"] = clockify_result
    if not skip_gitlab:
        ok_gitlab, gitlab_result = apply_gitlab(row, repo, dry_run)
        row["gitlab_result"] = gitlab_result
        if ok_gitlab and not dry_run:
            row["gitlab_applied"] = True

    if ok_clockify and ok_gitlab:
        if not dry_run:
            row.update({"applied": True, "applied_at": now})
        return "applied", row

    row["apply_error_at"] = now
    return "failed", row


def proposal_files(since: str | None, until: str | None) -> list[Path]:
    files = sorted(PROPOSALS_DIR.glob("*.jsonl"))
    if since:
        files = [p for p in files if p.stem >= since]
    if until:
        files = [p for p in files if p.stem <= until]
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply Kratt time-tracking proposals")
    parser.add_argument("--since", help="First proposal date YYYY-MM-DD")
    parser.add_argument("--until", help="Last proposal date YYYY-MM-DD")
    parser.add_argument("--hash", action="append", dest="hashes", help="Only apply matching commit hash prefix (repeatable)")
    parser.add_argument("--issue", action="append", dest="issues", help="Only apply matching issue, e.g. #19 (repeatable)")
    parser.add_argument("--exclude-issue", action="append", dest="exclude_issues", help="Skip matching issue, e.g. #20 (repeatable)")
    parser.add_argument("--dry-run", action="store_true", help="Print/apply no external changes")
    parser.add_argument("--include-low", action="store_true", help="Apply low-confidence proposals too")
    parser.add_argument("--mark-skipped", help="Mark selected proposals skipped with this reason instead of applying")
    parser.add_argument("--no-dedupe-patch-id", action="store_true", help="Do not skip duplicate cherry-pick patch-ids")
    parser.add_argument("--skip-clockify", action="store_true")
    parser.add_argument("--skip-gitlab", action="store_true")
    parser.add_argument("--repo", default=DEFAULT_GITLAB_REPO)
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    args = parser.parse_args()

    prefixes = tuple(args.hashes or [])
    include_issues = set(args.issues or [])
    exclude_issues = set(args.exclude_issues or [])
    totals = {"applied": 0, "skipped": 0, "ignored": 0, "failed": 0}
    minutes_by_status = {key: 0 for key in totals}

    seen_patch_ids: dict[str, str] = {}
    if not args.no_dedupe_patch_id:
        for path in proposal_files(None, None):
            for row in load_file(path):
                if not (row.get("applied") or row.get("skipped")):
                    continue
                h = str(row.get("hash", ""))
                pid = row.get("patch_id") or commit_patch_id(h)
                if pid:
                    seen_patch_ids.setdefault(str(pid), h[:8])

    for path in proposal_files(args.since, args.until):
        rows = load_file(path)
        changed = False
        for i, row in enumerate(rows):
            h = str(row.get("hash", ""))
            issue = str(row.get("issue", ""))
            if prefixes and not any(h.startswith(prefix) for prefix in prefixes):
                continue
            if include_issues and issue not in include_issues:
                continue
            if exclude_issues and issue in exclude_issues:
                continue
            pid = row.get("patch_id") or commit_patch_id(h)
            if pid:
                row["patch_id"] = pid
            before = json.dumps(row, sort_keys=True)
            try:
                if pid and pid in seen_patch_ids and not (row.get("applied") or row.get("skipped")):
                    row.update(
                        {
                            "skipped": True,
                            "skip_reason": f"duplicate patch-id of {seen_patch_ids[pid]}",
                            "applied_at": datetime.now().isoformat(timespec="seconds"),
                        }
                    )
                    status, new_row = "skipped", row
                else:
                    status, new_row = apply_row(
                        row,
                        project_id=args.project_id,
                        repo=args.repo,
                        dry_run=args.dry_run,
                        include_low=args.include_low,
                        skip_clockify=args.skip_clockify,
                        skip_gitlab=args.skip_gitlab,
                        mark_skipped=args.mark_skipped,
                    )
                    if pid and status in {"applied", "skipped"}:
                        seen_patch_ids.setdefault(str(pid), h[:8])
            except Exception as e:
                status, new_row = "failed", row
                new_row["apply_exception"] = repr(e)
            rows[i] = new_row
            totals[status] = totals.get(status, 0) + 1
            minutes_by_status[status] = minutes_by_status.get(status, 0) + int(new_row.get("duration_min") or 0)
            after = json.dumps(new_row, sort_keys=True)
            if before != after:
                changed = True
            print(
                f"{status:7} {path.stem} {h[:8]} {new_row.get('issue','?')} "
                f"{int(new_row.get('duration_min') or 0)}m {new_row.get('description','')}"
            )
            if status == "failed":
                print(f"  ERROR: {new_row.get('clockify_result') or new_row.get('gitlab_result') or new_row.get('apply_exception')}", file=sys.stderr)
                log(f"failed {h[:8]} {new_row.get('apply_exception') or new_row.get('clockify_result') or new_row.get('gitlab_result')}")
        if changed and not args.dry_run:
            write_file(path, rows)

    print("\nSummary:")
    for key in ("applied", "skipped", "ignored", "failed"):
        mins = minutes_by_status.get(key, 0)
        print(f"- {key}: {totals.get(key, 0)} records, {mins // 60}h {mins % 60}m")
    return 1 if totals.get("failed") else 0


if __name__ == "__main__":
    raise SystemExit(main())
