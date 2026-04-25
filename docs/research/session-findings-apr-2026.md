# Session Findings: April 5-13, 2026

Extracted from Claude Code session `a21420ac-d1eb-4574-b29e-68856290793c` (kratt-log).
Covers sprint from April 5 (v8 planning) through April 13 (expert MoE breakthrough).

---

## 1. Methodology Discoveries

### 1.1 FAPH Measurement Was Wrong (Fixed April 7)

The clip-level FPR metric used for v1-v9 evaluation was **not** streaming FAPH. The canonical method uses `microwakeword.test.compute_false_accepts_per_hour` with:
- `sliding_window=5` (50ms moving average)
- `cooldown=200` slices (2s refractory period)
- Single concatenated audio stream (not per-clip max scores)

Per-clip FPR on training data gave misleadingly low numbers due to data leakage: clips used in training were also used for evaluation. All thesis tables referencing old clip-level FPR are invalid and need replacement with canonical streaming FAPH.

**Commit**: `6e76e0a fix(eval): canonical streaming FAPH via microwakeword.test function`

### 1.2 Benchmark Does Not Predict Real-World Performance

The most important finding of the entire sprint:

| Model | FAPH (CV ET bench) | FAPH (MacBook bg) | IRL usability |
|-------|-------------------|-------------------|---------------|
| v6-residual | 11.5 | **3.4** | Unusable (100% hard neg FPR) |
| v15 | **216.2** | 45.4 | **Best IRL balance** (73% recall, 20% HN) |
| v10 | 20.4 | 4.3 | Good HN rejection but 45% FRR |

**v15 was worst on bench but best in real life.** The CV ET benchmark measures sensitivity to random Estonian speech, not selectivity against confusable phrases. Real-world performance depends on hard negative rejection, which the standard bench does not capture.

Reference: Dubois et al. (2020) tested production smart speakers with real TV audio and found "internal benchmarks never matched customer experience" -- exactly our problem.

### 1.3 Test Set Is Statistically Useless

With only 11 test clips from one speaker (ode/sister):
- 7/11 recall 95% CI: **[30.8%, 89.1%]** -- essentially meaningless
- FAPH 0.8 @ 3.8h CI: [0.16, 2.30]
- Minimum needed: **100+ clips per condition**, 20+ hours negative audio for tight FAPH CI

### 1.4 Three-Metric Evaluation Required

Single FAPH is insufficient. Need to report:
1. **FAPH** (false accepts per hour on ambient/speech)
2. **Recall** (detection rate on real speakers at deployment threshold)
3. **Hard negative FPR** (rejection rate of confusable phrases)

These three are often in fundamental conflict for a 22K-parameter model. Standard in literature: report FRR @ fixed FA/h operating point, hard neg FPR in separate table.

---

## 2. Model Results Summary

### 2.1 Pure Ablation: Residual Connections (-37% FAPH)

First and only clean single-variable ablation in the project. Exact same v6 dataset, only `residual_connection: 0,0,0,0` -> `1,1,1,1`.

| Threshold | v6 (baseline) | v6-residual | Change |
|-----------|--------------|-------------|--------|
| 0.9 | 60.2 | 28.8 | -52% |
| 0.95 | 43.2 | 23.8 | -45% |
| 0.97 | 36.4 | 21.2 | -42% |
| 0.99 | 24.3 | 16.2 | -33% |
| 0.995 | 21.2 | **13.4** | **-37%** |

### 2.2 Pure Ablation: SpecAugment (-33% FAPH on v10 data)

v13a (SA OFF) vs v13b (SA ON), both on v10 dataset with residual ON and 421 mined negatives:

| | v13a (SA OFF) | v13b (SA ON) |
|---|---|---|
| FAPH @0.995 | 113.6 | **75.6** (-33%) |

Note: SA was only tested on v10 dataset (which performed poorly overall). v6-dataset SA ablation was never performed cleanly.

### 2.3 Hard Negative Ratio

| Model | Hard neg ratio | FAPH @0.995 | Recall @0.9 | HN FPR @0.9 |
|-------|---------------|-------------|-------------|-------------|
| v6 | 16% | 21.2 | 100% | 65% |
| v10 | **46%** | 20.4 | 92% | **40%** |
| v14 | **18%** | 120.7 | 100% | 18.5% (worse) |
| v15 | 27% | 216.2 | -- | -- |

Literature (microWakeWord internal, Hou et al.): optimal is 10-20% hard neg by count, 2-4x sampling weight for 20-40% gradient contribution. Our v10 at 46% was too high.

### 2.4 Residual + Hard Neg Interaction

Critical discovery: residual connections interact badly with hard negatives.

| Config | FAPH @0.995 |
|--------|-------------|
| v6 (no residual, no hard neg v2) | 21.2 |
| v6-residual (residual ON, no hard neg v2) | **13.4** |
| v13b (residual ON, v10 data + mined neg, SA ON) | 75.6 |
| v15 (residual ON, +1500 hard neg v2) | **216.2** |

Residual makes the model "too good" at learning phonetic patterns. With hard negatives, it over-discriminates and loses general robustness.

### 2.5 MoE Consensus Architecture

No single 22K-parameter model can simultaneously achieve low FAPH, high recall, and low hard neg FPR. Solution: **Mixture of Experts consensus**.

**Early consensus (v10+v15):**
- FAPH: 6.8, Recall: 7/11, HN Mac: 7%, Android: 8%

**Expert A + Expert B v2 (purpose-trained):**

| Config | FAPH CV | FAPH Mac | Recall (ode) | HN Mac | Android |
|--------|---------|----------|--------------|--------|---------|
| @0.996/0.996 | **0.79** | 0.0 | 5/11 | 13% | 4% |
| @0.997/0.997 | **0.80** | 0.0 | 5/11 | 7% | 4% |
| @0.990/0.990 | 1.8 | 0.0 | 5/11 | 20% | 4% |
| @0.970/0.970 | 4.7 | 0.0 | 5/11 | 27% | 4% |

**v6-residual + Expert B v2:**
- @0.997/0.997: **0.52 FAPH** (best absolute), recall 3/11

**Sub-1 FAPH achieved** -- first time in project. Expert A (gatekeeper, 96 filters, residual ON, no hard neg) + Expert B v2 (verifier, 48 filters, SA ON, 80% hard neg + 20% general neg) = 0.79 FAPH @ 0.996/0.996.

### 2.6 Expert Architecture Design

**Expert A (Gatekeeper):**
- Goal: "Is this speech that resembles the wake word?" (low FAPH)
- Positives: 1076 (real mic only -- NO TTS to avoid TTS overfitting)
- Negatives: ~9560 (CV ET + KORVO-2 + MacBook + mined false accepts, 0% hard neg)
- Architecture: 96 filters, residual ON, SpecAugment OFF
- Size: 148KB

**Expert B v2 (Verifier):**
- Goal: "Is this EXACTLY kuule kratt, not kuule rott?" (low hard neg FPR)
- Positives: ~3343 (mic + TTS + XTTS + SSML -- diverse voices)
- Negatives: ~5045 (80% hard neg + 20% general neg -- not 100%, that failed in v1)
- Architecture: 48 filters, residual OFF, SpecAugment ON
- Size: 55KB

Expert B v1 (100% hard neg, 0% general) failed catastrophically -- 1482 FAPH, triggered on everything. Adding 20% general negatives (1000 clips) fixed it: FAPH dropped to 42.7, HN Mac dropped from 100% to 13%.

### 2.7 ex2a Failure: TTS Overfitting in Gatekeeper

Adding all TTS/XTTS positives to Expert A made it WORSE:
- expert-a (mic-only): 9/11 recall, 25.6 FAPH
- ex2a (all pos, 72% TTS): 5/11 recall, 78.5 FAPH

TTS dominance in positives caused the model to learn TTS artifacts as "positive" features. Park et al. 2024 TTS overfitting confirmed. Real voices must dominate positives (>70%).

---

## 3. Critical Bugs Found

### 3.1 Augmentation Was Nearly Disabled

All training runs v1-v15 used:
```
PitchShift: p=0.05 (5%)     -- should be 0.3-0.5
SevenBandParametricEQ: p=0.05 -- should be 0.2-0.3
AddBackgroundNoise: p=0.0    -- should be 0.5+
RIR (room impulse response): p=0.0 -- should be 0.3
```

Speaker-diversifying augmentation was essentially off. This is likely the primary cause of single-speaker overfitting and poor recall on new voices.

### 3.2 negative_class_weight=20 Is Extreme

`negative_class_weight: 20` combined with `sampling_weight: 10` gives ~100x combined negative emphasis. microWakeWord default is `negative_class_weight: 1`. Value of 20 was copied from a notebook example designed for datasets with 1000+ speakers.

Recommended fix: `negative_class_weight: 5`.

### 3.3 Training Steps Too Few

All models trained with 10,000 steps. Literature and microWakeWord examples use 30,000-60,000. Larger models (96 filters) likely underfit at 10K.

microWakeWord supports multi-phase LR natively:
```yaml
training_steps: [15000, 5000]
learning_rates: [0.001, 0.0001]
```

### 3.4 No LR Schedule

Single constant LR=0.001 for all models. Should use multi-phase: warmup + decay.

### 3.5 MUSAN Nested Glob Bug

`prepare_kuule_kratt_experiment.py` used `glob("*.wav")` (non-recursive) for MUSAN speech/music directories. These have nested subdirectories (`speech/librivox/`, `music/fma/`), so **0 files** were actually included in v10 despite logs suggesting otherwise.

v10's "MUSAN advantage" was illusory -- it succeeded for other reasons.

### 3.6 Riigikogu shuf Failure (v11)

```bash
shuf --random-source=<(echo 42) | head -n 50
```
`echo 42` provides only 3 bytes of entropy. GNU `shuf` needs more for 1001 items, fails silently. Result: empty Riigikogu subset, v11 trained without the new data. Compounded by FLAC glob issue (script only globbed `*.wav`, Riigikogu files are FLAC).

### 3.7 openWakeWord Pipeline Crashes (10+)

Sequential failures during openWakeWord training attempts:
1. Piper TTS import (even when `--generate_clips` not used)
2. Sample rate mismatch (22050Hz files not resampled)
3. OOM on GPU (augmentation_batch_size=500 too large)
4. batch_n_per_class type error (integer vs dict)
5. false_positive_validation_data_path format mismatch
6. Empty negative_test directory (StopIteration)
7. Stale cached features from crashed runs
8. Resource model download failures
9. Symlinks overwriting resampled files on resubmit
10. PartitionTimeLimit on HPC short partition

---

## 4. Research References & Findings

### Papers Cited/Discovered

| Paper | Key Finding | Relevance |
|-------|------------|-----------|
| **Park et al. 2024** (Google) | TTS overfitting: KWS learns TTS artifacts, 98% accuracy distinguishing synth vs real in hidden layers | Explains ex2a failure, validates multi-TTS strategy |
| **Hou et al. 2020** (Microsoft, ICASSP) | Regional Hard-Example Mining: 45-58% FRR reduction | Validates our mined false accepts approach |
| **Zhang et al. 2025** (Google, Interspeech) | GraphemeAug: systematic confusable generation, 61% AUC improvement | Not yet implemented, next step |
| **Dubois et al. 2020** | Bench does not predict real-world for smart speakers | Exactly our finding |
| **Alvarez et al. 2024** (Google) | 100+ speakers minimum for good recall | We have 1 speaker -- root cause of recall issue |
| **Deka et al. 2025** | VTLP (Vocal Tract Length Perturbation) significantly helps speaker diversification | Not implemented, highest priority |
| **Felzenszwalb et al. 2010** | Hard negative mining (11K+ citations) | Theoretical foundation for our mining approach |
| **Lin et al. 2017** | Focal Loss: implicit hard example focus | Better than class weighting for KWS |
| **Choi et al. (BC-ResNet)** | 96.9% accuracy with 9.2K params via residual connections | Validates our residual finding |
| **Kundu et al. (Apple HEiMDaL)** | Two-stage: primary DNN (12 FAPH) -> Conformer re-scorer -> 0.006 FAPH | Validates our MoE approach |
| **Lin et al. 2020** (Google, ICASSP) | Multi-speaker TTS augmentation improves KWS on real speech | Validates multi-engine TTS |

### Key Numerical References

| System | FA/h | FRR | Test Corpus |
|--------|------|-----|------------|
| microWakeWord okay_nabu | 0.187 | <5% | DiPCo 5.5h |
| Picovoice "alexa" | 0.1 | ~5% | LibriSpeech 5.4h |
| Google "OK Google" | 0.133 | 1.81% | Internal |
| **Our Expert A+B2** | **0.79** | ~55% (5/11) | CV ET 3.8h |

---

## 5. Tools & Infrastructure Built

- `multi_model_live_test.py` -- parallel inference of N models on same mic, consensus logic, JSONL logging
- `kratt live` multi-model mode -- `kratt live v10 v15 0.97` with Swift overlay consensus trigger
- `generate_det_curve.py` -- DET curves and operating point tables for all models
- `compare_models.py` updated with FAPH, recall, hard neg FPR columns
- `model_evaluation_results.json` -- comprehensive results database
- Android false trigger logger (277 mined clips from 36h deployment)
- Augmentation pipeline fix (PitchShift/EQ/BGNoise/RIR settings)
- Training script default changed: `residual_connection: 1,1,1,1` always ON

---

## 6. Key Decisions Made

1. **v6-residual is best single model** for FAPH (3.4 MacBook) but unusable alone (100% hard neg FPR)
2. **MoE consensus is the path forward** -- no single model can do all three metrics
3. **Expert A+B2 @ 0.996 = 0.79 FAPH** is the current best deployment config
4. **Recall 5/11 is not acceptable** for deployment, needs 5-10 real speakers
5. **All future training must use fixed augmentation** (PitchShift 0.4, BGNoise 0.5, RIR 0.3)
6. **negative_class_weight should be 5** (not 20)
7. **Training steps should be [15000, 5000]** with LR schedule
8. **openWakeWord comparison** still in scope but pipeline has persistent bugs
9. **Scenario test stream** (2h annotated real-world audio) needed for proper eval

---

*Generated 2026-04-13 from session a21420ac-d1eb-4574-b29e-68856290793c*
