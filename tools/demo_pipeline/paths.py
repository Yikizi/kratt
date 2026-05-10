from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "wake-word/models"
STT_MODEL_DIR = PROJECT_ROOT / "wake-word/models/kiirkirjutaja-int8"
MOCK_MCP_SERVER = PROJECT_ROOT / "tools/mock-ha-server/server.py"
WIZ_MCP_SERVER = PROJECT_ROOT / "tools/wiz-server/server.py"
WIZ_CLI = PROJECT_ROOT / "tools/wiz-cli/wiz"
LOG_DIR = PROJECT_ROOT / "output/demo-logs"
