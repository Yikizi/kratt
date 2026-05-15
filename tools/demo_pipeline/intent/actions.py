from __future__ import annotations

import re
from typing import Any

ALLOWED_INTENT_ACTIONS = {
    "turn_on",
    "turn_off",
    "set_brightness",
    "set_color",
    "get_state",
    "list_devices",
    "get_time",
    "get_date",
    "get_weather",
    "get_capabilities",
    "run_effect",
    "cook",
    "stop",
    "status",
}

ENTITY_ACTIONS = {"turn_on", "turn_off", "set_brightness", "set_color", "get_state", "run_effect"}
AIRFRYER_ACTIONS = {"cook", "stop", "status"}

_HEX_COLOR_RE = re.compile(r"^#?([0-9a-fA-F]{6})$")
_RGB_STRING_RE = re.compile(r"^rgb\s*\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$")


def _clamp_rgb(values: list[int] | tuple[int, int, int]) -> list[int]:
    return [max(0, min(255, int(v))) for v in values[:3]]


def parse_rgb_value(value: Any) -> list[int] | None:
    if isinstance(value, (list, tuple)) and len(value) >= 3:
        try:
            return _clamp_rgb([int(value[0]), int(value[1]), int(value[2])])
        except (TypeError, ValueError):
            return None
    if isinstance(value, dict):
        try:
            return _clamp_rgb([int(value["r"]), int(value["g"]), int(value["b"])])
        except (KeyError, TypeError, ValueError):
            return None
    text = str(value or "").strip()
    match = _RGB_STRING_RE.match(text)
    if match:
        return _clamp_rgb([int(match.group(1)), int(match.group(2)), int(match.group(3))])
    return None


def parse_hex_color(value: Any) -> list[int] | None:
    text = str(value or "").strip()
    match = _HEX_COLOR_RE.match(text)
    if not match:
        return None
    raw = match.group(1)
    return [int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)]


def normalize_color_fields(raw: dict[str, Any], action: dict[str, Any]) -> bool:
    """Copy supported color fields from raw LLM JSON into normalized action.

    Supports named colors/temperature strings, RGB triples, and #RRGGBB hex.
    Returns True if at least one color representation was found.
    """
    found = False
    if "rgb" in raw:
        rgb = parse_rgb_value(raw.get("rgb"))
        if rgb is not None:
            action["rgb"] = rgb
            found = True
    if "hex" in raw:
        rgb = parse_hex_color(raw.get("hex"))
        if rgb is not None:
            action["hex"] = "#" + "".join(f"{v:02x}" for v in rgb)
            action["rgb"] = rgb
            found = True
    if "color" in raw:
        color = str(raw.get("color") or "").strip()
        if color:
            rgb = parse_rgb_value(color) or parse_hex_color(color)
            if rgb is not None:
                action["rgb"] = rgb
                if color.lstrip().startswith("#") or _HEX_COLOR_RE.match(color):
                    action["hex"] = "#" + "".join(f"{v:02x}" for v in rgb)
                found = True
            else:
                action["color"] = color
                found = True
    return found


def normalize_intent_actions(
    raw_actions: Any,
    *,
    default_entity_id: str | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Validate and normalize LLM-produced action JSON before execution."""
    if raw_actions in (None, ""):
        return [], []
    if not isinstance(raw_actions, list):
        return [], ["actions must be a list"]

    normalized: list[dict[str, Any]] = []
    errors: list[str] = []
    for i, raw in enumerate(raw_actions, start=1):
        if not isinstance(raw, dict):
            errors.append(f"action #{i} is not an object")
            continue

        action_name = str(raw.get("action", "")).strip()
        if action_name not in ALLOWED_INTENT_ACTIONS:
            errors.append(f"action #{i} has unsupported action: {action_name or '<missing>'}")
            continue

        action: dict[str, Any] = {"action": action_name}
        if action_name in ENTITY_ACTIONS:
            entity_id = str(raw.get("entity_id") or default_entity_id or "").strip()
            if not entity_id:
                errors.append(f"action #{i} missing entity_id")
                continue
            action["entity_id"] = entity_id

        if action_name == "cook":
            try:
                temperature_c = int(raw.get("temperature_c", raw.get("temp", raw.get("temperature"))))
            except (TypeError, ValueError):
                errors.append(f"action #{i} has invalid temperature_c: {raw.get('temperature_c')!r}")
                continue
            try:
                time_minutes = int(raw.get("time_minutes", raw.get("minutes", raw.get("time"))))
            except (TypeError, ValueError):
                errors.append(f"action #{i} has invalid time_minutes: {raw.get('time_minutes')!r}")
                continue
            action["temperature_c"] = max(40, min(200, temperature_c))
            action["time_minutes"] = max(1, min(60, time_minutes))

        if action_name in {"turn_on", "set_brightness"} and "brightness" in raw:
            try:
                brightness = int(raw["brightness"])
            except (TypeError, ValueError):
                errors.append(f"action #{i} has invalid brightness: {raw.get('brightness')!r}")
                continue
            action["brightness"] = max(0, min(255, brightness))
        elif action_name == "set_brightness":
            errors.append(f"action #{i} missing brightness")
            continue

        if action_name in {"turn_on", "set_color"}:
            has_color = normalize_color_fields(raw, action)
            if action_name == "set_color" and not has_color:
                errors.append(f"action #{i} missing color/rgb/hex")
                continue

        if action_name == "get_time":
            try:
                action["offset_minutes"] = int(raw.get("offset_minutes", 0) or 0)
            except (TypeError, ValueError):
                errors.append(f"action #{i} has invalid offset_minutes: {raw.get('offset_minutes')!r}")
                continue
        elif action_name == "get_date":
            try:
                action["offset_days"] = int(raw.get("offset_days", 0) or 0)
            except (TypeError, ValueError):
                errors.append(f"action #{i} has invalid offset_days: {raw.get('offset_days')!r}")
                continue
        elif action_name == "get_weather":
            location = str(raw.get("location") or "Tallinn").strip() or "Tallinn"
            mode = str(raw.get("mode") or "current").strip().lower()
            if mode not in {"current", "rain", "clothing"}:
                mode = "current"
            try:
                action["offset_days"] = int(raw.get("offset_days", 0) or 0)
            except (TypeError, ValueError):
                errors.append(f"action #{i} has invalid offset_days: {raw.get('offset_days')!r}")
                continue
            action["location"] = location
            action["mode"] = mode
        elif action_name == "run_effect":
            effect = str(raw.get("effect") or "").strip().lower().replace("-", "_")
            aliases = {
                "disco": "disco",
                "disko": "disco",
                "party": "disco",
                "color_cycle": "color_cycle",
                "cycle_colors": "color_cycle",
                "colors": "color_cycle",
                "pulse": "pulse",
                "vilkumine": "pulse",
                "blink": "pulse",
            }
            effect = aliases.get(effect, effect)
            if effect not in {"disco", "color_cycle", "pulse"}:
                errors.append(f"action #{i} has unsupported effect: {raw.get('effect')!r}")
                continue
            action["effect"] = effect
            try:
                duration_seconds = float(raw.get("duration_seconds", 6) or 6)
            except (TypeError, ValueError):
                errors.append(f"action #{i} has invalid duration_seconds: {raw.get('duration_seconds')!r}")
                continue
            try:
                step_seconds = float(raw.get("step_seconds", 0.35) or 0.35)
            except (TypeError, ValueError):
                errors.append(f"action #{i} has invalid step_seconds: {raw.get('step_seconds')!r}")
                continue
            action["duration_seconds"] = max(0.5, min(12.0, duration_seconds))
            action["step_seconds"] = max(0.12, min(2.0, step_seconds))
            if "brightness" in raw:
                try:
                    brightness = int(raw["brightness"])
                except (TypeError, ValueError):
                    errors.append(f"action #{i} has invalid brightness: {raw.get('brightness')!r}")
                    continue
                action["brightness"] = max(0, min(255, brightness))
            normalize_color_fields(raw, action)

        normalized.append(action)

    return normalized, errors
