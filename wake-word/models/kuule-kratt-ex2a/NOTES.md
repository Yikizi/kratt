# kuule-kratt-ex2a notes

**Status:** Failed expert-family experiment; retained as a TTS-overfit warning.

## Evidence used

- Local model directory contents
- `analysis/dataset_summary.json`
- `analysis/training_config_snapshot.json`
- `wake-word/docs/MODEL_LINEAGE.md`
- `wake-word/docs/research/session-findings-apr-2026.md`

## Data / config

- Positives: 3343
- Negatives: 9560
- Hard negatives: 0
- Ambient: 1002
- Training steps: 10000
- SpecAug: OFF in restored config (`freq_mask_count: [0]`, `time_mask_count: [0]`)
- Checkpoint objective: accuracy (`target_minimization: 0.0`, `maximization_metric: accuracy`)

## Observed role

Unified benchmark @0.995 reports FAPH CV 124.3, Rec Isa 92%, Rec Ode 27%,
HN Mac 93%, HN Isa 85%. Session findings record the intended lesson: adding all
TTS/XTTS positives to expert-a made recall and FAPH worse rather than better.

## Caveat

Use as evidence for the "real voices must dominate positives" lesson, not as a
candidate model.
