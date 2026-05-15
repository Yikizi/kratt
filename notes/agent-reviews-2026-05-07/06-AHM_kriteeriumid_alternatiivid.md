---
source_prompt: AHM_kriteeriumid_alternatiivid.txt
prompt_type: generative (AHP scaffolding — kriteeriumid + alternatiivid)
generated: 2026-05-07
---

# AHP-i kriteeriumide ja alternatiivide tuletamine bakalaureusetööst

## Eelmärkus: otsustusprobleemi tuletamine tekstist

Esitatud lõputöö ei sõnasta eksplitsiitselt AHP/Saaty paariviisilist otsustusülesannet, kuid sisaldab selgelt äratuvat valikuprobleemi, mis sobib AHP raamistusse. Töö metoodikapeatükis (§ Võrdlusraamistik) on toodud neli telge raamistike võrdlemiseks (treenimise praktiline keerukus, mudeli kvaliteet, integreeritavus, laiendatavus eesti keelele) ning arutelupeatükk lisab tegelikult kasutatud mudelivaliku teljed (sõltumatu taustaheli FAPH, päriskõnelejate tuvastamismäär, sarnaste negatiivnäidete eristus, fraasistruktuuri kontroll, ESP32-S3 mälu-mahutavus jt).

Kõige loomulikum AHP otsustusprobleem, mida saab tekstist puhtalt välja kasvatada, on järgmine:

> **Otsustusküsimus:** Milline äratussõna tuvastuse arendus- ja juurutusrada valida eestikeelse fraasi „Kuule Kratt“ lokaalseks tuvastamiseks ESP32-S3 klassi nutikodu satelliidil, võttes arvesse väikese keele andmestiku piiranguid ja Home Assistanti integratsiooninõuet?

Kõik allpool esitatud kriteeriumid ja alternatiivid on tuletatud otse töö tekstist (sissejuhatus, peatükid 1–3 ja kokkuvõte). Ühtegi tehnoloogiat ega arvu ei ole väljaspool teksti juurde leiutatud; juhul kui tekst ei dokumenteeri konkreetse alternatiivi käitumist, on see allpool märgitud sõnaselgelt kui hinnanguline täiendus.

---

## 1. Kriteeriumite nimekiri (sorteeritud sobivuse järgi kahanevalt)

*Kokku 7 kriteeriumi, mis on tuletatud töö hindamis- ja võrdlusloogikast. MECE-kontroll: kriteeriumid on sõnastatud nii, et nad katavad eraldi tehnilise toru, mudeli kvaliteedi (jagatud kolmeks praktiliselt eristuvaks alariskiks), juurutuse ja arendusprotsessi kulu ning eesti keele/väikese andmestiku spetsiifika. FAPH on jagatud taustaheli (üldine valekäivituste määr) ja sarnaste negatiivnäidete (fraasistruktuur) vahel, kuna töö § Mitmemõõtmeline hindamisprotokoll näitab eksplitsiitselt, et üks ühine FAPH peidab need kaks erinevat lühitee-riski.*

### K1. Päriskõnelejate tuvastamismäär juurutamislävel
* **Kriteerium:** Reaalsete eesti kõnelejate tuvastamismäär (recall) külmutatud lävel
* **Sobivuse hinnang:** 10/10
* **Analüüs/Põhjendus:** Töö sissejuhatus seab eksplitsiitse projektisihi: lähikõne tuvastamismäär $\geq$ 0{,}95 (introduction.tex). Kolmas peatükk dokumenteerib, et XTTS-positiivsetel klippidel saavutatud 1{,}0000 ei kandunud üle reaalsetele „Kule“-hääldustele ning et see lahknevus on töö üks keskseid jääkriske (§ Põhjus 1, § Mida saab juba praegu väita). Ilma reaalse kõneleja tuvastamiseta ei ole äratussõna kasutatav, mistõttu see kriteerium on AHP eesmärgi puhul vältimatult vajalik ja ei ole asendatav ühegi teisega.
* **Mõõtmine ja võrdlemise tegevuskava:** Kasutajatesti taasmängu tuvastamismäär 20–30 osaleja viie puhta äratussõna ütluse pealt (vt § Kasutajatesti metoodika), külmutatud lävel; raporteeritakse koos Wilsoni 95\%~usaldusvahemikuga. Paariviisilises võrdluses võrreldakse mediaanide ja CI-kattuvuste alusel; suurem tuvastamismäär = kriteeriumi suhtes parem alternatiiv.

### K2. Sõltumatu taustaheli FAPH (üldine valeaktiveeringute määr)
* **Kriteerium:** Voogedastus-FAPH sõltumatul kõrvalejäetud taustaheli/kõnekorpusel
* **Sobivuse hinnang:** 10/10
* **Analüüs/Põhjendus:** Töö sissejuhatus seab teise eksplitsiitse sihi FAPH $<$ 1 ning peatükk 1 (§ Hindamismõõdikud, §~Subsec FAPH-i variandid) selgitab, miks see on äratussõna kirjanduses peamine raporteeritud streaming-mõõdik. Common~Voice ET kõrvalejäetud komplektil saavutatud 0{,}79 FAPH (kokkuvõte; § Mida saab juba praegu väita) on töö keskne empiiriline tulemus. Kriteerium on K1-st sõltumatu, sest madala FAPH-i saab saavutada ka tuvastamismäära ohverdamise hinnaga (§ Mitmemõõtmeline hindamisprotokoll, kolmas ring).
* **Mõõtmine ja võrdlemise tegevuskava:** Skriptitud taasmängu FAPH (offline, 2~s jahtumisaeg) Common~Voice ET kõrvalejäetud komplektil ja vähemalt ühel teisel sõltumatul taustaheli rajal. Raporteeritakse koos Poissoni-Garwoodi 95\%~vahemikuga; $k=0$ korral kasutatakse kolmereeglit (§ Hindamismõõdikud). Madalam FAPH = parem.

### K3. Sarnaste negatiivnäidete ja fraasistruktuuri eristus
* **Kriteerium:** Selektiivsus „kuule rott / kuule kraam / kule / üksiku sõna / pööratud järjekorra“ vastu
* **Sobivuse hinnang:** 9/10
* **Analüüs/Põhjendus:** § Mitmemõõtmeline hindamisprotokoll (teine ring) näitab, et kolme-mõõdikuline raporteerimine ilma fraasistruktuuri kontrollita lubab mudelitel õppida prefiksi-lühitee „kuule“ või „kule“; töö nimetab seda eraldi mõõdetavaks neljaks alamtestiks. Töö viitab, et see on tööstuses tuntud risk (Apple’i partial-keyword/swapped-order treening, Shrivastava et al. 2021). Kriteerium on K1 ja K2-st loogiliselt eristuv, sest mudel võib olla samaaegselt hea recall’iga, madala üldise FAPH-iga ja siiski vallanduda osafraasidel.
* **Mõõtmine ja võrdlemise tegevuskava:** FPR neljal alamtestil (prefiks, üksik sõna, pööratud järjekord, kuule/kule segiajamine) kasutajatesti viie sarnase negatiivfraasi ja sünteetilise sarnaste-fraaside komplekti pealt. Iga alamtest saab Wilsoni CI; kriteeriumi koondskoor on alamtestide kaalutud keskmine FPR (madalam = parem).

### K4. ESP32-S3 mälumahu ja arvutusvõime nõuetele vastavus
* **Kriteerium:** Mudeli mahutavus mikrokontrolleri flash-/töömällu ja voogedastusrežiimis töötamine
* **Sobivuse hinnang:** 9/10
* **Analüüs/Põhjendus:** Töö praktiline siht (sissejuhatus, ülesandepüstitus) on ESP32-S3 Korvo-2 plaat ESPHome kihiga. Peatükis 1 fikseeritakse konkreetsed mahud: TFLite mudel 57\,KB / 148\,KB (v16c), tensor\_arena 45–50\,KB, kogusumma alla 200\,KB. § Võrdlusraamistik märgib, et openWakeWord ei sihi mikrokontrollerit, mistõttu integreeritavuse telg on alternatiivide vahel asümmeetriline, mitte „eelistus“. See kriteerium ei ole alistatav K1–K3 poolt: kui mudel ei mahu seadmesse või ei tööta voogedastusrežiimis, kogu otsus langeb.
* **Mõõtmine ja võrdlemise tegevuskava:** Binaarne mahutavuse kontroll (mahub / ei mahu) + kvantitatiivne RAM/flash-tarbimine ja voogedastusrežiimi latentsus mõõdetuna ESPHome compile/flash-pinkilt. Paariviisilises võrdluses: alternatiiv, mis ei mahu, saab dominantse halvema hinnangu; mahtuvate vahel võrreldakse vaba mälu reservi.

### K5. Hindamismetoodika reprodutseeritavus ja tõendusdistsipliin
* **Kriteerium:** Avaliku kontrollkatse, andmelekke kontrolli ja kõrvalejäetud komplekti toe olemasolu valitud rajal
* **Sobivuse hinnang:** 8/10
* **Analüüs/Põhjendus:** Töö nimetab oma peamiseks teaduslikuks panuseks just hindamisprotokolli (§ Mitmemõõtmeline hindamisprotokoll, § Töö-tasemel panus ja selle ülekantavus, kokkuvõte). Speech~Commands marvin kontrollkatse, treening--test disjointsuskontroll, kontrollpunkti komposiitne valikukriteerium ja FAPH-variandi-tabeli (§~Subsec FAPH-i variandid) eksplitsiitne identifitseerimine on need omadused, mille puudumine alternatiivis tähendab, et alternatiivi numbrid ei ole võrreldavad. Kriteerium eristub K1–K4-st, sest viimased mõõdavad lõpptulemust, samas kui K5 mõõdab tulemuse usaldusväärsust.
* **Mõõtmine ja võrdlemise tegevuskava:** Eksperthinnang 1–5 skaalal viie alamküsimuse keskmisena: (a) avalik kontrollkatse läbi tehtud, (b) treening/test disjointsus tõestatud, (c) kõrvalejäetud komplekt sõltumatu, (d) FAPH-variant identifitseeritud, (e) kontrollpunkti valik komposiitne. Kõrgem skoor = parem.

### K6. Eesti keele toe ja sünteetilise andmestiku integratsioon
* **Kriteerium:** Raamistiku sõltumatus ingliskeelsetest eeldustest ning toetus sünteetilise (TTS) ja päris kõne segule
* **Sobivuse hinnang:** 7/10
* **Analüüs/Põhjendus:** § Võrdlusraamistik nimetab seda eksplitsiitselt neljanda telje all. Picovoice Porcupine on töös teadlikult välja jäetud just selle telje (litsents, eesti keele puudumine, kasutaja oma sõna treenimise võimatus) põhjal. Kriteerium eristub K4-st (riistvara) ja K1-st (recall): alternatiiv võib mahtuda ESP32-le ja saavutada hea recall’i kunstlikel klippidel, kuid kui ta ei toeta kohaliku andmestiku ehitust, ei vasta ta töö lähteülesandele.
* **Mõõtmine ja võrdlemise tegevuskava:** Eksperthinnang 1–5 skaalal kahel alamteljel: (a) eesti keele otsene tugi või dokumenteeritud tugi uue keele lisamiseks, (b) TTS-i ja päris kõne segu treenimise tugi. Keskmine skoor; kõrgem = parem.

### K7. Arenduskulu ja Home Assistanti integratsiooni jõukohasus
* **Kriteerium:** Treenimise, eksportimise ja seadmesse juurutamise praktiline keerukus üksiku autori jaoks
* **Sobivuse hinnang:** 6/10
* **Analüüs/Põhjendus:** § Võrdlusraamistik nimetab seda esimese telje all (treenimise praktiline keerukus, hüperparameetrite tundlikkus, tööriistade kasutusmugavus). Töö arutelupeatükis (§ Agentpõhine arendus) tunnistatakse, et osa tööst sai teostatavaks tänu agentpõhisele arendusele; kriteerium kajastab, kui palju manuaalset tööd jääb agentpõhise võimenduse järel alles. Kriteerium on madalama kaaluga, sest see mõjutab projekti teostatavust, mitte lõpliku süsteemi käitumist kasutaja jaoks. Eristub K5-st (metoodika kvaliteet), K4-st (riistvara) ja K6-st (keeletugi).
* **Mõõtmine ja võrdlemise tegevuskava:** Eksperthinnang 1–5 skaalal: andmete ettevalmistuse maht, hüperparameetrite tundlikkus, ESPHome/Wyoming integratsiooni dokumenteeritus. Madalam kulu = kõrgem skoor.

### Välja jäetud kandidaatkriteeriumid (põhjendus)

* **Latentsus** — töös ei ole eraldi mõõdetud ega seatud sihti; kvalitatiivselt kaetud K4 (voogedastusrežiim) all.
* **Privaatsus / lokaalsus** — kõik tekstis tõsiselt käsitletud alternatiivid on lokaalsed (Porcupine on välja jäetud K6 all); kriteerium ei eristaks alternatiive.
* **Mudeli suurus eraldi K4-st** — mahub K4 alla.
* **Subjektiivne rahulolu (UMUX-Lite)** — § Kasutajatesti metoodika märgib, et seda raporteeritakse eraldi diagnostilise mõõdikuna, mitte AHP otsustuskriteeriumina.

Kriteeriumide arv (7) jääb Saaty 7$\pm$2 reegli ülemisele piirile; kui CR (consistency ratio) osutub paariviisilisel võrdlusel liiga kõrgeks, on esimene loogiline taandus K7 väljajätmine (madalaim hinnang) või K2 ja K3 ühendamine kompositseks „streaming-selektiivsuse“ kriteeriumiks — kuid see ühendamine kaotaks just selle eristuse, mille empiirilist olulisust töö § Mitmemõõtmeline hindamisprotokoll dokumenteerib.

---

## 2. Alternatiivide nimekiri

*Kokku 6 alternatiivi. Esimesed neli on tuletatud otse töö tekstist konkreetsete mudelite/raamistike kaudu; kaks viimast on töös eksplitsiitselt diskuteeritud disainivariandid (konsensus ja kaskaad), mis sõnastavad realistliku otsustusruumi täielikumalt. Kõik kuus jagavad sama lõpprakendust (ESP32-S3 + Home Assistant), mistõttu nad on AHP mõistes võrreldavad.*

* **Alternatiiv A1: microWakeWord + üksikmudel `v16c` (piloodi vaikevalik)**
    * **Põhjendus:** § Kasutajatesti metoodika nimetab `v16c` piloodi aktiivseks kandidaadiks ja stabiilseks üksikmudeli baasjooneks. Quantiseeritud TFLite maht 148\,KB, tensor\_arena 45–50\,KB — mahub ESP32-S3-le. See on töö konkreetne juurutuskandidaat, millest sõltub kasutajatesti vaikekonfiguratsioon.

* **Alternatiiv A2: microWakeWord + ekspertkonsensus `expert-a` $\cap$ `expert-b2`**
    * **Põhjendus:** Kokkuvõte ja § Mida saab juba praegu väita dokumenteerivad, et see konsensus saavutab Common~Voice ET kõrvalejäetud komplektil FAPH = 0{,}79 — töö ainsa alla-1-FAPH-tulemuse. Töö nimetab seda eksplitsiitselt diagnostiliseks tulemuseks ning § Edasised suunad: kaskaadarhitektuur seob selle laiema tööstusliku praktikaga.

* **Alternatiiv A3: microWakeWord + üksikmudel `v6-residual` (residuaal-ablatsioon)**
    * **Põhjendus:** Peatükk 1 (§~Subsec Residuaalühendused) ja § Empiiriline tõendus lahknevusest dokumenteerivad selle versiooni eraldi: ${\sim}99$~h Android-välikatses 0{,}58 FAPH (parim väli-FAPH töös), kuid madalam recall ja sarnaste fraaside risk. Esindab „madala FAPH-i, madala recall’i“ otsa kompromissispektril.

* **Alternatiiv A4: openWakeWord (Raspberry Pi 5 hosti suunaline rada)**
    * **Põhjendus:** § Võrdlusraamistik käsitleb seda teise praktiliselt relevantse avatud raamistikuna; töö nimetab seda paindlikuma mudeliehitusega, kuid sihib ONNX-runtime’i ja Raspberry Pi klassi hosti, mitte mikrokontrollerit. Esindab arhitektuurset alternatiivi, kus äratussõna jookseks sama Pi 5 peal nagu Kiirkirjutaja STT.

* **Alternatiiv A5: Kaskaadarhitektuur — kerge esimene aste + täpsem teine aste**
    * **Põhjendus:** § Edasised suunad: kaskaadarhitektuur kirjeldab seda eksplitsiitselt töö loomuliku järgmise sammuna, viidates Apple/Google’i tööstuspraktikale (Gruenstein 2017, Sigtia 2020 jt). Esimene aste oleks A1- või A2-laadne detektor, teine aste kontrolliks „kuule“ ja „kratt“ kohalolu ning järjekorda. Esindab töö soovitatud edasiarendusrada.

* **Alternatiiv A6: Picovoice Porcupine (kommertsalternatiiv, võrdlusraamistik)**
    * **Põhjendus:** § Võrdlusraamistik nimetab seda eksplitsiitselt töös välja jäetud kommertsalternatiivina (suletud lähtekood, eesti keele puudumine, kasutaja oma sõna treenimise võimatus). AHP raamistuses on see vajalik kui kontrollalternatiiv, mis võimaldab näidata, miks töö valis avatud lähtekoodi raja: K6 (eesti keele tugi) ja K5 (reprodutseeritavus) telgedel saab Porcupine madala hinnangu, mis põhjendab tema väljajätmist juurutuskandidaatide hulgast.

### Tahtlikult välja jäetud alternatiivid

* **Pilvepõhine äratussõna teenus** — vastuolus töö lokaalsuse põhinõudega (sissejuhatus, ülesandepüstitus); ei oleks AHP eesmärgi mõistes kandidaat.
* **Üksikud nõrgemad mudeliversioonid v1–v15 ilma residuaalita** — § Mitmemõõtmeline hindamisprotokoll selgitab, miks need on tõendite kogumise sammud, mitte juurutuskandidaadid; nende eraldi AHP-sse võtmine täidaks otsustusmaatriksi mürateabega.

Alternatiivide arv (6) jääb prompti soovitatud vahemikku 4–7. Paariviisilise võrdluse maatriks on $6\times 6 = 15$ paari kriteeriumi kohta, mis on inimeksperdile veel mõõdukalt jõukohane; kui see osutub liiga koormavaks, on esimene loogiline taandus A6 väljajätmine (Porcupine on niikuinii kvalitatiivse põhjendusega välistatud) ja A3 ühendamine A1-ga „üksikmudeli tipp“-grupina.
