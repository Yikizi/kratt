#!/usr/bin/env python3
"""Lightweight documentation freshness audit for the Kratt monorepo."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class KeyDoc:
    path: str
    label: str
    max_age_days: int
    requires_update_stamp: bool = False


KEY_DOCS = [
    KeyDoc("docs/PROJECT_TODO.md", "Master task tracker", 14, True),
    KeyDoc(
        "docs/research/source-of-truth-apr-2026.md",
        "Stable decisions / source of truth",
        21,
    ),
    KeyDoc(
        "docs/research/wake-word-evaluation-methodology.md",
        "Evaluation methodology",
        45,
    ),
    KeyDoc("README.md", "Repo landing page", 21),
    KeyDoc("wake-word/CLAUDE.md", "Wake-word operator context", 21),
    KeyDoc("wake-word/README.md", "Wake-word package README", 21),
    KeyDoc("docs/GIT_WORKFLOW.md", "Git/process guidance", 45, True),
]

UPDATE_PATTERNS = [
    re.compile(r"(?im)^Last updated:\s*(\d{4}-\d{2}-\d{2})\s*$"),
    re.compile(r"(?im)^>\s*Last updated:\s*(\d{4}-\d{2}-\d{2})\s*$"),
    re.compile(r"(?im)^\*\*Last updated\*\*:\s*(\d{4}-\d{2}-\d{2})\s*$"),
    re.compile(r"(?im)^\*\*Updated\*\*:\s*(\d{4}-\d{2}-\d{2})\s*$"),
]

LEGACY_MARKERS = {
    r"\brequirements\.txt\b": "old pip/requirements setup path",
    r"\bpython3\.9\s+-m\s+venv\b": "hard-coded Python 3.9 bootstrap",
    r"\brecord_samples\.py\b": "legacy recording workflow reference",
    r"\bdownload_negatives\.py\b": "legacy negative-data download reference",
    r"\btraining/experiments/\b": "legacy training directory reference",
}

IGNORE_PATH_PARTS = {
    ".git",
    ".claude",
    ".venv",
    ".serena",
    ".hermes",
    "external-repos",
    "managed_components",
    "site-packages",
}

IGNORE_EXACT = {
    "docs/documentation-maintenance.md",
    "docs/notebooklm-pack/README.md",
    "docs/stitch-taltech-pack/README.md",
}

IGNORE_PREFIXES = (
    "stt-integration/kiirkirjutaja-source/",
    "tools/tartunlp-tts/",
    "tools/text-to-speech-worker/",
)


def git_last_commit_date(path: Path) -> date | None:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", str(path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    value = result.stdout.strip()
    if result.returncode != 0 or not value:
        return None
    return date.fromisoformat(value)


def extract_update_stamp(text: str) -> date | None:
    for pattern in UPDATE_PATTERNS:
        match = pattern.search(text)
        if match:
            return date.fromisoformat(match.group(1))
    return None


def collect_markdown_files() -> list[Path]:
    candidates: list[Path] = []
    for path in REPO_ROOT.rglob("*.md"):
        rel = path.relative_to(REPO_ROOT)
        rel_str = rel.as_posix()
        if any(part in IGNORE_PATH_PARTS for part in rel.parts):
            continue
        if rel_str in IGNORE_EXACT:
            continue
        if rel_str.startswith(IGNORE_PREFIXES):
            continue
        candidates.append(path)
    return sorted(candidates)


def status_for_age(age_days: int, max_age_days: int) -> str:
    if age_days <= max_age_days:
        return "OK"
    if age_days <= max_age_days * 2:
        return "WARN"
    return "STALE"


def git_worktree_status(path: Path) -> str | None:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--", str(path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout.strip()
    return output or None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if warnings or stale findings exist.",
    )
    args = parser.parse_args()

    today = datetime.now().date()

    key_rows: list[tuple[str, str, int | None, str, str]] = []
    issues: list[str] = []

    for doc in KEY_DOCS:
        path = REPO_ROOT / doc.path
        if not path.exists():
            key_rows.append((doc.path, "MISSING", None, "-", doc.label))
            issues.append(f"{doc.path}: missing required key document")
            continue

        text = path.read_text(encoding="utf-8")
        commit_date = git_last_commit_date(path)
        update_stamp = extract_update_stamp(text)
        worktree_status = git_worktree_status(path)
        age_days = (today - commit_date).days if commit_date else None

        if worktree_status:
            status = "IN_PROGRESS"
        elif age_days is None:
            status = "WARN"
            issues.append(f"{doc.path}: could not determine last git commit date")
        else:
            status = status_for_age(age_days, doc.max_age_days)
            if status != "OK":
                issues.append(
                    f"{doc.path}: last changed {age_days}d ago (threshold {doc.max_age_days}d)"
                )

        if doc.requires_update_stamp and update_stamp is None:
            status = "WARN" if status == "OK" else status
            issues.append(f"{doc.path}: missing explicit Last updated stamp")

        if update_stamp and commit_date and update_stamp < commit_date and not worktree_status:
            issues.append(
                f"{doc.path}: update stamp {update_stamp.isoformat()} older than git commit {commit_date.isoformat()}"
            )
            if status == "OK":
                status = "WARN"

        key_rows.append((doc.path, status, age_days if not worktree_status else 0, update_stamp.isoformat() if update_stamp else "-", doc.label))

    legacy_hits: list[tuple[str, int, str, str]] = []
    for path in collect_markdown_files():
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(REPO_ROOT).as_posix()
        for pattern, label in LEGACY_MARKERS.items():
            match = re.search(pattern, text, flags=re.MULTILINE)
            if match:
                line_no = text[: match.start()].count("\n") + 1
                legacy_hits.append((rel, line_no, label, match.group(0)))

    print("# Documentation Freshness Audit")
    print()
    print(f"Generated: {today.isoformat()}")
    print()
    print("## Key Docs")
    print()
    print("| Path | Status | Age | Update Stamp | Role |")
    print("|---|---|---:|---|---|")
    for path, status, age_days, stamp, label in key_rows:
        age_text = "-" if age_days is None else f"{age_days}d"
        print(f"| `{path}` | **{status}** | {age_text} | {stamp} | {label} |")

    print()
    print("## Legacy Marker Hits")
    print()
    if legacy_hits:
        for rel, line_no, label, snippet in legacy_hits[:20]:
            print(f"- `{rel}:{line_no}` — {label} (`{snippet}`)")
        if len(legacy_hits) > 20:
            print(f"- ... {len(legacy_hits) - 20} more hit(s)")
    else:
        print("- None")

    print()
    print("## Suggested Quiet Cleanup Order")
    print()
    print("- Keep `docs/PROJECT_TODO.md` and `docs/research/source-of-truth-apr-2026.md` current first.")
    print("- Fix high-traffic entry docs next: `README.md`, `wake-word/README.md`, `wake-word/CLAUDE.md`.")
    print("- Mark dated research snapshots as historical rather than rewriting them into pseudo-current docs.")
    print("- Treat notebook/export packs as generated context, not source of truth.")

    if issues:
        print()
        print("## Findings")
        print()
        for issue in issues:
            print(f"- {issue}")

    return 1 if args.strict and (issues or legacy_hits) else 0


if __name__ == "__main__":
    sys.exit(main())
