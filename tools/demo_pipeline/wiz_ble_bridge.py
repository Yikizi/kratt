from __future__ import annotations

import importlib.util
import ipaddress
import threading
import time
from typing import Any

from tools.demo_pipeline.paths import PROJECT_ROOT

BLE_BRIDGE_DIR = PROJECT_ROOT / "tools" / "ble-wiz-bridge"
WIZ_BRIDGE_DEFAULT_PORT = 38899
WIZ_BRIDGE_DEFAULT_BULB_IP = "auto"
WIZ_BRIDGE_EFFECT_PALETTE = [
    "punane",
    "roheline",
    "sinine",
    "kollane",
    "lilla",
    "roosa",
    "oranž",
    "valge",
]

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
_WIZ_BRIDGE_CLOSER = None
_WIZ_BRIDGE_MODULE = None
_EFFECT_LOCK = threading.Lock()
_EFFECT_STOP: threading.Event | None = None
_EFFECT_THREAD: threading.Thread | None = None
_EFFECT_SEQ = 0


def load_ble_bridge_module():
    global _WIZ_BRIDGE_MODULE
    if _WIZ_BRIDGE_MODULE is not None:
        return _WIZ_BRIDGE_MODULE
    bridge_path = BLE_BRIDGE_DIR / "bridge.py"
    if not bridge_path.exists():
        raise RuntimeError(f"BLE bridge module missing: {bridge_path}")
    spec = importlib.util.spec_from_file_location("kratt_ble_wiz_bridge", bridge_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load BLE bridge module: {bridge_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _WIZ_BRIDGE_MODULE = module
    return module


def get_default_wiz_bridge_bulb_ip() -> str:
    if not BLE_BRIDGE_DIR.exists():
        return WIZ_BRIDGE_DEFAULT_BULB_IP

    try:
        bridge = load_ble_bridge_module()
    except Exception:
        return WIZ_BRIDGE_DEFAULT_BULB_IP
    return getattr(bridge, "WIZ_BRIDGE_DEFAULT_BULB_IP", None) or WIZ_BRIDGE_DEFAULT_BULB_IP


def load_ble_bridge_sender():
    global _WIZ_BRIDGE_SENDER
    global _WIZ_BRIDGE_RESPONSE_SENDER
    global _WIZ_BRIDGE_WARMER
    global _WIZ_BRIDGE_CLOSER
    global WIZ_BRIDGE_DEFAULT_BULB_IP
    if _WIZ_BRIDGE_SENDER is not None:
        return _WIZ_BRIDGE_SENDER

    if not BLE_BRIDGE_DIR.exists():
        raise RuntimeError(f"BLE bridge path missing: {BLE_BRIDGE_DIR}")

    bridge = load_ble_bridge_module()
    bridge_default_ip = getattr(bridge, "WIZ_BRIDGE_DEFAULT_BULB_IP", None)
    if bridge_default_ip:
        WIZ_BRIDGE_DEFAULT_BULB_IP = bridge_default_ip

    _WIZ_BRIDGE_SENDER = bridge.send_wiz_via_ble
    _WIZ_BRIDGE_RESPONSE_SENDER = bridge.send_wiz_via_ble_response
    _WIZ_BRIDGE_WARMER = bridge.warm_ble_bridge
    _WIZ_BRIDGE_CLOSER = bridge.close_ble_bridge
    return _WIZ_BRIDGE_SENDER


def load_ble_bridge_response_sender():
    load_ble_bridge_sender()
    return _WIZ_BRIDGE_RESPONSE_SENDER


def warm_ble_bridge_connection() -> bool:
    load_ble_bridge_sender()
    if _WIZ_BRIDGE_WARMER is None:
        return True
    return bool(_WIZ_BRIDGE_WARMER())


def close_ble_bridge_connection() -> None:
    cancel_running_effect(wait=False)
    if _WIZ_BRIDGE_CLOSER is None:
        return
    try:
        _WIZ_BRIDGE_CLOSER()
    except Exception:
        pass


def parse_bulb_ips(raw: str | None) -> list[str]:
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


def resolve_bulb_targets(entity_id: str | None, bulb_ips: list[str]) -> tuple[list[str], str | None]:
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


def brightness_to_wiz(value: int) -> int:
    return max(10, min(100, round((value / 255) * 100)))


def apply_wiz_color(params: dict[str, Any], raw_color: Any) -> str | None:
    color = WIZ_BRIDGE_COLOR_MAP.get(str(raw_color).lower())
    if color is None:
        return f"Unsupported color: {raw_color}"
    if isinstance(color, tuple):
        params.update({"r": color[0], "g": color[1], "b": color[2]})
    else:
        params["temp"] = color
    return None


def build_wiz_payload(action_name: str, action: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    if action_name == "turn_on":
        params: dict[str, int | bool] = {"state": True}
        if "brightness" in action:
            params["dimming"] = brightness_to_wiz(int(action["brightness"]))
        if "color" in action:
            color_error = apply_wiz_color(params, action["color"])
            if color_error:
                return {}, color_error
        return {"method": "setPilot", "params": params}, None

    if action_name == "turn_off":
        return {"method": "setPilot", "params": {"state": False}}, None

    if action_name == "set_brightness":
        if "brightness" not in action:
            return {}, "set_brightness missing brightness"
        params = {"state": True, "dimming": brightness_to_wiz(int(action["brightness"]))}
        return {"method": "setPilot", "params": params}, None

    if action_name == "set_color":
        params: dict[str, Any] = {"state": True}
        color_error = apply_wiz_color(params, action.get("color", ""))
        if color_error:
            return {}, color_error
        return {"method": "setPilot", "params": params}, None

    if action_name == "get_state":
        return {"method": "getPilot", "params": {}}, None

    return {}, f"Unsupported action for BLE path: {action_name}"


def _color_payload(color_name: str, *, brightness: int | None = None) -> tuple[dict[str, Any], str | None]:
    params: dict[str, Any] = {"state": True}
    color_error = apply_wiz_color(params, color_name)
    if color_error:
        return {}, color_error
    if brightness is not None:
        params["dimming"] = brightness_to_wiz(brightness)
    return {"method": "setPilot", "params": params}, None


def cancel_running_effect(*, wait: bool = False) -> None:
    global _EFFECT_STOP, _EFFECT_THREAD
    with _EFFECT_LOCK:
        stop = _EFFECT_STOP
        thread = _EFFECT_THREAD
        if stop is not None:
            stop.set()
    if wait and thread is not None and thread is not threading.current_thread():
        thread.join(timeout=1.0)


def _effect_finished(seq: int) -> None:
    global _EFFECT_STOP, _EFFECT_THREAD
    with _EFFECT_LOCK:
        if seq == _EFFECT_SEQ:
            _EFFECT_STOP = None
            _EFFECT_THREAD = None


def _effect_wait(stop_event: threading.Event, seconds: float) -> bool:
    return stop_event.wait(max(0.0, seconds))


def _send_effect_to_target(
    send,
    target: str,
    action: dict[str, Any],
    stop_event: threading.Event,
) -> tuple[str, bool]:
    effect = str(action.get("effect") or "").strip().lower()
    duration_s = max(0.5, min(12.0, float(action.get("duration_seconds", 6) or 6)))
    step_s = max(0.12, min(2.0, float(action.get("step_seconds", 0.35) or 0.35)))

    if effect == "color_cycle":
        colors = WIZ_BRIDGE_EFFECT_PALETTE
        # For "show all colors", one pass is usually better UX than looping.
        max_steps = min(len(colors), max(1, int(duration_s / step_s)))
        for color in colors[:max_steps]:
            if stop_event.is_set():
                return f"{target}: color cycle cancelled", True
            payload, err = _color_payload(color)
            if err:
                return err, False
            if not send(target, payload, port=WIZ_BRIDGE_DEFAULT_PORT):
                return f"{target}: BLE command failed during color cycle", False
            if _effect_wait(stop_event, step_s):
                return f"{target}: color cycle cancelled", True
        return f"{target}: color cycle sent ({max_steps} colors)", True

    if effect == "disco":
        colors = WIZ_BRIDGE_EFFECT_PALETTE[:6]
        end = time.monotonic() + duration_s
        steps = 0
        while time.monotonic() < end:
            if stop_event.is_set():
                return f"{target}: disco cancelled", True
            color = colors[steps % len(colors)]
            payload, err = _color_payload(color)
            if err:
                return err, False
            if not send(target, payload, port=WIZ_BRIDGE_DEFAULT_PORT):
                return f"{target}: BLE command failed during disco", False
            steps += 1
            if _effect_wait(stop_event, step_s):
                return f"{target}: disco cancelled", True
        return f"{target}: disco sent ({steps} steps)", True

    if effect == "pulse":
        color = str(action.get("color") or "roosa").strip() or "roosa"
        end = time.monotonic() + duration_s
        steps = 0
        high = True
        while time.monotonic() < end:
            if stop_event.is_set():
                return f"{target}: pulse cancelled", True
            payload, err = _color_payload(color, brightness=255 if high else 25)
            if err:
                return err, False
            if not send(target, payload, port=WIZ_BRIDGE_DEFAULT_PORT):
                return f"{target}: BLE command failed during pulse", False
            high = not high
            steps += 1
            if _effect_wait(stop_event, step_s):
                return f"{target}: pulse cancelled", True
        return f"{target}: pulse sent ({steps} steps)", True

    return f"Unsupported effect: {effect}", False


def _effect_worker(
    seq: int,
    send,
    targets: list[str],
    action: dict[str, Any],
    stop_event: threading.Event,
) -> None:
    try:
        for target in targets:
            if stop_event.is_set():
                break
            _send_effect_to_target(send, target, action, stop_event)
    finally:
        _effect_finished(seq)


def start_background_effect(send, targets: list[str], action: dict[str, Any]) -> tuple[str, bool]:
    global _EFFECT_SEQ, _EFFECT_STOP, _EFFECT_THREAD
    cancel_running_effect(wait=False)

    effect = str(action.get("effect") or "effect").strip().lower()
    duration_s = max(0.5, min(12.0, float(action.get("duration_seconds", 6) or 6)))
    stop_event = threading.Event()
    with _EFFECT_LOCK:
        _EFFECT_SEQ += 1
        seq = _EFFECT_SEQ
        _EFFECT_STOP = stop_event
        _EFFECT_THREAD = threading.Thread(
            target=_effect_worker,
            args=(seq, send, list(targets), dict(action), stop_event),
            name=f"kratt-wiz-effect-{effect}",
            daemon=True,
        )
        _EFFECT_THREAD.start()
    target_text = ", ".join(targets)
    return f"{target_text}: {effect} started ({duration_s:g}s)", True


def format_ble_state_response(response: dict[str, Any] | None) -> str:
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
        send = load_ble_bridge_sender()
    except Exception as exc:
        return f"BLE bridge unavailable: {exc}", False

    targets, target_error = resolve_bulb_targets(action.get("entity_id"), bulb_ips)
    if target_error:
        return target_error, False

    if action_name == "run_effect":
        return start_background_effect(send, targets, action)

    if action_name in {"turn_on", "turn_off", "set_brightness", "set_color"}:
        cancel_running_effect(wait=False)

    payload, payload_error = build_wiz_payload(action_name, action)
    if payload_error:
        return payload_error, False

    if action_name == "get_state":
        send_response = load_ble_bridge_response_sender()
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
            return format_ble_state_response(responses[0]), True
        on_count = sum(1 for r in responses if r.get("state_valid") and r.get("state"))
        known_count = sum(1 for r in responses if r.get("state_valid"))
        if known_count:
            return f"{on_count}/{known_count} WiZ tuld põleb.", True
        return "WiZ tulede olek on teadmata.", True

    failed: list[str] = []
    results: list[str] = []
    for ip in targets:
        # Demo setPilot commands use BLE write acknowledgement only. Reading the
        # status characteristic after every color/brightness change made the
        # CoreBluetooth/NimBLE session go stale and caused 20s+ false failures,
        # even when the lamp visibly applied the command.
        ok = send(ip, payload, port=WIZ_BRIDGE_DEFAULT_PORT)
        result = "WiZ command sent" if ok else "BLE command failed"
        results.append(f"{ip}: {result}")
        if not ok:
            failed.append(ip)

    if failed:
        return f"Failed to send BLE command to: {', '.join(failed)} ({'; '.join(results)})", False

    return "; ".join(results), True
