# v18 clean benchmark summary

Source CSV: `benchmark_checkpoint_faph20_v18d_threshold_sweep_20260429.csv`
Threshold: `0.995`

Lower is better for FPR/FAPH; higher is better for recall.

| model | recall isa XTTS | recall Ode | recall Mattias short | recall friend1 | HN Mac FPR | HN Isa FPR | HN canary FPR | prefix-only FPR | single Kratt FPR | reversed Kratt-kuule FPR | kuule/kule confusable FPR | FAPH CV ET | FAPH LibriSpeech | FAPH Mac bg | FAPH DiPCo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| checkpoint-faph20-v18d-clean96-pw96x4 | 72.9% | 90.9% | 81.5% | 42.1% | 46.7% | 61.7% | 0.0% | 73.2% | 95.2% | 93.8% | 78.3% | 23.29 | 8.00 | 52.24 | 3.01 |

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
