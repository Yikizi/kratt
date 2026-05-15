from __future__ import annotations

import os
import select
import signal
import sys
import termios
import threading
import tty


class TerminalKeyOverride:
    """Tiny cbreak-mode key listener for live-demo emergency overrides.

    Space is an armed false-trigger reset key after an accidental wake. Esc is
    a hard reset/abort. Q / Ctrl-C / Ctrl-D request demo shutdown. A separate
    key can be used as a global mic-mute toggle while teaching a participant how
    to say the wake word.
    Terminal input cannot reliably detect key release, so the mute key is a
    toggle, not a hold-to-release chord.
    """

    def __init__(
        self,
        *,
        key: bytes = b" ",
        enabled: bool = True,
        mute_key: bytes | None = b"m",
    ):
        self.key = key
        self.mute_key = mute_key
        self.enabled = enabled
        self.available = False
        self.cancel_event = threading.Event()
        self.abort_event = threading.Event()
        self.quit_event = threading.Event()
        self.stop_tts_event = threading.Event()
        self.stop_effect_event = threading.Event()
        self.help_event = threading.Event()
        self.missed_wake_event = threading.Event()
        self.recording_toggle_event = threading.Event()
        self.participant_boundary_event = threading.Event()
        self.muted_event = threading.Event()
        self.mute_changed_event = threading.Event()
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
        self.abort_event.clear()
        self._active.set()

    def disarm(self) -> None:
        self._active.clear()
        self.cancel_event.clear()
        self.abort_event.clear()

    def consume(self) -> bool:
        """Consume the Space false-trigger reset only.

        Esc is handled separately via clear_abort() so an operator hard reset is
        not mislabeled as a wake-word false accept.
        """
        if not self.available:
            return False
        triggered = self.cancel_event.is_set()
        self._active.clear()
        self.cancel_event.clear()
        return triggered

    def is_muted(self) -> bool:
        return self.muted_event.is_set()

    def toggle_mute(self) -> bool:
        if self.muted_event.is_set():
            self.muted_event.clear()
        else:
            self.muted_event.set()
        self.mute_changed_event.set()
        return self.muted_event.is_set()

    def clear_mute_changed(self) -> bool:
        changed = self.mute_changed_event.is_set()
        self.mute_changed_event.clear()
        return changed

    def request_quit(self) -> None:
        """Request a full demo shutdown and unblock current audio/TTS work."""
        self.quit_event.set()
        self.abort_event.set()
        self.cancel_event.set()
        self.stop_tts_event.set()
        self.stop_effect_event.set()
        self._active.clear()

    def consume_quit(self) -> bool:
        triggered = self.quit_event.is_set()
        self.quit_event.clear()
        return triggered

    def consume_stop_tts(self) -> bool:
        triggered = self.stop_tts_event.is_set()
        self.stop_tts_event.clear()
        return triggered

    def consume_stop_effect(self) -> bool:
        triggered = self.stop_effect_event.is_set()
        self.stop_effect_event.clear()
        return triggered

    def consume_help(self) -> bool:
        triggered = self.help_event.is_set()
        self.help_event.clear()
        return triggered

    def consume_missed_wake(self) -> bool:
        triggered = self.missed_wake_event.is_set()
        self.missed_wake_event.clear()
        return triggered

    def consume_recording_toggle(self) -> bool:
        triggered = self.recording_toggle_event.is_set()
        self.recording_toggle_event.clear()
        return triggered

    def consume_participant_boundary(self) -> bool:
        triggered = self.participant_boundary_event.is_set()
        self.participant_boundary_event.clear()
        return triggered

    def clear_abort(self) -> bool:
        triggered = self.abort_event.is_set()
        if triggered:
            self._active.clear()
            self.cancel_event.clear()
        self.abort_event.clear()
        return triggered

    def _restore_terminal(self) -> None:
        if self._fd is not None and self._old_attrs is not None:
            try:
                termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old_attrs)
            except Exception:
                pass

    def stop(self) -> None:
        self._stop.set()
        self._active.clear()
        self._restore_terminal()
        if self._thread is not None and self._thread is not threading.current_thread():
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
            lower = ch.lower()
            if ch == b"\x03":
                # In cbreak/raw terminal modes Ctrl-C can be consumed here
                # instead of becoming a normal SIGINT. Make it a hard emergency
                # exit so a PortAudio/LLM hang cannot trap the operator.
                self.request_quit()
                self._restore_terminal()
                try:
                    os.killpg(os.getpgrp(), signal.SIGTERM)
                except Exception:
                    os.kill(os.getpid(), signal.SIGTERM)
                return
            if ch == b"\x04" or lower == b"q":
                self.request_quit()
            elif ch == b"\x1b":
                self.abort_event.set()
                self.cancel_event.set()
            elif self.mute_key is not None and lower == self.mute_key.lower():
                self.toggle_mute()
            elif lower == b"s":
                self.stop_tts_event.set()
            elif lower == b"e":
                self.stop_effect_event.set()
            elif lower == b"h":
                self.help_event.set()
            elif lower == b"w" and not self._active.is_set():
                self.missed_wake_event.set()
            elif lower == b"r":
                self.recording_toggle_event.set()
            elif lower == b"n" and not self._active.is_set():
                self.participant_boundary_event.set()
            elif ch == self.key and self._active.is_set():
                self.cancel_event.set()
