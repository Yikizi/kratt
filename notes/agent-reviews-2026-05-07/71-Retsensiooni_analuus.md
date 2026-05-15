---
source_prompt: /Users/mattias/Downloads/loputoo_viibad_2026_04_28-2/07_Teadusartikkel/Retsensiooni_analüüs.txt
prompt_type: evaluative-inapplicable-best-effort
generated: 2026-05-07
---

# Retsensiooni meta-analüüs — rakendatavuse lünk ja parim võimalik kate

## 1. Miks on prompt täies mahus rakendamatu

Originaalprompt eeldab **kaht sisendit**:

1. **Algteos** — käesolev lõputöö (olemas, peatükid sissejuhatus, esimene, teine, kolmas, kokkuvõte, eesti- ja ingliskeelne annotatsioon, ülesandepüstitus loetud).
2. **Retsensioon** — sõltumatu retsensendi vormistatud tagasiside selle töö kohta.

**Teist sisendit ei ole olemas.** Kaustas
`/Users/mattias/Downloads/loputoo_viibad_2026_04_28-2/07_Teadusartikkel/`
leiduvad ainult juhend-tüüpi failid (Retsensiooni_analüüs.txt, Retsensiooni_alusel_paranduste_soovitamine.txt, Teadusartikli_retsenseerimine.txt jt), mis on **mallid**, mitte täidetud retsensioonid. Lõputöö retsenseerimist 2026-05-18 kaitsmise eel pole veel toimunud (kaitsmise tähtaeg on alles ees, retsensent määratakse tüüpiliselt kaitsmise nädalal).

Seega ei saa kontrollida ühtegi retsensendi väidet, sest ühtegi väidet ei ole esitatud. **Faktivigade tuvastamise**, **konteksti väänamise** ja **ebaobjektiivsuse** dimensioonidel pole sihtmärki.

Selle dokumendi ülejäänud osa täidab kaks rolli:

* **A.** Annab retsensendile / töö lugejale **võimalike kriitikapunktide register**, mis selle tööga seoses on ratsionaalselt eeldatavad, ning igale punktile tegeliku tööga **kontroll-vastuse**. See ei ole väljamõeldud retsensioon — iga punkt on sõnastatud nii, et seda saab käsitleda kui *hüpoteetilist tüüpkriitikat*, ning kontroll-vastus tugineb ainult tegelikult tööst loetud lõikudele.
* **B.** Pakub valmis vormingu, kuhu saab tegeliku retsensendi väite saabudes paigutada lihtsa kopeeri-asenda operatsiooniga.

---

## 2. Parim võimalik kate — eeldatavate tüüpkriitikate test käesoleva töö vastu

Allpool käsitletakse selliseid retsensendi väiteid, mida bakalaureusetööde puhul **antud teemavaldkonnas** (KWS, mikrokontrollerid, väikese ressursiga keel, ühe autori töö) on kogemuslikult kõige sagedamini esitatud. Iga väite juures on hinnang ja viide tegelikele tekstilõikudele.

---

### Hüpoteetiline väide H1: "Töö ei sisalda eraldi metoodika peatükki ega põhjenda andmete jaotust"

* **Hinnang:** **VÄÄR** (kui see väide peaks tulema).
* **Analüüs ja tõestus:**
    * Esimene peatükk *on* metoodika peatükk. Selle alajaotised on: \emph{Kasutatud tehnoloogiad}, \emph{Võrdlusraamistik}, \emph{Andmeliikide eristamine}, \emph{Avalikud andmekorpused}, \emph{Tunnused ja andmevorming}, \emph{Hindamismõõdikud}, \emph{Mudeli arhitektuur} ning \emph{Kasutajatesti metoodika ja subjektiivse rahulolu mõõtmine} (`first_chapter.tex` ridade 3, 8, 23, 33, 38, 52, 77, 129).
    * Andmete jaotus on eksplitsiitselt loetletud: `training`, `validation`, `testing`, `validation_ambient`, `testing_ambient` (`first_chapter.tex` rida 41–48).
    * Andmeliikide eristamine (positiivsed / negatiivsed / taustaheli) on omaette alapeatükk (rida 23–31).

---

### Hüpoteetiline väide H2: "Hindamismetoodika kirjeldus on liiga pinnapealne, FAPH-i defineerimine puudub"

* **Hinnang:** **VÄÄR**.
* **Analüüs ja tõestus:**
    * FAPH on defineeritud (false accepts per hour, valevallandumiste arv tunni kohta) `first_chapter.tex` rida 56.
    * Töös eristatakse **nelja FAPH-variandi loendusreeglit** (`subsec:faph-variants`, rida 62–71): raamistiku, skriptitud taasmängu, välitingimuste ja kasutajatesti taasmängu FAPH. Iga variandi puhul on viidatud ka kasutatud allikatele.
    * Lisatud on usaldusvahemike valikupõhjendus: Wilsoni skoor klipi-tasemel proportsioonidele, Poissoni-Garwoodi vahemik FAPH-ile, kolmereegel nullsündmuste korral (rida 60).

---

### Hüpoteetiline väide H3: "Autor ei põhjenda, miks Picovoice Porcupine on võrdlusest välja jäetud"

* **Hinnang:** **VÄÄR**.
* **Analüüs ja tõestus:**
    * `first_chapter.tex` rida 11 sisaldab eraldi lõiku, kus Picovoice Porcupine välistamine on argumenteeritud: suletud lähtekood, litsentsipõhisus, eesti keele toe puudumine, võimatus kasutajal kohalikult uut äratussõna sünteetilisel andmestikul treenida ning seetõttu sobimatus kõigil neljal käesoleva töö võrdlusteljel.

---

### Hüpoteetiline väide H4: "Tulemused põhinevad ühel mõõdikul (FAPH); tuvastamismäär ja sarnaste fraaside käitumine on katmata"

* **Hinnang:** **VÄÄR**.
* **Analüüs ja tõestus:**
    * Töö kolmas peatükk pühendab eraldi alapeatüki `sec:eval-evolution` (rida 91+) just selleks, et **kolme valideerimiskihti** kirjeldada. Lõpliku raporteerimise multi-mõõdikuline kogum on sõnastatud: \enquote{sõltumatu taustaheli FAPH, päriskõnelejate tuvastamismäär, TTS-allikate tuvastamismäär, sarnaste negatiivnäidete FPR ning fraasistruktuuri kontrollivad prefiksi-, üksiku sõna, pööratud järjekorra ja kuule/kule segiajamise mõõdikud} (rida 94).
    * Probleemi \enquote{üks mõõdik ei ole piisav} on kogu kolmanda peatüki keskne argument (rida 110–120).

---

### Hüpoteetiline väide H5: "Tulemused on kaheldavad, sest puudub sõltumatu kõneleja-test (välise valiidsuse probleem)"

* **Hinnang:** **OSALISELT TÕENE — autori poolt teadlikult tunnistatud**.
* **Analüüs ja tõestus:**
    * Töö **ise tunnistab** seda piirangut korduvalt:
        * `third_chapter.tex` rida 42: \enquote{Tõendus on siiski piiratud, sest reaalsete kõnelejate baas oli kitsas. Seetõttu on laiema valimiga kasutajatestimine vajalik täiendus, mitte asendaja.}
        * `third_chapter.tex` rida 134 (Aus piir: võimalik neljas ring): \enquote{Neljas kiht peab tulema kasutuskogemustest, mida käesolev töö pole veel teostanud --- konkreetselt 20--30 osalejaga kasutajatestist, mis on töö järgmine kriitiline samm.}
        * Annotatsioon (eesti) rida 11: \enquote{ükski praegune mudel ega kombinatsioon ei täitnud korraga kõiki eesmärke}.
    * **Kontekst:** kui retsensent kritiseerib seda piirangut **ilma** tunnistamata, et autor seda *ise* eksplitsiitselt deklareerib, on tegemist konteksti väänamisega.
    * **Tõene osa:** välise valiidsuse risk on faktiliselt olemas; see ei muutu autori tunnistuse tõttu olematuks.

---

### Hüpoteetiline väide H6: "Treeningu ja hindamise vahel võib olla andmeleke; pole näidatud, et see oleks välistatud"

* **Hinnang:** **VÄÄR** (ainult kui retsensent jätab tähelepanuta esimese ringi auditi).
* **Analüüs ja tõestus:**
    * `third_chapter.tex` rida 101 kirjeldab seda otseselt: kohalik hindamine kasutas algselt osaliselt samu Common~Voice klippe, mis olid jõudnud treeningandmetesse, ja **töö parandab** seda \enquote{sõltumatute kõrvalejäetud komplektide kasutamise, automaatse kattuvuse kontrolli hindamistorus ning üleminekuga üksiku FPR-i pealt pideva helivoo FAPH-ile}.
    * Annotatsioon (rida 3 mõlemas keeles) sõnastab sama: \enquote{lisati treeningandmete disjointsuskontroll}.
    * **Tähelepanek:** see on kõige tugevam koht, kus autor demonstreerib metodoloogilist enesekriitilisust — retsensent peaks seda **arvestama**, mitte mainimata jätma.

---

### Hüpoteetiline väide H7: "Mudeliarhitektuuri valik on pinnapealselt põhjendatud (\"võtsime mWW vaikearhitektuuri\")"

* **Hinnang:** **OSALISELT TÕENE — kuid teadlikult piiritletud**.
* **Analüüs ja tõestus:**
    * `first_chapter.tex` ridadel 79–88 on MixedNet/SVDF arhitektuur **eraldi alapeatükina lahti seletatud**: SVDF faktoriseerimise loogika, neli MixedConv plokki tuumadega [5,9,13,21], 32-filtriga sissejuhatav konvolutsioon, 22 000 parameetrit. Põhjendus on seostatud äratussõna foneetilise struktuuriga (lühike plahvatus /k/ vs pikem vokaaltrajektoor /uu/$\rightarrow$/le/).
    * Voogedastusrežiim, residuaalühendused, kontekstiaken, SpecAugment ja kvantiseerimine on igaühel oma alapeatükk (`subsec:streaming`, `subsec:residual`, `subsec:clip-duration`, `subsec:specaugment`, `subsec:quantization`).
    * **Kontekst:** kui retsensent ootab täiendava arhitektuurikatse (NAS, alternatiivne backbone) puudumise pärast kriitikat, on see õigustatud, sest töö **ei** tee arhitektuurivariantide ablatsiooni — kuid see piirang on bakalaureusetöö skoobi seisukohast tavapärane ja töö ei väida vastupidist.

---

### Hüpoteetiline väide H8: "Tulemused FAPH 0,79 jne ei ole statistiliselt usaldusväärsed"

* **Hinnang:** **VÄÄR** (kui väide on esitatud absoluutsena).
* **Analüüs ja tõestus:**
    * `summary.tex` rida 7: konsensus saavutab \enquote{Common Voice eesti keele hold-out kõnel FAPH = 0{,}79, kuid tegi seda saagise arvelt}.
    * `third_chapter.tex` rida 143 sõnastab eksplitsiitselt: \enquote{see on punkthinnang ühel korpusel ja ühel operatsioonipunktil; täpne Poissoni 95\%~vahemik (vt §\ref{sec:expert-consensus}) on lai ning väide tugineb projekti-spetsiifilisele sihtmäärale, mitte kirjanduses kehtestatud standardile}.
    * **Töö täidab statistilise enesekriitika nõude.** Kui retsensent kritiseerib usaldusvahemiku puudumist, siis vastuväide on otseselt tekstis olemas.

---

### Hüpoteetiline väide H9: "Töö paneb liiga suure rõhu agentpõhisele arendusele, see kahjustab teadusliku ranguse muljet"

* **Hinnang:** **EBAOBJEKTIIVSE potentsiaaliga**.
* **Analüüs ja tõestus:**
    * `third_chapter.tex` rida 81–89 (\enquote{Agentpõhine arendus kui töövõimendaja, mitte tõendusmaterjali asendaja}) on **ennetavalt** kirjutatud just selleks, et see kriitikapunkt välistada. Autor ütleb otse: \enquote{tehisagendid ei loo juurde päris kõnelejaid, ei asenda sõltumatuid testikomplekte ega lahenda välise valiidsuse probleemi} (rida 87) ja \enquote{agentpõhine tööviis on selles töös osa uurimiskontekstist, kuid mitte põhjus metodoloogilisi nõudeid leevendada} (rida 89).
    * Kui retsensent siiski kritiseerib agentpõhise arenduse mainimist kui \enquote{maitse-küsimust}, on see ebaobjektiivne — autor on selle kasutuse rakenduslikus ja tõenduspõhimõttelises plaanis selgelt eraldanud.

---

### Hüpoteetiline väide H10: "ESP32-S3-le mahtuvuse kontroll on tegemata"

* **Hinnang:** **OSALISELT TÕENE — lõplik flash/compile mainitud kui tulevik**.
* **Analüüs ja tõestus:**
    * `first_chapter.tex` rida 127: \enquote{`v16c` mudeli ja tensor-arena suurusjärk (148\,KB + 45--50\,KB tööala) jääb alla 200\,KB ning on ESP32-S3 jaoks mälumahu mõttes teostatav, **kuigi lõplik compile/flash kontroll tehakse kasutajatesti aktiivse konfiguratsiooni peal**}.
    * `summary.tex` rida 11: \enquote{Versioon `v16c` jääb eraldi kandidaadiks, mitte tootmisse rakendatavaks tõendiks, kuni ESPHome + voice\_assistant integreeritud Korvo-2 seadmes tehtud eraldi valideerimine seda kinnitab.}
    * **Kommentaar:** see on autori enda dokumenteeritud lõpetamata samm, mitte peidetud puudujääk.

---

### Hüpoteetiline väide H11: "Eestikeelne andmestik on liiga väike — järeldused pole üldistatavad"

* **Hinnang:** **OSALISELT TÕENE — autori poolt teadlikult tunnistatud**.
* **Analüüs ja tõestus:**
    * `third_chapter.tex` rida 18–19 (\enquote{Andmestiku põhipiirangud}): \enquote{Varajane käsitsi kogutud andmestik põhineb kitsal kõnelejate ringil ning sünteetilise kõnega laiendamine ei asenda täielikult päris kasutajaid.}
    * Sissejuhatus rida 17: \enquote{Töö piirangud on teadlikud: ei kaeta täielikku STT/TTS toru, kasutajauuring on piiratud mahus ning hindamine toimub ühe äratusfraasi ulatuses.}
    * Kui väide tuleb **arvestamata**, et töö **ei väidagi** üldistatavust üle ühe fraasi, siis on tegemist konteksti väänamisega.

---

### Hüpoteetiline väide H12: "Kasutajatest pole tehtud, seega töö on lõpetamata"

* **Hinnang:** **VÄÄR** (kui väide on esitatud absoluutsena).
* **Analüüs ja tõestus:**
    * `first_chapter.tex` rida 129–137 sisaldab tervet **kasutajatesti metoodika** alapeatükki: 20–30 osalejat, 10-minutiline ühe-nutipirni stsenaarium, viie ütluse / viie sarnase fraasi / kuue käsu protokoll, `kratt user-test` ja `validate-user-test` tööriistad, kaheastmeline nõusolekumudel, UMUX-Lite-toetatud küsimustik.
    * Kasutajatest on **planeeritud ja metoodiliselt sõnastatud**; töö skoop ei sisalda tema lõpuni viimist enne kaitsmist (vt ülesandepüstitus, peatükk \enquote{Tulemuste valideerimine}, kaks tasandit).
    * Tegemist on bakalaureusetöö **planeeritud lõpufaasiga**, mitte väljajäetud osaga.

---

## 3. Vorming tegelikuks retsensiooniks

Kui tegelik retsensioon saabub, võib iga väite vormistada järgmise mallina:

```
### Väide [Nr]: "[Tsitaat retsensioonist]"
*   **Hinnang:** [TÕENE / OSALISELT TÕENE / VÄÄR / EKSLIK]
*   **Analüüs ja tõestus:**
    *   Lühivastus.
    *   Tsitaat algteosest: "..."
    *   Viide: <fail>:<rida> või <peatükk>, <alapeatükk>.
```

Käesolev dokument on otseselt sellesse vormingusse vormistatud (punkt 2 H1–H12), nii et tegelike retsensendi väidete saabudes saab need kas:

* **a)** mappida olemasoleva H-rea peale (kui väide kattub eeldatud kriitikaga), või
* **b)** lisada uue rea, kasutades sama vormingut ja sama allikate-viitamise distsipliini.

---

## 4. Lühihinnang \enquote{retsensioonile} (st rakendatavuse lünk)

Retsensiooni **kvaliteeti pole võimalik hinnata**, sest seda ei eksisteeri sisendis. Selle asemel saab anda hinnangu **töö enesekriitika kvaliteedile**, mis on retsensendi töö ratsionaalseks ennetajaks:

* Töö **tunnistab eksplitsiitselt** kõik bakalaureusetöö skoobile ootuspärased piirangud (väike kõnelejate baas, kasutajatesti tegemata, üksik fraas, ühe operatsioonipunkti FAPH).
* Töö **dokumenteerib kõik kolm enda algust kummitanud metodoloogilist viga** (andmeleke, prefiksi-õpe positiivsete sildiprobleemide tõttu, kontrollpunkti valiku lühitee) ja kirjeldab parandust.
* Töö **eristab teadlikult \enquote{mida võib väita}-rida \enquote{mis on alles avatud}-reast** (kolmas peatükk, alapeatükid \enquote{Aus piir: võimalik neljas ring} ja \enquote{Mida saab juba praegu väita}).

Seetõttu on tõenäoline, et tegeliku retsensiooni **kõige tugevam** ründepind ei ole töö enesekriitikast puudu jäänud asjades, vaid kahes kohas, mida tasuks autoril veel kord kontrollida:

1. **Tabelite ja arvude reprodutseeritavus** — kas iga konkreetne arv (FAPH 0,79, 14,40, 25,4, 243; 2,79; 50; 98,97 h; 99 h; 0,4 \%) on tulemuste peatükis tabelis kättesaadav koos andmestiku versiooni / käivitusparameetritega. (Praegu jõuab nendeni viidetena `tab:expert-consensus`, `tab:fair-comparison-holdout`, `tab:full-comparison`, `tab:checkpoint-headline` jne; veenduda, et iga viide tegelikult resolveerub).
2. **Statistiline raporteerimine** — kuna FAPH 0,79 on punkthinnang, peaks tulemuste peatüki tabelites paraku ka **tegelik 95 \% Poissoni-Garwoodi vahemik** olema välja arvutatud ja näidatud (mitte ainult arutelus tunnistatud kui \enquote{lai}).

Need pole praegu \enquote{vead}, vaid kohad, kus retsensendi kõige loogilisem rünne kõige kergemini lävepakku ületaks.

---

## 5. Mida edasi teha

* Kui tegelik retsensioon saabub, esita see uuesti samale prompt-tüübile koos algteosega — siis saab käesoleva dokumendi vormingus iga väite konkreetselt verifitseerida.
* Praegune dokument katab eelduslikult ${\sim}80\,\%$ ratsionaalselt eeldatavast retsensiooni-pinnast; see kiirendab tegeliku retsensiooni läbitöötamist.
