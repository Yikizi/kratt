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
                        await self._send_empty_audio()
                        return True

                    wav_data = await resp.read()
        except Exception:
            _LOGGER.exception("Failed to call Neurokõne API")
            await self._send_empty_audio()
            return True

        converted = self._wav_to_pcm16_and_rate(wav_data)
        if converted is None:
            await self._send_empty_audio()
            return True

        pcm_audio, source_rate = converted
        pcm_audio = self._resample(pcm_audio, source_rate, 16000)

        rate = 16000
        width = 2  # 16-bit
        channels = 1

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
        return True

    async def _send_empty_audio(self) -> None:
        """Send a well-formed empty audio response so Wyoming clients do not hang."""
        await self.write_event(AudioStart(rate=16000, width=2, channels=1).event())
        await self.write_event(AudioStop().event())

    @staticmethod
    def _wav_to_pcm16_and_rate(wav_data: bytes) -> tuple[bytes, int] | None:
        """Convert mono/stereo PCM16 or float32 WAV bytes to mono PCM16 + sample rate."""
        try:
            if len(wav_data) < 12 or wav_data[:4] != b"RIFF" or wav_data[8:12] != b"WAVE":
                _LOGGER.error("Unexpected response: not a RIFF/WAVE file")
                return None

            pos = 12  # skip RIFF header
            data_bytes = b""
            fmt_tag = 0
            channels = 0
            sample_rate = 0
            bits_per_sample = 0

            while pos + 8 <= len(wav_data):
                chunk_id = wav_data[pos : pos + 4]
                chunk_size = struct.unpack_from("<I", wav_data, pos + 4)[0]
                pos += 8
                chunk = wav_data[pos : pos + chunk_size]
                if chunk_id == b"fmt " and len(chunk) >= 16:
                    fmt_tag, channels, sample_rate, _byte_rate, _block_align, bits_per_sample = struct.unpack_from(
                        "<HHIIHH", chunk, 0
                    )
                elif chunk_id == b"data":
                    data_bytes = chunk
                pos += chunk_size
                # Align to even boundary
                if chunk_size % 2:
                    pos += 1

            if not data_bytes or not sample_rate or channels < 1:
                _LOGGER.error("Incomplete WAV response from Neurokõne")
                return None

            if fmt_tag == 1 and bits_per_sample == 16:
                sample_count = len(data_bytes) // 2
                samples = struct.unpack(f"<{sample_count}h", data_bytes)
                if channels > 1:
                    samples = samples[0::channels]
                return struct.pack(f"<{len(samples)}h", *samples), sample_rate

            if fmt_tag == 3 and bits_per_sample == 32:
                sample_count = len(data_bytes) // 4
                float_samples = struct.unpack(f"<{sample_count}f", data_bytes)
                if channels > 1:
                    float_samples = float_samples[0::channels]
                pcm_samples = []
                for sample in float_samples:
                    sample = max(-1.0, min(1.0, sample))
                    pcm_samples.append(int(sample * 32767))
                return struct.pack(f"<{len(pcm_samples)}h", *pcm_samples), sample_rate

            _LOGGER.error(
                "Unsupported WAV format from Neurokõne: fmt=%s bits=%s channels=%s rate=%s",
                fmt_tag,
                bits_per_sample,
                channels,
                sample_rate,
            )
            return None
        except Exception:
            _LOGGER.exception("Failed to convert WAV to PCM16")
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
