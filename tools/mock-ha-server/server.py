#!/usr/bin/env python3
"""Mock Home Assistant MCP server for testing voice pipeline LLM integration.

Simulates smart home devices that an LLM would control in a real HA setup.
Exposes tools via stdin/stdout MCP protocol (JSON-RPC).

Usage:
    python server.py
    # or via MCP client configuration
"""

import json
import sys
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger(__name__)

# --- Simulated device state ---

DEVICES = {
    "light.elutuba": {
        "friendly_name": "Elutoa lamp",
        "type": "light",
        "state": "off",
        "brightness": 255,
        "color": {"r": 255, "g": 200, "b": 100},
        "color_name": "soe valge",
    },
    "light.magamistuba": {
        "friendly_name": "Magamistoa lamp",
        "type": "light",
        "state": "off",
        "brightness": 255,
        "color": {"r": 255, "g": 200, "b": 100},
        "color_name": "soe valge",
    },
    "switch.kohvimasin": {
        "friendly_name": "Kohvimasin",
        "type": "switch",
        "state": "off",
    },
    "sensor.temperatuur": {
        "friendly_name": "Toa temperatuur",
        "type": "sensor",
        "state": "21.5",
        "unit": "°C",
    },
    "sensor.kellaaeg": {
        "friendly_name": "Kellaaeg",
        "type": "sensor",
        "state": None,  # dynamic
        "unit": "",
    },
}

COLOR_MAP = {
    "punane": {"r": 255, "g": 0, "b": 0},
    "roheline": {"r": 0, "g": 255, "b": 0},
    "sinine": {"r": 0, "g": 0, "b": 255},
    "kollane": {"r": 255, "g": 255, "b": 0},
    "lilla": {"r": 128, "g": 0, "b": 255},
    "roosa": {"r": 255, "g": 105, "b": 180},
    "oranž": {"r": 255, "g": 165, "b": 0},
    "valge": {"r": 255, "g": 255, "b": 255},
    "soe valge": {"r": 255, "g": 200, "b": 100},
    "külm valge": {"r": 200, "g": 220, "b": 255},
    "red": {"r": 255, "g": 0, "b": 0},
    "green": {"r": 0, "g": 255, "b": 0},
    "blue": {"r": 0, "g": 0, "b": 255},
    "yellow": {"r": 255, "g": 255, "b": 0},
    "purple": {"r": 128, "g": 0, "b": 255},
    "pink": {"r": 255, "g": 105, "b": 180},
    "orange": {"r": 255, "g": 165, "b": 0},
    "white": {"r": 255, "g": 255, "b": 255},
}

# --- Tool definitions (MCP schema) ---

TOOLS = [
    {
        "name": "turn_on",
        "description": "Lülita seade sisse. Töötab lampide ja lülititega. / Turn on a device (lights, switches).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Seadme ID, nt 'light.elutuba' või 'switch.kohvimasin'",
                },
                "brightness": {
                    "type": "integer",
                    "description": "Heledus 0-255 (ainult lambid)",
                    "minimum": 0,
                    "maximum": 255,
                },
                "color": {
                    "type": "string",
                    "description": "Värvi nimi eesti või inglise keeles, nt 'punane', 'sinine', 'blue'",
                },
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "turn_off",
        "description": "Lülita seade välja. / Turn off a device.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Seadme ID, nt 'light.elutuba'",
                },
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "set_color",
        "description": "Muuda lambi värvi. / Change light color.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Lambi ID, nt 'light.elutuba'",
                },
                "color": {
                    "type": "string",
                    "description": "Värvi nimi eesti või inglise keeles",
                },
            },
            "required": ["entity_id", "color"],
        },
    },
    {
        "name": "set_brightness",
        "description": "Muuda lambi heledust. / Change light brightness.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Lambi ID",
                },
                "brightness": {
                    "type": "integer",
                    "description": "Heledus 0-255 (0=hämar, 255=täis)",
                    "minimum": 0,
                    "maximum": 255,
                },
            },
            "required": ["entity_id", "brightness"],
        },
    },
    {
        "name": "get_state",
        "description": "Küsi seadme olekut. Saab küsida temperatuuri, kellaaega, lambi olekut jne. / Get device state.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Seadme ID, nt 'sensor.temperatuur'",
                },
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "list_devices",
        "description": "Näita kõiki saadaolevaid seadmeid. / List all available devices.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]

# --- Tool execution ---


def execute_tool(name: str, args: dict) -> str:
    """Execute a tool call and return result text."""

    if name == "turn_on":
        entity_id = args["entity_id"]
        if entity_id not in DEVICES:
            return f"Viga: seadet '{entity_id}' ei leitud."
        dev = DEVICES[entity_id]
        dev["state"] = "on"
        result = f"✓ {dev['friendly_name']} on nüüd SEES"
        if "brightness" in args and dev["type"] == "light":
            dev["brightness"] = args["brightness"]
            result += f" (heledus: {args['brightness']})"
        if "color" in args and dev["type"] == "light":
            color_name = args["color"].lower()
            if color_name in COLOR_MAP:
                dev["color"] = COLOR_MAP[color_name]
                dev["color_name"] = color_name
                result += f" (värv: {color_name})"
            else:
                result += f" (tundmatu värv: {color_name}, kasutan vaikimisi)"
        log.info("TURN_ON %s → %s", entity_id, result)
        return result

    elif name == "turn_off":
        entity_id = args["entity_id"]
        if entity_id not in DEVICES:
            return f"Viga: seadet '{entity_id}' ei leitud."
        dev = DEVICES[entity_id]
        dev["state"] = "off"
        result = f"✓ {dev['friendly_name']} on nüüd VÄLJAS"
        log.info("TURN_OFF %s → %s", entity_id, result)
        return result

    elif name == "set_color":
        entity_id = args["entity_id"]
        if entity_id not in DEVICES:
            return f"Viga: seadet '{entity_id}' ei leitud."
        dev = DEVICES[entity_id]
        if dev["type"] != "light":
            return f"Viga: {dev['friendly_name']} ei ole lamp."
        color_name = args["color"].lower()
        if color_name in COLOR_MAP:
            dev["color"] = COLOR_MAP[color_name]
            dev["color_name"] = color_name
            dev["state"] = "on"
            result = f"✓ {dev['friendly_name']} värv on nüüd {color_name}"
        else:
            result = f"Tundmatu värv: {color_name}. Saadaval: {', '.join(COLOR_MAP.keys())}"
        log.info("SET_COLOR %s → %s", entity_id, result)
        return result

    elif name == "set_brightness":
        entity_id = args["entity_id"]
        if entity_id not in DEVICES:
            return f"Viga: seadet '{entity_id}' ei leitud."
        dev = DEVICES[entity_id]
        if dev["type"] != "light":
            return f"Viga: {dev['friendly_name']} ei ole lamp."
        dev["brightness"] = args["brightness"]
        dev["state"] = "on"
        pct = round(args["brightness"] / 255 * 100)
        result = f"✓ {dev['friendly_name']} heledus on nüüd {pct}%"
        log.info("SET_BRIGHTNESS %s → %s", entity_id, result)
        return result

    elif name == "get_state":
        entity_id = args["entity_id"]
        if entity_id not in DEVICES:
            return f"Viga: seadet '{entity_id}' ei leitud."
        dev = DEVICES[entity_id]
        if entity_id == "sensor.kellaaeg":
            now = datetime.now()
            return f"Praegu on kell {now.strftime('%H:%M')}"
        if dev["type"] == "sensor":
            return f"{dev['friendly_name']}: {dev['state']}{dev['unit']}"
        if dev["type"] == "light":
            if dev["state"] == "off":
                return f"{dev['friendly_name']} on VÄLJAS"
            pct = round(dev["brightness"] / 255 * 100)
            return f"{dev['friendly_name']} on SEES (heledus: {pct}%, värv: {dev['color_name']})"
        return f"{dev['friendly_name']}: {dev['state']}"

    elif name == "list_devices":
        lines = []
        for eid, dev in DEVICES.items():
            state = dev["state"]
            if eid == "sensor.kellaaeg":
                state = datetime.now().strftime("%H:%M")
            lines.append(f"- {dev['friendly_name']} ({eid}): {state}")
        return "Saadaolevad seadmed:\n" + "\n".join(lines)

    return f"Tundmatu tööriist: {name}"


# --- MCP JSON-RPC protocol ---


def send_response(id, result):
    msg = {"jsonrpc": "2.0", "id": id, "result": result}
    out = json.dumps(msg)
    sys.stdout.write(out + "\n")
    sys.stdout.flush()


def send_error(id, code, message):
    msg = {"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}}
    out = json.dumps(msg)
    sys.stdout.write(out + "\n")
    sys.stdout.flush()


def handle_request(req: dict):
    method = req.get("method", "")
    id = req.get("id")
    params = req.get("params", {})

    if method == "initialize":
        send_response(id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "mock-ha-server", "version": "1.0.0"},
        })

    elif method == "notifications/initialized":
        pass  # no response needed

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
    log.info("Mock HA MCP server started. Waiting for JSON-RPC messages on stdin...")
    log.info("Available devices: %s", ", ".join(DEVICES.keys()))

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
            log.error("Error handling request: %s", e, exc_info=True)
            send_error(req.get("id"), -32603, str(e))


if __name__ == "__main__":
    main()
