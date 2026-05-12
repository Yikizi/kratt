from __future__ import annotations


CONFIDENCE_VALUE = {
    "high": 3,
    "medium": 2,
    "low": 1,
}

EFFORT_VALUE = {
    "tiny": 3,
    "small": 2,
    "review": 1,
}

IMPACT_VALUE = {
    "submission": 4,
    "defense": 3,
    "clarity": 2,
    "polish": 1,
}


HIGH_CONFIDENCE_PREFIXES = (
    "1.terminology.english-",
    "1.terminology.split-",
    "2.estonian_style.english-gloss",
    "2.estonian_style.bureaucratic-",
    "7.formal_latex.todo-marker",
    "7.formal_latex.empty-reference",
    "7.formal_latex.missing-label",
)

NOISY_PREFIXES = (
    "8.readability.duplicate-phrase",
    "9.narrative.thin-section-opening",
    "2.estonian_style.vague-intensifier",
    "8.readability.filler-phrase",
)

DEFENSE_PREFIXES = (
    "3.claim_evidence.",
    "4.methodology.",
    "5.scope.",
    "6.defense_risk.",
    "9.narrative.unsupported-absolute-claim",
)


def rank_finding(finding: dict) -> dict:
    check = str(finding.get("check", ""))
    severity = str(finding.get("severity", "warn"))

    confidence = "medium"
    impact = "clarity"
    effort = "small"
    reason = "Heuristic lint finding; review the local sentence before editing."

    if check.startswith(HIGH_CONFIDENCE_PREFIXES):
        confidence = "high"
        impact = "clarity"
        effort = "tiny"
        reason = "Concrete pattern with an established local replacement or formal rule."
    elif check.startswith(DEFENSE_PREFIXES):
        confidence = "medium"
        impact = "defense"
        effort = "review"
        reason = "Potential defense or evidence risk; may be real, but needs context before editing."
    elif check.startswith(NOISY_PREFIXES):
        confidence = "low"
        impact = "polish"
        effort = "review"
        reason = "Noisy prose heuristic; useful for review, not an automatic fix."
    elif check.startswith("7.formal_latex.long-caption"):
        confidence = "high"
        impact = "polish"
        effort = "small"
        reason = "Caption length is directly measurable; shorten if it does not carry required evidence."
    elif check.startswith("8.readability.long-sentence"):
        confidence = "medium"
        impact = "clarity"
        effort = "small"
        reason = "Long sentence is measurable, but splitting must preserve claim and citation scope."
    elif check.startswith("10.ethics."):
        confidence = "medium"
        impact = "submission"
        effort = "review"
        reason = "Ethics/privacy risk is high impact, but nearby context must be inspected."

    if severity == "error":
        impact = "submission"
        confidence = "high" if confidence != "low" else "medium"

    score = (
        CONFIDENCE_VALUE[confidence] * 30
        + IMPACT_VALUE[impact] * 15
        + EFFORT_VALUE[effort] * 5
    )

    enriched = dict(finding)
    enriched.update(
        {
            "rank_score": score,
            "confidence": confidence,
            "impact": impact,
            "fix_effort": effort,
            "rank_reason": reason,
        }
    )
    return enriched


def rank_findings(findings: list[dict]) -> list[dict]:
    ranked = [rank_finding(item) for item in findings]
    return sorted(
        ranked,
        key=lambda item: (
            -int(item["rank_score"]),
            item["path"],
            int(item["line"]),
            item["check"],
        ),
    )
