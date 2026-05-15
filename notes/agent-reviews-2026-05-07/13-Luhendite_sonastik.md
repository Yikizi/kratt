---
source_prompt: Lühendite_ja_mõistete_sõnastik.txt
prompt_type: generative (auditeeriv ja parandav nimekirja-koostamine)
generated: 2026-05-07
---

# Lühendite ja mõistete sõnastiku audit

## 1. Analüüsi kokkuvõte

### Eemaldamissoovitused (nimekirjas, kuid töös ei esine eraldiseisva lühendina)

- **CPU** — termin ei esine üheski auditeeritud peatükis (sissejuhatus, ptk 1--3, kokkuvõte, abstraktid, ülesandepüstitus). Mikrokontrolleri kontekstis räägitakse kogu töös \enquote{ESP32-S3 protsessorist} või \enquote{mikrokontrollerist}, mitte \enquote{CPU-st}. Soovitus: eemaldada.
- **DSP** — termin ei esine kasutuses üheski auditeeritud peatükis. Soovitus: eemaldada.
- **IOT** — termin ei esine üheski auditeeritud peatükis. \enquote{Asjade internet} kontseptsioon on töös implitsiitne, kuid lühendit endiselt ei kasutata. Soovitus: eemaldada.
- **ESP** — eraldiseisev lühend \enquote{ESP} ei esine; kõikjal kasutatakse konkreetselt \enquote{ESP32-S3} või \enquote{ESPHome}. Soovitus: asendada konkreetse kirjega \enquote{ESP32-S3} (vt allpool) ja eemaldada üldine \enquote{ESP} kirje, kuna see eksitab lugejat (ESPHome ei ole \enquote{Espressif Systems mikrokontrollerite perekond}, vaid eraldi tarkvarakiht).

### Puudujäägid (tekstis kasutusel, kuid nimekirjast puuduvad)

Olulised puuduvad lühendid ja mõisted:

- **ASR** — kasutusel ptk 1 ja 2 (nt \enquote{automaatse kõnetuvastuse (ASR)}, \enquote{ASR-korpus}).
- **AUC** — kasutusel ptk 1 ja 2 ROC-analüüsi tulemuste juures.
- **CC-BY-SA 3.0** — kasutusel ptk 2 korpuse litsentsi tähistusena.
- **Common Voice / CV ET** — kasutusel kogu töös; \enquote{ET} on Common Voice'i eestikeelse alamkogu lühend.
- **DET-kõver** — kasutusel ptk 2 (\emph{detection error tradeoff}).
- **DiPCo** — kasutusel ptk 2 taustaheli korpusena, ei ole defineeritud.
- **DNN-HMM** — kasutusel ptk 2 ja 3 (Apple'i \enquote{Hey Siri} viited).
- **ESP32-S3} — keskne sihtplatvorm; viidatakse pidevalt, kuid eraldiseisva kirjena puudub.
- **ESPHome** — kasutusel sissejuhatuses, ptk 1 ja 2; eraldi mõiste, mis ei ole \enquote{ESP}.
- **ESP32-S3-Korvo-2 / Korvo-2** — konkreetne arendusplaat, kasutusel ülesandepüstituses ja ptk 2.
- **ETIS** — kasutusel ptk 2 (lõputööde register).
- **FAPH-i variandid** (raamistiku, skriptitud taasmängu, välitingimuste, kasutajatesti taasmängu) — defineeritud ptk 1 §2.6.1, kuid mõiste \enquote{FAPH} kirje ei viita variantidele.
- **FA/h} — esineb ptk 2 ja sissejuhatuses; sama nähtus mis FAPH, kuid eri kirjapildiga.
- **Hold-out / kõrvalejäetud komplekt** — kasutusel kokkuvõttes ja ptk 2 keskse mõistena.
- **Home Assistant** — kasutusel kogu töös; mõiste vajab lühikirjeldust mittetehnilisele lugejale.
- **HPC** — kasutusel ptk 2 (\enquote{HPC-treeningu ülesseadmine}).
- **INT8** — kasutusel ptk 1 §1.6.5 kvantiseerimise juures.
- **KWS** — kasutusel ptk 2 ja 3 (\enquote{KWS võrdlusalused}, \enquote{KWS-süsteem}).
- **Kiirkirjutaja** — viidatakse ülesandepüstituses ja kontekstis; nimi/projekt vajab selgitust.
- **kratt CLI / kratt user-test** — kasutusel ptk 1 §1.6.7; töötavate käsureatööriistade pere.
- **mel-spektrogramm / mel-sagedus** — kasutusel ptk 1 mudeli arhitektuuri kontekstis.
- **microWakeWord** — keskne raamistik, viidatakse pidevalt; mõiste vajab lühikirjeldust.
- **MISP** — kasutusel ptk 3 (MISP Challenge).
- **MixedNet / MixConv / MixedConv plokk** — kasutusel ptk 1 ja ülesandepüstituses; tuumarhitektuur.
- **MUSAN** — kasutusel ptk 1 ja 2 taustaheli korpusena.
- **Neurokõne** — kasutusel ptk 2 sünteetiliste positiivsete allikana.
- **ONNX** — kasutusel ptk 1 §1.2 (openWakeWord'i runtime).
- **openWakeWord** — kasutusel kogu töös võrdlusraamistikuna.
- **Picovoice Porcupine} — kasutusel sissejuhatuses ja ptk 1; suletud lähtekoodiga võrdluspunkt.
- **RMS} — kasutusel ptk 1 §1.6.7 (audiosignaali energianäitaja).
- **RNG} — kasutusel ptk 2 (\enquote{RNG seeme} = juhuslike arvude generaator).
- **ROC** — juba nimekirjas, kuid selgitus võib olla täpsem (vt kriitika).
- **SLURM** — viidatud projekti kontekstis (HPC ülesannete planeerija); kontrollida, kas tekstis tegelikult esineb (CLAUDE.md mainib, mitte tingimata thesis text — kontrollituna esineb \enquote{HPC-treeningu} viidetes).
- **Speech Commands** — kasutusel ptk 1 ja 2 avaliku andmestikuna.
- **SpecAugment** — kasutusel ptk 1 §1.6.4 ja ptk 2; treeningaegne regulariseerimistehnika.
- **SRAM** — kasutusel ptk 2 (ESP32-S3 mälupiirang).
- **SSML** — kasutusel ptk 2 Neurokõne kõnesünteesi märgistuskeelena.
- **STT** — juba nimekirjas, kasutusel.
- **SVDF** — kasutusel ptk 1 §1.6 mudeli arhitektuuri ehituskivina.
- **Tensor Arena / tensor\_arena** — kasutusel ptk 1 ja 2 ESP32 töömälu kontekstis.
- **TFLite-Micro** — kasutusel ptk 2 mikrokontrolleri-poolse interpretaatorina; eraldi \enquote{TFLite}-st.
- **TTS** — juba nimekirjas, kasutusel.
- **UMUX-Lite** — kasutusel ptk 1 §1.7 kasutatavuse skaalana.
- **UV (usaldusvahemik)** — eestikeelne lühend kasutusel ptk 2 kõikides tabelites; ei ole rahvusvaheline akronüüm, kuid lugejale vajalik.
- **VAD** — kasutusel ptk 1 §2.6.1 (\emph{voice activity detection}).
- **voice\_assistant} — kasutusel sissejuhatuses, kokkuvõttes, ülesandepüstituses Home Assistanti liidesena.
- **VOiCES** — kasutusel ptk 1 ja 2 taustaheli korpusena.
- **WAV** — kasutusel ptk 1 §1.7 ja ptk 2 audiofaili vorminguna.
- **wake word / äratussõna** — kogu töö keskne mõiste; eestikeelne vaste vajab esmamääratlust nimekirjas.
- **Wilsoni usaldusvahemik / Poissoni-Garwoodi vahemik / kolmereegel** — kasutusel ptk 1 ja 2; statistilised mõisted.
- **Wyoming protokoll** — viidatud projekti kontekstis (CLAUDE.md), kontrollida lõputöö tekstis; käesolevas auditis põhitekstis ei tuvastatud, seega ei pakuta lisamiseks ilma täiendava kontrollita.
- **XML** — kasutusel ptk 2 (Neurokõne SSML/XML-märgendid).
- **XTTS** — kasutusel ptk 2 ja 3 sünteetiliste hääleklooni positiivide allikana.

### Kriitika olemasolevate kirjete kohta

- **FRR}: praeguses nimekirjas seisab \enquote{Valetagasiloikamise määr} --- see on kirjavea-kahtlusega tehiskeelend, mille tähendus jääb hägusaks. Õige termin on \enquote{valetagasilükkamise määr} või \enquote{valenegatiivsuse määr}; selgitus peaks ka avama, et tegemist on osakaaluga tegelikest äratussõna juhtudest, mis jäävad tabamata.
- **FAPH**: olemasolev tõlge \enquote{Valetriggerid tunni kohta} sisaldab toorlaenu \enquote{trigger}. Asendada \enquote{valeaktiveeringud} või \enquote{valevallandumised} (sama termin, mida töö ise pidevalt kasutab).
- **ROC**: \enquote{Lävekõver} ei ole tavakasutuses kinnistunud termin ja jätab lugejale ähmase pildi. Avada täpsemalt: kõver, mis kuvab tundlikkuse ja valepositiivsuse suhte erinevatel otsustuslävedel.
- **TFLite}: praegu kirjeldatud kui \enquote{mudelivorming servaseadmetele}. Täpsem oleks \enquote{TensorFlow'i järeldusraamistik ja mudelivorming servaseadmetele}, kuna TFLite ei ole ainult vorming.
- **API**: kirje on tehniliselt korrektne, kuid kontrollida tuleks, kas lühend tegelikult auditeeritavas tekstis esineb (käesolevas auditis ASR-API ega muu API-viidet põhitekstis ei tuvastatud --- kui see jääb tekstist välja, võib ka selle eemaldada).

## 2. Parandatud \enquote{Lühendid ja mõisted}

*(Tähestikulises järjekorras. Lühendite puhul: lühend -- täispikk kirjapilt (ingliskeelne tõlge \emph{kursiivis}, kui asjakohane) ja selgitus. Mõistete puhul: mõiste -- selgitus. Selgitused on hoitud 1--2 lausesse.)*

- **API** -- Rakendusliides (\emph{Application Programming Interface}). Tarkvarakomponendi avalik kutseliides, mille kaudu teised programmid sellega suhtlevad. *(Säilitada üksnes juhul, kui lõplikus tekstis esineb; vastasel juhul eemaldada.)*
- **ASR** -- Automaatne kõnetuvastus (\emph{Automatic Speech Recognition}). Kõne sisu tekstiks teisendamise tehnoloogia, mille korpuseid käesolevas töös kasutatakse äratussõna negatiiv\-andmetena.
- **AUC** -- Kõveraalune pindala (\emph{Area Under the Curve}). ROC-kõvera all olev pindala; üks koondnäitaja klassifikaatori kvaliteedist üle kõikide otsustuslävede.
- **CC-BY-SA 3.0** -- Creative Commonsi litsents \enquote{Autorile viidatud, jagatav samadel tingimustel} versioon 3.0; lubab korpuse vaba taaskasutust eeldusel, et tuletatud teos jagatakse sama litsentsi all.
- **Common Voice (ET)** -- Mozilla avatud kõnekorpus; \enquote{ET} tähistab eestikeelset alamkorpust, mida käesolev töö kasutab nii treeningu negatiivide kui ka taustaheli FAPH-i mõõtmise allikana.
- **DET-kõver** -- Tuvastusvigade kompromissikõver (\emph{Detection Error Tradeoff}). Logaritmilises skaalas joonistatud valeaktiveeringute ja valenegatiivide vaheline kompromissikõver, mida kasutatakse mudeliperekondade võrdlemiseks üle lävede vahemiku.
- **DiPCo** -- Avalik mitmemikrofoniline kodusalvestuste korpus (\emph{Dinner Party Corpus}), mida käesolev töö kasutab taustaheli FAPH-i mõõtmiseks.
- **DNN-HMM** -- Sügava närvivõrgu ja peidetud Markovi mudeli hübriid (\emph{Deep Neural Network -- Hidden Markov Model}). Klassikaline äratussõna ja kõnetuvastuse arhitektuur, millele Apple'i \enquote{Hey Siri} algupärane treeningskeem tugineb.
- **DNN** -- Sügav närvivõrk (\emph{Deep Neural Network}). Mitmekihiline närvivõrk, mille raamistikus käesoleva töö kõik äratussõna mudelid on treenitud.
- **ESP32-S3** -- Espressifi madala energiatarbega kahetuumaline mikrokontroller; käesoleva töö sihtplatvorm äratussõna mudeli juurutamiseks.
- **ESP32-S3-Korvo-2 (Korvo-2)** -- Espressifi referentsarendusplaat ESP32-S3 baasil koos mikrofonimassiivi ja heliesitusega; töös kasutatav peamine demonstreeriv riistvara.
- **ESPHome** -- Avatud lähtekoodiga püsivara-ehitamise raamistik, mis pakub valmis Home Assistanti integratsiooni ja äratussõna komponendi (\texttt{voice\_assistant}) ESP-mikrokontrolleritele.
- **ETIS** -- Eesti Teadusinfosüsteem; siin viidatud sealse lõputööde registri kontekstis varem avaldatud eestikeelse äratussõna- või KWS-töö otsinguruumina.
- **FAPH** -- Valeaktiveeringud tunnis (\emph{False Accepts Per Hour}). Pidevas helivoo režiimis registreeritud valede äratussõna-vallandumiste keskmine arv tunnis; käesoleva töö peamine valeaktiveerimise mõõdik. Töös eristatakse nelja varianti (raamistiku, skriptitud taasmängu, välitingimuste, kasutajatesti taasmängu) erineva loendusreegli ja runtime-loogika tõttu.
- **FA/h** -- Sünonüüm FAPH-ile (\emph{false accepts per hour}); käesolevas töös kasutatakse mõlemat kirjapilti samas tähenduses.
- **FPR** -- Valepositiivsete määr (\emph{False Positive Rate}). Osakaal negatiivseteks märgistatud klippidest, mida mudel valesti äratussõnaks tuvastab; mõõdetakse klipi-tasemel, mitte ajaühiku kohta.
- **FRR** -- Valenegatiivsuse määr (\emph{False Rejection Rate}). Osakaal tegelikest äratussõna ütlustest, mida mudel ei suuda tuvastada.
- **Hold-out komplekt (kõrvalejäetud komplekt)** -- Sõltumatu hindamiskomplekt, mille klipid ei ole treeningus ega valideerimises kasutatud; käesolevas töös keskne andmelekke vältimise vahend.
- **Home Assistant** -- Avatud lähtekoodiga lokaalne kodu\-automaatika platvorm, millega äratussõna mudel töös integreeritakse \texttt{voice\_assistant} liidese kaudu.
- **HPC** -- Kõrgjõudlusega arvutuste keskkond (\emph{High-Performance Computing}); käesoleva töö mudeleid treeniti TalTechi ühisarvutusklastris.
- **INT8** -- 8-bitine täisarvuline esitlus (\emph{8-bit integer}). Kvantiseeritud mudelis kasutatav numbrivorming, kus nii kaalud kui aktivatsioonid on 8-bitised täisarvud, võimaldades tõhusat järeldamist mikrokontrolleril.
- **IoT** -- Asjade internet (\emph{Internet of Things}). Igapäeva\-seadmete võrgustamine andmevahetuseks; siin nutikodu seadmete üldnimetajana. *(Säilitada üksnes juhul, kui lõplikus tekstis esineb.)*
- **KB / MB** -- Kilobait / megabait; mälumahu suurusühikud (1\,KB = 1024 baiti).
- **Kiirkirjutaja** -- Avatud lähtekoodiga reaalajas eestikeelse kõnetuvastuse mudel ja tööriist (\url{https://github.com/alumae/kiirkirjutaja}); käesolevas töös toetav komponent terviklahenduse valideerimiseks.
- **kratt CLI** -- Käesoleva töö raames välja töötatud käsureatööriista pere (\texttt{kratt user-test}, \texttt{kratt validate-user-test}, \texttt{kratt replay-user-test}, \texttt{kratt summarize-user-test}), mis korraldab kasutajatestide salvestust, valideerimist ja taasesitust.
- **KWS} -- Märksõnatuvastus (\emph{Keyword Spotting}). Kõneuuringu valdkond, mis tegeleb lühikeste sõnade või fraaside tuvastamisega pidevast helivoogust; äratussõna tuvastus on KWS-i alamharu.
- **mel-spektrogramm} -- Inimkuulmise tundlikkust matkiv mel-skaalal sageduskaartega spektrogramm; käesoleva töö mudelite sisendvorming.
- **microWakeWord** -- Avatud lähtekoodiga TensorFlow-põhine treeningraamistik, mis on suunatud mikrokontrolleri-mahuliste äratussõna mudelite treenimisele ja TFLite-Micro vormingusse eksportimisele.
- **MISP Challenge** -- Mandariini\-keelne avalik äratussõna ja kõnetuvastuse võistlus (\emph{Multimodal Information based Speech Processing}), mille korraldajad rõhutavad reaalsete elukeskkondade salvestuste kasutamist; käesolev töö viitab sellele kui näitele võrdlusaluste ja kasutusolukorra lõhe ületamise pingutusest.
- **MixedNet / MixedConv plokk** -- microWakeWord raamistiku vaikearhitektuur, mis koosneb mitme tuumasuurusega ajalistest süvakonvolutsiooni- ja punktkonvolutsioonikihtidest (MixedConv plokid); võimaldab suurt vastuvõtuvälja väikese parameetriarvu juures.
- **MUSAN** -- Avalik müra-, muusika- ja kõnekorpus, mida kasutatakse äratussõna mudelite negatiivsete ja taustaheli näidete allikana.
- **Neurokõne** -- Tartu Ülikooli ja TalTechi koostöös arendatud eestikeelne kõnesüntesaator; käesolevas töös sünteetiliste positiivsete näidete üks allikas.
- **ONNX** -- Avatud närvivõrgu vahetusvorming (\emph{Open Neural Network Exchange}); openWakeWord'i järeldamise sihtformaat Raspberry Pi klassi seadmetel.
- **openWakeWord** -- Avatud lähtekoodiga äratussõna treenimise ja järeldamise raamistik, mis on suunatud Raspberry Pi klassi hostidele ja toimib käesoleva töö võrdlusraamistikuna.
- **Picovoice Porcupine** -- Suletud lähtekoodiga kommertsiaalne äratussõna lahendus, mida kasutatakse käesolevas töös kontekstuaalse võrdluspunktina, kuid jäetakse otsesest tehnilisest võrdlusest välja, kuna see ei toeta eesti keelt ega kasutaja\-poolset mudelitreeningut.
- **Poissoni-Garwoodi vahemik** -- Täpne usaldusvahemik harvade sündmuste loendamiseks ajaühiku kohta; kasutatakse FAPH-i punkthinnangu juures.
- **RMS** -- Ruutkeskmine (\emph{Root Mean Square}); audiosignaali keskmise energiataseme näitaja, mille abil valideeritakse, kas salvestatud kasutajatesti klipi tase on piisav.
- **RNG} -- Juhuslike arvude generaator (\emph{Random Number Generator}); seemnel põhinev pseudojuhuslik järjestus, mis tagab andmevaliku reprodutseeritavuse.
- **ROC-kõver** -- Tuvastusoperatsioonikõver (\emph{Receiver Operating Characteristic}). Joonistab klassifikaatori tundlikkuse ja valepositiivsuse suhte erinevatel otsustuslävedel; võimaldab võrrelda mudelite kompromisse ilma ühte läve fikseerimata.
- **SLURM** -- Avatud lähtekoodiga klastri-ülesannete planeerija (\emph{Simple Linux Utility for Resource Management}); kasutatakse TalTechi HPC keskkonnas treeningutööde esitamiseks.
- **Speech Commands** -- Google'i avalik 35-sõnaline lühisõnade kõnekorpus, mida käesolev töö kasutab treeningu- ja hindamistoru valideerimiseks äratussõnaga \texttt{marvin}.
- **SpecAugment** -- Treeningaegne regulariseerimistehnika, mis maskeerib spektrogrammis juhuslikke aja- ja sagedusribasid, et vähendada ülesobitumist.
- **SRAM** -- Staatiline muutmälu (\emph{Static Random-Access Memory}); ESP32-S3 töömälu, mis piirab tensor\_arena ja äratussõna mudeli järeldamise käigus kasutatava puhvri suurust.
- **SSML** -- Kõnesünteesi märgistuskeel (\emph{Speech Synthesis Markup Language}); XML-põhine vorming, millega juhitakse kõnesünteesi prosoodiat ja hääldust.
- **STT** -- Kõne tekstiks teisendamine (\emph{Speech to Text}); sama valdkond mis ASR, kuid süsteemi-vaates. Käesolevas töös kasutatakse mõisteid läbisegi.
- **SVDF kiht** -- Singulaarväärtuste\-lahutusel põhinev filterkiht (\emph{Singular Value Decomposition Filter}); MixedNet arhitektuuri ehituskivi, mis faktoriseerib aja- ja sageduse töötluse eraldi operatsioonideks.
- **Tensor Arena (\texttt{tensor\_arena})** -- TFLite-Micro interpretaatori töömälu\-puhver, kuhu paigutatakse mudeli vahetulemused järeldamise ajal; käesolevas töös oluline ESP32-S3 mahupiirangute arvutamisel.
- **TFLite** -- TensorFlow Lite; kerge järeldusraamistik ja mudelivorming serva- ja mobiili\-seadmetele.
- **TFLite-Micro** -- TFLite alamharu mikrokontrolleritele, mille interpretaator töötab ilma operatsioonisüsteemita ja kasutab käsitsi etteantud tensor\_arena-puhvrit.
- **TTS** -- Teksti kõneks teisendamine (\emph{Text to Speech}); käesolevas töös kõnesünteesi kasutatakse positiivsete treeningnäidete genereerimiseks.
- **UMUX-Lite** -- Lühike valideeritud kasutatavuse skaala (\emph{Usability Metric for User Experience -- Lite}); kahe väitega kiirhinnang süsteemi kasutatavusele kasutajatesti lõpus.
- **UV} -- Usaldusvahemik; statistiline vahemik, mis hindab punktiväärtuse ebakindlust antud usaldustasemel (käesolevas töös 95\%). Klipi-tasemel kasutatakse Wilsoni skoorimeetodit, FAPH-i juures Poissoni-Garwoodi vahemikku.
- **VAD** -- Häältuvastus (\emph{Voice Activity Detection}); eelfilter, mis otsustab, kas helivoos esineb kõnet, et vältida pideva järeldamise kulu.
- **\texttt{voice\_assistant}** -- Home Assistanti / ESPHome komponent, mis seob mikrokontrolleri-äratussõna seadme keskse hääljuhtimise toruga.
- **VOiCES** -- Avalik kaugkõne ja ruumiakustika andmestik, mida kasutatakse äratussõna negatiivide ja taustaheli realistlikumaks katmiseks.
- **wake word (äratussõna)** -- Lühike fraas, millega kasutaja annab hääljuhtimisseadmele märku, et järgnev kõne on käsk; käesolevas töös fraas \enquote{Kuule Kratt}.
- **WAV** -- Pakkimata audiofaili vorming (\emph{Waveform Audio File Format}); käesolevas töös 16\,kHz mono salvestuste kandja.
- **Wilsoni skoorivahemik** -- Binaarsete proportsioonide jaoks soovitatav 95\% usaldusvahemik, mis käitub paremini kui normaaljaotuse lähend väikese valimi ja äärmuslike osakaalude juures.
- **Wyoming protokoll** -- Avatud lähtekoodiga sõnumiprotokoll Home Assistanti hääljuhtimise komponentide vahel. *(Säilitada üksnes juhul, kui lõplikus tekstis tõepoolest viidatakse; auditi käigus käesolevas tekstis seda ei tuvastatud.)*
- **XML** -- Laiendatav märgistuskeel (\emph{Extensible Markup Language}); käesolevas töös viidatud SSML-i alusvorminguna Neurokõne sünteesi väljundis.
- **XTTS** -- Avatud lähtekoodiga mitmekeelne hääleklooni\-süsteem (\emph{Cross-lingual Text-to-Speech}); käesolevas töös kasutatud sünteetiliste positiivsete näidete ja kontrollitud unseen-kõneleja klippide allikana.

---

### Märkused tööprotsessi kohta

- **Allikate kaetus**: audit hõlmas faile \texttt{introduction.tex}, \texttt{first\_chapter.tex}, \texttt{second\_chapter.tex}, \texttt{third\_chapter.tex}, \texttt{summary.tex}, \texttt{abstract-estonian.tex}, \texttt{abstract-english.tex}, \texttt{ylesandepystitus.tex} ja olemasolev \texttt{terms\_abbreviations.tex}.
- **Mittetuvastatud kontekstid}: kui \texttt{Wyoming}, \texttt{SLURM} või \texttt{API} ei esine põhitekstis tegelikult, soovitatakse need välja jätta; sõnastikku lisatakse ainult tegelikult tekstis esinevad lühendid.
- **Stiilireeglid}: vältisin toorlaene (\emph{trigger} $\rightarrow$ \emph{vallandumine}; \emph{benchmark} on jäetud, kuna selle eestikeelne vaste \enquote{võrdlusalus} esineb juba töös; \emph{cutoff} $\rightarrow$ \emph{lävi}). Inglise terminid on antud kursiivis ainult lühendi täiskirjapildis ning peamine selgitus on eestikeelne.
- **Sihtgrupp}: selgitused on hoitud lühikesed ja keskenduvad sellele, mis lugejal töö lugemiseks vaja teada, mitte termini täielikule akadeemilisele definitsioonile.
