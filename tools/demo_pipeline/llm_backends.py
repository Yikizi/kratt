from __future__ import annotations

import json
import os
import re
import select
import shutil
import subprocess
import threading
import time
import uuid
from typing import Any

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_KEEP_ALIVE = os.getenv("KRATT_OLLAMA_KEEP_ALIVE", "1h")
OLLAMA_REQUEST_TIMEOUT = float(os.getenv("KRATT_OLLAMA_REQUEST_TIMEOUT", "20"))
OLLAMA_JSON_OPTIONS = {"temperature": 0, "num_predict": 80}
OLLAMA_SESSION = requests.Session()
DEFAULT_LLM_MODEL = "qwen2.5:7b"
DEFAULT_PI_MODEL = "openai-codex/gpt-5.3-codex-spark"
DEFAULT_PI_THINKING = "minimal"
DEFAULT_PI_RPC_TIMEOUT = 8.0
DEFAULT_HELPER_RPC_TIMEOUT = float(os.getenv("KRATT_HELPER_RPC_TIMEOUT", "45"))

LLM_MODEL = DEFAULT_LLM_MODEL
PI_MODEL = DEFAULT_PI_MODEL
PI_THINKING = DEFAULT_PI_THINKING
PI_RESET_EACH_TURN = False
PI_RPC_TIMEOUT = DEFAULT_PI_RPC_TIMEOUT
USE_CLAUDE_CODE = False
USE_PI_CLI = False
PI_RPC_CLIENTS: dict[str, "PiRpcClient"] = {}
PI_RPC_CLIENTS_LOCK = threading.Lock()
CLAUDE_SESSION_ID = str(uuid.uuid4())
CLAUDE_SESSION_STARTED = False


def configure_llm_backend(
    *,
    llm_model: str | None = None,
    pi_model: str | None = None,
    pi_thinking: str | None = None,
    pi_reset_each_turn: bool | None = None,
    pi_rpc_timeout: float | None = None,
    use_pi_cli: bool | None = None,
    use_claude_code: bool | None = None,
    claude_session_id: str | None = None,
    claude_session_started: bool | None = None,
) -> None:
    """Update process-wide backend settings for this demo run."""
    global LLM_MODEL, PI_MODEL, PI_THINKING, PI_RESET_EACH_TURN, PI_RPC_TIMEOUT
    global USE_PI_CLI, USE_CLAUDE_CODE, CLAUDE_SESSION_ID, CLAUDE_SESSION_STARTED

    if llm_model is not None:
        LLM_MODEL = llm_model
    if pi_model is not None:
        PI_MODEL = pi_model
    if pi_thinking is not None:
        PI_THINKING = pi_thinking
    if pi_reset_each_turn is not None:
        PI_RESET_EACH_TURN = pi_reset_each_turn
    if pi_rpc_timeout is not None:
        PI_RPC_TIMEOUT = pi_rpc_timeout
    if use_pi_cli is not None:
        USE_PI_CLI = use_pi_cli
    if use_claude_code is not None:
        USE_CLAUDE_CODE = use_claude_code
    if claude_session_id is not None:
        CLAUDE_SESSION_ID = claude_session_id
    if claude_session_started is not None:
        CLAUDE_SESSION_STARTED = claude_session_started


def llm_backend_label() -> str:
    if USE_PI_CLI:
        return f"pi-rpc:{PI_MODEL}:{PI_THINKING}"
    if USE_CLAUDE_CODE:
        return f"claude-code:{CLAUDE_SESSION_ID}"
    return LLM_MODEL


def claude_code_json(system_prompt: str, user_prompt: str) -> dict:
    """Call Claude Code in print mode and parse a JSON object from stdout.

    First call creates the session with --session-id; later calls must use
    --resume <session-id>. Reusing --session-id after creation makes Claude Code
    return "Session ID ... is already in use".
    """
    global CLAUDE_SESSION_STARTED

    prompt = (
        "Vasta AINULT ühe korrektse JSON objektiga. Ära lisa markdowni ega selgitusi.\n\n"
        f"Kasutaja sisend:\n{user_prompt}"
    )
    session_args = ["--resume", CLAUDE_SESSION_ID] if CLAUDE_SESSION_STARTED else ["--session-id", CLAUDE_SESSION_ID]
    proc = subprocess.run(
        [
            "claude",
            "--print",
            "--system-prompt",
            system_prompt,
            *session_args,
            prompt,
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip())
    CLAUDE_SESSION_STARTED = True
    text = (proc.stdout or "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def _json_object_from_text(text: str) -> dict:
    text = (text or "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            raise
        return json.loads(match.group(0))


class PiRpcClient:
    """Long-lived pi RPC client so model startup is paid once at demo start."""

    def __init__(self, system_prompt: str):
        if shutil.which("pi") is None:
            raise RuntimeError("pi CLI not found in PATH")
        self.needs_reset = False
        self.lock = threading.RLock()
        self.proc = subprocess.Popen(
            [
                "pi",
                "--mode",
                "rpc",
                "--model",
                PI_MODEL,
                "--thinking",
                PI_THINKING,
                "--no-session",
                "--no-context-files",
                "--no-tools",
                "--no-extensions",
                "--no-skills",
                "--no-prompt-templates",
                "--no-themes",
                "--system-prompt",
                system_prompt,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

    def _send(self, message: dict[str, Any]) -> None:
        if self.proc.poll() is not None:
            stderr = self.proc.stderr.read() if self.proc.stderr else ""
            raise RuntimeError(f"pi RPC exited with code {self.proc.returncode}: {stderr}")
        assert self.proc.stdin is not None
        self.proc.stdin.write(json.dumps(message, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()

    def _read_event(self, deadline: float) -> dict[str, Any]:
        assert self.proc.stdout is not None
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("pi RPC timed out")
        ready, _, _ = select.select([self.proc.stdout], [], [], remaining)
        if not ready:
            raise TimeoutError("pi RPC timed out")
        line = self.proc.stdout.readline()
        if not line:
            stderr = self.proc.stderr.read() if self.proc.stderr else ""
            raise RuntimeError(f"pi RPC closed stdout: {stderr}")
        return json.loads(line)

    def reset_session(self, timeout_s: float = 5.0) -> None:
        with self.lock:
            req_id = str(uuid.uuid4())
            self._send({"id": req_id, "type": "new_session"})
            deadline = time.monotonic() + timeout_s
            while True:
                event = self._read_event(deadline)
                if event.get("type") == "response" and event.get("id") == req_id:
                    if not event.get("success", False):
                        raise RuntimeError(event.get("error", "pi RPC new_session failed"))
                    self.needs_reset = False
                    return

    def request_json(self, user_prompt: str, timeout_s: float | None = None) -> dict:
        if timeout_s is None:
            timeout_s = PI_RPC_TIMEOUT
        with self.lock:
            if PI_RESET_EACH_TURN and self.needs_reset:
                self.reset_session()
            req_id = str(uuid.uuid4())
            prompt = (
                "Treat this as an independent voice-command turn. Ignore previous user commands; use only system rules.\n"
                "Kasutaja STT sisend:\n"
                f"{user_prompt}\n\n"
                "Vasta AINULT ühe korrektse JSON objektiga. Ära lisa markdowni ega selgitusi."
            )
            self._send({"id": req_id, "type": "prompt", "message": prompt})
            deadline = time.monotonic() + timeout_s
            text_parts: list[str] = []
            final_text = ""
            while True:
                event = self._read_event(deadline)
                if event.get("type") == "message_update":
                    delta = event.get("assistantMessageEvent", {})
                    if delta.get("type") == "text_delta":
                        text_parts.append(delta.get("delta", ""))
                    elif delta.get("type") == "text_end" and not text_parts:
                        final_text = delta.get("content", "")
                elif event.get("type") == "agent_end":
                    if text_parts:
                        final_text = "".join(text_parts)
                    if not final_text:
                        final_text = _last_text_from_agent_end(event)
                    self.needs_reset = True
                    break
                elif event.get("type") == "message_end" and not text_parts:
                    final_text = _text_from_message(event.get("message", {}))
            return _json_object_from_text(final_text)

    def close(self) -> None:
        with self.lock:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=3)
            except Exception:
                self.proc.kill()


def _text_from_message(message: dict[str, Any]) -> str:
    content = message.get("content", [])
    if isinstance(content, str):
        return content
    parts = [block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text"]
    return "".join(parts).strip()


def _last_text_from_agent_end(event: dict[str, Any]) -> str:
    for message in reversed(event.get("messages", [])):
        if message.get("role") == "assistant":
            text = _text_from_message(message)
            if text:
                return text
    return ""


def get_pi_rpc_client(system_prompt: str) -> PiRpcClient:
    with PI_RPC_CLIENTS_LOCK:
        client = PI_RPC_CLIENTS.get(system_prompt)
        if client is None or client.proc.poll() is not None:
            client = PiRpcClient(system_prompt)
            PI_RPC_CLIENTS[system_prompt] = client
        return client


def close_pi_rpc_clients() -> None:
    with PI_RPC_CLIENTS_LOCK:
        clients = list(PI_RPC_CLIENTS.values())
        PI_RPC_CLIENTS.clear()
    for client in clients:
        client.close()


def pi_cli_json(system_prompt: str, user_prompt: str) -> dict:
    return get_pi_rpc_client(system_prompt).request_json(user_prompt)


def llm_parse_intent(user_text: str, system_prompt: str) -> dict:
    if USE_PI_CLI:
        return pi_cli_json(system_prompt, user_text)
    if USE_CLAUDE_CODE:
        return claude_code_json(system_prompt, user_text)
    resp = OLLAMA_SESSION.post(
        OLLAMA_URL,
        json={
            "model": LLM_MODEL,
            "stream": False,
            "format": "json",
            "keep_alive": OLLAMA_KEEP_ALIVE,
            "options": OLLAMA_JSON_OPTIONS,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
        },
        timeout=OLLAMA_REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return json.loads(resp.json()["message"]["content"])
