# v18 clean benchmark summary

Source CSV: `benchmark_checkpoint_faph_v18d_20260429.csv`
Threshold: `0.995`

Lower is better for FPR/FAPH; higher is better for recall.

| model | recall isa XTTS | recall Ode | recall Mattias short | recall friend1 | HN Mac FPR | HN Isa FPR | HN canary FPR | prefix-only FPR | single Kratt FPR | reversed Kratt-kuule FPR | kuule/kule confusable FPR | FAPH CV ET | FAPH LibriSpeech | FAPH Mac bg | FAPH DiPCo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| checkpoint-faph-v18d-clean96-pw96x4 | 4.2% | 0.0% | 60.5% | 0.7% | 20.0% | 0.0% | 0.0% | 67.3% | 30.6% | 29.7% | 24.5% | 1.31 | 0.89 | 0.86 | 0.60 |
| expert-a | 79.2% | 90.9% | 92.3% | 95.9% | 100.0% | 75.0% | 40.0% | 91.4% | 100.0% | 100.0% | 99.8% | 32.98 | 2.67 | 11.99 | 2.11 |
| expert-b2 | 20.8% | 63.6% | 76.0% | 15.2% | 6.7% | 11.7% | 0.0% | 69.5% | 38.7% | 35.9% | 21.0% | 63.08 | 142.66 | 35.97 | 62.31 |
| v15 | 66.7% | 54.5% | 72.1% | 37.9% | 46.7% | 90.0% | 0.0% | 63.6% | 91.4% | 79.7% | 97.0% | 243.15 | 73.82 | 59.95 | 21.37 |
| v16c | 100.0% | 90.9% | 89.8% | 87.6% | 100.0% | 90.0% | 0.0% | 90.5% | 9.7% | 85.9% | 99.8% | 75.12 | 11.21 | 16.27 | 7.83 |
| v18b-clean48-sa | 89.6% | 90.9% |  | 92.4% | 100.0% | 60.0% | 0.0% | 99.6% | 98.4% | 98.4% | 99.0% | 132.18 | 84.32 | 193.54 | 79.16 |
| v18d-clean96 | 91.7% | 100.0% |  | 97.9% | 93.3% | 75.0% | 60.0% | 100.0% | 100.0% | 93.8% | 99.8% | 535.51 | 382.27 | 669.67 | 232.37 |
| v6-residual | 100.0% | 100.0% | 78.7% | 95.2% | 100.0% | 75.0% | 0.0% | 82.3% | 74.2% | 84.4% | 99.5% | 14.40 | 4.09 | 3.43 | 0.30 |
| v6-residual + expert-a | 79.2% | 90.9% | 76.0% | 91.7% | 100.0% | 70.0% | 0.0% | 79.1% | 74.2% | 84.4% | 99.3% | 2.62 | 0.36 | 0.86 | 0.00 |
| v18b-clean48-sa + expert-a | 75.0% | 81.8% |  | 89.0% | 100.0% | 53.3% | 0.0% | 90.9% | 98.4% | 98.4% | 98.8% | 3.93 | 0.36 | 0.86 | 0.30 |
| v18d-clean96 + expert-a | 77.1% | 90.9% |  | 93.8% | 93.3% | 61.7% | 40.0% | 91.4% | 100.0% | 93.8% | 99.7% | 9.68 | 0.36 | 4.28 | 0.90 |
| v18b-clean48-sa + v16c | 89.6% | 81.8% |  | 82.8% | 100.0% | 55.0% | 0.0% | 90.0% | 9.7% | 85.9% | 98.8% | 3.66 | 0.89 | 4.28 | 0.90 |
| v18d-clean96 + v16c | 91.7% | 90.9% |  | 86.2% | 93.3% | 70.0% | 0.0% | 90.5% | 9.7% | 85.9% | 99.7% | 18.06 | 2.67 | 5.14 | 0.60 |

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
| neg_prefix_only_mattias_short | 220 |  |
| neg_single_kratt_neurokone | 186 |  |
| neg_reversed_kratt_kuule | 64 |  |
| neg_kuule_kule_confusables | 600 |  |
| faph_cv_et | 2000 | 3.82 |
| faph_librispeech | 2620 | 5.62 |
| faph_macbook_bg | 14 | 1.17 |
| faph_dipco | 6 | 3.32 |
