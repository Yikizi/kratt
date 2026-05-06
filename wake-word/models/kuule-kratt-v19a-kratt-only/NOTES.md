# kuule-kratt-v19a-kratt-only

Preliminary `Kratt`-only ablation trained on HPC 2026-05-04/05.

## Hypothesis

A single-word wake target (`Kratt`) may be easier for a tiny KWS model than the exact two-word phrase `Kuule/Kule Kratt`, which had persistent prefix/phrase-selectivity failures.

## Target policy

Different from earlier `Kuule Kratt` models:

- Positive: any clean utterance containing the target word `Kratt`.
- Not valid as negatives: `Kuule Kratt`, `Tere Kratt`, `Kratt kuule`, or any phrase containing actual `Kratt`.
- Valid hard negatives must be target-free confusables, e.g. `kurat`, `kraam`, `kraan`, `kraad`, `ratas`, `rattad`, `rott`, `kaart`, `kart`.

## Data

- Positives: `data/processed/positive_kratt_only_v19a/accepted`
  - 551 reviewed `Kratt` cuts from clean strict `Kuule/Kule Kratt` source.
  - Training split: 469 train / 82 internal positive test.
- Negatives:
  - 5000 Common Voice ET clips, excluding transcript word `kratt` only.
  - 6725 extra general/device/mined negatives.
  - 0 hard negatives in the first ablation, to avoid old exact-phrase label poisoning.
- Ambient: 1002 clips.

## Training

Submitted as SLURM job `923301` on `common`, completed successfully in 03:54:42.

Command:

```bash
./cli/kratt train-kratt-only v19a-kratt-only \
  --steps 15000,5000 \
  --time 08:00:00 \
  --partition common
```

Main config:

- clip duration: 1000 ms
- recall profile: on
- SpecAugment: on
- pointwise filters: `96,96,96,96`
- residual: default/on
- target minimization: 20

## Internal result

Training run directory:

```text
/gpfs/mariana/smbhome/malinh/kratt-data/training/runs/microwakeword-kratt-only-v19a-kratt-only-20260504-203253
```

Exported TFLite:

```text
tflite_stream_state_internal_quant/stream_state_internal_quant.tflite
```

Internal streaming TFLite eval:

| cutoff | FRR | FAPH |
|---:|---:|---:|
| 0.99 | 0.0435 | 2.0 |
| 1.00 | 1.0000 | 0.0 |

Recommended cutoff from internal analysis: `0.99` for best <=2 FAPH operating point.

Local artifact sync: downloaded from HPC on 2026-05-05 into this directory; `kuule_kratt_v19a-kratt-only.tflite` is a symlink to `model.tflite`.

## External Kratt-only-aware benchmark (2026-05-05)

Source: `wake-word/evaluation/benchmark_v19a_kratt_only_20260505.md` / `.csv`.
Cutoff shown: `0.99` (internal recommendation).

Important: under this target policy, single `Kratt`, reversed `Kratt kuule`, and phrases containing actual `Kratt` are positives, not hard negatives.

| test set | metric @0.99 | result |
|---|---:|---:|
| pos_isa_xtts_kuule_kratt | recall | 0/48 = 0.0% |
| pos_ode_kuule_kratt | recall | 1/11 = 9.1% |
| pos_friend1_kuule_kratt | recall | 0/145 = 0.0% |
| pos_mattias_short_kuule_kratt | recall | 66/362 = 18.2% |
| pos_single_kratt_neurokone | recall | 184/186 = 98.9% |
| pos_reversed_kratt_kuule | recall | 45/64 = 70.3% |
| neg_hard_mac_holdout | FPR | 0/15 = 0.0% |
| neg_hard_isa_xtts_target_free | FPR | 0/45 = 0.0% |
| neg_kuule_kule_confusables_target_free | FPR | 81/600 = 13.5% |
| faph_cv_et | FAPH | 0.79 |
| faph_librispeech | FAPH | 1.60 |
| faph_macbook_bg | FAPH | 5.99 |
| faph_dipco | FAPH | 0.00 |

Diagnostic sanity checks, not final held-out evidence:

- training-source cuts `positive_kratt_only_v19a/accepted`: 551/551 recall @0.99;
- exploratory real-voice `Kratt` cuts `positive_kratt_only_real_voice_probe_kguard/accepted`: 221/610 = 36.2% recall @0.99 (directory is not fully final-reviewed and includes eval-style speakers, so use only as a cutter/domain diagnostic).

## Interpretation

This first `Kratt`-only ablation learned the isolated generated `Kratt` cuts very strongly, but it does **not** generalize well to full two-word real/XTTS clips where the target word appears in phrase context. Ambient FAPH is encouraging on CV/LibriSpeech/DiPCo, but same-device Mac background remains non-trivial and target-free confusables still trigger 13.5% at the recommended cutoff.

Therefore this model is useful as diagnostic evidence for target-policy/data-window sensitivity, not as a demo/user-test replacement for `v16c`.

## Next step

Do not promote before critical-path user testing/writing. If this branch is revisited later:

- build and freeze `Kratt`-like target-free hard negatives (`kurat`, `kraam`, `kraan`, `kraad`, `ratas`, etc.);
- investigate why isolated `Kratt` cuts transfer poorly to full-phrase clips;
- evaluate on reviewed real-speaker `Kratt` cuts and frozen ambient/hard-negative sets only.
