---
source_prompt: /Users/mattias/Downloads/loputoo_viibad_2026_04_28-2/02_Ülesandepüstitus/Ülesandepüstituse_genereerimine.txt
prompt_type: generative
generated: 2026-05-07
---

# Bakalaureusetöö ülesandepüstitus

> **Töö esialgne pealkiri:** Eestikeelse äratussõna tuvastus piiratud ressursiga nutikodu mikrokontrolleril
> **Üliõpilane:** Mattias Linholm
> **Juhendaja:** [juhendaja nimi sisendmaterjalides ei sisaldu — täita lõplikus dokumendis]

## Ülesandepüstitus

### Taust

Hääljuhtimine on muutunud üheks valdavaks viisiks nutikoduga suhtlemiseks ning lahenduste raskuskese on viimastel aastatel nihkunud serveripoolsest ja pilvepõhisest töötlusest serva- ja seadmesisese arvutuse poole, kus kogu kõnetöötlustoru käib lokaalselt kasutaja füüsilises keskkonnas [1, 2]. Sellise toru avab nn äratussõna (ingl \emph{wake word}) tuvastamine: pidev madala energiatarbega detektor, mis ärkab üksnes etteantud lühifraasi kuuldes ja annab seejärel sõna kõnetuvastusele ning käsuparserile [3]. Eesti keele jaoks on suuremad kõnetehnoloogia komponendid juba olemas — laiapõhjalised kõnekorpused ning lokaalselt jooksutatav reaalajas kõnetuvastus Kiirkirjutaja näol [4, 5] —, kuid äratussõna tuvastust käesoleva töö koostamise hetkel ei toeta ei avatud lähtekoodiga raamistik \texttt{openWakeWord} ega lähim suletud lähtekoodiga võrdluspunkt Picovoice Porcupine [3, 6]. Mikrokontrolleri-klassi äratussõna tuvastusele on samas rahvusvaheliselt olemas konkreetsed metoodilised tugipunktid: nii Speech Commands tüüpi võrdlusalused kui ka avatud raamistik \texttt{microWakeWord}, mis on suunatud just ESP32-klassi sihtseadmetele [2, 7]. Eesti keele ja mikrokontrolleri-klassi riistvara ristumine on seetõttu hõivamata vahepiirkond, kus üldised tehnoloogiakomponendid on olemas, kuid keelepõhine integratsioon puudub.

### Motivatsioon

Kasutaja vaatest on äratussõna kogu hääljuhtimise esimene filter: kui see filter pidevalt valesti vallandub või vastupidi, jätab kasutaja ütluse vahele, mõjutab see otseselt kogu süsteemi usaldusväärsust, sõltumata sellest, kui hea on järgnev kõnetuvastus või käsutõlgendus [3]. Eesti keelt kõnelev kasutaja peab täna valima kahe kompromissi vahel: kasutada võõrkeelset, sageli ingliskeelset äratussõna ühes pilvepõhiste hääleabilistega või loobuda hääljuhtimisest täielikult. Privaatsuse, andmesuveräänsuse ja Euroopa Liidu isikuandmete kaitse üldmääruse kontekstis on lokaalsel, ilma pilve sõltuvuseta töötaval häältorul eraldi avalik väärtus, eriti kodukeskkonnas, kus mikrofon kuulab pidevalt. Lisaks puudub eesti keele kogukonnal praegu avalik ja reprodutseeritav metoodikabaas, mille najal järgmised üliõpilased ja arendajad saaksid eestikeelseid äratussõnamudeleid süstemaatiliselt arendada ja võrrelda. Just praegu on mõistlik selle lüngaga tegeleda, sest mikrokontrolleritele suunatud avatud lähtekoodiga raamistikud on jõudnud küpsuseni, mis lubab piiratud ressursiga koolitööna jõuda terviksüsteemini, mitte üksnes prototüüpse komponendini [2, 7].

### Probleemipüstitus

Eestikeelse äratussõna lokaalse tuvastuse probleem ei taandu üksnes mudeli treenimisele. Töö ettevalmistuse käigus selgus mitu omavahel põimunud puudujääki, mis senistel projektidel on jäänud süstemaatiliselt katmata. Esiteks ei ole eesti keelele suunatud tervet \emph{toru} (andmete ettevalmistus, treenimine, kvantiseerimine, seadmesse paigaldamine ja hindamine) avalikult ja reprodutseeritavalt dokumenteeritud, mistõttu iga uus üritus alustab nullist. Teiseks ei piisa traditsioonilisest klipi-tasemel täpsuse ja valepositiivsete näitamisest: nutikodu kasutaja jaoks loeb pidev helivoo režiim, kus mõõta tuleb valevallandumiste arvu \emph{tunnis} (FAPH) pikemal taustaheli korpusel, mitte protsenti lühikeste klippide hulgas [3]. Kolmandaks toob piiratud andmestik kaasa kvalitatiivselt uue riski: mudel võib õppida ära mitte sihtfraasi, vaid sellega korreleeruvad lühiteed (näiteks ainult prefiksi „Kuule", salvestuskanali eripära või sünteetilise kõne tämbri), ilma et see klassikaliste mõõdikute järgi nähtavale tuleks. Tulemus on, et ilma süstemaatilise hindamis- ja audeerimisprotokollita ei saa väita, et antud mudel on koduses keskkonnas kasutuskõlblik, isegi kui võrdlusaluste skoorid on muljetavaldavad. Töö ülesanne on see lünk täita: luua eestikeelse äratussõna „Kuule Kratt" jaoks reprodutseeritav arendus- ja hindamistoru ning tõestada, et see toru tuvastab eelnimetatud lühiteed ja kompromissid enne juurutusotsuse langetamist.

### Lahenduse idee ja keerukus

Lahenduse keskmes on projekt „Kratt": kahesõnaline eestikeelne äratusfraas „Kuule Kratt", mille jaoks treenitakse \texttt{microWakeWord} raamistikus mikrokontrolleri sihtformaadile (TensorFlow Lite, INT8 kvantiseerimine) sobiv MixedNet-arhitektuuriga mudel ja paigaldatakse see ESPHome'i \texttt{voice\_assistant} liidese kaudu ESP32-S3 klassi seadmesse, mis suhtleb Home Assistanti hääljuhtimise ahelaga [2, 7, 8]. Voogedastav järeldamine peab toimuma kaaderhaaval, sisemise olekuga ja konstantse arvutuskuluga, et seade saaks pidevalt kuulata. Võrdlusraamistikuna kaasatakse \texttt{openWakeWord}, mis sihib pigem Raspberry Pi klassi hosti kui mikrokontrollerit ja võimaldab seetõttu hinnata raamistikuvaliku põhjendatust nelja telje lõikes: treenimise praktiline keerukus, mudeli kvaliteet, integreeritavus ja laiendatavus eesti keelele [3].

Tehnilised väljakutsed jagunevad kolme kihti. \emph{Andmekiht} nõuab, et väikse keele jaoks tuleb eristada kolme andmeliiki — positiivsed klipid, negatiivsed klipid ja taustaheli — ning kombineerida olemasolevaid avalikke korpusi (\texttt{Speech Commands}, \texttt{MUSAN}, \texttt{VOiCES}, \texttt{Common Voice} eesti keele osa) sünteetilise kõnega, hoides samas ranget treening- ja testandmete eraldatust ning kontrollides andmelekke riski [9, 10, 11, 12]. \emph{Mudelikiht} nõuab MixedNet-arhitektuuri konfigureerimist (tuumade suurused, MixedConv plokid, residuaalühendused, SpecAugment regulariseerimine, kontekstiaken, INT8 kvantiseerimine) selliselt, et lõpptulemus mahuks ESP32-S3 mälupiirangutesse ja jookseks reaalajas, säilitades samas kahesilbilise eestikeelse fraasi foneetilise eristusvõime [13]. \emph{Hindamiskiht} nõuab, et lisaks tavapärasele klipi-tasemel tuvastamismäärale ja valepositiivsete määrale tuleb defineerida eraldiseisev FAPH-i loendusreegel (raamistiku-sisene, skriptitud taasmäng, välitingimused, kasutajatesti taasmäng) ning lugeda iga raporteeritud arvuga kaasa Wilsoni või Poissoni-Garwoodi 95\% usaldusvahemik, et üksiku punkthinnangu varieeruvust mitte alahinnata [14, 15]. Just hindamiskihi distsipliini puudumine on kirjanduses tunnistatud üheks äratussõna valdkonna laiemaks reprodutseeritavuse auguks [3].

### Teaduslik uudsus ja kasu

Töö teaduslik uudsus on kahetasandiline. Praktilisel tasandil on tegemist esimese avalikult dokumenteeritud lokaalse äratussõna lahendusega eesti keele jaoks, mis hõlmab tervet ahelat alates andmete ettevalmistusest kuni Home Assistanti integratsioonini ja mille kõik komponendid on reprodutseeritavad avatud lähtekoodiga vahenditega. Metoodilisel tasandil — ja just seda osa peetakse käesoleva töö pikemaajaliseks panuseks — pakub töö välja \emph{väikese ressursiga keele kohaliku äratussõna mitmemõõtmelise valideerimise protokolli}: minimaalse kriteeriumide kogumi (sõltumatu taustaheli FAPH, päriskõnelejate tuvastamismäär, TTS-allikate tuvastamismäär, sarnaste negatiivnäidete FPR ning fraasistruktuuri kontrollivad prefiksi-, üksiku sõna, pööratud järjekorra ja segiajamise mõõdikud), mis on otseselt ülekantav teiste väikeste keeleruumide projektidele. Töös fikseeritakse ka kolm kvalitatiivselt erinevat valideerimise „ringi" — andmelekke kontroll, positiivse klassi sisuline audit ja kontrollpunkti komposiitne valikukriteerium —, mis mõõdavad konkreetseid riske, mitte üksnes mudeli üldist headust.

Praktilist kasu saavad sellest mitu rühma. Eesti keelt kõnelevad nutikodu kasutajad saavad esimese terviklikult emakeelse, lokaalselt töötava ja privaatsust säilitava hääljuhtimise eelfiltri. TalTechi ning laiema eesti kõnetehnoloogia kogukond saab avaliku metoodikabaasi, mille najal saab järgmistes töödes võrrelda mudeleid, hindamisprotokolle ja andmestikuvariante samaväärsetel alustel. Avatum nutikodu kogukond (Home Assistant, ESPHome) saab konkreetse näite eesti keelt toetavast äratussõna mudelist ja juhtumiuuringu sellest, kuidas väikese keele tugi avatud lähtekoodiga raamistikele lisada. Lisaks omab metoodiline panus väärtust ka teiste väikeste keelte (nt läti, soome murded, väiksemad uurali keeled) äratussõnaprojektide jaoks, mille väljakutsete struktuur on sarnane.

### Valideerimine

Lahenduse valideerimine on kolmekihiline ja lähtub töös kirjeldatud hindamisprotokollist. \emph{Esimene kiht — kontrollkatse —} valideerib treening- ja hindamistoru avaliku \texttt{Speech Commands} korpuse \texttt{marvin} sihtsõnaga, kontrollitud baasülesande peal, kus on võimalik veenduda, et kogu otsast lõpuni ahel (treenimine, eksport, evaluatsioon) töötab enne eesti keele andmestikule liikumist [9]. \emph{Teine kiht — tehniline mõõtmine —} hõlmab eestikeelse mudeli mõõtmist sõltumatutel kõrvalejäetud testikomplektidel, tagades treeningu- ja testikomplektide eraldatuse automatiseeritud kontrolliga, ning raporteerib korraga klipi-tasemel tuvastamismäära, sarnaste negatiivnäidete FPR-i, prefiksi- ja segiajamismõõdikud ning pidevvoo FAPH-i koos täpsete usaldusvahemikega [14, 15]. Operatsiooniliseks sihiks on FAPH < 1 pikemal taustaheli korpusel ja lähikõne tuvastamismäär ≥ 0,95; need on käesoleva töö projekti-spetsiifilised otsustuskriteeriumid, mis on kalibreeritud avatud raamistike soovituslike sihtväärtuste järgi (avalikes vastandlikes võrdlusalustes alates < 0,5 FA/h kuni 1 FA / 10 h), mitte vastastikku eelretsenseeritud universaalsed standardid [3, 6]. \emph{Kolmas kiht — kasutajapõhine valideerimine —} on planeeritud lühike, umbes 10-minutiline ühe-nutipirni stsenaarium 20–30 osalejaga, kus aktiivne süsteem on enne kogumist külmutatud ning iga sessioon annab nii kontrollitud äratussõna ütlused, sihtfraasiga foneetiliselt sarnased negatiivfraasid kui ka skriptitud nutikodu käsud. Kõik kogutud kasutajatesti helid taasesitatakse hiljem identsete külmutatud lävedega mitme varimudeli peal, et mudelivõrdlus toimuks identse helisisendi peal. Subjektiivse rahulolu jaoks kasutatakse lühikest sessioonijärgset küsimustikku ja, kui ajapiir lubab, valideeritud lühiskaalat UMUX-Lite [16]. Saadud andmed käsitletakse esmalt hindamis-, mitte treeningandmestikuna, et säilitada hindamisprotokolli sõltumatus.

Kokkuvõttes peavad valideerimise tulemusena saama põhjendatud vastused töö neljale alamküsimusele: kas treeningu- ja hindamistoru on enne eesti keele juurde liikumist tehniliselt usaldusväärne, milline on positiivsete, negatiivsete ja taustaheli-andmete eristatud roll mudeli kvaliteedi hindamisel, kas andmestikust tulenevad probleemid on tehnilistest piirangutest eristatavad ning kas treenitud mudel saavutab eestikeelsel taustaheli korpusel pidevvoo FAPH < 1 ja lähikõne tuvastamismäära ≥ 0,95 sihi.

## Kasutatud allikad

[1] Home Assistant, „Voice control with Home Assistant", võrguteavik. Saadaval: \url{https://www.home-assistant.io/voice_control/}.

[2] K. Ahrendt, „microWakeWord: training framework for on-device wake-word detection on microcontrollers", võrguteavik. Saadaval: \url{https://github.com/kahrendt/microWakeWord}.

[3] I. López-Espejo, Z.-H. Tan, J. H. L. Hansen ja J. Jensen, „Deep Spoken Keyword Spotting: An Overview", \emph{IEEE Access}, kd 10, lk 4169–4199, 2022.

[4] T. Alumäe \emph{et al.}, „Estonian speech recognition data and models at TalTech", võrguteavik (2024).

[5] T. Alumäe, „Kiirkirjutaja: Real-time Estonian Speech Recognition", võrguteavik. Saadaval: \url{https://github.com/alumae/kiirkirjutaja}.

[6] Picovoice, „Porcupine Wake Word Engine: benchmarks and supported languages", võrguteavik. Saadaval: \url{https://picovoice.ai/}.

[7] D. Scripka, „openWakeWord: an open-source wake-word detection framework", võrguteavik. Saadaval: \url{https://github.com/dscripka/openWakeWord}.

[8] ESPHome, „voice\_assistant component documentation", võrguteavik. Saadaval: \url{https://esphome.io/}.

[9] P. Warden, „Speech Commands: A Dataset for Limited-Vocabulary Speech Recognition", \emph{arXiv preprint}, arXiv:1804.03209, 2018.

[10] D. Snyder, G. Chen ja D. Povey, „MUSAN: A Music, Speech, and Noise Corpus", \emph{arXiv preprint}, arXiv:1510.08484, 2015.

[11] C. Richey \emph{et al.}, „Voices Obscured in Complex Environmental Settings (VOiCES) Corpus", \emph{Interspeech}, 2018.

[12] R. Ardila \emph{et al.}, „Common Voice: A Massively-Multilingual Speech Corpus", \emph{LREC}, 2020.

[13] B. Kim \emph{et al.}, „Broadcasted Residual Learning for Efficient Keyword Spotting" (BC-ResNet), \emph{Interspeech}, 2021.

[14] E. B. Wilson, „Probable Inference, the Law of Succession, and Statistical Inference", \emph{Journal of the American Statistical Association}, kd 22, nr 158, lk 209–212, 1927.

[15] F. Garwood, „Fiducial Limits for the Poisson Distribution", \emph{Biometrika}, kd 28, nr 3/4, lk 437–442, 1936.

[16] J. R. Lewis, B. S. Utesch ja D. E. Maher, „UMUX-LITE: When There's No Time for the SUS", \emph{CHI}, 2013.

---

**Märkus genereerimise kohta.** Käesolev ülesandepüstitus on koostatud lähtuvalt sisendmaterjalidest (introduction.tex, first\_chapter.tex, second\_chapter.tex, third\_chapter.tex, summary.tex, abstract-estonian.tex, abstract-english.tex ja olemasolev ylesandepystitus.tex). Juhendaja nimi sisendmaterjalides ei kajastunud — see tuleb täita lõpliku dokumendi vormistamisel. Olemasoleva \texttt{ylesandepystitus.tex} võrdluseks vaadates on käesolev variant põhjalikum (lisab tausta, motivatsiooni, probleemipüstituse, lahenduse keerukuse jaotuse, teadusliku uudsuse mitmetasandilise põhjenduse ja struktureeritud valideerimise) ning järgib täpsemalt prompti nõutud kuueosalist loogilist ülesehitust. Allikate nimekiri on harmoneeritud töö enda kasutatud viidetega ning täidab nõude vähemalt viie asjakohase allika kohta.
