## Files Retrieved
1. `docs/thesis/thesis-tex-estonian/chapters/third_chapter.tex` (lines 1-243) - Chapter 4 draft: metoodiline järeldus, avalik `marvin` kontroll, kahe raamistiku põhjendus, domeeninihe, andme-/hindamisprotokollid, benchmark-gap, agentpõhine arendus, mitmemõõtmeline valideerimisprotokoll, väited ja tulevikutöö.

## Kiirhinnang
Põhinarratiiv on tugev alates realt 121: standardsete benchmarkide ja päriskasutuse lõhe ning sellest tuletatud mitmemõõtmeline hindamisprotokoll. Suurim kärpevajadus on ridadel 18-119, kus põhitekst muutub reprodutseeritavus-READMEks: failiteed, Kotlin-klassid, skriptikutsed, mudelikonfigid ja täpsed parameetrid tuleks põhiosas asendada lühikese metoodilise kokkuvõttega ning viia lisasse.

## Klassifikatsioon ja soovitatud tegevus

| Read | Otsus | Põhjendus | Soovitus |
|---|---|---|---|
| 1 | KEEP | Hea avav tees: klipitaseme head skoorid ei taga streaming-käitumist. | Jätta, aga kasutada seda ainsa üldise algusõigustusena. |
| 3-6 `Miks avalik kontrollkatse oli vajalik` | COMPRESS | Avaliku kontrollkatse vajalikkus on sisuline, kuid kordab rida 1 ja kõlab kaitsekõnena. | Lühendada 1 lõiguks: `marvin` kontroll de-riskis treeningutoru ja paljastas taustaheli komponendi puudujäägi. Rida 6 üldist kordust kärpida. |
| 8-11 `Miks kahe raamistiku võrdlus tugevdab tööd` | COMPRESS | Rida 9 sisaldab vajalikku microWakeWord vs openWakeWord kompromissi; rida 11 kordab üldist “tugevdab tööd” põhjendust. | Jätta konkreetne tehniline kompromiss, pealkiri muuta neutraalsemaks (`Raamistikuvaliku põhjendus`). Rida 11 kas eemaldada või siduda ühe lausega tulemuse/sihtplatvormiga. |
| 13-16 `Domeeninihke mõju` | KEEP / COMPRESS | Domeeninihe on peatüki jaoks oluline, kuid “telefon vs kaugmikrofon” on hüpoteetiline ning hiljem real 29 tagasi täpsustatud. | Sõnastada otse Kratti riski ümber: mikrofoni/ruumi/kõnelejate mitmekesisus ja taustaheli. Vältida hüpoteesi, mis kohe ümber lükatakse. |
| 18-31 `Positiivse klassi kogumisprotokoll` | MOVE TO APPENDIX + COMPRESS | Vajalik reprodutseeritavuseks, kuid põhitekstis liiga detailne: seade, formaadid, mic1/mic2 arvud, ruumikirjeldus. | Põhiteksti jätta 2-3 lauset: Korvo-2, 1076 klippi, üks kõneleja, TTS/XTTS laiendus ja holdout. Bullet-list lisasse. Rida 29 kaob, kui domeeninihe ümber kirjutada. |
| 33-42 `Sarnaste negatiivnäidete kogumisprotokoll` | MOVE TO APPENDIX + COMPRESS | Foneetilised hard negative’id on sisuliselt olulised, kuid VAD parameetrid, mustrikoodid ja täpsed töövood koormavad peatükki. | Põhiteksti jätta: 100 foneetiliselt lähedast fraasi, TTS + Korvo salvestused, ei lisatud FAPH-taustasse, sõltumatu Mac holdout. Rida 39 VAD-detailid lisasse. |
| 44-52 `Androidi valevallandumiste logija` | MOVE TO APPENDIX | Täpselt kasutaja kriitika koht: Androidi failitee, `Settings.kt`, `DetectorConfig`, `AudioCapture.kt`, `EventLogger.kt`, `DetectionEvent`, `events.jsonl`, `logs/` loevad nagu README. | Põhiosas jätta ainult üks metoodiline lause: logija salvestas päriskasutuse valevallandumised ja negatiivseks lisati vaid käsitsi kinnitatud mitte-sihtfraasid. Kõik klassi-/konfigi-/tee-detailid lisasse või README-sse. |
| 54-73 `Treeningaja augmenteerimise parameetrid` | MOVE TO APPENDIX + KEEP 2 key points | Täpne augmentatsiooni ja arhitektuuri konfiguratsioon on põhitekstis liiga madala taseme detail. | Põhiteksti jätta ainult tõlgendust mõjutavad faktid: taustamüra/RIR segamine oli välja lülitatud (rida 58), SpecAugment/versioonierinevused mõjutasid katseid (57-59, 70-72), kontrollpunkt valiti accuracy järgi (64). Ülejäänu lisasse. |
| 75-88 `Voogedastushindamise parameetrid` | COMPRESS | FAPH protokoll on põhinarratiivi jaoks oluline, kuid Common Voice lõike skript, HF peegel, indeksid ja `compare_models.py` on README müra. | Jätta FAPH põhjendus, korpused, lävi, silumine, refraktoorperiood ja valem. Rida 79 skriptikäsk ja rida 87 skriptitee lisasse. |
| 90-99 `MoE-konsensushindamise parameetrid` | COMPRESS | Konsensuse tulemus on oluline, aga mudelifailide teed, KB suurused ja benchmark-skripti käsk pole põhiteksti materjal. | Jätta: kaks eksperti, freimitasandi AND, silumine enne kombineerimist, läved 0.996/0.996, FAPH=0.79. Ridade 94 ja 98 failiteed lisasse. |
| 101-115 `Reaalajas seadme-testi protokoll` | COMPRESS | Vajalik, sest benchmark-gap tugineb neile numbritele; siiski skriptiteed ja detailsed töövood saab kärpida. | Jätta n, kõnelejad, kaugus, testitud hard negative’id, käsitsi loendus ja statistiline piiratus (115). Ridade 105 ja 111 skriptiviited lisasse. |
| 117-119 `ESP32-S3 sihtseadmele juurutamise konfiguratsioon` | MOVE TO APPENDIX | Väga tihe ESPHome/YAML/manifest/config kirjeldus; peaaegu täielikult README/juurutusjuhendi toon. | Põhiteksti jätta 1 lause: sama TFLite artefakt juurutati Korvo-2/ESPHome seadmele sama cutoff’i ja silumisega. Kõik `gain_factor`, `tensor_arena`, `on_boot`, `voice_assistant.start`, manifesti teed lisasse. |
| 121-169 `Standardsete võrdlusaluste ebapiisavus...` | KEEP | Peatüki tugevaim sisuline osa: näitab benchmarkide ja päriskasutuse lõhet ning põhjendab uut hindamisvoogu. | Jätta põhiteksti. Võib kergelt tihendada rida 132 ja rida 169, et vältida kordust hilisema panuse-osaga. |
| 134-152 neli põhjust | KEEP / LIGHT COMPRESS | Hea struktuur; otse vastab “miks standardne hindamine ei piisa”. | Jätta alampealkirjad. Vajadusel ühendada Põhjus 3 ja 4 lühemateks lõikudeks. |
| 154-169 stsenaariumpõhine testimisvoog | KEEP | Annab selge metodoloogilise ettepaneku, mitte pelga kriitika. | Jätta. 2-tunnise protokolli list sobib põhiteksti; kirjandusviited hoida mõõdukalt. |
| 171-179 `Agentpõhine arendus...` | COMPRESS | Teema on huvitav, kuid kordab mitu korda “töövõimendaja, mitte tõendusmaterjali asendaja” ning loetleb tööriistu uuesti. | Suruda 1 lõiguks pärast metoodika-osa või jätta arutelu peatükki. Hoida mõte: agentid kiirendasid tööriistu, kuid ei asenda pärisandmeid. |
| 181-226 `Mitmemõõtmeline hindamisprotokoll...` | KEEP / COMPRESS | See on tõenäoliselt peatüki põhiväide. Samas kolm auditi-ringide lõiku on väga pikad ja sisaldavad taas failinimesid/skripte. | Jätta, kuid vormistada tabeliks: ring → avastatud lühitee → parandus → uus mõõdik. Failinimed (`manifest.json`, `audit_positive_sources.py`) lisasse või joonealusesse. |
| 184, 215-219 panuse/ülekantavuse väited | COMPRESS | Mitmes kohas korratakse, et panus pole “parim mudel”, vaid valideerimisprotokoll. | Hoida üks tugev panuse-lõik; rida 217 võib asendada rida 184 korduse. Rida 219 tööstusvõrdlus jätta lühendatult. |
| 221-226 `Aus piir: võimalik neljas ring` | KEEP / LIGHT COMPRESS | Aus piirang on kaitsmisel kasulik. | Jätta põhimõte, kuid lühendada näidete loetelu real 224. |
| 228-238 `Mida saab juba praegu väita` | KEEP / COMPRESS | Hea kokkuvõte, aga kordab alguse `marvin`, FAPH ja andmeriski väiteid. | Hoida bullet-list. Rida 233 jagada kaheks või lühendada; kui algus kärbitakse, võib `marvin` jääda siin kokkuvõtteks. |
| 240-242 `Edasised suunad: kaskaadarhitektuur` | COMPRESS / MOVE | Üks väga pikk kirjandus- ja tulevikutöö lõik; sobib pigem “edasised tööd” lõppu, mitte metoodilise auditi tuuma. | Lühendada 2-3 lauseks: konsensus on kaskaadi erijuhtum; järgmine aste võiks kontrollida `kuule`/`kratt` järjestust; risk on esimese astme lühitee. |

## README-müra, mida põhitekstist eemaldada
- Android/Kotlin detailid: read 45, 47-50, 51 (`android/.../falselog/`, `Settings.kt`, `DEFAULT_MODEL`, `AudioCapture.kt`, `DetectorConfig`, `EventLogger.kt`, `DetectionEvent`, `events.jsonl`, `logs/`).
- Treeningu/config detailid: read 55, 57-64, 68-72 (`generate_microwakeword_mmaps.py`, YAML, augmentation class, random seed, layer widths, class weights, checkpoint metric).
- Hindamisskriptid ja andmevaliku käsud: read 79, 87, 94, 98, 105, 111, 191, 193.
- ESPHome/Home Assistant detailid: read 117-119 (`voice-satellite...yaml`, manifest, `gain_factor`, `tensor_arena_size`, `on_boot`, `voice_assistant.start`).

## Soovitatud uus peatükivoog
1. Avatees + `marvin` kontroll + raamistikuvalik: read 1-11 kokku 2-3 lõiguks.
2. Domeeninihe ja andmete põhimõte: read 13-42 kokku lühikeseks metoodikaülevaateks, detailid lisasse.
3. FAPH/streaming hindamise minimaalne protokoll: read 75-99 tihendatult.
4. Benchmark-gap ja stsenaariumitest: read 121-169 põhiosas peaaegu alles.
5. Mitmemõõtmeline valideerimisprotokoll: read 181-226 põhiosa, aga tabelistada ja eemaldada failinimed.
6. Kokkuvõte ja tulevik: read 228-242 tihendada.

## Start Here
Alusta kärpimist ridadest 44-73 ja 117-119: need annavad suurima tekstivõidu ning sisaldavad kõige ilmsemat README/config müra. Seejärel tihenda alguse õigustused ridadel 3-11, et peatükk jõuaks kiiremini põhiväitena ridadeni 121-169 ja 181-226.
