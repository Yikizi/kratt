# v19a Kratt-only benchmark (target-policy aware)

Source CSV: `benchmark_v19a_kratt_only_20260505.csv`
Model: `v19a-kratt-only`
Recommended internal cutoff: `0.99`; table below uses `0.99`.

Important: this is **single-word `Kratt` target policy**. Single `Kratt`, reversed `Kratt kuule`, and any phrase containing actual `Kratt` are positives here, not hard negatives.

## Metrics at cutoff 0.99

| test_set | kind | metric | value | hits | n | duration_h | notes |
|---|---|---|---:|---:|---:|---:|---|
| pos_isa_xtts_kuule_kratt | positive | recall | 0.0% | 0 | 48 |  | two-word clips; target word present |
| pos_ode_kuule_kratt | positive | recall | 9.1% | 1 | 11 |  | real speaker; small N; target word present |
| pos_friend1_kuule_kratt | positive | recall | 0.0% | 0 | 145 |  | real speaker; target word present |
| pos_mattias_short_kuule_kratt | positive | recall | 18.2% | 66 | 362 |  | Mattias real clips; target word present |
| pos_single_kratt_neurokone | positive | recall | 98.9% | 184 | 186 |  | was negative for exact two-word models; positive for Kratt-only |
| pos_reversed_kratt_kuule | positive | recall | 70.3% | 45 | 64 |  | contains target word; positive for Kratt-only |
| neg_hard_mac_holdout | hard_negative | fpr | 0.0% | 0 | 15 |  | real target-free hard negatives per manifest/docs |
| neg_hard_isa_xtts_target_free | hard_negative | fpr | 0.0% | 0 | 45 |  | old XTTS hard negatives filtered to filenames without kratt |
| neg_kuule_kule_confusables_target_free | hard_negative | fpr | 13.5% | 81 | 600 |  | target-free kuule/kule confusables |
| faph_cv_et | ambient | faph | 0.79 | 3.0 | 2000 | 3.82 | streaming FAPH; target occurrence not transcript-audited |
| faph_librispeech | ambient | faph | 1.60 | 9.0 | 2620 | 5.62 | streaming FAPH; target occurrence not transcript-audited |
| faph_macbook_bg | ambient | faph | 5.99 | 7.0 | 14 | 1.17 | streaming FAPH; target occurrence not transcript-audited |
| faph_dipco | ambient | faph | 0.00 | 0.0 | 6 | 3.32 | streaming FAPH; target occurrence not transcript-audited |

## Diagnostic sanity checks, not final held-out evidence

- Training-source cuts `positive_kratt_only_v19a/accepted`: 551/551 recall @0.99.
- Exploratory real-voice `Kratt` cuts `positive_kratt_only_real_voice_probe_kguard/accepted`: 221/610 = 36.2% recall @0.99. This directory is not fully final-reviewed and includes eval-style speakers, so use it only as a cutter/domain diagnostic.

## All thresholds

| threshold | test_set | metric | value | hits | n | duration_h |
|---:|---|---|---:|---:|---:|---:|
| 0.97 | pos_isa_xtts_kuule_kratt | recall | 0.0% | 0 | 48 |  |
| 0.99 | pos_isa_xtts_kuule_kratt | recall | 0.0% | 0 | 48 |  |
| 0.995 | pos_isa_xtts_kuule_kratt | recall | 0.0% | 0 | 48 |  |
| 0.999 | pos_isa_xtts_kuule_kratt | recall | 0.0% | 0 | 48 |  |
| 0.97 | pos_ode_kuule_kratt | recall | 9.1% | 1 | 11 |  |
| 0.99 | pos_ode_kuule_kratt | recall | 9.1% | 1 | 11 |  |
| 0.995 | pos_ode_kuule_kratt | recall | 9.1% | 1 | 11 |  |
| 0.999 | pos_ode_kuule_kratt | recall | 0.0% | 0 | 11 |  |
| 0.97 | pos_friend1_kuule_kratt | recall | 0.0% | 0 | 145 |  |
| 0.99 | pos_friend1_kuule_kratt | recall | 0.0% | 0 | 145 |  |
| 0.995 | pos_friend1_kuule_kratt | recall | 0.0% | 0 | 145 |  |
| 0.999 | pos_friend1_kuule_kratt | recall | 0.0% | 0 | 145 |  |
| 0.97 | pos_mattias_short_kuule_kratt | recall | 21.0% | 76 | 362 |  |
| 0.99 | pos_mattias_short_kuule_kratt | recall | 18.2% | 66 | 362 |  |
| 0.995 | pos_mattias_short_kuule_kratt | recall | 16.6% | 60 | 362 |  |
| 0.999 | pos_mattias_short_kuule_kratt | recall | 15.2% | 55 | 362 |  |
| 0.97 | pos_single_kratt_neurokone | recall | 99.5% | 185 | 186 |  |
| 0.99 | pos_single_kratt_neurokone | recall | 98.9% | 184 | 186 |  |
| 0.995 | pos_single_kratt_neurokone | recall | 98.9% | 184 | 186 |  |
| 0.999 | pos_single_kratt_neurokone | recall | 98.9% | 184 | 186 |  |
| 0.97 | pos_reversed_kratt_kuule | recall | 71.9% | 46 | 64 |  |
| 0.99 | pos_reversed_kratt_kuule | recall | 70.3% | 45 | 64 |  |
| 0.995 | pos_reversed_kratt_kuule | recall | 68.8% | 44 | 64 |  |
| 0.999 | pos_reversed_kratt_kuule | recall | 68.8% | 44 | 64 |  |
| 0.97 | neg_hard_mac_holdout | fpr | 6.7% | 1 | 15 |  |
| 0.99 | neg_hard_mac_holdout | fpr | 0.0% | 0 | 15 |  |
| 0.995 | neg_hard_mac_holdout | fpr | 0.0% | 0 | 15 |  |
| 0.999 | neg_hard_mac_holdout | fpr | 0.0% | 0 | 15 |  |
| 0.97 | neg_hard_isa_xtts_target_free | fpr | 0.0% | 0 | 45 |  |
| 0.99 | neg_hard_isa_xtts_target_free | fpr | 0.0% | 0 | 45 |  |
| 0.995 | neg_hard_isa_xtts_target_free | fpr | 0.0% | 0 | 45 |  |
| 0.999 | neg_hard_isa_xtts_target_free | fpr | 0.0% | 0 | 45 |  |
| 0.97 | neg_kuule_kule_confusables_target_free | fpr | 15.3% | 92 | 600 |  |
| 0.99 | neg_kuule_kule_confusables_target_free | fpr | 13.5% | 81 | 600 |  |
| 0.995 | neg_kuule_kule_confusables_target_free | fpr | 13.0% | 78 | 600 |  |
| 0.999 | neg_kuule_kule_confusables_target_free | fpr | 11.7% | 70 | 600 |  |
| 0.97 | faph_cv_et | faph | 1.31 | 5.0 | 2000 | 3.82 |
| 0.99 | faph_cv_et | faph | 0.79 | 3.0 | 2000 | 3.82 |
| 0.995 | faph_cv_et | faph | 0.79 | 3.0 | 2000 | 3.82 |
| 0.999 | faph_cv_et | faph | 0.52 | 2.0 | 2000 | 3.82 |
| 0.97 | faph_librispeech | faph | 1.96 | 11.0 | 2620 | 5.62 |
| 0.99 | faph_librispeech | faph | 1.60 | 9.0 | 2620 | 5.62 |
| 0.995 | faph_librispeech | faph | 1.42 | 8.0 | 2620 | 5.62 |
| 0.999 | faph_librispeech | faph | 0.89 | 5.0 | 2620 | 5.62 |
| 0.97 | faph_macbook_bg | faph | 10.28 | 12.0 | 14 | 1.17 |
| 0.99 | faph_macbook_bg | faph | 5.99 | 7.0 | 14 | 1.17 |
| 0.995 | faph_macbook_bg | faph | 4.28 | 5.0 | 14 | 1.17 |
| 0.999 | faph_macbook_bg | faph | 3.43 | 4.0 | 14 | 1.17 |
| 0.97 | faph_dipco | faph | 0.60 | 2.0 | 6 | 3.32 |
| 0.99 | faph_dipco | faph | 0.00 | 0.0 | 6 | 3.32 |
| 0.995 | faph_dipco | faph | 0.00 | 0.0 | 6 | 3.32 |
| 0.999 | faph_dipco | faph | 0.00 | 0.0 | 6 | 3.32 |
