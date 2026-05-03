#!/usr/bin/env bash
# Monitor overnight v18 clean HPC jobs, download completed models, benchmark, and notify this iTerm tab.
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

REMOTE="malinh@base.hpc.taltech.ee"
REMOTE_RUNS="/gpfs/mariana/smbhome/malinh/kratt-data/training/runs"
LOG_DIR="${ROOT_DIR}/logs"
mkdir -p "${LOG_DIR}"
LOG_PATH="${LOG_DIR}/v18-overnight-monitor-$(date +%Y%m%d_%H%M%S).log"

# The launching pi/iTerm session. Override with ITERM_NOTIFY_SESSION=<uuid> if needed.
ITERM_NOTIFY_SESSION="${ITERM_NOTIFY_SESSION:-${ITERM_SESSION_ID#*:}}"
POLL_SECONDS="${POLL_SECONDS:-300}"

TAGS=(
  v18a-clean48
  v18b-clean48-sa
  v18c-clean48-hn
  v18d-clean96
  v18e-clean48-tts-hn
  v18f-clean48-tts-hn-fast
)
JOB_IDS=(
  921556
  921550
  921558
  921560
  921573
  921575
)
BASELINE_MODELS=(v16c expert-a v17a v17b)

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "${LOG_PATH}"
}

notify() {
  local msg="$*"
  log "NOTIFY: ${msg}"
  if command -v osascript >/dev/null 2>&1; then
    local osamsg="${msg//\\/\\\\}"
    osamsg="${osamsg//\"/\\\"}"
    osascript -e "display notification \"${osamsg}\" with title \"Kratt v18 overnight\"" >/dev/null 2>&1 || true
  fi
  if command -v it2 >/dev/null 2>&1 && [[ -n "${ITERM_NOTIFY_SESSION}" ]]; then
    # The target is the pi agent TUI, not a shell: send a readable prompt that
    # becomes a user message and wakes the agent on completion/error.
    it2 session run --session "${ITERM_NOTIFY_SESSION}" "[Kratt v18 overnight] ${msg}" >/dev/null 2>&1 || true
  fi
}

job_state() {
  local id="$1"
  ssh -o BatchMode=yes "${REMOTE}" \
    "sacct -j ${id} --format=JobIDRaw,State,ExitCode -P -n 2>/dev/null | awk -F'|' '\$1==\"${id}\" {print \$2 \"|\" \$3; exit}'" \
    2>/dev/null | tail -1
}

squeue_snapshot() {
  ssh -o BatchMode=yes "${REMOTE}" \
    "squeue -u malinh -o '%.10i %.35j %.2t %.10M %.10l %.20R' | head -40" \
    2>/dev/null || true
}

remote_log_tail() {
  local tag="$1"
  ssh -o BatchMode=yes "${REMOTE}" \
    "tail -60 ${REMOTE_RUNS}/logs/kratt-kuule-kratt-${tag}-*.out 2>/dev/null || true" \
    2>/dev/null || true
}

COMPLETED_TAGS=()
FAILED_TAGS=()
if [[ "${SUPPRESS_START_NOTIFY:-0}" != "1" ]]; then
  notify "monitor started for ${TAGS[*]} (jobs ${JOB_IDS[*]}); polling every ${POLL_SECONDS}s"
else
  log "monitor started for ${TAGS[*]} (jobs ${JOB_IDS[*]}); polling every ${POLL_SECONDS}s"
fi
log "Writing monitor log to ${LOG_PATH}"

while true; do
  log "Polling job states..."
  terminal_count=0
  failed=0
  for idx in "${!JOB_IDS[@]}"; do
    id="${JOB_IDS[$idx]}"
    tag="${TAGS[$idx]}"
    state_exit="$(job_state "${id}")"
    state="${state_exit%%|*}"
    exit_code="${state_exit#*|}"
    [[ "${state}" == "${exit_code}" ]] && exit_code=""
    state="${state:-UNKNOWN}"
    log "${tag} (${id}): ${state} ${exit_code}"
    case "${state}" in
      COMPLETED)
        terminal_count=$((terminal_count + 1))
        ;;
      FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)
        terminal_count=$((terminal_count + 1))
        failed=1
        notify "${tag} job ${id} ended ${state} ${exit_code}; tailing log in ${LOG_PATH}"
        {
          echo "--- remote log tail for ${tag} (${id}) ---"
          remote_log_tail "${tag}"
          echo "--- end log tail ---"
        } >> "${LOG_PATH}"
        ;;
    esac
  done
  {
    echo "--- squeue snapshot ---"
    squeue_snapshot
    echo "--- end squeue snapshot ---"
  } >> "${LOG_PATH}"

  if [[ "${terminal_count}" -eq "${#JOB_IDS[@]}" ]]; then
    break
  fi
  sleep "${POLL_SECONDS}"
done

# Final state classification. Continue with completed jobs even if wider/extra
# variants timed out, so the morning report still contains usable models.
COMPLETED_TAGS=()
FAILED_TAGS=()
for idx in "${!JOB_IDS[@]}"; do
  id="${JOB_IDS[$idx]}"
  tag="${TAGS[$idx]}"
  state_exit="$(job_state "${id}")"
  state="${state_exit%%|*}"
  state="${state:-UNKNOWN}"
  if [[ "${state}" == "COMPLETED" ]]; then
    COMPLETED_TAGS+=("${tag}")
  else
    FAILED_TAGS+=("${tag}:${id}:${state}")
  fi
done

if [[ "${#FAILED_TAGS[@]}" -gt 0 ]]; then
  notify "some v18 jobs did not complete: ${FAILED_TAGS[*]}; continuing with completed: ${COMPLETED_TAGS[*]:-none}"
fi
if [[ "${#COMPLETED_TAGS[@]}" -eq 0 ]]; then
  notify "no v18 jobs completed; see ${LOG_PATH}"
  exit 1
fi

notify "completed v18 jobs: ${COMPLETED_TAGS[*]}; downloading models"

for tag in "${COMPLETED_TAGS[@]}"; do
  log "Downloading ${tag}"
  if ./cli/kratt hpc download "${tag}" >> "${LOG_PATH}" 2>&1; then
    log "Downloaded ${tag}"
  else
    notify "download failed for ${tag}; see ${LOG_PATH}"
    exit 1
  fi
  # Preserve the HPC training log locally next to the model for inspection.
  mkdir -p "wake-word/models/kuule-kratt-${tag}/analysis"
  scp -q "${REMOTE}:${REMOTE_RUNS}/logs/kratt-kuule-kratt-${tag}-*.out" \
    "wake-word/models/kuule-kratt-${tag}/analysis/" >> "${LOG_PATH}" 2>&1 || true
done

notify "models downloaded; running prefix set build + benchmark"

cd "${ROOT_DIR}/wake-word"
uv run python data/validation/build_prefix_regression_set.py --force >> "${LOG_PATH}" 2>&1

BENCH_CSV="evaluation/benchmark_v18_clean_$(date +%Y%m%d_%H%M).csv"
BENCH_MD="${BENCH_CSV%.csv}.md"
uv run python evaluation/benchmark_all_models.py \
  --models "${BASELINE_MODELS[@]}" "${COMPLETED_TAGS[@]}" \
  --thresholds 0.995 0.996 0.999 \
  --output "${BENCH_CSV}" >> "${LOG_PATH}" 2>&1
uv run python evaluation/summarize_benchmark_csv.py \
  "${BENCH_CSV}" --threshold 0.995 --output "${BENCH_MD}" >> "${LOG_PATH}" 2>&1

ln -sf "$(basename "${BENCH_CSV}")" evaluation/benchmark_v18_clean_latest.csv
ln -sf "$(basename "${BENCH_MD}")" evaluation/benchmark_v18_clean_latest.md

# Create lightweight per-model notes if they do not already exist.
for tag in "${COMPLETED_TAGS[@]}"; do
  notes="models/kuule-kratt-${tag}/NOTES.md"
  if [[ ! -f "${notes}" ]]; then
    cat > "${notes}" <<EOF_NOTES
# kuule-kratt-${tag}

Overnight v18 clean-positive experiment submitted 2026-04-27.

## Hypothesis
Strict two-word positive policy (only \`kuule/kule kratt\`, no filler/context/SSML/XML/full-command positives) should remove the v17 prefix-only failure mode.

## Training data policy
- Generated strict positives built per job from Neurokõne phase1/phase2 + kule/kuule A/B test.
- Known-bad SSML/XML and XTTS full-command positives quarantined by default.
- Positive duration gate: 0.50s–4.00s.
- Random positive cropping disabled by default.

## Variant
See \`analysis/\` and the HPC log for exact flags. This model is included in \`${BENCH_MD}\`.

## Status
Benchmark generated by overnight monitor; review \`wake-word/${BENCH_MD}\` before promoting.
EOF_NOTES
  fi
done

notify "v18 benchmark complete: wake-word/${BENCH_MD}"
log "Done. Summary: wake-word/${BENCH_MD}; CSV: wake-word/${BENCH_CSV}"
