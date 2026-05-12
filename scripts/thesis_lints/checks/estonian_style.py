from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


CHECK_PREFIX = "2.estonian_style"
MAX_FINDINGS = 50
MAX_PER_RULE = 6
LONG_SENTENCE_WORDS = 48


STYLE_RULES: tuple[tuple[str, re.Pattern[str], str, str], ...] = (
    (
        "english-gloss",
        re.compile(r"\(\s*ingl\b|\bingl\.?\s+[A-Za-zÀ-ž-]+", re.IGNORECASE),
        "Tekst kasutab sulgudes ingliskeelset glossi.",
        "Defineeri ingliskeelne vaste üks kord mõistete loetelus või eemalda gloss põhitekstist.",
    ),
    (
        "bureaucratic-omama",
        re.compile(r"\bomab\b|\bomavad\b|\bomas\b|\bomanud\b", re.IGNORECASE),
        "'Omama' teeb tehnilise lause sageli raskepäraseks.",
        "Kasuta täpsemat verbi, näiteks 'sisaldab', 'hõlmab', 'sellel on' või 'annab'.",
    ),
    (
        "bureaucratic-teostama",
        re.compile(r"\bteosta(?:ma|da|b|vad|s|sid|ti|tud|nud|mine|mise|mist|miseks|misel)\b", re.IGNORECASE),
        "'Teostama' on lõputöö tehnilises proosas sageli tühiverb.",
        "Kasuta täpsemat verbi, näiteks 'tegema', 'mõõtma', 'hindama' või 'rakendama'.",
    ),
    (
        "bureaucratic-labi-viima",
        re.compile(r"\bläbi\s+vi\w+\b", re.IGNORECASE),
        "'Läbi viima' on raskepärane tegusõnaühend.",
        "Kasuta konteksti järgi 'tegema', 'korraldama', 'mõõtma' või 'hindama'.",
    ),
    (
        "demonstrative-antud",
        re.compile(r"\bantud\b", re.IGNORECASE),
        "'Antud' kasutatakse sageli inglise 'given/this' mõjul.",
        "Kui mõte ei ole matemaatiliselt 'ette antud', kasuta 'see', 'käesolev' või nimeta objekt otse.",
    ),
    (
        "agent-poolt",
        re.compile(r"\b[A-Za-zÀ-ž-]+(?:\s+[A-Za-zÀ-ž-]+){0,2}\s+poolt\b", re.IGNORECASE),
        "'Poolt' konstruktsioon võib muuta lause kohmakaks.",
        "Muuda lause aktiivseks või kasuta omastavat vormi, näiteks 'kasutaja hinnang' mitte 'kasutaja poolt antud hinnang'.",
    ),
    (
        "vague-intensifier",
        re.compile(r"\b(väga|üsna|suhteliselt|päris|palju|natuke)\b", re.IGNORECASE),
        "Ebamäärane tugevussõna nõrgestab tehnilist väidet.",
        "Asenda mõõdetava väärtusega või eemalda, kui rõhutus ei kanna sisulist infot.",
    ),
    (
        "colloquial-paika-panema",
        re.compile(r"\bpaika\s+pan\w+\b", re.IGNORECASE),
        "'Paika panema' on lõputöö tehnilises stiilis kõnekeelne.",
        "Kasuta 'määrama', 'fikseerima', 'valima' või 'kehtestama'.",
    ),
)


DECIMAL_DOT_RE = re.compile(r"(?<![A-Za-z0-9_.-])\d+\.\d+(?![A-Za-z0-9_.-])")
WORD_RE = re.compile(r"[A-Za-zÀ-ž0-9]+(?:[-–][A-Za-zÀ-ž0-9]+)?")
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
            raw_without_comment = _strip_latex_comment(raw_line)
            prose = _strip_codeish(raw_without_comment)
            if not _is_prose_line(prose):
                continue

            for rule_id, pattern, message, suggestion in STYLE_RULES:
                if counts.get(rule_id, 0) >= MAX_PER_RULE:
                    continue
                if pattern.search(prose):
                    findings.append(_finding(rule_id, "warn", path, line_no, message, suggestion))
                    counts[rule_id] = counts.get(rule_id, 0) + 1
                    break

            if counts.get("decimal-dot", 0) < MAX_PER_RULE and _has_decimal_dot(prose, raw_without_comment):
                findings.append(
                    _finding(
                        "decimal-dot",
                        "info",
                        path,
                        line_no,
                        "Eestikeelses proosas kasutatakse kümnendkoma, mitte kümnendpunkti.",
                        "Kirjuta mõõtetulemused kujul '0,79'. Jäta punkt alles versioonides, failinimedes ja koodis.",
                    )
                )
                counts["decimal-dot"] = counts.get("decimal-dot", 0) + 1

            if counts.get("long-sentence", 0) < MAX_PER_RULE:
                word_count = _max_sentence_word_count(prose)
                if word_count > LONG_SENTENCE_WORDS:
                    findings.append(
                        _finding(
                            "long-sentence",
                            "info",
                            path,
                            line_no,
                            f"Lause või reavahetusega lõik on väga pikk ({word_count} sõna).",
                            "Jaga väide kaheks lauseks või tõsta kõrvalinfo eraldi lausesse.",
                        )
                    )
                    counts["long-sentence"] = counts.get("long-sentence", 0) + 1

            if len(findings) >= MAX_FINDINGS:
                return findings

    return findings


def _finding(rule_id: str, severity: str, path: str, line: int, message: str, suggestion: str) -> dict:
    return {
        "check": f"{CHECK_PREFIX}.{rule_id}",
        "severity": severity,
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
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    return text


def _is_prose_line(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if stripped.startswith(("\\begin", "\\end", "\\label", "\\includegraphics", "\\bibliography")):
        return False
    return bool(re.search(r"[A-Za-zÀ-ž]", stripped))


def _has_decimal_dot(prose: str, raw_line: str) -> bool:
    if not DECIMAL_DOT_RE.search(prose):
        return False
    if re.search(r"\\texttt\{|[/_.-][A-Za-z0-9_.-]*\d+\.\d+|\bv\d+\.\d+", raw_line):
        return False
    return True


def _is_english_abstract(path: str) -> bool:
    return path.endswith("misc/abstract-english.tex") or path.endswith("abstract-english.tex")


def _max_sentence_word_count(text: str) -> int:
    sentences = [part for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]
    if not sentences:
        return 0
    return max(len(WORD_RE.findall(sentence)) for sentence in sentences)
