from __future__ import annotations

import re

CHECK_PREFIX = "8.readability"
MAX_LONG_SENTENCES = 14
MAX_DENSE_PARAGRAPHS = 8
MAX_DUPLICATES = 10
MAX_FILLER = 10

FILLER_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(?:väga|üpris|suhteliselt|päris|üsna)\s+(?:oluline|hea|halb|suur|väike|keeruline)\b", re.IGNORECASE), "Replace vague intensity with a concrete measurement or remove it."),
    (re.compile(r"\b(?:erinevad|mitmed|paljud|mõned)\s+(?:asjad|tegurid|probleemid|võimalused)\b", re.IGNORECASE), "Name the factors directly or compress the phrase."),
    (re.compile(r"\b(?:antud|käesolev)\s+(?:töö|peatükk|lahendus|mudel)\b", re.IGNORECASE), "Prefer the direct noun unless the distinction is needed."),
    (re.compile(r"\b(?:oluline on märkida|tasub mainida|võib öelda),?\s+et\b", re.IGNORECASE), "Start with the claim itself."),
]
SENTENCE_END_PATTERN = re.compile(r"[\.\?!](?:\s|$)")


def run(document, context) -> list[dict]:
    findings: list[dict] = []
    findings.extend(_find_long_sentences(document))
    findings.extend(_find_dense_paragraphs(document))
    findings.extend(_find_duplicate_phrases(document))
    findings.extend(_find_filler_phrases(document))
    return findings


def _find_long_sentences(document) -> list[dict]:
    findings: list[dict] = []
    for file in _tex_files(document):
        for line_no, sentence in _iter_sentences(file):
            clean = _plain_text(sentence)
            words = _word_count(clean)
            if words > 42:
                findings.append(_finding(
                    "long-sentence",
                    "warn",
                    file,
                    line_no,
                    f"Sentence is about {words} words, which is hard to read in Estonian technical prose.",
                    "Split the sentence or move one qualifier into the previous/next sentence.",
                ))
                if len(findings) >= MAX_LONG_SENTENCES:
                    return findings
    return findings


def _find_dense_paragraphs(document) -> list[dict]:
    findings: list[dict] = []
    for file in _tex_files(document):
        for line_no, paragraph in _iter_paragraphs(file):
            clean = _plain_text(paragraph)
            words = _word_count(clean)
            sentence_count = max(1, len(list(_sentence_endings(clean))))
            if words > 145 or (words > 95 and sentence_count <= 2):
                findings.append(_finding(
                    "dense-paragraph",
                    "info",
                    file,
                    line_no,
                    f"Paragraph is dense: about {words} words across {sentence_count} sentence(s).",
                    "Break it into two paragraphs or make the paragraph's topic sentence explicit.",
                ))
                if len(findings) >= MAX_DENSE_PARAGRAPHS:
                    return findings
    return findings


def _find_duplicate_phrases(document) -> list[dict]:
    phrase_locations: dict[str, list[tuple[object, int]]] = {}
    for file in _tex_files(document):
        for line_no, paragraph in _iter_paragraphs(file):
            words = [word.lower() for word in re.findall(r"[A-Za-zÀ-ž]{4,}", _plain_text(paragraph))]
            for idx in range(0, len(words) - 3):
                phrase = " ".join(words[idx: idx + 4])
                if _is_low_value_phrase(phrase):
                    continue
                phrase_locations.setdefault(phrase, []).append((file, line_no))

    findings: list[dict] = []
    for phrase, locations in phrase_locations.items():
        unique_locations = _unique_locations(locations)
        if len(unique_locations) < 2:
            continue
        file, line_no = unique_locations[1]
        findings.append(_finding(
            "duplicate-phrase",
            "info",
            file,
            line_no,
            f"Phrase repeated in nearby thesis prose: '{phrase}'.",
            "Keep repeated framing only when it carries a deliberate term; otherwise compress or vary the sentence.",
        ))
        if len(findings) >= MAX_DUPLICATES:
            break
    return findings


def _find_filler_phrases(document) -> list[dict]:
    findings: list[dict] = []
    for file in _tex_files(document):
        for line_no, raw in enumerate(file.lines, start=1):
            line = _strip_latex_comment(raw)
            if _skip_line(line):
                continue
            clean = _plain_text(line)
            for pattern, suggestion in FILLER_PATTERNS:
                if pattern.search(clean):
                    findings.append(_finding(
                        "filler-phrase",
                        "info",
                        file,
                        line_no,
                        "Phrase is likely wordy or imprecise.",
                        suggestion,
                    ))
                    break
            if len(findings) >= MAX_FILLER:
                return findings
    return findings


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
        if SENTENCE_END_PATTERN.search(joined):
            parts = re.split(r"(?<=[\.\?!])\s+", joined)
            for sentence in parts[:-1]:
                yield start_line, sentence
            buffer = [parts[-1]] if parts[-1] else []
            start_line = line_no
    if buffer:
        yield start_line, " ".join(buffer)


def _iter_paragraphs(file):
    buffer: list[str] = []
    start_line = 1
    for line_no, raw in enumerate(file.lines, start=1):
        line = _strip_latex_comment(raw)
        stripped = line.strip()
        if _skip_line(line) or stripped == "":
            if buffer:
                yield start_line, " ".join(buffer)
                buffer = []
            continue
        if not buffer:
            start_line = line_no
        buffer.append(stripped)
    if buffer:
        yield start_line, " ".join(buffer)


def _sentence_endings(text: str):
    return SENTENCE_END_PATTERN.finditer(text)


def _unique_locations(locations: list[tuple[object, int]]) -> list[tuple[object, int]]:
    seen: set[tuple[str, int]] = set()
    unique: list[tuple[object, int]] = []
    for file, line_no in locations:
        key = (_path(file), line_no)
        if key not in seen:
            seen.add(key)
            unique.append((file, line_no))
    return unique


def _is_low_value_phrase(phrase: str) -> bool:
    stop_phrases = (
        "selle töö eesmärk on",
        "käesoleva töö eesmärk on",
        "on toodud joonisel",
        "on esitatud tabelis",
    )
    return phrase in stop_phrases or len(set(phrase.split())) < 4


def _tex_files(document):
    return [file for file in document.files if _path(file).endswith(".tex")]


def _skip_line(line: str) -> bool:
    stripped = line.strip()
    return (
        not stripped
        or stripped.startswith("%")
        or stripped.startswith("\\")
        or stripped.startswith(r"\item")
    )


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
