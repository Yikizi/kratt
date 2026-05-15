#!/usr/bin/env python3
"""Airfryer MCP server — raw JSON-RPC (Python 3.9 compat, no mcp lib dep).

Drop-in replacement for mock-ha-server / wiz-server in demo-pipeline.
Wraps the local HTTP daemon at http://127.0.0.1:8767 (see ~/airfryer/airfryer.py serve).

Tools: cook(temperature_c, time_minutes) · stop · status

Protocol: stdin/stdout JSON-RPC 2.0 (MCP 2024-11-05).
Methods: initialize, notifications/initialized, tools/list, tools/call, ping.
"""
from __future__ import annotations

import json
import logging
import sys
import time
import urllib.error
import urllib.request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("airfryer")

BASE_URL = "http://127.0.0.1:8767"
HTTP_TIMEOUT = 15

TOOLS = [
    {
        "name": "cook",
        "description": "Start cooking with temperature (°C, 40-200) and time (minutes, 1-60).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "temperature_c": {"type": "integer", "minimum": 40, "maximum": 200},
                "time_minutes": {"type": "integer", "minimum": 1, "maximum": 60},
            },
            "required": ["temperature_c", "time_minutes"],
        },
    },
    {
        "name": "stop",
        "description": "Stop active cooking. Only works if started via `cook`.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "status",
        "description": "One-line summary of current airfryer state.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def _http(method: str, path: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if data else {},
    )
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
        return json.loads(r.read())


def tool_cook(args: dict) -> str:
    t = args.get("temperature_c")
    m = args.get("time_minutes")
    if not isinstance(t, int) or not 40 <= t <= 200:
        return f"error: temperature_c must be 40-200, got {t}"
    if not isinstance(m, int) or not 1 <= m <= 60:
        return f"error: time_minutes must be 1-60, got {m}"
    try:
        # State transitions need processing time on the peakontroller side.
        # Without waits, only the first command lands and start is ignored.
        _http("POST", "/wake")
        time.sleep(2)
        _http("POST", "/set", {"temp": t, "time": m * 60, "fahrenheit": False})
        time.sleep(2)
        _http("POST", "/start")
        # Verify cooking actually entered
        time.sleep(2)
        try:
            r = _http("POST", "/raw", {"command": "getPort", "port": "Status"})
            p = (r.get("data") or {}).get("properties") or {}
            actual = p.get("status", "?")
            if actual not in ("cooking", "active", "setting"):
                return f"warning: start sent but status={actual}, fans may not be running"
        except Exception:
            pass
        return f"cooking started: {t}°C for {m} min"
    except urllib.error.URLError as e:
        return f"error: airfryer daemon unreachable ({e})"


def tool_stop(_args: dict) -> str:
    try:
        _http("POST", "/stop")
        return "stopped"
    except urllib.error.URLError as e:
        return f"error: airfryer daemon unreachable ({e})"


def tool_status(_args: dict) -> str:
    try:
        ports = _http("POST", "/raw", {"command": "getPort", "port": "Status"})
        p = (ports.get("data") or {}).get("properties") or {}
        if not p:
            shadow = _http("GET", "/shadow")
            r = (shadow.get("state") or {}).get("reported") or {}
            return f"{r.get('productState', '?')} (powerOn={r.get('powerOn', '?')})"
        s = p.get("status", "?")
        if s in ("cooking", "setting"):
            unit = "°F" if p.get("temp_unit") is True else "°C"
            return f"{s} at {p.get('temp', '?')}{unit}, {p.get('cur_time', 0)}/{p.get('time', 0)}s"
        return s
    except Exception as e:
        return f"error: {e}"


TOOL_HANDLERS = {"cook": tool_cook, "stop": tool_stop, "status": tool_status}


def _reply(req_id, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}) + "\n")
    sys.stdout.flush()


def _error(req_id, code, message):
    sys.stdout.write(
        json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}) + "\n"
    )
    sys.stdout.flush()


def handle_request(req: dict):
    method = req.get("method")
    req_id = req.get("id")
    params = req.get("params") or {}

    if method == "initialize":
        _reply(req_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "airfryer", "version": "1.0"},
        })
    elif method == "notifications/initialized":
        return  # no reply for notifications
    elif method == "tools/list":
        _reply(req_id, {"tools": TOOLS})
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        handler = TOOL_HANDLERS.get(name)
        if not handler:
            _error(req_id, -32601, f"unknown tool: {name}")
            return
        try:
            text = handler(args)
            _reply(req_id, {"content": [{"type": "text", "text": text}], "isError": False})
        except Exception as e:
            log.exception("tool %s failed", name)
            _error(req_id, -32000, str(e))
    elif method == "ping":
        _reply(req_id, {})
    else:
        _error(req_id, -32601, f"unknown method: {method}")


def main():
    log.info("airfryer MCP server starting (HTTP daemon: %s)", BASE_URL)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError as e:
            log.warning("bad JSON: %s", e)
            continue
        try:
            handle_request(req)
        except Exception:
            log.exception("request failed")


if __name__ == "__main__":
    main()
