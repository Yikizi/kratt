# Improving Unseen-Speaker Recall for Kratt

## Executive summary

- The most likely diagnosis is **G: a combination of factors**, with the largest contributors being **D (checkpoint/threshold selection over-optimizing ambient false accepts)**, **A (too little real speaker diversity)**, and **B (synthetic-data domain mismatch / shortcut learning)**. I think **C (objective mismatch for exact two-word phrase detection)** is also real, but secondary to the first three. I do **not** think **F (tiny-model capacity alone)** is the main blocker. **Confidence: high.** citeturn14view0turn24view0turn24view3turn26view6turn11view2turn37view0

- Your own evidence already shows that **ambient-FAPH optimization can destroy useful recall**: the `checkpoint-faph20 + v16c` combo nearly zeros ambient FAPH, but Friend1 recall falls from **87.6% to 40.0%**. That pattern is exactly what the literature warns about when operating points are chosen too conservatively or when second-stage gating is not recall-aware. **Confidence: high.** citeturn14view0turn14view1turn11view3turn37view0

- The literature does **not** support a simple rule like “TTS can replace real speakers.” What it does support is narrower: TTS helps a lot when paired with either **strong pretrained embeddings/backbones**, **large synthetic diversity**, **real negative audio**, or **a modest but diverse real positive set**. Public studies repeatedly show that **speaker diversity matters more than adding many more utterances per already-seen speaker**. **Confidence: high.** citeturn21view0turn19view4turn24view3turn25view0turn22view4turn26view6

- The strongest public synthetic-data papers now explicitly warn that **TTS introduces artifacts the model can exploit**, hurting real-speech generalization. Adversarially suppressing TTS-specific cues improved real-speech accuracy by **up to 12%**, and even improved accuracy in a no-real-positive setting by **up to 8%** in one 2024 study. **Confidence: high.** citeturn24view0turn24view1turn24view2

- Your remaining false accepts on **prefix-only**, **reversed order**, and **`kuule/kule <confusable>`** strongly suggest that a plain binary clip classifier is still learning something closer to a **permissive phonetic trigger** than a strict ordered two-word phrase detector. Public production systems from Apple, Amazon, and Google frequently use **multi-stage**, **phonetic/HMM**, **ASR-aligned**, or **verification** components precisely for this reason. **Confidence: medium-high.** citeturn11view2turn37view0turn29search2turn40search0turn40search7

- The best **immediate, thesis-safe** move is **not** a brand-new architecture. It is to change **model selection and thresholding**: move from “minimize ambient FAPH first” to a **constrained Pareto rule** that rejects any checkpoint failing minimum unseen-speaker recall and hard-negative rejection floors. This is low-risk and directly aligned with your observed failure mode. **Confidence: high.** citeturn14view0turn14view1turn14view2

- The best **single high-value v19 experiment** is a **two-stage system**: keep a **high-recall** ESP32 microWakeWord gate, but verify candidate windows on the Raspberry Pi / Home Assistant side with a small **phrase verifier** that is order-aware and confusable-aware. Public wake-word systems and open-source recipes support this architecture, and it is a better fit for your exact-phrase requirement than continuing to force one tiny binary model to do everything. **Confidence: medium-high.** citeturn11view2turn37view0turn29search2turn26view4turn26view5

- If you cannot add consented development speakers before the thesis deadline, the academically safest conclusion is that **Kratt is now mostly limited by real-speaker diversity and realistic synthetic methodology**, not by a lack of “clean labels” alone. The public evidence is strong enough to justify that conclusion. **Confidence: high.** citeturn24view3turn25view0turn26view6turn24view0

## Literature map

| Paper / system | Year | Method | Data scale / setting | Key result | Relevance to Kratt | DOI / source |
|---|---:|---|---|---|---|---|
| Sainath & Parada, *Convolutional Neural Networks for Small-footprint Keyword Spotting* | 2015 | Small-footprint CNN for KWS | On-device small-footprint KWS | Replaced earlier keyword/filler HMM baselines with compact neural models; helped establish the small-footprint neural KWS line | Useful as the “binary small model” baseline family Kratt belongs to | 10.21437/Interspeech.2015-248 / PDF source citeturn40search15 |
| Rybakov et al., *Streaming Keyword Spotting on Mobile Devices* | 2020 | Streaming conversion library; benchmarked DNN/CNN/SVDF/CRNN/MHSA families | Mobile / streaming KWS | Reported latency–accuracy tradeoffs and a 10% classification-error reduction with MHSA models on Speech Commands | Strong background for streaming deployment and why architecture alone is usually a tradeoff, not a silver bullet | arXiv:2005.06720 citeturn28search0 |
| Lin et al., *Training Keyword Spotters with Limited and Synthesized Speech Data* | 2020 | Synthetic positives + pretrained speech embeddings | Small spoken-term detectors around 400k params | Synthetic-only + pretrained embeddings matched a model trained on **500+ real examples**; without the embedding model, roughly **4000+** real examples were needed for the same accuracy | Strong evidence that TTS can help, but only when paired with a strong backbone | ICASSP 2020, DOI 10.1109/ICASSP40776.2020.9053193 / arXiv:2002.01322 citeturn21view0 |
| Werchniak et al., *Exploring the application of synthetic audio in training keyword spotters* | 2021 | Careful TTS + human mixing | Low-resource keyword spotting | Careful TTS/human mixing reduced DET AUC by **over 11%** | Supports mixing synthetic with real rather than replacing real outright | ICASSP 2021, DOI 10.1109/ICASSP39728.2021.9413448 citeturn19view4 |
| Mazumder et al., *Few-Shot Keyword Spotting in Any Language* | 2021 | Multilingual transfer / embedding model | 760 words from 9 languages; evaluated on 22 languages | With **5 examples**, got average F1 **0.75** on keyword classification; streaming KWS **87.4% TPR** at **4.3% FPR** across 22 languages | Important caveat: few-shot works when you start from multilingual pretraining, not when you train a tiny binary detector from scratch | arXiv:2104.01454 citeturn22view0turn22view2turn22view3 |
| Rikhye et al., *Personalized Keyphrase Detection using Speaker and Environment Information* | 2021 | Streaming ASR + SV + speaker separation + ANC | Customizable multi-word keyphrases | Speaker verification sharply reduced false triggers; separation and ANC reduced false rejects | Strong evidence for a second-stage verifier and environment-aware front-end | arXiv:2104.13970 citeturn29search2 |
| Higuchi et al., *Multi-task Learning with Cross Attention for Keyword Spotting* | 2021 | ASR/KWS multi-task with phonetic encoder + cross-attention decoder | Phrase KWS with ASR supervision | Reported **12% relative FRR reduction** over a conventional multi-task baseline and explicitly framed the phoneme-vs-KWS loss mismatch problem | Helpful if you want a sequence-aware post-thesis research direction | arXiv:2107.07634 citeturn40search0turn40search2 |
| Ghosh et al., *Low-resource Low-footprint Wake-word Detection using Knowledge Distillation* | 2022 | Distillation from large acoustic model + phone-synchronous targets | Simulated low-resource subsets of **100/500/1000/2000** positives; subsets covered **19–404 speakers** depending on corpus | Accuracy improved across dataset sizes; phone-synchronous targets also reduced latency | Very relevant: shows low-resource wake-word quality tracks both data size and transfer-learning strength | DOI 10.21437/Interspeech.2022-529 / PDF source citeturn19view7turn22view4 |
| Lee & Baek, *Keyword Spotting with Synthetic Data using Heterogeneous Knowledge Distillation* | 2022 | Synthetic-only unseen-class KWS with embedding KD | Unseen user-defined keywords | Student model learned unseen keyword classes from synthetic data by mimicking a real-data reference model | Supports “synthetic works better when mediated by a richer teacher/reference space” | DOI 10.21437/Interspeech.2022-47 / PDF source citeturn19view5 |
| Apple, *Voice Trigger System for Siri* and *Personalized Hey Siri* | 2018–2023 | Multi-stage detector + checker + speakerID + SDSD; phoneme/HMM first stage | Production wake-word pipeline | Publicly states that production voice trigger uses **multiple stages** for recall, precision, speaker discrimination, and phonetically similar rejection | Strongest public evidence that strict wake-word quality usually needs more than one tiny binary threshold | Official research articles citeturn11view2turn11view3 |
| Park et al., *Adversarial training of Keyword Spotting to Minimize TTS Data Overfitting* | 2024 | Adversarial suppression of TTS-specific cues | Large TTS usage, scarce real positives | Real-speech accuracy improved by **up to 12%**; **up to 8%** even without real positive examples | Direct evidence that naive TTS can create shortcut learning and that the problem is fixable | arXiv:2408.10463 / workshop DOI 10.21437/SynData4GenAI.2024-18 citeturn24view0turn24view2 |
| Zhu et al., *Synth4Kws* | 2024 | Controlled study of phrase diversity, TTS volume, and TTS/real ratios | 38k phrases; 726 speakers; 5 prosodies; 50k-real baseline | More TTS phrase diversity and more samples per phrase improved monotonically; adding optimal TTS cut EER by **30.1%** and improved AUC by **46.7%** in low-resource settings | Strong evidence for systematic synthetic diversification, but note that the setup is triplet/embedding-based and not a tiny binary wake-word classifier | arXiv:2407.16840 / DOI 10.21437/SynData4GenAI.2024-3 citeturn23view0 |
| Park et al., *Utilizing TTS Synthesized Data for Efficient Development of Keyword Spotting Model* | 2024 | Large TTS + small real positive sweeps | Baseline had **3.8M** real positives; TTS mixed with **1k–20k** real positives | **100 speakers × 10 utt** with TTS beat adding many more utterances per fewer speakers; speaker count helped more than per-speaker repetition | Probably the single most relevant public result for your unseen-speaker issue | arXiv:2407.18879 citeturn24view3turn25view0 |
| Zhang et al., *GraphemeAug* | 2025 | Synthesized hard negatives from grapheme edits | Held-out hard-negative evaluation | Hard-negative AUC improved by **61%** while maintaining positive and ambient-negative quality | Directly relevant to `kuule/kule <confusable>`, prefixes, and near-neighbor negatives | DOI 10.21437/Interspeech.2025-1038 / arXiv:2505.14814 citeturn32search0turn20view1 |
| openWakeWord and Home Assistant / microWakeWord docs | 2023–2025 | Practical open-source wake-word recipes | Synthetic positives, large negative pools; server-side vs MCU deployment | openWakeWord recommends **several thousand** generated positives, used roughly **30,000 h** of negatives, and exposes second-stage verifier models; Home Assistant explicitly says real voices are still needed to improve microWakeWord | High-value engineering guidance directly adjacent to your stack | Official docs / repos citeturn26view2turn26view3turn26view4turn26view5turn26view6turn27view1 |

## Diagnosis of the current failure mode

My bottom-line diagnosis is:

> **Kratt is primarily limited by insufficient real-speaker diversity and an over-conservative checkpoint-selection regime, with additional damage from synthetic-domain shortcut learning and a one-stage binary objective that is not ideal for exact ordered two-word detection.** **Confidence: high.** citeturn24view3turn25view0turn24view0turn11view2turn37view0turn14view0

The strongest reason to put **speaker diversity** near the top is that the public evidence that best matches your symptom says exactly what your Friend1 set is telling you: with TTS as a base, adding **more speakers** helps much more than adding many more utterances from the same few speakers. In the 2024 TTS/real mixing study, with fixed TTS and fixed negatives, FRR improved far more when speaker count increased than when utterances-per-speaker increased, and the authors concluded that speaker diversity had more impact than per-speaker repetition. The low-resource distillation paper also shows that “100, 500, 1000, 2000 positives” correspond to dramatically different speaker counts, and performance rises with that scale. The Home Assistant team’s own public call for recordings is notable here: even with a mature synthetic-first recipe, they still say real voices across genders, ages, and accents are needed to improve microWakeWord. **Confidence: high.** citeturn25view0turn22view4turn26view6

The strongest reason to put **checkpoint-selection bias** at the very top is your own result: `checkpoint-faph20 + v16c` almost solves ambient false accepts, but Friend1 recall collapses to 40%. That is too large to dismiss as ordinary threshold tradeoff noise. It looks like an optimization target that is finding a model mixture that is excellent at rejecting backgrounds but systematically under-generalizes to some real speakers. This is also consistent with the microWakeWord recipe itself, which prioritizes a minimization metric first and then maximizes a second metric only after a target is met; that is a useful mechanism, but if the first metric is too dominant and does not include unseen-speaker recall constraints, it will pick over-conservative models. **Confidence: high.** citeturn14view0turn13view0

The reason to keep **synthetic methodology** as a major contributor is that recent literature now explicitly names the problem you are worried about: TTS artifacts can create **hidden-domain shortcuts**. Park et al. 2024 show that adversarially suppressing TTS-specific cues improves real-speech accuracy by up to 12%, which is a direct confirmation that naive TTS can distort the learned decision rule. Public synthetic recipes that work well also go far beyond “plain TTS of the wake phrase”: they mix many speakers, prosodies, room/distance simulation, speed variation, and large real negative pools; one openWakeWord recipe even caps generations per source voice and interpolates speaker embeddings afterward. Your cleaned v18 positives fixed label purity, which was necessary, but the literature says label purity alone does **not** solve synthetic-to-real mismatch. **Confidence: high.** citeturn24view0turn24view1turn23view0turn26view0turn26view2

I think **objective mismatch** is real, but I rate it slightly below the three factors above because your baseline `v16c` still gets very high recall on some external speakers. So the objective is not fatally wrong for “wake-word-ish” behavior; it is just probably too weak for **strict ordered phrase** behavior under limited data. The public production literature is persuasive here: Apple’s voice trigger stack uses a **streaming high-recall detector**, a **high-precision checker**, and then additional speaker/disambiguation logic; Amazon reports gains from a two-stage monophone-background system; Google’s personalized keyphrase detector uses an ASR model plus speaker/environment components. All three point to the same engineering lesson: exact phrase selectivity and low FRR at low FAR are often solved with **cascades**, not a single tiny clip classifier. **Confidence: medium-high.** citeturn11view2turn37view0turn29search2

I think **hard-negative composition** may be contributing, but I do not think it is the primary cause by itself. The literature supports **smart** hard-negative mining and **systematic** confusable generation, not simply increasing negative weight until FAPH drops. Hou et al. show that indiscriminate use of all negative frames creates class-imbalance problems, and their regional hard-example mining helped by controlling the negative/positive ratio. GraphemeAug is also encouraging precisely because it improves hard-negative behavior **while maintaining positive and ambient performance**. That is close to your goal: better phrase selectivity without wrecking recall. **Confidence: medium.** citeturn33view0turn34view1turn32search0

I think **architecture capacity / frontend** is the weakest of the candidate explanations. Tiny architectures matter, and some are better than others, but the public literature shows plenty of strong small-footprint KWS results with DS-CNN, BC-ResNet, MatchboxNet, and streaming CNN/attention variants. More importantly, your own `v16c` can already hit 100% Isa XTTS and 87.6% Friend1 at the same tiny-device scale. That makes it hard to argue the hardware budget is the first-order problem. I would instead say the tiny budget mainly limits how much **phrase modeling** you can ask one stage to do; it does not by itself explain the whole Friend1 collapse. **Confidence: medium.** citeturn5search8turn5search12turn28search0turn26view5

If I map your A–G options directly, my ranking is:

| Option | Verdict | Why |
|---|---|---|
| **A. Primarily data-limited in real speaker diversity** | **Yes, major factor** | Public sweeps show speaker count matters disproportionately, and open-source maintainers still ask for many real voices even with synthetic pipelines. **Confidence: high.** citeturn25view0turn26view6 |
| **B. Flawed synthetic data methodology** | **Yes, major factor** | Recent work directly shows TTS artifact overfitting and gains from adversarial mitigation; strong recipes use richer variation than naive TTS. **Confidence: high.** citeturn24view0turn24view1turn26view0 |
| **C. Binary clip objective is mismatched** | **Probably yes, secondary factor** | Public production systems for strict wake phrases commonly add sequence-aware or second-stage verification. **Confidence: medium-high.** citeturn11view2turn37view0turn29search2turn40search0 |
| **D. Checkpoint/threshold selection over-optimizes FAPH** | **Yes, major factor** | Your own numbers already demonstrate it. **Confidence: high.** citeturn14view0 |
| **E. Hard-negative ratio/composition causes recall collapse** | **Possible contributor, not primary** | Literature supports controlled hard-negative mining, not brute-force negative weighting. **Confidence: medium.** citeturn33view0turn32search0 |
| **F. Architecture / frontend mismatch is the bottleneck** | **Unlikely primary bottleneck** | Tiny models can work well; your baseline already partly does. **Confidence: medium.** citeturn5search8turn28search0turn26view5 |
| **G. Combination of the above** | **Best overall answer** | Best fits both your results and the literature. **Confidence: high.** citeturn24view0turn25view0turn11view2 |

For statistical validity: **Friend1 recall collapse is enough evidence of poor generalization**. With **n = 145**, 40.0% recall is not a small-sample wobble; a rough 95% binomial interval is only about ±8 percentage points. By contrast, Ode’s **n = 11** is too small to support strong conclusions, and Isa XTTS is useful but is still synthetic / proxy data. So the right framing is: **Friend1 is the decisive speaker-generalization warning set; Ode is only suggestive; Isa XTTS is supportive but not sufficient.** **Confidence: high.**

**Open questions / limitations:** no public paper I found gives a universal scaling law for “how many positives/speakers are enough” for a tiny custom two-word wake phrase in Estonian. Most strong public results either rely on large pretrained backbones, huge private datasets, non-Estonian TTS, or multi-stage systems. So the literature can justify direction and diagnosis, but it cannot promise that a specific speaker count will solve Kratt completely. **Confidence: high.** citeturn21view0turn22view0turn24view3

## What we might be doing wrong

Use this as a skeptical audit list before changing architecture:

- **Are we still selecting checkpoints with an objective that has no recall floor on held-out real speakers?** If yes, fix that first. Your present failure mode is exactly what happens when ambient negatives dominate model selection. **Evidence tier: strong.** citeturn14view0

- **Are we treating “clean exact positives” as sufficient, without also maximizing speaker and channel diversity?** Clean labels were necessary after v17, but the literature says they are not enough for real-speaker generalization. **Evidence tier: strong.** citeturn24view3turn26view6

- **Are the synthetic positives too homogeneous?** That includes one or too few TTS engines, too few speaker identities, too little prosody variation, no style transfer, no room/distance simulation, and no codec/microphone diversification. Strong public synthetic pipelines do all of those. **Evidence tier: strong.** citeturn23view0turn26view5turn26view0

- **Are we under-using real negative audio?** The 2024 TTS/real study found that adding a base set of real negatives dramatically improved TTS-based models. openWakeWord also scales negatives aggressively, reportedly using about 30,000 hours. **Evidence tier: strong.** citeturn25view0turn26view3

- **Is microWakeWord’s current feature-generation path missing audio-domain augmentation before feature extraction?** The current repo explicitly says it is still early, does not include sample generation or audio augmentation end-to-end, and applies no direct audio augmentation at feature conversion time. That creates a real pathway for weaker synth-to-real transfer than the openWakeWord-style pipeline. **Evidence tier: strong.** citeturn27view1turn26view5

- **Are positive windows too “tight” or too context-poor for the micro frontend?** The microWakeWord docs explicitly say generalization improves if features are generated over a longer time span than the model strictly needs, because the preprocessor applies PCAN and noise reduction. If your positive crops are too aggressively standardized, you may be making that worse. **Evidence tier: medium-high.** citeturn27view2

- **Are we overweighting hard negatives late in training without monitoring real-speaker FRR per condition?** The repo itself says increasing negative class weight near the end reduces false accepts, but the hard-negative literature argues for **controlled** mining, not unbounded negative pressure. **Evidence tier: medium-high.** citeturn13view4turn33view0

- **Are we expecting one tiny binary model to solve both speaker generalization and exact ordered phrase verification?** Public production systems usually split those jobs across stages. **Evidence tier: strong.** citeturn11view2turn37view0turn29search2

- **Are we reading too much into tiny evaluation sets?** Keep using Friend1 aggressively; treat Ode as anecdotal until you have more speakers. Also report per-speaker results, not just pooled recall. **Evidence tier: strong.** citeturn38view0turn14view1

- **Are we silently assuming “synthetic proxy speaker” equals “unseen real speaker”?** The literature does not support that assumption. XTTS/voice-cloned success is encouraging, but it is not the same as real unseen-speaker robustness. **Evidence tier: medium-high.** citeturn24view0turn26view6

## Ranked intervention plan

### Immediate

| Rank | Intervention | Expected benefit | Risk | Data needed | Complexity | How to evaluate | Evidence / confidence |
|---|---|---|---|---|---|---|---|
| 1 | **Replace FAPH-only checkpointing with constrained Pareto selection**: require minimum Friend1 recall, minimum hard-negative rejection, and only then minimize ambient FAPH | Likely largest immediate gain because it directly targets your observed failure mode | Low | No new data required, though a small consented real-dev split helps | Low | Compare DET / recall curves for `v16c`, faph10, faph20, and mixtures; pick checkpoints only from the Pareto front | Supported by your own results plus microWakeWord’s two-step selection design. **Confidence: high.** citeturn14view0turn13view0 |
| 2 | **Stop treating the `checkpoint-faph20 + v16c` consensus as the default thesis candidate** unless it meets a real-speaker recall floor | High | Low | No new data | Low | Re-benchmark at multiple thresholds, and include per-speaker recall floors in the selection rule | Supported by your Friend1 collapse. **Confidence: high.** |
| 3 | **Upgrade the synthetic pipeline before feature extraction**: multi-speaker TTS, prosody control, room/distance simulation, speed variation, background mixing, codec/mic simulation, and speaker-embedding interpolation where possible | Medium-high | Moderate; could increase training variance if done sloppily | Existing transcripts + TTS access + negatives | Moderate | Hold out a fixed real-dev set and A/B each augmentation family; do not trust synthetic validation alone | Supported by Synth4Kws, Park 2024, openWakeWord / Home Assistant pipelines, and the Sonos room-simulation study. **Confidence: high.** citeturn23view0turn24view0turn26view5turn31search0 |
| 4 | **Add hard negatives systematically, not just heavily**: `kuule`, `kratt`, reversed order, `kuule/kule <not kratt>`, and grapheme-edited confusables around “kuule/kule kratt” | Medium | Moderate: too much weight can hurt recall | Existing text inventory + TTS + real hard negatives | Moderate | Track positive FRR and each hard-negative group separately after every change | Supported by GraphemeAug and hard-negative mining work. **Confidence: medium-high.** citeturn32search0turn33view0 |
| 5 | **Generate features from longer audio context before model truncation** so PCAN/noise reduction stabilize | Medium | Low | No new data | Low | A/B with identical data and same architecture | Explicitly recommended by microWakeWord docs. **Confidence: medium-high.** citeturn27view2 |
| 6 | **Use a small, explicit real-speaker dev split if consent allows**; otherwise do leave-one-speaker-out validation on the currently available real speakers | Medium | Low | Existing consented real positives | Low-moderate | Report per-speaker recall and pooled recall | Supported by privacy-aware evaluation literature and by your current uncertainty imbalance across Friend1/Ode/XTTS. **Confidence: high.** citeturn38view0 |

A practical immediate recipe, based on the public evidence and your time constraints, is therefore:

1. freeze architecture for one more cycle;  
2. rebuild checkpoint selection around **real-speaker recall floors**;  
3. improve the synthetic/augmentation path;  
4. add **balanced** confusable negatives;  
5. only then decide whether architecture change is still necessary.

That sequence is the lowest-risk route to a thesis-safe result. **Confidence: high.**

### V19 candidate

**Recommended v19 experiment:** **high-recall first stage on ESP32 + phrase/order-aware second-stage verifier on Raspberry Pi / Home Assistant.**  
Why this one? Because it directly addresses your strongest tension: the edge model needs recall, but strict phrase selectivity is still weak. Public production systems routinely separate those jobs. openWakeWord also explicitly supports second-stage verifier models, and Home Assistant already distinguishes MCU-class and server-class wake-word engines. **Confidence: medium-high.** citeturn11view2turn37view0turn26view4turn26view5

Concretely:

- **Stage 1 on ESP32-S3:** keep a recall-oriented microWakeWord model near the `v16c` operating region, possibly even slightly lowering the threshold if Stage 2 will catch false accepts.
- **Stage 2 on Pi / server:** verify only candidate 1.0–1.5 s windows with a small model that explicitly scores the ordered phrase `kuule kratt` / `kule kratt` against:
  - `kuule`
  - `kratt`
  - `kratt kuule`
  - `kuule/kule <confusable>`
  - held-out real hard negatives

For the verifier, the lowest-risk implementation is **not** a giant new ASR stack. The best options are:

- a tiny **CTC / alignment** verifier over a few tokens or phoneme-like symbols; or
- an **embedding + alignment** verifier over the candidate window; or
- a tiny ASR-alignment checker if you already have a lightweight Estonian recognizer available.

This is feasible because the second stage only runs on a **small number of candidate windows**, not continuously. That relaxes the model-size constraint dramatically. **Confidence: medium-high.** citeturn29search2turn9search3turn40search7turn37view0

### Post-thesis

The most promising post-thesis path is a **sequence-aware or open-vocabulary formulation**, not another long series of one-stage binary sweeps. The shortlist is:

- **multi-task KWS + phonetic / ASR supervision**,  
- **CTC-based phrase verification**,  
- **metric-learning / prototypical embedding approaches for low-resource personalization**, or  
- **on-device / post-deployment domain adaptation** if the product eventually wants per-home or per-user adaptation. **Confidence: medium.** citeturn40search0turn9search3turn29search0turn35view0turn39search0

If privacy and consent permit later product work, the most compelling deployable research direction is a **generic speaker-independent gate + optional post-deployment adaptation** for device/domain noise, not immediate per-user threshold tuning. Recent embedded work reports double-digit gains from on-device self-learning or domain adaptation, but that is better framed as a future track than as a thesis-critical fix. **Confidence: medium.** citeturn35view0turn39search0

## Suggested thesis wording if the conclusion is data-limited

The following formulation is academically defensible:

> *The remaining weakness of the Kratt detector appears to be primarily a speaker-generalization problem rather than a label-purity problem. After contaminated positives were removed, ambient false accepts could be reduced substantially through more conservative checkpoint selection, but this improvement came with a marked drop in unseen real-speaker recall, especially on the Friend1 evaluation set. Public wake-word and low-resource KWS literature suggests that such behavior is consistent with insufficient real-speaker diversity, synthetic-to-real mismatch, and overly conservative operating-point selection. In particular, recent studies show that speaker diversity in the positive class is more important than repeated utterances from a small number of speakers, and that large volumes of synthetic speech can still induce domain-specific shortcut learning unless combined with diverse real audio, realistic augmentation, or explicit mitigation techniques. Therefore, the most plausible explanation for the remaining error is that the project has reached the limit of what can be achieved with the current small real-speaker pool and current synthetic methodology within a single tiny-device binary-classification setup.*  

That wording is well supported by the public evidence on speaker diversity, TTS overfitting, and multi-stage wake-word design. **Confidence: high.** citeturn25view0turn24view0turn26view6turn11view2turn37view0

## Suggested v19 experiment design if a fix seems plausible

**Hypothesis:** unseen-speaker recall can improve **without** giving up low false accepts if Kratt is turned into a **recall-first gate + exact-phrase verifier** rather than a single all-purpose classifier. **Confidence: medium-high.** citeturn11view2turn37view0turn29search2

**Design**

| Component | Proposal |
|---|---|
| Main change | Keep a tiny high-recall first-stage Kratt detector on ESP32, but move phrase-selective verification to the Raspberry Pi / Home Assistant side |
| Stage 1 target | Maximize recall on clean + augmented `kuule/kule kratt`; require only moderate background FAPH |
| Stage 2 target | Reject prefix-only, reversed-order, and confusable triggers while preserving Stage 1 true positives |
| Positives for Stage 2 | strict `kuule kratt` and `kule kratt`; real speaker clips prioritized; TTS only as augmentation |
| Negatives for Stage 2 | `kuule`, `kratt`, `kratt kuule`, `kuule/kule <not kratt>`, grapheme-edited confusables, real conversational hard negatives |
| Model family | tiny CTC verifier, tiny phoneme/token alignment scorer, or embedding-alignment verifier |
| What not to do | do not train on final held-out user-test audio unless consent and explicit dev/test split exist |

**Training protocol**

- Use the current best *high-recall* first-stage model, not the best ambient-FAPH model.
- For Stage 2, train on candidate windows only.
- Keep hard-negative ratios bounded. Start with a balanced or mildly negative-skewed mix, not an aggressive negative overweighting pass.
- Select checkpoints by a constrained rule:
  - Friend1 recall floor,
  - prefix-only FPR floor,
  - `kuule/kule <confusable>` FPR floor,
  - then ambient FAPH.

**Evaluation**

Report all of the following, with 95% binomial confidence intervals for recall/FPR percentages where sample counts are known:

- Stage 1 recall and FAPH,
- Stage 2 conditional recall,
- end-to-end recall,
- end-to-end FAPH,
- end-to-end hard-negative FPR by subgroup,
- per-speaker recall,
- pooled recall.

Also report **A/B vs v16c** and **A/B vs current best combo**, not only absolute values. That is important because AB/BA-style relative evaluation is deliberately designed for KWS settings where privacy and rare false positives make evaluation difficult. **Confidence: high.** citeturn38view0

**Success criterion for v19**

I would call v19 successful if it achieves all three:

1. Friend1 recall materially above the current 40% combo failure case and ideally near or above `v16c`,  
2. clear reduction in `kuule/kule <confusable>` FPR relative to `v16c`,  
3. acceptable ambient FAPH even if not as extreme as `checkpoint-faph20`.  

That is the right trade to optimize for the thesis. A near-zero ambient FAPH model with unusable unseen-speaker recall is not a better wake-word detector for your problem.

## Bibliography with DOIs and source links

- Apple. *Personalized Hey Siri* (official research article, 2018). citeturn11view3  
- Apple. *Voice Trigger System for Siri* (official research article, 2023). citeturn11view2  
- Bezzam, Scheibler, Cadoux, Gisselbrecht. *A study on more realistic room simulation for far-field keyword spotting* (APSIPA 2020). arXiv:2006.02774. citeturn31search0  
- Ghosh et al. *Low-resource Low-footprint Wake-word Detection using Knowledge Distillation* (Interspeech 2022). DOI: **10.21437/Interspeech.2022-529**. citeturn19view7turn20view2  
- Higuchi, Gupta, Dhir. *Multi-task Learning with Cross Attention for Keyword Spotting* (2021). arXiv:2107.07634. citeturn40search0turn40search2  
- Hou et al. *Mining Effective Negative Training Samples for Keyword Spotting* (ICASSP 2020). PDF source. citeturn33view0turn34view1  
- Lee, Baek. *Keyword Spotting with Synthetic Data using Heterogeneous Knowledge Distillation* (Interspeech 2022). DOI: **10.21437/Interspeech.2022-47**. citeturn19view5turn20view0  
- Lin et al. *Training Keyword Spotters with Limited and Synthesized Speech Data* (ICASSP 2020). DOI: **10.1109/ICASSP40776.2020.9053193**; arXiv:2002.01322. citeturn17search1turn21view0  
- Mazumder et al. *Few-Shot Keyword Spotting in Any Language* (2021). arXiv:2104.01454. Uses multilingual Common Voice data from entity["organization","Mozilla","foundation"]. citeturn22view0turn22view2  
- openWakeWord project documentation and repository (official docs / repo). citeturn14view1turn14view2turn26view4  
- Park et al. *Adversarial training of Keyword Spotting to Minimize TTS Data Overfitting* (2024). arXiv:2408.10463; workshop DOI: **10.21437/SynData4GenAI.2024-18**. citeturn24view0turn24view2  
- Park et al. *Utilizing TTS Synthesized Data for Efficient Development of Keyword Spotting Model* (2024). arXiv:2407.18879. citeturn24view3turn25view0  
- Petegrosso et al. *AB/BA analysis: A framework for estimating keyword spotting recall improvement while maintaining audio privacy* (NAACL 2022). DOI: **10.18653/v1/2022.naacl-industry.4**. citeturn38view0  
- Raju et al. *Data Augmentation for Robust Keyword Spotting under Playback Interference* (2018). arXiv:1808.00563. citeturn30search0turn30search3  
- Rikhye et al. *Personalized Keyphrase Detection using Speaker and Environment Information* (2021). arXiv:2104.13970. citeturn29search2  
- Rusci et al. *Self-Learning for Personalized Keyword Spotting on Ultra-Low-Power Audio Sensors* (2024). arXiv:2408.12481. citeturn35view0turn36view0  
- Rybakov et al. *Streaming Keyword Spotting on Mobile Devices* (2020). arXiv:2005.06720. citeturn28search0  
- Sainath, Parada. *Convolutional Neural Networks for Small-footprint Keyword Spotting* (Interspeech 2015). DOI: **10.21437/Interspeech.2015-248**. citeturn40search15  
- Werchniak et al. *Exploring the application of synthetic audio in training keyword spotters* (ICASSP 2021). DOI: **10.1109/ICASSP39728.2021.9413448**. citeturn19view4  
- Wu et al. *Monophone-based Background Modeling for Two-stage On-device Wake Word Detection* (ICASSP 2018). DOI: **10.1109/ICASSP.2018.8462227**. citeturn37view0  
- Zhang et al. *GraphemeAug: A Systematic Approach to Synthesized Hard Negative Keyword Spotting Examples* (Interspeech 2025). DOI: **10.21437/Interspeech.2025-1038**; arXiv:2505.14814. citeturn32search0turn20view1  
- Zhu et al. *Synth4Kws: Synthesized Speech for User Defined Keyword Spotting in Low Resource Environments* (2024). DOI: **10.21437/SynData4GenAI.2024-3**; arXiv:2407.16840. citeturn19view3turn23view0