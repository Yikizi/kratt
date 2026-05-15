---
source_prompt: /Users/mattias/Downloads/loputoo_viibad_2026_04_28-2/06_Kaitsmine/Kaitsmiskomisjoni_küsimused.txt
prompt_type: generative
generated: 2026-05-07
---

# Kaitsmiskomisjoni küsimused — harjutusvoor

Märkus: retsensioonifaili ei olnud kaasas, mistõttu kõik 15 küsimust on koostatud ainult lõputöö enda materjali põhjal. Küsimused tuginevad sissejuhatuse, esimese, teise ja kolmanda peatüki, eestikeelse ja ingliskeelse annotatsiooni ning ülesandepüstituse sisule. Konkreetsete tulemuste numbrid (FAPH = 0,79; v6 ≈ 50 valeaktiveeringut/h; v6-residual 0,58 vs. expert-a 2,79; v16c maht 148 KB jne) on võetud otse töö tekstist.

---

## 1. Toetavad ja suunavad küsimused

1. Töö üks kesksemaid panuseid on kolme valideerimiskihiga (klipi-tasemeline FPR → kolme-mõõdiku raporteerimine → komposiitne kontrollpunkti valik) hindamisprotokoll. Kas Te saaksite komisjonile lühidalt kirjeldada, milline konkreetne empiiriline tähelepanek viis Teid igal kolmel sammul järgmise kihi juurde, ja millist riski iga kiht eraldi maandab?

2. Te kirjeldate töös, et samaaegselt klipi-tasemel madala FPR ning madala FAPH-iga mudel (nt v6) andis MacBook Pro mikrofoniga umbes 50 valeaktiveeringut tunnis. Mis oli Teie jaoks selle leiu juures kõige üllatavam ja kuidas muutis see Teie arusaama äratussõna mudeli usaldusväärsuse hindamisest tervikuna?

3. Töö üks olulisi praktilisi tulemusi on, et expert-a + expert-b2 konsensus saavutab Common Voice ET kõrvalejäetud komplektil FAPH = 0,79 alla projekti sihiks seatud 1 vea/h. Kuidas Te näete sellise kahe spetsialiseeritud mudeli konsensuse rolli laiemalt — kas see on ühekordne nipp Krati jaoks või üldistatav muster madala ressursiga keelte äratussõna projektidele?

4. Te käsitlete agentpõhist tarkvaraarendust kui töövõimendajat, mis ei asenda tõendusmaterjali. Millise konkreetse tööriista või komponendi (Androidi valevallandumiste logija, taustaheli korpuse haldus, mudelite paralleelne taasmäng vms) ehitamine ilma agentidekasutuseta oleks Teie hinnangul olnud üksiktöö ajaraamis kõige raskem ja kuidas see omakorda muutis töö metoodilist horisonti?

5. Töös on välja toodud konkreetne edasine suund — kaskaadarhitektuur, kus teine aste kontrolliks eraldi „kuule" ja „kratt" sõnade kohalolu ja järjekorda. Kuidas Te kavandaksite empiiriliselt mõõta, kas selline teine aste vähendab valeaktiveeringuid ilma päris äratuste tuvastamismäära kahandamata, lähtudes just käesolevas töös välja arendatud mitmekriteeriumilisest hindamisest?

---

## 2. Kriitilised ja skeptilised küsimused

1. Te eristate töös koguni nelja erinevat FAPH-i varianti (raamistiku, skriptitud taasmängu, välitingimuste ja kasutajatesti taasmängu FAPH) ning märgite, et need ei ole otseselt vastastikku võrreldavad. Tulemuste peatüki tabelid kasutavad „skriptitud taasmängu FAPH-i" 2-sekundilise jahtumisajaga, samas kui ESPHome seadme runtime-loogika on teistsugune. Kuidas Te põhjendate, et Teie keskne väide „FAPH = 0,79" on praktiliselt sisukas, kui kasutaja kogeb seadmel hoopis raamistiku FAPH-i? Mis garanteerib, et need kaks suurust käituvad sama suunas?

2. Te raporteerite konsensushindamise tulemuse FAPH = 0,79 ühe operatsioonipunkti ja ühe korpuse (Common Voice ET kõrvalejäetud komplekt) peal. Sissejuhatuses on töö siht sõnastatud kui „pidevvoo FAPH < 1 pikemal taustaheli korpusel". Kas Te ei segi siin „pikemat taustaheli korpust" tihedalt artikuleeritud kõnekorpusega? §3 §sec:benchmark-gap §Põhjus 2 ütleb selgelt, et tihe Common Voice kõne ei ennusta päris kodu helipilti. Kuidas saate siis sama korpuse peal mõõdetud 0,79 üldse kasutada lõputöö sihi täitmise tõenduseks?

3. Töö annotatsioon ütleb, et „ükski praegune mudel ega kombinatsioon ei täitnud korraga kõiki eesmärke", aga sissejuhatuse panus loetelu ja peatükk §sec:contribution-transferability väidab samal ajal, et töö pakub välja „väikese ressursiga keele kohaliku äratussõna mitmemõõtmelise valideerimise protokolli". Kui ükski mudel ei suuda Teie enda raamistikus läbida kõiki kriteeriume, siis kas Te ei tõesta tegelikult lihtsalt, et Teie protokoll on liiga range? Mille alusel komisjon peaks otsustama, kas tegu on eduka töö või eduka „protokolliga, mille all on negatiivne tulemus"?

4. Te kasutate v6-residual ablatsiooni näitena, et residuaalühenduste lülitamine sisse vähendas Common Voice ET FAPH-i 25,4 → 14,4. Kuid §3 §sec:benchmark-gap §Põhjus 2 toodud konkreetses näites annab v6-residual välitingimustes 0,58 FAPH 98,97 h jooksul, samal ajal kui expert-a annab 2,79. Kas see ei anna Teile tegelikult signaali, et v6-residual on üksikmudelina parem kui Teie eelistatud expert-a + expert-b2 konsensus, ja konsensuse 0,79 number on lihtsalt ülerangelt valitud Common Voice korpuse artefakt? Miks Te jätkuvalt eelistate konsensust v6-residualile?

5. Sissejuhatuses on alamküsimus „kas treenitud mudel saavutab eestikeelsel taustaheli korpusel pidevvoo FAPH < 1 ja lähikõne tuvastamismäära ≥ 0,95 sihi". §sec:can-claim-now ütleb otsesõnu, et tuvastamismäär reaalsetel „Kule"-hääldustel jääb juurutuslävel madalamaks kui TTS-positiivsetel klippidel ja juurutusotsus sõltub käimasolevast kasutajatestist. Tegelikult on Teie töö esitamise hetkel tuvastamismäära ≥ 0,95 siht päris kõnelejatel kontrollimata. Kas Te möönate, et üks Teie kahest sihtkriteeriumist ei ole tegelikult täidetud, ja kuidas mõjutab see Teie peamiste väidete kandejõudu?

---

## 3. Laiema vaate ja rakendatavuse küsimused

1. Selgitage palun komisjonile, kes ei tegele igapäevaselt äratussõnadega, lihtsas keeles: mille poolest erineb äratussõna tuvastus tavalisest kõnetuvastusest ja miks ei piisa Teie töös eestikeelsest kõnetuvastusest, et nutikodu hääljuhtimine töötaks?

2. Mis on Teie töö praktiline kasu tavakasutaja jaoks aastal 2026? Kui ma soovin täna kodus eestikeelse häälega tulesid juhtida, kas ma saan Teie töö tulemust kuskilt alla laadida ja oma Home Assistanti paigaldada, või on tegemist puhtalt akadeemilise tõendiga, et selline süsteem on põhimõtteliselt teostatav?

3. Te toonitate korduvalt eraelu puutumatust ja lokaalset töötlust. Kuidas Te seletaksite kasutajale, kes ei tea, mis on „pilveteenus" ega „mikrokontroller", milles seisneb sisuline vahe Teie lahenduse ja näiteks Google Assistanti või Alexa vahel, kui mõlemad reageerivad samuti tema häälele?

4. Te plaanite 20–30 osalejaga kasutajatesti, mille käigus iga osaleja ütleb 5 äratussõna ja täidab lühikese küsimustiku. Kui keegi väljaspool ülikooli — näiteks omavalitsus või kohalik nutikoduettevõte — sooviks Teie tulemust kasutada otsuse alusena, et eestikeelse äratussõna lahendus on „valmis" tegelikku kasutusse võtmiseks, siis mida Te neile ütleksite: mida Teie töö sellise otsuse jaoks suudab tõestada ja mida mitte?

5. Kui Teil oleks järgmine aasta vabu ressursse — täiendav rahastus, paar kaastöötajat ja ligipääs suuremale kõnelejavalimile — siis milline on Teie hinnangul üks konkreetne samm, mis annaks tavakasutaja jaoks suurima nähtava paranemise: kas (a) parem mudel rohkemate kõnelejate andmetel, (b) kaskaadarhitektuuri teine aste, (c) avalik tooteküps Home Assistanti integratsioon koos paigaldusjuhendiga eesti keeles, või (d) midagi muud? Põhjendage valikut.
