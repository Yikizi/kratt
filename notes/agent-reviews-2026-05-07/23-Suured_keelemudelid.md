---
source_prompt: 03_Lõputöö_alamosad/Suured_keelemudelid.txt
prompt_type: evaluative (futurikindluse audit GenAI/LLM prisma kaudu)
generated: 2026-05-07
---

# GenAI- ja LLM-prisma audit: \enquote{Kuule Kratt} eestikeelse äratussõna lõputöö tulevikukindlus

Analüüs on koostatud lõputöö sissejuhatuse, esimese ja teise peatüki, kokkuvõtte ning eesti- ja ingliskeelse abstrakti põhjal. Kolmanda peatüki (tulemused) sisu on kasutatud kaudselt — viidetena, mis sisalduvad arutelupeatükis (FAPH 0,79, v6-residual, ekspertkonsensus, andmelekke audit). Hinnangud on antud äratussõna tuvastuse spetsiifikat ja töö enda piiranguid arvesse võttes.

## 1. Ohu hindamine (Obsolescence Risk)

### 1.1 Kas tipptaseme LLM-id (GPT-5, Gemini 3 jms) suudaksid lõputöö probleemi automaatselt lahendada?

Lõputöös püstitatud probleem on **eestikeelse äratussõna tuvastus piiratud ressursiga mikrokontrolleril (ESP32-S3) lokaalse, pidevvoo režiimis töötava süsteemina**. Selle ülesande olemus seab generatiivsetele suurte keelemudelite süsteemidele põhimõttelisi piiranguid, mis vähendavad otsest asendusriski:

- **Riistvarapiirang.** Töö siht on ${\sim}57$--$148$\,KB suurune INT8-kvantiseeritud TFLite-mudel ja ${\sim}45$--$50$\,KB \texttt{tensor\_arena} ESP32-S3 piires (vt teine peatükk, §\,Kvantiseerimine). Tipptaseme LLM-id (GPT-5, Gemini 3) on miljarditeparameetrilised pilveteenused, mis ei mahu ega ole mõeldudki sellele riistvaraklassile. Isegi tihendatud variantides (mobiilsed väikemudelid) on parameetrite arv suurusjärkudes erinev.
- **Tegumi-spetsiifika.** Äratussõna tuvastus on kitsas binaarne signaali-tasandi klassifitseerimine voogedastusrežiimis. See ei ole keele-mõistmise ülesanne, vaid akustilise mustri tuvastamine. Suured keelemudelid on tugevad teksti- ja multimodaalse mõistmise ülesannetes, kuid pidevvoo helist madala latentsusega \enquote{kratti} eraldamine ei ole nende loomulik töötsükkel.
- **Privaatsus- ja arhitektuurinõue.} Töö rõhutab lokaalsust ja pilveteenuseta toimimist (vt sissejuhatus, abstrakt). LLM-põhine pilvelahendus oleks selle nõude vastandiks ja seetõttu ei lahenda \emph{sama} ülesannet, vaid ainult sellega visuaalselt sarnast.

**Järeldus:** otsene asendusrisk tipptaseme LLM-ide poolt on \emph{madal}. LLM ei lahenda lokaalse, mikrokontrolleripõhise, väikese keele äratussõna ülesannet automaatselt. Kaudne risk on aga olemas — sellest allpool.

### 1.2 Kaudne ohuhinnang: kus võivad LLM-id ja GenAI-süsteemid töö relevantsust nõrgestada?

Mitmes komponendis on AI-mõjuga muutused juba toimumas ning töö peab nendega arvestama, et mitte vananeda enne kaitsmist või vahetult selle järel:

- **Andmesünteesi tööriistad ja TTS-mudelid arenevad kiiresti.** Töö üks peamisi piiranguid on positiivsete näidete kogumise mahukus ja XTTS-kloonitud kõne piiratud realism. Arenenud TTS-süsteemid (nt suuremate prosoodiamudelitega lahendused, multimodaalsed kõnesüntesaatorid) võivad lähikuudel teha sünteetilise positiivse klassi laiendamise oluliselt lihtsamaks. Töö \emph{empiiriline järeldus}, et TTS-positiivsed klipid ülehindavad tuvastamismäära (vt §3.2 \enquote{Põhjus 1}, viide Park et al.\,2024), püsib selle muutuse korral kehtiv ja muutub väärtuslikumaks. Konkreetsed mudeliversioonid v6, v16c, expert-a/b2 muutuvad aga kiiremini iganenuks.
- **End-to-end häälagentide universaalne mudel.** Tippmudelid liiguvad selles suunas, et üks suur multimodaalne mudel täidab korraga äratuse, kõnetuvastuse ja kavatsuste mõistmise. Kui see suund jõuab ka pilveteenusteta servaseadmetele (näiteks läbi destilleeritud variantide), võib eraldiseisev äratussõna komponent muutuda osaks integreeritud pinust. Töö arhitektuurne valik (eraldi äratussõna toru) jääb sellisel juhul ühe alternatiivina, mitte ainsa kanoonilise lähenemisena. \textbf{See ei kahjusta töö järeldusi, kuid muudab raamistuse oluliseks: töö peaks selgelt põhjendama, miks just \emph{nüüd} (mitte 2030) on lokaalne servaseadme äratussõna kõige loogilisem lahendus.} Sissejuhatus seda osaliselt teeb (riistvaraklass, lokaalsus, latentsus), kuid LLM-de kontekstis võiks olla teravam.
- **\enquote{Mudelivalik} muutub kommodiseerituks; protokoll mitte.** Eelseisva 2--3 aasta jooksul on tõenäoline, et väikeste keelte jaoks tekib avatud lähtekoodiga eelnevalt treenitud äratussõna mudeleid (sh openWakeWord-ile lisanduvaid eesti keele baasmudeleid). Sellisel juhul väheneb panuse \enquote{esimene eesti äratussõna mudel} uudsus. Töö ise tunnistab seda (vt §\,sec:contribution-transferability: \enquote{tehniline maht on tagasihoidlik tööstuslike süsteemidega võrreldes}). Kaitstavaks jääb see, mis on käsitletud kui \emph{töö metoodiline põhipanus} — väikese ressursiga keele kohaliku äratussõna mitme\-mõõdikuline valideerimisprotokoll. See osa on isegi LLM-ajastul väärtuslik, sest \emph{hindamine} jääb inimkeskseks tegevuseks ka siis, kui mudelite treenimine automatiseeritakse.

### 1.3 Kas tulemused võivad muutuda ebaoluliseks, sest AI lahendab probleemi kiiremini või odavamalt?

Lühi- ja keskpikalt (1--2 aastat) on vastus eitav: konkreetne mikrokontrolleri-tasemel lokaalse äratussõna tuvastuse probleem ei kao automaatselt ja keele-spetsiifiline empiiriline tõendusmaterjal jääb kasulikuks. Pikemalt (5+ aastat) on aga tõenäoline, et kvantiseeritud ja distilleeritud universaalsed kõnemudelid katavad ka väikeseid keeli vaikimisi. Selleks ajaks peab töö pakkuma \emph{midagi muud} kui ainult ühte mudelit ja ühte FAPH-numbrit. Töö kõige püsivamad osad on:

\begin{enumerate}
    \item kolmeringiline hindamise valideerimismuster (andmeleke $\rightarrow$ positiivse klassi audit $\rightarrow$ kontrollpunkti komposiitkriteerium), mille kirjeldus on töö metoodilise panuse keskmes;
    \item nelja FAPH-variandi eristus (raamistiku / skriptitud taasmängu / välitingimuste / kasutajatesti) — see on protseduuriline ja ei vanane mudelite arenedes;
    \item benchmark-vs-reaalsuse lõhe empiiriline dokumenteerimine konkreetsete numbritega (Common Voice ET FPR 0,4\% vs.\ MacBook Pro $\sim\!50$~FAPH/h).
\end{enumerate}

## 2. Sünergia ja täiendamine (Enhancement)

Töös on agentpõhise arenduse roll juba selgelt sõnastatud (vt §\,Agentpõhine arendus kui töövõimendaja). See on hea metakomm\-entaar ning Eesti bakalaureusetööde kontekstis võrdlemisi haruldane aus käsitlus. Allpool toodud soovitused tugevdavad seda joont, mitte ei dubleeri.

### 2.1 Kus saaks LLM-id metoodikat \emph{tugevdada} (mitte asendada)

- **Sarnaste negatiivnäidete genereerimine süstemaatilisemalt.** Töö üks põhilisi nõrkusi (nimetatud nii teises kui kolmandas peatükis) on \enquote{kuule rott}, \enquote{kuule kraam}, \enquote{kule kratt} jms foneetiliselt sarnaste fraaside puudulik katvus treeningus ja hindamises. LLM-i saab kasutada \emph{assistent-leksikograafina}: genereerida kontrollitud nimekirja eestikeelseid fraase, mis algavad \enquote{kuule}/\enquote{kule}-eesliitega või sisaldavad \texttt{Kratt}-iga foneetiliselt sarnaseid sõnu (rott, raam, kraam, krati, krattide). Inimene valideerib loendi (kontekst ja loomulikkus); seejärel sünteesitakse hääled mitme TTS-allika kaudu. See on klassikaline \enquote{LLM kui ettepaneku-generaator, inimene kui hindaja} muster ja ei ohusta tõendusahela usaldusväärsust.
- **Stsenaariumi-skriptide automaatne mitmekesistamine.** §3.2 alaosas \enquote{Lahendusena: stsenaariumpõhine testimisvoog} on kirjeldatud nelja kategooriat (vaikus, TV/muusika, vestlus sarnaste fraasidega, äratusütlused). LLM saab genereerida kümneid loomulikke vestlustranskriptsioone, mis sisaldavad foneetiliselt sarnaseid fraase looduslikus kontekstis (\enquote{kuule, rott on köögis}). Need on hiljem inimese poolt redigeeritud ja sünteesitud või loetud. See annab kontrollitud, kuid mitmekesise hindamiskorpuse, mille käsitsi koostamine oleks ebaproportsionaalne.
- **Tulemuste kirjanduspõhise kontekstualiseerimise abi.** LLM-i saab kasutada \emph{assistent-bibliograafina}: ette anda töö FAPH-tulemused ja paluda välja tuua, millistes hiljutistes (2024--2026) artiklites on raporteeritud sarnaseid suurusjärke ja milliste eelduste juures. Inimene kontrollib viited Google Scholaris või arXivis. Töö praegu tugineb peamiselt 2014--2022 perioodi viidetel; LLM aitab leida värskemat võrreldavat materjali, mille olemasolu autor võib käsitsi otsides kahe silma vahele jätta.
- **Auditidoominide laiendamine.** Kolme valideerimisringi muster (§\,sec:three-rounds) on töö metoodiline tuum. LLM-i saab kasutada \emph{punase tiimina}: anda mudelile töö hindamisseadistus ja küsida, milliseid lühiteid mudel veel võiks õppida. Vastused on hüpoteesid, mitte tõendid, kuid need aitavad süstemaatiliselt mõelda, milliseid lühiteid on jäänud katmata. See seob hästi §\,sec:fourth-round nimetatud \enquote{võimaliku neljanda ringi} ausa piiranguga.

### 2.2 Kus on LLM kui assistent-analüütik vahetult kohaldatav

- **Common Voice ET segmentide kvaliteedikontroll.** LLM (multimodaalne, kuulamisvõimega) võib aidata leida segmente, kus eestikeelses Common Voice'is on tegelikult midagi taustaga sarnast \enquote{kuule}-prefiksiga sõnu, mis selgitaksid mudeli vallandumismustreid. See ei asenda käsitsi auditit, kuid leiab kandidaatklippe.
- **Kasutajatesti vabavormiliste vastuste temaatiline kodeerimine.** Plaanitavas 20--30 osalejaga testis (§\,sec:user-test-methodology) kogutakse üks avatud küsimus häiriva või üllatava kogemuse kohta. LLM saab pakkuda esmast temaatilist kodeerimist, mille autor seejärel valideerib ja korrigeerib. See on klassikaline kvalitatiivse analüüsi assistent-roll.
- **Mudeli/koodibaasi tehnilise dokumentatsiooni kvaliteedi kontroll.** Töö kirjutab ise, et agentpõhine arendus võimaldas paralleelselt arendada mõõte- ja tugivahendeid (Android-logija, hindamisskriptid). LLM-i saab kasutada nende tööriistade dokumentatsiooni kvaliteedi kontrollimiseks (vastavus käitumisele, vananenud lõigud) — see on tüüpiline \enquote{assistent-redaktor} ülesanne.

## 3. Unikaalne inimväärtus (Human Value Proposition)

Need töö osad nõuavad kriitilist mõtlemist, füüsilise maailma tunnetust, unikaalseid andmeid või eetilist kaalutlust ja \emph{ei} ole AI-le delegeeritavad — see on töö tegelik kestev väärtus.

### 3.1 Töö osad, mida AI ei suuda jäljendada

- **Päris kõnelejate kogumine ja kasutajatesti läbiviimine.** 20--30 osalejaga test eestikeelse \enquote{Kuule Kratt} hääldusvariantidega on \emph{unikaalne empiiriline andmestik}. AI ei saa seda genereerida ilma loomulikkust kaotamata. Sellega seotud aktuaalne avastus — \enquote{Kule} vs \enquote{Kuule} hääldusbias — on füüsilise reaalsuse tähelepanek, mis tekkis ainult inimese kuulamisest. See on töö üks selgemaid püsivaid panuseid.
- **Eetiline ja juriidiline kaalutlus.** Töös on kahetasandiline nõusolekumudel (minimaalne tehniline + audio opt-in), GDPR- ja eetikakomitee-läbimõtlemine. AI võib pakkuda mustrit, kuid vastutus, kontekstipõhine kohandamine ja TalTech-spetsiifiline rakendus jäävad inimese pädevusse.
- **Domeeninihke empiiriline tõendamine.** Konkreetne avastus, et v6 Common Voice ET FPR 0,4\% versus MacBook Pro mikrofoni $\sim\!50$\,FAPH/h on \emph{kahe suurusjärgu} lõhe, on tõestus reaalse riistvara peal. Selliseid numbreid ei genereeri ükski LLM — need tulevad ainult tegelikust mõõtmisest.
- **Andmelekke audit ja sellest järelduvad protokollimuudatused.} Kolme ringi valideerimismuster (§\,sec:three-rounds) on inimese diagnostilise mõtlemise tulemus. LLM saaks luua \emph{narratiivi} sellisest auditiprotsessist, kuid ei avastaks, et lokaalne hindamine kasutas samu Common Voice klippe kui treening — selline avastus nõuab kogu pipeline'i kontekstuaalset tundmist.
- **Otsustuskriteeriumid kompromissi all.** Kontrollpunkti komposiitvalik (taustaheli FAPH + päriskõnelejate tuvastamismäär + fraasistruktuuri test korraga) on inimese väärtushinnang, mille tuum on otsus, et \emph{ühe mõõdiku optimeerimine ei ole vastuvõetav}. See on metoodiline, mitte algoritmiline otsus.

### 3.2 \enquote{Aus piir} kui väärtus

§\,sec:fourth-round (\enquote{Aus piir: võimalik neljas ring}) on töö üks intellektuaalselt küpseimaid lõike. LLM-süsteem ei kirjuta tavaliselt selliseid auseid metakommentaare oma piiride kohta — see nõuab autori isiklikku epistemoloogilist alandlikkust. Töö peaks seda joont \emph{tugevdama}, sest just see eristab seda potentsiaalsest AI-genereeritud tekstist.

## 4. Soovitused tulevikukindluse tagamiseks

Allpool on viis konkreetset soovitust, mille rakendamine vähendaks LLM-ajastu poolt kaasa toodavaid tulevikuriske ja tõstaks töö püsivat väärtust. Iga soovitus on raamistatud maksumuse ja deadline-i (2026-05-18) kontekstis.

### 4.1 Lisada lühike alalõik, mis raamistab töö LLM/GenAI ajastuga

\textbf{Kus:} arutelupeatüki algusesse või agentpõhise arenduse alalõigu järele (§\,Agentpõhine arendus kui töövõimendaja).

\textbf{Sisu:} ühe-kahe lõigu pikkune käsitlus, mis vastab küsimusele \enquote{miks ei lahenda seda probleemi GPT-5/Gemini 3 automaatselt ja kas see kehtib ka aastal 2030}. Argumendid on kõik juba olemas töö enda lõigetes — vaja on need ühte fookusesse koondada: (a) riistvaraklass, (b) latentsus ja lokaalsus, (c) andmesuveräänsus, (d) protokolli ülekantavus jääb püsima isegi siis, kui mudel iseenesest vananeb. \textbf{Maht:} ${\sim}300$ sõna; \textbf{aeg:} 1--2 tundi.

\textbf{Põhjus:} retsensent ja kaitsekomisjon küsib seda peaaegu kindlasti 2026. aasta kaitsmisel. Eelprobleemina vastamine kaitseb tööd \enquote{millal see vananeb} -tüüpi küsimuste eest.

### 4.2 Sõnastada ümber abstraktis ja kokkuvõttes peamine panus protokolli, mitte mudelina

\textbf{Kus:} \texttt{misc/abstract-estonian.tex} ja \texttt{misc/abstract-english.tex} ning \texttt{chapters/summary.tex}.

\textbf{Sisu:} praegune sõnastus rõhutab \enquote{reprodutseeritavat torut, dokumenteeritud andmestikku- ja hindamisprotokolli}. Kolmas peatükk (§\,sec:contribution-transferability) ütleb selgemalt: \emph{\enquote{töö üks peamisi panuseid ei ole esimene eesti äratussõna mudel\,..., vaid väikese ressursiga keele kohaliku äratussõna mitmemõõtmelise valideerimise protokoll.}} Sama framing peab jõudma juba abstraktidesse. Inimese koostatud protokoll on LLM-resistentne; konkreetne mudeliversioon ei ole.

\textbf{Aeg:} 30 minutit. \textbf{Risk:} muudatus on minimaalne, kuid mõju lugeja taju\-le suur.

### 4.3 Lisada ühe peatüki sees \emph{eraldi paragrahvi} \enquote{Mida LLM-id käesoleva töö osas ei suuda}

\textbf{Kus:} arutelupeatüki sisse, kas §\,sec:contribution-transferability lõppu või \emph{enne} \enquote{Aus piir} alalõiku.

\textbf{Sisu:} loend (3--5 punkti) konkreetsetest ülesannetest, mille puhul LLM-süsteem ei oleks saanud tööd asendada — näiteks: päris kõnelejate \enquote{Kule}-bias avastamine (vt mälu), domeeninihke kahe suurusjärgu mõõtmine reaalsel mikrofonil, kasutaja-eetika kahetasandiline nõusolekumudel. Selle paragrahvi eesmärk on aktiivselt vastata küsimusele \enquote{miks ei oleks ChatGPT seda tööd kirjutanud}.

\textbf{Aeg:} 1--2 tundi. \textbf{Mõju:} eristab töö selgelt potentsiaalsest AI-genereeritud lõputööst.

### 4.4 \emph{Mitte} lisada peatükki, mis võrdleb autori tulemusi LLM-i genereeritud tulemustega

See oli üks prompti pakutud variantidest, kuid käesoleva töö kontekstis on see \textbf{vastunäidustatud}:

- LLM-id ei suuda treenida ESP32-S3 äratussõna mudelit. Võrdlus oleks ebaaus ja eksitav.
- Kasutajatesti või FAPH-mõõtmisi LLM ei tee. Võrdlus oleks tehniliselt võimatu.
- \enquote{LLM kirjutas sama lõputöö ja sain x\%} on ebausaldusväärne tõend.
- Deadline-i (2026-05-18) ja lõpetamata kasutajatesti (vt PROJECT\_TODO) tõttu on uue eksperimendi lisamine kõrge risk.

\textbf{Soovitus:} jätta see prompti soovitus rakendamata. Soovituse 4.3 (\enquote{mida LLM-id ei suuda}) tekstipõhine analüüs annab sama epistemoloogilise kasu ilma uue eksperimendi maksumuseta.

### 4.5 Tugevdada §\,sec:fourth-round (\enquote{Aus piir}) kui töö epistemoloogiline allkiri

\textbf{Kus:} arutelupeatüki §\,sec:fourth-round.

\textbf{Sisu:} lõik on praegu hea, kuid võiks olla pisut konkreetsem selle kohta, milliseid \emph{tüüpi} viie\-ndaid, kuue\-ndaid jne ringe võib veel tulla ja miks see ei muuda käesolevat tööd kehtetuks. See sõnumitab lugejale, et autor mõtleb selle üle ja töö ei ole staatiline väide. Selline meta\-tase on inim\-autoritel haruldane ja eristab tööd algoritmiliselt genereeritud akadeemilisest tekstist.

\textbf{Aeg:} 1 tund. \textbf{Mõju:} otsene tulevikukindluse tugevdaja.

## 5. Kokkuvõte

Käesoleva töö \textbf{otsene asendusrisk} suurte keelemudelite poolt on \emph{madal}: ülesanne on riistvara-, latentsus- ja privaatsuspiirangute tõttu LLM-ide haarduspinnast väljas. \textbf{Kaudne risk} on \emph{keskmine}: konkreetsed mudeliversioonid (v16c, ekspertkonsensus FAPH 0,79) iganevad 2--5 aastaga, kui väikeste keelte avatud baasmudelid muutuvad kättesaadavaks. \textbf{Tulevikukindluse võti} on töö metoodiline tuum — kolmeringiline valideerimismuster, nelja FAPH-variandi eristus, benchmark-vs-reaalsuse lõhe empiiriline tõendus ja \enquote{aus piir} mõtteviis. Need osad ei vanane mudeli\-arenguga.

Soovituslik tegevuskava on minimaalne (umbes 4--6 töötundi kuni deadline-ini): üks lühike LLM-konteksti raamistav alalõik arutelu peatükki, abstraktide rõhuasetuse muutus protokollile, üks paragrahv \enquote{mida LLM ei suuda} ja \enquote{ausa piiri} lõigu tugevdamine. Uue eksperimentaalse võrdluse lisamist LLM-iga \emph{ei} soovitata, sest see oleks kontseptuaalselt halvasti määratletud ja kasutaks deadline-i suhtes ebaproportsionaalse osa eelarvest.

\textbf{Töö lõputöö-tasemel kandvus} on tugev, kui peamine panus jääb järjepidevalt sõnastatud kui \emph{väikese ressursiga keele kohaliku äratussõna mitmemõõtmelise valideerimise protokoll}, mille konkreetne rakendus on eestikeelne \enquote{Kuule Kratt} mudel. Mudel võib vananeda; protokoll inimese hindamisotsustega ei vanane.
