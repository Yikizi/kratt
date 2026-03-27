#!/usr/bin/python3
"""Show a large fullscreen overlay when a DETECTED line appears in a log file."""

from __future__ import annotations

import argparse
import os
import re
import sys
import tkinter as tk
from pathlib import Path
from typing import Optional


DETECTED_RE = re.compile(
    r">>> DETECTED (?P<name>.+?)! \(prob=(?P<prob>\d+\.\d+), count=(?P<count>\d+)\) <<<"
)


class OverlayApp:
    def __init__(self, root: tk.Tk, log_file: Path, title_text: str, hide_after_ms: int):
        self.root = root
        self.log_file = log_file
        self.title_text = title_text
        self.hide_after_ms = hide_after_ms
        self.file_handle: Optional[object] = None
        self.file_inode: Optional[int] = None
        self.hide_job: Optional[str] = None

        self.root.withdraw()
        self.root.title("Kratt Detection Overlay")
        self.root.bind("<Escape>", self.quit_app)
        self.root.bind("<q>", self.quit_app)

        self.window = tk.Toplevel(self.root)
        self.window.withdraw()
        self.window.configure(bg="#08131f")
        self.window.attributes("-fullscreen", True)
        self.window.attributes("-topmost", True)
        self.window.bind("<Escape>", self.quit_app)
        self.window.bind("<q>", self.quit_app)

        container = tk.Frame(self.window, bg="#08131f")
        container.pack(expand=True, fill="both")

        self.label = tk.Label(
            container,
            text=self.title_text,
            fg="#f8fafc",
            bg="#08131f",
            font=("Helvetica", 72, "bold"),
            wraplength=1400,
            justify="center",
        )
        self.label.pack(expand=True)

        self.sub_label = tk.Label(
            container,
            text="",
            fg="#7dd3fc",
            bg="#08131f",
            font=("Helvetica", 28, "bold"),
            justify="center",
        )
        self.sub_label.pack(pady=(0, 80))

        self.status = tk.Label(
            container,
            text=f"Watching {self.log_file}  |  Esc to exit",
            fg="#94a3b8",
            bg="#08131f",
            font=("Helvetica", 16),
            justify="center",
        )
        self.status.pack(pady=(0, 24))

    def quit_app(self, _event=None):
        if self.file_handle is not None:
            self.file_handle.close()
        self.root.quit()

    def open_log(self):
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.file_handle = open(self.log_file, "r", encoding="utf-8", errors="replace")
        stat = os.fstat(self.file_handle.fileno())
        self.file_inode = stat.st_ino
        self.file_handle.seek(0, os.SEEK_END)

    def ensure_log_open(self):
        if self.file_handle is None:
            if self.log_file.exists():
                self.open_log()
            return

        try:
            current_inode = self.log_file.stat().st_ino
        except FileNotFoundError:
            return

        if current_inode != self.file_inode:
            self.file_handle.close()
            self.open_log()

    def show_detection(self, line: str):
        match = DETECTED_RE.search(line)
        if match:
            wake_name = match.group("name")
            probability = match.group("prob")
            count = match.group("count")
            subtitle = f"{wake_name}  |  p={probability}  |  count={count}"
        else:
            subtitle = line.strip()

        self.label.config(text=self.title_text)
        self.sub_label.config(text=subtitle)
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()

        if self.hide_job is not None:
            self.root.after_cancel(self.hide_job)
        self.hide_job = self.root.after(self.hide_after_ms, self.window.withdraw)

    def poll(self):
        self.ensure_log_open()
        if self.file_handle is not None:
            while True:
                line = self.file_handle.readline()
                if not line:
                    break
                if ">>> DETECTED " in line:
                    self.show_detection(line)
        self.root.after(100, self.poll)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--log-file",
        default="/Users/mattias/kratt/output/demo-logs/live_test_latest.log",
        help="Log file to follow.",
    )
    parser.add_argument(
        "--text",
        default="KRATT KUULIS",
        help="Main fullscreen message shown on detection.",
    )
    parser.add_argument(
        "--hide-after",
        type=float,
        default=2.5,
        help="Seconds to keep the overlay visible after a detection.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    root = tk.Tk()
    app = OverlayApp(
        root=root,
        log_file=Path(args.log_file).expanduser(),
        title_text=args.text,
        hide_after_ms=int(args.hide_after * 1000),
    )
    app.poll()
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
