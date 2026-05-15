---
source_prompt: 06_Kaitsmine/Slaidiettekande_kontroll.txt
prompt_type: evaluative (slaidiaudit, esitluskoolitaja roll)
generated: 2026-05-07
---

# Slaidiettekande audit

## Märkus rakendatavuse kohta

Etteande algse promptiga eeldatakse kahte sisendit: (a) lõputöö käsikiri ja (b) **kaitsmise slaidid**. Käesolevasse ülesandepüstitusse on lisatud ainult lõputöö \texttt{.tex}-failid. Repositoorses kataloogis \texttt{docs/thesis/presentation/} leitud ainus tekstiline slaididokument on \texttt{vahekaitsmine-slaidid.md} ehk **2026-03-24 vahekaitsmise slaidid**. Need ei ole lõppkaitsmise slaidid ja sisaldavad slaidi enda päises tunnistatud andmeleket (v3--v6 tabel slaidil 7). Audit tehakse seetõttu nende slaidide alusel, kuid esitatud kommentaarides eristatakse selgelt:

* mis on vahekaitsmise slaidi tasandi probleem (st parandatav slaidi tekstis), ja
* mis on **kontseptuaalne ebakõla** lõppmaterjaliga (lõputöö §2--§3 tulemused on liikunud edasi FAPH-põhisele protokollile, ekspertkonsensusele ja \texttt{v16c} kandidaadile, mistõttu kogu vahekaitsmise tabel slaidil 7 ei ole enam lõppkaitsmise tõendiks sobiv).

Ettekande kestuseks on slaidides endis fikseeritud ${\sim}10$~minutit (juhise muutuja oli täitmata). Hindamine lähtub sellest pikkusest. Kui lõppkaitsmise tegelik aeg on 7 minutit, tuleb mahtu täiendavalt kärpida (vt §1 ajamajandus).

---

### 1. Üldhinnang ja Analüüs

* **Esitluse hinne:** 4{,}5/10. Hinne on madal mitte slaidide ülesehituse pärast, mille loogika (probleem $\rightarrow$ uurimisküsimus $\rightarrow$ arhitektuur $\rightarrow$ andmed $\rightarrow$ leid $\rightarrow$ seis $\rightarrow$ edasi) on iseenesest puhas, vaid seetõttu, et **slaidide tuumtõendid ei kattu lõputöö praeguse argumentatsiooniga**. Slaid 7 esitab v6 läbimurdena (FPR 0{,}9~\%), kuid lõputöö §2 ütleb otse, et see oli mõõtmise illusioon ja et keskseks mõõdikuks on tõstetud FAPH; lisaks on lõputöö (sissejuhatus, kokkuvõte) liikunud üksikmudeli baasjoonelt \texttt{v16c} ja ekspertmudelite konsensuse (FAPH~$=$~0{,}79) kontekstile. Kaitsmiskomisjonile praegusel kujul esitatuna tekiks lahknevus käsikirja ja slaidide vahel kohe esimeses sisuslaidis pärast tutvustust.

* **Üldine analüüs:**
  * **Suurim tugevus:** narratiivne raam slaididel 1, 6 ja 9 --- \enquote{ma ei parandanud ainult mudelit, vaid ka seda, kuidas otsustada, kas mudel on hea} --- on täpselt see metoodikaline tuum, mille üle lõputöö §2 ja §3 argumenteerivad (andmelekke avastus, FAPH, mitmekihiline hindamine). Seda tuleb lõppslaididel **säilitada**.
  * **Suurim nõrkus:** slaid 7 (\enquote{Peamine leid - degradatsiooni org}) põhineb arvudel, mille lõputöö ise on sõnaselgelt diskrediteerinud (CV~FPR~0{,}4~\%, KORVO-2~FPR~0{,}9~\%). Need tuleb asendada lõputöö §2 lõpliku tulemustetabeliga (FAPH koos 95~\% usaldusvahemikega, mitmekihiline hindamine, ekspertkonsensus FAPH~$=$~0{,}79, kontrollpunkti-FAPH eksperimendi tagasilangus saagisele). Kuni seda pole tehtud, ei saa slaide kaitsmiseks lugeda.
  * **Ajaoht:** 10~slaidi ${\times}$ 1--1{,}5~min ${=}$ 10--15~min. Slaidides on praegu summeeritud aeg ${\sim}9$~min~40~s, st mahub 10~minuti sisse. **Kui kaitsmise reaalne aeg on 7~minutit, on praegune materjal ${\sim}40$~\% liiga pikk.** Sel juhul tuleb kustutada slaidid 5 (\enquote{Arendustee lühidalt}) ja 8 (kui demot ei tehta) ning liita slaid 4 (Andmestik) järelejäänud sisuga.
  * **Keelekiht:** üldiselt korras, kuid läbivalt esinevad inglise päritolu \emph{wake word}, \emph{recall}, \emph{hard negatives}, \emph{streaming}, \emph{deploy} jne ilma eestikeelse vastendita. Lõputöös on need süsteemselt eestindatud (\emph{äratussõna}, \emph{tuvastamismäär}, \emph{rasked negatiivsed näited}, \emph{voogedastus}, \emph{juurutus}). Slaididel tuleb sama distsipliin järgida.

---

### 2. Strukturaalsed muudatused (Tervikpilt)

* **Kustutamist vajavad slaidid:**
  * **Slaid 5 \enquote{Arendustee lühidalt}** --- info kordub slaidil 6 ja 9; iseseisvana ei lisa midagi, mida ekspert ei tuleta tagasiblikkavast slaidist 6. Eemaldamine annab tagasi ${\sim}30$~s.
  * **Slaid 7 senine kuju (v3--v6 FPR-tabel)** --- ei kustutata struktuurselt, kuid **sisu** tuleb täielikult välja vahetada, sest kasutatud arvud sisaldavad andmeleket (vt slaidi enda päise märkust). Allpool slaidipõhises tagasisides on kavand asendusslaidile.
  * **Slaid 8 \enquote{Mis on juba praktiliselt töötav}** --- praegusel kujul kordab \texttt{v6} narratiivi, kuid lõputöö praegu kasutatav baasjoon on \texttt{v16c}. Kui demot ei tehta, võib slaidi 9 (\enquote{Mis on veel teha}) sisse sulatada ühe punktiga \enquote{prototüüp on Korvo-2 peal demonstreeritav}. 7-minutilise variandi puhul kustutada eraldi slaidina.

* **Puuduvad slaidid (Lisamise soovitus):**
  * **(Uus) Slaid \enquote{Hindamisprotokoll: kolm kihti}** (asendab/täiendab slaidi 4 või 7 lähedust). Märksõnad: klipi-tase, voogedastus FAPH, kasutajatest. Põhjus: lõputöö §3.5 sõnastab \enquote{kolm valideerimiskihti} ühe metoodilise põhipanusena --- praegu pole sellele slaididel ühtegi visuaalset esindust, kuid see on töö üks tugevamaid kaitsearumente.
  * **(Uus) Slaid \enquote{Lõpptulemused: FAPH ja saagise kompromiss}** (uus slaid 7). Sisu: tabel kolme tulemusega lõputöö §2 lõplikus vormis: (a) ühtne mudel \texttt{v16c} kui piloodi baasjoon, (b) ekspert~A + ekspert~B2 konsensus FAPH~$=$~0{,}79 Common~Voice ET hold-out kõnel, (c) kontrollpunkti-FAPH eksperimendi õppetund (saagise tagasilangus FAPH-i lõdvendamisel). Iga arv koos $T$ (tundide arv) ja 95~\%~UV-iga.
  * **(Uus) Slaid \enquote{Töö piirid ja ausus}** (enne küsimusteslaidi). Märksõnad: üks äratusfraas, piiratud kasutajavalim, \texttt{v16c} kandidaat, mitte tootmistõend, ESPHome + \texttt{voice\_assistant} integratsioon vajab veel valideerimist Korvo-2 peal. Põhjus: lõputöö §3.4 ja kokkuvõte deklareerivad need piirid sõnaselgelt; nende slaidile toomine vähendab komisjoni ohtu küsida \enquote{aga miks te ei...} mõistlikult eeldatava skoobi kohta.

---

### 3. Slaidipõhine tagasiside

**Slaid 1: Probleem ja väide**

* **Sisu parandused:** lause \enquote{Probleem ei ole STT puudumine, vaid see, et kasutaja peab süsteemi kuidagi loomulikult äratama} on tugev avalause --- jätta. Esimene täpploend \enquote{Eesti keele jaoks puudub praktiline ja lokaalne wake word lahendus} on liiga absoluutne ja ei haaku lõputöö sissejuhatusega, mis täpsustab, et puudub eelkõige **MCU-klassi mudel**, mitte üldse äratussõna lahendus (Picovoice on olemas, ent suletud ja ilma eesti keele toeta). Soovitus muuta täpploend kujule: \enquote{Eesti keele jaoks puudub avatud, lokaalne, MCU-klassi äratussõnamudel}. Väide-täpploend (\enquote{Kuule Kratt teostatav ESP32-klassi seadmel}) on liiga nõrk lõpputulemuse kohta, mille lõputöö tegelikult deklareerib --- soovitus täpsustada: \enquote{teostatav lokaalselt, mõõdetava FAPH-i ja kompromisside dokumenteerimisega}.
* **Keelelised parandused:**
  * Vigane: \enquote{wake word lahendus} $\rightarrow$ Parandus: \enquote{äratussõna lahendus} (toorlaen; lõputöös süsteemselt eestindatud).
  * Vigane: \enquote{Pilvepõhised lahendused ei sobi privaatsusnõudega kasutusjuhtudesse} $\rightarrow$ Parandus: \enquote{Pilvepõhised lahendused ei sobi privaatsust nõudvateks kasutusjuhtudeks} (käändeviga: \enquote{kasutusjuhtudesse} ei ole õige rektsioon \enquote{ei sobi} järel).

**Slaid 2: Töö eesmärk ja uurimisküsimus**

* **Sisu parandused:** struktuur on hea. Uurimisküsimuse kolm täpploendit (\enquote{täpne, lõimitav, kasutatav}) on lõputöö ülesandepüstituse kolme telje (mudeliarendus, süsteemi lõimimine, empiiriline valideerimine) lühiprojektsioon --- jätta. Lisada tuleks üks **mõõdetav siht**: lõputöö sissejuhatuses on see fikseeritud kui \enquote{FAPH~$<$~1 ja lähikõne tuvastamismäär~$\geq$~0{,}95}. Ilma selleta ei mõista ekspert, mida tähendab \enquote{piisavalt täpne}.
* **Keelelised parandused:**
  * Vigane: \enquote{wake word} $\rightarrow$ Parandus: \enquote{äratussõnamudel} (toorlaen).

**Slaid 3: Süsteemi arhitektuur**

* **Sisu parandused:** ASCII-skeem on kompaktne ja loetav. Kuid voo all olev nimekiri mainib \enquote{Wyoming} integratsiooni --- lõputöös (sissejuhatus, ülesandepüstitus, §1) on integratsioon **konsekventselt** kirjeldatud kui ESPHome + \texttt{voice\_assistant}, mitte Wyoming. Wyoming on planeerimisdokumentide ajalooline jälg. Soovitus eemaldada \enquote{Wyoming}, et slaid ei räägiks vastu käsikirjale.
* **Keelelised parandused:**
  * Vigane: \enquote{Deploy formaat} $\rightarrow$ Parandus: \enquote{Juurutusvorming} (toorlaen).
  * Vigane: \enquote{wake word raamistik} $\rightarrow$ Parandus: \enquote{äratussõna raamistik}.

**Slaid 4: Andmestiku strateegia**

* **Sisu parandused:** tabel on selge ja edastab põhi-idee \enquote{õiged andmed õiges rollis}. Paranduseks: lõputöö §1.3 eristab kolme andmeliiki (positiivsed, negatiivsed, **taustaheli salvestused**) ja rõhutab, et **taustaheli on omaette kategooria**, mitte negatiivsete alaliik. Slaidi tabelis on \enquote{MUSAN + Korvo-2 ambient} liigitatud rollile \enquote{streaming false positive hindamine}, mis on õige, kuid eraldiseisev rida \enquote{taustaheli} muudaks slaidi sõnumi kooskõlla §1.3-ga. Lisaks: rida \enquote{TTS hard negatives} (\enquote{Hei Kratt}, \enquote{Tere Kratt}, \enquote{Kratt}) on lõputöö §2.5 ja §2.7 (Teine auditiring, fraasi-täielikkuse protokoll) järgi eluliselt oluline ja vääriks rasvas kirjas.
* **Keelelised parandused:**
  * Vigane: \enquote{hard negatives} $\rightarrow$ Parandus: \enquote{rasked negatiivnäited} (lõputöös süsteemselt nii).
  * Vigane: \enquote{ambient} $\rightarrow$ Parandus: \enquote{taustaheli}.
  * Vigane: \enquote{streaming false positive hindamine} $\rightarrow$ Parandus: \enquote{voogedastuse valepositiivse käitumise hindamine}.

**Slaid 5: Arendustee lühidalt**

* **Sisu parandused:** soovitatav slaid kustutada (vt §2 ülal). Kui see siiski jääb, siis täpploend \enquote{toru metodoloogiline parandamine + iteratiivne arendus} on adekvaatne, kuid praeguste sõnastustega (\enquote{Algusfaasis sõnastasin probleemi ja proovisin erinevaid voice assistant radu}) tekib eksitav mulje, et töö oli laialivalguv. Lõputöö narratiiv on rangem: probleem $\rightarrow$ avalik kontrollkatse $\rightarrow$ andmelekke avastus $\rightarrow$ FAPH-protokoll $\rightarrow$ ekspertkonsensus. Kui slaid jääb, vahetada täpploendid välja nende viie etapi vastu.
* **Keelelised parandused:**
  * Vigane: \enquote{voice assistant radu} $\rightarrow$ Parandus: \enquote{häälassistendi alternatiive} (toorlaen ja kõnekeelne mitmus).

**Slaid 6: Mis ei töötanud alguses**

* **Sisu parandused:** **see on ettekande tugevaim slaid ja seda tuleb säilitada**. Kolm probleemiklassi (treeningukeskkond, eksitav evaluatsioon, domeeninihe) on täpne kondenseering lõputöö §2 ja §3 mitmest ringist. Soovitus: lisada **üks number**, mis muudab abstraktse \enquote{mõõtmise illusioon} narratiivi kaitstavaks --- nt lõputöö §2-st pärit konkreetne klipi-FPR vs. voogedastus-FAPH lahknevus (v6 MacBook~Pro mikrofon, FAPH~${\approx}$~50, vt sissejuhatus). Üks arv siin maandab kogu järgneva metoodikaargumendi.
* **Keelelised parandused:**
  * Vigane: \enquote{streaming ambient hindamist} $\rightarrow$ Parandus: \enquote{voogedastuse-tasemel taustaheli hindamist}.
  * Vigane: \enquote{ei triggerdanud} $\rightarrow$ Parandus: \enquote{ei vallandunud} (lõputöös süsteemselt \emph{vallanduma}).

**Slaid 7: Peamine leid - degradatsiooni org**

* **Sisu parandused:** **slaid tuleb sisuliselt välja vahetada.** Praegune tabel (v1--v6, FPR Common~Voice ja Korvo-2) põhineb arvudel, mille slaidi enda päise märkus ja lõputöö §2 alapeatükk \enquote{Andmelekke avastamine ja korrigeeritud hindamine} on diskrediteerinud kui treeningandmete osahulgalt arvutatud (st mudel oli neid klippe juba näinud). Selle slaidi näitamine kaitsmisel võrdub teadaolevalt vigase tõendi esitamisega.

  Asendusslaidi kavand (märksõnad, mitte täislaused):
  * Pealkiri: \enquote{Lõpptulemus: kolm tulemust, mitte üks}.
  * Tabel kolme reaga, kõikidel veerud: mudel/konfiguratsioon, FAPH (sh $T$ tundi ja 95~\% UV), tuvastamismäär, märkus.
    * \texttt{v16c}: piloodi baasjoon, üksikmudel.
    * Ekspert~A + ekspert~B2 konsensus: FAPH~$=$~0{,}79 Common~Voice ET hold-out kõnel; saagise hind eraldi reas.
    * Kontrollpunkti-FAPH eksperiment: FAPH-i lõdvendamine $\rightarrow$ saagis paranes ainult osaliselt, valeaktiveeringud kasvasid kiiresti tagasi.
  * All üks lause: \enquote{Üks mudel ei suuda kõiki sihte korraga --- see ongi peamine leid}.

  Hüpoteesid H1/H2 võib slaidilt eemaldada. Vahekaitsmise H1/H2 raamistik (\enquote{sama-seadme negatiivid parandavad eristusvõimet}, \enquote{generaliseerub teisele mikrofonile}) on lõputöös §2.6--§2.8 (ristmikrofoni asümmeetria) edasi arenenud ja H2 kinnitus on osutunud asümmeetriliseks. Hüpoteesi-stiilis esitlus tekitab komisjonile ootuse, mille lõputöö ise on lammutanud.
* **Keelelised parandused:**
  * Vigane: \enquote{Recall} $\rightarrow$ Parandus: \enquote{tuvastamismäär}.
  * Vigane: \enquote{generaliseerub teisele mikrofonile} $\rightarrow$ Parandus: \enquote{üldistub teisele mikrofonile} (lõputöö §2.7 termin).
  * Vigane: \enquote{degradatsiooni org} $\rightarrow$ Parandus: kui slaid säilitab Park~et~al. viite, kasutada \enquote{degradeerumise org}; soovitatud uue slaidi puhul aga viidet üldse mitte kasutada, sest see slaid ei ole enam selle nähtuse kohta.

**Slaid 8: Mis on juba praktiliselt töötav**

* **Sisu parandused:** slaid kordab \texttt{v6} kui käivitatud mudelit. Lõputöö kokkuvõte ütleb otse, et \texttt{v16c} on piloodi aktiivseks kandidaadiks valitud kvantiseeritud TFLite-mudel ja et \enquote{v16c jääb eraldi kandidaadiks, mitte tootmisse rakendatavaks tõendiks, kuni ESPHome + \texttt{voice\_assistant} integreeritud Korvo-2 seadmes tehtud eraldi valideerimine seda kinnitab}. Slaid tuleb seetõttu **viia 2026-04 seisu**: mudelina mainida \texttt{v16c}, integratsioon ESPHome + \texttt{voice\_assistant} kaudu, juurutus mahuga ${\sim}148$~KB + ${\sim}45$--$50$~KB \texttt{tensor\_arena} (lõputöö §1.7.6). Demo soovitus jätta minimaalsena, ausa varuvariandiga (\enquote{kui demo on riskantne, ütlen lihtsalt, et süsteem on demonstreeritav}) --- see on klassikaliselt hea kaitsetaktika.
* **Keelelised parandused:**
  * Vigane: \enquote{deploy'itud} $\rightarrow$ Parandus: \enquote{juurutatud}.

**Slaid 9: Mis on veel teha ja miks töö on kaitstav**

* **Sisu parandused:** struktuur \enquote{veel teha} + \enquote{miks juba tugev} on hea kaitsmisretooriline samm. Kuid täpploend \enquote{lõputöö kirjutamine ja formaliseerimine} ei sobi **lõppkaitsmise** slaidile (lõputöö on selleks hetkeks valmis). Sõnastus oli kohane vahekaitsmiseks, mitte 2026-05 kaitsmiseks. Asendada \enquote{täismahus kasutajatesti läbiviimine, kasutajatesti taasmäng külmutatud lävega varimudelite peal} (vastab lõputöö §1.10 ja §2.9 plaanitud sammudele).

  Lõpulause-soovitus (\enquote{reprodutseeritav tee, kuidas väikese keeleruumi äratussõna usaldusväärselt arendada}) on tugev ja seda tuleks **säilitada sõna-sõnalt**. Lõputöö kokkuvõte sõnastab sama ideed: \enquote{määrav metodoloogiliselt korrektne hindamine, mitte üksnes mudeli treenimine}.
* **Keelelised parandused:**
  * Vigane: \enquote{rohkem kõnelejaid positiivsetesse} $\rightarrow$ Parandus: \enquote{positiivse kõnelejavalimi laiendamine} (lõputöö kokkuvõtte sõnastus).

**Slaid 10: Küsimused**

* **Sisu parandused:** Sisu ja keel on korras, muudatusi pole vaja. Soovitus ainult eemaldada repo URL ülemineku-slaidilt, kui kaitsmine on TalTechi sisene ja repo ligipääs piiratud --- aga see on protseduuriline, mitte sisuline.
* **Keelelised parandused:** Keelevigu ei tuvastatud.

---

### Üldine soovituste järjekord (rakendamise prioriteet)

1. **Asendada slaid 7 sisu** lõputöö §2 lõplike FAPH-tulemustega (kõige suurem risk auditi mõttes; ilma selleta ei ole slaidid kaitstavad).
2. **Lisada \enquote{kolm valideerimiskihti}** uue slaidina enne praegust slaidi 7 (toetab uut slaidi 7 ja muudab metoodilise panuse nähtavaks).
3. **Viia slaid 8 (mudel, integratsioon, mahud) 2026-04 seisu** (\texttt{v16c}, ESPHome + \texttt{voice\_assistant}, mitte Wyoming).
4. **Eemaldada Wyoming slaidilt 3** ja toorlaenud kõikidelt slaididelt.
5. **Eemaldada slaid 5** ja vajadusel slaid 8, kui kaitsmise aeg on 7~min, mitte 10~min.
6. Lõpetuseks: **kasutada slaide 1, 6 ja 9 sõnastusi sõna-sõnalt edasi** --- need on lõputöö narratiivi tugevaim kondenseering ja need ei vaja muuta.
