---
source_prompt: 04_Kontrollimine/Üldisem_tagasiside/Hindamine_ükskiktöö.txt
prompt_type: evaluative
generated: 2026-05-07
---

# Lõputöö hindamine: "Eestikeelne äratussõna piiratud ressursiga nutikodu mikrokontrolleril"

## 1. Hinne (skaalal 0-5): **4 (väga hea)**

## 2. Lühike põhjendus

Lõputöö saab koondhindeks 4/5.

### Sisuline lahendus ja analüüs

**Hinnang: väga hea, tugevuste poolest 5-le kalduv.**

**Tugevused:**
- *Ülesande püstitus on selge ja korrektselt piiritletud.* Sissejuhatus sõnastab põhiküsimuse ("kuidas luua ja hinnata eestikeelset äratussõna tuvastust nii, et see oleks usaldusväärne nutikodu mikrokontrolleri piiratud ressursi tingimustes?") koos nelja konkreetse alamküsimusega ja tunnistab teadlikult töö piiranguid (üks äratusfraas, piiratud kasutajauuring, mitte täielik STT/TTS toru). Operatsionaalne sihtmäär (FAPH < 1, lähikõne tuvastamismäär $\geq$ 0,95) on eksplitsiitselt seatud projektispetsiifiliseks otsustuskriteeriumiks, mitte universaalseks standardiks.
- *Teema aktuaalsus ja uudsus on tugevalt põhjendatud.* Töö täidab selgelt dokumenteeritud tühimiku — eesti keel ei kuulu openWakeWordi ega Picovoice Porcupine'i toetatud keelte hulka, ning töö on autori kontrollitud otsingu järgi esimene avalikus kirjanduses, mis kasutab eesti ASR-mahus korpusi (TalTechNLP, Riigikogu stenogrammid jt) KWS-negatiividena.
- *Lahenduse mõistlikkus ja teostus on ulatuslikud.* Töö esitab täisahelat: andmete eristamine (positiivsed / negatiivsed / taustaheli), avaliku marvin-kontrollkatse kui torude valideerimissamm enne eestikeelse ülesande juurde liikumist, MixedNeti arhitektuuri parameetriline kirjeldus, kvantiseerimise ja tensor-arena mahuhinnangud ESP32-S3 jaoks. Kontrollitud ablatsioonid (v6 vs v6-residual; v13a vs v13b SpecAugment) on metoodiliselt eraldatud süsteemivariantidest, mis on autori enda poolt eksplitsiitselt välja toodud distsipliin.
- *Alternatiivsete lahenduste analüüs on põhjalik.* Võrreldakse microWakeWord vs openWakeWord neljal teljel; Picovoice Porcupine'i väljajätt on põhjendatud (suletud lähtekood, eesti keele tugi puudub); arutatakse kaskaadarhitektuuri (gruenstein2017cascade, Apple Hey Siri) ja ekspertmudelite konsensust, viidates HEiMDaL-i tulemustele.
- *Tulemuste valideerimine on töö silmapaistvaim tugevus.* Kolm dokumenteeritud auditiringi (andmeleke kõrvalejäetud komplektidega lahendatud; positiivse klassi reostuse audit fraasi-täielikkuse mõõdikutega lahendatud; FAPH-optimeeritud kontrollpunkti valiku lühitee-leid) annavad õpiku-näite enesekriitilisest tõendusdistsipliinist. Mõõdikute juurde lisatud Wilsoni ja täpse Poissoni-Garwoodi 95% usaldusvahemikud on bakalaureusetöö astme kohta erandlikult küpsed. FAPH-i loendusreegli neli varianti on §\ref{subsec:faph-variants}-s eraldi defineeritud.
- *Sisulise analüüsi maht on märkimisväärne.* 15+ mudeliversiooni süstemaatiline võrdlus, ristkeelne FAPH analüüs (LibriSpeech vs Common Voice ET), DET-tüüpi kõverate ja Pareto-mähise kasutamine ühe-läve hajuvuse esitamiseks, ekspertmudelite kalibreerimisefekt (Ekspert B v1 vs v2: HN FPR 100% → 13%) — kõik need on töö metoodilist sisu kandvad tulemused.

**Nõrkused:**
- Päris kõnelejate baas ühe peamise tuvastamismäära riski kohta (Kule-vorm) on jäänud kitsaks (Kõneleja D N=145 on hea, kuid Kõneleja B N=11 on liiga väike Wilsoni vahemike sisuliseks tõlgenduseks). Seda tunnistatakse ausalt §\ref{sec:fourth-round} ja kasutajatesti seisu jaotuses, kuid see jätab töö lõppjäreldused enamasti hindamismetoodika kohta käivateks, mitte deploy-otsuse kohta.
- Kasutajatest (planeeritud 20-30 osalejaga, vt §\ref{sec:user-test-methodology}) on kirjutamise hetkeks lõpetamata. Töö katab selle aususega, kuid see piirab töö empiirilist haaret.
- Mõned tabelis raporteeritud Mac-taustamonitori tulemused on saadud autori enda mikrofonil ja saavad lühitee-kahtluse ka töös endas (§\ref{sec:checkpoint-listening}); see on avatud probleem, mitte vaibapeale-pühitud.

### Lahendatava ülesande keerukus

**Hinnang: väga hea, kohati silmapaistev.**

Töö katab kolme erinevat tehnoloogilist tasandit: (a) ML-mudeli arendus (microWakeWord, MixedNet, kvantiseerimine, SpecAugment, residuaalühendused), (b) hindamismetoodika ja statistika (Wilson, Poisson-Garwood, FAPH-i varianditaksonoomia, mähised, DET-kõverad) ning (c) süsteemi-integratsioon (ESPHome, Home Assistant, ESP32-S3 mälupiirangud, sõltumatud Android-välikatsed ja Mac-taustamonitor). Lisaks on autor ise ehitanud vahetööriistu (Android valevallandumiste logija, `kratt user-test`/`replay-user-test`/`summarize-user-test` CLI-d) ja korraldanud HPC-treeningu (SLURM job-id-d on dokumenteeritud). Sisemine viidete- ja audit-distsipliin (mudelite NOTES.md, MODEL_LINEAGE.md, kvarantiinitud andmehulkade poliitika treeningskriptides) viitab pingutusele, mis on bakalaureusetöö astmelt selgelt üle ootuste. Agent-põhise arenduse roll on §\ref{sec:agentic} eraldi reflekteeritud — see on autori poolt teadvustatud osa metoodikakontekstist, mitte pinnataskuste kompenseerimiseks. Töö sügavus konkurentsivõimelise teadusliku panuse seisukohalt — väikese ressursiga keele kohaliku äratussõna mitmemõõtmeline valideerimisprotokoll — on selgelt tunnustatav.

### Vormistamine

**Hinnang: hea kuni väga hea.**

**Tugevused:**
- LaTeX-vormistus on professionaalne: BibTeX-viited on järjepidevad, joonistele ja tabelitele on viidatud `\ref`-iga, peatükkide ja jaotuste märgendid (`\label{...}`) on süstemaatilised.
- Allikate kvaliteet on kõrge: viidatud on otseselt asjakohastele rahvusvahelistele primaarsetele allikatele (Park et al. 2024 adversarial KWS, Dubois et al. 2020 triggers, Schönherr 2022, Apple Hey Siri 2017, Kundu et al. HEiMDaL, Park et al. 2019 SpecAugment, Wilson 1927, Garwood 1936, Hanley 1983 rule-of-three, Choi et al. 2021 BC-ResNet jt) ja korpustele (MUSAN, VOiCES, Common Voice, LibriSpeech, DiPCo, Speech Commands).
- Termivalik on järjepidev: ingliskeelsed terminid on tutvustatud sulgudes "ingl ..." vormis ning eesti keel on muidu järjepidev.
- Tasakaalustatus: sissejuhatus, metoodika, tulemused, arutelu ja kokkuvõte on iseseisvalt välja loetavad ning peatükkide proportsioonid on bakalaureusetöö ootustele vastavad. Tulemuste peatüki suur maht on põhjendatud tegeliku tõendusmaterjaliga.

**Nõrkused:**
- Tulemuste peatükk (~686 rida) on tihedalt tabeli-küllane ja mõnevõrra raskelt jälgitav esmakordsel lugemisel. Vahekokkuvõtted §-lõpus on olemas, kuid mõned tabelid sisaldavad palju veerge (eriti `tab:fair-comparison-holdout`, `tab:v18-family-results`) ja nõuavad lugejalt mitmekordset edasi-tagasi navigeerimist. See on vältimatu kompromiss tõendusmahu ja loetavuse vahel, kuid jääb ainsaks vormistuslikuks pingutuseks.
- Mõned terminoloogilised valikud kõiguvad ("recall" / "tuvastamismäär" / "saagis" — viimane esineb kokkuvõttes); ühtlustamine kogu tekstis tugevdaks loetavust.
- Üksikud kohad, kus tabelite footnote-id on pikad ja võiksid liikuda teksti sisse selguse huvides (nt `tab:expert-consensus` $u_{95}$-väärtuste tabel-headerisse paigutatud loend).
- Sissejuhatus on tihe ja sisaldab esimese lõigu lõpus pikka klauslit ("Mikrokontrolleri-klassi äratussõna tuvastusele on rahvusvaheliselt olemas..."), mille võiks rütmi parandamiseks jagada kaheks lauseks.
- Üks kirjaviga märgatav: "kuuekohnumbrelise" (kavatsetud "kuue suurusjärgu" vms; kontrollida §\ref{sec:data-leakage} ümbruses) — soovitada veelkordset õigekirjakontrolli enne lõplikku esitamist.

### Kokkuvõttev põhjendus koondhindele

Töö sisuline tugevus — auditi-distsipliin, statistilise kindluse väljatoomine, erinevate mõõdikute eristamine projektipõhiselt ja korraga väikese ressursiga keele kontekstis teostatud praktiline süsteem ESP32-S3-l — on selge **viie** taseme kandidaat. Töö lahendatava ülesande keerukus on **viie** taseme kandidaat ka, sest see ühendab ML-i, statistika ja süsteemi-integratsiooni tasandid ühe inimese töömahuks erakordselt laialt. Vormistus on **nelja** taseme kandidaat.

Koondhinde **4** (väga hea, mitte 5 silmapaistev) põhjendus seisneb järgmises:

1. **Empiiriline jääkpiirang.** Töö tunnistab korduvalt (sissejuhatus, §\ref{sec:fourth-round}, kokkuvõte, §\ref{sec:user-test-results}), et lõplik deploy-väide sõltub veel käimasolevast 20-30 osalejaga kasutajatestist, mis ei ole kirjutamise hetkeks lõpetatud. Selle täismahus tulemus on "neljas valideerimisring", mille võimalikkust töö ise kuulutab. Hinde 5 silmapaistvuskriteerium ("kõik kriteeriumid on täidetud silmapaistvalt") eeldaks, et see ring oleks lõpetatud või vähemalt eelregistreeritud pilootandmestik raporteeritud.
2. **Tuvastamismäära jääkprobleem.** Kõige usaldusväärsem konsensuslahendus (Ekspert A + B v2 @ 0,997/0,997) saavutab CV ET FAPH 0,8, mis on töö operatsionaalse FAPH < 1 sihi sees, kuid Kõneleja A XTTS unseen-kõneleja tuvastamismäära 31% (15/48) juures — see on selgelt allpool seatud lähikõne tuvastamismäära $\geq$ 0,95 sihti. Töö sõnastab selle ausalt avatud riskina (Kule-vormi tuvastamismäär), kuid see jätab kahe operatsionaalse sihi vahelise lõhe lahtiseks.
3. **Vormistuse väiksed parandused.** Tulemuste peatüki tabeli-tihedus, mõned kõikuvad terminid ja üksikud õigekirjavead on hindes 4 normaalselt aktsepteeritavad ("pisivead vormistuses... on aktsepteeritavad, kui sisu ja keerukus on tugevad"), kuid ei kvalifitseeru hindeks 5.

Ükski kolmest peakriteeriumist ei vasta hindele 0; null-reegel ei rakendu. Töö annab tugevama panuse hindamismetoodikasse ja tõendusprotokolli kui konkreetsesse mudeliartefakti ja autor seda eksplitsiitselt teadvustab — see ausus on iseenesest töö üks tugevamaid külgi ja õigustab kindlat hinnet "väga hea" hinde "hea" asemel.

**Otsus: 4/5 (väga hea).** Kui kirjutamise lõpp-faasis õnnestub kasutajatestist lisada vähemalt 10 osaleja külmutatud-läve replay-tulemused koos Wilsoni 95% usaldusvahemikega, oleks töö hinde 5 jaoks reaalne kandidaat — kuid praeguse seisuga, kus § \ref{sec:user-test-results} jätab tabelite koha tühjaks ja seab edasised väited eraldi seisva sõltuva sammu sisse, on hinne 4 õiglane.
