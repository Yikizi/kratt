#!/usr/bin/env python3
import sounddevice as sd
import numpy as np
import webrtcvad
import time
import threading
from queue import Queue, Full
from faster_whisper import WhisperModel
from collections import deque

# ================= CONFIG =================

SAMPLE_RATE = 16000

FRAME_DURATION = 30  # ms (10/20/30 supported by webrtcvad)
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION / 1000)

SILENCE_TIMEOUT = 0.35  # seconds of silence = end of utterance
MIN_AUDIO_LENGTH = 0.3  # minimum seconds of audio to process
MAX_AUDIO_SECONDS = 4.0  # hard cap - prevents decoder explosion

# ==========================================

print("🎤 Estonian Whisper – Live Streaming Test")
print("=" * 50)

print("🧠 Loading Whisper medium-et (int8)...")
model = WhisperModel("whisper-medium-et-ct2", device="cpu", compute_type="int8")
print("✅ Model ready\n")

vad = webrtcvad.Vad(2)  # aggressiveness: 0–3

# ==========================================

buffer = []
voiced = False
silence_start = None
audio_queue = deque()

# Single-worker transcription queue (maxsize=1 = keep only latest)
transcribe_queue = Queue(maxsize=1)


def transcribe_worker():
    """Single worker - NEVER run more than one model.transcribe() at a time on CPU."""
    while True:
        audio, duration = transcribe_queue.get()
        t0 = time.time()

        segments, _ = model.transcribe(
            audio,
            language="et",
            beam_size=1,
            vad_filter=False,
        )

        text = " ".join(seg.text for seg in segments).strip()
        dt = time.time() - t0

        if text:
            print(f"📝 {text}")
            print(f"⏱️  {dt:.2f}s (RTF: {dt/duration:.2f}x)\n")
        else:
            print(f"⚠️  (no text recognized)")
            print(f"⏱️  {dt:.2f}s\n")

        transcribe_queue.task_done()


# Start EXACTLY ONE worker
threading.Thread(target=transcribe_worker, daemon=True).start()


def audio_callback(indata, frames, time_info, status):
    """Called by sounddevice for each audio block."""
    if status:
        print(f"⚠️  Audio status: {status}")
    audio_queue.append(indata.copy())


print("🎧 Listening... Speak naturally (Ctrl+C to stop)\n")

try:
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        blocksize=FRAME_SIZE,
        dtype="int16",
        callback=audio_callback,
    ):
        while True:
            if not audio_queue:
                time.sleep(0.01)
                continue

            frame = audio_queue.popleft()
            frame = frame.squeeze()

            if len(frame) != FRAME_SIZE:
                continue

            is_speech = vad.is_speech(frame.tobytes(), SAMPLE_RATE)

            if is_speech:
                if not voiced:
                    print("🟢 speech", flush=True)
                voiced = True
                silence_start = None
                buffer.append(frame.astype(np.float32) / 32768.0)

            elif voiced:
                buffer.append(frame.astype(np.float32) / 32768.0)

                if silence_start is None:
                    silence_start = time.time()

                elif time.time() - silence_start > SILENCE_TIMEOUT:
                    print("🔵 end", flush=True)

                    audio = np.concatenate(buffer)
                    audio_duration = len(audio) / SAMPLE_RATE

                    # Hard cap to prevent decoder explosion
                    if audio_duration > MAX_AUDIO_SECONDS:
                        audio = audio[-int(MAX_AUDIO_SECONDS * SAMPLE_RATE):]
                        audio_duration = len(audio) / SAMPLE_RATE
                        print(f"✂️  Capped to {MAX_AUDIO_SECONDS}s")

                    print(f"📊 Audio: {audio_duration:.2f}s", flush=True)

                    buffer.clear()
                    voiced = False
                    silence_start = None

                    if audio_duration < MIN_AUDIO_LENGTH:
                        print(f"⚠️  Too short\n")
                        continue

                    # Submit to single worker (drop old if busy)
                    if transcribe_queue.full():
                        try:
                            transcribe_queue.get_nowait()  # drop old
                            print("⏭️  Dropped old audio (worker busy)")
                        except:
                            pass

                    transcribe_queue.put((audio.copy(), audio_duration))

except KeyboardInterrupt:
    print("\n👋 Stopped")
