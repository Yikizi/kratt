#!/usr/bin/env python3
"""Tier 1: ask cheap LLM (codex by default) to propose a Clockify entry.

Async fire-and-forget. Failures are logged, never raised.
Output: appends JSON to ~/.kratt-time-log/proposals/YYYY-MM-DD.jsonl.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from apply_proposals import apply_row, commit_patch_id, load_file, proposal_files

LOG_DIR = Path.home() / ".kratt-time-log"
PROPOSALS_DIR = LOG_DIR / "proposals"
LOGS_DIR = LOG_DIR / "logs"
ERR_LOG = LOGS_DIR / "propose-errors.log"

DEFAULT_AGENT = os.environ.get("KRATT_TIME_AGENT_FAST", "codex exec")
TIMEOUT_SEC = int(os.environ.get("KRATT_TIME_AGENT_TIMEOUT", "180"))
AUTO_APPLY = os.environ.get("KRATT_TIME_AUTO_APPLY", "1") != "0"
CLOCKIFY_PROJECT_ID = os.environ.get("KRATT_CLOCKIFY_PROJECT_ID", "")
GITLAB_REPO = os.environ.get("KRATT_GITLAB_REPO", "malinh/iaib")
SKIP_CLOCKIFY = os.environ.get("KRATT_TIME_SKIP_CLOCKIFY", "0") == "1"
SKIP_GITLAB = os.environ.get("KRATT_TIME_SKIP_GITLAB", "0") == "1"

# Hand-curated; keep in sync with `glab issue list --repo malinh/iaib`.
ISSUES_CATALOG = """#18 wake-word pipeline hardening + ambient eval
#19 thesis drafting + framework comparison
#20 Home Assistant voice pipeline
#23 Background chapter writing
#24 Multi-engine TTS ablation
#25 Streaming FAPH evaluation methodology
#27 MoE arhitektuur (multi-model consensus)
#28 User-testing pilot + full run
#29 Thesis automation + project tracking automation
#30 v19 'Kratt' single-word ablation"""

PROMPT_TEMPLATE = """Sa oled time-tracking assistant Mattias' Kratt-projektis.
Antud git commiti põhjal pakku Clockify+GitLab kirje.

Reegel:
- gap_min on viimase commiti vahe MINUTITES — see on UPPER BOUND, mitte tegelik focused-aeg.
- Tüüpilised duration_min: 15 (väike fix), 30-45 (üks fokuseerit blokk), 60-120 (sügav iteratsioon).
- Kui commit on selge automation/scheduler väljund (per-tunni docs/thesis lane fix), pakku 5-10 min.
- description: lühike eestikeelne fraas, 4-10 sõna.
- confidence: high kui commit-msg sisaldab issue#, medium kui scope on selge, low kui ebaselge.

VASTA AINULT compact JSON-iga, mitte midagi muud:
{{"issue":"#NN","duration_min":N,"description":"...","confidence":"high|medium|low"}}

Saadaval issue'd:
{issues}

Commit:
hash: {hash}
branch: {branch}
msg: {msg}
files_changed: {files_changed}, +{insertions}/-{deletions}
gap_min: {gap_min}

Diff stat:
{diff_stat}
"""


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def call_agent(prompt: str) -> str | None:
    cmd = shlex.split(DEFAULT_AGENT)
    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=TIMEOUT_SEC,
        )
        if result.returncode != 0:
            log_err(f"agent rc={result.returncode}: {result.stderr[:500]}")
            return None
        return result.stdout
    except subprocess.TimeoutExpired:
        log_err(f"agent timeout after {TIMEOUT_SEC}s")
        return None
    except FileNotFoundError as e:
        log_err(f"agent binary missing: {e}")
        return None


def log_err(msg: str) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with ERR_LOG.open("a") as f:
        f.write(f"{datetime.now().isoformat()} {msg}\n")


def extract_json(text: str) -> dict | None:
    """LLMs sometimes wrap JSON in fences or add prose. Find first {...} block."""
    text = text.strip()
    # Strip code fences
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    # Or first {...} balance
    if not text.startswith("{"):
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            text = m.group(0)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def existing_patch_ref(patch_id: str | None) -> str | None:
    if not patch_id:
        return None
    for path in proposal_files(None, None):
        for row in load_file(path):
            if not (row.get("applied") or row.get("skipped")):
                continue
            existing = row.get("patch_id")
            if not existing:
                existing = commit_patch_id(str(row.get("hash", "")))
            if existing == patch_id:
                return str(row.get("hash", ""))[:8]
    return None


def maybe_auto_apply(proposal: dict) -> dict:
    if not AUTO_APPLY:
        return proposal
    try:
        dup = existing_patch_ref(proposal.get("patch_id"))
        if dup:
            proposal.update(
                {
                    "skipped": True,
                    "skip_reason": f"duplicate patch-id of {dup}",
                    "applied_at": datetime.now().isoformat(timespec="seconds"),
                }
            )
            return proposal
        status, proposal = apply_row(
            proposal,
            project_id=CLOCKIFY_PROJECT_ID,
            repo=GITLAB_REPO,
            dry_run=False,
            include_low=False,
            skip_clockify=SKIP_CLOCKIFY,
            skip_gitlab=SKIP_GITLAB,
            mark_skipped=None,
        )
        proposal["auto_apply_status"] = status
        if status == "failed":
            log_err(f"auto-apply failed for {proposal.get('hash', '')[:8]}")
        return proposal
    except Exception as e:
        proposal["auto_apply_exception"] = repr(e)
        log_err(f"auto-apply exception for {proposal.get('hash', '')[:8]}: {e!r}")
        return proposal


def main() -> int:
    if len(sys.argv) < 3:
        log_err("usage: propose_commit.py <hash> <gap_sec>")
        return 0
    h, gap_sec_str = sys.argv[1], sys.argv[2]
    try:
        gap_sec = int(gap_sec_str)
    except ValueError:
        gap_sec = 0

    repo = Path(git("rev-parse", "--show-toplevel")).name
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    msg = git("log", "-1", "--format=%B", h).strip()
    diff_stat = subprocess.check_output(
        ["git", "show", "--stat", "--format=", h], text=True
    ).strip()
    diff_stat = "\n".join(diff_stat.splitlines()[:30])

    stats_line = subprocess.check_output(
        ["git", "log", "-1", "--shortstat", "--format=", h], text=True
    ).strip()
    files_changed = insertions = deletions = 0
    for part in stats_line.split(","):
        part = part.strip()
        if not part:
            continue
        n_str, _, kind = part.partition(" ")
        try:
            n = int(n_str)
        except ValueError:
            continue
        if "file" in kind:
            files_changed = n
        elif "insertion" in kind:
            insertions = n
        elif "deletion" in kind:
            deletions = n

    prompt = PROMPT_TEMPLATE.format(
        issues=ISSUES_CATALOG,
        hash=h,
        branch=branch,
        msg=msg,
        files_changed=files_changed,
        insertions=insertions,
        deletions=deletions,
        gap_min=gap_sec // 60,
        diff_stat=diff_stat,
    )

    response = call_agent(prompt)
    if response is None:
        return 0

    proposal = extract_json(response)
    if proposal is None:
        log_err(f"could not parse JSON for {h[:8]}: {response[:500]}")
        return 0

    proposal.update(
        {
            "ts": git("log", "-1", "--format=%cI", h),
            "hash": h,
            "branch": branch,
            "repo": repo,
            "applied": False,
            "agent": DEFAULT_AGENT,
            "patch_id": commit_patch_id(h),
        }
    )
    proposal = maybe_auto_apply(proposal)

    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    out = PROPOSALS_DIR / f"{today}.jsonl"
    with out.open("a") as f:
        f.write(json.dumps(proposal, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        log_err(f"unhandled: {e!r}")
        sys.exit(0)
