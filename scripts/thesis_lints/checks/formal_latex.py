from __future__ import annotations

import re
from pathlib import Path

CHECK_PREFIX = "7.formal_latex"
MAX_TODO_FINDINGS = 12
MAX_REF_FINDINGS = 12
MAX_CAPTION_FINDINGS = 10

TODO_PATTERN = re.compile(
    r"\b(TODO|FIXME|XXX|TBD)\b|platsihoidj|Something Else|Something\b|lorem ipsum",
    re.IGNORECASE,
)
REF_COMMAND_PATTERN = re.compile(r"\\(?:ref|autoref|pageref|eqref)\{([^{}]*)\}")
CITE_COMMAND_PATTERN = re.compile(r"\\(?:cite|parencite|textcite|footcite)\*?(?:\[[^\]]*\]){0,2}\{([^{}]*)\}")
CAPTION_START_PATTERN = re.compile(r"\\caption(?:\[[^\]]*\])?\{")
LABEL_PATTERN = re.compile(r"\\label\{([^{}]+)\}")
FIGURE_BEGIN_PATTERN = re.compile(r"\\begin\{(figure|table|lstlisting)\}")


def run(document, context) -> list[dict]:
    findings: list[dict] = []
    findings.extend(_find_todo_markers(document))
    findings.extend(_find_empty_or_bad_refs(document))
    findings.extend(_find_caption_label_issues(document))
    findings.extend(_find_taltech_formal_issues(document))
    return findings


def _find_todo_markers(document) -> list[dict]:
    findings: list[dict] = []
    for file in _tex_files(document):
        for line_no, raw in enumerate(file.lines, start=1):
            line = _strip_latex_comment(raw)
            if _is_comment(line):
                continue
            if TODO_PATTERN.search(line):
                findings.append(_finding(
                    "todo-marker",
                    "error",
                    file,
                    line_no,
                    "Draft marker or placeholder text remains in the thesis source.",
                    "Remove the marker or replace it with final Estonian thesis prose.",
                ))
                if len(findings) >= MAX_TODO_FINDINGS:
                    return findings
    return findings


def _find_empty_or_bad_refs(document) -> list[dict]:
    findings: list[dict] = []
    labels = _collect_labels(document)
    seen: set[tuple[str, int, str]] = set()

    for file in _tex_files(document):
        for line_no, raw in enumerate(file.lines, start=1):
            line = _strip_latex_comment(raw)
            if _is_comment(line):
                continue
            for command, target in _iter_ref_like(line):
                target = target.strip()
                key = (str(_path(file)), line_no, f"{command}:{target}")
                if key in seen:
                    continue
                seen.add(key)
                if not target or "??" in target:
                    findings.append(_finding(
                        "empty-reference",
                        "error",
                        file,
                        line_no,
                        f"Empty or unresolved {command} target.",
                        "Point the reference to a concrete label or citation key.",
                    ))
                elif command == "ref" and target not in labels:
                    findings.append(_finding(
                        "missing-label",
                        "warn",
                        file,
                        line_no,
                        f"Reference target '{target}' has no matching \\label in the loaded thesis files.",
                        "Check for a typo or add the matching label near the referenced object.",
                    ))
                if len(findings) >= MAX_REF_FINDINGS:
                    return findings
    return findings


def _find_caption_label_issues(document) -> list[dict]:
    findings: list[dict] = []
    for file in _tex_files(document):
        blocks = _environment_blocks(file.lines)
        for env_name, start_line, block in blocks:
            if not CAPTION_START_PATTERN.search(block):
                if env_name in {"figure", "table"}:
                    findings.append(_finding(
                        "missing-caption",
                        "warn",
                        file,
                        start_line,
                        f"{env_name} environment has no caption.",
                        "Add a concise Estonian caption or move purely decorative content out of a floating environment.",
                    ))
            elif not LABEL_PATTERN.search(block):
                findings.append(_finding(
                    "caption-without-label",
                    "warn",
                    file,
                    start_line,
                    f"{env_name} caption has no label for stable cross-referencing.",
                    "Add \\label{fig:...}, \\label{tab:...}, or another consistent label after the caption.",
                ))

            for caption_line, caption in _iter_captions(block, start_line):
                words = _word_count(_strip_latex(caption))
                if words > 45:
                    findings.append(_finding(
                        "long-caption",
                        "info",
                        file,
                        caption_line,
                        f"Caption is about {words} words, which is likely too long for TalTech thesis formatting.",
                        "Move interpretation into body text and keep the caption descriptive.",
                    ))
            if len(findings) >= MAX_CAPTION_FINDINGS:
                return findings
    return findings


def _find_taltech_formal_issues(document) -> list[dict]:
    findings: list[dict] = []
    titlepage = _find_file(document, "titlepage.tex")
    declaration = _find_file(document, "authordeclaration.tex")
    main = _find_file(document, "main.tex")

    if titlepage and not re.search(r"TalTech|Tallinna\s+Tehnikaülikool", titlepage.text, re.IGNORECASE):
        findings.append(_finding(
            "taltech-titlepage",
            "error",
            titlepage,
            1,
            "Title page does not mention TalTech or Tallinna Tehnikaülikool.",
            "Keep the official university name visible on the title page.",
        ))

    if declaration and re.search(r"TODO|nimi|allkiri|kuupäev", declaration.text, re.IGNORECASE):
        findings.append(_finding(
            "author-declaration-placeholder",
            "warn",
            declaration,
            _first_match_line(declaration, r"TODO|nimi|allkiri|kuupäev"),
            "Author declaration may still contain placeholder signing fields.",
            "Verify that the final declaration matches the TalTech template requirements.",
        ))

    if main and "\\tableofcontents" not in main.text:
        findings.append(_finding(
            "missing-toc",
            "warn",
            main,
            1,
            "Main LaTeX file does not include \\tableofcontents.",
            "Confirm the table of contents is generated by the template or add it in the expected location.",
        ))

    return findings


def _iter_ref_like(line: str):
    for match in REF_COMMAND_PATTERN.finditer(line):
        yield "ref", match.group(1)
    for match in CITE_COMMAND_PATTERN.finditer(line):
        for target in match.group(1).split(","):
            yield "cite", target


def _collect_labels(document) -> set[str]:
    labels: set[str] = set()
    for file in _tex_files(document):
        labels.update(match.group(1).strip() for match in LABEL_PATTERN.finditer(file.text))
    return labels


def _environment_blocks(lines: list[str]) -> list[tuple[str, int, str]]:
    blocks: list[tuple[str, int, str]] = []
    i = 0
    while i < len(lines):
        begin = FIGURE_BEGIN_PATTERN.search(lines[i])
        if not begin:
            i += 1
            continue
        env_name = begin.group(1)
        start = i + 1
        end_pattern = re.compile(rf"\\end\{{{re.escape(env_name)}\}}")
        block_lines = [lines[i]]
        i += 1
        while i < len(lines):
            block_lines.append(lines[i])
            if end_pattern.search(lines[i]):
                break
            i += 1
        blocks.append((env_name, start, "\n".join(block_lines)))
        i += 1
    return blocks


def _iter_captions(block: str, block_start_line: int):
    for match in CAPTION_START_PATTERN.finditer(block):
        start = match.start()
        balance = 0
        end = match.end()
        for idx in range(match.end() - 1, len(block)):
            char = block[idx]
            if char == "{":
                balance += 1
            elif char == "}":
                balance -= 1
                if balance == 0:
                    end = idx + 1
                    break
        line_no = block_start_line + block[:start].count("\n")
        yield line_no, block[match.end(): end - 1]


def _tex_files(document):
    return [file for file in document.files if str(_path(file)).endswith(".tex")]


def _find_file(document, name: str):
    for file in document.files:
        if Path(str(_path(file))).name == name:
            return file
    return None


def _path(file) -> str:
    return str(getattr(file, "rel_path", getattr(file, "path", "")))


def _is_comment(line: str) -> bool:
    return line.lstrip().startswith("%")


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


def _first_match_line(file, pattern: str) -> int:
    regex = re.compile(pattern, re.IGNORECASE)
    for idx, line in enumerate(file.lines, start=1):
        if regex.search(line):
            return idx
    return 1


def _strip_latex(text: str) -> str:
    text = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?(?:\{([^{}]*)\})?", r" \1 ", text)
    return re.sub(r"[$\\{}_^&%#~]", " ", text)


def _word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-zÀ-ž0-9]+(?:[-–][A-Za-zÀ-ž0-9]+)?", text))


def _finding(check: str, severity: str, file, line: int, message: str, suggestion: str) -> dict:
    return {
        "check": f"{CHECK_PREFIX}.{check}",
        "severity": severity,
        "path": _path(file),
        "line": int(line),
        "message": message,
        "suggestion": suggestion,
    }
