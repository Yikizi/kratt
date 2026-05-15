from __future__ import annotations

import re

# Kiirkirjutaja sometimes hears "kustu" as "vastu" in short light-off
# commands. "Pane tuli vastu" is not a meaningful smart-home command, so for
# the demo parser we canonicalize only this narrow light-command pattern.
_LIGHT_OBJECT_RE = r"(?:tuli|tuld|tuled?|lambid?|lamp|valgus|pirnid?|pirn)"
_PANE_LIGHT_VASTU_RE = re.compile(
    rf"\b(pane)\s+({_LIGHT_OBJECT_RE})\s+vastu\b",
    flags=re.IGNORECASE,
)
_NEGATED_PANE_LIGHT_VASTU_RE = re.compile(
    rf"\bära\s+pane\s+{_LIGHT_OBJECT_RE}\s+vastu\b",
    flags=re.IGNORECASE,
)


def normalize_stt_artifacts(text: str) -> str:
    """Canonicalize known STT artifacts before intent parsing.

    Keeps the original transcript available for telemetry/UI, but lets the LLM
    see the intended command.
    """
    normalized = (text or "").strip()
    if not normalized:
        return normalized
    if _NEGATED_PANE_LIGHT_VASTU_RE.search(normalized):
        return normalized
    normalized = _PANE_LIGHT_VASTU_RE.sub(lambda m: f"{m.group(1)} {m.group(2)} kustu", normalized)
    return normalized
