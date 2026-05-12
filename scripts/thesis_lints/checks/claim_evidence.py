from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


CHECK_PREFIX = "3.claim_evidence"
MAX_FINDINGS = 40
MAX_PER_RULE = 6


STRONG_CLAIM_RE = re.compile(
    r"\b("
    r"esimene|ainus|parim|suurim|väikseim|täielik|kindlasti|tõestab|tõestas|"
    r"märkimisväärselt|oluliselt|selgelt\s+parem|ületab|ületavad|ületati|"
    r"tootmiskandidaat|production\s+candidate|publicly\s+available"
    r")\b",
    re.IGNORECASE,
)
COMPARATIVE_RE = re.compile(
    r"\b(parem|halvem|suurem|väiksem|kiirem|aeglasem|täpsem|madalam|kõrgem|paranes|vähenes|suurenes|langes)\b",
    re.IGNORECASE,
)
METRIC_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])\d+(?:[,.]\d+)?\s*(?:\\?%|FAPH|FA/h|ms|s|h|tundi|KB|kB|MB|MHz|kHz)\b",
    re.IGNORECASE,
)
EVIDENCE_RE = re.compile(
    r"\\(?:cite\w*|ref|pageref|autoref|cref|Cref|eqref)\b|"
    r"\b(?:Tabel|tabel|Joonis|joonis|Lisa|lisa)\s*~?\\(?:ref|autoref|cref)\b|"
    r"\b(?:tabelis|joonisel|lisas)\s+\d+",
    re.IGNORECASE,
)
DATA_SOURCE_RE = re.compile(
    r"\b("
    r"mõõdeti|hindamis|testikomplekt|andmestik|katse|tabel|joonis|lisa|"
    r"Common\s*Voice|DiPCo"
    r")\b",
    re.IGNORECASE,
)

CODEISH_COMMANDS = (
    "texttt",
    "url",
    "path",
    "href",
    "label",
    "ref",
    "pageref",
    "autoref",
    "cref",
    "Cref",
    "cite",
    "citep",
    "citet",
)


def run(document, context) -> list[dict]:
    findings: list[dict] = []
    counts: dict[str, int] = {}

    for thesis_file in getattr(document, "files", []):
        path = _display_path(thesis_file, context)
        if path and not path.endswith(".tex"):
            continue
        numbered_lines = list(_iter_lines(thesis_file))

        for offset, (line_no, raw_line) in enumerate(numbered_lines):
            raw_without_comment = _strip_latex_comment(raw_line)
            prose = _strip_codeish(raw_without_comment)
            if not _is_claim_line(prose, raw_without_comment):
                continue

            window = _evidence_window(numbered_lines, offset)
            has_evidence = bool(EVIDENCE_RE.search(window) or DATA_SOURCE_RE.search(window))

            if counts.get("unsupported-strong-claim", 0) < MAX_PER_RULE and _has_unnegated_strong_claim(prose):
                if not has_evidence:
                    findings.append(
                        _finding(
                            "unsupported-strong-claim",
                            path,
                            line_no,
                            "Tugev uudsus-, paremuse- või kindlusväide vajab lähedast tõendit.",
                            "Lisa samasse lõiku viide, tabeli/joonise osutus või pehmenda väidet tõenditega kooskõlla.",
                        )
                    )
                    counts["unsupported-strong-claim"] = counts.get("unsupported-strong-claim", 0) + 1

            if counts.get("unsupported-metric-comparison", 0) < MAX_PER_RULE:
                if METRIC_RE.search(prose) and COMPARATIVE_RE.search(prose) and not has_evidence:
                    findings.append(
                        _finding(
                            "unsupported-metric-comparison",
                            path,
                            line_no,
                            "Arvuline võrdlus või paranemisväide vajab otsest tõendusallikat.",
                            "Seo väide tabeli, joonise, mõõtmisprotokolli või viitega.",
                        )
                    )
                    counts["unsupported-metric-comparison"] = counts.get("unsupported-metric-comparison", 0) + 1

            if counts.get("missing-experiment-reference", 0) < MAX_PER_RULE:
                if _looks_like_result_claim(prose) and not has_evidence:
                    findings.append(
                        _finding(
                            "missing-experiment-reference",
                            path,
                            line_no,
                            "Tulemuse või mõõdiku väide ei osuta lähedal katsele, tabelile ega allikale.",
                            "Lisa viide mõõtmisprotokollile, tabelile/joonisele või kirjuta väide kirjeldavamalt.",
                        )
                    )
                    counts["missing-experiment-reference"] = counts.get("missing-experiment-reference", 0) + 1

            if len(findings) >= MAX_FINDINGS:
                return findings

    return findings


def _finding(rule_id: str, path: str, line: int, message: str, suggestion: str) -> dict:
    return {
        "check": f"{CHECK_PREFIX}.{rule_id}",
        "severity": "warn",
        "path": path,
        "line": line,
        "message": message,
        "suggestion": suggestion,
    }


def _iter_lines(thesis_file) -> Iterable[tuple[int, str]]:
    lines = getattr(thesis_file, "lines", None)
    if lines is None:
        lines = getattr(thesis_file, "text", "").splitlines()
    for index, line in enumerate(lines, start=1):
        yield index, str(line)


def _display_path(thesis_file, context) -> str:
    rel_path = getattr(thesis_file, "rel_path", None)
    if rel_path:
        return str(rel_path)

    path = Path(str(getattr(thesis_file, "path", "")))
    root = getattr(context, "root", None) or getattr(context, "thesis_root", None) or getattr(context, "repo_root", None)
    if root:
        try:
            return str(path.relative_to(Path(root)))
        except ValueError:
            pass
    return str(path)


def _strip_latex_comment(line: str) -> str:
    escaped = False
    for index, char in enumerate(line):
        if char == "\\" and not escaped:
            escaped = True
            continue
        if char == "%" and not escaped:
            return line[:index]
        escaped = False
    return line


def _strip_codeish(text: str) -> str:
    for command in CODEISH_COMMANDS:
        text = re.sub(rf"\\{command}\*?(?:\[[^\]]*\])?\{{[^{{}}]*\}}", " ", text)
    return text


def _is_claim_line(prose: str, raw_line: str) -> bool:
    stripped = prose.strip()
    if not stripped:
        return False
    if stripped.startswith(("\\begin", "\\end", "\\label", "\\includegraphics", "\\bibliography", "\\chapter", "\\section", "\\subsection")):
        return False
    if "&" in raw_line and r"\\" in raw_line:
        return False
    return bool(re.search(r"[A-Za-zÀ-ž]", stripped))


def _evidence_window(numbered_lines: list[tuple[int, str]], offset: int) -> str:
    start = max(0, offset - 1)
    end = min(len(numbered_lines), offset + 2)
    return "\n".join(_strip_latex_comment(line) for _, line in numbered_lines[start:end])


def _looks_like_result_claim(prose: str) -> bool:
    if not METRIC_RE.search(prose):
        return False
    return bool(
        re.search(
            r"\b(saavutas|saavutati|andis|annab|näitas|näitab|tulemus|täpsus|"
            r"valepositiiv|tuvastusmäär|veamäär|latentsus)\b",
            prose,
            re.IGNORECASE,
        )
    )


def _has_unnegated_strong_claim(prose: str) -> bool:
    for match in STRONG_CLAIM_RE.finditer(prose):
        prefix = prose[max(0, match.start() - 40): match.start()].lower()
        if re.search(r"\b(?:mitte|ei|ega)\s+(?:\w+\s+){0,2}$", prefix):
            continue
        return True
    return False
