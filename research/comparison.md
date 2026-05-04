# Real-World Evaluation of Wake-Word Systems for Kratt

## Executive summary

For a bachelor’s thesis on **Kratt**—an Estonian wake-word and voice-satellite prototype built around microWakeWord, TensorFlow Lite INT8, and ESP32-S3 / Android deployment—the strongest external literature supports a **methodology thesis**, not a “production-grade wake-word solved” thesis. The best peer-reviewed evidence does **not** support the idea that clip-level or clean-speech benchmark scores are enough to predict deployment behavior. Instead, the literature repeatedly points to a gap between fixed-length benchmark evaluation and always-on operation in continuous audio, especially under far-field capture, TV or playback audio, overlapping speech, reverberation, and phonetically confusable phrases. citeturn25view2turn25view0turn10view0turn31view0turn38view0turn42view0

The clearest peer-reviewed commercial evidence comes from smart-speaker misactivation studies. In one controlled study of commercial speakers from entity["company","Amazon","e-commerce and cloud"], entity["company","Apple","consumer electronics"], entity["company","Google","internet company"], and entity["company","Microsoft","software company"] exposed to two rounds of 134 hours of TV dialogue in the US and UK, researchers observed **up to 0.95 misactivations per hour**, with many events being **non-repeatable** and some devices having **10% of misactivations lasting at least 10 seconds**. A second study with 11 smart speakers in a “living-room-like” setup found rates on TV content as high as **one accidental trigger every 1 h 16 min** for Hey Cortana, **every 3 h 52 min** for Alexa, and **every 60 h** for Hey Siri, with accidental triggers also appearing in news and professional speech datasets. citeturn9view5turn10view0turn31view0

For Kratt, the most defensible academic position is therefore: **the contribution is the construction and audit of a low-resource Estonian wake-word pipeline, plus a realistic evaluation framework that exposed benchmark–deployment mismatch**. Your Android 24/7 logger and short replay/user-test are not “just tooling”; they fit directly into an ecological evaluation tradition in HCI and speech systems, where in-the-wild logs, conditional recorders, and field deployments are used because closed systems and household use cannot be fully captured by laboratory corpora alone. citeturn25view5turn37view0turn37view1

The thesis should therefore avoid claims such as “production-ready”, “commercial-level”, “solved Estonian wake-word detection”, or “real-world FA/h below X” unless backed by much larger longitudinal, multi-device, multi-home evidence. A conservative, well-supported conclusion is that Kratt demonstrates **prototype feasibility**, **methodological rigor**, and **clear evidence that continuous-stream FAPH/FA/h, hard negatives, and field logging are necessary to characterize actual wake-word behavior in a low-resource language setting**. citeturn14view1turn36view2turn25view0turn10view0turn31view0

## Most relevant source table

| Citation | Source type | What it measured | Corpus / environment | Key numerical findings | Why it matters for Kratt |
|---|---|---|---|---|---|
| **Dubois et al., 2020, “When Speakers Are All Ears”** citeturn9view6turn10view0 | Peer-reviewed privacy / measurement paper | Misactivations of commercial smart speakers in controlled playback | 134 h of TV dialogue from 12 shows, repeated in US and UK | Up to **0.95 misactivations/h**; **1.43 per 10,000 words**; some devices had **10%** of misactivations lasting **≥10 s**; many misactivations were **not repeatable** | Strongest direct evidence that realistic long-form playback reveals behavior not captured by clean clip tests |
| **Schönherr et al., 2022, “Exploring accidental triggers of smart speakers”** citeturn31view0turn11view7 | Peer-reviewed speech / security paper | Accidental triggers of 11 commercial smart speakers | Simulated living-room scenario with 24 h TV shows, news, LibriSpeech, Common Voice, CHiME; 10x trigger replay | On TV shows: **Hey Cortana ~1 trigger / 1h16m**, **Alexa ~1 / 3h52m**, **Hey Siri ~1 / 60h**; around **75%** of Amazon/Google triggers were medium-to-high reproducibility | Excellent support for using TV/news/conversational long-form audio and replay verification, not only clip-level benchmarks |
| **López-Espejo et al., 2022, “Deep Spoken Keyword Spotting: An Overview”** citeturn25view2turn25view0turn26view1turn25view5 | Peer-reviewed review | KWS datasets, metrics, robustness, streaming vs non-streaming evaluation | Review of KWS literature and datasets | Notes that common GSC-style evaluation is often **non-streaming**, while “real-life KWS involves the continuous processing of an input audio stream”; recommends **false alarms per hour** as a user-relevant metric for voice assistants | Best general citation for why clip-level accuracy/FPR can mislead, and why FA/h is a defensible thesis metric |
| **Tang et al., 2020, “Howl”** citeturn42view0turn1search17 | Peer-reviewed open-source system paper | Open wake-word system and deployment evaluation | Mozilla Common Voice–derived wake-word dataset; Firefox Voice deployment | Deployed model reported **16% FRR at 5 false alarms per hour**; paper explicitly warns that speech-command classifiers with limited negatives are not rigorously tested for wake-word detection | Useful external analogy for low-resource/open wake-word work and for separating wake-word detection from generic speech-command classification |
| **Liu et al., 2020, “Metadata-Aware End-to-End Keyword Spotting”** citeturn38view0 | Peer-reviewed industry paper | Effect of playback/device state metadata on KWS | Internal Alexa playback vs non-playback wake-word data | Playback caused a noticeable mean shift in acoustic features; metadata-aware model achieved **14.63% relative FRR improvement** at the same FAR | Strong justification that playback states matter and that TV/music/alarm/audio-output conditions can alter model behavior substantially |
| **Van Segbroeck et al., 2020, “DiPCo — Dinner Party Corpus”** citeturn19search0turn19search2 | Peer-reviewed dataset paper | Far-field, natural multi-party conversational speech in a home-like environment | 10 dinner-party sessions, 15–45 min each, recorded by far-field arrays | Designed specifically for natural conversation around a dining table with far-field microphones | Strong justification for using DiPCo as a realistic held-out negative set for conversational far-field speech |
| **Watanabe et al., 2020, CHiME-6 Challenge** citeturn20search0turn20search6 | Peer-reviewed challenge paper | Distant, multi-microphone conversational speech in real homes | 20 real dinner parties, 4 participants each, multi-room home recordings | Highlights far-field, overlapping speech, and unsegmented real-home conditions as core challenge factors | Good support for the claim that home conversational audio is much harder than clean isolated clips |
| **Chen et al., 2022, MISP Challenge** citeturn32view0turn32view1turn41search1 | Peer-reviewed challenge / dataset paper | Real-home TV-room wake-word and ASR evaluation | Home TV scenario with several people chatting while watching TV; **124.79 h** AVWWS corpus | Described as the first open evaluation targeting real-world AV wake-word issues in a home-TV scenario | Highly relevant for TV playback, living-room, and multi-party distraction conditions that standard corpora miss |
| **Porcheron et al., 2018, “Voice Interfaces in Everyday Life”** citeturn37view0turn40search8 | Peer-reviewed HCI field study | Naturalistic household use and interaction capture methodology | Month-long Echo deployments in 5 households with a Conditional Voice Recorder | Collected **over 6 h** of captured verbal exchanges and **883** distinct request utterances | Strong methodological precedent for using supplemental logging/recording infrastructure in the home as research evidence |
| **Wei et al., 2022, “What Could Possibly Go Wrong…”** citeturn37view1turn40search12 | Peer-reviewed HCI field study | In-the-wild voice interaction errors and logging methodology | 3-week field deployment in 13 homes using auxiliary recordings and logs | Captured **1,213** interactions and **30,000** logs; found substantial interaction errors in real homes | Supports treating Kratt’s Android logger and replay study as empirical methodology, not merely engineering instrumentation |
| **openWakeWord documentation** citeturn36view2turn36view0 | High-quality open-source documentation | Recommended real-world wake-word evaluation practice | Realistic wake-word examples plus Dinner Party Corpus for false accepts | Recommends false accepts from **hours of continuous speech and background noise**; practical target of **<0.5 FA/h** and **<5% FRR**, explicitly marked **subjective** | Useful for thesis discussion of practical engineering thresholds, but should be framed as non-peer-reviewed guidance |
| **microWakeWord documentation** citeturn14view1 | High-quality open-source documentation | Training/evaluation protocol for low-power wake-word systems | Ambient clips split into streaming windows during training | States estimated FA/h during training is **not a perfect estimate** of real-world streaming FA/h | Directly supports your claim that offline training-time FA/h and deployment FA/h are different things |

## Research answers to the thesis questions

### Strongest sources on the lab–deployment gap

The strongest peer-reviewed sources are not a single paper but a **stack of complementary evidence**. The best general survey source is López-Espejo et al. because it explicitly criticizes non-streaming benchmark practice and explains why always-on systems should be evaluated in terms of **false alarms per hour**, not just clip-level class metrics. It also points out that popular benchmarks such as Google Speech Commands are often evaluated in **non-streaming mode**, while actual wake-word use is continuous and heavily dominated by non-keyword audio. citeturn25view2turn25view0turn26view1

The best direct commercial-system evidence is Dubois et al. and Schönherr et al. Dubois et al. show that long-form TV playback near real devices can produce frequent misactivations and, critically, that **most misactivations are not repeatable** even under nominally identical conditions. Schönherr et al. extend this by testing 11 smart speakers across TV, news, and professional speech in a living-room-like setup, showing that accidental triggers vary sharply by wake word, by device, and by corpus, and that replay verification is necessary because many candidate triggers sit near the decision boundary. citeturn10view0turn31view0turn11view7

Two additional sources are especially useful for Kratt’s thesis framing. First, Howl warns that speech-command classifiers with limited negative sets are not rigorously evaluated for wake-word detection and reports a deployed operating point in **FA/h**, not just offline classification accuracy. Second, Amazon’s metadata-aware KWS paper shows that device playback state shifts the feature distribution enough that extra metadata improves performance, which is an unusually direct industry acknowledgment that deployment acoustics differ from “normal” speech conditions. citeturn42view0turn38view0

### Measured real-world false activation rates in commercial systems

Public studies do report false-activation rates for commercial systems, but the numbers are **not directly comparable** because the operating point, devices, wake phrases, and counting rules differ. Some studies count local triggers only; others count local-plus-cloud verified triggers; some normalize by hour, some by 10,000 words, and some report raw event counts over weeks. That caveat needs to be explicit in the thesis. citeturn31view0turn9view5

Under **TV dialogue playback**, Dubois et al. measured **up to 0.95 misactivations per hour** on commercial smart speakers, corresponding to **1.43 misactivations per 10,000 words** in the most affected conditions. The same paper also found that some devices had **10%** of misactivations lasting **10 seconds or more**, which matters because a false wake is not merely a classifier error; it can become a recorded and transmitted interaction. citeturn9view5turn10view0turn10view2

In Schönherr et al.’s **living-room-like** setup, estimated rates on **TV shows** ranged from about **0.017/h** for Hey Siri up to **0.783/h** for Hey Cortana across all datasets, and specifically on TV content the authors summarize the user-facing rates as about **one trigger every 60 hours** for Hey Siri, **every 3 h 52 min** for Alexa, and **every 1 h 16 min** for Hey Cortana. They also report nontrivial accidental-trigger rates on **news** and **professional speech** corpora, not just TV, which is important because it means the problem is not limited to entertainment audio. citeturn31view0

A smaller observational apartment study of four Echo devices over **eight weeks** found **144 original human-voice false positives**, **46 TV false positives**, and **225 total false positives** when repeats and “other” audio were included. Because the study used four devices over 56 days, that is roughly **0.64 original human-voice false positives per device-day** and about **1.0 total false positives per device-day** overall. The study is weaker than the controlled speech papers because it is small-N and not standardized in FA/h, but it is still useful as everyday-use context. citeturn33view0

A separate but important industry point is that vendors use **secondary cloud verification** precisely because on-device wake-word detection still produces false wakes from like-sounding words. Amazon’s own documentation describes cloud verification as a second-stage check that can close the stream after a local false wake, which supports the thesis argument that false activations are significant enough to shape production architectures. citeturn17search2turn17search5

### Defensible protocol for a small academic project

For a bachelor’s-level project without access to thousands of hours of home audio, the most defensible protocol is **layered evidence**, not a single benchmark. In practice, that means combining: **held-out streaming FAPH/FA/h on long-form negatives**, **held-out positive recall evaluation**, **hard-negative / confusable-phrase stress tests**, **target-device field logging**, and a **small replay-based user test**. This is consistent with both the KWS review literature and the best open-source guidance, both of which emphasize realistic continuous audio and user-relevant metrics rather than clip-level accuracy alone. citeturn25view0turn25view2turn36view2turn14view1

The negative side of the protocol should be continuous-stream evaluation on **held-out long-form audio** that was never used in training or threshold tuning. For Kratt, your current Common Voice Estonian slice, LibriSpeech test-clean, and DiPCo subset form a defensible small-suite because they cover **in-language read speech**, **clean out-of-language speech**, and **far-field multi-party conversational speech**. This does not make them a complete deployment simulation, but it is much stronger than clip-level negative testing or reusing training negatives. citeturn25view2turn19search2turn20search0

The positive side should report **wake recall or false-reject rate** on held-out wake-phrase examples with realistic augmentation or real device captures, and the operating point should be shown as a **curve**, not a single threshold. That is standard in KWS, and it matters because the same threshold that looks good on clean held-out positives may be unacceptable on hard negatives or live acoustic conditions. citeturn25view0turn36view2turn23search13

A third layer should be a curated **hard-negative suite** built around phonetically and structurally confusable phrases, prefix variants, reversed-order phrases, and semantically plausible household speech. External literature strongly supports this: KWS work routinely emphasizes challenging non-keyword examples, and smart-speaker studies repeatedly find accidental triggers from phonetically similar words, proper names, gibberish-like material, and even some non-speech events. citeturn26view0turn31view0turn29search0

A fourth layer should be **field logging on the actual always-on runtime path**. Even if the dataset is smaller than industry practice, a continuous device-side logger closes the exact gap that the literature identifies: the gap between laboratory clips and persistent streaming use in a real acoustic environment. This is especially important for Kratt because your system is low-resource, deployed on different hardware classes, and uses a streaming detector whose real-world FA/h cannot be inferred perfectly from training-time approximations. citeturn14view1turn36view2turn37view1

### Why Android field logging and replay tests count as thesis evidence

Android 24/7 false-trigger logging is research evidence when it is presented as a **measurement instrument for ecological validity**, not just a debugging tool. The literature on KWS and smart-speaker interaction makes exactly this move: objective benchmark metrics are useful, but the “gold plate” remains relevant end-user behavior; meanwhile, real household studies commonly require extra logging or conditional recording because the systems are closed and because everyday use is not reducible to offline lab clips. citeturn25view5turn37view0turn35search1

Your Android logger is especially defensible because it measures the thing users experience: **continuous false triggers during unattended runtime**. That makes it methodologically closer to smart-speaker field studies and conditional voice-recording setups than to a mere engineering benchmark. If the logger runs multiple models simultaneously on the same input stream, it also improves internal validity by controlling the acoustic exposure while comparing thresholds or architectures. citeturn37view0turn37view1

A short replay-based user test is likewise legitimate thesis evidence if it is framed correctly. It does **not** prove long-term household FAPH, but it does provide a controlled bridge between pure corpus evaluation and uncontrolled field use. In the literature, replay and repeated playback are often used specifically to verify candidate triggers and examine reproducibility around the decision boundary. A 20–30 participant replay study can therefore support claims about wake success, user-to-user variation, pronunciation tolerance, and robustness to adversarially chosen confusables under standardized conditions. citeturn11view7turn31view0

### Claims to avoid

Avoid claiming that Kratt is **production-ready**, **commercial-level**, **field-proven**, or **solves Estonian wake-word detection**. Public peer-reviewed commercial studies use much larger and more heterogeneous audio exposures than your current evidence, and even they show strong dependence on device, corpus, and operating point. Small-sample field logging plus modest held-out corpora can support a strong prototype and methodology claim, but not a certification-style production claim. citeturn9view6turn31view0turn25view5

Avoid claiming a stable real-world rate such as “**real-world FAPH is below X**” unless the claim is explicitly restricted to the evaluated device, threshold, acoustic environment, and model version. The microWakeWord documentation is unusually honest here: its training-time ambient FA/h estimate is “not a perfect estimate” of real-world streaming behavior. Your thesis should adopt the same caution. citeturn14view1

Avoid claiming that a single benchmark ranking proves overall superiority. Both the speech literature and the smart-speaker studies show environment-specific behavior: TV playback, news, conversational far-field speech, hard negatives, and practical deployment can reorder model rankings. A much safer formulation is that one model provided the **best observed trade-off under the tested conditions**. citeturn31view0turn38view0turn42view0

### Conservative conclusion wording

The safest thesis conclusion is that Kratt demonstrates **feasibility plus evaluation insight**, not final product quality. A strong conservative version would say that the project successfully built a realistic low-resource Estonian wake-word pipeline, showed that earlier clip-based evaluation overstated performance, and established a more defensible real-world evaluation loop based on streaming FA/h, hard negatives, and field logging. It can also say that the prototype identifies plausible operating points and design trade-offs for “Kuule Kratt / Kule Kratt” on constrained hardware, while leaving final model optimization and large-scale household validation as future work. citeturn25view0turn10view0turn14view1turn36view2

### Short quotable excerpts and safe interpretations

> “real-life KWS involves the continuous processing of an input audio stream.” citeturn25view2  
**Safe interpretation:** clip-level or fixed-window evaluation is insufficient as the primary thesis metric.

> “most misactivations are not repeatable” citeturn10view1  
**Safe interpretation:** near-threshold false wakes are partly stochastic, so repeated replay or longer field logging is necessary.

> “hours of continuous speech and background noise” citeturn36view4  
**Safe interpretation:** negative evaluation should approximate sustained real deployment conditions, not just short held-out clips.

> “This is not a perfect estimate of the streaming model’s real-world false accepts per hour” citeturn14view1  
**Safe interpretation:** offline ambient FA/h is useful for model selection, but not a substitute for deployment measurement.

## Evaluation protocol recommendation for Kratt

The most defensible way to map the literature onto Kratt is to present evaluation as **four complementary layers**, each answering a different question.

### Streaming corpus evaluation

Use **held-out Common Voice Estonian**, **LibriSpeech test-clean**, and **DiPCo** as your primary long-form negative suite, and report **false accepts per hour** under frozen thresholds. In the thesis, justify this by saying that continuous non-keyword audio better matches real wake-word operating conditions than non-streaming clip classification, and that the three corpora cover distinct but relevant stressors: in-language speech, clean out-of-language speech, and far-field conversational overlap. Present the result as **benchmark FAPH/FA/h under selected corpora**, not as deployment FAPH. citeturn25view2turn25view0turn19search2turn20search0

### Hard-negative and confusable-phrase evaluation

Keep a separate **hard-negative benchmark** for phrase-order reversals, rhyming or confusable substitutes, prefix-only forms, and structurally similar commands such as “Kuule rott”, “Kratt kuule”, “Kuule robot”, and “kuule/kule <not kratt>”. Literature support is strong here: challenging non-keyword samples are a recognized failure mode in KWS, and smart-speaker accidental-trigger studies repeatedly find phonetically similar words and unusual names as real trigger sources. This layer should be reported separately from corpus FA/h because it measures **adversarial lexical confusability**, not natural incidence. citeturn26view0turn31view0turn29search0

### Field logging on the Android always-on path

Use the **98.97 h Android logger session** as your main ecological false-trigger result, clearly labeled by **device, threshold, runtime path, and model version**. State explicitly that this is closer to deployment evidence because it measures continuous inference on an actual always-on device in a real acoustic environment, but also that it is limited to one hardware family and one field session. The logger should therefore be treated as a **field estimate of practical FA/h under one deployment pathway**, not as a universal property of the model. citeturn37view1turn14view1turn36view2

For your concrete figures, the thesis can responsibly say that, in one 98.97 h Android field session at threshold 0.90, the compared models occupied different practical points on the recall–FAPH trade-off, with v6-residual showing the lowest observed false-trigger rate in that setup, expert-a giving a stronger balance once prior recall evidence is included, and some historically important models proving much noisier in live use than earlier offline rankings suggested. Because these are your internal measurements rather than published ones, the published literature should be used to justify the **need** for this field layer, not to launder the numbers into stronger generality than they warrant. citeturn25view5turn37view0

### Replay-based user study

Run the **20–30 participant replay study** as a distinct usability-and-robustness layer. It should not be sold as household FA/h measurement. Instead, use it to answer narrower questions: how robust is the system to accent, tempo, pronunciation reduction, user-to-user variation, and realistic confusables when the playback path and device setup are controlled? A replay protocol is well aligned with the trigger-verification logic used in accidental-trigger research, and a small participant study is consistent with HCI field methods where rich audio logs and targeted probes are used to study error behavior despite modest N. citeturn11view7turn37view0turn37view1

A strong protocol would include: participant-issued true wake phrases at near and far distances; conversational carrier phrases with and without the wake phrase; confusables and prefix-only forms; TV/music or loudspeaker distractors; and at least one fixed operating point carried over from the offline evaluation. Report **wake success**, **misses**, and any **false wakes** observed during negative replays, but avoid converting this short study into a general “real-world FA/h” claim. citeturn31view0turn38view0

### Reporting and thesis structure

In reporting, keep **training, model selection, threshold tuning, and final evaluation** visibly separated. Because your early evaluation reused training negatives and used clip-level FPR, the thesis should explicitly describe that as a methodological pitfall and then explain the corrected protocol: held-out long-form streaming negatives, device-side field logging, and hard-negative suites. That transparency will strengthen the thesis, not weaken it. citeturn42view0turn25view2turn14view1

## Recommended thesis framing

Kratt ei väida, et oleks saavutanud tootmisküpse eestikeelse äratussõna tuvastuse. Töö peamine panus on realistliku madala ressursiga toru loomine fraasi **„Kuule Kratt / Kule Kratt”** jaoks ning näitamine, et klipipõhine laborihindamine võib tegelikku kasutuskogemust oluliselt üle hinnata. Töö käigus asendati varasemad lihtsustatud mõõdikud vooghindamisega, kus valepositiive hinnati pidevas helivoos false accepts per hour alusel ning eraldi käsitleti raskete negatiivide ja segadust tekitavate fraaside mõju. Lisaks korpusepõhisele hindamisele loodi reaalseadme välilogimise ja lühikese kasutajatesti metoodiline raamistik, et hinnata äratussõna käitumist tingimustes, mida standardsed korpused ei kata. Tulemused näitavad, et mudelite pingeread sõltuvad tugevalt hindamiskeskkonnast: puhas kõne, kaugevälja vestlus, segavad fraasid ja päris kasutus ei anna sama järjestust. Seetõttu tuleks Kratti käsitleda kui metoodiliselt põhjendatud prototüüpi ja uurimisinstrumenti, mitte veel lõplikku tootmistaseme äratussõna lahendust. citeturn25view2turn10view0turn31view0turn14view1turn36view2

## Limitations and caveats

The main limitation is **sample size**. A 98.97 h field session is meaningful for a bachelor’s thesis and very useful for model ranking under one runtime path, but it is still far too small to certify a stable household FA/h below a stringent threshold such as 0.5/h, especially for rare-event estimation. The same applies to a 20–30 participant replay study: it can reveal weak spots and user variability, but it cannot stand in for a longitudinal multi-home deployment. citeturn36view0turn37view1

A second limitation is **device and domain mismatch**. Android microphones, DSP, and power-management behavior are not the same as ESP32-S3 / ESPHome satellites; similarly, Common Voice ET, LibriSpeech, and DiPCo do not fully represent spontaneous Estonian household speech, TV playback, or family interaction. The literature strongly suggests that playback state, room acoustics, far-field capture, and overlapping speech can shift behavior enough to reorder model rankings. citeturn38view0turn19search2turn20search0

A third limitation is **threshold tuning bias**. If thresholds are adjusted after inspecting benchmark or field outcomes, the resulting figures are best described as exploratory operating points rather than unbiased final estimates. The thesis should therefore document whether thresholds were frozen before each evaluation layer or tuned iteratively, and it should distinguish “selection” results from “final” results. citeturn14view1turn36view1

A fourth limitation is the difference between **benchmark FA/h** and **deployment FA/h**. Even robust open-source KWS documentation warns that training-time or offline ambient FA/h is not the same as the streaming detector’s real-world behavior. In other words, it is entirely plausible for a model to look good on held-out corpora and still underperform on hard negatives, TV playback, or real household audio. That is not a flaw in Kratt’s methodology; it is one of Kratt’s main findings. citeturn14view1turn36view2turn42view0

A final caveat is that **no public, universally accepted user-annoyance threshold** emerged from the peer-reviewed literature I found. The closest practical rule of thumb is from openWakeWord, which suggests that **<0.5 FA/h** and **<5% FRR** is often reasonable in practice, but it explicitly labels this threshold as **subjective**. In the thesis, that should be presented as engineering guidance, not as a scientifically established standard. citeturn36view0turn36view1

## BibTeX entries

The BibTeX below covers the sources that are most worth citing directly in the thesis text. Bibliographic details were transcribed from the paper and publisher pages used above. citeturn40search0turn40search8turn40search12turn41search1turn42view0turn24view0

```bibtex
@article{dubois2020when,
  author  = {Dubois, Daniel J. and Kolcun, Roman and Mandalari, Anna Maria and Paracha, Muhammad Talha and Choffnes, David and Haddadi, Hamed},
  title   = {When Speakers Are All Ears: Characterizing Misactivations of IoT Smart Speakers},
  journal = {Proceedings on Privacy Enhancing Technologies},
  year    = {2020},
  volume  = {2020},
  number  = {4},
  pages   = {255--276},
  doi     = {10.2478/popets-2020-0072}
}

@article{schoenherr2022exploring,
  author  = {Sch{\"o}nherr, Lea and Golla, Maximilian and Eisenhofer, Thorsten and Wiele, Jan and Kolossa, Dorothea and Holz, Thorsten},
  title   = {Exploring Accidental Triggers of Smart Speakers},
  journal = {Computer Speech \& Language},
  year    = {2022},
  volume  = {73},
  pages   = {101328},
  doi     = {10.1016/j.csl.2021.101328}
}

@article{lopezespejo2022deep,
  author  = {L{\'o}pez-Espejo, Iv{\'a}n and Tan, Zheng-Hua and Hansen, John H. L. and Jensen, Jesper},
  title   = {Deep Spoken Keyword Spotting: An Overview},
  journal = {IEEE Access},
  year    = {2022},
  volume  = {10},
  pages   = {4169--4199},
  doi     = {10.1109/ACCESS.2021.3139508}
}

@inproceedings{tang2020howl,
  author    = {Tang, Raphael and Lee, Jaejun and Razi, Afsaneh and Cambre, Julia and Bicking, Ian and Kaye, Jofish and Lin, Jimmy},
  title     = {Howl: A Deployed, Open-Source Wake Word Detection System},
  booktitle = {Proceedings of the Second Workshop for NLP Open Source Software},
  year      = {2020},
  pages     = {61--65},
  publisher = {Association for Computational Linguistics},
  url       = {https://cs.uwaterloo.ca/~jimmylin/publications/Tang_etal_NLP-OSS2020.pdf}
}

@inproceedings{liu2020metadata,
  author    = {Liu, Hongyi and Abhyankar, Apurva and Mishchenko, Yuriy and Sen{\'e}chal, Thibaud and Fu, Gengshen and Kulis, Brian and Stein, Noah and Shah, Anish and Vitaladevuni, Shiv Naga Prasad},
  title     = {Metadata-Aware End-to-End Keyword Spotting},
  booktitle = {Proc. Interspeech 2020},
  year      = {2020},
  pages     = {849--853},
  publisher = {ISCA},
  url       = {https://www.isca-archive.org/interspeech_2020/liu20j_interspeech.pdf}
}

@inproceedings{vansegbroeck2020dipco,
  author    = {Van Segbroeck, Maarten and Zaid, Ahmed and Kutsenko, Ksenia and Huerta, Cirenia and Nguyen, Tinh and Luo, Xuewen and Hoffmeister, Bj{\"o}rn and Trmal, Jan and Omologo, Maurizio and Maas, Roland},
  title     = {{DiPCo} -- Dinner Party Corpus},
  booktitle = {Proc. Interspeech 2020},
  year      = {2020},
  publisher = {ISCA},
  url       = {https://www.isca-archive.org/interspeech_2020/segbroeck20_interspeech.pdf}
}

@inproceedings{watanabe2020chime6,
  author    = {Watanabe, Shinji and Mandel, Michael and Barker, Jon and Vincent, Emmanuel and Arora, Ashish and Chang, Xuankai and Khudanpur, Sanjeev and Manohar, Vimal and Povey, Daniel and Raj, Desh and Snyder, David and Shanmugam Subramanian, Aswin and Trmal, Jan and Yair, Bar Ben and Boeddeker, Christoph and Ni, Zhaoheng and Fujita, Yusuke and Horiguchi, Shota and Kanda, Naoyuki and Yoshioka, Takuya and Ryant, Neville},
  title     = {{CHiME}-6 Challenge: Tackling Multispeaker Speech Recognition for Unsegmented Recordings},
  booktitle = {Proc. CHiME 2020 Workshop},
  year      = {2020},
  doi       = {10.21437/CHiME.2020-1}
}

@inproceedings{chen2022misp,
  author    = {Chen, Hang and Zhou, Hengshun and Du, Jun and Lee, Chin-Hui and Chen, Jingdong and Watanabe, Shinji and Siniscalchi, Sabato Marco and Scharenborg, Odette and Liu, Di-Yuan and Yin, Bao-Cai and Pan, Jia and Gao, Jian-Qing and Liu, Cong},
  title     = {The First Multimodal Information Based Speech Processing Challenge: Data, Tasks, Baselines and Results},
  booktitle = {Proceedings of the IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
  year      = {2022},
  pages     = {9266--9270},
  doi       = {10.1109/ICASSP43922.2022.9746683}
}

@inproceedings{porcheron2018voice,
  author    = {Porcheron, Martin and Fischer, Joel E. and Reeves, Stuart and Sharples, Sarah},
  title     = {Voice Interfaces in Everyday Life},
  booktitle = {CHI '18: Proceedings of the 2018 CHI Conference on Human Factors in Computing Systems},
  year      = {2018},
  publisher = {ACM},
  pages     = {Paper 640},
  doi       = {10.1145/3173574.3174214}
}

@inproceedings{wei2022what,
  author    = {Wei, Jing and Tag, Benjamin and Trippas, Johanne R. and Dingler, Tilman and Kostakos, Vassilis},
  title     = {What Could Possibly Go Wrong When Interacting with Proactive Smart Speakers? A Case Study Using an ESM Application},
  booktitle = {CHI '22: Proceedings of the 2022 CHI Conference on Human Factors in Computing Systems},
  year      = {2022},
  publisher = {ACM},
  doi       = {10.1145/3491102.3517432}
}

@inproceedings{werchniak2020synthetic,
  author    = {Werchniak, Andrew and Rybakov, Oleg and Kononenko, Natalia and Levis, Philip and Laurenzo, Stuart},
  title     = {Exploring the Application of Synthetic Audio in Training Keyword Spotters in Low-Resource Settings},
  booktitle = {Proc. Interspeech 2020},
  year      = {2020},
  publisher = {ISCA},
  url       = {https://cdn.amazon.science/20/8b/696fd11d4d99a69e2adfc4602ccd/exploring-the-application-of-synthetic-audio-in-training-keyword-spotters.pdf}
}

@inproceedings{rikhye2021personalized,
  author    = {Rikhye, Rajeev and Wang, Quan and Liang, Qiao and He, Yanzhang and Zhao, Ding and Huang, Yiteng and Narayanan, Arun and McGraw, Ian},
  title     = {Personalized Keyphrase Detection Using Speaker and Environment Information},
  booktitle = {Proc. Interspeech 2021},
  year      = {2021},
  pages     = {4204--4208},
  publisher = {ISCA},
  doi       = {10.21437/Interspeech.2021-204}
}

@misc{openwakeword2026,
  author       = {Scripka, David},
  title        = {openWakeWord},
  year         = {2026},
  howpublished = {\url{https://github.com/dscripka/openWakeWord}},
  note         = {GitHub repository and documentation, accessed 2026-05-03}
}

@misc{microwakeword2026,
  author       = {Ahrendt, Kevin and Open Home Foundation},
  title        = {microWakeWord},
  year         = {2026},
  howpublished = {\url{https://github.com/OHF-Voice/micro-wake-word}},
  note         = {GitHub repository and documentation, accessed 2026-05-03}
}

@misc{edpb2021vva,
  author       = {{European Data Protection Board}},
  title        = {Guidelines 02/2021 on Virtual Voice Assistants},
  year         = {2021},
  howpublished = {\url{https://www.edpb.europa.eu/system/files/2021-07/edpb_guidelines_202102_on_vva_v2.0_adopted_en.pdf}},
  note         = {Version 2.0, adopted 2021-07-07}
}

@misc{karczewski2017cloud,
  author       = {Karczewski, Ted},
  title        = {Cloud-Based Wake Word Verification Improves “Alexa” Wake Word Accuracy on Your AVS Products},
  year         = {2017},
  howpublished = {\url{https://developer.amazon.com/blogs/alexa/post/b136b3e7-0ba8-4589-aaf9-2a037fc4e9c9/cloud-based-wake-word-verification-improves-alexa-wake-word-accuracy-on-your-avs-products}},
  note         = {Amazon developer blog}
}
```