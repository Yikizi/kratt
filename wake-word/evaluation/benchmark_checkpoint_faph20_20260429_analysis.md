# Checkpoint-FAPH20 v18d benchmark analysis (2026-04-29)

Artifacts:

- Model: `wake-word/models/kuule-kratt-checkpoint-faph20-v18d-clean96-pw96x4/kuule_kratt_checkpoint-faph20-v18d-clean96-pw96x4.tflite`
- Main comparison CSV: `wake-word/evaluation/benchmark_checkpoint_faph20_20260429.csv`
- Main comparison summary: `wake-word/evaluation/benchmark_checkpoint_faph20_20260429.md`
- Positive recall probe: `wake-word/evaluation/positive_recall_probe_checkpoint_faph20_20260429.md`
- Threshold sweep: `wake-word/evaluation/benchmark_checkpoint_faph20_v18d_threshold_sweep_20260429.csv`

## Context

This run reused the v18d clean-positive / 96-filter architecture but relaxed the FAPH-oriented checkpoint-selection target from `10.0` to `20.0`:

- `clip_duration_ms: 2000`
- SpecAugment ON
- `pointwise_filters: 96,96,96,96`
- `target_minimization: 20.0`
- `minimization_metric: ambient_false_positives_per_hour`
- `maximization_metric: average_viable_recall`

The purpose was not to claim a production model, but to map the upper end of the FAPH/recall trade-off after the previous checkpoint results:

- `target=2`: excellent ambient FAPH, external recall collapse.
- `target=10`: good ambient FAPH, still poor real-speaker generalization.
- `target=20`: test whether accepting more FAPH restores recall before the model becomes too permissive.

## Headline comparison at threshold 0.995

| model | Rec Isa | Rec Friend1 | HN Mac FPR | HN Isa FPR | prefix-only FPR | single-Kratt FPR | confusable FPR | FAPH CV | FAPH LS | FAPH Mac | FAPH DiPCo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `checkpoint-faph-v18d-clean96-pw96x4` | 4.2% | 0.7% | 20.0% | 0.0% | 67.3% | 30.6% | 24.5% | 1.31 | 0.89 | 0.86 | 0.60 |
| `checkpoint-faph10-v18d-clean96-pw96x4` | 72.9% | 22.1% | 80.0% | 35.0% | 58.6% | 86.0% | 85.8% | 4.19 | 3.02 | 9.42 | 0.60 |
| `checkpoint-faph20-v18d-clean96-pw96x4` | 72.9% | 42.1% | 46.7% | 61.7% | 73.2% | 95.2% | 78.3% | 23.29 | 8.00 | 52.24 | 3.01 |
| `v16c` | 100.0% | 87.6% | 100.0% | 90.0% | 90.5% | 9.7% | 99.8% | 75.12 | 11.21 | 16.27 | 7.83 |
| `v6-residual` | 100.0% | 95.2% | 100.0% | 75.0% | 82.3% | 74.2% | 99.5% | 14.40 | 4.09 | 3.43 | 0.30 |

## Threshold sweep for faph20

| threshold | Isa recall | Friend1 recall | HN Mac FPR | HN Isa FPR | prefix FPR | confusable FPR | FAPH CV | FAPH LS | FAPH Mac | FAPH DiPCo |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.5 | 83.3% | 75.2% | 80.0% | 71.7% | 88.2% | 94.0% | 209.12 | 39.49 | 304.86 | 39.73 |
| 0.7 | 81.2% | 70.3% | 73.3% | 70.0% | 85.9% | 92.0% | 151.02 | 31.49 | 214.09 | 24.38 |
| 0.9 | 79.2% | 62.8% | 53.3% | 63.3% | 81.8% | 89.5% | 82.97 | 20.28 | 129.31 | 13.85 |
| 0.95 | 75.0% | 56.5% | 53.3% | 63.3% | 78.2% | 87.3% | 60.98 | 16.19 | 100.19 | 8.13 |
| 0.97 | 75.0% | 50.3% | 53.3% | 63.3% | 77.7% | 85.0% | 45.02 | 13.87 | 83.92 | 6.02 |
| 0.98 | 72.9% | 48.3% | 53.3% | 61.7% | 76.4% | 83.8% | 37.43 | 12.63 | 71.93 | 4.82 |
| 0.99 | 72.9% | 44.1% | 53.3% | 61.7% | 74.6% | 80.7% | 28.53 | 9.25 | 57.38 | 3.31 |
| 0.995 | 72.9% | 42.1% | 46.7% | 61.7% | 73.2% | 78.3% | 23.29 | 8.00 | 52.24 | 3.01 |
| 0.996 | 72.9% | 42.1% | 46.7% | 61.7% | 73.2% | 78.0% | 22.25 | 7.83 | 51.38 | 3.01 |
| 0.997 | 70.8% | 40.7% | 46.7% | 61.7% | 72.3% | 77.2% | 18.84 | 6.76 | 47.96 | 2.71 |
| 0.998 | 70.8% | 40.7% | 46.7% | 61.7% | 72.3% | 77.2% | 18.84 | 6.76 | 47.96 | 2.71 |
| 0.999 | 66.7% | 39.3% | 46.7% | 60.0% | 70.0% | 75.7% | 14.92 | 5.69 | 44.53 | 2.71 |

## Consensus checks at threshold 0.995

| combo | Rec Isa | Rec Friend1 | HN Mac FPR | HN Isa FPR | prefix-only FPR | single-Kratt FPR | confusable FPR | FAPH CV | FAPH LS | FAPH Mac | FAPH DiPCo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `checkpoint-faph20 + v16c` | 72.9% | 40.0% | 46.7% | 60.0% | 68.2% | 9.7% | 78.2% | 0.52 | 0.00 | 0.00 | 0.00 |
| `checkpoint-faph20 + expert-a` | 66.7% | 41.4% | 46.7% | 58.3% | 69.1% | 95.2% | 78.3% | 0.26 | 0.00 | 1.71 | 0.00 |
| `checkpoint-faph20 + v6-residual` | 72.9% | 42.1% | 46.7% | 56.7% | 63.2% | 69.9% | 78.2% | 0.26 | 0.00 | 0.00 | 0.00 |
| `checkpoint-faph20 + checkpoint-faph10` | 64.6% | 15.2% | 46.7% | 30.0% | 50.0% | 82.8% | 72.8% | 0.52 | 0.18 | 0.86 | 0.00 |

## Interpretation

1. Raising `target_minimization` from 10 to 20 restores some external real-speaker recall, but not enough for deployment. Friend1 improves from 22.1% to 42.1% at threshold 0.995, while Isa remains 72.9%.
2. The cost is substantial: CV FAPH rises from 4.19 to 23.29 and Mac background FAPH rises from 9.42 to 52.24 at threshold 0.995.
3. Phrase selectivity is still unsolved. `checkpoint-faph20` fires on 78.3% of `kuule/kule <not kratt>` confusables and 73.2% of prefix-only clips at threshold 0.995.
4. Consensus with `v16c`, `expert-a`, or `v6-residual` recovers excellent ambient FAPH, but recall remains capped by the checkpoint model and confusable rejection remains weak.
5. The target=20 run is therefore a useful Pareto-boundary measurement: allowing a higher FAPH checkpoint target improves recall only partially and quickly reintroduces unacceptable false accepts.

## Thesis-value conclusion

The checkpoint-FAPH series is strong evidence that checkpoint selection must use a composite objective. Ambient FAPH alone is insufficient; even a relaxed FAPH target (`20`) still fails to recover robust unseen-speaker recall and exact phrase selectivity. The final model-selection contract should remain the trio: ambient FAPH + real/unseen-speaker recall + held-out prefix/confusable rejection.
