#!/usr/bin/env python3
"""Full interactive voice pipeline: wake word → STT → LLM → MCP → response.

Supports multi-model temporal consensus detection (matching `kratt live`),
real WiZ bulb control, and interaction logging.

Usage:
    python pipeline.py --no-wakeword --wiz              # manual trigger + WiZ
    python pipeline.py --models v15 --wiz               # single model + WiZ
    python pipeline.py --models v10 v15 --wiz           # multi-model consensus + WiZ
    python pipeline.py --models v15 --wiz --bulbs 192.168.68.56,192.168.68.57
    python pipeline.py --wiz --ble-bridge
    python pipeline.py --log --participant P01          # enable telemetry
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import queue
import re
import select
import shlex
import shutil
import subprocess
import sys
import time
import ipaddress
import threading
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import requests
import sounddevice as sd

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    try:
        import tensorflow.lite as tflite
    except ImportError:
        tflite = None

# --- Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "wake-word/models"
STT_MODEL_DIR = PROJECT_ROOT / "wake-word/models/kiirkirjutaja-int8"
MOCK_MCP_SERVER = PROJECT_ROOT / "tools/mock-ha-server/server.py"
WIZ_MCP_SERVER = PROJECT_ROOT / "tools/wiz-server/server.py"
WIZ_CLI = PROJECT_ROOT / "tools/wiz-cli/wiz"
LOG_DIR = PROJECT_ROOT / "output/demo-logs"

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_KEEP_ALIVE = "10m"
OLLAMA_JSON_OPTIONS = {"temperature": 0, "num_predict": 80}
OLLAMA_PROTOCOL_OPTIONS = {
    "temperature": 0,
    "num_predict": 24,
    "repeat_penalty": 1.05,
    "top_k": 20,
    "top_p": 0.8,
}
OLLAMA_PROTOCOL_FORMAT = {
    "type": "object",
    "properties": {
        "cmd": {
            "type": "string",
            "enum": [
                "OFF", "ON", "COLOR", "DIM", "BRIGHTEN", "BRIGHT",
                "STATE", "TIME", "DATE", "WEATHER", "NONE",
            ],
        },
        "arg": {"type": "string"},
    },
    "required": ["cmd"],
    "additionalProperties": False,
}
OLLAMA_SESSION = requests.Session()
WEATHER_SESSION = requests.Session()
DEFAULT_WEATHER_LOCATION = os.getenv("KRATT_WEATHER_LOCATION", "Tallinn")
LLM_MODEL = "qwen2.5:3b"
PI_MODEL = "openai-codex/gpt-5.3-codex-spark"
PI_THINKING = "minimal"
PI_RESET_EACH_TURN = False
PI_RPC_TIMEOUT = 8.0
USE_CLAUDE_CODE = False
USE_PI_CLI = False
PI_RPC_CLIENTS: dict[str, "PiRpcClient"] = {}
CLAUDE_SESSION_ID = str(uuid.uuid4())
CLAUDE_SESSION_STARTED = False
TTS_URL = "http://127.0.0.1:5380/synthesize"
TTS_SPEAKER = "meelis"
TTS_SPEED = 1.0
SAMPLE_RATE = 16000
FRAME_MS = 10
MA_WINDOW = 5

# ANSI
BOLD = "\033[1m"
RESET = "\033[0m"
COLORS = ["\033[32m", "\033[33m", "\033[36m", "\033[35m", "\033[34m", "\033[91m"]

SYSTEM_PROMPT_MOCK = """\
Sa oled Kratt, eestikeelne häälassistent. Juhi nutiseadmeid kasutaja käskude järgi.

Saadaolevad toimingud (vasta AINULT JSON-iga):
- {"action":"turn_on","entity_id":"...","color":"värv"}
- {"action":"turn_off","entity_id":"..."}
- {"action":"set_color","entity_id":"...","color":"värv"}
- {"action":"set_brightness","entity_id":"...","brightness":0-255}
- {"action":"get_state","entity_id":"..."}

Seadmed:
- light.elutuba — Elutoa lamp (RGB, heledus)
- light.magamistuba — Magamistoa lamp (RGB, heledus)
- switch.kohvimasin — Kohvimasin (sees/väljas)
- sensor.temperatuur — Toa temperatuuri andur
- sensor.kellaaeg — Praegune kellaaeg

Vasta: {"actions":[...],"response":"lühike eestikeelne vastus"}
Kui tuba pole täpsustatud, kasuta elutuba. Vastus olgu lühike (TTS).
"""

SYSTEM_PROMPT_WIZ = """\
Sa oled Kratt, eestikeelne häälassistent. Juhi WiZ lampe kasutaja käskude järgi.

Saadaolevad toimingud (vasta AINULT JSON-iga):
- {"action":"turn_on","entity_id":"...","brightness":0-255,"color":"värvitoon"}
- {"action":"turn_off","entity_id":"..."}
- {"action":"set_brightness","entity_id":"...","brightness":0-255}
- {"action":"set_color","entity_id":"...","color":"värvitoon"}
- {"action":"get_state","entity_id":"..."}
- {"action":"list_devices"}

Seadmed (päris WiZ lambid):
- light.wiz_1 — WiZ pirn 1 (heledus, värvitemperatuur)
- light.wiz_2 — WiZ pirn 2 (heledus, värvitemperatuur)

Värvitoonid: "soe valge" (2700K), "neutraalne" (4000K), "päevavalgus" (5000K), "külm valge" (6500K), "öövalgus" (2200K).

Vasta: {"actions":[...],"response":"lühike eestikeelne vastus"}
Kui pirn pole täpsustatud, mõjuta mõlemat. Vastus olgu lühike (TTS).
"""

SYSTEM_PROMPT_WIZ_PROTOCOL = """\
Klassifitseeri kasutaja eestikeelne lause täpselt ühe sildiga loetelust:
OFF, ON, COLOR <värvus>, DIM, BRIGHTEN, BRIGHT <0-255>, STATE, TIME [±minutid], DATE [±päevad], WEATHER [koht], NONE.

Reeglid:
- "tuli/lamp/pirn/valgus" tähistab ainult sihtmärki, mitte käsku.
- ON ainult kui tekstis on: põlema, põle, põleda, sisse, tööle, lülita sisse, peale.
- OFF kui tekstis on: kustu, kustuta, välja, ära, kinni, sulge, pimedaks. (NB: "ära" + tegusõna LAUSE ALGUSES on eitus → NONE, vt allpool.)
- COLOR <värvus> kui ilmub värvisõna. Värvused: sinine, punane, roheline, kollane, lilla, roosa, oranž, valge, soe valge, külm valge, neutraalne. Käände vormid taanda algkujule (siniseks→sinine, valgeks→valge, roosaks→roosa, lillaks→lilla, oranžiks→oranž, kollaseks→kollane).
- "soojemaks/soojem" → COLOR soe valge. "külmemaks/külmem" → COLOR külm valge.
- DIM kui kasutaja kurdab et liiga hele/ere/valge või palub vähemaks/madalamaks/tumedamaks/hämaramaks/dimmida.
- BRIGHTEN kui kasutaja kurdab et liiga tume/hämar, ei näe, on pime, või palub heledamaks/valgemaks/eredamaks/juurde.
- NB! "valgemaks/valgem" tähendab eredamat valgust → BRIGHTEN (mitte COLOR valge).
- NB! "valgust juurde/rohkem" → BRIGHTEN (mitte COLOR).
- "liiga hämar" → BRIGHTEN ("hämar" = liiga vähe valgust).
- BRIGHT <number> ainult kui kasutaja annab numbri.
- STATE küsimuste puhul: "kas tuli põleb", "mis seisus lamp", "kas X töötab".
- TIME ainult kella-küsimustele. "kahe tunni pärast"=+120, "tunni pärast"=+60, "poole tunni pärast"=+30, "kümne minuti pärast"=+10. "tagasi/oli"=negatiivne.
- DATE ainult kuupäeva/päeva-küsimustele. "homme"=+1, "eile"=-1, "N päeva pärast"=+N.
- WEATHER kui ilmub: ilm, ilmateade, sajab, vihm, lumi, väljas, temperatuur, jope, "kui külm/soe väljas". Vaikimisi koht: Tallinn. Käänded: Tallinnas→Tallinn, Tartus→Tartu, Pärnus→Pärnu.
- NONE kui:
  * Lause ALGAB "ära" + tegusõnaga ("ära pane", "ära kustuta", "ära muuda", "ära tee") → NONE.
  * Lauses on "ütlesin ära" / "ma keelasin" / "ma ei taha" → NONE.
  * Äratus ("ärata mind"), taimer ("pane taimer"), tervitus, nali, muusika, uks → NONE.

Vasta JSON-objektina: {"cmd":"<silt>","arg":"<lisaargument või tühi>"}.
arg sisaldab värvi (COLOR), kohta (WEATHER), numbrit (BRIGHT/TIME/DATE) või on tühi.

Näited (kasutaja sisend → JSON väljund):
pane tuli kustu -> {"cmd":"OFF","arg":""}
pane tuli kinni -> {"cmd":"OFF","arg":""}
kustuta tuli ära -> {"cmd":"OFF","arg":""}
kustuta valgus -> {"cmd":"OFF","arg":""}
ole hea kustuta lamp ära -> {"cmd":"OFF","arg":""}
pane tuli põlema -> {"cmd":"ON","arg":""}
tuli sisse -> {"cmd":"ON","arg":""}
valgust palun -> {"cmd":"ON","arg":""}
pane valgus peale -> {"cmd":"ON","arg":""}
tuli võiks põleda -> {"cmd":"ON","arg":""}
mis kell on -> {"cmd":"TIME","arg":""}
mis ilm on -> {"cmd":"WEATHER","arg":"Tallinn"}
mis kuupäev täna on -> {"cmd":"DATE","arg":""}
kas tuli põleb -> {"cmd":"STATE","arg":""}
mis seisus lamp on -> {"cmd":"STATE","arg":""}
mängi muusikat -> {"cmd":"NONE","arg":""}
liiga hele -> {"cmd":"DIM","arg":""}
liiga ere -> {"cmd":"DIM","arg":""}
liiga valge -> {"cmd":"DIM","arg":""}
tee tuba pimedaks -> {"cmd":"DIM","arg":""}
tee natuke tumedamaks -> {"cmd":"DIM","arg":""}
tee hämaramaks -> {"cmd":"DIM","arg":""}
vähenda heledust -> {"cmd":"DIM","arg":""}
keera valgust vähemaks -> {"cmd":"DIM","arg":""}
valgust vähemaks -> {"cmd":"DIM","arg":""}
dimmi tuli ära -> {"cmd":"DIM","arg":""}
liiga tume -> {"cmd":"BRIGHTEN","arg":""}
liiga hämar -> {"cmd":"BRIGHTEN","arg":""}
suurenda heledust -> {"cmd":"BRIGHTEN","arg":""}
tee heledamaks -> {"cmd":"BRIGHTEN","arg":""}
tee valgemaks -> {"cmd":"BRIGHTEN","arg":""}
tuba võiks valgem olla -> {"cmd":"BRIGHTEN","arg":""}
valgust juurde -> {"cmd":"BRIGHTEN","arg":""}
keera valgust juurde -> {"cmd":"BRIGHTEN","arg":""}
ma ei näe midagi -> {"cmd":"BRIGHTEN","arg":""}
mul on pime -> {"cmd":"BRIGHTEN","arg":""}
pane tuli siniseks -> {"cmd":"COLOR","arg":"sinine"}
pane tuli valgeks -> {"cmd":"COLOR","arg":"valge"}
tee tuba valgeks -> {"cmd":"COLOR","arg":"valge"}
valge valgus -> {"cmd":"COLOR","arg":"valge"}
oranz tuli -> {"cmd":"COLOR","arg":"oranž"}
tee tuli roosaks -> {"cmd":"COLOR","arg":"roosa"}
tee tuli oranžiks -> {"cmd":"COLOR","arg":"oranž"}
tee tuli lillaks -> {"cmd":"COLOR","arg":"lilla"}
tee valgus soojemaks -> {"cmd":"COLOR","arg":"soe valge"}
tee valgus külmemaks -> {"cmd":"COLOR","arg":"külm valge"}
ma tahan sinist valgust -> {"cmd":"COLOR","arg":"sinine"}
kui külm väljas on -> {"cmd":"WEATHER","arg":"Tallinn"}
kas ma peaks jope panema -> {"cmd":"WEATHER","arg":"Tallinn"}
ilm Tallinnas -> {"cmd":"WEATHER","arg":"Tallinn"}
milline ilm Tallinnas on -> {"cmd":"WEATHER","arg":"Tallinn"}
pärnu ilm -> {"cmd":"WEATHER","arg":"Pärnu"}
palju kell poole tunni pärast on -> {"cmd":"TIME","arg":"+30"}
mis kell oli kümme minutit tagasi -> {"cmd":"TIME","arg":"-10"}
mis kell oli kaks tundi tagasi -> {"cmd":"TIME","arg":"-120"}
ära pane tuld põlema -> {"cmd":"NONE","arg":""}
ära kustuta tuld -> {"cmd":"NONE","arg":""}
ära muuda valgust -> {"cmd":"NONE","arg":""}
ära tee midagi -> {"cmd":"NONE","arg":""}
ma ütlesin ära pane siniseks -> {"cmd":"NONE","arg":""}
ärata mind kahe tunni pärast -> {"cmd":"NONE","arg":""}
pane taimer viieks minutiks -> {"cmd":"NONE","arg":""}
"""

SYSTEM_PROMPT_WIZ_INTENT_EXPERT = """\
You are a fast tool-call parser for an Estonian smart-light assistant.
Input is noisy STT; words may be misspelled, joined together, or inflected.
Infer the user's likely intent. Return ONLY JSON: {"actions":[...],"response":"short Estonian TTS reply"}

Each action object:
- action: one of "turn_on", "turn_off", "set_brightness", "set_color", "get_state", "list_devices"
- entity_id: one of "all", "light.wiz_1", "light.wiz_2". Default: "all".
- brightness: integer 0..255 only for set_brightness/turn_on if asked.
- color: simple Estonian color only for set_color/turn_on if asked.

Meaning hints:
- tuli/lamp/pirn/valgus/valgustus = WiZ light.
- kustu/kustuta/välja/ära/off = turn_off.
- põlema/põle/sisse/tööle/on = turn_on.
- punane/roheline/sinine/kollane/lilla/roosa/oranž/soe valge/külm valge/neutraalne = color.
- Estonian color inflections map to base color: sinise/siniseks/sinist -> sinine; punase/punaseks -> punane; rohelise/roheliseks -> roheline; kollase/kollaseks -> kollane; lilla/lillaks -> lilla.
- If the utterance contains a color word and a light word, prefer set_color over turn_on.
- If likely light intent is clear despite STT errors, create the action.
- actions=[] only if there is no executable light/device intent.
- response should be what Kratt says if the action succeeds.
- If actions=[], response must NOT claim success; ask briefly to clarify.

Examples:
pane tuli kustu -> {"actions":[{"action":"turn_off","entity_id":"all"}],"response":"Tuli on kustutatud."}
pantuli kustu -> {"actions":[{"action":"turn_off","entity_id":"all"}],"response":"Tuli on kustutatud."}
pane tuli põlema -> {"actions":[{"action":"turn_on","entity_id":"all"}],"response":"Tuli põleb."}
pane tuli siniseks -> {"actions":[{"action":"set_color","entity_id":"all","color":"sinine"}],"response":"Tuli on sinine."}
pane tuli sinise -> {"actions":[{"action":"set_color","entity_id":"all","color":"sinine"}],"response":"Tuli on sinine."}
"""

SYSTEM_PROMPT_WIZ_BASH = """\
Sa oled Kratt. Teisenda kasutaja eestikeelne käsk bash-käsuks, mis juhib WiZ lampe läbi `wiz` CLI.

Vasta AINULT JSON kujul:
{"command":"...","response":"..."}

Reeglid:
- `command` võib sisaldada bash control-flow'd (`for`, `&&`, `;`, `sleep`, jne)
- Eelista `wiz` käske (`wiz on/off/color/brightness/temp/scene/disco/chase/pulse/stop/status/list`)
- Väldi lõpmatuid loop'e; kasuta mõistlikku lõpp-tingimust või kestust
- ÄRA kasuta failisüsteemi käske ega süsteemi muutvaid käske
- Kui käsk ebaselge, jäta `command` tühjaks ja vasta lühikese seletusega `response`
"""


def build_wiz_system_prompt(bulb_count: int | None = None) -> str:
    """Return WiZ prompt with the actual number of configured bulbs when known."""
    if not bulb_count or bulb_count <= 0:
        return SYSTEM_PROMPT_WIZ
    devices = "\n".join(
        f"- light.wiz_{i} — WiZ pirn {i} (heledus, värvitemperatuur)"
        for i in range(1, bulb_count + 1)
    )
    default_rule = (
        "Kui pirn pole täpsustatud, kasuta light.wiz_1."
        if bulb_count == 1
        else "Kui pirn pole täpsustatud, mõjuta kõiki loetletud pirne."
    )
    return re.sub(
        r"Seadmed \(päris WiZ lambid\):\n(?:- light\.wiz_\d+.*\n)+",
        f"Seadmed (päris WiZ lambid):\n{devices}\n",
        SYSTEM_PROMPT_WIZ,
    ).replace("Kui pirn pole täpsustatud, mõjuta mõlemat.", default_rule)

DISALLOWED_BASH_RE = re.compile(r"(^|[;|&()\s])(rm|cp|mv)(?=($|[;|&()\s]))")


def _cached_wiz_bulbs() -> str | None:
    """Return comma-separated WiZ IPs from KRATT_WIZ_BULBS or wiz-cli cache."""
    if os.getenv("KRATT_WIZ_BULBS"):
        return os.getenv("KRATT_WIZ_BULBS")
    try:
        with open("/tmp/wiz_bulbs.json") as f:
            bulbs = json.load(f)
        ips = [b.get("ip") for b in bulbs if b.get("ip")]
        return ",".join(ips) if ips else None
    except Exception:
        return None


def apply_demo_profile(args) -> None:
    """Collapse long demo command lines into named profiles."""
    if not args.profile:
        return

    if args.profile == "demo":
        args.claude_code = False
        args.wiz = True
        args.ble_bridge = True
        args.models = args.models or ["v16c"]
        if args.threshold == [0.97]:
            args.threshold = [0.996]

    elif args.profile == "wiz-claude":
        args.claude_code = True
        args.wiz = True
        args.models = args.models or ["v16c"]
        if args.threshold == [0.97]:
            args.threshold = [0.996]
        args.bulbs = args.bulbs or _cached_wiz_bulbs()

    elif args.profile == "wiz-claude-safe":
        args.claude_code = True
        args.wiz = True
        args.models = args.models or ["v16c"]
        if args.threshold == [0.97]:
            args.threshold = [0.997]
        args.wake_hold_frames = max(args.wake_hold_frames, 5)
        args.wake_model_cooldown = max(args.wake_model_cooldown, 6.0)
        args.post_trigger_cooldown = max(args.post_trigger_cooldown, 6.0)
        args.bulbs = args.bulbs or _cached_wiz_bulbs()

    elif args.profile == "wiz-manual":
        args.claude_code = False
        args.wiz = True
        args.ble_bridge = True
        args.no_wakeword = True

    elif args.profile == "wiz-7b":
        # Higher-accuracy LLM (qwen2.5:7b ~98.6% intent acc, ~700ms warm) for UX trials
        args.claude_code = False
        args.wiz = True
        args.ble_bridge = True
        args.llm = "qwen2.5:7b"
        args.models = args.models or ["v16c"]
        if args.threshold == [0.97]:
            args.threshold = [0.996]


def _sanitize_wiz_bash_command(raw: str) -> str:
    cmd = (raw or "").strip()
    if not cmd:
        return ""
    if DISALLOWED_BASH_RE.search(cmd):
        return ""
    # map leading "wiz" to absolute path at execution time
    return cmd


def llm_plan_wiz_command(user_text: str) -> dict:
    if USE_PI_CLI:
        data = pi_cli_json(SYSTEM_PROMPT_WIZ_BASH, user_text)
    elif USE_CLAUDE_CODE:
        data = claude_code_json(SYSTEM_PROMPT_WIZ_BASH, user_text)
    else:
        resp = OLLAMA_SESSION.post(
            OLLAMA_URL,
            json={
                "model": LLM_MODEL,
                "stream": False,
                "format": "json",
                "keep_alive": OLLAMA_KEEP_ALIVE,
                "options": OLLAMA_JSON_OPTIONS,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT_WIZ_BASH},
                    {"role": "user", "content": user_text},
                ],
            },
        )
        resp.raise_for_status()
        data = json.loads(resp.json()["message"]["content"])
    command = _sanitize_wiz_bash_command(data.get("command", ""))
    return {"command": command, "response": data.get("response", "")}


def _resolve_wiz_aliases(command: str) -> str:
    return re.sub(r"\bwiz\b", shlex.quote(str(WIZ_CLI)), command)


def execute_wiz_cli_command(command: str) -> tuple[str, int]:
    resolved = _resolve_wiz_aliases(command)
    proc = subprocess.run(
        resolved,
        shell=True,
        capture_output=True,
        text=True,
        timeout=45,
    )
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    text = out if out else err
    return text, proc.returncode


def build_fallback_response_for_wiz(command: str, rc: int) -> str:
    if rc == 0:
        return "Käsk täidetud."
    return "Käsk ebaõnnestus."


def execute_wiz_bash_mode(transcript: str) -> tuple[str, str, str, bool]:
    """Returns (command, cli_result, response, ok)."""
    plan = llm_plan_wiz_command(transcript)
    command = plan.get("command", "")
    if not command:
        msg = plan.get("response", "Vabandust, ma ei saanud käsku turvaliselt täita.")
        return "", "", msg, False

    cli_out, rc = execute_wiz_cli_command(command)
    ok = rc == 0
    response = plan.get("response") or build_fallback_response_for_wiz(command, rc)
    return command, cli_out, response, ok


# BLE bridge path (ESP32 GATT sink + UDP forward)
BLE_BRIDGE_DIR = PROJECT_ROOT / "tools" / "ble-wiz-bridge"
WIZ_BRIDGE_DEFAULT_PORT = 38899
WIZ_BRIDGE_DEFAULT_BULB_IP = "auto"
WIZ_BRIDGE_COLOR_MAP = {
    "soe valge": 2700,
    "warm white": 2700,
    "soe": 2700,
    "warm": 2700,
    "neutraalne": 4000,
    "neutral": 4000,
    "külm valge": 6500,
    "cool white": 6500,
    "päevavalgus": 5000,
    "daylight": 5000,
    "öövalgus": 2200,
    "night": 2200,
    "red": (255, 0, 0),
    "punane": (255, 0, 0),
    "green": (0, 255, 0),
    "roheline": (0, 255, 0),
    "blue": (0, 0, 255),
    "sinine": (0, 0, 255),
    "yellow": (255, 255, 0),
    "kollane": (255, 255, 0),
    "purple": (180, 0, 255),
    "lilla": (180, 0, 255),
    "cyan": (0, 255, 255),
    "orange": (255, 120, 0),
    "oranž": (255, 120, 0),
    "pink": (255, 30, 140),
    "roosa": (255, 30, 140),
    "white": (255, 255, 255),
    "valge": (255, 255, 255),
}


_WIZ_BRIDGE_SENDER = None
_WIZ_BRIDGE_RESPONSE_SENDER = None
_WIZ_BRIDGE_WARMER = None


def _get_default_wiz_bridge_bulb_ip() -> str:
    if not BLE_BRIDGE_DIR.exists():
        return WIZ_BRIDGE_DEFAULT_BULB_IP

    if str(BLE_BRIDGE_DIR) not in sys.path:
        sys.path.append(str(BLE_BRIDGE_DIR))

    try:
        from bridge import WIZ_BRIDGE_DEFAULT_BULB_IP as bridge_default_ip
    except Exception:
        return WIZ_BRIDGE_DEFAULT_BULB_IP
    return bridge_default_ip or WIZ_BRIDGE_DEFAULT_BULB_IP


def _load_ble_bridge_sender():
    global _WIZ_BRIDGE_SENDER
    global _WIZ_BRIDGE_RESPONSE_SENDER
    global _WIZ_BRIDGE_WARMER
    global WIZ_BRIDGE_DEFAULT_BULB_IP
    if _WIZ_BRIDGE_SENDER is not None:
        return _WIZ_BRIDGE_SENDER

    if not BLE_BRIDGE_DIR.exists():
        raise RuntimeError(f"BLE bridge path missing: {BLE_BRIDGE_DIR}")

    if str(BLE_BRIDGE_DIR) not in sys.path:
        sys.path.append(str(BLE_BRIDGE_DIR))

    from bridge import (
        WIZ_BRIDGE_DEFAULT_BULB_IP as bridge_default_ip,
        send_wiz_via_ble,
        send_wiz_via_ble_response,
        warm_ble_bridge,
    )
    if bridge_default_ip:
        WIZ_BRIDGE_DEFAULT_BULB_IP = bridge_default_ip

    _WIZ_BRIDGE_SENDER = send_wiz_via_ble
    _WIZ_BRIDGE_RESPONSE_SENDER = send_wiz_via_ble_response
    _WIZ_BRIDGE_WARMER = warm_ble_bridge
    return _WIZ_BRIDGE_SENDER


def _load_ble_bridge_response_sender():
    _load_ble_bridge_sender()
    return _WIZ_BRIDGE_RESPONSE_SENDER


def _warm_ble_bridge_connection() -> bool:
    _load_ble_bridge_sender()
    if _WIZ_BRIDGE_WARMER is None:
        return True
    return bool(_WIZ_BRIDGE_WARMER())


def _parse_bulb_ips(raw: str | None) -> list[str]:
    if not raw:
        return []
    ips: list[str] = []
    for item in raw.split(","):
        ip = item.strip()
        if not ip:
            continue
        if ip.lower() == "auto":
            ips.append("auto")
            continue
        # validate early and keep as canonical dotted string
        obj = ipaddress.ip_address(ip)
        if obj.version != 4:
            raise ValueError(f"Invalid IPv4 bulb address: {ip}")
        ips.append(ip)
    return ips


def _resolve_bulb_targets(entity_id: str | None, bulb_ips: list[str]) -> tuple[list[str], str | None]:
    if not bulb_ips:
        return [], "No bulb IPs configured. Set --bulbs or cache with --wiz discovery first."

    if not entity_id:
        if len(bulb_ips) == 1:
            return bulb_ips, None
        return [], "Multiple bulbs found. Specify entity_id (light.wiz_1, light.wiz_2, all)."

    ent = (entity_id or "").strip().lower()
    if ent == "all":
        return bulb_ips, None

    if ent.startswith("light."):
        ent = ent[len("light."):]

    if ent.startswith("wiz_"):
        ent = ent[4:]

    if ent.isdigit():
        idx = int(ent)
        if 1 <= idx <= len(bulb_ips):
            return [bulb_ips[idx - 1]], None
        return [], f"Bulb index out of range: {idx}"

    if ent in ("light", "bulb"):
        return [], "Use a concrete entity_id for BLE path: light.wiz_1 / light.wiz_2 / all"

    return [], f"Unknown bulb target: {entity_id}"


def _brightness_to_wiz(value: int) -> int:
    return max(10, min(100, round((value / 255) * 100)))


def _apply_wiz_color(params: dict[str, Any], raw_color: Any) -> str | None:
    color = WIZ_BRIDGE_COLOR_MAP.get(str(raw_color).lower())
    if color is None:
        return f"Unsupported color: {raw_color}"
    if isinstance(color, tuple):
        params.update({"r": color[0], "g": color[1], "b": color[2]})
    else:
        params["temp"] = color
    return None


def _build_wiz_payload(action_name: str, action: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    if action_name == "turn_on":
        params: dict[str, int | bool] = {"state": True}
        if "brightness" in action:
            params["dimming"] = _brightness_to_wiz(int(action["brightness"]))
        if "color" in action:
            color_error = _apply_wiz_color(params, action["color"])
            if color_error:
                return {}, color_error
        return {"method": "setPilot", "params": params}, None

    if action_name == "turn_off":
        return {"method": "setPilot", "params": {"state": False}}, None

    if action_name == "set_brightness":
        if "brightness" not in action:
            return {}, "set_brightness missing brightness"
        params = {"state": True, "dimming": _brightness_to_wiz(int(action["brightness"]))}
        return {"method": "setPilot", "params": params}, None

    if action_name == "set_color":
        params: dict[str, Any] = {"state": True}
        color_error = _apply_wiz_color(params, action.get("color", ""))
        if color_error:
            return {}, color_error
        return {"method": "setPilot", "params": params}, None

    if action_name == "get_state":
        return {"method": "getPilot", "params": {}}, None

    return {}, f"Unsupported action for BLE path: {action_name}"



_HOUR_NOMINATIVE = {
    1: "üks",
    2: "kaks",
    3: "kolm",
    4: "neli",
    5: "viis",
    6: "kuus",
    7: "seitse",
    8: "kaheksa",
    9: "üheksa",
    10: "kümme",
    11: "üksteist",
    12: "kaksteist",
}

_HOUR_GENITIVE = {
    1: "ühe",
    2: "kahe",
    3: "kolme",
    4: "nelja",
    5: "viie",
    6: "kuue",
    7: "seitsme",
    8: "kaheksa",
    9: "üheksa",
    10: "kümne",
    11: "üheteistkümne",
    12: "kaheteistkümne",
}

_NUMBER_NOMINATIVE = {
    1: "üks",
    2: "kaks",
    3: "kolm",
    4: "neli",
    5: "viis",
    6: "kuus",
    7: "seitse",
    8: "kaheksa",
    9: "üheksa",
    10: "kümme",
    11: "üksteist",
    12: "kaksteist",
    13: "kolmteist",
    14: "neliteist",
    15: "viisteist",
    16: "kuusteist",
    17: "seitseteist",
    18: "kaheksateist",
    19: "üheksateist",
    20: "kakskümmend",
}

_NUMBER_GENITIVE = {
    1: "ühe",
    2: "kahe",
    3: "kolme",
    4: "nelja",
    5: "viie",
    6: "kuue",
    7: "seitsme",
    8: "kaheksa",
    9: "üheksa",
    10: "kümne",
    11: "üheteistkümne",
    12: "kaheteistkümne",
    13: "kolmeteistkümne",
    14: "neljateistkümne",
    15: "viieteistkümne",
    16: "kuueteistkümne",
    17: "seitsmeteistkümne",
    18: "kaheksateistkümne",
    19: "üheksateistkümne",
    20: "kahekümne",
}


def number_nom_et(n: int) -> str:
    if n <= 20:
        return _NUMBER_NOMINATIVE.get(n, str(n))
    if n < 30:
        return f"kakskümmend {_NUMBER_NOMINATIVE[n - 20]}"
    return str(n)


def number_gen_et(n: int) -> str:
    if n <= 20:
        return _NUMBER_GENITIVE.get(n, str(n))
    if n < 30:
        return f"kahekümne {_NUMBER_GENITIVE[n - 20]}"
    return str(n)


def natural_time_et(now: datetime | None = None) -> str:
    """Return a TTS-friendly Estonian time phrase for the supplied/current minute."""
    now = now or datetime.now().astimezone()
    hour = now.hour % 12 or 12
    minute = now.minute
    next_hour = (hour % 12) + 1

    if minute == 0:
        return f"Kell on {_HOUR_NOMINATIVE[hour]}."
    if minute == 15:
        return f"Kell on veerand {_HOUR_NOMINATIVE[next_hour]}."
    if minute == 30:
        return f"Kell on pool {_HOUR_NOMINATIVE[next_hour]}."
    if minute == 45:
        return f"Kell on kolmveerand {_HOUR_NOMINATIVE[next_hour]}."
    if minute < 30:
        minute_word = number_nom_et(minute)
        unit = "minut" if minute == 1 else "minutit"
        return f"Kell on {minute_word} {unit} üle {_HOUR_GENITIVE[hour]}."

    minutes_to_next = 60 - minute
    minute_word = number_gen_et(minutes_to_next)
    return f"Kell on {minute_word} minuti pärast {_HOUR_NOMINATIVE[next_hour]}."


def time_response_et(offset_minutes: int = 0) -> str:
    target = datetime.now().astimezone() + timedelta(minutes=offset_minutes)
    phrase = natural_time_et(target)
    if offset_minutes == 0:
        return phrase
    prefix = "Kell on "
    if phrase.startswith(prefix):
        verb = "oli" if offset_minutes < 0 else "on"
        return f"Siis {verb} kell " + phrase[len(prefix):]
    return phrase


_DATE_ORDINAL = {
    1: "esimene",
    2: "teine",
    3: "kolmas",
    4: "neljas",
    5: "viies",
    6: "kuues",
    7: "seitsmes",
    8: "kaheksas",
    9: "üheksas",
    10: "kümnes",
    11: "üheteistkümnes",
    12: "kaheteistkümnes",
    13: "kolmeteistkümnes",
    14: "neljateistkümnes",
    15: "viieteistkümnes",
    16: "kuueteistkümnes",
    17: "seitsmeteistkümnes",
    18: "kaheksateistkümnes",
    19: "üheksateistkümnes",
    20: "kahekümnes",
    21: "kahekümne esimene",
    22: "kahekümne teine",
    23: "kahekümne kolmas",
    24: "kahekümne neljas",
    25: "kahekümne viies",
    26: "kahekümne kuues",
    27: "kahekümne seitsmes",
    28: "kahekümne kaheksas",
    29: "kahekümne üheksas",
    30: "kolmekümnes",
    31: "kolmekümne esimene",
}

_MONTH_ET = {
    1: "jaanuar",
    2: "veebruar",
    3: "märts",
    4: "aprill",
    5: "mai",
    6: "juuni",
    7: "juuli",
    8: "august",
    9: "september",
    10: "oktoober",
    11: "november",
    12: "detsember",
}

_WEEKDAY_ET = {
    0: "esmaspäev",
    1: "teisipäev",
    2: "kolmapäev",
    3: "neljapäev",
    4: "reede",
    5: "laupäev",
    6: "pühapäev",
}


def natural_date_et(offset_days: int = 0, now: datetime | None = None) -> str:
    target = (now or datetime.now().astimezone()) + timedelta(days=offset_days)
    day = _DATE_ORDINAL.get(target.day, str(target.day))
    month = _MONTH_ET[target.month]
    weekday = _WEEKDAY_ET[target.weekday()]
    if offset_days == 0:
        return f"Täna on {weekday}, {day} {month}."
    return f"Siis on {weekday}, {day} {month}."


_WEATHER_CODE_ET = {
    0: "selge",
    1: "peamiselt selge",
    2: "osaliselt pilves",
    3: "pilves",
    45: "udune",
    48: "härmase uduga",
    51: "kerge uduvihm",
    53: "uduvihm",
    55: "tugev uduvihm",
    61: "kerge vihm",
    63: "vihmane",
    65: "tugev vihm",
    71: "kerge lumesadu",
    73: "lumesadu",
    75: "tugev lumesadu",
    80: "hoovihm",
    81: "tugev hoovihm",
    82: "väga tugev hoovihm",
    95: "äike",
    96: "äike ja rahe",
    99: "tugev äike ja rahe",
}


def _weather_code_et(code: int | None) -> str:
    if code is None:
        return "ilm teadmata"
    return _WEATHER_CODE_ET.get(int(code), "ilm teadmata")


def place_inessive_et(place: str) -> str:
    name = (place or "").strip()
    lower = name.lower()
    if lower == "tallinn":
        return "Tallinnas"
    if lower in ("tartu", "pärnu", "parnu", "võru", "voru"):
        return f"{name}s"
    if lower.endswith("s"):
        return name
    return f"{name}s"


def normalize_place_et(place: str | None) -> str:
    name = (place or "").strip()
    lower = name.lower()
    known = {
        "tallinnas": "Tallinn",
        "tallinn": "Tallinn",
        "tartus": "Tartu",
        "tartu": "Tartu",
        "pärnus": "Pärnu",
        "parnus": "Pärnu",
        "pärnu": "Pärnu",
        "parnu": "Pärnu",
    }
    return known.get(lower, name)


def weather_response_et(place: str | None = None) -> str:
    """Fetch current weather via Open-Meteo, no API key required."""
    place = normalize_place_et(place or DEFAULT_WEATHER_LOCATION) or DEFAULT_WEATHER_LOCATION
    try:
        geo = WEATHER_SESSION.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": place, "count": 1, "language": "et", "format": "json"},
            timeout=4,
        )
        geo.raise_for_status()
        results = geo.json().get("results") or []
        if not results:
            return f"Ma ei leidnud ilma asukoha {place} kohta."
        loc = results[0]
        loc_name = loc.get("name") or place
        loc_phrase = place_inessive_et(loc_name)
        forecast = WEATHER_SESSION.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": loc["latitude"],
                "longitude": loc["longitude"],
                "current": "temperature_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
                "timezone": "auto",
            },
            timeout=4,
        )
        forecast.raise_for_status()
        current = forecast.json().get("current") or {}
        temp = round(float(current.get("temperature_2m")))
        apparent = round(float(current.get("apparent_temperature", temp)))
        wind = round(float(current.get("wind_speed_10m", 0)))
        precipitation = float(current.get("precipitation", 0) or 0)
        description = _weather_code_et(current.get("weather_code"))
        rain_part = " Sajab." if precipitation > 0 else " Sademeid hetkel ei ole."
        return (
            f"{loc_phrase} on praegu {temp} kraadi ja {description}. "
            f"Tundub nagu {apparent} kraadi. Tuul on {wind} kilomeetrit tunnis."
            f"{rain_part}"
        )
    except Exception:
        return "Ilmateadet ei saanud praegu kätte."


def demo_response_for_action(action_name: str, action: dict[str, Any] | None = None) -> str:
    action = action or {}
    if action_name == "turn_off":
        return "Tuli on kustutatud."
    if action_name == "turn_on":
        return "Tuli põleb."
    if action_name == "set_color":
        color = str(action.get("color", "")).strip()
        return f"Tuli on {color}." if color else "Värv muudetud."
    if action_name == "set_brightness":
        return "Heledus muudetud."
    if action_name == "get_state":
        return "Vaatan olekut."
    if action_name == "list_devices":
        return "Vaatan seadmeid."
    return "Tehtud."


def _format_ble_state_response(response: dict[str, Any] | None) -> str:
    if not response:
        return "Tule olekut ei saanud küsida."
    if response.get("state_valid"):
        state = bool(response.get("state"))
        dimming = response.get("dimming")
        if state and isinstance(dimming, int) and dimming >= 0:
            return f"Tuli põleb, heledus on {dimming} protsenti."
        return "Tuli põleb." if state else "Tuli on kustutatud."
    if response.get("response_ok") is False:
        return "Käsu saatsin, aga WiZ pirn ei vastanud."
    raw = str(response.get("last_response") or response.get("raw") or "").strip()
    return f"WiZ vastus: {raw[:120]}" if raw else "Tule olek on teadmata."


def execute_wiz_ble_action(action_name: str, action: dict[str, Any], bulb_ips: list[str]) -> tuple[str, bool]:
    try:
        send = _load_ble_bridge_sender()
    except Exception as exc:
        return f"BLE bridge unavailable: {exc}", False

    targets, target_error = _resolve_bulb_targets(action.get("entity_id"), bulb_ips)
    if target_error:
        return target_error, False

    payload, payload_error = _build_wiz_payload(action_name, action)
    if payload_error:
        return payload_error, False

    if action_name == "get_state":
        send_response = _load_ble_bridge_response_sender()
        if send_response is None:
            return "BLE bridge response path unavailable", False
        responses: list[dict[str, Any]] = []
        failed: list[str] = []
        for ip in targets:
            response = send_response(ip, payload, port=WIZ_BRIDGE_DEFAULT_PORT)
            if response is None:
                failed.append(ip)
            else:
                responses.append(response)
        if failed:
            return f"Failed to query BLE state from: {', '.join(failed)}", False
        if len(responses) == 1:
            return _format_ble_state_response(responses[0]), True
        on_count = sum(1 for r in responses if r.get("state_valid") and r.get("state"))
        known_count = sum(1 for r in responses if r.get("state_valid"))
        if known_count:
            return f"{on_count}/{known_count} WiZ tuld põleb.", True
        return "WiZ tulede olek on teadmata.", True

    failed: list[str] = []
    for ip in targets:
        if not send(ip, payload, port=WIZ_BRIDGE_DEFAULT_PORT):
            failed.append(ip)

    if failed:
        return f"Failed to send BLE command to: {', '.join(failed)}", False

    if len(targets) == 1:
        return f"Sent WiZ command to {targets[0]}", True

    return f"Sent WiZ command to {len(targets)} bulbs", True


# ============================================================
# Streaming wake word model (from multi_model_live_test.py)
# ============================================================


class StreamingModel:
    """Single TFLite wake word model with moving-average smoothing."""

    def __init__(
        self,
        name: str,
        tflite_path: str,
        threshold: float,
        color: str = "",
        use_ma: bool = True,
    ):
        self.name = name
        self.threshold = threshold
        self.color = color
        self.use_ma = use_ma
        self.interpreter = tflite.Interpreter(model_path=tflite_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.audio_input_idx = 0
        self.detection_count = 0
        self.last_detection_time = 0.0
        self.cooldown_s = 2.0
        self.warmup_frames = 50
        self.required_consecutive = 1
        self.consecutive_hits = 0
        self.frame_count = 0
        self.scores: list[float] = []

        self.reset()

    def reset(self):
        """Reset model state and counters for a fresh detection cycle."""
        # The wake model is stateful. Clearing only input tensors leaves TFLite
        # variables hot after a trigger, which can cause an immediate re-trigger
        # when listening resumes. reset_all_variables() is the important part.
        reset_vars = getattr(self.interpreter, "reset_all_variables", None)
        if callable(reset_vars):
            reset_vars()
        for detail in self.input_details:
            self.interpreter.set_tensor(
                detail["index"],
                np.zeros(detail["shape"], dtype=detail["dtype"]),
            )
        self.frame_count = 0
        self.consecutive_hits = 0
        self.scores.clear()

    def process_features(self, features: np.ndarray) -> float | None:
        """Process one spectrogram frame. Returns MA probability on detection."""
        expected_shape = self.input_details[self.audio_input_idx]["shape"]
        features = features.reshape(expected_shape)

        inp_dtype = self.input_details[self.audio_input_idx]["dtype"]
        if inp_dtype == np.int8:
            scale, zp = self.input_details[self.audio_input_idx]["quantization"]
            features = (features / scale + zp).clip(-128, 127).astype(np.int8)

        self.interpreter.set_tensor(
            self.input_details[self.audio_input_idx]["index"], features
        )
        self.interpreter.invoke()
        self.frame_count += 1

        if self.frame_count <= self.warmup_frames:
            return None

        output = self.interpreter.get_tensor(self.output_details[0]["index"])
        out_dtype = self.output_details[0]["dtype"]
        if out_dtype in (np.int8, np.uint8):
            scale, zp = self.output_details[0]["quantization"]
            prob = float(((output.astype(np.float32) - zp) * scale).flat[0])
        else:
            prob = float(output.flatten()[0])

        # Moving average (only when use_ma is set, i.e. multi-model mode)
        self.scores.append(prob)
        if len(self.scores) > MA_WINDOW:
            self.scores.pop(0)
        check_prob = sum(self.scores) / len(self.scores) if self.use_ma else prob

        now = time.monotonic()
        if check_prob >= self.threshold:
            self.consecutive_hits += 1
        else:
            self.consecutive_hits = 0

        if (
            self.consecutive_hits >= self.required_consecutive
            and (now - self.last_detection_time) >= self.cooldown_s
        ):
            self.detection_count += 1
            self.last_detection_time = now
            self.consecutive_hits = 0
            return check_prob

        return None


# ============================================================
# Interaction logger (opt-in via --log flag)
# ============================================================


class InteractionLogger:
    """Append-only JSONL logger for one user testing session."""

    def __init__(
        self,
        enabled: bool,
        participant_id: str,
        log_dir: Path,
        llm_model: str,
        wake_models: list[str],
        wake_threshold: float,
    ):
        self.enabled = enabled
        self.participant_id = participant_id
        self.session_id = uuid.uuid4().hex[:8]
        self.session_start = datetime.now(timezone.utc).isoformat()
        self.llm_model = llm_model
        self.wake_threshold = wake_threshold
        self._interaction_seq = 0
        self._current_task: str | None = None

        if not enabled:
            self.path = None
            return

        log_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.path = log_dir / f"{participant_id}_{ts}_{self.session_id}.jsonl"

        self._write(
            {
                "type": "session_start",
                "session_id": self.session_id,
                "participant_id": participant_id,
                "timestamp": self.session_start,
                "llm_model": llm_model,
                "wake_threshold": wake_threshold,
                "wakeword_models": wake_models,
                "stt_model": STT_MODEL_DIR.name,
                "host": os.uname().nodename,
            }
        )
        print(f"  Logging to {self.path.name}")

    def set_task(self, task_id: str | None):
        self._current_task = task_id
        if self.enabled and task_id:
            self._write(
                {
                    "type": "task_change",
                    "task_id": task_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

    def log_interaction(self, record: dict):
        if not self.enabled:
            return
        self._interaction_seq += 1
        record = {
            "type": "interaction",
            "session_id": self.session_id,
            "participant_id": self.participant_id,
            "task_id": self._current_task,
            "seq": self._interaction_seq,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **record,
        }
        self._write(record)

    def _write(self, record: dict):
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def close(self):
        if not self.enabled:
            return
        self._write(
            {
                "type": "session_end",
                "session_id": self.session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "interaction_count": self._interaction_seq,
            }
        )


class StepTimer:
    """Collect wall-clock + monotonic timestamps for demo latency debugging."""

    def __init__(self, label: str, log_fn=None):
        self.label = label
        self.log_fn = log_fn
        self.started_mono = time.monotonic()
        self.last_mono = self.started_mono
        self.events: list[dict[str, Any]] = []
        self.mark("start")

    @staticmethod
    def _ts() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

    def mark(self, step: str, note: str | None = None) -> None:
        now = time.monotonic()
        event = {
            "step": step,
            "timestamp": self._ts(),
            "since_start_ms": int((now - self.started_mono) * 1000),
            "delta_ms": int((now - self.last_mono) * 1000),
            **({"note": note} if note else {}),
        }
        self.events.append(event)
        self.last_mono = now
        if self.log_fn:
            self._log_event(self.log_fn, event)

    def elapsed_ms(self) -> int:
        return int((time.monotonic() - self.started_mono) * 1000)

    def as_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "total_ms": self.elapsed_ms(),
            "events": self.events,
        }

    @staticmethod
    def _log_event(log_fn, event: dict[str, Any]) -> None:
        note = f" — {event['note']}" if event.get("note") else ""
        log_fn(
            "  [timing] "
            f"{event['timestamp']} "
            f"+{event['since_start_ms']:>5}ms "
            f"Δ{event['delta_ms']:>5}ms "
            f"{event['step']}{note}"
        )

    def log(self, log_fn, title: str | None = None) -> None:
        log_fn(f"  [timing] {title or self.label}: total={self.elapsed_ms()}ms")
        if self.log_fn is None:
            for event in self.events:
                self._log_event(log_fn, event)


# ============================================================
# STT (sherpa-onnx)
# ============================================================


class SpeechRecognizer:
    def __init__(self, model_dir: str):
        import sherpa_onnx

        self.recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
            tokens=f"{model_dir}/tokens.txt",
            encoder=f"{model_dir}/encoder.int8.onnx",
            decoder=f"{model_dir}/decoder.int8.onnx",
            joiner=f"{model_dir}/joiner.int8.onnx",
            num_threads=2,
            sample_rate=SAMPLE_RATE,
            feature_dim=80,
            enable_endpoint_detection=True,
            rule1_min_trailing_silence=2.0,
            rule2_min_trailing_silence=1.0,
            rule3_min_utterance_length=300,
            decoding_method="modified_beam_search",
        )

    def transcribe(self, audio_float32: np.ndarray) -> str:
        stream = self.recognizer.create_stream()
        tail = np.zeros(int(0.3 * SAMPLE_RATE), dtype=np.float32)
        audio = np.concatenate([audio_float32, tail])
        stream.accept_waveform(SAMPLE_RATE, audio)
        while self.recognizer.is_ready(stream):
            self.recognizer.decode_stream(stream)
        return self.recognizer.get_result(stream).strip()


# ============================================================
# TTS (TartuNLP via local HTTP server + sox character voice)
# ============================================================


class TextToSpeech:
    """Synthesize Estonian text via local TTS server, apply sox character
    effects (Kratt voice), and play the result."""

    SOX_EFFECTS = [
        "pitch",
        "200",
        "overdrive",
        "5",
        "10",
        "treble",
        "+2",
        "contrast",
        "30",
        "gain",
        "-2",
    ]

    def __init__(
        self,
        url: str = TTS_URL,
        speaker: str = TTS_SPEAKER,
        speed: float = TTS_SPEED,
        apply_effects: bool = True,
    ):
        self.url = url
        self.speaker = speaker
        self.speed = speed
        self.apply_effects = apply_effects
        self._available: bool | None = None
        self.session = requests.Session()
        self.cache_dir = PROJECT_ROOT / "output" / "tts-cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def is_available(self) -> bool:
        if self._available is None:
            try:
                r = self.session.get(
                    self.url.replace("/synthesize", "/speakers"), timeout=2
                )
                self._available = r.status_code == 200
            except Exception:
                self._available = False
        return self._available

    def _cache_path(self, text: str) -> Path:
        key = hashlib.sha1(
            json.dumps(
                {
                    "text": text,
                    "speaker": self.speaker,
                    "speed": self.speed,
                    "effects": self.apply_effects,
                },
                ensure_ascii=False,
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()[:16]
        return self.cache_dir / f"{key}.wav"

    def prepare(self, text: str) -> Path | None:
        """Synthesize/cache text without playback."""
        if not text or not self.is_available():
            return None
        out_path = self._cache_path(text)
        if out_path.exists() and out_path.stat().st_size > 0:
            return out_path

        import tempfile

        r = self.session.post(
            self.url,
            json={
                "text": text,
                "speaker": self.speaker,
                "speed": self.speed,
            },
            timeout=30,
        )
        r.raise_for_status()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as raw:
            raw.write(r.content)
            raw_path = raw.name

        try:
            if self.apply_effects:
                tmp_out = str(out_path) + f".{uuid.uuid4().hex}.tmp.wav"
                cmd = ["sox", raw_path, tmp_out] + self.SOX_EFFECTS
                subprocess.run(cmd, check=True, capture_output=True)
                os.replace(tmp_out, out_path)
            else:
                os.replace(raw_path, out_path)
                raw_path = ""
        finally:
            if raw_path and os.path.exists(raw_path):
                os.unlink(raw_path)
        return out_path

    def prepare_common_responses(self) -> None:
        for text in (
            "Tuli on kustutatud.",
            "Tuli põleb.",
            "Värv muudetud.",
            "Heledus muudetud.",
            "Tuli on sinine.",
            "Tuli on punane.",
            "Ma ei saanud käsku täita.",
        ):
            try:
                self.prepare(text)
            except Exception:
                pass

    def speak(self, text: str) -> float:
        """Synthesize/cache and play text. Returns duration in seconds."""
        if not text or not self.is_available():
            return 0.0

        t0 = time.monotonic()
        play_path = self.prepare(text)
        if not play_path:
            return 0.0

        # Play audio (blocks until done)
        subprocess.run(["sox", str(play_path), "-d"], capture_output=True)
        return time.monotonic() - t0


# ============================================================
# MCP client
# ============================================================


class MCPClient:
    def __init__(self, server_path: Path, extra_args: list[str] | None = None):
        cmd = [sys.executable, str(server_path)]
        if extra_args:
            cmd.extend(extra_args)
        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        resp = self._send(
            {"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {}}
        )
        server_name = (
            resp.get("result", {}).get("serverInfo", {}).get("name", "unknown")
        )
        print(f"  MCP server: {server_name}")

    def _check_alive(self):
        rc = self.proc.poll()
        if rc is not None:
            stderr = self.proc.stderr.read() if self.proc.stderr else ""
            raise RuntimeError(f"MCP server exited with code {rc}\n{stderr}")

    def _send(self, req: dict) -> dict:
        self._check_alive()
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            self._check_alive()
            return {}
        return json.loads(line) if line.strip() else {}

    def execute(self, action: str, args: dict) -> str:
        resp = self._send(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": action, "arguments": args},
            }
        )
        content = resp.get("result", {}).get("content", [{}])
        return content[0].get("text", "") if content else ""

    def close(self):
        try:
            self.proc.terminate()
            self.proc.wait(timeout=3)
        except Exception:
            self.proc.kill()


# ============================================================
# LLM (Ollama / Claude Code / Pi CLI)
# ============================================================


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
            "--permission-mode",
            "bypassPermissions",
            "--dangerously-skip-permissions",
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
    client = PI_RPC_CLIENTS.get(system_prompt)
    if client is None or client.proc.poll() is not None:
        client = PiRpcClient(system_prompt)
        PI_RPC_CLIENTS[system_prompt] = client
    return client


def close_pi_rpc_clients() -> None:
    for client in list(PI_RPC_CLIENTS.values()):
        client.close()
    PI_RPC_CLIENTS.clear()


def pi_cli_json(system_prompt: str, user_prompt: str) -> dict:
    return get_pi_rpc_client(system_prompt).request_json(user_prompt)


def _protocol_color(value: str) -> str:
    color = (value or "").strip().lower()
    color = color.replace("värv", "").replace("color", "").strip()
    aliases = {
        "sinise": "sinine",
        "siniseks": "sinine",
        "sinist": "sinine",
        "punase": "punane",
        "punaseks": "punane",
        "rohelise": "roheline",
        "roheliseks": "roheline",
        "kollase": "kollane",
        "kollaseks": "kollane",
        "lillaks": "lilla",
        "oranzi": "oranž",
        "oranz": "oranž",
    }
    return aliases.get(color, color)


def _protocol_to_plan(line: str) -> dict[str, Any]:
    raw = (line or "").strip().strip("` ")
    raw = raw.splitlines()[0].strip() if raw else ""
    if "->" in raw:
        raw = raw.split("->", 1)[1].strip()
    parts = raw.split(maxsplit=1)
    command = parts[0].upper() if parts else "NONE"
    arg = parts[1].strip() if len(parts) > 1 else ""

    if command == "OFF":
        return {
            "actions": [{"action": "turn_off", "entity_id": "all"}],
            "response": "Tuli on kustutatud.",
            "protocol": raw,
        }
    if command == "ON":
        return {
            "actions": [{"action": "turn_on", "entity_id": "all"}],
            "response": "Tuli põleb.",
            "protocol": raw,
        }
    if command == "COLOR":
        color = _protocol_color(arg)
        if not color:
            return {"actions": [], "response": "Ma ei saanud värvist aru.", "protocol": raw}
        return {
            "actions": [{"action": "set_color", "entity_id": "all", "color": color}],
            "response": f"Tuli on {color}.",
            "protocol": raw,
        }
    if command == "DIM":
        return {
            "actions": [{"action": "set_brightness", "entity_id": "all", "brightness": 80}],
            "response": "Heledus muudetud.",
            "protocol": raw,
        }
    if command == "BRIGHTEN":
        return {
            "actions": [{"action": "set_brightness", "entity_id": "all", "brightness": 200}],
            "response": "Heledus muudetud.",
            "protocol": raw,
        }
    if command in ("BRIGHT", "BRIGHTNESS"):
        match = re.search(r"\d{1,3}", arg)
        brightness = max(0, min(255, int(match.group(0)))) if match else 200
        return {
            "actions": [{"action": "set_brightness", "entity_id": "all", "brightness": brightness}],
            "response": "Heledus muudetud.",
            "protocol": raw,
        }
    if command == "TIME":
        match = re.search(r"[-+]?\d+", arg)
        offset_minutes = int(match.group(0)) if match else 0
        return {
            "actions": [],
            "response": time_response_et(offset_minutes),
            "protocol": raw,
        }
    if command == "DATE":
        match = re.search(r"[-+]?\d+", arg)
        offset_days = int(match.group(0)) if match else 0
        return {
            "actions": [],
            "response": natural_date_et(offset_days),
            "protocol": raw,
        }
    if command == "WEATHER":
        return {
            "actions": [],
            "response": weather_response_et(arg or DEFAULT_WEATHER_LOCATION),
            "protocol": raw,
        }
    if command in ("STATE", "STATUS"):
        return {
            "actions": [{"action": "get_state", "entity_id": "all"}],
            "response": "",
            "protocol": raw,
        }
    if command == "LIST":
        return {
            "actions": [{"action": "list_devices"}],
            "response": "",
            "protocol": raw,
        }
    return {"actions": [], "response": "Ma ei saanud käsku täita.", "protocol": raw or "NONE"}


def llm_parse_wiz_protocol(user_text: str) -> dict[str, Any]:
    """Fast JSON-schema-constrained protocol parser for the normal WiZ demo path."""
    if USE_PI_CLI or USE_CLAUDE_CODE:
        # Keep non-Ollama backends on the older JSON contract.
        return llm_parse_intent(user_text, SYSTEM_PROMPT_WIZ_INTENT_EXPERT)
    resp = OLLAMA_SESSION.post(
        OLLAMA_URL,
        json={
            "model": LLM_MODEL,
            "stream": False,
            "format": OLLAMA_PROTOCOL_FORMAT,
            "keep_alive": OLLAMA_KEEP_ALIVE,
            "options": OLLAMA_PROTOCOL_OPTIONS,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT_WIZ_PROTOCOL},
                {"role": "user", "content": user_text},
            ],
        },
    )
    resp.raise_for_status()
    raw = resp.json()["message"]["content"]
    try:
        parsed = json.loads(raw)
        cmd = (parsed.get("cmd") or "NONE").strip().upper()
        arg = (parsed.get("arg") or "").strip()
    except (json.JSONDecodeError, AttributeError):
        return _protocol_to_plan(raw)
    if cmd == "COLOR" and arg:
        text = f"COLOR {arg.lower()}"
    elif cmd in ("WEATHER", "TIME", "DATE", "BRIGHT") and arg:
        text = f"{cmd} {arg}"
    else:
        text = cmd
    return _protocol_to_plan(text)


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
    )
    resp.raise_for_status()
    return json.loads(resp.json()["message"]["content"])



# ============================================================
# Audio recording (VAD-based stop)
# ============================================================


def record_until_silence(
    max_seconds: float = 8.0,
    silence_threshold: float = 0.01,
    silence_duration: float = 1.5,
) -> np.ndarray:
    frame_size = int(SAMPLE_RATE * 0.032)
    chunks = []
    silent_frames = 0
    frames_for_silence = int(silence_duration / 0.032)
    max_frames = int(max_seconds / 0.032)
    done = threading.Event()

    def callback(indata, frames, time_info, status):
        nonlocal silent_frames
        chunks.append(indata[:, 0].copy())
        energy = np.sqrt(np.mean(indata**2))
        if energy < silence_threshold:
            silent_frames += 1
        else:
            silent_frames = 0
        if silent_frames >= frames_for_silence or len(chunks) >= max_frames:
            done.set()

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=frame_size,
        callback=callback,
    ):
        done.wait(timeout=max_seconds + 1)

    if not chunks:
        return np.array([], dtype=np.float32)
    return np.concatenate(chunks)


def record_and_transcribe_streaming(
    stt: SpeechRecognizer,
    max_seconds: float = 8.0,
    silence_threshold: float = 0.01,
    silence_duration: float = 1.0,
) -> tuple[np.ndarray, str, float]:
    """Record one utterance while feeding audio into sherpa-onnx online STT.

    The old path waited for VAD to finish, then decoded the whole utterance.
    This keeps the recognizer stream hot during recording, so by the time VAD
    stops we usually already have the transcript. Returns (audio, text,
    stt_decode_cpu_seconds).
    """
    frame_size = int(SAMPLE_RATE * 0.032)
    frames_for_silence = int(silence_duration / 0.032)
    max_frames = int(max_seconds / 0.032)
    audio_q: queue.Queue[np.ndarray] = queue.Queue(maxsize=128)
    chunks: list[np.ndarray] = []
    silent_frames = 0
    seen_voice = False
    decode_time_s = 0.0
    stream = stt.recognizer.create_stream()
    is_endpoint = getattr(stt.recognizer, "is_endpoint", None)

    def callback(indata, frames, time_info, status):
        try:
            audio_q.put_nowait(indata[:, 0].copy())
        except queue.Full:
            # Dropping here is better than blocking PortAudio's callback thread.
            pass

    start = time.monotonic()
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=frame_size,
        callback=callback,
    ):
        while len(chunks) < max_frames:
            try:
                chunk = audio_q.get(timeout=0.1)
            except queue.Empty:
                if (time.monotonic() - start) >= max_seconds + 0.5:
                    break
                continue

            chunks.append(chunk)
            energy = float(np.sqrt(np.mean(chunk**2)))
            if energy < silence_threshold:
                silent_frames += 1
            else:
                silent_frames = 0
                seen_voice = True

            t_decode = time.monotonic()
            stream.accept_waveform(SAMPLE_RATE, chunk)
            while stt.recognizer.is_ready(stream):
                stt.recognizer.decode_stream(stream)
            decode_time_s += time.monotonic() - t_decode

            if seen_voice and callable(is_endpoint) and is_endpoint(stream):
                break
            if silent_frames >= frames_for_silence:
                break

    # Small zero tail flushes the online recognizer without adding user-visible
    # waiting time (we are already outside the input stream).
    t_decode = time.monotonic()
    stream.accept_waveform(SAMPLE_RATE, np.zeros(int(0.15 * SAMPLE_RATE), dtype=np.float32))
    while stt.recognizer.is_ready(stream):
        stt.recognizer.decode_stream(stream)
    decode_time_s += time.monotonic() - t_decode

    audio = np.concatenate(chunks) if chunks else np.array([], dtype=np.float32)
    return audio, stt.recognizer.get_result(stream).strip(), decode_time_s


# ============================================================
# Model loading
# ============================================================


def resolve_models(tags: list[str]) -> list[tuple[str, Path]]:
    """Resolve version tags to (tag, tflite_path) pairs."""
    results = []
    for tag in tags:
        tflite_path = MODELS_DIR / f"kuule-kratt-{tag}" / f"kuule_kratt_{tag}.tflite"
        if not tflite_path.exists():
            print(f"  Model not found: {tflite_path}")
            available = sorted(
                d.name.replace("kuule-kratt-", "")
                for d in MODELS_DIR.glob("kuule-kratt-v*")
                if (
                    d / f"kuule_kratt_{d.name.replace('kuule-kratt-', '')}.tflite"
                ).exists()
            )
            print(f"  Available: {', '.join(available)}")
            sys.exit(1)
        results.append((tag, tflite_path))
    return results


def _version_sort_key(d):
    """Sort key for version directories: v1, v2, ..., v9, v10, v11, ..., v6-residual."""
    import re

    tag = d.name.replace("kuule-kratt-", "")
    m = re.match(r"v(\d+)(.*)", tag)
    if m:
        return (int(m.group(1)), m.group(2))
    return (0, tag)


def find_latest_model() -> str:
    """Find latest version tag by version sort (matches `sort -V`)."""
    dirs = sorted(MODELS_DIR.glob("kuule-kratt-v*"), key=_version_sort_key)
    for d in reversed(dirs):
        tag = d.name.replace("kuule-kratt-", "")
        if (d / f"kuule_kratt_{tag}.tflite").exists():
            return tag
    sys.exit("No wake word models found in " + str(MODELS_DIR))


# ============================================================
# Main pipeline
# ============================================================


def run_pipeline(args):
    startup_timer = StepTimer("startup")
    print(f"{BOLD}Kratt voice pipeline{RESET}")
    if args.wiz_bash:
        mode = "WiZ bash-agent"
    elif args.ble_bridge:
        mode = "WiZ bridge over BLE"
    else:
        mode = "WiZ bulbs" if args.wiz else "Mock HA"
    print(f"  Backend: {mode}")
    print(f"  LLM: {llm_backend_label()}")
    print("=" * 60)

    system_prompt = SYSTEM_PROMPT_WIZ if args.wiz else SYSTEM_PROMPT_MOCK
    if args.wiz and args.bulbs:
        system_prompt = build_wiz_system_prompt(len([b for b in args.bulbs.split(",") if b.strip()]))
    use_protocol_intent = args.wiz and not args.wiz_bash and not (USE_PI_CLI or USE_CLAUDE_CODE)
    intent_prompt = SYSTEM_PROMPT_WIZ_PROTOCOL if use_protocol_intent else system_prompt
    if args.intent_expert and args.wiz and not args.wiz_bash and not use_protocol_intent:
        intent_prompt = SYSTEM_PROMPT_WIZ_INTENT_EXPERT
    if args.wiz_bash:
        system_prompt = SYSTEM_PROMPT_WIZ_BASH
        intent_prompt = SYSTEM_PROMPT_WIZ_BASH

    if args.wiz_bash and not WIZ_CLI.exists():
        sys.exit(f"wiz CLI not found: {WIZ_CLI}")
    startup_timer.mark("prompts_ready", f"protocol_intent={use_protocol_intent} intent_expert={args.intent_expert}")

    # --- Wake word models ---
    models: list[StreamingModel] = []
    model_tags: list[str] = []
    if not args.no_wakeword:
        if tflite is None:
            sys.exit("tflite_runtime or tensorflow required for wake word detection")

        from pymicro_features import MicroFrontend

        if not args.models:
            args.models = [find_latest_model()]
            print(f"  Using latest model: {args.models[0]}")

        model_tags = args.models
        resolved = resolve_models(model_tags)
        use_ma = len(resolved) > 1  # single model: raw prob, multi: MA smoothing

        # Expand thresholds
        thresholds = args.threshold
        if len(thresholds) == 1:
            thresholds = thresholds * len(resolved)
        elif len(thresholds) != len(resolved):
            sys.exit(f"{len(thresholds)} thresholds for {len(resolved)} models")

        for i, (tag, path) in enumerate(resolved):
            color = COLORS[i % len(COLORS)]
            m = StreamingModel(tag, str(path), thresholds[i], color, use_ma=use_ma)
            m.required_consecutive = args.wake_hold_frames
            m.cooldown_s = args.wake_model_cooldown
            models.append(m)
            size_kb = path.stat().st_size // 1024
            print(f"  {color}■{RESET} {tag} ({size_kb}KB) threshold={thresholds[i]}")

    startup_timer.mark("wake_models_ready", f"models={model_tags or ['manual']}")

    # --- Consensus config ---
    n_models = len(models)
    min_consensus = args.consensus if args.consensus is not None else n_models
    consensus_window_s = args.consensus_window_ms / 1000.0

    # --- STT ---
    print(f"  STT: {STT_MODEL_DIR.name}")
    stt_load_t = time.monotonic()
    stt = SpeechRecognizer(str(STT_MODEL_DIR))
    startup_timer.mark("stt_ready", f"load_ms={int((time.monotonic() - stt_load_t) * 1000)}")

    # --- Target discovery / action transport ---
    wiz_bulb_ips = _parse_bulb_ips(args.bulbs)
    ha = None
    bridge_sender = None

    if args.wiz_bash:
        pass
    elif args.ble_bridge:
        print(f"  Using BLE bridge transport ({len(wiz_bulb_ips)} bulb target(s))")
        try:
            bridge_sender = _load_ble_bridge_sender()
            print("  BLE bridge: connecting/warming GATT session...")
            if not _warm_ble_bridge_connection():
                sys.exit("Failed to warm BLE bridge (scan/connect failed)")
            print("  BLE bridge: connected and kept warm")
        except Exception as e:
            sys.exit(f"Failed to initialize BLE bridge: {e}")
    elif args.wiz:
        mcp_server = WIZ_MCP_SERVER
        mcp_args = ["--bulbs", args.bulbs] if args.bulbs else []

        print(f"  Starting MCP server...")
        ha = MCPClient(mcp_server, mcp_args)
    else:
        print(f"  Using Mock HA fallback actions (no WiZ target)")
        ha = MCPClient(MOCK_MCP_SERVER, [])
    startup_timer.mark("transport_ready", mode)

    # --- Logger ---
    logger = InteractionLogger(
        enabled=args.log,
        participant_id=args.participant,
        log_dir=LOG_DIR,
        llm_model=llm_backend_label(),
        wake_models=model_tags,
        wake_threshold=args.threshold[0] if args.threshold else 0,
    )
    if args.task:
        logger.set_task(args.task)

    # --- Log file for overlay ---
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    demo_log = LOG_DIR / f"demo_{timestamp}.log"
    demo_latest = LOG_DIR / "demo_latest.log"
    demo_latest.unlink(missing_ok=True)
    demo_latest.symlink_to(demo_log)
    demo_log_fh = open(demo_log, "a")

    def log_line(line: str):
        """Write to demo log (overlay watches this) and stdout."""
        print(line)
        demo_log_fh.write(line + "\n")
        demo_log_fh.flush()

    # --- TTS ---
    tts = TextToSpeech(apply_effects=not args.no_tts_effects)
    if args.no_tts:
        tts_available = False
        print(f"  TTS: disabled")
    elif tts.is_available():
        tts_available = True
        print(
            f"  TTS: {TTS_SPEAKER} @ {TTS_URL} (sox effects: {not args.no_tts_effects})"
        )
        threading.Thread(target=tts.prepare_common_responses, name="kratt-tts-precache", daemon=True).start()
    else:
        tts_available = False
        print(f"  TTS: not available — käivita teises terminalis: kratt tts-server")
    startup_timer.mark("tts_checked", f"available={tts_available}")

    # --- LLM warmup ---
    print(f"  Warming up {llm_backend_label()}...")
    startup_timer.mark("llm_warmup_start")
    if use_protocol_intent:
        print("  Intent mode: lightweight protocol")
    elif args.intent_expert and args.wiz and not args.wiz_bash:
        print("  Intent mode: STT-tolerant single-model expert")
    try:
        if use_protocol_intent:
            llm_parse_wiz_protocol("tere")
        else:
            llm_parse_intent("tere", intent_prompt)
        startup_timer.mark("llm_warmup_done")
        print(f"  LLM ready")
    except Exception as e:
        startup_timer.mark("llm_warmup_failed", str(e))
        print(f"  LLM warmup failed: {e}")
        print("  Make sure the selected LLM backend is available")
        return

    # --- Ready ---
    print(f"\n{'=' * 60}")
    if models:
        if n_models > 1:
            print(
                f"  Consensus: {min_consensus}/{n_models} within {args.consensus_window_ms}ms"
            )
        print(f'  Listening for "Kuule Kratt"...')
    else:
        print("  Wake word disabled — press Enter to start recording")
    print(f"  Log: {demo_log}")
    print(f"  Ctrl+C to exit\n")
    startup_timer.mark("ready")

    # --- Audio state ---
    frame_samples = int(SAMPLE_RATE * FRAME_MS / 1000)
    frame_bytes = frame_samples * 2
    audio_buffer = bytearray()

    def wakeword_callback(indata, frames, time_info, status):
        nonlocal audio_buffer
        int16 = (indata[:, 0] * 32768).clip(-32768, 32767).astype(np.int16)
        audio_buffer.extend(int16.tobytes())

    # Consensus state
    consensus_count = 0
    turn_seq = 0
    last_consensus_time = 0.0
    consensus_cooldown_s = args.post_trigger_cooldown
    recent_detections: dict[str, float] = {}
    light_state: dict[str, Any] = {"known": False, "on": None, "color": None, "brightness": None}

    def update_light_state(action_name: str, action: dict[str, Any], ok: bool = True) -> None:
        if not ok:
            return
        if action_name == "turn_off":
            light_state.update({"known": True, "on": False})
        elif action_name == "turn_on":
            light_state.update({"known": True, "on": True})
            if "color" in action:
                light_state["color"] = action["color"]
            if "brightness" in action:
                light_state["brightness"] = action["brightness"]
        elif action_name == "set_color":
            light_state.update({"known": True, "on": True, "color": action.get("color")})
        elif action_name == "set_brightness":
            light_state.update({"known": True, "on": True, "brightness": action.get("brightness")})

    def cached_light_state_response() -> str:
        if not light_state.get("known"):
            return "Ma ei tea veel tule olekut."
        if not light_state.get("on"):
            return "Tuli on kustutatud."
        color = light_state.get("color")
        brightness = light_state.get("brightness")
        if color and brightness is not None:
            return f"Tuli põleb, värv on {color} ja heledus on {brightness}."
        if color:
            return f"Tuli põleb ja on {color}."
        if brightness is not None:
            return f"Tuli põleb, heledus on {brightness}."
        return "Tuli põleb."

    def prepare_next_listen() -> None:
        """Enforce post-trigger dead-time on every wake outcome.

        Early exits (too-short audio / empty STT) used to reopen the wake
        detector immediately and could produce a second detection from residual
        speech/noise. Successful turns already had this cooldown; keep all
        paths consistent.
        """
        nonlocal audio_buffer
        recent_detections.clear()
        audio_buffer = bytearray()
        if models and args.post_trigger_cooldown > 0:
            print(f"  Cooldown {args.post_trigger_cooldown:.1f}s before listening again...")
            time.sleep(args.post_trigger_cooldown)
        if models:
            print(f'  Listening for "Kuule Kratt"...\n')

    try:
        while True:
            wake_prob = None
            wake_models_agreed: list[str] = []

            if models:
                # --- Multi-model consensus wake word detection ---
                audio_buffer = bytearray()
                detected = False
                frontend = MicroFrontend()
                process_fn = getattr(frontend, "process_samples", None) or getattr(
                    frontend, "ProcessSamples", None
                )

                # Reset all models for fresh detection cycle
                for m in models:
                    m.reset()
                recent_detections.clear()

                with sd.InputStream(
                    samplerate=SAMPLE_RATE,
                    channels=1,
                    dtype="float32",
                    blocksize=frame_samples,
                    callback=wakeword_callback,
                ):
                    while not detected:
                        while len(audio_buffer) >= frame_bytes:
                            chunk = bytes(audio_buffer[:frame_bytes])
                            del audio_buffer[:frame_bytes]

                            result = process_fn(chunk)
                            if not result.features:
                                continue

                            features = np.array(result.features, dtype=np.float32)
                            now = time.monotonic()

                            # Feed same features to ALL models
                            for m in models:
                                prob = m.process_features(features.copy())
                                if prob is not None:
                                    recent_detections[m.name] = now
                                    # Print individual model hits for terminal debugging,
                                    # but keep the overlay log consensus-only. Otherwise
                                    # one real wake event shows the overlay twice.
                                    print(
                                        f"  >>> DETECTED kuule kratt {m.name}! "
                                        f"(prob={prob:.3f}, count={m.detection_count}) <<<"
                                    )

                            # Check consensus
                            if (now - last_consensus_time) >= consensus_cooldown_s:
                                agreeing = [
                                    name
                                    for name, t in recent_detections.items()
                                    if (now - t) < consensus_window_s
                                ]
                                if len(agreeing) >= min_consensus:
                                    consensus_count += 1
                                    last_consensus_time = now
                                    models_str = "+".join(agreeing)
                                    wake_prob = max(
                                        sum(m.scores) / max(len(m.scores), 1)
                                        for m in models
                                        if m.name in agreeing
                                    )
                                    wake_models_agreed = list(agreeing)

                                    log_line(
                                        f"\n  {BOLD}>>> CONSENSUS {len(agreeing)}/{n_models}: "
                                        f"KUULE KRATT! (#{consensus_count}) [{models_str}] <<<{RESET}"
                                    )

                                    detected = True
                                    recent_detections.clear()
                                    break

                        time.sleep(0.005)
            else:
                input("\nPress Enter to start recording...")

            turn_seq += 1
            turn_timer = StepTimer(f"turn_{turn_seq}")
            turn_timer.mark(
                "trigger_ready",
                (
                    f"wake_prob={wake_prob:.3f} models={'+'.join(wake_models_agreed)}"
                    if wake_prob is not None
                    else "manual_trigger"
                ),
            )

            # --- Record user speech + STT ---
            t0 = time.monotonic()
            if args.streaming_stt:
                turn_timer.mark("record_streaming_stt_start")
                print("  Recording + streaming STT... (speak now, stops on silence)")
                audio, transcript, t_stt = record_and_transcribe_streaming(stt)
                t_rec = time.monotonic() - t0
                turn_timer.mark("record_streaming_stt_done", f"rec={t_rec:.3f}s decode={t_stt:.3f}s")
                print(f"  Recorded {t_rec:.1f}s of audio")
                print(f'  STT streamed (decode={t_stt:.1f}s): "{transcript}"')
            else:
                turn_timer.mark("record_start")
                print("  Recording... (speak now, stops on silence)")
                audio = record_until_silence()
                t_rec = time.monotonic() - t0
                turn_timer.mark("record_done", f"rec={t_rec:.3f}s audio={float(len(audio)) / SAMPLE_RATE:.3f}s")
                print(f"  Recorded {t_rec:.1f}s of audio")

                print("  Transcribing...")
                turn_timer.mark("stt_start")
                t1 = time.monotonic()
                transcript = stt.transcribe(audio)
                t_stt = time.monotonic() - t1
                turn_timer.mark("stt_done", f"stt={t_stt:.3f}s transcript={transcript!r}")
                print(f'  STT ({t_stt:.1f}s): "{transcript}"')

            if len(audio) < SAMPLE_RATE * 0.3:
                turn_timer.mark("skip_too_short")
                print("  Too short, skipping")
                logger.log_interaction(
                    {
                        "outcome": "skipped_too_short",
                        "wake_word_prob": wake_prob,
                        "wake_models": wake_models_agreed,
                        "audio_duration_s": round(float(len(audio)) / SAMPLE_RATE, 3),
                        "timing": turn_timer.as_dict(),
                    }
                )
                prepare_next_listen()
                continue

            if not transcript:
                turn_timer.mark("skip_empty_transcript")
                print("  Empty transcript, skipping")
                logger.log_interaction(
                    {
                        "outcome": "empty_transcript",
                        "wake_word_prob": wake_prob,
                        "wake_models": wake_models_agreed,
                        "audio_duration_s": round(float(len(audio)) / SAMPLE_RATE, 3),
                        "stt_latency_ms": int(t_stt * 1000),
                        "timing": turn_timer.as_dict(),
                    }
                )
                prepare_next_listen()
                continue

            # --- LLM / execute ---
            t2 = time.monotonic()
            llm1_error = None
            llm2_error = None
            t_llm2 = 0.0
            actions = []
            tool_results = []
            executed_actions = []
            response = ""
            parsed = {}

            if args.wiz_bash:
                print("  Planning WiZ bash command...")
                turn_timer.mark("llm_plan_start", "wiz_bash")
                try:
                    command, cli_result, response, ok = execute_wiz_bash_mode(transcript)
                    actions = [{"command": command}] if command else []
                    print(f"  LLM ({time.monotonic() - t2:.1f}s): {command or '<no command>'}")
                    if cli_result:
                        print(f"  -> {cli_result}")
                    if command:
                        executed_actions.append(
                            {"action": "bash", "args": {"command": command}, "result": cli_result}
                        )
                        tool_results.append(cli_result)
                    if not ok:
                        llm1_error = "bash_command_failed_or_rejected"
                except Exception as e:
                    llm1_error = str(e)
                    response = "Vabandust, käsu täitmine ebaõnnestus."
                t_llm1 = time.monotonic() - t2
                turn_timer.mark("llm_plan_done", f"llm={t_llm1:.3f}s error={llm1_error}")
                if llm1_error:
                    print(f"  LLM/tool error: {llm1_error}")
            else:
                print("  Parsing intent...")
                turn_timer.mark("llm_intent_start", f"{llm_backend_label()} protocol={use_protocol_intent}")
                try:
                    parsed = llm_parse_wiz_protocol(transcript) if use_protocol_intent else llm_parse_intent(transcript, intent_prompt)
                    actions = parsed.get("actions", [])
                except Exception as e:
                    parsed = {}
                    actions = []
                    llm1_error = str(e)
                t_llm1 = time.monotonic() - t2
                turn_timer.mark("llm_intent_done", f"llm={t_llm1:.3f}s actions={len(actions)} error={llm1_error}")
                print(f"  LLM ({t_llm1:.1f}s): {json.dumps(actions, ensure_ascii=False)}")
                if llm1_error:
                    print(f"  LLM error: {llm1_error}")

                # --- Execute actions ---
                turn_timer.mark("execute_start", f"actions={len(actions)} transport={'ble' if args.ble_bridge else 'mcp'}")
                if args.ble_bridge:
                    for i, action in enumerate(actions, start=1):
                        if not isinstance(action, dict):
                            print(f"  Skipping malformed action: {action}")
                            turn_timer.mark("execute_skip_malformed", str(action))
                            continue
                        action_copy = dict(action)
                        action_name = action_copy.pop("action", "")
                        action_t = time.monotonic()
                        turn_timer.mark(f"action_{i}_start", action_name)
                        result, ok = execute_wiz_ble_action(action_name, action_copy, wiz_bulb_ips)
                        if not ok and llm1_error is None:
                            llm1_error = "ble_bridge_command_failed"
                        tool_results.append(f"{action_name}: {result}")
                        update_light_state(action_name, action_copy, ok)
                        executed_actions.append(
                            {"action": action_name, "args": action_copy, "result": result, "ok": ok}
                        )
                        turn_timer.mark(
                            f"action_{i}_done",
                            f"{action_name} ok={ok} ms={int((time.monotonic() - action_t) * 1000)} result={result}",
                        )
                        print(f"  -> {action_name}: {result}")
                else:
                    for i, action in enumerate(actions, start=1):
                        if not isinstance(action, dict):
                            print(f"  Skipping malformed action: {action}")
                            turn_timer.mark("execute_skip_malformed", str(action))
                            continue
                        action_name = action.pop("action", "")
                        action_t = time.monotonic()
                        turn_timer.mark(f"action_{i}_start", action_name)
                        ok = True
                        try:
                            result = ha.execute(action_name, action)
                        except RuntimeError as e:
                            result = f"MCP error: {e}"
                            ok = False
                        tool_results.append(f"{action_name}: {result}")
                        update_light_state(action_name, action, ok)
                        executed_actions.append(
                            {"action": action_name, "args": action, "result": result, "ok": ok}
                        )
                        turn_timer.mark(
                            f"action_{i}_done",
                            f"{action_name} ms={int((time.monotonic() - action_t) * 1000)} result={result}",
                        )
                        print(f"  -> {action_name}: {result}")
                turn_timer.mark("execute_done", f"executed={len(executed_actions)} error={llm1_error}")

                # --- Response: no second LLM call on the demo hot path. ---
                t3 = time.monotonic()
                turn_timer.mark("response_start")
                planned_response = str(parsed.get("response", "")).strip()
                if llm1_error == "ble_bridge_command_failed":
                    response = "Vabandust, käsku ei saanud täita."
                elif executed_actions and executed_actions[0].get("action") == "get_state":
                    if args.ble_bridge and executed_actions[0].get("result"):
                        response = str(executed_actions[0].get("result"))
                        print("  Response: BLE state")
                    else:
                        response = cached_light_state_response()
                        print("  Response: cached state")
                elif planned_response:
                    response = planned_response
                    print("  Response: planned")
                elif executed_actions:
                    first = executed_actions[0]
                    response = demo_response_for_action(first.get("action", ""), first.get("args", {}))
                    print("  Response: template")
                elif not actions:
                    response = "Ma ei saanud käsku täita."
                else:
                    response = "Tehtud."
                t_llm2 = time.monotonic() - t3
                turn_timer.mark("response_done", f"llm2={t_llm2:.3f}s error={llm2_error} response={response!r}")
                if llm2_error:
                    print(f"  Response LLM error: {llm2_error}")

            t_total_no_tts = time.monotonic() - t0
            turn_timer.mark("response_print_ready", f"total_no_tts={t_total_no_tts:.3f}s")
            print(f"\n  KRATT: {BOLD}{response}{RESET}")

            # --- TTS: speak the response ---
            t_tts = 0.0
            if tts_available and response:
                try:
                    turn_timer.mark("tts_start")
                    t_tts = tts.speak(response)
                    turn_timer.mark("tts_done", f"tts={t_tts:.3f}s")
                    print(f"  TTS: {t_tts:.1f}s")
                except Exception as e:
                    turn_timer.mark("tts_error", str(e))
                    print(f"  TTS error: {e}")
            else:
                turn_timer.mark("tts_skipped", f"available={tts_available} response={bool(response)}")

            t_total = time.monotonic() - t0
            turn_timer.mark("turn_done", f"total_with_tts={t_total:.3f}s")
            print(
                f"  rec={t_rec:.1f}s stt={t_stt:.1f}s llm1={t_llm1:.1f}s llm2={t_llm2:.1f}s "
                f"no_tts={t_total_no_tts:.1f}s total={t_total:.1f}s"
            )

            logger.log_interaction(
                {
                    "outcome": "completed"
                    if not (llm1_error or llm2_error)
                    else "llm_error",
                    "wake_word_prob": wake_prob,
                    "wake_models": wake_models_agreed,
                    "audio_duration_s": round(float(len(audio)) / SAMPLE_RATE, 3),
                    "rec_duration_s": round(t_rec, 3),
                    "stt_latency_ms": int(t_stt * 1000),
                    "stt_transcript": transcript,
                    "llm1_latency_ms": int(t_llm1 * 1000),
                    "llm1_error": llm1_error,
                    "intent_actions": executed_actions,
                    "llm2_latency_ms": int(t_llm2 * 1000),
                    "llm2_error": llm2_error,
                    "response": response,
                    "tts_latency_ms": int(t_tts * 1000),
                    "e2e_no_tts_latency_ms": int(t_total_no_tts * 1000),
                    "e2e_latency_ms": int(t_total * 1000),
                    "timing": turn_timer.as_dict(),
                }
            )

            print()
            prepare_next_listen()

    except KeyboardInterrupt:
        print("\n\nStopped.")
        if models:
            print(f"  Consensus detections: {consensus_count}")
            for m in models:
                print(f"  {m.color}■{RESET} {m.name}: {m.detection_count} individual")
    finally:
        demo_log_fh.close()
        logger.close()
        if ha is not None:
            ha.close()
        close_pi_rpc_clients()


def main():
    global LLM_MODEL, PI_MODEL, PI_THINKING, PI_RESET_EACH_TURN, PI_RPC_TIMEOUT, USE_CLAUDE_CODE, USE_PI_CLI, CLAUDE_SESSION_ID, CLAUDE_SESSION_STARTED

    parser = argparse.ArgumentParser(description="Kratt full voice pipeline")
    parser.add_argument(
        "--profile",
        choices=["demo", "wiz-claude", "wiz-claude-safe", "wiz-manual"],
        default=None,
        help="Optional preset override; bare `kratt demo` has sane live-demo defaults.",
    )
    parser.add_argument(
        "--models",
        nargs="*",
        default=None,
        help="Model version tags (e.g. v10 v15). Default: v16c for live demo.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        nargs="+",
        default=[0.996],
        help="One threshold for all, or one per model. Default: 0.996.",
    )
    parser.add_argument(
        "--consensus",
        type=int,
        default=None,
        help="Min models that must agree. Default: all (N/N).",
    )
    parser.add_argument(
        "--consensus-window-ms",
        type=int,
        default=1000,
        help="Time window for consensus agreement (ms). Default: 1000.",
    )
    parser.add_argument(
        "--wake-hold-frames",
        type=int,
        default=3,
        help="Require N consecutive above-threshold frames before wake trigger. Default: 3.",
    )
    parser.add_argument(
        "--wake-model-cooldown",
        type=float,
        default=4.0,
        help="Per-model wake refractory period in seconds. Default: 4.0.",
    )
    parser.add_argument(
        "--post-trigger-cooldown",
        type=float,
        default=2.0,
        help="Cooldown after a trigger/turn before listening again. Default: 2.0.",
    )
    parser.add_argument(
        "--no-wakeword", action="store_true", help="Skip wake word, manual trigger"
    )
    parser.add_argument(
        "--streaming-stt",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Feed microphone audio into online STT while recording. Default: true.",
    )
    parser.add_argument(
        "--wiz",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Use real WiZ bulbs. Default: auto-enable when cached/discovered bulbs exist.",
    )
    parser.add_argument(
        "--wiz-bash",
        action="store_true",
        help="Use LLM->wiz CLI bash-agent mode (no MCP JSON actions)",
    )
    parser.add_argument(
        "--ble-bridge",
        action="store_true",
        help="Send WiZ JSON to bulbs over the ESP32 BLE bridge instead of local UDP/MCP.",
    )
    parser.add_argument(
        "--bulbs",
        type=str,
        default=None,
        help=(
            "Comma-separated WiZ bulb IPs (skip discovery). "
            "For --ble-bridge, omit this or use 'auto' to broadcast on the ESP32 AP subnet."
        ),
    )
    parser.add_argument(
        "--llm",
        type=str,
        default=LLM_MODEL,
        help=f"Ollama model name. Default: {LLM_MODEL}",
    )
    parser.add_argument(
        "--pi-cli",
        "--pi-gpt",
        dest="pi_cli",
        action="store_true",
        help="Use long-lived pi RPC + GPT as the single LLM backend (default model: gpt-5.3-codex-spark).",
    )
    parser.add_argument(
        "--pi-model",
        type=str,
        default=PI_MODEL,
        help=f"pi CLI model. Default: {PI_MODEL}",
    )
    parser.add_argument(
        "--pi-thinking",
        type=str,
        default=PI_THINKING,
        help=f"pi CLI thinking level. Default: {PI_THINKING}",
    )
    parser.add_argument(
        "--pi-reset-each-turn",
        action="store_true",
        help="Clear pi RPC conversation between turns. Safer, but slower; default keeps warm context for speed.",
    )
    parser.add_argument(
        "--pi-rpc-timeout",
        type=float,
        default=PI_RPC_TIMEOUT,
        help=f"Timeout for one pi RPC LLM turn in seconds. Default: {PI_RPC_TIMEOUT}.",
    )
    parser.add_argument(
        "--intent-expert",
        "--stt-tolerant-intent",
        dest="intent_expert",
        action="store_true",
        help="Use a compact STT-error-tolerant prompt for the first intent/tool-call LLM pass.",
    )
    parser.add_argument(
        "--claude-code",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Use Claude Code instead of local Ollama. Default: false.",
    )
    parser.add_argument(
        "--claude-session-id",
        type=str,
        default=None,
        help="Claude Code session UUID to reuse. Default: one UUID reused for this demo run.",
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Enable per-interaction JSONL telemetry",
    )
    parser.add_argument(
        "--participant", default="dev", help="Participant ID for log file naming"
    )
    parser.add_argument(
        "--task", default=None, help="Initial task ID tag for logged interactions"
    )
    parser.add_argument(
        "--no-tts", action="store_true", help="Disable TTS voice output"
    )
    parser.add_argument(
        "--no-tts-effects",
        action="store_true",
        help="TTS without sox character effects",
    )
    args = parser.parse_args()

    apply_demo_profile(args)

    # Sane demo defaults: `kratt demo` should run the normal live demo.
    # Explicit flags still override these defaults.
    if args.models is None and not args.no_wakeword:
        args.models = ["v16c"]
    if args.bulbs is None:
        if args.ble_bridge:
            args.bulbs = _get_default_wiz_bridge_bulb_ip()
        else:
            args.bulbs = _cached_wiz_bulbs()
    if args.wiz is None:
        args.wiz = bool(args.bulbs)

    if args.ble_bridge and args.wiz_bash:
        sys.exit("--ble-bridge and --wiz-bash are mutually exclusive")
    if args.wiz_bash or args.ble_bridge:
        args.wiz = True

    LLM_MODEL = args.llm
    PI_MODEL = args.pi_model
    PI_THINKING = args.pi_thinking
    PI_RESET_EACH_TURN = args.pi_reset_each_turn
    PI_RPC_TIMEOUT = args.pi_rpc_timeout
    USE_PI_CLI = args.pi_cli
    USE_CLAUDE_CODE = False if args.pi_cli else args.claude_code
    if args.claude_session_id:
        CLAUDE_SESSION_ID = args.claude_session_id
        CLAUDE_SESSION_STARTED = True

    run_pipeline(args)


if __name__ == "__main__":
    main()
