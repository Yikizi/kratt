#!/usr/bin/env python3
"""Test full loop: user speech → LLM intent → mock HA execution → LLM response.

Simulates the complete voice pipeline (minus wake word and STT/TTS).
Uses Ollama for LLM and the mock HA MCP server for device control.

Usage:
    python test_loop.py "lülita tuli põlema"
    python test_loop.py  # interactive mode
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from typing import Optional

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma3:12b"

SYSTEM_PROMPT = """Sa oled Kratt, eestikeelne häälassistent. Juhi nutiseadmeid kasutaja käskude järgi.

Saadaolevad toimingud (vasta AINULT JSON-iga):
- {"action":"turn_on","entity_id":"...","color":"värv"} - seadme sisselülitamine (color valikuline, ainult lambid)
- {"action":"turn_off","entity_id":"..."} - seadme väljalülitamine
- {"action":"set_color","entity_id":"...","color":"värv"} - lambi värvi muutmine
- {"action":"set_brightness","entity_id":"...","brightness":0-255} - lambi heleduse muutmine
- {"action":"get_state","entity_id":"..."} - sensori/seadme oleku päring

Seadmed:
- light.elutuba — Elutoa lamp (RGB, heledus reguleeritav)
- light.magamistuba — Magamistoa lamp (RGB, heledus reguleeritav)
- switch.kohvimasin — Kohvimasin (sees/väljas)
- sensor.temperatuur — Toa temperatuuri andur
- sensor.kellaaeg — Praegune kellaaeg

Vasta ALATI selles JSON formaadis:
{"actions":[...],"response":"lühike eestikeelne vastus"}

Reeglid:
- Kui tuba pole täpsustatud, kasuta elutuba vaikimisi
- Kui kasutaja ütleb "kõik tuled", lisa mõlemad lambid actions listi
- response peab olema lühike, sest seda loetakse ette TTS-iga
- Ära hallutsinneeri seadmeid mida pole nimekirjas
- Kui ei saa aidata, {"actions":[],"response":"selgitus miks"}"""

# Start mock HA server as subprocess
_mcp_proc = None


def start_mcp_server():
    global _mcp_proc
    _mcp_proc = subprocess.Popen(
        [sys.executable, "tools/mock-ha-server/server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    # Initialize
    _send_mcp({"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {}})


def _send_mcp(request: dict) -> dict:
    _mcp_proc.stdin.write(json.dumps(request) + "\n")
    _mcp_proc.stdin.flush()
    line = _mcp_proc.stdout.readline()
    return json.loads(line) if line.strip() else {}


def execute_action(action: dict) -> str:
    """Execute a single action via MCP server."""
    name = action.get("action", "")
    args = {k: v for k, v in action.items() if k != "action"}
    resp = _send_mcp({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": name, "arguments": args},
    })
    result = resp.get("result", {})
    content = result.get("content", [{}])
    return content[0].get("text", "") if content else ""


def query_llm(user_text: str, tool_results: str | None = None) -> dict:
    """Send user text to LLM and get structured response."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
    ]
    if tool_results:
        messages.append({
            "role": "user",
            "content": f"Tööriistade tulemused: {tool_results}\nVasta nüüd kasutajale nende tulemuste põhjal.",
        })

    resp = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "stream": False,
        "format": "json",
        "messages": messages,
    })
    resp.raise_for_status()
    content = resp.json().get("message", {}).get("content", "{}")
    return json.loads(content)


def process_utterance(text: str):
    """Full pipeline: text → LLM → execute actions → final response."""
    print(f"\n{'='*50}")
    print(f"KASUTAJA: {text}")
    print(f"{'='*50}")

    # Step 1: LLM parses intent
    t0 = time.monotonic()
    parsed = query_llm(text)
    t_llm = time.monotonic() - t0
    print(f"\n[LLM] ({t_llm:.1f}s) Parsed: {json.dumps(parsed, ensure_ascii=False, indent=2)}")

    actions = parsed.get("actions", [])
    response = parsed.get("response", "")

    # Step 2: Execute actions via MCP
    tool_results = []
    for action in actions:
        t1 = time.monotonic()
        result = execute_action(action)
        t_action = time.monotonic() - t1
        tool_results.append(result)
        print(f"[MCP] ({t_action*1000:.0f}ms) {action.get('action')}: {result}")

    # Step 3: For get_state, we need a 2nd LLM call — real HA tools return
    # raw data (e.g. {"state": "21.5"}), not human-readable strings.
    # LLM must formulate a natural language response from the raw values.
    needs_data = any(a.get("action") == "get_state" for a in actions)
    if needs_data and tool_results:
        t2 = time.monotonic()
        final = query_llm(text, "\n".join(tool_results))
        t_llm2 = time.monotonic() - t2
        response = final.get("response", response)
        print(f"[LLM] ({t_llm2:.1f}s) Final response with tool data")

    # Step 4: Output
    print(f"\n🔊 KRATT: {response}")
    print(f"   Total: {time.monotonic() - t0:.1f}s")
    return {"response": response, "actions": actions, "latency": time.monotonic() - t0}


def main():
    start_mcp_server()

    if len(sys.argv) > 1:
        process_utterance(" ".join(sys.argv[1:]))
    else:
        print("Kratt voice pipeline test (type 'exit' to quit)")
        print("Simulates: wake word → STT → [this] → TTS")
        while True:
            try:
                text = input("\n> ").strip()
                if text.lower() in ("exit", "quit", "q"):
                    break
                if text:
                    process_utterance(text)
            except (EOFError, KeyboardInterrupt):
                break

    _mcp_proc.terminate()
    print("\nDone.")


if __name__ == "__main__":
    main()
