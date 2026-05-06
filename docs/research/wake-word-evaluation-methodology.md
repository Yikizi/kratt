# Wake Word Detection - Evaluation Methodology Best Practices

**Status**: Reference document for thesis methodology chapter.  
**Compiled**: April 2026, from primary sources (Apple, Picovoice, Google, openWakeWord, microWakeWord, academic papers).  
Last updated: 2026-04-29  
**Purpose**: Define what "correct" evaluation looks like for the Kratt wake-word system, contrast with what we initially did wrong, and lock in defensible practices going forward.

## 0. 2026-04-29 addendum — current application to Kratt

The current thesis evaluation must use the following framing:

- `v16c` is a stable single-model baseline / active demo candidate, not a production-ready claim.
- v17 exposed a positive-label corruption incident; v18 showed clean labels are necessary but not sufficient.
- checkpoint-FAPH showed that optimizing ambient FAPH alone can collapse real-speaker recall.
- Final tables must report **FAPH + recall + hard/prefix/confusable FPR** together at frozen thresholds.
- Prefix/confusable regression sets are now part of the evaluation story; if a model family saw related sources during training, report that result as diagnostic rather than final independent holdout.

---

## 1. Core metrics: what to measure

Wake word detectors are binary classifiers, but the conventional ML metrics (accuracy, F1, AUC) can be misleading. The field has converged on a small set of metrics that reflect real deployment.

### 1.1 False Reject Rate (FRR)

The proportion of true wake-word utterances that the model fails to detect. Reported as a **percentage**.

- **Apple Siri**: targets <1% FRR for native speakers in the supported acoustic conditions ([Hey Siri](https://machinelearning.apple.com/research/hey-siri))
- **openWakeWord**: <5% FRR is considered "reasonable in practice" ([openWakeWord README](https://github.com/dscripka/openWakeWord))
- **Picovoice**: <0.3% FRR is the bar for a "successful" wake word ([Picovoice benchmarks](https://picovoice.ai/blog/wake-word-benchmarks/))

### 1.2 False Accept Rate (FAR / FAPH)

The number of times the model fires when the wake word is **not** spoken, normalized by exposure time. **Always report as false-accepts-per-hour, never as a percentage of clips.**

> "An important consideration for FAR is the unit of measurement. When evaluating FAR claims, you should ask for FAR per hour, as percentage is not a sensible unit of measurement for FAR."
> --- Picovoice

Why per-hour, not per-clip:
- A wake word system runs **continuously**. The relevant question is "how often does it falsely fire per unit time", not "what fraction of clips trigger it"
- Per-clip FPR depends on clip length: a 1-second clip and a 1-hour clip with the same per-clip FPR translate to vastly different user experiences
- Industry has standardized on FAPH (or FA/h or FAR/hour) for this reason

### 1.3 Industry FAR targets

| Source | Target | Notes |
|---|---|---|
| **Apple Siri (production)** | ~1 false-alarm per **week** (~0.006/h) | Sampled weekly across deployed devices |
| **Apple HEiMDaL (research)** | 12 FA/h on dense conversational speech | Worst-case stress test |
| **openWakeWord** | <0.5 FA/h | Considered "below annoyance threshold" |
| **Picovoice (production)** | <0.5 FA/h at fixed FRR | Used as the comparison point for benchmarks |
| **openWakeWord Hey Jarvis on DiPCo** | 0.187 FA/h | Achieved with the standard recipe |

**Implication for our work**: a model with FAPH ~50-150 (where v6, v8 currently sit on Common Voice ET) is far outside production-acceptable territory. v7 at 96 is still 192x worse than openWakeWord's target. The strict bar is one FA per several hours.

### 1.4 ROC / DET curves and operating point selection

Single-threshold metrics (e.g., FRR @ FAR=0.5/h) are operating points on an ROC curve. The standard practice is:

1. Generate the full ROC curve (FAR/FAPH vs. FRR) by sweeping threshold
2. Compute AUC as a threshold-independent quality measure
3. Pick the **deployment threshold** at the point where FRR is acceptable AND FAR is acceptable for the application
4. Report **both** the ROC and the chosen operating point

**Key warning**: don't tune the threshold on the test set. Tune on a validation set, then report the chosen threshold's performance on the held-out test set. We have NOT been doing this — our v6/v7/v8 reports use the same `threshold=0.97` chosen heuristically, but threshold should be data-driven.

---

## 2. Test set construction: the rules

This is where our initial v6 evaluation collapsed. Here are the rules we should have followed (and now do).

### 2.1 RULE: never measure on training data

> "The only way to really solve data leakage is to retain an independent test set and keep it held out until the study is complete and use it for final validation."
> --- MachineLearningMastery

This rule sounds obvious but is **especially easy to violate** with wake word datasets because the test sets and training negatives often come from the same corpus (Common Voice, MUSAN, LibriSpeech). If you score the model against `negative_samples/` from the experiment dir, that IS the training data. Our `compare_models.py` did exactly this.

**Mitigations**:
- **Disjointness assertion in code** (we now have `assert_disjoint_from_training()` in `evaluation/test_sets.py`) — a tripwire that fails CI if test files appear in training source dirs
- **Carve test sets at the FIRST step**, before splits or shuffles, so they cannot accidentally leak in
- **Use index-based splits** when sampling from a large corpus: e.g. legacy recipe
  "training uses CV ET indices 0-4999, evaluation uses 5000-7000". `faph_cv_et`
  stays a frozen legacy final-eval anchor from that recipe; CV ET 7000+ is a separate
  pool for mining/dev only.

### 2.2 RULE: positive test data must reflect deployment conditions

The positive test set must capture real-world variation that the model will face:

| Variation axis | Why it matters |
|---|---|
| **Different speakers** | Recall on the trained speaker is meaningless if the model is for general use |
| **Different microphones** | Each mic has its own frequency response, noise floor, distortion |
| **Different distances** | Far-field detection is dramatically harder than close-field |
| **Different acoustic environments** | Room reverb, background noise, music |
| **Different prosody** | Faster/slower speech, emphasis variations |

Apple's positive test data is recorded "in various conditions, such as in the kitchen (both close and far), car, bedroom, and restaurant." For our thesis, we should have:
- ✅ Multiple speakers (Mac Mattias + XTTS clones; **but** XTTS is synthetic — 4 voice-cloned speakers is not the same as 4 real speakers)
- ⚠️ Single microphone domain (KORVO-2 + Mac mic only)
- ❌ Distance variation not tested
- ❌ Background noise variation not systematically tested

### 2.3 RULE: negative test data must be hours long, not clips

For FAPH measurement to be statistically meaningful, you need **continuous audio** measured in hours, not seconds. This is because at FAPH ~1, a single false fire in 30 minutes vs. 60 minutes makes a 100% difference.

| Source | Negative test hours | Notes |
|---|---|---|
| **Apple Siri** | "thousands of hours" | Aiming at FA/week resolution |
| **openWakeWord (DiPCo)** | 5.5 hours | Far-field dinner-party conversations |
| **openWakeWord (full validation)** | ~11 hours | DiPCo + Santa Barbara + MUSDB |
| **Picovoice benchmark** | LibriSpeech test_clean | Hours of clean speech |
| **Our `faph_cv_et`** | ~3.65 hours raw / ~3.82 hours streaming track | Common Voice ET, frozen legacy untrained subset (indices 5000-7000); benchmark track includes 300 ms inter-clip silence |
| **Our `faph_dipco` (local)** | 3.32 hours | DiPCo eval-session subset (S01/S03/S06/S07/S08), not full 5.5h |

**Recommendation for thesis**: ~3.65 hours raw / ~3.82 hours after benchmark concatenation is on the low end. Should add at least one more long-form source (e.g., 10+ hours of Estonian podcast or news audio) to make FAPH stable. Even better: include English (out-of-language) negatives to test cross-language false fires.

### 2.4 RULE: hard negatives are a separate dimension

Hard negatives (phonetically similar phrases) test a different ability than general FAPH. A model can be great at one and bad at the other:

- **General FAPH** asks: does the model fire on random speech?
- **Hard negative FPR** asks: does the model fire on "kuule kraam" when the target is "kuule kratt"?

These are **separate test sets** and **separate metrics**. Don't average them.

### 2.5 RULE: test negative composition must reflect the threat model

If your wake word is for English-speaking smart homes, test with English speech, music, TV, kitchen sounds. If for an Estonian-language voice assistant, test with **Estonian** speech, plus likely background like radio, conversation, kitchen sounds.

**For the Kratt thesis**:
- ✅ Estonian speech (Common Voice ET) - in domain
- ⚠️ KORVO-2 ambient + MUSAN - in training, leaking
- ❌ TV/radio in Estonian - not tested
- ❌ Music - not tested  
- ❌ Multi-speaker conversation - not tested
- ❌ Children's voices - not tested

---

## 3. Training data: best practices

### 3.1 Positive data ratio and quantity

| Source | Positive samples | Comment |
|---|---|---|
| **openWakeWord Hey Jarvis** | ~200,000 synthetic | Multi-TTS with voice mixing |
| **microWakeWord (Okay Nabu)** | Similar order of magnitude, Piper-generated | |
| **Our v8** | ~2800 (TTS + KORVO + Mac + 3 XTTS speakers) | **2 orders of magnitude smaller** |

**Key insight**: industry KWS models use **hundreds of thousands** of synthetic positives. Our 2800 is tiny by comparison. The reason we get away with it is because we're testing on the same speaker/domain. For real generalization (and the unseen-speaker recall on Isa shows this) we need much more positive variation.

### 3.2 Negative data ratio and quantity

| Source | Negative hours | Sources |
|---|---|---|
| **openWakeWord** | ~31,000 hours | ACAV100M (10K) + Common Voice 11 (10K) + Podcastindex (10K) + FMA (1K) |
| **Apple Siri** | "thousands of hours" | Podcasts, multilingual Siri inputs, background |
| **Our v8 negatives** | ~5.6 hours (estimate from clip count × duration) | CV ET + KORVO-2 |

**Implication**: we have **5,000x less negative data** than openWakeWord. This is the single biggest gap and explains why our FAPH is so high. We are trying to discriminate "is this Kuule Kratt or not" but the model has only seen 5 hours of "not" examples.

**Realistic recommendation for the thesis**: we cannot generate 30,000 hours of negative data, but we can:
1. Add unused Common Voice ET (we have 27K validated clips, used 5K → 22K available = ~30 hours)
2. Add MUSAN speech subdir (we use noise; speech is unused, ~16h)
3. Add MUSAN music subdir (~42h)
4. Add reverberated versions of all of above
5. Add Podcastindex Estonian podcasts (free)
6. Add VOiCES dataset (already on HPC, ~20K clips)

Realistic ceiling: 100-200 hours of negatives. This is still 100x less than openWakeWord, but ~30x more than what we have now.

### 3.3 Augmentation: standard techniques

Industry-standard augmentations for wake word training:

1. **SpecAugment**: time masking + frequency masking on spectrograms. The single most-cited regularization for KWS. Kevin Ahrendt confirms microWakeWord uses it.
2. **Mixing positive with background noise** at random SNR (5-15 dB). openWakeWord does this.
3. **Reverberation** with simulated room impulse responses. openWakeWord uses BIRD IR dataset.
4. **Pitch shifting** (±2 semitones). audiomentations standard.
5. **Time stretching** (0.85-1.15x). audiomentations standard.
6. **Volume scaling** (random gain).
7. **Multi-TTS voice mixing**: blend multiple TTS speakers' embeddings to create novel synthetic voices (openWakeWord Hey Jarvis paper).

**Our v8 status**: We use audiomentations for time/pitch/noise/gain — covered. We do NOT use SpecAugment in v8 (we did in v7 — and v7 has the best FAPH). We do NOT use room impulse response convolution. We do NOT do multi-TTS voice mixing.

### 3.4 Hard negative mining (GraphemeAug)

[GraphemeAug paper](https://arxiv.org/html/2505.14814) (Google DeepMind, Interspeech 2025) shows the systematic approach:

1. Take the target keyword grapheme sequence
2. Generate confusables via:
   - **Insert**: add one grapheme at any position
   - **Delete**: remove one grapheme
   - **Substitute**: replace one grapheme with another of the same class (vowel↔vowel, consonant↔consonant)
3. Use TTS with style transfer to synthesize them
4. Add as hard negatives in training

**Key results**:
- Edit distance 3 (3 changes to the keyword) gives biggest improvement
- Models trained with 10,000 unique confusables > 10 unique confusables
- 61% AUC improvement on synthetic confusables, 54% on real confusables

**Critical caveat from Park et al. (2024)**: TTS hard negatives can fail because the model learns to detect TTS artifacts (98% TTS-vs-real classifier accuracy on hidden features) instead of phonetic content. **Style transfer or domain adversarial training is needed** to make the TTS examples actually teach phonetics.

**Our experience**: This is exactly what happened to us. v7's 6000 Neurokõne hard negatives improved FAPH (96 vs v6's 154) but did NOT improve hard negative discrimination on real-mic test set (still 80%). v8's 480 real Mac hard negatives DID improve hard neg discrimination (33%) but at the cost of FAPH regression. The lesson is: **real hard negatives are needed for real hard negative discrimination**, but you should keep the TTS hard negatives too because they help general FAPH (likely as additional regularization).

### 3.5 Class balance / sampling weights

microWakeWord and openWakeWord both upsample negatives heavily:
- `sampling_weight: 10.0` for negatives vs `2.0` for positives (5x oversampling)
- `negative_class_weight: 20` vs `positive_class_weight: 1` (20x loss weight on negatives)

Net effect: in practice the model sees ~100x more "weight" toward correctly classifying negatives than positives. This makes sense because in deployment, **>99.9% of audio is non-wake-word** — the model needs to be very confident before firing.

**Our setup uses these defaults**, which is correct. For v8 we added a third feature set for hard negatives with `sampling_weight: 4.0` and `penalty_weight: 3.0` — also reasonable.

### 3.6 Two-stage cascade detection

If single-model performance is insufficient, the standard industry trick is a two-stage cascade:

1. **Stage 1**: small, fast on-device model with relaxed threshold (high recall, high FPR)
2. **Stage 2**: larger verifier model that only runs when stage 1 fires (high precision)

Examples:
- **Apple HEiMDaL**: Cascaded detection + localization
- **Amazon Echo**: DNN-HMM stage 1 + small NN stage 2 (16% FRR reduction at fixed FAR)
- **openWakeWord**: Custom verifier models for personalization
- **microWakeWord on ESP32-S3**: supports up to 4 models running in parallel

**For our work**: this is a viable v10/v11 strategy. Stage 1 = small "kuule kr*" detector with cutoff 0.7. Stage 2 = "kratt vs kraam" discriminator with cutoff 0.97. Stage 2 only runs when stage 1 fires, so it doesn't add average compute.

### 3.7 VAD gatekeeper check (pre-routing only)

Silero VAD can be used as a *speech gate* in front of KWS, but it should be audited with hold-out data before we claim any recall/FAPH gains.

- For recall sets, measure:
  - speech coverage (% speech duration in each clip)
  - first-speech latency (ms from clip start)
  - how many clips have zero speech (hard recall floor for strict VAD gating)
- For ambient/FAPH sets, measure:
  - speech duty cycle (`speech_duration / total_duration`)
- Upper-bound FAPH math:
  - `faph_gated <= faph_raw × duty_cycle` (best case)
  - if duty cycle is 20%, even perfect gating cannot reduce FAPH by more than 80%
- Recall warning:
  - report `%` clips with no detected speech and `%` with very late first speech (e.g. >250ms), because both are potential recall-loss boundaries when hard-gating KWS.

Minimal script for this audit (no model scoring):

```bash
python wake-word/evaluation/benchmark_silero_vad_gate.py \
  --baseline-faph-csv wake-word/evaluation/benchmark_openwakeword_<timestamp>.csv \
  --baseline-model expert-a \
  --baseline-threshold 0.97
```

---

## 4. Threshold and probability cutoff

### 4.1 Default thresholds

| System | Default cutoff | Notes |
|---|---|---|
| openWakeWord | 0.5 | "Tune for your environment" |
| microWakeWord (ESPHome) | varies | Per-model `probability_cutoff` in manifest |
| Picovoice Porcupine | 0.5 (sensitivity scale) | User-tunable per-keyword |
| Our `compare_models.py` | 0.97 | Chosen heuristically; should be data-driven |

### 4.2 How to choose threshold properly

**Bad practice (what we did)**:
1. Run model on test data
2. Pick the threshold that gives nicest numbers
3. Report that threshold
This is silently fitting to the test set.

**Good practice**:
1. Train model
2. Use a **validation set** (not test) to compute ROC
3. Pick threshold at the point where: (a) FRR is below acceptable max, AND (b) FAPH is below acceptable max
4. Report that fixed threshold's performance on **test set**
5. Also report ROC AUC for threshold-independent comparison

**For our thesis**: we should redo the v1-v8 comparison by:
1. For each model, derive an operating point from a validation slice
2. Report the chosen threshold AND its FRR/FAPH on the held-out test set
3. Also report ROC AUC across all thresholds for fair comparison

### 4.4 Final thesis reporting contract

Final thesis claims must be conservative and explicit:

- Report **one declared operating threshold** and show all headline numbers at that same threshold:
  - streaming FAPH
  - recall
  - hard-negative FPR
- Never choose that threshold on the test set. Use **validation/dev** only, then apply the fixed threshold on held-out test. This is the only valid way to avoid optimistic bias.
- Treat small sample sizes as uncertainty, not precision:
  - small recall denominators (few positive test utterances) => report confidence interval or explicit "small-N" warning
  - short negative-hours or few false events for FAPH => report instability or CI rather than one-point certainty
- Do not compare metrics across incomparable thresholds/platforms. Our Android field runs use a different deployment threshold (often around `0.90`) than offline offline sweeps (`0.97` / `0.995`), so direct numeric comparison is invalid unless a recalibration mapping is explicitly provided.

### 4.3 Sliding-window averaging

In streaming inference, single-frame scores are noisy. Standard practice is to average over a sliding window:
- ESPHome `micro_wake_word`: configurable `sliding_window_size`
- openWakeWord: built-in moving average over inference scores
- Our `run_faph_test.py`: 5-frame moving average + 2-second refractory

**Refractory period** (cooldown after a fire) is important: without it, a single positive utterance can trigger multiple "activations" because the score stays high for several frames.

---

## 5. The biggest mistakes — a checklist

These are the failure modes most cited in industry blog posts and research papers. Mark which ones we made:

| Mistake | Description | Did we do it? |
|---|---|---|
| **Test on training data** | Reuse training negatives as eval | ✅ YES (v1-v8 reported numbers from same negs as training) |
| **No FAPH metric** | Only report clip-level FPR | ✅ YES until April 2026 |
| **No long-form ambient test** | Only short clips, no continuous audio | ✅ YES until April 2026 |
| **Threshold tuned on test set** | No separate val/test split | ⚠️ PROBABLY (we picked 0.97 by looking at outputs) |
| **Single mic domain** | All training and testing on one mic | ⚠️ PARTIALLY (KORVO-2 dominant) |
| **Single speaker dominant** | Training data mostly one voice | ✅ YES (Mattias dominant until v8) |
| **TTS-only positives** | Synthetic data shortcuts | ⚠️ PARTIAL (we have both TTS and real) |
| **TTS hard neg without style transfer** | Model learns TTS artifacts not phonetics | ✅ YES (Neurokõne v7 hard negs failed because of this) |
| **Class imbalance not addressed** | Equal weights for unequal classes | ❌ NO (we use sampling_weight + class_weight) |
| **No room impulse response augmentation** | Model has no reverb robustness | ✅ YES (we don't use RIR) |
| **No held-out cross-speaker eval** | Recall only on trained speaker | ✅ FIXED (we now have pos_isa_xtts and pos_mac_mattias) |
| **No held-out cross-device eval** | FPR only on trained mic | ⚠️ PARTIAL (Mac mic is held out for v1-v7) |
| **Treat clips as IID** | Ignore that streaming context matters | ✅ YES until run_faph_test.py |
| **Compare different test sets** | "v1 was 8%, v3 is 98%" on different sets | ✅ YES (acknowledged in thesis §2.X but original was on different sets) |
| **No statistical confidence intervals** | Single point estimates | ✅ YES (we don't compute CIs) |
| **No reproducible test set** | Random sampling at eval time | ✅ FIXED (test_sets.py is canonical now) |

**Score: 12 out of 16 mistakes made.** The good news: we've identified them all and fixed most. The thesis methodology section should explicitly walk through these and how they were addressed.

---

## 6. Recommended methodology for the Kratt thesis

Based on the above, here's the corrected methodology that should go into the thesis:

### 6.1 Test set design

Three categories of disjoint hold-out sets:

1. **Positive recall sets**:
   - `pos_isa_xtts` (48 clips) — primary cross-version unseen-speaker recall benchmark
   - `pos_mac_mattias` (30 clips) — cross-device recall benchmark for v1-v7
   - **Add**: `pos_korvo2_holdout` — Mattias re-records 50-100 fresh clips with deliberate variation (distance, prosody, time of day) and these are NEVER touched in training
   
2. **Hard negative discrimination sets**:
   - `hard_neg_mac_holdout` (15 clips, Mac mic, real)
   - `hard_neg_isa_xtts` (60 clips, voice-cloned)
   - **Add**: `hard_neg_korvo2_holdout` — record the same 100 phrases on KORVO-2 mic
   
3. **Long-form FAPH sets** (each measured separately, never averaged):
   - `faph_cv_et` (~3.65h raw, ~3.82h streaming track with 300 ms gaps, in-domain Estonian) — primary
   - `faph_dipco` (3.32h, DiPCo eval sessions S01/S03/S06/S07/S08 only) — primary frozen final-eval split
   - `faph_dipco` mining/dev sessions (S02/S04/S05/S09/S10) are intentionally disjoint from final-eval sessions.
   - `faph_korvo2_holdout` (~30 min, same-device, fresh recording) — primary same-device
    - **Add**: `faph_estonian_podcast` (10+ hours, free podcasts not in training)
   - **Optionally**: `faph_voices` (English, cross-language test)
   - **Optionally**: `faph_musan_music` (music robustness test)

### 6.2 Reporting protocol

For each model version, report:

1. **ROC AUC** on a fixed hold-out set (threshold-independent quality)
2. **FRR @ FAPH=1.0/h** (a fixed operating point — what's the recall at the deployment-acceptable FAR)
3. **FRR @ FAPH=0.5/h** (the openWakeWord target)
4. **FAPH @ FRR=5%** (the dual: at acceptable recall, what's the actual false-fire rate)
5. **Per-condition breakdowns**: same-device, cross-device, cross-speaker, hard-neg

### 6.3 Statistical considerations

- Report **clip counts** for every metric
- For small test sets (<100 clips), report **Wilson 95% confidence interval**
- For FAPH, report **total exposure hours** along with the rate

### 6.4 Reproducibility

- Test sets defined in code (`evaluation/test_sets.py`) with explicit paths
- `assert_disjoint_from_training()` checks at every evaluation
- All numbers in CSV (`model_comparison_holdout.csv`) regenerable from the same script
- Random seeds documented (e.g. `seed=42` for Common Voice shuffle)

---

## 7. Historical planning notes for v9 and beyond

> **Historical note (2026-04-29):** this section preserves the April planning logic that led to v9+ experiments. It is not current training guidance. Current guidance is in `docs/PROJECT_TODO.md`, `docs/research/source-of-truth-apr-2026.md`, `wake-word/DATA_STRATEGY.md`, and `wake-word/docs/MODEL_LINEAGE.md`.

Based on the research, here's the specific recipe v9 should test:

### v9: balanced FAPH + hard neg discrimination

- **Positives**: v8 set (Mattias mic1+mic2+TTS+SSML+Mac+3 XTTS) — keeps speaker diversity
- **Negatives**: v8 set (CV + KORVO-2 + MacBook segmented) — adds fresh negatives
- **Hard negatives** (separate feature set):
  - v8 reals (Mac aug + 3 XTTS speakers)
  - **plus** Neurokõne TTS hard negatives v1+v2 (this was v7's secret sauce — `--tts-hard-neg-in-hard-set` flag)
- **SpecAugment**: ON (`--spec-augment` flag, this is v7's other secret sauce)
- **Architecture**: same MixConv as v6/v7/v8 (no changes)

This is essentially "v7 retsept + v8 real hard negatives". The hypothesis: it should achieve v7-level FAPH (~96) AND v8-level hard neg discrimination (~33%).

### v10 ideas (further experiments)

- **More general negatives**: add MUSAN speech + music + Estonian podcast scrape (100+ hours total)
- **Room impulse response augmentation**: convolve all negatives with random RIRs from BIRD or MIT IR dataset
- **Multi-TTS voice mixing**: blend XTTS speaker embeddings to create synthetic novel voices
- **Two-stage cascade**: train a "kuule kr*" coarse detector + "kratt" verifier
- **GraphemeAug systematic confusables**: generate edit-distance-3 variants of "kuule kratt" (we had ad-hoc confusables, GraphemeAug is the systematic way)

### v11+ deterministic false-trigger mining (new)

Randomly waiting for false activations is too slow and non-reproducible. We now add a deterministic adversarial mining loop.

1. **Generate parameterized non-speech rhythms** (tap-like impulse trains, tonal/noise pulses) on a fixed cartesian grid.
2. **Score with the live pipeline itself** (same frontend + streaming TFLite path as `live_test_tflite.py`).
3. **Rank by max probability and threshold crossings** and export top-K trigger clips.
4. **Promote top triggers to a permanent red-team holdout set** for every new model.

Implementation:
- Script: `wake-word/evaluation/deterministic_trigger_fuzzer.py`
- Output: `fuzzer_results.csv`, `summary.json`, and `top_triggers/*.wav`
- Determinism: fixed seed + hash-derived per-candidate seeds for reproducible clips.

Suggested release gate:
- For deployment thresholds (e.g. 0.97/0.98/0.99), report:
  - number of mined triggers with max score >= threshold,
  - detections per clip with deployment cooldown,
  - held-out positive recall.
- A new model should not be promoted unless mined-trigger counts improve without unacceptable recall loss.

---

## 8. Key sources

Primary sources cited above:

- [Apple - Hey Siri ML Research](https://machinelearning.apple.com/research/hey-siri)
- [Apple - HEiMDaL](https://machinelearning.apple.com/research/heimdal)
- [Picovoice - Wake Word Benchmarks 2025](https://picovoice.ai/blog/wake-word-benchmarks/)
- [Picovoice - Wake Word Detection Guide 2026](https://picovoice.ai/blog/complete-guide-to-wake-word/)
- [openWakeWord README](https://github.com/dscripka/openWakeWord)
- [openWakeWord features dataset](https://huggingface.co/datasets/davidscripka/openwakeword_features)
- [microWakeWord GitHub](https://github.com/OHF-Voice/micro-wake-word)
- [microWakeWord HF dataset](https://huggingface.co/datasets/kahrendt/microwakeword)
- [Kevin Ahrendt - microWakeWord blog](https://www.kevinahrendt.com/micro-wake-word)
- [GraphemeAug paper (Interspeech 2025)](https://arxiv.org/html/2505.14814)
- [Park et al. - Adversarial training of KWS to minimize TTS data overfitting (ICASSP 2024)](https://arxiv.org/html/2408.10463v1)
- [Amazon - Monophone-based Background Modeling for Two-Stage WW Detection](https://www.amazon.science/publications/monophone-based-background-modeling-for-two-stage-on-device-wake-word-detection)
- [Mining Effective Negative Training Samples for KWS - Microsoft Research](https://www.microsoft.com/en-us/research/publication/mining-effective-negative-training-samples-for-keyword-spotting/)
- [Towards more robust KWS for voice assistants (USENIX 2022)](https://www.usenix.org/system/files/sec22summer_ahmed.pdf)
- [Advances in Small-Footprint KWS Review 2025](https://arxiv.org/html/2506.11169v1)
- [Speech Commands Dataset (Google)](https://huggingface.co/datasets/google/speech_commands)
- [DiPCo - Dinner Party Corpus](https://arxiv.org/pdf/1909.13447)
