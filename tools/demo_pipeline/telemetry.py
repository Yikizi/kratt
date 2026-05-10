from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.demo_pipeline.paths import STT_MODEL_DIR

class InteractionLogger:
    """Append-only JSONL logger for one user testing session."""

    def __init__(
        self,
        enabled: bool,
        participant_id: str,
        log_dir: Path,
        llm_model: str,
        wake_models: list[str],
        wake_threshold: float,
    ):
        self.enabled = enabled
        self.participant_id = participant_id
        self.session_id = uuid.uuid4().hex[:8]
        self.session_start = datetime.now(timezone.utc).isoformat()
        self.llm_model = llm_model
        self.wake_threshold = wake_threshold
        self._interaction_seq = 0
        self._current_task: str | None = None

        if not enabled:
            self.path = None
            return

        log_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.path = log_dir / f"{participant_id}_{ts}_{self.session_id}.jsonl"

        self._write(
            {
                "type": "session_start",
                "session_id": self.session_id,
                "participant_id": participant_id,
                "timestamp": self.session_start,
                "llm_model": llm_model,
                "wake_threshold": wake_threshold,
                "wakeword_models": wake_models,
                "stt_model": STT_MODEL_DIR.name,
                "host": os.uname().nodename,
            }
        )
        print(f"  Logging to {self.path.name}")

    def set_task(self, task_id: str | None):
        self._current_task = task_id
        if self.enabled and task_id:
            self._write(
                {
                    "type": "task_change",
                    "task_id": task_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

    def log_interaction(self, record: dict):
        if not self.enabled:
            return
        self._interaction_seq += 1
        record = {
            "type": "interaction",
            "session_id": self.session_id,
            "participant_id": self.participant_id,
            "task_id": self._current_task,
            "seq": self._interaction_seq,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **record,
        }
        self._write(record)

    def _write(self, record: dict):
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def close(self):
        if not self.enabled:
            return
        self._write(
            {
                "type": "session_end",
                "session_id": self.session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "interaction_count": self._interaction_seq,
            }
        )


class StepTimer:
    """Collect wall-clock + monotonic timestamps for demo latency debugging."""

    def __init__(self, label: str, log_fn=None):
        self.label = label
        self.log_fn = log_fn
        self.started_mono = time.monotonic()
        self.last_mono = self.started_mono
        self.events: list[dict[str, Any]] = []
        self.mark("start")

    @staticmethod
    def _ts() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

    def mark(self, step: str, note: str | None = None) -> None:
        now = time.monotonic()
        event = {
            "step": step,
            "timestamp": self._ts(),
            "since_start_ms": int((now - self.started_mono) * 1000),
            "delta_ms": int((now - self.last_mono) * 1000),
            **({"note": note} if note else {}),
        }
        self.events.append(event)
        self.last_mono = now
        if self.log_fn:
            self._log_event(self.log_fn, event)

    def elapsed_ms(self) -> int:
        return int((time.monotonic() - self.started_mono) * 1000)

    def as_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "total_ms": self.elapsed_ms(),
            "events": self.events,
        }

    @staticmethod
    def _log_event(log_fn, event: dict[str, Any]) -> None:
        note = f" — {event['note']}" if event.get("note") else ""
        log_fn(
            "  [timing] "
            f"{event['timestamp']} "
            f"+{event['since_start_ms']:>5}ms "
            f"Δ{event['delta_ms']:>5}ms "
            f"{event['step']}{note}"
        )

    def log(self, log_fn, title: str | None = None) -> None:
        log_fn(f"  [timing] {title or self.label}: total={self.elapsed_ms()}ms")
        if self.log_fn is None:
            for event in self.events:
                self._log_event(log_fn, event)
