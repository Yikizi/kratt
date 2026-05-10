from __future__ import annotations

import json
import select
import subprocess
import sys
from pathlib import Path

class MCPClient:
    def __init__(self, server_path: Path, extra_args: list[str] | None = None, timeout_s: float = 8.0):
        if not server_path.exists():
            raise RuntimeError(f"MCP server not found: {server_path}")
        self.timeout_s = timeout_s
        cmd = [sys.executable, str(server_path)]
        if extra_args:
            cmd.extend(extra_args)
        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            resp = self._send(
                {"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {}}
            )
        except Exception:
            self.close()
            raise
        server_name = (
            resp.get("result", {}).get("serverInfo", {}).get("name", "unknown")
        )
        print(f"  MCP server: {server_name}")

    def _check_alive(self):
        rc = self.proc.poll()
        if rc is not None:
            stderr = self.proc.stderr.read() if self.proc.stderr else ""
            raise RuntimeError(f"MCP server exited with code {rc}\n{stderr}")

    def _send(self, req: dict) -> dict:
        self._check_alive()
        assert self.proc.stdin is not None
        assert self.proc.stdout is not None
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()
        ready, _, _ = select.select([self.proc.stdout], [], [], self.timeout_s)
        if not ready:
            self._check_alive()
            self.close()
            raise TimeoutError(f"MCP server did not respond within {self.timeout_s:.1f}s")
        line = self.proc.stdout.readline()
        if not line:
            self._check_alive()
            return {}
        resp = json.loads(line) if line.strip() else {}
        if "error" in resp:
            raise RuntimeError(resp["error"].get("message", str(resp["error"])))
        return resp

    def execute(self, action: str, args: dict) -> str:
        resp = self._send(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": action, "arguments": args},
            }
        )
        content = resp.get("result", {}).get("content", [{}])
        return content[0].get("text", "") if content else ""

    def close(self):
        try:
            self.proc.terminate()
            self.proc.wait(timeout=3)
        except Exception:
            self.proc.kill()
