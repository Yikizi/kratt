#!/usr/bin/env bash
# Long-running scheduler entrypoint for tmux/launchd.
# Runs thesis automation jobs serially; see bin/scheduler.py.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$(cd "$HERE/../.." && pwd)"
exec /usr/bin/env python3 "$HERE/bin/scheduler.py" "$@"
