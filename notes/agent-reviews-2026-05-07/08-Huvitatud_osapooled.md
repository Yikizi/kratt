---
source_prompt: 03_Lõputöö_alamosad/Huvitatud_osapooled.txt
prompt_type: generative
generated: 2026-05-07
---

# Huvitatud osapoolte analüüs

Käesolev analüüs tugineb lõputöö sissejuhatusele, metoodika peatükile, arutelu peatükile, kokkuvõttele ning ülesandepüstitusele. Töö keskmes on eestikeelne äratussõna \enquote{Kuule Kratt} mikrokontrolleril (ESP32-S3), microWakeWord põhine treeningu- ja hindamistoru, FAPH-l rajanev voogedastushindamine, kahe avatud lähtekoodiga raamistiku (microWakeWord ja openWakeWord) võrdlus, lokaalne integreerimine Home Assistanti hääletoruga ning väikese ressursiga keele jaoks koostatud mitmemõõtmeline hindamisprotokoll.

## 1. Osapooled, kellele töö on huvitav praegusel kujul

* **Eestikeelse nutikodu lõppkasutajad ja eraisikust koduautomaatika harrastajad (Home Assistanti kasutajad):** Töö pakub avatud lähtekoodiga eestikeelset äratussõna mudelit ning ESPHome'i \texttt{voice\_assistant} liidese kaudu juurutatavat lokaalset hääljuhtimise lahendust, mis ei nõua pilveteenust. See vastab otse vajadusele kasutada koduautomaatikat oma emakeeles privaatsust säilitades.

* **microWakeWord ja openWakeWord raamistike arendajad ning panustajad:** Töö dokumenteerib mõlema raamistiku praktilist kasutuskogemust väikese ressursiga keele tingimustes, sealhulgas treenimise keerukust, mudeli kvaliteeti, integreeritavust ja laiendatavust eesti keelele. Tagasiside pakub raamistike arendajatele empiirilist alust mitteinglise keelte tuge laiendada.

* **Home Assistanti ja Nabu Casa hääletoru arendajad:** Töö näitab konkreetset eestikeelset rakendusjuhtumit Home Assistanti \texttt{voice\_assistant} arhitektuuris ning kirjeldab, kuidas väikese keeleruumi äratussõna sobitub olemasolevasse hääletorusse. See annab platvormi arendajatele tõendusmaterjali, kuidas nende arhitektuur väikeste keelte korral käitub.

* **Madala ressursiga keelte (\emph{low-resource languages}) kõnetehnoloogia uurijad:** Töö peamine teaduslik panus on dokumenteeritud mitmemõõtmeline hindamisprotokoll (sõltumatu kõrvalejäetud komplekti audit, positiivse klassi sisuline audit, fraasistruktuuri kontrollivad mõõdikud, komposiitne kontrollpunkti valik), mis on otse ülekantav teistele väikeste keelte äratussõna projektidele. Kirjeldatud lühitee-mehhanismid (andmeleke, prefiksi-õpe, üksikmõõdiku optimeerimine) on metoodiliselt huvipakkuvad.

* **Äratussõna tuvastuse (KWS) ja servaarvutuse kogukond:** Empiiriline tõendus standardsete võrdlusaluste ja reaalse kasutuse vahelise lõhe kohta (FAPH-i variantide loendusreegli erinevused, TTS-positiivsete klippide ülehinnatud tuvastamismäär, foneetiliselt sarnaste fraaside käitumine voogedastusrežiimis) täiendab Dubois et al., Sch\"onherri ning MISP Challenge'i tähelepanekuid uue keele kontekstis.

* **TalTechi informaatika õppejõud, juhendajad ning bakalaureusetööde retsensendid:** Töö on hindamiseks esitatud bakalaureuseaste, mille metoodiline distsipliin (kontrollkatse, andmelekke audit, mitme mõõdiku raporteerimine usaldusvahemikega) pakub näidet selle kohta, kuidas üksikautori projektis säilitada tõendusrangust.

* **Eesti keele tehnoloogia arendajad ja keeleressursside hoidjad (TalTechi keeletehnoloogia töörühm, Tartu Neurokõne meeskond):** Töö kasutab Tartu Neurokõne sünteesi treeningandmestiku laiendamiseks ning Common~Voice eestikeelset osa hindamiseks; see näitab konkreetse rakenduse, mille tarbeks olemasolevad keeleressursid teenivad ühte privaatsuskeskset, kohaliku riistvara nutikodu kasutusjuhtumit.

* **Kiirkirjutaja ja eestikeelse kõnetuvastuse kogukond:** Käesolev töö ei dubleeri kõnetuvastust, vaid lisab eestikeelse hääljuhtimise toru puuduva eelmise lüli (äratussõna). Selle täienduse olemasolu suurendab Kiirkirjutaja praktilist kasutusväärtust nutikodu kontekstis.

* **ESPHome ja sellel põhinevate riistvaraprojektide kogukond (sh ESP32-S3 Korvo-2 platvormi kasutajad):** Töö annab konkreetse mudelifaili, kvantiseerimise ja \texttt{tensor\_arena} mahuhinnangu (148\,KB mudel, ${\sim}45\text{--}50$\,KB töömälu), mis on otse rakendatav ESPHome manifestides.

* **Avatud lähtekoodiga privaatsust eelistavad tehnoloogiaajakirjanikud ja kogukonna blogijad (nt Home Assistant blogi, Linux-suunalise meedia esindajad):** Esimene avalikult dokumenteeritud eestikeelne lokaalne äratussõna pakub konkreetset näidisjuhtumit, mille ümber on võimalik koostada arvustusi ja juhendeid pilvevaba hääljuhtimise teemal.

* **Tarkvaraarenduse metoodika uurijad, keda huvitab agentpõhine arendus (\emph{agentic engineering}):** Töö esitab läbipaistva refleksiooni selle kohta, kuidas tehisagentidega kiirendatud tööriistaehitus nihutab pudelikaela teostuselt tõendusmaterjalile, ilma et see leevendaks metoodilisi nõudeid. See on otsene panus arutellu, kuidas hinnata üksikautori projekte agentpõhise arenduse ajastul.

## 2. Osapooled, kellele töö oleks huvitav pärast täiendusi

* **Eesti tervishoiu- ja eakate hoolduse pakkujad (nt Tervisekassa, hooldekodud, koduhoolduse teenusepakkujad):** Lokaalne eestikeelne hääljuhtimine võiks toetada nõrgenenud nägemise või liikumispiiranguga eakaid igapäevastes nutikodu toimingutes.
    * *Vajalik täiendus:* Lisada eraldi peatükk vanemaealiste kõneleja-rühma testimisest, hindamisprotokoll prosoodiamuutuste (aeglane tempo, värisev hääl) ning kuuldeaparaadi mõju kohta, samuti turvaolulised stsenaariumid (nt \enquote{kutsu abi} käsklus).

* **Hariduse ja eripedagoogika kogukond (lapsed, kõnedefektidega kasutajad, logopeedid):** Eestikeelne lasteaiaealine kasutaja võiks puutuda kokku oma emakeelse hääleliidesega õpitarkvaras või abivahendites.
    * *Vajalik täiendus:* Lapse kõne korpuse kaasamine treeningusse ja hindamisse, eraldi vanusepõhine tuvastamismäära raporteerimine ning eetikakomitee heakskiit alaealiste osalemiseks kasutajatestis.

* **TalTechi ja Tartu Ülikooli keeletehnoloogia teadusrühmad (laiendamiseks teistele väikestele keeltele):** Käesolevas töös kirjeldatud protokoll võiks olla aluseks võro, seto, liivi või soome-ugri keelte äratussõnaprojektidele.
    * *Vajalik täiendus:* Foneetilise lähedusanalüüsi (sihtfraasiga sarnaste negatiivnäidete genereerimise) üldistatud kirjeldus, mis ei sõltuks ainult eesti keele konkreetsetest sõnadest, ning mitme keele kõrvutiv katse.

* **Küberturbe ja privaatsuse uurijad (CERT-EE, Andmekaitse Inspektsioon, akadeemilised \emph{adversarial ML} uurijad):** Pidev kuulamine kodus tõstatab privaatsus- ja ründevektorite küsimusi (nt sihilikud valeaktiveerimised, helireklaamiründed).
    * *Vajalik täiendus:* Eraldi turvariskide ja \emph{adversarial} stsenaariumide peatükk, GDPR-mõju hindamine, ohumudel (\emph{threat model}) lokaalse seadme jaoks ning katse sihiliku helisignaaliga rünnatava äratuse vastu.

* **Riigiasutused ja keelepoliitika kujundajad (Haridus- ja Teadusministeerium, Eesti Keele Instituut, Eesti Keele Sihtasutus):** Eesti keele digitaalse elujõu hoidmiseks on huvi, et nutikodu ja häälliidesed toetaksid eesti keelt.
    * *Vajalik täiendus:* Selgelt kvantifitseeritud keelepoliitiline raamistik (eesti keele praegune kaetus kommertshäälassistentides, eelis pilvevaba lokaalse lahenduse kasuks), poliitikasoovitused ning ühilduvuse nõuded riigi infosüsteemiga.

* **Kommertshäälassistente arendavad ettevõtted (nt Picovoice, Sensory, Home Assistant Voice'i tootmispartnerid):** Töö metoodiline panus võiks anda sisendit oma hindamisprotokollidele.
    * *Vajalik täiendus:* Otsene võrdlus Picovoice Porcupine'i suletud lähtekoodiga mudeliga ühisel testikorpusel (kui litsents lubab) ning täismahus 20--30 osalejaga kasutajatesti tulemused, mille põhjal saaks väiteid üldistada.

* **Robotitehnika ja autotööstuse häälliidese arendajad:** Servaseadmel jooksev äratussõna tuvastus on rakendatav ka mobiilrobotitel ja sõidukitel.
    * *Vajalik täiendus:* Mürarikka liikuva keskkonna katsed (mootorimüra, tuule müra), ümberseadistatava äratussõna juhend (mitte ainult \enquote{Kuule Kratt}) ning latentsuse mõõtmine reaalajas juhtimisstsenaariumites.

* **Klassikalise muusika ja meediatootmise kogukond (raadio, TV-tootjad):** Häälaktiveeruvate seadmete tahtmatu vallandamine TV-saates on tuntud probleem.
    * *Vajalik täiendus:* Eraldi TV- ja raadiosignaali (eestikeelse) korpuse peal hindamine ning soovitused saatesisu kujundajatele, kuidas vältida tahtmatuid aktiveerimisi.

* **Standardiseerimisorganisatsioonid (ETSI, ISO, EVS):** Äratussõna kvaliteedimõõdikute standardimine on alles algfaasis.
    * *Vajalik täiendus:* FAPH-i nelja variandi (raamistiku, skriptitud taasmängu, välitingimuste, kasutajatesti taasmängu) loendusreeglite ja runtime-loogika ametliku spetsifikatsiooni mustand, mis võiks olla aluseks tööstusstandardile.

* **Andmeteaduse ja masinõppe õppejõud (juhendmaterjal):** Töö dokumenteerib mitmeid pedagoogiliselt väärtuslikke vigu (andmelekke avastamine, prefiksi-õpe, kontrollpunkti valiku lühitee).
    * *Vajalik täiendus:* Eraldi õppematerjali variandi koostamine (näiteks lisa või eraldi artikkel), mille saaks kursusele lisada juhtumianalüüsina; praegune tekst on optimeeritud lõputöö formaadi, mitte õppevahendi jaoks.

* **Eelretsenseeritud akadeemiline kogukond (Interspeech, ICASSP, SLT konverentsid):** Mitmemõõtmeline hindamisprotokoll on potentsiaalselt avaldamiskõlblik panus.
    * *Vajalik täiendus:* Vähemalt kahe väikese ressursiga keele kõrvutiv rakendus (mitte ainult eesti keel), suurem osalejate arv kasutajatestis ning eraldi statistilise testi (nt McNemari test mudelipaaride vahel) kasutamine vahede usaldusväärsuse näitamiseks.

* **Tehnoloogiakiirendite, idufirmade tugiprogrammide ja innovatsiooniagentuuride esindajad (EAS, Tehnopol, Startup Estonia):** Avatud lähtekoodiga eestikeelne häälemootor võiks olla alus kohalikele toodetele.
    * *Vajalik täiendus:* Litsentsi- ja kommertskasutuse selgesõnaline kirjeldus, võimaliku ärimudeli ülevaade ning hinnang sellele, milline arenguetapp on enne tootestamist veel vajalik.

## Märkused

Analüüs põhineb üksnes lõputöö dokumenteeritud sisul ning ei ületa tõendatud väiteid: töö praegune kasutajatestide korraldamine on alles planeerimisfaasis (\texttt{kratt user-test} tööriistaga, sihiks 20--30 osalejat) ning juurutuskandidaat \texttt{v16c} ootab veel ESPHome + \texttt{voice\_assistant} integreeritud Korvo-2 valideerimist. Mitmed esimese etapi osapooled saavad seetõttu tööst praegu kasu eelkõige metoodika ja vahendiraamistiku tasemel; tootmisküps konkreetne mudelijuurutus eeldab kasutajatesti lõpetamist.
