from __future__ import annotations

import re

MAX_PER_CHECK = 4


def run(document, context) -> list[dict]:
    findings: list[dict] = []
    counts: dict[str, int] = {}

    for thesis_file in getattr(document, "files", []):
        path = _path(thesis_file)
        for line_no, raw_line in enumerate(_lines(thesis_file), start=1):
            line = _strip_latex_comment(raw_line).strip()
            if not line:
                continue
            lowered = line.lower()

            if _production_ready_claim(lowered):
                _emit(
                    findings,
                    counts,
                    "5.scope.production_ready_claim",
                    "error",
                    path,
                    line_no,
                    "Väide kõlab tootmisvalmiduse või püsiva töökindluse lubadusena.",
                    "Piira sõnastus prototüübi, demokandidaadi või mõõdetud katseseadistuse tasemele.",
                )

            if _full_voice_assistant_scope(lowered):
                _emit(
                    findings,
                    counts,
                    "5.scope.full_voice_assistant_scope",
                    "warn",
                    path,
                    line_no,
                    "Sõnastus laiendab töö äratussõnalt terviklikule häälassistendile.",
                    "Rõhuta, et põhikomponent on eestikeelne äratussõna ja ülejäänu on integratsiooni-/demokeskkond.",
                )

            if _overbroad_smart_home_solution(lowered):
                _emit(
                    findings,
                    counts,
                    "5.scope.overbroad_solution_claim",
                    "warn",
                    path,
                    line_no,
                    "Väide esitab töö liiga laia nutikodu või keeletoe lahendusena.",
                    "Sõnasta panus kitsamalt: kohalik äratussõna, hindamisprotokoll ja prototüüpne Home Assistant integratsioon.",
                )

            if _universal_environment_claim(lowered):
                _emit(
                    findings,
                    counts,
                    "5.scope.universal_environment_claim",
                    "warn",
                    path,
                    line_no,
                    "Üldistus kõigile kasutajatele, seadmetele või keskkondadele on kaitsmisel riskantne.",
                    "Seo väide konkreetsete testitud seadmete, kõnelejate, andmekogude või ruumitingimustega.",
                )

            if _stt_tts_development_claim(lowered):
                _emit(
                    findings,
                    counts,
                    "5.scope.stt_tts_development_claim",
                    "warn",
                    path,
                    line_no,
                    "Sõnastus võib jätta mulje, et töö arendas ka STT/TTS põhisüsteeme.",
                    "Kui STT/TTS kasutati valmis komponendina, sõnasta see integratsiooni või sõltuvusena.",
                )

    return findings


def _path(thesis_file) -> str:
    return str(getattr(thesis_file, "rel_path", None) or getattr(thesis_file, "path", ""))


def _lines(thesis_file) -> list[str]:
    lines = getattr(thesis_file, "lines", None)
    if lines is not None:
        return list(lines)
    return str(getattr(thesis_file, "text", "")).splitlines()


def _strip_latex_comment(line: str) -> str:
    return re.split(r"(?<!\\)%", line, maxsplit=1)[0]


def _emit(
    findings: list[dict],
    counts: dict[str, int],
    check: str,
    severity: str,
    path: str,
    line: int,
    message: str,
    suggestion: str,
) -> None:
    if counts.get(check, 0) >= MAX_PER_CHECK:
        return
    counts[check] = counts.get(check, 0) + 1
    findings.append(
        {
            "check": check,
            "severity": severity,
            "path": path,
            "line": line,
            "message": message,
            "suggestion": suggestion,
        }
    )


def _production_ready_claim(line: str) -> bool:
    return bool(
        re.search(
            r"\b(tootmisvalmis|production[- ]ready|tootmiskasutuse\w* valmis|valmis tootmisse|"
            r"päris kasutuses töökind\w*|igapäevaseks kasutuseks valmis|stabiilne lõpplahendus)\b",
            line,
        )
    )


def _full_voice_assistant_scope(line: str) -> bool:
    if not re.search(r"\b(täielik\w*|terviklik\w*|end[- ]to[- ]end|täisfunktsionaal\w*)\b", line):
        return False
    return bool(re.search(r"\b(häälassist\w*|voice assistant\w*|nutiabil\w*)\b", line))


def _overbroad_smart_home_solution(line: str) -> bool:
    if re.search(r"\b(äratussõna|wake word|prototüüp\w*|demonstratsioo\w*|katse\w*)\b", line):
        return False
    return bool(
        re.search(
            r"\b(lahendab|võimaldab täielikult|katab kogu|asendab)\b.{0,80}"
            r"\b(eestikeel\w* hääljuhtimi\w*|nuttikodu|nutikodu|häälassist\w*|voice assistant\w*)\b",
            line,
        )
    )


def _universal_environment_claim(line: str) -> bool:
    universal_target = (
        r"\b(kõik\w*|iga\w*|universaal\w*|mistahes|ükskõik mill\w*)\b.{0,40}"
        r"\b(kasutaja\w*|seadme\w*|keskkonna\w*|ruumi\w*|aktsendi\w*|müra\w*)\b"
    )
    target_universal = (
        r"\b(kasutaja\w*|seadme\w*|keskkonna\w*|ruumi\w*|aktsendi\w*|müra\w*)\b.{0,40}"
        r"\b(kõik\w*|universaal\w*|mistahes|ükskõik mill\w*)\b"
    )
    if not (re.search(universal_target, line) or re.search(target_universal, line)):
        return False
    return not re.search(r"\b(osaleja|katse|klipp|fail|wav|rida|tabel)\w*\b", line)


def _stt_tts_development_claim(line: str) -> bool:
    if re.search(r"\b(integreer\w*|kasutab|kasutati|valmis|olemasolev\w*|kiirkirjutaja)\b", line):
        return False
    return bool(
        re.search(r"\b(arendas\w*|loodi|treeniti|realiseeriti)\b.{0,70}\b(kõnetuvastus\w*|stt\b|kõnesüntees\w*|tts\b)\b", line)
    )
