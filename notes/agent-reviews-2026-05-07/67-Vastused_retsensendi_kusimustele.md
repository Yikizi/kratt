---
source_prompt: /Users/mattias/Downloads/loputoo_viibad_2026_04_28-2/06_Kaitsmine/Vastused_retsensendi_küsimustele.txt
prompt_type: generative (kaitsmise ettevalmistus — slaidid + suuline vastus retsensendi küsimustele)
generated: 2026-05-07
---

# Vastused retsensendi küsimustele — kaitsmise ettevalmistuse mustand

## Märkus rakendatavuse kohta

Etteantud sisendfail (`Vastused_retsensendi_küsimustele.txt`) sisaldab **ainult juhise enda — rolli ja väljundvormingu kirjelduse**, kuid mitte tegelikku retsensiooni ega retsensendi konkreetseid küsimusi. Klassikaline juhise-rakendamine eeldab, et retsensiooni fail on samuti olemas — see siin puudub.

Et siiski anda kaitsmiseks kasulik töömustand, koostan **eeldatavate küsimuste komplekti**, mis on tuletatud lõputöö enda nõrkadest kohtadest, piirangutest ja "ausatest tunnistustest", mis on kirjas peatükkides 1, 3 ja kokkuvõttes (§\ref{sec:fourth-round}, §\ref{sec:benchmark-gap}, sissejuhatuse piirangulõik, kokkuvõtte v16c-kandidaadi reservatsioon). Kui retsensent esitab teistsugused küsimused, tuleb skripte siin allpool kohendada — formaat on universaalne. **Asendage iga küsimuse plokis tärnidega märgitud osad reaalse retsensendi sõnastusega niipea, kui retsensioon on käes.**

Iga küsimus järgib juhise nõudmisi: Slaid A (küsimus muutmata), Slaid B (märksõnad, viited töö osadele), suuline vastus ~200–250 sõna 2-minutise tempo jaoks, ainult lõputöös tõestatavad väited.

---

### Küsimus 1

**Slaid 1: Retsensendi küsimus**
> *Millel põhineb teie väide, et tegemist on \enquote{esimese eestikeelse äratussõna mudeliga} — kuidas olete veendunud, et samaväärset varasemat tööd ei ole olemas, ning miks on see panus oluline, kui mudel on tehnilises mahus tagasihoidlik?*

**Slaid 2: Vastuse teesid**
- **Pealkiri:** Panuse sõnastus ja selle aus piiritlemine
- Sissejuhatus, lõik 1: openWakeWord ega Picovoice ei toeta eesti keelt
- Tööstustegijate (Apple, Sensory, Picovoice) ressursimahu erinevus — vt §\ref{sec:contribution-transferability}
- Töö **peamine** panus pole "esimene mudel", vaid **valideerimisprotokoll** — vt §\ref{sec:contribution-transferability}
- Konsensus FAPH = 0,79 Common Voice ET kõrvalejäetud komplektil — vt tabel \ref{tab:expert-consensus}

**Suuline vastus (Script):**
"Tänan selle täpsustava küsimuse eest, sest see puudutab töö positsioneerimise tuuma. Sissejuhatuses on viidatud kahele konkreetsele faktile: openWakeWord avalik mudelijaotus ei sisalda eesti keelt ning Picovoice Porcupine toetatud keelte nimekirjas eesti keelt ei ole. Need on kontrollitavad allikad ja just nendest tuleneb tühimik, mida töö täidab.

Samas, mis on sama oluline — alapeatükis 3.6.3 ütlen otsesõnu, et töö konkurentsivõimeline väide ei ole \enquote{parim eesti äratussõna}. Suurematel rühmadel on rohkem ressursse ning üksiku mudeli tehniline maht jääb tööstuslikele süsteemidele alla. Töö peamine panus on hoopis **väikese ressursiga keele lokaalse äratussõna mitmemõõtmeline valideerimisprotokoll** — kolm dokumenteeritud auditit: andmelekke audit, positiivse klassi sisuline audit ja kontrollpunkti-objektiivi audit.

Tehniline tulemus on selle protokolli rakendamise saadus, mitte vastupidi: ekspertide konsensus saavutab Common Voice ET kõrvalejäetud komplektil FAPH 0,79, mis on alla seatud sihtmäära 1, ja seda numbrit raporteerin koos Poissoni usaldusvahemikuga, mitte punkthinnanguna. Seega väide \enquote{esimene} on faktipõhine, kuid panuse tuum on metoodiline ülekantavus teistele väikestele keeltele."

---

### Küsimus 2

**Slaid 1: Retsensendi küsimus**
> *Töö üks peamisi numbrilisi väiteid on FAPH 0{,}79. Kas ühe punkti — ühe korpuse, ühe operatsioonipunkti — pealt saab teha juurutusotsuse?*

**Slaid 2: Vastuse teesid**
- **Pealkiri:** Punkthinnangu staatus ja selle teadlik piiritlemine
- §\ref{sec:benchmark-gap}: standardse benchmarki ja reaalse kasutuse lahknevus
- Poissoni-Garwoodi usaldusvahemik FAPH-ile (§\ref{sec:user-test-methodology} eelnev)
- Neli erinevat FAPH-varianti — vt tabel/§\ref{subsec:faph-variants}
- Kasutajatest 20–30 osalejaga kui neljas valideerimiskiht — §\ref{sec:fourth-round}

**Suuline vastus (Script):**
"See on töö kõige kriitilisem küsimus ja vastus on ühene: **ei**, üksinda ei saa.

Esiteks raporteerin alapeatükis \enquote{Mida saab juba praegu väita} otseselt, et 0,79 on **punkthinnang ühel korpusel ja ühel operatsioonipunktil**, ning et selle Poissoni 95\% usaldusvahemik on lai. See on teadlik formuleering, mitte juurutusväide.

Teiseks eristan alapeatükis 2.6.1 nelja **FAPH-varianti**, millel on erinev loendusreegel: raamistiku, skriptitud taasmängu, välitingimuste ja kasutajatesti taasmängu FAPH. Need ei ole vastastikku otseselt võrreldavad — see on äratussõna kirjanduses üks levinumaid reprodutseeritavuse auke ja ma märgistan iga tabeli juures, milline variant on kasutuses.

Kolmandaks pühendan §3.4 ja §3.6.4 aus tunnistus, et **standardne benchmark ei ennusta reaalset kasutust**: dokumenteerin ${\sim}99$-tunnise välikatse, kus madalaim klipipõhine valenegatiivsus ei langenud kokku madalaima välivälja FAPH-iga.

Sellepärast on lõplik juurutusotsus seotud kasutajatestiga 20–30 osalejaga — see on töös kirjas neljanda valideerimiskihina ja kokkuvõttes on otseselt öeldud, et v16c jääb kandidaadiks, mitte tootmistõendiks, kuni see kontroll on tehtud."

---

### Küsimus 3

**Slaid 1: Retsensendi küsimus**
> *Kasutate sünteetilist kõnet (XTTS) positiivsete näidete jaoks. Kuidas tagate, et mudel ei õpi TTS-süsteemi artefakte ja ei anna seetõttu \enquote{topelt ülepaisutatud} hinnangut?*

**Slaid 2: Vastuse teesid**
- **Pealkiri:** TTS-bias ja selle teadlik kontroll
- §\ref{sec:benchmark-gap}, põhjus 1: skoore 1,0000 sünteetilistel klippidel — vale kindlustunne
- Park et al. 2024 viide: TTS-treenitud mudelid ülehindavad sünteesitud kõnel
- Eraldi raporteerimisreegel: TTS-positiivne ja päriskõneleja-positiivne lahus
- §\ref{sec:user-test-methodology}: kasutajatest reaalsete kõnelejatega kui korrektsioon

**Suuline vastus (Script):**
"Tänan, see on metodoloogiliselt keskne küsimus. Töös ma **ei** väida, et TTS-positiivsetel klippidel saadud tuvastamismäär kirjeldab reaalsete kõnelejate käitumist — vastupidi, alapeatükis 3.4.1 on see eraldi alapeatükina põhjusena nr 1 lahti kirjutatud.

Konkreetselt: XTTS-kloonitud hääle isoleeritud klipid andsid skoore täpselt 1,0000. Tsiteerin Park et al. 2024 tähelepanekut, et TTS-treenitud mudelid ülehindavad sünteesitud kõnel, ja lisan olulise täpsustuse — probleem ei piirdu treeninguga, vaid laieneb hindamisele. Kui testikomplekt koosneb samadest TTS-häältest, mida kasutati treenimisel, on hinnang **topelt ülepaisutatud**.

Töös on kasutusel kolm konkreetset vastumeedet. Esiteks, raporteerimispoliitika: **TTS-allikate tuvastamismäär ja päriskõnelejate tuvastamismäär raporteeritakse alati eraldi**. Need on kaks erinevat kriteeriumit alapeatüki 3.6 mitmemõõtmelise hindamisprotokolli sees. Teiseks, kasutajatest 20–30 osalejaga, mille metoodika on §2.7 — see toob sisse pärisinimeste hääldused, sealhulgas \enquote{Kule}-variandi, mille tuvastamismäär jääb juurutuslävel teadlikult madalamaks kui TTS-positiivsetel klippidel. Kolmandaks ei lisata kasutajatesti heli enne lõplikku hindamist treeningandmetesse.

Seega TTS-bias on töös eksplitsiitselt deklareeritud risk, mitte peidetud eeldus."

---

### Küsimus 4

**Slaid 1: Retsensendi küsimus**
> *Miks on \texttt{Picovoice Porcupine} võrdlusest täielikult välja jäetud, kui see on tööstuses kõige laiemalt kasutatud äratussõna lahendus?*

**Slaid 2: Vastuse teesid**
- **Pealkiri:** Võrdluse nelja telje terviklikkus
- §2.2: võrdluse neli telge — keerukus, kvaliteet, integreeritavus, **laiendatavus eesti keelele**
- Porcupine: suletud lähtekood, litsents, eesti keele tugi puudub
- Picovoice avaliku **võrdlusalusena** kasutatakse — sissejuhatus, §2.2
- Võrdlus piirdub kahe avatud lähtekoodiga raamistikuga, mille kasutaja saab eesti keelele rakendada

**Suuline vastus (Script):**
"Tänan selle küsimuse eest — see on hea koht selgitada, mis on võrdluses ja mis ei ole. Alapeatüki 2.2 alguses on neli võrdlustelge: treenimise praktiline keerukus, mudeli kvaliteet, integreeritavus ESP32-S3-le ja **laiendatavus eesti keelele**.

Just neljas telg on Porcupine'i välistamise põhjus. Porcupine on suletud lähtekoodiga litsentsipõhine lahendus, mis ei toeta eesti keelt ega võimalda kasutajal endal kohalikul masinal sünteetilisel andmestikul uut äratussõna mudelit treenida. See tähendab, et **kahel võrdlusteljel neljast — laiendatavus eesti keelele ja sünteetilise andmestiku roll — Porcupine'i ei saa hinnata samadel alustel** kui openWakeWord'i ja microWakeWord'i. Võrdlus oleks asümmeetriline ja eksitav.

See ei tähenda, et Porcupine'i ignoreeritakse. Sissejuhatuses on Picovoice avalik **võrdlusalus** kasutusel sihtväärtuse — alla 1 valeaktiveeringu 10 tunni kohta — kontekstualiseerimiseks; alapeatükis 2.2 on Porcupine eksplitsiitselt kommertsalternatiivina nimetatud. Seega on Porcupine **võrdluskontekstina** olemas, kuid mitte raamistikuna, mida saaks selles töös samaväärselt eesti keele peal proovile panna.

See on teadlik metoodiline valik, mitte huvide konflikt ega tähelepanematus."

---

### Küsimus 5

**Slaid 1: Retsensendi küsimus**
> *Kasutajatest 20–30 osalejaga ei ole töö esitamise hetkeks veel täies mahus tehtud. Kuidas saate siis väita, et mudel on \enquote{usaldusväärne}?*

**Slaid 2: Vastuse teesid**
- **Pealkiri:** Mida väidetakse ja mida ei väideta
- Sissejuhatus: **operatsionaalne** sihimäärang — FAPH < 1, recall ≥ 0,95
- Kokkuvõte: \enquote{v16c jääb **kandidaadiks, mitte tootmistõendiks}}
- §\ref{sec:fourth-round}: kasutajatest kui **neljas** valideerimiskiht
- §\ref{sec:user-test-methodology}: külmutatud lävi, taasmäng varimudelitel — disain on kirjas

**Suuline vastus (Script):**
"See on õigustatud küsimus ja vastus algab sõnavalikust. Sissejuhatuses defineerin \enquote{usaldusväärne} kui **operatsionaalse sihi**: pidevvoo FAPH alla ühe tunnis ja lähikõne tuvastamismäär vähemalt 0,95. Need on käesoleva projekti otsustuskriteeriumid, **mitte kirjanduses kehtestatud universaalsed standardid** — see on otsesõnu sissejuhatuses kirjas.

Mis on **tõestatud** töö hetkeseisuga: treening- ja hindamistoru on Speech Commands `marvin`-kontrollkatsega valideeritud, andmeleke on auditeeritud, positiivse klassi sildistus on auditeeritud, kontrollpunkti valikukriteerium on komposiitne, ja konsensushinnang ühel kõrvalejäetud korpusel annab FAPH 0,79.

Mis on **avameelselt deklareeritud kui veel tõestamata**: kokkuvõttes ütlen, et v16c jääb \emph{kandidaadiks, mitte tootmistõendiks}, kuni ESPHome integreeritud Korvo-2 seadmes tehakse eraldi valideerimine. Alapeatükis 3.6.4 — \enquote{Aus piir: võimalik neljas ring} — ütlen otsesõnu, et lugeja **ei tohi tõlgendada \enquote{multi-mõõdikuline hindamine on parem} kui \enquote{multi-mõõdikuline hindamine on piisav}}.

Kasutajatest on metodoloogiliselt valmis: §2.7 kirjeldab külmutatud läve, varimudelite taasmängu samadel WAV-failidel ning subjektiivse rahulolu lühiküsimustikku UMUX-Lite'iga. Seega on töö lubadus protseduuri korralikkus, mitte mudeli täiuslikkus."

---

### Küsimus 6

**Slaid 1: Retsensendi küsimus**
> *Mainite kasutajatesti subjektiivse rahulolu hindamiseks UMUX-Lite'i, kuid lisate ka uurija enda küsimusi. Kuidas vältida, et mitte-valideeritud küsimused ei moonutaks tulemust?*

**Slaid 2: Vastuse teesid**
- **Pealkiri:** Valideeritud skaalad vs diagnostilised küsimused
- §\ref{sec:user-test-methodology}: UMUX-Lite raporteeritakse **eraldi** valideeritud lühiskaalana
- Uurija küsimused: \enquote{diagnostilised, mitte valideeritud koondskaala tulemused}
- Lewis 2013 ja Sauro/Lewis SEQ kui usaldusväärsuse alus
- Audio opt-in eraldi nõusolekuna — ei sega tehnilist hindamist

**Suuline vastus (Script):**
"Tänan, see on hea metodoloogiline täpsustus. Alapeatükis 2.7 on see kahetasandiline lähenemine eksplitsiitne.

Kui sessiooni ajapiir lubab, siis raporteeritakse UMUX-Lite'i kaks väidet **eraldi valideeritud lühiskaalana**, viidates Lewis 2013 ja Sauro 2009 metoodikale. UMUX-Lite on vastastikku eelretsenseeritud, korreleerub SUS-iga ja sobib lühikese sessiooni jaoks.

Ülejäänud küsimused — süsteemi usaldusväärsuse, kiiruse, käskude loomulikkuse ja kodus kasutamise valmisoleku Likerti hinnangud, üks avatud küsimus häiriva või üllatava kogemuse kohta — on **uurija enda koostatud** ja töös on need otsesõnu märgistatud kui \emph{diagnostilised, mitte valideeritud koondskaala tulemused}. Need ei lähe ühtsesse koondskoori, vaid kasutatakse kvalitatiivse signaali ja konkreetsete probleemikohtade leidmiseks.

See eristus on töös oluline kahel põhjusel. Esiteks ei ole juurutusotsuse alus mitte-valideeritud küsimustiku koondskoor. Teiseks ei riski uurija enda küsimuste raporteerimine UMUX-Lite skoori \enquote{lahjendamisega}, sest need on raporteeritud eraldi tabelitena.

Lisaks: nõusolekumudel on kaheastmeline — minimaalne nõusolek (pseudonüümsed tehnilised tulemused) ja audio opt-in. See tähendab, et tehniline tuvastamismäära mõõtmine ei sõltu sellest, kas osaleja lubab oma häält salvestada."

---

### Küsimus 7

**Slaid 1: Retsensendi küsimus**
> *Töö rõhutab agentpõhise arenduse rolli. Kuidas tagate, et lõputöö tulemused on **teie** akadeemiline panus, mitte tehisagentide oma?*

**Slaid 2: Vastuse teesid**
- **Pealkiri:** Agendid kui töövõimendaja, mitte tõendusmaterjali asendaja
- §3.5 pealkiri ise: \enquote{töövõimendaja, mitte tõendusmaterjali asendaja}
- Agendid ei loo päris kõnelejaid, ei asenda sõltumatuid testikomplekte
- Põhipanus: **valideerimisprotokoll** — metoodika otsus, mitte koodi-tükk
- TI kasutuse deklaratsioon (vt töö kaante-osa)

**Suuline vastus (Script):**
"Tänan, see on kaitstav küsimus ja vastus on töös eraldi alapeatükina — §3.5, mille pealkiri on otseselt \enquote{Agentpõhine arendus kui töövõimendaja, mitte tõendusmaterjali asendaja}.

Teen seal kolm väidet, mis vastavad otse teie küsimusele. Esiteks: agendid vähendasid rakendusliku töö, skriptimise ja prototüüpimise kulu. Konkreetselt — Androidi valevallandumiste logija, hindamisskriptid, koondajad. Need on **tööriistad**, mitte tulemused.

Teiseks — ja see on töö üks keskseid järeldusi — **agendid ei vähenda tõendusmaterjali hankimise kulu samal määral**. Tehisagendid ei loo juurde päris kõnelejaid, ei asenda sõltumatuid testikomplekte, ei lahenda välise valiidsuse probleemi. Seetõttu on töö pudelikael nihkunud teostuselt tõendusele — ja just tõendusmaterjali, mitte koodi, on töö keskmes.

Kolmandaks: töö **akadeemiline põhipanus** ei ole konkreetne mudel ega konkreetne skript, vaid **valideerimisprotokoll** — kolm dokumenteeritud auditit ja mitmemõõtmeline kriteeriumikogum. Need on metoodilised otsused, mille põhjus, struktuur ja piirangud on minu kirjutatud ja minu vastutusel.

Lisaks on kaitsetöös eraldi tehisintellekti kasutuse deklaratsioon, kus on dokumenteeritud, kus ja kuidas agente kasutati. Seega ei ole agendid varjatud kaaskirjutaja, vaid läbipaistev tööriist."

---

## Lõpumärkused esinejale

1. **Asendage küsimused tegelike retsensendi sõnastustega**, niipea kui retsensioon on käes — vastuste sisu jääb suures osas kehtivaks, sest see toetub töös juba kirjapandud passuusidele.
2. Kui retsensent küsib **konkreetseid numbreid** (parameetrite arv, mudeli maht, tensor\_arena), kasutage §\ref{sec:model-architecture} ja §\ref{subsec:quantization} numbreid: ~22\,000 parameetrit, v16c 148\,KB, varasemad 57\,KB, tensor\_arena 45–50\,KB.
3. Kui küsimus puudutab **andmestiku eetikat ja GDPR-i**, viidake §2.7 kahetasandilisele nõusolekumudelile ja sellele, et kasutajatesti heli ei lähe enne lõpphindamist treeningusse.
4. Pidage kõnetempot rahulik — iga skript on testitud ~200–250 sõnal, mis vastab 2 minuti rahulikule tempole.
5. **Vältige üleväitmist**: töös on terve rida \enquote{ausat piiri} formuleeringuid (sissejuhatus, §\ref{sec:fourth-round}, kokkuvõte). Need ei ole nõrkused, vaid teaduslik distsipliin — kasutage neid.
