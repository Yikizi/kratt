## 1. Executive summary

1. **Kratt’s failure mode is literature-recognizable, not anomalous.** A binary clip-level wake-word classifier can learn “some evidence of the target phrase” rather than “the exact ordered phrase.” Apple’s DNN-HMM KWS work explicitly adds partial-keyword hard negatives “because we do not want the model to trigger at partial phrases,” and uses swapped-order negatives to reject incorrect word order. This is directly relevant to `kuule/kule`-only and `kratt kuule` triggers. ([ar5iv][1])

2. **Clean positives are necessary but not sufficient.** Removing SSML/XML, command tails, and prefix-only positives fixes a data-integrity problem, but exact phrase selectivity still depends on the training objective, temporal alignment, model capacity, and whether partial/confusable negatives are represented. This is strongly consistent with KWS literature; the specific v18 outcome is a Kratt project finding. ([ar5iv][1])

3. **Low ambient FAPH is not enough.** Standard wake-word evaluation uses both false accepts per hour and false rejects/recall, and large negative sets should include background speech and phrases users might say. Apple explicitly distinguishes FAR/FAPH from FRR and notes that threshold movement trades one for the other. ([Apple Machine Learning Research][2])

4. **Hard/confusable negatives should be first-class data, not an afterthought.** FakeWake, accidental-trigger, adversarial-confusing-word, and GraphemeAug work all show that phonetically similar “fake” wake phrases are a practical false-accept source and that systematic confusable generation can improve robustness. ([arXiv][3])

5. **Binary KWS with more hard negatives is feasible on ESP32-S3, but it does not inherently enforce order.** It can reduce `kuule <not kratt>` errors if the data distribution is right, but exact two-token order is only weakly encoded unless the model architecture/objective has temporal structure or the negative set explicitly includes partials and permutations.

6. **Sequence-aware methods address the core issue more directly.** DNN-HMM, keyword/filler decoding, CTC, and RNN-T-style KWS encode temporal paths or label sequences, so they are a better conceptual match for “`kuule/kule` followed by `kratt`.” They are more difficult to fit into the current microWakeWord pipeline but are feasible on Raspberry Pi 5 and relevant as future work. ([arXiv][4])

7. **A two-stage local cascade is the most thesis-safe practical path.** Industry systems commonly use a low-power high-recall first-pass detector plus a higher-precision checker/verifier; Apple, Amazon, and Google all describe this pattern. For Kratt, the cloud verifier can be replaced with local Kiirkirjutaja/Sherpa-ONNX or a phonetic matcher on Raspberry Pi 5. ([Apple Machine Learning Research][5])

8. **VAD helps with non-speech false accepts, but it is not a phrase verifier.** ESPHome’s microWakeWord documentation explicitly treats VAD as a way to reduce false accepts from non-speech sounds, while the wake-word threshold still trades false accepts against false rejections. It cannot distinguish `kuule rott` from `kuule kratt`. ([ESPHome - Smart Home Made Simple][6])

9. **The thesis should frame Kratt as a rigorous low-resource methodology contribution.** The defensible contribution is a corrected Estonian wake-word pipeline and evaluation protocol showing that exact multi-word phrase selectivity is a separate requirement from ambient FAPH and nominal recall.

10. **Recommended final evaluation contract:** report frozen-threshold ambient FAPH, real/unseen-speaker recall, and category-level hard-negative FPR for prefix-only, suffix-only, reversed-order, and `kuule/kule <confusable>` phrases.

---

## 2. Diagnosis: why a binary clip-level KWS model can become permissive

A small binary wake-word classifier trained on fixed audio windows is usually optimized to answer “does this clip contain the target class?” rather than “does this clip contain exactly this ordered token sequence and nothing weaker?” If the label is clip-level and the architecture uses convolution/pooling or sliding-window scores, the network can learn that a highly discriminative subsegment such as `kuule/kule` or `kratt` is enough evidence for the positive class. Apple’s older “Hey Siri” system avoids a purely bag-like decision by mapping frames to speech-sound classes and then applying temporal integration over the expected sequence; their later DNN-HMM work makes the ordering constraint even more explicit through HMM decoding. ([Apple Machine Learning Research][2])
**Evidence strength for Kratt:** direct for wake-word sequence modeling; project-specific for the exact Estonian phrase.

Fixed windows and random cropping make this worse when the positive label remains attached to a window that contains only part of the phrase. In that case, the model is literally trained that the prefix alone is positive. Apple’s end-metric KWS paper is unusually explicit here: it samples “tightly” overlapping positive windows, samples low-overlap negatives, adds partial-keyword hard negatives, and creates swapped-order hard negatives so the model gives a high score only when states occur in the right order. This maps almost one-to-one onto Kratt’s `kuule/kule`-only, `kratt`-only, and `kratt kuule` audit categories. ([ar5iv][1])
**Evidence strength:** direct.

Positive-label impurity is especially dangerous in low-resource KWS because the positive set is small, synthetic data may be overrepresented, and the model is highly capacity-limited. If SSML/XML tags are spoken aloud, command tails are included, or prefix-only clips are mislabeled positive, the learned positive concept expands from “`kuule/kule kratt`” to “sounds like an invocation prefix, maybe with extra speech.” microWakeWord itself is designed for low-power custom wake words and TFLite Micro deployment, but its documentation notes that training new models is difficult and typically requires experimentation with hyperparameters and sample generation. ([GitHub][7])
**Evidence strength:** general direct support for microWakeWord training difficulty; the corruption modes are Kratt-specific findings.

Class imbalance and negative-set composition also matter. Long ambient audio mainly tests accidental activation on background/noise/general speech. It does not necessarily test near-boundary spoken negatives such as `kuule rott` or `kuule robot`. The smart-speaker accidental-trigger literature shows that similar words and sounds can trigger commercial assistants, and FakeWake shows that “fuzzy words” can cause false wake-up activations. Therefore, an ambient-FAPH-optimized checkpoint can look good while still being unsafe for spoken confusables. ([arXiv][8])
**Evidence strength:** direct for false wakes/confusables; project-specific for Kratt’s measured split between ambient FAPH and confusable FPR.

Finally, the threshold problem is real. Raising the microWakeWord probability cutoff reduces false accepts but increases false rejections; Apple similarly describes FAR/FAPH and FRR as different-dimensional metrics connected by a threshold tradeoff. This explains why FAPH-optimized Kratt checkpoints can collapse real-speaker recall: they may simply move to a very conservative operating point rather than solving phrase selectivity. ([ESPHome - Smart Home Made Simple][6])
**Evidence strength:** direct.

---

## 3. Detailed literature review by method family

### A. Binary KWS with explicit partial/confusable hard negatives

This is the closest continuation of the current microWakeWord path. The idea is to keep the same binary target class but make the negative class more realistic: `kuule`, `kule`, `kratt`, `kratt kuule`, `tere kratt`, `kuule rott`, `kuule robot`, `kuule, kas sa kuuled?`, and many `kuule/kule <not kratt>` phrases must be labeled negative and oversampled enough that the model cannot ignore them. Apple’s DNN-HMM training work explicitly uses partial-keyword hard negatives and hard-negative selection to avoid partial phrase triggers, which supports this as a principled method, not just a heuristic. ([ar5iv][1])

For Kratt, this addresses the exact observed failure modes: prefix-only triggering, suffix-only triggering, and near-phrase triggering. It needs clean exact positives, real-speaker positives, TTS positives only after validation, ambient negatives, and hard negative categories with enough speaker and acoustic variation. It can preserve recall if hard-negative ratios and thresholds are tuned carefully, but the risk is high if the model learns that any acoustic variation around `kuule` is dangerous and suppresses true `kuule kratt`. GraphemeAug also warns that edit distances that are too low can create examples nearly identical to the keyword and increase false rejects. ([arXiv][9])

On ESP32-S3, this is the most feasible approach because it changes training data, not inference. It fits the current TFLite Micro / microWakeWord workflow. It does not strongly enforce word order by itself unless reversed-order negatives and temporally constrained sampling are included. Appropriate metrics are FAPH on long ambient audio, real/unseen-speaker recall, and category-level FPR for each confusable family at frozen thresholds.

**Evidence strength:** direct for partial hard negatives; direct/analogous for Estonian confusables.

---

### B. Systematic hard-negative generation: phoneme/grapheme edit distance, GraphemeAug, FakeWake

The hard-negative set should not be limited to manually guessed examples. FakeWake automatically generated 965 fuzzy wake words for English and Chinese assistants and found phonetic features that contribute to false acceptance. The accidental-trigger study used a pronouncing dictionary and weighted phone-based Levenshtein distance to craft candidate accidental triggers. GraphemeAug systematically mutates the target keyword/keyphrase at the grapheme level to synthesize acoustically similar confusables, and reports that synthetic confusables improved AUC on real confusable audio. ([arXiv][3])

For Kratt, the practical version is an Estonian confusable generator. Start with the canonical strings `kuule kratt` and `kule kratt`, then generate negatives by edits and substitutions around both words: vowel length changes, consonant substitutions, deletion of `kratt`, replacement of `kratt` with `rott`, `kass`, `robot`, `ratas`, or other plausible Estonian words, and insertion of common post-prefix phrases such as `kuule kas ...`. A phoneme-aware version is better than pure grapheme distance, because Estonian length and pronunciation matter, but pure grapheme mutation is still useful for producing a broad candidate list.

This method needs TTS or real recordings of generated confusables, plus a held-out real-speaker confusable regression set. It is ESP32-feasible because generation affects only training. It does not inherently enforce word order unless the generation rules include deletion, permutation, and insertion categories. Recall risk is medium: useful confusables improve selectivity, but too many near-identical negatives can push the decision boundary into true positives. ([arXiv][9])

**Evidence strength:** direct for confusable-generation concept; analogous for Estonian because published work is not Estonian-specific.

---

### C. Two-stage cascade: small always-on detector plus verifier

The most mature production pattern is a cascade. Apple describes a streaming high-recall first-pass detector running on low-power hardware, followed by a high-precision checker on a more capable processor, plus speaker and directed-speech checks. Amazon describes a secondary wake-word verification network to prevent responses when the first detector fires by mistake. Google’s contextual-ASR KWS work uses ASR after a limited-resource on-device trigger and reports large false-accept reduction with minimal false-reject increase in that server-side setting. ([Apple Machine Learning Research][5])

For Kratt, the privacy-first local variant is: ESP32-S3 microWakeWord acts as a high-recall candidate detector; Raspberry Pi 5 receives the buffered candidate window; a local verifier checks whether the ordered phrase is actually `kuule/kule kratt`. The verifier could be Kiirkirjutaja/Sherpa-ONNX ASR, a phoneme-level decoder, or a small second-stage neural verifier trained on exact positives and hard negatives. Kiirkirjutaja is an Estonian real-time speech-to-text tool using streaming transducer models and Sherpa-ONNX decoding, so it is a plausible local ASR component for a Home Assistant-side experiment. ([GitHub][10])

This addresses the core capacity mismatch: an MCU model need not solve every confusable; it only needs high recall and manageable candidate rate. The recall risk moves to the verifier, which may reject true positives because of ASR errors, clipping, dialect, background noise, or pronunciation variation. The evaluation must therefore report both verifier-only recall/rejection and end-to-end recall/FPR.

**Evidence strength:** direct for cascade architecture; project-specific for replacing cloud verification with local Estonian ASR.

---

### D. Keyword/filler HMM and hybrid DNN-HMM approaches

Keyword/filler models represent the wake phrase as an ordered path through keyword states, with filler/silence absorbing non-keyword speech. DNN-HMM systems use a neural acoustic model but an HMM decoder to impose temporal sequence constraints. Apple’s first-stage voice trigger system is DNN-HMM based, and the LF-MMI wake-word paper trains a hybrid DNN/HMM detector from partially labeled data, removing the need for frame-level alignments and using online FST decoding. ([Apple Machine Learning Research][5])

This family directly targets the `bag-of-phonemes` problem. A keyword/filler decoder can score the ordered phoneme/state path for `/kuule kratt/` and penalize partials or wrong order. Apple’s end-metric paper is especially relevant because it states that swapped-order negatives help reject incorrect word ordering in the trigger phrase. ([ar5iv][1])

For Kratt, the drawback is implementation effort. It is not a drop-in microWakeWord change. A tiny DNN-HMM might be technically possible on ESP32-S3, but it would require a custom decoder/runtime and careful memory budgeting. It is much more feasible on Raspberry Pi 5 or as future work. Metrics should be DET curves, FRR/recall at fixed FA/hr, localization correctness, and partial/reversed-order false trigger rates.

**Evidence strength:** direct for order-sensitive wake-word modeling; future-work feasibility for Kratt.

---

### E. Phoneme posterior and keyword/filler decoding

A phoneme posterior approach uses a model that emits phoneme probabilities over time, then searches for the expected phoneme sequence with a filler model or dynamic program. This is conceptually close to Apple’s description of a DNN producing speech-sound probabilities for “Hey Siri” plus silence/other-speech classes, followed by temporal integration. ([Apple Machine Learning Research][2])

For Kratt, this is attractive because the accepted pronunciation variant can be expressed directly: one path for `kuule kratt`, another for `kule kratt`. Prefix-only `kuule/kule` lacks the required second word; reversed order follows the wrong path; `kuule rott` diverges in the second token. The method needs an Estonian phoneme inventory or G2P rules, plus either an Estonian phone recognizer or a trained small acoustic model.

ESP32 feasibility is low unless the phone posterior model is extremely small and the decoder is simple. Raspberry Pi feasibility is good, especially as a post-trigger verifier. Recall preservation depends on whether the phone model handles Estonian vowel length, real speaker variation, and noise.

**Evidence strength:** direct for the modeling principle; implementation for Kratt is future work.

---

### F. CTC or sequence/objective-based KWS

CTC and RNN-T models optimize sequence labels rather than clip-level binary labels. This helps when the problem is “detect this token sequence in this order.” DONUT uses CTC for online query-by-example custom wake-word detection and emphasizes interpretability and embedded suitability. Google’s sequence-to-sequence KWS work trains streaming RNN-T models to predict phonemes or graphemes, allowing arbitrary keyword phrases without out-of-vocabulary issues. Meta compares alignment-based CE, alignment-free CTC, and hybrid approaches for wake-word detection and reports that alignment-free training performed better at the target operating point in their setup. ([arXiv][11])

For Kratt, CTC is a clean conceptual fit: label the target as `k u u l e  k r a t t` or phoneme tokens, then decode whether the ordered sequence appears. It naturally distinguishes `kuule` from `kuule kratt` if the decoder requires the full sequence. However, CTC does not magically solve data imbalance or acoustic confusability; it still needs hard negatives and careful thresholding.

On ESP32-S3, full CTC/RNN-T is probably outside the current microWakeWord thesis scope unless using a very small quantized model. On Raspberry Pi 5, it is feasible as a verifier or future standalone detector. Metrics should include sequence-level recall, partial-trigger FPR, confusable FPR, and latency.

**Evidence strength:** direct for sequence KWS; hardware feasibility estimate is project/engineering judgment supported by MCU constraints.

---

### G. ASR-based wake phrase verification after first-stage trigger

ASR verification decodes the candidate wake window and checks whether the transcript contains the exact ordered phrase. Apple notes that if a later recognizer hears something other than “Hey Siri,” such as “Hey Seriously,” it can cancel the wake; Google’s contextual-ASR KWS work uses ASR to reduce false accepts after a limited-resource trigger. Amazon’s cloud-based wake-word verification similarly uses a secondary check after the device wake-word engine fires. ([Apple Machine Learning Research][2])

For Kratt, this is the most realistic tight-deadline verifier. A local Pi-side ASR verifier can canonicalize transcripts by lowercasing, removing punctuation, mapping `kuule` and `kule`, and requiring `kuule/kule` immediately followed by `kratt`. It should explicitly reject one-token transcripts, reversed order, and `kuule/kule <not kratt>`. If full ASR is too brittle, a phonetic edit-distance matcher over ASR alternatives or subword outputs may be more robust.

This cannot run always-on on ESP32-S3, but it can run only after microWakeWord triggers on Raspberry Pi 5. The recall risk is non-trivial: Estonian ASR may misrecognize short wake phrases, clipped audio, distant speech, or dialectal variants. Therefore, the thesis should present ASR verification as promising but not solved unless measured end-to-end.

**Evidence strength:** direct for cascade/ASR verification; Kratt’s local Estonian ASR performance is project-specific.

---

### H. Personalized/custom verifier models

openWakeWord supports a custom verifier that acts as a filter on top of a base wake-word model. Its documentation says this can reduce false activations by focusing on a known target speaker or deployment environment, with minimal data collection, and that false activations can be used as effective negative examples. ([GitHub][12])

For Kratt, a personalized verifier could help if the target deployment is one household or a small set of speakers. It does not by itself guarantee exact phrase order, because the documented openWakeWord verifier is a lightweight logistic regression over shared features. But it can reduce false activations from other speakers and repeated local confusables. It is best viewed as an optional second-stage filter, not the primary phrase-order solution.

ESP32 feasibility is limited in the current microWakeWord stack. Raspberry Pi feasibility is good. Recall risk is medium: it may reject legitimate unseen speakers, which is unacceptable if the product goal is speaker-independent Estonian wake detection.

**Evidence strength:** direct for personalized false-activation reduction; weak/analogous for exact phrase selectivity.

---

### I. Multi-model consensus or mixture of experts

A practical lightweight trick is to combine several imperfect detectors: for example, one exact-phrase model, one anti-prefix/confusable model, or separate detectors for `kuule/kule` and `kratt` with temporal ordering logic. This can reduce false accepts if model errors are uncorrelated. However, it can also compound false rejects, because every additional gate becomes another way to reject a true wake phrase.

For Kratt, consensus can enforce a crude order if the system produces timestamps: require evidence for `kuule/kule` followed shortly by evidence for `kratt`. But ordinary microWakeWord model outputs may not be temporally localized enough for reliable token-level ordering. Multiple 50–150 KB models may also strain MCU flash/RAM/CPU budgets depending on the device and ESPHome configuration. ESPHome supports multiple microWakeWord models and a sliding-window/probability configuration, but that does not itself provide token-level sequence verification. ([ESPHome - Smart Home Made Simple][6])

**Evidence strength:** engineering inference from available tooling; not strongly established as the best scientific route for this case.

---

### J. VAD or speech-gating as prefilter only

VAD is useful for suppressing non-speech false accepts. ESPHome’s microWakeWord documentation says VAD can reduce false accepts from non-speech sounds. But VAD does not know whether the speech was `kuule kratt`, `kuule rott`, or `kuule, kas sa kuuled?`. ([ESPHome - Smart Home Made Simple][6])

For Kratt, VAD belongs in the pipeline as a noise/latency/energy prefilter, not as evidence of phrase selectivity. VAD metrics should be reported separately if used, because it can improve ambient FAPH while leaving spoken confusable FPR unchanged.

**Evidence strength:** direct for VAD’s intended role; direct project implication.

---

## 4. Decision table

| Approach                           |                                       Exact phrase selectivity |                                Recall risk | ESP32-S3 / microWakeWord feasibility | Raspberry Pi 5 feasibility | Best metrics                                                   |
| ---------------------------------- | -------------------------------------------------------------: | -----------------------------------------: | -----------------------------------: | -------------------------: | -------------------------------------------------------------- |
| Binary KWS + manual hard negatives |                                                         Medium |               Medium–high if over-weighted |       **High**; training-only change |                       High | FAPH, unseen-speaker recall, prefix/confusable FPR             |
| Systematic confusable generation   |                                                         Medium |                                     Medium |        **High**; generated data only |                       High | Category FPR, real-confusable AUC/FPR, recall                  |
| Two-stage KWS + verifier           |                    **High** if verifier is sequence/text-aware | Medium; verifier can reject true positives |                         Stage 1 only |                   **High** | Stage-1 recall, verifier rejection, end-to-end FAPH/FPR/recall |
| Keyword/filler HMM / DNN-HMM       |                                                       **High** |                 Low–medium if trained well |    Low–medium; custom runtime needed |                   **High** | FRR at FA/hr, partial/reversed-order FPR                       |
| Phoneme posterior + decoder        |                                                       **High** |                Medium; phone errors matter |                                  Low |                   **High** | Phoneme path score, hard-negative FPR, latency                 |
| CTC / RNN-T sequence KWS           |                                                       **High** |               Medium; data/model dependent |         Low for current thesis scope |                   **High** | Sequence recall, partial FPR, latency, DET                     |
| ASR-based verifier                 |                            **High** when transcript is correct |  Medium–high on short/clipped/noisy phrase |                                   No |                   **High** | Verifier recall, confusable rejection, end-to-end latency      |
| Personalized/custom verifier       | Low–medium for exact phrase; high for target speaker filtering |         Medium; rejects non-enrolled users |                 Low in current stack |                       High | Speaker-specific FRR/FAR, false activation reduction           |
| Multi-model consensus              |                                         Medium if time-ordered |                                Medium–high |                 Medium if models fit |                       High | Consensus recall, category FPR, CPU/RAM                        |
| VAD / speech gate                  |                                     Low for phrase selectivity |                                 Low–medium |                             **High** |                   **High** | Non-speech FAPH, VAD false rejection, downstream recall        |

Hardware basis: ESP32-S3 is a dual-core 240 MHz MCU with 512 KB internal SRAM and vector instructions, while LiteRT/TFLite Micro is designed for devices with only kilobytes of memory. Raspberry Pi 5 has a quad-core Cortex-A76 CPU at 2.4 GHz and RAM options up to 16 GB, making local ASR/verifier experiments realistic. ([Espressif Systems][13])

---

## 5. Deployment-specific recommendations

### ESP32-S3 / TFLite Micro / microWakeWord

Use ESP32-S3 for **always-on candidate detection**, not for full phrase understanding. microWakeWord is explicitly meant for custom wake-word detection on low-power devices and produces TFLite Micro-suitable models; Home Assistant adopted it because openWakeWord was too large for low-power ESP32-S3 devices. ([GitHub][7])

The most realistic ESP32-side improvements are:

* strict positive hygiene;
* no positive random crop that can remove `kratt`;
* explicit partial/confusable hard negatives;
* threshold selected on a development set and frozen before test;
* optional VAD only to reduce non-speech false accepts;
* possibly a second tiny anti-confusable model only if memory and CPU allow.

Do **not** claim ESP32 microWakeWord can fully solve exact Estonian phrase verification unless the hard-negative regression set shows it.

### Raspberry Pi 5 / Home Assistant

Use Pi 5 for the **second-stage verifier**. The Pi has enough CPU/RAM headroom for local ASR or a small verifier, and Kiirkirjutaja/Sherpa-ONNX is directly relevant because it is an Estonian real-time STT stack using Sherpa-ONNX decoding. ([Raspberry Pi][14])

The most thesis-safe local verifier is:

1. ESP32 sends a wake candidate or starts streaming after a high-recall trigger.
2. Pi extracts a buffered window containing the candidate phrase.
3. Kiirkirjutaja/Sherpa-ONNX decodes it.
4. A deterministic verifier accepts only `kuule kratt` or `kule kratt` in the required order.
5. The evaluation reports verifier recall and rejection separately from first-stage KWS misses.

### Cloud/server

Cloud verification is important literature context because Amazon and Google describe second-stage server checks, but it should not be the Kratt deployment recommendation. Kratt’s privacy-first framing should state that the same cascade principle can be implemented locally on Raspberry Pi 5 instead of sending wake audio to a remote service. ([Developer Portal Master][15])

---

## 6. Recommended thesis wording

**Paragraph 1 — problem framing.**
This thesis treats Estonian wake-word detection as a low-resource, privacy-first embedded speech problem rather than as a solved application of generic binary classification. The target phrase, `Kuule Kratt`, is a two-word ordered phrase with an accepted pronunciation variant `Kule Kratt`. Therefore, a deployable detector must reject not only ambient noise and unrelated speech, but also partial and near phrases such as `kuule`, `kratt`, `kratt kuule`, and `kuule <not kratt>`.

**Paragraph 2 — why the observed failure is plausible.**
The experiments show that a clip-level binary wake-word model can achieve low ambient false accepts while still firing on partial or confusable phrases. This is consistent with wake-word literature: production systems distinguish false accepts from false rejects, tune thresholds between them, and use large negative sets containing background speech and plausible user phrases. More directly, Apple’s DNN-HMM KWS work adds hard negatives containing partial keywords and swapped-order trigger segments specifically to avoid partial-phrase and wrong-order triggers. ([Apple Machine Learning Research][2])

**Paragraph 3 — label purity.**
The v17 audit demonstrates a data-integrity failure: spoken SSML/XML tags, command tails, and prefix-only clips corrupted the positive class. Removing these examples is necessary because a supervised classifier cannot learn a strict phrase boundary from labels that mark non-strict examples as positive. However, the v18 result shows that clean positives alone are not sufficient for exact phrase selectivity; the negative set and/or objective must also teach the model that partial and near phrases are negative. The first part is a general supervised-learning and KWS principle; the second part is a project-specific Kratt finding supported by the hard-negative and sequence-KWS literature.

**Paragraph 4 — hard negatives and confusables.**
Partial and confusable phrases should be treated as first-class evaluation categories. FakeWake, accidental-trigger, adversarial-confusing-word, and GraphemeAug studies all show that phonetically similar phrases can trigger wake systems and that generated confusables can improve robustness. For Kratt, this means `kuule/kule`-only, `kratt`-only, reversed order, and `kuule/kule <not kratt>` must be present in held-out regression tests, not only in ad hoc manual listening. ([arXiv][3])

**Paragraph 5 — limits of ambient FAPH.**
Ambient FAPH is an important metric but not a sufficient deployment criterion. A model with very low ambient FAPH may simply operate at a threshold that rejects many real speakers, or it may remain vulnerable to near-phrase spoken negatives. Therefore, this thesis reports ambient FAPH together with real/unseen-speaker recall and hard-negative false-positive rates at frozen thresholds.

**Paragraph 6 — system architecture.**
The most practical low-resource architecture is a two-stage cascade. The ESP32-S3 microWakeWord model should be optimized as a small always-on candidate detector, while a Raspberry Pi 5/Home Assistant component can perform higher-precision local verification using ASR, phonetic matching, or a learned verifier. This mirrors the cascade design used in commercial systems, but preserves Kratt’s privacy-first constraint by keeping verification local. ([Apple Machine Learning Research][5])

**Paragraph 7 — contribution claim.**
The thesis should avoid claiming that Estonian exact wake-word detection is solved. A stronger and safer claim is that the project builds and evaluates a realistic Estonian wake-word pipeline, identifies positive-label contamination as a critical failure mode, corrects the evaluation methodology, and provides empirical evidence that exact multi-word phrase selectivity is a separate challenge from generic FAPH optimization.

---

## 7. Which thesis claims are strongly supported vs project-specific

| Claim                                                         | Support level                                                             | How to phrase it                                                                                                                                            |
| ------------------------------------------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Clean positive labels are necessary                           | Strong general support                                                    | “Necessary for meaningful supervised training and confirmed by the v17 audit.”                                                                              |
| Clean positives are not sufficient for exact phrase detection | Literature-consistent + Kratt-specific                                    | “In Kratt, v18 showed this empirically; literature suggests hard negatives/order-aware objectives are needed.”                                              |
| Binary clip KWS can improve FAPH while failing confusables    | Strongly plausible; direct false-wake literature; Kratt-specific evidence | “Ambient FAPH does not measure near-phrase selectivity.”                                                                                                    |
| Partial and near phrases should be first-class negatives      | Strong direct support                                                     | Apple explicitly uses partial-keyword and swapped-order hard negatives; FakeWake/GraphemeAug support confusable generation. ([ar5iv][1])                    |
| Low ambient FAPH alone is insufficient                        | Strong direct support                                                     | Standard evaluation reports both false accepts and false rejects; Kratt adds hard-negative FPR as a needed category. ([Apple Machine Learning Research][2]) |
| Two-stage embedded KWS + local verifier is practical          | Strong analogous industry support; local ASR part project-specific        | “A privacy-preserving local adaptation of common production cascades.”                                                                                      |
| microWakeWord alone cannot solve exact phrase selectivity     | Too strong as universal claim                                             | Safer: “The current binary microWakeWord setup did not solve it in these experiments.”                                                                      |

---

## 8. Minimal v19-style phrase-selectivity experiment

This is optional if time permits; it is small enough to be thesis-safe.

**Goal:** isolate whether phrase-selective hard negatives improve exact `kuule/kule kratt` detection without collapsing recall.

**Training data contract**

* Positives: only exact `kuule kratt` and `kule kratt`; no SSML/XML; no command tails; no crops that remove either word.
* Easy negatives: ambient household noise, general Estonian speech, non-target speech.
* Hard negatives:

  * prefix-only: `kuule`, `kule`;
  * suffix-only: `kratt`;
  * reversed: `kratt kuule`, `kratt kule`;
  * wrong first word: `tere kratt`;
  * wrong second word: `kuule rott`, `kuule robot`, `kuule kass`, `kuule ratas`, and other `kuule/kule <not kratt>`;
  * sentence confusables: `kuule, kas sa kuuled?`, `kuule, ...` conversational phrases.

**Minimal model grid**

Train the same architecture with only data/sampling changed:

* baseline clean positives + ordinary negatives;
* * partial negatives;
* * partial and reversed-order negatives;
* * partial, reversed, and `kuule/kule <confusable>` negatives.

Avoid a large hyperparameter search. The point is not to produce a perfect model but to show whether the failure mode responds to targeted negatives.

**Held-out regression sets**

Keep held-out sets separate by speaker, TTS voice, phrase template, and recording session:

* real/unseen exact positives;
* long ambient negative audio;
* prefix-only negatives;
* suffix-only negatives;
* reversed-order negatives;
* `kuule/kule <confusable>` negatives;
* conversational `kuule/kule ...` negatives.

**Reporting**

Use frozen thresholds chosen on development data. Report recall, FAPH, and category-level hard-negative FPR. Include threshold values, sliding-window settings, and confidence intervals where feasible.

---

## 9. Minimal two-stage verifier experiment

This is the most useful small experiment if v19 cannot fully solve selectivity.

**Experiment design**

1. Use the best high-recall microWakeWord checkpoint as stage 1.
2. On every trigger, save a short candidate window with pre-roll so the wake phrase is not clipped.
3. Run local Kiirkirjutaja/Sherpa-ONNX ASR on the candidate window.
4. Canonicalize the transcript:

   * lowercase;
   * remove punctuation;
   * map `kule` and `kuule` as accepted variants;
   * require `kuule/kule` followed immediately or near-immediately by `kratt`;
   * reject prefix-only, suffix-only, reversed order, and `kuule/kule <not kratt>`.
5. Measure:

   * stage-1 recall on exact positives;
   * verifier recall on true wake windows;
   * verifier rejection rate on hard negatives;
   * end-to-end recall and hard-negative FPR;
   * added latency.

**Thesis-safe interpretation**

Present this as an exploratory verifier, not as proof of production readiness. If it rejects many confusables but loses some true positives, that still supports the thesis claim that ordered textual/phonetic verification is promising but must be evaluated against recall and latency.

---

## 10. Suggested future-work section

Future work should move from binary clip-level detection toward explicit sequence verification. The first direction is a larger controlled hard-negative corpus for Estonian, generated with grapheme and phoneme edit rules and then recorded or synthesized with multiple voices. This would test whether the microWakeWord architecture can learn stricter selectivity when the negative class covers partials, reversed order, and `kuule/kule <not kratt>` cases.

A second direction is a local verifier cascade. The ESP32-S3 detector should be tuned for high recall and acceptable candidate rate, while a Raspberry Pi 5 verifier performs ASR, phoneme decoding, or a learned phrase-verification task. This keeps the privacy-first design while matching the multi-stage pattern used in production voice-trigger systems.

A third direction is sequence-based KWS: DNN-HMM, CTC, RNN-T, or phoneme-posterior keyword/filler decoding. These methods are better aligned with the requirement that `kuule/kule` must precede `kratt`, but they require more implementation effort than a microWakeWord data-cleaning iteration.

A fourth direction is personalization. For household deployments, a lightweight verifier trained from a few user examples may reduce false activations, but it should be evaluated separately from phrase selectivity because speaker filtering is not the same as exact phrase recognition.

Finally, future evaluations should include stable public-style regression sets: long ambient audio, real unseen speakers, prefix-only negatives, suffix-only negatives, reversed-order negatives, and near-phrase confusables. The benchmark should report frozen-threshold metrics so that improvements are not caused only by threshold retuning.

---

## 11. BibTeX entries for important sources

```bibtex
@misc{apple2017heysiri,
  author       = {{Siri Team}},
  title        = {Hey Siri: An On-device DNN-powered Voice Trigger for Apple's Personal Assistant},
  year         = {2017},
  howpublished = {Apple Machine Learning Research},
  url          = {https://machinelearning.apple.com/research/hey-siri}
}

@misc{apple2023voicetrigger,
  author       = {{Apple Machine Learning Research}},
  title        = {Voice Trigger System for Siri},
  year         = {2023},
  howpublished = {Apple Machine Learning Research},
  url          = {https://machinelearning.apple.com/research/voice-trigger}
}

@inproceedings{shrivastava2021optimize,
  author    = {Ashish Shrivastava and Arnav Kundu and Chandra Dhir and Devang Naik and Oncel Tuzel},
  title     = {Optimize What Matters: Training DNN-HMM Keyword Spotting Model Using End Metric},
  booktitle = {ICASSP},
  year      = {2021},
  eprint    = {2011.01151},
  archivePrefix = {arXiv},
  doi       = {10.48550/arXiv.2011.01151}
}

@inproceedings{wang2020lfmmi,
  author    = {Yiming Wang and Hang Lv and Daniel Povey and Lei Xie and Sanjeev Khudanpur},
  title     = {Wake Word Detection with Alignment-Free Lattice-Free MMI},
  booktitle = {Interspeech},
  year      = {2020},
  eprint    = {2005.08347},
  archivePrefix = {arXiv},
  doi       = {10.48550/arXiv.2005.08347}
}

@inproceedings{michaely2017contextual,
  author    = {Assaf Michaely and Carolina Parada and Frank Zhang and Gabor Simko and Petar Aleksic},
  title     = {Keyword Spotting for Google Assistant Using Contextual Speech Recognition},
  booktitle = {IEEE ASRU},
  year      = {2017}
}

@inproceedings{chen2021fakewake,
  author    = {Yanjiao Chen and Yijie Bai and Richard Mitev and Kaibo Wang and Ahmad-Reza Sadeghi and Wenyuan Xu},
  title     = {FakeWake: Understanding and Mitigating Fake Wake-up Words of Voice Assistants},
  booktitle = {ACM CCS},
  year      = {2021},
  eprint    = {2109.09958},
  archivePrefix = {arXiv},
  doi       = {10.1145/3460120.3485365}
}

@article{schoenherr2022accidental,
  author  = {Lea Sch{\"o}nherr and Maximilian Golla and Thorsten Eisenhofer and Jan Wiele and Dorothea Kolossa and Thorsten Holz},
  title   = {Unacceptable, where is my privacy? Exploring accidental triggers of smart speakers},
  journal = {Computer Speech \& Language},
  year    = {2022},
  eprint  = {2008.00508},
  archivePrefix = {arXiv}
}

@misc{zhang2025graphemeaug,
  author       = {Jie Zhang and others},
  title        = {GraphemeAug: A Systematic Approach to Synthesized Hard Negative Keyword Spotting Examples},
  year         = {2025},
  eprint       = {2505.14814},
  archivePrefix = {arXiv}
}

@misc{wang2022confusingwords,
  author       = {Haoxu Wang and Yan Jia and Zeqing Zhao and Xuyang Wang and Junjie Wang and Ming Li},
  title        = {Generating Adversarial Samples For Training Wake-up Word Detection Systems Against Confusing Words},
  year         = {2022},
  eprint       = {2201.00167},
  archivePrefix = {arXiv},
  doi          = {10.48550/arXiv.2201.00167}
}

@article{kumar2020wakewordverification,
  author  = {Rajath Kumar and Mike Rodehorst and Joe Wang and Jiacheng Gu and Brian Kulis},
  title   = {Building a robust word-level wakeword verification network},
  year    = {2020},
  url     = {https://www.amazon.science/publications/building-a-robust-word-level-wakeword-verification-network}
}

@misc{lugosch2018donut,
  author       = {Loren Lugosch and Samuel Myer and Vikrant Singh Tomar},
  title        = {DONUT: CTC-based Query-by-Example Keyword Spotting},
  year         = {2018},
  eprint       = {1811.10736},
  archivePrefix = {arXiv},
  doi          = {10.48550/arXiv.1811.10736}
}

@inproceedings{he2017rnntkws,
  author    = {Yanzhang He and Rohit Prabhavalkar and Kanishka Rao and Wei Li and Anton Bakhtin and Ian McGraw},
  title     = {Streaming Small-Footprint Keyword Spotting Using Sequence-to-Sequence Models},
  booktitle = {IEEE ASRU},
  year      = {2017}
}

@misc{zhang2017helloedge,
  author       = {Yundong Zhang and Naveen Suda and Liangzhen Lai and Vikas Chandra},
  title        = {Hello Edge: Keyword Spotting on Microcontrollers},
  year         = {2017},
  eprint       = {1711.07128},
  archivePrefix = {arXiv},
  doi          = {10.48550/arXiv.1711.07128}
}

@misc{warden2018speechcommands,
  author       = {Pete Warden},
  title        = {Speech Commands: A Dataset for Limited-Vocabulary Speech Recognition},
  year         = {2018},
  eprint       = {1804.03209},
  archivePrefix = {arXiv}
}

@misc{microwakeword,
  author       = {{Open Home Foundation Voice}},
  title        = {microWakeWord},
  year         = {2024},
  howpublished = {GitHub repository},
  url          = {https://github.com/OHF-Voice/micro-wake-word}
}

@misc{esphome_microwakeword,
  author       = {{ESPHome}},
  title        = {Micro Wake Word},
  year         = {2026},
  howpublished = {Documentation},
  url          = {https://esphome.io/components/micro_wake_word/}
}

@misc{openwakeword_verifier,
  author       = {David Scripka},
  title        = {openWakeWord Custom Verifier Models},
  year         = {2026},
  howpublished = {GitHub documentation},
  url          = {https://github.com/dscripka/openWakeWord/blob/main/docs/custom_verifier_models.md}
}
```

---

## 12. Search terms and sources checked

| Search/source checked                                  | What it contributed                                                                                | Specifically discusses multi-word partial-trigger failure?                                                                                                    |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Apple “Hey Siri” on-device voice trigger               | Metrics, two-word detector, threshold tradeoff, multi-stage checks, similar-phrase cancellation    | Partly; discusses two-word trigger and similar phrases, but not partial-trigger training as explicitly as later paper. ([Apple Machine Learning Research][2]) |
| Apple “Voice Trigger System for Siri”                  | Modern multi-stage architecture, phonetically similar false triggers, CTC checker, personalization | Discusses similar-sounding triggers; not focused on `prefix-only` but directly relevant. ([Apple Machine Learning Research][5])                               |
| Apple “Optimize What Matters” DNN-HMM KWS              | Partial-keyword hard negatives, swapped-order hard negatives, DET/FAPH evaluation                  | **Yes. This is the strongest direct source.** ([ar5iv][1])                                                                                                    |
| FakeWake                                               | Fuzzy/fake wake-word generation and mitigation                                                     | Discusses fake/fuzzy wake words; not specifically two-word prefix-only, but directly relevant to confusables. ([arXiv][3])                                    |
| Accidental triggers of smart speakers                  | Similar words/sounds causing real assistant false wakes; phone Levenshtein generation              | Discusses accidental similar triggers; not specifically multi-word partials. ([arXiv][8])                                                                     |
| GraphemeAug                                            | Systematic synthetic hard negatives via grapheme mutation; real-confusable robustness              | Discusses confusable generation; not specifically ordered two-word partials. ([arXiv][9])                                                                     |
| Adversarial confusing words for wake-up word detection | Generated confusing samples: concatenated, synthesized, partially masked                           | Discusses confusing words and partially masked keywords; relevant to partials. ([arXiv][16])                                                                  |
| Google contextual ASR KWS                              | KWS + ASR cascade reducing false accepts                                                           | Discusses ASR verification after trigger, not prefix-only failure. ([Google Research][17])                                                                    |
| Amazon wake-word verification                          | Secondary verifier after first-stage detection; temporal phonetic dependencies                     | Discusses wake verification and like-sounding words; not specifically prefix-only. ([Amazon Science][18])                                                     |
| DNN-HMM / LF-MMI wake-word detection                   | Keyword/filler and online decoding with partial labels                                             | Supports sequence/order-sensitive modeling; not phrase-partial examples in abstract. ([arXiv][4])                                                             |
| DONUT CTC KWS                                          | CTC query-by-example custom wake-word detection                                                    | Supports sequence-based custom wake words; not partial-trigger failure. ([arXiv][11])                                                                         |
| Google RNN-T small-footprint KWS                       | Sequence-to-sequence phoneme/grapheme keyword phrase detection                                     | Supports arbitrary ordered phrase detection; not partial-trigger failure. ([Google Research][19])                                                             |
| Meta alignment comparison                              | Alignment-based vs CTC/hybrid wake-word training                                                   | Supports alignment/objective discussion; not partial-trigger failure. ([AI Meta][20])                                                                         |
| ESPHome microWakeWord docs                             | Current deployment model, cutoff/VAD/sliding-window behavior                                       | Deployment details; no multi-word partial discussion. ([ESPHome - Smart Home Made Simple][6])                                                                 |
| microWakeWord GitHub                                   | TFLite Micro low-power custom wake-word framework; training difficulty                             | Deployment/training context; no partial-trigger discussion. ([GitHub][7])                                                                                     |
| Home Assistant Voice Chapter 6                         | Why microWakeWord is used on ESP32-S3; openWakeWord too large for ESP32-S3                         | Hardware/deployment context only. ([Home Assistant][21])                                                                                                      |
| openWakeWord custom verifier docs                      | Personalized verifier as a false-activation filter                                                 | Verifier context; not exact phrase-order verification. ([GitHub][12])                                                                                         |
| ESP32-S3, LiteRT Micro, Raspberry Pi 5 official docs   | Hardware feasibility boundaries                                                                    | Hardware only. ([Espressif Systems][13])                                                                                                                      |
| Kiirkirjutaja / Sherpa-ONNX                            | Local Estonian ASR feasibility                                                                     | ASR context; not wake-word-specific. ([GitHub][10])                                                                                                           |

**Search terms used included:** `wake word partial keyword hard negatives`, `DNN-HMM keyword spotting partial phrases`, `wake word swapped order hard negatives`, `FakeWake fuzzy wake words`, `smart speaker accidental triggers phone Levenshtein`, `GraphemeAug hard negative keyword spotting`, `adversarial confusing words wake-up word detection`, `keyword filler HMM wake word detection`, `CTC keyword spotting wake word`, `streaming small-footprint keyword spotting RNN-T`, `Google Assistant contextual ASR keyword spotting`, `Amazon wake word verification`, `microWakeWord ESPHome ESP32-S3`, `openWakeWord custom verifier`, `ESP32-S3 SRAM 240 MHz`, `Raspberry Pi 5 Cortex-A76`, and `Kiirkirjutaja Sherpa-ONNX Estonian ASR`.

[1]: https://ar5iv.labs.arxiv.org/html/2011.01151 "[2011.01151] Optimize what matters: Training DNN-HMM Keyword Spotting Model Using End Metric"
[2]: https://machinelearning.apple.com/research/hey-siri "Hey Siri: An On-device DNN-powered Voice Trigger for Apple’s Personal Assistant - Apple Machine Learning Research"
[3]: https://arxiv.org/abs/2109.09958 "[2109.09958] FakeWake: Understanding and Mitigating Fake Wake-up Words of Voice Assistants"
[4]: https://arxiv.org/abs/2005.08347 "[2005.08347] Wake Word Detection with Alignment-Free Lattice-Free MMI"
[5]: https://machinelearning.apple.com/research/voice-trigger "Voice Trigger System for Siri - Apple Machine Learning Research"
[6]: https://esphome.io/components/micro_wake_word/ "Micro Wake Word - ESPHome - Smart Home Made Simple"
[7]: https://github.com/OHF-Voice/micro-wake-word "GitHub - OHF-Voice/micro-wake-word: A TensorFlow based wake word detection training framework using synthetic sample generation suitable for certain microcontrollers. · GitHub"
[8]: https://arxiv.org/abs/2008.00508 "[2008.00508] Unacceptable, where is my privacy? Exploring Accidental Triggers of Smart Speakers"
[9]: https://arxiv.org/html/2505.14814v2 "GraphemeAug: A Systematic Approach to Synthesized Hard Negative Keyword Spotting Examples"
[10]: https://github.com/alumae/kiirkirjutaja "GitHub - alumae/kiirkirjutaja · GitHub"
[11]: https://arxiv.org/abs/1811.10736 "[1811.10736] DONUT: CTC-based Query-by-Example Keyword Spotting"
[12]: https://github.com/dscripka/openWakeWord/blob/main/docs/custom_verifier_models.md "openWakeWord/docs/custom_verifier_models.md at main · dscripka/openWakeWord · GitHub"
[13]: https://www.espressif.com/en/products/socs/esp32-s3 "ESP32-S3 Wi-Fi & BLE 5 SoC | Espressif Systems"
[14]: https://www.raspberrypi.com/products/raspberry-pi-5/ "Buy a Raspberry Pi 5 – Raspberry Pi"
[15]: https://developer.amazon.com/blogs/alexa/post/b136b3e7-0ba8-4589-aaf9-2a037fc4e9c9/cloud-based-wake-word-verification-improves-alexa-wake-word-accuracy-on-your-avs-products "Cloud-Based Wake Word Verification Improves “Alexa” Wake Word Accuracy on Your AVS Products : Alexa Blogs"
[16]: https://arxiv.org/abs/2201.00167 "[2201.00167] Generating Adversarial Samples For Training Wake-up Word Detection Systems Against Confusing Words"
[17]: https://research.google/pubs/keyword-spotting-for-google-assistant-using-contextual-speech-recognition/ "Keyword Spotting for Google Assistant Using Contextual Speech Recognition"
[18]: https://www.amazon.science/publications/building-a-robust-word-level-wakeword-verification-network "Building a robust word-level wakeword verification network - Amazon Science"
[19]: https://research.google/pubs/streaming-small-footprint-keyword-spotting-using-sequence-to-sequence-models/ "Streaming Small-Footprint Keyword Spotting Using Sequence-to-Sequence Models"
[20]: https://ai.meta.com/research/publications/handling-the-alignment-forwake-word-detection-a-comparison-between-alignment-based-alignment-free-and-hybrid-approaches/ "Handling the Alignment forWake Word Detection: A Comparison Between Alignment-Based, Alignment-Free and Hybrid Approaches | Research - AI at Meta"
[21]: https://www.home-assistant.io/blog/2024/02/21/voice-chapter-6/ "On device wake word on ESP32-S3 is here - Voice: Chapter 6 - Home Assistant"
