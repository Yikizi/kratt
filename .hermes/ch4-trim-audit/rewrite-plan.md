# Chapter 4 trim/rewrite plan

Source inspected: `docs/thesis/thesis-tex-estonian/chapters/third_chapter.tex`  
Line numbers below come from `nl -ba` on the current file state.

## Main finding

Chapter 4 currently reads partly like a replication README: it mixes the methodological argument with physical repository paths, Android/Kotlin implementation names, script invocations, flags, YAML/config keys and augmentation probability dumps. This makes the chapter longer and hides the main contribution: **a multi-metric evaluation protocol for a low-resource Estonian wake-word model**.

The rewrite should keep details that affect scientific interpretation:

- data sources and whether they are training vs held-out;
- major counts where they support limitations or comparability;
- audio format only when it affects comparability (`16 kHz mono` is enough);
- evaluation metric definitions, thresholds used for reported numbers, smoothing/refractory logic where it changes FAPH;
- separation of positive detection, background FAPH and hard-negative/phrase-selectivity tests.

Cut or move out of prose:

- physical file paths (`android/app/src/...`, `wake-word/evaluation/...`, ESPHome YAML paths, model artifact paths);
- Kotlin class names and constants (`Settings.kt`, `DetectorConfig`, `AudioCapture.kt`, `Build.MODEL`, `DetectionEvent`, etc.);
- command-line flags and exact script calls (`--skip`, `--limit`, `--combo`, `--thresholds`, etc.);
- config-string dumps (`probability_cutoff`, `sliding_window_size`, `tensor_arena_size`, `stop_after_detection`, etc.);
- full augmentation class/probability lists unless moved to an appendix/replication artifact.

## Structural rewrite recommendation

1. Merge the opening two “Miks ...” sections into one section: **`Kontrollkatse ja raamistikuvalik`**. The current sections repeat the same risk-reduction argument.
2. Keep **domain shift** as the umbrella section for data collection. Put positive data, hard negatives, Android false-trigger logger and training protocol under it.
3. In each protocol subsection, start from the methodological purpose, not from code/config. One paragraph + short list is enough.
4. For exact reproducibility, cite “projekti reprodutseerimisartefakt” or appendix, not source-tree paths. The thesis chapter should explain *what was controlled and why*, not *which class/flag implemented it*.
5. Later in the chapter, avoid re-stating the same benchmark-gap claim in three places. Keep it once as the empirical problem, then let the multi-metric protocol section be the conclusion.

---

# Exact CUT/REPLACE draft: beginning through Android logger/training protocol

## A. CUT lines 1--16 and REPLACE with

This replaces the opening paragraph, `\section{Miks avalik kontrollkatse oli vajalik}`, `\section{Miks kahe raamistiku võrdlus tugevdab tööd}` and the initial `\section{Domeeninihke mõju}` text with a shorter combined introduction.

```tex
Peatüki lähtekoht on metoodiline: äratussõna mudelit ei saa hinnata ainult isoleeritud klippide põhjal, sest kasutuses töötab mudel pideval helivool. Seetõttu eristab töö klipitaseme tuvastust, taustaheli FAPH-i ja reaalajas katseid ning käsitleb häid üksikmõõdikuid ainult koos teiste kontrollidega.

\section{Kontrollkatse ja raamistikuvalik}
Enne eestikeelse sihtfraasi treenimist valideeriti treeningu- ja hindamistoru avaliku \texttt{marvin} kontrollkatsega. Kontrollkatse eesmärk ei olnud parandada \texttt{marvin}-mudelit, vaid veenduda, et andmete ettevalmistus, treening, kvantiseerimine ja voogedastushindamine töötavad enne väikese kohaliku andmestiku kasutamist. See vähendas riski, et hilisemad vead tõlgendatakse ekslikult eesti keele või seadme mikrofoni probleemina.

Raamistike võrdluses käsitleti \texttt{microWakeWord}i ja \texttt{openWakeWord}i projekti vajadustest lähtuva kompromissina: esimene sobib paremini mikrokontrolleril töötavaks lõppseadmeks, teine pakub paindlikumat arenduskeskkonda suurema arvutusvõimsusega seadmetel \cite{microwakeword2026,openwakeword2026}. Võrdlus annab tehnoloogiavalikule kontrollitud põhjenduse, kuid peatükk ei väida, et üks raamistik oleks üldiselt teisest parem.

\section{Domeeninihe ja andmete kogumine}
Pärast toru kontrollimist nihkus peamine risk andmetele. Äratussõna mudel peab üldistuma olukorda, kus treeningklipid, taustaheli ja lõppkasutuse mikrofon ei ole akustiliselt identsed. Seetõttu koguti osa positiivseid ja sihtfraasiga sarnaseid negatiivseid näiteid sihtseadmega samas ruumis ning hindamises hoiti eraldi nii sõltumatud kõnelejad, taustaheli korpused kui ka foneetiliselt sarnased kõrvalejäetud fraasid.
```

Expected effect: removes repeated “risk reduction” framing and shortens three small sections into one methodological setup.

## B. CUT lines 18--31 and REPLACE with

```tex
\subsection{Positiivse klassi kogumisprotokoll}
Positiivse klassi aluseks olid käsitsi segmenteeritud \enquote{Kuule Kratt} ütlused, mis salvestati ESP32-S3-Korvo-2 sihtplaadi mikrofoni kaudu 16~kHz monohelina. Korpus sisaldas 1076 päriskõne klippi ühelt kõnelejalt. Sama mikrofoni- ja ruumiseadistus valiti selleks, et treeningu põhiandmed ei erineks lõppkasutuse akustilisest kanalist.

Ühe kõneleja piirangut leevendati sünteetilise kõnega: positiivset klassi laiendati Neurokõne ja XTTS~v2 abil, kuid osa hääli hoiti treeningust eraldi ja kasutati ainult hindamises. Nii ei mõõtnud test ainult sama hääle taastootmist, vaid ka üldistumist varem nägemata häältele; andmestiku versioonid on koondatud ptk~2 tabelisse~\ref{tab:model-versions}.
```

Cut rationale:

- Remove mic1/mic2 split from prose unless it is directly interpreted later.
- Remove ADC/no-postprocessing detail; `16 kHz mono` and target-board microphone are sufficient.
- Keep the one-speaker limitation and TTS/held-out-voice mitigation because they matter methodologically.

## C. CUT lines 33--42 and REPLACE with

```tex
\subsection{Sarnaste negatiivnäidete kogumisprotokoll}
Sarnaste negatiivnäidete eesmärk oli õpetada mudelit eristama sihtfraasi foneetiliselt lähedastest fraasidest, mitte lisada neid taustaheli FAPH-i korpusesse. Fraaside nimekiri kattis \enquote{kuule/kule} algusega, \enquote{kratt}-sarnased, riimuvad ja ümberpööratud mustrid, näiteks \enquote{Kuule kraam}, \enquote{Kuule rott} ja \enquote{See kratt}; täpne maht mudeliversioonide kaupa on ptk~2 tabelis~\ref{tab:model-versions}.

Negatiivseid näiteid loodi kahest allikast. Esiteks sünteesiti 100 foneetiliselt lähedast fraasi mitme eesti TTS-häälega ja erinevatel tempodel ning tulemused dedupliseeriti. Teiseks salvestati sihtseadmega samas ruumis päriskõnet ning jagati see VAD-i või fikseeritud akende abil klippideks. Need klipid läksid treeningu negatiivsesse klassi; eraldi Mac-mikrofoniga salvestatud 15 fraasi jäid treeningust kõrvale sõltumatuks foneetilise eristusvõime kontrolliks.
```

Cut rationale:

- Remove eight-pattern config labels such as `\texttt{kuule+kr-}`.
- Remove Silero VAD parameter dump; “VAD or fixed windows” is enough for method.
- Keep the “training negative vs FAPH background” distinction.
- Keep the held-out 15 hard negatives because later results depend on that limitation.

## D. CUT lines 44--52 and REPLACE with

```tex
\subsection{Androidi valevallandumiste logija}
Reaalkasutuse negatiivsete näidete kogumiseks kasutati Androidi logijat, mis jooksutas telefonis sama äratussõna mudeliperekonna TFLite-artefakti ja salvestas iga vallandumise ümbert lühikese helilõigu. Logija kasutas 16~kHz mono PCM-heli; tavarežiimis talletati pikem eel- ja järelkontekst valevallandumiste kuulamiseks, kogumisrežiimis kasutati madalamat läve, et võimalikud pärisütlused ei jääks registreerimata.

Iga sündmuse juurde salvestati minimaalne manifest: ajatempel, mudel ja skoorid, kasutatud lävi ja klipi kestused ning vastava WAV-faili viide. Negatiivse klassi laiendamiseks kasutati ainult käsitsi üle kuulatud klippe, milles sihtfraasi ei öeldud; võimalikud pärisäratused hoiti eraldi positiivsete kandidaatide kogumiseks.
```

Cut rationale:

- Remove physical Android source path.
- Remove Kotlin class names/constants (`Settings.kt`, `DEFAULT_MODEL`, `DetectorConfig`, `AudioCapture.kt`, `Build.MODEL`, `EventLogger.kt`, `DetectionEvent`).
- Remove storage tree names and implementation-specific event field list.
- Keep manual verification rule, because it prevents label contamination.

## E. CUT lines 54--73 and REPLACE with

```tex
\subsection{Treeningu- ja augmenteerimisprotokoll}
Mudelite treeningus kasutati 16~kHz mono klippe, mis teisendati 10~ms sammuga logmel-tunnusteks. Treeningkomplekt jaotati deterministlikult suhtega 80/10/10 ning sama jaotusloogikat kasutati positiivsete, tavaliste negatiivsete ja sarnaste negatiivsete näidete puhul. Augmenteerimine sisaldas helitugevuse, värvilise müra, sagedusfiltri, väikeste helikõrguse muutuste ja spektrogrammi maskimise variante. Taustamüra segamist ja ruumiimpulss-vastuseid selles treeninguliinis eraldi ei kasutatud, mistõttu taustaheli robustsust kontrolliti hiljem voogedastushindamisega.

Põhimudel oli \texttt{microWakeWord}i väike \texttt{MixedNet}-tüüpi arhitektuur, mis eksporditi kvantiseeritud TFLite-artefaktina sihtseadmele. Võrdluses kasutatud v6-residual, v15 ja v16c erinesid baasmudelist ainult arhitektuuri väikeste muudatuste, SpecAugmenti kasutuse ja treeningandmestiku koosseisu poolest; täpsed versioonierinevused on koondatud ptk~2 tabelisse~\ref{tab:model-versions}. Peatükis hoitakse seetõttu fookus metoodilisel võrdlusel: sama läve- ja hindamisloogika all vaadatakse, kuidas andmestiku ja mudeli muudatused mõjutasid FAPH-i ning tuvastamismäära.
```

Cut rationale:

- Remove code path to mmap generation script and YAML file.
- Remove augmentation class names and probability dump.
- Remove full architecture/config dump from prose; keep only model family and deployment-relevant TFLite fact.
- Remove repeated version-specific training-set counts here; table~\ref{tab:model-versions} already carries them.

---

# Follow-on trim plan for the rest of Chapter 4

These ranges do not require full replacement prose here, but they should be trimmed in the same style.

| Lines | Current issue | Concrete action |
|---:|---|---|
| 75--88 | Voogedastushindamise section contains a Common Voice selection recipe, Python call details and script path. | Keep FAPH definition, corpora/durations, exclusion of target words, 16~kHz mono, concatenation with short silence, smoothing, threshold and refractory period. Cut exact `validated.tsv` reading procedure, Python index notation, script name and flags. If exact reconstruction is required, move to appendix/replication artifact. |
| 90--99 | MoE section includes full model artifact paths, lineage path and benchmark command. | Keep: two independently trained experts, smoothed frame-level AND/minimum, thresholds 0.996/0.996, 2~s refractory, FAPH result. Cut physical paths, KB sizes unless deployment memory is discussed, `np.minimum.reduce`, command flags. |
| 101--115 | Live device protocol mostly useful, but script path and repeated decision rules lengthen it. | Keep sample sizes (`n=11`, `n=15`), two speakers, approximate distance, real-time not replayed, threshold/refractory. Cut script path and repeated explanation of rising-edge if already defined in FAPH protocol. |
| 117--119 | ESP32 deployment paragraph is a config dump. | Replace with one paragraph: target board uses 16~kHz mono I2S audio into microWakeWord, same threshold and smoothing as evaluation, TFLite artifact deployed without retraining, detection starts Home Assistant voice pipeline. Cut YAML/manifest paths and config keys (`probability_cutoff`, `sliding_window_size`, `feature_step_size`, `tensor_arena_size`, `stop_after_detection`, etc.). |
| 121--169 | Benchmark-gap argument repeats the intro and overlaps with the later multi-dimensional protocol section. | Condense to: one empirical contrast paragraph (v6-residual vs v15), one bullet list of four reasons, one paragraph proposing scenario-based evaluation. Keep 1--2 literature citations, not three separate citation-heavy subsections. |
| 171--179 | Agent-based development section repeats “tools accelerated work but not evidence” across four paragraphs. | Reduce to two paragraphs: (1) agents enabled logger/evaluation tooling, (2) bottleneck remains real data and external validity. Avoid listing every tool twice. |
| 181--226 | Core contribution is valuable but very long; the three validation rounds duplicate benchmark-gap examples. | Convert the three rounds into a compact table or three shorter paragraphs: problem → failure mode → correction. Keep the general principle and transferability, but cut repeated numbers already shown in Results. |
| 228--238 | “Mida saab juba praegu väita” has one very long bullet duplicating consensus/checkpoint caveats. | Split or shorten: validated pipeline; background FAPH is required; expert consensus achieves sub-1 FAPH as a point estimate; real-speaker recall remains the main deployment limitation. Move rejected checkpoint detail to Results only. |
| 240--242 | Future cascade is a dense literature dump. | Keep the conceptual link: current consensus is a one-stage approximation of cascade design; future work should add a second stage checking word order/presence. Cut most percentages and keep only the most relevant citations. |

## Repetition to remove globally

- Replace repeated “Et ... oleks reprodutseeritav, fikseeritakse ...” openers with one sentence before the protocol block: “Alljärgnevad protokollid esitavad ainult need detailid, mis mõjutavad tulemuste tõlgendust.”
- Avoid manual section numbers such as `§3.3.4` in prose; use labels or say “voogedastushindamise protokollis”.
- Mention `FAPH` definition once, then reuse the abbreviation.
- Do not list both a result and its rejected-checkpoint caveat in every section. Put rejected configurations in Results; keep Chapter 4 focused on methodological lessons.

## Expected length impact

- Lines 1--73: replacement should reduce about 73 source lines to roughly 34--38 lines.
- Lines 75--119: a concise protocol rewrite should reduce 45 lines to about 18--22 lines.
- Lines 121--242: targeted condensation should save another 50--70 lines without removing the main argument.

Overall, Chapter 4 can likely be shortened by about one third while becoming clearer: methods stay reproducible at the conceptual level, and implementation-level details move out of the prose.
