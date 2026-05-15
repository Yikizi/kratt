---
source_prompt: Tulemuse_hindamise_veebiküsitluse_kontrollimine.txt
prompt_type: evaluative (audit küsitluse disainile)
generated: 2026-05-07
---

# Audit: Krati piloodi mini-küsimustiku v1 valideerimisküsitlus

Auditeeritav dokument: `docs/user-testing/mini-questionnaire-form-v1.md`
(lukustatud piloodivorm, 2026-05-07; eesmärk on koguda üks võrreldav lühikene kasutatavusskoor pluss Krati-spetsiifiline diagnostiline tagasiside).

Töö kontekst: bakalaureusetöö \enquote{Kuule Kratt} äratussõnamudeli ja selle Home Assistanti integratsiooni hindamiseks; küsimustik on osa peatükis~\ref{sec:user-test-methodology} kirjeldatud 10-minutilisest stsenaariumitestist 20--30 osalejaga, kus iga osaleja annab nii positiivseid äratussõna ütlusi, sarnaseid negatiivfraase, skriptitud käske kui ka vaba valgusülesande, mille audio taasesitatakse hiljem külmutatud lävedega varimudelite peal.

---

## 1. Üldine hinnang ja tugevused

Küsimustik on metoodiliselt heal tasemel ja praktiliselt küps. Selle eesmärk --- saada üks võrreldav lühike kasutatavusskoor pluss diagnostiline projekti-spetsiifiline tagasiside --- on selgelt sõnastatud, ning autor on teadlikult eristanud valideeritud lühiskaala (UMUX-Lite + SEQ) ja uurija koostatud diagnostilised hinnangud. See vastab täpselt sellele, mida lõputöö kontekst nõuab: töö ei taotle UX-koondskaala loomist, vaid soovib (a) raporteerida tunnustatud lühiskaalal saadud arvu ja (b) toetada objektiivseid äratussõna mõõdikuid kvalitatiivse signaaliga.

Tugevused, mis tasub eraldi nimetada:

- **Skaala kalibratsioon vastab valideeritud allikatele.** UMUX-Lite kasutab 7-pallist skaalat ja just selle kahe väite minimaalset versiooni \cite{lewis2013umuxlite}; SEQ on samuti 7-palline standardvormis \cite{sauro2009seq}. Normaliseerimisvalem (mean$-$1)/6$\cdot$100 on UMUX-Lite kanooniline.
- **Selge piirjoon objektiivse ja subjektiivse vahel.** Raportimisjuhis ütleb otse, et nelja Krati-spetsiifilist hinnangut ei tohi liita üheks UX-skooriks ja et subjektiivne usaldus seotakse äratussõna saagise / käsu täitmise objektiivsete näitajatega, kuid mitte sulatatakse ühte. See kaitseb tööd \enquote{üheks numbriks paneme kõik} tüüpi kriitika eest.
- **Pseudonüümsus ja nõusoleku tase on vormis sees.** Eraldi väli \enquote{consent level — metrics only / audio opt-in} on kooskõlas peatüki~\ref{sec:user-test-methodology} kaheastmelise nõusolekumudeliga. See on lõputöö GDPR-perspektiivist väärtuslik.
- **N$\approx$20--30 jaoks sobiv raportimisjuhis.** Mediaan + IQR igale küsimusele on metoodiliselt korrektne valik nii väikese valimi puhul; keskmine + standardhälve oleks olnud halvem signaal.
- **Vorm on lühike.** Kaheksa küsimust + taustainfo on adekvaatne 10-minutilise stsenaariumi jaoks. Pikem küsimustik tekitaks osalejate väsimust ning kahjustaks vastavalt heli- ja käsuandmete kvaliteeti.

Töö praeguse küpsusastme juures ei ole küsimustik veel \enquote{laitmatu}, kuid puuduvad osad on enamasti väikesed parandused ja paar struktuurilist täpsustust, mitte sisulised metoodikavead.

---

## 2. Tuvastatud nõrkused ja kriitika

### 2.1 \enquote{Süsteem reageeris piisavalt usaldusväärselt} — implitsiitselt suunav ja semantiliselt ülekaetud

- **Probleem:** Ei-suunavus + üheselt mõistetavus. Sõna \enquote{piisavalt} viitab juba positiivsele eeldatavale lävele (\enquote{piisav} on \enquote{rahuldav}); see suunab vastajat \enquote{nõustun} suunas. Lisaks katab \enquote{usaldusväärselt} lõputöö mõõdikute keeles korraga vähemalt kahte erinevat asja: (i) tabamise saagis (kas Kratt vastas õigetele äratustele) ja (ii) valeaktiveeringute puudumine (kas Kratt jäi vait, kui ei pidanud reageerima). Need kaks võivad osaleja peas anda eri suunaga vastuseid, mis muudab punkti tõlgendamise raskeks.
- **Näide kavast:** \enquote{4. Süsteem reageeris piisavalt usaldusväärselt.}
- **Mõju:** Vastus ei eristu peatüki~\ref{sec:benchmark-gap} keskses dimensioonis (saagis vs. valeaktiveeringud), mille ümber kogu töö tõendusdistsipliin on üles ehitatud. Andmeanalüüsis ei saa seda hinnangut otse seostada objektiivse FAPH-i ega tuvastamismääraga, kuigi raportimisjuhis selle sidumist nõuab.

### 2.2 \enquote{Süsteem reageeris piisavalt kiiresti} — sama \enquote{piisavalt} probleem

- **Probleem:** Suunav sõnastus.
- **Näide kavast:** \enquote{5. Süsteem reageeris piisavalt kiiresti.}
- **Mõju:** Sama mehhanism nagu 2.1; väiksem mõju, kuna kiirus on lihtsam tajumõõde, kuid \enquote{piisavalt}-baseliine on vaja kõrvaldada kõikides paralleelsetes Likerti väidetes, vastasel juhul tekib nõustumiseelarvamus (\emph{acquiescence bias}).

### 2.3 \enquote{Käskude sõnastamine tundus loomulik} — käsu sõnastus vs. süsteemi käitumine

- **Probleem:** Üheselt mõistetavus. Kas \enquote{loomulik} viitab sellele, kuidas osaleja pidi käsku ütlema (st keelelisele sõnastusele) või sellele, kuidas süsteem käsku tõlgendas? Krati hindamise seisukohalt on need eri asjad: keeleline sõnastus puudutab käsuvalikut (mis sõnu skript pakkus), süsteemi käitumine puudutab äratussõna ja STT lõpptulemust.
- **Näide kavast:** \enquote{6. Käskude sõnastamine tundus loomulik.}
- **Mõju:** Tõlgenduse hajumine; vastuste agregaat ei räägi puhtalt kummastki teemast.

### 2.4 \enquote{Kasutaksin sellist süsteemi kodus} — konfondeeritud kogu seadme + kontekstiga

- **Probleem:** Üheselt mõistetavus + konteksti adekvaatsus. \enquote{Selline süsteem} võib osaleja peas tähendada (a) ainult Krati äratussõna, (b) Krati + Home Assistanti kogu satelliiti, (c) ükskõik millist eestikeelset häälassistenti. Lõputöö hinnatav komponent on äratussõna tuvastus, mitte üldine \enquote{häälassistent kodus}.
- **Näide kavast:** \enquote{7. Kasutaksin sellist süsteemi kodus.}
- **Mõju:** See punkt on praegu välise valiidsuse mõõdik mõnele halvasti määratud objektile. Kui see soovitakse jätta, peaks vorm täpsustama, mida \enquote{selline süsteem} hõlmab; muidu jääb tulemus retsensendi käes \enquote{midagi mõõdab, ent mida?} kategooriasse.

### 2.5 \enquote{Mis oli kõige häirivam või üllatavam?} — topelt-küsimus

- **Probleem:** Double-barreled. Häiriv ja üllatav on kaks erinevat afektitooni; sama vastusse mahub korraga ainult üks neist mõistlikult. Klassikaline juhus on see, et osaleja on üllatunud millestki positiivsest ja häiritud millestki muust, ega tea, kummale vastata.
- **Näide kavast:** \enquote{8. Mis oli kõige häirivam või üllatavam?}
- **Mõju:** Kvalitatiivse signaali lahjenemine. Lõputöö arutelu peatükk vajab kvalitatiivset tagasisidet just \emph{häirivuse} kohta (peatükis~\ref{sec:fourth-round} mainitud \enquote{neljanda ringi} riskid: häälduse vahevormid, aktsendid, vaikne äratus pärast pikka vaikust). \enquote{Üllatav} on liiga lai, et seda eraldi kasutada.

### 2.6 Eesti keele tase \enquote{emakeel / C1-C2 / B1-B2 / A1-A2 / muu / ei soovi öelda} — MECE puhastus

- **Probleem:** Vastuste ammendavus ja välistavus (MECE). \enquote{Emakeel} ja \enquote{C1-C2} ei välista üksteist (emakeelekõneleja \emph{on} C2). \enquote{Muu} on alamkategooria, mille suhe ülejäänutega on määramata.
- **Näide kavast:** \enquote{Eesti keele tase: emakeel / C1-C2 / B1-B2 / A1-A2 / muu / ei soovi öelda.}
- **Mõju:** Praktiline mõju on väike, kuna emakeele osakaal on Krati piloodis tõenäoliselt ülekaalukas, kuid range MECE kontroll on retsensendi standardküsimus ja võiks olla vormistuses puhtalt esitatud.

### 2.7 Sagedusvalikud nutikodu kasutusele on lühemad kui häälassistendi omad

- **Probleem:** Skaalade adekvaatsus / sümmeetria. \enquote{Varasem häälassistendi kasutus} on neljaastmeline (mitte kunagi / harva / iganädalaselt / iga päev), \enquote{Nutikodu kasutus} on kolmeastmeline (ei kasuta / aeg-ajalt / regulaarselt). Kahe lähedase küsimuse vahel astmestike erinevus on kohmakas ning teeb hilisema risttabuleerimise asjatult ebaühtlaseks.
- **Näide kavast:** \enquote{Nutikodu kasutus: ei kasuta / aeg-ajalt / regulaarselt.}
- **Mõju:** Pigem stiililine, kuid teaduslikult auditeeritavas tekstis tasub seda ühtlustada.

### 2.8 Demograafilist baasi on minimaalselt — teadlik valik, kuid maini lõputöös

- **Probleem:** Konteksti adekvaatsus. Vorm ei küsi vanust ega sugu. Lõputöö FAPH-i ja saagise tõlgendamise jaoks on kõneleja vanus ja sugu (eriti hääleulatuse mõttes) potentsiaalselt informatiivsed jaotamistunnused.
- **Mõju:** Kui plaan on neid mitte küsida (privaatsuse maandamiseks), siis on see õigustatud valik, kuid see otsus peaks olema metoodikas eksplitsiitselt põhjendatud, mitte vaikimisi valitud. Kui plaan on neid küsida, peaks vanus olema MECE vahemike kujul (näiteks 18--29, 30--44, 45--59, 60+) ja \enquote{ei soovi öelda} valikuga.

### 2.9 \enquote{Konteksti adekvaatsus} äratussõna ootuspärasele probleemile

- **Probleem:** Lõputöö arutelu peatükk (eriti §\ref{sec:benchmark-gap}) toob spetsiifiliselt välja, et \enquote{Kule} vs \enquote{Kuule} on Krati keskne probleem. Praegune küsimustik ei küsi otse, kas osaleja kogeb, et tema hääldus oli süsteemile probleem. Üks lühike Likerti väide selle kohta annaks otsese subjektiivse paari objektiivse hääldusvariandi-mõõdikuga.
- **Mõju:** Praegune vorm jätab ainult \enquote{häiriv/üllatav} avatud välja kandma seda signaali. See töötab juhul, kui osaleja ise tähele paneb; struktuurset kontrolli pole.

---

## 3. Konkreetsed soovitused ja parandused

### 3.1 Sõnasta ümber \enquote{piisavalt}-baseliinid

- **Sõnasta ümber (4):** \enquote{Süsteem reageeris õigesti, kui ütlesin äratussõna \enquote{Kuule Kratt}.}
  - *(Mõõdab subjektiivset saagist; on objektiivse äratussõna saagise paariliseks.)*
- **Lisa eraldi (4b):** \enquote{Süsteem jäi vait siis, kui mina või keegi teine ei öelnud äratussõna.}
  - *(Mõõdab subjektiivset valeaktiveeringute hinnangut; on FAPH-i paariliseks. Eraldatuna saab vältida 2.1 topelt-küsimuse probleemi.)*
- **Sõnasta ümber (5):** \enquote{Süsteem reageeris kiiresti.} (Eemalda \enquote{piisavalt}.)

Need muudatused viiksid Krati-spetsiifilised hinnangud kuueks (4, 4b, 5, 6, 7) selliselt, et iga Likerti väide räägib ühest mõõdetavast asjast ja iga väide on otseselt seotud objektiivse mõõdikuga (saagis, FAPH, latents, käsu loomulikkus, valmidus kodus kasutada).

Kui kogu vormi pikkus on probleem (10-minutilise stsenaariumi pärast), on alternatiiv käsitleda seda hinnatud paaridena ja võtta nende keskmine \emph{ainult} sisemise konsistentsuse kontrolli jaoks (Cronbachi $\alpha$), kuid \emph{mitte} ühe \enquote{usaldusväärsus}-skoorina raporteerida.

### 3.2 Sõnasta ümber \enquote{loomulikkus} ja \enquote{kodus kasutamine}

- **Sõnasta ümber (6):** \enquote{Skripti antud käsklused tundusid loomulikud eestikeelsed laused.}
  - *(Eraldab keele sõnastuse süsteemi käitumisest.)*
- **Sõnasta ümber (7):** \enquote{Kasutaksin Kratti äratussõnana enda kodu nutikodu hääljuhtimises.}
  - *(Täpsustab, et hindamise objekt on äratussõna, mitte mingi üldine häälassistent.)*

### 3.3 Lõhu \enquote{häiriv või üllatav} kaheks (kerge)

- **Sõnasta ümber (8):** \enquote{Mis oli sessiooni juures kõige häirivam?}
- **Lisa (8b, valikuline ja vabatahtlik):** \enquote{Kas oli midagi, mis sind üllatas? Kui jah, siis mis?}

Kui ajaline koorem on probleem, võib jätta ainult 8 (häiriv); kvalitatiivse riski-signaali jaoks on häiriv olulisem kui üllatav.

### 3.4 Lisa hääldusprobleemi-spetsiifiline väide

- **Lisa (Likerti 1--5):** \enquote{Süsteem mõistis mind isegi siis, kui ütlesin \enquote{Kule Kratt} \enquote{Kuule Kratt} asemel.}

See on otsene kontroll lõputöö §\ref{sec:benchmark-gap} kesksele probleemile; kui osaleja ei kuule erinevust või ei mõtle selle peale, vastab ta keskele, ja see fakt ise on diagnostiline.

### 3.5 Puhasta MECE-puudused

- **Sõnasta ümber (taust 1):** \enquote{Eesti keel on minu jaoks: emakeel / teine keel C1--C2 / teine keel B1--B2 / teine keel A1--A2 / muu / ei soovi öelda.}
- **Sõnasta ümber (taust 3):** Joonda nutikodu sageduse skaala häälassistendi omaga, näiteks \enquote{Nutikodu kasutus: mitte kunagi / harva / iganädalaselt / iga päev}.

### 3.6 Lisa minimaalne demograafia või põhjenda selle puudumine

Kui vanus ja sugu jäetakse vormist välja, lisa lõputöö kasutajatesti metoodika peatükki üks lause põhjendusega (privaatsuse minimeerimine, väike valim, et MECE-vahemikud ei tooks lisaväärtust). Kui need lisatakse, kasuta MECE vanusevahemikke ja \enquote{ei soovi öelda} valikut.

### 3.7 Seosta vormi väljad andmestiku skeemiga

Vormistuses on hetkel \texttt{participant\_id}, \texttt{date}, \texttt{session\_id}; see on hea. Lisaks tasub vormi alla lisada märkus, kuidas need väljad seostuvad \texttt{trials.jsonl} ja \texttt{kratt summarize-user-test} väljunditega; see ei ole metoodiline parandus, vaid auditeeritavuse kindlustus, et vormi vastuseid saaks tagasiulatuvalt seostada konkreetse mudeli-konfiguratsiooniga (peatüki~\ref{sec:user-test-methodology} kasutajatesti taasmängu FAPH variant).

### 3.8 Raportimisjuhis: lisa selge ootus käitlemise korral

Praegune juhis ütleb, et nelja Krati-spetsiifilist hinnangut ei liideta. Pärast 3.1 muudatust (väited 4 ja 4b on saagise / FAPH paarilised) tuleks raportimisjuhisesse lisada eksplitsiitne nõue:

- Raporteeri (4) ja (4b) eraldi mediaani + IQR-iga;
- Kuva ristttabuleeritult koos sama osaleja objektiivse äratussõna saagise ja FAPH-iga;
- Kommentaar peatükis \enquote{Tulemused} peab näitama, kas subjektiivne ja objektiivne mõõdik osutavad samale järeldusele või lähevad lahku --- viimane on §\ref{sec:benchmark-gap} \enquote{benchmark vs reaalsus} mustri otsene proov.

---

## 4. Keelelised parandused (toimetamine)

Praegu on vorm pigem inglise raamistikuga (peatükid \enquote{Required fields}, \enquote{Background}, \enquote{Reporting guidance}), aga sisuline osa --- nimelt küsimused, mida osaleja näeb --- on eestikeelne. See on töötav lahendus, kuid kasutajatestide auditi vaatest tasub parandada paar kohta:

- **Algne tekst:** \enquote{Selle süsteemi võimekused vastavad mu nõudmistele.}
  **Parandus:** \enquote{Selle süsteemi võimalused vastavad minu vajadustele.}
  **Põhjus:** \enquote{Võimekused} on kohmakas; \enquote{nõudmised} on selles kontekstis liiga formaalne. UMUX-Lite originaal \cite{lewis2013umuxlite} on \enquote{This system's capabilities meet my requirements}, mille tavapärane eesti vaste on \enquote{võimalused vastavad minu vajadustele}. Lukustatud vormis muudatus tuleb teha teadlikult ja ühtemoodi kõikidele osalejatele.

- **Algne tekst:** \enquote{Kui lihtne oli Kratiga etteantud ülesandeid lõpule viia?}
  **Parandus:** \enquote{Kui lihtne oli Kratiga ülesandeid lõpule viia?} (kui \enquote{etteantud} on juba kontekstist selge) või \enquote{Kui lihtne oli sulle antud ülesandeid Kratiga lõpule viia?}
  **Põhjus:** \enquote{Etteantud ülesandeid} on kohmakas, kuna SEQ originaal \cite{sauro2009seq} on \enquote{Overall, this task was \ldots} ja viitab konkreetsele just lõpetatud ülesandele.

- **Algne tekst:** \enquote{1 = ei nõustu üldse}, \enquote{üldse ei nõustu}.
  **Parandus:** Vali üks vorm ja kasuta seda kõikidel skaaladel järjepidevalt. Soovitan: \enquote{1 = ei nõustu üldse}, \enquote{5/7 = nõustun täielikult}.
  **Põhjus:** Vormis esinevad praegu mõlemad sõnastused (UMUX-Lite all \enquote{ei nõustu üldse}, diagnostilises plokis \enquote{üldse ei nõustu}). Järjepidevus välistab selle, et osaleja peatab vastamise sõnastuse vahetuse pärast.

- **Algne tekst:** \enquote{Mis oli kõige häirivam või üllatavam?}
  **Parandus:** Vt 3.3 (poolitamine kaheks küsimuseks); ühtlasi \enquote{üllatavam} võiks olla \enquote{üllatav}.
  **Põhjus:** Üheselt mõistetavus + ülivõrde tarbetu vältimine.

- **Algne tekst:** \enquote{Süsteem reageeris piisavalt kiiresti.} ja sarnased.
  **Parandus:** Vt 3.1 (\enquote{piisavalt} eemaldamine).
  **Põhjus:** Suunav sõnastus.

- **Algne tekst:** \enquote{consent level — metrics only / audio opt-in.}
  **Parandus:** \enquote{Nõusoleku tase: ainult mõõtmised / lisaks heli salvestamise nõusolek.}
  **Põhjus:** Osaleja-suunaline tekst peab olema eesti keeles, et nõusoleku väide oleks osalejale arusaadav; sisemise andmevälja võti võib jääda inglise keelseks (\texttt{consent\_level}), kuid osalejale näidatav silt peab olema eesti keeles.

---

## Kokkuvõte

Vorm täidab oma eesmärki: koguda lõputöö 20--30 osalejaga piloodist üks võrreldav lühike kasutatavusskoor (UMUX-Lite + SEQ) ja suunatud diagnostilisi hinnanguid Krati-spetsiifiliste mõõdikute jaoks. Audit ei tuvastanud ühtegi metoodiliselt fataalset viga. Peamine soovitus on lõhustada \enquote{usaldusväärselt} kaheks väiteks (saagis vs valeaktiveeringud), eemaldada kõikjalt sõna \enquote{piisavalt}, lõhkuda \enquote{häiriv või üllatav} topelt-küsimus ning täpsustada \enquote{selline süsteem}. Lisaks tasub puhtalt MECE-vormi viia eesti keele tase ja nutikodu kasutuse skaalad ning lisada üks väide \enquote{Kule}/\enquote{Kuule} hääldusprobleemi katmiseks --- viimane on otseselt peatüki §\ref{sec:benchmark-gap} keskses fookuses. Need muudatused tugevdavad andmete tõlgendatavust olulisel määral, ilma et küsimustik pikeneks oluliselt üle praeguse 8-küsimuse mahu.
