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
    "Mu põhitöö on WiZ lamp: sisse ja välja, värvid, soe või külm valge, heledus, olek, disko, värvide läbikäimine ja vilgutamine. Lisaks ütlen kellaaega, kuupäeva ja ilma, ka homse või ülehomse kohta.",
    "Ma oskan praegu juhtida valgust: põlema, kustu, värv, heledus, olek ja lühikesed efektid nagu disko või vilgutamine. Veel oskan öelda kellaaega, kuupäeva, ilma ja vajadusel küsida abimudelilt lühikest nõu.",
    "Valgustus on minu koduväljak: värvid, heledus, soe ja külm valge, olek ning efektid. Kõrvalt oskan vastata aja, kuupäeva ja ilma kohta ning üldküsimuse puhul saan targema mudeli appi kutsuda.",
]

AIRFRYER_CAPABILITY_RESPONSES = [
    "Selles režiimis juhin õhufritüüri: saan küpsetamise käivitada temperatuuri ja ajaga, peatada ning olekut vaadata.",
    "Praegu olen õhufritüüri kratt. Ütle toit või temperatuur ja minutid, ning saan küpsetamise käivitada, peatada või olekut kontrollida.",
]

SMARTHOME_CAPABILITY_RESPONSES = [
    "Saan juhtida WiZ lampi: sisse, välja, värv, heledus ja efektid. Lisaks saan õhufritüüri käivitada temperatuuri ja ajaga, peatada ning olekut vaadata.",
    "Praegu oskan nii lampi kui õhufritüüri: valguse värvid, heledus ja efektid; õhufritüüril küpsetamine, stopp ja staatus. Lisaks ütlen kellaaega, kuupäeva ja ilma.",
]

CLARIFY_COLOR_QUESTIONS = [
    "Mis värvi ma ta keeran?",
    "Ütle värv ja ma teen ära.",
    "Mis toon sobib?",
    "Millist värvi sa tahad?",
]


def holding_phrase(transcript: str | None = None) -> str:
    return choose_variant(HELPER_HOLDING_PHRASES, "holding", transcript)


def capabilities_response(turn_seq: int = 0, *, mode: str = "lights") -> str:
    if mode == "smarthome":
        return choose_variant(SMARTHOME_CAPABILITY_RESPONSES, "capabilities_smarthome", turn_seq)
    if mode == "airfryer":
        return choose_variant(AIRFRYER_CAPABILITY_RESPONSES, "capabilities_airfryer", turn_seq)
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
    if mode == "forecast":
        prefixes = ["Ennustuse järgi:", "Selle päeva kohta:", "Ilmateade ütleb:"]
        return f"{choose_variant(prefixes, text, turn_seq)} {text}"
    # Current weather is already compact; only avoid every answer starting identically.
    prefixes = ["Praegu on nii:", "Ilm ütleb praegu:", "Väljas paistab nii:"]
    return f"{choose_variant(prefixes, text, turn_seq)} {text}"
