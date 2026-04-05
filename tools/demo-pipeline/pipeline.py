#!/usr/bin/env python3
"""Full interactive voice pipeline: wake word → STT → LLM → MCP → response.

Runs entirely on Mac: TFLite wake word, sherpa-onnx STT, Ollama LLM, mock HA.

Usage:
    python pipeline.py
    python pipeline.py --threshold 0.7 --no-wakeword  # skip wake word, just STT→LLM
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import threading
from pathlib import Path

import numpy as np
import requests
import sounddevice as sd

# --- Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
WAKEWORD_MODEL = PROJECT_ROOT / "wake-word/models/kuule-kratt-v7/kuule_kratt_v7.tflite"
STT_MODEL_DIR = PROJECT_ROOT / "wake-word/models/kiirkirjutaja-int8"
MCP_SERVER = PROJECT_ROOT / "tools/mock-ha-server/server.py"

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
                continue

            # STT
            print("📝 Transcribing...")
            t1 = time.monotonic()
            transcript = stt.transcribe(audio)
            t_stt = time.monotonic() - t1
            print(f"   STT ({t_stt:.1f}s): \"{transcript}\"")

            if not transcript:
                print("   Empty transcript, skipping")
                continue

            # LLM: parse intent
            print("🧠 Parsing intent...")
            t2 = time.monotonic()
            parsed = llm_parse_intent(transcript)
            t_llm1 = time.monotonic() - t2
            actions = parsed.get("actions", [])
            print(f"   LLM ({t_llm1:.1f}s): {json.dumps(actions, ensure_ascii=False)}")

            # Execute actions
            tool_results = []
            for action in actions:
                action_name = action.pop("action", "")
                result = ha.execute(action_name, action)
                tool_results.append(result)
                print(f"   ⚡ {action_name}: {result}")

            # LLM: generate response
            print("💬 Generating response...")
            t3 = time.monotonic()
            response = llm_respond(transcript, "\n".join(tool_results))
            t_llm2 = time.monotonic() - t3

            t_total = time.monotonic() - t0
            print(f"\n🔊 KRATT: {response}")
            print(f"   ⏱️  rec={t_rec:.1f}s stt={t_stt:.1f}s llm1={t_llm1:.1f}s llm2={t_llm2:.1f}s total={t_total:.1f}s")
            print()
            if wakeword:
                print(f'Listening for "Kuule Kratt"...')

    except KeyboardInterrupt:
        print("\n\nStopped.")
    finally:
        ha.close()


def main():
    parser = argparse.ArgumentParser(description="Kratt full voice pipeline")
    parser.add_argument("--threshold", type=float, default=0.5, help="Wake word threshold")
    parser.add_argument("--no-wakeword", action="store_true", help="Skip wake word, manual trigger")
    args = parser.parse_args()
    run_pipeline(args)


if __name__ == "__main__":
    main()
