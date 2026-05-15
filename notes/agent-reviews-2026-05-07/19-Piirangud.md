---
source_prompt: 03_Lõputöö_alamosad/Piirangud.txt
prompt_type: generative
generated: 2026-05-07
---

# Töö piirangud

## Sissejuhatav märkus autori käsitlusele

Lõputöö ei sisalda eraldi pealkirjastatud peatükki \enquote{Töö piirangud}. Piirangutele osutavad mainimised on hajutatud sissejuhatusse (lõpulause: \enquote{Töö piirangud on teadlikud: ei kaeta täielikku STT/TTS toru, kasutajauuring on piiratud mahus ning hindamine toimub ühe äratusfraasi ulatuses.}), kolmanda peatüki alajaotusse \emph{Andmestiku põhipiirangud}, agentpõhise arenduse alajaotuse hoiatusosasse, alajaotusse \emph{Aus piir: võimalik neljas ring} ning kokkuvõtte komposiit-kompromisside kirjeldusse. Autor on neid piiranguid teadvustanud ausalt, kuid esitanud need narratiivsete kõrvalmärkustena, mitte süstemaatilise validiteediarutluse kujul. Käesolev sünteespeatükk koondab autori enda mainitud punktid ja täiendab neid varjatud piirangutega, mis tulenevad Wohlin et al.\ raamistikust (sisemine, väline ja konstrukti valiidsus) ning DSR-i hindamisloogikast (artefakti valideerimine realistlikus keskkonnas).

Autori esitusele kriitiliselt vaadates: piirangud on tüüpiliselt sõnastatud \emph{leevenduspakkumisena} (\enquote{kasutajatest on järgmine samm}), mitte praeguste tulemuste kehtivust kahandava jõuna. See nõrgestab autori enda käsitluse rangust. Allpool sõnastatakse piirangud nii, nagu need mõjutavad praeguseid väiteid, mitte tulevasi.

## Metodoloogilised piirangud

### Hindamisprotokolli enesetõestuse risk
*   **Hindamismetoodika on töö peamine panus, kuid sama metoodika hindab ka töö enda mudeleid.** (Mõju: Tugev)
    *   *Selgitus:* Töö positsioneerib peamiseks teaduslikuks panuseks \enquote{väikese ressursiga keele kohaliku äratussõna mitmemõõtmelise valideerimise protokolli} (kolmanda peatüki §~\emph{Töö-tasemel panus ja selle ülekantavus}). Sama protokoll on aga see, mille alusel hinnatakse töö enda mudeleid (v6, v6-residual, v16c, expert-a, expert-b2, konsensus). See loob ringluse: mudelite tulemused legitimeerivad protokolli ja protokoll legitimeerib mudelite tulemusi. Selline kahekordne kasutus on tüüpiline DSR-i sisemise valiidsuse oht, kus loodud artefakti hinnatakse selle artefakti enda kriteeriumide alusel.
    *   *Mõju analüüs:* Tugev, kuna see seab kahtluse alla protokolli ülekantavuse väite. Sõltumatu valideerimine (nt sama protokolli rakendamine teisele väikese ressursiga keelele või teise sõltumatu uurija poolt eestikeelsele äratussõnale) puudub. Töö ise tunnistab \enquote{võimalikku neljandat ringi}, kuid ei käsitle ringluse riski.
    *   *Leevendamine ja tulevik:* Tulevased uurimused võiksid rakendada protokolli sõltumatult kogutud andmestikule või teisele keelele (nt soome, läti) ning hinnata, kas samad kolm valideerimiskihti (kõrvalejäetud komplekt, positiivse klassi audit, kontrollpunkti komposiit-objektiiv) avastavad seal samalaadseid lühitee-probleeme. Autor on protokolli ülekantavust väitnud, kuid pole seda empiiriliselt näidanud.

### Kasutajatesti puudumine praeguses tõendusbaasis
*   **Kõik mudeli kvaliteediväited tuginevad sünteetilistele või väikese kõnelejabaasiga andmetele; valideeriv kasutajatest on kavas, kuid pole läbi viidud.** (Mõju: Tugev)
    *   *Selgitus:* Töö kõige tugevam empiiriline tugipunkt --- $0{,}79$~FAPH konsensusmudelil Common~Voice ET kõrvalejäetud komplektil --- on raporteeritud koos selge hoiatusega, et see on \emph{punkthinnang ühel korpusel ja ühel operatsioonipunktil}. Päris kõnelejate tuvastamismäära kohta puudub töös usaldusväärne arv: autor tunnistab, et \enquote{Kule}-hääldustel jääb tuvastamismäär juurutuslävel madalamaks kui TTS-positiivsetel klippidel, kuid täpset arvu pole esitatud. 20--30 osalejaga kasutajatest on kavandatud (alajaotus 2.\emph{Kasutajatesti metoodika}), kuid pole sooritatud. See tähendab, et töö lõplik valiidne väide reaalse kasutuskogemuse kohta puudub.
    *   *Mõju analüüs:* Tugev, sest töö enda autor toob 3.\ peatükis välja, et standardsed võrdlusalused ei ennusta reaalset kasutust ($\S$~\emph{Standardsete võrdlusaluste ebapiisavus reaalse kasutuse ennustamisel}). Kuna kasutajatest on töö enda metoodika järgi vajalik just selle lõhe ületamiseks, siis kasutajatesti puudumine teeb kõik praegused mudelivalikud tinglikuks. Tegemist pole väikese kõrvalpiiranguga, vaid avatud peamise tõendusahela puudujäägiga.
    *   *Leevendamine ja tulevik:* Töö hõlmab valmis tööriistastiku (\texttt{kratt user-test}, \texttt{kratt validate-user-test}, \texttt{kratt replay-user-test}, \texttt{kratt summarize-user-test}) ja kavandab külmutatud läve ning varimudelite taasmängu. Selline ettevalmistus on metoodiliselt tugev, kuid ei asenda tegelikku andmehulka. Lugeja peaks töö hindamisel arvestama, et lõputöö esitatud tähtaja seisuga (2026-05-18) puudub osalejate-pealne tõendus.

### Mõõdikute valik tugineb projekti-spetsiifilistele sihtidele
*   **\enquote{Usaldusväärsuse} sihid (FAPH~$<$~1, tuvastamismäär~$\geq$~0{,}95) on autori enda valitud, mitte kirjanduses kehtestatud.} (Mõju: Keskmine)
    *   *Selgitus:* Töö sissejuhatus tunnistab seda otse: \enquote{Need on käesoleva töö projekti-spetsiifilised otsustuskriteeriumid, mitte kirjanduses kehtestatud universaalsed standardid.} openWakeWord'i $<\!0{,}5$~FA/h ja Picovoice'i 1~FA/10~h on toodud orientiiridena, kuid ei moodusta vastastikku eelretsenseeritud baasi. See tähendab, et töö \enquote{eesmärk saavutatud / pole saavutatud} otsus sõltub ühest valikust, mille kohta ei tehta tundlikkusanalüüsi (nt mis muutuks, kui sihiks oleks $0{,}5$~FAPH ja tuvastamismäär $\geq$~0{,}90).
    *   *Mõju analüüs:* Keskmine. Sihtide valik on dokumenteeritud ja põhjendatud, mistõttu ei kahjusta see töö läbipaistvust. Kuid otsuste tundlikkus erinevate sihiväärtuste suhtes pole näidatud, mistõttu praktilised juurutamissoovitused on autori sihivaliku konditsionaalsed.
    *   *Leevendamine ja tulevik:* Tundlikkusanalüüs (näiteks ROC-tasandil mitme sihtpunkti võrdlus) tugevdaks töö üldistatavust. Töös on kõrvalejäetud komplektidel ROC-laadne kõver mainitud, kuid täpne tundlikkusarvustus puudub.

### Statistilise võimsuse puudumine FAPH-i punkthinnangutes
*   **$0{,}79$~FAPH on raporteeritud Poissoni 95\%~vahemikuga, mis on lai, kuid praktilist mõju vahemiku laiusest pole edasi arutletud.** (Mõju: Keskmine)
    *   *Selgitus:* Autor lisab statistiliselt korrektse hoiatuse, et \enquote{täpne Poissoni 95\%~vahemik on lai}. Sellele järgnev tõlgendus puudub: kui ülemine piir on näiteks 1{,}5--2 FAPH, siis töö siht (FAPH~$<$~1) ei pruugi olla täidetud isegi, kui punkthinnang seda näitab. Töö ei esita konkreetseid vahemiku piire, mistõttu lugeja ei saa hinnata, kui kindlustatud on töö peamine kvantitatiivne väide.
    *   *Mõju analüüs:* Keskmine, sest hoiatus on olemas, kuid mõju peamisele väitele \enquote{alla ühe valeaktiveeringu tunnis} on alaarutatud. Tugevaks ei klassifitseeri, kuna autor ei väida, et tulemus on lõplik tõestus.
    *   *Leevendamine ja tulevik:* Konkreetsete usaldusvahemike piirude esitamine ja $T$ (vaatlustundide arv) suurendamine ($\sim$99~h on minimaalne, mitte standardne) tugevdaks väidet märkimisväärselt.

## Valim ja andmed

### Kõnelejate mitmekesisuse puudus positiivses klassis
*   **Treeningu positiivsed näited tuginevad valdavalt TTS-allikatele ja kitsale käsitsi kogutud kõnelejate ringile.** (Mõju: Tugev)
    *   *Selgitus:* 3.\ peatüki alajaotus \emph{Andmestiku põhipiirangud} tunnistab seda otse: \enquote{Varajane käsitsi kogutud andmestik põhineb kitsal kõnelejate ringil ning sünteetilise kõnega laiendamine ei asenda täielikult päris kasutajaid.} Tõsisem on aga lekkiv väiksem fakt, mis ilmneb projekti memuuridest (\emph{Kule vs Kuule training bias}, mis pole praegu thesise tekstis avalikult dokumenteeritud, kuid mida autor on tunnistanud): treeningandmestikus on \enquote{Kuule}-hääldus tugevalt üleesindatud (${\sim}86$\%), samas kui reaalsed kõnelejad ütlevad sageli \enquote{Kule}. See tekitab süstemaatilise tuvastamismäära langu päris kasutuses --- mehaanism, mida autor 3.\ peatükis kirjeldab, kuid ei kvantifitseeri.
    *   *Mõju analüüs:* Tugev, sest see piirang seletab töö enda peamist jääkriski (Kule-hääldused juurutuslävel) ja seab kahtluse alla iga juurutusotsuse, mis tugineb praegustele tuvastamismäärale. Kasutajatestita pole võimalik öelda, kas isegi 0{,}95 sihti on praeguste mudelite puhul saavutatav. Üheaegselt mõjutab see otseselt välist valiidsust.
    *   *Leevendamine ja tulevik:* Häälduse-tasakaalu kontroll (Kule/Kuule jaotus), laiem käsitsi kõnelejate kogumine ja tasakaalustatud andmevalim. Töö kirjeldab seda kui \enquote{järgmist sammu}, kuid see piirang on praeguste tulemuste tõlgenduses keskne.

### Sünteetilise kõne ülehinnang
*   **TTS-kloonitud positiivsete klippide tuvastamismäära skoorid (1{,}0000) on töö enda hinnangul ülehinnatud, kuid ei kvantifitseerita reaalse kõneleja vastet.** (Mõju: Keskmine)
    *   *Selgitus:* Töö viitab Park et al.~\cite{park2024adversarial} tööle, kes näitas, et TTS-treenitud mudelid kipuvad sünteetilist kõnet ülehindama. Autor tunnistab, et \enquote{kui testikomplekt koosneb samadest TTS-häältest, millega treeniti, on tuvastamismäära hinnang topelt üle paisutatud}. Sellele vaatamata kasutavad tabelid (nt \texttt{tab:full-comparison}) jätkuvalt TTS-põhiseid skoore. Kvantitatiivset \enquote{ülehinnangu suurusjärku} (nt mitu protsendipunkti TTS vs.\ reaalne kõneleja) töös ei esitata.
    *   *Mõju analüüs:* Keskmine. Autor on probleemi avalikult arutanud ja kasutab seda argumendina kasutajatesti vajalikkuse kasuks. Kuid praegused tabelid jäävad tõlgendusse \enquote{üle paisutatud} kõrvallisaga, mis nõrgestab nende otsest praktilist väärtust.
    *   *Leevendamine ja tulevik:* TTS- ja reaalse kõne tuvastamismäära kõrvuti raporteerimine sama läve juures. Praeguse töö raames oleks see saavutatav vaid väikese olemasoleva päris-kõneleja komplekti kaudu, kuid kasutajatest täidaks selle puudujäägi täielikult.

### Single-mikrofoni tingimused
*   **Töö valideerib mudeli ühe seadme- ja mikrofoniklassiga, kuigi sihtkasutus eeldab mitut.** (Mõju: Keskmine)
    *   *Selgitus:* Praktiliselt on kõik välitingimuste FAPH-mõõtmised tehtud Android-seadmel ja MacBook Pro sisemikrofoniga. Korvo-2 ESP32-S3 sihtseade on mainitud kui \enquote{piloodi aktiivne kandidaat}, kuid \enquote{lõplik compile/flash kontroll tehakse kasutajatesti aktiivse konfiguratsiooni peal}. See tähendab, et sihtseadme empiirilised andmed on praegu vähesed.
    *   *Mõju analüüs:* Keskmine, sest kõikide mudelite peamine sihtraud on ESP32-S3 Korvo-2, kuid valideerimine on toimunud peamiselt asenduskeskkonnas. Mikrofoni asümmeetria on töö enda metoodikas tunnistatud (\emph{Mic symmetry rule}, taustamemuuridest), kuid kandidaadi seade pole täismahus läbi mõõdetud.
    *   *Leevendamine ja tulevik:* Sama mudeli FAPH ja tuvastamismäär ESP32-S3 Korvo-2 peal sõltumatus 24--48~h taustaheli protokollis annaks võrreldava punkti.

### Taustaheli korpuse Eesti-spetsiifilisus
*   **FAPH-mõõtmine kasutab valdavalt rahvusvahelisi taustaheli korpusi (MUSAN, VOiCES) ja Common~Voice ET-d, mitte Eesti kodude akustilist tegelikkust.} (Mõju: Keskmine)
    *   *Selgitus:* 3.\ peatüki §~\emph{Domeeninihke mõju} ja §~\emph{Stsenaariumpõhine testimisvoog} käsitleb seda riski selgesõnaliselt: \enquote{Kui hindamine toimub ainult puhta kõne või vaikuse peal, ei kirjelda see koduse keskkonna tegelikku helipilti.} Kuid kavandatud 2-tunnine annoteeritud Eesti kodu salvestus pole töös tegelikult sooritatud.
    *   *Mõju analüüs:* Keskmine. Kavandatud lahendus on dokumenteeritud, kuid praegused tulemused tuginevad rahvusvahelistele korpustele, mille akustiline jaotus ei pruugi vastata Eesti kodudele (nt Eesti TV/raadio kõnemustrid).
    *   *Leevendamine ja tulevik:* Kasutajatesti käigus saadav 99--132~h logi (sõltuvalt osalejate arvust) lisab Eesti-spetsiifilist taustamaterjali. Töö enda strateegia on suunatud selle puudujäägi täitmisele.

## Tehnilised piirangud

### Üks äratusfraas, üks keel
*   **Töö katab ainult fraasi \enquote{Kuule Kratt} ühes keeles.** (Mõju: Nõrk)
    *   *Selgitus:* Sissejuhatus tunnistab seda otse: \enquote{hindamine toimub ühe äratusfraasi ulatuses}. See on metoodiliselt täiesti aktsepteeritav bakalaureusetöö ulatuse jaoks, kuid piirab \enquote{protokolli ülekantavuse} väidet, mille kohta puuduvad teiste fraaside või keelte kontrollkatsed.
    *   *Mõju analüüs:* Nõrk piirang, kuna see on bakalaureusetöö loomulik fookuspiir, mitte tõendite usaldusväärsuse kahandaja. Mõjutab vaid panuse üldistatavuse väidet.
    *   *Leevendamine ja tulevik:* Teiste eestikeelsete fraaside (nt \enquote{Tere Kratt}) ja teiste väikeste keelte rakendamine on loomulik järgmine samm.

### STT/TTS toru väljajätt
*   **Tervikvoo otsast-lõpuni hindamine puudub.} (Mõju: Nõrk)
    *   *Selgitus:* Sissejuhatus tunnistab: \enquote{ei kaeta täielikku STT/TTS toru, kasutajauuring on piiratud mahus}. See on teadlik valik, sest STT (Kiirkirjutaja) ja TTS (Neurokõne) on olemasolevad tehnoloogiad. Siiski ei dokumenteerita, kuidas äratussõna vea-mustrid (eriti FAPH > 0) interakteeruvad STT-ga (nt valeaktiveerimine + STT-pikne kõnetöötlus + ekslik tegevus).
    *   *Mõju analüüs:* Nõrk, sest töö ulatus on selgelt määratletud äratussõna kihiks. Kuid praktilise nutikodu kogemuse seisukohalt on äratussõna FAPH üks ahela osa, mille reaalset kasutusmõju saab hinnata vaid otsast-lõpuni.
    *   *Leevendamine ja tulevik:* Kasutajatesti \enquote{kuus skriptitud pirnikäsku} ja \enquote{vabas vormis valgusülesanne} (alajaotus 2.\emph{Kasutajatesti metoodika}) annavad osalise otsast-lõpuni vaate; lõpliku väite jaoks vajalik longitudinaalne kasutus puudub.

### Kvantiseerimise mõju eraldi ei mõõdeta
*   **INT8 kvantiseerimise mõju täpsusele on raporteerimata.} (Mõju: Keskmine)
    *   *Selgitus:* Alajaotus 2.\ref{subsec:quantization} kirjeldab kvantiseerimisprotsessi, kuid ei esita FP32 vs.\ INT8 erinevust ühelgi mudeli versioonil. See tähendab, et kõik raporteeritud FAPH-i ja tuvastamismäära arvud on INT8 omad, kuid lugeja ei tea, kas kvantiseerimine ise viis kvaliteedi alla või mitte.
    *   *Mõju analüüs:* Keskmine. Microcontroller'i juurutamiseks on INT8 paratamatu, kuid teadusliku läbipaistvuse seisukohalt on kvantiseerimise hinnaerinevus oluline puuduv ablatsioon.
    *   *Leevendamine ja tulevik:* Lihtne ablatsioon: sama mudel FP32 ja INT8 sama kõrvalejäetud komplekti peal.

### \texttt{tensor\_arena} ja Korvo-2 lõpliku järeldamise valideerimispuudus
*   **\texttt{v16c} mudeli lõplik compile/flash ja kestva järeldamise stabiilsuse kontroll Korvo-2 peal on kavandatud, mitte sooritatud.} (Mõju: Keskmine)
    *   *Selgitus:* Kokkuvõte tunnistab: \enquote{Versioon \texttt{v16c} jääb eraldi kandidaatiks, mitte tootmisse rakendatavaks tõendiks, kuni ESPHome + \texttt{voice\_assistant} integreeritud Korvo-2 seadmes tehtud eraldi valideerimine seda kinnitab.} See on selgesõnaline, kuid kõik praegused juurutamise-väited (mälusobivus, järeldamise praktilisus) tuginevad arvutuslikule hinnangule, mitte tegelikule mõõtmisele.
    *   *Mõju analüüs:* Keskmine. Töö ei väida \texttt{v16c}-d lõplikuks, kuid sihtraua tegeliku järeldamise kontrolli puudumine vähendab DSR-mõttes artefakti valideerimise täielikkust.
    *   *Leevendamine ja tulevik:* Kasutajatesti aktiivse konfiguratsiooni Korvo-2 peal järeldamise stabiilsuse logi (latentsus, mälukasutus, ülevaade ametlikust ESPHome \texttt{tensor\_arena} kasutusest) on otsene leevendamise samm.

## Konstrukti valiidsus

### \enquote{Usaldusväärsuse} mõiste konstrukt
*   **\enquote{Usaldusväärne} on töös defineeritud kui FAPH < 1 ja tuvastamismäär $\geq$ 0,95, mis on operatiivne, kuid mitte ainus võimalik tõlgendus.} (Mõju: Keskmine)
    *   *Selgitus:* Sissejuhatus annab konstrukti määratluse, kuid see jätab kõrvale teised \enquote{usaldusväärsuse} aspektid: latentsus, järjepidevus üle aja (mudeli käitumise stabiilsus mitme nädala lõikes), kasutaja subjektiivne kindlustunne, mitte-tehniliste kasutajate hinnang süsteemile. Kasutajatesti küsimustik (UMUX-Lite, sessioonijärgne hinnang) puudutab seda kaudselt, kuid praegused mõõdikud ei kvantifitseeri pikaajalist stabiilsust.
    *   *Mõju analüüs:* Keskmine. Definitsioon on dokumenteeritud, kuid mitmemõõtmelisem konstrukti raamistik (nt SUS-skoor pluss tehnilised mõõdikud) annaks rikkalikuma pildi.
    *   *Leevendamine ja tulevik:* Pikaajalise stabiilsuse mõõtmine 2--4 nädala kasutusperioodil on otsene täiendus.

### Kasutajatesti subjektiivse rahulolu mõõdiku piirangud
*   **Sessioonijärgne küsimustik kombineerib UMUX-Lite valideeritud osa uurija koostatud diagnostiliste küsimustega.} (Mõju: Nõrk)
    *   *Selgitus:* Alajaotus 2.\emph{Kasutajatesti metoodika} tunnistab selle: \enquote{ülejäänud uurija koostatud küsimusi käsitletakse diagnostiliste, mitte valideeritud koondskaala tulemustena}. See on metoodiliselt korrektne, kuid tähendab, et kasutaja kogemuse koondhindamine tugineb lühikesele lühiskaalale. Avatud küsimuse \enquote{häiriva või üllatava kogemuse kohta} analüüs tugineb tõlgendusele, mille reliability'd ei valideerita teise kodeerija poolt.
    *   *Mõju analüüs:* Nõrk, kuna autor tunnistab piirangut ja eraldi käsitleb diagnostilisi küsimusi sellistena. Mõjutab kasutajakogemuse koondhindamise täpsust, mitte tehniliste mõõdikute valiidsust.
    *   *Leevendamine ja tulevik:* Avatud vastuste kahekordne kodeerimine ja UMUX-Lite asemel täielik UMUX/SUS lisaks aega vajaval pikemal sessioonil.

## DSR-spetsiifilised piirangud

### Artefakti valideerimine kavandatud, mitte sooritatud realistlikus keskkonnas
*   **Lõplik DSR-mõttes \enquote{naturalistlik hindamine} (Venable et al.\ FEDS raamistikus) on töö esitamise hetkel pooleli.} (Mõju: Tugev)
    *   *Selgitus:* FEDS-i mõttes liigub artefakti hindamine \emph{ex-ante / artificial} faasist \emph{ex-post / naturalistic} faasi siis, kui artefakt on testitud reaalsete kasutajate poolt reaalses keskkonnas reaalse ülesandega. Käesolev töö asub ex-ante / artificial otsas: hindamine on toimunud avalike korpuste peal, autori enda Android-välitestide peal ja TTS-positiivsete klippide peal. 20--30 osalejat on kavas, kuid lõputöö esitamise piiril (2026-05-18) sõltuvalt sellest, mil määral kasutajatest jõutakse läbi viia ja tulemustesse integreerida, võib artefakti DSR-staatuse väide jääda kavandatud, mitte realiseeritud.
    *   *Mõju analüüs:* Tugev, kuna DSR-mõttes ei ole artefakt täielikult valideeritud, kuni naturalistliku hindamise faas on läbitud. See pole pelgalt kasutajatesti puudus, vaid mõjutab kogu töö DSR-positsioneerimist.
    *   *Leevendamine ja tulevik:* Kasutajatesti läbiviimine ja tulemuste integreerimine enne kaitsmist on selgelt vajalik samm. Kui aega ei jätku, peaks kaitsmise versioonis selgesõnaliselt liigitama artefakti \enquote{piloot-staadiumis, naturalistliku valideerimiseta}.

### Probleemi- ja keskkonnamõju vahel pole võrdlevat hindamist
*   **Töö ei võrdle olukorda \enquote{Krati lahendusega} ja \enquote{ilma lahenduseta} ühegi mõõdetava kasutaja-kogemuse näitaja peal.} (Mõju: Keskmine)
    *   *Selgitus:* DSR-i tugevamad rakendused võrdlevad artefakti efekti võrdluskeskkonnaga (nt \enquote{kasutajad pilvepõhise süsteemiga vs.\ Krati lokaalse süsteemiga}). Käesolev töö ei sisalda sellist võrdlust ühegi konkureeriva lahendusega (nt Google Home eestikeelne osalahendus, Alexa). Põhjus on praktiline: eestikeelseid alternatiivseid äratussõna lahendusi praktiliselt pole. Kuid see on samal ajal töö motivatsioon ja DSR-raamistikus piirang.
    *   *Mõju analüüs:* Keskmine. Konkurentide puudumine on osaliselt töö motivatsioon, mistõttu võrdluse puudumine on osaliselt vältimatu. Kuid see piirab \enquote{kasutajakogemus paranes} tüüpi väidet.
    *   *Leevendamine ja tulevik:* Privaatsuse / lokaalsuse perspektiivist saaks võrrelda Krati t pilvepõhise lahendusega (latentsus, andmevoog, GDPR-konformsus), mis annaks DSR-mõttes tugevama efekti-väite.

## Välise valiidsuse piirangud

### Üldistatavus teistele kõnelejagruppidele
*   **Lapsed, eakad, aktsendiga rääkijad ja kõneerivusega rääkijad ei kuulu kavandatud kasutajatesti valimisse.} (Mõju: Keskmine)
    *   *Selgitus:* Töö ise tunnistab seda alajaotuses §~\emph{Aus piir: võimalik neljas ring}: \enquote{Kasutajatest võib avalikustada režiime, mida praegune hindamine ei suuda eraldada: näiteks häälduse vahevormid, aktsendid, lapse kõne või äärejuhud nagu vaikne äratus pärast pikka vaikust.} Kavandatud 20--30 osalejat on tüüpiliselt täiskasvanud eestikeelsed kõnelejad ilma süstemaatilise demograafilise tasakaalustamiseta.
    *   *Mõju analüüs:* Keskmine, kuna nutikodu kasutajakond ei ole demograafiliselt homogeenne. Lapse-kõne ja aktsendiga kõneleja on eriti olulised juhud, mida ei kaeta.
    *   *Leevendamine ja tulevik:* Demograafilise tasakaalustatud valimi kavandamine järgmises uuringus, eriti laps-kõne (mis on tehniliselt teine probleem) ja vene aktsendiga eesti kõne, mis on Eesti kontekstis praktiliselt oluline alajaotus.

### Kasutuskoha üldistatavus
*   **Töö ei mõõda lahenduse käitumist erinevates akustilistes ruumides ega erinevatel mikrofoni-kaugustel süstemaatiliselt.} (Mõju: Keskmine)
    *   *Selgitus:* Kasutajatest on kavandatud üheainsa pirnistsenaariumiga 10-minutilise sessioonina ühes ruumis. Seetõttu ei kata see kaja, suure ruumi, müraga köögi ega kauguse-mõju eraldi.
    *   *Mõju analüüs:* Keskmine, sest kodu-akustika varieeruvus on praktiliselt suur, kuid kavandatud 2-tunnine annoteeritud salvestus võib seda osaliselt katta.
    *   *Leevendamine ja tulevik:* Mitmes ruumis ja mitme kauguse juures sooritatav protokoll lisaks järgmisesse iteratsiooni.

## Sisemise valiidsuse piirangud

### Mudelite-vahelised võrdlused tehtud erinevatel ajahetkedel
*   **15+ mudeli versiooni on välja töötatud iteratiivselt, mis tähendab, et metoodika ise muutus arenduse käigus.} (Mõju: Keskmine)
    *   *Selgitus:* Töö enda peatükis \emph{Mitmemõõtmeline hindamisprotokoll} kirjeldatakse kolme valideerimiskihti (klipi-tase, kolm-mõõdik, komposiit-objektiiv). Iga kiht avastas vea, mis muutis järgnevate mudelite hindamist. See tähendab, et v1--v6 ei ole hinnanud sama mõõdikuhulga peal kui v15--v16c. Päästev faktor on \enquote{ühtne 2026-04-21 hindamine}, mis taasrakendas hilisemaid mõõdikuid varasematele mudelitele, kuid see ei taga, et iga versiooni iga arenduskäikukõik muudatust on hindamisel võrdselt kohaldatud.
    *   *Mõju analüüs:* Keskmine. Töö on retrospektiivse audi kaudu seda parandanud, kuid puhas \enquote{kõik mudelid sama protokolli all} versioonipuu pole avalikult dokumenteeritud.
    *   *Leevendamine ja tulevik:* Üks lõplik koondtabel, mis näitab kõikide jälgitavate versioonide kõiki praeguseid mõõdikuid sama läve juures.

### Autori-osaluse risk hindamises
*   **Päris-kõneleja FAPH-i ja tuvastamismäära mõõtmised on toimunud autori enda häälel.} (Mõju: Keskmine)
    *   *Selgitus:* Mainitud, et \enquote{positiivsete andmete laiendamiseks lisati autori lühiklippe}. Reaalajas testimise sessioonid (mis on alus väidetele \enquote{päris kõneleja häälel käivitus see sagedamini õigel ajal}) on tõenäoliselt autori enda kõnel, mis on \emph{single-speaker} kallak. See on bakalaureusetöö-skaalas tüüpiline, kuid metoodiliselt loob konfundeerumis-riski: autor on samaaegselt arendaja, hindaja ja tõenäoliselt ka peamine kõneleja.
    *   *Mõju analüüs:* Keskmine, sest mõju on otsene reaalajas tulemuste tõlgendusele. Hilisem 20--30-osalejaline kasutajatest peaks selle riski leevendama.
    *   *Leevendamine ja tulevik:* Autori-enda hääle eemaldamine kasutajatesti valimist; autori hääle eraldi raporteerimine kui kontroll-punkt, mitte üldine tõend.

## Vormistuslikud piirangud

### Mõnede leidude kvantitatiivne raporteerimine on osaline
*   **Mõned väited on raporteeritud suunaerinevusena, mitte täpsete arvudena.} (Mõju: Nõrk)
    *   *Selgitus:* Näiteks 3.\ peatükis on tõdetud: \enquote{Täpsemad arvud on esitatud tulemuste peatükis; arutelu seisukohalt on oluline just suunaerinevus, mitte konkreetne mudelitähis.} Sama lähenemine on kohati \emph{prefiksi-tüüpi} ja mittekõne-tüüpi näidete puhul (\enquote{üksikud juhtumid}, \enquote{süstemaatilist aktivatsioonimäära mittekõnelistel stiimulitel käesolevas töös eraldi ei mõõdetud}).
    *   *Mõju analüüs:* Nõrk, kuna autor tunnistab piirangut ja peamised väited on kvantitatiivselt põhjendatud. Mõjutab teisejärgulisi väiteid.
    *   *Leevendamine ja tulevik:* Lisatabelid ja konkreetsete arvude lisamine.

## Kokkuvõttev hinnang piirangutele

Töö piirangud jagunevad kolme suurde rühma. \emph{Tugevad mõjud} (kasutajatesti puudumine, hindamisprotokolli ringluse risk, kõnelejate mitmekesisuse puudus, naturalistliku DSR-valideerimise lõpetamatus) seavad ühisselt kahtluse alla töö lõplikud juurutamissoovitused, kuid mitte töö metodoloogilist panust. \emph{Keskmised mõjud} (TTS-ülehinnang, statistilise võimsuse käsitlus, single-mikrofon, kvantiseerimise eraldi mõõtmise puudus, autori-osaluse risk) mõjutavad konkreetseid kvantitatiivseid väiteid, kuid jätavad töö narratiivi kehtima. \emph{Nõrkadeks mõjudeks} liigituvad ulatuse-piirangud, mis on bakalaureusetööle loomulikud (üks fraas, üks keel, ühe-sessiooni kasutajatest).

Tähelepanuväärne on, et autor on enamikku tugevaid piiranguid teadvustanud --- sageli isegi enne, kui käesolev sünteespeatükk neid esile tooks. Nõrgim koht on aga see, et need piirangud on hajutatud üle töö ja sageli sõnastatud \emph{järgmise sammuna}, mitte \emph{praeguse väite kvalifitseeringuna}. Lugeja, kes loeb ainult sissejuhatuse ja kokkuvõtte, võib jääda mulje, et töö lõplikud arvud (FAPH~$=$~0{,}79; tuvastamismäära siht 0{,}95) on tõestatud, kuigi need on sõltuvuses veel sooritamata kasutajatestist. Tugev piirangute peatükk peaks selle ettevaatlikkust eelpoole tooma.
