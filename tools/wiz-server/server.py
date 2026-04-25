#!/usr/bin/env python3
from __future__ import annotations

"""WiZ bulb MCP server — drop-in replacement for mock-ha-server.

Same JSON-RPC stdin/stdout protocol, but controls real WiZ bulbs via UDP.
Auto-discovers bulbs on startup.

Usage:
    python server.py                  # auto-discover
    python server.py --bulbs 192.168.68.56,192.168.68.57  # explicit IPs
"""

import argparse
import json
import socket
import sys
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger(__name__)

WIZ_PORT = 38899
COMMAND_TIMEOUT = 2.0
DISCOVERY_TIMEOUT = 3.0


# --- WiZ UDP communication ---


def wiz_send(ip: str, method: str, params: dict | None = None) -> dict:
    """Send UDP command to a WiZ bulb, return parsed response."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(COMMAND_TIMEOUT)
    msg = {"method": method}
    if params:
        msg["params"] = params
    try:
        sock.sendto(json.dumps(msg).encode(), (ip, WIZ_PORT))
        data, _ = sock.recvfrom(1024)
        return json.loads(data.decode())
    except socket.timeout:
        return {"error": "timeout"}
    finally:
        sock.close()


def discover_bulbs() -> dict[str, dict]:
    """Broadcast discovery, return {mac: {ip, mac, module, firmware}}."""
    import subprocess

    broadcast_addrs = ["255.255.255.255"]
    try:
        result = subprocess.run(
            ["ifconfig", "en0"], capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.split("\n"):
            if "broadcast" in line:
                parts = line.strip().split()
                for i, p in enumerate(parts):
                    if p == "broadcast" and i + 1 < len(parts):
                        broadcast_addrs.append(parts[i + 1])
    except Exception:
        pass

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
        for addr in broadcast_addrs:
            try:
                sock.sendto(discovery_msg.encode(), (addr, WIZ_PORT))
            except Exception:
                continue

        seen: dict[str, dict] = {}
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                resp = json.loads(data.decode())
                mac = resp.get("result", {}).get("mac", "")
                if mac and mac not in seen:
                    seen[mac] = {"ip": addr[0], "mac": mac}
            except socket.timeout:
                break
    finally:
        sock.close()

    # Enrich with config info
    for mac, info in seen.items():
        try:
            cfg = wiz_send(info["ip"], "getSystemConfig")
            r = cfg.get("result", {})
            info["module"] = r.get("moduleName", "unknown")
            info["firmware"] = r.get("fwVersion", "unknown")
        except Exception:
            pass

    return seen


# --- Device registry ---

class WizDeviceRegistry:
    """Maps entity_id style names to real WiZ bulb IPs."""

    def __init__(self, bulb_ips: list[str] | None = None):
        self.bulbs: dict[str, dict] = {}  # entity_id -> {ip, mac, name, ...}

        if bulb_ips:
            for i, ip in enumerate(bulb_ips):
                entity_id = f"light.wiz_{i + 1}"
                self.bulbs[entity_id] = {
                    "ip": ip,
                    "friendly_name": f"WiZ pirn {i + 1}",
                    "entity_id": entity_id,
                }
        else:
            log.info("Discovering WiZ bulbs...")
            discovered = discover_bulbs()
            for i, (mac, info) in enumerate(sorted(discovered.items())):
                entity_id = f"light.wiz_{i + 1}"
                self.bulbs[entity_id] = {
                    "ip": info["ip"],
                    "mac": mac,
                    "friendly_name": f"WiZ pirn {i + 1}",
                    "entity_id": entity_id,
                    "module": info.get("module", ""),
                }

        if not self.bulbs:
            log.warning("No WiZ bulbs found!")
        else:
            for eid, b in self.bulbs.items():
                log.info("  %s → %s (%s)", eid, b["ip"], b["friendly_name"])

    def get(self, entity_id: str) -> dict | None:
        # Allow "light.wiz_1" or just "wiz_1" or "1"
        if entity_id in self.bulbs:
            return self.bulbs[entity_id]
        prefixed = f"light.{entity_id}" if not entity_id.startswith("light.") else entity_id
        if prefixed in self.bulbs:
            return self.bulbs[prefixed]
        # Try by index
        try:
            idx = int(entity_id)
            key = f"light.wiz_{idx}"
            return self.bulbs.get(key)
        except (ValueError, IndexError):
            pass
        # "all" targets all bulbs
        return None

    def all(self) -> list[dict]:
        return list(self.bulbs.values())

    def get_state(self, ip: str) -> dict:
        resp = wiz_send(ip, "getPilot")
        r = resp.get("result", {})
        return {
            "on": r.get("state", False),
            "dimming": r.get("dimming", 0),
            "temperature_k": r.get("temp", 0),
            "scene_id": r.get("sceneId", 0),
            "rssi": r.get("rssi", 0),
        }


# --- Globals ---
registry: WizDeviceRegistry = None  # initialized in main()

# --- Brightness conversion ---
# Pipeline uses 0-255 (HA style), WiZ uses 10-100%

def ha_brightness_to_wiz(brightness: int) -> int:
    """Convert HA 0-255 brightness to WiZ 10-100%."""
    pct = round(brightness / 255 * 100)
    return max(10, min(100, pct))


def wiz_dimming_to_ha(dimming: int) -> int:
    """Convert WiZ 10-100% to HA 0-255."""
    return round(dimming / 100 * 255)


# --- Color temperature mapping ---
# Estonian color names → WiZ color temp (K)

COLOR_TEMP_MAP = {
    "soe valge": 2700,
    "warm white": 2700,
    "soe": 2700,
    "warm": 2700,
    "neutraalne": 4000,
    "neutral": 4000,
    "külm valge": 6500,
    "cool white": 6500,
    "külm": 6500,
    "cool": 6500,
    "päevavalgus": 5000,
    "daylight": 5000,
    "öövalgus": 2200,
    "night": 2200,
}

# --- Tool definitions ---

TOOLS = [
    {
        "name": "turn_on",
        "description": "Lülita WiZ lamp sisse. / Turn on a WiZ bulb.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Lambi ID, nt 'light.wiz_1' või 'light.wiz_2'",
                },
                "brightness": {
                    "type": "integer",
                    "description": "Heledus 0-255 (0=hämar, 255=täis)",
                    "minimum": 0,
                    "maximum": 255,
                },
                "color": {
                    "type": "string",
                    "description": "Värvitoon: 'soe valge', 'külm valge', 'päevavalgus', 'öövalgus'",
                },
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "turn_off",
        "description": "Lülita WiZ lamp välja. / Turn off a WiZ bulb.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Lambi ID, nt 'light.wiz_1'",
                },
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "set_brightness",
        "description": "Muuda lambi heledust. / Change bulb brightness.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Lambi ID",
                },
                "brightness": {
                    "type": "integer",
                    "description": "Heledus 0-255",
                    "minimum": 0,
                    "maximum": 255,
                },
            },
            "required": ["entity_id", "brightness"],
        },
    },
    {
        "name": "set_color",
        "description": "Muuda lambi värvitemperatuuri. / Change bulb color temperature.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Lambi ID",
                },
                "color": {
                    "type": "string",
                    "description": "Värvitoon: 'soe valge', 'külm valge', 'päevavalgus', 'neutraalne'",
                },
            },
            "required": ["entity_id", "color"],
        },
    },
    {
        "name": "get_state",
        "description": "Küsi lambi olekut. / Get bulb state.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Lambi ID, nt 'light.wiz_1'",
                },
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "list_devices",
        "description": "Näita kõiki WiZ lampe. / List all WiZ bulbs.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


# --- Tool execution ---

def execute_tool(name: str, args: dict) -> str:
    if name == "turn_on":
        entity_id = args.get("entity_id", "")
        bulb = registry.get(entity_id)
        if not bulb:
            return f"Viga: lampi '{entity_id}' ei leitud. Kasuta list_devices."
        params: dict = {"state": True}
        if "brightness" in args:
            params["dimming"] = ha_brightness_to_wiz(args["brightness"])
        if "color" in args:
            color = args["color"].lower()
            temp = COLOR_TEMP_MAP.get(color)
            if temp:
                params["temp"] = temp
        resp = wiz_send(bulb["ip"], "setPilot", params)
        if resp.get("result", {}).get("success"):
            result = f"✓ {bulb['friendly_name']} on nüüd SEES"
            if "dimming" in params:
                result += f" (heledus: {params['dimming']}%)"
            if "temp" in params:
                result += f" (värvus: {params['temp']}K)"
            log.info("TURN_ON %s (%s) → %s", entity_id, bulb["ip"], result)
            return result
        return f"Viga: {resp}"

    elif name == "turn_off":
        entity_id = args.get("entity_id", "")
        bulb = registry.get(entity_id)
        if not bulb:
            return f"Viga: lampi '{entity_id}' ei leitud."
        resp = wiz_send(bulb["ip"], "setPilot", {"state": False})
        if resp.get("result", {}).get("success"):
            result = f"✓ {bulb['friendly_name']} on nüüd VÄLJAS"
            log.info("TURN_OFF %s (%s) → %s", entity_id, bulb["ip"], result)
            return result
        return f"Viga: {resp}"

    elif name == "set_brightness":
        entity_id = args.get("entity_id", "")
        bulb = registry.get(entity_id)
        if not bulb:
            return f"Viga: lampi '{entity_id}' ei leitud."
        dimming = ha_brightness_to_wiz(args.get("brightness", 255))
        resp = wiz_send(bulb["ip"], "setPilot", {"state": True, "dimming": dimming})
        if resp.get("result", {}).get("success"):
            result = f"✓ {bulb['friendly_name']} heledus on nüüd {dimming}%"
            log.info("SET_BRIGHTNESS %s → %s", entity_id, result)
            return result
        return f"Viga: {resp}"

    elif name == "set_color":
        entity_id = args.get("entity_id", "")
        bulb = registry.get(entity_id)
        if not bulb:
            return f"Viga: lampi '{entity_id}' ei leitud."
        color = args.get("color", "").lower()
        temp = COLOR_TEMP_MAP.get(color, 4000)
        resp = wiz_send(bulb["ip"], "setPilot", {"state": True, "temp": temp})
        if resp.get("result", {}).get("success"):
            result = f"✓ {bulb['friendly_name']} värvus on nüüd {temp}K ({color})"
            log.info("SET_COLOR %s → %s", entity_id, result)
            return result
        return f"Viga: {resp}"

    elif name == "get_state":
        entity_id = args.get("entity_id", "")
        bulb = registry.get(entity_id)
        if not bulb:
            return f"Viga: lampi '{entity_id}' ei leitud."
        state = registry.get_state(bulb["ip"])
        if state["on"]:
            return (
                f"{bulb['friendly_name']} on SEES "
                f"(heledus: {state['dimming']}%, "
                f"värvus: {state['temperature_k']}K, "
                f"signaal: {state['rssi']}dBm)"
            )
        return f"{bulb['friendly_name']} on VÄLJAS"

    elif name == "list_devices":
        lines = []
        for bulb in registry.all():
            try:
                state = registry.get_state(bulb["ip"])
                status = "SEES" if state["on"] else "VÄLJAS"
                lines.append(
                    f"- {bulb['friendly_name']} ({bulb['entity_id']}): "
                    f"{status}, {bulb['ip']}"
                )
            except Exception:
                lines.append(f"- {bulb['friendly_name']} ({bulb['entity_id']}): ei vasta")
        return "WiZ lambid:\n" + "\n".join(lines) if lines else "Ühtegi lampi ei leitud."

    return f"Tundmatu tööriist: {name}"


# --- MCP JSON-RPC protocol (same as mock-ha-server) ---

def send_response(id, result):
    msg = {"jsonrpc": "2.0", "id": id, "result": result}
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def send_error(id, code, message):
    msg = {"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}}
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def handle_request(req: dict):
    method = req.get("method", "")
    id = req.get("id")
    params = req.get("params", {})

    if method == "initialize":
        send_response(id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "wiz-bulb-server", "version": "1.0.0"},
        })

    elif method == "notifications/initialized":
        pass

    elif method == "tools/list":
        send_response(id, {"tools": TOOLS})

    elif method == "tools/call":
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})
        log.info("Tool call: %s(%s)", tool_name, json.dumps(tool_args, ensure_ascii=False))
        result_text = execute_tool(tool_name, tool_args)
        send_response(id, {
            "content": [{"type": "text", "text": result_text}],
        })

    elif method == "ping":
        send_response(id, {})

    else:
        if id is not None:
            send_error(id, -32601, f"Method not found: {method}")


def main():
    global registry

    parser = argparse.ArgumentParser(description="WiZ bulb MCP server")
    parser.add_argument(
        "--bulbs",
        type=str,
        default=None,
        help="Comma-separated bulb IPs (skip discovery)",
    )
    args = parser.parse_args()

    bulb_ips = args.bulbs.split(",") if args.bulbs else None
    registry = WizDeviceRegistry(bulb_ips)

    log.info("WiZ MCP server ready. %d bulb(s).", len(registry.bulbs))

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            handle_request(req)
        except json.JSONDecodeError as e:
            log.error("Invalid JSON: %s", e)
            send_error(None, -32700, f"Parse error: {e}")
        except Exception as e:
            log.error("Error: %s", e, exc_info=True)
            send_error(req.get("id"), -32603, str(e))


if __name__ == "__main__":
    main()
