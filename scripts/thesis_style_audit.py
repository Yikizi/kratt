#!/usr/bin/env python3
"""Audit the Estonian thesis for compression-mode style regressions.

This is intentionally lightweight: it does not parse LaTeX fully. It catches the
patterns that have made the Kratt thesis too long or visually inconsistent:
source footnotes, unnecessary English glosses, mixed-language terminology,
overlong captions, and TODO/dummy artefacts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_THESIS_ROOT = REPO_ROOT / "docs" / "thesis" / "thesis-tex-estonian"

ENGLISHISM_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    ("wake word", re.compile(r"\bwake[- ]word\b", re.I), "äratussõna"),
    ("pipeline", re.compile(r"\bpipeline\b", re.I), "töötlustoru / treeningutoru"),
    ("baseline", re.compile(r"\bbaseline\b", re.I), "baasvariant / baasjoon"),
    ("hold-out", re.compile(r"\bhold[- ]out\b", re.I), "sõltumatu testikomplekt"),
    ("hard negative", re.compile(r"\bhard[- ]negative\w*\b|\bhard negatiiv", re.I), "foneetiliselt sarnane negatiivne näide"),
    ("unseen", re.compile(r"\bunseen[- ](?:speaker|kõneleja)|\bunseen\b", re.I), "treeningus nägemata kõneleja"),
    ("recall", re.compile(r"\brecall(?:'i|i|\b)", re.I), "tuvastusmäär"),
    ("threshold/cutoff", re.compile(r"\bthreshold\b|\bcutoff\b", re.I), "lävi"),
    ("streaming", re.compile(r"\bstreaming\b", re.I), "pidevvoog / voogedastus"),
    ("deploy", re.compile(r"\bdeploy(?:-\w+)?\b|\bdeployment\b", re.I), "juurutamine"),
    ("runtime", re.compile(r"\bruntime\b", re.I), "käitusaeg"),
    ("framework", re.compile(r"\bframework\b", re.I), "raamistik"),
    ("sanity-check", re.compile(r"\bsanity[- ]check\b", re.I), "kontrollkatse"),
    ("shortcut", re.compile(r"\bshortcut\b", re.I), "lühitee"),
    ("feature", re.compile(r"\bfeature(?:s)?\b", re.I), "tunnus"),
]

@dataclass
class Finding:
    kind: str
    path: str
    line: int
    snippet: str
    suggestion: str


def thesis_files(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for subdir in ("chapters", "misc"):
        base = root / subdir
        if not base.exists():
            continue
        for path in sorted(base.glob("*.tex")):
            if subdir == "misc" and not path.name.startswith("abstract") and path.name != "terms_abbreviations.tex":
                continue
            candidates.append(path)
    return candidates


def strip_codeish(text: str) -> str:
    """Remove common code/file-name/cross-reference LaTeX wrappers before prose checks."""
    # Good enough for one-level arguments used in this thesis.
    for cmd in ("texttt", "url", "path", "label", "ref", "pageref", "cite"):
        text = re.sub(rf"\\{cmd}\{{[^{{}}]*\}}", "", text)
    return text


def word_count(text: str) -> int:
    text = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?(?:\{([^{}]*)\})?", r" \1 ", text)
    text = re.sub(r"[$\\{}_^&%#~]", " ", text)
    return len(re.findall(r"[A-Za-zÀ-ž0-9]+(?:[-–][A-Za-zÀ-ž0-9]+)?", text))


def iter_caption_blocks(lines: list[str]) -> list[tuple[int, str]]:
    blocks: list[tuple[int, str]] = []
    i = 0
    while i < len(lines):
        if "\\caption{" not in lines[i]:
            i += 1
            continue
        start = i + 1
        buf = [lines[i]]
        balance = lines[i].count("{") - lines[i].count("}")
        i += 1
        while i < len(lines) and balance > 0:
            buf.append(lines[i])
            balance += lines[i].count("{") - lines[i].count("}")
            i += 1
        blocks.append((start, " ".join(buf)))
    return blocks


def audit_file(path: Path, root: Path, caption_words: int) -> list[Finding]:
    rel = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
    lines = path.read_text(encoding="utf-8").splitlines()
    findings: list[Finding] = []

    for idx, raw in enumerate(lines, start=1):
        prose = strip_codeish(raw)
        snippet = raw.strip()
        if not snippet or snippet.startswith("%"):
            continue

        if "\\footnote{" in raw:
            findings.append(Finding(
                "chapter-footnote",
                str(rel),
                idx,
                snippet[:220],
                "Kasuta allika jaoks \\cite{...}; jäta joonealused märkused ainult vältimatutele vormilistele märkustele.",
            ))

        if re.search(r"\(\s*ingl\b|\bingl\.?\s+|\binglise\s+keel", prose, re.I):
            findings.append(Finding(
                "english-gloss",
                str(rel),
                idx,
                snippet[:220],
                "Eemalda '(ingl ...)' muster või asenda üks kord lühendite/mõistete sõnastikus defineeritud terminiga.",
            ))

        if re.search(r"\bTODO\b|platsihoidj|Something Else|Something\b", prose, re.I):
            findings.append(Finding(
                "placeholder-artifact",
                str(rel),
                idx,
                snippet[:220],
                "Eemalda TODO/dummy artefakt lõppdokumendist või asenda päris tulemusega.",
            ))

        for name, pattern, estonian in ENGLISHISM_PATTERNS:
            if pattern.search(prose):
                findings.append(Finding(
                    "englishism",
                    str(rel),
                    idx,
                    snippet[:220],
                    f"Kaalu eestikeelset vastet: {estonian} (muster: {name}).",
                ))
                break

    for line_no, caption in iter_caption_blocks(lines):
        n = word_count(caption)
        if n > caption_words:
            findings.append(Finding(
                "long-caption",
                str(rel),
                line_no,
                caption.strip()[:220],
                f"Lühenda pealkirja/märkust; praegu umbes {n} sõna, piir {caption_words}.",
            ))

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit thesis prose for compression-mode style issues")
    parser.add_argument("--root", type=Path, default=DEFAULT_THESIS_ROOT, help="thesis LaTeX root")
    parser.add_argument("--caption-words", type=int, default=45, help="flag captions longer than this many words")
    parser.add_argument("--max-examples", type=int, default=80, help="maximum examples to print in text mode")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--fail-on-findings", action="store_true", help="exit 1 when findings exist")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not root.exists():
        print(f"missing thesis root: {root}", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    for path in thesis_files(root):
        findings.extend(audit_file(path, root, args.caption_words))

    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.kind] = counts.get(finding.kind, 0) + 1

    if args.json:
        print(json.dumps({
            "root": str(root),
            "count": len(findings),
            "by_kind": counts,
            "findings": [asdict(f) for f in findings],
        }, ensure_ascii=False, indent=2))
    else:
        print("# Thesis style audit")
        print(f"Root: {root}")
        print(f"Findings: {len(findings)}")
        for kind, count in sorted(counts.items()):
            print(f"- {kind}: {count}")
        if findings:
            print("\n## Examples")
            for finding in findings[: args.max_examples]:
                print(f"- {finding.kind} {finding.path}:{finding.line}: {finding.snippet}")
                print(f"  -> {finding.suggestion}")
            if len(findings) > args.max_examples:
                print(f"... {len(findings) - args.max_examples} more (use --json or --max-examples)")

    if findings and args.fail_on_findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
