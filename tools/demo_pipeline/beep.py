from __future__ import annotations

import subprocess
import threading


def play_wake_beep(*, enabled: bool = True) -> None:
    """Play a short non-blocking readiness beep after wake detection."""
    if not enabled:
        return

    def _run() -> None:
        # macOS built-in sound; very short and does not need TTS server.
        subprocess.run(
            ["afplay", "/System/Library/Sounds/Glass.aiff"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    threading.Thread(target=_run, name="kratt-wake-beep", daemon=True).start()
