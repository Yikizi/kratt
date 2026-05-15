#!/usr/bin/env python3
"""Run lightweight thesis linters against the Estonian LaTeX thesis."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from collections import Counter
from pathlib import Path

from thesis_lints.model import LintContext, SEVERITY_ORDER, ThesisDocument, ThesisFile
from thesis_lints.ranker import rank_findings


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_THESIS_ROOT = REPO_ROOT / "docs" / "thesis" / "thesis-tex-estonian"

CHECKS = {
    "terminology": "thesis_lints.checks.terminology",
    "abbreviations": "thesis_lints.checks.abbreviations",
    "estonian-style": "thesis_lints.checks.estonian_style",
    "claim-evidence": "thesis_lints.checks.claim_evidence",
    "methodology": "thesis_lints.checks.methodology",
    "scope": "thesis_lints.checks.scope",
    "defense-risk": "thesis_lints.checks.defense_risk",
    "formal-latex": "thesis_lints.checks.formal_latex",
    "readability": "thesis_lints.checks.readability",
    "narrative": "thesis_lints.checks.narrative",
    "ethics": "thesis_lints.checks.ethics",
}

PROFILES = {
    "quick": [
        "terminology",
        "abbreviations",
        "claim-evidence",
        "scope",
        "formal-latex",
        "readability",
    ],
    "final": list(CHECKS),
    "all": list(CHECKS),
}


def thesis_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for subdir in ("chapters", "misc"):
        base = root / subdir
        if not base.exists():
            continue
        for path in sorted(base.glob("*.tex")):
            if subdir == "misc" and not (
                path.name.startswith("abstract") or path.name == "terms_abbreviations.tex"
            ):
                continue
            paths.append(path)
    if not paths and root.is_file():
        paths.append(root)
    return paths


def load_document(root: Path) -> ThesisDocument:
    if not root.exists():
        raise FileNotFoundError(f"missing thesis root: {root}")
    files: list[ThesisFile] = []
    for path in thesis_files(root):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
        files.append(ThesisFile(path=path, rel_path=str(rel), text=text, lines=text.splitlines()))
    return ThesisDocument(root=root, files=files)


def selected_checks(args: argparse.Namespace) -> list[str]:
    checks: list[str] = []
    for profile in args.profile:
        checks.extend(PROFILES[profile])
    for check in args.check:
        checks.append(check)
    seen: set[str] = set()
    selected: list[str] = []
    for check in checks or PROFILES["quick"]:
        if check not in CHECKS:
            raise ValueError(f"unknown check: {check}")
        if check not in seen:
            seen.add(check)
            selected.append(check)
    return selected


def run_checks(document: ThesisDocument, context: LintContext, checks: list[str]) -> list[dict]:
    findings: list[dict] = []
    for check in checks:
        module = importlib.import_module(CHECKS[check])
        run = getattr(module, "run")
        for item in run(document, context):
            normalized = {
                "check": item.get("check", check),
                "severity": item.get("severity", "warn"),
                "path": item.get("path", ""),
                "line": int(item.get("line", 1)),
                "message": item.get("message", ""),
                "suggestion": item.get("suggestion", ""),
            }
            findings.append(normalized)
    return sorted(
        findings,
        key=lambda item: (
            -SEVERITY_ORDER.get(item["severity"], 0),
            item["path"],
            item["line"],
            item["check"],
        ),
    )


def print_text(findings: list[dict], *, max_findings: int, ranked: bool) -> None:
    counts = Counter(item["severity"] for item in findings)
    by_check = Counter(item["check"] for item in findings)
    print("# Thesis lint")
    print(f"Findings: {len(findings)}")
    for severity in ("error", "warn", "info"):
        if counts[severity]:
            print(f"- {severity}: {counts[severity]}")
    if by_check:
        print("\n## By Check")
        for check, count in sorted(by_check.items()):
            print(f"- {check}: {count}")
    if findings:
        print("\n## Findings")
        for item in findings[:max_findings]:
            rank = ""
            if ranked:
                rank = (
                    f" score={item['rank_score']} confidence={item['confidence']}"
                    f" impact={item['impact']}"
                )
            print(f"- {item['severity']}{rank} {item['path']}:{item['line']} [{item['check']}] {item['message']}")
            if item["suggestion"]:
                print(f"  -> {item['suggestion']}")
            if ranked and item.get("rank_reason"):
                print(f"  rank: {item['rank_reason']}")
        if len(findings) > max_findings:
            print(f"... {len(findings) - max_findings} more (use --json or --max-findings)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Kratt thesis lint checks")
    parser.add_argument("--root", type=Path, default=DEFAULT_THESIS_ROOT)
    parser.add_argument("--profile", action="append", choices=sorted(PROFILES), default=[])
    parser.add_argument("--check", action="append", choices=sorted(CHECKS), default=[])
    parser.add_argument("--list-checks", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--ranked", action="store_true", help="add confidence/impact ranking and sort by rank")
    parser.add_argument("--max-findings", type=int, default=80)
    parser.add_argument(
        "--fail-on",
        choices=("none", "warn", "error"),
        default="none",
        help="exit non-zero when findings at this severity or higher exist",
    )
    args = parser.parse_args(argv)

    if args.list_checks:
        for check in CHECKS:
            print(check)
        return 0

    try:
        checks = selected_checks(args)
        root = args.root.resolve()
        document = load_document(root)
        context = LintContext(
            repo_root=REPO_ROOT,
            thesis_root=root,
            profile=",".join(args.profile or ["quick"]),
        )
        findings = run_checks(document, context, checks)
        if args.ranked:
            findings = rank_findings(findings)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(
            json.dumps(
                {
                    "root": str(root),
                    "profile": args.profile or ["quick"],
                    "checks": checks,
                    "count": len(findings),
                    "by_severity": dict(Counter(item["severity"] for item in findings)),
                    "by_check": dict(Counter(item["check"] for item in findings)),
                    "findings": findings,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print_text(findings, max_findings=args.max_findings, ranked=args.ranked)

    if args.fail_on != "none":
        threshold = SEVERITY_ORDER[args.fail_on]
        if any(SEVERITY_ORDER.get(item["severity"], 0) >= threshold for item in findings):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
