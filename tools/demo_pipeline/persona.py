from __future__ import annotations

import hashlib
import random
from typing import Any


def _rng(*parts: Any) -> random.Random:
    seed = "|".join(str(p) for p in parts if p is not None)
    digest = hashlib.blake2s(seed.encode("utf-8"), digest_size=8).digest()
    return random.Random(int.from_bytes(digest, "big"))


def choose_variant(variants: list[str], *seed_parts: Any) -> str:
    if not variants:
        return ""
    return _rng(*seed_parts).choice(variants)


HELPER_HOLDING_PHRASES = [
    "See on juba targema krati töö. Küsin korra abi.",
    "Üks hetk, ma kutsun suurema aju appi.",
    "See vajab natuke rohkem mõtlemist. Ma küsin abi.",
    "Ma ei hakka siin puusalt pakkuma. Küsin targemalt mudelilt.",
]

CAPABILITY_RESPONSES = [
    "Kõige paremini oskan ma lampi kamandada: värvid, heledus, sisse-välja ja väike disko. Lisaks ütlen ilma ja kellaaega ning keerulisemate küsimuste jaoks saan suurema mudeli appi kutsuda.",
    "Ma olen praegu eeskätt valguse kratt: panen tule põlema, muudan värvi, timmin heledust ja teen efekte. Boonusena oskan ilma, kuupäeva ja kellaaega öelda ning üldisemate küsimuste puhul abi küsida.",
    "Valgustus on minu koduväljak: värvid, heledus, olek ja efektid. Kui küsid midagi muud, näiteks retsepti või nõu, saan selleks targema mudeli käest abi paluda.",
]

CLARIFY_COLOR_QUESTIONS = [
    "Mis värvi ma ta keeran?",
    "Ütle värv ja ma teen ära.",
    "Mis toon sobib?",
    "Millist värvi sa tahad?",
]


def holding_phrase(transcript: str | None = None) -> str:
    return choose_variant(HELPER_HOLDING_PHRASES, "holding", transcript)


def capabilities_response(turn_seq: int = 0) -> str:
    return choose_variant(CAPABILITY_RESPONSES, "capabilities", turn_seq)


def color_clarification(transcript: str | None = None) -> str:
    return choose_variant(CLARIFY_COLOR_QUESTIONS, "color_clarify", transcript)


def soften_weather_response(response: str, *, mode: str = "current", turn_seq: int = 0) -> str:
    """Small persona layer for deterministic weather tool results.

    The weather tool still computes facts; this only changes the spoken wrapper.
    """
    text = (response or "").strip()
    if not text:
        return text
    mode = (mode or "current").strip().lower()
    if mode == "rain":
        prefixes = ["Vihma mõttes:", "Saju kohta:", "Kui vihma kardad, siis"]
        return f"{choose_variant(prefixes, text, turn_seq)} {text}"
    if mode == "clothing":
        prefixes = ["Riietuse mõttes ütleks nii:", "Mina paneks nii:", "Õue minnes arvestaks sellega:"]
        return f"{choose_variant(prefixes, text, turn_seq)} {text}"
    # Current weather is already compact; only avoid every answer starting identically.
    prefixes = ["Praegu on nii:", "Ilm ütleb praegu:", "Väljas paistab nii:"]
    return f"{choose_variant(prefixes, text, turn_seq)} {text}"
