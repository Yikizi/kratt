# Lk 1–70 kriitika destilleeritud backlog (2026-05-15)

Allikas: viimased 70 Claude sessiooni `~/.claude/projects/-Users-mattias-kratt/` + auditid `/tmp/kratt-critique-audit/audit-*.md`.

Eesmärk: kasutada kriitikat **tegevusloendina**, mitte pimesi paranduskäsuna. Iga muudatus peab jääma lõputöö esitamise kriitilisele rajale.

## Triage reeglid

- **P0**: kaitsmisel/esitamisel piinlik või sisuliselt riskantne; paranda enne järgmist PDF-i.
- **P1**: parandab loetavust, kaitstavust või reprodutseeritavust; tee pärast P0-d.
- **P2**: maitse/vormistus/paigutus; tee ainult kui ei ohusta tähtaega.
- Leheküljenumbrid on osaliselt nihkes, sest osa agente luges `loputoo.pdf` või varasemat `main.pdf`. Tee parandust **sisu järgi**, mitte ainult lehenumbri järgi.

## P0 — enne järgmist thesis closeout PDF-i

| ID | Teema | Kriitika sisu | Konkreetne tegevus | Failid / ala | Vastuvõtukriteerium |
|---|---|---|---|---|---|
| PC-P0-01 | Bibliograafia korrastus | Lk 65–70 viidetes on sisekommentaare, katkisi venue-välju, ebaühtlane `Accessed`, puuduvad leheküljed ja võimalikud valed allikatüübid. | Puhasta `references.bib`: eemalda annotatsioonid bibliokirjetest; paranda [18], [41], [44], [45]; ühtlusta `urldate`/vaadatud stiil; lisa venue/leheküljed ICASSP/Interspeech kirjetele. | `docs/thesis/thesis-tex-estonian/references.bib` | PDF bibliograafia ei sisalda kommentaar-lauseid nagu “introduces …”; [44] pole enam “Teoses: 2017”; stiil on ühtlane. |
| PC-P0-02 | Annotatsioon + abstract + kokkuvõte | Töö lubab prototüüpi, aga tegelik tugev panus on hindamisprotokoll; kvantitatiivsed võtmetulemused on liiga nõrgalt esil. | Lisa 2–3 võtmenumbrit: parim ambient FAPH koos recall/selektiivsuse hinnaga; ütle selgelt, et ükski mudel ei täida kõiki tingimusi korraga; raami panus “prototüüp + hindamisprotokoll”. | `misc/abstract-estonian.tex`, `misc/abstract-english.tex`, `chapters/summary.tex` | Annotatsioon/abstract/kokkuvõte sisaldab numbrilist tulemust ja ei jäta production-ready muljet. |
| PC-P0-03 | Mõõdikute raam | FAPH/FPR/FRR/DET ning FAPH < 1 põhjendus on hajus; FAPH ja FPR eristus vajab paremat lauset. | Sõnastikus ja metoodikas lisa lühike eristus: FAPH = ajapõhine pidevvoog, FPR = näidetepõhine testikomplekt; “ROC-laadne” täpsustada DET/threshold curve’ina; FAPH < 1 kasutajavaate põhjendus pehmendada. | `misc/terms_abbreviations.tex`, `chapters/introduction.tex`, `chapters/first_chapter.tex` | Lugeja saab enne tulemusi aru, miks kasutatakse FAPH-i ja FPR-i eri kohtades. |
| PC-P0-04 | Andmeleke ja ümberarvutatud tulemused | Andmeleke/XTTS-kloon/uue kõneleja üldistus on kaitsmisel lihtne rünnakukoht. | Ütle tulemuste peatükis selgelt: millised varased tulemused olid eksitavad; mis muutus pärast mittekattuvuse kontrolli; `pos_speaker_a_xtts` ei ole sõltumatu päris kõneleja. | `chapters/second_chapter.tex` | Tekst eristab “XTTS-kloon”, “päris kõneleja”, “held-out” ja “ümber arvutatud” staatuse. |
| PC-P0-05 | N-id ja usaldusvahemikud | Mitmes tabelis/lõigus on “100%”, “enamik”, “üksikud”, “0,00” ilma N/toorloendi või ülemise piirita. | Lisa N ja/või toores loend kõikjale, kus järeldus sõltub väiksest valimist: Mac 40-min FAPH, käsitsi kuulamine, H2 100%, prefix/confusable komplektid. | `chapters/second_chapter.tex` tabelid/lõigud | Iga protsendi või nulltulemuse juures on N, tundide arv või UV/ülemine piir. |
| PC-P0-06 | Checkpoint-FAPH / konsensus | Madal FAPH võib tähendada, et mudel on vait, mitte et ta tunneb fraasi. | Too see järeldus varem ja teravamalt: FAPH-only checkpointing = Goodharti/lühitee risk; madal FAPH peab alati olema koos recall + confusable FPR-iga. | `chapters/second_chapter.tex`, `chapters/third_chapter.tex` | Ükski lõik ei müü FAPH 0,00 või sub-1 tulemust ilma recall/selektiivsuse caveat’ita. |
| PC-P0-07 | User-test / freeze claim | Kui külmutatud kasutajatesti andmeid pole, ei tohi tulemuste tekst neid lubada. | Täida freeze-policy või kirjuta thesis tekstis ausalt “policy candidate / limitation”; ära jäta tühje tulemusetabeleid. | `docs/user-testing/frozen-threshold-policy.md`, `chapters/first_chapter.tex`, `chapters/second_chapter.tex` | Freeze-väide on kas tõendatud kuupäeva/commit/model/thresholdiga või nimetatud piiranguks. |
| PC-P0-08 | Puuduv lk 47 audit | Viimases 70 sessioonis puudus lk 47 kriitika. | Käivita uus drift-kindel page prompt ainult lk 47 jaoks: `kratt thesis-page-critique --build --pages 47`, seejärel loe prompt/LLM vastus ja lisa käsitsi triage. | `.hermes/thesis-page-critiques/*` | Lk 47 on auditeeritud sama PDF SHA alusel kui ülejäänud closeout. |

## P1 — pärast P0-d, kui jõuab

| ID | Teema | Kriitika sisu | Konkreetne tegevus | Failid / ala | Vastuvõtukriteerium |
|---|---|---|---|---|---|
| PC-P1-01 | Tulemuste peatükk kui changelog | 3.4–3.6 on kohati eksperimendipäevik, mitte kompaktne teaduslik tulemus. | Tihenda kronoloogiat: iga alajaotus peab lõppema ühe “mida see tõendab / ei tõenda” lausega; eemalda duplikaatsed mudeliajaloo seletused. | `chapters/second_chapter.tex` | Peatükk loeb kui tõendusketi analüüs, mitte mudeliversioonide logi. |
| PC-P1-02 | Tabelite legendid | Lühendid nagu HN, Tuv., Pre/1K/Conf, `[< u95]`, CV/Mac/LS on osalt tihedad või defineerimata. | Lisa tabeliallkirjadesse minimaalsed legendid; vajadusel split/shorten table 10–12. | `chapters/second_chapter.tex` | Tabelid on loetavad ilma eelnevat alapeatükki uuesti otsimata. |
| PC-P1-03 | Hard-negative/fraasilähedased negatiivid | Andmeliikide metoodika ei rõhuta piisavalt, et confusable/prefix negatiivid on eraldi riskiklass. | Lisa metoodikas lühike eristus: üldnegatiiv vs taustaheli vs fraasilähedane negatiiv. | `chapters/first_chapter.tex` | Täpse fraasi selektiivsus on metoodikas enne tulemusi nähtav. |
| PC-P1-04 | Arhitektuuri tehniline täpsus | SVDF/MixedConv seos, BC-ResNet, kontekstiaken ja kvantiseerimine on kohati liiga üldistavad. | Piiritle “põhineb ideedel” vs “sama kiht”; paranda pseudo-IPA, lisa hüperparameetri põhjendus või ütle, et see on raamistikust pärinev seadistus. | `chapters/first_chapter.tex` | Ei jää muljet, et MixedConv = SVDF või üks tsitaat tõestab kõiki arhitektuurivalikuid. |
| PC-P1-05 | Tehnoloogiapinu | “Nelja komponendi” loendus ei klapi tegeliku loeteluga; Korvo-2/treeningutaristu/reprodutseeritavus jääb nõrgaks. | Muuda loendus kas “mitmest komponendist” või täpseks 4 komponendiks; maini Korvo-2 ja Python/eval toolingut lühidalt. | `chapters/first_chapter.tex` | Loenduse arv klapib tekstiga. |
| PC-P1-06 | Positiivsete kvaliteedikontroll | v17/SSML/kestusvärav on töö tugev metoodiline leid, aga vajab kvantifitseerimist. | Tabel 9 juurde N/% või auditi protokoll; kestusvärava 0,80–4,00 s põhjendus. | `chapters/second_chapter.tex` | Positiivsete andmete puhastuse leid pole anekdootlik. |
| PC-P1-07 | Lõppmulje | Kokkuvõte lõpeb liiga defensiivselt “valideerimata kandidaadi” piiranguga. | Lõpeta panuse lausega: mida töö annab järgmisele tegijale, mitte ainult mida see ei tõenda. | `chapters/summary.tex` | Viimane lõik on aus, kuid mitte allaandev. |

## P2 — ignoreeri või tee ainult lõpus

- Lehekülgede valge ruum ja float-paigutus, kui see pole enam praeguses `main.pdf`-is probleem.
- Väited, mis põhinesid vanal `loputoo.pdf`-il või nihkunud lehekülgedel, eriti lk 22, 25–28, 35, 38, 51–53.
- “20–30 osalejat” kriitika — praegune töö räägib kuni 10 osalejast.
- Puhtad stiilimaitse küsimused (“pealkiri kõlab manifestina”, “poeetiline”) enne sisulisi P0/P1 parandusi.
- Väliskontrollita väited TalTechi AI-deklaratsiooni, Apple/Sensory/Samsung allikate või peer-reviewed protsendiläve kohta; kontrollida enne muutmist.

## Kriitika-süsteemi parandused järgmiseks jooksuks

Rakendatud repo muudatus:

- Lisatud `kratt thesis-page-critique` / `scripts/thesis_page_critique_packet.py`.
- Tööriist loob ühe **kanoniseeritud PDF-paketi**: `manifest.json`, `pages/page-NN.txt`, `prompts/page-NN.md`, `run-claude.sh`.
- Prompt sisaldab `main.pdf` SHA-256, page count’i, genereerimise aega ja lehe tekstiekstrakti.
- Prompt keelab sibling-PDF-id (`loputoo.pdf`, `ylesandepystitus.pdf`, ülesandepüstituse PDF) kui kasutaja pole neid eksplitsiitselt valinud.
- Vaikimisi katkestab tööriist, kui `main.pdf` on allikafailidest vanem; kasuta `--build`, et enne promptide loomist PDF uuesti kompileerida.

Soovitatud järgmine full-run:

```bash
kratt thesis-page-critique --build --pages 1-70 --out .hermes/thesis-page-critiques/$(date +%Y-%m-%d_%H%M%S)-main
# seejärel kasuta loodud prompts/*.md või run-claude.sh
```

Kui eesmärk on ainult puuduv lk 47:

```bash
kratt thesis-page-critique --build --pages 47
```
