---
source_prompt: 04_Kontrollimine/Konkreetsed_vead/Vorm/Asjatud_võõrsõnad_släng.txt
prompt_type: evaluative
generated: 2026-05-07
---

# Asjatud võõrsõnad ja kõnekeelne släng — keeleline audit

Audit on tehtud kompromissitult, kuid jälgides prompti hoiatust: \emph{ära paranda väljakujunenud erialaterminoloogiat}. Sellisteks loetakse käesolevas töös äratussõna kontekstis: \texttt{streaming}, \texttt{FAPH}, \texttt{FPR}, \texttt{ROC}, \texttt{DET}, \texttt{benchmark} (kohati), \texttt{recall}, \texttt{cutoff}, \texttt{batch}, \texttt{kernel}, \texttt{convolution}, \texttt{tensor\_arena}, \texttt{TFLite}, \texttt{HPC}, \texttt{SLURM}, \texttt{ESPHome}, \texttt{Wyoming}, \texttt{ONNX}, \texttt{Voice Assistant}, \texttt{MoE}, \texttt{INT8}, \texttt{ASR}, \texttt{KWS}, \texttt{TTS}, \texttt{XTTS}, \texttt{XML}, \texttt{SSML}, \texttt{VAD}, \texttt{MUSAN}, \texttt{LibriSpeech}, \texttt{DiPCo}, \texttt{Common Voice}, \texttt{Speech Commands}, \texttt{Wilson}/\texttt{Poisson}, \texttt{SpecAugment}, \texttt{MixedNet}, \texttt{SVDF}, \texttt{checkpoint} (üldlevinud, kuid sünonüüm \emph{kontrollpunkt} on töös juba kasutusel ning sageli eelistatav). Auditeeritud on ainult selliseid kohti, kus eestikeelne kirjakeele variant on võrdselt täpne või täpsem ning autor ise on enamjaolt juba kasutanud.

Töö üldine keeletase on akadeemiline ja korrektne; absoluutne enamus võõrsõnu on põhjendatud erialaterminid. Allpool on välja toodud kohad, kus toimetaja oma rangeimas hoiakus võib õigustatult parandust soovitada. Tegemist on ettepanekutega, mitte kohustuslike paranduste loendiga — autor võib mitme puhul argumenteeritult vastu vaielda.

---

## 1. Asjatud võõrsõnad ja toorlaenud

---
**Algne lause:** „See faktoriseerimine võimaldab saavutada suure ajalise vastuvõtuvälja väikese parameetriarvuga, mis on mikrokontrollerile suunatud mudeli puhul kriitiline nõue“
**Probleemne sõna/fraas:** \emph{kriitiline nõue}
**Asukoht:** ptk 2, §\ref{sec:model-architecture} (MixedConv plokid)
**Parandatud lause:** „See faktoriseerimine võimaldab saavutada suure ajalise vastuvõtuvälja väikese parameetriarvuga, mis on mikrokontrollerile suunatud mudeli puhul \emph{möödapääsmatu} (või \emph{määrav}) nõue.“
**Põhjendus:** „kriitiline“ esineb töös toorlaen-tähenduses 'oluline/möödapääsmatu'; eesti kirjakeeles tähendab \emph{kriitiline} eelkõige 'arvustav'. Soovitatav asendada \emph{määrav}, \emph{möödapääsmatu} või \emph{otsustav}.
---

---
**Algne lause:** „Reaalajas testimine näitas aga vastupidist pilti…“
**Probleemne sõna/fraas:** \emph{reaalajas} (kui ingliskeelse \emph{real-time / live} otsetõlge füüsilise testimise tähenduses)
**Asukoht:** ptk 3, §\ref{sec:benchmark-gap}, ka mujal (nt §\ref{sec:cross-mic-asymmetry}, §\ref{sec:cross-mic-h2})
**Parandatud lause:** „\emph{Päris-/elavtingimustes} (või \emph{seadme peal}) testimine näitas aga vastupidist pilti…“
**Põhjendus:** „reaalajas“ on tehniliselt põhjendatud, kui jutt on \emph{reaalajalisest} (real-time) järeldamisest. Töö kasutab seda aga sageli laiemalt 'pärisseadmel/elavtestil' tähenduses, mis on \emph{real-life}, mitte \emph{real-time}. Tasub eristada: kus mõeldakse voogedastavat kaadritöötlust, jätta \emph{reaalajas}; kus mõeldakse päristestimist, kasutada \emph{päristingimustes} või \emph{seadme peal}.
---

---
**Algne lause:** „Mudel, mis tihedal kõnel vallandub 243 korda tunnis, ei pruugi elutoas vallanduda üldse, sest suurem osa ajast puudub foneetiliselt sarnane sisend.“
**Probleemne sõna/fraas:** üldiselt OK; vt aga „domeen“ („sihtdomeeni“, „domeenivälise“, „domeenispetsiifilise“) järjepidev kasutus
**Asukoht:** ptk 3, §\ref{sec:cross-mic-asymmetry}, ka §\ref{sec:benchmark-gap}, §\ref{sec:contribution-transferability}
**Parandatud lause:** „…sihtkeele \emph{kasutusvaldkonnast} pärit negatiive…“ (üksiku esmamainimise juures)
**Põhjendus:** „domeen“ on omaks võetud erialatermin ja seda asendada täielikult ei tasu. Esmamainimisel on aga kasulik tuua välja eestikeelne sünonüüm \emph{(kasutus)valdkond} või \emph{tegevusala}, et lugeja seoseid mõistaks. Praegune kasutus on tehniliselt korrektne — see on pigem stiililine vinjett.
---

---
**Algne lause:** „Pikem kontekstiaken (nt 2000\,ms) annaks rohkem eelkonteksti ja lubaks mudelil paremini diskrimineerida pikemaid sarnaseid fraase…“
**Probleemne sõna/fraas:** \emph{diskrimineerida}
**Asukoht:** ptk 2, §\ref{subsec:clip-duration}
**Parandatud lause:** „Pikem kontekstiaken (nt 2000\,ms) annaks rohkem eelkonteksti ja lubaks mudelil paremini \emph{eristada} pikemaid sarnaseid fraase…“
**Põhjendus:** \emph{diskrimineerida} on tarbetu võõrsõna; eesti kirjakeeles on neutraalne sõna \emph{eristada}. Töö kasutab muudes kohtades juba „eristada“, mistõttu siin tasub ühtlustada.
---

---
**Algne lause:** „MacBook taustamonitori 70-minutilise seansi jooksul ei registreeritud ühtegi valevallandumist…“
**Probleemne sõna/fraas:** \emph{seansi}
**Asukoht:** ptk 2, §\ref{sec:expert-consensus}
**Parandatud lause:** „MacBook taustamonitori 70-minutilise \emph{salvestuse} (või \emph{katsejooksu}) jooksul ei registreeritud ühtegi valevallandumist…“
**Põhjendus:** \emph{seanss} on aktsepteeritud, aga teaduslikus tekstis kõlab \emph{salvestus} või \emph{katsejooks} loomulikumalt. Stiililine vinjett, mitte viga.
---

---
**Algne lause:** „Andmed teisendatakse spektraalseteks tunnusteks ja salvestatakse \texttt{mmap} vormingus. Memory-mapped file lähenemine võimaldab töödelda suuri andmehulkasid…“
**Probleemne sõna/fraas:** \emph{Memory-mapped file lähenemine}
**Asukoht:** ptk 2, „Tunnused ja andmevorming“
**Parandatud lause:** „\emph{Mälukaardistatud failide (ingl \emph{memory-mapped files})} lähenemine võimaldab töödelda suuri andmehulkasid…“ — või järjekindlalt „\texttt{mmap}-faili lähenemine“
**Põhjendus:** segakeelne fraas „Memory-mapped file lähenemine“ on toorlaen, mis murrab teksti üldise stiili. Soovitavalt kas eestikeelne kirjeldus + sulgudes ingliskeelne termin (nagu töö mujal teeb), või lihtsalt \texttt{mmap}-faili.
---

---
**Algne lause:** „…kahekohanumbrelise suurusjärgu erinevus prognoosist“ ja „kahe \emph{kuuekoht\-numbrelise} suurusjärgu erinevus prognoosist“
**Probleemne sõna/fraas:** \emph{kuuekohtnumbrelise}
**Asukoht:** ptk 3, §\ref{sec:three-rounds}, esimene ring
**Parandatud lause:** „kahe \emph{suurusjärgu} (factor of $\sim$100) erinevus prognoosist“
**Põhjendus:** „kuuekohtnumbreline suurusjärk“ on otsetõlke-stiilis, eesti keeles ebaharilik konstruktsioon, mis pealegi ei ole tähenduslikult ühene (kas mõeldud on faktorit $10^6$? Kontekstist on lugeda, et tegu on $\sim$100$\times$ erinevusega, mis vastaks \emph{kahele suurusjärgule}). Vt ka prompt: \emph{otsetõlge inglise keelest, mis ei kõla loomulikult}. Lisaks tasub kontrollida, kas õige number on 100$\times$ vs $10^6\times$.
---

---
**Algne lause:** „…vahepealse v6-residual eksperimendi tulemus näitas, et residuaalühendused parandasid \emph{streaming}-stabiilsust…“ (parafraseeriv kokkuvõte v6 vs v6-residual ablatsioonist)
**Probleemne sõna/fraas:** \emph{streaming}-stabiilsus, \emph{streaming-konteksti}, \emph{streaming-režiimis} (esmamainimine on töös tehtud korrektselt: „voogedastusrežiimis (voogedastav järeldamine, ingl \emph{streaming inference})“)
**Asukoht:** ptk 2, §\ref{sec:residual-ablation}; ptk 3, „Põhjus 3“
**Parandatud lause:** Asendada hilisemates esinemistes „streaming“ järjepidevalt eestikeelse \emph{voogedastav} või \emph{pidevvoo}-vormiga.
**Põhjendus:** Töö esmamainimine on hea; pärast seda tuleks toorlaen \emph{streaming} asendada juba kasutusele võetud terminiga \emph{voogedastav} / \emph{pidevvoo}. Praegu vahelduvad mõlemad. Järjepidevus on akadeemilises eesti keeles oluline.
---

---
**Algne lause:** „Reaalajas test paljastas aga, et osa mudeleid vallandus üksiku sõna \enquote{kuule} või \enquote{kule} peale, ilma \enquote{kratt}-i lisamata.“
**Probleemne sõna/fraas:** \emph{lisamata}
**Asukoht:** ptk 3, §\ref{sec:three-rounds}
**Parandatud lause:** „…vallandus üksiku sõna \enquote{kuule} või \enquote{kule} peale, ilma \enquote{kratt}-i \emph{järele lisamata}.“ (või veel parem: „ilma sõna \enquote{kratt} \emph{järele ütlemata}.“)
**Põhjendus:** otsetõlge \emph{without adding} → \emph{lisamata}; kuid kuna jutt on hääldusest, on idiomaatilisem \emph{järele ütlemata}.
---

---
**Algne lause:** „…tehakse järeldamine\,…ESPHome\,…lisaks 45--50\,KB töömälu (\texttt{tensor\_arena}), kuhu paigutatakse vahetulemused.“
**Probleemne sõna/fraas:** \emph{vahetulemused}
**Asukoht:** ptk 2, §\ref{subsec:quantization}
**Parandatud lause:** lubatav ja korrektne; pole vaja parandada
**Põhjendus:** ei kvalifitseeru kui võõrsõna ega släng; läbis kontrolli.
---

---
**Algne lause:** „Sensory, kes arendab Samsung'i äratussõna mudeleid, on tunnistanud…“
**Probleemne sõna/fraas:** \emph{tunnistanud}
**Asukoht:** ptk 3, §\ref{sec:benchmark-gap} („Põhjus 2“)
**Parandatud lause:** korrektne, ei vaja muutmist (\emph{tunnistama} on hea eesti omakeelne sõna)
**Põhjendus:** läbis kontrolli.
---

---
**Algne lause:** „…praktiline pudelikael ei ole enam toru tehniline puudulikkus…“
**Probleemne sõna/fraas:** \emph{pudelikael}
**Asukoht:** ptk 3, „Mida saab juba praegu väita“
**Parandatud lause:** „…praktiline \emph{kitsaskoht} ei ole enam toru tehniline puudulikkus…“
**Põhjendus:** \emph{pudelikael} on inglise \emph{bottleneck} otsetõlge ja kuigi kasutatud, on \emph{kitsaskoht} eesti kirjakeeles akadeemilises tekstis loomulikum. See on aga maitse küsimus — \emph{pudelikael} on lubatav.
---

---
**Algne lause:** „Lisaks tugevdati \texttt{train\_microwakeword\_experiment.sh} skriptis tunnusekäo (\emph{feature cache}) sõrmejälge…“
**Probleemne sõna/fraas:** \emph{tunnusekäo}, \emph{sõrmejälge}
**Asukoht:** ptk 2, §\ref{sec:training-guards}
**Parandatud lause:** „Lisaks tugevdati \texttt{train\_microwakeword\_experiment.sh} skriptis tunnuste \emph{vahemälu} (\emph{feature cache}) sõrmejälge (\emph{fingerprint})…“
**Põhjendus:** \emph{tunnusekäoks} on tõlgitud \emph{cache}, mis aga eesti tehnikakirjanduses on harva sellisel kujul kasutusel; tavaline vaste on \emph{vahemälu}. \emph{Sõrmejälg} on okei (omakeelne ja tähenduslik), aga esmamainimisel võiks lisada \emph{fingerprint} sulgudes.
---

---
**Algne lause:** „…audit (vt ptk~\ref{chapter:results}, §\ref{sec:positive-audit}) näitas, et positiivses klassis oli \emph{teist järku sildistusprobleem}…“
**Probleemne sõna/fraas:** \emph{audit}
**Asukoht:** kogu töös laialt (vähemalt 10+ esinemist: §\ref{sec:positive-audit}, §\ref{sec:second-audit}, §\ref{sec:third-audit}, §\ref{sec:metric-iteration-conclusion} jt)
**Parandatud lause:** \emph{Audit} on lubatav ja eesti keeles olemas (sõnaraamatutes), kuid „auditiring“ → võimalik asendada \emph{kontrolliring}.
**Põhjendus:** \emph{audit} on terminoloogiliselt väljakujunenud (eriti raamatupidamis- ja tarkvarakontekstis), kuid kombinatsioon „auditiring“ on töö-spetsiifiline neologism. Akadeemilisemalt: \emph{kontrolliring} või \emph{revisjoniring}. Soovitan jätta \emph{audit} sees ja muuta ainult juhul, kui kogu töö läbiv järjepidevus seda kannab. Mitte kohustuslik.
---

---
**Algne lause:** „Korrigeeritud hindamine võimaldas teha täiendava eksperimendi…“
**Probleemne sõna/fraas:** \emph{korrigeeritud}, \emph{eksperimendi}
**Asukoht:** kogu töös laialt
**Parandatud lause:** mõlemad on aktsepteeritavad akadeemilised võõrsõnad, vasted (\emph{parandatud}, \emph{katse}) eksisteerivad ja oleks puhtam, kuid mitte kohustuslik.
**Põhjendus:** \emph{korrigeeritud} → \emph{parandatud} oleks ilusam, kuid „korrigeeritud“ on aktsepteeritav. \emph{Eksperiment} → \emph{katse} on puhtam, aga „eksperiment“ on lubatud. Stiililine maitseküsimus.
---

---
**Algne lause:** „…operatsionaalset sihti…“
**Probleemne sõna/fraas:** \emph{operatsionaalset}
**Asukoht:** sissejuhatus
**Parandatud lause:** „…\emph{kasutuspõhist} (või \emph{tööpõhist}) sihti…“
**Põhjendus:** \emph{operatsionaalne} on raskepärane võõrsõna; \emph{kasutuspõhine} või \emph{tööpõhine} on kergem. Promptis on selgelt välja toodud sarnane juhtum (\emph{fokusseerima} → \emph{keskenduma}).
---

---
**Algne lause:** „…multi-mõõdikuline hindamine on parem kui ühe-mõõdikuline…“
**Probleemne sõna/fraas:** \emph{multi-mõõdikuline}
**Asukoht:** ptk 3, §\ref{sec:fourth-round}; mujal „mitme-mõõdikuline“ ja „multi-mõõdikuline“ vahelduvad
**Parandatud lause:** asendada järjepidevalt eestikeelse vormiga: \emph{mitme-mõõdikuline}.
**Põhjendus:** segakeelne \emph{multi-mõõdikuline} on inglise eesliite ja eesti tüve hübriidvorm; eesti keeles toimib \emph{mitme-} samas funktsioonis. Töö kasutab juba mõlemat — vajalik ühtlustada.
---

---
**Algne lause:** „…integreeritavus, sealhulgas mudeli suurus, järeldamise praktiline teostatavus ja sobivus ESP32-S3 klassi seadmele…“
**Probleemne sõna/fraas:** \emph{integreeritavus}
**Asukoht:** ptk 1, „Võrdlusraamistik“
**Parandatud lause:** „…\emph{lõimitavus} (sh sobivus mikrokontrolleri ressurssidega)…“
**Põhjendus:** \emph{lõimima/lõimitavus} on töös \emph{ülesandepüstituses} juba kasutusel („süsteemi lõimimine“). Stiililise järjepidevuse huvides tasub esimese peatüki \emph{integreeritavus} ühtlustada \emph{lõimitavusega}, kui see ei muuda terminiviiteid teistes kohtades.
---

---
**Algne lause:** „Esmane \emph{benchmark} (2026-04-26, lävi 0,995) andis tõepoolest näiliselt soovitud tulemuse…“
**Probleemne sõna/fraas:** \emph{benchmark} (toorlaenuna)
**Asukoht:** ptk 2, §\ref{sec:second-audit}
**Parandatud lause:** „Esmane \emph{võrdluskatse} (või \emph{võrdlusalus}) (2026-04-26, lävi 0,995) andis tõepoolest näiliselt soovitud tulemuse…“
**Põhjendus:** Töö kasutab paralleelselt \emph{võrdlusalus} ja \emph{benchmark}. Esmamainimisel kasutab autor eestikeelset vastet (\emph{võrdlusalus}) ning seda võiks järgida ka edaspidi. \emph{Benchmark}-tulemus → \emph{võrdluskatse tulemus}.
---

---
**Algne lause:** „…lokaalsel riistvaral juba kasutatav…“
**Probleemne sõna/fraas:** \emph{lokaalsel}
**Asukoht:** sissejuhatus, kogu töös
**Parandatud lause:** \emph{kohalik(ul)}
**Põhjendus:** \emph{kohalik} ja \emph{lokaalne} esinevad töös vaheldumisi (nt „kohalik äratussõna treeningu- ja hindamistoru“ ↔ „lokaalse nutikodu satelliidi näitel“). Akadeemilises eesti keeles on neutraalne valik \emph{kohalik}; \emph{lokaalne} on lubatav, kuid raskepärasem. Soovitatav järjepidevalt eelistada \emph{kohalik}.
---

---
**Algne lause:** „Need on käesoleva töö projekti-spetsiifilised otsustuskriteeriumid…“
**Probleemne sõna/fraas:** \emph{projekti-spetsiifilised}
**Asukoht:** sissejuhatus
**Parandatud lause:** „Need on käesoleva töö \emph{projektipõhised} otsustuskriteeriumid…“
**Põhjendus:** \emph{spetsiifiline} → \emph{eriomane / -põhine} on eesti keeles puhtam vorm. „Projektipõhine“ kõlab loomulikumalt.
---

---
**Algne lause:** „…Mac sarnaste negatiivnäidete FPR jäi 100\% tasemele ning Kõneleja~A XTTS sarnaste negatiivnäidete FPR isegi halvenes 60\%-lt 73\%-le.“
**Probleemne sõna/fraas:** \emph{halvenes} (siin OK), kuid kõrval „mudeleid v2, v5 ja v6 ei saa nende klippide järgi statistiliselt eristada“ → \emph{statistiliselt} (lubatud)
**Asukoht:** ptk 2 mitmel pool
**Parandatud lause:** ei vaja parandust
**Põhjendus:** läbis kontrolli.
---

---

## 2. Kõnekeelne släng ja stiilivead

---
**Algne lause:** „v6 mudel andis MacBook~Pro mikrofoni 40-minutilisel tavakõne testil FAPH~$\approx$~50…“
**Probleemne sõna/fraas:** \emph{andis} (kõnekeelne) — koos teiste kohtadega, kus mudel „annab“ FAPH-i
**Asukoht:** sissejuhatus; ptk 2 mitmel pool
**Parandatud lause:** „…v6 mudel \emph{tootis} (või \emph{registreeris} / \emph{näitas}) MacBook~Pro mikrofoni 40-minutilisel tavakõne testil FAPH~$\approx$~50…“
**Põhjendus:** \emph{andma} on suupärane, kuid akadeemilises kontekstis on \emph{registreeris}, \emph{näitas} või \emph{tootis} täpsem. Töö kasutab kõiki kolme variante; ühtlustamine on stiililine valik.
---

---
**Algne lause:** „…osa automaatselt loodud või liiga lühikesi positiivseid näiteid ei kandnud sisuliselt tervet fraasi.“
**Probleemne sõna/fraas:** ei kvalifitseeru
**Asukoht:** ptk 3, §\ref{sec:three-rounds}
**Parandatud lause:** ei vaja parandust
**Põhjendus:** läbis kontrolli.
---

---
**Algne lause:** „Mõned konfiguratsioonid jõudsid valitud taustaradadel nulli lähedase FAPH-ini…“
**Probleemne sõna/fraas:** \emph{Mõned}
**Asukoht:** ptk 3, §\ref{sec:three-rounds}, kolmas ring
**Parandatud lause:** „\emph{Osa} (või \emph{Mitu}) konfiguratsiooni jõudis valitud taustaradadel nulli lähedase FAPH-ini…“
**Põhjendus:** \emph{mõned} on aktsepteeritav, kuid akadeemilises stiilis kõlab \emph{osa} või \emph{mitu} mõnevõrra ametlikumalt. Maitsmise küsimus.
---

---
**Algne lause:** „…tegelik põhjus võinuks peituda hoopis treeningutoru tehnilises piirangus…“
**Probleemne sõna/fraas:** \emph{hoopis}
**Asukoht:** ptk 3, „Miks avalik kontrollkatse oli vajalik“
**Parandatud lause:** „…tegelik põhjus võinuks peituda \emph{hoopiski} (või \emph{tegelikult / pigem}) treeningutoru tehnilises piirangus…“
**Põhjendus:** \emph{hoopis} on kõnekeelelähedane partikkel. Akadeemilises tekstis sobib \emph{hoopiski}, \emph{pigem} või vormingu ümbersõnastus. Mitte oluline puudus, pigem nõuanne.
---

---
**Algne lause:** „…iga uus reaalajas test võib paljastada uue mõõtmata puuduse.“
**Probleemne sõna/fraas:** \emph{paljastada}
**Asukoht:** ptk 2, §\ref{sec:metric-iteration-conclusion}
**Parandatud lause:** korrektne; ei vaja muutmist
**Põhjendus:** \emph{paljastama} on hea eestikeelne sõna ja akadeemilises kontekstis aktsepteeritav.
---

---
**Algne lause:** „v17 kujunes ootamatuks tagasilöögiks.“
**Probleemne sõna/fraas:** \emph{tagasilöögiks}
**Asukoht:** ptk 2, §\ref{sec:second-audit}
**Parandatud lause:** „v17 kujunes \emph{ootamatuks komistuskiviks} (või \emph{tagasiminekuks}).“
**Põhjendus:** \emph{tagasilöök} on lubatav, kuid teaduslikus tekstis veidi liialt narratiivne. Pole otseselt släng — pigem stilistiline märkus.
---

---
**Algne lause:** „Mudel ei õppinud mitte kahe-sõnalist äratusfraasi, vaid foneetilist eesliidet — mistahes \enquote{kuule}- või \enquote{kule}-tüüpi konsonant-vokaal mustrit, millele võis järgneda peaaegu suvaline jätk.“
**Probleemne sõna/fraas:** \emph{peaaegu suvaline jätk}
**Asukoht:** ptk 2, §\ref{sec:second-audit}
**Parandatud lause:** „…millele võis järgneda \emph{praktiliselt mistahes} jätk.“
**Põhjendus:** \emph{suvaline} on aktsepteeritav, kuid teaduslikus tekstis täpsem on \emph{mistahes} või \emph{ükskõik milline}. \emph{Peaaegu suvaline} on kõnekeelselik. Vinjett.
---

---
**Algne lause:** „…lubatud venitatud vokaalid…“ (v18 positiivse poliitika kirjelduses)
**Probleemne sõna/fraas:** \emph{venitatud vokaalid}
**Asukoht:** ptk 2, §\ref{sec:v18-results}
**Parandatud lause:** „…lubatud \emph{pikendatud} (\emph{prolongeeritud}) vokaalid…“
**Põhjendus:** \emph{venitatud} on kõnekeelelähedane; foneetikas korrektne termin on \emph{pikendatud} või \emph{prolongeeritud vokaal} (vrd Asu \& Teras 2009). Selge stiiliviga akadeemilises tekstis.
---

---
**Algne lause:** „v6 paistis tippkvaliteediga tulemus.“
**Probleemne sõna/fraas:** \emph{paistis tippkvaliteediga tulemus}
**Asukoht:** ptk 2, §\ref{sec:three-rounds} esimene ring (vt ptk 3 vaste)
**Parandatud lause:** „v6 \emph{paistis kõrgekvaliteedilise tulemusena}.“
**Põhjendus:** \emph{tippkvaliteet} on suupärane reklaamilik tarind. \emph{Kõrgekvaliteediline} või \emph{tipptasemel} on neutraalsem.
---

---
**Algne lause:** „…tegemist polnud generalisatsiooni mõõtmisega, vaid mälu kontrolliga.“
**Probleemne sõna/fraas:** \emph{generalisatsiooni}
**Asukoht:** ptk 3, §\ref{sec:three-rounds}; ptk 2, §\ref{sec:cross-mic-asymmetry}
**Parandatud lause:** „…tegemist polnud \emph{üldistusvõime} mõõtmisega, vaid mälu kontrolliga.“
**Põhjendus:** \emph{generalisatsioon} on aktsepteeritav statistilises masinõppe kirjanduses, kuid eestikeelne \emph{üldistusvõime} / \emph{üldistumine} esineb töös juba teises kohas (sissejuhatus: „mudeli üldistusvõimest“). Soovitatav järjepidevus.
---

---
**Algne lause:** „Mudel \emph{paistis ülevallandununa}.“ (v3 kohta)
**Probleemne sõna/fraas:** \emph{ülevallandunud}, \emph{ülevallandunununa}
**Asukoht:** ptk 2, §\ref{sec:three-rounds}, „Iteratiivne paranemine: v4 kuni v6“
**Parandatud lause:** „Mudel paistis \emph{üleaktiivsena} (või \emph{liiga vallanduvana}).“
**Põhjendus:** „ülevallandunud“ on töö-sisene neologism, mis kõlab kui kõnekeelne moodustis. Korrektsem oleks \emph{üleaktiveeruv}, \emph{üleaktiivne} või kirjeldav „liiga sageli vallanduv“. Mitte släng kitsamas mõttes, kuid akadeemilises tekstis ebaharilik.
---

---
**Algne lause:** „v17 kujunes ootamatuks tagasilöögiks. Selle eesmärk oli tõsta tuvastamismäära…“
**Probleemne sõna/fraas:** \emph{tõsta tuvastamismäära}
**Asukoht:** ptk 2, §\ref{sec:second-audit}
**Parandatud lause:** „…Selle eesmärk oli \emph{parandada} tuvastamismäära…“
**Põhjendus:** \emph{tõsta} numbri kohta on suupärane; akadeemilises eesti keeles \emph{parandada} (kvaliteedi mõttes) või \emph{kasvatada} (numbrilises mõttes) on selgemad. Pole olulises mõttes släng.
---

---
**Algne lause:** „Mudelite reaalajas testimisel ilmnes seletus, mida benchmark üksi ei näidanud.“
**Probleemne sõna/fraas:** kombinatsioon \emph{reaalajas + benchmark} ühes lauses
**Asukoht:** ptk 2, §\ref{sec:second-audit}
**Parandatud lause:** „Mudelite \emph{seadme peal} testimisel ilmnes seletus, mida \emph{võrdluskatse} üksi ei näidanud.“
**Põhjendus:** kahe toorlaenu kuhjumine ühte lausesse; vt eelnevaid soovitusi.
---

---
**Algne lause:** „Tabeli \enquote{parimad} märkimine vastab ühele lävele; DET-kõvera (\emph{detection error tradeoff}) põhjal (joonis~\ref{fig:det-v6-v15-v16c-experta}) ei domineeri ükski perekond kogu töövahemikus.“
**Probleemne sõna/fraas:** \emph{ei domineeri}
**Asukoht:** ptk 2, §\ref{sec:expert-consensus}
**Parandatud lause:** „…ei \emph{ületa} (või \emph{ei jää teistest paremaks}) ükski perekond kogu töövahemikus.“
**Põhjendus:** prompt toob otseselt välja: \emph{domineerima} → \emph{valitsema/ületama}. Statistilise dominantsuse mõistest tuleneb otsene tõlge \emph{ei domineeri}, mis on omakorda erialatermini-piirialal — kuid lugejale on \emph{ei ületa kõigis töövahemikupunktides} arusaadavam.
---

---
**Algne lause:** „v6 mudel andis MacBook~Pro mikrofoni 40-minutilisel tavakõne testil FAPH~$\approx$~50“ (sissejuhatus)
**Probleemne sõna/fraas:** \emph{tavakõne}
**Asukoht:** sissejuhatus; ptk 2, §\ref{sec:cross-mic-asymmetry}
**Parandatud lause:** korrektne, ei vaja parandust
**Põhjendus:** läbis kontrolli — \emph{tavakõne} on neutraalne kirjakeelne väljend.
---

---
**Algne lause:** „Üksiku eestikeelse äratussõnamudeli peale on äratussõnade kontekstis suurematel rühmadel oluliselt rohkem ressursse…“
**Probleemne sõna/fraas:** \emph{peale}
**Asukoht:** ptk 3, §\ref{sec:eval-evolution}
**Parandatud lause:** „\emph{Üksiku eestikeelse äratussõnamudeli kõrval} on äratussõnade kontekstis suurematel rühmadel…“
**Põhjendus:** „X-i peale on Y-il rohkem ressursse“ on kõnekeelne konstruktsioon (X-i \emph{vastu}, X-iga \emph{võrreldes}). Akadeemiline vorm: \emph{kõrval}, \emph{võrreldes}, \emph{vastandina}.
---

---
**Algne lause:** „Need süsteemid on treenitud kümnete tuhandete tundide negatiivsete andmetega…“
**Probleemne sõna/fraas:** \emph{kümnete tuhandete tundide}
**Asukoht:** ptk 2, §\ref{sec:expert-consensus}
**Parandatud lause:** korrektne, ei vaja parandust
**Põhjendus:** läbis kontrolli.
---

---
**Algne lause:** „Mõlema mudeli puhul lülitati SpecAugment sisse samal ajal, kui lisati 6090 uut TTS sihtfraasiga sarnast negatiivklippi…“
**Probleemne sõna/fraas:** \emph{lülitati sisse} (kõnekeelne)
**Asukoht:** ptk 2, §\ref{sec:specaug-ablation}
**Parandatud lause:** „v7 puhul \emph{aktiveeriti} SpecAugment samal ajal, kui lisati…“ (või „võeti SpecAugment kasutusele samal ajal, kui…“)
**Põhjendus:** \emph{lülitada sisse/välja} on kõnekeelne väljend, eriti programmi/parameetri kohta. \emph{Aktiveerida}, \emph{rakendada} või \emph{kasutusele võtta} on neutraalsemad. Promptis on otsesõnu välja toodud sarnased juhtumid (nt \emph{tšekkama → kontrollima}).
---

---
**Algne lause:** „Pere koosneb kuuest variandist…“
**Probleemne sõna/fraas:** \emph{pere} (mudeliperekonna lühendina)
**Asukoht:** ptk 2, §\ref{sec:v18-results} ja kogu töös
**Parandatud lause:** kasutada järjepidevalt \emph{perekond} (mitte \emph{pere}); \emph{pere} on töös vaheldumisi.
**Põhjendus:** \emph{pere} on argisem vorm \emph{perekonnast}; akadeemilises tekstis tuleks valida üks vorm ja seda järjepidevalt kasutada. Töö kasutab juba mõlemat (nt „v18 perekonna tulemused“ ↔ „Pere koosneb kuuest variandist“). Eelistatav: \emph{perekond} läbivalt.
---

---

## Kokkuvõttev hinnang

Töö keelekasutus on üldiselt akadeemilisel tasemel. Suuremad probleemid on:

1. **Järjepidevus**, mitte üksikud vead. Töös vahelduvad samade mõistete eesti- ja võõrkeelsed variandid: \emph{streaming} ↔ \emph{voogedastav}; \emph{lokaalne} ↔ \emph{kohalik}; \emph{benchmark} ↔ \emph{võrdluskatse / võrdlusalus}; \emph{generalisatsioon} ↔ \emph{üldistusvõime}; \emph{pere} ↔ \emph{perekond}; \emph{multi-} ↔ \emph{mitme-}. Soovitan teha läbiv ühtlustamine eesti vormi kasuks.
2. **Üksikud kõnekeelelised konstruktsioonid**, mida tasub parandada: „lülitada sisse“, „venitatud vokaalid“, „X-i peale on Y-il“, „kuuekohtnumbreline suurusjärk“, „peaaegu suvaline jätk“.
3. **Stiili-ühtsus**: „audit“ ja „auditiring“ on töö enda neologismid; soovitatav neid säilitada (et terminoloogia oleks töösisesest järjepidev), kuid teadvustada, et kompromissitu eesti keele toimetaja võib pakkuda \emph{kontrolliring}.
4. **Toorlaenude esmamainimise distsipliin** on töös enamasti hästi järgitud (\emph{streaming inference}, \emph{detection error tradeoff}, \emph{feature cache} on esmamainimisel sulgudes). See tasub säilitada.

Töö ei sisalda klassikalisi promptis nimetatud slängi-näiteid (\emph{äpp}, \emph{proge}, \emph{bugi}, \emph{tšekkama}, \emph{okei}, \emph{jooksutama}, \emph{feilima}, \emph{suht}, \emph{jube}). Selles mõttes on tekst akadeemiliselt distsiplineeritud. Põhilised parandused jäävad kahte kategooriasse: (a) toorlaenude järjepidev asendamine eestikeelsete vastetega, mis on töös juba olemas, ning (b) üksikud kõnekeelelised pöörded, mille parandamine on lihtne.
