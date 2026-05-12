from __future__ import annotations

import re

MAX_PER_CHECK = 4


def run(document, context) -> list[dict]:
    findings: list[dict] = []
    counts: dict[str, int] = {}
    results_have_limitations = _results_have_limitations(document)

    for thesis_file in getattr(document, "files", []):
        path = _path(thesis_file)
        intro_like = _is_intro_like_path(path)

        for line_no, raw_line in enumerate(_lines(thesis_file), start=1):
            line = _strip_latex_comment(raw_line).strip()
            if not line:
                continue
            lowered = line.lower()

            if _unsupported_superlative(lowered):
                _emit(
                    findings,
                    counts,
                    "6.defense_risk.unsupported_superlative",
                    "warn",
                    path,
                    line_no,
                    "Superlatiiv või uudsusväide vajab kaitsmisel väga täpset tõenduspiiri.",
                    "Lisa allikas/piirang või pehmenda väide kujule 'teadaolevalt', 'üks esimesi' või 'antud võrdluses'.",
                )

            if _absolute_proof_language(lowered):
                _emit(
                    findings,
                    counts,
                    "6.defense_risk.absolute_proof_language",
                    "warn",
                    path,
                    line_no,
                    "Absoluutne tõestus- või garantiisõnastus kutsub komisjonilt vastunäiteid.",
                    "Asenda mõõdetud, piiratud väitega: 'tulemused viitavad', 'katse näitas' või 'antud seadistuses'.",
                )

            if _process_excuse_or_agent_language(lowered):
                _emit(
                    findings,
                    counts,
                    "6.defense_risk.process_excuse",
                    "warn",
                    path,
                    line_no,
                    "See kõlab protsessivabanduse või töökorralduse päevikuna, mitte akadeemilise järeldusena.",
                    "Sõnasta piirang metoodilise riskina ja lisa, kuidas seda mõõdeti või maandati.",
                )

            if _vague_quality_judgment(lowered):
                _emit(
                    findings,
                    counts,
                    "6.defense_risk.vague_quality_judgment",
                    "warn",
                    path,
                    line_no,
                    "Ebamäärane kvaliteedihinnang on kaitsmisel nõrk ilma mõõdikuta.",
                    "Seo hinnang FAPH, recall'i, kasutajatesti tulemuse või konkreetse kvalitatiivse vaatlusega.",
                )

            if intro_like and results_have_limitations and _strong_intro_success_claim(lowered):
                _emit(
                    findings,
                    counts,
                    "6.defense_risk.intro_vs_results",
                    "warn",
                    path,
                    line_no,
                    "Sissejuhatus/kokkuvõte kõlab tugevamalt kui tulemuste teadaolevad piirangud.",
                    "Joonda sissejuhatav väide tulemuste osaga: prototüüp, mõõdetud piirangud ja mitte tootmisvalmidus.",
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


def _is_intro_like_path(path: str) -> bool:
    lowered = path.lower()
    return bool(
        re.search(
            r"(abstract|kokkuv[õo]te|sissejuhatus|introduction|ylesandepystitus|ülesandepüstitus|first_chapter)",
            lowered,
        )
    )


def _results_have_limitations(document) -> bool:
    limitation_re = re.compile(
        r"\b(ei saavutanud|ei ole tootmisvalmis|piirang\w*|nõrk\w*|ebaõnnest\w*|"
        r"valepositiiv\w*|false positive\w*|prefiks\w*|prefix\w*|segadusfraas\w*|confusable\w*)\b",
        re.IGNORECASE,
    )
    result_path_re = re.compile(r"(third|fourth|fifth|tulem|result|arutelu|discussion|j[aä]reld)", re.IGNORECASE)
    for thesis_file in getattr(document, "files", []):
        path = _path(thesis_file)
        if result_path_re.search(path) and limitation_re.search(getattr(thesis_file, "text", "")):
            return True
    return False


def _unsupported_superlative(line: str) -> bool:
    if re.search(
        r"\b(igas reas|tabel|caption|esimene reaalajas test|esimesed tulemused|esialgsed tulemused|ei ole üheselt parim)\b",
        line,
    ):
        return False
    if re.search(r"\b(teadaolevalt|üks esimesi|üks parimaid|antud võrdluses|fikseeritud|mõõdetud|piiratud)\b", line):
        return False
    novelty_claim = re.search(
        r"\b(esimes\w*|ains\w*|unikaal\w*)\b.{0,50}\b(eestikeel\w*|eesti\b|avalik\w*|äratussõna\w*|wake word\w*)\b",
        line,
    ) or re.search(
        r"\b(eestikeel\w*|eesti\b|avalik\w*|äratussõna\w*|wake word\w*)\b.{0,50}\b(esimes\w*|ains\w*|unikaal\w*)\b",
        line,
    )
    if re.search(r"\b(ei ole|pole|mitte)\b.{0,30}\b(parim|madalaim|suurim|kõige parem|kõige täpsem)\b", line):
        return bool(novelty_claim)
    best_claim = re.search(
        r"\b(parim|kõige parem|kõige täpsem|madalaim|suurim)\b.{0,40}\b(mudel\w*|lahendus\w*|süsteem\w*|tulemus\w*|faph\w*|recall\w*)\b",
        line,
    ) or re.search(
        r"\b(mudel\w*|lahendus\w*|süsteem\w*|tulemus\w*)\b.{0,40}\b(parim|kõige parem|kõige täpsem|madalaim|suurim)\b",
        line,
    )
    return bool(novelty_claim or best_claim)


def _absolute_proof_language(line: str) -> bool:
    return bool(
        re.search(
            r"\b(tõestab lõplikult|tõestati täielikult|garanteerib|tagab alati|kahtlemata|vaieldamatult|"
            r"ilmselgelt|on selge, et|täielikult kõrvaldab)\b",
            line,
        )
    )


def _process_excuse_or_agent_language(line: str) -> bool:
    return bool(
        re.search(
            r"\b(ei olnud aega|ei jõudnud|jäi tegemata|kiirustades|agent tegi|llm kirjutas|"
            r"chatgpt|claude|codex)\b",
            line,
        )
    )


def _vague_quality_judgment(line: str) -> bool:
    if re.search(r"\b(faph|recall|täpsus|protsent|%|valepositiiv|valenegatiiv|kasutajatest)\b", line):
        return False
    return bool(re.search(r"\b(päris hea|väga hea|suhteliselt hea|normaalne|rahuldav|piisavalt hea|toimib hästi)\b", line))


def _strong_intro_success_claim(line: str) -> bool:
    return bool(
        re.search(
            r"\b(tootmisvalmis|töökindel|lahendab|valmis kasutamiseks|saavutas\w*|edukalt realiseeriti|"
            r"terviklik\w* häälassist\w*|täielik\w* lahendus)\b",
            line,
        )
    )
