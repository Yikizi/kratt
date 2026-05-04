# kuule-kratt-expert-b2 notes

**Status:** Historical MoE verifier paired with expert-a; not standalone final.

## Evidence used

- Local model directory contents
- `analysis/dataset_summary.json`
- `analysis/training_config_snapshot.json`
- `wake-word/evaluation/model_evaluation_results.json`
- `wake-word/docs/MODEL_LINEAGE.md`

## Data / config

- Positives: 3343
- Negatives: 5045
- Hard negatives: 0
- Ambient: 1002
- Training steps: 10000
- SpecAug: ON in restored config (`freq_mask_count: [2]`, `time_mask_count: [2]`)
- Checkpoint objective: accuracy (`target_minimization: 0.0`, `maximization_metric: accuracy`)

## Observed role

Unified benchmark @0.995 reports FAPH CV 63.1, FAPH LS 142.7, FAPH DiPCo 62.3,
Rec Isa 33%, Rec Ode 64%, Rec Mattias 76%, HN Mac 13%, HN Isa 15%.
`model_evaluation_results.json` describes it as a verifier with 80% hard
negatives + 20% general negatives, designed for consensus with expert-a.

## Caveat

Standalone recall is too weak for deployment. Its historical value is the MoE
consensus experiment, not single-model performance.
