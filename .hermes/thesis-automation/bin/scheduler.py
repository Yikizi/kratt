#!/usr/bin/env python3
"""Long-running scheduler for Kratt thesis automation.

This replaces Claude Code session cron for the mechanical schedule.  It runs the
existing thesis-automation entrypoints directly, serially, with logs and a lock
so jobs do not overlap.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

REPO = Path(__file__).resolve().parents[3]
AUTO = REPO / ".hermes" / "thesis-automation"
LOGS = AUTO / "logs" / "scheduler"
STATE = AUTO / "state" / "scheduler.json"
LOCK = AUTO / "state" / "scheduler.lock"

DEFAULT_PATH = f"{Path.home()}/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"


def resolve_claude_bin() -> str:
    """Find Claude Code across the per-user installer and Homebrew paths."""
    override = os.environ.get("CLAUDE_BIN")
    if override:
        return override
    for candidate in (
        Path.home() / ".local" / "bin" / "claude",
        Path("/opt/homebrew/bin/claude"),
        Path("/usr/local/bin/claude"),
    ):
        if candidate.exists():
            return str(candidate)
    return "claude"


CLAUDE_BIN = resolve_claude_bin()


def now_local() -> dt.datetime:
    return dt.datetime.now().replace(microsecond=0)


def iso(t: dt.datetime | None = None) -> str:
    return (t or now_local()).isoformat()


def parse_iso(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value)
    except Exception:
        return None


def read_json(path: Path, default):
    try:
        if path.exists():
            return json.loads(path.read_text())
    except Exception:
        pass
    return default


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    tmp.replace(path)


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def next_hourly(after: dt.datetime, minute: int = 7) -> dt.datetime:
    c = after.replace(minute=minute, second=0, microsecond=0)
    if c <= after:
        c += dt.timedelta(hours=1)
    return c


def next_daily(after: dt.datetime, hour: int = 3, minute: int = 11) -> dt.datetime:
    c = after.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if c <= after:
        c += dt.timedelta(days=1)
    return c


def next_weekly(after: dt.datetime, weekday: int = 0, hour: int = 4, minute: int = 17) -> dt.datetime:
    # Python weekday: Monday=0.
    days = (weekday - after.weekday()) % 7
    c = (after + dt.timedelta(days=days)).replace(hour=hour, minute=minute, second=0, microsecond=0)
    if c <= after:
        c += dt.timedelta(days=7)
    return c


@dataclass(frozen=True)
class Job:
    name: str
    cmd: list[str]
    next_after: Callable[[dt.datetime], dt.datetime]
    catchup: dt.timedelta
    timeout_s: int


def build_jobs(include_research_distill: bool) -> list[Job]:
    jobs = [
        Job(
            name="hourly",
            cmd=[str(AUTO / "run-hourly.sh")],
            next_after=lambda t: next_hourly(t, 7),
            catchup=dt.timedelta(hours=2),
            timeout_s=60 * 60,
        ),
        Job(
            name="daily",
            cmd=[str(AUTO / "run-daily-consolidation.sh")],
            next_after=lambda t: next_daily(t, 3, 11),
            catchup=dt.timedelta(hours=24),
            timeout_s=3 * 60 * 60,
        ),
        Job(
            name="weekly",
            cmd=[str(AUTO / "run-weekly-review.sh")],
            next_after=lambda t: next_weekly(t, 0, 4, 17),
            catchup=dt.timedelta(days=7),
            timeout_s=3 * 60 * 60,
        ),
    ]
    if include_research_distill:
        jobs.append(
            Job(
                name="research-distill",
                cmd=[str(AUTO / "run-research-distill-cycle.sh"), "research-note", "distill-sentence"],
                next_after=lambda t: next_hourly(t, 15),
                catchup=dt.timedelta(hours=2),
                timeout_s=2 * 60 * 60,
            )
        )
    return jobs


def acquire_lock():
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    fh = LOCK.open("w")
    try:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print(f"another scheduler already holds {LOCK}", file=sys.stderr)
        sys.exit(2)
    fh.write(f"pid={os.getpid()} started={iso()}\n")
    fh.flush()
    return fh


def scheduler_log(msg: str) -> None:
    line = f"[{iso()}] {msg}"
    print(line, flush=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    with (LOGS / "scheduler.log").open("a") as f:
        f.write(line + "\n")


def ensure_job_state(state: dict, jobs: list[Job], reset: bool = False) -> dict:
    current = now_local()
    state.setdefault("jobs", {})
    known = {job.name: job for job in jobs}

    # Drop state for jobs that are no longer enabled.
    for stale in list(state["jobs"].keys()):
        if stale not in known:
            del state["jobs"][stale]

    for job in jobs:
        js = state["jobs"].setdefault(job.name, {})
        next_run = None if reset else parse_iso(js.get("next_run"))
        if next_run is None:
            js["next_run"] = job.next_after(current).isoformat()
            js.setdefault("runs", 0)
            js.setdefault("last_run", None)
            js.setdefault("last_rc", None)
            continue

        # If we were down for too long, skip stale backlog and resume from the
        # next future slot.  Short delays are caught up below by run_due_jobs().
        if current - next_run > job.catchup:
            js["skipped_stale_next_run"] = next_run.isoformat()
            js["next_run"] = job.next_after(current).isoformat()

    state["updated"] = iso(current)
    write_json(STATE, state)
    return state


def advance_next(job: Job, previous_next: dt.datetime | None, current: dt.datetime) -> str:
    # Run at most once per job per loop.  If several slots were missed while a
    # long job ran, skip backlog and resume with the first future slot.
    base = max(previous_next or current, current)
    return job.next_after(base).isoformat()


def claude_auth_smoke(timeout_s: int = 60) -> tuple[bool, str]:
    """Return whether Claude Code can make a tiny authenticated API call."""
    env = os.environ.copy()
    env["PATH"] = f"{DEFAULT_PATH}:{env.get('PATH', '')}"
    # This automation is intended to use Claude Code's first-party OAuth login.
    # A stale API-key/provider env from the parent shell can override OAuth and
    # turn every run into a 401, so keep the scheduled process OAuth-only.
    env.pop("CLAUDE_API_KEY", None)
    env.pop("CLAUDE_CODE_USE_OPENAI", None)

    cmd = [
        CLAUDE_BIN,
        "--print",
        "--output-format", "text",
        "--permission-mode", "default",
        "--model", "sonnet",
        "--tools", "",
        "--disable-slash-commands",
        "--strict-mcp-config",
        "--mcp-config", '{"mcpServers":{}}',
        "--no-session-persistence",
        "--max-budget-usd", "0.05",
    ]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(REPO),
            env=env,
            input="Reply OK only.\n",
            text=True,
            capture_output=True,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        return False, f"auth smoke timed out after {timeout_s}s"
    except FileNotFoundError:
        return False, f"claude binary not found: {CLAUDE_BIN}"

    if proc.returncode == 0:
        return True, "ok"
    detail = ((proc.stdout or "") + (proc.stderr or "")).strip().replace("\n", " ")
    return False, detail[:500] or f"claude exited rc={proc.returncode}"


def run_job(job: Job) -> dict:
    started = now_local()
    day_dir = LOGS / started.strftime("%Y-%m-%d")
    day_dir.mkdir(parents=True, exist_ok=True)
    slug = started.strftime("%Y%m%d_%H%M%S")
    stdout_path = day_dir / f"{slug}_{job.name}.stdout.log"
    stderr_path = day_dir / f"{slug}_{job.name}.stderr.log"

    scheduler_log(f"START {job.name}: {' '.join(job.cmd)}")
    env = os.environ.copy()
    env["PATH"] = f"{DEFAULT_PATH}:{env.get('PATH', '')}"
    env.setdefault("KRATT_DASHBOARD_QUIET", "1")
    env.setdefault("CLAUDE_BIN", CLAUDE_BIN)
    env.pop("CLAUDE_API_KEY", None)
    env.pop("CLAUDE_CODE_USE_OPENAI", None)

    timed_out = False
    rc: int | None = None
    with stdout_path.open("w") as out, stderr_path.open("w") as err:
        proc = subprocess.Popen(
            job.cmd,
            cwd=str(REPO),
            env=env,
            stdout=out,
            stderr=err,
            text=True,
            preexec_fn=os.setsid,
        )
        try:
            rc = proc.wait(timeout=job.timeout_s)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                rc = proc.wait(timeout=20)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                rc = proc.wait()

    finished = now_local()
    row = {
        "ts": iso(finished),
        "job": job.name,
        "cmd": job.cmd,
        "started": iso(started),
        "finished": iso(finished),
        "duration_s": int((finished - started).total_seconds()),
        "rc": rc,
        "timed_out": timed_out,
        "stdout_log": str(stdout_path.relative_to(REPO)),
        "stderr_log": str(stderr_path.relative_to(REPO)),
    }
    append_jsonl(LOGS / "runs.jsonl", row)
    status = "TIMEOUT" if timed_out else ("OK" if rc == 0 else f"RC={rc}")
    scheduler_log(f"END {job.name}: {status} in {row['duration_s']}s stdout={row['stdout_log']}")
    return row


def run_due_jobs(state: dict, jobs: list[Job], *, dry_run: bool = False) -> bool:
    current = now_local()
    ran_any = False
    for job in jobs:
        js = state["jobs"][job.name]
        next_run = parse_iso(js.get("next_run"))
        if next_run is None:
            js["next_run"] = job.next_after(current).isoformat()
            continue
        if current < next_run:
            continue
        if dry_run:
            scheduler_log(f"DUE {job.name} scheduled={next_run.isoformat()} cmd={' '.join(job.cmd)}")
            continue

        auth_ok, auth_detail = claude_auth_smoke()
        if not auth_ok:
            retry_at = current + dt.timedelta(minutes=15)
            js["last_auth_failure"] = iso(current)
            js["last_auth_failure_detail"] = auth_detail
            js["next_run"] = retry_at.isoformat()
            state["updated"] = iso(current)
            write_json(STATE, state)
            append_jsonl(LOGS / "auth-skips.jsonl", {
                "ts": iso(current),
                "job": job.name,
                "scheduled": next_run.isoformat(),
                "retry_at": retry_at.isoformat(),
                "detail": auth_detail,
            })
            scheduler_log(f"SKIP {job.name}: Claude auth failed; retry at {retry_at.isoformat()} detail={auth_detail}")
            continue

        row = run_job(job)
        ran_any = True
        current = now_local()
        js["last_run"] = row["finished"]
        js["last_scheduled_run"] = next_run.isoformat()
        js["last_rc"] = row["rc"]
        js["last_timed_out"] = row["timed_out"]
        js["runs"] = int(js.get("runs") or 0) + 1
        js["next_run"] = advance_next(job, next_run, current)
        state["updated"] = iso(current)
        write_json(STATE, state)
    return ran_any


def sleep_until_next_minute(max_sleep_s: int = 60) -> None:
    current = dt.datetime.now()
    target = (current + dt.timedelta(minutes=1)).replace(second=0, microsecond=0)
    delay = max(1.0, min(max_sleep_s, (target - current).total_seconds()))
    time.sleep(delay)


def main() -> int:
    ap = argparse.ArgumentParser(description="Run thesis automation jobs serially from a long-lived tmux/launchd process.")
    ap.add_argument("--once", action="store_true", help="Check due jobs once and exit.")
    ap.add_argument("--dry-run", action="store_true", help="Print due jobs without running them.")
    ap.add_argument("--reset-next-run", action="store_true", help="Reset next_run times to future slots on startup.")
    ap.add_argument("--include-research-distill", action="store_true", help="Also run run-research-distill-cycle.sh hourly at :15.")
    args = ap.parse_args()

    _lock_fh = acquire_lock()
    jobs = build_jobs(include_research_distill=args.include_research_distill)
    state = ensure_job_state(read_json(STATE, default={}), jobs, reset=args.reset_next_run)

    scheduler_log("scheduler started; jobs=" + ", ".join(f"{j.name}->{state['jobs'][j.name]['next_run']}" for j in jobs))
    try:
        while True:
            state = ensure_job_state(read_json(STATE, default={}), jobs)
            run_due_jobs(state, jobs, dry_run=args.dry_run)
            if args.once:
                break
            sleep_until_next_minute()
    except KeyboardInterrupt:
        scheduler_log("scheduler stopped by KeyboardInterrupt")
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
