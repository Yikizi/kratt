---
source_prompt: Juhendaja_kompaktne.txt
prompt_type: generative
generated: 2026-05-07
---

Töö käsitleb eestikeelse äratussõna \enquote{Kuule Kratt} tuvastusmudeli loomist ja hindamist piiratud ressursiga ESP32-S3 mikrokontrolleril ning selle lõimimist Home Assistanti lokaalsesse hääljuhtimisahelasse. Teema on aktuaalne, kuna eesti keele kõnetuvastus on lokaalselt juba kasutatav, kuid äratussõna tuvastus --- mis määrab kogu hääljuhtimise kasutuskogemuse esimese filtri --- on väikeste keelte jaoks praktiliselt katmata.

**Tugevused**

* Töös käsitletakse selgelt sõnastatud ja hästi piiritletud uurimisküsimust ning eraldatakse lokaalne äratussõna tuvastus laiemast kõnetöötluse torust, mis tagab töö ulatuse jõukohasuse ilma teemafookuse hägustamiseta.
* Üliõpilane töötas välja mitmemõõtmelise hindamisprotokolli, mis ühendab klipi-tasemelised mõõdikud, voogedastusrežiimi FAPH-i, fraasistruktuuri kontrollivad testid (prefiks, üksiksõna, pööratud järjekord, \enquote{kuule}/\enquote{kule} segiajamine) ning sõltumatud kõrvalejäetud testikomplektid; see protokoll on töö metoodiline põhipanus ja ülekantav teistele väikese ressursiga keelte projektidele.
* Üliõpilane diagnoosis ja dokumenteeris süstemaatiliselt kolm valideerimiskihti --- andmeleke (esimene ring), positiivse klassi sildistusprobleem (teine ring) ning kontrollpunkti valikukriteeriumi kitsus (kolmas ring) ---, mis tõstab töö metodoloogilist väärtust üle pelga mudelitulemuse.
* Töös käsitletakse võrdlevalt kahte avatud lähtekoodiga raamistikku (\texttt{microWakeWord} ja \texttt{openWakeWord}) nelja telje (treenimise keerukus, mudelikvaliteet, integreeritavus, laiendatavus eesti keelele) lõikes ning põhjendatakse Picovoice Porcupine'i välja jätmist sisuliselt, mitte mugavusest lähtuvalt.
* Üliõpilane kasutab raporteeritud mõõdikute juures Wilsoni ja Poissoni-Garwoodi usaldusvahemikke ning kolmereeglit nullsündmuste korral, samuti FAPH-i nelja varianti (raamistiku, skriptitud taasmängu, välitingimuste, kasutajatesti taasmängu); selline statistiline distsipliin on bakalaureusetöö tasemel selgelt üle keskmise.
* Töö arutleb läbipaistvalt agentpõhise tarkvaraarenduse rolli ja piiranguid, eristades selgelt teostuse võimendamist tõendusmaterjali hankimisest, mis on metodoloogiliselt aus ja akadeemiliselt asjakohane refleksioon.

**Nõrkused**

* Lõplikku kasutajatesti 20--30 osalejaga ei olnud töö esitamise hetkeks veel läbi viidud, mistõttu väited päriskõnelejate tuvastamismäära ja kasutuskogemuse usaldusväärsuse kohta jäävad osaliselt hüpoteetiliseks; seda tunnistab ka üliõpilane ise \enquote{võimaliku neljanda ringi} käsitluses, kuid lõputöö lõpliku panuse hindamiseks oleks olnud vaja seda kihti juba sisse arvestada.
* Töö viitab korduvalt vastandlikele tulemustele konkreetsete mudeliversioonide vahel (nt \texttt{v6}, \texttt{v6-residual}, \texttt{v16c}, \texttt{expert-a}, \texttt{expert-b2}), kuid arutelupeatükis viidatakse mõnel pool \enquote{ühele versioonile} ja \enquote{teisele versioonile} ilma versioonitähiseta; selline anonüümistamine raskendab lugejal arutelu sidumist tulemuste peatüki konkreetsete tabelitega.
* Mudeliversioonide arvu (15+) ja paralleelsete katsete mahtu arvestades oleks võinud panustada eraldi mudelipuu või ajatelje joonisesse, mis võtaks visuaalselt kokku mudeliversioonide pärilussuhted, peamised muudatused ja iga ringi parandused; praegu peab lugeja selle pildi kokku panema mitme alamjao tekstist.
* Sünteetilise kõne (XTTS, Neurokõne) rolli treeningus ja hindamises käsitletakse ühel pool kompromissina, teisel pool aga riskina (TTS-andmetega treenitud mudelite ülehinnatud tuvastamismäär); süsteemne kvantitatiivne ablatsioon, mis võrdleks otse sünteetilise andmestiku osakaalu mõju reaalsete kõnelejate tuvastamismäärale, oleks seda arutelu märgatavalt tugevdanud.
* Töö piiritlemise paragrahvis on mainitud, et hindamine toimub ühe äratusfraasi ulatuses, kuid tulevikusuundades pakutakse välja kaskaadarhitektuur ja teine aste, mis kontrolliks \enquote{kuule} ja \enquote{kratt} eraldi; selle ettepaneku teostatavusele oleks võinud lisada vähemalt esialgse mahukao ja latentsuse hinnangu ESP32-S3 piirangute kontekstis, et lugeja näeks edasiminekutee realistlikkust.
