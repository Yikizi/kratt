#!/usr/bin/env bash
# Thin wrapper so cron/launchd can call one command.
# Delegates to the Python runner.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec /usr/bin/env python3 "$HERE/bin/runner.py" hourly "$@"
