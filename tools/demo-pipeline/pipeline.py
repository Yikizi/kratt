#!/usr/bin/env python3
"""Full interactive voice pipeline: wake word → STT → LLM → MCP → response.

Supports multi-model temporal consensus detection (matching `kratt live`),
real WiZ bulb control, interaction logging, and Space-key false-trigger reset.

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
import json
import os
import re
import shlex
import subprocess
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import sounddevice as sd

# --- Importable package bootstrap ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.demo_pipeline.intent.actions import normalize_intent_actions
from tools.demo_pipeline.intent.responses_et import (
    demo_response_for_action,
    natural_date_et,
    time_response_et,
    weather_response_et,
)
from tools.demo_pipeline.mcp_client import MCPClient
from tools.demo_pipeline.persona import (
    capabilities_response,
    color_clarification,
    holding_phrase,
    soften_weather_response,
)
from tools.demo_pipeline.paths import (
    LOG_DIR,
    MOCK_MCP_SERVER,
    PROJECT_ROOT,
    STT_MODEL_DIR,
    WIZ_CLI,
    WIZ_MCP_SERVER,
)
from tools.demo_pipeline.prompts import (
    SYSTEM_PROMPT_MOCK,
    SYSTEM_PROMPT_WIZ,
    SYSTEM_PROMPT_WIZ_BASH,
    SYSTEM_PROMPT_WIZ_INTENT_EXPERT,
    build_wiz_system_prompt,
)
from tools.demo_pipeline.telemetry import InteractionLogger, StepTimer
from tools.demo_pipeline.keyboard import TerminalKeyOverride
from tools.demo_pipeline.audio import (
    SAMPLE_RATE,
    SpeechRecognizer,
    record_and_transcribe_streaming,
    record_until_silence,
)
from tools.demo_pipeline.tts import TTS_SPEAKER, TTS_URL, TextToSpeech
from tools.demo_pipeline.wakeword import (
    TFLITE_AVAILABLE,
    StreamingModel,
    find_latest_model,
    resolve_models,
)
from tools.demo_pipeline.wiz_ble_bridge import (
    close_ble_bridge_connection,
    execute_wiz_ble_action,
    get_default_wiz_bridge_bulb_ip,
    load_ble_bridge_sender,
    parse_bulb_ips,
    warm_ble_bridge_connection,
)
from tools.demo_pipeline.helper_conversation import ask_helper_assistant, warm_helper_assistant
from tools.demo_pipeline.llm_backends import (
    DEFAULT_HELPER_RPC_TIMEOUT,
    DEFAULT_LLM_MODEL,
    DEFAULT_PI_MODEL,
    DEFAULT_PI_RPC_TIMEOUT,
    DEFAULT_PI_THINKING,
    close_pi_rpc_clients,
    configure_llm_backend,
    llm_backend_label,
    llm_parse_intent,
)

FRAME_MS = 10


# ANSI
BOLD = "\033[1m"
RESET = "\033[0m"
COLORS = ["\033[32m", "\033[33m", "\033[36m", "\033[35m", "\033[34m", "\033[91m"]



SAFE_WIZ_SUBCOMMANDS = {
    "on", "off", "brightness", "color", "temp", "scene", "status", "list",
    "disco", "chase", "pulse", "stop",
}
MAX_SAFE_WIZ_COMMANDS = 20
MAX_SAFE_SLEEP_SECONDS = 2.0
MAX_SAFE_TOTAL_SLEEP_SECONDS = 10.0
DANGEROUS_SHELL_CHARS_RE = re.compile(r"[|<>`$\\()]")


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


def _explicit(args, name: str) -> bool:
    return bool(getattr(args, "_explicit", {}).get(name))


def _set_profile_default(args, name: str, value: Any) -> None:
    if not _explicit(args, name):
        setattr(args, name, value)


def _set_profile_wiz_transport(args, *, ble_bridge: bool = False) -> None:
    if not _explicit(args, "wiz"):
        args.wiz = True
    if ble_bridge and not _explicit(args, "ble_bridge"):
        args.ble_bridge = True


def apply_demo_profile(args) -> None:
    """Collapse long demo command lines into named profiles."""
    if not args.profile:
        return

    if args.profile == "demo":
        _set_profile_default(args, "claude_code", False)
        _set_profile_wiz_transport(args, ble_bridge=True)
        if args.models is None:
            args.models = ["v16c"]
        if not _explicit(args, "threshold"):
            args.threshold = [0.996]

    elif args.profile == "wiz-claude":
        _set_profile_default(args, "claude_code", True)
        _set_profile_wiz_transport(args)
        if args.models is None:
            args.models = ["v16c"]
        if not _explicit(args, "threshold"):
            args.threshold = [0.996]
        if not _explicit(args, "bulbs"):
            args.bulbs = args.bulbs or _cached_wiz_bulbs()

    elif args.profile == "wiz-claude-safe":
        _set_profile_default(args, "claude_code", True)
        _set_profile_wiz_transport(args)
        if args.models is None:
            args.models = ["v16c"]
        if not _explicit(args, "threshold"):
            args.threshold = [0.997]
        if not _explicit(args, "wake_hold_frames"):
            args.wake_hold_frames = max(args.wake_hold_frames, 5)
        if not _explicit(args, "wake_model_cooldown"):
            args.wake_model_cooldown = max(args.wake_model_cooldown, 6.0)
        if not _explicit(args, "post_trigger_cooldown"):
            args.post_trigger_cooldown = max(args.post_trigger_cooldown, 6.0)
        if not _explicit(args, "bulbs"):
            args.bulbs = args.bulbs or _cached_wiz_bulbs()

    elif args.profile == "wiz-manual":
        _set_profile_default(args, "claude_code", False)
        _set_profile_wiz_transport(args, ble_bridge=True)
        args.no_wakeword = True

    elif args.profile == "wiz-7b":
        # Higher-accuracy LLM (qwen2.5:7b ~98.6% intent acc, ~700ms warm) for UX trials
        _set_profile_default(args, "claude_code", False)
        _set_profile_wiz_transport(args, ble_bridge=True)
        _set_profile_default(args, "llm", "qwen2.5:7b")
        if args.models is None:
            args.models = ["v16c"]
        if not _explicit(args, "threshold"):
            args.threshold = [0.996]


def _parse_safe_wiz_command_sequence(raw: str) -> list[list[str]]:
    """Parse an LLM-produced WiZ command sequence into safe argv lists.

    Only `wiz ...` subcommands and bounded `sleep N` pauses are allowed. No raw
    shell syntax reaches subprocess.
    """
    command = (raw or "").strip()
    if not command or DANGEROUS_SHELL_CHARS_RE.search(command):
        return []

    normalized = re.sub(r"\s*&&\s*", ";", command)
    parts = [part.strip() for part in normalized.split(";") if part.strip()]
    if not parts or len(parts) > MAX_SAFE_WIZ_COMMANDS:
        return []

    argv_list: list[list[str]] = []
    total_sleep = 0.0
    for part in parts:
        try:
            tokens = shlex.split(part)
        except ValueError:
            return []
        if not tokens:
            continue

        head = tokens[0]
        if head == "sleep":
            if len(tokens) != 2:
                return []
            try:
                seconds = float(tokens[1])
            except ValueError:
                return []
            if seconds < 0 or seconds > MAX_SAFE_SLEEP_SECONDS:
                return []
            total_sleep += seconds
            if total_sleep > MAX_SAFE_TOTAL_SLEEP_SECONDS:
                return []
            argv_list.append(["sleep", str(seconds)])
            continue

        if Path(head).name != "wiz" or len(tokens) < 2:
            return []
        subcommand = tokens[1]
        if subcommand not in SAFE_WIZ_SUBCOMMANDS:
            return []
        argv_list.append([str(WIZ_CLI), *tokens[1:]])

    return argv_list


def _sanitize_wiz_bash_command(raw: str) -> str:
    return (raw or "").strip() if _parse_safe_wiz_command_sequence(raw) else ""


def llm_plan_wiz_command(user_text: str) -> dict:
    data = llm_parse_intent(user_text, SYSTEM_PROMPT_WIZ_BASH)
    command = _sanitize_wiz_bash_command(data.get("command", ""))
    return {"command": command, "response": data.get("response", "")}


def execute_wiz_cli_command(command: str) -> tuple[str, int]:
    commands = _parse_safe_wiz_command_sequence(command)
    if not commands:
        return "Rejected unsafe WiZ command", 2

    outputs: list[str] = []
    effective_rc = 0
    for argv in commands:
        if argv[0] == "sleep":
            time.sleep(float(argv[1]))
            continue
        proc = subprocess.run(
            argv,
            shell=False,
            capture_output=True,
            text=True,
            timeout=45,
        )
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        if out or err:
            outputs.append(out if out else err)
        if proc.returncode != 0 and effective_rc == 0:
            effective_rc = proc.returncode

    return "\n".join(outputs), effective_rc


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


# ============================================================
# Audio recording (VAD-based stop)
# ============================================================



# ============================================================
# Model loading
# ============================================================



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
    intent_prompt = SYSTEM_PROMPT_WIZ_INTENT_EXPERT if args.wiz and not args.wiz_bash else system_prompt
    if args.wiz_bash:
        system_prompt = SYSTEM_PROMPT_WIZ_BASH
        intent_prompt = SYSTEM_PROMPT_WIZ_BASH

    if args.wiz_bash and not WIZ_CLI.exists():
        sys.exit(f"wiz CLI not found: {WIZ_CLI}")
    startup_timer.mark("prompts_ready", "llm_tool_parser")

    # --- Wake word models ---
    models: list[StreamingModel] = []
    model_tags: list[str] = []
    if not args.no_wakeword:
        if not TFLITE_AVAILABLE:
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
    wiz_bulb_ips = parse_bulb_ips(args.bulbs)
    ha = None

    if args.wiz_bash:
        pass
    elif args.ble_bridge:
        print(f"  Using BLE bridge transport ({len(wiz_bulb_ips)} bulb target(s))")
        try:
            load_ble_bridge_sender()
            print("  BLE bridge: connecting/warming GATT session...")
            if not warm_ble_bridge_connection():
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
    if args.wiz and not args.wiz_bash:
        print("  Intent mode: LLM tool-call parser")
    try:
        llm_parse_intent("tere", intent_prompt)
        startup_timer.mark("llm_warmup_done")
        print(f"  LLM ready")
    except Exception as e:
        startup_timer.mark("llm_warmup_failed", str(e))
        print(f"  LLM warmup failed: {e}")
        print("  Make sure the selected LLM backend is available")
        demo_log_fh.close()
        logger.close()
        if ha is not None:
            ha.close()
        close_ble_bridge_connection()
        close_pi_rpc_clients()
        return

    # --- Helper-model warmup (non-blocking) ---
    helper_warmup_state: dict[str, Any] = {"started": False, "ready": False, "error": None}

    def _background_helper_warmup() -> None:
        helper_warmup_state["started"] = True
        started = time.monotonic()
        try:
            warm_helper_assistant(timeout_s=args.helper_warmup_timeout)
            helper_warmup_state["ready"] = True
            startup_timer.mark(
                "helper_warmup_done",
                f"ms={int((time.monotonic() - started) * 1000)} model={args.pi_model}",
            )
            print(f"  Helper ready: pi-rpc:{args.pi_model}:{args.pi_thinking}")
        except Exception as exc:
            helper_warmup_state["error"] = str(exc)
            startup_timer.mark("helper_warmup_failed", str(exc))
            print(f"  Helper warmup failed: {exc}")

    if not args.no_helper and args.helper_warmup:
        print(f"  Helper: warming pi-rpc:{args.pi_model}:{args.pi_thinking} in background...")
        threading.Thread(
            target=_background_helper_warmup,
            name="kratt-helper-warmup",
            daemon=True,
        ).start()
    else:
        startup_timer.mark("helper_warmup_skipped")

    # --- Ready ---
    false_trigger_override = TerminalKeyOverride(
        enabled=bool(models) and not args.no_false_trigger_key
    )
    false_trigger_key_enabled = false_trigger_override.start()

    print(f"\n{'=' * 60}")
    if models:
        if n_models > 1:
            print(
                f"  Consensus: {min_consensus}/{n_models} within {args.consensus_window_ms}ms"
            )
        print(f'  Listening for "Kuule Kratt"...')
        if false_trigger_key_enabled:
            print("  False trigger override: press Space after a wake to cancel/reset")
        elif not args.no_false_trigger_key:
            print("  False trigger override: unavailable (stdin is not interactive)")
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
        elif action_name == "run_effect":
            light_state.update({"known": True, "on": True})

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

    def execute_local_info_action(action_name: str, action: dict[str, Any]) -> tuple[str, bool]:
        if action_name == "get_time":
            return time_response_et(int(action.get("offset_minutes", 0) or 0)), True
        if action_name == "get_date":
            return natural_date_et(int(action.get("offset_days", 0) or 0)), True
        if action_name == "get_weather":
            mode = str(action.get("mode") or "current")
            result = weather_response_et(str(action.get("location") or "Tallinn"), mode=mode)
            return soften_weather_response(result, mode=mode, turn_seq=turn_seq), True
        if action_name == "get_capabilities":
            return capabilities_response(turn_seq), True
        return "", False

    local_runtime_actions = {"get_time", "get_date", "get_weather", "get_capabilities"}

    def speak_intermediate(text: str, turn_timer: StepTimer, label: str) -> float:
        text = (text or "").strip()
        if not text:
            return 0.0
        print(f"\n  KRATT: {BOLD}{text}{RESET}")
        if not tts_available:
            turn_timer.mark(f"{label}_tts_skipped", "tts_unavailable")
            return 0.0
        try:
            turn_timer.mark(f"{label}_tts_start")
            tts_s = tts.speak(text)
            turn_timer.mark(f"{label}_tts_done", f"tts={tts_s:.3f}s")
            print(f"  TTS: {tts_s:.1f}s")
            return tts_s
        except Exception as exc:
            turn_timer.mark(f"{label}_tts_error", str(exc))
            print(f"  TTS error: {exc}")
            return 0.0

    def record_followup_text(turn_timer: StepTimer, idx: int) -> tuple[str, float, float, float]:
        print("  Recording follow-up... (answer now, no wake word needed)")
        started = time.monotonic()
        turn_timer.mark(f"followup_{idx}_record_start")
        if args.streaming_stt:
            audio2, text2, stt2 = record_and_transcribe_streaming(
                stt,
                max_seconds=args.followup_max_seconds,
                initial_silence_timeout=args.followup_initial_silence_timeout,
            )
        else:
            audio2 = record_until_silence(
                max_seconds=args.followup_max_seconds,
                initial_silence_timeout=args.followup_initial_silence_timeout,
            )
            t_decode = time.monotonic()
            text2 = stt.transcribe(audio2) if len(audio2) else ""
            stt2 = time.monotonic() - t_decode
        rec2 = time.monotonic() - started
        audio_s = float(len(audio2)) / SAMPLE_RATE if audio2 is not None else 0.0
        turn_timer.mark(
            f"followup_{idx}_record_done",
            f"rec={rec2:.3f}s audio={audio_s:.3f}s stt={stt2:.3f}s text={text2!r}",
        )
        print(f'  Follow-up STT (rec={rec2:.1f}s decode={stt2:.1f}s): "{text2}"')
        return text2.strip(), rec2, stt2, audio_s

    def ask_helper_with_followups(
        *,
        original_transcript: str,
        helper_question: str,
        turn_timer: StepTimer,
    ) -> tuple[str, float, list[dict[str, Any]], str | None]:
        helper_messages = [{"role": "user", "text": helper_question or original_transcript}]
        intermediate_tts = 0.0
        helper_turns: list[dict[str, Any]] = []
        error: str | None = None

        for idx in range(1, max(1, args.helper_max_turns) + 1):
            started = time.monotonic()
            turn_timer.mark(f"helper_{idx}_start")
            try:
                result = ask_helper_assistant(helper_messages, timeout_s=args.helper_timeout)
            except Exception as exc:
                error = str(exc)
                turn_timer.mark(f"helper_{idx}_error", error)
                return "Vabandust, abimudel ei vastanud praegu.", intermediate_tts, helper_turns, error

            elapsed = time.monotonic() - started
            say = str(result.get("say") or "").strip()
            ask_user = result.get("ask_user")
            done = bool(result.get("done", not ask_user))
            helper_turns.append(
                {"idx": idx, "latency_ms": int(elapsed * 1000), "say": say, "ask_user": ask_user, "done": done}
            )
            turn_timer.mark(
                f"helper_{idx}_done",
                f"latency={elapsed:.3f}s done={done} ask_user={bool(ask_user)}",
            )

            if ask_user and not done:
                question = say or str(ask_user)
                intermediate_tts += speak_intermediate(question, turn_timer, f"helper_{idx}_question")
                helper_messages.append({"role": "assistant", "text": question})
                follow_text, _, _, audio_s = record_followup_text(turn_timer, idx)
                if audio_s < 0.3 or not follow_text:
                    return "Ma ei kuulnud vastust. Proovime hiljem uuesti.", intermediate_tts, helper_turns, None
                if follow_text.lower().strip(" .!?…") in {"aitäh", "aitah", "tänan", "tanan", "lõpeta", "lopeta", "pole vaja"}:
                    return "Olgu, lõpetan selle vestluse.", intermediate_tts, helper_turns, None
                helper_messages.append({"role": "user", "text": follow_text})
                continue

            return say or "Valmis.", intermediate_tts, helper_turns, None

        return "See vestlus läks liiga pikaks, lõpetan siinkohal.", intermediate_tts, helper_turns, None

    def prepare_next_listen(
        *,
        cooldown: bool = True,
        hard_reset_wake: bool = False,
        clear_wake_cooldowns: bool = False,
    ) -> None:
        """Reset demo wake state before reopening the microphone.

        Normal early exits keep post-trigger dead-time to avoid residual speech
        loops. Manual false-trigger override is different: the operator wants a
        clean, immediate retry, so it can request a hard wake-model reset and no
        sleep.
        """
        nonlocal audio_buffer, last_consensus_time
        recent_detections.clear()
        audio_buffer = bytearray()
        if models:
            for m in models:
                m.reset(hard=hard_reset_wake, clear_cooldown=clear_wake_cooldowns)
        if clear_wake_cooldowns:
            last_consensus_time = 0.0
        if cooldown and models and args.post_trigger_cooldown > 0:
            print(f"  Cooldown {args.post_trigger_cooldown:.1f}s before listening again...")
            time.sleep(args.post_trigger_cooldown)
        if models:
            print(f'  Listening for "Kuule Kratt"...\n')

    def handle_false_trigger_override(
        turn_timer: StepTimer,
        wake_prob: float | None,
        wake_models_agreed: list[str],
        audio: np.ndarray,
        t_rec: float,
        t_stt: float = 0.0,
    ) -> None:
        audio_duration_s = round(float(len(audio)) / SAMPLE_RATE, 3) if audio is not None else 0.0
        turn_timer.mark(
            "false_trigger_manual_override",
            f"audio={audio_duration_s:.3f}s rec={t_rec:.3f}s",
        )
        log_line(f"  {BOLD}>>> MANUAL OVERRIDE: false trigger reset <<<{RESET}")
        logger.log_interaction(
            {
                "outcome": "false_trigger_manual_override",
                "manual_override_key": "space",
                "wake_word_prob": wake_prob,
                "wake_models": wake_models_agreed,
                "audio_duration_s": audio_duration_s,
                "rec_duration_s": round(t_rec, 3),
                "stt_latency_ms": int(t_stt * 1000),
                "timing": turn_timer.as_dict(),
            }
        )

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
            if false_trigger_key_enabled:
                false_trigger_override.arm()
                print("  False trigger? Press Space to reset.")

            t0 = time.monotonic()
            if args.streaming_stt:
                turn_timer.mark("record_streaming_stt_start")
                print("  Recording + streaming STT... (speak now, stops on silence)")
                audio, transcript, t_stt = record_and_transcribe_streaming(
                    stt,
                    initial_silence_timeout=args.initial_silence_timeout,
                    cancel_event=false_trigger_override.cancel_event
                    if false_trigger_key_enabled
                    else None,
                )
                t_rec = time.monotonic() - t0
                turn_timer.mark("record_streaming_stt_done", f"rec={t_rec:.3f}s decode={t_stt:.3f}s")
                if false_trigger_override.consume():
                    handle_false_trigger_override(turn_timer, wake_prob, wake_models_agreed, audio, t_rec, t_stt)
                    prepare_next_listen(
                        cooldown=False,
                        hard_reset_wake=True,
                        clear_wake_cooldowns=True,
                    )
                    continue
                print(f"  Recorded {t_rec:.1f}s of audio")
                print(f'  STT streamed (decode={t_stt:.1f}s): "{transcript}"')
            else:
                turn_timer.mark("record_start")
                print("  Recording... (speak now, stops on silence)")
                audio = record_until_silence(
                    initial_silence_timeout=args.initial_silence_timeout,
                    cancel_event=false_trigger_override.cancel_event
                    if false_trigger_key_enabled
                    else None,
                )
                t_rec = time.monotonic() - t0
                turn_timer.mark("record_done", f"rec={t_rec:.3f}s audio={float(len(audio)) / SAMPLE_RATE:.3f}s")
                if false_trigger_override.consume():
                    handle_false_trigger_override(turn_timer, wake_prob, wake_models_agreed, audio, t_rec)
                    prepare_next_listen(
                        cooldown=False,
                        hard_reset_wake=True,
                        clear_wake_cooldowns=True,
                    )
                    continue
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
            helper_llm_s = 0.0
            intermediate_tts_s = 0.0
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
                turn_timer.mark("llm_intent_start", llm_backend_label())
                action_errors: list[str] = []
                try:
                    parsed = llm_parse_intent(transcript, intent_prompt)
                    default_entity_id = "all" if args.wiz else "light.elutuba"
                    actions, action_errors = normalize_intent_actions(
                        parsed.get("actions", []),
                        default_entity_id=default_entity_id,
                    )
                    if action_errors and not actions:
                        llm1_error = "invalid_actions"
                except Exception as e:
                    parsed = {}
                    actions = []
                    llm1_error = str(e)
                t_llm1 = time.monotonic() - t2
                turn_timer.mark("llm_intent_done", f"llm={t_llm1:.3f}s actions={len(actions)} error={llm1_error}")
                print(f"  LLM ({t_llm1:.1f}s): {json.dumps(actions, ensure_ascii=False)}")
                for err in action_errors:
                    print(f"  Skipping invalid action: {err}")
                    turn_timer.mark("action_validation_error", err)
                if llm1_error:
                    print(f"  LLM error: {llm1_error}")

                route = str(parsed.get("route") or "").strip().lower()
                if route not in {"execute", "clarify", "ask_help"}:
                    route = "execute" if actions else "clarify"
                turn_timer.mark("route_selected", route)
                print(f"  Route: {route}")

                if route == "ask_help" and args.no_helper and not llm1_error:
                    parsed["response"] = "See vajab abimudelit, aga abimudel on praegu välja lülitatud."
                    actions = []
                elif route == "ask_help" and not llm1_error:
                    holding = holding_phrase(transcript)
                    helper_question = str(parsed.get("question") or transcript).strip()
                    intermediate_tts_s += speak_intermediate(holding, turn_timer, "helper_holding")
                    print("  Asking helper model...")
                    helper_started = time.monotonic()
                    helper_response, helper_tts, helper_turns, helper_error = ask_helper_with_followups(
                        original_transcript=transcript,
                        helper_question=helper_question,
                        turn_timer=turn_timer,
                    )
                    helper_llm_s = time.monotonic() - helper_started
                    intermediate_tts_s += helper_tts
                    if helper_error:
                        llm2_error = helper_error
                    parsed["response"] = helper_response
                    actions = []
                    executed_actions.append(
                        {
                            "action": "ask_help",
                            "args": {"question": helper_question},
                            "result": helper_response,
                            "ok": helper_error is None,
                            "helper_turns": helper_turns,
                        }
                    )
                    tool_results.append(f"ask_help: {helper_response}")
                    turn_timer.mark(
                        "helper_done",
                        f"helper={helper_llm_s:.3f}s turns={len(helper_turns)} error={helper_error}",
                    )
                elif route == "clarify" and not actions and not llm1_error:
                    clarification = str(parsed.get("response") or "").strip()
                    if "värv" in clarification.lower() or "värvi" in transcript.lower():
                        clarification = color_clarification(transcript)
                    if not clarification:
                        clarification = "Täpsusta natuke ja ma proovin uuesti."
                    intermediate_tts_s += speak_intermediate(clarification, turn_timer, "clarify_question")
                    follow_text, _, _, follow_audio_s = record_followup_text(turn_timer, 1)
                    if follow_audio_s < 0.3 or not follow_text:
                        parsed["response"] = "Ma ei kuulnud täpsustust. Proovime hiljem uuesti."
                    elif follow_text.lower().strip(" .!?…") in {"aitäh", "aitah", "tänan", "tanan", "lõpeta", "lopeta", "pole vaja"}:
                        parsed["response"] = "Olgu, jätan pooleli."
                    else:
                        try:
                            turn_timer.mark("clarify_reparse_start")
                            reparsed = llm_parse_intent(
                                f"Algne käsk: {transcript}\nKasutaja täpsustus: {follow_text}",
                                intent_prompt,
                            )
                            reparsed_actions, reparse_errors = normalize_intent_actions(
                                reparsed.get("actions", []),
                                default_entity_id="all" if args.wiz else "light.elutuba",
                            )
                            parsed = reparsed
                            actions = reparsed_actions
                            action_errors.extend(reparse_errors)
                            if reparse_errors and not actions:
                                llm1_error = "invalid_actions"
                            turn_timer.mark(
                                "clarify_reparse_done",
                                f"actions={len(actions)} errors={len(reparse_errors)}",
                            )
                            print(f"  Clarified LLM: {json.dumps(actions, ensure_ascii=False)}")
                        except Exception as exc:
                            parsed["response"] = "Vabandust, täpsustuse mõistmine ebaõnnestus."
                            llm1_error = str(exc)
                            turn_timer.mark("clarify_reparse_error", str(exc))

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
                        if action_name in local_runtime_actions:
                            result, ok = execute_local_info_action(action_name, action_copy)
                        else:
                            result, ok = execute_wiz_ble_action(action_name, action_copy, wiz_bulb_ips)
                            if not ok and llm1_error is None:
                                llm1_error = "ble_bridge_command_failed"
                        tool_results.append(f"{action_name}: {result}")
                        update_light_state(action_name, action_copy, ok)
                        executed_actions.append(
                            {"action": action_name, "args": action_copy, "result": result, "ok": ok}
                        )
                        action_ms = int((time.monotonic() - action_t) * 1000)
                        turn_timer.mark(
                            f"action_{i}_done",
                            f"{action_name} ok={ok} ms={action_ms} result={result}",
                        )
                        print(f"  -> {action_name}: {result} ({action_ms}ms)")
                else:
                    for i, action in enumerate(actions, start=1):
                        if not isinstance(action, dict):
                            print(f"  Skipping malformed action: {action}")
                            turn_timer.mark("execute_skip_malformed", str(action))
                            continue
                        action_copy = dict(action)
                        action_name = action_copy.pop("action", "")
                        action_t = time.monotonic()
                        turn_timer.mark(f"action_{i}_start", action_name)
                        if action_name in local_runtime_actions:
                            result, ok = execute_local_info_action(action_name, action_copy)
                        else:
                            ok = True
                            try:
                                result = ha.execute(action_name, action_copy)
                            except (RuntimeError, TimeoutError) as e:
                                result = f"MCP error: {e}"
                                ok = False
                            if not ok and llm1_error is None:
                                llm1_error = "mcp_command_failed"
                        tool_results.append(f"{action_name}: {result}")
                        update_light_state(action_name, action_copy, ok)
                        executed_actions.append(
                            {"action": action_name, "args": action_copy, "result": result, "ok": ok}
                        )
                        action_ms = int((time.monotonic() - action_t) * 1000)
                        turn_timer.mark(
                            f"action_{i}_done",
                            f"{action_name} ms={action_ms} result={result}",
                        )
                        print(f"  -> {action_name}: {result} ({action_ms}ms)")
                turn_timer.mark("execute_done", f"executed={len(executed_actions)} error={llm1_error}")

                # --- Response: no second LLM call on the demo hot path. ---
                t3 = time.monotonic()
                turn_timer.mark("response_start")
                planned_response = str(parsed.get("response", "")).strip()
                if llm1_error in {"ble_bridge_command_failed", "mcp_command_failed", "invalid_actions"}:
                    response = "Vabandust, käsku ei saanud täita."
                elif executed_actions and executed_actions[0].get("action") == "get_state":
                    if executed_actions[0].get("result"):
                        response = str(executed_actions[0].get("result"))
                        print("  Response: tool state")
                    else:
                        response = cached_light_state_response()
                        print("  Response: cached state")
                elif executed_actions and executed_actions[0].get("action") in local_runtime_actions:
                    response = str(executed_actions[0].get("result") or planned_response or "Vaatan.")
                    print("  Response: local info")
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
                t_llm2 = helper_llm_s + (time.monotonic() - t3)
                turn_timer.mark("response_done", f"llm2={t_llm2:.3f}s error={llm2_error} response={response!r}")
                if llm2_error:
                    print(f"  Response LLM error: {llm2_error}")

            t_total_no_tts = time.monotonic() - t0
            turn_timer.mark("response_print_ready", f"total_no_tts={t_total_no_tts:.3f}s")
            print(f"\n  KRATT: {BOLD}{response}{RESET}")

            # --- TTS: speak the response ---
            t_tts = intermediate_tts_s
            if tts_available and response:
                try:
                    turn_timer.mark("tts_start")
                    final_tts_s = tts.speak(response)
                    t_tts += final_tts_s
                    turn_timer.mark("tts_done", f"tts={final_tts_s:.3f}s total_tts={t_tts:.3f}s")
                    print(f"  TTS: {final_tts_s:.1f}s")
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
        false_trigger_override.stop()
        demo_log_fh.close()
        logger.close()
        if ha is not None:
            ha.close()
        close_ble_bridge_connection()
        close_pi_rpc_clients()


def _argv_has_option(argv: list[str], *options: str) -> bool:
    return any(arg == opt or arg.startswith(opt + "=") for arg in argv for opt in options)


def _mark_explicit_args(args: argparse.Namespace, argv: list[str]) -> None:
    args._explicit = {
        "profile": _argv_has_option(argv, "--profile"),
        "models": _argv_has_option(argv, "--models"),
        "threshold": _argv_has_option(argv, "--threshold"),
        "consensus": _argv_has_option(argv, "--consensus"),
        "consensus_window_ms": _argv_has_option(argv, "--consensus-window-ms"),
        "wake_hold_frames": _argv_has_option(argv, "--wake-hold-frames"),
        "wake_model_cooldown": _argv_has_option(argv, "--wake-model-cooldown"),
        "post_trigger_cooldown": _argv_has_option(argv, "--post-trigger-cooldown"),
        "initial_silence_timeout": _argv_has_option(argv, "--initial-silence-timeout"),
        "streaming_stt": _argv_has_option(argv, "--streaming-stt", "--no-streaming-stt"),
        "wiz": _argv_has_option(argv, "--wiz", "--no-wiz"),
        "wiz_bash": _argv_has_option(argv, "--wiz-bash"),
        "ble_bridge": _argv_has_option(argv, "--ble-bridge"),
        "bulbs": _argv_has_option(argv, "--bulbs"),
        "llm": _argv_has_option(argv, "--llm"),
        "pi_cli": _argv_has_option(argv, "--pi-cli", "--pi-gpt"),
        "pi_model": _argv_has_option(argv, "--pi-model"),
        "pi_thinking": _argv_has_option(argv, "--pi-thinking"),
        "pi_reset_each_turn": _argv_has_option(argv, "--pi-reset-each-turn"),
        "pi_rpc_timeout": _argv_has_option(argv, "--pi-rpc-timeout"),
        "no_helper": _argv_has_option(argv, "--no-helper"),
        "helper_warmup": _argv_has_option(argv, "--helper-warmup", "--no-helper-warmup"),
        "helper_timeout": _argv_has_option(argv, "--helper-timeout"),
        "helper_warmup_timeout": _argv_has_option(argv, "--helper-warmup-timeout"),
        "helper_max_turns": _argv_has_option(argv, "--helper-max-turns"),
        "followup_initial_silence_timeout": _argv_has_option(argv, "--followup-initial-silence-timeout"),
        "followup_max_seconds": _argv_has_option(argv, "--followup-max-seconds"),
        "claude_code": _argv_has_option(argv, "--claude-code", "--no-claude-code"),
        "claude_session_id": _argv_has_option(argv, "--claude-session-id"),
        "log": _argv_has_option(argv, "--log"),
        "participant": _argv_has_option(argv, "--participant"),
        "task": _argv_has_option(argv, "--task"),
        "no_tts": _argv_has_option(argv, "--no-tts"),
        "no_tts_effects": _argv_has_option(argv, "--no-tts-effects"),
    }


def validate_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.ble_bridge and args.wiz_bash:
        parser.error("--ble-bridge and --wiz-bash are mutually exclusive")
    if args.pi_cli and args.claude_code:
        parser.error("--pi-cli and --claude-code are mutually exclusive")
    if (args.ble_bridge or args.wiz_bash) and args.wiz is False:
        parser.error("--ble-bridge/--wiz-bash require WiZ; remove --no-wiz")
    if _explicit(args, "bulbs") and args.wiz is False:
        parser.error("--bulbs requires WiZ; remove --no-wiz or omit --bulbs")

    if any(threshold < 0.0 or threshold > 1.0 for threshold in args.threshold):
        parser.error("--threshold values must be between 0.0 and 1.0")
    if args.consensus is not None:
        if args.no_wakeword:
            parser.error("--consensus is only valid when wake-word detection is enabled")
        if args.consensus < 1:
            parser.error("--consensus must be at least 1")
        if args.models and args.consensus > len(args.models):
            parser.error("--consensus cannot exceed the number of wake-word models")
    if args.consensus_window_ms <= 0:
        parser.error("--consensus-window-ms must be positive")
    if args.wake_hold_frames < 1:
        parser.error("--wake-hold-frames must be at least 1")
    if args.wake_model_cooldown < 0:
        parser.error("--wake-model-cooldown must be non-negative")
    if args.post_trigger_cooldown < 0:
        parser.error("--post-trigger-cooldown must be non-negative")
    if args.initial_silence_timeout <= 0:
        parser.error("--initial-silence-timeout must be positive")
    if args.pi_rpc_timeout <= 0:
        parser.error("--pi-rpc-timeout must be positive")
    if args.helper_timeout <= 0:
        parser.error("--helper-timeout must be positive")
    if args.helper_warmup_timeout <= 0:
        parser.error("--helper-warmup-timeout must be positive")
    if args.helper_max_turns < 1:
        parser.error("--helper-max-turns must be at least 1")
    if args.followup_initial_silence_timeout <= 0:
        parser.error("--followup-initial-silence-timeout must be positive")
    if args.followup_max_seconds <= 0:
        parser.error("--followup-max-seconds must be positive")
    if args.bulbs:
        try:
            bulb_targets = parse_bulb_ips(args.bulbs)
        except ValueError as exc:
            parser.error(str(exc))
        if not args.ble_bridge and any(target == "auto" for target in bulb_targets):
            parser.error("--bulbs auto is only valid with --ble-bridge")


def main():
    parser = argparse.ArgumentParser(description="Kratt full voice pipeline", allow_abbrev=False)
    parser.add_argument(
        "--profile",
        choices=["demo", "wiz-claude", "wiz-claude-safe", "wiz-manual", "wiz-7b"],
        default=None,
        help="Optional preset override; bare `kratt demo` has sane live-demo defaults.",
    )
    parser.add_argument(
        "--models",
        nargs="+",
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
        default=5,
        help="Require N consecutive above-threshold frames before wake trigger. Default: 5.",
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
        "--initial-silence-timeout",
        type=float,
        default=3.0,
        help="Seconds to wait for the user to start speaking after wake. Default: 3.0.",
    )
    parser.add_argument(
        "--no-wakeword", action="store_true", help="Skip wake word, manual trigger"
    )
    parser.add_argument(
        "--no-false-trigger-key",
        action="store_true",
        help="Disable Space key false-trigger override in wake-word mode.",
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
        help="Use real WiZ bulbs. Default: on via BLE bridge; use --no-wiz for Mock HA.",
    )
    parser.add_argument(
        "--wiz-bash",
        action="store_true",
        help="Use legacy LLM->wiz CLI command mode (safe allowlist, no raw shell)",
    )
    parser.add_argument(
        "--ble-bridge",
        action="store_true",
        help="Send WiZ JSON to bulbs over the ESP32 BLE bridge (default demo transport).",
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
        default=DEFAULT_LLM_MODEL,
        help=f"Ollama model name. Default: {DEFAULT_LLM_MODEL}",
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
        default=DEFAULT_PI_MODEL,
        help=f"pi CLI model. Default: {DEFAULT_PI_MODEL}",
    )
    parser.add_argument(
        "--pi-thinking",
        type=str,
        default=DEFAULT_PI_THINKING,
        help=f"pi CLI thinking level. Default: {DEFAULT_PI_THINKING}",
    )
    parser.add_argument(
        "--pi-reset-each-turn",
        action="store_true",
        help="Clear pi RPC conversation between turns. Safer, but slower; default keeps warm context for speed.",
    )
    parser.add_argument(
        "--pi-rpc-timeout",
        type=float,
        default=DEFAULT_PI_RPC_TIMEOUT,
        help=f"Timeout for one pi RPC LLM turn in seconds. Default: {DEFAULT_PI_RPC_TIMEOUT}.",
    )
    parser.add_argument(
        "--no-helper",
        action="store_true",
        help="Disable the pi/Codex helper route for general questions.",
    )
    parser.add_argument(
        "--helper-warmup",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Warm the pi/Codex helper in the background after local LLM startup. Default: true.",
    )
    parser.add_argument(
        "--helper-timeout",
        type=float,
        default=DEFAULT_HELPER_RPC_TIMEOUT,
        help=f"Timeout for one helper-model turn in seconds. Default: {DEFAULT_HELPER_RPC_TIMEOUT}.",
    )
    parser.add_argument(
        "--helper-warmup-timeout",
        type=float,
        default=20.0,
        help="Timeout for background helper warmup in seconds. Default: 20.0.",
    )
    parser.add_argument(
        "--helper-max-turns",
        type=int,
        default=10,
        help="Maximum helper conversation back-and-forth turns. Default: 10.",
    )
    parser.add_argument(
        "--followup-initial-silence-timeout",
        type=float,
        default=4.0,
        help="Seconds to wait for a follow-up answer without wake word. Default: 4.0.",
    )
    parser.add_argument(
        "--followup-max-seconds",
        type=float,
        default=8.0,
        help="Maximum seconds to record one follow-up answer. Default: 8.0.",
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
    argv = sys.argv[1:]
    args = parser.parse_args(argv)
    _mark_explicit_args(args, argv)

    apply_demo_profile(args)

    # Sane demo defaults: `kratt demo` should run the normal portable demo.
    # The designed/default deployment path is ESP32 BLE bridge -> WiZ UDP.
    # Explicit --no-wiz keeps Mock HA, and explicit --wiz without --ble-bridge
    # remains the escape hatch for direct LAN UDP/MCP.
    if (
        not _explicit(args, "wiz")
        and not _explicit(args, "ble_bridge")
        and not args.wiz_bash
    ):
        args.wiz = True
        args.ble_bridge = True

    # Explicit flags still override these defaults.
    if args.models is None and not args.no_wakeword:
        args.models = ["v16c"]
    if args.bulbs is None:
        if args.ble_bridge:
            args.bulbs = get_default_wiz_bridge_bulb_ip()
        else:
            args.bulbs = _cached_wiz_bulbs()
    if (args.ble_bridge or args.wiz_bash) and args.wiz is False:
        parser.error("--ble-bridge/--wiz-bash require WiZ; remove --no-wiz")
    if args.wiz_bash or args.ble_bridge:
        args.wiz = True
    if args.wiz is None:
        args.wiz = bool(args.bulbs)
    if not args.wiz and not _explicit(args, "bulbs"):
        args.bulbs = None

    validate_args(args, parser)

    configure_llm_backend(
        llm_model=args.llm,
        pi_model=args.pi_model,
        pi_thinking=args.pi_thinking,
        pi_reset_each_turn=args.pi_reset_each_turn,
        pi_rpc_timeout=args.pi_rpc_timeout,
        use_pi_cli=args.pi_cli,
        use_claude_code=False if args.pi_cli else args.claude_code,
        claude_session_id=args.claude_session_id,
        claude_session_started=True if args.claude_session_id else None,
    )

    run_pipeline(args)


if __name__ == "__main__":
    main()
