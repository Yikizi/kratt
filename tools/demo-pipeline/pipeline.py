#!/usr/bin/env python3
"""Full interactive voice pipeline: wake word → STT → LLM → MCP → response.

Runs entirely on Mac: TFLite wake word, sherpa-onnx STT, Ollama LLM, mock HA.

Usage:
    python pipeline.py
    python pipeline.py --threshold 0.7 --no-wakeword  # manual trigger mode
    python pipeline.py --log --participant P01        # enable telemetry logging
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests
import sounddevice as sd

# --- Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
WAKEWORD_MODEL = PROJECT_ROOT / "wake-word/models/kuule-kratt-v7/kuule_kratt_v7.tflite"
STT_MODEL_DIR = PROJECT_ROOT / "wake-word/models/kiirkirjutaja-int8"
MCP_SERVER = PROJECT_ROOT / "tools/mock-ha-server/server.py"
LOG_DIR = PROJECT_ROOT / "wake-word/evaluation/logs"

OLLAMA_URL = "http://localhost:11434/api/chat"
LLM_MODEL = "gemma3:12b"
SAMPLE_RATE = 16000

SYSTEM_PROMPT = """\
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


# ============================================================
# Interaction logger (opt-in via --log flag)
# ============================================================

class InteractionLogger:
    """Append-only JSONL logger for one user testing session.

    One file per session. Each line is a complete interaction record.
    Disabled by default — only writes when explicitly enabled via --log.
    """

    def __init__(
        self,
        enabled: bool,
        participant_id: str,
        log_dir: Path,
        llm_model: str,
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

        # Session header
        self._write({
            "type": "session_start",
            "session_id": self.session_id,
            "participant_id": participant_id,
            "timestamp": self.session_start,
            "llm_model": llm_model,
            "wake_threshold": wake_threshold,
            "wakeword_model": WAKEWORD_MODEL.name,
            "stt_model": STT_MODEL_DIR.name,
            "host": os.uname().nodename,
        })
        print(f"📊 Logging to {self.path.name}")

    def set_task(self, task_id: str | None):
        self._current_task = task_id
        if self.enabled and task_id:
            self._write({
                "type": "task_change",
                "task_id": task_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

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
        self._write({
            "type": "session_end",
            "session_id": self.session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "interaction_count": self._interaction_seq,
        })


# ============================================================
# Wake word detector
# ============================================================

class WakeWordDetector:
    def __init__(self, model_path: str, threshold: float = 0.5):
        try:
            import tensorflow.lite as tflite
        except ImportError:
            import tflite_runtime.interpreter as tflite

        from pymicro_features import MicroFrontend

        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.threshold = threshold
        self.frontend = MicroFrontend()
        self.process_fn = getattr(self.frontend, "process_samples", None) or \
                          getattr(self.frontend, "ProcessSamples", None)

        self.reset()

    def reset(self):
        """Reset all model state tensors and warmup counter."""
        for detail in self.input_details:
            self.interpreter.set_tensor(
                detail['index'],
                np.zeros(detail['shape'], dtype=detail['dtype'])
            )
        self._frame_count = 0
        self._warmup = 50
        self.frontend = type(self.frontend)()
        self.process_fn = getattr(self.frontend, "process_samples", None) or \
                          getattr(self.frontend, "ProcessSamples", None)

    def process_audio(self, audio_int16: bytes) -> float | None:
        """Process raw int16 audio bytes, return probability if past warmup."""
        result = self.process_fn(audio_int16)
        if not result.features:
            return None

        features = np.array(result.features, dtype=np.float32)
        expected_shape = self.input_details[0]['shape']
        features = features.reshape(expected_shape)

        inp_dtype = self.input_details[0]['dtype']
        if inp_dtype == np.int8:
            scale, zero_point = self.input_details[0]['quantization']
            features = (features / scale + zero_point).clip(-128, 127).astype(np.int8)

        self.interpreter.set_tensor(self.input_details[0]['index'], features)
        self.interpreter.invoke()
        self._frame_count += 1

        if self._frame_count <= self._warmup:
            return None

        output = self.interpreter.get_tensor(self.output_details[0]['index'])
        out_dtype = self.output_details[0]['dtype']
        if out_dtype in (np.int8, np.uint8):
            scale, zero_point = self.output_details[0]['quantization']
            return float(((output.astype(np.float32) - zero_point) * scale).flat[0])
        return float(output.flatten()[0])


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
        """Transcribe float32 audio array."""
        stream = self.recognizer.create_stream()
        # Add audio + tail padding
        tail = np.zeros(int(0.3 * SAMPLE_RATE), dtype=np.float32)
        audio = np.concatenate([audio_float32, tail])
        stream.accept_waveform(SAMPLE_RATE, audio)

        while self.recognizer.is_ready(stream):
            self.recognizer.decode_stream(stream)

        return self.recognizer.get_result(stream).strip()


# ============================================================
# MCP client (mock HA)
# ============================================================

class MockHAClient:
    def __init__(self):
        self.proc = subprocess.Popen(
            [sys.executable, str(MCP_SERVER)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self._send({"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {}})

    def _send(self, req: dict) -> dict:
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        return json.loads(line) if line.strip() else {}

    def execute(self, action: str, args: dict) -> str:
        resp = self._send({
            "jsonrpc": "2.0", "id": 1,
            "method": "tools/call",
            "params": {"name": action, "arguments": args},
        })
        content = resp.get("result", {}).get("content", [{}])
        return content[0].get("text", "") if content else ""

    def close(self):
        self.proc.terminate()


# ============================================================
# LLM (Ollama)
# ============================================================

def llm_parse_intent(user_text: str) -> dict:
    """First LLM call: parse user intent into actions."""
    resp = requests.post(OLLAMA_URL, json={
        "model": LLM_MODEL,
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
    })
    resp.raise_for_status()
    return json.loads(resp.json()["message"]["content"])


def llm_respond(user_text: str, tool_results: str) -> str:
    """Second LLM call: generate natural response from tool results."""
    resp = requests.post(OLLAMA_URL, json={
        "model": LLM_MODEL,
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
            {"role": "user", "content": f"Tööriistade tulemused: {tool_results}\nVasta kasutajale."},
        ],
    })
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
    """Record from mic until silence detected or max duration."""
    frame_size = int(SAMPLE_RATE * 0.032)  # 32ms frames
    chunks = []
    silent_frames = 0
    frames_for_silence = int(silence_duration / 0.032)
    max_frames = int(max_seconds / 0.032)
    done = threading.Event()

    def callback(indata, frames, time_info, status):
        nonlocal silent_frames
        chunks.append(indata[:, 0].copy())
        energy = np.sqrt(np.mean(indata ** 2))
        if energy < silence_threshold:
            silent_frames += 1
        else:
            silent_frames = 0
        if silent_frames >= frames_for_silence or len(chunks) >= max_frames:
            done.set()

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32',
                        blocksize=frame_size, callback=callback):
        done.wait(timeout=max_seconds + 1)

    if not chunks:
        return np.array([], dtype=np.float32)
    return np.concatenate(chunks)


# ============================================================
# Main pipeline
# ============================================================

def run_pipeline(args):
    print("Kratt voice pipeline")
    print("=" * 50)

    logger = InteractionLogger(
        enabled=args.log,
        participant_id=args.participant,
        log_dir=LOG_DIR,
        llm_model=LLM_MODEL,
        wake_threshold=args.threshold,
    )
    if args.task:
        logger.set_task(args.task)

    # Init components
    wakeword = None
    if not args.no_wakeword:
        print(f"Loading wake word model: {WAKEWORD_MODEL.name}")
        wakeword = WakeWordDetector(str(WAKEWORD_MODEL), threshold=args.threshold)

    print(f"Loading STT model: {STT_MODEL_DIR.name}")
    stt = SpeechRecognizer(str(STT_MODEL_DIR))

    print("Starting mock HA server...")
    ha = MockHAClient()

    # Warm up Ollama (preload model + cache system prompt)
    print(f"Warming up {LLM_MODEL}...")
    try:
        llm_parse_intent("tere")
        print("LLM ready (prompt cached)")
    except Exception as e:
        print(f"LLM warmup failed: {e}")
        print("Make sure ollama is running: ollama serve")
        return

    print("\n" + "=" * 50)
    if wakeword:
        print(f'Listening for "Kuule Kratt" (threshold={args.threshold})...')
    else:
        print("Wake word disabled — press Enter to start recording")
    print("Ctrl+C to exit\n")

    frame_samples = int(SAMPLE_RATE * 0.01)  # 10ms frames for wake word
    frame_bytes = frame_samples * 2  # int16
    audio_buffer = bytearray()
    last_detection = 0.0

    def wakeword_callback(indata, frames, time_info, status):
        nonlocal audio_buffer
        int16 = (indata[:, 0] * 32768).clip(-32768, 32767).astype(np.int16)
        audio_buffer.extend(int16.tobytes())

    try:
        while True:
            wake_prob = None
            wake_detected_at = None
            if wakeword:
                # Wake word listening loop
                audio_buffer = bytearray()
                detected = False

                with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32',
                                    blocksize=frame_samples, callback=wakeword_callback):
                    while not detected:
                        while len(audio_buffer) >= frame_bytes:
                            chunk = bytes(audio_buffer[:frame_bytes])
                            del audio_buffer[:frame_bytes]

                            prob = wakeword.process_audio(chunk)
                            if prob is None:
                                continue

                            now = time.monotonic()
                            if prob > args.threshold and (now - last_detection) > 2.0:
                                detected = True
                                last_detection = now
                                wake_prob = prob
                                wake_detected_at = now
                                wakeword.reset()
                                print(f"\n>>> KUULE KRATT detected! (prob={prob:.3f})")
                                break
                            elif prob > 0.1:
                                bar = "█" * int(prob * 30)
                                print(f"  {prob:.3f} {bar}", end="\r")

                        time.sleep(0.005)
            else:
                input("\nPress Enter to start recording...")

            # Record user speech
            print("🎙️  Recording... (speak now, stops on silence)")
            t0 = time.monotonic()
            audio = record_until_silence()
            t_rec = time.monotonic() - t0
            print(f"   Recorded {t_rec:.1f}s of audio")

            if len(audio) < SAMPLE_RATE * 0.3:  # Less than 0.3s
                print("   Too short, skipping")
                logger.log_interaction({
                    "outcome": "skipped_too_short",
                    "wake_word_prob": wake_prob,
                    "audio_duration_s": round(float(len(audio)) / SAMPLE_RATE, 3),
                })
                continue

            # STT
            print("📝 Transcribing...")
            t1 = time.monotonic()
            transcript = stt.transcribe(audio)
            t_stt = time.monotonic() - t1
            print(f"   STT ({t_stt:.1f}s): \"{transcript}\"")

            if not transcript:
                print("   Empty transcript, skipping")
                logger.log_interaction({
                    "outcome": "empty_transcript",
                    "wake_word_prob": wake_prob,
                    "audio_duration_s": round(float(len(audio)) / SAMPLE_RATE, 3),
                    "stt_latency_ms": int(t_stt * 1000),
                })
                continue

            # LLM: parse intent
            print("🧠 Parsing intent...")
            t2 = time.monotonic()
            llm1_error = None
            try:
                parsed = llm_parse_intent(transcript)
                actions = parsed.get("actions", [])
            except Exception as e:
                parsed = {}
                actions = []
                llm1_error = str(e)
            t_llm1 = time.monotonic() - t2
            print(f"   LLM ({t_llm1:.1f}s): {json.dumps(actions, ensure_ascii=False)}")

            # Execute actions
            tool_results = []
            executed_actions = []
            for action in actions:
                action_copy = dict(action)  # preserve for logging
                action_name = action.pop("action", "")
                result = ha.execute(action_name, action)
                tool_results.append(result)
                executed_actions.append({"action": action_name, "args": action, "result": result})
                print(f"   ⚡ {action_name}: {result}")

            # LLM: generate response
            print("💬 Generating response...")
            t3 = time.monotonic()
            llm2_error = None
            try:
                response = llm_respond(transcript, "\n".join(tool_results))
            except Exception as e:
                response = ""
                llm2_error = str(e)
            t_llm2 = time.monotonic() - t3

            t_total = time.monotonic() - t0
            print(f"\n🔊 KRATT: {response}")
            print(f"   ⏱️  rec={t_rec:.1f}s stt={t_stt:.1f}s llm1={t_llm1:.1f}s llm2={t_llm2:.1f}s total={t_total:.1f}s")

            logger.log_interaction({
                "outcome": "completed" if not (llm1_error or llm2_error) else "llm_error",
                "wake_word_prob": wake_prob,
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
                "e2e_latency_ms": int(t_total * 1000),
            })

            print()
            if wakeword:
                print(f'Listening for "Kuule Kratt"...')

    except KeyboardInterrupt:
        print("\n\nStopped.")
    finally:
        logger.close()
        ha.close()


def main():
    parser = argparse.ArgumentParser(description="Kratt full voice pipeline")
    parser.add_argument("--threshold", type=float, default=0.5, help="Wake word threshold")
    parser.add_argument("--no-wakeword", action="store_true", help="Skip wake word, manual trigger")
    parser.add_argument(
        "--log",
        action="store_true",
        help="Enable per-interaction JSONL telemetry (off by default to keep dev runs clean)",
    )
    parser.add_argument(
        "--participant",
        default="dev",
        help="Participant ID for log file naming (default: dev)",
    )
    parser.add_argument(
        "--task",
        default=None,
        help="Initial task ID tag for logged interactions (e.g. T1_turn_on)",
    )
    args = parser.parse_args()
    run_pipeline(args)


if __name__ == "__main__":
    main()
