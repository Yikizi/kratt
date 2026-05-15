---
source_prompt: Rakenduse_kasutatavus_ligipääsetavus.txt
prompt_type: evaluative (heuristiline UX/ligipääsetavuse audit) — kontekstis suuresti rakendamatu
generated: 2026-05-07
---

# Rakenduse kasutatavuse ja ligipääsetavuse audit — kontekstipõhine puudelünga selgitus ja parim võimalik hinnang

## 0. Rakendatavuse hinnang ja metoodiline lünk

Algne viip eeldab sisendiks **rakenduse ekraanipilte või videot** ning palub UX-eksperdil viia läbi heuristiline audit Jakob Nielseni 10 heuristika ja WCAG AA/AAA visuaalsete kriteeriumide alusel (värvikontrast, tüpograafia, klikitavate alade suurus, fookuse nähtavus, vigade visuaalne signaal). Käesolev sisend ei ole aga rakenduse visuaalne artefakt, vaid **bakalaureusetöö LaTeX-tekst** eestikeelsest äratussõna tuvastusest ESP32-S3 mikrokontrolleril. Olemasolevad failid on töö sissejuhatus, metoodika, arutelu, kokkuvõte ja kaks annotatsiooni; ei ühtki ekraanipilti, kasutajaliidese kirjeldust pikselitäpsuses ega videosalvestust.

Seetõttu on viip **rangelt vormistatud kujul rakendamatu**: ilma visuaalita ei saa hinnata kontrastisuhteid, fookusrõngaid, ikoonide äratuntavust ega \enquote{microcopy}-d nupul, mida pole olemas. Kõik viie kasutatavusheuristika alamhinded (õpitavus, efektiivsus, meeldejäävus, veahaldus, rahulolu) eeldavad konkreetset interaktsioonipinda, mida bakalaureusetöö dokument ei paku.

Allpool on **parim võimalik tõlgendus**, mis kohandab viipa kahele asjale, mis töös tegelikult eksisteerivad ja mille \enquote{kasutajaliides} on kirjeldatud kas tekstiliselt või kavandatava artefaktina:

1. **Kasutaja vahetu kogemus eestikeelse äratussõnaga \enquote{Kuule Kratt}** — see on tegelik \enquote{front-end} (hääleliides), mille kasutatavus on töös eksplitsiitselt püstitatud uurimisülesandena (vt sissejuhatus ja §\ref{sec:user-test-methodology}).
2. **Käsureatööriistad `kratt user-test`, `kratt validate-user-test`, `kratt replay-user-test`, `kratt summarize-user-test`** — need on töös ainsad tegelikult eksisteerivad ja dokumenteeritud kasutajaliidesed ja eksperimendi läbiviija puutub nendega vahetult kokku (vt §\ref{sec:user-test-methodology}).

Mõlemal juhul ei saa hinnata WCAG AA/AAA visuaalseid kriteeriume, sest ühel pole graafilist liidest (kõneliides) ja teisel on ASCII-tekstiline (CLI). Asendan visuaalse ligipääsetavuse osa **mitte-visuaalse ligipääsetavusega**: kõneliidese puhul tähendab see auditiivse signaali, latentsuse ja eksimustaluvuse hindamist; CLI puhul tähendab see ekraanilugeja ja klaviatuurikasutaja kogemuse arvestamist.

Kus aluseks olev tekst ei sisalda piisavalt konkreetseid disainifakte, **ei väljamõelda** numbrilisi mõõteid (kontrastisuhted, klõpsuala suurus pikslites jms), vaid raporteeritakse \emph{informatsiooni puudumine}. Hinded antakse alla 10 vaid seal, kus tekst ise paljastab puudujäägi.

---

## 1. Kasutatavuse detailne analüüs

Hinnatakse kahte tegelikku liidest paralleelselt, sest viip nõuab struktureeritud tabelivormi: **(A) hääleliides \enquote{Kuule Kratt}** ja **(B) `kratt user-test` CLI-perekond**.

### 1.1. Õpitavus (Learnability)

* **Hinne:** A 6/10  •  B 7/10
* **Analüüs:**
  * **(A) Hääleliides.** Tekst ütleb, et äratusfraas on \enquote{Kuule Kratt} — kahesõnaline eestikeelne fraas, mille puhul autor ise rõhutab eestlasele tuttavat mütoloogilist konteksti (kratt). See toetab õpitavust: fraas on häälduses loomulik ja kõlab keele rütmi sees usutavalt. Õpitavust pärsib aga töös avatult dokumenteeritud risk: §\ref{sec:benchmark-gap} nimetab konkreetselt segiajamisriski sõnadega \enquote{kuule rott}, \enquote{kuule kraam} ja \enquote{kule}-prefiksiga juhtumid, samuti tekitab \enquote{kuule}/\enquote{kule} hääldusvarieeruvus reaalsetel kõnelejatel madalama tuvastamismäära kui sünteetilistel klippidel. See tähendab, et **uus kasutaja ei saa esimesel katsel kindlat tagasisidet**: kui süsteem ei vallandu, ei ole võimalik liidesest endast aru saada, kas öeldi valesti, räägiti liiga kaugelt või on mudel lihtsalt selle hääldusega tundlikum. See on klassikaline \emph{Nielseni heuristika #1 — süsteemi staatuse nähtavus} rikkumine: kasutaja ei saa teada, miks ta ootab vastust.
  * **(B) CLI.** Käsuhulk on kavandatud nimetussüsteemiga, mis on **kõrgelt õpitav**: `kratt user-test`, `kratt validate-user-test`, `kratt replay-user-test`, `kratt summarize-user-test`. Verbid (test, validate, replay, summarize) järgivad ühtset infinitiivseid mustrit ja domeenisõnastik (`user-test`) on järjekindel. Kuid metoodika peatükk ei kirjelda, kas käsud annavad esmakordsel käivitamisel \texttt{--help}-juhise, kas eksisteerib näitepruugi rida või paigaldusjuhend, mistõttu uus eksperimendi läbiviija peab tuginema kas autori juhendamisele või lähtekoodile.
* **Soovitused:**
  * (A) Lisada audiosignaal aktiveerumise hetkele (\enquote{didong}) ja teine, eristuv signaal mitteaktiveerumise puhul, kui kasutaja sõna öeldi, kuid lävi jäi alla. Töös kirjeldatud Wyoming-protokoll seda toetab; selle kasutuselevõtt on \emph{Nielseni heuristika #1 — süsteemi staatus} kõige odavam fix.
  * (A) Demonstreerida õige hääldus kasutajatesti onboardingu osana lühikese näidisfailiga (üks kõneleja \enquote{Kuule Kratt} õigel tempol), enne kui osaleja ise ütleb. See vähendab \enquote{Kule/Kuule} segiajamisbiasi, mille töö ise §\ref{sec:benchmark-gap} all tuvastab.
  * (B) Iga `kratt user-test*` käsu juurde lisada `--help` esimene kasutuse rida koos näitega ja minimaalne edukäigu transkript. Hetketekst kirjeldab funktsionaalsust akadeemiliselt (\enquote{loob iga katse kohta ühe märgendatud rea failis \texttt{trials.jsonl}}), kuid ei dokumenteeri kasutajavoogu samm-sammult.

### 1.2. Efektiivsus (Efficiency)

* **Hinne:** A 5/10  •  B 8/10
* **Analüüs:**
  * **(A) Hääleliides.** Kogenud kasutaja eesmärk on käivitada kodumasin (\enquote{Kuule Kratt, lülita köögitule sisse}) ühe lausungi jooksul. Töös eesmärgistatud sihiväärtused — pidevvoo FAPH < 1 ja lähikõne tuvastamismäär $\geq$ 0,95 — on sõnastatud eksplitsiitselt sissejuhatuses; arutelu kinnitab, et reaalsetel \enquote{Kule}-hääldustel jääb tuvastamismäär juurutuslävel \emph{madalamaks} kui TTS-positiivsetel klippidel (vt sissejuhatus, §\ref{sec:benchmark-gap}, kokkuvõte). Praktikas tähendab see, et kasutaja peab vahel fraasi kordama — see on otsene **efektiivsuskaotus** ja sama ka \emph{Nielseni heuristika #7 — paindlikkus ja efektiivsus} rikkumine: puudub kiirtee, mis võimaldaks tuvastust ka veidi erineva hääldusega.
  * **(B) CLI.** CLI-perekond on töövoo seisukohast efektiivne: salvesta → valideeri → taasmängi → kokkuvõte. See modelleerib nelja loomulikku lülingut ja hoiab eksperimendi läbiviija peast väljaspool, et iga sessioon järgib sama struktuuri. Märkimist väärt on see, et autor kasutab eraldi `replay`-sammu mitme varimudeliga (\texttt{v16c}, \texttt{expert-a}, \texttt{expert-b2}, \texttt{v6-residual}, \texttt{v10}, \texttt{v15}, \texttt{expert-a+expert-b2}), mis tähendab, et osaleja ei pea fraasi kordama iga mudeli jaoks. See on **väga hea efektiivsusotsus**.
* **Soovitused:**
  * (A) Lisada juurutuse kõrvale **kahe tunnijätkamise (latching) režiim**: kui esimene aktivatsioon ebaõnnestus, jääb mikrofon 1,5 s veel \enquote{kuula valmis} olekusse ja teine kordusütlus aktsepteeritakse alama lävega (saavutamata kasvavad valeaktiveeringud, kui esimese poole on juba olnud signaal). See on klassikaline \emph{kaskaadne kinnitus}, mida töö §\ref{sec:future-cascade} all juba teoreetiliselt mainib.
  * (B) Kaaluda `kratt user-test --resume` võimalust: kui sessioon katkeb, jätkata samast triaalist, mitte algusest. Tekstist see ei selgu.

### 1.3. Meeldejäävus (Memorability)

* **Hinne:** A 8/10  •  B 6/10
* **Analüüs:**
  * **(A) Hääleliides.** Kahesõnaline foneetiliselt eristuv eestikeelne fraas \enquote{Kuule Kratt} on **väga meeldejääv**: mütoloogiline konnotatsioon, alliteratsioon (\enquote{K}-K), lühike pikkus (0,8–1,2 s töö enda mõõtmise järgi). Naasev kasutaja ei pea midagi uuesti õppima.
  * **(B) CLI.** Käsud `kratt user-test`, `validate-user-test`, `replay-user-test`, `summarize-user-test` on järjekindlad, kuid **postfiksiline kordumine** (\texttt{-user-test}) tähendab, et ühelt teisele üleminek nõuab tabamise asemel kogu nimega kirjutamist. Seda saab leevendada shellitäiendamisega, kuid tekst ei kirjelda, kas need on `kratt`-CLI sees alamkäsud (`kratt user-test validate`) või iseseisvad. Praegusel kujul käsud paaripäevase pausi järel võivad sundida kasutajat `kratt --help` käivitamisele, et sõnajärje meelde tuletada.
* **Soovitused:**
  * (B) Reorganiseerida nimeruum kahe tasandi mustrisse, mis on shellitäiendamise ja meeldejäävuse jaoks parem: `kratt user-test record`, `kratt user-test validate`, `kratt user-test replay`, `kratt user-test summarize`. See on \emph{Nielseni heuristika #4 — järjepidevus ja standardid}, mis järgib `kubectl`/`gh`/`docker` mustrit.

### 1.4. Veahaldus (Error Management)

* **Hinne:** A 4/10  •  B 7/10
* **Analüüs:**
  * **(A) Hääleliides.** Töö ise paljastab kõige selgema veahalduse probleemi: kasutajal pole praegu ühtegi viisi vahet teha nelja erineva ebaõnnestumise vahel: (1) ütlesin liiga kaugelt, (2) ütlesin valet hääldust (\enquote{Kule}, mitte \enquote{Kuule}), (3) ütlesin õigesti, kuid mudel ei tabanud (FRR-tabamus), (4) süsteem ei kuule mind seadme tehnilise tõrke tõttu. Kõik need annavad sama vastuse: vaikus. See on **kriitiline veahalduse lünk** ja \emph{Nielseni heuristika #9 — aita kasutajatel tuvastada, diagnoosida ja taastuda vigadest} otsene rikkumine.
  * **(B) CLI.** Tekst kirjeldab `kratt validate-user-test` käsku, mis kontrollib \enquote{katsete arvu, WAV-failide olemasolu, kanalite ja diskreetimissageduse vastavust ning liiga madala RMS-i hoiatusi}. See on \textbf{eeskujulik} — vea avastamine kohe peale salvestust, mitte hilisemas analüüsis, on tugev veaennetuse muster (\emph{Nielseni heuristika #5 — vigade ennetamine}). Hinde langetab see, et ei ole kirjeldatud, kas viga ütleb operaatorile selgelt, mida edasi teha (nt \enquote{kanal 2 puudub — palu osalejal sessioon korrata} vs. lihtsalt veakood).
* **Soovitused:**
  * (A) Lisada lühike, foneetiliselt eristuv \emph{negatiivne} signaal (nt madala tooniga \enquote{plonk}), mis vallandub, kui mudel registreeris kõnesignaali, kuid lävi jäi piiri lähedale alla. See annab kasutajale informatsiooni \enquote{ma nägin sind, aga lävi jäi alla} — \emph{Nielseni heuristika #1 + #9} korraga. Tehniliselt nõuab see kahe-läve süsteemi (`activation_threshold`, `attempted_threshold`), mis ei suurenda valeaktiveeringuid, kuid annab tagasisidet.
  * (A) Kaaluda visuaalse staatuse LED-i seadme küljel, mille värv kodeerib (a) mikrofon kuulab, (b) ümbruskonna helitase liiga madal, (c) tuvastatud osaline signaal, (d) edukas aktiveerumine. **Hoiatus:** see ei vasta WCAG-värvipimeduse nõuetele, kui ainus signaal on värv — vaja oleks lisada vilkumise/särituse muster (vt §2.2).
  * (B) `kratt validate-user-test` peab vea korral väljastama **konkreetse parandustegevuse** soovituse, mitte üksnes vea kirjelduse. Praegu pole tekstis selgelt kinnitatud, kas seda tehakse.

### 1.5. Rahulolu (Satisfaction)

* **Hinne:** A 6/10  •  B 7/10
* **Analüüs:**
  * **(A) Hääleliides.** Kasutaja vaatest on rahulolu otseselt seotud sellega, kui sageli süsteem kasutaja kõrva järgi \enquote{ei kuula}, ja kui sageli aktiveerub valesti (FAPH). Töö ise sõnastab subjektiivse rahulolu mõõtmise plaani UMUX-Lite skaala kaudu (§\ref{sec:user-test-methodology}), mis on \textbf{metoodiliselt korrektne valik} (Lewis & Sauro). Hetkeline empiiriline pilt — TTS-klippidel kõrge tuvastamismäär, päris \enquote{Kule}-kõnel madalam — viitab, et tüüpiline esimene kasutuskogemus võib olla **frustreeriv**, eriti kui kasutaja ütleb \enquote{Kule kratt} (mis on töös tuvastatult sage hääldusvariant). Usaldusväärsuse hinde tõstab kõva osa: süsteem on **lokaalne, ilma pilveteenusteta** ja seda väärtustab privaatsusteadlik eestikeelne kasutaja.
  * **(B) CLI.** Käsureatööriist on eksperimendi läbiviija jaoks ja selle rahulolu tõuseb tugevalt sellest, et samad WAV-id mängitakse mitme mudeli vastu. See **vähendab eksperimendi koormust** ja on hea uurija UX. Hinnet langetab dokumentatsiooni puudus tekstis (kasutusnäidised, edukuvad).
* **Soovitused:**
  * (A) Onboarding-stsenaariumi (10-min kasutajatest) algusesse lisada **harjutusring**: kasutaja ütleb \enquote{Kuule Kratt} kolm korda ja saab kohese visuaalse/auditiivse tagasiside, kas tuvastati. Selle järel toimub mõõdetav osa. See vähendab esmase frustratsiooni mõju UMUX-Lite skooridele ja on Nielseni \emph{onboarding} parima praktika järgimine. Töö §\ref{sec:user-test-methodology} kirjeldab juba 5 puhast positiivset, kuid ei tee neist eksplitsiitselt \enquote{harjutusringi}; piir nende ja mõõdetava osa vahel võiks olla konsentreeritum.
  * (B) Lisada `kratt summarize-user-test` käsu väljundisse **inimloetav lühikokkuvõte** (nt \enquote{14 osalejat, mediaan-tuvastamismäär 0,87, sarnaste fraaside FPR 0,12}) lisaks JSON-väljundile. See vastab \emph{Nielseni heuristika #8 — esteetiline ja minimalistlik disain}.

---

## 2. Koondhinnangud ja muud tähelepanekud

### 2.1. Üldine Kasutatavus (Overall Usability)

* **Hinne:** A 6/10  •  B 7/10
* **Kokkuvõte:**
  * **Tugevused.** Hääleliidese fraasivalik (\enquote{Kuule Kratt}) on foneetiliselt ja kultuuriliselt hästi maandatud. Eksperimendi tööriistastik (`kratt user-test*` perekond) on metoodiliselt eeskujulik — eraldi `validate`-samm on UX-i jaoks oluline ja vähendab andmehävimist. Lokaalne juurutus ilma pilveta annab tugeva privaatsuspõhise rahulolu.
  * **Nõrkused.** Hääleliidese kõige suurem nõrkus on kasutajale puuduv tagasiside, kui aktiveerumine ebaõnnestub — kasutaja ei tea, kas mudel kuulis halba hääldust, oli liiga kaugel, või tehniliselt ei töötanud. Töös eksplitsiitselt dokumenteeritud \enquote{Kuule}/\enquote{Kule} hääldusvariatsiooni risk ja TTS-vs-päris-kõneleja tuvastamismäära langus võivad tüüpilise esimese kasutaja kogemuse muuta frustreerivaks. CLI poolel jääb dokumentatsiooni-UX puuduliku kirjelduse tasemele.

### 2.2. Üldine Ligipääsetavus (Overall Accessibility)

* **Hinne:** Visuaalsel teljel **ei rakendu / 10** (graafiline liides puudub). Mitte-visuaalsel teljel **A 5/10  •  B 6/10**.
* **Analüüs:**
  * **WCAG AA/AAA visuaalsed kriteeriumid (kontrastisuhted, klikitavate alade suurus, fookusrõngad, vigade visuaalne signaal).** Sisendmaterjalist ei ole võimalik hinnata: töö ei kirjelda graafilist liidest pikselitäpsuses ega esita ekraanipilte. **Informatsioon puudub.** Audit ei väljamõtle numbreid.
  * **Mitte-visuaalne ligipääsetavus (kõneliidese ja CLI-spetsiifilised kriteeriumid).**
    * \textbf{Kõneliides.} Hääljuhtimine on **iseenesest kasulik motoorse puudega kasutajale**, kes ei saa puutetundlikku ekraani kasutada — see on positiivne kaasamise samm. **Negatiivne pool:** lahendus eeldab kõnevõimet ja eestikeelset hääldust ilma märkimisväärse kõnehäireta. Töö ei käsitle eksplitsiitselt **kõnehäirega kasutajaid, lapsi ega tugeva aktsendiga eestikeelseid kõnelejaid**; arutelu §\ref{sec:fourth-round} möönab seda kui võimalikku neljandat valideerimiskihti, mis pole veel teostatud. Kuulmispuudega kasutaja jaoks ei paku praegune hääleliides midagi, kuid see on kõneliidese kategooriaomane piirang, mitte konkreetne disainiviga.
    * \textbf{CLI.} Käsureatööriistad on **ekraanilugejaga ühilduvad** (eeldatavalt; tekst ei kirjelda värvikoodide kasutust väljundis). Kui `kratt validate-user-test` näiteks kasutab punast/rohelist värvi vea/edu signaaliks ilma teksti dubleerimiseta, on see WCAG 1.4.1 (\enquote{Use of Color}) rikkumine — kuid sellele tekstis vihjet ei ole, seega **informatsioon puudub** ja hinnet on antud konservatiivselt.
* **Soovitused:**
  * (A) Lisada \enquote{push-to-talk} alternatiiv (füüsiline nupp seadme küljel), mis ei vaja äratusfraasi. See toetab kõnehäirega kasutajat, lapse rasket äratamist ja mitmesugust aktsenti. Tehniliselt on see ESPHome konfiguratsioonifaili paari rea lisamine.
  * (A) Kasutajatesti onboarding-protokollis lisada **demograafiline ja keelekasutuslik küsimus** (emakeel, kõnehäire, tugev aktsent), et hindamisel saaks need alagrupid eristada. Töö §\ref{sec:user-test-methodology} ei kirjelda neid eksplitsiitselt.
  * (B) Auditi käigus tegelikus CLI väljundis kontrollida, kas värv on dubleeritud sümboliga (`OK` / `FAIL` / `WARN`) ega ole ainus eristusviis. Lähtekoodist see selguks, käesolevast tekstist mitte.
  * **Üldine ligipääsetavus eestikeelse väikesekeelelise lahendusena** on töö üks alusväärtustest: lokaalne ja eestikeelne. Selle eelduslik tugevus tasakaalustab tuvastamise ebaühtluse riski.

### 2.3. Keeleline korrektsus ja teksti selgus (Microcopy)

Kuna sisend ei ole rakenduse ekraanipilt vaid bakalaureusetöö LaTeX-tekst, ei saa hinnata nuppude silte ega veateateid. Hinnatud on **töötekstis tsiteeritud käsunimede, fraaside ja kasutaja-puutuvate stringide** korrektsust.

* **Kirja- ja grammatikavead:**
  * **Keelelisi vigu (kirjavigu, grammatikavigu) tsiteeritud kasutaja-puutuvates stringides ei tuvastatud.** Käsud (`kratt user-test`, `kratt validate-user-test`, `kratt replay-user-test`, `kratt summarize-user-test`) on ingliskeelsed, järjekindlad ja õigesti vormistatud. Äratusfraas \enquote{Kuule Kratt} on eesti keele reeglite järgi korrektne (käskiv kõneviis 2. p ainsus + nimisõna nominatiivis pärisnimena). Töö enda akadeemiline tekst sisaldab eestikeelseid termineid (\enquote{voogedastushindamine}, \enquote{tuvastamismäär}, \enquote{valevallandumised}), mis on järjekindlad.
* **Segane sõnastus (potentsiaalne, kui sellest saaks edaspidi rakenduse microcopy):**
  * \textbf{Käsunimi `kratt summarize-user-test`} on kasutajatesti läbiviija jaoks selge, kuid liidesest pole võimalik aru saada, kas \enquote{summarize} tähendab JSON-väljundit, inimloetavat aruannet või mõlemat. **Soovitus:** kui CLI väljub vaikimisi JSON-iga, lisada CLI tasandil flag `--human` või `--report` (tabelvorm), mis on eksperimendi läbiviijale loomulikum.
  * \textbf{Hääleliidese sõnastust} (mida kasutaja näeks rakenduse onboardingus, kui see oleks olemas) tekstis ei eksisteeri — seda ei saa hinnata. **Märkus:** soovitatav on enne kasutajatesti välitööd kirjutada üheleheküljeline juhend osalejale, mille microcopy tuleb eraldi keeleliselt üle vaadata. Tekstis seda ei mainita.
  * \textbf{FAPH ja FRR}-laadne žargoon (false accepts per hour, false rejection rate) on töös korralikult avatud sissejuhatuses ja metoodikas (\enquote{FAPH ehk valevallandumiste arv tunnis}). Kui sama akronüüm satub kunagi kasutaja-puutuvasse liidesesse (nt seadistuse paneel Home Assistantis), tuleb see asendada eestikeelse selgitusega; akadeemilises tekstis on see aga sobiv.

---

## Kokkuvõte ja piir

Käesolev audit on tehtud parima võimaliku tõlgendusena viibast, mis ootab visuaalset rakendust. Sisendina antud bakalaureusetöö ei ole rakenduse ekraanipilt ega video, mistõttu **WCAG visuaalsete kriteeriumide (kontrast, klikitavate alade suurus, fookusrõngad) numbriline hindamine ei ole võimalik ja jäetakse \enquote{informatsioon puudub} märkega**. Hinnati kahte tegelikku liidest, mis tööst ekstraheeritavad:

1. eestikeelse äratussõna \enquote{Kuule Kratt} hääleliidest — kasutatavus 6/10, ligipääsetavus mitte-visuaalsel teljel 5/10;
2. `kratt user-test*` käsureaperekonda — kasutatavus 7/10, ligipääsetavus mitte-visuaalsel teljel 6/10.

Peamised praktilised paranduskohad, mis tulenevad töö enda dokumenteeritud probleemidest (mitte väljamõeldud puudustest):

* **Hääleliides peab andma selgema tagasiside ebaõnnestunud aktiveerumise kohta** (kahe-läve süsteem, auditiivne \enquote{ma nägin sind, aga lävi jäi alla}-signaal), kuna \enquote{Kuule}/\enquote{Kule} hääldusvariatsioon on töös tuvastatud kui reaalsete kõnelejate tuvastamismäära langetav põhirisk.
* **Onboardingusse lisada lühike harjutusring** enne mõõdetavat 10-minutilist sessiooni, et eristada esmane õpitavuse hõõrdumine subjektiivse rahulolu mõõtmisest.
* **CLI nimeruum tasub kahetasandiliseks ümber kujundada** (`kratt user-test record/validate/replay/summarize`) shellitäiendamise ja meeldejäävuse parandamiseks.
* **Push-to-talk alternatiiv ja demograafiline alagrupi-kategoorium** parandavad ligipääsetavust kõnehäirega ja tugeva aktsendiga kasutajatele, mida arutelu §\ref{sec:fourth-round} ise nimetab võimaliku neljanda valideerimiskihina.
