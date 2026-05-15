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
import contextlib
import json
import os
import re
import shlex
import subprocess
import sys
import time
import threading
import wave
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import sounddevice as sd

# --- Importable package bootstrap ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.demo_pipeline.beep import play_wake_beep
from tools.demo_pipeline.intent.actions import normalize_intent_actions
from tools.demo_pipeline.intent.stt_artifacts import normalize_stt_artifacts
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
    AIRFRYER_MCP_SERVER,
    LOG_DIR,
    MOCK_MCP_SERVER,
    PROJECT_ROOT,
    STT_MODEL_DIR,
    WIZ_CLI,
    WIZ_MCP_SERVER,
)
from tools.demo_pipeline.prompts import (
    SYSTEM_PROMPT_AIRFRYER_INTENT,
    SYSTEM_PROMPT_MOCK,
    SYSTEM_PROMPT_PI_CONVERSATIONAL_ASSISTANT,
    SYSTEM_PROMPT_RESPONSE_EN,
    SYSTEM_PROMPT_SMARTHOME_INTENT,
    SYSTEM_PROMPT_WIZ,
    SYSTEM_PROMPT_WIZ_BASH,
    SYSTEM_PROMPT_WIZ_INTENT_EXPERT,
    build_wiz_system_prompt,
)
from tools.demo_pipeline.telemetry import InteractionLogger, StepTimer
from tools.demo_pipeline.translation import DEFAULT_EN_ET_CT2_MODEL, EnglishToEstonianTranslator
from tools.demo_pipeline.keyboard import TerminalKeyOverride
from tools.demo_pipeline.audio import (
    SAMPLE_RATE,
    SpeechRecognizer,
    record_and_transcribe_streaming,
    record_until_silence,
)
from tools.demo_pipeline.serial_audio import (
    DEFAULT_SERIAL_BAUD,
    KorvoSerialAudioSource,
    record_and_transcribe_streaming_from_source,
    record_until_silence_from_source,
)
from tools.demo_pipeline.tts import TTS_SPEAKER, TTS_URL, TextToSpeech
from tools.demo_pipeline.wakeword import (
    TFLITE_AVAILABLE,
    StreamingModel,
    find_latest_model,
    resolve_models,
)
from tools.demo_pipeline.wiz_ble_bridge import (
    cancel_running_effect,
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
    llm_generate_json,
    llm_parse_intent,
    request_pi_rpc_json,
    reset_pi_rpc_session,
)

FRAME_MS = 10


# ANSI
BOLD = "\033[1m"
RESET = "\033[0m"
YELLOW = "\033[33m"
COLORS = ["\033[32m", "\033[33m", "\033[36m", "\033[35m", "\033[34m", "\033[91m"]


class DemoAudioRecorder:
    """Operator-toggled mono WAV recorder for free-form demo sessions."""

    def __init__(self, *, participant_id: str, session_id: str, log_dir: Path, log_event):
        self.participant_id = participant_id
        self.session_id = session_id
        self.log_dir = log_dir
        self.log_event = log_event
        self.active = False
        self.path: Path | None = None
        self._wav: wave.Wave_write | None = None
        self._lock = threading.Lock()
        self._started_mono = 0.0
        self._frames_written = 0

    def start(self, *, reason: str = "operator") -> Path | None:
        with self._lock:
            if self.active:
                return self.path
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            safe_participant = re.sub(r"[^A-Za-z0-9_.-]+", "_", self.participant_id)[:60] or "participant"
            out_dir = self.log_dir / safe_participant
            out_dir.mkdir(parents=True, exist_ok=True)
            self.path = out_dir / f"{safe_participant}_{stamp}_{self.session_id}.wav"
            self._wav = wave.open(str(self.path), "wb")
            self._wav.setnchannels(1)
            self._wav.setsampwidth(2)
            self._wav.setframerate(SAMPLE_RATE)
            self._frames_written = 0
            self._started_mono = time.monotonic()
            self.active = True
            path = self.path
        self.log_event(
            "audio_recording_started",
            {"path": str(path), "reason": reason, "sample_rate": SAMPLE_RATE, "channels": 1},
        )
        return path

    def stop(self, *, reason: str = "operator") -> Path | None:
        with self._lock:
            if not self.active:
                return self.path
            path = self.path
            duration_s = self._frames_written / SAMPLE_RATE if self._frames_written else 0.0
            wall_s = time.monotonic() - self._started_mono if self._started_mono else 0.0
            wav = self._wav
            self._wav = None
            self.active = False
            if wav is not None:
                wav.close()
        self.log_event(
            "audio_recording_stopped",
            {
                "path": str(path) if path else None,
                "reason": reason,
                "audio_duration_s": round(duration_s, 3),
                "wall_duration_s": round(wall_s, 3),
            },
        )
        return path

    def write_int16_bytes(self, data: bytes) -> None:
        if not data or not self.active:
            return
        with self._lock:
            if not self.active or self._wav is None:
                return
            self._wav.writeframes(data)
            self._frames_written += len(data) // 2

    def write_float_audio(self, audio: np.ndarray | None) -> None:
        if audio is None or not self.active:
            return
        pcm = (np.asarray(audio, dtype=np.float32).reshape(-1) * 32768.0).clip(-32768, 32767).astype(np.int16)
        self.write_int16_bytes(pcm.tobytes())


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
        # Kept for backward compatibility; current demo LLM is qwen3:8b.
        _set_profile_default(args, "claude_code", False)
        _set_profile_wiz_transport(args, ble_bridge=True)
        _set_profile_default(args, "llm", "qwen3:8b")
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
    if args.airfryer and args.ble_bridge:
        mode = "WiZ bridge over BLE + Airfryer MCP"
    elif args.airfryer and args.wiz:
        mode = "WiZ bulbs + Airfryer MCP"
    elif args.airfryer:
        mode = "Airfryer MCP"
    elif args.pi_conversation:
        mode = "Pi conversational cloud agent"
    elif args.wiz_bash:
        mode = "WiZ bash-agent"
    elif args.ble_bridge:
        mode = "WiZ bridge over BLE"
    else:
        mode = "WiZ bulbs" if args.wiz else "Mock HA"
    print(f"  Backend: {mode}")
    print(f"  LLM: {llm_backend_label()}")
    if args.pi_cli:
        print(f"  Pi tools: {args.pi_tools or 'disabled'}")
    print("=" * 60)

    korvo_audio: KorvoSerialAudioSource | None = None
    if args.audio_source == "korvo-serial":
        korvo_audio = KorvoSerialAudioSource(
            port=args.serial_port,
            baud=args.serial_baud,
            gain=args.serial_gain,
            channel=args.serial_channel,
        )
        print(
            f"  Audio: Korvo-2 serial PCM ({korvo_audio.port}, {args.serial_baud} baud, "
            f"channel={args.serial_channel}, STT gain={args.serial_gain:g}x)"
        )
        korvo_audio.start(wait_for_frame=True, timeout_s=args.serial_start_timeout)
        print("  Audio: Korvo-2 stream locked")
    else:
        print("  Audio: host default microphone (sounddevice)")
    startup_timer.mark("audio_source_ready", args.audio_source)

    if args.airfryer and args.wiz and not args.wiz_bash:
        system_prompt = SYSTEM_PROMPT_SMARTHOME_INTENT
        intent_prompt = SYSTEM_PROMPT_SMARTHOME_INTENT
    elif args.airfryer:
        system_prompt = SYSTEM_PROMPT_AIRFRYER_INTENT
        intent_prompt = SYSTEM_PROMPT_AIRFRYER_INTENT
    else:
        system_prompt = SYSTEM_PROMPT_WIZ if args.wiz else SYSTEM_PROMPT_MOCK
        if args.wiz and args.bulbs:
            system_prompt = build_wiz_system_prompt(len([b for b in args.bulbs.split(",") if b.strip()]))
        intent_prompt = SYSTEM_PROMPT_WIZ_INTENT_EXPERT if args.wiz and not args.wiz_bash else system_prompt
        if args.wiz_bash:
            system_prompt = SYSTEM_PROMPT_WIZ_BASH
            intent_prompt = SYSTEM_PROMPT_WIZ_BASH

    airfryer_hints = (
        "õhufrit", "õhu frit", "fritü", "frit", "airfryer", "air fryer",
        "friik", "nagits", "köögivil", "juurik", "kana", "kala",
    )
    light_hints = (
        "tuli", "tuled", "tule ", "lamp", "lambi", "pirn", "valgus", "valgust",
        "punane", "roheline", "sinine", "kollane", "lilla", "roosa", "oranž", "oranz",
        "valge", "värv", "disko", "vilguta", "pulseeri",
    )
    ambiguous_device_words = (
        "pane", "käivita", "lülita", "tööle", "sisse", "välja", "peata", "lõpeta", "stopp",
    )

    def select_intent_prompt_for_turn(text: str) -> tuple[str | None, str]:
        """Keep both-device mode reliable by routing to small domain prompts.

        The combined smart-home prompt is only used when the utterance clearly
        mentions both domains in one turn.
        """
        lowered = f" {text.lower()} "
        air = args.airfryer and any(hint in lowered for hint in airfryer_hints)
        light = args.wiz and any(hint in lowered for hint in light_hints)
        if args.airfryer and args.wiz and air and light and not args.wiz_bash:
            return SYSTEM_PROMPT_SMARTHOME_INTENT, "mixed"
        if air:
            return SYSTEM_PROMPT_AIRFRYER_INTENT, "airfryer"
        if light and not args.wiz_bash:
            return SYSTEM_PROMPT_WIZ_INTENT_EXPERT, "lights"
        if args.airfryer and args.wiz and any(word in lowered for word in ambiguous_device_words):
            return None, "ambiguous_device"
        if args.airfryer and not args.wiz:
            return SYSTEM_PROMPT_AIRFRYER_INTENT, "airfryer"
        return intent_prompt, "default"

    if args.wiz_bash and not WIZ_CLI.exists():
        sys.exit(f"wiz CLI not found: {WIZ_CLI}")
    startup_timer.mark("prompts_ready", "llm_tool_parser")

    # --- Wake word models ---
    models: list[StreamingModel] = []
    model_tags: list[str] = []
    shadow_models: list[StreamingModel] = []
    shadow_tags: list[str] = []
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
            print(f"  {color}■{RESET} active {tag} ({size_kb}KB) threshold={thresholds[i]}")

        if args.shadow_models:
            shadow_tags = args.shadow_models
            for i, (tag, path) in enumerate(resolve_models(shadow_tags)):
                color = COLORS[(i + len(models)) % len(COLORS)]
                m = StreamingModel(tag, str(path), args.shadow_threshold, color, use_ma=True)
                m.required_consecutive = args.shadow_hold_frames
                m.cooldown_s = args.shadow_cooldown
                shadow_models.append(m)
                size_kb = path.stat().st_size // 1024
                print(f"  {color}◇{RESET} shadow {tag} ({size_kb}KB) threshold={args.shadow_threshold}")

    startup_timer.mark(
        "wake_models_ready",
        f"active={model_tags or ['manual']} shadow={shadow_tags or []}",
    )

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
    airfryer_ha = None

    if args.airfryer:
        print(f"  Starting Airfryer MCP server (HTTP daemon: 127.0.0.1:8767, timeout=30s)")
        # Airfryer `cook` intentionally does wake -> wait -> set -> wait -> start -> wait -> verify.
        # That is ~6s minimum before cloud/MQTT latency, so the generic 8s MCP timeout is too tight.
        airfryer_ha = MCPClient(AIRFRYER_MCP_SERVER, [], timeout_s=30.0)

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

        print(f"  Starting WiZ MCP server...")
        ha = MCPClient(mcp_server, mcp_args)
    elif not args.airfryer:
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
        shadow_models=shadow_tags,
        shadow_threshold=args.shadow_threshold if shadow_tags else None,
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

    # --- Optional English→Estonian response translation ---
    response_translator: EnglishToEstonianTranslator | None = None
    if args.response_mode == "en-mt":
        response_translator = EnglishToEstonianTranslator(
            model_id=args.response_mt_model,
            device=args.response_mt_device,
            compute_type=args.response_mt_compute_type,
        )
        print("  Response mode: LLM English reply → local EN→ET MT → TTS")
        try:
            mt_load_s = response_translator.load()
            print(
                f"  MT: {args.response_mt_model} "
                f"({args.response_mt_device}/{args.response_mt_compute_type}, load={mt_load_s:.2f}s)"
            )
            startup_timer.mark("response_mt_ready", f"load={mt_load_s:.3f}s model={args.response_mt_model}")
        except Exception as exc:
            response_translator = None
            startup_timer.mark("response_mt_failed", str(exc))
            print(f"  MT unavailable, falling back to direct Estonian responses: {exc}")
    else:
        print("  Response mode: direct Estonian from intent/helper/runtime")
        startup_timer.mark("response_mt_skipped")

    # --- LLM warmup ---
    print(f"  Warming up {llm_backend_label()}...")
    startup_timer.mark("llm_warmup_start")
    warmup_prompts: list[tuple[str, str]] = [("default", intent_prompt)]
    if args.pi_conversation:
        print("  Intent mode: persistent Pi conversational agent (cloud, context kept)")
        warmup_prompts = []
    elif args.airfryer and args.wiz and not args.wiz_bash:
        print("  Intent mode: routed LLM tool-call parser (lights + airfryer)")
        warmup_prompts = [
            ("lights", SYSTEM_PROMPT_WIZ_INTENT_EXPERT),
            ("airfryer", SYSTEM_PROMPT_AIRFRYER_INTENT),
        ]
    elif (args.wiz and not args.wiz_bash) or args.airfryer:
        print("  Intent mode: LLM tool-call parser")
    try:
        if args.pi_conversation:
            request_pi_rpc_json(
                SYSTEM_PROMPT_PI_CONVERSATIONAL_ASSISTANT,
                "Soojendus. Vasta ainult: {\"route\":\"chat\",\"actions\":[],\"say\":\"Valmis.\"}",
                timeout_s=max(args.pi_rpc_timeout, 15.0),
                independent=False,
            )
            # Do not let warmup become part of the live household conversation.
            reset_pi_rpc_session(SYSTEM_PROMPT_PI_CONVERSATIONAL_ASSISTANT, timeout_s=5.0)
            startup_timer.mark("llm_warmup_pi_conversation_done")
        for warm_label, warm_prompt in warmup_prompts:
            llm_parse_intent("tere", warm_prompt)
            startup_timer.mark(f"llm_warmup_{warm_label}_done")
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
        if airfryer_ha is not None:
            airfryer_ha.close()
        close_ble_bridge_connection()
        close_pi_rpc_clients()
        if korvo_audio is not None:
            korvo_audio.close()
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

    if not args.pi_conversation and not args.no_helper and args.helper_warmup:
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
        enabled=bool(models) and not args.no_false_trigger_key,
        mute_key=None if args.no_mute_key else args.mute_key.encode("utf-8")[:1],
    )
    false_trigger_key_enabled = false_trigger_override.start()
    session_recorder = DemoAudioRecorder(
        participant_id=args.participant,
        session_id=logger.session_id,
        log_dir=PROJECT_ROOT / "output" / "demo-recordings",
        log_event=logger.log_event,
    )

    print(f"\n{'=' * 60}")
    if models:
        if n_models > 1:
            print(
                f"  Consensus: {min_consensus}/{n_models} within {args.consensus_window_ms}ms"
            )
        print(f'  Listening for "Kuule Kratt"...')
        if shadow_models:
            print(f"  Passive shadow logging: {', '.join(shadow_tags)}")
        if false_trigger_key_enabled:
            print("  Audio recording: press 'r' to start/stop local WAV capture after consent")
            if args.false_positive_audio:
                print(
                    "  False-positive clips: Space saves local wake pre-roll "
                    f"({args.false_positive_preroll_seconds:.1f}s) to output/wake-false-positives/"
                )
            print("  False trigger reset: press Space only if Kratt woke without the wake phrase")
            print("  Missed wake marker: press 'w' right after the participant tried the wake phrase but Kratt did not react")
            if not args.no_mute_key:
                print(f"  Mic mute: press {args.mute_key!r} to toggle wake listening while teaching")
        elif not args.no_false_trigger_key:
            print("  False trigger override / mic mute: unavailable (stdin is not interactive)")
    else:
        print("  Wake word disabled — press Enter to start recording, or q/quit to exit")
    print(f"  Log: {demo_log}")
    print(f"  Press q or Ctrl+C to exit\n")
    startup_timer.mark("ready")

    # --- Audio state ---
    frame_samples = int(SAMPLE_RATE * FRAME_MS / 1000)
    frame_bytes = frame_samples * 2
    audio_buffer = bytearray()
    wake_preroll_buffer = bytearray()
    wake_preroll_max_bytes = max(0, int(args.false_positive_preroll_seconds * SAMPLE_RATE) * 2)
    wake_trigger_clip_bytes = b""

    def wakeword_callback(indata, frames, time_info, status):
        nonlocal audio_buffer, wake_preroll_buffer
        int16 = (indata[:, 0] * 32768).clip(-32768, 32767).astype(np.int16)
        chunk = int16.tobytes()
        audio_buffer.extend(chunk)
        if args.false_positive_audio and wake_preroll_max_bytes > 0:
            wake_preroll_buffer.extend(chunk)
            if len(wake_preroll_buffer) > wake_preroll_max_bytes:
                del wake_preroll_buffer[: len(wake_preroll_buffer) - wake_preroll_max_bytes]
        session_recorder.write_int16_bytes(chunk)

    # Consensus state
    consensus_count = 0
    turn_seq = 0
    last_consensus_time = 0.0
    consensus_cooldown_s = args.post_trigger_cooldown
    recent_detections: dict[str, float] = {}
    shadow_cycle_start_mono = time.monotonic()
    shadow_wake_snapshot: dict[str, Any] = {}
    shadow_stats: dict[str, dict[str, Any]] = {}
    light_state: dict[str, Any] = {"known": False, "on": None, "color": None, "brightness": None}

    def reset_shadow_cycle(*, clear_cooldown: bool = False) -> None:
        nonlocal shadow_cycle_start_mono, shadow_wake_snapshot
        shadow_cycle_start_mono = time.monotonic()
        shadow_wake_snapshot = {}
        shadow_stats.clear()
        for model in shadow_models:
            model.reset(clear_cooldown=clear_cooldown)
            shadow_stats[model.name] = {
                "peak": 0.0,
                "last_score": 0.0,
                "hit": False,
                "first_hit_mono": None,
                "trigger_count": 0,
                "threshold": model.threshold,
            }

    def shadow_snapshot(now: float | None = None) -> dict[str, Any]:
        if not shadow_models:
            return {}
        now = time.monotonic() if now is None else now
        snapshot: dict[str, Any] = {}
        for model in shadow_models:
            stat = shadow_stats.get(model.name, {})
            first_hit = stat.get("first_hit_mono")
            snapshot[model.name] = {
                "peak": round(float(stat.get("peak", 0.0)), 4),
                "last_score": round(float(stat.get("last_score", 0.0)), 4),
                "hit": bool(stat.get("hit", False)),
                "first_hit_age_ms": int((float(first_hit) - now) * 1000) if first_hit is not None else None,
                "trigger_count": int(stat.get("trigger_count", 0)),
                "threshold": stat.get("threshold", model.threshold),
            }
        return snapshot

    def update_shadow_models(features: np.ndarray, now: float) -> None:
        if not shadow_models:
            return
        for model in shadow_models:
            detected_score = model.process_features(features.copy())
            score = sum(model.scores) / len(model.scores) if model.scores else 0.0
            stat = shadow_stats.setdefault(
                model.name,
                {
                    "peak": 0.0,
                    "last_score": 0.0,
                    "hit": False,
                    "first_hit_mono": None,
                    "trigger_count": 0,
                    "threshold": model.threshold,
                },
            )
            stat["last_score"] = float(score)
            if score > float(stat.get("peak", 0.0)):
                stat["peak"] = float(score)
            if score >= model.threshold:
                stat["hit"] = True
                if stat.get("first_hit_mono") is None:
                    stat["first_hit_mono"] = now
            if detected_score is not None:
                stat["trigger_count"] = int(stat.get("trigger_count", 0)) + 1
                logger.log_event(
                    "shadow_wake_trigger",
                    {
                        "model_name": model.name,
                        "score": round(float(detected_score), 4),
                        "threshold": model.threshold,
                        "seconds_since_listen_start": round(now - shadow_cycle_start_mono, 3),
                        "shadow_summary": shadow_snapshot(now),
                    },
                )

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
            offset_days = int(action.get("offset_days", 0) or 0)
            result = weather_response_et(str(action.get("location") or "Tallinn"), mode=mode, offset_days=offset_days)
            persona_mode = "forecast" if offset_days != 0 and mode == "current" else mode
            return soften_weather_response(result, mode=persona_mode, turn_seq=turn_seq), True
        if action_name == "get_capabilities":
            cap_mode = "smarthome" if args.airfryer and args.wiz else "airfryer" if args.airfryer else "lights"
            return capabilities_response(turn_seq, mode=cap_mode), True
        return "", False

    local_runtime_actions = {"get_time", "get_date", "get_weather", "get_capabilities"}
    airfryer_actions = {"cook", "stop", "status"}

    def combined_local_runtime_response(executed: list[dict[str, Any]]) -> str:
        parts: list[str] = []
        for item in executed:
            if item.get("action") not in local_runtime_actions:
                continue
            text = str(item.get("result") or "").strip()
            if text:
                parts.append(text)
        return " ".join(parts)

    def _spoken_target_prefix(entity_id: Any) -> str:
        return "Tuli" if str(entity_id or "").strip() == "all" and len(wiz_bulb_ips) == 1 else "Tuled"

    def _spoken_action_response(action_name: str, action: dict[str, Any]) -> str:
        target = _spoken_target_prefix(action.get("entity_id"))
        if action_name == "turn_on":
            return f"{target} põleb."
        if action_name == "turn_off":
            return f"{target} on kustutatud."
        if action_name == "set_color":
            color = str(action.get("color") or "").strip()
            if color:
                return f"{target} on nüüd {color}."
            if action.get("hex"):
                return f"{target} on nüüd valitud värvi."
            if action.get("rgb"):
                return f"{target} on nüüd valitud värvi."
            return f"{target} värv on muudetud."
        if action_name == "set_brightness":
            return f"{target} heledus on muudetud."
        if action_name == "cook":
            temp = action.get("temperature_c")
            minutes = action.get("time_minutes")
            return f"Panen õhufritüüri tööle {temp} kraadi juures {minutes} minutiks."
        if action_name == "stop":
            return "Peatan õhufritüüri."
        if action_name == "status":
            return "Vaatan õhufritüüri olekut."
        return demo_response_for_action(action_name, action)

    def combined_executed_response(executed: list[dict[str, Any]]) -> str:
        parts: list[str] = []
        local = combined_local_runtime_response(executed)
        if local:
            parts.append(local)
        for item in executed:
            action_name = str(item.get("action") or "")
            if action_name in local_runtime_actions:
                continue
            if action_name == "get_state" and item.get("result"):
                parts.append(str(item.get("result")))
                continue
            if item.get("ok", True):
                parts.append(_spoken_action_response(action_name, item.get("args", {})))
        return " ".join(part.strip() for part in parts if part and part.strip())

    COLOR_ET_TO_EN = {
        "sinine": "blue",
        "punane": "red",
        "roheline": "green",
        "kollane": "yellow",
        "lilla": "purple",
        "roosa": "pink",
        "oranž": "orange",
        "oranz": "orange",
        "soe valge": "warm white",
        "külm valge": "cool white",
        "neutraalne": "neutral white",
        "päevavalgus": "daylight white",
    }

    def _response_target_label(entity_id: Any) -> str:
        entity = str(entity_id or "").strip()
        if entity == "all":
            return "the light" if len(wiz_bulb_ips) == 1 else "all lights"
        if entity.startswith("light.wiz_"):
            suffix = entity.rsplit("_", 1)[-1]
            return f"light {suffix}" if suffix.isdigit() else "the light"
        if entity.startswith("light."):
            return entity.removeprefix("light.").replace("_", " ")
        return entity or "the device"

    def _response_action_summary(executed: list[dict[str, Any]]) -> list[dict[str, Any]]:
        summaries: list[dict[str, Any]] = []
        for item in executed[:4]:
            args_dict = item.get("args") if isinstance(item.get("args"), dict) else {}
            color = args_dict.get("color")
            color_en = COLOR_ET_TO_EN.get(str(color).strip().lower(), color) if color else None
            summary: dict[str, Any] = {
                "action": item.get("action"),
                "target": _response_target_label(args_dict.get("entity_id")),
                "ok": bool(item.get("ok", True)),
            }
            if color_en:
                summary["color"] = color_en
            if args_dict.get("brightness") is not None:
                summary["brightness"] = args_dict.get("brightness")
            if item.get("result"):
                summary["tool_result"] = str(item.get("result"))[:180]
            summaries.append(summary)
        return summaries

    def _response_event(
        *,
        route: str,
        transcript: str,
        executed: list[dict[str, Any]],
        parsed: dict[str, Any],
        llm1_error: str | None,
    ) -> dict[str, Any]:
        if llm1_error or any(item.get("ok") is False for item in executed):
            result = "error"
        elif route == "clarify" and not executed:
            result = "clarify"
        elif executed:
            result = "success"
        else:
            result = "clarify"
        return {
            "result": result,
            "user_et": transcript,
            "route": route,
            "actions": _response_action_summary(executed),
            "parser_response": str(parsed.get("response") or "")[:160],
            "parser_question": str(parsed.get("question") or "")[:160],
            "error": llm1_error,
        }

    def response_via_en_mt(
        event: dict[str, Any],
        turn_timer: StepTimer,
        label: str,
    ) -> tuple[str, str, float, float, str | None]:
        if response_translator is None:
            return "", "", 0.0, 0.0, "translator_unavailable"
        response_options = {
            "temperature": args.response_temperature,
            "num_predict": args.response_num_predict,
        }
        llm_started = time.monotonic()
        turn_timer.mark(f"{label}_en_start")
        raw = llm_generate_json(
            json.dumps(event, ensure_ascii=False),
            SYSTEM_PROMPT_RESPONSE_EN,
            ollama_options=response_options,
        )
        llm_s = time.monotonic() - llm_started
        say_en = str(raw.get("say_en") or raw.get("response") or raw.get("say") or "").strip()
        turn_timer.mark(f"{label}_en_done", f"llm={llm_s:.3f}s say_en={say_en!r}")
        if not say_en:
            return "", say_en, llm_s, 0.0, "empty_english_response"

        mt_result = response_translator.translate(say_en)
        turn_timer.mark(
            f"{label}_mt_done",
            f"mt={mt_result.latency_s:.3f}s ok={mt_result.ok} error={mt_result.error} et={mt_result.text!r}",
        )
        if not mt_result.ok:
            return "", say_en, llm_s, mt_result.latency_s, mt_result.error or "mt_failed"
        return mt_result.text, say_en, llm_s, mt_result.latency_s, None

    def should_generate_en_mt_response(
        *,
        route: str,
        executed: list[dict[str, Any]],
        llm1_error: str | None,
    ) -> bool:
        if args.pi_conversation:
            return False
        if args.response_mode != "en-mt" or response_translator is None:
            return False
        if route == "ask_help":
            return False
        if llm1_error == "invalid_actions":
            return False
        if executed and executed[0].get("action") in local_runtime_actions:
            # Time/date/weather/capability tools already return fact-aware Estonian.
            return False
        return bool(executed)

    def print_operator_help() -> None:
        print(
            "  Operator keys: "
            f"{args.mute_key}=mute wake, r=toggle audio recording, n=next participant, w=mark missed wake, "
            "Space=false-trigger reset after accidental wake, Esc=hard reset/abort, "
            "s=stop TTS, e=stop effect, h=help, q=quit"
        )

    def service_global_key_events() -> None:
        if false_trigger_override.consume_quit():
            raise KeyboardInterrupt
        if false_trigger_override.consume_help():
            print_operator_help()
        if false_trigger_override.consume_recording_toggle():
            if session_recorder.active:
                path = session_recorder.stop(reason="operator_toggle")
                log_line(f"  [REC ○] stopped: {path}")
            else:
                path = session_recorder.start(reason="operator_toggle")
                log_line(f"  [REC ●] recording: {path}")
        if false_trigger_override.consume_participant_boundary():
            was_recording = session_recorder.active
            if was_recording:
                path = session_recorder.stop(reason="participant_boundary")
                log_line(f"  [REC ○] participant segment stopped: {path}")
            segment = logger.mark_participant_boundary(reason="operator_key_n")
            log_line(f"  >>> PARTICIPANT BOUNDARY: next participant segment #{segment} <<<")
            if was_recording:
                path = session_recorder.start(reason="participant_boundary")
                log_line(f"  [REC ●] participant segment recording: {path}")
        if false_trigger_override.consume_stop_effect():
            cancel_running_effect(wait=False)
            print("  Effect stopped by operator.")
        if false_trigger_override.consume_stop_tts():
            tts.stop()
            print("  TTS stopped by operator.")

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
            false_trigger_override.stop_tts_event.clear()
            tts_s = tts.speak(text, stop_event=false_trigger_override.stop_tts_event)
            false_trigger_override.consume_stop_tts()
            service_global_key_events()
            turn_timer.mark(f"{label}_tts_done", f"tts={tts_s:.3f}s")
            print(f"  TTS: {tts_s:.1f}s")
            return tts_s
        except Exception as exc:
            turn_timer.mark(f"{label}_tts_error", str(exc))
            print(f"  TTS error: {exc}")
            return 0.0

    def speak_intermediate_background(text: str, turn_timer: StepTimer, label: str) -> threading.Event | None:
        """Print/speak a short holding notice while a slow cloud LLM request runs."""
        text = (text or "").strip()
        if not text:
            return None
        print(f"\n  KRATT: {BOLD}{text}{RESET}")
        turn_timer.mark(f"{label}_prompted", text)
        if not tts_available:
            turn_timer.mark(f"{label}_tts_skipped", "tts_unavailable")
            return None
        stop_event = threading.Event()

        def _worker() -> None:
            try:
                tts.speak(text, stop_event=stop_event)
            except Exception as exc:
                print(f"  TTS warning error: {exc}")

        threading.Thread(target=_worker, name=f"kratt-{label}-tts", daemon=True).start()
        return stop_event

    def record_followup_text(turn_timer: StepTimer, idx: int) -> tuple[str, float, float, float]:
        print("  Recording follow-up... (answer now, no wake word needed)")
        started = time.monotonic()
        turn_timer.mark(f"followup_{idx}_record_start")
        if args.streaming_stt:
            if korvo_audio is not None:
                audio2, text2, stt2 = record_and_transcribe_streaming_from_source(
                    korvo_audio,
                    stt,
                    max_seconds=args.followup_max_seconds,
                    silence_threshold=args.vad_silence_threshold,
                    silence_duration=args.utterance_silence_duration,
                    initial_silence_timeout=args.followup_initial_silence_timeout,
                    speech_start_grace=args.speech_start_grace,
                    cancel_event=false_trigger_override.cancel_event
                    if false_trigger_key_enabled
                    else None,
                    use_stt_endpoint=False,
                )
            else:
                audio2, text2, stt2 = record_and_transcribe_streaming(
                    stt,
                    max_seconds=args.followup_max_seconds,
                    silence_threshold=args.vad_silence_threshold,
                    silence_duration=args.utterance_silence_duration,
                    initial_silence_timeout=args.followup_initial_silence_timeout,
                    speech_start_grace=args.speech_start_grace,
                    cancel_event=false_trigger_override.cancel_event
                    if false_trigger_key_enabled
                    else None,
                    use_stt_endpoint=False,
                )
        else:
            if korvo_audio is not None:
                audio2 = record_until_silence_from_source(
                    korvo_audio,
                    max_seconds=args.followup_max_seconds,
                    silence_threshold=args.vad_silence_threshold,
                    silence_duration=args.utterance_silence_duration,
                    initial_silence_timeout=args.followup_initial_silence_timeout,
                    speech_start_grace=args.speech_start_grace,
                    cancel_event=false_trigger_override.cancel_event
                    if false_trigger_key_enabled
                    else None,
                )
            else:
                audio2 = record_until_silence(
                    max_seconds=args.followup_max_seconds,
                    silence_threshold=args.vad_silence_threshold,
                    silence_duration=args.utterance_silence_duration,
                    initial_silence_timeout=args.followup_initial_silence_timeout,
                    speech_start_grace=args.speech_start_grace,
                    cancel_event=false_trigger_override.cancel_event
                    if false_trigger_key_enabled
                    else None,
                )
            t_decode = time.monotonic()
            text2 = stt.transcribe(audio2) if len(audio2) else ""
            stt2 = time.monotonic() - t_decode
        rec2 = time.monotonic() - started
        audio_s = float(len(audio2)) / SAMPLE_RATE if audio2 is not None else 0.0
        session_recorder.write_float_audio(audio2)
        service_global_key_events()
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
        if shadow_models:
            reset_shadow_cycle(clear_cooldown=clear_wake_cooldowns)
        if clear_wake_cooldowns:
            last_consensus_time = 0.0
        if cooldown and models and args.post_trigger_cooldown > 0:
            print(f"  Cooldown {args.post_trigger_cooldown:.1f}s before listening again...")
            cooldown_until = time.monotonic() + args.post_trigger_cooldown
            while time.monotonic() < cooldown_until:
                service_global_key_events()
                time.sleep(min(0.05, max(0.0, cooldown_until - time.monotonic())))
        if models:
            if false_trigger_override.is_muted():
                print(f'  Listening paused (mic muted). Press {args.mute_key!r} to resume.\n')
            else:
                print(f'  Listening for "Kuule Kratt"...\n')

    def _write_int16_wav(path: Path, pcm_bytes: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(SAMPLE_RATE)
            wav.writeframes(pcm_bytes)

    def save_false_positive_clip(
        *,
        turn_timer: StepTimer,
        wake_prob: float | None,
        wake_models_agreed: list[str],
        audio: np.ndarray | None,
        transcript: str | None,
    ) -> dict[str, Any] | None:
        if not args.false_positive_audio or not wake_trigger_clip_bytes:
            return None
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        safe_participant = re.sub(r"[^A-Za-z0-9_.-]+", "_", args.participant)[:60] or "participant"
        out_dir = PROJECT_ROOT / "output" / "wake-false-positives" / safe_participant
        base = f"{safe_participant}_{stamp}_{logger.session_id}_turn{turn_seq:03d}_fp"
        wake_path = out_dir / f"{base}_wake_preroll.wav"
        meta_path = out_dir / f"{base}.json"
        _write_int16_wav(wake_path, wake_trigger_clip_bytes)

        post_wake_path = None
        post_audio_duration_s = 0.0
        if audio is not None and len(audio):
            post_audio_duration_s = float(len(audio)) / SAMPLE_RATE
            post_pcm = (np.asarray(audio, dtype=np.float32).reshape(-1) * 32768.0).clip(-32768, 32767).astype(np.int16)
            post_wake_path = out_dir / f"{base}_post_wake.wav"
            _write_int16_wav(post_wake_path, post_pcm.tobytes())

        info: dict[str, Any] = {
            "label": "false_positive",
            "source": "operator_space",
            "participant_id": args.participant,
            "session_id": logger.session_id,
            "turn_seq": turn_seq,
            "timestamp": datetime.now().astimezone().isoformat(timespec="milliseconds"),
            "sample_rate": SAMPLE_RATE,
            "wake_preroll_path": str(wake_path),
            "wake_preroll_duration_s": round(len(wake_trigger_clip_bytes) / 2 / SAMPLE_RATE, 3),
            "post_wake_path": str(post_wake_path) if post_wake_path else None,
            "post_wake_duration_s": round(post_audio_duration_s, 3),
            "transcript": transcript,
            "wake_word_prob": wake_prob,
            "wake_models": wake_models_agreed,
            "shadow_wake": shadow_wake_snapshot or None,
            "note": "Wake preroll is the training-relevant false-positive clip; post_wake is optional context after activation.",
        }
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        meta_path.write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        info["metadata_path"] = str(meta_path)
        logger.log_event("false_positive_clip_saved", info)
        turn_timer.mark("false_positive_clip_saved", str(wake_path))
        log_line(f"  Saved false-positive wake clip: {wake_path}")
        return info

    def handle_false_trigger_override(
        turn_timer: StepTimer,
        wake_prob: float | None,
        wake_models_agreed: list[str],
        audio: np.ndarray,
        t_rec: float,
        t_stt: float = 0.0,
        transcript: str | None = None,
    ) -> None:
        audio_duration_s = round(float(len(audio)) / SAMPLE_RATE, 3) if audio is not None else 0.0
        clip_info = save_false_positive_clip(
            turn_timer=turn_timer,
            wake_prob=wake_prob,
            wake_models_agreed=wake_models_agreed,
            audio=audio,
            transcript=transcript,
        )
        turn_timer.mark(
            "false_trigger_manual_override",
            f"audio={audio_duration_s:.3f}s rec={t_rec:.3f}s clip={bool(clip_info)}",
        )
        log_line(f"  {BOLD}>>> MANUAL OVERRIDE: false trigger reset <<<{RESET}")
        logger.log_interaction(
            {
                "outcome": "false_trigger_manual_override",
                "manual_override_key": "space",
                "wake_word_prob": wake_prob,
                "wake_models": wake_models_agreed,
                "shadow_wake": shadow_wake_snapshot or None,
                "false_positive_clip": clip_info,
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
                wake_preroll_buffer = bytearray()
                wake_trigger_clip_bytes = b""
                detected = False
                frontend = MicroFrontend()
                process_fn = getattr(frontend, "process_samples", None) or getattr(
                    frontend, "ProcessSamples", None
                )

                # Reset all models for fresh detection cycle
                for m in models:
                    m.reset()
                reset_shadow_cycle()
                recent_detections.clear()

                if korvo_audio is not None:
                    korvo_audio.clear()
                    wake_stream_context = contextlib.nullcontext(None)
                else:
                    wake_stream_context = sd.InputStream(
                        samplerate=SAMPLE_RATE,
                        channels=1,
                        dtype="float32",
                        blocksize=frame_samples,
                        callback=wakeword_callback,
                    )

                with wake_stream_context as wake_stream:
                    while not detected:
                        if korvo_audio is not None:
                            serial_chunk = korvo_audio.read_pcm_bytes(timeout=0.05)
                            if serial_chunk:
                                audio_buffer.extend(serial_chunk)
                                if args.false_positive_audio and wake_preroll_max_bytes > 0:
                                    wake_preroll_buffer.extend(serial_chunk)
                                    if len(wake_preroll_buffer) > wake_preroll_max_bytes:
                                        del wake_preroll_buffer[: len(wake_preroll_buffer) - wake_preroll_max_bytes]
                                session_recorder.write_int16_bytes(serial_chunk)

                        service_global_key_events()
                        if false_trigger_override.clear_abort():
                            audio_buffer = bytearray()
                            recent_detections.clear()
                            for m in models:
                                m.reset(hard=True, clear_cooldown=True)
                            reset_shadow_cycle(clear_cooldown=True)
                            print("  Abort/reset by operator. Listening continues.")
                            continue
                        if false_trigger_override.consume_missed_wake():
                            now = time.monotonic()
                            miss_shadow = shadow_snapshot(now)
                            logger.log_event(
                                "operator_missed_wake",
                                {
                                    "seconds_since_listen_start": round(now - shadow_cycle_start_mono, 3),
                                    "shadow_summary": miss_shadow,
                                },
                            )
                            log_line(f"  {YELLOW}>>> OPERATOR MARK: missed wake <<<{RESET}")
                            audio_buffer = bytearray()
                            recent_detections.clear()
                            for m in models:
                                m.reset(hard=True, clear_cooldown=True)
                            reset_shadow_cycle(clear_cooldown=True)
                            continue
                        if false_trigger_override.is_muted():
                            if false_trigger_override.clear_mute_changed():
                                audio_buffer = bytearray()
                                recent_detections.clear()
                                for m in models:
                                    m.reset(hard=True, clear_cooldown=True)
                                reset_shadow_cycle(clear_cooldown=True)
                                print(f"  Mic muted — wake listening paused. Press {args.mute_key!r} to resume.")
                            time.sleep(0.05)
                            continue
                        elif false_trigger_override.clear_mute_changed():
                            audio_buffer = bytearray()
                            recent_detections.clear()
                            for m in models:
                                m.reset(hard=True, clear_cooldown=True)
                            reset_shadow_cycle(clear_cooldown=True)
                            print(f'  Mic unmuted — listening for "Kuule Kratt"...')

                        while len(audio_buffer) >= frame_bytes:
                            chunk = bytes(audio_buffer[:frame_bytes])
                            del audio_buffer[:frame_bytes]

                            result = process_fn(chunk)
                            if not result.features:
                                continue

                            features = np.array(result.features, dtype=np.float32)
                            now = time.monotonic()

                            # Feed same features to active and passive shadow models.
                            update_shadow_models(features, now)
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
                                    shadow_wake_snapshot = shadow_snapshot(now)
                                    wake_trigger_clip_bytes = bytes(wake_preroll_buffer)
                                    logger.log_event(
                                        "active_wake_trigger",
                                        {
                                            "wake_word_prob": round(float(wake_prob), 4),
                                            "wake_models": wake_models_agreed,
                                            "shadow_summary": shadow_wake_snapshot,
                                        },
                                    )

                                    log_line(
                                        f"\n  {BOLD}>>> CONSENSUS {len(agreeing)}/{n_models}: "
                                        f"KUULE KRATT! (#{consensus_count}) [{models_str}] <<<{RESET}"
                                    )
                                    play_wake_beep(enabled=not args.no_wake_beep)

                                    detected = True
                                    recent_detections.clear()
                                    try:
                                        # Avoid occasional PortAudio close/open deadlock
                                        # when switching from wake listening to command
                                        # recording immediately after a trigger.
                                        wake_stream.abort(ignore_errors=True)
                                    except Exception:
                                        pass
                                    break

                        time.sleep(0.005)
            else:
                manual_command = input("\nPress Enter to start recording, or q/quit to exit... ").strip().lower()
                if manual_command in {"q", "quit", "exit"}:
                    raise KeyboardInterrupt

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
                print("  False trigger? Press Space to reset. Esc aborts turn.")

            t0 = time.monotonic()
            if args.streaming_stt:
                turn_timer.mark("record_streaming_stt_start")
                print("  Recording + streaming STT... (speak now, stops on silence)")
                if korvo_audio is not None:
                    audio, transcript, t_stt = record_and_transcribe_streaming_from_source(
                        korvo_audio,
                        stt,
                        max_seconds=args.utterance_max_seconds,
                        silence_threshold=args.vad_silence_threshold,
                        silence_duration=args.utterance_silence_duration,
                        initial_silence_timeout=args.initial_silence_timeout,
                        speech_start_grace=args.speech_start_grace,
                        cancel_event=false_trigger_override.cancel_event
                        if false_trigger_key_enabled
                        else None,
                        use_stt_endpoint=False,
                    )
                else:
                    audio, transcript, t_stt = record_and_transcribe_streaming(
                        stt,
                        max_seconds=args.utterance_max_seconds,
                        silence_threshold=args.vad_silence_threshold,
                        silence_duration=args.utterance_silence_duration,
                        initial_silence_timeout=args.initial_silence_timeout,
                        speech_start_grace=args.speech_start_grace,
                        cancel_event=false_trigger_override.cancel_event
                        if false_trigger_key_enabled
                        else None,
                        use_stt_endpoint=False,
                    )
                t_rec = time.monotonic() - t0
                session_recorder.write_float_audio(audio)
                service_global_key_events()
                turn_timer.mark("record_streaming_stt_done", f"rec={t_rec:.3f}s decode={t_stt:.3f}s")
                if false_trigger_override.clear_abort():
                    turn_timer.mark("operator_abort_turn")
                    logger.log_event(
                        "operator_abort_turn",
                        {
                            "wake_word_prob": wake_prob,
                            "wake_models": wake_models_agreed,
                            "shadow_wake": shadow_wake_snapshot or None,
                            "audio_duration_s": round(float(len(audio)) / SAMPLE_RATE, 3),
                            "rec_duration_s": round(t_rec, 3),
                            "stt_latency_ms": int(t_stt * 1000),
                        },
                    )
                    prepare_next_listen(
                        cooldown=False,
                        hard_reset_wake=True,
                        clear_wake_cooldowns=True,
                    )
                    continue
                if false_trigger_override.consume():
                    handle_false_trigger_override(
                        turn_timer,
                        wake_prob,
                        wake_models_agreed,
                        audio,
                        t_rec,
                        t_stt,
                        transcript,
                    )
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
                if korvo_audio is not None:
                    audio = record_until_silence_from_source(
                        korvo_audio,
                        max_seconds=args.utterance_max_seconds,
                        silence_threshold=args.vad_silence_threshold,
                        silence_duration=args.utterance_silence_duration,
                        initial_silence_timeout=args.initial_silence_timeout,
                        speech_start_grace=args.speech_start_grace,
                        cancel_event=false_trigger_override.cancel_event
                        if false_trigger_key_enabled
                        else None,
                    )
                else:
                    audio = record_until_silence(
                        max_seconds=args.utterance_max_seconds,
                        silence_threshold=args.vad_silence_threshold,
                        silence_duration=args.utterance_silence_duration,
                        initial_silence_timeout=args.initial_silence_timeout,
                        speech_start_grace=args.speech_start_grace,
                        cancel_event=false_trigger_override.cancel_event
                        if false_trigger_key_enabled
                        else None,
                    )
                t_rec = time.monotonic() - t0
                session_recorder.write_float_audio(audio)
                service_global_key_events()
                turn_timer.mark("record_done", f"rec={t_rec:.3f}s audio={float(len(audio)) / SAMPLE_RATE:.3f}s")
                if false_trigger_override.clear_abort():
                    turn_timer.mark("operator_abort_turn")
                    logger.log_event(
                        "operator_abort_turn",
                        {
                            "wake_word_prob": wake_prob,
                            "wake_models": wake_models_agreed,
                            "shadow_wake": shadow_wake_snapshot or None,
                            "audio_duration_s": round(float(len(audio)) / SAMPLE_RATE, 3),
                            "rec_duration_s": round(t_rec, 3),
                            "stt_latency_ms": 0,
                        },
                    )
                    prepare_next_listen(
                        cooldown=False,
                        hard_reset_wake=True,
                        clear_wake_cooldowns=True,
                    )
                    continue
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
                        "shadow_wake": shadow_wake_snapshot or None,
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
                        "shadow_wake": shadow_wake_snapshot or None,
                        "audio_duration_s": round(float(len(audio)) / SAMPLE_RATE, 3),
                        "stt_latency_ms": int(t_stt * 1000),
                        "timing": turn_timer.as_dict(),
                    }
                )
                prepare_next_listen()
                continue

            # --- LLM / execute ---
            intent_transcript = normalize_stt_artifacts(transcript)
            if intent_transcript != transcript:
                print(f'  STT artifact normalized for intent: "{transcript}" -> "{intent_transcript}"')
                turn_timer.mark(
                    "stt_artifact_normalized",
                    f"original={transcript!r} normalized={intent_transcript!r}",
                )

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
            response_en = ""
            response_source = "direct"
            response_mt_error = None
            response_gen_s = 0.0
            response_mt_s = 0.0
            parsed = {}

            if args.wiz_bash:
                print("  Planning WiZ bash command...")
                turn_timer.mark("llm_plan_start", "wiz_bash")
                try:
                    command, cli_result, response, ok = execute_wiz_bash_mode(intent_transcript)
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
                intent_domain = "pi_conversation"
                selected_prompt = None
                if not args.pi_conversation:
                    selected_prompt, intent_domain = select_intent_prompt_for_turn(intent_transcript)
                turn_timer.mark("llm_intent_start", f"{llm_backend_label()} domain={intent_domain}")
                action_errors: list[str] = []
                try:
                    if args.pi_conversation:
                        parsed = request_pi_rpc_json(
                            SYSTEM_PROMPT_PI_CONVERSATIONAL_ASSISTANT,
                            intent_transcript,
                            timeout_s=args.pi_rpc_timeout,
                            independent=False,
                            cancel_event=[
                                false_trigger_override.cancel_event,
                                false_trigger_override.abort_event,
                                false_trigger_override.quit_event,
                            ] if false_trigger_key_enabled else None,
                        )
                        if not str(parsed.get("response") or "").strip() and parsed.get("say"):
                            parsed["response"] = str(parsed.get("say") or "").strip()
                        default_entity_id = "all" if args.wiz else None
                        actions, action_errors = normalize_intent_actions(
                            parsed.get("actions", []),
                            default_entity_id=default_entity_id,
                        )
                        if action_errors and not actions:
                            llm1_error = "invalid_actions"
                    elif selected_prompt is None:
                        parsed = {
                            "route": "clarify",
                            "actions": [],
                            "response": "Kas mõtled tuld või õhufritüüri?",
                        }
                        actions = []
                    else:
                        parsed = llm_parse_intent(intent_transcript, selected_prompt)
                        default_entity_id = "all" if args.wiz else None
                        actions, action_errors = normalize_intent_actions(
                            parsed.get("actions", []),
                            default_entity_id=default_entity_id,
                        )
                        if action_errors and not actions:
                            llm1_error = "invalid_actions"
                except InterruptedError as e:
                    if false_trigger_override.consume_quit():
                        raise KeyboardInterrupt
                    false_trigger_override.clear_abort()
                    false_trigger_override.consume()
                    parsed = {}
                    actions = []
                    turn_timer.mark("operator_abort_turn", f"pi_rpc_interrupted: {e}")
                    logger.log_event(
                        "operator_abort_turn",
                        {
                            "reason": "pi_rpc_interrupted",
                            "wake_word_prob": wake_prob,
                            "wake_models": wake_models_agreed,
                            "shadow_wake": shadow_wake_snapshot or None,
                            "audio_duration_s": round(float(len(audio)) / SAMPLE_RATE, 3),
                            "transcript": transcript,
                        },
                    )
                    print("  Pi RPC interrupted by operator; returning to wake listening.")
                    prepare_next_listen(
                        cooldown=False,
                        hard_reset_wake=True,
                        clear_wake_cooldowns=True,
                    )
                    continue
                except Exception as e:
                    parsed = {}
                    actions = []
                    llm1_error = str(e)
                t_llm1 = time.monotonic() - t2
                turn_timer.mark("llm_intent_done", f"llm={t_llm1:.3f}s domain={intent_domain} actions={len(actions)} error={llm1_error}")
                print(f"  LLM ({t_llm1:.1f}s, {intent_domain}): {json.dumps(actions, ensure_ascii=False)}")
                for err in action_errors:
                    print(f"  Skipping invalid action: {err}")
                    turn_timer.mark("action_validation_error", err)
                if llm1_error:
                    print(f"  LLM error: {llm1_error}")

                route = str(parsed.get("route") or "").strip().lower()
                if args.pi_conversation and route == "ask_help":
                    # In conversational cloud-agent mode, general questions are answered directly,
                    # not delegated to the old helper fallback.
                    route = "chat"
                if route not in {"execute", "clarify", "ask_help", "chat"}:
                    if actions:
                        route = "execute"
                    elif args.pi_conversation and str(parsed.get("response") or "").strip():
                        route = "chat"
                    else:
                        route = "clarify"
                turn_timer.mark("route_selected", route)
                print(f"  Route: {route}")

                if route == "ask_help" and args.no_helper and not llm1_error:
                    parsed["response"] = "See vajab abimudelit, aga abimudel on praegu välja lülitatud."
                    actions = []
                elif route == "ask_help" and not llm1_error:
                    holding = holding_phrase(intent_transcript)
                    helper_question = str(parsed.get("question") or intent_transcript).strip()
                    if helper_warmup_state.get("error"):
                        print(f"  Helper warmup had failed, retrying fresh RPC: {helper_warmup_state['error']}")
                    elif helper_warmup_state.get("started") and not helper_warmup_state.get("ready"):
                        print("  Helper still warming; live request will wait/reuse RPC...")
                    intermediate_tts_s += speak_intermediate(holding, turn_timer, "helper_holding")
                    print("  Asking helper model...")
                    helper_started = time.monotonic()
                    helper_response, helper_tts, helper_turns, helper_error = ask_helper_with_followups(
                        original_transcript=intent_transcript,
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
                    if args.response_mode == "en-mt" and response_translator is not None:
                        try:
                            clarification_et, clarification_en, gen_s, mt_s, mt_error = response_via_en_mt(
                                _response_event(
                                    route="clarify",
                                    transcript=intent_transcript,
                                    executed=[],
                                    parsed=parsed,
                                    llm1_error=None,
                                ),
                                turn_timer,
                                "clarify_response",
                            )
                            if clarification_et:
                                clarification = clarification_et
                                print(
                                    f"  Response EN→ET clarify: {clarification_en!r} -> {clarification!r} "
                                    f"({gen_s + mt_s:.2f}s)"
                                )
                            elif mt_error:
                                print(f"  Response EN→ET clarify failed: {mt_error}")
                        except Exception as exc:
                            turn_timer.mark("clarify_response_en_mt_error", str(exc))
                            print(f"  Response EN→ET clarify error: {exc}")
                    elif "värv" in clarification.lower() or "värvi" in intent_transcript.lower():
                        clarification = color_clarification(intent_transcript)
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
                            reparse_text = f"Algne käsk: {intent_transcript}\nKasutaja täpsustus: {follow_text}"
                            reparse_prompt, reparse_domain = select_intent_prompt_for_turn(reparse_text)
                            turn_timer.mark("clarify_reparse_start", f"domain={reparse_domain}")
                            if reparse_prompt is None:
                                reparsed = {
                                    "route": "clarify",
                                    "actions": [],
                                    "response": "Kas mõtled tuld või õhufritüüri?",
                                }
                            else:
                                reparsed = llm_parse_intent(reparse_text, reparse_prompt)
                            reparsed_actions, reparse_errors = normalize_intent_actions(
                                reparsed.get("actions", []),
                                default_entity_id="all" if args.wiz else None,
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
                        elif action_name in airfryer_actions:
                            ok = True
                            if airfryer_ha is None:
                                result = "Airfryer backend is not enabled."
                                ok = False
                            else:
                                try:
                                    result = airfryer_ha.execute(action_name, action_copy)
                                except (RuntimeError, TimeoutError) as e:
                                    result = f"MCP error: {e}"
                                    ok = False
                            if not ok and llm1_error is None:
                                llm1_error = "airfryer_command_failed"
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
                        elif action_name in airfryer_actions:
                            ok = True
                            if airfryer_ha is None:
                                result = "Airfryer backend is not enabled."
                                ok = False
                            else:
                                try:
                                    result = airfryer_ha.execute(action_name, action_copy)
                                except (RuntimeError, TimeoutError) as e:
                                    result = f"MCP error: {e}"
                                    ok = False
                            if not ok and llm1_error is None:
                                llm1_error = "airfryer_command_failed"
                        else:
                            ok = True
                            if ha is None:
                                result = "Light backend is not enabled."
                                ok = False
                            else:
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
                if llm1_error in {"ble_bridge_command_failed", "mcp_command_failed", "airfryer_command_failed", "invalid_actions"}:
                    response = "Vabandust, käsku ei saanud täita."
                elif executed_actions and executed_actions[0].get("action") == "get_state":
                    if executed_actions[0].get("result"):
                        response = str(executed_actions[0].get("result"))
                        print("  Response: tool state")
                    else:
                        response = cached_light_state_response()
                        print("  Response: cached state")
                elif (
                    args.pi_conversation
                    and planned_response
                    and executed_actions
                    and executed_actions[0].get("action") == "get_capabilities"
                ):
                    response = planned_response
                    print("  Response: planned capabilities")
                elif executed_actions and any(item.get("action") in local_runtime_actions for item in executed_actions):
                    response = combined_executed_response(executed_actions) or planned_response or "Vaatan."
                    print("  Response: combined executed")
                elif executed_actions and executed_actions[0].get("action") == "status":
                    response = str(executed_actions[0].get("result") or planned_response or "Vaatan õhufritüüri olekut.").strip()
                    print("  Response: airfryer status")
                elif planned_response and (
                    args.pi_conversation
                    or not (
                        executed_actions
                        and len(wiz_bulb_ips) == 1
                        and str(executed_actions[0].get("args", {}).get("entity_id")) == "all"
                    )
                ):
                    response = planned_response
                    print("  Response: planned")
                elif executed_actions:
                    first = executed_actions[0]
                    response = _spoken_action_response(first.get("action", ""), first.get("args", {}))
                    print("  Response: template")
                elif not actions:
                    response = "Ma ei saanud käsku täita."
                else:
                    response = "Tehtud."

                if should_generate_en_mt_response(route=route, executed=executed_actions, llm1_error=llm1_error):
                    try:
                        response_event = _response_event(
                            route=route,
                            transcript=intent_transcript,
                            executed=executed_actions,
                            parsed=parsed,
                            llm1_error=llm1_error,
                        )
                        translated_response, response_en, response_gen_s, response_mt_s, response_mt_error = response_via_en_mt(
                            response_event,
                            turn_timer,
                            "response",
                        )
                        if translated_response:
                            response = translated_response
                            response_source = "en_mt"
                            print(
                                f"  Response EN→ET: {response_en!r} -> {response!r} "
                                f"({response_gen_s + response_mt_s:.2f}s)"
                            )
                        else:
                            response_source = "direct_fallback_after_en_mt"
                            print(f"  Response EN→ET failed, using direct fallback: {response_mt_error}")
                    except Exception as exc:
                        response_source = "direct_fallback_after_en_mt_error"
                        response_mt_error = str(exc)
                        turn_timer.mark("response_en_mt_error", str(exc))
                        print(f"  Response EN→ET error, using direct fallback: {exc}")

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
                    false_trigger_override.stop_tts_event.clear()
                    final_tts_s = tts.speak(response, stop_event=false_trigger_override.stop_tts_event)
                    t_tts += final_tts_s
                    false_trigger_override.consume_stop_tts()
                    service_global_key_events()
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
                    "shadow_wake": shadow_wake_snapshot or None,
                    "audio_duration_s": round(float(len(audio)) / SAMPLE_RATE, 3),
                    "rec_duration_s": round(t_rec, 3),
                    "stt_latency_ms": int(t_stt * 1000),
                    "stt_transcript": transcript,
                    "intent_transcript": intent_transcript,
                    "llm1_latency_ms": int(t_llm1 * 1000),
                    "llm1_error": llm1_error,
                    "intent_actions": executed_actions,
                    "llm2_latency_ms": int(t_llm2 * 1000),
                    "llm2_error": llm2_error,
                    "response": response,
                    "response_source": response_source,
                    "response_en": response_en,
                    "response_mt_error": response_mt_error,
                    "response_gen_latency_ms": int(response_gen_s * 1000),
                    "response_mt_latency_ms": int(response_mt_s * 1000),
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
        if session_recorder.active:
            session_recorder.stop(reason="shutdown")
        false_trigger_override.stop()
        demo_log_fh.close()
        logger.close()
        if ha is not None:
            ha.close()
        if airfryer_ha is not None:
            airfryer_ha.close()
        close_ble_bridge_connection()
        close_pi_rpc_clients()
        if korvo_audio is not None:
            korvo_audio.close()


def _argv_has_option(argv: list[str], *options: str) -> bool:
    return any(arg == opt or arg.startswith(opt + "=") for arg in argv for opt in options)


def _mark_explicit_args(args: argparse.Namespace, argv: list[str]) -> None:
    args._explicit = {
        "profile": _argv_has_option(argv, "--profile"),
        "models": _argv_has_option(argv, "--models"),
        "threshold": _argv_has_option(argv, "--threshold"),
        "shadow_models": _argv_has_option(argv, "--shadow-models"),
        "shadow_threshold": _argv_has_option(argv, "--shadow-threshold"),
        "shadow_hold_frames": _argv_has_option(argv, "--shadow-hold-frames"),
        "shadow_cooldown": _argv_has_option(argv, "--shadow-cooldown"),
        "consensus": _argv_has_option(argv, "--consensus"),
        "consensus_window_ms": _argv_has_option(argv, "--consensus-window-ms"),
        "wake_hold_frames": _argv_has_option(argv, "--wake-hold-frames"),
        "wake_model_cooldown": _argv_has_option(argv, "--wake-model-cooldown"),
        "post_trigger_cooldown": _argv_has_option(argv, "--post-trigger-cooldown"),
        "initial_silence_timeout": _argv_has_option(argv, "--initial-silence-timeout"),
        "speech_start_grace": _argv_has_option(argv, "--speech-start-grace"),
        "utterance_max_seconds": _argv_has_option(argv, "--utterance-max-seconds"),
        "utterance_silence_duration": _argv_has_option(argv, "--utterance-silence-duration"),
        "vad_silence_threshold": _argv_has_option(argv, "--vad-silence-threshold"),
        "mute_key": _argv_has_option(argv, "--mute-key"),
        "no_mute_key": _argv_has_option(argv, "--no-mute-key"),
        "no_wake_beep": _argv_has_option(argv, "--no-wake-beep"),
        "false_positive_audio": _argv_has_option(argv, "--false-positive-audio", "--no-false-positive-audio"),
        "false_positive_preroll_seconds": _argv_has_option(argv, "--false-positive-preroll-seconds"),
        "streaming_stt": _argv_has_option(argv, "--streaming-stt", "--no-streaming-stt"),
        "audio_source": _argv_has_option(argv, "--audio-source"),
        "serial_port": _argv_has_option(argv, "--serial-port"),
        "serial_baud": _argv_has_option(argv, "--serial-baud"),
        "serial_start_timeout": _argv_has_option(argv, "--serial-start-timeout"),
        "serial_gain": _argv_has_option(argv, "--serial-gain"),
        "serial_channel": _argv_has_option(argv, "--serial-channel"),
        "wiz": _argv_has_option(argv, "--wiz", "--no-wiz"),
        "wiz_bash": _argv_has_option(argv, "--wiz-bash"),
        "ble_bridge": _argv_has_option(argv, "--ble-bridge"),
        "airfryer": _argv_has_option(argv, "--airfryer"),
        "bulbs": _argv_has_option(argv, "--bulbs"),
        "llm": _argv_has_option(argv, "--llm"),
        "pi_cli": _argv_has_option(argv, "--pi-cli", "--pi-gpt"),
        "pi_conversation": _argv_has_option(argv, "--pi-conversation", "--cloud-agent", "--smart-kratt"),
        "pi_model": _argv_has_option(argv, "--pi-model"),
        "pi_thinking": _argv_has_option(argv, "--pi-thinking"),
        "pi_reset_each_turn": _argv_has_option(argv, "--pi-reset-each-turn"),
        "pi_rpc_timeout": _argv_has_option(argv, "--pi-rpc-timeout"),
        "pi_tools": _argv_has_option(argv, "--pi-tools"),
        "no_pi_tools": _argv_has_option(argv, "--no-pi-tools"),
        "no_helper": _argv_has_option(argv, "--no-helper"),
        "helper_warmup": _argv_has_option(argv, "--helper-warmup", "--no-helper-warmup"),
        "helper_timeout": _argv_has_option(argv, "--helper-timeout"),
        "helper_warmup_timeout": _argv_has_option(argv, "--helper-warmup-timeout"),
        "helper_max_turns": _argv_has_option(argv, "--helper-max-turns"),
        "response_mode": _argv_has_option(argv, "--response-mode", "--translate-responses"),
        "response_mt_model": _argv_has_option(argv, "--response-mt-model"),
        "response_mt_device": _argv_has_option(argv, "--response-mt-device"),
        "response_mt_compute_type": _argv_has_option(argv, "--response-mt-compute-type"),
        "response_temperature": _argv_has_option(argv, "--response-temperature"),
        "response_num_predict": _argv_has_option(argv, "--response-num-predict"),
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
    if args.airfryer and args.wiz_bash:
        parser.error("--airfryer cannot be combined with --wiz-bash; use the normal LLM tool parser")
    if (args.pi_cli or args.pi_conversation) and args.claude_code:
        parser.error("--pi-cli/--pi-conversation and --claude-code are mutually exclusive")
    if (args.ble_bridge or args.wiz_bash) and args.wiz is False:
        parser.error("--ble-bridge/--wiz-bash require WiZ; remove --no-wiz")
    if _explicit(args, "bulbs") and args.wiz is False:
        parser.error("--bulbs requires WiZ; remove --no-wiz or omit --bulbs")

    if any(threshold < 0.0 or threshold > 1.0 for threshold in args.threshold):
        parser.error("--threshold values must be between 0.0 and 1.0")
    if args.shadow_threshold < 0.0 or args.shadow_threshold > 1.0:
        parser.error("--shadow-threshold must be between 0.0 and 1.0")
    if args.shadow_models and args.no_wakeword:
        parser.error("--shadow-models require wake-word detection; remove --no-wakeword")
    if args.shadow_hold_frames < 1:
        parser.error("--shadow-hold-frames must be at least 1")
    if args.shadow_cooldown < 0:
        parser.error("--shadow-cooldown must be non-negative")
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
    if args.speech_start_grace < 0:
        parser.error("--speech-start-grace must be non-negative")
    if args.utterance_max_seconds <= 0:
        parser.error("--utterance-max-seconds must be positive")
    if args.utterance_silence_duration <= 0:
        parser.error("--utterance-silence-duration must be positive")
    if args.vad_silence_threshold < 0:
        parser.error("--vad-silence-threshold must be non-negative")
    if args.audio_source == "korvo-serial":
        if args.serial_baud <= 0:
            parser.error("--serial-baud must be positive")
        if args.serial_start_timeout <= 0:
            parser.error("--serial-start-timeout must be positive")
        if args.serial_gain <= 0 or args.serial_gain > 32:
            parser.error("--serial-gain must be in (0, 32]")
    elif (
        _explicit(args, "serial_port")
        or _explicit(args, "serial_baud")
        or _explicit(args, "serial_start_timeout")
        or _explicit(args, "serial_gain")
        or _explicit(args, "serial_channel")
    ):
        parser.error("--serial-* options require --audio-source korvo-serial")
    if args.false_positive_preroll_seconds <= 0:
        parser.error("--false-positive-preroll-seconds must be positive")
    if args.mute_key and len(args.mute_key.encode("utf-8")) != 1:
        parser.error("--mute-key must be a single-byte terminal key, e.g. m")
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
    if args.response_temperature < 0 or args.response_temperature > 2:
        parser.error("--response-temperature must be between 0 and 2")
    if args.response_num_predict < 8:
        parser.error("--response-num-predict must be at least 8")
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
        help="One threshold for all active models, or one per active model. Default: 0.996.",
    )
    parser.add_argument(
        "--shadow-models",
        nargs="+",
        default=None,
        help=(
            "Passive model tags to score/log on the same microphone stream without "
            "changing the visible wake behaviour, e.g. v16c expert-a expert-b2."
        ),
    )
    parser.add_argument(
        "--shadow-threshold",
        type=float,
        default=0.996,
        help="Detection threshold for passive shadow telemetry. Default: 0.996.",
    )
    parser.add_argument(
        "--shadow-hold-frames",
        type=int,
        default=5,
        help="Consecutive above-threshold frames for passive shadow trigger events. Default: 5.",
    )
    parser.add_argument(
        "--shadow-cooldown",
        type=float,
        default=4.0,
        help="Per-shadow-model trigger cooldown in seconds. Default: 4.0.",
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
        "--speech-start-grace",
        type=float,
        default=0.15,
        help="Ignore only this much post-wake audio before speech can start. Default: 0.15.",
    )
    parser.add_argument(
        "--utterance-max-seconds",
        type=float,
        default=14.0,
        help="Maximum command recording length after wake. Default: 14.0 (was 8s).",
    )
    parser.add_argument(
        "--utterance-silence-duration",
        type=float,
        default=1.6,
        help="Trailing silence required before command recording stops. Default: 1.6s.",
    )
    parser.add_argument(
        "--vad-silence-threshold",
        type=float,
        default=0.008,
        help="RMS threshold below which audio counts as silence. Lower is more forgiving. Default: 0.008.",
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
        "--false-positive-audio",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Save local WAV clips for operator-marked false wake triggers. Default: true; use --no-false-positive-audio to disable.",
    )
    parser.add_argument(
        "--false-positive-preroll-seconds",
        type=float,
        default=8.0,
        help="Seconds of wake-listening audio to keep/save before a false-positive Space marker. Default: 8.0.",
    )
    parser.add_argument(
        "--no-wake-beep",
        action="store_true",
        help="Disable short audible cue after wake detection.",
    )
    parser.add_argument(
        "--mute-key",
        type=str,
        default="m",
        help="Terminal key to toggle wake listening during demos/teaching. Default: m.",
    )
    parser.add_argument(
        "--no-mute-key",
        action="store_true",
        help="Disable terminal mic-mute toggle.",
    )
    parser.add_argument(
        "--streaming-stt",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Feed microphone audio into online STT while recording. Default: true.",
    )
    parser.add_argument(
        "--audio-source",
        choices=["host", "korvo-serial"],
        default="host",
        help="Microphone source. host=sounddevice default input; korvo-serial=Korvo-2 PCM serial streamer. Default: host.",
    )
    parser.add_argument(
        "--serial-port",
        default=None,
        help="Serial port for --audio-source korvo-serial. Default: auto-detect /dev/cu.usbserial-*.",
    )
    parser.add_argument(
        "--serial-baud",
        type=int,
        default=DEFAULT_SERIAL_BAUD,
        help=f"Baud rate for Korvo serial PCM. Default: {DEFAULT_SERIAL_BAUD}.",
    )
    parser.add_argument(
        "--serial-start-timeout",
        type=float,
        default=5.0,
        help="Seconds to wait for first Korvo PCM frame. Default: 5.0.",
    )
    parser.add_argument(
        "--serial-gain",
        type=float,
        default=1.0,
        help="Software gain applied to Korvo command/follow-up audio before VAD/STT. Default: 1.0.",
    )
    parser.add_argument(
        "--serial-channel",
        choices=["mic1", "mic2", "mix"],
        default="mic1",
        help="Korvo serial channel to feed to wake/STT. Default: mic1 (usually cleaner for STT than mix).",
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
        "--airfryer",
        action="store_true",
        help="Also enable Philips airfryer MCP server alongside the default WiZ/BLE demo (requires HTTP daemon at 127.0.0.1:8767). Use --no-wiz for airfryer-only.",
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
        help="Use long-lived pi RPC + GPT as the single LLM backend for the existing JSON router (still stateless/rigid by prompt).",
    )
    parser.add_argument(
        "--pi-conversation",
        "--cloud-agent",
        "--smart-kratt",
        dest="pi_conversation",
        action="store_true",
        help="Use a persistent pi RPC conversational cloud-agent instead of the local/stateless intent router. Transcript context is kept across turns.",
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
        "--pi-tools",
        nargs="?",
        const="all",
        default=None,
        help="Enable pi built-in tools for pi RPC. Use without value for all built-ins, or pass a comma list. all=read,bash,edit,write,grep,find,ls.",
    )
    parser.add_argument(
        "--no-pi-tools",
        action="store_true",
        help="Disable pi built-in tools even in smart shortcuts.",
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
        "--response-mode",
        choices=["direct-et", "en-mt"],
        default="direct-et",
        help="Spoken response mode. direct-et uses current Estonian replies; en-mt generates English then translates locally. Default: direct-et.",
    )
    parser.add_argument(
        "--translate-responses",
        dest="response_mode",
        action="store_const",
        const="en-mt",
        help="Shortcut for --response-mode en-mt.",
    )
    parser.add_argument(
        "--response-mt-model",
        default=DEFAULT_EN_ET_CT2_MODEL,
        help=f"CTranslate2 EN→ET model for --response-mode en-mt. Default: {DEFAULT_EN_ET_CT2_MODEL}.",
    )
    parser.add_argument(
        "--response-mt-device",
        default="cpu",
        choices=["cpu", "cuda", "auto"],
        help="Device for response MT. Default: cpu.",
    )
    parser.add_argument(
        "--response-mt-compute-type",
        default="int8",
        help="CTranslate2 compute type for response MT. Default: int8.",
    )
    parser.add_argument(
        "--response-temperature",
        type=float,
        default=0.35,
        help="Ollama temperature for English response generation in en-mt mode. Default: 0.35.",
    )
    parser.add_argument(
        "--response-num-predict",
        type=int,
        default=70,
        help="Max tokens for English response generation in en-mt mode. Default: 70.",
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

    if args.pi_conversation:
        # Conversational mode is implemented through the same long-lived pi RPC
        # transport, but bypasses the old stateless/tool-router prompts.
        args.pi_cli = True
        if not _explicit(args, "helper_warmup"):
            args.helper_warmup = False

    all_pi_builtin_tools = "read,bash,edit,write,grep,find,ls"
    if args.no_pi_tools:
        args.pi_tools = None
    elif args.pi_tools == "all":
        args.pi_tools = all_pi_builtin_tools
    elif args.pi_tools:
        aliases = {"rw": "read,grep,find,ls", "safe": "read,grep,find,ls"}
        args.pi_tools = aliases.get(str(args.pi_tools).strip().lower(), str(args.pi_tools).strip())

    validate_args(args, parser)

    configure_llm_backend(
        llm_model=args.llm,
        pi_model=args.pi_model,
        pi_thinking=args.pi_thinking,
        pi_reset_each_turn=args.pi_reset_each_turn,
        pi_rpc_timeout=args.pi_rpc_timeout,
        pi_rpc_tools=args.pi_tools,
        use_pi_cli=args.pi_cli,
        use_claude_code=False if args.pi_cli else args.claude_code,
        claude_session_id=args.claude_session_id,
        claude_session_started=True if args.claude_session_id else None,
    )

    run_pipeline(args)


if __name__ == "__main__":
    main()
