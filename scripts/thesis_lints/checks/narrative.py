from __future__ import annotations

import re
from pathlib import Path

CHECK_PREFIX = "9.narrative"
MAX_LOCAL_FINDINGS = 10

CONTRIBUTION_TERMS = {
    "estonian": re.compile(r"\beesti(?:keel\w*| keele| keel)\b|väikeressurs", re.IGNORECASE),
    "wake_word": re.compile(r"äratussõn|wake[- ]word|kuule\s+kratt", re.IGNORECASE),
    "evaluation": re.compile(r"hindamisprotokoll|valideerimisprotokoll|katseprotokoll|testikomplekt|false positive|FAPH|tuvastusmäär", re.IGNORECASE),
    "local_deployment": re.compile(r"lokaal\w*|seadmesisene|ESP32|Home Assistant|Wyoming|ESPHome", re.IGNORECASE),
}

ROLE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("benchmark-best", re.compile(r"benchmark(?:i)?[- ]parim|parim\s+benchmark|võrdluskatsete\s+parim", re.IGNORECASE)),
    ("production-candidate", re.compile(r"tootmiskandidaat|juurutuskandidaat|production[- ]candidate", re.IGNORECASE)),
    ("field-best", re.compile(r"välitingimustes\s+parim|kasutajatestis\s+parim|field[- ]best", re.IGNORECASE)),
    ("packaged-default", re.compile(r"vaikemudel|pakendatud\s+mudel|packaged[- ]default", re.IGNORECASE)),
]

ABSOLUTE_CLAIM_PATTERN = re.compile(
    r"\b(esimene|ainus|parim|täielikult|lõplik|tootmisküps|production[- ]ready)\b",
    re.IGNORECASE,
)
EVIDENCE_PATTERN = re.compile(
    r"\\cite\{|joonis(?:el)?~?\\ref|tabel(?:is)?~?\\ref|lisas?~?\\ref|katse|mõõt|tulemus|andmestik",
    re.IGNORECASE,
)


def run(document, context) -> list[dict]:
    findings: list[dict] = []
    findings.extend(_find_contribution_gaps(document))
    findings.extend(_find_model_role_confusion(document))
    findings.extend(_find_unsupported_absolute_claims(document))
    findings.extend(_find_weak_transitions(document))
    return findings


def _find_contribution_gaps(document) -> list[dict]:
    findings: list[dict] = []
    for file in _core_files(document):
        text = _plain_text(file.text)
        missing = [name for name, pattern in CONTRIBUTION_TERMS.items() if not pattern.search(text)]
        if not missing:
            continue
        findings.append(_finding(
            "contribution-gap",
            "warn",
            file,
            1,
            f"Core thesis section is missing contribution anchors: {', '.join(missing)}.",
            "Keep the thesis contribution consistent: Estonian/small-language wake word, evaluation protocol, and local deployment context.",
        ))
    return findings


def _find_model_role_confusion(document) -> list[dict]:
    findings: list[dict] = []
    by_file: dict[str, set[str]] = {}
    first_line: dict[tuple[str, str], tuple[object, int]] = {}
    for file in _tex_files(document):
        roles: set[str] = set()
        for line_no, raw in enumerate(file.lines, start=1):
            line = _strip_latex_comment(raw)
            if _skip_line(line):
                continue
            for role, pattern in ROLE_PATTERNS:
                if pattern.search(line):
                    roles.add(role)
                    first_line.setdefault((_path(file), role), (file, line_no))
        if roles:
            by_file[_path(file)] = roles

    for path, roles in by_file.items():
        if len(roles) < 2:
            continue
        role = sorted(roles)[1]
        file, line_no = first_line[(path, role)]
        findings.append(_finding(
            "model-role-mix",
            "warn",
            file,
            line_no,
            f"Multiple model roles are discussed in one section: {', '.join(sorted(roles))}.",
            "State explicitly whether the model is benchmark-best, field-best, production-candidate, or packaged default.",
        ))
        if len(findings) >= MAX_LOCAL_FINDINGS:
            break
    return findings


def _find_unsupported_absolute_claims(document) -> list[dict]:
    findings: list[dict] = []
    for file in _tex_files(document):
        for line_no, sentence in _iter_sentences(file):
            if not ABSOLUTE_CLAIM_PATTERN.search(sentence):
                continue
            if EVIDENCE_PATTERN.search(sentence):
                continue
            findings.append(_finding(
                "unsupported-absolute-claim",
                "warn",
                file,
                line_no,
                "Absolute novelty or readiness claim appears without nearby evidence.",
                "Qualify the claim or attach a citation, measurement, table, or explicit evaluation result.",
            ))
            if len(findings) >= MAX_LOCAL_FINDINGS:
                return findings
    return findings


def _find_weak_transitions(document) -> list[dict]:
    findings: list[dict] = []
    for file in _tex_files(document):
        for line_no, raw in enumerate(file.lines, start=1):
            if not re.match(r"\\(?:section|subsection|subsubsection)\{", raw.strip()):
                continue
            after = " ".join(file.lines[line_no: line_no + 4])
            clean_after = _plain_text(after).strip()
            if clean_after and _word_count(clean_after) < 18:
                findings.append(_finding(
                    "thin-section-opening",
                    "info",
                    file,
                    line_no,
                    "Section opening appears very thin after the heading.",
                    "Add one orienting sentence that connects the section to the thesis question or previous result.",
                ))
                if len(findings) >= MAX_LOCAL_FINDINGS:
                    return findings
    return findings


def _core_files(document):
    core_names = {
        "abstract-estonian.tex",
        "abstract-english.tex",
        "introduction.tex",
        "summary.tex",
    }
    return [file for file in _tex_files(document) if Path(_path(file)).name in core_names]


def _iter_sentences(file):
    buffer: list[str] = []
    start_line = 1
    for line_no, raw in enumerate(file.lines, start=1):
        line = _strip_latex_comment(raw)
        if _skip_line(line):
            continue
        if not buffer:
            start_line = line_no
        buffer.append(line.strip())
        joined = " ".join(buffer)
        if re.search(r"[\.\?!](?:\s|$)", joined):
            parts = re.split(r"(?<=[\.\?!])\s+", joined)
            for sentence in parts[:-1]:
                yield start_line, sentence
            buffer = [parts[-1]] if parts[-1] else []
            start_line = line_no
    if buffer:
        yield start_line, " ".join(buffer)


def _tex_files(document):
    return [file for file in document.files if _path(file).endswith(".tex")]


def _skip_line(line: str) -> bool:
    stripped = line.strip()
    return not stripped or stripped.startswith("%") or stripped.startswith("\\label")


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


def _plain_text(text: str) -> str:
    text = re.sub(r"\\(?:cite|ref|autoref|pageref|label|url|path|texttt)\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?", " ", text)
    text = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?(?:\{([^{}]*)\})?", r" \1 ", text)
    return re.sub(r"[$\\{}_^&%#~]", " ", text)


def _word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-zÀ-ž0-9]+(?:[-–][A-Za-zÀ-ž0-9]+)?", text))


def _path(file) -> str:
    return str(getattr(file, "rel_path", getattr(file, "path", "")))


def _finding(check: str, severity: str, file, line: int, message: str, suggestion: str) -> dict:
    return {
        "check": f"{CHECK_PREFIX}.{check}",
        "severity": severity,
        "path": _path(file),
        "line": int(line),
        "message": message,
        "suggestion": suggestion,
    }
