# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.9"]
# ///
"""Philips HD9285 airfryer MCP server — cloud-relay via local HTTP daemon.

Prerequisite: airfryer HTTP server running at http://127.0.0.1:8767
  (see ~/airfryer/airfryer.py serve --port 8767)

Config in claude settings:
  "airfryer": {
    "type": "stdio",
    "command": "uv",
    "args": ["run", "scripts/mcp/airfryer.py"]
  }
"""

import json
import urllib.error
import urllib.request

from mcp.server.fastmcp import FastMCP

BASE_URL = "http://127.0.0.1:8767"
HTTP_TIMEOUT = 15

mcp = FastMCP(
    "airfryer",
    instructions=(
        "Control a Philips airfryer in the kitchen. "
        "Use `cook` to start cooking with temperature and time. "
        "Use `stop` to halt cooking. "
        "Use `status` to check current state. "
        "Safety: cooking started physically on the device cannot be stopped remotely — "
        "only cooking started via `cook` can be stopped via `stop`."
    ),
)


def _http(method: str, path: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if data else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
            return json.loads(r.read())
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"airfryer daemon at {BASE_URL} unreachable: {e}. "
            "Start it with: cd ~/airfryer && uv run python airfryer.py serve --port 8767"
        )


@mcp.tool()
def cook(temperature_c: int, time_minutes: int) -> str:
    """Start cooking with the given temperature and time.

    temperature_c: target temperature in Celsius (40-200)
    time_minutes: cooking time in minutes (1-60)

    Returns a confirmation string.
    """
    if not 40 <= temperature_c <= 200:
        return f"error: temperature_c must be 40-200, got {temperature_c}"
    if not 1 <= time_minutes <= 60:
        return f"error: time_minutes must be 1-60, got {time_minutes}"
    _http("POST", "/wake")
    _http("POST", "/set", {"temp": temperature_c, "time": time_minutes * 60, "fahrenheit": False})
    _http("POST", "/start")
    return f"cooking started: {temperature_c}°C for {time_minutes} min"


@mcp.tool()
def stop() -> str:
    """Stop active cooking (pause then standby). Only works if cooking was started via `cook`."""
    _http("POST", "/stop")
    return "stopped"


@mcp.tool()
def status() -> str:
    """Return a one-line summary of the current airfryer state."""
    try:
        ports = _http("POST", "/raw", {"command": "getPort", "port": "Status"})
        p = ports.get("data", {}).get("properties", {})
        if not p:
            shadow = _http("GET", "/shadow")
            r = shadow.get("state", {}).get("reported", {})
            return f"{r.get('productState', '?')} (powerOn={r.get('powerOn', '?')})"
        s = p.get("status", "?")
        if s in ("cooking", "setting"):
            unit = "°F" if p.get("temp_unit") is True else "°C"
            return f"{s} at {p.get('temp', '?')}{unit}, {p.get('cur_time', 0)}/{p.get('time', 0)}s"
        return s
    except Exception as e:
        return f"error: {e}"


if __name__ == "__main__":
    mcp.run()
