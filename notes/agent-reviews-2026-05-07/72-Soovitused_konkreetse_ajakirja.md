---
source_prompt: 07_Teadusartikkel/Soovitused_konkreetse_ajakirja_jaoks.txt
prompt_type: evaluative
generated: 2026-05-07
---

# Toimetaja-hinnang: lõputöö potentsiaal teadusartikliks

## Eelmärkus: prompti lünk

Promptis on koht `<Sisesta ajakirja nimi>`, kuhu konkreetne ajakiri ei ole täidetud. Seetõttu ei saa käesolev hinnang olla rangelt ühe ajakirja "Aims and Scope" peale kalibreeritud ega viidata reaalajas tehtud veebiotsingu tulemustele konkreetse ajakirja viimaste numbrite kohta (käesolevas keskkonnas pole veebiotsingut käivitatud). Selle lünga raviks teen järgmist:

1. Hindan tööd kolme realistliku sihtkoha suhtes, mis selle töö profiili tegelikult katavad: (a) **Interspeech / ICASSP / ASRU** tüüpi konverentsi-paber (mitte ajakiri, kuid sama "gatekeeper"-loogikaga), (b) **Speech Communication** (Elsevier, kõnetöötluse ajakiri), (c) **Eesti Rakenduslingvistika Ühingu aastaraamat / ERÜ** või **Estonian Journal of Engineering / Proceedings of the Estonian Academy of Sciences** (kohalik, eestikeelne või kakskeelne, väiksema mõjufaktoriga, kuid valdkondlikult sobiv).
2. Annan iga sihtkoha kohta eraldi Go/No-Go hinnangu.
3. Viin läbi ühisosa: mida nõuab iga "karm peatoimetaja" sõltumata ajakirjast.

Kui Mattias soovib hilisemat täpsemat sihtimist, tuleb prompt täita konkreetse ajakirjanimega ning käivitada uuesti veebiotsingu õigustega.

---

## 1. Sobivuse otsus (Go / No-Go)

### Sihtkoht A — Interspeech / ICASSP (KWS / low-resource speech track)

**Hinnang: 55%** — **Go (kohandatuna, mitte sellisel kujul)**.

Põhjus: Töö metoodiline tuum (a) andmelekke audit, (b) positiivse klassi sildiaudit, (c) mitmemõõtmeline kontrollpunkti valikukriteerium ning (d) standardsete KWS võrdlusaluste ja päris kasutuse vahelise lahknevuse empiiriline dokumenteerimine on Interspeech'i KWS / robustness sessiooni jaoks **olemuslikult sobiv** sisu. Lopez-Espejo 2021 ülevaade ja MISP-laadne motivatsioon viitavad just sellisele tühimikule, kuhu töö asetub. Eestikeelsus on lisaboonus low-resource teemana, mitte takistus.

Põhjus, miks ainult 55% (mitte 70+): praegune empiiriline tugi on **piiratud kõnelejate arvuga** (kasutajatest 20–30 osalejat on alles planeeritav, mitte täidetud). Interspeech'i retsensent küsib esimese asjana "kui mitu päris kõnelejat?" ning vastus "kasutajatest käib" on praeguses faasis "Reject — premature". Kui kasutajatest enne esitamist (NB: deadline 2026-05-18 thesis, Interspeech submission cycle on tüüpiliselt märts) jõutakse läbi viia, tõuseb hinnang 70%-ni.

### Sihtkoht B — Speech Communication (Elsevier, full journal article)

**Hinnang: 35%** — **TAGASI LÜKATUD (REJECT)**.

Põhjus: Speech Communication ootab ajakirja-mahus tööd, kus on kas (i) uus mudeliarhitektuur tõestatud kõnelejate baasil, (ii) suuremahuline empiiriline uuring 50+ osalejaga, või (iii) selgelt uus metoodiline raamistik, mille üldistatavus on tõestatud rohkem kui ühe keele või sõna peal. Käesolev töö on **üks keel, üks fraas, üks platvormiklass, kitsas kõnelejate baas**. Metoodiline panus (kolm valideerimiskihti) on huvitav, kuid tõendusbaas on liiga õhuke ajakirja-tasemel artikli jaoks, eriti kui töö ise möönab "võimaliku neljanda ringi" piirangut.

Lõpetan vastuse selle sihtkoha osas siin.

### Sihtkoht C — Kohalik (ERÜ aastaraamat / Eesti TA Toimetised)

**Hinnang: 70%** — **Go**.

Põhjus: Eestikeelse äratussõna esimene dokumenteeritud katse ja kohalik metoodikapanus on kohaliku valdkondliku ajakirja jaoks **otseselt sobivad**. Ulatuse-piirangud, mis tapavad Speech Communication'i sobivuse, on siin pigem voorus: ühe keele üks sõna on kohaliku ajakirja jaoks asjakohane skoop. Riskiks jääb, et töö metoodiline raskuskese (audit-protokoll) võib kohalikku auditooriumi vähem huvitada kui rahvusvahelist KWS-kogukonda.

---

Edasi ainult sihtkohtade A ja C kohta (B sai Reject).

## 2. Teisenduse plaan: lõputööst artiks

Lõputöö on praegu ${\sim}80$+ lk struktuur, mis ei mahu ühtegi artiklisse. Kärbe on halastamatu.

### Mida halastamatult välja visata

- **Kogu raamistike võrdlus microWakeWord vs openWakeWord** (teine peatükk, "Võrdlusraamistik" ja seotud osad). See on lõputöö-tasemel kohustuslik vormistuselement, kuid ajakirja-artikkel ei saa endale lubada nelja-teljelist tooliuuringut. Säilita ainult üks lause: "valitud raamistikuks on microWakeWord ESP32-S3 sihtplatvormi tõttu" + üks viide.
- **Mudeli arhitektuuri pikk kirjeldus** (MixedConv plokid, SVDF-kihid, kontekstiakna pikk arutelu, SpecAugment'i kirjeldus). Need on kõik standardsed ehitusplokid; piisab ühest joonisest + 1–2 lauset. Üliõpilastöö stiilis pedagoogiline ekspositsioon (mida teeb depthwise vs pointwise konvolutsioon) tuleb täielikult välja.
- **Agentpõhise arenduse osa** (kolmanda peatüki §). See on lõputöö-poliitiline kontekst (TI deklaratsiooni aluseks), mitte teaduspaberi sisu. Kui üldse jätta, siis ühe lausena meetodites ("tooling implementation was assisted by LLM coding agents; substantive scientific decisions were made by the author").
- **Kasutajatesti metoodika kirjeldus** ulatuses, milles see on planeeritav, mitte täidetud (§\ref{sec:user-test-methodology}). Ajakirja-artikkel ei kirjelda tulevikus tehtavat tööd.
- **Avalik marvin-kontrollkatse põhjenduse pikk arutelu** (kolmanda peatüki algus). Üks lause meetodites: "pipeline was sanity-checked on Speech Commands `marvin` before applying to Estonian data."
- **FAPH-i nelja variandi taksonoomia** (§\ref{subsec:faph-variants}). Vajalik metoodikalisa, mitte põhitekst.
- **Ülesandepüstitus, sissejuhatuse "töö struktuur" lõik, kokkuvõte praegusel kujul.** Ajakirja-artiklis pole neid vaja.

### Üks väide, millele artikkel keskendub

Kahel sihtkohal erinev fookus.

**Sihtkohale A (Interspeech)** — keskenda *ühele* metoodikaväitele:

> "Standard KWS benchmarks (clip-level recall on cloned-TTS positives, FAPH on dense-speech corpora, isolated hard-negative clips) systematically *over*-predict deployment quality for low-resource wake words. We show this with a 15+ version Estonian case study and propose a three-layer audit protocol (held-out leakage check, positive-class label audit, multi-criterion checkpoint selection) that exposes the gap."

Tehniline tõestus: tabel kahe-kolme mudeliversiooni vahel, kus benchmark-edetabel ja kasutuskogemuse-edetabel lähevad lahku. Üks joonis: "benchmark FAPH vs field FAPH" scatter, kus diagonaalist kõrvalekalle on visuaalselt jälgitav.

**Sihtkohale C (kohalik ajakiri)** — keskenda artikkel narratiivile "esimene eestikeelne äratussõna mudel ja selle hindamise õppetunnid". Sissejuhatusena Eesti hääleassistentide ökosüsteemi lünk, tuumana sama auditi-protokoll kuid lihtsamal kujul, lõpus konkreetne juurutusartefakt (mudel + ESPHome integratsioon).

## 3. "Desk Reject" vältimise strateegia (tehniline tase)

### Vormistuslikud nõuded

**Sihtkoht A (Interspeech 4-page paper):**
- 4 lehekülge + viited, IEEE/ISCA template. Praegune töö on TalTechi LaTeX šabloonis — kogu vormistus tuleb migreerida.
- Bibliograafia stiil: IEEE numeric. Mõned senised viited (`microwakeword2026`, `openwakeword2026`, `homeassistant2026`) on **veebilingid kuupäevaga "viimati vaadatud"** — ajakirja jaoks nõutakse archived snapshot või versioonisiltide täpsust (commit hash, release tag). Praegune kuju saaks desk-reject'i tehnilise viite-puuduse pärast.
- Joonised: 300 DPI, ingliskeelsed sildid (eesti tekst figuuridel = automaatne tagasi).
- Anonümiseerimine vastavalt double-blind nõudele (kui ajakiri seda nõuab) — kogu "Mattias", "TalTech HPC", "Kratt" projekti-spetsiifiline raamistus tuleb meetodites ümber kirjutada anonüümsesse vormi.

**Sihtkoht C (kohalik ajakiri):**
- ${\sim}10$–15 lk, eesti keeles (mis on praegu juba olemas).
- Vähem ranged anonüümsuse ja arhiveerimise nõuded.

### Kaaskirja ja abstrakti müügiargumendid

Praegune eestikeelne abstrakt on **liiga lõputöö-stiilis**: räägib "rekonstrueerimisest", "täpsustamisest", "valideerimiskihtidest". Ajakirja abstraktil on kolm asja: (1) probleem ühe lausega, (2) panus ühe lausega, (3) tulemus ühe arvuga.

Müügiargument peab kõlama:

> "We document a systematic gap between standard KWS benchmarks and deployment quality for low-resource wake words: in 15+ Estonian model versions, benchmark ranking did not predict real-speaker recall ranking. We propose a three-layer audit protocol that exposed leakage, label-class drift and shortcut learning that single-metric evaluation hid."

NB: see on **negatiivne tulemus** valdkonnale (benchmark'id ei tööta) + **positiivne metoodikapanus** (audit-protokoll). Praegune abstrakt müüb pigem "tegime ühe mudeli", mis on kaaskirja jaoks nõrk.

### Keelekasutus ja stiil

Praegune eestikeelne tekst on **liiga arutelu-keelne** ("Käesoleva töö ... ei piisa ... pealtnäha hea tulemus võib olla eksitav"). Ajakirja-artikkel kasutab kuiva, deklaratiivset stiili. Kõik "võib olla", "tundub", "praktiliselt" tuleks kas eemaldada või asendada konkreetse arvuga.

## 4. "Reviewer Reject" vältimise strateegia (sisuline tase)

### Uudsuse tõestamine

Kõige keerulisem osa. Töö ise möönab korduvalt, et:
- Mitme-mõõdikuline KWS hindamine **pole uudne** (Apple, Picovoice, openWakeWord raporteerivad samuti mitut mõõdikut).
- Kaskaadarhitektuuri idee on tuntud (Gruenstein 2017 jt).
- Andmeleke kui probleem on üldteada.
- Eesti keel kui esimene-keelne KWS pole iseseisvalt piisav novelty rahvusvahelise ajakirja jaoks (Sihtkoht B kukutab just selle peal).

Mis siis ON uus?

1. **Empiiriline dokumentatsioon konkreetse versioonidevahelise lahknevuse kohta** ühe low-resource keele 15+ iteratsiooni peal. Kirjandus mainib lahknevust üldiselt; käesolev töö annab **arvu**.
2. **Kolme-ringi auditi-protokoll kui replikatsioonijuhend** teiste low-resource projektide jaoks (transferability claim §\ref{sec:contribution-transferability}).
3. **"Hindamise piirid kui treenitavad lühiteed"** (§\ref{sec:general-principle}) — see formulatsioon on minu nähtuna kirjanduses harvem ja hästi väljendatud. Seda peaks artiklis tugevdama Goodhart'i / specification gaming kirjandusele viitega.

Risk: retsensent ütleb "this is just standard ML hygiene applied to KWS, not a new contribution". Vastutõestus peab olema konkreetne: tabel "what each round caught that prior single-metric evaluation missed" + üks number iga rea kohta.

### Metoodilised nõrkused, mis tuleb enne esitamist parandada või ausalt tunnistada

1. **Kõnelejate baas kitsas.** Kui kasutajatest pole esitamise hetkeks tehtud, peab Limitations osas olema ühene tekst: "claims about real-speaker recall are based on N=K speakers; user study with 20–30 participants is in progress and findings will be reported in a follow-up." Mitte peita.
2. **TTS-positive treening + TTS-positive eval** topelt-paisutab tuvastamismäära (peatükk seda mainibki). Artiklis peab see olema **selgelt eraldi joonisena** ("controlled inflation") koos numbriga.
3. **FAPH variandid pole otseselt võrreldavad** (§\ref{subsec:faph-variants}). Iga numbri juurde tuleb märkida variandi nimi. Praegune tekst on selles juba korralik, aga retsensent küsib ikka.
4. **Ühe-fraasi piirang.** Töö ei kontrolli, kas auditi-protokoll töötab teise eestikeelse fraasi peal. See piirang tuleb ausalt tunnistada (üldistatavuse väide on hetkel disainisoovituslik, mitte tõestatud).
5. **"Komposiitne kontrollpunkti valikukriteerium"** ei ole peatükis kvantifitseeritud — kuidas täpselt mitut mõõdikut kombineeritakse? Pareto frontier? Skalaarne kaal? Lävekombinatsioon? Retsensent kindlasti küsib. Praegune tekst räägib põhimõttest, mitte algoritmist.
6. **Statistiline tugi.** Hea, et Wilson + Garwood-Poisson + kolmereegli on kasutusel. Retsensent kontrollib, kas iga raporteeritud arvu kõrval on usaldusvahemik või ei ole. Praegune sissejuhatus mainib "0,79 FAPH" konkreetse vahemiku kõrval ainult "lai vahemik" sõnaliselt — seda peab näitama numbrina, ka tabelis.

### Kas tulemused on piisavalt üldistatavad?

**Aus vastus: ei.** Töö katab ühe keele, ühe fraasi, ühe platvormiklassi, ühe sünteetilise positiivse allika. Üldistatavuse väide on **disainisoovituslik** (auditi-protokoll on ülekantav teistele projektidele), mitte tõestatud. See on ühtlasi põhjus, miks Sihtkoht B (Speech Communication) saab Reject — seal nõutakse rohkem.

Sihtkohale A (Interspeech) on see piirang aktsepteeritav, KUI artikkel raamistab end **case study + protocol proposal** žanrina, mitte "general method" žanrina. Kaaskirjas peaks see olema eraldi rida: "we present this as a case study; the protocol is offered as a hypothesis for transferability, not a proven generalization".

---

## Kokkuvõtlik tegevussoovitus

Kui Mattisel on aega ja kasutajatest jõuab valmis enne 2026 sügist, **on Interspeech 2027 (või EUSIPCO / SLT 2026) realistlik siht**. Kui aega pole, tee Sihtkoht C (kohalik ajakiri) — see on alla-50% riski variant, kus töö praegune kuju saab adapteeritud 12–15 lk peale ilma uue empiirikata.

Sihtkoht B (Speech Communication või sarnase profiiliga full journal) jäta kõrvale, kuni on olemas (a) 50+ osalejaga kasutajatest VÕI (b) auditi-protokolli replikatsioon teisel keelel/fraasil. Praeguse tõendusbaasiga see desk-reject'iks läheb.
