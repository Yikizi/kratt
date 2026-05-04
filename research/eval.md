# Defensible wake-word evaluation protocol and fair external baselines for Kratt

## Executive summary

For a BSc thesis at entity["organization","Tallinn University of Technology","Tallinn, Estonia"], the most defensible framing is **not** “we built a production-ready wake word,” but “we built an Estonian wake-word prototype and corrected the evaluation methodology so that future claims are scientifically meaningful.” The literature and official engineering documentation are strongly aligned on one point: wake-word quality is fundamentally a **trade-off between false alarms per hour and false rejects**, and that trade-off must be reported at a clearly defined operating point. citeturn16view1turn15search2turn23search0turn19view0

The single biggest methodological correction is to treat wake-word detection as a **streaming event-detection task**, not a clip classifier. False accepts should be counted per hour of continuous negative audio using the detector’s actual streaming logic, smoothing, and trigger rules. Official documentation for openWakeWord uses about 5.5 hours of far-field dinner-party audio for false-accept testing, and microWakeWord explicitly says it estimates false accepts per hour from long-duration ambient clips to simulate streaming rather than relying on ordinary clip classification. citeturn10view1turn13view0turn31search0turn37search2

A second major conclusion is that **operating point matters more than raw “accuracy.”** Academic and industrial sources commonly report FRR at a fixed FA/h level such as 0.1, 0.5, 1.0, or 1 per 10 hours. Those are not interchangeable conventions. A model evaluated at 0.1 FA/h is being tested at a much stricter operating point than a model evaluated at 0.5 FA/h. Therefore, the thesis should never juxtapose external numbers unless the metric, corpus, and operating point are all clearly aligned. citeturn23search0turn24search5turn24search6turn25search2turn29search18

For the present thesis, the safest final reporting structure is: **threshold-free exploratory curves on validation/dev**, then **frozen-threshold confirmatory tables** on held-out or realistically separated evidence. At each frozen threshold, report: long-form FA/h on negative streams, recall/FRR on real or unseen speakers, and separate hard-negative or confusable false-trigger results. This is more defensible than a single optimized headline number because recent literature and industry docs both emphasize threshold-dependent trade-offs and corpus dependence. citeturn16view1turn23search5turn25search13turn19view0

Your current instinct to separate **canonical/framework FA/h**, **offline benchmark FA/h**, and **field/device FA/h** is correct. In the public ESPHome/microWakeWord logic, detections depend on a sliding-window rule, VAD gating if enabled, and post-detection probability reset; Home Assistant’s deployment path can also stop the detector after a hit. That means a script with its own extra 2-second cooldown is **not** the same metric as the native framework logic unless the deployed system uses that exact behavior. citeturn31search0turn37search0turn37search1turn37search2

The weakest current evidence bucket is any claim based on **short false-alarm exposure**. If a corpus has zero false accepts over \(T\) hours, the classic “rule of three” gives an approximate 95% upper bound of \(3/T\). That means 3.65 hours with zero events supports only an upper bound of about **0.82 FA/h**, not a strong claim of “below 0.5 FA/h”; 5.5 hours with zero events supports only about **0.55 FA/h**. Stronger low-FA/h claims need more hours, ideally across more than one corpus and then corroborated by field logging. citeturn21search0turn21search12turn22search1

The external comparison story should therefore be conservative: **openWakeWord’s “<0.5 FA/h and <5% FRR” is a documentation target, not a peer-reviewed universal standard**; **microWakeWord public materials describe methodology and relative improvements, but not a stable peer-reviewed benchmark for “okay nabu” in text form**; **Picovoice/Porcupine publicly centers a stricter 1 false alarm per 10 hours benchmark**; and **Apple and Amazon describe multistage production systems whose public numbers are mostly relative or methodological, not directly comparable absolute FA/h for a single-stage MCU detector**. citeturn10view2turn23search7turn25search2turn25search1turn16view2turn16view3turn15search2

Possible Estonian thesis-ready wording: *“Äratussõna detektori põhimõõdikuks tuleb kasutada voogedastuslikku valede aktiveerumiste arvu tunni kohta (FA/h), mitte klipi-põhist valepositiivsete määra, sest need mõõdikud ei ole samaväärsed.”* Also: *“Väliste süsteemidega saab tulemusi võrrelda ainult siis, kui tööpunkt, testkorpus ja mõõtmismetoodika on võrreldavad; vastasel juhul on tegu üksnes ligikaudse suurusjärgu võrdlusega.”* citeturn19view0turn23search5turn16view1

## Definitions and metric conventions

**False accepts per hour** — often written FA/h, FAR/hour, or FAPH — should mean the number of **distinct unintended activations** divided by the exposure time in hours of negative audio. Official Apple writing explicitly says false accepts for a key-phrase trigger are typically measured on a **per-hour basis**, and the wake-word literature review notes that authors use inconsistent names for similar concepts, with “false alarm rate” sometimes reported per utterance and sometimes per hour of speech. The thesis should therefore define FA/h explicitly as an **event rate over hours of evaluated negative audio**, not as a clip percentage. citeturn16view1turn19view0

**False reject rate** is the proportion of true wake-word attempts that the model misses. **Recall** is the complementary quantity, \(1-\mathrm{FRR}\). Apple’s official terminology uses FR as the fraction of true “Hey Siri” instances that fail to wake the device, and recent wake-word papers plot FRR against FA/h in DET curves for exactly this reason: a threshold that reduces false alarms inevitably raises misses, and vice versa. citeturn16view1turn23search0turn15search2

A **DET curve** in this domain is best understood as a threshold sweep whose x-axis is false alarms per hour and whose y-axis is false reject rate per utterance. Recent wake-word papers explicitly use this convention, and Amazon’s wake-word work also reports FRR and FAR through DET curves while tuning decision thresholds. For a thesis, a DET-like plot is preferable to a single “accuracy” number because it makes the operating-point trade-off visible. citeturn23search0turn15search2

An **operating point** is the specific threshold or threshold set at which the detector runs. Apple’s “Personalized Hey Siri” article states plainly that the chosen thresholds affect FA, FR, and related errors; higher thresholds reduce false accepts at the cost of increased false rejects. Academic small-footprint KWS papers often operationalize this by fixing FA/h first and then reporting FRR at that point — for example 0.5 FA/h or 0.1 FA/h — rather than reporting threshold-free “best” numbers. citeturn16view1turn24search5turn23search0

**Streaming evaluation** means running the same kind of frame-by-frame detector logic used in deployment on a continuous audio stream. That contrasts with **clip-level evaluation**, where each clip is classified independently and clip boundaries implicitly reset state. The open-source and industry materials reviewed here all treat wake-word detection as a streaming problem: openWakeWord evaluates false accepts on hours of far-field mixed-content audio, and microWakeWord’s own documentation says it estimates FA/h by splitting long ambient clips to simulate streaming behavior. Clip-level false-positive rate is therefore a diagnostic quantity at best; it is not the same as FA/h. citeturn10view1turn13view0turn19view0

A **cooldown** or **refractory period** is the period after a detection during which new activations are suppressed or debounced so that one spoken event is not counted multiple times. In the public ESPHome/microWakeWord implementation, wake-word detection is based on a **mean probability over a sliding window**; VAD, when enabled, uses a sliding-window criterion as well; and after a detection the model probabilities are reset. Public docs clearly expose the sliding window and reset behavior, but they do **not** define a single user-facing standardized duration for a universal cooldown. Therefore, the thesis should report the exact runtime logic used in every metric: smoothing/window size, whether VAD gates detection, whether the detector stops after a hit, and any added offline cooldown. citeturn31search0turn37search0turn37search1turn37search2

**Latency** should be treated as a separate deployment property, not folded into FA/h or FRR. Google’s streaming KWS work is explicitly about latency/accuracy trade-offs, and ESPHome documentation says a smaller sliding-window size lowers latency but may increase false accepts. If end-to-end timing is not available for this thesis, it is acceptable to mention latency qualitatively and focus the confirmatory results on FA/h, FRR, and phrase-confusable robustness. citeturn18view0turn31search0

## External baseline table

The table below distinguishes between **measured numeric results**, **relative improvements only**, and **documentation targets**. “Comparable” here means *scientifically comparable to a small-footprint Estonian single-stage wake-word detector evaluated on your current corpora*. It does **not** mean “useful background.” 

| System / paper / source | Wake word(s) | Model / architecture | Test corpus / hours | Reported FA/h or FAPH | Reported FRR / recall | Operating point convention | Comparable? | Citation |
|---|---|---|---|---|---|---|---|---|
| openWakeWord documentation | “alexa”, “hey mycroft”, others | shared embedding backbone + small FC classifier | False accepts on ~5.5 h Dinner Party Corpus; positives depend on model doc | **Target**, not universal standard: aims for **<0.5 FA/h** | **Target**: aims for **<5% FRR** with threshold tuning | Threshold-tuned model-specific operation; default threshold 0.5 is only a starting point | **Partially** — useful as a target/methodology reference, not a direct baseline for Estonian or your corpora | citeturn10view2turn10view1turn8view0turn9view0 |
| microWakeWord / ESPHome docs | custom wake words; official model set includes “okay nabu” | streaming MixConv-style MCU model + sliding-window decision | ambient long-duration clips for training-time FA/h estimate; Home Assistant blog gives relative benchmark figure | Exact public text number for “okay nabu” **not found**; docs emphasize FA/h minimization and note the estimate is not a perfect real-world FA/h | Exact public text number for “okay nabu” **not found** in reviewed docs; Home Assistant blog says v2 performs about twice as well as v1, especially with VAD | Sliding-window mean vs cutoff; VAD optional; framework resets probabilities after detection | **Partially** — the methodology is highly relevant; public text-form external numeric baseline is limited | citeturn13view0turn31search0turn37search0turn37search1turn37search2turn23search7 |
| entity["company","Picovoice","voice ai company"] Porcupine benchmark docs / product page | benchmark averaged over six keywords | proprietary wake-word engine | benchmark with noise at 10 dB SNR and background speech; miss rate reported at **1 false alarm per 10 hours** | Benchmark convention: **0.1 FA/h** (1 per 10 h) | Benchmark repo reports **miss rate** at that point; product page advertises **97.1% accuracy** under those conditions | Fixed FAR benchmark; configurable sensitivity exposed separately | **Partially / not directly** — stricter operating point than 0.5 or 1.0 FA/h, different keywords and corpora, vendor benchmark | citeturn25search2turn29search18turn25search1 |
| entity["company","Apple","consumer electronics company"] Siri voice trigger articles | “Hey Siri”, “Siri” | multistage on-device detector + checker + speaker ID + directed-speech detection | production system; public sources describe architecture, not a thesis-style fixed corpus benchmark | FA is defined per hour, but open absolute production FA/h number **not found** in reviewed official sources | open absolute FRR number **not found** in reviewed official sources | Threshold-dependent multistage production system | **Not directly** — multistage commercial system with extra modules beyond a single-stage MCU wake word | citeturn16view1turn16view2turn16view0 |
| entity["company","Amazon","e commerce company"] two-stage Alexa papers | Alexa wake word | two-stage DNN acoustic model / classifier | real production-style internal data; absolute FAR anonymized in later paper | 2018 paper gives **relative** FAR reduction (about 37% at fixed miss, 67% for stage-2 classifier); 2020 data-efficient paper says absolute FAR values are anonymized | about **16% relative FRR reduction** at fixed FA level in the 2018 paper | DET / fixed-FA vs fixed-miss comparisons; no public absolute production operating point | **Not directly** — informative for architecture and reporting conventions, not an absolute baseline | citeturn16view3turn15search2 |
| entity["organization","Mozilla","web software organization"] Howl | deployed Firefox Voice wake word | open-source wake-word toolkit | Common Voice-derived wake-word data; paper reports “per hour of speech” | Paper summary reports about **4 FA/h of speech** in deployed setting; figure commentary also discusses ~5 FA/h of speech depending on threshold | Paper summary reports about **10% FRR** in deployed setting | Threshold sweep / ROC-style reporting; per hour of **speech**, not wall-clock device hours | **Partially / not directly** — open-source numeric reference, but different corpus and a speech-only FA/h convention | citeturn26search3turn26search2 |
| entity["company","Google","internet technology company"] TDNN small-footprint KWS paper | in-house wake word task | TDNN vs CNN baseline | in-house dataset, clean and 10 dB noisy conditions | Fixed at **0.5 FA/h** | TDNN: **3.1% FRR clean**, **5.8% FRR noisy**; baseline CNN much worse | FRR reported at fixed FA/h | **Partially** — academically useful convention, but different data and likely different wake-word difficulty | citeturn24search5 |
| HEiMDaL | unnamed wake word task | low-footprint CNN with alignment-based loss | Apple research summary; full absolute benchmark not in open summary | Absolute open numeric FA/h **not found** in reviewed summary | Relative statement only: **73% reduction in detection metrics** at same memory footprint | Relative DET improvement vs end-to-end DNN-HMM baseline | **Not directly** — useful architectural context, not an absolute baseline | citeturn28view0 |
| Ribeiro et al. alignment paper | wake-word detection training variants | alignment-based / alignment-free / hybrid | internal datasets with multiple data splits | Fixed at **0.1 FA/h** | FRR values reported at 0.1 FA/h, with several models around **5–7% FRR** depending on split | Explicit DET framing with x-axis FA/h, y-axis FRR | **Methodologically comparable**, but not an external product baseline | citeturn23search0turn23search4 |

Two takeaways from this table matter most. First, **external sources do not converge on one operating point**: 0.1 FA/h, 0.5 FA/h, 1.0 FA/h, and 1 false alarm per 10 hours all appear in the literature and documentation. Second, several widely cited production systems either publish only **relative improvements** or omit absolute FA/h numbers entirely. That makes method alignment more important than marketing-style number comparison. citeturn23search0turn24search5turn25search2turn16view3turn15search2

## Fair-comparison decision guide for this thesis

A comparison is **fair** when all of the following are aligned: the metric definition, the operating point, the detector logic, and the corpus type. For wake-word work, that means comparing **FRR at a fixed FA/h**, or comparing **FA/h at a clearly fixed threshold that was frozen on validation**, on corpora with comparable content. Matching only the threshold number is not enough, because a threshold has meaning only inside a specific model and post-processing pipeline. citeturn16view1turn23search5turn19view0

It is **not fair** to write: “our model has X FAPH at threshold 0.995 on 3.65 h Estonian Common Voice, while openWakeWord targets <0.5 FA/h and <5% FRR.” The correct critique is that openWakeWord’s number is a **documentation target under its own evaluation procedure**, with false accepts measured on roughly 5.5 hours of Dinner Party Corpus far-field audio and positives defined per model. Your measurement is on a different language, different corpus, different threshold, and likely different trigger logic. That comparison can only be presented as **same-order-of-magnitude context**, not as a head-to-head result. citeturn10view1turn10view2turn8view0turn9view0

A fairer wording would be: *“The observed offline FA/h is of the same order of magnitude as public documentation targets reported for openWakeWord, but the numbers are not directly comparable because the language, corpus, and operating point differ.”* That sentence is cautious and defensible because it avoids implying equivalence of methodology. citeturn10view2turn19view0

For the thesis tables, the best practice is to report **all three views**, but with clear labels. The primary confirmatory table should be **frozen-threshold results**. A second figure can show the **DET or FRR-versus-FA/h curve** from validation/dev to show the trade-off. If you have enough held-out data, you may also include a secondary table such as **FRR at dev-selected 0.5 FA/h and 1.0 FA/h operating points**. What you should avoid is selecting the threshold on the same test set and then presenting the best point as final. If you show such a sweep, label it exploratory. citeturn23search5turn25search13turn16view1

A good wording template for threshold sweeps is: *“Threshold sweeps on the held-out set are shown for diagnostic transparency only. Because these thresholds were explored on the same data, they should not be interpreted as confirmatory estimates of deployable performance.”* That is consistent with the general warning against cherry-picked wake-word benchmarks and with the threshold-dependent nature of FA/FR trade-offs. citeturn23search5turn25search13

Your Android logger evidence at runtime threshold 0.90 should be treated as **separate field evidence**, not directly compared to offline 0.995 measurements. The threshold is different, the runtime path is different, and the environment is different. The fair wording is: *“The Android logging run provides field evidence under a distinct runtime operating point and should not be numerically compared with offline benchmark FA/h measured at a different threshold.”* This follows directly from the literature’s insistence that operating point and corpus type affect FA/h materially. citeturn16view1turn19view0

Comparisons to entity["organization","Open Home Foundation","home automation nonprofit"] microWakeWord or entity["organization","Home Assistant","home automation platform"] “okay nabu” should also be qualified carefully. The microWakeWord and ESPHome materials are highly relevant to **method and deployment logic**, but the public text reviewed here does not provide a stable peer-reviewed, text-form, apples-to-apples external benchmark number for “okay nabu” comparable to your Estonian model. The correct wording is: *“microWakeWord is an implementation and methodology baseline for constrained-device streaming wake-word detection, but its public numeric comparisons for the shipped English models are limited in the reviewed text sources.”* citeturn13view0turn31search0turn23search7

Comparisons to entity["company","Apple","consumer electronics company"] and entity["company","Amazon","e commerce company"] should be **architectural only**, not numeric headline comparisons. Both official sources describe multistage systems that use additional filtering beyond a simple single-stage wake-word detector, and Amazon explicitly anonymizes absolute FAR in one later paper. The defensible sentence is: *“Industrial production systems typically use multistage trigger pipelines and therefore are not directly comparable to a single-stage MCU wake-word detector.”* citeturn16view2turn16view3turn15search2

## Recommended final thesis reporting protocol

The thesis should contain **one threshold-free figure** and **three frozen-threshold tables**. The threshold-free figure should be a DET-like plot or an FRR-versus-FA/h curve produced on **validation/dev only**. If you do not have enough independent development hours, you can still show a test-set sweep, but it must be labeled exploratory rather than final. The purpose of that figure is to reveal the trade-off shape and to show whether a model is dominated by another across plausible operating points. citeturn23search0turn15search2turn23search5

The first frozen-threshold table should be the main **offline benchmark table**. It should include one or at most two named operating points, frozen beforehand — for example, “OP-A: nearest dev threshold to 1.0 FA/h on the primary validation long-form negative corpus” and optionally “OP-B: nearest dev threshold to 0.5 FA/h.” For each operating point, report results on **each corpus separately**: `faph_cv_et`, `faph_librispeech`, `faph_dipco`, and any additional field-like background set. Do **not** average them blindly into a single FA/h number, because the reviewed literature explicitly warns that FA/h depends on how much speech and what kinds of sounds are in the stream. If you do also report a pooled number, it should be secondary and accompanied by total hours. citeturn19view0turn10view1turn13view0

The second frozen-threshold table should be the **positive recall table**. At the same operating point(s), report recall/FRR separately for `pos_isa_xtts`, `pos_ode_real`, `pos_friend1_real`, and the final user-study replay set. Each row should show the sample count \(N\), hits, misses, recall, FRR, and a confidence interval. In the thesis narrative, explicitly classify `pos_ode_real` and very small early sets as **diagnostic** rather than decisive. The 20–30 participant frozen-threshold replay should be the main human-facing evidence for claims about real-speaker usability. citeturn16view1turn23search5

The third frozen-threshold table should be the **hard-negative and confusable table**. This should not be forced into FA/h unless the challenge set was evaluated as one concatenated stream with native streaming logic. For phrase-specific challenge sets such as prefix-only, single `kratt`, reversed order, and `kuule <not kratt>` confusables, the cleanest measure is **utterance-level false-trigger count / rate on the challenge set** at the same frozen threshold. In other words, treat these as discrete adversarial diagnostics and report them separately from long-form ambient FA/h. That separation is well motivated by literature on confusing words, which shows that confusable or phonetically similar phrases can degrade wake-word systems badly and deserve dedicated treatment. citeturn30search0turn30search6

For the **counting rule**, define one false accept as one distinct activation event emitted by the detector’s runtime logic. Repeated frame-level threshold crossings within the same activation should not count as multiple false accepts. In the public ESPHome/microWakeWord implementation, wake-word detection uses a sliding-window mean rule and resets model probabilities after a hit; therefore, the most reproducible offline metric is to re-run the same native trigger logic on continuous audio and count emitted detection events. If older scripts additionally apply a 2-second cooldown, report those as a **different metric variant**, not as the canonical framework FA/h. citeturn37search1turn37search2turn31search0

The thesis should name these variants explicitly:

- **Framework-native offline FA/h**: same wake-word/VAD logic as the deployed ESPHome/microWakeWord path, with the actual sliding window, cutoff, and any native post-hit reset behavior.
- **Scripted offline FA/h**: any offline replay path that adds extra smoothing or a manual cooldown not guaranteed to match deployment.
- **Field FA/h**: Android or device logger evidence under the actual runtime threshold, device microphone, and ambient conditions.
- **User-study replay results**: frozen-threshold offline re-analysis of labeled participant sessions, separated from naturally occurring field logs.

That naming scheme is stronger than trying to force everything into a single “FAPH” number, because it prevents accidental mixing of incompatible counting rules. citeturn19view0turn31search0turn37search1turn37search2

Statistical uncertainty should be explicit. For FA/h, report the event count \(k\), exposure hours \(T\), the point estimate \(k/T\), and a **Poisson rate confidence interval**. When \(k=0\), give at minimum the approximate 95% upper bound \(3/T\) and state it in text. For recall/FRR, report a binomial confidence interval with the denominator shown. These intervals matter especially in a low-resource thesis because the difference between “0 events observed” and “system proven safe” is exactly the point the statistical literature warns about. citeturn21search0turn21search12turn22search1

A practical final package for this thesis would therefore be:

- one validation DET or FRR-vs-FA/h figure,
- one frozen-threshold offline corpus table,
- one frozen-threshold positive recall table,
- one frozen-threshold hard-negative/confusable table,
- one short field-evidence table for Android/device logging,
- one concise narrative section explaining which sets are **final**, **dev**, **diagnostic**, or **exploratory**.

That is enough for a strong BSc thesis and does not require a huge new experiment. citeturn23search5turn19view0

## Gaps or corrections to current project assumptions

The strongest correction is about **how much negative audio is needed**. A common but misleading inference is that “zero false accepts on a few hours means sub-1 FA/h.” The rule-of-three says the approximate 95% upper bound after zero events is \(3/T\). On **3.65 h**, that is about **0.82 FA/h**; on **5.5 h**, about **0.55 FA/h**; on **98.97 h**, about **0.03 FA/h**. So 3.65 hours is enough to support only a **weak** sub-1/h statement if and only if zero events were observed, and even then only for that exact evaluation condition. It is **not** enough for a strong “below 0.5/h” claim. citeturn21search0turn21search12turn22search1

That means the phrase **“sub-1 FAPH”** needs very careful wording. It is acceptable as a **point estimate** on a specific short corpus, for example “0 events over 3.65 h” or “1 event over 5.6 h,” but it should not be presented as a stable system property without exposure hours and interval estimates. The safer wording is: *“The observed false-accept rate on this corpus was below 1 FA/h, but the confidence bounds are wide because the exposure duration is limited.”* citeturn21search0turn22search1

The phrase **“0.5 FA/h annoyance threshold”** should also be softened. In the reviewed material, the clearest explicit statement is in the openWakeWord README, which itself says that the threshold is **subjective** and “often reasonable in practice.” That is useful documentation, but it is **not** a peer-reviewed universal standard. Some recent academic work instead points to user satisfaction around **0.1 FA/h with about 5% FRR**, which is a stricter operating point. Therefore, the thesis should present 0.5 FA/h as a **practical reference point used in parts of the literature and tooling**, not as settled scientific consensus. citeturn10view2turn23search0

Your intuition about public baselines is also correct: **microWakeWord and openWakeWord targets are mainly documentation claims, not peer-reviewed benchmark standards.** That does not make them unusable; it just changes how they should be cited. In the thesis, cite them as *implementation documentation* or *project documentation*, not as if they were peer-reviewed canonical baselines. citeturn10view2turn13view0turn31search0

Similarly, production claims from entity["company","Apple","consumer electronics company"] or entity["company","Amazon","e commerce company"] should not be used as “the baseline” for a single-stage Estonian MCU detector. Apple’s current official system is explicitly multistage and includes checker, speaker identification, and directed-speech detection. Amazon’s public technical material includes strong relative improvements, but one later paper anonymizes absolute FAR. Those are invaluable references for architecture and evaluation culture, but they are not numerically comparable to a microcontroller binary trigger trained for a new language. citeturn16view2turn16view3turn15search2

Another important correction is that **far-field dinner-party English** and **speech-corpus Estonian negatives** are not interchangeable. The systematic review directly warns that FA/h can differ drastically depending on whether the denominator is speech-only recordings or real device time where speech occupies only part of the day. This means Common Voice Estonian, LibriSpeech, DiPCo, MacBook background, and Android field logging should be treated as **different stress tests**, not pooled as though they all estimate the same deployment quantity. citeturn19view0

The reviewed literature also strongly supports your concern that **ambient FA/h alone is not enough**. Apple’s 2023 voice trigger article explicitly lists rejection of phonetically similar trigger phrases as a core challenge, and confusion-word papers show that words sounding similar to the wake phrase can cause severe degradation unless they are modeled directly. So your plan to keep prefix-only, reversed-order, single-word, and `kuule/kule <not kratt>` challenge sets as first-class diagnostics is scientifically well motivated. citeturn16view2turn30search0turn30search6

### Open questions and limitations

A few issues remain genuinely unresolved in the public record. First, I did **not** find a peer-reviewed public text source giving a clean, stable numeric external benchmark for the shipped English “okay nabu” model; the reviewed public materials emphasize methodology and relative improvement more than a canonical text-form FA/h/FRR pair. Second, official public materials for entity["company","Picovoice","voice ai company"] Porcupine mix benchmark miss-rate framing with product-page “accuracy” language, so the safest thesis use is to cite the **benchmark operating point** rather than over-translate the vendor number into FRR. Third, I did not identify a public official source that pins Apple’s or Amazon’s current consumer wake-word systems to a simple single-stage absolute FA/h headline number that would be appropriate for direct comparison. Those absences should be stated directly in the thesis rather than filled in by inference. citeturn23search7turn25search2turn25search1turn16view2turn15search2

## BibTeX

```bibtex
@online{apple_hey_siri_2017,
  title        = {Hey Siri: An On-device DNN-powered Voice Trigger for Apple's Personal Assistant},
  author       = {{Siri Team}},
  year         = {2017},
  organization = {Apple Machine Learning Research},
  url          = {https://machinelearning.apple.com/research/hey-siri},
  note         = {Accessed 2026-05-03}
}

@online{apple_personalized_hey_siri_2018,
  title        = {Personalized Hey Siri},
  author       = {{Apple Machine Learning Research}},
  year         = {2018},
  organization = {Apple},
  url          = {https://machinelearning.apple.com/research/personalized-hey-siri},
  note         = {Accessed 2026-05-03}
}

@online{apple_voice_trigger_2023,
  title        = {Voice Trigger System for Siri},
  author       = {{Apple Machine Learning Research}},
  year         = {2023},
  organization = {Apple},
  url          = {https://machinelearning.apple.com/research/voice-trigger},
  note         = {Accessed 2026-05-03}
}

@inproceedings{wu2018monophone,
  title        = {Monophone-based Background Modeling for Two-stage On-device Wake Word Detection},
  author       = {Wu, Minhua and Panchapagesan, Sankaran and Sun, Ming and Gu, Jiacheng and Thomas, Ian and Vitaladevuni, Shiv Naga Prasad and Hoffmeister, Bj{\"o}rn and Mandal, Arindam},
  booktitle    = {ICASSP 2018},
  year         = {2018},
  url          = {https://www.amazon.science/publications/monophone-based-background-modeling-for-two-stage-on-device-wake-word-detection}
}

@article{gao2020dataefficient,
  title        = {Towards Data-efficient Modeling for Wake Word Spotting},
  author       = {Gao, Yixin and Mishchenko, Yuriy and Shah, Anish and Matsoukas, Spyros and Vitaladevuni, Shiv},
  journal      = {arXiv preprint arXiv:2010.06659},
  year         = {2020},
  url          = {https://assets.amazon.science/7c/b2/5e3e6a164920bfc167fb5586d3f2/scipub-1260.pdf}
}

@inproceedings{rybakov2020streaming,
  title        = {Streaming Keyword Spotting on Mobile Devices},
  author       = {Rybakov, Oleg and Kononenko, Natasha and Subrahmanya, Niranjan and Visontai, Mirko and Laurenzo, Stella},
  booktitle    = {Interspeech 2020},
  year         = {2020},
  doi          = {10.21437/Interspeech.2020-1003},
  url          = {https://arxiv.org/abs/2005.06720}
}

@inproceedings{myer2018tdnn,
  title        = {Efficient Keyword Spotting Using Time Delay Neural Networks},
  author       = {Myer, Stephen and Tomar, Vikas Singh},
  booktitle    = {Interspeech 2018},
  year         = {2018},
  url          = {https://www.isca-archive.org/interspeech_2018/myer18_interspeech.pdf}
}

@inproceedings{ribeiro2023alignment,
  title        = {Handling the Alignment for Wake Word Detection: A Comparison Between Alignment-Based, Alignment-Free and Hybrid Approaches},
  author       = {Ribeiro, Vitor and others},
  booktitle    = {Interspeech 2023},
  year         = {2023},
  url          = {https://www.isca-archive.org/interspeech_2023/ribeiro23_interspeech.pdf}
}

@article{kolesau2020review,
  title        = {Voice Activation Systems for Embedded Devices: Systematic Literature Review},
  author       = {Kolesau, Aliaksei and {\v{S}}e{\v{s}}ok, Dmitrij},
  journal      = {Informatica},
  volume       = {31},
  number       = {1},
  pages        = {65--88},
  year         = {2020},
  url          = {https://informatica.vu.lt/journal/INFORMATICA/article/1153/text}
}

@inproceedings{tang2020howl,
  title        = {Howl: A Deployed, Open-Source Wake Word Detection System},
  author       = {Tang, Raphael and Lee, Jaejun and Razi, Afsaneh and Cambre, Julia and Bicking, Ian and Kaye, Jofish and Lin, Jimmy},
  booktitle    = {NLP-OSS 2020},
  year         = {2020},
  url          = {https://aclanthology.org/2020.nlposs-1.9/}
}

@article{jia2020confusionwords,
  title        = {Training Wake Word Detection with Synthesized Speech Data on Confusion Words},
  author       = {Jia, Yan and Cai, Zexin and Ma, Murong and Zhao, Zeqing and Wang, Xuyang and Wang, Junjie and Li, Ming},
  journal      = {arXiv preprint arXiv:2011.01460},
  year         = {2020},
  url          = {https://arxiv.org/abs/2011.01460}
}

@article{wang2022adversarialconfusing,
  title        = {Generating Adversarial Samples for Training Wake-up Word Detection Systems Against Confusing Words},
  author       = {Wang, Haoxu and Jia, Yan and Zhao, Zeqing and Wang, Xuyang and Wang, Junjie and Li, Ming},
  journal      = {arXiv preprint arXiv:2201.00167},
  year         = {2022},
  url          = {https://arxiv.org/abs/2201.00167}
}

@inproceedings{kundu2023heimdal,
  title        = {HEiMDaL: Highly Efficient Method for Detection and Localization of Wake-words},
  author       = {Kundu, Arnav and Razlighi, Mohammad Samragh and Cho, Minsik and Padmanabhan, Priyanka and Naik, Devang},
  booktitle    = {ICASSP 2023},
  year         = {2023},
  url          = {https://machinelearning.apple.com/research/heimdal}
}

@online{openwakeword_readme_2026,
  title        = {openWakeWord GitHub README and Performance Documentation},
  author       = {{dscripka/openWakeWord contributors}},
  year         = {2026},
  organization = {GitHub},
  url          = {https://github.com/dscripka/openWakeWord},
  note         = {Documentation; accessed 2026-05-03}
}

@online{openwakeword_alexa_doc_2026,
  title        = {openWakeWord Alexa Model Documentation},
  author       = {{dscripka/openWakeWord contributors}},
  year         = {2026},
  organization = {GitHub},
  url          = {https://github.com/dscripka/openWakeWord/blob/main/docs/models/alexa.md},
  note         = {Documentation; accessed 2026-05-03}
}

@online{openwakeword_hey_mycroft_doc_2026,
  title        = {openWakeWord Hey Mycroft Model Documentation},
  author       = {{dscripka/openWakeWord contributors}},
  year         = {2026},
  organization = {GitHub},
  url          = {https://github.com/dscripka/openWakeWord/blob/main/docs/models/hey_mycroft.md},
  note         = {Documentation; accessed 2026-05-03}
}

@online{microWakeWord_github_2026,
  title        = {microWakeWord GitHub README},
  author       = {{OHF-Voice/micro-wake-word contributors}},
  year         = {2026},
  organization = {GitHub},
  url          = {https://github.com/OHF-Voice/micro-wake-word},
  note         = {Documentation; accessed 2026-05-03}
}

@online{esphome_micro_wake_word_docs_2026,
  title        = {ESPHome Micro Wake Word Component Documentation},
  author       = {{ESPHome contributors}},
  year         = {2026},
  organization = {ESPHome},
  url          = {https://esphome.io/components/micro_wake_word/},
  note         = {Documentation; accessed 2026-05-03}
}

@online{esphome_mww_cpp_api_2026,
  title        = {ESPHome API Docs: micro\_wake\_word.cpp},
  author       = {{ESPHome contributors}},
  year         = {2026},
  organization = {ESPHome},
  url          = {https://api-docs.esphome.io/micro__wake__word_8cpp_source},
  note         = {API documentation; accessed 2026-05-03}
}

@online{esphome_wakewordmodel_api_2026,
  title        = {ESPHome API Docs: WakeWordModel Class Reference},
  author       = {{ESPHome contributors}},
  year         = {2026},
  organization = {ESPHome},
  url          = {https://api-docs.esphome.io/classesphome_1_1micro__wake__word_1_1_wake_word_model},
  note         = {API documentation; accessed 2026-05-03}
}

@online{esphome_vadmodel_api_2026,
  title        = {ESPHome API Docs: VADModel Class Reference},
  author       = {{ESPHome contributors}},
  year         = {2026},
  organization = {ESPHome},
  url          = {https://api-docs.esphome.io/classesphome_1_1micro__wake__word_1_1_v_a_d_model},
  note         = {API documentation; accessed 2026-05-03}
}

@online{homeassistant_voice_chapter7_2024,
  title        = {Voice Chapter 7: Supercharged Wake Words and Timers},
  author       = {{Home Assistant}},
  year         = {2024},
  organization = {Home Assistant},
  url          = {https://www.home-assistant.io/blog/2024/06/26/voice-chapter-7/},
  note         = {Engineering blog / documentation; accessed 2026-05-03}
}

@online{picovoice_wake_word_benchmark_repo_2026,
  title        = {Picovoice Wake Word Benchmark Repository},
  author       = {{Picovoice}},
  year         = {2026},
  organization = {GitHub},
  url          = {https://github.com/Picovoice/wake-word-benchmark},
  note         = {Benchmark documentation; accessed 2026-05-03}
}

@online{picovoice_wake_word_benchmark_docs_2026,
  title        = {Wake Word Detection Engine Benchmark},
  author       = {{Picovoice}},
  year         = {2026},
  organization = {Picovoice},
  url          = {https://picovoice.ai/docs/benchmark/wake-word/},
  note         = {Benchmark documentation; accessed 2026-05-03}
}

@online{picovoice_porcupine_product_2026,
  title        = {Porcupine Wake Word: On-Device Keyword Spotting},
  author       = {{Picovoice}},
  year         = {2026},
  organization = {Picovoice},
  url          = {https://picovoice.ai/products/voice/wake-word/},
  note         = {Product documentation; accessed 2026-05-03}
}

@online{picovoice_benchmarking_blog_2022,
  title        = {Benchmarking a Wake Word Detection Engine},
  author       = {{Picovoice}},
  year         = {2022},
  organization = {Picovoice},
  url          = {https://picovoice.ai/blog/benchmarking-a-wake-word-detection-engine/},
  note         = {Technical blog; accessed 2026-05-03}
}

@online{picovoice_benchmarks_blog_2025,
  title        = {Wake Word Benchmarks: How to Verify Vendor Claims},
  author       = {{Picovoice}},
  year         = {2025},
  organization = {Picovoice},
  url          = {https://picovoice.ai/blog/wake-word-benchmarks/},
  note         = {Technical blog; accessed 2026-05-03}
}

@article{hanley1983ruleofthree,
  title        = {If Nothing Goes Wrong, Is Everything All Right? Interpreting Zero Numerators},
  author       = {Hanley, James A. and Lippman-Hand, Andre},
  journal      = {JAMA},
  year         = {1983},
  url          = {https://jhanley.biostat.mcgill.ca/Reprints/If_Nothing_Goes_1983.pdf}
}

@article{ulm1990poisson,
  title        = {A Simple Method to Calculate the Confidence Interval of a Standardized Mortality Ratio},
  author       = {Ulm, Kurt},
  journal      = {American Journal of Epidemiology},
  volume       = {131},
  number       = {2},
  pages        = {373--375},
  year         = {1990},
  url          = {https://academic.oup.com/aje/article-abstract/131/2/373/138128}
}
```