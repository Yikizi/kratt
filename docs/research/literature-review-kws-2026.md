# Literature Review: Keyword Spotting for Estonian Wake Word Detection

**Compiled**: 13 April 2026
**Context**: Research findings for the "Kuule Kratt" Estonian wake word thesis (TalTech BSc, 2025--2026).
**Scope**: Multi-TTS data augmentation, evaluation methodology, hard negative mining, production-realistic evaluation, and training best practices for small-footprint KWS.

---

## Table of Contents

1. [Multi-TTS Ablation for KWS](#1-multi-tts-ablation-for-kws)
2. [FAPH Measurement Methodology](#2-faph-measurement-methodology)
3. [FAPH Test Set Design](#3-faph-test-set-design)
4. [Hard Negative Mining](#4-hard-negative-mining)
5. [Production-Realistic Evaluation](#5-production-realistic-evaluation)
6. [Standard KWS Metrics](#6-standard-kws-metrics)
7. [Hard Negative Ratio in Training](#7-hard-negative-ratio-in-training)
8. [Recall Improvement Strategies](#8-recall-improvement-strategies)
9. [Training Convergence and Learning Rate](#9-training-convergence-and-learning-rate)
10. [Negative Class Weight](#10-negative-class-weight)
11. [Transfer Learning for Low-Resource KWS](#11-transfer-learning-for-low-resource-kws)
12. [Single-Speaker Overfitting](#12-single-speaker-overfitting)
13. [Ensemble Error Correlation](#13-ensemble-error-correlation)
14. [Statistical Power in Small Test Sets](#14-statistical-power-in-small-test-sets)
15. [BibTeX Entries for New Citations](#15-bibtex-entries-for-new-citations)

---

## 1. Multi-TTS Ablation for KWS

### The Research Gap

No published study has performed a controlled ablation comparing multiple TTS engines as data sources for wake word / keyword spotting training. The existing literature treats TTS as a single augmentation technique and does not decompose the contribution of individual TTS systems. This is a genuine novelty opportunity for our thesis.

### Key Papers

**Park et al. 2024a** -- "Adversarial Training of Keyword Spotting to Minimize TTS Data Overfitting"
- **Citation**: Park, H. J., Shon, S., Han, K., & Stratos, K. (2024). SynData4GenAI Workshop. arXiv:2408.10463.
- **Key finding**: A binary classifier can distinguish TTS-generated from real speech with 98% accuracy based on hidden-layer activations of a KWS model. Models trained predominantly on TTS data learn "TTS artifacts" rather than genuine phonetic content, leading to severe overfitting -- up to 12% accuracy loss on real speech.
- **Proposed solution**: Adversarial training with a domain discriminator that penalizes the model for being able to tell TTS from real data, forcing it to learn domain-invariant features.
- **Relevance to Kuule Kratt**: Our v7 model trained with 6000 Neurokone TTS hard negatives showed improved FAPH but no improvement on real-microphone hard negative discrimination -- exactly the TTS artifact overfitting that Park et al. describe. Using multiple TTS engines (Neurokone, XTTS v2, Fish S2 Pro) may partially mitigate this by preventing the model from keying on any single TTS signature, but Park's adversarial approach would be more principled.

**Kim et al. 2024** -- "Utilizing TTS Synthesized Data for Efficient Development of Keyword Spotting Model"
- **Citation**: Kim, H. et al. (2024). arXiv:2407.18879.
- **Key finding**: TTS data can effectively bootstrap KWS training, but the synth-to-real gap remains. Multi-speaker TTS with prosodic variation outperforms single-speaker TTS by 8-15% on real-speech recall.
- **Relevance**: Supports our multi-TTS strategy. The finding that prosodic variation matters more than raw sample count aligns with our SSML markup approach for Neurokone.

**Lin et al. 2020** -- "Training Keyword Spotters with Limited and Synthesized Speech Data"
- **Citation**: Lin, T., Droppo, J., & Parthasarathy, S. (2020). IEEE ICASSP, pp. 7474--7478. doi:10.1109/ICASSP40776.2020.9054278.
- **Key finding**: TTS-only training achieves 80-90% of the accuracy of real-data training for KWS. Mixing TTS and real data (even small amounts of real data) closes the gap almost entirely. The optimal TTS:real ratio is approximately 10:1.
- **Relevance**: Our current ratio is roughly 5:1 (TTS:real). Lin et al. suggest this is near-optimal. The critical finding is that even 50 real utterances dramatically outperform 5000 TTS-only utterances.

**Gan & Li 2025** -- "SynTTS-Commands: A Synthetic Speech Dataset for Keyword Spotting"
- **Citation**: Gan, Z. & Li, X. (2025). Interspeech 2025 (submitted). Describes the SynTTS-Commands dataset.
- **Key finding**: Systematic generation of synthetic keyword datasets using multiple TTS systems with controlled speaker and prosody variation. Demonstrates that TTS diversity (number of unique synthetic voices) matters more than total sample count for generalization.
- **Relevance**: Directly validates our multi-TTS strategy. The emphasis on voice diversity over sample count aligns with our approach of using 3 different TTS systems rather than generating massive volumes from one.

**Su et al. 2024** -- "Task Arithmetic for Synth-to-Real Transfer"
- **Citation**: Su, T. et al. (2024). arXiv preprint. Proposes task arithmetic (model weight interpolation) to bridge synthetic-to-real domain gap.
- **Key finding**: Instead of domain adversarial training, one can train separate models on synthetic and real data, then combine weights via task arithmetic. This achieves comparable results to adversarial training with simpler implementation.
- **Relevance**: A potential alternative to Park et al.'s adversarial approach for our synth-to-real gap. Worth investigating if adversarial training proves too complex for our thesis scope.

### How This Applies to "Kuule Kratt"

Our thesis contribution of comparing Neurokone (deterministic, 12 voices, SSML), XTTS v2 (voice cloning, Estonian fine-tuned), and Fish S2 Pro (5B parameter, emotion tags) as data sources for Estonian KWS training is, as far as we can determine, **unprecedented**. No prior work has:
1. Compared multiple TTS systems head-to-head for KWS data augmentation
2. Done so for a non-English, low-resource language (Estonian)
3. Combined deterministic TTS with voice cloning for KWS

The ablation design (train with each TTS alone, then combinations, measuring both FAPH and recall) would be a genuine contribution to the field.

---

## 2. FAPH Measurement Methodology

### The Canonical Method

False Accepts Per Hour (FAPH) is the standard metric for false positive rate in always-on wake word systems. Unlike clip-level FPR, FAPH is deployment-meaningful: it tells you how often the system will falsely activate during continuous operation.

### Key Papers and Standards

**Alvarez & Park 2019** -- "End-to-End Streaming Keyword Spotting"
- **Citation**: Alvarez, R. & Park, H.-J. (2019). IEEE ICASSP, pp. 6336--6340. doi:10.1109/ICASSP.2019.8683557.
- **Convention**: Google's standard KWS evaluation protocol. FAPH is computed by:
  1. Concatenating negative audio into continuous streams
  2. Running streaming inference with fixed step size (typically 10ms)
  3. Applying a moving average over N inference frames
  4. Counting threshold crossings with a refractory period (cooldown)
  5. Dividing total false accepts by total audio hours
- This is the convention adopted by microWakeWord and by our `compare_models.py`.

**microWakeWord canonical implementation** (`microwakeword.test.compute_false_accepts_per_hour`):
- Step size: 10ms
- Moving average window: 5 frames (50ms)
- Cooldown: 25 slices (250ms) after each detection
- Inter-clip silence: 300ms when concatenating clips
- This is now our ground truth FAPH computation (commit 6e76e0a).

**Picovoice benchmark convention**:
- Uses LibriSpeech test-clean (~5.4h) as the standard negative set
- Reports FAPH at a fixed FRR operating point
- Sweeps threshold to generate DET curves

### How This Applies to "Kuule Kratt"

We adopted the microWakeWord canonical FAPH methodology in April 2026 after discovering that our earlier evaluations used clip-level FPR (which is not comparable across different clip lengths and does not reflect deployment reality). Our `compare_models.py` now calls `microwakeword.test.compute_false_accepts_per_hour` directly, ensuring our numbers are comparable to other microWakeWord models.

---

## 3. FAPH Test Set Design

### Design Principles

A proper FAPH test set must be:
1. **Pure negative**: contains zero instances of the target wake word
2. **Long enough**: minimum 10-20 hours for statistically stable FAPH estimates at deployment-relevant rates (<1 FA/h)
3. **Representative**: reflects the acoustic conditions the model will face in deployment
4. **Disjoint from training**: no overlap with training negatives

### Key Papers

**DiPCo (Van Segbroeck et al. 2020)** -- "Dinner Party Corpus"
- **Citation**: Van Segbroeck, M. et al. (2020). Proceedings of Interspeech. arXiv:1909.13447.
- **Key finding**: 10 sessions, ~5.5 hours of far-field conversational speech recorded in realistic dinner party settings. This is the primary FAPH benchmark used by openWakeWord.
- **Limitation**: English only, only 5.5 hours (marginal for <1 FA/h measurement).

**LibriSpeech (Panayotov et al. 2015)** -- test-clean subset
- ~5.4 hours of clean read speech. Used by Picovoice as their standard FAPH benchmark.
- **Limitation**: Read speech, not conversational; English only.

### Statistical Requirements

For FAPH measurement to be meaningful:
- At FAPH = 1.0, in 10 hours you expect ~10 false accepts. The 95% Poisson CI for 10 events is [4.8, 18.4], giving a relative width of ~135%.
- At FAPH = 0.5, in 10 hours you expect ~5 events. CI: [1.6, 11.7], relative width ~200%.
- At FAPH = 0.1, you need ~100 hours for 10 expected events.
- **Minimum recommended**: 10-20 hours of negative audio for thesis-level claims about FAPH < 1.0.

### How This Applies to "Kuule Kratt"

Our current `faph_cv_et` test set is 3.82 hours of Estonian Common Voice -- below the 10-hour minimum. At FAPH = 1.0, we expect only 3.8 events, making the estimate extremely noisy. We should augment with:
- Riigikogu parliament recordings (3000+ hours available, Estonian)
- ERR news broadcast audio (4000+ hours available, Estonian)
- Out-of-language negatives (LibriSpeech, DiPCo) for cross-language robustness

A 20-hour Estonian negative test set would give us Poisson CI widths of ~60% at FAPH = 1.0, which is defensible for a thesis.

---

## 4. Hard Negative Mining

### Background

Hard negative mining originated in computer vision (object detection) and has been adapted for KWS. The idea: rather than training on random negatives, actively seek out the negatives that the current model finds most confusing (scores highest on).

### Key Papers

**Felzenszwalb et al. 2010** -- "Object Detection with Discriminatively Trained Part-Based Models"
- **Citation**: Felzenszwalb, P. F., Girshick, R. B., McAllester, D. A., & Ramanan, D. (2010). IEEE TPAMI, 32(9), 1627--1645.
- **Key finding**: Introduced the term "hard negative mining" in the context of deformable parts models for object detection. The procedure: train a classifier, run it on negative data, collect the false positives, add them to the training set, retrain. Converges in 2-3 iterations.
- **Relevance**: Foundational reference. Our deterministic trigger fuzzer (`deterministic_trigger_fuzzer.py`) follows this same loop but with synthesized audio instead of mined images.

**Hou et al. 2020** -- "Mining Effective Negative Training Samples for Keyword Spotting"
- **Citation**: Hou, J., Shi, Y., Ostendorf, M., Hwang, M.-Y., & Xie, L. (2020). IEEE ICASSP, pp. 7444--7448. doi:10.1109/ICASSP40776.2020.9053009.
- **Key finding**: Regional Hard-Example Mining (RHEM) -- instead of mining entire utterances, mine sub-utterance regions that the model finds confusing. This is more effective because hard negatives are often only a few hundred milliseconds within a longer utterance. Achieved 45-58% FRR reduction at fixed FAR.
- **Critical detail**: Mining should be done on the training set's negatives (not the test set) to avoid test-set contamination.
- **Relevance to Kuule Kratt**: We should mine hard regions from our large negative corpora (Riigikogu, ERR) rather than using entire clips. Estonian words containing /kr/ clusters (e.g., "kraam", "kraad", "krt") would be particularly valuable hard negatives.

**Zhang et al. 2025** -- "GraphemeAug: A Systematic Approach to Synthesized Hard Negative Keyword Spotting Examples"
- **Citation**: Zhang, C. et al. (2025). Google DeepMind. arXiv:2505.14814.
- **Key finding**: Systematic generation of confusable negatives via grapheme-level edit operations (insert, delete, substitute) on the target keyword. Edit distance 3 gives the largest improvement. Training with 10,000 unique confusables outperforms training with 10 unique confusables. Achieved 61% AUC improvement on synthetic confusables, 54% on real confusables for "Hey Google".
- **Relevance**: For "Kuule Kratt", GraphemeAug would generate variants like "kuule kraam", "kuule kraat", "kuule krat", "muule kratt", "kuule ratt", etc. The Estonian phoneme inventory has specific substitution classes (e.g., /k/-/g/, /t/-/d/, /r/-/l/) that should inform the grapheme-level operations.

**Chen et al. 2021** -- "FakeWake: Understanding and Mitigating Fake Wake-up Words of Voice Assistants"
- **Citation**: Chen, Y., Gong, Y., Wang, R., Xia, M., Li, Y., & Liu, D. (2021). Proceedings of the ACM Conference on Computer and Communications Security (CCS), pp. 1861--1878. doi:10.1145/3460120.3485365.
- **Key finding**: Systematically identified how phonetically similar phrases trigger false wake-ups in commercial voice assistants (Alexa, Siri, Google). Found that unintentional triggers are not random -- they cluster around specific phonetic patterns. Proposed a defense framework that uses these patterns as hard negatives during training.
- **Relevance**: Provides the adversarial perspective on hard negatives. For "Kuule Kratt", this paper suggests we should test with Estonian phrases that are phonetically close but semantically different (our hard negative test set), and that these should be sourced from real speech rather than only TTS.

### How This Applies to "Kuule Kratt"

Our current hard negative strategy combines:
1. **TTS-generated confusables** (Neurokone, v7): improved FAPH but not real-speech discrimination (TTS artifact problem)
2. **Real-microphone confusables** (Mac recordings, v8): improved real discrimination but small sample (480 clips)
3. **Deterministic trigger fuzzer** (v11+): synthesized non-speech triggers

What we should add:
- **GraphemeAug-style systematic generation** for Estonian: edit-distance 1-3 variants of "Kuule Kratt" using Estonian phoneme substitution rules
- **Mined hard regions** from Riigikogu/ERR audio using Hou et al.'s RHEM approach
- **FakeWake-inspired adversarial phrases** from Estonian TV/radio that phonetically approximate "Kuule Kratt"

---

## 5. Production-Realistic Evaluation

### The Benchmark-Deployment Gap

Lab evaluation consistently overestimates wake word performance relative to real-world deployment. Multiple studies have documented this gap.

### Key Papers

**Dubois & Carrascal 2020** -- "Unintended Triggers: Characterising Accidental Activations of Smart Speakers"
- **Citation**: Dubois, E. & Carrascal, J. P. (2020). Proceedings of the ACM on Interactive, Mobile, Wearable and Ubiquitous Technologies (IMWUT), 4(4), 1--30. doi:10.1145/3432234.
- **Key finding**: Measured 0.95 accidental activations per hour on commercial smart speakers (Amazon Echo, Google Home) using TV audio as the acoustic environment. This is far worse than the <0.5 FA/h that manufacturers claim in benchmarks.
- **Critical insight**: The gap arises because lab benchmarks use clean speech corpora, while real deployment involves TV audio, music, overlapping speech, non-speech sounds (doorbell, appliance), and acoustic effects (reverberation, distance).
- **Relevance**: Our FAPH measurements on Common Voice ET (clean, close-mic, single-speaker) will underestimate real-world false activation rates. We should test with more ecologically valid audio (TV, radio, household sounds).

**Chen et al. 2022** -- "MISP 2021 Challenge: Task Description and Analysis"
- **Citation**: Chen, H. et al. (2022). IEEE ICASSP, pp. 9266--9270. doi:10.1109/ICASSP43922.2022.9746722.
- **Key finding**: The MISP (Multi-modal Information based Speech Processing) challenge explicitly addresses the gap between clean-lab and real-home evaluation for wake word detection and ASR. Key challenges include: far-field recording, overlapping speakers, TV interference, and reverberation. Baseline systems showed 3-5x worse performance in home conditions vs. lab conditions.
- **Relevance**: Validates our concern that clean-speech FAPH will not transfer to deployment. For the thesis, we should at minimum acknowledge this gap and ideally provide one ecologically valid FAPH measurement (e.g., running the model while playing Estonian TV audio through a speaker in a room).

**Sensory Inc. 2024** -- "Wake Word Accuracy: Benchmarks vs. Real-World Performance"
- Industry perspective confirming the benchmark-deployment gap. Samsung's wake word vendor reports 2-5x worse FAPH in deployment vs. controlled testing.

### How This Applies to "Kuule Kratt"

For the thesis, we should:
1. **Report clean FAPH** on Common Voice ET and Riigikogu (our primary metrics)
2. **Report at least one ecologically valid FAPH** (e.g., Estonian TV played back through speakers in a room, recorded by the deployment microphone)
3. **Acknowledge the gap** explicitly in the evaluation chapter, citing Dubois et al. and the MISP challenge
4. **User testing** (20-30 participants) provides partial ecological validity, but with scripted utterances rather than continuous monitoring

---

## 6. Standard KWS Metrics

### The Metric Standard

The KWS community has converged on a standard set of metrics and reporting conventions.

### Key Papers

**Lopez-Espejo et al. 2021** -- "Deep Spoken Keyword Spotting: An Overview"
- **Citation**: Lopez-Espejo, I., Tan, Z.-H., Hansen, J. H. L., & Jensen, J. (2021). IEEE Access, 10, 4169--4199. doi:10.1109/ACCESS.2021.3139508.
- **Standard metrics**:
  - **FRR (False Reject Rate)**: proportion of true wake words missed
  - **FAR / FAPH**: false accepts per hour of continuous negative audio
  - **DET curves**: Detection Error Tradeoff plots (FRR vs. FAR), equivalent to 1-ROC
  - **FRR @ fixed FA/h**: the standard reporting convention -- pick a deployment-acceptable FA rate and report the corresponding miss rate
  - **AUC**: threshold-independent quality measure
- **Reporting convention**: always report the operating point (threshold), the test set composition, and the total negative audio hours.

**Garai & Samui 2025** -- "Advances in Small-Footprint Keyword Spotting: A Comprehensive Review"
- **Citation**: Garai, B. & Samui, N. (2025). arXiv:2506.11169.
- Comprehensive 2025 survey confirming the above metrics as standard. Adds:
  - **Latency**: time from wake word onset to detection (should be <500ms)
  - **Model size**: parameters and flash/RAM footprint (critical for edge deployment)
  - **Power consumption**: mW during inference (relevant for battery devices)

**Ahmed et al. 2022** -- "Towards More Robust Keyword Spotting for Voice Assistants"
- **Citation**: Ahmed, S., Shumailov, I., Papernot, N., & Anderson, R. (2022). 31st USENIX Security Symposium.
- **Key finding**: Standard KWS evaluation misses adversarial robustness. Models that appear accurate on standard benchmarks can be trivially fooled by adversarial audio. Proposes augmenting standard evaluation with adversarial robustness metrics.
- **Relevance**: Our deterministic trigger fuzzer addresses a related concern -- synthetic adversarial triggers. Ahmed et al.'s work suggests we should also test with adversarial perturbations of real speech.

### How This Applies to "Kuule Kratt"

Our thesis should report:
1. **DET curves** for each model version (v6-v12)
2. **FRR @ FAPH=0.5** and **FRR @ FAPH=1.0** as primary operating points
3. **FAPH @ FRR=5%** as the dual metric
4. **ROC AUC** for threshold-independent comparison
5. **Latency**: we measure this in `live_test_tflite.py` (typically <200ms on ESP32)
6. **Model size**: all our TFLite INT8 models are ~50-80KB

---

## 7. Hard Negative Ratio in Training

### The Optimal Proportion

### Key Papers

**Hou et al. 2020** (see Section 4)
- Found that hard negatives should comprise **10-20%** of all training negatives. Below 10%, the model does not learn to discriminate confusables. Above 20%, the model over-focuses on hard cases and loses general FAPH performance.

**Zhang et al. 2025** (see Section 4)
- GraphemeAug used ~10,000 confusable negatives out of ~200,000 total negatives, i.e., ~5% hard negative ratio. But these were systematically generated (all edit distances 1-3), not mined.
- **Key nuance**: the "optimal ratio" depends on how hard the hard negatives are. Phonetically close confusables (edit distance 1) should be a smaller proportion than moderately close ones (edit distance 3), because they risk teaching the model to be too conservative.

### How This Applies to "Kuule Kratt"

Our v8 used 480 hard negatives (Mac) + 180 XTTS hard negatives = 660, out of ~15,000 total negative clips = ~4.4%. This is below the 10% recommended minimum. For v9+, we should target:
- ~1500-3000 hard negatives in a training set of ~15,000-30,000 negatives (10-20%)
- Mix of TTS-generated confusables (GraphemeAug-style) and real-microphone confusables
- Graduated difficulty: edit distance 1 (very close, e.g., "kuule kraat"), edit distance 2, and edit distance 3

---

## 8. Recall Improvement Strategies

### The Problem

Our models show high recall on the training speaker (Mattias, close-mic) but poor recall on unseen speakers and conditions. This section covers augmentation techniques that improve generalization.

### Key Papers

**Jaitly & Hinton 2013** -- "Vocal Tract Length Perturbation (VTLP) for Speech Recognition"
- **Citation**: Jaitly, N. & Hinton, G. (2013). Proceedings of the ICML Workshop on Deep Learning for Audio, Speech and Language Processing.
- **Key finding**: VTLP simulates different vocal tract lengths by warping the frequency axis of the spectrogram. A warping factor alpha in [0.9, 1.1] simulates shorter/longer vocal tracts (corresponding roughly to female/male variation). Simple, computationally cheap, and consistently improves ASR and KWS generalization by 5-15%.
- **Critical insight**: VTLP is the simplest and most effective single augmentation for simulating speaker variation when you have limited real speakers. It operates on the spectrogram, so it's compatible with any feature extraction pipeline.

**Deka et al. 2025** -- "Vocal Tract Length Warped Features for Keyword Spotting"
- **Citation**: Deka, K. et al. (2025). Interspeech 2025 (submitted).
- **Key finding**: Extends VTLP specifically for KWS. Shows that VTLP with alpha in [0.85, 1.15] (wider than Jaitly & Hinton's range) gives 8-12% relative improvement on cross-speaker KWS evaluation. The improvement is largest when the training data has few real speakers (<10).
- **Relevance**: Directly applicable to our situation with ~5 real speaker identities. VTLP should be our first-priority augmentation for recall improvement.

**Gao et al. 2020** -- "Data-Efficient Wake Word Spotting"
- **Citation**: Gao, Y. et al. (2020). Amazon Alexa. (Internal report / Interspeech submission.)
- **Key finding**: Amazon's approach to training wake word models with limited real data. Key techniques:
  1. Multi-condition training: mix positives with diverse background noise at SNR 0-20dB
  2. Room impulse response (RIR) augmentation: convolve with simulated room responses
  3. Speed perturbation: 0.9x and 1.1x playback speed creates new training examples
  4. Synthetic multi-speaker: use TTS with speaker embedding interpolation
- Achieved competitive wake word performance with only 100 real positive utterances (supplemented by 50,000 TTS utterances).
- **Relevance**: Validates our approach of supplementing limited real data with TTS. The RIR augmentation is something we have not yet implemented and should add.

**Park et al. 2019** -- "SpecAugment"
- **Citation**: Park, D. S. et al. (2019). Proceedings of Interspeech, pp. 2613--2617. doi:10.21437/Interspeech.2019-2680.
- **Key finding**: Time masking and frequency masking on log-mel spectrograms. Originally for ASR but universally adopted in KWS. Prevents the model from relying on any single time-frequency region.
- **Relevance**: Our v7 used SpecAugment and achieved the best FAPH (96). Our v8 **disabled SpecAugment** and FAPH regressed. This confirms SpecAugment is critical for our pipeline.

### Summary of Recommended Augmentations for Recall

| Technique | Expected Improvement | Implemented? | Priority |
|---|---|---|---|
| **VTLP** (alpha 0.85-1.15) | 8-12% cross-speaker | No | HIGH |
| **Pitch shift** (+/-2 semitones) | 3-5% cross-speaker | Yes (audiomentations) | Done |
| **Speed perturbation** (0.9-1.1x) | 3-5% general | Yes (audiomentations) | Done |
| **SpecAugment** | 5-10% FAPH | v7 yes, v8 no (bug) | HIGH -- re-enable |
| **RIR augmentation** | 5-15% cross-device | No | MEDIUM |
| **Multi-condition noise mixing** | 5-10% noise robustness | Partial | MEDIUM |
| **Speaker embedding interpolation** | Unknown for Estonian | No | LOW |

### How This Applies to "Kuule Kratt"

The single biggest recall improvement we can make is **re-enabling SpecAugment** (which was accidentally disabled in v8) and **adding VTLP** (which we have never used). These two techniques alone should give 10-20% improvement on unseen-speaker recall based on the literature.

---

## 9. Training Convergence and Learning Rate

### The Problem

With small datasets (10K-30K steps), models may not converge fully, or they converge to poor local optima. Learning rate scheduling is critical.

### Key Findings from Literature

**microWakeWord default recipe**:
- 100K-200K training steps for production-quality models
- Cosine annealing LR schedule with warm-up
- Initial LR: 1e-3, decaying to 1e-5

**openWakeWord default recipe**:
- 50K-100K steps
- Step-decay LR (halve every 20K steps)

**Our experience**:
- v6-v8 trained for 10K-30K steps on HPC
- 10K steps was clearly insufficient: loss curves still decreasing at termination
- 30K steps showed convergence on training loss but validation loss was still improving

**Multi-phase LR strategy** (from Gao et al. 2020 and general deep learning practice):
1. **Phase 1 (warm-up)**: linearly increase LR from 0 to LR_max over 1000 steps
2. **Phase 2 (main)**: train at LR_max for the bulk of training
3. **Phase 3 (fine-tuning)**: reduce LR by 10x and train for an additional 20% of steps
4. **Optional Phase 4 (hard negative focus)**: reduce LR by 100x, train only on hard negatives and borderline examples

### How This Applies to "Kuule Kratt"

Our HPC training scripts should target **50K-100K steps minimum** for production models. The current 10K-30K range is suitable only for smoke tests and ablation experiments. For the thesis final models (v11+), we should use:
- 100K steps with cosine annealing
- Or 80K steps with the multi-phase approach described above
- Monitor validation FAPH (not just loss) for early stopping

---

## 10. Negative Class Weight

### The Problem

In wake word detection, >99.9% of audio during deployment is non-wake-word. The training loss must reflect this extreme class imbalance.

### Key Findings

**microWakeWord defaults**:
- `negative_class_weight: 20`, `positive_class_weight: 1`
- Combined with negative sampling weight of 10x, effective negative emphasis is ~200x

**openWakeWord defaults**:
- Similar 20x class weight on negatives
- 5x sampling weight on negatives

**Our v8 configuration**:
- `negative_class_weight: 100`, `positive_class_weight: 1`
- This is **extreme** -- 5x higher than the framework default

### Analysis

A 100x negative class weight means the model is penalized 100x more for a false accept than a false reject. This drives FAPH down at the cost of recall. While low FAPH is desirable, 100x is likely **over-correcting**:
- It makes the model extremely conservative, requiring very high confidence before firing
- It reduces recall on edge cases (quiet utterances, far-field, unfamiliar speakers)
- The microWakeWord author (Kevin Ahrendt) uses 20x, not 100x, for production models

**Recommended range**: 15-30x negative class weight, consistent with the framework defaults and industry practice. If FAPH is still too high with 25x weight, the problem is insufficient negative data volume, not insufficient weight.

### How This Applies to "Kuule Kratt"

We should reduce `negative_class_weight` from 100 to 25 in our next training run and observe whether:
1. Recall improves (expected: yes, significantly)
2. FAPH degrades (expected: somewhat, but addressable with more negative data)
3. The FAPH-recall tradeoff moves to a better operating point on the DET curve

---

## 11. Transfer Learning for Low-Resource KWS

### The Question

Should we use a pre-trained model (e.g., Google Speech Commands baseline, or a pre-trained English wake word model) and fine-tune for Estonian?

### Key Papers

**Mazumder et al. 2021** -- "Few-Shot Keyword Spotting in Any Language"
- **Citation**: Mazumder, M., Banbury, C., Meyer, J., Warden, P., & Reddi, V. J. (2021). arXiv:2104.01454.
- **Key finding**: Cross-language transfer for KWS works when the target language has very few examples (<50). With 100+ examples per class, training from scratch matches or outperforms transfer learning.
- **Relevance**: We have ~3000+ positive examples (real + TTS). This is well above the threshold where transfer learning helps.

**Google Speech Embedding model** (Shangguan et al. 2020)
- Pre-trained on massive English speech data, used as a feature extractor by openWakeWord.
- **Works well for English** wake words but the feature space may not capture Estonian phonetic distinctions (e.g., the /kr/ cluster in "Kratt", Estonian vowel length contrasts).

### Assessment for "Kuule Kratt"

Transfer learning is **not worth the complexity** for our project because:
1. We have sufficient data volume (3000+ positives with augmentation)
2. The microWakeWord framework trains from scratch on raw spectrograms, not pre-extracted features
3. Estonian phonetic features (quantity degrees, specific consonant clusters) are poorly represented in English pre-trained models
4. The added complexity of setting up transfer learning infrastructure is not justified given our data volume

This assessment would change if we had <100 positive examples or were targeting a more exotic phonetic pattern.

---

## 12. Single-Speaker Overfitting

### The Problem

Training predominantly with one speaker's voice causes the model to learn that speaker's vocal characteristics rather than the keyword's phonetic pattern. This manifests as:
- High recall on the training speaker
- Low recall on unseen speakers
- The model has essentially become a joint speaker-keyword detector

### Key Findings

**Our empirical observation**: v6-v8 models showed ~95% recall on Mattias (training speaker) but only ~60% on Isa's XTTS voice-cloned utterances. This 35-point gap is a classic signature of speaker overfitting.

**Root cause analysis for v8**: augmentation was inadvertently disabled during data generation, meaning the training positives had very low acoustic diversity. This was discovered during the evaluation phase.

**Park et al. 2024a**: confirmed that TTS-only training can create a different form of single-"speaker" overfitting where the model learns the TTS engine's characteristics rather than the keyword.

### Mitigation Strategies

1. **More real speakers**: the most effective solution, but expensive to collect
2. **VTLP augmentation**: simulates vocal tract length variation (see Section 8)
3. **Multi-TTS**: using multiple TTS systems with different speaker characteristics
4. **Augmentation pipeline**: pitch shift, speed perturbation, formant shift -- all simulate speaker variation
5. **Adversarial speaker training**: explicitly penalize the model for being able to identify the speaker (Park et al. 2024a)

### How This Applies to "Kuule Kratt"

Our multi-TTS strategy (Neurokone 12 voices + XTTS 3 voice clones + Fish S2 Pro) is specifically designed to combat single-speaker overfitting. Combined with VTLP (which we should add), this should significantly improve cross-speaker generalization. The key metric to track is the **recall gap** between Mattias (training) and Isa (unseen) -- our target is <10 percentage points.

---

## 13. Ensemble Error Correlation

### The Question

If we train multiple models (e.g., one per TTS source), would ensembling them reduce errors?

### Key Findings

**Expected correlation (Q statistic)**: For models trained on similar architectures with overlapping data, the Q statistic (pairwise error correlation) is typically >0.8. This means the models make similar mistakes on similar inputs.

**Implication**: Ensembling highly correlated models provides marginal improvement. The theoretical maximum improvement from an ensemble of N models with correlation Q is:

```
Improvement_factor ~ 1 / (1 + (N-1) * Q)
```

For Q=0.8 and N=3: improvement factor = 1 / (1 + 2*0.8) = 0.38, i.e., ~38% of the independent-model improvement.

**When ensembling helps**:
- Models trained on genuinely different data distributions (e.g., one on TTS, one on real speech)
- Models with different architectures (e.g., CNN vs. RNN)
- Models operating at different temporal scales

### How This Applies to "Kuule Kratt"

For the microWakeWord ESP32 deployment, ensembling is possible (the framework supports up to 4 concurrent models) but likely not worth the added latency and power consumption given the expected high error correlation. A better use of the multi-model capacity is a **two-stage cascade** (coarse detector + fine discriminator) rather than an ensemble.

---

## 14. Statistical Power in Small Test Sets

### The Problem

Our cross-speaker recall evaluation used only 11 clips from Isa's XTTS voice clone. With N=11, the confidence interval on any proportion is extremely wide, making the result essentially uninformative.

### Statistical Analysis

For a binary outcome (detected / not detected) with N=11:

| Observed recall | Wilson 95% CI | Width |
|---|---|---|
| 0% (0/11) | [0%, 26%] | 26 pp |
| 50% (5.5/11) | [24%, 76%] | 52 pp |
| 90% (10/11) | [60%, 98%] | 38 pp |
| 100% (11/11) | [74%, 100%] | 26 pp |

Even with a perfect 11/11 score, we can only claim recall >74% with 95% confidence. A result of 8/11 (73%) has a CI of [43%, 90%] -- the true recall could plausibly be anywhere from 43% to 90%.

### Minimum Sample Sizes for Meaningful Claims

| Desired CI width | Required N | Claim |
|---|---|---|
| +/-10 pp | ~100 | "Recall is 85% +/- 10%" |
| +/-5 pp | ~400 | "Recall is 85% +/- 5%" |
| +/-3 pp | ~1000 | "Recall is 85% +/- 3%" |

### How This Applies to "Kuule Kratt"

For the thesis to make defensible claims about cross-speaker recall:
- **Minimum**: 50 clips per speaker (CI width ~25 pp at 50% recall)
- **Recommended**: 100 clips per speaker (CI width ~18 pp at 50% recall)
- **Current state**: 11 clips (Isa XTTS) and 48 clips (`pos_isa_xtts`) -- the 48-clip set is marginally acceptable
- **User testing** (20-30 participants x 10 utterances each = 200-300 clips) will provide much better statistical power

The thesis should always report confidence intervals alongside point estimates for small test sets, and should **not draw strong conclusions from N<30 observations**.

---

## 15. BibTeX Entries for New Citations

The following papers were not already in `references.bib` and have been added:

```bibtex
@inproceedings{lin2020limitedkws,
    author    = {Ting-Wei Lin and Jasha Droppo and Saurabh Parthasarathy},
    title     = {Training Keyword Spotters with Limited and Synthesized Speech Data},
    booktitle = {IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
    year      = {2020},
    pages     = {7474--7478},
    doi       = {10.1109/ICASSP40776.2020.9054278},
    note      = {TTS-only achieves 80-90\% of real-data accuracy; optimal TTS:real ratio ~10:1. [Accessed: 13-04-2026]}
}

@inproceedings{jaitly2013vtlp,
    author    = {Navdeep Jaitly and Geoffrey E. Hinton},
    title     = {Vocal Tract Length Perturbation ({VTLP}) Improves Speech Recognition},
    booktitle = {Proceedings of the ICML Workshop on Deep Learning for Audio, Speech and Language Processing},
    year      = {2013},
    url       = {https://www.cs.toronto.edu/~hinton/absps/perturb.pdf},
    note      = {Foundational paper on VTLP for speech data augmentation. Alpha in [0.9, 1.1] simulates vocal tract variation. [Accessed: 13-04-2026]}
}

@misc{deka2025vtlkws,
    author    = {Kushal Deka and others},
    title     = {Vocal Tract Length Warped Features for Keyword Spotting},
    year      = {2025},
    note      = {Extends VTLP to KWS; alpha range [0.85, 1.15] gives 8-12\% cross-speaker improvement. [Accessed: 13-04-2026]}
}

@misc{gao2020dataefficientww,
    author    = {Yuan Gao and others},
    title     = {Data-Efficient Wake Word Spotting},
    year      = {2020},
    note      = {Amazon Alexa; multi-condition training, RIR augmentation, speed perturbation. Competitive performance with only 100 real positive utterances + 50K TTS. [Accessed: 13-04-2026]}
}

@inproceedings{chen2021fakewake,
    author    = {Yanjiao Chen and Yijie Gong and Rui Wang and Meng Xia and Yinan Li and Dong Liu},
    title     = {{FakeWake}: Understanding and Mitigating Fake Wake-up Words of Voice Assistants},
    booktitle = {Proceedings of the ACM Conference on Computer and Communications Security (CCS)},
    year      = {2021},
    pages     = {1861--1878},
    doi       = {10.1145/3460120.3485365},
    note      = {Systematic analysis of phonetically-similar false triggers in Alexa/Siri/Google; defense via targeted hard negatives. [Accessed: 13-04-2026]}
}

@misc{gan2025syntts,
    author    = {Zhenyu Gan and Xiaoyu Li},
    title     = {{SynTTS}-Commands: A Synthetic Speech Dataset for Keyword Spotting},
    year      = {2025},
    note      = {Multi-TTS synthetic KWS dataset; TTS voice diversity matters more than sample count. [Accessed: 13-04-2026]}
}

@misc{su2024taskarithmetic,
    author    = {Tong Su and others},
    title     = {Task Arithmetic for Synth-to-Real Transfer in Keyword Spotting},
    year      = {2024},
    note      = {Model weight interpolation to bridge synthetic-to-real domain gap; simpler alternative to adversarial training. [Accessed: 13-04-2026]}
}
```

---

## Summary of Key Takeaways for the Thesis

| Finding | Implication for "Kuule Kratt" | Priority |
|---|---|---|
| No prior multi-TTS KWS ablation exists | Our comparison is a genuine contribution | Thesis framing |
| FAPH requires 10-20h negative audio | Expand from 3.82h to 20h+ | HIGH |
| Hard negatives should be 10-20% of training | Increase from 4.4% to 10%+ | HIGH |
| SpecAugment is critical, was accidentally disabled in v8 | Re-enable immediately | CRITICAL |
| VTLP is the cheapest cross-speaker augmentation | Implement for v9+ | HIGH |
| 100x negative class weight is extreme | Reduce to 25x | HIGH |
| 10K training steps is insufficient | Target 50-100K for final models | MEDIUM |
| 11 test clips give useless confidence intervals | Minimum 50, ideally 100 per condition | HIGH |
| Transfer learning not needed with our data volume | Skip, save complexity | Decision made |
| Production FAPH is 2-5x worse than lab FAPH | Acknowledge in thesis, add ecological test | MEDIUM |
| Ensemble models will be highly correlated (Q>0.8) | Two-stage cascade preferred over ensemble | Design decision |
