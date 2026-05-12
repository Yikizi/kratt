from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ThesisFile:
    path: Path
    rel_path: str
    text: str
    lines: list[str]


@dataclass(frozen=True)
class ThesisDocument:
    root: Path
    files: list[ThesisFile]


@dataclass(frozen=True)
class LintContext:
    repo_root: Path
    thesis_root: Path
    profile: str


SEVERITY_ORDER = {
    "info": 0,
    "warn": 1,
    "error": 2,
}


def finding(
    check: str,
    severity: str,
    path: str,
    line: int,
    message: str,
    suggestion: str = "",
) -> dict:
    if severity not in SEVERITY_ORDER:
        raise ValueError(f"unknown severity: {severity}")
    return {
        "check": check,
        "severity": severity,
        "path": path,
        "line": int(line),
        "message": message,
        "suggestion": suggestion,
    }


def cap_findings(items: list[dict], limit: int) -> list[dict]:
    return items[:limit]
