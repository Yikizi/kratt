---
source_prompt: Eelkaitsmine_retsensioonina_pöördprojekteeritud.txt
prompt_type: evaluative
generated: 2026-05-07
---

# RETSENSIOON

**Tallinna Tehnikaülikool, Infotehnoloogia teaduskond**

**Lõputöö pealkiri:** Eestikeelse äratussõna tuvastus piiratud ressursiga nutikodu mikrokontrolleril (projekt „Kratt", fraas „Kuule Kratt")
**Lõputöö autori nimi:** Mattias Linholm
**Retsensendi nimi, ametikoht, asutus/organisatsioon:** *(täidab retsensent enne allkirjastamist)*

---

## Lühike kirjeldus tööst

Töö käsitleb eestikeelse äratussõna tuvastusmudeli arendamist ESP32-S3 klassi mikrokontrollerile, kasutades \texttt{microWakeWord} raamistikku ja TensorFlow Lite vormingusse kvantiseeritud INT8-mudelit. Autor rekonstrueerib varasema treeningu- ja hindamistoru, valideerib selle avalikul \texttt{Speech Commands} \texttt{marvin} kontrollkatsel ning treenib mitukümmend eestikeelse äratussõna mudeliversiooni (v1--v8 põhiseeria, hilisemad v13--v18, ekspertmudelid, \texttt{v16c}-baasjoon ning ekspertide konsensus). Töö metoodiline keskmes on äratussõna mudelite mitmemõõtmeline hindamisprotokoll: klipitaseme tuvastamismäära ja FPR-i kõrval kasutatakse FAPH-i (\emph{false accepts per hour}) variante (raamistiku, skriptitud taasmängu, välitingimuste ja kasutajatesti taasmäng), fraasistruktuuri kontrollivaid teste (prefiks, üksiksõna, pööratud järjekord, \enquote{kuule}/\enquote{kule}-segiajamine) ning Wilsoni ja Poissoni-Garwoodi usaldusvahemikke.

Töö peamiseks teaduslikuks panuseks on autor ise sõnastanud \emph{väikese ressursiga keele kohaliku äratussõna mitmemõõtmelise valideerimise protokolli} (kolme valideerimiskihi muster: andmeleke $\rightarrow$ vale positiivne klass $\rightarrow$ kontrollpunkti valikukriteerium). Selle empiiriliseks aluseks on dokumenteeritud lahknevus standardsete KWS võrdlusaluste ja reaalse kasutuskogemuse vahel (§\ref{sec:benchmark-gap}), mis on illustreeritud konkreetsete numbritega (nt v6 mudeli FAPH${\sim}50$ MacBook Pro mikrofonil vs.\ Common~Voice ET FPR 0,4\%). Praktilise tulemusena raporteeritakse ekspertmudelite konsensuse tulemus FAPH=0,79 Common~Voice ET kõrvalejäetud komplektil, ent autor ise täpsustab, et tegu on punkthinnanguga ühel korpusel ja ühel operatsioonipunktil ning lai Poissoni 95\%-vahemik ning kasutajatestide puudumine ei luba veel juurutusotsust teha.

Töö esitatud osa on sisuliselt kirjutatud ja struktuurselt terviklik (sissejuhatus, metoodika, tulemused, arutelu, kokkuvõte; eestikeelne ja ingliskeelne lühikokkuvõte täidetud). Kõige nähtavam puudus on, et keskne lõpp-tõendus --- 20--30 osalejaga kasutajatest, mida autor ise nimetab \enquote{neljandaks valideerimiskihiks} (§\ref{sec:fourth-round}) ja millest sõltub juurutusotsus (§\ref{sec:user-test-methodology}) --- on tööversiooni esitamise ajal alles kavandamise ja külmutuse-eelses faasis. Sellega seoses tuleb tööd hinnata kui \emph{tugevalt edenenud, kuid lõpphindamise osas teadlikult lõpetamata bakalaureusetööd}: protokoll on dokumenteeritud, kuid ei ole sõltumatu kõnelejavalimi peal kinnitatud.

### Tugevused

- **[s1]** (kogu töö, eriti §\ref{sec:eval-evolution} ja §\ref{sec:benchmark-gap}, sisu): autor sõnastab oma teadusliku panuse \emph{teadlikult mittevõistlevana} \enquote{parima eesti äratussõna mudeli} suhtes ja paigutab selle hindamisprotokolli tasandile. See on bakalaureusetöö ulatusele realistlik ja akadeemiliselt korrektne raamistus.
- **[s2]** (peatükk \ref{chapter:method}, §\ref{subsec:faph-variants}, sisu): nelja FAPH-variandi (raamistiku, skriptitud taasmängu, välitingimuste, kasutajatesti taasmäng) eksplitsiitne eristamine ning iga tabeli/joonise juures variandi identifitseerimise kohustus on sisuline metoodiline panus, mis adresseerib otseselt äratussõna kirjanduses tuntud reprodutseeritavuse-auku \cite{lopezespejo2021deepkws}.
- **[s3]** (peatükk \ref{chapter:method}, §\ref{sec:user-test-methodology}, sisu): kasutajatesti disain on hoolikalt eraldatud treeningust (heli läheb hindamisandmestikuks, mitte treeningusse), kasutab külmutatud läve ja taasmängu mitme varimudeli peal --- see väldib mudelispetsiifilist osalejakoormust ning loob võrreldava aluse mudelite võrdluseks identsel sisendil.
- **[s4]** (peatükk \ref{chapter:method}, §\ref{sec:user-test-methodology}, sisu): subjektiivse rahulolu instrumentide eristamine valideeritud lühiskaalaks (UMUX-Lite \cite{lewis2013umuxlite,sauro2009seq}) ja diagnostiliseks uurija-koostatud osaks on metoodiliselt aus ning väldib kohatut \enquote{koondskoori} esitamist.
- **[s5]** (peatükk \ref{chapter:method}, §\ref{sec:model-architecture}, sisu): MixedNet/SVDF arhitektuur on põhjendatud nii kirjanduses (\cite{alvarez2019svdf,chen2014smallfootprint,sainath2015cnn,choi2021bcresnet}) kui ka Eesti äratussõna foneetilises spetsiifikas (lühike /k/ vs.\ pikem vokaaltrajektoor /uu/$\rightarrow$/le/), mis demonstreerib teadlikkust nii üldarhitektuurist kui ka domeenist.
- **[s6]** (peatükk \ref{chapter:method}, §\ref{sec:user-test-methodology}, sisu): kõikidel hindamisetappidel on \texttt{kratt} CLI-tööriist (\texttt{user-test}, \texttt{validate-user-test}, \texttt{replay-user-test}, \texttt{summarize-user-test}). Reprodutseeritav tööriistastik on bakalaureusetöös harv ning siin oluliselt tugevdatud.
- **[s7]** (peatükk \ref{chapter:discussion}, §\ref{sec:three-rounds}--§\ref{sec:general-principle}, sisu): kolme valideerimiskihi narratiiv (klipi FPR $\rightarrow$ kolm-mõõdikuline raporteerimine $\rightarrow$ kontrollpunkti valikukriteerium) on metoodiliselt küps ja näitab autori võimet tõlgendada negatiivseid tulemusi kui distsipliini täiendavaid tõendeid.
- **[s8]** (sissejuhatus, lk 1; peatükk \ref{chapter:discussion}, §\ref{sec:fourth-round}, sisu): \enquote{usaldusväärsuse} mõiste on määratletud projektispetsiifilise operatsionaalse sihina (FAPH${<}1$, recall${\geq}0{,}95$), mitte kirjanduses kehtestatud universaalse standardina; samuti on aus tunnistus võimaliku \enquote{neljanda ringi} olemasolust.
- **[s9]** (peatükk \ref{chapter:method}, sisu): Wilsoni \cite{wilson1927probable,brown2001interval} ja Poissoni-Garwoodi \cite{garwood1936fiducial,ulm1990poisson} usaldusvahemike kasutamine ning \enquote{kolmereegli} \cite{hanley1983ruleofthree} eksplitsiitne kasutamine null-sündmustega rajadel on statistiliselt korrektsem kui valdkonnas tüüpiline punkthinnangute esitamine.
- **[s10]** (peatükk \ref{chapter:discussion}, §\ref{sec:future-cascade}, sisu): konsensushindamise paigutamine kaskaadarhitektuuri \cite{gruenstein2017cascade,apple_voice_trigger_2023,michaely2017googlekws,sigtia2020multitask,garg2021streaming} erijuhuna sidub töö tulemused tööstuspraktikaga ja näitab arendussuundi.

### Nõrkused

- **[w1]** (kogu töö, sisu/staadium): kõige olulisem empiiriline tõenduslüli --- 20--30 osalejaga kasutajatest --- on töö esitatud versioonis kavandamise ja külmutuse-eelses faasis (§\ref{sec:user-test-methodology}, §\ref{sec:fourth-round}, kokkuvõte lk 11). See tähendab, et töö \enquote{neljas valideerimiskiht} ei ole veel täidetud ning juurutusotsus on autori enda sõnastuses lahtine. Bakalaureusetöö lõppjäreldused tuginevad seega eeskätt offline-tõenditele.
- **[w2]** (peatükk \ref{chapter:results}, lk ${\sim}4$, sisu): tabel~\ref{tab:fair-comparison} (v1/v3 võrdlus) on esitatud ainult ühel läviväärtusel (0,99); §\ref{sec:eval-evolution} pakub välja \enquote{komposiitse kontrollpunkti valikukriteeriumi}, kuid lugeja ei näe selle koondkriteeriumi ühtset matemaatilist sõnastust ega operatsionaliseeringut (kuidas täpselt kaalutakse FAPH-i, recall'i ja fraasistruktuuri eksimusi).
- **[w3]** (peatükk \ref{chapter:method}, §\ref{subsec:specaugment} ja §\ref{subsec:residual}, sisu): autor ise teeb selgeks, et v7 oli süsteemitaseme variant, mis ei sobi SpecAugmenti põhjusliku mõju tõendamiseks, ning v6-residual oli ablatsioon. v13a/v13b kontrollitud ablatsiooni tulemustabel ei ole esimeses 100 reas teises peatükis nähtav --- lugeja peab usaldama, et see eksisteerib hilisemates tabelites; \enquote{Aktiivne valideeritud kontrollpunkt vs.\ enesedeklaratsioon} eristust tuleks lugeda igal pool.
- **[w4]** (peatükk \ref{chapter:discussion}, §\ref{sec:benchmark-gap}, alajaotus \enquote{Põhjus 1}, sisu): autor kirjutab, et \enquote{täpne ütluse-tasandi skoorijaotus pole eraldi artefaktina fikseeritud}. See on ausalt tunnistatud, kuid ka väga oluline tükk, mis võiks olla viidatud konkreetsele tulevasele jaotisele või lisale --- praegu jätab see lünga ühe töö keskse väite (TTS-positiivne paisutab tuvastamismäära) empiirilises tugevuses.
- **[w5]** (peatükk \ref{chapter:results}, §\ref{sec:benchmark-gap} viide \enquote{ptk~\ref{chapter:results}}, sisu/struktuur): arutelu peatükk viitab korduvalt tulemuste peatüki tabelitele ja jaotistele (\texttt{tab:checkpoint-headline}, \texttt{tab:full-comparison}, \texttt{tab:fair-comparison-holdout}, \texttt{tab:expert-consensus}, §\ref{sec:data-leakage}, §\ref{sec:positive-audit}, §\ref{sec:expert-consensus}). Esitatud peatükkide ulatuses on need viited olemas, ent ekspertkonsensuse 0,79 FAPH-i Poissoni 95\%-vahemiku konkreetne arvuline ulatus ei ilmu sissejuhatuses ega arutelu \enquote{Mida saab juba praegu väita} loendis --- ainult viide selle olemasolule \cite{garwood1936fiducial}. Lugeja ei saa ühelt vaatelt aru, kas vahemiku ülemine piir on lähedal projektisihile FAPH${<}1$.
- **[w6]** (peatükk \ref{chapter:results}, §\ref{sec:cross-mic-asymmetry} viide sissejuhatuses, sisu): sissejuhatuses lk 1 esitatakse v6 MacBook Pro mikrofoni FAPH${\approx}50$ kui üks töö motivatsiooninumbreid. Selle arvulise kalibratsioonikorvi (proovi pikkus, transkriptsiooni protokoll, läviväärtus) detailid on viidatud, kuid sissejuhatusse ulatuses, mis lugejal varakult kahtluse kõrvaldaks, ei ole esitatud --- mitte vea, vaid rütmistuse tähenduses.
- **[w7]** (peatükk \ref{chapter:discussion}, §\ref{sec:benchmark-gap}, alajaotus \enquote{Põhjus 4}, sisu): \enquote{Mittekõneliste helide puudumine} on toodud välja kui standardsete benchmarkide piirang, kuid samas tunnistatakse, et \enquote{süstemaatilist aktivatsioonimäära mittekõnelistel stiimulitel käesolevas töös eraldi ei mõõdetud}. Kuna see on üks töö neljast põhjendusest standardsete võrdlusaluste ebapiisavusele, langetab mõõtmise puudumine selle põhjenduse tõenduslikku jõudu.
- **[w8]** (peatükk \ref{chapter:method}, §\ref{sec:model-architecture} ja §\ref{subsec:quantization}, vormistus): TFLite-mudeli ja \texttt{tensor\_arena} suurused on antud nii varasemate (${\sim}57$\,KB) kui ka \texttt{v16c} (148\,KB; ${\sim}107$\,KB koos töömäluga; ESPHome lisaks 45--50\,KB) puhul, ent koondtabel mudeliversioonide \emph{mahtude} kohta puudub. See raskendab kvantiseerimise mõju silmaga jälgimist.
- **[w9]** (sissejuhatus ja kokkuvõte, sisu): autor mainib, et \texttt{v16c} on \enquote{piloodi aktiivne kandidaat}, ent jätab juurutusotsuse kasutajatesti tulemuse järele. Lugeja, kes ootab bakalaureusetöö lõpus selget mudelivalikut, võib seda kogeda kui \emph{lahtine järeldus}; see ei ole metoodiline viga, kuid tuleb eelkaitsmisel selgelt põhjendada.
- **[w10]** (peatükk \ref{chapter:discussion}, §\ref{sec:future-cascade}, sisu): kaskaadarhitektuuri ettepanek on hästi viidatud, kuid arutelu ei sisalda konkreetset eelhinnangut, kas teine aste mahuks ESP32-S3 ressursipiirangutesse, või eeldatakse, et teine aste käivitub Raspberry Pi 5 hostis. Selle praktilise piiritluse puudumine jätab edasiste suundade ettepaneku üldsõnaliseks.
- **[w11]** (sissejuhatus, lk 1, sisu): sissejuhatus läheb otse kontekstist (eestikeelse äratussõna lünk) ja FAPH-mõõdikust töö konkreetsete sihtmäärade juurde, kuid ei sõnasta eraldi peatükina või lõiguna nõustaja-soovituslikul kujul \enquote{lahendamata probleemi formuleeringut} --- probleem on ridade vahel selge, kuid eelkaitsmisel oodatakse seda tihti eraldi ühe lausena.
- **[w12]** (kogu töö, vormistus): annotatsioonid on täidetud (eesti+inglise), kuid \texttt{\textbackslash calculatepages} jt automaattäitmise väärtused saavad lõplikud arvud alles kompileerimisel; kontrollkompileerimine ja lehekülje-/joonise-/tabelinumbrite verifitseerimine peab olema enne kaitsmist tehtud, et lugeja ei näeks \enquote{0 jooniseid} või muid kohatuid arve.

---

## Tekstiline hinnang

### Sisu ja analüüs

- Töö uurimisküsimused on sõnastatud konkreetselt ja operatsionaliseeritavalt (sissejuhatus lk 1: pidevvoo FAPH${<}1$ ja lähikõne recall${\geq}0{,}95$). Alamküsimused on hierarhiliselt korrektsed --- toru valideerimine $\rightarrow$ andmestiku rolli analüüs $\rightarrow$ andmestiku-puuduste eraldamine toru piirangutest $\rightarrow$ sihtmäära saavutamine. Selline hierarhia annab tööle metoodilise selgroo.
- Metoodika on tugev kahel tasandil: (a) hindamisprotokolli enda kujundamine kolme valideerimiskihina ja (b) selle toetamine eksplitsiitsete usaldusvahemikega ja FAPH-variandi-disambigueeringuga. Need on töö juurkontribuudid, mille autor on ise õigesti identifitseerinud.
- Tulemuste osas on positiivne see, et negatiivseid (s.t.\ esialgu eksitavaid) tulemusi käsitletakse kui tõendusmaterjali, mitte kui peidetud ebaõnnestumisi. Andmelekke avastus, positiivse klassi sildistusprobleem ja kontrollpunkti valikukriteeriumi laiendamine on bakalaureusetöö narratiivi seisukohalt väärtuslikud.
- Töö valmidusaste \emph{lõppjärelduste} osas on osaliselt: kasutajatest pole veel teostatud, mistõttu \enquote{kas mudel on juurutuskõlblik} on autori enda sõnastuses lahtine küsimus. See on metoodiliselt aus, kuid lõpetamata bakalaureusetöö juures võib mõjutada hinde-soovitust.
- Järelduste loend §\enquote{Mida saab juba praegu väita} on hästi piiritletud (mida väidab vs.\ mida ei väida); sarnast distsipliini võiks rakendada ka kokkuvõttes, mis praegu kordab arutelu, kuid mitte kõiki piiritlusi.

### Töö maht ja ülesande keerukus

- Töö maht on bakalaureusetöö ootuspärasele ulatusele tugevalt vastav: teine peatükk on 686 rida, kolmas 152 rida (LaTeX-allikas), eestikeelne kokkuvõte lühike ja keskendunud. Ridade arv viitab sellele, et valminud peatükkide tasakaal on Tulemuste peatüki kasuks --- mis on TalTech IT teaduskonna soovitatud jaotuse järgi (chapter:results 30--40\%) õigesti kaalutud.
- Ülesande tehniline keerukus on bakalaureusetöö jaoks kõrge: andmestikud, treeningu raamistiku integreerimine, INT8-kvantiseerimine, ESP32-S3 paigaldus, kahe raamistiku võrdlus, mitmemõõtmeline hindamine, Androidi logija, \texttt{kratt} CLI ökosüsteem ja kavandatav 20--30 osalejaga kasutajatest. Mahuline ettevalmistustöö on selgelt suurem kui \enquote{üks mudel + üks raport}.
- Eraldi väärib märkimist, et autor on teadlik tehisagent-arenduse mõjust töömahule (peatükk \ref{chapter:discussion}, \enquote{Agentpõhine arendus...}); see käsitlus on metoodiliselt küps ja sõnastab \emph{tõenduspudelikaela nihke teostuselt tõendusmaterjalile} laiema valdkondliku tähelepanekuna.

### Töö kirjaliku vormistuse kvaliteet

- Eesti keel on professionaalsel tasemel; ingliskeelsed terminid on kursiivis ja eestindatud (nt \emph{streaming evaluation} $\rightarrow$ pidev helivoo režiim, \emph{wake word} $\rightarrow$ äratussõna), mis on bakalaureusetöös soovitatud praktika.
- Viitamiskultuur on tugev: kasutatakse arvukalt rahvusvahelisi peer-reviewed allikaid (\cite{he2016resnet,park2019specaugment,chen2014smallfootprint,alvarez2019svdf,sainath2015cnn,choi2021bcresnet,jacob2018quantization,wilson1927probable,brown2001interval,garwood1936fiducial,ulm1990poisson,hanley1983ruleofthree,cawley2010overfitting,park2024adversarial,dubois2020triggers,schoenherr2022accidental,chen2022misp,shrivastava2021optimize,gruenstein2017cascade,apple_voice_trigger_2023,michaely2017googlekws,sigtia2020multitask,garg2021streaming,kumar2020wakeword,wang2020lfmmi,rikhye2021personalized,lewis2013umuxlite,sauro2009seq}) ja tööstusallikaid (\cite{microwakeword2026,openwakeword2026,esphome2026,homeassistant2026,picovoice-benchmark2026,picovoice-guide2026,sensory2024realworld,apple-heysiri2017}).
- Annotatsioonid (eesti ja inglise) on olemas, sisuliselt kirjutatud ja vastavuses peatekstiga; ülesandepüstitus on \texttt{ylesandepystitus.tex} kujul olemas. Kohustuslikud vormielemendid on katmas.
- Vormistuslikud potentsiaalsed riskid: tabelite numbrite ja viidete sünkroon (vt \textbf{[w12]}), automaattäitmise väärtused (\texttt{\textbackslash calculatepages}, \texttt{\textbackslash totvalue}). Need on triviaalselt parandatavad, kuid neid ei tohi unustada.

---

## Hinnete soovitused

**NB!** Retsensendil on õigus muuta oma eelnevaid hindeid kaitsmisel. Lisandub hinne ka kaitsmise eest.

### Sisu ja analüüs
> *Töö sisu ja analüüs on metoodiliselt küps ja akadeemiliselt aus; kõige tähtsam empiiriline tõenduslüli (kasutajatest, \enquote{neljas ring}) on aga teadlikult lõpetamata. Kui kasutajatest enne kaitsmist sooritatakse ja selle koondhinnang lisatakse vähemalt arutelu jaotisesse, on töö hinnang \enquote{väga hea}; praeguses, kasutajatestita seisus ei saa retsensent juurutuskõlblikkuse osas lõplikku hinnangut anda ning soovitatav vahemik on \enquote{hea} kuni \enquote{väga hea}, sõltuvalt sellest, kui kindlalt suudab autor kaitsmisel selgitada, miks hindamisprotokolli panus on iseseisvalt piisav teaduslik panus juba ilma kasutajatestita.*

### Töö maht ja ülesande keerukus
> *Hinnang \enquote{väga hea}. Töö maht on tehnilises ulatuses üle bakalaureusetöö keskmise tava (mitukümmend mudeliversiooni, INT8 paigaldus seadmes, kavandatud kasutajatest, \texttt{kratt} CLI tööriistastik, Androidi logija). Bakalaureusetöö jaoks tüüpilist mahupuudust ei esine.*

### Töö kirjaliku vormistuse kvaliteet
> *Hinnang \enquote{väga hea}, eeldusel et lõplik kompileerimine kontrollib lehekülgede, jooniste ja tabelite arvu (\textbf{[w12]}) ning tabelite/jaotiste viited tulemuste peatükist on terviklikud. Kui need vormistuslikud lõpptäpsustused tehakse, jääb keelekasutus, viitamiskultuur ja struktuur soovituseta märkuste vajaduseta.*

---

## Märkus AI-tööriistade kasutamise kohta (kui on asjakohane)

Autor sõnastab arutelu peatükis (\enquote{Agentpõhine arendus kui töövõimendaja, mitte tõendusmaterjali asendaja}) eksplitsiitselt, et kasutas tehisagent-tarkvaraarendust koodi mustandi, ümberkirjutamise ja tehnilise dokumenteerimise faasides ning et see mõjutas töö ulatust (Androidi logija, hindamisskriptid, \texttt{kratt} CLI). Samas kirjutab ta, et tehisagendid \emph{ei vähenda} tõendusmaterjali hankimise kulu (päris kõnelejaid ei saa luua, sõltumatuid testikomplekte ei asendata) ning et autori järeldused tuginevad eraldi kogutud või avalikele andmetele. See käsitlus on metoodiliselt aus ja vastab TalTech-i ja IT teaduskonna ootustele AI-deklaratsiooni osas. Eraldi vormistatud TI/AI kasutuse deklaratsioon (mis on TalTech-i bakalaureusetöödes nõutav) peab olema vormistatud lõputöö lõplikus versioonis vastavalt teaduskonna juhendile; käesoleva mustandi lugemise ulatuses on see sisuliselt arutelu peatükis kaetud, kuid ametliku deklaratsiooni vormistamine eraldi lehel jääb autori kohuseks.

---

## Parandusettepanekud

### Sisu ja analüüs

- **[p1]** *(maht: high)*: viia läbi 20--30 osalejaga kasutajatest külmutatud lävedega \texttt{v16c} aktiivse mudeli ja varimudelite (\texttt{expert-a}, \texttt{expert-b2}, \texttt{v6-residual}, \texttt{v10}, \texttt{v15}, \texttt{expert-a+expert-b2} konsensus) peal vastavalt §\ref{sec:user-test-methodology} disainile; lisada vähemalt koondtabel (recall, FPR sarnastel negatiividel, FAPH taasmängul) Wilsoni/Poissoni vahemikega ning üks paragrahv kokkuvõttes. -> [w1]
- **[p2]** *(maht: medium)*: sõnastada \enquote{komposiitse kontrollpunkti valikukriteeriumi} (§\ref{sec:eval-evolution}) konkreetne operatsionaalne reegel --- nt \enquote{aktsepteeri mudel ainult siis, kui FAPH${<}1$ kõrvalejäetud Common~Voice ET kõnel \emph{ja} recall reaalsetel kõnelejatel ${\geq}0{,}9$ \emph{ja} prefiks-/üksiksõna FPR ${\leq}X$\%}. -> [w2]
- **[p3]** *(maht: low)*: lisada selgesõnaline viide v13a/v13b SpecAugment-ablatsiooni tulemustabelile peatüki \ref{chapter:method} §\ref{subsec:specaugment} lõpus, et lugeja näeks otse, kus eraldatud mõju on raporteeritud. -> [w3]
- **[p4]** *(maht: low)*: fikseerida vähemalt sama-seadme reaalsete \enquote{Kule}-hääldustega ütluse-tasandi skoorijaotus (histogramm või kvantiilid) lisana või tulemuste alajaotusena ja viidata sellele §\ref{sec:benchmark-gap} \enquote{Põhjus 1} all. -> [w4]
- **[p5]** *(maht: low)*: tuua ekspertide konsensuse 0,79 FAPH-i juurde Poissoni 95\%-vahemiku konkreetne ülemine piir nii sissejuhatuses kui ka \enquote{Mida saab juba praegu väita} loendis. -> [w5]
- **[p6]** *(maht: low)*: lisada sissejuhatusse v6 MacBook Pro mikrofoni FAPH${\approx}50$ arvulise näite juurde lühike sulgudes täpsustus (proovi pikkus, lävi, transkriptsiooniprotokoll), et lugeja saaks numbrit lugeda enne tulemuste peatüki juurde jõudmist. -> [w6]
- **[p7]** *(maht: medium)*: kas esitada vähemalt esialgsed mõõtmised mittekõneliste stiimulite (klaviatuuriklõpsud, taustamuusika, koduhelid) aktivatsioonimäära kohta, või sõnastada §\ref{sec:benchmark-gap} \enquote{Põhjus 4} kitsamalt --- mitte \enquote{ükski standardne benchmark seda ei mõõda}, vaid \enquote{käesolev töö ei mõõtnud süstemaatiliselt}. -> [w7]
- **[p8]** *(maht: low)*: koondtabelisse lisada iga mudeliversiooni TFLite-mudeli ja \texttt{tensor\_arena} suurus paralleelselt teiste tulemustega; see lubab lugejal näha kvantiseerimise mõju otse, ilma teksti kombineerimata. -> [w8]
- **[p9]** *(maht: low)*: kokkuvõttesse lisada selge lause, miks juurutusotsus on \emph{teadlikult} lükatud kasutajatesti järele (mitte vaikiv ebakindlus). -> [w9]
- **[p10]** *(maht: medium)*: kaskaadarhitektuuri ettepaneku §\ref{sec:future-cascade} juurde lisada üks lõik konkreetse ressursipiirangu kalkulatsiooniga --- kas teine aste mahuks ESP32-S3 mällu (FLASH/RAM) või eeldatakse Raspberry Pi 5 hostmist (Wyoming protokolli kaudu). -> [w10]

### Töö maht ja ülesande keerukus

- **[p11]** *(maht: low)*: lisada kogu töö avalehe kõrvale või sissejuhatuse esimese lõigu järele lühike eraldi paragrahv \enquote{Probleemi formuleering ja töö piiritlemine} (kuni 6 lauset), mis sõnastab eksplitsiitselt lahendamata probleemi ja töö skoobi väljapoole jäävad osad. See on eelkaitsmisel sageli oodatav formaat. -> [w11]

### Töö kirjaliku vormistuse kvaliteet

- **[p12]** *(maht: low)*: enne kaitsmist teha lõplik kompileerimine ja kontrollida visuaalselt, et \texttt{\textbackslash calculatepages}, \texttt{\textbackslash total\{figure\}}, \texttt{\textbackslash total\{table\}} jt automaatväärtused on annotatsioonides ja kõikjal mujal korrektsed; samuti viidete (\texttt{\textbackslash ref}) puuduvate sihtide loendi kontroll. -> [w12]
- **[p13]** *(maht: low)*: vormistada ametlik AI-tööriistade kasutamise deklaratsioon eraldi vormielemendina vastavalt TalTech-i juhendile, isegi kui sisuline käsitlus on arutelus olemas. -> *(ei seo otseselt nõrkusega; vormistuse täiendus)*

---

## Kaitsmise küsimused

1. **[q1]** *(metoodika --- mitmemõõtmelise hindamise empiiriline alus)*: Te väidate, et töö kõige kindlamini kaitstav teaduslik panus on \emph{väikese ressursiga keele kohaliku äratussõna mitmemõõtmelise valideerimise protokoll}, samas kui üksiku mudeli osas (sh ekspertide konsensuse 0,79 FAPH) jääte ettevaatlikuks. Kuidas Te vastate võimalikule kriitikale, et ilma 20--30 osalejaga kasutajatesti tulemusteta on \enquote{neljas ring} avatud ja Teie protokoll on \emph{ette pakutud}, mitte \emph{tõestatud}, et see üldistub uutele kõnelejatele? Mida konkreetselt Teie töö juba praegu tõendab \emph{protokolli edasikantavuse} kohta?
   *Mõõdab:* metoodilise põhjenduse oskust ja eristusvõimet \enquote{tõestatud} ja \enquote{ette pakutud} panuse vahel; teadlikkust välise valiidsuse piiridest.

2. **[q2]** *(statistika --- usaldusvahemikud null-sündmustega)*: Te kasutate Poissoni-Garwoodi vahemikku ja kolmereeglit ${\sim}3/T$ null-sündmustega taustaheli rajadel. Konsensuse FAPH=0,79 puhul, kui Common~Voice ET kõrvalejäetud kogumis täheldati teatud arv valeaktiveeringuid teatud aja jooksul, milline on Teie meelest 95\%-i ülemine piir ja miks see arv on/ei ole piisavalt kitsas, et teha juurutusotsust selle põhjal?
   *Mõõdab:* statistilise pädevuse oskust tõlgendada usaldusvahemiku laiust kui tõendusmaterjali ja eristada punkthinnangut intervallhinnangust.

3. **[q3]** *(domeen --- \enquote{Kuule} vs.\ \enquote{Kule} segiajamine)*: Te tunnistate, et tuvastamismäär reaalsetel \enquote{Kule}-hääldustel jääb juurutuslävel madalamaks kui TTS-positiivsetel klippidel. Eesti keeles on \enquote{Kuule} ja \enquote{Kule} foneetiliselt ja kasutuses lähedased; samas on Teie treeningandmestik (Neurokõne TTS) tõenäoliselt esindanud peamiselt formaalset \enquote{Kuule} vormi. Kuidas Te seda treeningandmestiku tasakaalu probleemi konkreetsemalt lahendaksite, kui Teil oleks veel kolm kuud aega? Mille võtaksite eelistataks: rohkem \enquote{Kule}-positiivseid, kaskaadarhitektuuri teine aste, või andmestiku-poolne tasakaalustamine?
   *Mõõdab:* domeeniteadlikkust eesti hääldusvormide kohta, oskust põhjendada andmestiku-disaini valikuid ja prioriteete piiratud aja juures.

4. **[q4]** *(infrastruktuur --- kaskaadarhitektuuri ressursipiirangud)*: Te pakute §\ref{sec:future-cascade} välja kaskaadarhitektuuri kui edasise suuna. ESP32-S3 \texttt{tensor\_arena} on Teie töös ${\sim}107$\,KB ja v16c TFLite ise 148\,KB. Kui teine aste oleks samuti MixedNet-suurusjärgus mudel, kas see mahuks samale seadmele või eeldaks see seadme-kõrvalist hostmist? Kui jah, siis mis oleks Teie esimene valik (Wyoming-protokolli kaudu Raspberry Pi 5 host vs.\ teine ESP32) ja miks?
   *Mõõdab:* riistvaratundlikkust, oskust konkreetselt mõõta ressursinõudeid ja sõnastada arhitektuurilisi valikuid.

5. **[q5]** *(metodoloogia --- \enquote{lühitee} mõiste kriitika)*: Te kirjutate, et \enquote{kolm-mõõdikuline raporteerimine \emph{tahtis} mõõta äratussõna eristamist, kuid \emph{mõõtis} \enquote{kuule}- või \enquote{kule}-eesliite tuvastamist}. Kuidas Te kindlaks teete, et Teie praegune mitme-mõõdikuline raporteerimine (sh fraasistruktuuri testid) ei õpeta omakorda uut, käesoleva töö jaoks veel nähtamatut \emph{lühiteed}? Millise meetodiga avastaksite \enquote{viies ring}, kui see eksisteeriks?
   *Mõõdab:* metoodilise eneserefleksioon, teadlikkust testimise piiridest, oskust formuleerida iteratiivse hindamise distsipliini.

6. **[q6]** *(panus --- bakalaureusetöö ulatusega kooskõla)*: Te paigutate töö panuse hindamisprotokolli tasandile ja loobute eksplitsiitselt väitest \enquote{parim eesti äratussõna mudel}. Kuidas Te vastate vastuargumendile, et bakalaureusetöö \emph{primaarne} ootus on töötav süsteem, mitte metaehitis selle hindamise ümber, ning et metoodika peatüki maht ei tohiks kasvada nõrga lõpptulemuse kompenseerimiseks?
   *Mõõdab:* oskust kaitsta töö raamistust ja paigutada see TalTech-i bakalaureusetöö ootuste konteksti; akadeemilist enesekindlust ilma ülbuseta.

7. **[q7]** *(reprodutseeritavus --- agentpõhise arenduse roll)*: Te tunnistate, et töö ulatus (Androidi logija, hindamisskriptid, mitukümmend mudeliversiooni) sai võimalikuks tehisagent-tarkvaraarenduse abil. Kuidas Te tagate, et keegi teine, kes tahab Teie protokolli reprodutseerida ilma agentpõhise tarkvaraarenduseta, suudab seda mõistliku jõupingutuse piires teha? Mis on selle protokolli minimaalne käsitsi-teostatav tuumik?
   *Mõõdab:* reprodutseeritavuse arusaama, oskust eristada \emph{olemuslikku} ja \emph{instrumentaalset} (tööriistadest sõltuvat) panust.

8. **[q8]** *(eetika ja andmekaitse --- kasutajatesti nõusolekumudel)*: Kasutajatesti audio opt-in lubab säilitada lühikesi märgendatud heliklippe. Kuidas Te tagate, et nendele klippidele ei laienda hilisem treening (s.t.\ test ei muutu treeninguks)? Kas teil on tehniline mehhanism (nt eraldi salvestuskausta, hash-põhine välistus treeningskriptides), mis seda kindlustab, või on see ainult protseduuriline lubadus?
   *Mõõdab:* andmehaldus- ja eetika-tundlikkust, oskust eristada tehnilist tagatist protseduurilisest lubadusest.

---

**Allkiri:** ___________________________ */allkirjastatud digitaalselt/*

**Kuupäev:** ___________________________ */digitaalallkirjastamise kuupäev/*
