# ASR wake verifier probe — Kiirkirjutaja INT8

Generated: 2026-04-29T08:57:14.125434+00:00

Model: `stt-integration/kiirkirjutaja-source/models/sherpa-int8`

Files: 101

## Summary

| subset | n | strict `kuule/kule ... kratt` | loose wake-like |
|---|---:|---:|---:|
| negative_confusable | 23 | 0 (0.0%) | 5 (21.7%) |
| negative_partial | 5 | 0 (0.0%) | 0 (0.0%) |
| positive | 63 | 32 (50.8%) | 45 (71.4%) |
| positive_command | 10 | 0 (0.0%) | 0 (0.0%) |
| group:negative_real_prefix_tail_suspects | 5 | 0 (0.0%) | 0 (0.0%) |
| group:negative_tts_confusables | 13 | 0 (0.0%) | 1 (7.7%) |
| group:negative_tts_phase1_kratt_context | 10 | 0 (0.0%) | 4 (40.0%) |
| group:positive_real_friend1 | 14 | 8 (57.1%) | 12 (85.7%) |
| group:positive_real_mattias_mac | 8 | 7 (87.5%) | 8 (100.0%) |
| group:positive_real_mattias_short_ge0p80 | 10 | 2 (20.0%) | 6 (60.0%) |
| group:positive_real_ode | 11 | 7 (63.6%) | 8 (72.7%) |
| group:positive_tts_kule_vs_kuule | 8 | 3 (37.5%) | 5 (62.5%) |
| group:positive_tts_phase2_exact | 12 | 5 (41.7%) | 6 (50.0%) |
| group:positive_xtts_full_command | 10 | 0 (0.0%) | 0 (0.0%) |

Strict match is a simple normalized text rule: `\b(kuule|kule)\b.*\bkratt\b`. Loose match is exploratory only.

## Transcripts

| kind | group | file | dur | transcript | strict | loose |
|---|---|---|---:|---|---:|---:|
| positive | positive_tts_kule_vs_kuule | `albert_kule_kratt.wav` | 2.01 | kuule Gratt | 0 | 1 |
| positive | positive_tts_kule_vs_kuule | `albert_kuule_kratt.wav` | 2.08 | kuule Kratt | 1 | 1 |
| positive | positive_tts_kule_vs_kuule | `kalev_kule_kratt.wav` | 1.78 | kuule kurat | 0 | 0 |
| positive | positive_tts_kule_vs_kuule | `kalev_kuule_kratt.wav` | 1.97 | kuule Kratt | 1 | 1 |
| positive | positive_tts_kule_vs_kuule | `mari_kule_kratt.wav` | 2.09 | kuule Krat | 0 | 1 |
| positive | positive_tts_kule_vs_kuule | `mari_kuule_kratt.wav` | 2.09 | kuule Kratt | 1 | 1 |
| positive | positive_tts_kule_vs_kuule | `tambet_kule_kratt.wav` | 1.82 | kuule kurat | 0 | 0 |
| positive | positive_tts_kule_vs_kuule | `tambet_kuule_kratt.wav` | 1.89 | kuule kurat | 0 | 0 |
| positive | positive_real_ode | `ode_kuule_kratt_00_at_0.0s.wav` | 2.00 |  | 0 | 0 |
| positive | positive_real_ode | `ode_kuule_kratt_01_at_8.5s.wav` | 3.50 | Kuule, Kratt, kuule, Kratt, kuule, Kratt | 1 | 1 |
| positive | positive_real_ode | `ode_kuule_kratt_02_at_10.8s.wav` | 3.50 | kuule Gratt kuule Kratt kuule Krat | 1 | 1 |
| positive | positive_real_ode | `ode_kuule_kratt_03_at_12.9s.wav` | 3.50 | Kuule, Kratt, kuule, Kratt, | 1 | 1 |
| positive | positive_real_ode | `ode_kuule_kratt_04_at_15.6s.wav` | 3.50 | Et kuule, Gratt, kuule, Kratt, kuule, Kra | 1 | 1 |
| positive | positive_real_ode | `ode_kuule_kratt_05_at_18.6s.wav` | 3.50 | Kuule Kratt, kuule, Kratt | 1 | 1 |
| positive | positive_real_ode | `ode_kuule_kratt_06_at_25.2s.wav` | 3.50 | Kuule Kratt, kuule Kratt | 1 | 1 |
| positive | positive_real_ode | `ode_kuule_kratt_07_at_27.3s.wav` | 3.50 | kuule Gratt, kuule Krat | 0 | 1 |
| positive | positive_real_ode | `ode_kuule_kratt_08_at_29.4s.wav` | 3.50 | kuule Grat poole Kratt | 1 | 1 |
| positive | positive_real_ode | `ode_kuule_kratt_09_at_35.3s.wav` | 3.50 | kuule Krätt kuul | 0 | 0 |
| positive | positive_real_ode | `ode_kuule_kratt_10_at_38.2s.wav` | 3.50 | kuule ka et | 0 | 0 |
| positive | positive_real_mattias_mac | `mattias_pos_0000_20260405_114838.wav` | 2.50 | kuule Kratt | 1 | 1 |
| positive | positive_real_mattias_mac | `mattias_pos_0004_20260405_114859.wav` | 2.50 | kuule Kratt | 1 | 1 |
| positive | positive_real_mattias_mac | `mattias_pos_0008_20260405_114916.wav` | 2.50 | kuule Krait | 0 | 1 |
| positive | positive_real_mattias_mac | `mattias_pos_0012_20260405_114934.wav` | 2.50 | kuule Kratt | 1 | 1 |
| positive | positive_real_mattias_mac | `mattias_pos_0017_20260405_114956.wav` | 2.50 | kuule Kratt | 1 | 1 |
| positive | positive_real_mattias_mac | `mattias_pos_0021_20260405_115014.wav` | 2.50 | kuule Kratt | 1 | 1 |
| positive | positive_real_mattias_mac | `mattias_pos_0025_20260405_115033.wav` | 2.50 | kuule Kratt | 1 | 1 |
| positive | positive_real_mattias_mac | `mattias_pos_0029_20260405_115047.wav` | 2.50 | kuule Kratt | 1 | 1 |
| positive | positive_real_mattias_short_ge0p80 | `mattias-short_pos_0000_20260414_094205.wav` | 2.50 | kuule Grete | 0 | 0 |
| positive | positive_real_mattias_short_ge0p80 | `mattias-short_pos_0016_20260414_094303.wav` | 2.50 | kuule Grate | 0 | 1 |
| positive | positive_real_mattias_short_ge0p80 | `mattias-short_pos_0031_20260414_094352.wav` | 2.50 | kuule Grat | 0 | 1 |
| positive | positive_real_mattias_short_ge0p80 | `mattias-short_pos_0047_20260414_094445.wav` | 2.50 | kuule Kratt | 1 | 1 |
| positive | positive_real_mattias_short_ge0p80 | `mattias_eval_20260414_0014.wav` | 1.50 | kuule kurat | 0 | 0 |
| positive | positive_real_mattias_short_ge0p80 | `mattias_eval_20260414_0029.wav` | 1.50 | kuule Grete | 0 | 0 |
| positive | positive_real_mattias_short_ge0p80 | `mattias_eval_20260414_0045.wav` | 1.50 | et kuule Grate | 0 | 1 |
| positive | positive_real_mattias_short_ge0p80 | `mattias_eval_20260414_0061.wav` | 1.50 | kuule Grete | 0 | 0 |
| positive | positive_real_mattias_short_ge0p80 | `mattias_eval_20260414_0076.wav` | 1.50 | kuule Grad | 0 | 1 |
| positive | positive_real_mattias_short_ge0p80 | `mattias_eval_20260414_0312.wav` | 1.06 | Kuule, Kratt | 1 | 1 |
| positive | positive_real_friend1 | `friend1_s3_0001.wav` | 1.50 | Kuule, Kratt | 1 | 1 |
| positive | positive_real_friend1 | `friend1_s4_0003.wav` | 1.50 | Kuule Kratt | 1 | 1 |
| positive | positive_real_friend1 | `friend1_s4_0014.wav` | 1.50 | kuule Kratt | 1 | 1 |
| positive | positive_real_friend1 | `friend1_s5_0011.wav` | 1.50 | Kuule, Kratt | 1 | 1 |
| positive | positive_real_friend1 | `friend1_s6_0008.wav` | 1.50 | Kuule, Krant | 0 | 1 |
| positive | positive_real_friend1 | `friend1_s6_0019.wav` | 1.50 | Kuule, Kratt | 1 | 1 |
| positive | positive_real_friend1 | `friend1_s6_0030.wav` | 1.50 | Kolgratt | 0 | 0 |
| positive | positive_real_friend1 | `friend1_s6_0042.wav` | 1.50 | Kuule Kratt | 1 | 1 |
| positive | positive_real_friend1 | `friend1_s6_0053.wav` | 1.50 | Kuule, Kratt | 1 | 1 |
| positive | positive_real_friend1 | `friend1_s6_0064.wav` | 1.50 | Kuule Kratt | 1 | 1 |
| positive | positive_real_friend1 | `friend1_s6_0075.wav` | 1.50 | Kuule, Gret | 0 | 0 |
| positive | positive_real_friend1 | `friend1_s6_0086.wav` | 1.50 | kuule Graet | 0 | 1 |
| positive | positive_real_friend1 | `friend1_s6_0097.wav` | 1.50 | Kuule, Krat | 0 | 1 |
| positive | positive_real_friend1 | `friend1_s6_0108.wav` | 1.50 | kuule kraed | 0 | 1 |
| positive | positive_tts_phase2_exact | `albert_0000_kuule_kratt_speed0.8.wav` | 2.32 | Kuule Kratt, | 1 | 1 |
| positive | positive_tts_phase2_exact | `indrek_0006_kuule_kratt_speed1.1.wav` | 2.00 | kuule krat | 0 | 1 |
| positive | positive_tts_phase2_exact | `kalev_0014_kuule_kratt_speed1.05.wav` | 1.92 | kuule Kratt | 1 | 1 |
| positive | positive_tts_phase2_exact | `kylli_0023_kuule_kratt_speed1.05.wav` | 2.04 | kuule Kratt | 1 | 1 |
| positive | positive_tts_phase2_exact | `lee_0028_kule_kratt_speed0.85.wav` | 1.99 | kuule kurat | 0 | 0 |
| positive | positive_tts_phase2_exact | `liivika_0034_kule_kratt_speed1.15.wav` | 1.74 | kuule kurat | 0 | 0 |
| positive | positive_tts_phase2_exact | `luukas_0093_ee_kuule_kratt_speed0.95.wav` | 2.04 | Kulgrattu | 0 | 0 |
| positive | positive_tts_phase2_exact | `mari_0096_ee_kuule_kratt_speed1.1.wav` | 2.00 | ei kuule kurat | 0 | 0 |
| positive | positive_tts_phase2_exact | `meelis_0100_no_kuule_kratt_speed0.85.wav` | 2.22 | no kuule kurat | 0 | 0 |
| positive | positive_tts_phase2_exact | `peeter_0105_no_kuule_kratt_speed1.1.wav` | 1.94 | No kuule Kratt | 1 | 1 |
| positive | positive_tts_phase2_exact | `tambet_0110_noh_kuule_kratt_speed0.9.wav` | 2.33 | noh kuule kurat | 0 | 0 |
| positive | positive_tts_phase2_exact | `vesta_0116_noh_kuule_kratt_speed1.2.wav` | 2.23 | noh kuule Kratt tuleb | 1 | 1 |
| positive_command | positive_xtts_full_command | `isa_xtts_pos_0000_Kuule_Kratt_pane_tuli_põlema_r0.wav` | 1.30 | hulletrat | 0 | 0 |
| positive_command | positive_xtts_full_command | `isa_xtts_pos_0199_kuule_kratt_palun_pane_raadio_mängima.wav` | 1.30 | Kuulge | 0 | 0 |
| positive_command | positive_xtts_full_command | `ode_xtts_pos_0000_kuule_kratt_kas_sa_kuuled_mind.wav` | 1.30 | Kuule | 0 | 0 |
| positive_command | positive_xtts_full_command | `ode_xtts_pos_0199_kuule_kratt_palun_pane_raadio_mängima.wav` | 1.30 |  | 0 | 0 |
| positive_command | positive_xtts_full_command | `marta_xtts_pos_0000_Kuule_Kratt_pane_tuli_põlema_r0.wav` | 1.30 | kuule | 0 | 0 |
| positive_command | positive_xtts_full_command | `marta_xtts_pos_0047_Kuule_Kratt_ava_uks_lahti_r2.wav` | 1.30 | kuule | 0 | 0 |
| positive_command | positive_xtts_full_command | `annam_xtts_pos_0000_Kuule_Kratt_pane_tuli_põlema_r0.wav` | 1.30 | kuul | 0 | 0 |
| positive_command | positive_xtts_full_command | `annam_xtts_pos_0047_Kuule_Kratt_ava_uks_lahti_r2.wav` | 1.30 |  | 0 | 0 |
| positive_command | positive_xtts_full_command | `ema_xtts_pos_0000_Kuule_Kratt_pane_tuli_põlema_r0.wav` | 1.30 | kuule | 0 | 0 |
| positive_command | positive_xtts_full_command | `ema_xtts_pos_0047_Kuule_Kratt_ava_uks_lahti_r2.wav` | 1.30 | Kui need | 0 | 0 |
| negative_confusable | negative_tts_confusables | `luukas_03000_kuule_kraam_speed0.85.wav` | 2.03 | kuule kra | 0 | 1 |
| negative_confusable | negative_tts_confusables | `luukas_03220_kuule_rott_speed0.85.wav` | 2.10 | kuule Rootsi | 0 | 0 |
| negative_confusable | negative_tts_confusables | `luukas_03100_kuule_kass_speed0.85.wav` | 1.93 | kuule kas | 0 | 0 |
| negative_confusable | negative_tts_confusables | `luukas_03230_kuule_kraht_speed0.85.wav` | 2.01 | kuule küla | 0 | 0 |
| negative_confusable | negative_tts_confusables | `luukas_03030_kuule_kraft_speed0.85.wav` | 1.95 | kuule kurat | 0 | 0 |
| negative_confusable | negative_tts_confusables | `luukas_03055_kuule_kross_speed0.85.wav` | 2.12 | kuule, Kross sa | 0 | 0 |
| negative_confusable | negative_tts_confusables | `luukas_03470_kule_kass_speed0.85.wav` | 1.90 | kuule, kas | 0 | 0 |
| negative_confusable | negative_tts_confusables | `luukas_03265_kuule_palun_speed0.85.wav` | 1.97 | kuule palun | 0 | 0 |
| negative_confusable | negative_tts_confusables | `luukas_03255_kuule_nüüd_speed0.85.wav` | 1.88 | Kuula nüüd | 0 | 0 |
| negative_confusable | negative_tts_confusables | `luukas_03415_see_kratt_speed0.85.wav` | 1.99 | see on kurat | 0 | 0 |
| negative_confusable | negative_tts_confusables | `luukas_03440_sinu_kratt_speed0.85.wav` | 2.07 | sinu krat | 0 | 0 |
| negative_confusable | negative_tts_confusables | `luukas_03430_üks_kratt_speed0.85.wav` | 2.12 | Üks krat | 0 | 0 |
| negative_confusable | negative_tts_confusables | `luukas_03450_vana_kratt_speed0.85.wav` | 2.00 | Vanahlat | 0 | 0 |
| negative_confusable | negative_tts_phase1_kratt_context | `albert_0006_Kratt_kuule_speed0.8.wav` | 2.38 | Kratt kuule | 0 | 1 |
| negative_confusable | negative_tts_phase1_kratt_context | `vesta_0102_Kratt_kuule_speed1.1.wav` | 1.93 | Kratt kuule | 0 | 1 |
| negative_confusable | negative_tts_phase1_kratt_context | `albert_0008_Kratt_kas_sa_kuuled_speed0.8.wav` | 2.97 | Kratt kas sa kuule | 0 | 1 |
| negative_confusable | negative_tts_phase1_kratt_context | `vesta_0104_Kratt_kas_sa_kuuled_speed1.1.wav` | 2.29 | Kratt kas sa kuule | 0 | 1 |
| negative_confusable | negative_tts_phase1_kratt_context | `albert_0005_Hei_Kratt_speed0.8.wav` | 1.95 | heigrat | 0 | 0 |
| negative_confusable | negative_tts_phase1_kratt_context | `vesta_0053_Hei_Kratt_speed1.2.wav` | 1.76 | Heigrot | 0 | 0 |
| negative_confusable | negative_tts_phase1_kratt_context | `albert_0004_Tere_Kratt_speed0.8.wav` | 2.04 | tere Kratt | 0 | 0 |
| negative_confusable | negative_tts_phase1_kratt_context | `vesta_0052_Tere_Kratt_speed1.2.wav` | 1.74 | telekt | 0 | 0 |
| negative_confusable | negative_tts_phase1_kratt_context | `albert_0011_No_Kratt_speed0.8.wav` | 1.87 | no kratt | 0 | 0 |
| negative_confusable | negative_tts_phase1_kratt_context | `vesta_0059_No_Kratt_speed1.2.wav` | 1.70 | No Grat. | 0 | 0 |
| negative_partial | negative_real_prefix_tail_suspects | `mattias_eval_20260414_0087.wav` | 0.74 | Kuule | 0 | 0 |
| negative_partial | negative_real_prefix_tail_suspects | `mattias_eval_20260414_0098.wav` | 0.62 | Kuule | 0 | 0 |
| negative_partial | negative_real_prefix_tail_suspects | `mattias_eval_20260414_0100.wav` | 0.65 | Pla | 0 | 0 |
| negative_partial | negative_real_prefix_tail_suspects | `mattias_eval_20260414_0134.wav` | 0.71 | Kuule | 0 | 0 |
| negative_partial | negative_real_prefix_tail_suspects | `mattias_eval_20260414_0135.wav` | 0.74 | Pole | 0 | 0 |

## Post-hoc ordered verifier rule variants

| rule | positive | positive_command | negative_confusable | negative_partial |
|---|---:|---:|---:|---:|
| ordered_exact | 32/63 (50.8%) | 0/10 (0.0%) | 0/23 (0.0%) | 0/5 (0.0%) |
| ordered_fuzzy_safe | 41/63 (65.1%) | 0/10 (0.0%) | 0/23 (0.0%) | 0/5 (0.0%) |
| ordered_fuzzy_plus_grad | 42/63 (66.7%) | 0/10 (0.0%) | 0/23 (0.0%) | 0/5 (0.0%) |
| ordered_loose_kra_gra | 45/63 (71.4%) | 0/10 (0.0%) | 1/23 (4.3%) | 0/5 (0.0%) |

Ordered fuzzy variants require `kuule/kule` before the `kratt`-like token, which avoids reversed `Kratt kuule` false accepts in this subset.
