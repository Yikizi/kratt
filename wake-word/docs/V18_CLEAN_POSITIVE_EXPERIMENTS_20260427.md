# v18 clean-positive experiment pack (2026-04-27 overnight)

Purpose: recover from the v17 positive-label incident by training only on valid full wake-phrase positives.

## Strict positive policy

Valid positives must be exactly two words:

- `kuule kratt`
- `kule kratt`
- elongated variants are allowed only when still exactly the same two words, e.g. `kuuule kratt`, `kuulee kratt`

Excluded from positive training by default:

- single-word clips (`kuule`, `kule`, `kratt`)
- prefix-only/too-short clips (initially `<0.50s`; raised to `<0.80s` after the 2026-04-28 mattias-short STT audit)
- filler/context clips (`ee/no/noh kuule kratt`, full sentences, command tails)
- reversed phrase clips (`kratt kuule`)
- SSML/XML readout clips
- XTTS full-command positives

## Data builder

`data/validation/build_strict_positive_set.py` builds a generated strict positive source from:

- `data/raw/neurokone_phase1`
- `data/raw/neurokone_phase2`
- `data/raw/kule_vs_kuule_test`

Local/HPC count check with `--min-duration-s 0.50 --max-duration-s 4.00`:

- accepted: `709`
- rejected `exclude_pattern`: `373`
- rejected `not_exact_phrase_filename`: `632`

The submit script creates a per-tag strict directory such as:

`data/processed/positive_strict_kuule_kule_v18a-clean48`

## Training safeguards

- `submit_hpc_kuule_kratt.sh` recall-cv now uses the strict generated positives instead of broad `positive_tts`/SSML/XTTS positives.
- Known-bad SSML and XTTS positive dirs are quarantined by default.
- Positive duration gate for v18 was `0.50s`–`4.00s`; future runs use `0.80s`–`4.00s` unless manually whitelisted.
- Random positive cropping is disabled by default in mmap generation.
- microWakeWord augmentation still runs inside the training framework; the source-set cleanup should not remove augmentation behavior.

## New prefix/partial regression sets

`data/validation/build_prefix_regression_set.py` materializes negative regression sets under:

`data/processed/prefix_regression_test/`

Counts:

| set | count | intent |
|---|---:|---|
| `prefix_only_mattias_short_lt0p50` | 34 | original v18 user-audited too-short/prefix-only clips |
| `prefix_only_mattias_short_lt0p80` | 220 | updated post-STT-audit prefix/tail/empty candidate set for future benchmarks |
| `single_kratt_neurokone_phase1` | 186 | `kratt` alone must not trigger |
| `reversed_kratt_kuule_phase1` | 64 | reversed order must not trigger |
| `kuule_kule_confusables_neurokone_hard_neg_v2` | 600 | `kuule/kule <not kratt>` confusables |

Caveat: the confusable set overlaps with the TTS hard-negative source used by `v18e`/`v18f`; treat it as a training-regression sanity check for those variants, not an independent holdout. The other prefix/single/reversed sets remain useful independent controls.

## Overnight v18 matrix

| tag | job | variant | intent |
|---|---:|---|---|
| `v18a-clean48` | 921556 | strict positives, 48 filters, no SpecAugment | clean baseline |
| `v18b-clean48-sa` | 921550 | strict positives, 48 filters, SpecAugment | test whether SpecAugment helps after label cleanup |
| `v18c-clean48-hn` | 921558 | strict positives + real/folded hard negatives | test explicit hard negatives without TTS confusable set |
| `v18d-clean96` | 921560 | strict positives, 96 filters | wider-capacity control; may be slower |
| `v18e-clean48-tts-hn` | 921573 | strict positives + TTS hard negatives (`negative_tts_hard*`) | explicit prefix/confusable-negative control |
| `v18f-clean48-tts-hn-fast` | 921575 | same as v18e but `6000,2000` steps | fast backup in case full v18e times out |

Monitor script:

```bash
scripts/monitor_v18_overnight.sh
```

It polls SLURM, downloads completed models, builds prefix regression sets, runs `benchmark_all_models.py`, and writes:

- `wake-word/evaluation/benchmark_v18_clean_latest.csv`
- `wake-word/evaluation/benchmark_v18_clean_latest.md`

## Baseline prefix-regression numbers before v18

Source: `evaluation/benchmark_v18_baselines_with_prefix_20260427_2228.md` at threshold `0.995`.

| model | prefix-only FPR | single Kratt FPR | reversed Kratt-kuule FPR | kuule/kule confusable FPR | FAPH CV ET |
|---|---:|---:|---:|---:|---:|
| `expert-a` | 82.3% | 100.0% | 100.0% | 99.8% | 32.98 |
| `v16c` | 67.7% | 9.7% | 85.9% | 99.8% | 75.12 |
| `v17a` | 94.1% | 98.9% | 98.4% | 99.8% | 190.28 |
| `v17b` | 97.1% | 99.5% | 100.0% | 100.0% | 144.74 |

Interpretation: v17 is clearly broken, but older deployable candidates also lack robust partial/confusable rejection under the new regression sets. v18 should be judged on both standard benchmark metrics and these new negative controls.

## Overnight results (2026-04-28)

Source single-model benchmark: `wake-word/evaluation/benchmark_v18_clean_20260428_0214.md` at threshold `0.995`.

| model | Rec Isa | Rec Friend1 | HN Mac FPR | HN Isa FPR | prefix-only FPR | single Kratt FPR | confusable FPR | FAPH CV | FAPH LS | FAPH Mac |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `v16c` baseline | 100.0% | 87.6% | 100.0% | 86.7% | 67.7% | 9.7% | 99.8% | 75.12 | 11.21 | 16.27 |
| `expert-a` baseline | 100.0% | 95.9% | 86.7% | 73.3% | 82.3% | 100.0% | 99.8% | 32.98 | 2.67 | 11.99 |
| `v17a` failed baseline | 100.0% | 95.9% | 100.0% | 95.0% | 94.1% | 98.9% | 99.8% | 190.28 | 333.53 | 206.38 |
| `v17b` failed baseline | 100.0% | 98.6% | 100.0% | 81.7% | 97.1% | 99.5% | 100.0% | 144.74 | 255.79 | 140.44 |
| `v18a-clean48` | 100.0% | 93.1% | 86.7% | 71.7% | 97.1% | 99.5% | 99.3% | 515.35 | 304.36 | 572.91 |
| `v18b-clean48-sa` | 95.8% | 92.4% | 93.3% | 56.7% | 100.0% | 98.4% | 99.0% | 132.18 | 84.32 | 193.54 |
| `v18c-clean48-hn` | 31.2% | 84.1% | 40.0% | 13.3% | 82.3% | 100.0% | 94.3% | 84.54 | 66.71 | 445.31 |
| `v18d-clean96` | 97.9% | 97.9% | 80.0% | 76.7% | 100.0% | 100.0% | 99.8% | 535.51 | 382.27 | 669.67 |
| `v18e-clean48-tts-hn` | 75.0% | 90.3% | 33.3% | 45.0% | 85.3% | 99.5% | 88.5% | 356.48 | 192.11 | 491.55 |
| `v18f-clean48-tts-hn-fast` | 52.1% | 66.2% | 46.7% | 36.7% | 88.2% | 76.9% | 78.8% | 249.96 | 139.82 | 309.15 |

### Interpretation

The strict positive cleanup was necessary but **not sufficient**. It did not produce a deployable single model overnight.

Key observations:

1. **v17 was not only an SSML/XTTS problem.** Removing corrupted positives did not automatically teach the model that the full two-word phrase is required.
2. **All v18 single models still fire on partial/confusable phrases.** Prefix-only FPR stays 82–100%, and `kuule/kule <not kratt>` confusable FPR stays 79–100%.
3. **FAPH got worse for the clean-only models.** v18a/v18d are very permissive general-speech detectors despite clean positives.
4. **SpecAugment helped FAPH but not phrase selectivity.** v18b cut FAPH vs v18a but retained near-total prefix/confusable failure.
5. **Hard negatives help but trade away recall.** v18c/v18e/v18f reduce hard-negative/confusable FPR, but recall drops too much or FAPH remains high.

Updated conclusion: the next model family must treat partial phrases and near-phrase confusables as first-class negatives, not just rely on positive label purity. The training objective currently still allows the network to treat `kuule`/`kule` or `kratt`-like phonetics as enough evidence.

## Consensus follow-up (same night)

Source: `wake-word/evaluation/benchmark_v18_consensus_20260428_0242.md` at threshold `0.995`.

| consensus | Rec Isa | Rec Friend1 | HN Mac FPR | HN Isa FPR | prefix-only FPR | single Kratt FPR | confusable FPR | FAPH CV | FAPH LS | FAPH Mac |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `v18b-clean48-sa + expert-a` | 95.8% | 89.0% | 80.0% | 50.0% | 82.3% | 98.4% | 98.8% | 3.93 | 0.36 | 0.86 |
| `v18d-clean96 + expert-a` | 97.9% | 93.8% | 73.3% | 60.0% | 82.3% | 100.0% | 99.7% | 9.68 | 0.36 | 4.28 |
| `v18b-clean48-sa + v16c` | 95.8% | 82.8% | 93.3% | 51.7% | 67.7% | 9.7% | 98.8% | 3.66 | 0.89 | 4.28 |
| `v18e-clean48-tts-hn + expert-a` | 75.0% | 86.2% | 33.3% | 36.7% | 70.6% | 99.5% | 88.3% | 4.97 | 0.18 | 0.86 |
| `v18e-clean48-tts-hn + v16c` | 75.0% | 79.3% | 33.3% | 43.3% | 61.8% | 9.7% | 88.3% | 7.33 | 1.07 | 2.57 |

Consensus can recover excellent FAPH numbers, especially `v18b-clean48-sa + expert-a`, but it **still does not solve phrase selectivity**: prefix/confusable FPR remains too high. Treat these as diagnostic MoE candidates, not final deployment candidates.

## Next experiment recommendation

Do not run more clean-positive-only variants. Instead:

1. Build/freeze independent negative sets for `kuule` only, `kule` only, `kratt` only, `kuule/kule <confusable>`, and reversed/order-invalid phrases.
2. Include a controlled ratio of these as training negatives (start ~10–20% of the effective negative pool, not 40–50%).
3. Keep a **separate holdout** prefix/confusable set not used in training.
4. Consider two-stage detection: first word gate + second word confirmation, or a short sequence/CTC-style objective, because binary clip KWS is struggling to encode exact two-token order.
5. Use `v18b-clean48-sa + expert-a` as a low-FAPH MoE baseline, but only after a phrase-selectivity gate is added.
