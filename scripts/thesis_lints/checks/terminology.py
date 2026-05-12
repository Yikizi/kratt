from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


CHECK_PREFIX = "1.terminology"
MAX_FINDINGS = 45
MAX_PER_RULE = 4


TERMINOLOGY_RULES: tuple[tuple[str, re.Pattern[str], str, str], ...] = (
    (
        "english-wake-word",
        re.compile(r"\bwake[- ]word(?:'?\w*)?\b", re.IGNORECASE),
        "Ingliskeelne 'wake word' jääb eestikeelses lõputöös terminina võõraks.",
        "Kasuta läbivalt terminit 'äratussõna' ja defineeri ingliskeelne vaste ainult mõistete loetelus.",
    ),
    (
        "english-pipeline",
        re.compile(r"\bpipeline(?:'?\w*)?\b", re.IGNORECASE),
        "Ingliskeelne 'pipeline' on terminoloogiliselt ebamäärane.",
        "Kasuta konteksti järgi 'töötlustoru', 'treeningutoru' või 'protsess'.",
    ),
    (
        "english-baseline",
        re.compile(r"\bbaseline(?:'?\w*)?\b", re.IGNORECASE),
        "Ingliskeelne 'baseline' vajab eestikeelset vastet.",
        "Kasuta 'baasvariant', 'baasjoon' või 'võrdlusvariant'.",
    ),
    (
        "english-holdout",
        re.compile(r"\bhold[- ]out(?:'?\w*)?\b", re.IGNORECASE),
        "Ingliskeelne 'hold-out' võib lugejale jääda ebaselgeks.",
        "Kasuta 'sõltumatu testikomplekt' või 'treeningust eraldatud testikomplekt'.",
    ),
    (
        "english-hard-negative",
        re.compile(r"\bhard[- ]negative(?:'?\w*)?\b|\bhard negatiiv\w*\b", re.IGNORECASE),
        "Ingliskeelne 'hard negative' vajab täpset eestikeelset kirjeldust.",
        "Kasuta näiteks 'foneetiliselt sarnane negatiivne näide'.",
    ),
    (
        "english-recall",
        re.compile(r"\brecall(?:'?\w*)?\b", re.IGNORECASE),
        "Ingliskeelne 'recall' ei ole eestikeelses tekstis iseseisva terminina parim.",
        "Kasuta 'tuvastusmäär', 'saagis' või defineeri mõõdik mõistete loetelus.",
    ),
    (
        "english-threshold",
        re.compile(r"\bthreshold(?:'?\w*)?\b|\bcut[- ]?off(?:'?\w*)?\b", re.IGNORECASE),
        "Läve kohta kasutatakse ingliskeelset terminit.",
        "Kasuta 'lävi' või 'otsustuslävi'.",
    ),
    (
        "english-streaming",
        re.compile(r"\bstreaming(?:'?\w*)?\b", re.IGNORECASE),
        "Ingliskeelne 'streaming' tuleks eestikeelses tehnilises tekstis asendada.",
        "Kasuta 'pidevvoog', 'voogedastus' või 'voogedastusrada'.",
    ),
    (
        "english-deployment",
        re.compile(r"\bdeploy(?:ment|ed|ing)?(?:'?\w*)?\b", re.IGNORECASE),
        "Juurutamise kohta kasutatakse ingliskeelset tüve.",
        "Kasuta 'juurutama', 'juurutus' või 'kasutusele võtma'.",
    ),
    (
        "english-dataset",
        re.compile(r"\bdataset(?:'?\w*)?\b", re.IGNORECASE),
        "Ingliskeelne 'dataset' on eestikeelses tekstis välditav.",
        "Kasuta 'andmestik'.",
    ),
    (
        "split-aratussona",
        re.compile(r"\bäratus\s+sõn\w*\b", re.IGNORECASE),
        "Termin 'äratussõna' peaks olema kokku kirjutatud.",
        "Kirjuta 'äratussõna'.",
    ),
    (
        "split-false-positive",
        re.compile(r"\bvale\s+positiiv\w*\b|\bvale\s+negatiiv\w*\b", re.IGNORECASE),
        "Valepositiivne ja valenegatiivne kirjutatakse terminina kokku.",
        "Kasuta 'valepositiivne' või 'valenegatiivne'.",
    ),
    (
        "kuule-kratt-capitalization",
        re.compile(r"(?<![A-Za-zÀ-ž])kuule\s+kratt(?![A-Za-zÀ-ž])"),
        "Äratusfraasi nimi peaks olema läbivalt ühtse suurtähekasutusega.",
        "Kasuta äratusfraasi nimena 'Kuule Kratt'.",
    ),
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
        if _is_english_abstract(path):
            continue
        for line_no, raw_line in _iter_lines(thesis_file):
            prose = _strip_codeish(_strip_latex_comment(raw_line))
            if not _is_prose_line(prose):
                continue

            for rule_id, pattern, message, suggestion in TERMINOLOGY_RULES:
                if counts.get(rule_id, 0) >= MAX_PER_RULE:
                    continue
                if rule_id == "english-dataset" and _is_official_dataset_name(prose):
                    continue
                match = pattern.search(prose)
                if not match:
                    continue
                findings.append(_finding(rule_id, path, line_no, message, suggestion))
                counts[rule_id] = counts.get(rule_id, 0) + 1
                break

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


def _is_prose_line(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if stripped.startswith(("\\begin", "\\end", "\\label", "\\includegraphics", "\\bibliography")):
        return False
    return bool(re.search(r"[A-Za-zÀ-ž]", stripped))


def _is_english_abstract(path: str) -> bool:
    return path.endswith("misc/abstract-english.tex") or path.endswith("abstract-english.tex")


def _is_official_dataset_name(text: str) -> bool:
    return bool(re.search(r"\b[A-Z][A-Za-z]+\s+[A-Z][A-Za-z]+\s+Dataset\b", text))
