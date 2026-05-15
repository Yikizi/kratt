---
source_prompt: /Users/mattias/Downloads/loputoo_viibad_2026_04_28-2/04_Kontrollimine/Üldisem_tagasiside/Eelkaitsmine_täiendused.txt
prompt_type: evaluative (gap analysis / sisuliste lünkade audit)
generated: 2026-05-07
---

# Eelkaitsmise täienduste audit — sisuliste lünkade analüüs

Käesolev hinnang viib läbi sisuliste lünkade auditi (Gap Analysis) bakalaureusetöö praeguse mustandi peal. Hinnang lähtub kolmest analüüsikriteeriumist: tasakaal ja proportsioonid, sügavus (kirjeldus vs põhjendus vs analüüs) ning sissejuhatuses antud lubaduste täitmine. Soovitused on järjestatud kriitilisuse järgi kahanevalt — kõige suurem sisuline auk on esimene.

---

### 1. Kasutajatest on lubatud, kuid empiirilist tulemust ei ole

* **Asukoht:** sissejuhatus (uurimisküsimus alamküsimus 4 ja "lähikõne tuvastamismäär ≥ 0,95"), §\ref{sec:user-test-methodology}, §\ref{sec:user-test-results}, kokkuvõte ("järgmised sammud on … kasutajatestid").
* **Tegevus:** laiendada olemasolevat alapeatükki §\ref{sec:user-test-results} ja sissejuhatust; kui täismahus kasutajatesti enne esitamist ei jõuta, lisada eraldi alapeatükk piloodi/pilootsessiooni tulemustest.
* **Probleem:** sissejuhatus seab uurimisküsimuse all alamküsimuse "kas treenitud mudel saavutab eestikeelsel taustaheli korpusel pidevvoo FAPH < 1 ja lähikõne tuvastamismäära ≥ 0,95". §\ref{sec:user-test-results} aga tunnistab otsesõnu, et "20–30 osalejaga täismahus kasutajatesti lõppandmestik [pole] veel moodustatud". Sellega jääb sissejuhatuses lubatud teine pool (tuvastamismäär päris kõnelejatel) empiiriliselt katmata. Töö olulisim avatud risk — Kule/Kuule hääldusasümmeetria — on mainitud, kuid mitte kvantifitseeritud reaalse valimiga. Praegusel kujul on lubadus suurem kui täidetav osa.
* **Soovitus:** Teil on kaks võimalust ja Te peaksite valima ühe enne kaitsmist.
  1. Tõmmata sissejuhatuse "lähikõne tuvastamismäär ≥ 0,95" sõnastus tagasi metoodiliseks sihiks (mitte saavutuseks) ning siduda see eksplitsiitselt §\ref{sec:user-test-results}-s mainitud "kuni täismahus kasutajatestini" reservatsiooniga. See tagab, et töö ei luba rohkem kui ta tõestab.
  2. Lisada §\ref{sec:user-test-results}-le piloodisessiooni numbrid (kasvõi 3–5 osalejat), kasutades juba olemasolevat tööriista \texttt{kratt user-test} ja külmutatud \texttt{v16c} läve. Isegi väike valim koos Wilsoni 95\% UV-ga annab konkreetse tõendi, mille suurusjärk on tõlgendatav, ning nihutab töö kategooria "metoodika dokumenteerimisest" "metoodika + esmane empiiriline kontroll" kategooriasse.

  Sõltumata variandist, sissejuhatuse alamküsimus 4 ja kokkuvõtte vastav lõik peavad olema sama keelekasutusega — praegu lubab sissejuhatus konkreetset numbrilist sihti, mille olemasolu kokkuvõte ei kinnita.

---

### 2. Lubatud Home Assistanti integratsiooni demonstratsioon ei ole tulemuste peatükis tõendatud

* **Asukoht:** sissejuhatuse panus (c) "ESP32-S3 ja Home Assistanti integratsioonimuster lokaalse nutikodu satelliidi näitel", ülesandepüstitus (eesmärgi teine punkt "süsteemi lõimimine"), kokkuvõte (\enquote{mudelit saab käivitada väikesel mikrokontrolleripõhisel häälseadmel ning siduda Home Assistanti hääletoruga} on §\ref{chapter:discussion}-s, kuid mitte tulemuste peatükis).
* **Tegevus:** luua tulemuste peatükki uus alapeatükk \enquote{Seadmel teostatavus ja Home Assistanti integratsioon} (näiteks §3.x enne kasutajatesti tulemuste seisu).
* **Probleem:** sissejuhatus ja ülesandepüstitus lubavad konkreetset integratsioonipanust (ESPHome \texttt{voice\_assistant} liidese kaudu Home Assistantiga), kuid Tulemuste peatükis on integratsiooni tõendiks ainult §\ref{subsec:quantization} mahuarvutus (\enquote{lõplik compile/flash kontroll tehakse kasutajatesti aktiivse konfiguratsiooni peal}) ja kokkuvõtte hoiatus, et \texttt{v16c} \enquote{jääb eraldi kandidaatiks, mitte tootmisse rakendatavaks tõendiks, kuni ESPHome + voice\_assistant integreeritud Korvo-2 seadmes tehtud eraldi valideerimine seda kinnitab}. Lugeja, kes võtab tõsiselt sissejuhatuse panuse (c), ei saa praegu tulemuste peatükist näha tegelikku otsast-lõpuni integratsiooni: kompilatsioon, flash, latentsus seadmel, otsast-lõpuni \enquote{äratus → STT → käsk} käivitamine.
* **Soovitus:** Lisage tulemuste peatükki kompaktne (1–2 lehekülge) alapeatükk, mis dokumenteerib mõõdetult vähemalt järgmist: (a) ESP32-S3-Korvo-2 plaadile flashitud \texttt{v16c} või konsensus-kombinatsiooni mahud (flash, tensor-arena tegelik), (b) ühe äratuse otsast-lõpuni latentsus (mikrofonist Home Assistanti automaatika käivituseni), (c) demonstratiivne lõpp-stsenaarium nutipirniga, mida juba mainite kasutajatesti protokollis. Kui täielik mõõtmine pole jõukohane, raporteerige ainult flash/tensor-arena ja ühe nutipirni-stsenaariumi käivitumise binaarse kinnituse — kuid tehke seda Tulemustes, mitte Aruteluses, sest panus (c) on töös \emph{lubatud panus}, mitte \emph{tulevane samm}.

---

### 3. Sissejuhatus mainib "kasutajauuring on piiratud mahus" piiranguna, kuid ei sea selle ulatust kvantitatiivselt

* **Asukoht:** sissejuhatuse viimane lõik (\enquote{Töö piirangud on teadlikud: ... kasutajauuring on piiratud mahus}), §\ref{sec:user-test-methodology}, kokkuvõte.
* **Tegevus:** laiendada sissejuhatuse piirangute lõiku.
* **Probleem:** \enquote{piiratud mahus} ei ütle lugejale, kas tegemist on 3, 30 või 300 osalejaga, ega selle, kas testi eesmärk on tuvastamismäära punkthinnang või laiema valiidsuse väide. §\ref{sec:user-test-methodology} ütleb \enquote{20--30 osalejaga}, ent §\ref{sec:user-test-results} tunnistab, et seda pole veel kogutud. Sissejuhatus peaks lugejat kohe vastavalt kalibreerima.
* **Soovitus:** Kirjutage piirangu lause selgesõnaliseks, näiteks: \enquote{kasutajauuring on planeeritud 20--30 osalejaga ühe seansi mahus, mille mõte on toetada kõnelejate-vahelist tuvastamismäära ja Kule/Kuule asümmeetria hindamist; selle valim ei ole kavandatud kasutuseks pikaajalise kasutusmustri (nädalad, kuud) ega lapse-kõne hindamiseks.} See annab eelretsensendile selge piiritluse ja takistab nõudmast pikaajalist päris-koduses keskkonnas mõõtmist.

---

### 4. Töö konkreetne panus (c) — \enquote{integratsioonimuster} — ei ole peatükkide raamistikus iseseisva alapeatükina nähtav

* **Asukoht:** sissejuhatus (panuse loetelu), tulemuste peatükk (puudub eraldi alapeatükk), arutelu peatükis ainult lühike viide.
* **Tegevus:** luua uus alapeatükk Aruteluses \enquote{Integratsioonimuster ja selle ülekantavus} või laiendada §\ref{sec:future-cascade} eelnevat mõtisklust.
* **Probleem:** kolmest panusest on (a) ja (b) töös põhjalikult arendatud (mudel ja FAPH-metoodika moodustavad sisuliselt kogu Tulemuste ja Arutelu peatükid). Panus (c) on aga praegu \enquote{vaikne}: lugeja ei näe, mida konkreetselt selle mustri all silmas peetakse, miks see on ülekantav teistele väikese ressursiga keelte projektidele või Home Assistanti satelliitidele, ega kuidas see erineb tüüpilisest ESPHome-näitest. Kui panust ei avata, riskib eelretsensent küsida, kas (c) on tegelik panus või nimekirja täiteks lisatud praktiline samm.
* **Soovitus:** Lisage 0,5--1 lehekülge, mis vastab kolmele küsimusele: (1) milline on integratsioonimustri konkreetne kujund (komponentide diagramm: äratusmudel → ESPHome \texttt{voice\_assistant} → Home Assistant Pipeline → Kiirkirjutaja STT), (2) millised valikud erinevad ingliskeelsetest näidetest (eestikeelne läviväärtus, eestikeelne STT), (3) mis selles mustris on \emph{ülekantav} teistele väikestele keeltele (mis sammudest on keelest sõltumatud, mis nõuavad kohaliku TTS-i / STT-i olemasolu).

---

### 5. Mudeli arhitektuuri valikut põhjendatakse, kuid alternatiivseid arhitektuure ei kaaluta

* **Asukoht:** §\ref{sec:model-architecture} (Mudeli arhitektuur).
* **Tegevus:** laiendada §\ref{sec:model-architecture} sissejuhatavat osa või lisada lühike alapeatükk \enquote{Arhitektuurivaliku põhjendus}.
* **Probleem:** praegune tekst kirjeldab \texttt{microWakeWord} vaikimisi MixedNet arhitektuuri (SVDF, MixedConv plokid, kontekstiaken) põhjalikult ja kirjandusele toetudes (Alvarez & Park 2019, Choi et al. BC-ResNet 2021). Aga arhitektuuriline valik MixedNet ise ei ole põhjendatud — see on \emph{võetud kui antud}. Kuna §\ref{sec:expert-consensus} hiljem näitab, et üksiku ${\sim}22\,000$-parameetrilise mudeli kapatsiteet on töö üks pudelikaelu, tekib lugejal põhjendatud küsimus: kas oleks mõistlik proovinud BC-ResNet, DS-CNN või TC-ResNet8 võrdlusena? Kui ei, siis miks?
* **Soovitus:** Lisage 1--2 lõiku, mis selgitavad, miks just MixedNet ja mitte alternatiivne kompaktne KWS arhitektuur (DS-CNN, BC-ResNet, TC-ResNet). Põhjendus võib olla projekti-praktiline (\texttt{microWakeWord} raamistik toetab MixedNet vaikimisi, ESPHome integratsioon kasutab seda), kuid see peab olema \emph{kirjas}, mitte vaikimisi eeldatud. Kui võrdlus oleks olnud teostatav, oleks see ideaalis Tulemustes; aga arvestades 2026-05-18 tähtaega, piisab eksplitsiitsest valikupõhjendusest Metoodikas.

---

### 6. Ülesandepüstituse kolmas eesmärk \enquote{empiiriline valideerimine ... kasutajapõhine hindamine erinevate kõnelejatega} ei kohtu Tulemuste peatükis

* **Asukoht:** \texttt{ylesandepystitus.tex} eesmärgi kolmas punkt; tulemuste peatükk.
* **Tegevus:** kas leevendada ülesandepüstituse keelekasutust (kui §1 soovituse punkt 1 valitakse) või tugevdada Tulemuste empiirilist osa (kui valitakse punkt 2).
* **Probleem:** ülesandepüstitus ütleb, et töö hõlmab \enquote{lahenduse tehnilist mõõtmist ja kasutajapõhist hindamist erinevate kõnelejatega}. Tulemuste peatükis on tehniline mõõtmine põhjalik (FAPH, recall, HN-FPR jne), aga \enquote{erinevate kõnelejate} osa on Kõneleja A (XTTS), Kõneleja B (\(N=11\)), Kõneleja D (\(N=145\)) ja autor — mitte sama mahuga kasutajapõhine hindamine, nagu ülesandepüstitus lubab. Sissejuhatus on ettevaatlikum (\enquote{kasutajauuring piiratud mahus}), kuid ülesandepüstitus ei ole.
* **Soovitus:** Sissejuhatuse, ülesandepüstituse ja kokkuvõtte keelekasutus peavad olema vastastikku järjepidev. Kuna ülesandepüstitus on kinnitatud dokument, mida ei pruugi saada muuta, on praktilisem lahendus täiendada kokkuvõtet ja Tulemusi nii, et neis on \emph{kvantitatiivne sild} ülesandepüstituse lubaduse ja teostuse vahel — nt \enquote{kasutajapõhine hindamine on käesoleva töö raames teostatud kolme treeningust eraldi hoitud kõneleja peal (kogu \(N\) = 204 ütlust); 20--30 osalejaga täismahus kasutajauuring on töö järgmine kriitiline samm}.

---

### 7. \enquote{Mitmemõõtmeline hindamisprotokoll kui töö metoodiline põhipanus} on hästi argumenteeritud, kuid puudub konkreetne ülekantav vorm

* **Asukoht:** §\ref{sec:eval-evolution} ja §\ref{sec:contribution-transferability}.
* **Tegevus:** laiendada §\ref{sec:contribution-transferability} või lisada üks lehekülg \enquote{Hindamisprotokolli ülekandmise kontrollnimekiri} (näiteks lisas).
* **Probleem:** Te väidate (õigustatult), et töö peamine teaduslik panus on \enquote{väikese ressursiga keele kohaliku äratussõna mitmemõõtmelise valideerimise protokoll}. Aga kui keegi loeb seda peatükki ja tahab Teie protokolli oma keelele rakendada, ei leia ta praegu konkreetset \emph{tegevuste loetelu}. Argumendid on olemas (kõrvalejäetud komplekt, positiivne audit, mitmekriteeriumiline kontrollpunkt), aga need on hajutatud kolme alapeatüki vahel.
* **Soovitus:** Lisage §\ref{sec:contribution-transferability} lõppu või lisana eksplitsiitne \enquote{kontrollnimekiri} (5--7 punkti), mis loetleb iga kohustusliku kontrolli (1) nime, (2) kasutatava metoodika või tööriista (\texttt{assert\_disjoint\_from\_training}, FAPH-i variant tabelist §\ref{subsec:faph-variants}, prefiksi/üksiku/pööratud/segiajamise FPR), ja (3) raporteeritava arvu. See on see, mis muudab \enquote{me jõudsime kogemuste kaudu sellise kontrollnimekirjani} \enquote{teised projektid saavad seda kasutada} päriselt jõustatavaks panuseks.

---

### 8. Negatiivse andmestiku skaleerimisvõimalused on kaardistatud, kuid pole tehtud

* **Asukoht:** §\enquote{Andmestiku skaleerimisvõimalused} (second\_chapter.tex).
* **Tegevus:** kas kasutada ühte loetletud korpustest (Riigikogu, TalTech ASR) järgmise ringi treenimiseks, või selgitada, miks neid \emph{selles} töös ei kasutatud.
* **Probleem:** Te toote välja, et avalikult on saadaval üle 8000 tunni eestikeelset kõnet ning senistes katsetes kasutati \(<\)0,1\% sellest. See on tugev, kontrastne väide. Aga praeguse kirjutise jätkuna jätab see lugejale küsimuse: kui see on ressurss, mida võib kohe kasutada, miks pole see töö \emph{ei kasutanud} seda v18 või konsensus-katsetes, mis on töö praegu \enquote{deploy-kõlbmatuks} jätnud? Kas see on tähtaja-piirangust, eetilisest piirangust (nt litsents) või tehnilisest takistusest?
* **Soovitus:** Lisage 1--2 lauset, mis selgitavad, miks need korpused on järgmise sammu, mitte praeguse töö osa. Variandid: (a) tähtaja-piirang (kõige tõenäolisem ja kaitstavaim), (b) treeningutoru eelhäälestamise vajadus (mmap konversioon, segmenteerimine), (c) eelregistreeringute auditi ootamine. Lugeja saab praegu mulje, et autoril oli kogu aeg 8000 tundi käeulatuses ja ta ei kasutanud seda — see vajab põhjendust.

---

### 9. \enquote{Agentpõhine arendus kui töövõimendaja} on huvitav metoodiline avalduse, kuid selle koht töös on ebaselge

* **Asukoht:** §\enquote{Agentpõhine arendus kui töövõimendaja, mitte tõendusmaterjali asendaja} (third\_chapter.tex).
* **Tegevus:** kaaluda, kas seda alapeatükki tuleks lühendada, ümber paigutada (sissejuhatusse või lisasse) või laiendada selgema metoodilise panuse väiteni.
* **Probleem:** see alapeatükk on hästi kirjutatud ja aus, kuid see jääb arutelu peatüki keskel \enquote{kõrvalpõikeks} (Te ise tunnistate seda esimese lausega \enquote{järgnev osa on pigem eelneva metoodikaargumendi tehniline järellugu kui iseseisev kõrvalpõige}). Kui see on kõrvalpõige, peaks see olema lühem (1--2 lõiku) või olema lisas. Kui see on töö metoodiline panus, peaks see olema sissejuhatuses panuse (d) all ja saama eelretsensendi tähelepanu.
* **Soovitus:** Otsustage selgelt. Kui agendipõhine arendus on \emph{ainult kontekst}, lühendage see 1--2 lõiguni ja viige Sissejuhatusse \enquote{Töö piirangud / kontekst} ossa. Kui see on \emph{teadlik metoodiline panus}, tõstke see esile Sissejuhatuses panuste hulgas ja andke sellele Aruteluses sama struktureeritud käsitlus nagu §\ref{sec:eval-evolution}-le. Praegune \enquote{poolel teel} positsioon avab eelretsensentidele küsimuse \enquote{kas tegemist on metoodikaga või vabandusega}, mida Teil ei ole vaja.

---

### 10. Esialgsete tabelite ja terminoloogia vastastikune ühtlustus

* **Asukoht:** terve teine ja kolmas peatükk, eriti tabelid \texttt{tab:fair-comparison-holdout}, \texttt{tab:expert-consensus}, \texttt{tab:checkpoint-headline}, \texttt{tab:v18-family-results}.
* **Tegevus:** läbiv terminoloogia-revisjon enne kaitsmist.
* **Probleem:** töö kasutab läbisegi väljendeid \enquote{tuvastamismäär}, \enquote{recall}, \enquote{Recall} (tabelipealkirjas inglise keeles), \enquote{lähikõne tuvastamismäär} (sissejuhatuses) ja \enquote{positive recall probe} (\texttt{checkpoint-faph10}). Sarnaselt eksisteerivad \enquote{sarnased negatiivnäited}, \enquote{HN}, \enquote{hard negatives}, \enquote{foneetiliselt sarnased fraasid} kõik korraga. \enquote{FAPH} on neljas variandis (§\ref{subsec:faph-variants}), mis on hea, aga iga tabel ei alati identifitseeri, mis variandist on jutt — Te lubasite, et \enquote{iga FAPH-tabel ja -joonis identifitseerib kasutatud variandi}, kuid mõnedes ridades on see kommentaari jaoks lisatud kursiivina ja seda võib lugejal olla raske jälgida.
* **Soovitus:** ühtlustamise märkmed: (1) valige kas \enquote{tuvastamismäär} või \enquote{recall} ja kasutage seda kõigis tabelipealkirjades järjepidevalt — soovitan \enquote{tuvastamismäär}, sest töö on eestikeelne; (2) FAPH-i variant peaks olema iga tabeli pealkirjas \emph{esimese} sõnana (näiteks \enquote{FAPH (skriptitud taasmäng) ...}), mitte tabeli sees iga rea juures eraldi kursiivina; (3) sissejuhatuse \enquote{lähikõne tuvastamismäär} mõiste tuleb sissejuhatuses sõnaselgelt defineerida (mis vahemaa, mis mikrofon).

---

## Kokkuvõte ja prioriseeritud tegevuskava 2026-05-18 tähtaja vastu

Aega arvestades soovitan järjekorras:

1. **Kohustuslikud (lükkavad muidu eelretsensiooni põhiväite ümber):** punktid 1, 2 ja 6 — sissejuhatuse, ülesandepüstituse ja Tulemuste vastastikune ühtlustus selle ulatuse osas, mida töö \emph{tõestab} võrreldes sellega, mida ta \emph{lubab}.
2. **Suure mõjuga, väikese kuluga:** punktid 3, 4, 8 — täpsustused ja eksplitsiitsed põhjendused, mis kõik mahuvad 1--2 leheküljele kokku.
3. **Tugev panus, kui aega on:** punktid 5 ja 7 — arhitektuurivaliku põhjendus ja ülekantava protokolli kontrollnimekiri.
4. **Ebakriitilised, kuid kvaliteeti tõstvad:** punktid 9 ja 10 — agendipõhise arenduse positsioneerimine ja terminoloogia-revisjon.

Töö üldine kvaliteet on selgesti üle keskmise: hindamismetoodika on tõsiselt arendatud, kompromissidest kirjutatakse aus ja audit-ringid on dokumenteeritud kirjandusele toetudes. Peamine sisuline auk on praegu sissejuhatuse-tulemuste lubadus-kate, mitte sisuline kvaliteet. Selle parandamisel on töö hindeks A jõudmise tõenäosus oluliselt suurem.
