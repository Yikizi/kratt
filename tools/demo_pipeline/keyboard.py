from __future__ import annotations

import os
import select
import sys
import termios
import threading
import tty


class TerminalKeyOverride:
    """Tiny cbreak-mode key listener for live-demo emergency overrides.

    The listener is intentionally active only while a trigger is armed. This
    prevents a stale Space press from cancelling the next wake-word hit.
    """

    def __init__(self, *, key: bytes = b" ", enabled: bool = True):
        self.key = key
        self.enabled = enabled
        self.available = False
        self.cancel_event = threading.Event()
        self._active = threading.Event()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._fd: int | None = None
        self._old_attrs = None

    def start(self) -> bool:
        if not self.enabled or not sys.stdin.isatty():
            return False
        try:
            self._fd = sys.stdin.fileno()
            self._old_attrs = termios.tcgetattr(self._fd)
            tty.setcbreak(self._fd)
        except Exception:
            self._fd = None
            self._old_attrs = None
            return False

        self.available = True
        self._thread = threading.Thread(
            target=self._read_loop,
            name="kratt-key-override",
            daemon=True,
        )
        self._thread.start()
        return True

    def arm(self) -> None:
        if not self.available:
            return
        self.cancel_event.clear()
        self._active.set()

    def disarm(self) -> None:
        self._active.clear()
        self.cancel_event.clear()

    def consume(self) -> bool:
        if not self.available:
            return False
        triggered = self.cancel_event.is_set()
        self._active.clear()
        self.cancel_event.clear()
        return triggered

    def stop(self) -> None:
        self._stop.set()
        self._active.clear()
        if self._fd is not None and self._old_attrs is not None:
            try:
                termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old_attrs)
            except Exception:
                pass
        if self._thread is not None:
            self._thread.join(timeout=0.2)
        self.available = False

    def _read_loop(self) -> None:
        assert self._fd is not None
        while not self._stop.is_set():
            try:
                ready, _, _ = select.select([self._fd], [], [], 0.1)
            except (OSError, ValueError):
                return
            if not ready:
                continue
            try:
                ch = os.read(self._fd, 1)
            except OSError:
                return
            if ch == self.key and self._active.is_set():
                self.cancel_event.set()
