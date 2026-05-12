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

            if _threshold_tuned_on_test(lowered):
                _emit(
                    findings,
                    counts,
                    "4.methodology.threshold_tuned_on_test",
                    "error",
                    path,
                    line_no,
                    "Lävend või mudelivalik paistab olevat seotud test- või hindamiskogumiga.",
                    "Täpsusta, et lävend valiti arendus-/valideerimiskogumil ja testkogum jäi ainult lõpphindamiseks.",
                )

            if _train_eval_overlap(lowered):
                _emit(
                    findings,
                    counts,
                    "4.methodology.train_eval_overlap",
                    "warn",
                    path,
                    line_no,
                    "Sõnastus võib jätta mulje, et treening- ja hindamisandmed kattuvad.",
                    "Kui see kirjeldab ajaloolist ebaõnnestumist, hoia see selgelt õppetunnina; kui see kirjeldab lõpphindamist, täpsusta disjunktset jaotust.",
                )

            if _evaluated_on_training_data(lowered):
                _emit(
                    findings,
                    counts,
                    "4.methodology.evaluated_on_training_data",
                    "error",
                    path,
                    line_no,
                    "Hindamise sõnastus viitab treeningandmetel testimisele.",
                    "Kui see oli ainult sanity check, nimeta see nii; lõpptulemuste jaoks kasuta eraldi held-out kogumit.",
                )

            if _synthetic_or_augmented_eval_claim(lowered):
                _emit(
                    findings,
                    counts,
                    "4.methodology.synthetic_eval_claim",
                    "warn",
                    path,
                    line_no,
                    "Tulemusväide toetub sõnastuse järgi sünteetilistele või augmenteeritud andmetele.",
                    "Lisa, kas lõppjäreldus kinnitati päris kõne, kasutajatesti või eraldi held-out kogumiga.",
                )

            if _random_split_without_boundary(lowered):
                _emit(
                    findings,
                    counts,
                    "4.methodology.random_split_boundary",
                    "warn",
                    path,
                    line_no,
                    "Juhusliku jaotuse kirjeldus ei ütle, kas kõnelejad või allikad hoiti lahus.",
                    "Täpsusta speaker/source-disjoint reegel või põhjenda, miks klipipõhine jaotus oli piisav.",
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


def _threshold_tuned_on_test(line: str) -> bool:
    if not re.search(r"\b(lävend\w*|threshold\w*|otsustuslävend\w*)\b", line):
        return False
    if not re.search(r"\b(test\w*|hindamis\w*|evaluatsiooni\w*|eval\w*)\b", line):
        return False
    if not re.search(r"\b(valiti|seadistati|häälestati|optimeeriti|tuuniti|kalibreeriti|määrati)\b", line):
        return False
    return not re.search(r"\b(valideerimis\w*|validatsiooni\w*|arendus\w*|fikseeritud|eelnevalt|enne testimist)\b", line)


def _train_eval_overlap(line: str) -> bool:
    if not re.search(r"\b(treening\w*|õpetus\w*|train\w*)\b", line):
        return False
    if not re.search(r"\b(test\w*|hindamis\w*|eval\w*|valideerimis\w*)\b", line):
        return False
    if not re.search(r"\b(sama\w*|kattu\w*|nii\b.+\bkui ka\b|üht\w* ja sama)\b", line):
        return False
    return not re.search(
        r"\b(ei|mitte|väldi\w*|vältimi\w*|eraldi|lahus|disjunkt\w*|disjoint|kattuvuseta|tagab|kontroll\w*|assert_disjoint)\b",
        line,
    )


def _evaluated_on_training_data(line: str) -> bool:
    data_terms = r"(treeningand\w*|õpetusand\w*|treeningkomplekt\w*|treeningkogum\w*|training data|train set)"
    return bool(
        re.search(rf"\b(testiti|hinnati|mõõdeti|eval\w*)\b.{{0,60}}\b{data_terms}\b", line)
        or re.search(rf"\b{data_terms}\b.{{0,60}}\b(testiti|hinnati|mõõdeti|eval\w*)\b", line)
    )


def _synthetic_or_augmented_eval_claim(line: str) -> bool:
    if not re.search(r"\b(sünteetil\w*|tehis\w*|genereerit\w*|augment\w*(?:andme|klipi|kogum|test))\b", line):
        return False
    if not re.search(r"\b(tulemus\w*|täpsus\w*|recall\w*|faph\w*|valepositiiv\w*|saavutas\w*|hinnati|testiti)\b", line):
        return False
    return not re.search(r"\b(päris|reaal\w*|kasutaja\w*|held[- ]out|eraldi|testkogum\w*|common voice|dipco)\b", line)


def _random_split_without_boundary(line: str) -> bool:
    if not re.search(r"\b(juhuslik\w*|random\w*)\b", line):
        return False
    if not re.search(r"\b(jaot\w*|split\w*)\b", line):
        return False
    if not re.search(r"\b(test\w*|hindamis\w*|valideerimis\w*|eval\w*)\b", line):
        return False
    return not re.search(r"\b(kõneleja\w*|speaker\w*|allika\w*|source\w*|faili\w*|klipi\w*|disjunkt\w*|seed\w*)\b", line)
