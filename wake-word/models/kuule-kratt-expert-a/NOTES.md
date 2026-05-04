# kuule-kratt-expert-a notes

**Status:** Historical MoE gatekeeper / field-balance reference; not a standalone final model.

## Evidence used

- `analysis/dataset_summary.json`
- `analysis/training_config_snapshot.json`
- `wake-word/evaluation/model_evaluation_results.json`
- `wake-word/docs/MODEL_LINEAGE.md`

## Data / config

- Positives: 2241
- Negatives: 9560
- Hard negatives: 0
- Ambient: 1002
- Architecture role in evaluation record: mixednet 4x96f residual, SpecAug OFF gatekeeper
- Training steps: 10000
- Checkpoint objective: accuracy (`target_minimization: 0.0`, `maximization_metric: accuracy`)

## Observed role

Unified benchmark @0.995 reports FAPH CV 33.0, FAPH LS 2.7, FAPH DiPCo 2.1,
Rec Isa 100%, Rec Ode 82%, Rec Mattias 92%, HN Mac 87%, HN Isa 73%.
`model_evaluation_results.json` describes it as designed for consensus with
expert-b2.

## Caveat

Useful historical gatekeeper and field-balance reference, but not a standalone
production model. Later prefix/confusable tests still block promotion.
