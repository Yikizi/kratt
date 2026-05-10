from __future__ import annotations

import json
from typing import Any

from tools.demo_pipeline.llm_backends import DEFAULT_HELPER_RPC_TIMEOUT, get_pi_rpc_client
from tools.demo_pipeline.prompts import SYSTEM_PROMPT_HELPER_ASSISTANT

ConversationMessage = dict[str, str]


def _clean_text(value: Any, *, max_chars: int = 520) -> str:
    text = str(value or "").strip()
    if len(text) <= max_chars:
        return text
    # Prefer sentence boundaries over cutting a TTS response mid-word.
    kept: list[str] = []
    total = 0
    for part in text.replace("!", ".").replace("?", ".").split("."):
        sentence = part.strip()
        if not sentence:
            continue
        candidate = sentence + "."
        if total + len(candidate) + 1 > max_chars:
            break
        kept.append(candidate)
        total += len(candidate) + 1
    if kept:
        return " ".join(kept).strip()
    return text[: max_chars - 1].rstrip() + "…"


def _build_helper_prompt(messages: list[ConversationMessage]) -> str:
    return (
        "Allpool on lühike häälvestlus Kratt-assistendi ja kasutaja vahel. "
        "Vasta järgmise Kratti repliigiga JSON kujul.\n\n"
        "Vestlus JSONina:\n"
        f"{json.dumps(messages, ensure_ascii=False)}\n\n"
        "JSON skeem: {\"say\":\"eestikeelne kõnesõbralik vastus\","
        "\"ask_user\":null või \"küsimus kasutajale\",\"done\":true või false}.\n"
        "Kui vajad täpsustust, pane ask_user küsimuseks ja done=false. "
        "Kui vastus on valmis, pane ask_user=null ja done=true."
    )


def normalize_helper_result(raw: dict[str, Any]) -> dict[str, Any]:
    say = _clean_text(raw.get("say") or raw.get("response") or raw.get("answer"), max_chars=520)
    ask_user_raw = raw.get("ask_user") or raw.get("question")
    ask_user = _clean_text(ask_user_raw, max_chars=300) if ask_user_raw else None
    done = bool(raw.get("done", not ask_user))
    if ask_user:
        done = False
    if not say and ask_user:
        say = ask_user
    if not say:
        say = "Vabandust, ma ei saanud praegu head vastust."
        done = True
        ask_user = None
    return {"say": say, "ask_user": ask_user, "done": done}


def ask_helper_assistant(
    messages: list[ConversationMessage],
    *,
    timeout_s: float = DEFAULT_HELPER_RPC_TIMEOUT,
) -> dict[str, Any]:
    client = get_pi_rpc_client(SYSTEM_PROMPT_HELPER_ASSISTANT)
    return normalize_helper_result(client.request_json(_build_helper_prompt(messages), timeout_s=timeout_s))


def warm_helper_assistant(*, timeout_s: float = 20.0) -> dict[str, Any]:
    return ask_helper_assistant(
        [{"role": "user", "text": "Soojendus. Vasta ainult, et oled valmis."}],
        timeout_s=timeout_s,
    )
