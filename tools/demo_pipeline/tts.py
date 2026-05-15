from __future__ import annotations

import hashlib
import json
import os
import subprocess
import threading
import time
import uuid
from pathlib import Path

import requests

from tools.demo_pipeline.paths import PROJECT_ROOT

TTS_URL = "http://127.0.0.1:5380/synthesize"
TTS_SPEAKER = "meelis"
TTS_SPEED = 1.0

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
        self.session = requests.Session()
        self.cache_dir = PROJECT_ROOT / "output" / "tts-cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._play_proc: subprocess.Popen | None = None
        self._play_lock = threading.Lock()

    def is_available(self) -> bool:
        if self._available is None:
            try:
                r = self.session.get(
                    self.url.replace("/synthesize", "/speakers"), timeout=2
                )
                self._available = r.status_code == 200
            except Exception:
                self._available = False
        return self._available

    def _cache_path(self, text: str) -> Path:
        key = hashlib.sha1(
            json.dumps(
                {
                    "text": text,
                    "speaker": self.speaker,
                    "speed": self.speed,
                    "effects": self.apply_effects,
                },
                ensure_ascii=False,
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()[:16]
        return self.cache_dir / f"{key}.wav"

    def prepare(self, text: str) -> Path | None:
        """Synthesize/cache text without playback."""
        if not text or not self.is_available():
            return None
        out_path = self._cache_path(text)
        if out_path.exists() and out_path.stat().st_size > 0:
            return out_path

        import tempfile

        r = self.session.post(
            self.url,
            json={
                "text": text,
                "speaker": self.speaker,
                "speed": self.speed,
            },
            timeout=30,
        )
        r.raise_for_status()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as raw:
            raw.write(r.content)
            raw_path = raw.name

        try:
            if self.apply_effects:
                tmp_out = str(out_path) + f".{uuid.uuid4().hex}.tmp.wav"
                cmd = ["sox", raw_path, tmp_out] + self.SOX_EFFECTS
                subprocess.run(cmd, check=True, capture_output=True)
                os.replace(tmp_out, out_path)
            else:
                os.replace(raw_path, out_path)
                raw_path = ""
        finally:
            if raw_path and os.path.exists(raw_path):
                os.unlink(raw_path)
        return out_path

    def prepare_common_responses(self) -> None:
        for text in (
            "Tuli on kustutatud.",
            "Tuli põleb.",
            "Värv muudetud.",
            "Heledus muudetud.",
            "Tuli on sinine.",
            "Tuli on punane.",
            "Ma ei saanud käsku täita.",
        ):
            try:
                self.prepare(text)
            except Exception:
                pass

    def stop(self) -> None:
        with self._play_lock:
            proc = self._play_proc
        if proc is not None and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=0.4)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

    def speak(self, text: str, *, stop_event: threading.Event | None = None) -> float:
        """Synthesize/cache and play text. Returns duration in seconds."""
        if not text or not self.is_available():
            return 0.0

        t0 = time.monotonic()
        play_path = self.prepare(text)
        if not play_path:
            return 0.0

        proc = subprocess.Popen(["sox", str(play_path), "-d"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with self._play_lock:
            self._play_proc = proc
        try:
            while proc.poll() is None:
                if stop_event is not None and stop_event.is_set():
                    try:
                        proc.terminate()
                        proc.wait(timeout=0.4)
                    except Exception:
                        try:
                            proc.kill()
                        except Exception:
                            pass
                    break
                time.sleep(0.05)
        finally:
            with self._play_lock:
                if self._play_proc is proc:
                    self._play_proc = None
        return time.monotonic() - t0
