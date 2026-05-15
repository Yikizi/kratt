---
source_prompt: 04_Kontrollimine/Konkreetsed_vead/Sisu/Faktivead_ja_loogikavead.txt
prompt_type: evaluative
generated: 2026-05-07
---

# Faktivigade ja loogikavigade audit

Skeptiline lähilugemine kuue toimiku peale: `introduction.tex`, `first_chapter.tex` (metoodika), `second_chapter.tex` (osaliselt — fail oli liiga mahukas, kasutati struktuurset ülevaadet ja viiteid teistes peatükkides), `third_chapter.tex` (arutelu), `summary.tex`, `abstract-estonian.tex`, `abstract-english.tex` ja `ylesandepystitus.tex`. Eraldi vaadati ka tagajärgi, mis tulenevad ülesandepüstituses kirjas olevast aastast (\Year — eeldatavasti 2026; töö kontekst on 2026-05) ja sellest tulenevatest ajalistest ankrutest.

Auditit on tehtud sisulise eksimuse, mitte stiili tasandil. Kus väide nõuaks tegelikku numbrit `second_chapter.tex` Tulemuste peatükist, on see selgelt märgitud ja jäetud lahtiseks (ei ole leiutatud).

---

## 1. Tuvastatud faktivead ja sisemised vastuolud

### 1.1 Vastuolu mudeli mahu ja "v16c" suuruse vahel
* **Vigane väide:** „Piloodi aktiivseks kandidaadiks valitud `v16c` kvantiseeritud TFLite-mudeli maht on 148\,KB; varasemad väiksemad mudelid olid umbes 57\,KB."
    * **Asukoht:** Metoodika ptk, §\ref{subsec:quantization} (`first_chapter.tex`, ridade ümbruses 127).
    * **Selgitus:** Sama peatüki §\ref{subsec:quantization} eelnevas lõigus (samuti võrdlusraamistiku peatükis, rida 21) viidatakse, et „mudeli ja `tensor_arena` (käesolevas töös 57\,KB ning ${\sim}107$\,KB koos töömäluga)". CLAUDE.md projektikontekst kinnitab, et microWakeWord-mudel on $\sim$56 KB. Kui aktiivne kandidaat (`v16c`) on tegelikult 148 KB, siis võrdlusraamistiku § ei tohiks viidata 57 KB-le kui „käesoleva töö" mudelile — see number kuulub varasematele versioonidele. Lugejale jääb mulje, et Metoodika kasutab kahte eri mudelit kahes naaberlõigus, ilma et seda eraldi välja öeldaks. Vajalik täpsustus: kumb on mälupiirangute peamine reeglistik, kas v6 või v16c.

### 1.2 Vastuolu „prognoosi suurusjärkude" arvus
* **Vigane väide:** „Esimene reaalajas test MacBook Pro sisemikrofoniga registreeris ${\sim}50$ valeaktiveeringut tunnis --- kahe kuuekoht\-numbrelise suurusjärgu erinevus prognoosist."
    * **Asukoht:** Arutelu, §\ref{sec:eval-evolution} → „Esimene ring — klipi-tasemeline FPR" (`third_chapter.tex`, rida 101).
    * **Selgitus:** „Kuuekohtnumbreline suurusjärk" on suurusjärk, mille väärtus on $10^6$. Kahe kuuekohtnumbrelise suurusjärgu vahe oleks $10^{12}$, mis on absurd. Kontekstis (FPR 0,4% vs $\sim$50 FAPH) ei ole need ka samades ühikutes (üks on osakaal, teine sagedus tunnis), seega „suurusjärkude erinevus" pole isegi arvuline. Tõenäoliselt on autor mõelnud „suurusjärgu erinevus prognoosist" (st umbes kümnekordne) või soovinud öelda, et prognoosist tunnistati saadav „peaaegu null", aga mõõdetud sai $\sim$50 — kuid „kuuekohtnumbreline" ei ole õige kvantifikaator. See on samaaegselt nii kirjavormiviga kui ka loogikaviga, sest järeldus „kahe kuuekohtnumbrelise suurusjärgu erinevus" ei ole faktiliselt põhjendatud.

### 1.3 Sissejuhatuses on FAPH-i siht- ja näiteväärtuste vahel sisemine pinge
* **Vigane väide:** „v6 mudel MacBook~Pro mikrofoni 40-minutilisel tavakõne testil FAPH~$\approx$~50 (vt §\ref{sec:cross-mic-asymmetry}). Hilisem ${\sim}99$~h Android-välikatse kinnitas sama tähelepanekut: madalaima klipipõhise valenegatiivsusega mudel ei olnud tingimata madalaima välivälja FAPH-iga (nt v6-residual 0{,}58~FAPH vs.\ expert-a parima üldise tasakaalu juures 2{,}79~FAPH 98{,}97~h jooksul, vt §\ref{sec:benchmark-gap})".
    * **Asukoht:** `introduction.tex`, rida 7.
    * **Selgitus:** Kahel järjestikusel lausel tugineb autor erinevatele FAPH-allikatele: 40-minutiline „tavakõne test" ja 99 h Android-välikatse. Esimene allikas (40 min) annab pelgalt 0,67 h pikkusele rajale FAPH $\approx$ 50, mis viitab vaid $\sim$33 sündmusele — see on liiga väike valim, et öelda, et Android-välikatse seda „kinnitas". Loogikaviga ei seisne mitte numbrites, vaid seoses: 40-minutiline laboritest ja 99 h välikatse mõõdavad eri asja (mikrofoni-tundlikkus tihedas kõnes vs reaalse-keskkonna baas), ega saa olla otseses kinnitamissuhtes ilma vahepealseid eeldusi nimetamata. Nõuab kas ümbersõnastust („sama suuna tähelepanek", mitte „kinnitas") või vahepealse argumendi lisamist.

### 1.4 Konsensushindamise FAPH = 0,79 — väide on järjepidev, aga ülemine piir on aus
* **Vigane väide:** „kahe mudeli konsensushindamisel saavutab süsteem Common~Voice ET kõrvalejäetud komplektil alla ühe valeaktiveeringu tunnis (konkreetselt $0{,}79$; vt ptk~\ref{chapter:results}, tabel~\ref{tab:expert-consensus})".
    * **Asukoht:** Arutelu, „Mida saab juba praegu väita" (`third_chapter.tex`, rida 143); samuti `summary.tex` rida 7.
    * **Selgitus:** See väide on faktiliselt järjepidev (kõik kolm faili ütlevad sama 0,79). Faktiviga on, et eestikeelses **abstract-estonian.tex**-is sama numbrit ei mainita üldse, samas kui **abstract-english.tex** mainib „substantially reduced ambient-speech FAPH". Sisemiselt ei ole vastuolu, kuid lugejale, kes võrdleb annotatsiooni ja kokkuvõtet, jääb mulje, et kokkuvõte on tugevam väide kui annotatsioon. Soovituslik: kas mõlemas mainida sama operatsioonipunkti (0,79) või mõlemast jätta välja. Praegu ei ole tegu otsese eksitusega, kuid see on **sisemine asümmeetria**, mida üldretsensent võib märgata.

### 1.5 Sünonüümide hägus kasutus: „residual" / „residual ühendus"
* **Vigane väide:** „v6-residual 0{,}58~FAPH" (introduction.tex), „v6-residual" konfiguratsioon (1,1,1,1) (first_chapter.tex §\ref{subsec:residual}).
    * **Asukoht:** mitmes kohas, sh sissejuhatus rida 7, metoodika rida 104.
    * **Selgitus:** Mudeli nimi sisaldab sõna „residual" inglise keeles, kuid eestikeelses tekstis on seda mõnel pool tõlgitud (residuaalühendused) ja mõnel pool jäetud algkujul (`v6-residual` mudelitähisena). Tegemist ei ole faktiveaga, vaid **mõisteühilduvuse riskiga**: lugejale, kes peatükki „Residuaalühendused" eraldi ei loe, jääb arusaamatuks, et `v6-residual` on lihtsalt v6 + residual\_connection=(1,1,1,1). Soovitus: esimesel kasutamisel sissejuhatuses lisada sulgudes lühike täpsustus.

### 1.6 „Esimene eestikeelne äratussõna mudel" vs „CLAUDE.md core contribution 1"
* **Vigane väide:** „töö üks peamisi panuseid ei ole \enquote{esimene eesti äratussõna mudel} (mis on tõsi, kuid mille tehniline maht on tagasihoidlik tööstuslike süsteemidega võrreldes)".
    * **Asukoht:** `third_chapter.tex`, rida 127.
    * **Selgitus:** Väide „esimene eesti äratussõna mudel" on lõputöös teadlikult jäetud sulgudesse, kuid seda ei ole **kuskil empiiriliselt põhjendatud** (st: ei ole tsiteeritud, et openWakeWord/Picovoice/microWakeWord avalikes mudelivalimikes pole eestikeelset äratussõna). Sissejuhatuses (rida 1) viidatakse, et eesti keel ei kuulu „avatud raamistiku `openWakeWord` jaotatud mudelite ega lähima suletud lähtekoodiga võrdluspunkti Picovoice Porcupine toetatud keelte hulka" — see on lähedane, kuid ei ole sama, mis „esimene eesti äratussõna mudel olemas." Loogikaviga: arutelus väide järsku kinnitatakse („mis on tõsi") ilma allikata. Soovitus: kas lisada otsene tsiteerimine, et **avalikes** mudelipanga indeksites pole eelnevat eesti keele äratussõna mudelit, või öelda alandlikumalt „esimene avalikult dokumenteeritud."

### 1.7 Picovoice'i benchmark — võrdluspunkti määratlus on hägus
* **Vigane väide:** „Picovoice'i avalikud võrdlusalused kasutavad rangemat 1 valeaktiveeringu / 10~h punkti".
    * **Asukoht:** `introduction.tex`, rida 7.
    * **Selgitus:** Tegemist on tõenäoliselt korrektse väitega Picovoice'i benchmarki kohta (vt nende github.com/Picovoice/wake-word-benchmark — siin näidatakse missrate vs „1 false alarm per 10 hours"), kuid sõnastus „rangemat" on kontekstis ebapiisav: Picovoice'i 1 FA / 10 h on pigem „tunduvalt rangem" (kümnekordne) kui openWakeWord'i 0,5 FA / h. „Rangem" ilma kvantifikaatorita võib lugejat eksitada arvama, et erinevus on väike. Soovitus: lisada „kümnekordselt rangem" või „ligi 10× rangem".

### 1.8 Wilsoni vahemiku ja Poissoni-Garwoodi vahemiku rakendusala
* **Vigane väide:** „Klipi-tasemel mõõdikutele (tuvastamismäär, FPR) kasutatakse Wilsoni skoorimeetodi vahemikku".
    * **Asukoht:** `first_chapter.tex`, rida 60.
    * **Selgitus:** See on metoodiliselt korrektne, kuid sissejuhatuses on lubatud „lähikõne tuvastamismääraks (\emph{recall}) vähemalt 0{,}95" — kui valim on n=5 ütlust (kasutajatesti protokoll, §\ref{sec:user-test-methodology} rida 131), siis Wilsoni 95% usaldusvahemik 5/5 jaoks on $[0{,}57,\,1{,}00]$. See ei ole faktiviga, kuid loogikaviga: **tuvastamismäära $\geq$ 0,95 sihti ei saa rangelt kontrollida valimist 5 ütlus per osaleja, kui ainult 5 osalejat saab usaldusväärselt sihti kontrollida.** 30 osalejaga (kokku 150 ütlust) on see usaldusvahemik kitsam. Selle koha peal jääb sissejuhatuse siht ja kasutajatesti maht statistiliselt pingesse.

---

## 2. Tuvastatud loogikavead ja ajalised ebakõlad

### 2.1 Ajaline ebakõla: kasutajatest „kavandatud", aga töö esitatakse 2026-05
* **Probleemne arutluskäik:** „Lõpphindamise kasutajatest on kavandatud lühikese, umbes 10-minutilise ühe-nutipirni stsenaariumina 20--30 osalejaga... Piloodi vaikevalik on \texttt{v16c}".
    * **Asukoht:** `first_chapter.tex` §\ref{sec:user-test-methodology}, rida 131.
    * **Selgitus:** Töö esitamise kuupäev on hard-deadline 2026-05-18 (CLAUDE.md). Kui metoodikapeatükk räägib kasutajatestist tulevikuvormis („on kavandatud", „valideeritakse vahetult pärast salvestamist"), siis lugejal ei ole võimalust mõista, kas tulemused (Tulemuste peatükk, mida ei loetud, kuid millele viidatakse) sisaldavad selle testi tegelikke andmeid või mitte. Arutelus §\ref{sec:fourth-round} öeldakse selgesõnaliselt, et „neljas kiht peab tulema kasutuskogemustest, mida käesolev töö pole veel teostanud", mis viitab et kasutajatesti **ei ole** lõputöö esitamise hetkeks lõpetatud. See on **legitiimne ajaline raamistus**, kuid praegune sõnastus jätab metoodikas mulje, et „kasutajatest on osa lõputööst", ent arutelus järsku tunnistatakse, et see on tulevik. Soovitus: metoodika alguses §\ref{sec:user-test-methodology} lisada selge lause „käesoleva töö esitamise hetkeks on/ei ole läbi viidud," et lugejat orienteerida.

### 2.2 Ajaline ebakõla kuupäevades: 2026-04-21 → töö esitatakse 2026-05
* **Probleemne arutluskäik:** „See vähendas ühtsel 2026-04-21 hindamisel Common~Voice ET voogedastus-FAPH-i 25,4-lt 14,4-le".
    * **Asukoht:** `first_chapter.tex` §\ref{subsec:residual}, rida 104.
    * **Selgitus:** Kuupäev 2026-04-21 on 27 päeva enne deadline'i 2026-05-18. See on iseenesest kooskõlas, kuid kombineeritult §\ref{sec:user-test-methodology} kasutajatesti tulevikuvormiga jätab mulje, et töö viimase kuu jooksul on toimunud peamiselt mudelivärskendused, mitte kasutajatesti läbiviimine. **Loogikaprobleem ei ole ajaline absoluutselt** (kuupäev on minevikus), aga **kompositsiooniline:** kui mudel on kuupäeva järgi värske (3 nädalat enne lõpetamist) ja kasutajatest tulevikus, siis töö hindamisprotokoll ei ole mudelile veel rakendatud. Selle kohta peaks olema selgesõnaline märkus, et metoodika protokoll tugineb 0,79 FAPH-le mitte kasutajatesti andmetele.

### 2.3 Loogikahüpe: „lähikõne tuvastamismäär $\geq$ 0,95" — aga siht jääb täitmata
* **Probleemne arutluskäik:** „kas treenitud mudel saavutab eestikeelsel taustaheli korpusel pidevvoo FAPH~$<$~1 ja lähikõne tuvastamismäära~$\geq$~0{,}95 sihi" (`introduction.tex` rida 14) vs „jääkpiiranguna jääb tuvastamismäär reaalsetel \enquote{Kule}-hääldustel juurutuslävel madalamaks kui TTS-positiivsetel klippidel" (`third_chapter.tex` rida 144).
    * **Asukoht:** sissejuhatus + arutelu.
    * **Selgitus:** Sissejuhatus seab uurimisküsimuseks „kas mudel saavutab tuvastamismäära $\geq$ 0,95," kuid arutelu lõpus on tuvastamismäär „madalam kui TTS-positiivsetel klippidel" (täpne arv puudub viidatud lõigus). Lugejale jääb vastuse otsimine sisutühjaks: **uurimisküsimus on püstitatud, kuid otsest „jah"/„ei" vastust ei pakuta**. Kokkuvõte (`summary.tex` rida 7) tunnistab, et „üksiku mudeli puhul ei õnnestunud neid eesmärke täielikult ühendada" — see on aus, kuid kuna sissejuhatus oli numbriline siht ja kokkuvõte on kvalitatiivne tõdemus, on **otsene numbrline võrdlus jäänud tegemata**. See on **loogikaviga argumentatsioonis**: küsimus on numbriliselt püstitatud, vastus kvalitatiivselt antud. Soovitus: kokkuvõttes lisada konkreetne arv (parima mudeli reaalsete kõnelejate tuvastamismäär X%, mis on kas $\geq$ 0,95 või mitte).

### 2.4 Mõisteline segadus: „tuvastamismäär" vs „recall" vs „saagis"
* **Probleemne arutluskäik:** Sissejuhatus kasutab „lähikõne tuvastamismäära~$\geq$~0{,}95" (rida 14). Metoodika §\ref{subsec:faph-variants} pole täpset tuvastamismäära definitsiooni. Arutelus on „päriskõneleja tuvastamismäär", „TTS-allikate tuvastamismäär", „reaalsete kõnelejate tuvastamismäär". Kokkuvõte (`summary.tex` rida 6) kasutab varianti „uue kõneleja saagis" ja „äratussõna tabamine" sünonüümselt.
    * **Asukoht:** kogu töö.
    * **Selgitus:** Eestikeelses kirjanduses on „tuvastamismäär", „saagis" ja „recall" sünonüümid ainult kontekstis, kus alus (denominaator) on selgelt määratletud. Töö kasutab „tuvastamismäära" mitmes kontekstis ilma denominaatori täpsustuseta:
      - klipi-tasemel TTS-klippide tuvastamismäär,
      - sessiooni-tasemel päris kõneleja ütluse tuvastamismäär,
      - sõna-tasemel „kuule kratt" terve fraasi tuvastamismäär.
    Need kolm ei ole sama metricna isegi mitte arvuliselt vahetult võrreldavad. **Mõisteviga:** üks termin kannab kolme erinevat denominaatorit. Soovitus: defineerida metoodikas selgesõnaliselt, mida „tuvastamismäär" käesolevas töös tähendab, ja kasutada eraldi termineid (nt „klipi-tasemel tuvastamismäär", „session-level recall") iga kontekstis.

### 2.5 Loogikaviga: konsensus näitab 0,79 FAPH, kuid „saagis langeb"
* **Probleemne arutluskäik:** „katsetati töö praktilise laiendusena ka spetsialiseeritud ekspertmudelite konsensust, mis vähendas vääraktiveerimisi märgatavalt ja saavutas Common Voice eesti keele hold-out kõnel FAPH~$=$~0{,}79, kuid tegi seda saagise arvelt."
    * **Asukoht:** `summary.tex`, rida 7.
    * **Selgitus:** Loogiliselt kooskõlas, kuid **kvantifikaator puudub:** „saagise arvelt" — kui palju? Lugeja ei saa otsustada, kas konsensus on praktikas kasutatav lahendus. Kui saagis langeb 0,98 → 0,90, on konsensus akustiliselt kasutatav; kui 0,98 → 0,40, ei ole. Selline kvalitatiivne sõnastus üliolulise kompromissi puhul on **argumentatsiooni nõrkus**.

### 2.6 Põhjuslikkuse vihje: „benchmark vs reality gap" kui üldistus
* **Probleemne arutluskäik:** „Iga madala ressursiga keele äratussõna arendaja, kes tugineb ainult standardsetele mõõdikutele, riskib valida juurutamiseks vale mudeli."
    * **Asukoht:** `third_chapter.tex` rida 79.
    * **Selgitus:** See on **non sequitur kuni laia üldistuse**: töö dokumenteerib lahknevuse ühe keele (eesti), ühe sõnafraasi (Kuule Kratt) ja kitsa kõnelejate baasi peal. Üldistus „iga madala ressursiga keele arendaja" on liiga lai. Sama põhjapanev väide (§\ref{sec:contribution-transferability}) on autor leidnud „protokollis", mis on kohaldatav, mitte vältimatult tõene. Soovitus: kvalifitseerida „dokumenteeritud juhtumi alusel võib eeldada, et sarnane risk eksisteerib teistel sarnastel projektidel" — see ei nõrgenda väidet, vaid teeb selle kaitstavaks.

### 2.7 Ülesandepüstituse ja sissejuhatuse erinev sihtkonfiguratsioon
* **Probleemne arutluskäik:** ülesandepüstitus loetleb „MixConv kihtidel põhinevat mixednet arhitektuuri" (rida 83) ilma residuaalühendusi mainimata; metoodikas on residuaalühendused omaette alajaotis ja eraldi ablatsioon. Üks argument paistab arhitektuurselt staatiline, teine evolutsiooniline.
    * **Asukoht:** `ylesandepystitus.tex` vs `first_chapter.tex` §\ref{subsec:residual}.
    * **Selgitus:** Ülesandepüstitus on kirjutatud projekti alguses (eeldatavasti 2026 alguses) ja kirjeldab tehnoloogilist plaani ilma residuaalühendusteta. Metoodika lisab residuaalühendused hilisemate katsete põhjal. **Ajaline ebakõla ei ole eksitav**, kuid lugeja, kes võrdleb mõlemat dokumenti, näeb pingelist suhet plaanitud ja teostatud arhitektuuri vahel. Tavaliselt sellistel juhtudel lisatakse ülesandepüstitusse hiljem **redaktsioonimärkus** „lisatud residuaalühenduste ablatsioon," või metoodikas selgitatakse, et ülesandepüstitus oli eel-disain.

### 2.8 Kontekstiakna pikkuse spekulatiivne väide
* **Probleemne arutluskäik:** „Pikem kontekstiaken (nt 2000\,ms) annaks rohkem eelkonteksti ja lubaks mudelil paremini diskrimineerida pikemaid sarnaseid fraase, kuid nõuab ka rohkem mälu sisemise oleku hoidmiseks."
    * **Asukoht:** `first_chapter.tex` §\ref{subsec:clip-duration}, rida 113.
    * **Selgitus:** See on **spekulatiivne väide** ilma ablatsioonitõendita. Töös on tehtud mitmeid ablatsioone (residuaalühendused v13a/v13b, SpecAugment), kuid kontekstiakna ablatsiooni ei ole tehtud (1500ms hoiti kõikides versioonides). Loogikaviga ei ole faktiliselt vale, kuid see on **põhjendamata väide**, mis võib lugejas tekitada mulje, et see on testitud. Soovitus: lisada „(katsetamata käesolevas töös)" või eemaldada lause täielikult.

### 2.9 Vastuolu „Kule" hääldusbias'i argumendi kohta
* **Probleemne arutluskäik:** Sissejuhatuses ega metoodikas ei mainita konkreetselt „Kule"-vs-„Kuule" hääldusebimulli, mis on aga arutelus (§\ref{sec:eval-evolution} rida 114) keskne risk („mõõtis prefiksi-tüüpi heli"). Kokkuvõttes (rida 7) viidatakse uuesti.
    * **Asukoht:** kogu töö.
    * **Selgitus:** **Sisemine vastuolu argumentatsiooni kaalukuses:** sissejuhatus räägib „eestikeelsest äratussõnast Kuule Kratt" ühtse fraasina, kuid arutelu paljastab, et reaalsed kõnelejad ütlevad sageli „Kule" ja see asümmeetria on jäänud kuni Tulemuste peatükini varjus. CLAUDE.md kontekst kinnitab: „86% Kuule treeningus, aga reaalsed kõnelejad ütlevad Kule." Sissejuhatus võiks **tunnistada seda asümmeetriat varem**, et arutelu järelduslõpetus ei tundu järsk. Praegune ülesehitus on **argumentatsiooniliselt lekkiv**: lugeja ootab ühte fraasi, saab kahte; ja seda ei ole sissejuhatuses raamistatud.

### 2.10 ESPHome tensor\_arena: 45–50 KB vs 107 KB
* **Probleemne arutluskäik:** „mudeli ja `tensor_arena` (käesolevas töös 57\,KB ning ${\sim}107$\,KB koos töömäluga, vt §\ref{subsec:quantization})" (`first_chapter.tex` rida 21) vs „Järeldamise ajal vajab ESPHome manifest lisaks 45--50\,KB töömälu (\texttt{tensor\_arena})" (`first_chapter.tex` rida 127).
    * **Asukoht:** kaks erinevat lõiku samas peatükis.
    * **Selgitus:** Kui mudel on 57 KB ja kogu mälu (mudel + tensor\_arena) on $\sim$107 KB, siis tensor\_arena on $\sim$50 KB — see on **järjepidev** §\ref{subsec:quantization} arvuga. Kui aga aktiivne kandidaat on `v16c` (148 KB) ja tensor\_arena 45–50 KB, siis kogu mälu on $\sim$200 KB, mis vastab teisele lausele. **Faktivea ei ole, kuid sõnastusest ei selgu, et 107 KB on **vana** v6 number ja 200 KB on **uus** v16c number.** Lugejale jääb segane, kumb on siis töö „aktiivne" mälunõue.

---

## 3. Erilist tähelepanu nõudvad kohad (mitte kindlasti vead, aga kontroll soovitatav)

* **„99 h Android-välikatse" — täpsem maht 98,97 h.** Sissejuhatus mainib mõlemat: „${\sim}99$~h" ja „98{,}97~h" sama lause sees. Tehnililt korrektne, aga liigne segadusse ajav.
* **„15+ mudeliversiooni"** (`third_chapter.tex` rida 34): konkreetne arv puudub. Soovituslik kas „15" või „üle 15" konkretiseerida.
* **„kuni 0,95 tahtmatut aktiveerimist tunnis" Dubois et al.** viide — jätab arusaamatuks, kas see on FAPH ühel seadmel või keskmine; tasub kontrollida originaalis (Dubois 2020).
* **„MISP Challenge" — mandariini keele puhul.** Tegelikult MISP on multimodaalne ja sisaldab nii mandariini kui ka inglise keelt; täpsustada, kas käesoleva töö viide on rangelt mandariini-spetsiifiline.
* **„Apple'i otsast-lõpuni DNN-HMM treening"** (Shrivastava 2021) — DNN-HMM on hübriidsüsteem, „end-to-end" reklaameeritakse selles paberis tõenäoliselt teisiti; tasub kontrollida originaali täpne sõnastus, kas seal on tõesti „end-to-end DNN-HMM" või on autor ühitanud kaks eraldi mõistet.

---

## Kokkuvõte

**Tegelikult eksitavaid faktivigu** (kus arv on **vale**) sellest valimist ei leidnud. Eksitav on:
1. **„Kahe kuuekohtnumbrelise suurusjärgu erinevus"** (3.III ptk, §\ref{sec:eval-evolution}) — kvantifikaator on numbriliselt vale ja peab olema parandatud.
2. **Mudeli mahu kahetähenduslikkus** (`first_chapter.tex` §\ref{subsec:quantization}) — 57 KB / 148 KB koheselt küsivat lugejat võib eksitada.

**Loogikavigade hulgas peamine probleem:**
1. **Sissejuhatuses on numbriliselt määratletud uurimisküsimus** („tuvastamismäär $\geq$ 0,95"), aga kokkuvõttes vastatakse sellele kvalitatiivselt — küsimus jääb sisuliselt vastamata. See on **kõige tõsisem retsensendi-tasemel argument** ja oleks väärt ühe lause lisamist kokkuvõttesse.
2. **Mõisteline segadus „tuvastamismäära" definitsiooni ümber** — lahendatav metoodika definitsiooni ühe lausega.
3. **Ajaline ebakõla kasutajatesti vahel:** Metoodikas olevikuvormis, arutelus tunnistatud „pole veel teostatud" — soovitatav lisada metoodika alguses märkus.

**Töö üldine tugevus eksimuste suhtes:** töö on metoodiliselt aus (§\ref{sec:fourth-round} on üks ausamaid lõike kogu lõputöös: lubadus on protseduuri korralikkus, mitte mudeli täiuslikkus). Süsteemse faktivea probleemi ei ole. Peamine kvaliteediprobleem on **argumentatsiooni täielikkus** — mitmes kohas on väited kvalitatiivsed, kus lugeja ootab numbrilist toetust, ja vastupidi.
