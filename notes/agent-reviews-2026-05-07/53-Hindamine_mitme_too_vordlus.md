---
source_prompt: 04_Kontrollimine/Üldisem_tagasiside/Hindamine_mitme_töö_võrdlus.txt
prompt_type: evaluative (mitme töö võrdlev hindamine)
generated: 2026-05-07
---

# Hindamine: mitme töö võrdlus

## Rakendatavuse märkus

Promptis eeldatakse **mitut PDF-ina edastatud lõputööd**, mida saaks omavahel võrrelda ja millele anda relatiivne hinne. Käesolevas keskkonnas on edastatud ainult **üks töö** (Mattias Linholm, "Kuule Kratt": eestikeelse äratussõna mudel ja selle hindamine ESP32-S3 nutikodu satelliidil). Seetõttu pole võimalik teha tegelikku **võrdlevat** hindamist (st öelda, et töö X on töös Y tugevam kriteeriumis Z), küll aga saab kasutada ettenähtud rubriiki ja skaalat üksiku töö ranglemiseks. Allpool on tehtud just see: prompti rubriigi range rakendus käesolevale ühele tööle, koos lühikese märkega, kus võrdlev raamistik oleks andnud lisaväärtust.

---

## 1. Lõputöö pealkiri ja autor

**Pealkiri (eesti):** "Kuule Kratt": eestikeelse äratussõna mudeli arendamine ja hindamine ESP32-S3 põhisel nutikodu satelliidil (täpne pealkiri töö konfiguratsioonifailis; ülesandepüstituses kasutatakse pealkirja makrot \texttt{\textbackslash thesisTitleEst}).
**Autor:** Mattias Linholm, TalTech, informaatika bakalaureuseõpe.
**Juhendaja:** viitega \texttt{\textbackslash supervisorNameEst}.

---

## 2. Hinne (skaalal 0–10): **7/10**

(viie palli skaalal: 4 — väga hea; nüansiga 7 selle alumises ots-otsas, st mitte kindel 8, sest empiiriline lõpptõendus — kasutajatest 20–30 osalejaga ja päris ESP32-S3 + ESPHome lõppintegratsioon — on töö enda sõnastuses veel teostamata "neljas valideerimisring".)

---

## 3. Lühike põhjendus

### Sisuline lahendus ja analüüs: **8/10**

**Tugevused.**
- **Ülesande püstitus on selge ja kitsendatud teadlikult.** Sissejuhatus ja ülesandepüstitus piiritlevad probleemi keskselt: eestikeelse äratussõna lünk avatud raamistikes (\texttt{openWakeWord}, Picovoice ei toeta eesti keelt) ristumisel mikrokontrolleri-klassi piirangutega. Põhiküsimus ja neli alamküsimust on eksplitsiitsed (sissejuhatus, lõik 4).
- **Teema aktuaalsus ja uudsus.** Teema on aktuaalne — väikeste keelte häälassistent — ja töö ise rõhutab korrektselt, et "esimese eesti äratussõna" väide on tõene, kuid tehniliselt tagasihoidlik tööstuslike süsteemidega võrreldes (3. ptk, §\ref{sec:contribution-transferability}). Uudsus paigutub ümber **tõendusprotokolli** tasemele: töö dokumenteerib kolm valideerimisringi (andmeleke → positiivse klassi audit → komposiitne kontrollpunkti valik) ja sõnastab nende üldistatava printsiibi "hindamise piirid kui treenitavad lühiteed". See on intellektuaalselt küps panus.
- **Alternatiivide analüüs.** Võrreldakse \texttt{microWakeWord} ja \texttt{openWakeWord} nelja konkreetse telje järgi (treenimine, mudelikvaliteet, integreeritavus, eesti-laiendatavus); Picovoice Porcupine on teadlikult välja jäetud koos põhjendusega (suletud lähtekood, eesti puudub, kohalik treenimine puudub). Edasiarendusena on välja toodud kaskaadarhitektuur (§\ref{sec:future-cascade}) konkreetsete viidetega (Apple, Google).
- **Tulemuste valideerimine.** Töö **iseseisev metoodiline panus** seisneb just valideerimisel: avalik kontrollkatse \texttt{marvin}-i peal enne eestikeelsele andmestikule liikumist, sõltumatud kõrvalejäetud komplektid, treening–testi kattuvuse kontroll, neli FAPH-i varianti (subsec~\ref{subsec:faph-variants}) erinevate loendusreeglitega ning Wilsoni / Poissoni-Garwoodi usaldusvahemikud koos kolmereegli rakendusega null-sündmuste korral. See on bakalaureusetöö kohta üle keskmise statistilise küpsuse tase.
- **Standardsete benchmarkide ebapiisavuse analüüs (§\ref{sec:benchmark-gap}).** Neli põhjust (klipi-tasemel recall ↛ reaalne kõneleja; tihe kõne ↛ kodune helimuster; isoleeritud rasked negatiivnäited ↛ streaming kontekst; mittekõneliste helide puudumine) on iga punkt seotud konkreetse kirjandusliku tõendusega (Park 2024, Dubois 2020, Schönherr 2022, Sensory 2024, MISP) ja konkreetse projekti vaatlusega.

**Nõrkused.**
- **Lõpptõendus pole veel käes.** Kasutajatest (20–30 osalejat) on alles **plaan** (§\ref{sec:user-test-methodology}); arutelu peatükk tunnistab seda ausalt "neljanda ringina" (§\ref{sec:fourth-round}). Promptis nõutava range hinnangu järgi on see oluline — "tulemuste valideerimine" kriteeriumi all ei saa täismahus pluss kategoorial olla, kui kõige kriitilisem välise valiidsuse kiht on tulevikus.
- **v16c kui "aktiivne kandidaat"** on kokkuvõttes märgitud reservatsiooniga ("eraldi kandidaat, mitte tootmisse rakendatav tõend"), kuid läbi töö on operatiivne sihtmäär (FAPH < 1, recall ≥ 0,95) projekti-spetsiifiline ja töö ise sõnastab selle korrektselt — kuid lugeja võib jääda mõtlema, kas siht on saavutatud. Konsensusmudel (expert-a + expert-b2) andis FAPH = 0,79 ühel korpusel ühel operatsioonipunktil; recall-pool jäi käimasolevasse kasutajatesti. Seega siht **on poolenisti saavutatud** ja töö ütleb seda otse — see on intellektuaalne ausus, mitte nõrkus, kuid lugeja vaatest jääb tulemus ebakindlamaks kui "saavutatud / ei saavutatud" binaarses lugemises.
- **Üksikud detailid jäävad mainituks, mitte mõõdetuks.** Mittekõnelised stiimulid (klaviatuur, ninakahin, taustamuusika) on §\ref{sec:benchmark-gap} all sõnaselgelt märgitud kui "süstemaatiliselt mõõtmata"; see on aus, kuid kriteeriumis "läbitöötatuse aste" jätab ühe lahtri tühjaks.

### Lahendatava ülesande keerukus: **8/10**

**Tugevused.**
- **Tõestatud nähtav maht.** Töös on dokumenteeritud 15+ mudeliversiooni (v1..v18 + v6-residual, v13a/v13b ablatsioon, v16c, expert-a/b2, v10, v15), kolm valideerimisringi koos auditite tulemustega, neli FAPH-i varianti, treeningutoru taastamine ja valideerimine \texttt{marvin}-il, ekspertide konsensus, Androidi valevallandumiste logija, ESPHome + Home Assistanti integratsioon ESP32-S3 Korvo-2 peal, ${\sim}99$~h välikatse, kasutajatesti tööriistastik (\texttt{kratt user-test}, \texttt{validate-user-test}, \texttt{replay-user-test}, \texttt{summarize-user-test}). See on bakalaureusetöö ootuste suhtes selgelt üle keskmise.
- **Intellektuaalne keerukus.** Töö ei piirdu ühe mudeli treenimise või ühe raamistiku rakendamisega; see paigutab end teadlikult **tõendusdistsipliini** raamistikku ja arutleb sellel tasandil (lühitee-mõtlemine, hindamise piirid, kompromiss recall ↔ FAPH ↔ fraasistruktuuri eksimused). Ülesandepüstituse kolm tasandit (mudel + integratsioon + valideerimine) on iseseisvalt mitteühestrukku ülesanded.
- **Reprodutseeritavus.** Iga FAPH-tabel identifitseerib kasutatud variandi; treening- ja hindamistoru on torustatud CLI-deks (\texttt{kratt}-perekond); Wilsoni ja Poissoni vahemikud on raporteeritud. See on samuti lisamaht, mida tüüpiline bakalaureusetöö ei sisalda.

**Nõrkused.**
- **Sisuline maht on kõrge, aga osa on "tööriistastik töö ümber", mitte teaduslik panus.** Agentpõhise arenduse paragrahv (§ "Agentpõhine arendus...") tunnistab seda korralikult — see on töövõimendaja, mitte teadusliku ranguse asendaja. Range hindaja võiks öelda, et osa nähtavast mahust on **arendusvahendite kiht**, mille tõenduskaal on kaudne. See ei alanda hinnet, kuid hoiab selle kriteeriumi pigem 8/10 kui 9/10 alas.

### Vormistamine: **7/10**

**Tugevused.**
- **Struktuur.** Sissejuhatus → Metoodika → Tulemused → Arutelu → Kokkuvõte on selgelt järgitav. Sissejuhatus formuleerib põhiküsimuse + neli alamküsimust + kolmeosalise panuse + piirangud (lõik 4); see on hea klassikalise akadeemilise vormi tunnus.
- **Viitamine.** BibTeX-keskne, viited katavad nii klassikat (Wilson 1927; Garwood 1936; Hanley 1983 — usaldusvahemike statistika), keskset KWS-kirjandust (Chen 2014, López-Espejo 2021, Sainath 2015, Choi 2021, Park 2019 SpecAugment, Alvarez 2019 SVDF, He 2016 ResNet) kui ka tööstuslikke ja hiljutisi tõendeid (Apple Hey Siri, Picovoice benchmark, Sensory, Dubois 2020, Schönherr 2022, Park 2024, Apple voice-trigger 2023, MISP Challenge 2022, Shrivastava 2021). Allikate kvaliteet on hea — vastastikku eelretsenseeritud + kirjastajatööstuse tehnilised raportid + projektidokumentatsioon, ja töö eristab korrektselt "projekti-spetsiifiline sihtväärtus" vs. "kirjanduses kehtestatud standard".
- **Mitmes kohas eksplitsiitne metoodiline distsipliin.** Voogedastushindamise FAPH-variantide tabel-pealkirja loogika (subsec~\ref{subsec:faph-variants}), läve valik ainult valideerimisandmestikul (Cawley & Talbot 2010), kolmereegel — need on detailid, mis lugejale kinnitavad, et autor mõistab statistilisi lõkse.

**Nõrkused.**
- **Tasakaalustatus.** Kolmas peatükk (arutelu) on suure mahuga ja kohati esseelaadne; selle sees on enesetegelik töö metoodiline põhipanus (§\ref{sec:eval-evolution}, §\ref{sec:three-rounds}, §\ref{sec:general-principle}, §\ref{sec:contribution-transferability}, §\ref{sec:fourth-round}). Lugeja, kes hindab "tulemused vs arutelu" tasakaalu, võib täheldada, et osa metoodilistest järeldustest on dubleeritud nii metoodika peatükis (FAPH-variandid, andmeliikide eristamine) kui ka arutelus (lühitee-printsiip). Mõnetine kompressioon parandaks loetavust.
- **Termiini-tasandi konsistents.** Inglise terminite (wake word, streaming inference, vanishing gradients, false rejection rate jne) eestikeelsete vastete andmine on järjekindel ja korrektne (\texttt{\textbackslash emph}-tähistuses), kuid mõnes kohas korratakse selgitust, mis võib pikemaid lõike koormata.
- **Pisivormistus.** Korralikult järgitud tundub TalTech BSc šablonist, kuid PDF-i pole nähtud — eraldatud allikate puhul ei saa kontrollida joonistabelite numeratsiooni või leheküljeloendurite koondumist. Need on lugeja jaoks väikese kaaluga.
- **Kokkuvõtte ja abstraktide vahekord.** Eesti- ja ingliskeelne abstraktid on omavahel kooskõlas ja kompaktsed; kokkuvõtte tekst (chapters/summary.tex) lisab v16c-kandidaadi reservatsiooni — lugeja seisukohast tugev otsus, sest ei lubata enam kui on tõendatud.

---

## 4. Kokkuvõttev põhjendus koondhindele

Töö koondhinne on **7/10** (viie palli skaalal 4, väga hea, ots-otsas).

- Sisuline analüüs ja metoodiline distsipliin on tugevalt üle keskmise (8/10): töö paigutab end teadlikult **tõendusprotokolli** uudsusele, mitte "parimale eesti äratussõnale", ja peab seda lubadust läbi terve dokumendi.
- Ülesande keerukus ja maht on samuti üle keskmise (8/10): 15+ mudeliversiooni, neli FAPH-varianti, kolm valideerimisringi, ESP32-S3 + Home Assistant integratsioon, kasutajatesti tööriistastik on selge bakalaureusetöö ootuste ületamine.
- Vormistamine on hea (7/10): hea struktuur, kvaliteetne viitamine, statistiline distsipliin, kuid arutelu peatüki esseelaadsus ja mõnetine sisukordamine hoiavad selle alla "väga hea" piirsõlme.
- **Hinnet hoiab 8/10-st all** asjaolu, et **kasutajatesti — töö enda sõnastuses kõige kriitilisema välise valiidsuse kihi** — andmed pole veel olemas. Töö ise tunnistab seda ja lubab "protseduuri korralikkust, mitte mudeli täiuslikkust" (§\ref{sec:fourth-round}). See on intellektuaalselt aus, kuid range hindaja peab arvestama, et "Tulemuste valideerimine" kriteeriumis jääb üks tase katmata. Kui kasutajatest tehakse ja andmed lisanduvad enne kaitsmist, on põhjendatud hinde tõstmine 8/10 piirkonda.
- 0-reeglit ei rakendu: ükski kolmest peakriteeriumist ei lange "puuduliku" alla.

**Võrdleva hindamise lisapunkt.** Kui sama prompt jookseks reaalse mitme-töö batchina (näiteks 5–8 paralleelse BSc-tööga), eristuks käesolev töö tõenäoliselt **metoodilise audit-tihedusega ja tõendusdistsipliiniga** (kolm valideerimisringi, FAPH-variantide eristamine, läve-valiku päritolu, usaldusvahemikud, andmelekke ja positiivse klassi auditid). Praktiliste lõputulemuste poolelt (kasutajatest, ESP32-S3 lõppintegratsiooni välitõendus) jääks see tõenäoliselt **võrdsesse või veidi nõrgemasse seisu** võrreldes töödega, kus on lihtsam ülesanne lõpetatud puhtalt. Seega — iseloomult on tegemist **metoodika-rikka, lõpptõenduse-piiratud** tööga, mille hinne sõltub sellest, kas hindaja kaalub metoodilist küpsust või lõpetatud välitulemust kõrgemalt.
