---
source_prompt: Probleemide_tuvastamise_intervjuu.txt
prompt_type: generative (inapplicable — kohandatud)
generated: 2026-05-07
---

# Probleemide tuvastamise intervjuu --- prompti rakendatavus ja parim võimalik kohandus

## 1. Rakendatavuse hinnang ja lünk

Prompt eeldab klassikalist UX-uurimuse stsenaariumi: organisatsioon, millel on olemasolev (halva kasutatavusega) tarkvara, ja millel on mitu eristuvat kasutajarolli (juht, spetsialist, klienditeenindaja jne). Eesmärk on poolstruktureeritud intervjuude kaudu tuvastada pudelikaelad ja ettevalmistada uue tarkvara disainimist.

Käesolev lõputöö ei sobi sellesse raami otseselt:

- **Organisatsiooni puudumine.** Töö on üksiku autori bakalaureuseprojekt ESP32-S3 äratussõna mudeli arendamiseks. Ei ole tellijaorganisatsiooni, kasutusosakonda ega mitut funktsionaalset rolli, mille töövoogu annaks kontekstuaalse uurimuse meetoditega kaardistada.
- **Asendatava süsteemi puudumine.** Töö ei asenda olemasolevat halva kasutatavusega tarkvara. Eesti keele jaoks äratussõna lokaalse tuvastuse lahendust senini sisuliselt pole olemas (vt sissejuhatus: openWakeWord ega Picovoice Porcupine eesti keelt ei toeta). Seega ei saa intervjueerida \enquote{senise süsteemi kasutajaid} --- senist süsteemi pole.
- **Üks kasutajaroll, mitte mitu.** Kratt on lõpptarbija nutikoduseade. Töös ei eristata juhi, spetsialisti ja klienditeenindaja rolle; on ainult lõppkasutaja (nutikodu omanik), kes ütleb fraasi \enquote{Kuule Kratt} ja annab valgustuskäsu.
- **Töövoog vs.\ ühekordne hääljuhtimisžest.** Kontekstuaalne uurimus eeldab pikaajalisi tööringteid (workarounds), igahommikuseid rutiine, kriitilisi intsidente. Äratussõna kasutus on $\sim$1-sekundiline interaktsioon; tüüpilist mitmesammulist tööringteed seal pole.
- **Töö ajaline faas.** Lõputöö hard-deadline on 2026-05-18 (11 päeva pärast). Probleemide tuvastamise (\emph{discovery}) intervjuude koht oleks projekti alguses (2025), mitte praeguses lõpphindamise etapis. Praegu on prioriteet 20--30 osalejaga kasutajatest külmutatud süsteemiga ($v16c$), mitte avastav probleemide tuvastamise intervjuu uue tarkvara disainimiseks.

Seetõttu ei ole võimalik luua promptis nõutud kujul \enquote{rolli kaupa intervjuukava} ilma rolle juurde leiutamata. Selliste rollide leiutamine läheks vastuollu töö CLAUDE.md piiranguga \enquote{No invented facts}.

## 2. Parima võimaliku kohanduse pakkumine

Allpool on prompti loogika ümber sõnastatud lõputöö tegelikule kontekstile. Siht ei ole \enquote{olemasoleva tarkvara probleemide tuvastamine} (mida pole), vaid **eesti keele nutikodu hääljuhtimise praeguse kasutuskogemuse pudelikaelte tuvastamine** sihtgruppidelt, kes on eesti keelega kokku puutunud nutikodus juba olemasolevate (peamiselt ingliskeelsete) lahenduste kaudu. See annab Kratti disainile sisendi, säilitades prompti UX-uurimusliku metoodilise raami.

### 2.1 Metodoloogiline soovitus (valim)

Sihtgrupid ja arvud on valitud Nielsen Norman Groupi soovitusele tuginedes, et kvalitatiivse uurimuse käigus ilmneb tüüpilises domeenis 80\,\% kasutatavusprobleemidest juba 5--8 osalejaga ühe homogeenseima rühma kohta (Nielsen 2000, \emph{Why You Only Need to Test with 5 Users}). Andmete küllastumiseni jõudmiseks väiksema homogeensusega rühmas (nt mitmekülgne nutikoduomanike grupp) soovitatakse 10--12 intervjuud (Guest, Bunce \& Johnson 2006, \emph{How Many Interviews Are Enough?}).

Käesoleva töö kontekstis tähendab see järgmist jaotust (kavandatud, mitte tehtud --- vt §\ref{sec:user-test-methodology} viitega töös tehtavale 20--30 osalejaga kasutajatestile, mis täidab osalt sama eesmärki kvantitatiivselt):

| Roll | Soovitatav arv | Põhjendus |
|------|-----------------|-----------|
| **A. Eesti keelt rääkiv nutikoduomanik, kes kasutab praegu ingliskeelset hääljuhtimist** (Alexa, Google, HomePod, Home Assistant + Wyoming) | 8--10 | Põhirühm: kelle valupunktid annavad otsest sisendit Kratti väärtuspakkumisele |
| **B. Eestikeelne nutikodukasutaja, kes hääljuhtimist \emph{ei} kasuta} (kas ei taha või katsetas ja loobus) | 5--6 | Otsib põhjusi, miks praegune lahendus ei õnnestu konverteeruda --- privaatsus, valeaktiveeringud, keelebarjäär |
| **C. Eestikeelse pere lapse- või vanemaealise hääle kasutaja** (osaleja, kelle perekonnas on lapsi 5--12 a või eakaid 65+) | 3--4 | Kontrollib töö §\ref{sec:fourth-round} ausat piiri: kasutajatest võib avalikustada lapse-kõne ja aktsendi äärejuhud |

Kokku 16--20 intervjuud, mis paigutuvad praktiliselt mõõdetava ulatusse ja täiendavad kvantitatiivset 20--30 osalejaga kasutajatesti (vt töö §\ref{sec:user-test-methodology}).

### 2.2 Intervjuukava rollide kaupa

#### ROLL A: Eesti keelt rääkiv nutikoduomanik, kes kasutab praegu ingliskeelset hääljuhtimist

**Intervjuu fookus:** Kuidas inimesed töötavad ümber selle, et nende olemasolev nutikodu \enquote{ei räägi eesti keelt}? Millised on praktilised ringteed (workarounds), millal kasutaja loobub häälest ja võtab telefoni; kus tekib pere sisene konflikt (nt vanavanem ei oska \enquote{Hey Google}-it öelda)?

**Küsimustik:**

1. **Kirjelda mulle, kuidas sa täna hommikul tuli süütasid / muusika käivitasid / temperatuuri muutsid.**
   * *Tegevusjuhis intervjueerijale:* Palu osaleja oma telefon või tahvel ette võtta ja tegelikult demonstreerida vooavoogu --- mitte rääkida abstraktselt. Kui ta kasutab nuppu või rakendust, mitte häält, küsi miks just selles olukorras.

2. **Millal sa viimati ütlesid \enquote{Hey Google} või \enquote{Alexa} ja see ei töötanud nii nagu lootsid? Kirjelda seda olukorda võimalikult täpselt.**
   * *Tegevusjuhis:* Otsi kriitilist intsidenti (Critical Incident Technique, Flanagan 1954). Mitte hinnangut \enquote{kas see on hea}, vaid konkreetset juhtumit, mille ümber emotsioonid ja töötlusringid kerkivad.

3. **Kas sinu peres on inimesi, kes hääljuhtimist ei kasuta? Mis siis juhtub, kui nemad tahavad valgust panna?**
   * *Tegevusjuhis:* Tee tähelepanekuid pere sisestest töövõtetest --- nt \enquote{Mu ema ei saa Alexat tööle, nii et ta lülitab käsitsi}. See annab hüpoteesi eestikeelsuse mõjust.

4. **Mis sind häirib kõige rohkem praeguses hääljuhtimises?** *(avatud)*
   * *Tegevusjuhis:* Lase rääkida 60--90 sek ilma katkestamata. Märgi üles esimene mainitud teema --- see on tavaliselt kõige teravam valupunkt.

5. **Kui ma räägin sulle privaatsusest pilveteenuste kontekstis (Amazon, Google), mis on sinu suhtumine?**
   * *Tegevusjuhis:* Kontrollib töö (sissejuhatuse) väidet, et lokaalsus on osa väärtuspakkumisest. Kui osalejal on lokaalsuse vastu ükskõikne hoiak, on see tugev signaal.

6. **Näita mulle, kuidas sa praegu äratad oma häälassistendi --- ütle reaalselt äratussõna.**
   * *Tegevusjuhis:* Kuula intonatsiooni, kõvadust, kaugust mikrofonist. See on konteksuaalne uurimus selle kohta, mis tundub osalejale loomulikuna.

7. **Kui see assistent reageeriks fraasile \enquote{Kuule Kratt}, kas see oleks sinu jaoks loomulik või veider?**
   * *Tegevusjuhis:* Mõõdab kasutaja vastuvõtlikkust eestikeelse äratussõna idee suhtes. Otsi häälitsust ja kehakeelt, mitte ainult sõnu (osaleja võib viisakuse pärast nõustuda).

8. **Kui tihti sa eksid äratussõnaga --- ütled vale fraasi, ja seade ei reageeri?**
   * *Tegevusjuhis:* See seob kasutusprobleemi otseselt töö §\ref{sec:benchmark-gap} \enquote{kule vs.\ kuule} hääldusriskile. Kui kasutaja ütleb spontaanselt \enquote{Kule}, mitte \enquote{Kuule}, on see tugev tõend baseline-kriisi kohta.

#### ROLL B: Eestikeelne nutikodukasutaja, kes hääljuhtimist EI kasuta

**Intervjuu fookus:** Mis on lävepakk, miks osaleja häält ei kasuta? Privaatsus, töökindlus, keelebarjäär või lihtsalt rakenduse mugavus? Sageli kasutatakse häält rohkem siis, kui see töötab eesti keeles.

**Küsimustik:**

1. **Kas sa oled kunagi proovinud hääljuhtimist? Kirjelda seda kogemust.**
   * *Tegevusjuhis:* Otsi konkreetseid hetki, kus loobumine toimus.

2. **Mis takistab sind seda praegu kasutamast?** *(avatud)*
   * *Tegevusjuhis:* Lase enne küsimust paus. Esimene vastus on tavaliselt kõige loomulikum.

3. **Kui ma ütleksin, et lahendus toimib täielikult sinu enda võrgu sees ja eesti keeles --- kas see muudab sinu jaoks midagi?**
   * *Tegevusjuhis:* Kontrollib hüpoteesi, et lokaalsus + eesti keel on kombineeritult tõhusam kui kumbki üksi. Pane kirja, kumb mõjub tugevamalt.

4. **Mis on sinu jaoks olnud selline tehniline asi, mida sa oled tahtnud kasutada, aga loobunud, sest see ei räägi eesti keeles?**
   * *Tegevusjuhis:* Laiendab konteksti hääljuhtimisest üldisemalt. Annab indikatsiooni, kas eestikeelsus on käitumismuutuste käivitaja.

5. **Kui kohutavalt halb peab äratussõna olema, et sa loobuksid ka eestikeelsest variandist?**
   * *Tegevusjuhis:* Mõõdab tolerantsi valeaktiveeringutele ja missile. See on kvalitatiivne sisend töö FAPH < 1 sihiväärtusele: kui kasutajad räägivad \enquote{üks tunnis on talutav}, on töö siht õigesti kalibreeritud.

#### ROLL C: Eestikeelse pere lapse või vanemaealise hääle kasutaja

**Intervjuu fookus:** Töö §\ref{sec:fourth-round} ausa piiri täiendamine: kas praegune mudel arvestab lapse kõne, vanemaealiste kõnetempo ja võimalike murdejoontega? Tõenäoliselt mitte, kuid intervjuust saab konkreetsed riskid välja tuua.

**Küsimustik:**

1. **Kas pereliikmel, kelle nimi on \dots, on praegu juurdepääs hääljuhtimisele? Kui jah, kuidas see kasutus käib?**
   * *Tegevusjuhis:* Vajadusel paluda perekonnaliikmel proovida (kui see on nõusolekuga lubatud). Salvesta hääle erijooned (laps, vanaema, aktsendiline).

2. **Kas sina ise oled näinud, kuidas \dots püüab seadmega rääkida ja see ei mõista? Mida nemad siis teevad?**
   * *Tegevusjuhis:* Kriitilise intsidendi tehnika rakendamine: töövoo \enquote{ringtee} kaardistus.

3. **Kui assistent toetaks loomulikku eesti hääldust ja ka näiteks \enquote{Kule} kõrval \enquote{Kuule} hääldust, kas see oleks pere jaoks oluline?**
   * *Tegevusjuhis:* Mõõdab töö \enquote{kule vs.\ kuule} kalibreerimisotsuse mõju.

## 3. Kõrvalkommentaarid lõputööle

Selle prompti läbi käimisel ilmnesid kaks asjakohast tähelepanekut, mis võiks kasutajatesti planeerimisse jõuda (ainult informatiivselt, mitte tegevusettepanekuna):

1. **Roll A küsimus 8 ühildub töö §\ref{sec:benchmark-gap} \enquote{kule vs.\ kuule} narratiiviga.** Töö juba tunnistab, et reaalkõnelejatel on hääldusvariatsioon (Kule vs.\ Kuule); sessioonijärgse küsimustiku ühena võiks lisada \enquote{Kuidas sa fraasi tegelikult hääldasid?}, mis annab kvalitatiivse seose mudeli FRR-iga.

2. **Roll B küsimus 5 (\enquote{kohutavalt halb peab olema, et loobuksid}) annab kasutaja-poolse kalibreerimise FAPH \(<\) 1 sihtväärtusele.** Praegu on töö siht põhjendatud openWakeWord ja Picovoice'i numbritega; kasutajaintervjuu annaks sõltumatu, kasutajakogemusliku punkti.

## 4. Vastus prompti lähenemisele üldisemalt

Prompt on hea malli paljudele bakalaureuseprojektidele, kus uuritakse organisatsioonisisest tarkvara (nt panga klienditeenindaja CRM, kooli koolihaldussüsteem). Käesoleva töö (KWS-mudel) puhul on selle otsekohaldamine sundus, mille tulemus oleks olnud kunstlikult välja mõeldud rollide intervjuukava. Eelistatum on tunnistada lünk ja näidata, kuidas sama UX-uurimusliku raami põhimõtteid (käitumuspõhisus, kriitilised intsidendid, töövoo demonstreerimine) saab rakendada nutikodu lõppkasutaja kontekstis. Selle vastu annaks tegelikku väärtust ka töö enda jaoks: praegu §\ref{sec:user-test-methodology} kavandatud kasutajatest on valdavalt kvantitatiivne (FAPH ja FRR taasmängul), kvalitatiivne lisakomponent kahe-kolme intervjuuga (3--5 osaleja peal, mitte 16--20) annaks ausat lisainfot Kasutajakogemuse rahulolu mõõdiku (UMUX-Lite) numbrilise vastuse taha.
