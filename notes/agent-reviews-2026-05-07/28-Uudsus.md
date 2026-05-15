---
source_prompt: Uudsus.txt
prompt_type: generative (raamimisettepanekud) + evaluative (kriitiline analüüs)
generated: 2026-05-07
---

# Uudsuse ja ülekantava väärtuse analüüs

Käesolev analüüs vaatab tööd kahest vaatenurgast: (1) milliseid üldistatavaid teadmisi saab teos pakkuda lugejale, kes ei kavatse \enquote{Kuule Kratt} mudelit ega Home Assistanti satelliiti kunagi kasutada, ning (2) kuidas neid teadmisi sissejuhatuses ja kokkuvõttes raamida nii, et need ei kõlaks projekti kasutusjuhendina, vaid panusena valdkonna teadmistepagasisse.

## 1. Ülekantavad õppetunnid ja teadmine

Töö juba sisaldab mitut õppetundi, mis kehtivad väljaspool eestikeelse äratussõna projekti. Need on järgmised.

* **Hindamispiir kui treenitav lühitee.** Töö kolmeringiline kirjeldus (§\ref{sec:three-rounds} ja §\ref{sec:general-principle}) näitab, kuidas iga liiga kitsas hindamissõnastus muutub omaette optimeerimissihiks: klipi-tasemel FPR mõõdab tegelikult mälu, kolme-mõõdikuline raporteerimine mõõdab eesliite tuvastamist ning üksiku FAPH miinimumi sihtimine valib mudeli, mis on tundetu ka päris kõnelejale. See on otseselt ülekantav iga väikse korpuse klassifitseerimisülesande peale, kus mõõdik on tihedalt seotud treeninguandmete iseärasustega: keele\-tuvastus, akustiline süžeevalik, teksti\-tasakaaluga klassifikaatorid jms.
* **Andmelekke kontrolli mehhanism kui üldine reegel.** Sõltumatu kõrvalejäetud komplekti, automaatse kattuvuse kontrolli ja treening--testi disjointsuskontrolli kombineerimine (§\ref{sec:data-leakage} ja §\ref{sec:eval-evolution}) on tehniline retsept, mis kehtib igas üliõpilastasandi masinõppeprojektis, kus avalikest korpustest pärit klipid taasringlevad treeningu ja testi vahel. Töö dokumenteerib korrektselt, miks pelgalt heade arvude kuvamine ei tähenda generalisatsiooni.
* **FAPH-i variantide loendusreegli kirjeldus.** §\ref{subsec:faph-variants} eristab nelja FAPH-i varianti (raamistiku, skriptitud taasmängu, välitingimuste ja kasutajatesti taasmängu) ning rõhutab, et need ei ole vastastikku võrreldavad. See on praktiline panus äratussõna kirjandusse, kus loendusreegli ebamäärasus on tunnistatud reprodutseeritavuse auk. Sama mall on rakendatav igale sündmusepõhise tuvastuse mõõdikule (kõnetegevuse tuvastus, alarmi tuvastus, käejälgimine), kus iga töövoo enda jahtumisaeg ja resetiloogika muudab loendust.
* **TTS-positiivsete klippide topeltülehindamine.** Töö täpsustus, et TTS-andmetega treenitud mudelid on TTS-andmetega hinnates topelt üle paisutatud, on omaette metoodiline panus. See ületab Park et al.\ viidet konkreetse vaatlusena: probleem ei piirdu treeninguga, vaid laieneb hindamisele, kui valim on kloonitud samalt kõnelejalt. Sama loogika kehtib iga sünteetilise andme\-augmenteerimise kontekstis (kujutiste GAN-augmenteering, sünteetilised teksti\-andmed jms).
* **Agentpõhise arenduse kui pudelikaela nihutaja.** §-s \enquote{Agentpõhine arendus...} sõnastatud väide --- agendid vähendavad teostuse kulu, kuid mitte tõendusmaterjali kulu --- on ülekantav iga väikese ressursiga teadustöö konteksti. See on raamistus, mida saab tsiteerida ka neis valdkondades, kus arutletakse, kuidas LLM-tööriistad tegelikult akadeemilist tööd mõjutavad: pudelikaela asukoht muutub, mitte ei kao.
* **Konsensus kui kaskaadarhitektuuri erijuhtum.** §\ref{sec:future-cascade} positsioneerib kahe eksperdi ühisotsuse kaskaadarhitektuuri raami sees. See on otseselt ülekantav teistele madala ressursi tuvastusprojektidele: konsensushääletus on odav teine aste, mille saab implementeerida ilma uut mudelit treenimata, kuid mille kasum sõltub esimese astme lühitee-käitumisest.
* **Stsenaariumipõhine 2-tunnine annoteeritud salvestus kui kerge protokoll.** Lahenduse-alajaotus §-s \ref{sec:benchmark-gap} pakub konkreetset, kerget alternatiivi MISP Challenge stiilis kallitele korpustele: neljast osast (vaikus, taustamuusika, vestlus sarnaste fraasidega, kontrollitud äratused) koosnev annoteeritud salvestus on retsept, mida saab kohandada igale kohaliku äratussõna projektile.

## 2. Soovitused uudsuse rõhutamiseks

Töö praegune sissejuhatus ja kokkuvõte raamivad panust eelkõige tehnilise valmisseadme kaudu (\enquote{Kuule Kratt} mudel, ESP32-S3, Home Assistanti integratsioon). See on aus, kuid teeb tööd näiliselt väiksemaks kui ta on. Allpool on konkreetsed soovitused, kuidas raamida sama sisu nii, et ta kõnetaks ka väljaspool seda projekti seisvat lugejat.

### 2.1 Sissejuhatuse raamimine

* **Avalause peaks olema valdkondlik, mitte projekti\-keskne.** Praegune avalause räägib eestikeelsest äratussõnast ja kataloogi tühimikust. Tugevam raam oleks alustada üldistatava väitega: \emph{väikese ressursiga keele kohaliku äratussõna juurutatavus on hindamisprobleem, mitte mudeliprobleem}. Eesti keel ja \enquote{Kuule Kratt} muutuvad seejärel selle väite \emph{empiiriliseks juhtumiks}, mitte töö ainsaks sisuks.
* **Panuse loetelu (a)--(c) tuleks ümber järjestada.** Praegune järjekord asetab esimeseks \enquote{eestikeelne mudel koos toruga}; see kõlab nagu kasutusjuhend. Soovitatav järjekord, mis paigutab metoodilise uudsuse esikohale: (a) \emph{väikese ressursiga keele äratussõna mitmemõõtmelise valideerimise protokoll}, (b) \emph{FAPH-i variantide loendusreegli typoloogia}, (c) \emph{eestikeelse \enquote{Kuule Kratt} mudel selle protokolli empiirilise demonstratsioonina}. See vahetus säilitab kõik faktid, kuid muudab tehnilise teostuse panuse \emph{tõendusinstantsiks}, mitte iseseisvaks väiteks.
* **Hindamise lühitee-mehhanismi peaks tooma sissejuhatusse.** Praegu jõuab lugeja \enquote{hindamine kui treenitav lühitee} kontseptsioonini alles teises peatükis. Sissejuhatusse tuleks lisada üks lause, mis selle mehhanismi anonsib: nt \enquote{töö dokumenteerib, kuidas iga liiga kitsas hindamissõnastus muutus omaette treeningusihiks ning kuidas hindamise laiendamine andis sellele vasturohu}. See annab lugejale lubaduse, et tegemist on metoodilise leiu, mitte üksnes ühe mudeli aruandega.
* **Töö-tasemel piiratus tuleks raamida ülekantavuse, mitte vabandusena.** Praegune sõnastus \enquote{kasutajauuring on piiratud mahus ning hindamine toimub ühe äratusfraasi ulatuses} kõlab kaitsekõnena. Sama fakti saab esitada ülekantavuse võtmes: \enquote{tõendusprotokolli demonstreeritakse ühe fraasi ja kitsa kasutaja\-paneeli peal; sama protokoll on kavandatud nii, et selle saab korrata teiste väikese ressursiga keelte ja teiste fraaside peal ilma metoodikat ümber kirjutamata}. See pöörab piirangu järgmise projekti tee\-näitajaks.

### 2.2 Kokkuvõtte raamimine

* **Esimene lõik ei tohiks alata projekti eesmärgist.** Kokkuvõtte praegune avalause kordab sissejuhatuse projekti\-eesmärki. Tugevam raam alustaks õppetunniga: \enquote{käesolev töö dokumenteerib, et väikese ressursiga keele kohaliku äratussõna juurutatavus määratakse pigem hindamisprotokolli, mitte mudeli arhitektuuri kvaliteediga; eestikeelne \enquote{Kuule Kratt} on selle väite empiiriline juhtum}.
* **Tulemuste lõik peaks rääkima mehhanismist, mitte arvudest.** Praegu kokkuvõte mainib FAPH 0,79 ja \texttt{v16c}-d. Need numbrid kuuluvad tulemuste peatükki. Kokkuvõttes peaks rõhk olema mehhanismil: \emph{kolm valideerimiskihti, mille iga ring laiendas hindamise piiri ühe konkreetse lühitee võrra (andmeleke, prefiksi õppimine, kontrollpunkti optimeerimine)}. See teeb kokkuvõttest panuse, mida saab tsiteerida väljaspool projekti.
* **Lõpulõik peaks ülekantavust eraldi nimetama.** Praeguses kokkuvõttes on järgmiste sammude loetelu projekti\-keskne (kõnelejate mitmekesistamine, testiprotokolli külmutamine, kasutajatestid). Lisada tuleks eraldi lause: \enquote{kirjeldatud valideerimisprotokoll on kohaldatav teiste väikese ressursiga keelte kohaliku äratussõna projektidele, kus ingliskeelsete tööriistade ja nappide kohalike andmete kombinatsioon tekitab sama riskimustri}. See lause olemas peatükis~3 (§\ref{sec:contribution-transferability}); kokkuvõte ei tohiks seda välja jätta.

### 2.3 Pealkirjastamise ja terminite raamimine

* **\enquote{Esimene eesti äratussõna} ei ole töö tugevaim väide.** Töö ise tunnistab seda §-s \ref{sec:contribution-transferability}: tehniline maht on tagasihoidlik, kuid valideerimisprotokolli panus on uudne. Sissejuhatuses ja annotatsioonis tuleks see hierarhia teha lugejale nähtavaks juba esmasel lugemisel: \emph{esmajärjekorras valideerimisprotokoll, teisejärjekorras eestikeelne baasmudel}.
* **\enquote{Tõendusdistsipliin} on tugev termin, mida tasub eksponeerida.** Praegu esineb see peamiselt teises peatükis. Kui see termin tuua sissejuhatusse ja kokkuvõttesse, kerkib töö positsioonilt \enquote{üks projekt} positsioonile \enquote{üks juhtum tõendusdistsipliini rakendamisest}. See on retooriline, kuid madala kuluga muutus.
* **\enquote{Hindamispiir kui lühitee} kui kandev metafoor.} Töö praegune kandev metafoor on \enquote{kolm ringi}. See on hea, kuid puhtalt kronoloogiline. \enquote{Hindamispiir kui treenitav lühitee} on mehhanistlik metafoor, mis kannab töö üldistatavat ideed. Soovitatav oleks see eksplitsiitselt nimetada vähemalt sissejuhatuses, peatüki~3 tiitliosas ja kokkuvõttes; praegu on ta sõnastatud, kuid pealkirja\-tasandil mitte tähistatud.

### 2.4 Negatiivne kontroll: mida \emph{mitte} pakkuda uudsusena

Et hoida raamimist ausana, tasub eraldi nimetada, mida käesolev töö \emph{ei} ole uudne, kuigi võiks selliseks pürgida.

* **MixedNet arhitektuur ei ole töö panus.} See on \texttt{microWakeWord}-i vaikevalik. Sissejuhatus ja annotatsioon ei tohiks selle ümber retoorikat ehitada.
* **Mitmemõõdikuline hindamine üldiselt ei ole uudne.} Töö ise ütleb seda §-s \ref{sec:contribution-transferability}. Uudne on \emph{väikese ressursiga keele projekti jaoks teostatav} sõnastus.
* **Konsensushääletus kahe mudeli vahel ei ole uudne.} See on kaskaadarhitektuuri erijuhtum. Töö paigutab selle korrektselt §-s \ref{sec:future-cascade}; sissejuhatus ei tohiks seda iseseisva uudsusena esitada.

Need kolm negatiivset kontrolli kaitsevad tööd liialdatud uudsuse väite eest ning teevad ülejäänud raamimise usaldusväärsemaks.
