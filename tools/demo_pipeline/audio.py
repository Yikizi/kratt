from __future__ import annotations

import queue
import threading
import time

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000

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


def record_until_silence(
    max_seconds: float = 8.0,
    silence_threshold: float = 0.01,
    silence_duration: float = 1.5,
    initial_silence_timeout: float = 3.0,
    speech_start_grace: float = 0.4,
    cancel_event: threading.Event | None = None,
) -> np.ndarray:
    frame_size = int(SAMPLE_RATE * 0.032)
    chunks = []
    silent_frames = 0
    seen_voice = False
    frames_for_silence = int(silence_duration / 0.032)
    initial_silence_frames = int(initial_silence_timeout / 0.032)
    max_frames = int(max_seconds / 0.032)
    done = threading.Event()

    def callback(indata, frames, time_info, status):
        nonlocal silent_frames, seen_voice
        if cancel_event is not None and cancel_event.is_set():
            done.set()
            return
        chunks.append(indata[:, 0].copy())
        energy = np.sqrt(np.mean(indata**2))
        elapsed_s = len(chunks) * 0.032
        if energy < silence_threshold:
            silent_frames += 1
        else:
            silent_frames = 0
            # Ignore a short post-trigger tail from the wake phrase itself; a
            # user command that starts immediately will still be recorded and
            # marked as speech on subsequent frames.
            if elapsed_s >= speech_start_grace:
                seen_voice = True
        if seen_voice and silent_frames >= frames_for_silence:
            done.set()
        elif not seen_voice and len(chunks) >= initial_silence_frames:
            done.set()
        elif len(chunks) >= max_frames:
            done.set()

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=frame_size,
        callback=callback,
    ):
        deadline = time.monotonic() + max_seconds + 1
        while not done.wait(timeout=0.05):
            if cancel_event is not None and cancel_event.is_set():
                done.set()
                break
            if time.monotonic() >= deadline:
                break

    if not chunks:
        return np.array([], dtype=np.float32)
    return np.concatenate(chunks)


def record_and_transcribe_streaming(
    stt: SpeechRecognizer,
    max_seconds: float = 8.0,
    silence_threshold: float = 0.01,
    silence_duration: float = 1.0,
    initial_silence_timeout: float = 3.0,
    speech_start_grace: float = 0.4,
    cancel_event: threading.Event | None = None,
) -> tuple[np.ndarray, str, float]:
    """Record one utterance while feeding audio into sherpa-onnx online STT.

    The old path waited for VAD to finish, then decoded the whole utterance.
    This keeps the recognizer stream hot during recording, so by the time VAD
    stops we usually already have the transcript. Returns (audio, text,
    stt_decode_cpu_seconds).
    """
    frame_size = int(SAMPLE_RATE * 0.032)
    frames_for_silence = int(silence_duration / 0.032)
    initial_silence_frames = int(initial_silence_timeout / 0.032)
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
            if cancel_event is not None and cancel_event.is_set():
                break
            try:
                chunk = audio_q.get(timeout=0.1)
            except queue.Empty:
                if cancel_event is not None and cancel_event.is_set():
                    break
                if (time.monotonic() - start) >= max_seconds + 0.5:
                    break
                continue

            chunks.append(chunk)
            energy = float(np.sqrt(np.mean(chunk**2)))
            elapsed_s = len(chunks) * 0.032
            if energy < silence_threshold:
                silent_frames += 1
            else:
                silent_frames = 0
                # Ignore a short post-trigger tail from the wake phrase itself;
                # otherwise "Kuule Kratt <pause> command" can endpoint on that
                # tail and return an empty command transcript.
                if elapsed_s >= speech_start_grace:
                    seen_voice = True

            t_decode = time.monotonic()
            stream.accept_waveform(SAMPLE_RATE, chunk)
            while stt.recognizer.is_ready(stream):
                stt.recognizer.decode_stream(stream)
            decode_time_s += time.monotonic() - t_decode

            if seen_voice and callable(is_endpoint) and is_endpoint(stream):
                break
            if seen_voice and silent_frames >= frames_for_silence:
                break
            if not seen_voice and len(chunks) >= initial_silence_frames:
                break

    # Small zero tail flushes the online recognizer without adding user-visible
    # waiting time (we are already outside the input stream). Skip it when the
    # operator cancelled a false trigger; the caller will discard this turn.
    if cancel_event is None or not cancel_event.is_set():
        t_decode = time.monotonic()
        stream.accept_waveform(SAMPLE_RATE, np.zeros(int(0.15 * SAMPLE_RATE), dtype=np.float32))
        while stt.recognizer.is_ready(stream):
            stt.recognizer.decode_stream(stream)
        decode_time_s += time.monotonic() - t_decode

    audio = np.concatenate(chunks) if chunks else np.array([], dtype=np.float32)
    return audio, stt.recognizer.get_result(stream).strip(), decode_time_s
