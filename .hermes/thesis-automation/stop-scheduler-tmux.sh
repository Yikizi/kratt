#!/usr/bin/env bash
set -euo pipefail
SESSION="${KRATT_SCHEDULER_TMUX_SESSION:-kratt-thesis-scheduler}"
if tmux has-session -t "$SESSION" 2>/dev/null; then
  tmux kill-session -t "$SESSION"
  echo "stopped scheduler tmux session: $SESSION"
else
  echo "scheduler tmux session not running: $SESSION"
fi
