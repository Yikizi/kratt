#!/usr/bin/env bash
# Start the Kratt thesis automation scheduler in a detached tmux session.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
SESSION="${KRATT_SCHEDULER_TMUX_SESSION:-kratt-thesis-scheduler}"
INCLUDE_RESEARCH_DISTILL="${KRATT_SCHEDULER_INCLUDE_RESEARCH_DISTILL:-0}"

restart=0
if [[ "${1:-}" == "--restart" ]]; then
  restart=1
  shift
fi

if ! command -v tmux >/dev/null 2>&1; then
  echo "tmux not found; install tmux first" >&2
  exit 127
fi

if [[ "$restart" == "1" ]] && tmux has-session -t "$SESSION" 2>/dev/null; then
  tmux kill-session -t "$SESSION"
fi

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "scheduler already running in tmux session: $SESSION"
  tmux list-windows -t "$SESSION"
  exit 0
fi

args=()
if [[ "$INCLUDE_RESEARCH_DISTILL" == "1" ]]; then
  args+=(--include-research-distill)
fi
args+=("$@")

run_cmd="'$HERE/run-scheduler.sh'"
if (( ${#args[@]} > 0 )); then
  for arg in "${args[@]}"; do
    run_cmd+=" $(printf '%q' "$arg")"
  done
fi
cmd="cd '$REPO' && while true; do $run_cmd; rc=\$?; echo \"[\$(date '+%Y-%m-%dT%H:%M:%S')] scheduler exited rc=\$rc; restarting in 30s\"; sleep 30; done"
tmux new-session -d -s "$SESSION" -n scheduler "$cmd"
echo "started scheduler in tmux session: $SESSION"
echo "attach: tmux attach -t $SESSION"
echo "logs:   tail -f $REPO/.hermes/thesis-automation/logs/scheduler/scheduler.log"
