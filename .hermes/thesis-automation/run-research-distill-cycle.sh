#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_PATH="$HERE/logs/hourly/research-cycle.log"
mkdir -p "$(dirname "$LOG_PATH")"
RESEARCH_LANE="${1:-research-note}"
DISTILL_LANE="${2:-distill-sentence}"
TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

lane_active() {
  local lane="$1"
  python3 - "$HERE/lanes/lanes.json" "$lane" <<'PY'
import json, sys
path, lane_id = sys.argv[1], sys.argv[2]
data = json.load(open(path))
for lane in data.get("lanes", []):
    if lane.get("id") == lane_id:
        sys.exit(0 if lane.get("active", True) else 1)
sys.exit(2)
PY
}

run_lane() {
  local lane="$1"
  local output
  output="$("$HERE/run-hourly.sh" --lane "$lane" 2>&1)"
  printf '%s\n' "$output" | tee -a "$LOG_PATH"
  printf '%s\n' "$output" | tail -n 1
}

if ! lane_active "$RESEARCH_LANE"; then
  printf '%s phase-skip lane=%s reason=inactive-compression-mode\n' "$TS" "$RESEARCH_LANE" >> "$LOG_PATH"
  printf '{"lane":"%s","result":"skipped","reason":"inactive-compression-mode"}\n' "$RESEARCH_LANE"
  exit 0
fi

if ! lane_active "$DISTILL_LANE"; then
  printf '%s phase-skip lane=%s reason=inactive-compression-mode\n' "$TS" "$DISTILL_LANE" >> "$LOG_PATH"
  printf '{"lane":"%s","result":"skipped","reason":"inactive-compression-mode"}\n' "$DISTILL_LANE"
  exit 0
fi

printf '%s phase-start lane=%s\n' "$TS" "$RESEARCH_LANE" >> "$LOG_PATH"
research_line="$(run_lane "$RESEARCH_LANE")"
if echo "$research_line" | grep -q '"result":"committed"'; then
  printf '%s phase-continue lane=%s\n' "$TS" "$DISTILL_LANE" >> "$LOG_PATH"
  run_lane "$DISTILL_LANE"
else
  printf '%s phase-skip lane=%s reason=no-new-research\n' "$TS" "$DISTILL_LANE" >> "$LOG_PATH"
fi
printf '%s phase-end\n' "$TS" >> "$LOG_PATH"
