# Two-Stage Wake-Word Verification for Kratt

## Executive summary

- Two-stage wake-word cascades are established practice. Public descriptions from entity["company","Apple","Cupertino, CA, US"], entity["company","Google","Mountain View, CA, US"], and entity["company","Amazon","Seattle, WA, US"] all describe a small always-on detector that gates audio to a stronger second pass, whether that second pass is a larger trigger checker, contextual ASR, or a post-trigger false-trigger mitigation model. citeturn9view2turn19view0turn37view0turn9view8turn35search5

- Second-stage verifiers reduce false wakes because they can use richer evidence than a tiny streaming KWS model: a full transcript, an ordered phoneme sequence, a CTC sequence score, a localized wake-word verifier, speaker identity, or post-trigger intent cues. This is exactly the kind of added structure that helps when a stage-one detector overfires on prefixes or confusable phrases. citeturn22view1turn17view0turn15view0turn39view0turn8view0turn30search0

- For multi-word phrases, explicit sequence models are the clearest way to enforce order. Apple’s classic “Hey Siri” description explicitly says the system looks for the right sequence over time, while CTC and phoneme-sequence approaches score an ordered label sequence rather than an unordered acoustic similarity. That makes them much better conceptual fits for “Kuule/Kule” followed by “Kratt,” and much worse fits for `kratt kuule`, `kuule` alone, or `kratt` alone. citeturn19view1turn15view0turn27view1turn39view0

- ASR-backed verification is therefore a defensible approach for Kratt, but only as a **second-stage safety check**, not as proof that the wake phrase problem is “solved.” entity["company","Google","Mountain View, CA, US"] reported an 89% false-accept reduction with only a ~0.2% false-reject increase using server-side contextual ASR after first-pass KWS, but that system had large-server resources and multilingual production infrastructure that Kratt does not. citeturn37view0

- Public industrial results also show that post-trigger verification can be very strong even without full LVCSR. Apple’s streaming false-trigger mitigation work reports up to 95.8% rejection of unintended false triggers with one additional second of post-trigger audio, and Amazon’s older two-stage on-device system reported that a tiny second-stage classifier could cut false alarms by about 67% on top of first-stage hypotheses. citeturn14view1turn22view2

- The tradeoff is real: any stricter verifier will lose some true activations, and every extra 300–1000 ms of audio context adds wake latency. That tradeoff is normal in wake-word engineering; Apple, ESPHome, and Picovoice all document threshold tuning as a false-accept versus false-reject balance, not a free win. citeturn19view1turn8view2turn25view1

- For Kratt specifically, the highest-ROI option before a BSc deadline is **not** to train a new phonetic/CTC verifier from scratch. The most realistic next step is a **small local Raspberry Pi-side diagnostic verifier** that runs only after microWakeWord fires and checks whether a short localized Estonian transcript contains `kuule|kule` before `kratt`. That reuses the existing Kiirkirjutaja stack instead of rewriting the architecture. citeturn8view2turn8view3turn24view0turn24view1turn8view6

- Your own 101-clip probe already points the same way as the literature: strict ordered transcript matching looks promising for rejecting confusables and reversed order, but too brittle to be the default acceptance rule because it loses too many positives. So the thesis-safe claim is not “ASR verification solves wake words,” but “ASR verification is a promising local false-trigger filter worth evaluating as a second-stage gate.” This conclusion is consistent with industrial practice and with your current empirical subset.

- If privacy is a hard requirement, local verification is materially better than cloud confirmation. Industry commonly uses cloud confirmation, but that means the first-stage false trigger can still upload audio; third-party analyses and Google’s own privacy explanation both confirm that the device processes short local buffers first and then sends audio after activation. A local Kratt verifier avoids that extra privacy cost. citeturn18view1turn18view0turn18view2

- The best thesis framing is therefore conservative: **binary clip-level wake-word models can be weak at exact multi-word phrase selectivity; a local ASR verifier is a defensible proof-of-concept mitigation and a useful diagnostic tool, but not yet a production guarantee.** That framing is evidence-based, implementable in time, and compatible with your existing evaluation contract. citeturn14view3turn17view0turn37view0turn39view0

## Evidence table

| Source | System / method | Verifier type | Reported benefit | Relevance to Kratt |
|---|---|---|---|---|
| Apple 2017 + Apple 2023 | Siri multistage voice trigger | Small always-on detector, then larger checker; optional speaker ID; downstream “directed speech” filtering | Apple explicitly documents two-pass on-device detection and later a broader multistage architecture where candidate audio is rechecked by a higher-precision system. citeturn19view0turn9view2 | Strong evidence that “high-recall first pass + stricter second pass” is standard, not exotic. |
| Sigtia et al. 2020 | Smart-speaker voice trigger detection | Second-pass phonetic detector trained with multitask learning on confusable examples | The paper describes a two-stage cascade and reports roughly halving errors on challenging confusable conditions without adding parameters. citeturn14view3turn14view2 | Very close to Kratt’s problem statement: hard negatives and confusable phrases after stage-one activation. |
| Garg et al. 2021 | Two-stage VTD + false-trigger mitigation | Shared streaming encoder with phonetic transcription branch plus phrase-discrimination branch using post-trigger context | Average 18% relative FRR reduction at fixed false alarms, and up to 95.8% unintended false-trigger mitigation with one extra second of audio. citeturn14view1turn17view0 | Strong support for localized post-trigger verification as a real engineering technique. |
| Wu et al. 2018 | On-device Alexa wake-word stack | DNN-HMM first pass + tiny second-stage classifier with richer background modeling | About 16% relative FRR reduction at fixed alarms, about 37% FAR reduction at fixed miss rate, and ~67% FAR reduction from the second stage itself. citeturn22view2turn22view3 | Shows that even a lightweight verifier can materially improve first-pass hypotheses. |
| Kumar et al. 2020 | Alexa wake-word verification | Localized single-pass second-stage verifier; compared with ASR confidence and 2-stage DNN-HMM baselines | The proposed verifier beat ASR-confidence and classical phonetic baselines under both accurate and noisy alignment conditions. citeturn22view0turn22view1 | Important warning: plain ASR confidence is not always the strongest verifier, but it is a valid baseline. |
| Michaely et al. 2017 | Google Assistant client-server KWS | Server-side contextual ASR over wake phrase + query, then string match for trigger phrase | 89% reduction in false accepts, about 0.2% increase in false rejects, and improved WER by decoding trigger + command jointly. citeturn37view0 | Best direct evidence that ASR-based wake verification can work well in practice; also shows the latency/privacy tradeoff of server-side confirmation. |
| Lugosch et al. 2018 | DONUT | CTC-based query-by-example KWS using phoneme label-sequence hypotheses | Low-compute embedded-friendly method that models the wake phrase as an ordered label sequence, not just a single binary class. citeturn12view0turn15view0 | Useful conceptual template for future work if transcript matching proves too brittle. |
| Zhang et al. 2023 | U2-KWS | Two-pass open-vocabulary KWS: CTC first pass + decoder second pass | 41% relative wake-up-rate improvement at 0.5 false alarms/hour, with explicit first-pass/second-pass design. citeturn39view0 | Modern research support for sequence-aware two-pass KWS, but too large a jump for a last-minute thesis rewrite. |
| Lee & Cho 2023 | PhonMatchNet | Zero-shot phoneme-guided KWS with phoneme-level loss | Strong improvements on similar-pronunciation cases, with the phoneme-level loss specifically helping distinguish confusable words. citeturn15view2turn15view3 | Relevant to `kuule rott / kuule robot / kuule kraam`-type negatives; useful as future-work justification. |
| openWakeWord docs | Custom verifier models | Speaker-focused logistic-regression verifier invoked only after base threshold crossing | Documentation says a custom verifier can significantly reduce false activations, but it is aimed at known target speakers rather than phrase-order verification. citeturn8view0 | Relevant mostly as a taxonomy example; not the right primary fix for Kratt’s exact-order problem. |
| ESPHome + Home Assistant + Kiirkirjutaja docs | Kratt deployment stack | microWakeWord on low-power edge; Assist/Wyoming/local STT on server | ESPHome exposes threshold and window controls; Home Assistant supports external wake/STT services over Wyoming; Kiirkirjutaja is real-time STT built on streaming transducer + Sherpa-ONNX. citeturn8view2turn8view5turn8view6turn8view3turn24view0 | Confirms that “tiny edge wake word + heavier local post-trigger compute” fits your architecture. |
| Picovoice docs | Porcupine | Primarily one-stage on-device KWS with tunable sensitivity | Under-1MB runtime, small per-keyword files, and tunable sensitivity are emphasized, but no public second-stage verifier is presented in the docs. citeturn25view0turn25view1 | Useful contrast: mature one-stage KWS can work well, but it does not answer Kratt’s exact-order confusable issue. |

## Technical taxonomy of second-stage verifiers

The literature splits second-stage wake verification into a few practical families.

### Full-transcript ASR verification

This is the clearest version of “did the user really say the phrase I want?” A first-stage detector opens a short audio window, a stronger ASR system decodes that window, and acceptance becomes transcript logic. Google’s contextual KWS system does exactly that: after on-device triggering, the server decodes the trigger phrase and subsequent speech, and if the transcript does not contain the wake phrase, the query is suppressed. The paper reports a large reduction in false accepts with only a small false-reject increase. citeturn37view0

For Kratt, the attraction is obvious. You already have a local Estonian ASR stack, so the verifier can simply ask whether the localized transcript contains `kuule` or `kule` before `kratt`. This enforces **lexical identity** and **word order** in a way a binary wake-word classifier often does not. Reversed order, single-word prefixes, and many confusable ordinary phrases should fail because the transcript or rule does not match the ordered pattern. The weakness is equally clear: if the STT drops one of the two words, merges them, or substitutes `Kratt`, recall suffers immediately. That is exactly what your existing probe is already showing.

### Phoneme, CTC, and sequence-score verification

These methods do not necessarily need a full word transcript. Instead, they score whether the audio supports an **ordered sequence** of labels such as phonemes, graphemes, or HMM states. This family includes classical keyword/filler graphs, phoneme-loop background models, CTC forward scoring, and newer two-pass open-vocabulary systems. citeturn27view0turn27view1turn22view1turn39view0

For enforcing exact phrase order, this family is arguably the most principled. DONUT models the custom wake phrase as a sequence of labels and uses CTC to score that sequence; U2-KWS uses a CTC first pass and a decoder second pass; classical keyword/filler systems accept only legal phone paths for the target word sequence and compare them against filler/background paths. citeturn15view0turn39view0turn27view1

This is also where “prefix confusable” negatives are best conceptualized. A phoneme-sequence or keyword/filler system can reject `kuule` alone because the required second word never arrives, reject `kratt` alone because the first word is missing, and reject `kratt kuule` because the legal path order is wrong. However, these gains depend on having either phoneme posteriors, CTC outputs, or a wake-only decoding graph. That is why this family is technically strong but not the easiest late-stage thesis addition.

### Wake-word-specific localized binary verifiers

Industrial systems often use a second-stage model that is still a classifier, but a stronger one with more context and a better training objective. Apple’s multitask second-pass detector re-scores candidate segments using a phonetic model plus confusable training examples. Amazon’s wake-word verifier compares several baselines, including ASR confidence and phonetic systems, against a stronger localized verifier that operates on the post-trigger audio frame. citeturn14view3turn14view2turn22view0turn22view1

This family is pragmatic and production-friendly, but it has a danger that is especially relevant for Kratt: if the model is still fundamentally optimized as a binary accept/reject classifier over localized windows, it may still learn a permissive “wake-like acoustic pattern” rather than a robust two-word ordered structure. Your own findings already point in that direction. So this family is viable, but only if the training data and loss are explicitly engineered around the confusables you care about.

### Speaker-personalized verifiers

These verifiers ask not only “was the phrase said?” but also “was it said by the enrolled user?” Apple’s older Siri stack includes a personalized stage, and openWakeWord exposes custom verifier models that act as a filter over the base model and are explicitly described as most effective when the deployment target is a known speaker or small set of speakers. Google also has published text-dependent speaker verification work for the global password “Ok Google.” citeturn19view1turn8view0turn9view4

This is relevant to taxonomy, but it is not the best answer to Kratt’s problem. Your reported failure mode is **phrase selectivity**, not “wrong household member woke the device.” A speaker verifier could be an optional future extension for a single-user setup, but it does not solve `kuule rott` versus `kuule kratt`.

### Device-directed or intent verifiers

A final family looks at the **whole post-wake utterance** and asks whether the speech was intended for the device at all. Apple’s current Siri stack includes “Siri directed speech detection,” and Amazon has published device-directed utterance detection models that combine acoustics, ASR hypotheses, and decoder features to reject unintended interactions. citeturn9view2turn30search0

These are valuable for reducing accidental wake-ups from background conversations or follow-up misuse, but they are downstream of the exact wake phrase problem. For Kratt, they are useful context and future work, not the first thesis experiment.

## Recommended Kratt design options ranked by ROI and thesis risk

### Pi-side ASR verifier on localized wake snippets

**Rank:** highest ROI, lowest thesis risk.

This is the most defensible immediate step. microWakeWord remains the always-on trigger on the ESP32-S3, and the Raspberry Pi-side verifier runs only after a trigger using a short localized buffer. The verifier applies deterministic ordered matching rules to Kiirkirjutaja output. This is architecturally consistent with commercial two-stage systems and with Home Assistant’s “light edge trigger, heavier local server compute” model. ESPHome already exposes the stage-one operating point; Home Assistant and Wyoming already support local wake/STT services; Kiirkirjutaja is already a real-time streaming recognizer. citeturn8view2turn8view5turn8view6turn8view3turn24view0

Why it fits Kratt: it reuses infrastructure you already have, allows an exact ordered phrase rule, and can be deployed first as an **offline diagnostic** and later as an optional **live safety mode**. It does not require new model training. The main risk is recall loss if the transcript is brittle. Your own 101-clip probe says that risk is real, which is why this should begin as a diagnostic or optional gate, not as a thesis claim of production readiness.

### Local ASR verifier with slightly fuzzy ordered rules

**Rank:** high ROI, moderate thesis risk.

This is really a refinement of the first option, not a totally different architecture. Instead of requiring a strict exact transcript, you normalize casing, punctuation, and known orthographic variants, and accept only a **small whitelist** such as `{kuule, kule}` followed by `{kratt}` in order. If development data shows consistent benign ASR variants for `Kratt`, you may add them carefully, but only if they do not re-open the confusable failure modes.

This should be your preferred **research experiment**, because it directly addresses the evidence gap in your current probe: strict matching looks excellent on hard negatives but too harsh on positives. A small whitelist-based fuzzy rule is a thesis-sized intervention. It is also very easy to explain academically.

### Lightweight phonetic or CTC verifier

**Rank:** medium ROI, high thesis risk before deadline.

From a modeling perspective, this is arguably the cleanest solution to exact phrase order. A small phoneme/CTC verifier could explicitly score the sequences for `kuule kratt` and `kule kratt` and reject everything else. The literature strongly supports this family for ordered wake phrases and open-vocabulary KWS. citeturn15view0turn39view0turn27view1turn15view3

But it is a larger engineering step. You would need either phoneme posteriors from an existing model, a wake-only sequence decoder, or new model training. That is likely too much deviation from the stated thesis scope of “do not reinvent STT/TTS” and too risky near deadline. I would keep this as **future work**, unless you already have a nearly free route to phoneme posteriors from the Estonian STT stack.

### Custom localized binary verifier trained on Kratt hard negatives

**Rank:** medium ROI, medium-high thesis risk.

You could train a second-stage binary classifier on first-stage trigger snippets, including `kuule`, `kule`, `kratt`, reversed order, and confusables. This is similar in spirit to Apple/Amazon second-pass work. citeturn14view3turn22view2

The problem is that this pushes the thesis toward training **another** wake model and may still not impose the phrase order strongly enough unless you make it explicitly sequence-aware. Since your existing evidence already suggests that a binary decision surface can become permissive, this is less attractive than transcript-based verification for a conservative thesis.

### Keep ESP32-only and do not add a verifier

**Rank:** safest integration, lowest upside for your stated failure mode.

This may still be the right fallback demo architecture if a verifier hurts recall too much. But it is unlikely to solve the exact issue you care about. microWakeWord and ESPHome expose threshold and window tuning, and VAD can reduce non-speech false accepts, but those controls are not designed to guarantee exact two-word order against speech confusables. citeturn8view2

For the thesis, this should remain the **baseline** and active demo path if needed, but not the recommended answer to the research question.

### Integration recommendation

If you do a live prototype, the lowest-risk shape is not to modify core Home Assistant Assist deeply. The published pipeline structure has a single `wake_word` gate before STT, which implies that a second verifier must either be folded into a custom wake-word service or run as an outer wrapper around the Assist invocation. That is an engineering inference from the official pipeline design, not something Home Assistant documents as an off-the-shelf feature. citeturn8view5turn8view6

So the practical order of operations is:

1. Offline verifier experiment on saved clips and saved first-stage triggers.
2. Optional local “safety mode” for demos, implemented outside the default pipeline if necessary.
3. Anything more ambitious goes in future work.

## Minimal diagnostic experiment plan for the existing repo and data

The goal of the experiment should be modest: **measure whether a local second-stage verifier improves the combined system on the confusable cases you already know matter, without claiming a full architecture rewrite.**

### Data partitions

Create three partitions.

A **development** split is used for rule design: transcript normalization, accepted variants, clip window length, and any confidence thresholds. A **held-out internal test** split is used once after rules are frozen. A **final thesis user-test or unseen-speaker split** remains untouched until the end. This is the only way to avoid accidentally tuning on the final story.

Keep speaker separation strict. If possible, keep at least one held-out speaker group that never appears during rule design. If you have sequential recordings from the same session, keep sessions together to avoid leakage.

### Inputs

Use two input types.

The first is your existing labelled wake and hard-negative clips. That gives you clean conditional verifier numbers: “if I run the verifier on this clip, how often does it accept the true wake and reject confusables?” The second is **actual first-stage trigger snippets** collected from continuous background runs. That is the only path to honest combined false-accept estimates in per-hour units.

For each first-stage activation, save a localized window around the trigger. Based on the industrial literature, a practical starting point is a short pre-trigger buffer plus enough post-trigger audio to finish the wake phrase cleanly. Amazon’s verifier literature uses localized windows under two seconds and explicitly studies pre/post context; Apple’s false-trigger mitigation work shows that up to one additional second of post-trigger audio can help a lot. citeturn17view2turn14view1

A sensible Kratt-first diagnostic window would be something like **0.4–0.6 s before** the trigger and **0.8–1.2 s after** it. If that clips the beginning of `Kuule`, extend the pre-trigger side before changing anything else.

### Verifier rules

Evaluate at least four rules, all frozen before final held-out testing.

A **strict ordered transcript rule** accepts only when normalized output contains `kuule kratt` or `kule kratt` in that order.

A **small-whitelist fuzzy ordered rule** accepts a tiny set of development-approved orthographic variants for the first word and perhaps one safe variant for the second word, but still requires order and rejects any transcript where `kratt` appears before `kuule|kule`.

A **wake-like loose rule** is useful only as a baseline, not as a deployment candidate. It tells you how much recall can be recovered by relaxing transcript logic, and how quickly false accepts return.

If Kiirkirjutaja or the decoder wrapper exposes any confidence, n-best, or partial hypothesis information, add a **confidence-aware rule**. For example: accept if the ordered phrase appears in the 1-best output, or appears in the n-best output with reasonable confidence and no stronger conflicting hypothesis. Google’s contextual KWS system is essentially a string-match verifier on top of a stronger ASR stack, so this is a defensible baseline family even if your implementation is much simpler. citeturn37view0

Do **not** add many fuzzy variants. With your negative set, the easiest way to re-break the system is to let the verifier become too permissive again.

### Metrics

Report stage one and stage two separately, then the combined system.

For stage one, report the frozen-threshold metrics you already care about: recall/FRR on real wake data, hard-negative FPR on prefix/confusable sets, and false accepts per hour on background runs.

For the verifier alone, report:

- acceptance rate on true wake clips,
- rejection rate on hard negatives,
- rejection rate on first-stage false-trigger snippets,
- median and P95 extra latency,
- a breakdown of false rejects by cause.

For the combined system, report:

- **combined recall**: proportion of true wake events that both trigger stage one and pass the verifier,
- **combined hard-negative acceptance**: proportion of hard negatives that both trigger stage one and pass the verifier,
- **combined FAPH** on continuous background runs: first-stage false activations that also pass the verifier, divided by background hours.

One important thesis note: do **not** convert clip-level negative acceptance into per-hour false-accept claims. Per-hour numbers require actual background-hour denominators.

### Failure analysis

After the main metrics, manually label the verifier’s failures into a small number of buckets:

- first word dropped,
- second word substituted,
- reversed order,
- partial phrase only,
- ordinary confusable phrase,
- truncation due to buffer/VAD,
- accent/pronunciation issue,
- noise/reverberation issue.

This analysis is likely to be as valuable as the topline number, because it tells you whether the verifier is mostly an ASR-quality problem, a buffer-timing problem, or a true phrase-modeling problem.

### Minimal coding path

The smallest thesis-sized implementation is:

- export localized trigger snippets,
- batch-decode them with Kiirkirjutaja,
- run deterministic ordered-match rules,
- store transcript, decision, and latency,
- generate a combined confusion report.

That is enough for a serious diagnostic section. A live demo integration can come later only if the offline result is clearly positive.

## Thesis wording

A conservative thesis-safe wording could be:

> The experiments suggest that a binary wake-word detector trained at clip level may not always encode exact multi-word phrase order strongly enough for a production wake phrase such as “Kuule Kratt”. In particular, prefix-only and phonetically confusable utterances can remain problematic even when ambient false activations are reduced. Public industrial wake-word systems commonly address this by using a second-stage verifier after an initial always-on detector. citeturn14view3turn17view0turn37view0

> In the Kratt prototype, a local ASR-based verifier is therefore a defensible second-stage mitigation strategy. The proposed verifier does not replace the microcontroller-side wake detector, but re-checks only those short audio segments that already triggered the first stage. This approach is compatible with a privacy-first local architecture, because verification can be performed on the local server rather than in the cloud, and it allows the system to enforce that the accepted wake phrase contains the ordered sequence “Kuule/Kule” followed by “Kratt”. citeturn8view2turn8view6turn8view3turn24view0turn18view1

> However, the present work should not claim that ASR verification fully solves wake-word detection. The current evidence supports a narrower conclusion: a local second-stage verifier is a promising proof-of-concept and diagnostic tool for reducing prefix/confusable false activations, but its effect on recall, latency, and unseen-speaker robustness must be established empirically under frozen thresholds. For this reason, verifier results should be reported as combined-system measurements rather than as a replacement metric for the first-stage detector alone. citeturn19view1turn8view2turn37view0

## BibTeX entries

Below are the sources I would treat as the most important for the thesis narrative. For each one, I note what it supports; the BibTeX follows afterward.

- **Hey Siri: An On-device DNN-powered Voice Trigger for Apple’s Personal Assistant** — Apple, 2017. Supports the claim that two-pass on-device trigger detection and sequence-based phrase scoring are standard, and that later stages can include speaker-aware checks and server cancellation. citeturn19view0turn19view1
- **Voice Trigger System for Siri** — Apple, 2023. Supports the claim that current commercial systems are multistage and may include checker, speaker identification, and directed-speech filtering. citeturn9view2
- **Multi-Task Learning for Voice Trigger Detection** — Siddharth Sigtia et al., 2020, ICASSP. Supports the claim that second-pass detectors trained on confusable examples are useful and standard. citeturn14view3turn14view2
- **Streaming Transformer for Hardware Efficient Voice Trigger Detection and False Trigger Mitigation** — Vineet Garg et al., 2021, Interspeech. Supports the claim that post-trigger context can reject a large fraction of false triggers. citeturn14view1
- **Monophone-Based Background Modeling for Two-Stage On-Device Wake Word Detection** — Minhua Wu et al., 2018, ICASSP. Supports the claim that a tiny second stage can materially improve first-pass wake hypotheses. citeturn22view2
- **Building a Robust Word-Level Wakeword Verification Network** — Rajath Kumar et al., 2020, Interspeech. Supports the claim that ASR confidence, phonetic models, and stronger localized verifiers are all valid second-stage baselines, but not equally strong. citeturn22view0turn22view1
- **Keyword Spotting for Google Assistant Using Contextual Speech Recognition** — Assaf Michaely et al., 2017, ASRU. Supports the claim that ASR-based wake verification can sharply reduce false accepts while only slightly increasing false rejects. citeturn37view0
- **DONUT: CTC-based Query-by-Example Keyword Spotting** — Loren Lugosch et al., 2018. Supports the claim that ordered label-sequence scoring is an embedded-friendly alternative for wake verification. citeturn12view0turn15view0
- **Wake Word Detection with Alignment-Free Lattice-Free MMI** — Yiming Wang et al., 2020, Interspeech. Supports the claim that keyword/filler and sequence-based phonetic approaches remain strong for wake-word detection. citeturn27view1
- **U2-KWS: Unified Two-pass Open-vocabulary Keyword Spotting with Keyword Bias** — Ao Zhang et al., 2023/ASRU 2023. Supports the claim that modern open-vocabulary KWS also tends toward first-pass candidate generation plus second-pass validation. citeturn39view0
- **PhonMatchNet: Phoneme-Guided Zero-Shot Keyword Spotting for User-Defined Keywords** — Yong-Hyeok Lee and Namhyun Cho, 2023, Interspeech. Supports the claim that phoneme-level objectives help distinguish similar pronunciations. citeturn15view2turn15view3
- **openWakeWord custom verifier models** — project documentation. Supports the taxonomy point that speaker-focused second-stage verifiers are common in practice, but they solve a different problem from exact phrase-order verification. citeturn8view0
- **ESPHome microWakeWord / Home Assistant Assist and Wyoming docs / Kiirkirjutaja docs** — official engineering documentation. Supports the claim that Kratt’s edge-first-stage and Pi-side heavier compute split is realistic in the existing local stack. citeturn8view2turn8view5turn8view6turn8view3turn24view0

```bibtex
@article{apple2017_heysiri,
  title   = {Hey Siri: An On-device DNN-powered Voice Trigger for Apple's Personal Assistant},
  author  = {{Apple}},
  year    = {2017},
  url     = {https://machinelearning.apple.com/research/hey-siri},
  note    = {Apple Machine Learning Research, October 2017}
}

@article{apple2023_voice_trigger_system,
  title   = {Voice Trigger System for Siri},
  author  = {{Apple}},
  year    = {2023},
  url     = {https://machinelearning.apple.com/research/voice-trigger},
  note    = {Apple Machine Learning Research, August 2023}
}

@inproceedings{sigtia2020_multitask_vtd,
  title     = {Multi-Task Learning for Voice Trigger Detection},
  author    = {Sigtia, Siddharth and Clark, Pascal and Haynes, Rob and Richards, Hywel and Bridle, John},
  booktitle = {ICASSP 2020 - 2020 IEEE International Conference on Acoustics, Speech and Signal Processing},
  year      = {2020},
  doi       = {10.1109/ICASSP40776.2020.9053577},
  url       = {https://arxiv.org/abs/2001.09519}
}

@inproceedings{garg2021_streaming_transformer_vtd_ftm,
  title     = {Streaming Transformer for Hardware Efficient Voice Trigger Detection and False Trigger Mitigation},
  author    = {Garg, Vineet and Chang, Wonil and Sigtia, Siddharth and Adya, Saurabh and Simha, Pramod and Dighe, Pranay and Dhir, Chandra},
  booktitle = {Interspeech 2021},
  year      = {2021},
  pages     = {4209--4213},
  doi       = {10.21437/Interspeech.2021-1428},
  url       = {https://arxiv.org/abs/2105.06598}
}

@inproceedings{wu2018_monophone_background_modeling,
  title     = {Monophone-Based Background Modeling for Two-Stage On-Device Wake Word Detection},
  author    = {Wu, Minhua and Panchapagesan, Sankaran and Sun, Ming and Gu, Jiacheng and Thomas, Ryan and Vitaladevuni, Shiv Naga Prasad and Hoffmeister, Bjorn and Mandal, Arindam},
  booktitle = {ICASSP 2018 - 2018 IEEE International Conference on Acoustics, Speech and Signal Processing},
  year      = {2018},
  doi       = {10.1109/ICASSP.2018.8462227},
  url       = {https://www.amazon.science/publications/monophone-based-background-modeling-for-two-stage-on-device-wake-word-detection}
}

@inproceedings{kumar2020_wordlevel_wakeword_verification,
  title     = {Building a Robust Word-Level Wakeword Verification Network},
  author    = {Kumar, Rajath and Rodehorst, Mike and Wang, Joe and Gu, Jiacheng and Kulis, Brian},
  booktitle = {Interspeech 2020},
  year      = {2020},
  pages     = {1972--1976},
  doi       = {10.21437/Interspeech.2020-2018},
  url       = {https://www.amazon.science/publications/building-a-robust-word-level-wakeword-verification-network}
}

@inproceedings{michaely2017_google_contextual_kws,
  title     = {Keyword Spotting for Google Assistant Using Contextual Speech Recognition},
  author    = {Michaely, Assaf Hurwitz and Zhang, Xuedong and Simko, Gabor and Parada, Carolina and Aleksic, Petar},
  booktitle = {2017 IEEE Automatic Speech Recognition and Understanding Workshop (ASRU)},
  year      = {2017},
  pages     = {272--278},
  doi       = {10.1109/ASRU.2017.8268946},
  url       = {https://research.google/pubs/keyword-spotting-for-google-assistant-using-contextual-speech-recognition/}
}

@article{lugosch2018_donut,
  title   = {DONUT: CTC-based Query-by-Example Keyword Spotting},
  author  = {Lugosch, Loren and Myer, Samuel and Tomar, Vikrant Singh},
  journal = {arXiv preprint arXiv:1811.10736},
  year    = {2018},
  doi     = {10.48550/arXiv.1811.10736},
  url     = {https://arxiv.org/abs/1811.10736}
}

@inproceedings{wang2020_lfmmi_wakeword,
  title     = {Wake Word Detection with Alignment-Free Lattice-Free MMI},
  author    = {Wang, Yiming and Lv, Hang and Povey, Daniel and Xie, Lei and Khudanpur, Sanjeev},
  booktitle = {Interspeech 2020},
  year      = {2020},
  pages     = {4258--4262},
  doi       = {10.21437/Interspeech.2020-1811},
  url       = {https://www.isca-archive.org/interspeech_2020/wang20ga_interspeech.html}
}

@article{zhang2023_u2kws,
  title   = {U2-KWS: Unified Two-pass Open-vocabulary Keyword Spotting with Keyword Bias},
  author  = {Zhang, Ao and Zhou, Pan and Huang, Kaixun and Zou, Yong and Liu, Ming and Xie, Lei},
  journal = {arXiv preprint arXiv:2312.09760},
  year    = {2023},
  doi     = {10.48550/arXiv.2312.09760},
  url     = {https://arxiv.org/abs/2312.09760}
}

@inproceedings{lee2023_phonmatchnet,
  title     = {PhonMatchNet: Phoneme-Guided Zero-Shot Keyword Spotting for User-Defined Keywords},
  author    = {Lee, Yong-Hyeok and Cho, Namhyun},
  booktitle = {Interspeech 2023},
  year      = {2023},
  url       = {https://www.isca-archive.org/interspeech_2023/lee23d_interspeech.html}
}

@misc{openwakeword_custom_verifier_docs,
  title        = {Custom Verifier Models},
  author       = {{openWakeWord project}},
  year         = {2024},
  url          = {https://github.com/dscripka/openWakeWord/blob/main/docs/custom_verifier_models.md},
  note         = {Project documentation}
}

@misc{esphome_microwakeword_docs,
  title        = {Micro Wake Word},
  author       = {{ESPHome}},
  year         = {2026},
  url          = {https://esphome.io/components/micro_wake_word/},
  note         = {Official component documentation}
}

@misc{homeassistant_voice_pipelines_docs,
  title        = {Assist Pipelines},
  author       = {{Home Assistant}},
  year         = {2026},
  url          = {https://developers.home-assistant.io/docs/voice/pipelines/},
  note         = {Developer documentation}
}

@misc{homeassistant_wyoming_docs,
  title        = {Wyoming Protocol},
  author       = {{Home Assistant}},
  year         = {2026},
  url          = {https://www.home-assistant.io/integrations/wyoming/},
  note         = {Official integration documentation}
}

@misc{kiirkirjutaja_repo,
  title        = {Kiirkirjutaja},
  author       = {Alum{\"a}e, Tanel and collaborators},
  year         = {2021},
  url          = {https://github.com/alumae/kiirkirjutaja},
  note         = {Project source code and documentation}
}

@inproceedings{podziubanchuk2026_simulst_estonian,
  title     = {Simultaneous Speech-to-Text Translation Web Application for Estonian Live Captions},
  author    = {Podziubanchuk, Bohdan and others},
  booktitle = {Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics: System Demonstrations},
  year      = {2026},
  url       = {https://aclanthology.org/2026.eacl-demo.40/}
}
```

## Caveats and what not to claim

Do not claim that an ASR verifier is already a deployable production fix for Kratt. The strongest defensible statement is that it is a **promising local second-stage mitigation** whose utility must be measured in the combined system. That is exactly how industrial papers frame these methods: as tradeoffs among false accepts, false rejects, localization accuracy, and extra context, not as magic add-ons. citeturn14view1turn22view2turn37view0

Do not claim per-hour false-accept improvement from clip-only experiments. False accepts per hour require real background-hour evaluation, not just confusable clips. Apple’s own reporting language and wake-word literature treat false alarms per hour as a deployment metric tied to negative audio duration. citeturn19view1turn32search9

Do not claim that speaker verifiers or VAD solve your exact problem. They can help with non-speech or non-target-speaker activations, but they are not the main answer to prefix-only and wrong-order speech confusions. citeturn8view0turn8view2turn19view1

Do not claim that Home Assistant already provides a built-in post-trigger verifier hook for this design. The official docs clearly show a wake-word gate and then STT; using a second verifier appears feasible, but likely requires a wrapper or custom service rather than a one-click built-in setting. That is an engineering inference, not a documented product feature. citeturn8view5turn8view6

Do not claim published real-time latency for the exact combination of Kiirkirjutaja INT8 plus Raspberry Pi 5 unless you measure it yourself. The sources confirm streaming transducer architecture and int8-capable decoding infrastructure, but I did not find a published benchmark for your exact deployment bundle. citeturn8view3turn24view0turn24view1

Open questions that remain after this review are straightforward: whether Kiirkirjutaja exposes confidence or n-best outputs conveniently enough for a better verifier, how much pre-trigger buffering is needed so the first word is not clipped, and whether an ordered fuzzy transcript rule can recover enough recall to justify live deployment. Those are exactly the right questions for a thesis-sized diagnostic experiment.