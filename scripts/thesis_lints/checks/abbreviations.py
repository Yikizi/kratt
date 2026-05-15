from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from thesis_lints.model import finding


CHECK_PREFIX = "1.abbreviations"
MAX_FINDINGS = 40

# The goal is not to police every product name, programming language, or unit.
# It is to catch thesis-active acronym-like tokens that should be explained in
# misc/terms_abbreviations.tex.
IGNORED_TOKENS = {
    "C/C++",
    "KB",
    "OFF",
    "ON",
    "TypeScript/Node",
    "TypeScript/Node.js",
}

IGNORED_BASES = {
    # Proper names / product names that are self-identifying in prose or cited.
    "EuroSpeech",
    "Home",
    "LibriSpeech",
    "MacBook",
    "MixedConv",
    "MixedNet",
    "NumPy",
    "Picovoice",
    "SpecAugment",
    "Speech",
    "TalTech",
    "TalTechNLP",
    "TensorFlow",
    "WiZ",
    "microWakeWord",
    "openWakeWord",
    # Table/prose shorthand that is defined locally or not a glossary item.
    "Ambient-FAPH",
    "Hey-Siri",
    "Kontrollpunkti-FAPH",
    "Poissoni-Garwoodi",
}

# Estonian case endings and derivational tails often appear after a glossary
# acronym (FAPH-i, TTS-iga, XML-tekst). Strip only when the acronym part itself
# is known in the glossary.
CASE_SUFFIXES = {
    "d",
    "ga",
    "i",
    "iga",
    "il",
    "ile",
    "ilt",
    "ina",
    "ini",
    "ist",
    "it",
    "ks",
    "l",
    "le",
    "lt",
    "na",
    "ni",
    "s",
    "st",
    "t",
}

ACRONYM_RE = re.compile(
    r"(?<![A-Za-zÀ-ž0-9])(?:"
    # Metric/compound forms such as 1K-FPR, Conf-FPR, BC-ResNet, KWS-Net.
    r"(?:Conf|Pre|Rev)-FPR|DET-kõver|UMUX-Lite"
    r"|(?:[A-ZÄÖÕÜ0-9]*[A-ZÄÖÕÜ][A-Z0-9ÄÖÕÜ]+)(?:-[A-Za-z0-9ÄÖÕÜ]+)+"
    r"|FA/h"
    # Uppercase or uppercase-led mixed forms such as KWS, ESP32-S3, TFLite, VOiCES.
    r"|DiPCo|[A-ZÄÖÕÜ][a-z][A-ZÄÖÕÜ]"
    r"|[A-ZÄÖÕÜ]{2,}[A-Za-z0-9ÄÖÕÜ]*(?:/[A-Za-z0-9ÄÖÕÜ]+)?"
    r")(?!(?:[A-Za-z0-9]|\\))"
)

DROP_COMMAND_WITH_ARG_RE = re.compile(
    r"\\(?:cite|parencite|textcite|autocite|ref|pageref|label|zlabel|url|href|includegraphics|input|bibliography)"
    r"\*?(?:\[[^\]]*\])*\{[^{}]*\}"
)
COMMAND_RE = re.compile(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?")
TERM_ROW_RE = re.compile(r"^\s*([^&\\]+?)\s*&")


def run(document, context) -> list[dict]:
    glossary_terms = _glossary_terms(document)
    findings: list[dict] = []
    seen: set[str] = set()

    for thesis_file in getattr(document, "files", []):
        path = _display_path(thesis_file, context)
        if path.endswith("terms_abbreviations.tex"):
            continue
        if path and not path.endswith(".tex"):
            continue

        for line_no, raw_line in _iter_lines(thesis_file):
            line = _strip_latex_for_acronyms(_strip_latex_comment(raw_line))
            for token in _candidate_tokens(line):
                normalized = _normalize_token(token, glossary_terms)
                if not normalized:
                    continue
                if normalized in glossary_terms:
                    continue
                if normalized in IGNORED_TOKENS or normalized in IGNORED_BASES:
                    continue
                if _is_ignorable_token(normalized):
                    continue
                key = f"{path}:{normalized}"
                if key in seen:
                    continue
                seen.add(key)
                findings.append(
                    finding(
                        f"{CHECK_PREFIX}.missing-glossary-entry",
                        "warn",
                        path,
                        line_no,
                        f"Lühend või akronüüm '{normalized}' puudub lühendite ja mõistete tabelist.",
                        (
                            "Lisa termin faili misc/terms_abbreviations.tex või lisa see teadlikult "
                            "erandite hulka, kui tegu pole sõnastikuüksusega."
                        ),
                    )
                )
                if len(findings) >= MAX_FINDINGS:
                    return findings

    return findings


def _glossary_terms(document) -> set[str]:
    terms: set[str] = set()
    for thesis_file in getattr(document, "files", []):
        path = str(getattr(thesis_file, "rel_path", "") or getattr(thesis_file, "path", ""))
        if not path.endswith("terms_abbreviations.tex"):
            continue
        lines = getattr(thesis_file, "lines", None) or getattr(thesis_file, "text", "").splitlines()
        for raw_line in lines:
            match = TERM_ROW_RE.match(str(raw_line))
            if not match:
                continue
            term = match.group(1).strip()
            if term:
                terms.add(term)
    return terms


def _candidate_tokens(line: str) -> Iterable[str]:
    for match in ACRONYM_RE.finditer(line):
        token = match.group(0).strip("{}[]().,;:")
        if token:
            yield token


def _normalize_token(token: str, glossary_terms: set[str]) -> str | None:
    token = token.strip("{}[]().,;:")
    if not token:
        return None
    if token in glossary_terms:
        return token
    if "/" in token:
        parts = [part for part in token.split("/") if part]
        if parts and all(part in glossary_terms for part in parts):
            return None

    # Exact glossary terms with Estonian endings or compounds: FAPH-i, XML-tekst.
    for term in sorted(glossary_terms, key=len, reverse=True):
        if len(term) < 2:
            continue
        if token.startswith(term + "-"):
            tail = token[len(term) + 1 :]
            if tail in CASE_SUFFIXES or tail[:1].islower():
                return term

    # ET-l and similar short glossary terms.
    if "-" in token:
        head, tail = token.split("-", 1)
        if head in glossary_terms and (tail in CASE_SUFFIXES or tail[:1].islower()):
            return head

    return token


def _is_ignorable_token(token: str) -> bool:
    if token in IGNORED_TOKENS:
        return True
    if token in IGNORED_BASES:
        return True
    if token.startswith(("v", "V")) and re.fullmatch(r"[vV]\d+[A-Za-z0-9-]*", token):
        return True
    if re.fullmatch(r"\d+(?:/\d+)+", token):
        return True
    if re.fullmatch(r"\d+[A-Z]?/\d+", token):
        return True
    if re.fullmatch(r"\d+K?", token):
        return True
    return False


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


def _strip_latex_for_acronyms(text: str) -> str:
    text = DROP_COMMAND_WITH_ARG_RE.sub(" ", text)
    text = COMMAND_RE.sub(" ", text)
    return (
        text.replace(r"\%", "%")
        .replace(r"\_", "_")
        .replace("~", " ")
        .replace("$", " ")
    )


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
