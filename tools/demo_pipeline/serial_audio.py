from __future__ import annotations

import glob
import queue
import struct
import threading
import time
from pathlib import Path
from typing import Any

import numpy as np

SAMPLE_RATE = 16000
SERIAL_MAGIC = b"KPCM"
SERIAL_HEADER = struct.Struct("<4sHHIIIHH")
SERIAL_VERSION = 1
DEFAULT_SERIAL_BAUD = 921600
MAX_PAYLOAD_BYTES = 4096


class KorvoSerialAudioSource:
    """Read 16 kHz mono PCM frames from the Korvo-2 serial streamer firmware.

    The firmware emits framed binary packets so boot logs or occasional text logs
    can be skipped safely by scanning for the KPCM magic bytes.
    """

    def __init__(
        self,
        *,
        port: str | None = None,
        baud: int = DEFAULT_SERIAL_BAUD,
        queue_frames: int = 256,
        expected_sample_rate: int = SAMPLE_RATE,
        gain: float = 1.0,
        channel: str = "mic1",
    ):
        channel = channel.strip().lower()
        if channel not in {"mic1", "mic2", "mix"}:
            raise ValueError(f"Unsupported Korvo serial channel: {channel}")
        self.port = port or find_default_serial_port()
        self.baud = baud
        self.expected_sample_rate = expected_sample_rate
        self.gain = float(gain)
        self.channel = channel
        self._queue: queue.Queue[bytes] = queue.Queue(maxsize=queue_frames)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._serial: Any | None = None
        self.frames_received = 0
        self.bytes_received = 0
        self.last_seq: int | None = None
        self.last_frame_mono = 0.0

    def start(self, *, wait_for_frame: bool = True, timeout_s: float = 5.0) -> None:
        if self._thread is not None:
            return
        if not self.port:
            raise RuntimeError("No Korvo serial port found; pass --serial-port /dev/cu.usbserial-...")

        try:
            import serial  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "pyserial is required for --audio-source korvo-serial. "
                "Install it in the project env, e.g. `uv pip install --python .venv/bin/python pyserial`."
            ) from exc

        self._serial = serial.Serial(self.port, self.baud, timeout=0.1, write_timeout=0.5)
        # Avoid keeping the ESP32 in reset on adapters where DTR/RTS are wired.
        try:
            self._serial.setDTR(False)
            self._serial.setRTS(False)
        except Exception:
            pass

        self._stop.clear()
        self._thread = threading.Thread(target=self._reader_loop, name="kratt-korvo-serial-audio", daemon=True)
        self._thread.start()

        if wait_for_frame:
            deadline = time.monotonic() + timeout_s
            while time.monotonic() < deadline:
                if self.frames_received > 0:
                    return
                time.sleep(0.05)
            raise RuntimeError(
                f"No KPCM audio frames received from {self.port} at {self.baud} baud. "
                "Flash/start the Korvo serial streamer firmware first."
            )

    def close(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:
                pass
            self._serial = None

    def clear(self) -> None:
        while True:
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

    def read_pcm_bytes(self, timeout: float = 0.1) -> bytes | None:
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def read_float_chunk(self, timeout: float = 0.1) -> np.ndarray | None:
        payload = self.read_pcm_bytes(timeout=timeout)
        if not payload:
            return None
        pcm = np.frombuffer(payload, dtype="<i2")
        if pcm.size == 0:
            return None
        audio = pcm.astype(np.float32) / 32768.0
        if self.gain != 1.0:
            audio = np.clip(audio * self.gain, -1.0, 1.0)
        return audio

    def _select_mono_payload(self, payload: bytes, channels: int) -> bytes:
        if channels == 1:
            return payload
        pcm = np.frombuffer(payload, dtype="<i2")
        if pcm.size < 2:
            return b""
        frames = pcm.reshape(-1, channels)
        if self.channel == "mic1":
            mono = frames[:, 0]
        elif self.channel == "mic2":
            mono = frames[:, 1]
        else:
            mono = ((frames[:, 0].astype(np.int32) + frames[:, 1].astype(np.int32)) // 2).astype("<i2")
        return np.ascontiguousarray(mono, dtype="<i2").tobytes()

    def _put_payload(self, payload: bytes) -> None:
        if self._queue.full():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                pass
        try:
            self._queue.put_nowait(payload)
        except queue.Full:
            pass

    def _reader_loop(self) -> None:
        assert self._serial is not None
        buf = bytearray()
        while not self._stop.is_set():
            try:
                chunk = self._serial.read(2048)
            except Exception:
                time.sleep(0.05)
                continue
            if chunk:
                buf.extend(chunk)
            else:
                continue

            while True:
                magic_pos = buf.find(SERIAL_MAGIC)
                if magic_pos < 0:
                    # Keep only enough tail bytes to match a split magic on the next read.
                    del buf[:-3]
                    break
                if magic_pos > 0:
                    del buf[:magic_pos]
                if len(buf) < SERIAL_HEADER.size:
                    break

                try:
                    magic, version, header_size, seq, sample_rate, payload_bytes, channels, bits = SERIAL_HEADER.unpack(
                        bytes(buf[: SERIAL_HEADER.size])
                    )
                except struct.error:
                    break

                if (
                    magic != SERIAL_MAGIC
                    or version != SERIAL_VERSION
                    or header_size != SERIAL_HEADER.size
                    or payload_bytes <= 0
                    or payload_bytes > MAX_PAYLOAD_BYTES
                    or channels not in (1, 2)
                    or bits != 16
                    or payload_bytes % (channels * 2) != 0
                ):
                    del buf[:1]
                    continue

                frame_size = header_size + payload_bytes
                if len(buf) < frame_size:
                    break

                payload = bytes(buf[header_size:frame_size])
                del buf[:frame_size]

                if sample_rate != self.expected_sample_rate:
                    # Wrong stream for this demo; skip rather than poisoning STT timing.
                    continue
                mono_payload = self._select_mono_payload(payload, channels)
                if not mono_payload:
                    continue
                self.frames_received += 1
                self.bytes_received += len(mono_payload)
                self.last_seq = seq
                self.last_frame_mono = time.monotonic()
                self._put_payload(mono_payload)


def find_default_serial_port() -> str | None:
    candidates: list[str] = []
    patterns = [
        "/dev/cu.usbserial-*",
        "/dev/cu.SLAB_USBtoUART*",
        "/dev/cu.wchusbserial*",
        "/dev/cu.usbmodem*",
        "/dev/ttyUSB*",
        "/dev/ttyACM*",
    ]
    for pattern in patterns:
        candidates.extend(glob.glob(pattern))
    if not candidates:
        return None
    return sorted(candidates)[0]


def _record_from_source(
    source: KorvoSerialAudioSource,
    *,
    max_seconds: float,
    silence_threshold: float,
    silence_duration: float,
    initial_silence_timeout: float,
    speech_start_grace: float,
    cancel_event: threading.Event | None,
    stt: Any | None = None,
    use_stt_endpoint: bool = False,
) -> tuple[np.ndarray, str, float]:
    source.clear()
    chunks: list[np.ndarray] = []
    pre_voice_energies: list[float] = []
    seen_voice = False
    silent_s = 0.0
    speech_s = 0.0
    audio_elapsed_s = 0.0
    decode_time_s = 0.0

    stream = None
    is_endpoint = None
    if stt is not None:
        stream = stt.recognizer.create_stream()
        is_endpoint = getattr(stt.recognizer, "is_endpoint", None)

    started_wall = time.monotonic()
    deadline = started_wall + max_seconds + 1.0
    while audio_elapsed_s < max_seconds and time.monotonic() < deadline:
        if cancel_event is not None and cancel_event.is_set():
            break
        chunk = source.read_float_chunk(timeout=0.1)
        if chunk is None:
            continue
        if chunk.size == 0:
            continue

        chunks.append(chunk)
        chunk_s = float(chunk.size) / SAMPLE_RATE
        audio_elapsed_s += chunk_s

        energy = float(np.sqrt(np.mean(chunk**2)))
        if not seen_voice:
            pre_voice_energies.append(energy)
            del pre_voice_energies[:-128]
        noise_floor = float(np.median(pre_voice_energies)) if pre_voice_energies else 0.0
        speech_threshold = max(silence_threshold, min(0.018, noise_floor * 2.0))
        is_speech = energy >= speech_threshold
        if is_speech:
            silent_s = 0.0
            speech_s += chunk_s
            if audio_elapsed_s >= speech_start_grace and speech_s >= 0.09:
                seen_voice = True
        else:
            silent_s += chunk_s
            speech_s = 0.0

        if stt is not None and stream is not None:
            t_decode = time.monotonic()
            stream.accept_waveform(SAMPLE_RATE, chunk)
            while stt.recognizer.is_ready(stream):
                stt.recognizer.decode_stream(stream)
            decode_time_s += time.monotonic() - t_decode

        if use_stt_endpoint and seen_voice and callable(is_endpoint) and is_endpoint(stream):
            break
        if seen_voice and silent_s >= silence_duration:
            break
        if not seen_voice and audio_elapsed_s >= initial_silence_timeout:
            break

    if stt is not None and stream is not None and (cancel_event is None or not cancel_event.is_set()):
        t_decode = time.monotonic()
        stream.accept_waveform(SAMPLE_RATE, np.zeros(int(0.15 * SAMPLE_RATE), dtype=np.float32))
        while stt.recognizer.is_ready(stream):
            stt.recognizer.decode_stream(stream)
        decode_time_s += time.monotonic() - t_decode

    audio = np.concatenate(chunks) if chunks else np.array([], dtype=np.float32)
    text = stt.recognizer.get_result(stream).strip() if stt is not None and stream is not None else ""
    return audio, text, decode_time_s


def record_until_silence_from_source(
    source: KorvoSerialAudioSource,
    max_seconds: float = 14.0,
    silence_threshold: float = 0.008,
    silence_duration: float = 1.6,
    initial_silence_timeout: float = 3.0,
    speech_start_grace: float = 0.4,
    cancel_event: threading.Event | None = None,
) -> np.ndarray:
    audio, _, _ = _record_from_source(
        source,
        max_seconds=max_seconds,
        silence_threshold=silence_threshold,
        silence_duration=silence_duration,
        initial_silence_timeout=initial_silence_timeout,
        speech_start_grace=speech_start_grace,
        cancel_event=cancel_event,
        stt=None,
    )
    return audio


def record_and_transcribe_streaming_from_source(
    source: KorvoSerialAudioSource,
    stt: Any,
    max_seconds: float = 14.0,
    silence_threshold: float = 0.008,
    silence_duration: float = 1.6,
    initial_silence_timeout: float = 3.0,
    speech_start_grace: float = 0.4,
    cancel_event: threading.Event | None = None,
    use_stt_endpoint: bool = False,
) -> tuple[np.ndarray, str, float]:
    return _record_from_source(
        source,
        max_seconds=max_seconds,
        silence_threshold=silence_threshold,
        silence_duration=silence_duration,
        initial_silence_timeout=initial_silence_timeout,
        speech_start_grace=speech_start_grace,
        cancel_event=cancel_event,
        stt=stt,
        use_stt_endpoint=use_stt_endpoint,
    )
