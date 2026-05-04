# Kratt: Decision-Oriented Research Report on Two-Stage Wake-Word Verification for an Estonian Local Voice Satellite

## Bottom line

The literature strongly supports the **general architecture** you are considering: a low-power always-on first-pass wake detector, followed by a heavier second-pass verifier that is invoked only on candidate triggers. That pattern appears in official write-ups from entity["company","Apple","consumer electronics company"], entity["company","Google","search and cloud company"], and entity["company","Amazon","ecommerce and cloud company"], and it also appears in newer academic KWS systems that use rescoring, force alignment, CTC, or full ASR to reduce false wakes while preserving first-pass efficiency. In other words, the *cascaded* idea is not speculative; it is mainstream. citeturn30view0turn30view1turn23view0turn29view4turn33view0turn28view3turn14view1turn14view0

For **Kratt specifically**, a **local Kiirkirjutaja ASR verifier on Raspberry Pi after microWakeWord on ESP32-S3 is defensible as a thesis future-work path and as a small diagnostic experiment now**. The reason is narrow but important: your current failure mode is not “ambient noise only,” but **exact-phrase selectivity** under prefix-only, reversed-order, and confusable phrases. A second stage that explicitly checks ordered evidence for `kuule/kule ... kratt` is conceptually much better matched to that failure mode than a single binary embedded KWS score. Official industry systems make essentially the same move: Apple uses a high-precision checker and later false-trigger mitigation using full-utterance acoustic and ASR-lattice evidence; Google reported a secondary ASR-based KWS pass that cut false accepts by 89% with only a 0.2% false-reject increase in its client-server setting; Amazon reports large FAR reductions from second-stage verification as well. citeturn31view1turn31view2turn33view0turn28view3turn10view0turn10view2

The skeptical conclusion is equally important: **the literature does not justify claiming that a local Estonian ASR verifier will solve Kratt today**. Your own probe already points to the central risk: strict transcript matching appears able to suppress many confusables, but it also badly hurts recall, especially on short or command-appended clips. Amazon’s verifier literature explicitly warns that ASR-based verification is tied to ASR quality and can miss wakewords when the recognizer simply does not hypothesize them; Apple likewise says it does **not** rely on the one-best ASR transcript for false-trigger mitigation because that transcript can hallucinate the trigger phrase. So the right thesis recommendation is: **run a small cascade diagnostic now; do not promote the ASR verifier to the core contribution unless it survives real-speaker testing with only modest recall loss**. citeturn10view0turn10view2turn31view2

My decision-oriented recommendation is therefore:

**Run the small experiment now. Frame the ASR verifier as future work unless it clears a strict gate.** For this project, “clear” should mean something like: large reduction in prefix/confusable false accepts, little to no degradation on unseen real-speaker recall, and tolerable added latency on the Raspberry Pi path. If it does not clear that gate, it is still academically valuable as evidence that **binary embedded KWS alone struggles with exact two-word phrase selectivity** and that **a local second stage is plausible but not yet mature**. That is a strong and conservative thesis position. citeturn30view0turn33view0turn28view3turn14view1turn14view0

## Literature and prior art

Apple’s current public description of Siri voice triggering is unusually relevant to Kratt because it names almost the same failure class you found. Apple describes a **multistage architecture** with a streaming high-recall detector on the always-on processor, a **high-precision checker** on the application processor, optional speaker identification, and an additional **false-trigger mitigation** system that analyzes the whole utterance after the initial trigger. Apple explicitly says one of its core challenges is “identifying and rejecting acoustic segments that are phonetically similar to trigger phrases,” and it further notes that monophone/CTC acoustic-model objectives do not fully match the real goal, which is to discriminate true triggers from phonetically similar negatives. That is very close to your prefix/confusable finding. Apple’s later mitigation stack even uses **ASR lattices** and says it does **not** rely on the one-best ASR hypothesis because ASR can hallucinate the trigger phrase; instead it uses whole-lattice uncertainty and device-directed-speech evidence. For Kratt, that is the clearest industry precedent for saying “a second stage is reasonable, but a naïve transcript string match is not the gold standard.” citeturn30view0turn30view1turn30view2turn31view1turn31view2

Google provides two complementary precedents. First, its 2017 mobile cascade paper describes a **DSP first stage** plus **AP second stage** because running a higher-quality model continuously on the main application processor would violate mobile power constraints. The first stage is deliberately small and lenient; the second stage is larger and more accurate; an optional third server-side validation stage may reduce false accepts further. The paper also makes two points that map well to Kratt: the first-stage model should not be judged alone, and the decoder enforces that keyword subunits fire in the **specified order**. Second, in the same year Google published a directly relevant paper on **“Keyword Spotting for Google Assistant Using Contextual Speech Recognition.”** There, an on-device KWS system sent trigger-plus-query audio to a server-side contextual ASR system; if the ASR result did not contain the trigger phrase, the query was suppressed. Google reported an **89% reduction in false accepts with only a 0.2% increase in false rejects**, while also improving downstream ASR WER by using the trigger phrase context. Architecturally, that is the closest primary-source analogue to your proposed “ESP32 trigger, Pi ASR verify” idea, even though Google’s deployment was cloud/server rather than a local Raspberry Pi. citeturn23view0turn29view2turn29view4turn33view0

Amazon’s public research strengthens the case for cascades but also sharpens the warning about ASR. In its 2018 paper on **monophone-based background modeling for two-stage on-device wake word detection**, Amazon reports about **16% relative FRR reduction at fixed false alarm level**, about **37% relative FAR reduction at fixed miss rate**, and a second-stage classifier that reduced FAR by about **67% relative** over first-stage hypotheses with very limited extra computation. In other words, second-pass verification was not marginal; it materially improved the operating point. But Amazon’s later paper **“Building a Robust Word-Level Wakeword Verification Network”** says a secondary verifier is “often utilized,” then argues that ASR-based verification has important drawbacks: higher model complexity, need for large-vocabulary training data, and performance tightly coupled to end-to-end ASR WER. In its comparisons, ASR-based verification was often worse than word-level wakeword models except in a noisy-alignment corner case. Amazon’s 2024 “hot-fixing” paper also states that assistants often use the **ASR hypothesis to validate detections from on-device wake word models**, but its own contribution is to repair wakeword recognition inside a streaming ASR system, again showing that once you rely on ASR, wakeword quality becomes an ASR problem. citeturn28view3turn10view0turn10view1turn10view2turn11view1turn11view2

Open-source systems say something similar, but in a more practical and less polished way. The entity["organization","Open Home Foundation","open-source home automation org"] tooling stack explicitly supports **multiple microWakeWord models** and **VAD** in ESPHome, which means consensus and gated detection are already normal ideas in that ecosystem. The microWakeWord project itself describes a two-stage detection process inside the detector—streaming probabilities over windows rather than a single frame decision—and ESPHome exposes multiple models, enabling/disabling, and VAD gating on-device. openWakeWord goes further and documents a **custom verifier model** attached on top of a base wakeword model. However, its documented verifier is mainly for **speaker filtering**, not for exact phrase-order verification, so it is not a direct solution to your “kuule vs kuule kratt” problem. A more relevant open-source precedent is openSpeechToIntent, which explicitly presents a **sensitive wake detector plus a stronger second-stage matcher** as a way to suppress false activations; in its documented English example, a very permissive wake threshold produced about **3.58 false activations per hour**, while a second-stage intent matcher cut that to **<0.04/h**. That does not prove your Estonian wake verifier will work, but it does show that the open-source world independently arrived at the same basic cascade logic. citeturn19view1turn19view2turn19view3turn19view0turn8view6turn20view0

The academic KWS literature also gives you more exact phrase-order options than “binary classifier plus transcript string match.” **CaTT-KWS** uses a transducer detector, then a **force-alignment** verification stage, then a **transformer** verification stage; in one reported setup, false alarms fell from **1.47/h to 0.13/h** with little accuracy decay. **U2-KWS** uses a two-pass model where a streaming CTC branch proposes keyword candidates and a second-pass decoder rescors those candidates by predicting the **keyword sequence token by token**; the architecture is explicitly order-aware and only activates the heavy second pass after a first-pass candidate. Older **LSTM-CTC** work argues that arbitrary keywords can be detected without keyword-specific retraining, and classic **keyword/filler** and **phoneme-recognition/lattice** pipelines make exactly the tradeoff that matters for Kratt: they enforce a phoneme/word sequence more explicitly, but they are usually more engineering-heavy or computationally costly than a tiny binary KWS model. citeturn14view1turn16view4turn14view0turn16view0turn16view1turn14view3turn17view0turn17view1

One more literature lesson matters for your thesis framing: **a verifier is not the only way to attack the problem**. Google’s 2024 TTS-data paper shows that KWS quality remains strongly dependent on training data diversity; even large TTS corpora could not fully replace real positive and negative data, and speaker diversity mattered a great deal. The confusing-word augmentation literature likewise shows that KWS systems can fail specifically on phrases that sound like the keyword or are only parts of it, and that targeted confusing-word data can materially improve robustness. For Kratt, that means the verifier is defensible, but the thesis should not imply it is the only serious path. A data-centric route—better positives, better hard negatives, better confusable synthesis, and maybe a sequence-aware second-stage model later—remains equally defensible. citeturn21view0turn15view2

## Architectural options for Kratt

**ESP32 first-stage KWS plus Raspberry Pi ASR verifier** is the best **diagnostic** fit for the thesis as it exists now. It maps cleanly onto Google’s contextual-ASR second pass and Apple’s “whole-utterance” mitigation logic, except that you can keep it local for privacy. Its biggest advantage is that it can check **word order**, so it can in principle reject `kuule`-only, `kratt kuule`, and `kuule <not kratt>` confusables that a binary first-stage score struggles with. Its biggest risk is that it inherits ASR weaknesses: if the ASR misses `kratt`, mishears it as `kurat` or `Grete`, or fails on short appended commands, final recall drops immediately. So this option is strong as a **small experiment** and plausible as future work, but not yet strong enough to be claimed as the thesis’ solved engineering answer. citeturn33view0turn31view1turn31view2turn10view0turn10view2

**ESP32 first-stage KWS plus a small phoneme or keyword verifier** is probably the best **long-term technical fit**, even if it is not the quickest thesis add-on. Literature from keyword/filler systems, force-alignment systems, CaTT-KWS, U2-KWS, and Apple’s phrase-specific discriminative checker all point in the same direction: when the real problem is exact phrase sequence, a model or decoder that represents the phrase structure explicitly is often better matched than a binary “wake vs not wake” classifier or a generic ASR transcript. That path would likely let you encode `kuule/kule` as allowed first-word variants while still requiring a `kratt`-like second token in the right order. The price is more modeling and data work than the quick ASR-rule prototype. citeturn17view0turn17view1turn14view1turn14view0turn30view1turn30view2

**microWakeWord consensus or multi-model verification** is easy to test and fits your current stack, but it is the least convincing option if the first-stage models already share the same blind spot. ESPHome now supports multiple models per device plus VAD, and the OHF release notes explicitly say multiple models can run concurrently on ESP32-class hardware. That makes ensemble-style gating operationally feasible. The problem is epistemic: if v16c, expert-a, and related models were trained on similar positives and negatives, they may all still fire on the same prefix and confusable patterns. openWakeWord’s documented verifier support is also mostly speaker-focused rather than phrase-order-focused. So consensus is a useful engineering baseline, not a strong literature-backed answer to your exact phrase-selectivity problem. citeturn19view1turn19view2turn19view3turn8view6

**A direct CTC or sequence model trained specifically for `kuule/kule kratt`** is the strongest “pure KWS research” option if you were extending the project beyond the bachelor’s-thesis scope. The academic rationale is good: U2-KWS rescors token sequences in a second pass; CaTT-KWS does force alignment and transformer verification; older LSTM-CTC work supports arbitrary keyword spotting without per-keyword retraining. This is the clearest route if the scientific question becomes “how do we build an exact-order, resource-conscious Estonian wake detector,” rather than “what is a practical next step for a BSc prototype.” The difficulty is that it is a **new model-development contribution**, not a quick wrapper around the STT you already have. citeturn14view0turn16view0turn16view1turn14view1turn16view4turn14view3

**Keyword/filler or lattice-based phoneme verification** is very defensible academically and has a useful advantage for low-resource or custom phrases: it can work from a phoneme sequence and background/filler model, without requiring a large-vocabulary, general-purpose ASR front end. Amazon’s wakeword-independent verification paper even notes that ASR-based verification can be a bad fit when the wakeword is unknown, foreign-language, or outside the ASR lexicon. Since your wake phrase is fixed and you do have an Estonian ASR already, that advantage is smaller for Kratt than for some other projects. Still, if you later want a dedicated verifier that is more exact-order-sensitive than binary KWS but less generic than full ASR, this family is worth serious follow-up. citeturn10view4turn10view6turn17view0turn17view1

**Direct always-on full ASR** is the weakest option for Kratt and should be rejected for the bachelor’s-thesis system. Google’s cascade paper explicitly says always-on execution on a standard mobile application processor is incompatible with the power budget that made the DSP-first architecture necessary. Apple likewise keeps always-on detection on low-power hardware and only escalates to larger models after a candidate trigger. Even vendor documentation from entity["company","Picovoice","voice ai company"] says streaming STT is more resource-intensive, higher-latency, and worse for always-listening wake detection than a dedicated wake-word detector. A Raspberry Pi 5 may be able to run local ASR continuously, but that is not the same as saying it is a *good* architecture for a privacy-first smart-speaker satellite with an ESP32 front end. It would blur the clean separation between “cheap, always-on MCU listener” and “heavier local verifier only when needed.” citeturn23view0turn29view2turn30view0turn34view0

## Tradeoffs for this thesis project

The strongest argument **for** a local ASR verifier in Kratt is likely **false-accept reduction on the exact failure modes you actually observed**. Ordered rules over an ASR output are naturally able to reject `kuule`-only and reversed-order examples in a way a single binary score often cannot. The broader literature says this direction is plausible: Google’s contextual-ASR second pass cut false accepts by 89%; Amazon’s two-stage systems reported large relative FAR reductions; CaTT-KWS reduced false alarms per hour dramatically through successive verification stages. Those exact numbers should not be copied into the thesis as expected Kratt performance—the datasets, languages, and model budgets are too different—but the *direction* is well supported. citeturn33view0turn28view3turn16view4

The strongest argument **against** it is **recall loss**, and your own internal probe already shows why. ASR-based verification does not merely check phrase order; it first has to recognize enough of the phrase correctly. Amazon’s word-level verifier paper explicitly criticizes ASR-based verification because it is coupled to ASR performance and can fail if ASR never outputs the wakeword; Apple avoids trusting the one-best ASR path because it can hallucinate the trigger phrase. Your own probe is consistent with those warnings: a strict ordered transcript rule produced zero strict matches on the short `positive_command` subset and only about half on positives overall, while looser fuzzy rules improved recall but at the cost of making the acceptance logic less clean. So the literature and your internal evidence point in the same direction: **ASR verification is plausible, but one-best transcript string matching is brittle**. citeturn10view0turn10view2turn31view2

Latency is the next real concern. A second-stage verifier cannot be free because it needs a candidate segment, some buffering, and time to decode. Google’s cascade buffers about two seconds on the first stage before handing off to the second stage; Apple’s false-trigger mitigation analyzes the whole utterance after the trigger; and streaming STT systems generally work chunkwise and add at least some decoding delay. For Kratt, a local ASR verifier is acceptable only if it is used **after** a fast first-stage trigger and its added delay is measured explicitly. If the verifier has to wait for long post-trigger audio or end-of-speech before deciding, the user experience may become noticeably worse even if the final error rates improve. That tradeoff is acceptable in a diagnostic or future-work experiment; it is much harder to justify for a polished thesis demo unless the gains are large. citeturn23view0turn29view3turn31view1turn34view0

On privacy, the local Pi verifier is actually one of the most defensible parts of the idea. A whole line of literature on cloud-based wakeword verification exists precisely because many commercial systems escalate suspicious triggers to richer back-end processing. That same literature also treats the transmission of features or audio as a privacy risk. Your proposal avoids that by keeping verification on the local Raspberry Pi. So if the thesis says “a second stage is plausible and still privacy-preserving provided it remains local,” that is a strong argument, not a weak one. The main caveat is not privacy but engineering scope: once you start decoding more audio on the Pi, you are trading privacy-safe computation for more latency and more opportunities for ASR-induced misses. citeturn25view0turn33view0turn30view0

For robustness to accents and casual speech such as `kule`, the comparison becomes subtler. A binary wake model may overfire on partials because it learns a blurred acoustic template; a transcript-based verifier can be more structured, but it can also normalize accented pronunciations or casual realizations into the wrong lexical item. Google’s contextual-ASR work suggests wakeword-specific biasing and trigger non-terminals can help trigger recognition inside ASR, which is encouraging if you later add wake-phrase biasing to Kiirkirjutaja or the local decoder. Apple’s warning about ASR hallucination suggests the converse danger: if you over-bias toward the wake phrase, the verifier may start “finding” Kratt in things like `kurat` or `Grete`. That is why a thesis-grade verifier should distinguish at least three levels—strict, safe fuzzy, loose fuzzy—and report them separately rather than collapsing them into one headline result. citeturn33view0turn31view2

## Diagnostic experiment design for the thesis

The right experiment is a **small cascade evaluation**, not a full productization push.

Use your existing first-stage candidates exactly as you proposed: **v16c**, **expert-a**, **v18b+expert-a**, and **checkpoint-faph10+v16c** as diagnostic gates. Evaluate each in two modes: first stage alone, and first stage plus verifier. Because your thesis already learned that one number is misleading, preserve the same reporting philosophy in the cascade: streaming **FAPH**, unseen-speaker **recall**, and **hard-negative / prefix / confusable** false-positive rates must all be reported separately. Google and Picovoice both frame wake performance as a tradeoff between FRR and rate-per-hour false activations; for clip-based recall and hard-negative pass/fail proportions, report **95% Wilson score intervals** rather than Wald intervals, especially because some of your sets are small or near 0/1. citeturn29view4turn27view0turn26search0turn26search9

The verifier should have **three explicitly named rules**:

| Rule | Definition | Intended use |
|---|---|---|
| `strict_ordered_text` | Accept only if the transcript contains ordered `kuule` or `kule` before exact `kratt`; reject reversed order and partial-only matches. | Precision-first lower bound |
| `safe_fuzzy_ordered` | Accept ordered `kuule/kule` plus a curated whitelist of `kratt`-like second tokens validated on your probe; explicitly blacklist dangerous near-matches discovered in negatives. | Most realistic online candidate |
| `loose_fuzzy_ordered` | Accept ordered `kuule/kule` plus broader `kratt`-like fuzzy matching or phonetic similarity, optionally over n-best output if available. | Recall-first exploratory upper bound |

That separation matters because it keeps the thesis honest. A “good-looking” verifier can often be obtained simply by tightening the rule until it misses real users; a “good-looking” recall can often be obtained by loosening the rule until confusables slip through. Reporting all three rules prevents that kind of accidental cherry-picking. citeturn27view0turn31view2

The evaluation table for each first-stage candidate should have the following columns:

- **Stage-1 recall** on `pos_isa_xtts`, `pos_ode_real`, `pos_friend1_real`, and later on user-test positives.
- **Stage-1 FPR** on `hard_neg_mac_holdout`, `hard_neg_isa_xtts`, prefix-only sets, reversed-order sets, and `kuule/kule <not kratt>` confusables.
- **Verifier pass rate conditioned on stage-1 trigger**, split by the same datasets.
- **Final cascade recall/FPR** after the verifier.
- **Ambient final FAPH**, measured as confirmed false wakes per hour on long-form audio.
- **Added latency**, measured from stage-1 trigger timestamp to verifier accept/reject decision.

For ambient FAPH, do not force it into a clip-FPR framework. Report the raw exposure hours and the raw false-accept counts, because short long-form test durations can make per-hour estimates unstable. Picovoice’s benchmarking guidance argues that very short ambient tests are weak evidence for FAR claims, which is a useful caveat for your thesis discussion even if you continue using your practical held-out slices. citeturn27view0

A small but realistic user-test extension would be enough. With your planned **20–30 participants**, ask each participant to produce controlled positive wakes, hard negatives, and a few command-style utterances after the wake phrase. This matters because the current probe already suggests that short command-appended examples are exactly where a transcript-based verifier may break. If possible, preserve the raw stage-1 trigger timestamps and the verifier decision timestamps; otherwise you will not be able to report latency credibly.

The decision gate should be explicit in the thesis. I would label the outcome **promising** if, on the best first-stage candidate, the cascade does all of the following:

- cuts prefix/confusable false accepts **substantially**—ideally by **at least 80% relative** or to a clearly lower absolute level;
- keeps **real-speaker recall** within about **5 percentage points** of the first stage on `pos_friend1_real` and user-test positives;
- adds only moderate latency on Raspberry Pi verification;
- does not merely improve synthetic-clone performance while failing on real speakers.

I would label it **not worth pursuing online in this thesis** if any of the following happens:

- real-speaker recall drops by **more than about 10 percentage points**;
- the verifier still lets through a large share of prefix/confusable negatives;
- the online path requires long end-of-speech waits that make the interaction feel sluggish;
- the gains exist only on tiny or synthetic subsets.

Those thresholds are **project-specific decision criteria**, not literature standards, and the thesis should say so plainly.

## Thesis framing and conservative wording

For a bachelor’s thesis at entity["organization","Tallinn University of Technology","Tallinn, Harju, Estonia"], I would **not** recommend making the local ASR verifier the central implemented contribution unless the diagnostic experiment is unexpectedly strong. Your current core contribution is already coherent and defensible: an Estonian embedded wake-word effort, the data-quality audit, and the argument that wake-word evaluation must include FAPH, unseen-speaker recall, and confusable negatives, not a single clip score. The verifier fits best as **diagnostic evidence plus future work**.

In English, the conservative thesis claim should read roughly like this:

Binary embedded KWS can achieve useful recall for a wake phrase, but it may struggle to enforce exact multi-word phrase selectivity under prefix-only and phonetically confusable negatives. A local second-stage verifier based on ASR or sequence-aware rescoring is therefore a plausible mitigation. However, the current Kratt probe indicates that transcript-based verification can reduce confusable activations at the cost of recall and latency, especially on short or imperfectly transcribed utterances. Consequently, the approach is promising as future work, but it requires validation on a larger real-speaker user study before any production-readiness claims can be made.

A thesis-ready Estonian paragraph could be:

> Käesoleva töö tulemused viitavad, et väikese ressursijäljega binaarne ärksõnatuvastus võib saavutada hea tabamismäära, kuid jääda hätta täpse kaheastmelise fraasi „Kuule/Kule Kratt“ selektiivsel eristamisel. Eriti ilmnesid valepositiivsed käivitused prefiksi („kuule/kule“) ning häälikuliselt sarnaste väljendite korral. Seetõttu on põhjendatud käsitleda võimaliku leevendusena lokaalset teise astme verifitseerijat, mis kontrollib pärast esmast käivitust, kas kõnes esines järjestatud muster „kuule/kule … kratt“. Projekti esialgne proovikatse näitas, et selline ASR-põhine kontroll võib vähendada osa segadusttekitavaid valekäivitusi, kuid toob kaasa tundlikkuse kao ja lisalatentsi riski, eriti lühikeste või ebatäpselt transkribeeritud lausungite puhul. Seega ei saa lahendust pidada käesoleva töö põhjal tootmisküpseks, kuid see on põhjendatud tuleviku töö suund, mis vajab valideerimist suurema reaalkasutajate testiga.

That wording is careful, evidence-aligned, and does not overclaim.

## Open questions and limitations

Most of the strongest published gains for second-pass wake verification come from **large internal datasets**, **cloud/server settings**, or richer decoder structures than a simple transcript Contains-rule. That means the literature supports the **direction**, but not a numeric prediction for Kratt. citeturn33view0turn31view1turn28view3

Your internal ASR probe is also still small, and it appears to use mostly **1-best transcript logic**. Apple’s public write-up is a good reminder that one-best ASR output can hallucinate the trigger phrase; richer evidence such as n-best hypotheses, confidence scores, or lattices may matter if you continue this line of work. citeturn31view2

Finally, wake-word selectivity can also be improved by **better data and sequence-aware wake models**, not only by an ASR verifier. So if the verifier underperforms, that does not mean the exact-phrase problem is unsolved; it may simply mean this particular second-stage design is not the right one for the current thesis scope. citeturn21view0turn15view2turn14view0turn14view1

## Source table and BibTeX

### Peer-reviewed papers

| Title | Authors | Year | Venue / company | DOI / URL | Why it matters |
|---|---|---:|---|---|---|
| Keyword Spotting for Google Assistant Using Contextual Speech Recognition citeturn33view0 | Assaf Michaely et al. | 2017 | ASRU / Google | `doi:10.1109/ASRU.2017.8268946` | Closest primary-source analogue to “first-stage KWS + ASR verifier”; reports 89% FA reduction with 0.2% FR increase. |
| A Cascade Architecture for Keyword Spotting on Mobile Devices citeturn23view0turn29view4 | Alexander Gruenstein et al. | 2017 | NeurIPS workshop / Google | `https://arxiv.org/abs/1712.03603` | Canonical DSP-first, AP-second cascade; explains why always-on full ASR is a poor fit for low-power devices. |
| Monophone-based Background Modeling for Two-stage On-device Wake Word Detection citeturn28view3 | Minhua Wu et al. | 2018 | ICASSP / Amazon | `https://www.amazon.science/publications/monophone-based-background-modeling-for-two-stage-on-device-wake-word-detection` | Two-stage on-device wake verification with reported FRR/FAR gains and low extra compute. |
| An Audio-Based Wakeword-Independent Verification System citeturn10view4turn10view6 | Joe Wang et al. | 2020 | Interspeech / Amazon | `https://assets.amazon.science/c7/37/d027a0f24849a296853c0c62f883/an-audio-based-wakeword-independent-verification-system.pdf` | Useful for comparing ASR-based verification to wakeword-agnostic alternatives, especially for custom or lexicon-poor phrases. |
| CaTT-KWS: A Multi-stage Customized Keyword Spotting Framework based on Cascaded Transducer-Transformer citeturn14view1turn16view4 | Zhirui Yang et al. | 2022 | Interspeech | `doi:10.21437/Interspeech.2022-10258` | Strong modern example of multi-stage KWS with force-alignment and transformer verification. |
| U2-KWS: Unified Two-Pass Open-Vocabulary Keyword Spotting with Keyword Bias citeturn14view0turn16view0 | Aijia Zhang et al. | 2023 | ASRU / arXiv preprint | `https://arxiv.org/abs/2312.09760` | Shows a clean two-pass CTC-plus-decoder architecture that is explicitly order-aware. |
| Unrestricted Vocabulary Keyword Spotting Using LSTM-CTC citeturn14view3turn16view6 | B. Zhuang et al. | 2016 | Interspeech | `https://www.isca-archive.org/interspeech_2016/zhuang16_interspeech.html` | Classic open-vocabulary CTC reference for arbitrary keywords without per-keyword retraining. |
| Privacy-Preserving Feature Extraction for Cloud-Based Wake Word Verification citeturn25view0 | Timm Koppelmann et al. | 2021 | Interspeech | `https://leaschoenherr.me/media/paper/2021_interspeech.pdf` | Helps frame why a local second-stage verifier is privacy-friendlier than cloud verification. |

### Industry research and official documentation

| Title | Authors / org | Year | Source type | URL | Why it matters |
|---|---|---:|---|---|---|
| Voice Trigger System for Siri citeturn30view0turn31view1 | Siri Team / Apple | current public research page | Official research page | `https://machinelearning.apple.com/research/voice-trigger` | Best official industry source for multistage checker design, phonetically similar negs, and ASR-lattice false-trigger mitigation. |
| Personalized Hey Siri citeturn9view6 | Siri Team / Apple | 2018 | Official research page | `https://machinelearning.apple.com/research/personalized-hey-siri` | Useful for the text-dependent speaker-verification view of cascaded triggering. |
| Wake Word Benchmarks in 2026: How to Verify Vendor Claims citeturn27view0 | Picovoice | 2026 | Vendor benchmark guidance | `https://picovoice.ai/blog/wake-word-benchmarks/` | Good practical reference for reporting FRR at fixed FAR/FAPH rather than meaningless raw “accuracy.” |
| Complete Guide to Real-Time Transcription citeturn34view0 | Picovoice | 2026 | Vendor technical guide | `https://picovoice.ai/blog/complete-guide-to-streaming-speech-to-text/` | Useful only as a practical source for why always-on STT is heavier and higher-latency than dedicated KWS. |

### GitHub and open-source documentation

| Title | Authors / org | Year | Source type | URL | Why it matters |
|---|---|---:|---|---|---|
| openWakeWord custom verifier models citeturn8view6 | dscripka/openWakeWord | current | GitHub docs | `https://github.com/dscripka/openWakeWord/blob/main/docs/custom_verifier_models.md` | Shows that “base wake model + verifier” is also standard in open source, though mainly for speaker filtering. |
| Micro Wake Word docs for ESPHome citeturn19view1turn19view2 | ESPHome / OHF ecosystem | current | Official docs | `https://esphome.io/components/micro_wake_word/` | Confirms multiple on-device models, configurable thresholds, and VAD support in your ecosystem. |
| microWakeWord README citeturn19view0 | OHF-Voice/micro-wake-word | current | GitHub README | `https://github.com/OHF-Voice/micro-wake-word` | Useful for describing the embedded streaming detector design and constraints. |
| openSpeechToIntent README citeturn20view0 | dscripka/openSpeechToIntent | current | GitHub README | `https://github.com/dscripka/openSpeechToIntent` | An open-source example of using a stronger second stage to suppress false wake activations. |

### Speculative recommendations used in this report

The following are **project-specific recommendations**, not literature claims: use the Kiirkirjutaja verifier primarily as a **diagnostic/future-work path**, require a **small recall drop** before promoting it to the online path, and prefer a **safe fuzzy ordered** rule over either a brittle strict rule or an overly permissive loose rule for any user-facing demo.

### BibTeX for the most important sources

```bibtex
@inproceedings{michaely2017googlekws,
  title={Keyword Spotting for Google Assistant Using Contextual Speech Recognition},
  author={Michaely, Assaf Hurwitz and Zhang, Xuedong and Simko, Gabor and Parada, Carolina and Aleksic, Petar},
  booktitle={2017 IEEE Automatic Speech Recognition and Understanding Workshop (ASRU)},
  year={2017},
  doi={10.1109/ASRU.2017.8268946},
  url={https://research.google.com/pubs/archive/46554.pdf}
}

@article{gruenstein2017cascade,
  title={A Cascade Architecture for Keyword Spotting on Mobile Devices},
  author={Gruenstein, Alexander and Alvarez, Raziel and Thornton, Chris and Ghodrat, Mohammadali},
  journal={arXiv preprint arXiv:1712.03603},
  year={2017},
  url={https://arxiv.org/abs/1712.03603}
}

@article{wu2018monophone,
  title={Monophone-based Background Modeling for Two-stage On-device Wake Word Detection},
  author={Wu, Minhua and Panchapagesan, Sankaran and Sun, Ming and Gu, Jiacheng and Thomas, Ian and Vitaladevuni, Shiv Naga Prasad and Hoffmeister, Bjorn and Mandal, Arindam},
  year={2018},
  url={https://www.amazon.science/publications/monophone-based-background-modeling-for-two-stage-on-device-wake-word-detection}
}

@inproceedings{yang2022cattkws,
  title={CaTT-KWS: A Multi-stage Customized Keyword Spotting Framework based on Cascaded Transducer-Transformer},
  author={Yang, Zhirui and Sun, Shiliang and Li, Jinyu and Zhang, Xiaohui and Wang, Xiaofei and Ma, Lian and Xie, Lei},
  booktitle={Interspeech 2022},
  year={2022},
  doi={10.21437/Interspeech.2022-10258},
  url={https://www.isca-archive.org/interspeech_2022/yang22n_interspeech.html}
}

@article{zhang2023u2kws,
  title={U2-KWS: Unified Two-Pass Open-Vocabulary Keyword Spotting with Keyword Bias},
  author={Zhang, Aijia and Zhou, Pengfei and Huang, Kai and Zou, Yichong and Liu, Ming and Xie, Lei},
  journal={arXiv preprint arXiv:2312.09760},
  year={2023},
  url={https://arxiv.org/abs/2312.09760}
}

@inproceedings{zhuang2016lstmctc,
  title={Unrestricted Vocabulary Keyword Spotting Using LSTM-CTC},
  author={Zhuang, Bo and Yang, Guosheng and Dines, John and Yan, Chunlei and Zhu, Min},
  booktitle={Interspeech 2016},
  year={2016},
  url={https://www.isca-archive.org/interspeech_2016/zhuang16_interspeech.html}
}

@inproceedings{koppelmann2021privacywwv,
  title={Privacy-Preserving Feature Extraction for Cloud-Based Wake Word Verification},
  author={Koppelmann, Timm and Nelus, Alexandru and Sch{\"o}nherr, Lea and Kolossa, Dorothea and Martin, Rainer},
  booktitle={Interspeech 2021},
  year={2021},
  url={https://leaschoenherr.me/media/paper/2021_interspeech.pdf}
}

@article{siriteam2018personalized,
  title={Personalized Hey Siri},
  author={{Siri Team}},
  journal={Apple Machine Learning Research},
  year={2018},
  url={https://machinelearning.apple.com/research/personalized-hey-siri}
}
```