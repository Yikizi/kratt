"""Wyoming protocol TTS server for local TartuNLP text-to-speech-worker.

This intentionally does not call the public Neurokõne API. It loads the
TartuNLP multispeaker model inside the container and synthesizes locally.

Upstream: https://github.com/TartuNLP/text-to-speech-worker
Pinned base image/release in Dockerfile: v3.1.0
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import struct
import wave
from pathlib import Path

from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event
from wyoming.info import Attribution, Describe, Info, TtsProgram, TtsVoice
from wyoming.server import AsyncEventHandler, AsyncServer
from wyoming.tts import Synthesize

from tts_worker.config import read_model_config
from tts_worker.schemas import Request as TtsRequest
from tts_worker.synthesizer import Synthesizer

_LOGGER = logging.getLogger(__name__)

VOICES = [
    ("albert", "Male"),
    ("indrek", "Male"),
    ("kalev", "Male"),
    ("kylli", "Female"),
    ("liivika", "Female"),
    ("mari", "Female"),
    ("meelis", "Male"),
    ("peeter", "Male"),
    ("tambet", "Male"),
    ("vesta", "Female"),
]


def get_info() -> Info:
    attribution = Attribution(
        name="TartuNLP / University of Tartu",
        url="https://github.com/TartuNLP/text-to-speech-worker",
    )
    voices = [
        TtsVoice(
            name=name,
            description=f"{name.capitalize()} ({gender})",
            attribution=attribution,
            version="3.1.0",
            languages=["et"],
            installed=True,
        )
        for name, gender in VOICES
    ]
    return Info(
        tts=[
            TtsProgram(
                name="tartunlp-local-tts",
                description="Local TartuNLP Estonian neural TTS (text-to-speech-worker)",
                attribution=attribution,
                installed=True,
                version="3.1.0",
                voices=voices,
            )
        ]
    )


class LocalTartuNlpTtsHandler(AsyncEventHandler):
    def __init__(
        self,
        wyoming_info: Info,
        synthesizer: Synthesizer,
        default_voice: str,
        default_speed: float,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.wyoming_info = wyoming_info
        self.synthesizer = synthesizer
        self.default_voice = default_voice
        self.default_speed = default_speed
        self.voices = set(self.synthesizer.speakers.keys())

    async def handle_event(self, event: Event) -> bool:
        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info.event())
            return True

        if not Synthesize.is_type(event.type):
            _LOGGER.debug("Unexpected event: %s", event.type)
            return True

        synthesize = Synthesize.from_event(event)
        text = synthesize.text.strip()
        voice_name = self.default_voice
        if synthesize.voice and synthesize.voice.name:
            voice_name = synthesize.voice.name

        if voice_name not in self.voices:
            _LOGGER.warning(
                "Unknown TTS voice '%s', falling back to '%s'", voice_name, self.default_voice
            )
            voice_name = self.default_voice

        if not text:
            await self._send_empty_audio()
            return True

        _LOGGER.info("Synthesizing locally: %r with voice=%s", text, voice_name)
        try:
            response = await asyncio.to_thread(
                self.synthesizer.process_request,
                TtsRequest(text=text, speaker=voice_name, speed=self.default_speed),
            )
            if response.status_code != 200 or response.content is None:
                _LOGGER.error("TartuNLP TTS synthesis failed: %s", response.status)
                await self._send_empty_audio()
                return True
            wav_data = response.content.audio
            if isinstance(wav_data, str):
                wav_data = wav_data.encode("utf-8")
        except Exception:
            _LOGGER.exception("Local TartuNLP synthesis failed")
            await self._send_empty_audio()
            return True

        converted = self._wav_to_pcm16_and_rate(wav_data)
        if converted is None:
            await self._send_empty_audio()
            return True

        pcm_audio, source_rate = converted
        pcm_audio = self._resample(pcm_audio, source_rate, 16000)
        await self._send_pcm(pcm_audio, rate=16000)
        _LOGGER.info("Synthesis complete")
        return True

    async def _send_empty_audio(self) -> None:
        await self.write_event(AudioStart(rate=16000, width=2, channels=1).event())
        await self.write_event(AudioStop().event())

    async def _send_pcm(self, pcm_audio: bytes, rate: int) -> None:
        width = 2
        channels = 1
        await self.write_event(AudioStart(rate=rate, width=width, channels=channels).event())
        chunk_bytes = (rate // 10) * width * channels
        for i in range(0, len(pcm_audio), chunk_bytes):
            await self.write_event(
                AudioChunk(
                    audio=pcm_audio[i : i + chunk_bytes],
                    rate=rate,
                    width=width,
                    channels=channels,
                ).event()
            )
        await self.write_event(AudioStop().event())

    @staticmethod
    def _wav_to_pcm16_and_rate(wav_data: bytes) -> tuple[bytes, int] | None:
        try:
            with wave.open(__import__("io").BytesIO(wav_data), "rb") as wav:
                channels = wav.getnchannels()
                sample_rate = wav.getframerate()
                sample_width = wav.getsampwidth()
                frames = wav.readframes(wav.getnframes())

            if channels < 1 or not frames:
                _LOGGER.error("Incomplete WAV from local TTS")
                return None

            if sample_width == 2:
                sample_count = len(frames) // 2
                samples = struct.unpack(f"<{sample_count}h", frames)
                if channels > 1:
                    samples = samples[0::channels]
                return struct.pack(f"<{len(samples)}h", *samples), sample_rate

            if sample_width == 4:
                sample_count = len(frames) // 4
                float_samples = struct.unpack(f"<{sample_count}f", frames)
                if channels > 1:
                    float_samples = float_samples[0::channels]
                pcm_samples = [int(max(-1.0, min(1.0, s)) * 32767) for s in float_samples]
                return struct.pack(f"<{len(pcm_samples)}h", *pcm_samples), sample_rate

            _LOGGER.error("Unsupported WAV sample width from local TTS: %s", sample_width)
            return None
        except Exception:
            _LOGGER.exception("Failed to convert local TTS WAV to PCM16")
            return None

    @staticmethod
    def _resample(pcm_data: bytes, src_rate: int, dst_rate: int) -> bytes:
        if src_rate == dst_rate:
            return pcm_data
        num_samples = len(pcm_data) // 2
        if num_samples == 0:
            return b""
        src = struct.unpack(f"<{num_samples}h", pcm_data)
        ratio = dst_rate / src_rate
        out_len = int(num_samples * ratio)
        dst = []
        for i in range(out_len):
            pos = i / ratio
            idx = int(pos)
            if idx >= num_samples - 1:
                dst.append(src[-1])
            else:
                frac = pos - idx
                dst.append(int(src[idx] * (1 - frac) + src[idx + 1] * frac))
        return struct.pack(f"<{len(dst)}h", *dst)


def load_synthesizer(args: argparse.Namespace) -> Synthesizer:
    model_config = read_model_config(args.model_config, args.model_name)
    model_config.model_path = str(Path(args.model_dir).resolve())
    _LOGGER.info("Loading local TartuNLP TTS model from %s", model_config.model_path)
    return Synthesizer(model_config, max_input_length=args.max_input_length)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Local TartuNLP Wyoming TTS Server")
    parser.add_argument("--uri", default="tcp://0.0.0.0:10301")
    parser.add_argument("--model-config", default="/app/config/config.yaml")
    parser.add_argument("--model-name", default="multispeaker")
    parser.add_argument("--model-dir", default="/data/models/multispeaker")
    parser.add_argument("--voice", default="meelis")
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--max-input-length", type=int, default=500)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    synthesizer = load_synthesizer(args)
    wyoming_info = get_info()

    server = AsyncServer.from_uri(args.uri)
    _LOGGER.info("Starting local TartuNLP Wyoming TTS server on %s", args.uri)
    await server.run(
        lambda *a, **kw: LocalTartuNlpTtsHandler(
            wyoming_info,
            synthesizer,
            args.voice,
            args.speed,
            *a,
            **kw,
        )
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
