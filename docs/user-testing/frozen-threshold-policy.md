# User-test frozen threshold policy

**Status:** pilot freeze candidate, created 2026-05-04. Convert to final freeze only after the real-mic self-pilot confirms the active path is usable. Do not tune thresholds on participant data.

## Purpose

Keep the 20–30 participant user study defensible by separating:

1. pre-user-test operating-point choices;
2. final replay at fixed thresholds;
3. exploratory threshold/DET sweeps reported only as exploratory.

## Active demo candidate

| Field | Value |
|---|---|
| Active model | `v16c` |
| Active threshold/cutoff | `0.996` |
| Role | Stable single-model baseline / active-demo candidate, not production-ready claim |
| ESPHome preparation | `kratt prepare-esphome-model v16c --cutoff 0.996` |
| ESP32 status | local model copy prepared; compile/flash still required before ESP32 demo |

If real-mic pilot shows `v16c` is unusable for the visible demo, one pre-full-study switch to `expert-a` is allowed **only before** participant collection begins. Record the reason and new threshold in this file.

## Frozen replay set

Replay every consented user-test WAV with:

```bash
kratt replay-user-test <session_dir>
```

Default frozen replay configuration:

| Model/combo | Threshold | Notes |
|---|---:|---|
| `v16c` | `0.996` | active baseline candidate |
| `expert-a` | `0.996` | field/recall reference |
| `expert-b2` | `0.996` | verifier/consensus partner |
| `v6-residual` | `0.996` | conservative low-FAPH anchor |
| `v10` | `0.996` | earlier fallback anchor |
| `v15` | `0.996` | earlier balance reference |
| `expert-a+expert-b2` | `0.996/0.996` | primary consensus/MoE row |

Replay implementation details:

- moving-average window: 5 frames;
- frame step: 10 ms;
- prepended silence for streaming-state warmup: 0.5 s;
- output: `output/user-test-replay/<participant>/<session_id>/replay_scores.jsonl` and `replay_summary.csv`.

## Analysis rule

Main thesis tables must use the frozen rows above. Extra thresholds, extra models, extra MoE combinations, and DET sweeps are allowed only as exploratory analysis and must not replace the frozen main table.

## Commit/date record

Fill at final freeze:

```text
final_freeze_date: YYYY-MM-DD
repo_commit: <git sha>
active_path_verified: yes/no
real_mic_self_pilot_session: <path>
esp32_flashed_model: yes/no/not-used
operator: Mattias
notes:
```
