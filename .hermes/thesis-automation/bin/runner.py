#!/usr/bin/env python3
"""
Kratt thesis-automation runner.

Subcommands:
  hourly   Pick next lane in rotation, run reviewer + writer, commit at most once.
  daily    Triage lane commits since last consolidation, integrate accepted, distill rejected, refresh lanes.
  weekly   Rerun thesis-quality review and write a meta summary.

Design notes:
  - One commit per hourly run, only in the lane worktree.
  - Main is only touched by the daily consolidation step.
  - Rejected work is reduced to distilled guidance lines and then discarded.
  - State/logs live under .hermes/thesis-automation/.

Runs fine from either cron/launchd or manual invocation.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
AUTO = REPO / ".hermes" / "thesis-automation"
LANES_JSON = AUTO / "lanes" / "lanes.json"
MEMORY_DIR = AUTO / "memory"
LOGS_DIR = AUTO / "logs"
STATE_DIR = AUTO / "state"
PROMPTS_DIR = AUTO / "prompts"
REVIEWS_DIR = REPO / ".hermes" / "thesis-quality-reviews"

def resolve_claude_bin() -> str:
    """Find Claude Code across Homebrew and the per-user installer.

    launchd starts with a small PATH, while recent Claude Code installs place the
    executable under ~/.local/bin.  Keep CLAUDE_BIN as the override, but make the
    default robust after upgrades/reboots.
    """
    override = os.environ.get("CLAUDE_BIN")
    if override:
        return override
    found = shutil.which("claude")
    if found:
        return found
    for candidate in (
        Path.home() / ".local" / "bin" / "claude",
        Path("/opt/homebrew/bin/claude"),
        Path("/usr/local/bin/claude"),
    ):
        if candidate.exists():
            return str(candidate)
    return "claude"


CLAUDE_BIN = resolve_claude_bin()
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL")


# ---------- helpers ----------

def now_iso() -> str:
    return dt.datetime.now().replace(microsecond=0).isoformat()


def ts_slug() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    with path.open() as f:
        return json.load(f)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def append_jsonl(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def sh(cmd, cwd: Path | None = None, check: bool = True, env: dict | None = None,
       timeout: int | None = None, input_text: str | None = None) -> subprocess.CompletedProcess:
    if isinstance(cmd, str):
        printable = cmd
        args = cmd
        shell = True
    else:
        printable = " ".join(shlex.quote(str(c)) for c in cmd)
        args = [str(c) for c in cmd]
        shell = False
    return subprocess.run(
        args, cwd=str(cwd) if cwd else None, shell=shell, check=check,
        env={**os.environ, **(env or {})}, capture_output=True, text=True,
        timeout=timeout, input=input_text,
    )


def git(repo: Path, *args, check: bool = True) -> str:
    res = sh(["git", *args], cwd=repo, check=check)
    return res.stdout.strip()


def load_lanes() -> list[dict]:
    data = read_json(LANES_JSON)
    return [l for l in data["lanes"] if l.get("active", True)]


def lane_memory(lane_id: str) -> dict:
    return read_json(MEMORY_DIR / f"{lane_id}.json", default={
        "lane": lane_id, "updated": None, "guidance": [], "rejected_refs": []
    })


def save_lane_memory(lane_id: str, mem: dict) -> None:
    mem["updated"] = now_iso()
    write_json(MEMORY_DIR / f"{lane_id}.json", mem)


def global_memory() -> dict:
    return read_json(MEMORY_DIR / "global.json", default={"updated": None, "guidance": []})


def save_global_memory(mem: dict) -> None:
    mem["updated"] = now_iso()
    write_json(MEMORY_DIR / "global.json", mem)


def state() -> dict:
    return read_json(STATE_DIR / "rotation.json", default={})


def save_state(s: dict) -> None:
    write_json(STATE_DIR / "rotation.json", s)


def render_prompt(template: str, **kw) -> str:
    out = template
    for k, v in kw.items():
        out = out.replace("{{" + k + "}}", str(v))
    return out


def fmt_guidance(lines: list[str]) -> str:
    if not lines:
        return "(none)"
    return "\n".join(f"- {l}" for l in lines)


def _dependency_check(st: dict, lane: dict, lane_id: str) -> str | None:
    dep = lane.get("depends_on")
    if not dep:
        return None
    dep_lane = dep["lane"] if isinstance(dep, dict) else str(dep)
    dep_head = st.get("lane_progress", {}).get(dep_lane)
    dep_consumed = st.get("lane_dependency_consumed", {}).get(lane_id)
    if not dep_head or dep_head == dep_consumed:
        dep_name = dep_lane
        if not dep_head:
            return f"Dependency {dep_name} has no committed output yet."
        return f"Waiting for new work in {dep_name}: no new committed note since last consume."
    return None


def run_claude(prompt: str, cwd: Path, *, permission_mode: str = "default",
               dangerously: bool = False, model: str | None = None,
               tools: str = "default", max_budget_usd: float | None = None,
               timeout: int = 900, output_format: str = "text") -> dict:
    """Call claude -p. Returns {'stdout', 'stderr', 'returncode', 'text', 'model', 'tools'}."""
    active_model = model or CLAUDE_MODEL
    active_tools = tools

    cmd = [CLAUDE_BIN, "--print", "--output-format", output_format]
    if dangerously:
        cmd.append("--dangerously-skip-permissions")
    else:
        cmd += ["--permission-mode", permission_mode]
    if active_model:
        cmd += ["--model", active_model]
    if active_tools:
        cmd += ["--tools", active_tools]
    if max_budget_usd is not None:
        cmd += ["--max-budget-usd", str(max_budget_usd)]

    try:
        env = os.environ.copy()
        # Thesis automation is intended to use Claude Code's first-party OAuth
        # login. Stale provider/API-key variables from a parent shell can
        # override OAuth and cause every scheduled run to fail with 401.
        if os.environ.get("KRATT_CLAUDE_KEEP_API_ENV") != "1":
            env.pop("CLAUDE_API_KEY", None)
            env.pop("CLAUDE_CODE_USE_OPENAI", None)
        proc = subprocess.run(
            cmd, cwd=str(cwd), input=prompt, text=True, capture_output=True,
            timeout=timeout, env=env,
        )
    except subprocess.TimeoutExpired as e:
        return {"stdout": e.stdout or "", "stderr": f"timeout after {timeout}s",
                "returncode": 124, "text": ""}

    stdout = proc.stdout or ""
    text = stdout
    if output_format == "json":
        try:
            data = json.loads(stdout)
            text = data.get("result") or data.get("text") or stdout
        except Exception:
            pass
    return {
        "stdout": stdout, "stderr": proc.stderr or "",
        "returncode": proc.returncode, "text": text,
        "model": active_model or "default",
        "tools": active_tools or "default",
    }


# ---------- hourly ----------

def hourly_run(force_lane: str | None = None) -> int:
    lanes = load_lanes()
    if not lanes:
        print("hourly: no active lanes", file=sys.stderr)
        return 1

    st = state()
    if force_lane:
        idx = next((i for i, l in enumerate(lanes) if l["id"] == force_lane), None)
        if idx is None:
            print(f"hourly: unknown lane {force_lane}", file=sys.stderr)
            return 2
        cursor = idx
    else:
        cursor = st.get("lane_cursor", 0) % len(lanes)

    lane = lanes[cursor]
    lane_id = lane["id"]

    file_cursor = st.setdefault("file_cursor", {}).get(lane_id, 0) % len(lane["rotation"])
    target_file = lane["rotation"][file_cursor]

    # Advance cursors (save early so a crash doesn't lock us on one lane).
    if not force_lane:
        st["lane_cursor"] = (cursor + 1) % len(lanes)
    st["file_cursor"][lane_id] = (file_cursor + 1) % len(lane["rotation"])
    save_state(st)

    worktree = REPO / lane["worktree"]
    if not worktree.exists():
        print(f"hourly: worktree missing: {worktree} (run bootstrap-worktrees.sh)", file=sys.stderr)
        return 3

    # Pull the latest main into the lane before starting, so runs start from current accepted state.
    try:
        git(worktree, "fetch", "--quiet", "--no-tags", "origin", check=False)
    except Exception:
        pass
    # Don't auto-rebase: consolidation handles refresh. Just log head.
    lane_head = git(worktree, "rev-parse", "HEAD", check=False)

    lane_guid = lane_memory(lane_id)["guidance"]
    glob_guid = global_memory()["guidance"]

    reviewer_tmpl = (PROMPTS_DIR / "reviewer.md").read_text()
    writer_tmpl = (PROMPTS_DIR / "writer.md").read_text()

    subs = dict(
        LANE_ID=lane_id,
        LANE_TITLE=lane["title"],
        LANE_FOCUS=lane["focus"],
        TARGET_FILE=target_file,
        REVIEWER_EXTRA=lane.get("reviewer_extra", ""),
        WRITER_EXTRA=lane.get("writer_extra", ""),
        LANE_GUIDANCE=fmt_guidance(lane_guid),
        GLOBAL_GUIDANCE=fmt_guidance(glob_guid),
    )

    log_entry = {
        "ts": now_iso(),
        "lane": lane_id,
        "target_file": target_file,
        "worktree": str(worktree),
        "branch": lane["branch"],
        "head_before": lane_head,
        "reviewer": None,
        "writer": None,
        "commit": None,
        "result": None,
    }

    dep_error = _dependency_check(st, lane, lane_id)
    if dep_error:
        log_entry["result"] = "pushback"
        log_entry["reviewer"] = {
            "rc": 0,
            "stderr_tail": "",
            "text": f"Dependency gate not ready: {dep_error}",
        }
        log_entry["writer"] = {
            "rc": 0,
            "stderr_tail": "",
            "text": f"PUSHBACK: {dep_error}",
        }
        _finish_hourly(lane_id, log_entry)
        return 0

    # --- Reviewer ---
    reviewer_prompt = render_prompt(reviewer_tmpl, **subs)
    rev = run_claude(
        reviewer_prompt, cwd=worktree,
        permission_mode="default",
        max_budget_usd=0.5,
        timeout=600,
    )
    log_entry["reviewer"] = {
        "rc": rev["returncode"],
        "stderr_tail": (rev["stderr"] or "")[-400:],
        "text": rev["text"][:4000],
    }
    if rev["returncode"] != 0 or not rev["text"].strip():
        log_entry["result"] = "reviewer_failed"
        _finish_hourly(lane_id, log_entry)
        return 4

    # --- Writer ---
    writer_prompt = render_prompt(writer_tmpl, REVIEWER_OUTPUT=rev["text"], **subs)
    wri = run_claude(
        writer_prompt, cwd=worktree,
        dangerously=True,
        max_budget_usd=1.0,
        timeout=900,
    )
    log_entry["writer"] = {
        "rc": wri["returncode"],
        "stderr_tail": (wri["stderr"] or "")[-400:],
        "text": wri["text"][:4000],
    }

    head_after = git(worktree, "rev-parse", "HEAD", check=False)
    if head_after and head_after != lane_head:
        subject = git(worktree, "log", "-1", "--pretty=%s", check=False)
        log_entry["commit"] = {"sha": head_after, "subject": subject}
        log_entry["result"] = "committed"
        st.setdefault("lane_progress", {})[lane_id] = head_after
        if lane.get("depends_on"):
            dep = lane.get("depends_on")
            dep_lane = dep["lane"] if isinstance(dep, dict) else str(dep)
            st.setdefault("lane_dependency_consumed", {})[lane_id] = st.get("lane_progress", {}).get(dep_lane)
    else:
        # Detect pushback marker in writer output.
        if re.search(r"(?mi)^PUSHBACK:", wri["text"] or ""):
            log_entry["result"] = "pushback"
        else:
            log_entry["result"] = "no_change"

    save_state(st)
    _finish_hourly(lane_id, log_entry)
    return 0


def _finish_hourly(lane_id: str, entry: dict) -> None:
    day = dt.date.today().isoformat()
    append_jsonl(LOGS_DIR / "hourly" / f"{day}.jsonl", entry)
    print(json.dumps({
        "lane": lane_id, "result": entry["result"],
        "file": entry["target_file"],
        "commit": (entry.get("commit") or {}).get("sha"),
    }, ensure_ascii=False))


# ---------- daily consolidation ----------

def daily_run() -> int:
    lanes = load_lanes()
    st = state()
    last = st.get("last_consolidation")
    since_iso = last  # git understands ISO

    # Collect new commits per lane.
    lane_commits: dict[str, list[dict]] = {}
    for lane in lanes:
        branch = lane["branch"]
        base = "main"
        rng = f"{base}..{branch}"
        raw = git(REPO, "log", rng, "--pretty=%H%x1f%an%x1f%s%x1f%ct", check=False)
        commits = []
        for line in raw.splitlines():
            if not line.strip():
                continue
            parts = line.split("\x1f")
            if len(parts) < 4:
                continue
            commits.append({
                "sha": parts[0], "author": parts[1], "subject": parts[2], "ct": int(parts[3])
            })
        if commits:
            lane_commits[lane["id"]] = commits

    summary = {
        "ts": now_iso(),
        "since": since_iso,
        "lane_commits": {k: [c["sha"] for c in v] for k, v in lane_commits.items()},
        "decisions": [],
        "accepted": [],
        "rejected": [],
        "deferred": [],
        "guidance_updates": [],
        "refreshed_lanes": [],
        "errors": [],
    }

    if not lane_commits:
        print("daily: no new lane commits.")
    else:
        # Build consolidator input with diffs.
        blocks = []
        for lane_id, commits in lane_commits.items():
            for c in commits:
                try:
                    diff = git(REPO, "show", "--stat", "-p", c["sha"], check=False)
                except Exception:
                    diff = "(diff unavailable)"
                if len(diff) > 20000:
                    diff = diff[:20000] + "\n...[truncated]..."
                blocks.append(f"## lane: {lane_id}\nsha: {c['sha']}\nsubject: {c['subject']}\n\n```\n{diff}\n```\n")
        commits_section = "\n".join(blocks)

        tmpl = (PROMPTS_DIR / "consolidator.md").read_text()
        lane_guid_map = {l["id"]: lane_memory(l["id"])["guidance"] for l in lanes}
        prompt = (
            tmpl + "\n\n## Current global guidance\n" +
            fmt_guidance(global_memory()["guidance"]) +
            "\n\n## Current per-lane guidance\n" +
            "\n".join(f"- {lid}: {fmt_guidance(g)}" for lid, g in lane_guid_map.items()) +
            "\n\n## Commits to triage\n" + commits_section
        )

        result = run_claude(
            prompt, cwd=REPO,
            permission_mode="default",
            max_budget_usd=2.0,
            timeout=1200,
        )
        txt = result["text"]
        decisions_data = _parse_json_blob(txt)
        if decisions_data is None:
            summary["errors"].append("consolidator did not return valid JSON")
            summary["raw_consolidator_output"] = txt[:4000]
            _write_daily_log(summary)
            return 5

        summary["decisions"] = decisions_data.get("decisions", [])

        # --- Integrate accepted commits with stash / cherry-pick / pop flow. ---
        stash_report = _apply_accepted_with_stash_flow(
            [d for d in summary["decisions"] if d.get("action") == "accept"],
            lane_commits,
        )
        summary["stash_used"] = stash_report["stash_used"]
        summary["stash_ref"] = stash_report["stash_ref"]
        summary["stash_msg"] = stash_report["stash_msg"]
        summary["fixer_invocations"] = stash_report["fixer_invocations"]
        summary["reconciler_invoked"] = stash_report["reconciler_invoked"]
        summary["pop_status"] = stash_report["pop_status"]
        summary["status"] = stash_report["status"]
        summary["degraded_reasons"] = stash_report["degraded_reasons"]
        summary["accepted"].extend(stash_report["accepted"])
        summary["errors"].extend(stash_report["errors"])
        # Cherry-pick failures that the fixer couldn't save appear as rejections here.
        summary["rejected"].extend(stash_report["cherry_pick_failures"])

        for d in summary["decisions"]:
            action = d.get("action")
            lane_id = d.get("lane")
            sha = d.get("sha")
            if action == "reject":
                summary["rejected"].append({"lane": lane_id, "sha": sha, "reason": d.get("reason", "")})
            elif action == "defer":
                summary["deferred"].append({"lane": lane_id, "sha": sha, "reason": d.get("reason", "")})

        # Apply guidance updates.
        for ga in decisions_data.get("lane_guidance_additions", []) or []:
            lid = ga.get("lane")
            line = (ga.get("line") or "").strip()
            if not lid or not line:
                continue
            mem = lane_memory(lid)
            # Keep at most 3 guidance lines, newest first, deduped by lowercase prefix.
            existing = [g for g in mem.get("guidance", []) if g.strip().lower() != line.lower()]
            mem["guidance"] = ([line] + existing)[:3]
            rejected_refs = mem.setdefault("rejected_refs", [])
            for r in summary["rejected"]:
                if r["lane"] == lid:
                    rejected_refs.append({"sha": r["sha"], "reason": r["reason"], "distilled": line})
            # Trim rejected_refs to last 20.
            mem["rejected_refs"] = rejected_refs[-20:]
            save_lane_memory(lid, mem)
            summary["guidance_updates"].append({"lane": lid, "line": line})

        for gline in decisions_data.get("global_guidance_additions", []) or []:
            gline = (gline or "").strip()
            if not gline:
                continue
            gm = global_memory()
            existing = [g for g in gm.get("guidance", []) if g.strip().lower() != gline.lower()]
            gm["guidance"] = ([gline] + existing)[:5]
            save_global_memory(gm)
            summary["guidance_updates"].append({"lane": "global", "line": gline})

    # Refresh all lane branches/worktrees to the new main — but only if reconciliation
    # is resolved. If stash pop is still conflicted, the main worktree holds user WIP
    # that must be hand-inspected; destructive resets of lane worktrees would be fine
    # structurally, but per policy we skip to keep the run conservative and inspectable.
    summary["refresh_skipped_reason"] = None
    _skip_pop = summary.get("pop_status") in {"unresolved", "reconciler_failed"}
    _skip_push = "stash_push_failed" in (summary.get("degraded_reasons") or [])
    _skip_cp = any((r or "").startswith("cherry_pick_unresolved") for r in (summary.get("degraded_reasons") or []))
    if summary.get("status") == "degraded" and (_skip_pop or _skip_push or _skip_cp):
        why = "pop=" + (summary.get("pop_status") or "?") if _skip_pop else \
              ("stash_push_failed" if _skip_push else "cherry_pick_unresolved")
        summary["refresh_skipped_reason"] = f"degraded ({why}); skipping lane refresh"
    else:
        main_sha = git(REPO, "rev-parse", "main")
        for lane in lanes:
            try:
                _refresh_lane(lane, main_sha)
                summary["refreshed_lanes"].append(lane["id"])
            except Exception as e:
                summary["errors"].append(f"refresh {lane['id']}: {e}")

    st["last_consolidation"] = now_iso()
    save_state(st)
    _write_daily_log(summary)
    print(json.dumps({
        "status": summary.get("status", "clean"),
        "accepted": len(summary["accepted"]),
        "rejected": len(summary["rejected"]),
        "deferred": len(summary["deferred"]),
        "guidance_updates": len(summary["guidance_updates"]),
        "refreshed_lanes": len(summary["refreshed_lanes"]),
        "refresh_skipped_reason": summary.get("refresh_skipped_reason"),
        "stash_used": summary.get("stash_used", False),
        "fixer_invocations": summary.get("fixer_invocations", 0),
        "reconciler_invoked": summary.get("reconciler_invoked", False),
        "pop_status": summary.get("pop_status"),
        "degraded_reasons": summary.get("degraded_reasons", []),
        "errors": summary["errors"],
    }, ensure_ascii=False))
    return 0


def _parse_json_blob(text: str) -> dict | None:
    if not text:
        return None
    # Strip code fences if present.
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def _porcelain(repo: Path) -> str:
    return git(repo, "status", "--porcelain", check=False)


def _unmerged_files(repo: Path) -> list[str]:
    out = []
    for line in _porcelain(repo).splitlines():
        if not line:
            continue
        xy = line[:2]
        # Unmerged markers per git docs: DD AU UD UA DU AA UU
        if xy in {"DD", "AU", "UD", "UA", "DU", "AA", "UU"}:
            out.append(line[3:])
    return out


def _cherry_pick_in_progress(repo: Path) -> bool:
    gd = git(repo, "rev-parse", "--git-dir", check=False)
    if not gd:
        return False
    return (Path(gd) / "CHERRY_PICK_HEAD").exists() or (Path(repo) / gd / "CHERRY_PICK_HEAD").exists()


def _stash_push_if_dirty() -> tuple[bool, str | None, str | None]:
    """Stash tracked + untracked changes on main worktree, EXCLUDING the automation tree
    (.hermes/) so runner config/prompts stay on disk during the cherry-pick window.
    .claude/ is gitignored and thus not affected by `stash -u`. Return (stashed?, ref, msg)."""
    if not _porcelain(REPO).strip():
        return False, None, None
    msg = f"thesis-automation daily {ts_slug()}"
    try:
        sh(["git", "stash", "push", "-u", "-m", msg, "--", ":(exclude,glob).hermes/**", ":/"],
           cwd=REPO, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"stash push failed: {(e.stderr or '').strip()}")
    # Verify something actually got stashed (pathspec may have matched nothing).
    top = git(REPO, "stash", "list", "-n", "1", "--format=%gs", check=False).strip()
    if msg not in top:
        return False, None, None
    ref = git(REPO, "stash", "list", "-n", "1", "--format=%gd", check=False).strip() or "stash@{0}"
    return True, ref, msg


def _apply_accepted_with_stash_flow(accepts: list[dict], lane_commits: dict) -> dict:
    """Run: stash -> cherry-pick-each(+fixer) -> stash-pop(+reconciler).
    Returns a structured report. Never raises on controllable failure."""
    report = {
        "stash_used": False,
        "stash_ref": None,
        "stash_msg": None,
        "fixer_invocations": 0,
        "reconciler_invoked": False,
        "pop_status": None,           # None|"ok"|"unresolved"|"reconciler_failed"|"reconciled"|"clean"
        "status": "clean",            # "clean"|"degraded"
        "degraded_reasons": [],
        "accepted": [],
        "cherry_pick_failures": [],
        "errors": [],
    }

    original_branch = git(REPO, "rev-parse", "--abbrev-ref", "HEAD", check=False) or "main"

    # 1. Stash whatever dirty state sits on main.
    try:
        stashed, ref, msg = _stash_push_if_dirty()
    except Exception as e:
        report["errors"].append(str(e))
        report["status"] = "degraded"
        report["degraded_reasons"].append("stash_push_failed")
        return report
    report["stash_used"] = stashed
    report["stash_ref"] = ref
    report["stash_msg"] = msg

    # 2. Make sure we're on main for cherry-picks.
    try:
        git(REPO, "checkout", "main")
    except subprocess.CalledProcessError as e:
        report["errors"].append(f"checkout main failed: {(e.stderr or '').strip()}")
        report["status"] = "degraded"
        report["degraded_reasons"].append("checkout_main_failed")
        # Try to pop stash back before returning.
        _try_pop_back(report)
        return report

    # 3. Cherry-pick each accepted commit. Invoke fixer on conflict.
    lane_by_sha = {}
    for lane_id, commits in lane_commits.items():
        for c in commits:
            lane_by_sha[c["sha"]] = {"lane_id": lane_id, "subject": c["subject"]}

    for d in accepts:
        sha = d.get("sha")
        lane_id = d.get("lane") or (lane_by_sha.get(sha, {}) or {}).get("lane_id", "?")
        subject = (lane_by_sha.get(sha, {}) or {}).get("subject", "")
        picked = _cherry_pick_one(sha, lane_id, subject, report)
        if picked:
            report["accepted"].append({"lane": lane_id, "sha": sha, "reason": d.get("reason", "")})
        else:
            report["cherry_pick_failures"].append({
                "lane": lane_id, "sha": sha,
                "reason": d.get("reason", "") + " | cherry-pick unresolved after fixer",
            })
            # Cherry-pick unresolved is degrading but not fatal — we continue with remaining accepts.
            report["status"] = "degraded"
            report["degraded_reasons"].append(f"cherry_pick_unresolved:{sha}")

    # 4. Pop the stash. If conflict, dispatch reconciler.
    if report["stash_used"]:
        _pop_stash_with_reconciler(report)
    else:
        report["pop_status"] = "clean"

    # 5. Best-effort: return to original branch if we switched.
    # We stay on main if that's the natural place now; only leave if original was something else
    # and the worktree is clean enough to switch.
    try:
        if original_branch and original_branch not in {"main", "HEAD"}:
            if not _porcelain(REPO).strip():
                git(REPO, "checkout", original_branch, check=False)
    except Exception:
        pass

    return report


def _cherry_pick_one(sha: str, lane_id: str, subject: str, report: dict) -> bool:
    try:
        sh(["git", "cherry-pick", "-x", sha], cwd=REPO, check=True)
        return True
    except subprocess.CalledProcessError:
        # Conflict. Dispatch fixer.
        if not _cherry_pick_in_progress(REPO):
            # No in-progress state — cherry-pick failed for another reason. Nothing to fix.
            report["errors"].append(f"cherry-pick hard-failed (no in-progress state) for {sha}")
            return False

        unmerged = _unmerged_files(REPO)
        lanes = load_lanes()
        lane = next((l for l in lanes if l["id"] == lane_id), None)
        lane_targets = ",".join(lane.get("rotation", [])) if lane else "(unknown)"

        tmpl = (PROMPTS_DIR / "fixer.md").read_text()
        prompt = render_prompt(
            tmpl,
            SHA=sha,
            SUBJECT=subject,
            LANE_ID=lane_id,
            LANE_TARGETS=lane_targets,
            UNMERGED_FILES="\n".join(unmerged) or "(none listed)",
            STATUS=_porcelain(REPO) or "(empty)",
            REPO=str(REPO),
        )
        report["fixer_invocations"] += 1
        fx = run_claude(
            prompt, cwd=REPO,
            dangerously=True,
            max_budget_usd=1.0,
            timeout=900,
        )
        txt = fx.get("text", "") or ""
        if _cherry_pick_in_progress(REPO) or _unmerged_files(REPO):
            # Not repaired. Abort cleanly.
            sh(["git", "cherry-pick", "--abort"], cwd=REPO, check=False)
            report["errors"].append(f"fixer could not resolve {sha}: tail={txt[-300:]}")
            return False
        # Repaired. Ensure a new commit landed (cherry-pick --continue should have done it).
        return True


def _pop_stash_with_reconciler(report: dict) -> None:
    ref = report["stash_ref"] or "stash@{0}"
    # Try a clean pop first.
    try:
        sh(["git", "stash", "pop", "--", ref], cwd=REPO, check=True)
        report["pop_status"] = "ok"
        return
    except subprocess.CalledProcessError:
        # Conflict path.
        pass

    if not _unmerged_files(REPO) and not _porcelain(REPO).strip():
        # Nothing to reconcile — pop effectively a no-op.
        report["pop_status"] = "ok"
        return

    # Dispatch reconciler.
    report["reconciler_invoked"] = True
    tmpl = (PROMPTS_DIR / "reconciler.md").read_text()
    prompt = render_prompt(
        tmpl,
        REPO=str(REPO),
        STASH_REF=report["stash_ref"] or "(unknown)",
        STASH_MSG=report["stash_msg"] or "(unknown)",
        STATUS=_porcelain(REPO) or "(empty)",
        UNMERGED_FILES="\n".join(_unmerged_files(REPO)) or "(none)",
    )
    rc = run_claude(
        prompt, cwd=REPO,
        dangerously=True,
        max_budget_usd=1.0,
        timeout=900,
    )
    txt = rc.get("text", "") or ""
    if _unmerged_files(REPO):
        # Still conflicts. Mark degraded, do not force-drop the stash, do not touch files further.
        report["pop_status"] = "reconciler_failed"
        report["status"] = "degraded"
        report["degraded_reasons"].append("stash_pop_reconciler_failed")
        report["errors"].append(f"reconciler unresolved: tail={txt[-300:]}")
        return

    # No remaining conflicts. The stash may have been auto-removed by pop if all hunks applied;
    # if it still exists (because pop bailed mid-way), drop it now since its content is reflected
    # in the working tree the reconciler just approved.
    if _stash_still_present(ref):
        sh(["git", "stash", "drop", ref], cwd=REPO, check=False)

    report["pop_status"] = "reconciled"


def _stash_still_present(ref: str) -> bool:
    out = git(REPO, "stash", "list", check=False)
    if not out:
        return False
    # ref looks like 'stash@{0}'; presence of any stash line starting with the same index works.
    return any(line.startswith(ref) for line in out.splitlines())


def _try_pop_back(report: dict) -> None:
    """Best-effort pop used only on early-abort paths."""
    if not report.get("stash_used"):
        return
    try:
        sh(["git", "stash", "pop", "--", report["stash_ref"] or "stash@{0}"], cwd=REPO, check=True)
        report["pop_status"] = "ok"
    except subprocess.CalledProcessError:
        report["pop_status"] = "unresolved"
        report["status"] = "degraded"
        report["degraded_reasons"].append("stash_pop_unresolved_on_abort")


def _refresh_lane(lane: dict, main_sha: str) -> None:
    worktree = REPO / lane["worktree"]
    branch = lane["branch"]
    if not worktree.exists():
        # Let bootstrap re-create it.
        return
    # Clean working tree in the worktree before reset.
    sh(["git", "reset", "--hard"], cwd=worktree, check=False)
    sh(["git", "clean", "-fdx", "--", ":!.claude/"], cwd=worktree, check=False)
    # Move the branch to main.
    git(worktree, "update-ref", f"refs/heads/{branch}", main_sha)
    git(worktree, "checkout", branch)
    git(worktree, "reset", "--hard", main_sha)


def _write_daily_log(summary: dict) -> None:
    path = LOGS_DIR / "daily" / f"{ts_slug()}.json"
    write_json(path, summary)
    print(f"daily log: {path}")


# ---------- weekly ----------

def weekly_run() -> int:
    """
    Rerun the thesis-quality-review skill, then produce a short meta summary
    comparing the new review to the previous one, plus lane observations.
    """
    # 1) Rerun the review. We invoke claude -p with the skill slash command.
    ts = ts_slug()
    review_prompt = (
        "Use the thesis-quality-review skill to produce a new review for this project. "
        "Save outputs under .hermes/thesis-quality-reviews/ and update index.json as the skill specifies. "
        "Work autonomously. When done, print a single line: DONE <markdown_path>"
    )
    rv = run_claude(
        review_prompt, cwd=REPO,
        dangerously=True,
        max_budget_usd=3.0,
        timeout=1800,
    )
    if rv["returncode"] != 0:
        print(f"weekly: review rerun failed rc={rv['returncode']}", file=sys.stderr)

    # 2) Gather inputs and ask for meta summary.
    idx = read_json(REVIEWS_DIR / "index.json", default={"reviews": []})
    reviews = sorted(idx.get("reviews", []), key=lambda r: r.get("timestamp", ""))
    latest = reviews[-1] if reviews else None
    previous = reviews[-2] if len(reviews) >= 2 else None

    def _read_rel(p):
        if not p:
            return ""
        fp = REPO / p
        if not fp.exists():
            return ""
        return fp.read_text()

    latest_md = _read_rel(latest["markdown_path"]) if latest else ""
    previous_md = _read_rel(previous["markdown_path"]) if previous else ""

    lane_mem_dump = {
        l["id"]: lane_memory(l["id"]) for l in load_lanes()
    }

    # Compact last-week stats from hourly logs.
    stats = _hourly_stats(days=7)
    daily_logs = _recent_daily_logs(days=7)

    tmpl = (PROMPTS_DIR / "weekly.md").read_text()
    prompt = (
        tmpl +
        "\n\n## Latest review (markdown)\n" + latest_md[:12000] +
        "\n\n## Previous review (markdown)\n" + previous_md[:8000] +
        "\n\n## Lane memory\n```json\n" + json.dumps(lane_mem_dump, indent=2, ensure_ascii=False) + "\n```" +
        "\n\n## Hourly stats (7d)\n```json\n" + json.dumps(stats, indent=2) + "\n```" +
        "\n\n## Daily consolidation logs (7d)\n```json\n" + json.dumps(daily_logs, indent=2, ensure_ascii=False)[:16000] + "\n```"
    )

    meta = run_claude(
        prompt, cwd=REPO,
        permission_mode="default",
        max_budget_usd=1.5,
        timeout=900,
    )
    out_path = LOGS_DIR / "weekly" / f"{ts_slug()}-meta.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(meta["text"] or "(empty)\n")

    st = state()
    st["last_weekly_review"] = now_iso()
    save_state(st)

    print(json.dumps({"weekly_meta": str(out_path), "latest_review": (latest or {}).get("markdown_path")}))
    return 0


def _hourly_stats(days: int) -> dict:
    cutoff = dt.date.today() - dt.timedelta(days=days)
    out = {"runs": 0, "committed": 0, "no_change": 0, "pushback": 0, "failed": 0, "by_lane": {}}
    hdir = LOGS_DIR / "hourly"
    if not hdir.exists():
        return out
    for p in sorted(hdir.glob("*.jsonl")):
        try:
            day = dt.date.fromisoformat(p.stem)
        except Exception:
            continue
        if day < cutoff:
            continue
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            out["runs"] += 1
            res = e.get("result", "unknown")
            out[res] = out.get(res, 0) + 1
            lid = e.get("lane", "?")
            bl = out["by_lane"].setdefault(lid, {"runs": 0, "committed": 0})
            bl["runs"] += 1
            if res == "committed":
                bl["committed"] += 1
    return out


def _recent_daily_logs(days: int) -> list[dict]:
    cutoff = dt.datetime.now() - dt.timedelta(days=days)
    out = []
    ddir = LOGS_DIR / "daily"
    if not ddir.exists():
        return out
    for p in sorted(ddir.glob("*.json")):
        try:
            # filename is YYYY-MM-DD_HHMMSS.json
            stamp = dt.datetime.strptime(p.stem, "%Y-%m-%d_%H%M%S")
        except Exception:
            stamp = dt.datetime.now()
        if stamp < cutoff:
            continue
        try:
            out.append(json.loads(p.read_text()))
        except Exception:
            pass
    return out


# ---------- entry ----------

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    ph = sub.add_parser("hourly")
    ph.add_argument("--lane", help="Force a specific lane id (skips rotation)")

    sub.add_parser("daily")
    sub.add_parser("weekly")

    args = ap.parse_args()
    if args.cmd == "hourly":
        sys.exit(hourly_run(force_lane=args.lane))
    if args.cmd == "daily":
        sys.exit(daily_run())
    if args.cmd == "weekly":
        sys.exit(weekly_run())


if __name__ == "__main__":
    main()
