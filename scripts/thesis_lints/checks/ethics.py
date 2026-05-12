from __future__ import annotations

import re

CHECK_PREFIX = "10.ethics"
MAX_LOCAL_FINDINGS = 12

VOICE_DATA_PATTERN = re.compile(
    r"hääle(?:salvest|andme|fail|näid)|kõne(?:salvest|andme|fail|näid)|helisalvest|salvestati|mikrofon|kasutajakatse",
    re.IGNORECASE,
)
CONSENT_PATTERN = re.compile(r"nõusolek|informeeritud\s+nõusolek|opt[- ]?in|vabatahtlik", re.IGNORECASE)
GDPR_PATTERN = re.compile(r"GDPR|isikuandme|andmekaitse|anon(?:ü|u)m|pseudon(?:ü|u)m|kustuta|säilit", re.IGNORECASE)
RISKY_STORAGE_PATTERN = re.compile(
    r"(?:salvestati|säilitati|koguti|laeti|jagati).{0,80}(?:hääle|kõne|heli|kasutaja)",
    re.IGNORECASE,
)
IDENTIFIER_PATTERN = re.compile(r"\b(?:nimi|e-post|email|telefon|isikukood|IP-aadress)\b", re.IGNORECASE)


def run(document, context) -> list[dict]:
    findings: list[dict] = []
    findings.extend(_find_global_ethics_gaps(document))
    findings.extend(_find_local_consent_gaps(document))
    findings.extend(_find_identifier_gaps(document))
    return findings


def _find_global_ethics_gaps(document) -> list[dict]:
    text = "\n".join(_plain_text(file.text) for file in _tex_files(document))
    findings: list[dict] = []
    anchor = _first_voice_file(document)
    if not anchor:
        return findings

    if VOICE_DATA_PATTERN.search(text) and not CONSENT_PATTERN.search(text):
        findings.append(_finding(
            "missing-consent-mention",
            "error",
            anchor,
            1,
            "Voice or speech data is discussed, but informed consent is not mentioned in the thesis text.",
            "Add a concise consent statement covering participant opt-in and use of recordings.",
        ))

    if VOICE_DATA_PATTERN.search(text) and not GDPR_PATTERN.search(text):
        findings.append(_finding(
            "missing-gdpr-privacy-mention",
            "error",
            anchor,
            1,
            "Voice or speech data is discussed, but GDPR/privacy handling is not visible.",
            "Mention GDPR or equivalent privacy handling: minimisation, retention, anonymisation, and deletion where relevant.",
        ))

    return findings


def _find_local_consent_gaps(document) -> list[dict]:
    findings: list[dict] = []
    for file in _tex_files(document):
        for line_no, raw in enumerate(file.lines, start=1):
            line = _strip_latex_comment(raw)
            if _skip_line(line) or not RISKY_STORAGE_PATTERN.search(line):
                continue
            window = _nearby_text(file.lines, line_no, radius=3)
            if CONSENT_PATTERN.search(window) and GDPR_PATTERN.search(window):
                continue
            findings.append(_finding(
                "voice-recording-context",
                "warn",
                file,
                line_no,
                "Voice recording/storage sentence lacks nearby consent and privacy context.",
                "Add a nearby clause about opt-in consent, retention/deletion, or anonymisation.",
            ))
            if len(findings) >= MAX_LOCAL_FINDINGS:
                return findings
    return findings


def _find_identifier_gaps(document) -> list[dict]:
    findings: list[dict] = []
    for file in _prose_files(document):
        for line_no, raw in enumerate(file.lines, start=1):
            line = _strip_latex_comment(raw)
            if _skip_line(line) or not IDENTIFIER_PATTERN.search(line):
                continue
            window = _nearby_text(file.lines, line_no, radius=4)
            if GDPR_PATTERN.search(window) or CONSENT_PATTERN.search(window):
                continue
            findings.append(_finding(
                "personal-identifier-context",
                "warn",
                file,
                line_no,
                "Personal identifier is mentioned without nearby privacy handling context.",
                "Clarify why the identifier is needed and how it is minimised, protected, or removed.",
            ))
            if len(findings) >= MAX_LOCAL_FINDINGS:
                return findings
    return findings


def _first_voice_file(document):
    for file in _tex_files(document):
        if VOICE_DATA_PATTERN.search(file.text):
            return file
    return next(iter(_tex_files(document)), None)


def _nearby_text(lines: list[str], line_no: int, radius: int) -> str:
    start = max(0, line_no - radius - 1)
    end = min(len(lines), line_no + radius)
    return _plain_text(" ".join(lines[start:end]))


def _tex_files(document):
    return [file for file in document.files if _path(file).endswith(".tex")]


def _prose_files(document):
    skipped_names = {
        "authordeclaration.tex",
        "config.tex",
        "licence.tex",
        "titlepage.tex",
    }
    return [file for file in _tex_files(document) if _path(file).split("/")[-1] not in skipped_names]


def _skip_line(line: str) -> bool:
    stripped = line.strip()
    return not stripped or stripped.startswith("%") or stripped.startswith("\\")


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
