# v18 clean benchmark summary

Source CSV: `benchmark_v18_baselines_with_prefix_20260427_2228.csv`
Threshold: `0.995`

Lower is better for FPR/FAPH; higher is better for recall.

| model | recall isa XTTS | recall Ode | recall Mattias short | recall friend1 | HN Mac FPR | HN Isa FPR | HN canary FPR | prefix-only FPR | single Kratt FPR | reversed Kratt-kuule FPR | kuule/kule confusable FPR | FAPH CV ET | FAPH LibriSpeech | FAPH Mac bg | FAPH DiPCo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| expert-a | 100.0% | 81.8% | 92.3% | 95.9% | 86.7% | 73.3% | 40.0% | 82.3% | 100.0% | 100.0% | 99.8% | 32.98 | 2.67 | 11.99 | 2.11 |
| v16c | 100.0% | 81.8% | 89.8% | 87.6% | 100.0% | 86.7% | 0.0% | 67.7% | 9.7% | 85.9% | 99.8% | 75.12 | 11.21 | 16.27 | 7.83 |
| v17a | 100.0% | 81.8% | 99.2% | 95.9% | 100.0% | 95.0% | 60.0% | 94.1% | 98.9% | 98.4% | 99.8% | 190.28 | 333.53 | 206.38 | 112.27 |
| v17b | 100.0% | 90.9% | 99.7% | 98.6% | 100.0% | 81.7% | 40.0% | 97.1% | 99.5% | 100.0% | 100.0% | 144.74 | 255.79 | 140.44 | 49.66 |
| v17a + v17b | 100.0% | 81.8% | 98.9% | 95.2% | 100.0% | 81.7% | 40.0% | 94.1% | 98.4% | 98.4% | 99.8% | 35.86 | 59.59 | 44.53 | 10.23 |
| v17a + expert-a | 100.0% | 81.8% | 92.3% | 91.7% | 86.7% | 71.7% | 40.0% | 79.4% | 98.9% | 98.4% | 99.7% | 1.83 | 0.00 | 0.86 | 0.30 |
| v17b + expert-a | 100.0% | 81.8% | 92.0% | 94.5% | 86.7% | 70.0% | 20.0% | 79.4% | 99.5% | 100.0% | 99.8% | 4.45 | 0.53 | 0.00 | 0.30 |

## Test-set sizes

| test_set | n | duration_h |
|---|---:|---:|
| pos_isa_xtts | 48 |  |
| pos_ode | 11 |  |
| pos_mattias_short | 362 |  |
| pos_friend1 | 145 |  |
| hard_neg_mac_holdout | 15 |  |
| hard_neg_isa_xtts | 60 |  |
| hard_neg_canary | 5 |  |
| neg_prefix_only_mattias_short | 34 |  |
| neg_single_kratt_neurokone | 186 |  |
| neg_reversed_kratt_kuule | 64 |  |
| neg_kuule_kule_confusables | 600 |  |
| faph_cv_et | 2000 | 3.82 |
| faph_librispeech | 2620 | 5.62 |
| faph_macbook_bg | 14 | 1.17 |
| faph_dipco | 6 | 3.32 |
