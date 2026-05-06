"""Wyoming protocol TTS server wrapping Tartu Neurokõne API."""

import argparse
import asyncio
import io
import logging
import struct
import wave

import aiohttp
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event
from wyoming.info import Attribution, Describe, Info, TtsProgram, TtsVoice
from wyoming.server import AsyncEventHandler, AsyncServer
from wyoming.tts import Synthesize

_LOGGER = logging.getLogger(__name__)

NEUROKONE_API = "https://api.tartunlp.ai/text-to-speech/v2"

VOICES = [
    ("mari", "Female"),
    ("albert", "Male"),
    ("indrek", "Male"),
    ("kalev", "Male"),
    ("kylli", "Female"),
    ("lee", "Female"),
    ("liivika", "Female"),
    ("luukas", "Male"),
    ("meelis", "Male"),
    ("peeter", "Male"),
    ("tambet", "Male"),
    ("vesta", "Female"),
]


def get_info(default_voice: str) -> Info:
    attribution = Attribution(
        name="TartuNLP / University of Tartu",
        url="https://neurokone.ee",
    )
    voices = []
    for name, gender in VOICES:
        voices.append(
            TtsVoice(
                name=name,
                description=f"{name.capitalize()} ({gender})",
                attribution=attribution,
                version="3.0.1",
                languages=["et"],
                installed=True,
            )
        )
    return Info(
        tts=[
            TtsProgram(
                name="neurokone",
                description="Tartu Neurokõne - Estonian Neural TTS",
                attribution=Attribution(
                    name="TartuNLP / University of Tartu",
                    url="https://neurokone.ee",
                ),
                installed=True,
                version="3.0.1",
                voices=voices,
            )
        ]
    )


class NeurokoneEventHandler(AsyncEventHandler):
    def __init__(
        self,
        wyoming_info: Info,
        cli_args: argparse.Namespace,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.wyoming_info = wyoming_info
        self.cli_args = cli_args

    async def handle_event(self, event: Event) -> bool:
        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info.event())
            return True

        if not Synthesize.is_type(event.type):
            _LOGGER.debug("Unexpected event: %s", event.type)
            return True

        synthesize = Synthesize.from_event(event)
        text = synthesize.text
        voice = synthesize.voice
        if not voice or not voice.name:
            voice_name = self.cli_args.voice
        else:
            voice_name = voice.name

        _LOGGER.info("Synthesizing: '%s' with voice '%s'", text, voice_name)

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "text": text,
                    "speaker": voice_name,
                    "speed": self.cli_args.speed,
                }
                async with session.post(
                    NEUROKONE_API,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status != 200:
                        _LOGGER.error(
                            "Neurokõne API error: %s %s",
                            resp.status,
                            await resp.text(),
                        )
                        return True

                    wav_data = await resp.read()
        except Exception:
            _LOGGER.exception("Failed to call Neurokõne API")
            return True

        # Neurokõne returns 32-bit IEEE float WAV at 22050 Hz.
        # Convert to 16-bit PCM and resample to 16000 Hz for ESP compatibility.
        pcm_audio = self._float_wav_to_pcm16(wav_data)
        if pcm_audio is None:
            return True

        # Resample 22050 → 16000 Hz
        pcm_audio = self._resample(pcm_audio, 22050, 16000)

        rate = 16000
        width = 2  # 16-bit
        channels = 1
        total_samples = len(pcm_audio) // width

        # Send AudioStart with total sample count so HA knows stream length
        await self.write_event(
            AudioStart(rate=rate, width=width, channels=channels).event()
        )

        # Send in 100ms chunks
        chunk_bytes = (rate // 10) * width * channels
        for i in range(0, len(pcm_audio), chunk_bytes):
            chunk = pcm_audio[i : i + chunk_bytes]
            await self.write_event(
                AudioChunk(
                    audio=chunk,
                    rate=rate,
                    width=width,
                    channels=channels,
                ).event()
            )

        await self.write_event(AudioStop().event())
        _LOGGER.info("Synthesis complete")

    @staticmethod
    def _float_wav_to_pcm16(wav_data: bytes) -> bytes | None:
        """Convert 32-bit float WAV to 16-bit PCM."""
        # Manually parse WAV since Python's wave module doesn't support float
        try:
            pos = 12  # skip RIFF header
            data_bytes = b""
            fmt_tag = 0
            while pos < len(wav_data):
                chunk_id = wav_data[pos : pos + 4]
                chunk_size = struct.unpack_from("<I", wav_data, pos + 4)[0]
                pos += 8
                if chunk_id == b"fmt ":
                    fmt_tag = struct.unpack_from("<H", wav_data, pos)[0]
                elif chunk_id == b"data":
                    data_bytes = wav_data[pos : pos + chunk_size]
                pos += chunk_size
                # Align to even boundary
                if chunk_size % 2:
                    pos += 1

            if fmt_tag != 3 or not data_bytes:
                _LOGGER.error("Unexpected WAV format: %d", fmt_tag)
                return None

            # Convert float32 samples to int16
            num_samples = len(data_bytes) // 4
            float_samples = struct.unpack(f"<{num_samples}f", data_bytes)
            pcm_samples = []
            for s in float_samples:
                # Clamp to [-1.0, 1.0] then scale to int16
                s = max(-1.0, min(1.0, s))
                pcm_samples.append(int(s * 32767))
            return struct.pack(f"<{num_samples}h", *pcm_samples)
        except Exception:
            _LOGGER.exception("Failed to convert float WAV to PCM")
            return None

    @staticmethod
    def _resample(pcm_data: bytes, src_rate: int, dst_rate: int) -> bytes:
        """Resample 16-bit PCM audio using linear interpolation."""
        if src_rate == dst_rate:
            return pcm_data
        num_samples = len(pcm_data) // 2
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
        return struct.pack(f"<{out_len}h", *dst)
        return True


async def main() -> None:
    parser = argparse.ArgumentParser(description="Wyoming Neurokõne TTS Server")
    parser.add_argument(
        "--uri",
        default="tcp://0.0.0.0:10301",
        help="Wyoming server URI (default: tcp://0.0.0.0:10301)",
    )
    parser.add_argument(
        "--voice",
        default="mari",
        help="Default voice (default: mari)",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Speech speed multiplier 0.5-2.0 (default: 1.0)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    )

    wyoming_info = get_info(args.voice)

    _LOGGER.info(
        "Starting Wyoming Neurokõne TTS server on %s (voice: %s, speed: %.1f)",
        args.uri,
        args.voice,
        args.speed,
    )

    server = AsyncServer.from_uri(args.uri)
    await server.run(
        partial(NeurokoneEventHandler, wyoming_info, args)
    )


from functools import partial

if __name__ == "__main__":
    asyncio.run(main())
