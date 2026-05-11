#!/usr/bin/env python3
"""Tiny localhost bridge for Android Dev Voice -> kratt dev-voice send."""
from __future__ import annotations

import argparse
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
KRATT = REPO_ROOT / "cli" / "kratt"


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/dispatch":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        text = self.rfile.read(length).decode("utf-8", "replace").strip()
        if not text:
            self.send_error(400, "empty transcript")
            return
        print(f"[dev-voice-bridge] dispatch: {text}", flush=True)
        try:
            subprocess.run([str(KRATT), "dev-voice", "send", text], cwd=REPO_ROOT, check=True)
        except subprocess.CalledProcessError as exc:
            self.send_error(500, f"dispatch failed: {exc}")
            return
        self.send_response(204)
        self.end_headers()

    def log_message(self, fmt, *args):
        print(f"[dev-voice-bridge] {self.address_string()} - {fmt % args}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"[dev-voice-bridge] listening on http://{args.host}:{args.port}/dispatch", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
