#!/usr/bin/env python3
"""Full interactive voice pipeline: wake word → STT → LLM → MCP → response.

Supports multi-model temporal consensus detection (matching `kratt live`),
real WiZ bulb control, and interaction logging.

Usage:
    python pipeline.py --no-wakeword --wiz              # manual trigger + WiZ
    python pipeline.py --models v15 --wiz               # single model + WiZ
    python pipeline.py --models v10 v15 --wiz           # multi-model consensus + WiZ
    python pipeline.py --models v15 --wiz --bulbs 192.168.68.56,192.168.68.57
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
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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
LLM_MODEL = "gemma3:4b"
USE_CLAUDE_CODE = False
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

    if args.profile in ("wiz-claude", "demo"):
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
        args.claude_code = True
        args.wiz = True
        args.no_wakeword = True
        args.bulbs = args.bulbs or _cached_wiz_bulbs()


def _sanitize_wiz_bash_command(raw: str) -> str:
    cmd = (raw or "").strip()
    if not cmd:
        return ""
    if DISALLOWED_BASH_RE.search(cmd):
        return ""
    # map leading "wiz" to absolute path at execution time
    return cmd


def llm_plan_wiz_command(user_text: str) -> dict:
    if USE_CLAUDE_CODE:
        data = claude_code_json(SYSTEM_PROMPT_WIZ_BASH, user_text)
    else:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": LLM_MODEL,
                "stream": False,
                "format": "json",
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


# ============================================================
# Streaming wake word model (from multi_model_live_test.py)
# ============================================================


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

        # Zero state
        for detail in self.input_details:
            self.interpreter.set_tensor(
                detail["index"],
                np.zeros(detail["shape"], dtype=detail["dtype"]),
            )

    def reset(self):
        """Reset all state tensors and counters for fresh detection cycle."""
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
        if out_dtype == np.int8:
            scale, zp = self.output_details[0]["quantization"]
            prob = float((output.astype(np.float32) - zp) * scale)
        else:
            prob = float(output[0][0])

        if self.use_ma:
            self.scores.append(prob)
            if len(self.scores) > MA_WINDOW:
                self.scores = self.scores[-MA_WINDOW:]
            score = sum(self.scores) / len(self.scores)
        else:
            score = prob

        now = time.monotonic()
        if score >= self.threshold:
            self.consecutive_hits += 1
        else:
            self.consecutive_hits = 0
        if (
            self.consecutive_hits >= self.required_consecutive
            and (now - self.last_detection_time) > self.cooldown_s
        ):
            self.last_detection_time = now
            self.detection_count += 1
            self.consecutive_hits = 0
            return score

        return None


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


# ============================================================
# Model loading
# ============================================================


def resolve_models(tags: List[str]) -> List[Tuple[str, Path]]:
    resolved = []
    for t in tags:
        path = MODELS_DIR / f"kuule-kratt-{t}" / f"kuule_kratt_{t}.tflite"
        if not path.exists():
            sys.exit(f"Model not found: {path}")
        resolved.append((t, path))
    return resolved


def find_latest_model() -> str:
    cands = []
    for d in MODELS_DIR.glob("kuule-kratt-v*"):
        tag = d.name.replace("kuule-kratt-", "")
        if (d / f"kuule_kratt_{tag}.tflite").exists():
            cands.append((d.stat().st_mtime, tag))
    if cands:
        cands.sort(reverse=True)
        return cands[0][1]
    for d in MODELS_DIR.glob("kuule-kratt-*"):
        tag = d.name.replace("kuule-kratt-", "")
        if (d / f"kuule_kratt_{tag}.tflite").exists():
            return tag
    sys.exit("No wake word models found in " + str(MODELS_DIR))


# ============================================================
# Main pipeline
# ============================================================

# NOTE: This early copy was accidentally left in the file before helper classes
# (SpeechRecognizer, TextToSpeech, MCPClient, ...). Keep it unreachable so the
# complete later definition below is always the one that runs.
def _obsolete_run_pipeline_early(args):
    print(f"{BOLD}Kratt voice pipeline{RESET}")
    if args.wiz_bash:
        mode = "WiZ bash-agent"
    else:
        mode = "WiZ bulbs" if args.wiz else "Mock HA"
    print(f"  Backend: {mode}")
    llm_backend = f"Claude Code session={CLAUDE_SESSION_ID}" if USE_CLAUDE_CODE else LLM_MODEL
    print(f"  LLM: {llm_backend}")
    print("=" * 60)

    system_prompt = SYSTEM_PROMPT_WIZ if args.wiz else SYSTEM_PROMPT_MOCK
    if args.wiz and args.bulbs:
        system_prompt = build_wiz_system_prompt(len([b for b in args.bulbs.split(",") if b.strip()]))
    if args.wiz_bash:
        system_prompt = SYSTEM_PROMPT_WIZ_BASH

    if args.wiz_bash and not WIZ_CLI.exists():
        sys.exit(f"wiz CLI not found: {WIZ_CLI}")

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

    # --- Consensus config ---
    n_models = len(models)
    min_consensus = args.consensus if args.consensus is not None else n_models
    consensus_window_s = args.consensus_window_ms / 1000.0

    # --- STT ---
    print(f"  STT: {STT_MODEL_DIR.name}")
    stt = SpeechRecognizer(str(STT_MODEL_DIR))

    # --- MCP server ---
    ha = None
    if not args.wiz_bash:
        mcp_server = WIZ_MCP_SERVER if args.wiz else MOCK_MCP_SERVER
        mcp_args = []
        if args.wiz and args.bulbs:
            mcp_args = ["--bulbs", args.bulbs]

        print(f"  Starting MCP server...")
        ha = MCPClient(mcp_server, mcp_args)
    else:
        print(f"  Using wiz-cli bash mode: {WIZ_CLI}")

    # --- Logger ---
    logger = InteractionLogger(
        enabled=args.log,
        participant_id=args.participant,
        log_dir=LOG_DIR,
        llm_model=f"claude-code:{CLAUDE_SESSION_ID}" if USE_CLAUDE_CODE else LLM_MODEL,
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
    else:
        tts_available = False
        print(f"  TTS: not available (start tts-server/server.py for voice output)")

    # --- LLM warmup ---
    print(f"  Warming up {'Claude Code' if USE_CLAUDE_CODE else LLM_MODEL}...")
    try:
        if args.wiz_bash:
            llm_plan_wiz_command("pane tuli põlema")
        else:
            llm_parse_intent("tere", system_prompt)
        print(f"  LLM ready")
    except Exception as e:
        print(f"  LLM warmup failed: {e}")
        print("  Make sure ollama is running: ollama serve")
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
    last_consensus_time = 0.0
    consensus_cooldown_s = args.post_trigger_cooldown
    recent_detections: dict[str, float] = {}

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
                                    log_line(
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

            # --- Record user speech ---
            print("  Recording... (speak now, stops on silence)")
            t0 = time.monotonic()
            audio = record_until_silence()
            t_rec = time.monotonic() - t0
            print(f"  Recorded {t_rec:.1f}s of audio")

            if len(audio) < SAMPLE_RATE * 0.3:
                print("  Too short, skipping")
                logger.log_interaction(
                    {
                        "outcome": "skipped_too_short",
                        "wake_word_prob": wake_prob,
                        "wake_models": wake_models_agreed,
                        "audio_duration_s": round(float(len(audio)) / SAMPLE_RATE, 3),
                    }
                )
                if models:
                    print(f'  Listening for "Kuule Kratt"...\n')
                continue

            # --- STT ---
            print("  Transcribing...")
            t1 = time.monotonic()
            transcript = stt.transcribe(audio)
            t_stt = time.monotonic() - t1
            print(f'  STT ({t_stt:.1f}s): "{transcript}"')

            if not transcript:
                print("  Empty transcript, skipping")
                logger.log_interaction(
                    {
                        "outcome": "empty_transcript",
                        "wake_word_prob": wake_prob,
                        "wake_models": wake_models_agreed,
                        "audio_duration_s": round(float(len(audio)) / SAMPLE_RATE, 3),
                        "stt_latency_ms": int(t_stt * 1000),
                    }
                )
                if models:
                    print(f'  Listening for "Kuule Kratt"...\n')
                continue

            # --- LLM/execute ---
            t2 = time.monotonic()
            llm1_error = None
            executed_actions = []
            tool_results = []
            response = ""
            llm2_error = None
            t_llm2 = 0.0

            if args.wiz_bash:
                print("  Planning bash command...")
                try:
                    command, cli_result, response, ok = execute_wiz_bash_mode(transcript)
                    actions = [{"command": command}] if command else []
                    if command:
                        print(f"  LLM ({time.monotonic()-t2:.1f}s): {command}")
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
                    actions = []
                    llm1_error = str(e)
                    response = "Vabandust, käsu täitmine ebaõnnestus."
            else:
                print("  Parsing intent...")
                try:
                    parsed = llm_parse_intent(transcript, system_prompt)
                    actions = parsed.get("actions", [])
                except Exception as e:
                    parsed = {}
                    actions = []
                    llm1_error = str(e)
                print(f"  LLM ({time.monotonic()-t2:.1f}s): {json.dumps(actions, ensure_ascii=False)}")

                # --- Execute actions (MCP JSON mode) ---
                for action in actions:
                    if not isinstance(action, dict):
                        print(f"  Skipping malformed action: {action}")
                        continue
                    action_name = action.pop("action", "")
                    try:
                        result = ha.execute(action_name, action)
                    except RuntimeError as e:
                        result = f"MCP error: {e}"
                    tool_results.append(result)
                    executed_actions.append(
                        {"action": action_name, "args": action, "result": result}
                    )
                    print(f"  -> {action_name}: {result}")

                # --- LLM: generate response ---
                print("  Generating response...")
                t3 = time.monotonic()
                try:
                    response = llm_respond(
                        transcript, "\n".join(tool_results), system_prompt
                    )
                except Exception as e:
                    response = ""
                    llm2_error = str(e)
                t_llm2 = time.monotonic() - t3

            t_llm1 = time.monotonic() - t2

            t_total = time.monotonic() - t0
            print(f"\n  KRATT: {BOLD}{response}{RESET}")
            print(
                f"  rec={t_rec:.1f}s stt={t_stt:.1f}s llm1={t_llm1:.1f}s llm2={t_llm2:.1f}s total={t_total:.1f}s"
            )

            # --- TTS: speak the response ---
            t_tts = 0.0
            if tts_available and response:
                try:
                    t_tts = tts.speak(response)
                    print(f"  TTS: {t_tts:.1f}s")
                except Exception as e:
                    print(f"  TTS error: {e}")

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
                    "e2e_latency_ms": int(t_total * 1000),
                }
            )

            print()
            if models:
                print(f'  Listening for "Kuule Kratt"...\n')

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


def _obsolete_main_early():
    global LLM_MODEL, USE_CLAUDE_CODE, CLAUDE_SESSION_ID, CLAUDE_SESSION_STARTED

    parser = argparse.ArgumentParser(description="Kratt full voice pipeline")
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
        default=4.0,
        help="Cooldown after a trigger/turn before listening again. Default: 4.0.",
    )
    parser.add_argument(
        "--no-wakeword", action="store_true", help="Skip wake word, manual trigger"
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
        "--bulbs",
        type=str,
        default=None,
        help="Comma-separated WiZ bulb IPs (skip discovery)",
    )
    parser.add_argument(
        "--llm",
        type=str,
        default=LLM_MODEL,
        help=f"Ollama model name. Default: {LLM_MODEL}",
    )
    parser.add_argument(
        "--claude-code",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use Claude Code instead of Ollama/Gemma. Default: true. Use --no-claude-code for Ollama.",
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

    if args.wiz_bash:
        args.wiz = True

    LLM_MODEL = args.llm

    _obsolete_run_pipeline_early(args)


# ============================================================
# Streaming wake word model (from multi_model_live_test.py)
# ============================================================


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

        # Zero state
        for detail in self.input_details:
            self.interpreter.set_tensor(
                detail["index"],
                np.zeros(detail["shape"], dtype=detail["dtype"]),
            )

    def reset(self):
        """Reset all state tensors and counters for fresh detection cycle."""
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

    def is_available(self) -> bool:
        if self._available is None:
            try:
                r = requests.get(
                    self.url.replace("/synthesize", "/speakers"), timeout=2
                )
                self._available = r.status_code == 200
            except Exception:
                self._available = False
        return self._available

    def speak(self, text: str) -> float:
        """Synthesize and play text. Returns duration in seconds."""
        if not text or not self.is_available():
            return 0.0

        t0 = time.monotonic()
        r = requests.post(
            self.url,
            json={
                "text": text,
                "speaker": self.speaker,
                "speed": self.speed,
            },
            timeout=30,
        )
        r.raise_for_status()

        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as raw:
            raw.write(r.content)
            raw_path = raw.name

        if self.apply_effects:
            out_path = raw_path.replace(".wav", "_fx.wav")
            cmd = ["sox", raw_path, out_path] + self.SOX_EFFECTS
            subprocess.run(cmd, check=True, capture_output=True)
            play_path = out_path
        else:
            play_path = raw_path

        # Play audio (blocks until done)
        subprocess.run(["sox", play_path, "-d"], capture_output=True)

        # Cleanup
        os.unlink(raw_path)
        if self.apply_effects and os.path.exists(out_path):
            os.unlink(out_path)

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
# LLM (Ollama / Claude Code)
# ============================================================


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


def llm_parse_intent(user_text: str, system_prompt: str) -> dict:
    if USE_CLAUDE_CODE:
        return claude_code_json(system_prompt, user_text)
    resp = requests.post(
        OLLAMA_URL,
        json={
            "model": LLM_MODEL,
            "stream": False,
            "format": "json",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
        },
    )
    resp.raise_for_status()
    return json.loads(resp.json()["message"]["content"])


def llm_respond(user_text: str, tool_results: str, system_prompt: str) -> str:
    followup = f"{user_text}\n\nTööriistade tulemused: {tool_results}\nVasta kasutajale."
    if USE_CLAUDE_CODE:
        return claude_code_json(system_prompt, followup).get("response", "")
    resp = requests.post(
        OLLAMA_URL,
        json={
            "model": LLM_MODEL,
            "stream": False,
            "format": "json",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
                {
                    "role": "user",
                    "content": f"Tööriistade tulemused: {tool_results}\nVasta kasutajale.",
                },
            ],
        },
    )
    resp.raise_for_status()
    return json.loads(resp.json()["message"]["content"]).get("response", "")


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
    print(f"{BOLD}Kratt voice pipeline{RESET}")
    if args.wiz_bash:
        mode = "WiZ bash-agent"
    else:
        mode = "WiZ bulbs" if args.wiz else "Mock HA"
    print(f"  Backend: {mode}")
    llm_backend = f"Claude Code session={CLAUDE_SESSION_ID}" if USE_CLAUDE_CODE else LLM_MODEL
    print(f"  LLM: {llm_backend}")
    print("=" * 60)

    system_prompt = SYSTEM_PROMPT_WIZ if args.wiz else SYSTEM_PROMPT_MOCK
    if args.wiz and args.bulbs:
        system_prompt = build_wiz_system_prompt(len([b for b in args.bulbs.split(",") if b.strip()]))
    if args.wiz_bash:
        system_prompt = SYSTEM_PROMPT_WIZ_BASH

    if args.wiz_bash and not WIZ_CLI.exists():
        sys.exit(f"wiz CLI not found: {WIZ_CLI}")

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

    # --- Consensus config ---
    n_models = len(models)
    min_consensus = args.consensus if args.consensus is not None else n_models
    consensus_window_s = args.consensus_window_ms / 1000.0

    # --- STT ---
    print(f"  STT: {STT_MODEL_DIR.name}")
    stt = SpeechRecognizer(str(STT_MODEL_DIR))

    # --- MCP server ---
    mcp_server = WIZ_MCP_SERVER if args.wiz else MOCK_MCP_SERVER
    mcp_args = []
    if args.wiz and args.bulbs:
        mcp_args = ["--bulbs", args.bulbs]

    print(f"  Starting MCP server...")
    ha = MCPClient(mcp_server, mcp_args)

    # --- Logger ---
    logger = InteractionLogger(
        enabled=args.log,
        participant_id=args.participant,
        log_dir=LOG_DIR,
        llm_model=f"claude-code:{CLAUDE_SESSION_ID}" if USE_CLAUDE_CODE else LLM_MODEL,
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
    else:
        tts_available = False
        print(f"  TTS: not available (start tts-server/server.py for voice output)")

    # --- LLM warmup ---
    print(f"  Warming up {'Claude Code' if USE_CLAUDE_CODE else LLM_MODEL}...")
    try:
        llm_parse_intent("tere", system_prompt)
        print(f"  LLM ready")
    except Exception as e:
        print(f"  LLM warmup failed: {e}")
        print("  Make sure ollama is running: ollama serve")
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
    last_consensus_time = 0.0
    consensus_cooldown_s = args.post_trigger_cooldown
    recent_detections: dict[str, float] = {}

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
                                    log_line(
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

            # --- Record user speech ---
            print("  Recording... (speak now, stops on silence)")
            t0 = time.monotonic()
            audio = record_until_silence()
            t_rec = time.monotonic() - t0
            print(f"  Recorded {t_rec:.1f}s of audio")

            if len(audio) < SAMPLE_RATE * 0.3:
                print("  Too short, skipping")
                logger.log_interaction(
                    {
                        "outcome": "skipped_too_short",
                        "wake_word_prob": wake_prob,
                        "wake_models": wake_models_agreed,
                        "audio_duration_s": round(float(len(audio)) / SAMPLE_RATE, 3),
                    }
                )
                if models:
                    print(f'  Listening for "Kuule Kratt"...\n')
                continue

            # --- STT ---
            print("  Transcribing...")
            t1 = time.monotonic()
            transcript = stt.transcribe(audio)
            t_stt = time.monotonic() - t1
            print(f'  STT ({t_stt:.1f}s): "{transcript}"')

            if not transcript:
                print("  Empty transcript, skipping")
                logger.log_interaction(
                    {
                        "outcome": "empty_transcript",
                        "wake_word_prob": wake_prob,
                        "wake_models": wake_models_agreed,
                        "audio_duration_s": round(float(len(audio)) / SAMPLE_RATE, 3),
                        "stt_latency_ms": int(t_stt * 1000),
                    }
                )
                if models:
                    print(f'  Listening for "Kuule Kratt"...\n')
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

            if args.wiz_bash:
                print("  Planning WiZ bash command...")
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
                if llm1_error:
                    print(f"  LLM/tool error: {llm1_error}")
            else:
                print("  Parsing intent...")
                try:
                    parsed = llm_parse_intent(transcript, system_prompt)
                    actions = parsed.get("actions", [])
                except Exception as e:
                    parsed = {}
                    actions = []
                    llm1_error = str(e)
                t_llm1 = time.monotonic() - t2
                print(f"  LLM ({t_llm1:.1f}s): {json.dumps(actions, ensure_ascii=False)}")
                if llm1_error:
                    print(f"  LLM error: {llm1_error}")

                # --- Execute actions ---
                for action in actions:
                    if not isinstance(action, dict):
                        print(f"  Skipping malformed action: {action}")
                        continue
                    action_name = action.pop("action", "")
                    try:
                        result = ha.execute(action_name, action)
                    except RuntimeError as e:
                        result = f"MCP error: {e}"
                    tool_results.append(result)
                    executed_actions.append(
                        {"action": action_name, "args": action, "result": result}
                    )
                    print(f"  -> {action_name}: {result}")

                # --- LLM: generate response ---
                print("  Generating response...")
                t3 = time.monotonic()
                try:
                    response = llm_respond(
                        transcript, "\n".join(tool_results), system_prompt
                    )
                except Exception as e:
                    response = ""
                    llm2_error = str(e)
                t_llm2 = time.monotonic() - t3
                if llm2_error:
                    print(f"  Response LLM error: {llm2_error}")

            t_total = time.monotonic() - t0
            print(f"\n  KRATT: {BOLD}{response}{RESET}")
            print(
                f"  rec={t_rec:.1f}s stt={t_stt:.1f}s llm1={t_llm1:.1f}s llm2={t_llm2:.1f}s total={t_total:.1f}s"
            )

            # --- TTS: speak the response ---
            t_tts = 0.0
            if tts_available and response:
                try:
                    t_tts = tts.speak(response)
                    print(f"  TTS: {t_tts:.1f}s")
                except Exception as e:
                    print(f"  TTS error: {e}")

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
                    "e2e_latency_ms": int(t_total * 1000),
                }
            )

            if models and args.post_trigger_cooldown > 0:
                print(f"  Cooldown {args.post_trigger_cooldown:.1f}s before listening again...")
                time.sleep(args.post_trigger_cooldown)

            print()
            if models:
                print(f'  Listening for "Kuule Kratt"...\n')

    except KeyboardInterrupt:
        print("\n\nStopped.")
        if models:
            print(f"  Consensus detections: {consensus_count}")
            for m in models:
                print(f"  {m.color}■{RESET} {m.name}: {m.detection_count} individual")
    finally:
        demo_log_fh.close()
        logger.close()
        ha.close()


def main():
    global LLM_MODEL, USE_CLAUDE_CODE, CLAUDE_SESSION_ID, CLAUDE_SESSION_STARTED

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
        default=4.0,
        help="Cooldown after a trigger/turn before listening again. Default: 4.0.",
    )
    parser.add_argument(
        "--no-wakeword", action="store_true", help="Skip wake word, manual trigger"
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
        "--bulbs",
        type=str,
        default=None,
        help="Comma-separated WiZ bulb IPs (skip discovery)",
    )
    parser.add_argument(
        "--llm",
        type=str,
        default=LLM_MODEL,
        help=f"Ollama model name. Default: {LLM_MODEL}",
    )
    parser.add_argument(
        "--claude-code",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use Claude Code instead of Ollama/Gemma. Default: true. Use --no-claude-code for Ollama.",
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
        args.bulbs = _cached_wiz_bulbs()
    if args.wiz is None:
        args.wiz = bool(args.bulbs)

    if args.wiz_bash:
        args.wiz = True

    LLM_MODEL = args.llm
    USE_CLAUDE_CODE = args.claude_code
    if args.claude_session_id:
        CLAUDE_SESSION_ID = args.claude_session_id
        CLAUDE_SESSION_STARTED = True

    run_pipeline(args)


if __name__ == "__main__":
    main()
