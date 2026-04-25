# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.9"]
# ///
"""WiZ smart bulb MCP server — local UDP control, no cloud.

Run:  uv run scripts/mcp/wiz_bulbs.py
Config in claude settings:
  "wiz-bulbs": {
    "type": "stdio",
    "command": "uv",
    "args": ["run", "scripts/mcp/wiz_bulbs.py"]
  }
"""

import asyncio
import json
import socket
from dataclasses import dataclass, field

from mcp.server.fastmcp import FastMCP

WIZ_PORT = 38899
DISCOVERY_TIMEOUT = 3.0
COMMAND_TIMEOUT = 2.0

mcp = FastMCP(
    "wiz-bulbs",
    instructions=(
        "Control WiZ smart bulbs on the local network via UDP. "
        "Use discover_bulbs first to find bulbs, then control them by IP. "
        "Bulbs support on/off, dimming (10-100%), color temperature (2200-6500K), "
        "and named scenes."
    ),
)

# --- Scenes ---
SCENES = {
    "ocean": 1, "romance": 2, "sunset": 3, "party": 4, "fireplace": 5,
    "cozy": 6, "forest": 7, "pastel": 8, "wake up": 9, "bedtime": 10,
    "warm white": 11, "daylight": 12, "cool white": 13, "night light": 14,
    "focus": 15, "relax": 16, "true colors": 17, "tv time": 18,
    "plant growth": 19, "spring": 20, "summer": 21, "fall": 22,
    "deep dive": 23, "jungle": 24, "mojito": 25, "club": 26,
    "christmas": 27, "halloween": 28, "candlelight": 29, "golden white": 30,
    "pulse": 31, "steampunk": 32,
}


# --- Low-level UDP ---

def _send_udp(ip: str, payload: dict, timeout: float = COMMAND_TIMEOUT) -> dict:
    """Send a UDP JSON message to a WiZ bulb and return the response."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(json.dumps(payload).encode(), (ip, WIZ_PORT))
        data, _ = sock.recvfrom(1024)
        return json.loads(data.decode())
    finally:
        sock.close()


def _get_broadcast_addresses() -> list[str]:
    """Get broadcast addresses from en0 interface."""
    import subprocess

    addrs = ["255.255.255.255"]
    try:
        result = subprocess.run(
            ["ifconfig", "en0"], capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.split("\n"):
            if "broadcast" in line:
                parts = line.strip().split()
                for i, p in enumerate(parts):
                    if p == "broadcast" and i + 1 < len(parts):
                        addrs.append(parts[i + 1])
    except Exception:
        pass
    return addrs


@dataclass
class BulbInfo:
    ip: str
    mac: str
    state: bool = False
    dimming: int = 100
    temp: int = 2700
    scene_id: int = 0
    rssi: int = 0
    firmware: str = ""
    module: str = ""


# --- MCP Tools ---

@mcp.tool()
def discover_bulbs() -> list[dict]:
    """Discover all WiZ bulbs on the local WiFi network.

    Returns a list of bulbs with their IP, MAC, state, and settings.
    Call this first before controlling bulbs.
    """
    discovery_msg = json.dumps({
        "method": "registration",
        "params": {
            "phoneMac": "AAAAAAAAAAAA",
            "register": False,
            "phoneIp": "1.2.3.4",
            "id": "1",
        },
    })

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(DISCOVERY_TIMEOUT)

    try:
        for addr in _get_broadcast_addresses():
            try:
                sock.sendto(discovery_msg.encode(), (addr, WIZ_PORT))
            except Exception:
                continue

        seen: dict[str, str] = {}  # mac -> ip
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                resp = json.loads(data.decode())
                mac = resp.get("result", {}).get("mac", "")
                if mac and mac not in seen:
                    seen[mac] = addr[0]
            except socket.timeout:
                break
    finally:
        sock.close()

    bulbs = []
    for mac, ip in seen.items():
        info = {"ip": ip, "mac": mac}
        try:
            state = _send_udp(ip, {"method": "getPilot"})
            r = state.get("result", {})
            info.update({
                "on": r.get("state", False),
                "dimming": r.get("dimming", 0),
                "temperature_k": r.get("temp", 0),
                "scene_id": r.get("sceneId", 0),
                "rssi": r.get("rssi", 0),
            })
        except Exception:
            pass
        try:
            cfg = _send_udp(ip, {"method": "getSystemConfig"})
            r = cfg.get("result", {})
            info.update({
                "module": r.get("moduleName", ""),
                "firmware": r.get("fwVersion", ""),
            })
        except Exception:
            pass
        bulbs.append(info)

    return bulbs


@mcp.tool()
def turn_on(
    ip: str,
    dimming: int = 100,
    temperature_k: int = 0,
) -> dict:
    """Turn on a WiZ bulb.

    Args:
        ip: Bulb IP address (from discover_bulbs).
        dimming: Brightness 10-100%.
        temperature_k: Color temperature 2200-6500K. 0 = keep current.
    """
    params: dict = {"state": True, "dimming": max(10, min(100, dimming))}
    if temperature_k:
        params["temp"] = max(2200, min(6500, temperature_k))
    return _send_udp(ip, {"method": "setPilot", "params": params})


@mcp.tool()
def turn_off(ip: str) -> dict:
    """Turn off a WiZ bulb.

    Args:
        ip: Bulb IP address (from discover_bulbs).
    """
    return _send_udp(ip, {"method": "setPilot", "params": {"state": False}})


@mcp.tool()
def set_brightness(ip: str, dimming: int) -> dict:
    """Set bulb brightness (turns on if off).

    Args:
        ip: Bulb IP address.
        dimming: Brightness 10-100%.
    """
    return _send_udp(ip, {
        "method": "setPilot",
        "params": {"state": True, "dimming": max(10, min(100, dimming))},
    })


@mcp.tool()
def set_temperature(ip: str, temperature_k: int) -> dict:
    """Set bulb color temperature (turns on if off).

    Args:
        ip: Bulb IP address.
        temperature_k: 2200 (warm/orange) to 6500 (cool/blue-white).
    """
    return _send_udp(ip, {
        "method": "setPilot",
        "params": {
            "state": True,
            "temp": max(2200, min(6500, temperature_k)),
        },
    })


@mcp.tool()
def set_scene(ip: str, scene: str) -> dict:
    """Set a named scene on the bulb.

    Args:
        ip: Bulb IP address.
        scene: Scene name. Options: ocean, romance, sunset, party, fireplace,
               cozy, forest, pastel, wake_up, bedtime, warm_white, daylight,
               cool_white, night_light, focus, relax, true_colors, tv_time,
               plant_growth, spring, summer, fall, deep_dive, jungle, mojito,
               club, christmas, halloween, candlelight, golden_white, pulse,
               steampunk.
    """
    scene_lower = scene.lower().replace("_", " ")
    scene_id = SCENES.get(scene_lower)
    if scene_id is None:
        return {"error": f"Unknown scene '{scene}'. Available: {', '.join(SCENES.keys())}"}
    return _send_udp(ip, {
        "method": "setPilot",
        "params": {"state": True, "sceneId": scene_id},
    })


@mcp.tool()
def get_state(ip: str) -> dict:
    """Get current state of a WiZ bulb.

    Args:
        ip: Bulb IP address.
    """
    return _send_udp(ip, {"method": "getPilot"})


@mcp.tool()
def control_all(
    action: str,
    dimming: int = 100,
    temperature_k: int = 0,
    scene: str = "",
) -> list[dict]:
    """Control all discovered WiZ bulbs at once.

    Args:
        action: "on", "off", or "scene".
        dimming: Brightness 10-100% (for "on").
        temperature_k: Color temperature 2200-6500K (for "on", 0 = keep current).
        scene: Scene name (for "scene" action).
    """
    # Quick discovery
    bulbs = discover_bulbs()
    results = []
    for bulb in bulbs:
        ip = bulb["ip"]
        try:
            if action == "off":
                r = turn_off(ip)
            elif action == "scene" and scene:
                r = set_scene(ip, scene)
            else:
                r = turn_on(ip, dimming=dimming, temperature_k=temperature_k)
            results.append({"ip": ip, **r})
        except Exception as e:
            results.append({"ip": ip, "error": str(e)})
    return results


if __name__ == "__main__":
    mcp.run()
