# TTS and Synthetic Data for the Kratt Estonian Wake-Word Thesis

## Executive summary

- The strongest overall conclusion is that TTS-generated speech is best treated as a **bootstrapping and controlled-variation tool**, not as a substitute for real held-out speaker evidence in wake-word or keyword-spotting research. Across KWS and adjacent speech literature, synthetic data can reduce data-collection cost and improve some metrics, but the benefit is highly mixture-dependent and does not erase the synth-to-real gap. citeturn9view6turn10view2turn13view0turn15view0turn30view0

- There is **no universal synthetic:real ratio** recommended by the literature. Reported “good” mixtures vary by task, model, and evaluation protocol: one industrial wake-word paper found the best result around **75% synthetic / 25% real** in its setup; Synth4Kws found gains from added TTS but also a clear peak after which more TTS hurt; recent African-language ASR work found improvements around **1:1** or **1:2 real:synthetic**, depending on language and test set. citeturn10view2turn13view0turn30view0

- The most direct KWS evidence for **TTS artifact overfitting** is now quite strong: Park et al. trained a synthetic/real discriminator on KWS hidden features and reached **up to 98%** discrimination accuracy, then showed that adversarially suppressing those features improved real-speech KWS by **up to 12%**. That is a direct demonstration that KWS models can learn “syntheticness” rather than only wake-phrase acoustics. citeturn16view2turn15view0

- For low-resource settings, what matters more than raw synthetic volume is usually **anchoring with at least some real data** and **maximizing diversity** in the synthetic data. Several studies suggest that **speaker diversity** and **phrase diversity** matter more than simply generating many near-duplicate utterances. citeturn13view0turn41view3turn26view0turn31view0

- Synthetic hard negatives can help, especially for **confusable phrases**, but the literature shows that these gains are often clearest on **confusable-focused metrics** or synthetic hard-negative sets, not necessarily on open-ended real-world streaming evaluation. That fits your Kratt observation that some clip-level or curated-set gains were misleading. citeturn11view8turn7search6turn11view10turn15view0

- The wake-word literature supports your concern that **clean labels are necessary but not sufficient**. Even with correct positive labels, permissive phrase-level models can still confuse similar pronunciations or partial forms. The papers that do best on confusables increasingly use **phoneme-level**, **sequence-aware**, or **alignment-aware** objectives rather than relying only on coarse binary matching. citeturn36view2turn38view2turn37view0turn38view1

- For **multi-speaker TTS** and **voice diversity**, the evidence is favorable in principle: multi-speaker synthetic data often beats single-speaker synthetic data, and recent ASR work suggests that adding **new speaker timbres/prosodies** can matter more than merely regenerating the same speakers. But I did **not** find a strong, controlled **multi-engine TTS ablation specifically for KWS**; the clearest engine-comparison evidence I found was in adjacent ASR literature, not wake-word papers. citeturn26view0turn31view0turn20search0turn28view0

- **Voice cloning is useful but risky.** It can expand speaker/style coverage and is already being explored for zero-shot or personalized KWS, but cloned speech is still often highly distinguishable from real speech and can import the wrong prosody, lexical tails, or prompt contamination if generation is not tightly validated. citeturn21view0turn22view0turn15view0

- For your thesis, the safest framing is: **Kratt demonstrates a low-resource Estonian wake-word prototype and a careful evaluation methodology**, and your experiments show both the utility **and** the danger of TTS. The literature supports that framing well. What it does **not** support is any claim that good synthetic-data performance alone implies production readiness or robust unseen-speaker generalization. citeturn15view0turn17search2turn30view0

- The highest-value thesis move is probably **not** another broad TTS-training sweep before submission. The higher-value contribution is to present Kratt as a rigorous case study showing how TTS can help bootstrap Estonian wake-word training, how it can fail through artifact overfitting and label impurity, and why final conclusions must be based on **held-out real-speaker streaming evaluation**, not only clip-level or synthetic-set metrics. citeturn15view0turn13view0turn35view0turn40view2

## Literature map

| Source | Year | Type | What it studied | Key result | Relevance to Kratt | Confidence / caveats |
|---|---:|---|---|---|---|---|
| **Training Keyword Spotters with Limited and Synthesized Speech Data** citeturn9view6turn42search8 | 2020 | Peer-reviewed paper | Custom KWS with synthetic training and pre-trained speech embeddings | Synthetic-only training, when paired with strong embeddings, matched a model trained on **500+ real examples**; without embeddings it needed **4000+** real examples | Good support for “TTS can bootstrap data-poor KWS” | Early custom-KWS setting; not streaming wake-word field eval |
| **Exploring the Application of Synthetic Audio in Training Keyword Spotters** citeturn10view0turn10view2turn42search6 | 2021 | Peer-reviewed paper | Industrial wake-word training with TTS mixed with human data | Careful mixing of TTS with human speech reduced DET AUC by **>11%**; in that setup, the best mixture used substantial real anchoring and pure synthetic underperformed | Directly relevant to wake-word training mixture strategy | Industrial/private data; English; one wake word |
| **Training Wake Word Detection with Synthesized Speech Data on Confusion Words** citeturn11view8 | 2020 | arXiv / preprint | Multi-speaker TTS augmentation for confusing-word wake-word cases | Multi-speaker TTS improved robustness, especially on confusing-word scenarios | Strongly relevant to your hard-negative question | Preprint; result is about confusable scenario, not broad real-world eval |
| **Leveraging Synthetic Speech for CIF-Based Customized Keyword Spotting** citeturn6search0 | 2023 | Peer-reviewed conference chapter | Customized KWS trained with synthetic speech | Shows synthetic speech can assist customized KWS in a newer matching architecture | Supports thesis claim that TTS is already an active KWS research direction | Less cited; limited public detail in my review |
| **Synth4Kws** citeturn13view0 | 2024 | Workshop paper / arXiv | Systematic study of TTS in custom KWS under no-real/low-real settings | More phrase diversity and more sampling helped in no-real settings; with **50k real** utterances, optimal TTS improved EER by **30.1%** and AUC by **48.7%**, but too much TTS later hurt | One of the best sources for ratio/sampling strategy | English, single-word utterances; authors say generalization beyond that is plausible, but that remains an extrapolation |
| **Utilizing TTS Synthesized Data for Efficient Development of Keyword Spotting Model** citeturn9view0turn41view3 | 2024 | arXiv / preprint | Large-scale KWS with abundant TTS plus very small real anchor sets | About **100 speakers / 2k utterances** of real positives plus large TTS reached roughly **3× baseline FRR**; speaker diversity mattered more than more utterances per speaker | Very useful for framing “small real anchor + large TTS” | Still far from baseline; industrial/private setup |
| **Adversarial Training of Keyword Spotting to Minimize TTS Data Overfitting** citeturn15view0turn16view2 | 2024 | Workshop paper / arXiv | Domain-adversarial KWS to suppress TTS-specific artifacts | Synthetic/real discriminator reached **up to 98%**; adversarial training improved real-speech KWS by **up to 12%** | Best direct evidence for TTS artifact overfitting in KWS | Workshop/preprint; still one family of models/datasets |
| **MM-KWS** citeturn37view2turn38view1 | 2024 | Peer-reviewed paper | Multilingual user-defined KWS with hard-case mining | Confusable-keyword generation improved AUC/EER in ablations | Supports the need to model confusables explicitly | User-defined KWS, not closed fixed wake-word deployment |
| **PhonMatchNet** citeturn37view3 | 2023 | Peer-reviewed paper | Phoneme-guided zero-shot KWS | Phoneme-level modeling substantially improved similar-pronunciation cases | Strong support for your “sequence/phonetic order matters” interpretation | Zero-shot/open-vocabulary setting |
| **GraphemeAug** citeturn7search6 | 2025 | Peer-reviewed Interspeech paper | Systematic synthesized hard negatives via grapheme edits | Improved AUC on synthetic hard-negative sets by **61%** while maintaining positive and ambient negative quality | Very relevant to synthetic confusables and edit-distance generation | Main gain shown on synthetic hard-negative evaluation, not full field deployment |
| **LLM-Synth4KWS** citeturn11view10turn11view11 | 2025 | Peer-reviewed Interspeech paper | LLM-generated confusables plus TTS synthesis for custom KWS | Global AUC improved **3.7%**, but confusable-group c-AUC improved **11.3%** and LibriPhrase hard-negative AUC **12.5%** | Excellent support for separate confusable metrics | Improvement on overall metric was modest; not wake-word streaming on-device |
| **Personalized Speech Synthesis for Zero-Shot Keyword Spotting** citeturn21view0 | 2025 | Peer-reviewed conference paper | Personalized synthetic speech to adapt KWS to unseen words for known speakers | Synthetic speech improved KWS adaptability to new vocabularies | Relevant to voice cloning/personalization | Early evidence; limited public ablation detail |
| **Evaluating and Reducing the Distance Between Synthetic and Real Speech Distributions** citeturn17search2turn17search5 | 2023 | Peer-reviewed paper | Measured synth-to-real distribution gap with utterance statistics and Wasserstein distance | Synthetic speech still differed from real speech across speaker, prosody, and acoustic-environment dimensions; controlled conditioning reduced but did not remove the gap | Best adjacent evidence for why synthetic scores can mislead | ASR-focused, not KWS-specific |
| **Synt++** citeturn18search0turn18search6 | 2022 | Peer-reviewed paper | Synthetic-data mismatch mitigation for speech recognition and keyword detection | Artifact-containing and unevenly sampled synthetic data harms generalization; rejection sampling and separate batch normalization improved downstream performance | Useful for mitigation framing and “artifact regions” language | Not wake-word-specific |
| **An Exhaustive Evaluation of TTS- and VC-based Data Augmentation for ASR** citeturn28view0turn29view3turn29view4 | 2025 | arXiv / preprint | Which synthetic attributes actually help downstream speech models | Noise/reverb matching helped more than pitch augmentation; VC-based speaker augmentation was ineffective in that setup; adding more speakers had diminishing returns | Strong adjacent evidence for mitigation strategy choices | ASR, not KWS |
| **Synthetic Voice Data for ASR in African Languages** citeturn30view0 | 2025 | Workshop paper | Large-scale synthetic low-resource ASR for African languages | Best ratios varied by language and evaluation set; synthetic data helped, but effects were not uniform | Good low-resource-language evidence for conservative framing | ASR rather than wake-word detection |
| **SpeechQM-Agent** citeturn34view0turn35view1 | 2026 | Preprint / benchmark paper | Automated speech-data quality verification | Highlights practical checks: transcript normalization/tag removal, transcript-audio alignment, CTC score, WER checks, VAD, sample-rate checks | Very useful for label-purity and audit methodology | Not KWS-specific; recent and not yet mature |

## Detailed synthesis

### Synthetic positives

The literature is consistent on one narrow but important point: **synthetic positives can be genuinely useful when real positive data is scarce**, particularly early in development. Lin et al. showed that synthetic-only data was surprisingly competitive in custom KWS when paired with a strong pre-trained embedding model, and Werchniak et al. showed that a careful human+TTS mixture improved an industrial wake-word system. Synth4Kws pushes this further: in no-real settings, more phrase diversity and more utterance sampling improved performance monotonically, while in low-real settings an appropriate TTS mixture strongly improved EER/AUC over the real-only low-resource baseline. citeturn9view6turn10view2turn13view0

What the same literature says, however, is just as important: **synthetic positives are not equivalent to real positives**. In both Synth4Kws and the 2024 industrial preprint on efficient KWS development, performance improved with additional real data, and in Synth4Kws the benefit of more TTS eventually peaked and then reversed. The low-resource African-language ASR study reached the same qualitative conclusion: the useful ratio varied by language and evaluation set, which means the “right amount” of synthetic data is **empirical, not universal**. citeturn13view0turn41view3turn30view0

For Kratt, that means your current interpretation is scientifically defensible: **TTS positives are reasonable as a low-resource Estonian bootstrap mechanism**, especially because there is no large public wake-word corpus for “Kuule Kratt.” But the literature does **not** support treating TTS-positive gains as proof of generalization to unseen real Estonian speakers. The safest reading is that TTS expands coverage of lexical/prosodic variants and reduces data-collection burden, while real speech remains the anchor for validity. citeturn13view0turn15view0turn30view0

Your `expert-a` versus `ex2a` observation fits this pattern well. The literature does not give a paper that exactly reproduces your “mic-dominant gatekeeper worsened by broad TTS positives” result, but it does show the two ingredients needed for that interpretation: first, KWS systems can exploit TTS-specific cues; second, mixture proportions matter enough that “more TTS” is not monotonic progress. So your thesis can cautiously state that Kratt’s results are **consistent with** synthetic-positive over-weighting or over-representation of synthetic prosody/artifacts in the positive class. citeturn15view0turn13view0

### Synthetic hard negatives

The literature is more favorable to synthetic hard negatives than to synthetic positives, but with an important nuance. The clearest direct wake-word paper here is the 2020 confusion-words study, which found that **multi-speaker TTS of confusing words** improved robustness in confusing-word scenarios. More recent work makes this more systematic: GraphemeAug generates confusables by insertion, deletion, and substitution edits, while LLM-Synth4KWS uses LLM-generated confusable keyword groups plus TTS to improve not just overall AUC modestly, but confusable-group metrics much more strongly. citeturn11view8turn7search6turn11view10

That nuance is the key point for Kratt. The modern confusable-augmentation papers often report their biggest gains on **confusable-specific metrics** such as c-AUC or synthetic hard-negative AUC, not necessarily on broad real-world field metrics. LLM-Synth4KWS is a good example: the overall AUC gain was **3.7%**, while the confusable-group metric improved **11.3%**. This is exactly the kind of pattern that explains why your v5/v6 clip-level results could look promising while later streaming evaluation told a more conservative story. citeturn11view10turn11view11turn15view0

The strongest synthesis for the thesis is therefore:

1. synthetic confusables can absolutely help train **exact phrase selectivity**, and  
2. the resulting gains must be kept separate from claims about **ambient false accepts** and **unseen-speaker recall**.

That is, synthetic hard negatives are scientifically useful, but best treated as a targeted intervention for the decision boundary, not a blanket guarantee of field robustness. citeturn11view8turn7search6turn11view10

A second useful point comes from older wake-word work on **lexicon-based confusing-example mining**. Gao et al. reported that for a six-phoneme wake word, Levenshtein-distance thresholds of **1 or 2** produced sufficient negative examples for confusing-case augmentation. Together with GraphemeAug, this gives you a strong literature-backed recipe for generating candidate Estonian confusables: start from edit-distance mutations in graphemes and phoneme strings, then manually prune to linguistically plausible, acoustically dangerous phrases such as word-order flips, prefix-only fragments, and near-minimal-pair substitutions. citeturn36view1turn7search6

The literature is much thinner on one of your most interesting findings: that **real hard negatives** may teach phonetic selectivity better than pure TTS hard negatives. I did not find a strong published wake-word paper directly comparing large synthetic hard-negative pools against matched real-spoken hard negatives under the same architecture and evaluation. That absence is worth stating plainly in the thesis. It lets you frame your v8 result as a **project-specific empirical contribution**, not an overclaimed literature consensus.

### Voice cloning and multi-speaker TTS

The evidence for **multi-speaker synthetic data** is stronger than the evidence for **voice cloning specifically**. Older ASR augmentation work from Ueno et al. found that multi-speaker TTS improved over both a real-only baseline and a single-speaker synthetic baseline, which supports a simple and relevant principle: **voice diversity is a real asset, not just extra sample count**. The 2024 industrial KWS preprint reaches a closely related conclusion more directly for KWS: speaker diversity in the small real anchor set mattered more than simply adding more utterances per speaker. citeturn26view0turn41view3

Recent adjacent ASR work pushes this even further. In code-switching ASR, random-speaker TTS augmentation beat same-speaker TTS regeneration, and the authors explicitly interpreted the gain as coming from **new timbres and prosodies** rather than raw synthetic volume. That is not wake-word evidence, but it is a strong, recent signal that, when synthetic data helps, **diversity of voices can matter more than the total number of generated clips**. citeturn31view0

Voice cloning is more mixed. Personalized Speech Synthesis for Zero-Shot KWS is encouraging: it shows synthetic speech can help adapt KWS to unseen words for known speakers. But the XTTS-based profanity-recognition paper also found that its models could distinguish real from synthetic speech with **97–99%** accuracy, which means cloned or XTTS-generated audio can remain acoustically separable from real data even when it is useful for augmentation. Park et al.’s adversarial-overfitting paper reinforces the same concern inside KWS proper. citeturn21view0turn22view0turn15view0

So the safest thesis position is:

- **multi-speaker TTS is evidence-backed and useful**,  
- **voice cloning is plausible and potentially helpful**, especially for targeted speaker/style diversification,  
- but **voice-cloned positives are risky** unless transcript integrity and phrase isolation are aggressively audited, because the cloned data may still live in a synthetic sub-domain that the model can detect. citeturn21view0turn22view0turn16view2

I did **not** find a clean KWS paper that compares multiple TTS engines while holding text prompts, negative sets, and evaluation fixed. The clearest controlled “which TTS generator is best for downstream use?” study I found was in ASR, where Rossenbach et al. showed that different TTS decoders produce materially different downstream value and that standard MOS/intelligibility metrics do not predict that value well. For Kratt, that means “use more TTS engines” is a defensible future-work hypothesis, but **not yet a literature-backed prescription for KWS**. citeturn20search0turn20search4turn13view0turn15view0

### Synth-to-real gap and artifact overfitting

This is the strongest section of the literature for your thesis question. Park et al. give direct KWS evidence that hidden representations in a wake-word model encode enough information to distinguish synthetic from real audio with near-perfect accuracy, and that reducing that domain signal improves real-speech performance. In other words, the phrase “the model may be learning TTS artifacts” is no longer just intuition; there is now direct experimental support for it in KWS. citeturn16view2turn15view0

Adjacent ASR research helps explain why. Minixhofer et al. explicitly measured distance between synthetic and real speech distributions across speaker, prosody, and acoustic-environment dimensions. Hu et al. frame the problem in terms of **artifact regions**, **missing regions**, and **sampling bias** in the synthetic distribution. That language is very useful for Kratt, because it lets you go beyond “synthetic sounds different” and say something more precise: synthetic data may both invent acoustic regularities that do not occur in field recordings and fail to cover real variations that matter for unseen users. citeturn17search2turn18search0

This literature strongly supports your current thesis interpretation of the v5/v6 and `expert-a` / `ex2a` results. The conservative, evidence-backed claim is not that TTS is “bad,” but that **some measured improvements can be partly explained by better optimization inside the synthetic/curated domain rather than better generalization to real held-out speakers**. That is exactly why your thesis should keep clip-level synthetic or semi-synthetic metrics clearly separate from real-speaker streaming evaluation. citeturn15view0turn17search2

This is also where your v7 result becomes interpretable. The literature does not directly prove that “too many TTS hard negatives plus SpecAugment makes a small model too conservative,” because that exact ablation has not been cleanly published for wake-word detection. But it does show that models can overfit domain cues, that additional synthetic data can overshadow real information, and that not all diversity knobs actually help downstream recognition. So your “too conservative after hard-negative expansion” interpretation is a reasonable project-specific inference, especially for a small embedded model. citeturn13view0turn28view0turn29view4

### Label purity and segmentation

Here the literature is thinner on the exact Kratt failure mode, and it is important to say so explicitly. I did **not** find a paper directly about KWS positives being corrupted because **SSML tags were spoken aloud**, or because a TTS/clone positive accidentally included **command tails** beyond the wake phrase. That exact phenomenon is very plausible, and your v17 evidence is compelling, but it is primarily **supported by your project’s audit**, not by a mature published KWS literature.

What the literature does support very well is the broader principle that **speech-data quality control needs transcript normalization, transcript-audio alignment checks, and automated content validation**, especially in multilingual or low-resource settings. SpeechQM-Agent is directly useful here because its quality-control menu includes exactly the kinds of checks you wish you had applied earlier: transcript normalization and tag removal, transcript-audio alignment, CTC score checks, WER computation, and VAD-backed duration/silence checks. Recent multilingual dataset audits also show that content- and alignment-level quality issues are common enough to distort downstream evaluation and training. citeturn35view0turn35view1turn33search6

This gives you a clean thesis framing:

- **manual listening audits were necessary and justified**,  
- **exact-phrase filtering was a scientifically sound corrective step**, and  
- future pipelines should treat synthetic positives as needing the **same or stricter QC** as real recordings, not weaker QC.

That is a robust claim even though the exact failure mode is project-specific. citeturn35view0turn33search6

For recommended practice, the literature supports a **multi-stage audit** rather than a single heuristic filter: transcript normalization to strip markup, duration and VAD checks to exclude clips that are too short or mostly silence, forced-alignment or CTC-based transcript-audio agreement checks, ASR/WER validation for gross lexical mismatch, and manual listening on a sampled subset plus all automatically flagged outliers. citeturn35view0turn35view1

Your v18 result is also theoretically meaningful. It shows that **label purity fixed one real failure mode**, but did not fully solve wake-phrase selectivity. That is consistent with the confusable/phoneme-aware literature: even perfectly clean “positive” labels do not, by themselves, force a binary classifier to learn full phrase order and exact lexical boundaries. The model may still fire on prefix-like acoustics unless the task formulation or negative set makes those alternatives explicit. That is an inference, but a well-supported one. citeturn38view2turn37view0turn38view1turn36view2

### Mitigation strategies

The mitigation strategy with the clearest direct KWS support is **domain-adversarial training**. Park et al. show that a synthetic/real discriminator plus gradient reversal can reduce TTS overfitting and recover real-speech accuracy. For your thesis, this is the best citation if you want to say that the literature does not only identify the synthetic-artifact problem; it also proposes a principled mitigation. citeturn15view0turn16view2

The next-best supported mitigation is **real-data anchoring**. Across KWS and adjacent low-resource speech studies, synthetic speech works best as a complement to real anchors, not as a substitute. That is true in Synth4Kws, in the industrial KWS mixing studies, in the African-language ASR paper, and in the 2026 code-switching study where synthetic-only underperformed while mixed real+synthetic training helped. citeturn13view0turn10view2turn30view0turn31view0

After that, the strongest evidence is for **careful diversity design**, not indiscriminate augmentation. Phrase diversity, speaker diversity, confusable generation, and acoustic-environment matching all help under some conditions. But not every diversity knob helps equally. Ogun et al. found that **noise/reverb matching** helped much more consistently than **pitch augmentation**, and VC-based speaker augmentation was ineffective in their setup. That finding supports a conservative recommendation for Kratt: treat standard augmentation as **supportive regularization**, not as your main answer to synth-to-real mismatch. citeturn28view0turn29view4turn29view5

The literature is much weaker on **style transfer**, **speaker embedding interpolation**, and **voice mixing** specifically for KWS. There are promising ideas in adjacent speech work, and newer papers suggest creating synthetic speaker identities can help downstream tasks, but I did not find a wake-word paper that cleanly demonstrates those methods on a streaming small-footprint detector. That absence is itself useful thesis framing: it justifies why your thesis should emphasize conservative evaluation over speculative claims about sophisticated synthetic generation.

Finally, your proposed separation between **TTS-generated diagnostics** and **final held-out real-speaker evaluation** is strongly supported. LLM-Synth4KWS explicitly introduces confusable-group metrics because standard global metrics miss those cases; Park et al. use fixed false-accept-rate operating points on real speech; and synth-to-real-gap work emphasizes that distribution matching remains incomplete. The thesis can therefore defend a **two-layer evaluation protocol**: targeted synthetic/diagnostic tests for boundary analysis, and real-speaker streaming tests for any deployment-relevant claim. citeturn11view10turn15view0turn17search2

### Implications for embedded microWakeWord and ESP32 deployment

For an on-device system based on microWakeWord, your conservative framing becomes even more important because you are operating inside a small-footprint, threshold-sensitive regime. The official microWakeWord training/docs describe a two-stage process in which audio is converted into **40 spectrogram features every 10 ms**, and wake detection depends on a model probability and a smoothing window over multiple frames. ESPHome further exposes explicit settings for **probability cutoff**, **sliding window size**, and optional **VAD**, all of which trade false accepts against false rejects. citeturn40view0turn40view2

That matters for Kratt because your v7/v8 behavior is exactly what one would expect when a small embedded detector becomes too conservative or too permissive around a narrow phrase boundary. With these models, dataset composition and threshold calibration interact very strongly. So for a BSc thesis at entity["organization","TallTech","university in estonia"], it is scientifically safer to argue that Kratt evaluates a **prototype detector under realistic embedded constraints** for an entity["organization","Home Assistant","open source home automation"] voice-satellite context, rather than claiming to have solved general Estonian wake-word detection. citeturn40view0turn40view2turn40view3

The official project ecosystem also reinforces your privacy-first positioning. The entity["organization","Open Home Foundation","nonprofit smart home org"] documentation explicitly frames microWakeWord as a lightweight on-device alternative to server-side wake-word engines on low-power devices such as ESP32-S3-class hardware. That aligns well with Kratt’s scope: an Estonian wake-word prototype that prioritizes on-device activation, careful threshold trade-offs, and conservative claims about field readiness. citeturn40view3turn40view1

What this means in practice is that any thesis conclusion about “success” should be tied to **real streaming operating points** such as false accepts per hour, missed detections, and exact-phrase confusables, not only clip-level AUC or closed-set synthetic tests. That recommendation follows both from the wake-word literature and from the engineering realities of microWakeWord-style detectors. citeturn15view0turn40view2

## How this changes the Kratt thesis

### Safe claims

These claims are well supported by the literature and fit your project evidence.

- **TTS can be useful for low-resource wake-word bootstrapping**, especially when real positive data is scarce and controlled lexical/prosodic variation is needed. citeturn9view6turn10view2turn13view0
- **TTS is not equivalent to real unseen-speaker evidence**; synth-to-real mismatch and artifact overfitting remain real risks. citeturn15view0turn17search2turn18search0
- **The effect of synthetic data depends on the mixture with real data**, on speaker/phrase diversity, and on evaluation protocol. citeturn13view0turn41view3turn30view0
- **Synthetic hard negatives can improve confusable-phrase discrimination**, but their benefit should be validated separately from ambient or field robustness. citeturn11view8turn7search6turn11view10
- **Strict positive-label purity is essential**, yet exact wake-phrase selectivity may still require explicit confusable negatives or more sequence-aware objectives. citeturn35view0turn38view2turn37view0turn36view2
- **Kratt’s main contribution is a low-resource Estonian wake-word prototype and a defensible evaluation methodology for on-device deployment**, not a production-ready voice assistant. This is supported by your project evidence and consistent with the literature’s caution about synthetic data.

### Unsafe claims

These are not safely supported by the literature you need for a BSc thesis.

- “Adding TTS improved the model, therefore the detector generalizes to real unseen Estonian speakers.”
- “Voice cloning solves the low-resource problem.”
- “Cleaning positive labels is enough to guarantee exact phrase matching.”
- “Clip-level validation is sufficient evidence for deployment readiness.”
- “Synthetic hard negatives necessarily improve wake-word selectivity without harming recall.”
- “Kratt is production-grade” unless you later add strong real-user field evidence.

### Recommended final wording in Estonian

You asked for thesis-ready Estonian wording. The versions below are deliberately conservative.

**Variant for the main conclusion**

> Käesolev töö näitab, et sünteetiline TTS-kõne võib olla vähese ressursiga eestikeelse äratusfraasi tuvastuse arenduses kasulik andmete algkäivitamiseks ja kontrollitud varieeruvuse lisamiseks. Samas ei ole sünteetiline kõne võrdne reaalse, nähtamatute kõnelejate kõnega: kirjanduse ja käesoleva töö tulemused viitavad, et sünteetilise ja reaalse domeeni erinevus võib põhjustada eksitavalt häid vahetulemusi ning nõrgemat üldistumist reaalses kasutuses. Seetõttu käsitleb töö TTS-andmeid abistava, mitte asendava andmeallikana.

This wording is supported by the literature. citeturn13view0turn15view0turn17search2

**Variant for the Kratt-specific interpretation**

> Kratt demonstreerib eestikeelse äratusfraasi „Kuule Kratt“ / „Kule Kratt“ madala ressursiga prototüüpi ning selle hindamise metoodikat mikrojuhtseadmel töötava äratussõna tuvastaja kontekstis. Töö tulemuste põhjal aitas TTS osa andmestikust laiendada, kuid ei olnud piisav reaalse kõnelejateülese üldistumise tagamiseks. Eraldi ilmnes, et siltide puhtus on kriitiline ning binaarne märksõnatuvastus võib ilma segiaetavate negatiivsete näideteta õppida liiga lubavaid foneetilisi lühiteid.

The first sentence is supported by your project evidence; the rest is consistent with literature on TTS mismatch, QC, and confusable modeling. citeturn15view0turn35view0turn38view2turn37view0

### Recommended limitation and future-work wording in Estonian

> Töö piirang on see, et sünteetilise kõne kasu sõltus tugevalt selle genereerimise viisist, siltide kvaliteedist ning sünteetilise ja reaalse kõne vahekorrast. Käesolev töö ei näita, et TTS-andmetel saavutatud paranemine kanduks automaatselt üle nähtamatutele päriskõnelejatele. Edasine töö peaks uurima fonoloogiliselt motiveeritud raskete negatiivsete näidete koostamist, sünteetilise ja reaalse domeeni erinevust vähendavaid treeningvõtteid ning järjestus- või foneemiteadlikke äratussõna mudeleid, mis eristaksid paremini täisfraasi selle prefiksitest ja segiaetavatest väljenditest.

This is a safe limitation/future-work paragraph. citeturn15view0turn11view10turn38view2turn36view2

### Supported by literature, supported by this project, and speculation

**Supported by literature**

- TTS is useful for low-resource bootstrapping and controlled confusable generation. citeturn9view6turn11view8turn13view0
- TTS can create artifact shortcuts that hurt real-speech KWS. citeturn15view0turn18search0
- Speaker/phrase diversity matters, and more TTS is not always better. citeturn13view0turn41view3turn31view0
- Confusable-focused metrics should be separated from broad operating metrics. citeturn11view10turn15view0

**Supported by Kratt’s own evidence**

- Positive-label corruption in v17 taught the wrong target.
- Exact two-word positive filtering in v18 fixed one data-quality issue but did not fully solve selectivity.
- Real or cloned hard negatives appeared more phonetically informative than a large pool of pure TTS hard negatives in your setup.
- Large hard-negative pools could make a small model too conservative.

**Future work / still speculative**

- Multi-engine TTS may outperform single-engine TTS for Estonian wake-word training.
- Domain-adversarial training would materially improve Kratt on unseen speakers.
- Phoneme-sequence objectives would fully solve the prefix-only problem under your current deployment constraints.

Those are plausible hypotheses, but not claims the thesis should present as settled facts.

## Decision guidance

### Should the thesis present TTS as a contribution, a risk, or both?

It should present TTS as **both**, with the balance weighted toward **“useful but dangerous if overinterpreted.”** The literature now clearly supports both sides:

- TTS reduces data collection burden and can improve low-resource KWS training. citeturn9view6turn10view2turn13view0
- TTS can inject artifact shortcuts and mismatched prosody/domain cues, which can degrade real-speech performance. citeturn15view0turn17search2turn18search0

For the thesis, that dual framing is not a weakness. It is actually a stronger scientific contribution, because Kratt becomes a careful case study of **when synthetic data helps and when it misleads**.

### Should the project attempt more TTS-based training before thesis submission, or freeze and treat it as diagnostic evidence?

My recommendation is to **freeze broad training iteration** and treat the existing TTS experiments as **diagnostic evidence** unless you already have one nearly-finished, very small ablation waiting to run. The reason is not that more training would be useless; it is that the literature makes clear the optimum is setup-specific, while your current dataset already contains a thesis-worthy story about bootstrapping, overfitting, label purity, and evaluation mismatch. Another broad TTS sweep is unlikely to strengthen the scientific argument as much as a sharper analysis of what already happened. citeturn13view0turn15view0turn30view0

### What minimal extra analysis would have the highest value without new model training?

If you do anything extra, keep it strictly analytical.

The highest-value additions would be:

- **A compact positive-label audit table**, especially for v17 and v18: counts of exact phrases, prefix-only fragments, command tails, markup leakage, and other corruption classes. This directly supports your label-purity argument.
- **A speaker-stratified evaluation summary** for the main model families: exact target, prefix-only phrases, confusables, and ambient negatives, reported separately for clip-level and streaming evaluation. This would make the “clip metrics were misleading” point much stronger.
- **A threshold-sensitivity appendix** for the best few models, reporting false accepts per hour versus recall on the same held-out real streaming set. Because microWakeWord-style systems are thresholded streaming detectors, this is more deployment-relevant than one headline metric. citeturn15view0turn40view2
- **If transcripts for synthetic positives are still available**, run an automated lexical validation pass to quantify how often the audio actually corresponds to the intended two-word wake phrase. Literature-backed QC tools make this entirely thesis-relevant. citeturn35view0

What I would **not** prioritize before submission is a new large-scale synthetic-data search over engines, ratios, or augmentation knobs. That would cost time, and the thesis value would still depend on the same real-held-out evaluation problem.

### Open questions and limitations

A few things remain genuinely under-evidenced in the published literature and should be acknowledged as such.

- I did **not** find a strong, controlled **multi-TTS-engine ablation specifically for KWS/wake-word detection**.
- I did **not** find a published wake-word paper directly demonstrating the exact positive-label contamination failure modes you saw in v17, such as spoken SSML/XML or command-tail positives.
- I found only limited direct evidence comparing **synthetic hard negatives** against **matched real-spoken hard negatives** in wake-word systems.

Those absences are useful because they let you position parts of Kratt as empirical thesis contributions rather than overclaiming literature consensus.

## Annotated bibliography with BibTeX

Below are the sources I would prioritize in the thesis. I label each one by type and explain exactly why it matters.

**Lin et al. 2020 — peer-reviewed ICASSP.** Best early citation for the proposition that synthetic speech can meaningfully bootstrap custom KWS when little real data is available, especially when feature representations are strong. citeturn9view6turn42search8

**Werchniak et al. 2021 — peer-reviewed ICASSP.** Strong direct wake-word citation for careful real+synthetic mixing and for the point that mixture weighting matters. citeturn10view2turn42search6

**Zhang et al. 2024 — arXiv / industrial preprint.** Useful for the “small real anchor set + lots of TTS” framing and for the finding that speaker diversity matters more than more utterances from the same speaker. citeturn41view3

**Zhu et al. 2024 Synth4Kws — workshop / arXiv.** Best recent systematic study of TTS amount, phrase diversity, and low-resource ratio effects for custom KWS. citeturn13view0

**Park et al. 2024 adversarial overfitting — workshop / arXiv.** Essential citation for direct KWS evidence of synthetic-artifact overfitting and mitigation. citeturn15view0turn16view2

**Zhang et al. 2025 GraphemeAug — peer-reviewed Interspeech.** Best citation for systematic hard-negative generation from grapheme edits. citeturn7search6

**Zhu et al. 2025 LLM-Synth4KWS — peer-reviewed Interspeech.** Best citation for confusable-specific metrics and scalable confusable generation. citeturn11view10turn11view11

**Lee and Cho 2023 PhonMatchNet — peer-reviewed Interspeech.** Strong support for phoneme-level modeling when similar pronunciations matter. citeturn37view3

**Ai et al. 2024 MM-KWS — peer-reviewed Interspeech.** Good complementary citation showing hard-case mining helps confusable discrimination in multilingual user-defined KWS. citeturn37view2turn38view1

**Minixhofer et al. 2023 — peer-reviewed Interspeech.** Best adjacent citation for measuring the synthetic/real distribution gap itself. citeturn17search2turn17search5

**Hu et al. 2022 Synt++ — peer-reviewed ICASSP.** Very useful for the language of artifact regions, sampling bias, and synthetic-data mitigation. citeturn18search0turn18search6

**SpeechQM-Agent 2026 — recent preprint / benchmark.** Best source for a modern transcript/audio QC checklist you can directly adapt into thesis methodology. citeturn35view0turn35view1

```bibtex
@inproceedings{lin2020training,
  title     = {Training Keyword Spotters with Limited and Synthesized Speech Data},
  author    = {Lin, James and Kilgour, Kevin and Roblek, Dominik and Sharifi, Matthew},
  booktitle = {ICASSP 2020 - 2020 IEEE International Conference on Acoustics, Speech and Signal Processing},
  year      = {2020},
  pages     = {7474--7478},
  doi       = {10.1109/ICASSP40776.2020.9053193}
}

@inproceedings{werchniak2021exploring,
  title     = {Exploring the Application of Synthetic Audio in Training Keyword Spotters},
  author    = {Werchniak, Andrew and Barra-Chicote, Roberto and Mishchenko, Yuriy and Droppo, Jasha and Condal, Jeff and Liu, Peng and Shah, Anish},
  booktitle = {ICASSP 2021 - 2021 IEEE International Conference on Acoustics, Speech and Signal Processing},
  year      = {2021},
  pages     = {7993--7996},
  doi       = {10.1109/ICASSP39728.2021.9413448}
}

@inproceedings{ueno2019multispeaker,
  title     = {Multi-speaker Sequence-to-sequence Speech Synthesis for Data Augmentation in Acoustic-to-word Speech Recognition},
  author    = {Ueno, Sei and Mimura, Masato and Sakai, Shinsuke and Kawahara, Tatsuya},
  booktitle = {ICASSP 2019 - 2019 IEEE International Conference on Acoustics, Speech and Signal Processing},
  year      = {2019},
  pages     = {6161--6165},
  doi       = {10.1109/ICASSP.2019.8682816}
}

@article{liu2023selection,
  title   = {Towards Selection of Text-to-speech Data to Augment ASR Training},
  author  = {Liu, Shuo and Sar{\i}, Leda and Wu, Chunyang and Keren, Gil and Shangguan, Yuan and Mahadeokar, Jay and Kalinli, Ozlem},
  journal = {arXiv preprint arXiv:2306.00998},
  year    = {2023}
}

@inproceedings{liu2023cifkws,
  title     = {Leveraging Synthetic Speech for CIF-Based Customized Keyword Spotting},
  author    = {Liu, Shuiyun and Zhang, Ao and Huang, Kaixun and Xie, Lei},
  booktitle = {Man-Machine Speech Communication},
  series    = {CCIS},
  volume    = {2006},
  pages     = {354--365},
  year      = {2024}
}

@inproceedings{zhu2024synth4kws,
  title     = {Synth4Kws: Synthesized Speech for User Defined Keyword Spotting in Low Resource Environments},
  author    = {Zhu, Pai and Agarwal, Dhruuv and Bartel, Jacob W. and Partridge, Kurt and Park, Hyun Jin and Wang, Quan},
  booktitle = {Proc. SynData4GenAI Workshop},
  year      = {2024},
  note      = {Also available as arXiv:2407.16840}
}

@article{park2024efficientkws,
  title   = {Utilizing TTS Synthesized Data for Efficient Development of Keyword Spotting Model},
  author  = {Park, Hyun Jin and others},
  journal = {arXiv preprint arXiv:2407.18879},
  year    = {2024}
}

@article{park2024adversarial,
  title   = {Adversarial Training of Keyword Spotting to Minimize TTS Data Overfitting},
  author  = {Park, Hyun Jin and Agarwal, Dhruuv and Chen, Neng and Sun, Rentao and Partridge, Kurt and Chen, Justin and Zhang, Harry and Zhu, Pai and Bartel, Jacob and Kastner, Kyle and Wang, Gary and Rosenberg, Andrew and Wang, Quan},
  journal = {arXiv preprint arXiv:2408.10463},
  year    = {2024},
  note    = {Workshop paper at SynData4GenAI / Interspeech 2024 satellite}
}

@inproceedings{lee2023phonmatchnet,
  title     = {PhonMatchNet: Phoneme-Guided Zero-Shot Keyword Spotting for User-Defined Keywords},
  author    = {Lee, Yong-Hyeok and Cho, Namhyun},
  booktitle = {Proc. Interspeech 2023},
  year      = {2023},
  doi       = {10.21437/Interspeech.2023-597}
}

@inproceedings{ai2024mmkws,
  title     = {MM-KWS: Multi-modal Prompts for Multilingual User-defined Keyword Spotting},
  author    = {Ai, Zhiqi and Chen, Zhiyong and Xu, Shugong},
  booktitle = {Proc. Interspeech 2024},
  year      = {2024},
  doi       = {10.21437/Interspeech.2024-10}
}

@inproceedings{zhang2025graphemeaug,
  title     = {GraphemeAug: A Systematic Approach to Synthesized Hard Negative Keyword Spotting Examples},
  author    = {Zhang, Harry and Partridge, Kurt and Zhu, Pai and Chen, Neng and Park, Hyun Jin and Agarwal, Dhruuv and Wang, Quan},
  booktitle = {Proc. Interspeech 2025},
  year      = {2025},
  note      = {Also available as arXiv:2505.14814}
}

@inproceedings{zhu2025llmsynth4kws,
  title     = {LLM-Synth4KWS: Scalable Automatic Generation and Synthesis of Confusable Data for Custom Keyword Spotting},
  author    = {Zhu, Pai and Wang, Quan and Agarwal, Dhruuv and Partridge, Kurt},
  booktitle = {Proc. Interspeech 2025},
  year      = {2025},
  note      = {Also available as arXiv:2505.22995}
}

@inproceedings{minixhofer2023distance,
  title     = {Evaluating and Reducing the Distance Between Synthetic and Real Speech Distributions},
  author    = {Minixhofer, Christoph and Klejch, Ond{\v{r}}ej and Bell, Peter},
  booktitle = {Proc. Interspeech 2023},
  year      = {2023}
}

@inproceedings{hu2022syntpp,
  title     = {Synt++: Utilizing Imperfect Synthetic Data to Improve Speech Recognition},
  author    = {Hu, Ting-Yao and Armandpour, Mohammadreza and Shrivastava, Ashish and Chang, Jen-Hao Rick and Koppula, Hema and Tuzel, Oncel},
  booktitle = {ICASSP 2022 - 2022 IEEE International Conference on Acoustics, Speech and Signal Processing},
  year      = {2022}
}

@article{casanova2022crosslingual,
  title   = {ASR Data Augmentation in Low-Resource Settings Using Cross-Lingual Multi-Speaker TTS and Cross-Lingual Voice Conversion},
  author  = {Casanova, Edresson and Shulby, Christopher and Korolev, Alexander and Candido Junior, Arnaldo and Soares, Anderson da Silva and Alu{\'i}sio, Sandra and Ponti, Moacir Antonelli},
  journal = {arXiv preprint arXiv:2204.00618},
  year    = {2022}
}

@article{ogun2025exhaustive,
  title   = {An Exhaustive Evaluation of TTS- and VC-based Data Augmentation for ASR},
  author  = {Ogun, Sewade and Colotte, Vincent and Vincent, Emmanuel},
  journal = {arXiv preprint arXiv:2503.08954},
  year    = {2025}
}

@inproceedings{derenzi2025african,
  title     = {Synthetic Voice Data for Automatic Speech Recognition in African Languages},
  author    = {DeRenzi, Brian and Dixon, Anna and Farhi, Mohamed Aymane and Resch, Christian},
  booktitle = {Proceedings of the 1st Workshop on Advancing NLP for Low-Resource Languages},
  year      = {2025}
}

@inproceedings{gokgoz2025personalized,
  title     = {Personalized Speech Synthesis for Zero-Shot Keyword Spotting},
  author    = {G{\"o}kg{\"o}z, Fahrettin and Cornaggia-Urrigshardt, Alessia and Wilkinghoff, Kevin},
  booktitle = {Speech Communication. 16th ITG Conference},
  year      = {2025}
}

@misc{speechqm2026,
  title        = {SpeechQM-Agent: A Multi-Agent System for Speech Data Quality Management},
  author       = {Anonymous},
  year         = {2026},
  note         = {OpenReview preprint / benchmark on automated speech-data QA}
}
```