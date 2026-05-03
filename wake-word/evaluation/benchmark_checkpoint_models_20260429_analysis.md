# Checkpoint-FAPH v18d benchmark analysis (2026-04-29)

Artifacts:

- Exported completed model: `wake-word/models/kuule-kratt-checkpoint-faph-v18d-clean96-pw96x4/kuule_kratt_checkpoint-faph-v18d-clean96-pw96x4.tflite`
- Exported timed-out faph10 checkpoint manually from HPC weights: `wake-word/models/kuule-kratt-checkpoint-faph10-v18d-clean96-pw96x4/kuule_kratt_checkpoint-faph10-v18d-clean96-pw96x4.tflite`
- Main comparison CSV: `wake-word/evaluation/benchmark_checkpoint_models_20260429.csv` (ignored by git)
- Main comparison summary: `wake-word/evaluation/benchmark_checkpoint_models_20260429.md`
- Threshold sweeps:
  - `wake-word/evaluation/benchmark_checkpoint_faph_v18d_threshold_sweep_20260429.csv`
  - `wake-word/evaluation/benchmark_checkpoint_faph10_v18d_threshold_sweep_20260429.csv`

## Context

The checkpoint experiments were based on the v18d clean-positive / 96-filter configuration, but changed checkpoint selection toward the microWakeWord ambient FAPH objective.

- `checkpoint-faph-v18d-clean96-pw96x4`: exported from the completed run with `target_minimization: 2.0`.
- `checkpoint-faph10-v18d-clean96-pw96x4`: later run with `target_minimization: 10.0`; SLURM timed out before export, but `best_weights.weights.h5` existed and was manually exported with job `922275`.

## Headline comparison at threshold 0.995

| model | Rec Isa | Rec friend1 | HN Mac FPR | HN Isa FPR | prefix-only FPR | single-Kratt FPR | confusable FPR | FAPH CV | FAPH LS | FAPH Mac | FAPH DiPCo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `checkpoint-faph-v18d-clean96-pw96x4` | 4.2% | 0.7% | 20.0% | 0.0% | 67.3% | 30.6% | 24.5% | 1.31 | 0.89 | 0.86 | 0.60 |
| `checkpoint-faph10-v18d-clean96-pw96x4` | 72.9% | 22.1% | 80.0% | 35.0% | 58.6% | 86.0% | 85.8% | 4.19 | 3.02 | 9.42 | 0.60 |
| `v16c` | 100.0% | 87.6% | 100.0% | 90.0% | 90.5% | 9.7% | 99.8% | 75.12 | 11.21 | 16.27 | 7.83 |
| `v6-residual` | 100.0% | 95.2% | 100.0% | 75.0% | 82.3% | 74.2% | 99.5% | 14.40 | 4.09 | 3.43 | 0.30 |
| `expert-a` | 79.2% | 95.9% | 100.0% | 75.0% | 91.4% | 100.0% | 99.8% | 32.98 | 2.67 | 11.99 | 2.11 |
| `expert-b2` | 20.8% | 15.2% | 6.7% | 11.7% | 69.5% | 38.7% | 21.0% | 63.08 | 142.66 | 35.97 | 62.31 |

## Consensus checks with faph10

At threshold `0.995`:

| combo | Rec Isa | Rec friend1 | HN Mac FPR | HN Isa FPR | prefix-only FPR | single-Kratt FPR | confusable FPR | FAPH CV | FAPH LS | FAPH Mac | FAPH DiPCo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `checkpoint-faph10 + v16c` | 72.9% | 20.7% | 80.0% | 35.0% | 57.3% | 8.1% | 85.8% | 0.26 | 0.00 | 0.00 | 0.00 |
| `checkpoint-faph10 + expert-a` | 66.7% | 21.4% | 80.0% | 35.0% | 57.3% | 86.0% | 85.8% | 0.26 | 0.00 | 0.00 | 0.00 |
| `checkpoint-faph10 + v6-residual` | 72.9% | 21.4% | 80.0% | 35.0% | 53.2% | 64.5% | 85.5% | 0.00 | 0.00 | 0.00 | 0.00 |

## Interpretation

1. `checkpoint-faph-v18d-clean96-pw96x4` is an extreme low-FAPH checkpoint, not a usable wake-word model. It reaches near-sub-1 FAPH across all ambient sets, but external positive recall collapses almost completely.
2. `checkpoint-faph10-v18d-clean96-pw96x4` is less collapsed and has much better ambient behavior than v18d/v16c, but still fails as a deployment candidate because real-speaker generalization is poor (`friend1` recall 22.1%) and phrase selectivity remains weak (85.8% confusable FPR, 58.6% prefix-only FPR).
3. faph10 can act as a very strong ambient-FAPH gate in consensus (`faph10+v16c` gives 0.26 FAPH on CV and 0 on LS/Mac/DiPCo at 0.995), but it does not solve the core `kuule/kule <not kratt>` problem and caps recall badly for some real speakers.
4. The corrected checkpoint-selection logic is technically useful: it can select dramatically lower-FAPH checkpoints. However, the objective is still misaligned with the final deployment claim unless unseen-speaker recall and prefix/confusable rejection are part of checkpoint selection or validation.
5. Manual listening of the Mac background triggers showed mostly Mattias/MacBook-domain ordinary speech fragments such as Estonian fillers (`et`, `need on`) and a few other voices played/recorded through the MacBook microphone. This supports the interpretation that the faph10 checkpoint retained a Mattias/MacBook acoustic shortcut while suppressing broader CV/LibriSpeech false accepts.

## Thesis-value conclusion

This is a good negative/diagnostic result: FAPH-optimized checkpoint selection alone does not solve the binary clip-objective failure. It improves ambient false accepts but can simply select an over-conservative or prefix-insensitive detector. For the thesis, this supports the claim that final model choice must report the trio together: recall, hard/confusable rejection, and FAPH.
