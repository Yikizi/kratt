from __future__ import annotations

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
}

ENTITY_ACTIONS = {"turn_on", "turn_off", "set_brightness", "set_color", "get_state", "run_effect"}

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

        if action_name in {"turn_on", "set_color"} and "color" in raw:
            color = str(raw.get("color") or "").strip()
            if color:
                action["color"] = color
            elif action_name == "set_color":
                errors.append(f"action #{i} missing color")
                continue
        elif action_name == "set_color":
            errors.append(f"action #{i} missing color")
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
            if "color" in raw:
                color = str(raw.get("color") or "").strip()
                if color:
                    action["color"] = color

        normalized.append(action)

    return normalized, errors
