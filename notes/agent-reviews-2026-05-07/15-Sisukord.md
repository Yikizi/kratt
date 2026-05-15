---
source_prompt: /Users/mattias/Downloads/loputoo_viibad_2026_04_28-2/03_Lõputöö_alamosad/Kohustuslikud/Sisukord.txt
prompt_type: generative
generated: 2026-05-07
---

# Sisukord — alternatiivne mustand

Käesolev mustand on koostatud viiba juhiste järgi (TalTech-i nõuetele vastav, kuni kolm taset, *sentence case*, peatükkide juures alates teisest tasemest ilma lõpupunktita) ning tugineb töö tegelikule sisule (sissejuhatus, esimene/teine/kolmas peatükk, kokkuvõte, ülesandepüstitus, abstraktid). Töö tüüp: eksperimentaalne uurimistöö (väikeses keeleruumis äratussõna tuvastuse mudel ja hindamismetoodika), millega kaasneb riistvara- ja tarkvaraintegratsioon. Seetõttu on lisatud tingimuslik peatükk **Varem tehtud teadustöö** (mitte „Sarnased tarkvarad“), kuna töö pearõhk on hindamismetoodikal ja empiirilisel uurimisel, mitte uue tarkvaratoote arendusel. Põhitulemuste osas on valitud eksperimentaalse töö raam (Eksperimendi kavand → Eksperimendi tulemused), mis vastab töö tegelikule kulule kõige täpsemalt.

Kuna sisendis ei ole jälgi mitme autori või arendusmeeskonna olemasolust, on jaotis „Autori roll arendusmeeskonnas“ välja jäetud. Uurimisküsimused on töös sõnastatud (sissejuhatus, lõik nr 9), seetõttu on alapeatükk 1.3 ja vastav lülitaja-alapeatükk peatükis 6 lisatud.

## Sisukord (puhas tekst, vormistusnõuete kohaselt)

```
Sissejuhatus
1. Sissejuhatus
1.1 Taust ja probleem
1.2 Ülesandepüstitus
1.3 Uurimisküsimused
1.4 Töö struktuur

2. Metoodika
2.1 Tööriistad
2.2 Tööprotsess

3. Teoreetiline taust
3.1 Äratussõna tuvastus ja voogedastav järeldamine
3.2 Hindamismõõdikud ja FAPH ehk valevallandumiste loendus
3.3 Väikese ressursiga keele kohaliku äratussõna eripära

4. Varem tehtud teadustöö
4.1 Mikrokontrolleripõhise äratussõna kirjandus
4.2 Avatud lähtekoodiga raamistikud microWakeWord ja openWakeWord
4.3 Standardsete võrdlusaluste ja reaalse kasutuse vahelise lõhe käsitlus

5. Eksperimendi kavand
5.1 Andmeliigid ja andmestiku ülesehitus
5.2 Avalikud andmekorpused ja kontrollkatse Speech Commands peal
5.3 Mudeli arhitektuur ja konfiguratsioon
5.4 Hindamiskomplektid ja kõrvalejäetud rajad
5.5 Kasutajatesti protokoll ja subjektiivse rahulolu mõõtmine

6. Eksperimendi tulemused
6.1 Hindamis- ja treeningutoru rekonstrueerimine
6.2 Avaliku kontrollkatse tulemus
6.3 Eestikeelse äratussõna mudeliversioonide võrdlus
6.4 Andmelekke avastamine ja korrigeeritud hindamine
6.5 Ristmikrofoni ja ristkeelne FAPH analüüs
6.6 Sihipäraselt projekteeritud ekspertmudelite konsensus
6.7 Fraasi-täielikkuse ja positiivsete näidete reostuse audit
6.8 Kontrollpunkti FAPH-optimeerimise piirangute analüüs
6.9 Kasutajatesti vahetulemused

7. Tulemuste analüüs
7.1 Valideerimine
7.2 Vastused uurimisküsimustele
7.3 Tulemuste võrdlus varasema teadustööga
7.4 Standardsete võrdlusaluste ebapiisavus reaalse kasutuse ennustamisel
7.5 Mitmemõõtmeline hindamisprotokoll kui töö metoodiline põhipanus
7.6 Agentpõhine arendus kui töövõimendaja
7.7 Tööst huvitatud osapooled
7.8 Töö piirangud
7.9 Edasised arengusuunad

8. Tööprotsessi reflektsioon
8.1 Õnnestumised
8.2 Kitsaskohad ja probleemid
8.3 Parendusettepanekud edaspidiseks

Kokkuvõte
Kasutatud kirjandus
Lisa 1 — Töö avaldamise lihtlitsents
Lisa 2 — Kasutajatesti küsimustik ja protokoll
Lisa 3 — Mudeliversioonide ülevaatetabel ja hindamiskomplektide kirjeldus
Lisa 4 — FAPH-i variantide loendusreeglid ja näidisarvutused
```

## Vastavuskontroll viiba nõuetega

- **Keel ja stiil:** eestikeelne, *sentence case* — ainult lause esimene sõna ja pärisnimed (Speech Commands, microWakeWord, openWakeWord, FAPH) on suure tähega.
- **Sügavus:** maksimum kolm taset; struktuuri laiendamine sügavamale (nt 5.3.1) on jäetud lõpliku LaTeX-koondamise faasi. Käesolev mustand peatub teisel tasemel.
- **Numeratsioon:** esimese taseme numbri lõpus on punkt (`1.`); teise taseme number on punktita (`1.1`). „Kasutatud kirjandus“ ja „Lisad“ on numbrita.
- **Kohustuslikud alapeatükid peatükis 1:** Taust ja probleem, Ülesandepüstitus, Uurimisküsimused (sisendis olemas), Töö struktuur — kõik kaetud.
- **Kohustuslikud alapeatükid peatükis 2:** Tööriistad, Tööprotsess. „Autori roll arendusmeeskonnas“ on välja jäetud (üheautoriline töö).
- **Tingimuslik peatükk:** „Varem tehtud teadustöö“ lisatud, sest tegemist on uurimistööga ja töös refereeritakse mahukalt rahvusvahelist KWS-kirjandust (sh apple-heysiri2017, gruenstein2017cascade, dubois2020triggers, schoenherr2022accidental, park2024adversarial, chen2022misp, lopezespejo2021deepkws). „Sarnased tarkvarad“ on välja jäetud, sest töö ei ole tarkvaratoote väljaandmine, vaid mudeli ja hindamisprotokolli loomine.
- **Põhitulemuste raam:** „Eksperimendi kavand“ + „Eksperimendi tulemused“, mis kajastab töö tegelikku struktuuri (esimene peatükk on metoodika, teine peatükk eksperimentide tulemused, kolmas peatükk arutelu ja järeldused).
- **Peatüki 7 algus:** „Valideerimine“ on selle peatüki esimene alapunkt, nagu nõutud.
- **Peatüki 7 lõpp:** sisaldab nõutud blokk-kolmikut: Tööst huvitatud osapooled → Töö piirangud → Edasised arengusuunad.
- **Kontekstipõhised lisandused:**
  - „Vastused uurimisküsimustele“ on olemas, sest punktis 1.3 on uurimisküsimused.
  - „Tulemuste võrdlus varasema teadustööga“ on olemas, sest peatükk 4 on lisatud.
  - „Loodud lahenduse võrdlus sarnaste tarkvaradega“ pole asjakohane (Sarnased tarkvarad puudub).
  - „Riskianalüüsi“ pole eraldi lisatud, kuna olemasolev töö ei käsitle seda eraldi alapeatükina; töö piirangute, andmelekke ja kasutajatesti välise valiidsuse arutelu on koondatud alapeatükkidesse 7.4–7.8. Kui retsensent peaks „Riskianalüüsi“ siiski nõudma, on loomulik koht 7.9 ette lisada uus alapunkt „Riskianalüüs“.
- **Peatükk 8 (reflektsioon):** sisaldab täpselt kolme nõutud alapeatükki.
- **Lõpuosad:** numbrita Kokkuvõte, Kasutatud kirjandus ning Lisad. Lisade hulgast on sõnaselgelt välja jäetud lähtekoodi paigutamine (nõue „mitte lähtekood“). Lisa 1 on kohustuslik lihtlitsents; lisad 2–4 on tuletatud sisendist (kasutajatesti tööriistastik, mudeliversioonide tabel, FAPH-i variantide §\ref{subsec:faph-variants}).

## Lahknevused töö praeguse failistruktuuri ja sisukorra vahel

Tööfailides on praegu kolm sisupeatükki (`first_chapter.tex` — metoodika; `second_chapter.tex` — eestikeelse äratussõna eksperimentide tulemused; `third_chapter.tex` — arutelu, järeldused ja edasised suunad), mis koos sissejuhatuse ja kokkuvõttega katavad tegeliku narratiivi. Käesolev sisukord laiendab seda struktuuri viiba nõutud kujule, paigutades:

- praeguse `first_chapter.tex` peamiselt **2. Metoodika** ja **5. Eksperimendi kavand** vahele (mudeli arhitektuur, hindamismõõdikud ja kasutajatesti metoodika sobivad eksperimendi kavandisse);
- praeguse `second_chapter.tex` **6. Eksperimendi tulemused** alla;
- praeguse `third_chapter.tex` jaotuvalt **7. Tulemuste analüüs** (sh § 7.4–7.6) ja **8. Tööprotsessi reflektsioon** vahele.

**Teoreetiline taust** (peatükk 3) ei eksisteeri praegu eraldi failina — see oleks vaja kirjutada (lühike, 2–3 alapeatükki, vastavalt viibale „väldi üldtuntud teadmiste kordamist“). Sissejuhatuses ja metoodika peatükis on vajalik materjal juba laiali (KWS-kontekst, FAPH-i mõiste, väikese ressursiga keele eripära), kuid eraldi peatükina puudub.

**Varem tehtud teadustöö** (peatükk 4) puudub samuti omaette failina; sisendmaterjali jaoks on viited olemas (lopezespejo2021deepkws, chen2014smallfootprint, alvarez2019svdf, choi2021bcresnet, apple-heysiri2017, gruenstein2017cascade, dubois2020triggers, schoenherr2022accidental, sensory2024realworld, chen2022misp, shrivastava2021optimize, park2024adversarial), kuid neid pole eraldi peatükina koondatud.

**Tööprotsessi reflektsioon** (peatükk 8) puudub praegu eraldi peatükina. Töö kolmandas peatükis on agentpõhise arenduse käsitlus (§ „Agentpõhine arendus kui töövõimendaja, mitte tõendusmaterjali asendaja“), mille saaks osaliselt suunata 8.1–8.2 alla, kuid kolm nõutud alampunkti (õnnestumised, kitsaskohad, parendusettepanekud) tuleb sõnastada eraldi.

## Riskid ja soovitused

1. **Peatükkide 3 ja 4 lisamise kulu** kuni 18.05.2026 deadline-ini on reaalne riskiklass. Soovitus: hoida peatükid lühikesed (kumbki 2–4 lk), tugineda olemasolevatele BibTeX-viidetele ning vältida sisu dubleerimist sissejuhatuse ja peatüki 7 vahel.
2. **Peatüki 6 alajaotus** sõltub sellest, kui detailselt soovitakse iga audit-ringi (esimene, teine, kolmas) eraldi alapeatükina hoida. Käesolev mustand pakub vahepealse lahenduse: kontentid 6.7 ja 6.8 vastavad teisele ja kolmandale audit-ringile, esimene audit-ring on jaotatud 6.4–6.6 vahel.
3. **„Riskianalüüsi“ alapeatükk peatükis 7** on praegu välja jäetud. Kui juhendaja või retsensent soovib seda eraldi näha (nt privaatsus, GDPR, audio opt-in), on loomulik lisada „7.9 Riskianalüüs“ ja nihutada „Edasised arengusuunad“ 7.10-ks. See ei rikuks viiba reegleid.
4. **Lisade nimekiri** on minimaalne ja pärsitud (mitte lähtekood). Kui kasutajatesti küsimustik mahub põhiteksti, saab Lisa 2 ka ära jätta.
