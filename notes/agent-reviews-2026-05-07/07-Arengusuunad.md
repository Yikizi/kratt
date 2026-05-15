---
source_prompt: 03_Lõputöö_alamosad/Arengusuunad.txt
prompt_type: generative
generated: 2026-05-07
---

# Arengusuunad: eestikeelse äratussõna projekti edasiarendamine

Käesolev dokument koondab analüüsi põhjal tuvastatud edasiarendamise suunad projektile \enquote{Kratt}. Suunad on jaotatud nelja kategooriasse ja iga kategooria sees järjestatud olulisuse järgi kahanevalt: eespool ideed, mis annavad tööle või lahendusele suurimat lisaväärtust või on hädavajalikud järgmised sammud.

## Metodoloogilised ja teaduslikud jätku-uuringud

1. **Stsenaariumipõhise hindamiskorpuse loomine ja avaldamine** – Töö arutelupeatükis (§\ref{sec:benchmark-gap}) põhjendatakse vajadust kahetunnise annoteeritud stsenaariumipõhise salvestuse järele, mis kataks vaikuse, taustamuusika, vestluse, foneetiliselt sarnased fraasid ja äratusütlused. Selle korpuse koostamine, anonüümistamine ja avaldamine madala ressursiga keelte uurimisühenduses muudaks töö metoodilise panuse kontrollitavaks ja ülekantavaks. Praegu kirjeldab töö metoodikat, kuid ei paku selle teostamiseks vajalikku jagatud ressurssi.

2. **Neljanda valideerimisringi süstemaatiline läbiviimine** – Autor möönab ausalt (§\ref{sec:fourth-round}), et neljas valideerimiskiht --- kasutuskogemustele tuginev --- jääb käesolevast tööst välja. Pärast 20--30 osalejaga kasutajatesti tuleks samme korrata laiemal valimil, hõlmates aktsente, häälduse vahevorme, lapse kõnet ning vaikseid äratusi pikkade vaikuseperioodide järel. See sulgeks töö poolt avatud metoodilise tsükli ja annaks kvantitatiivse aluse väitele, et kolmest ringist piisab.

3. **Foneetiliselt sarnaste negatiivsete näidete süstemaatiline taksonoomia** – Töö dokumenteerib mitu konkreetset segiajamise riski (\enquote{kuule rott}, \enquote{kuule kraam}, prefiks \enquote{kuule}, segiminek \enquote{kule}/\enquote{kuule}). Edasiarenduseks oleks vajalik foneetiliselt sarnaste fraaside taksonoomia ja genereerimise reeglistiku väljatöötamine, mis tugineks eesti keele foneetikale (sh kvantiteediastmed) ning võimaldaks mehhaanilist genereerimist suvalisele kahesilbilisele äratussõnale.

4. **Domeeninihke kvantitatiivne mõõtmine** – Praegu kirjeldab töö domeeninihke riski peamiselt kvalitatiivselt (§3.3). Süstemaatiline uuring, mis varieeriks mikrofoni, ruumi ja kõneleja eraldi, võimaldaks lahutada nende panust valeaktiveeringutesse ja anda numbrilise hinnangu sellele, kui suur osa FAPH-i lahknevusest klipi-tasemest pidevasse helivoogu tuleneb akustilise keskkonna nihkest, mitte mudeli üldistusvõime piiridest.

5. **\enquote{Kuule}/\enquote{Kule} hääldusvariantide eristamise eraldi mudeluuring} – Töö identifitseerib hääldusvariandi \enquote{Kule} kui peamise reaalsete kõnelejate tuvastamismäära langetaja. Sellele pühendatud uuring --- positiivse klassi tasakaalustamine, eraldi audit hääldusmustrite kohta ning treeningandmete sihipärane laiendamine just \enquote{Kule}-vormiga --- oleks loogiline iseseisev jätku-uuring.

6. **TTS-bias'i süstemaatiline mõõtmine eesti keele kontekstis** – Park et al.\ \cite{park2024adversarial} viidatud üldine TTS-iga treenimise eelistus on töös tunnistatud, kuid selle eestikeelne kvantifitseerimine (XTTS, Neurokõne, Fish S2 Pro võrdlus identsel testikomplektil) on iseseisvalt avaldatav metoodiline panus, mis aitaks teisi eesti keeletehnoloogia projekte.

## Tehnilised täiendused

1. **Kaskaadarhitektuuri (kaheastmeline detektor) prototüüpimine** – Töö osutab juba (§\ref{sec:future-cascade}) konkreetsele edasiarendusele: teine aste, mis kontrollib eraldi sõnade \enquote{kuule} ja \enquote{kratt} kohalolu ning järjekorda. Kirjandus kinnitab selle suuna küpsust \cite{gruenstein2017cascade,apple_voice_trigger_2023}; teostuse põhiraskus on hoida esimene aste niivõrd selektiivne, et teine aste ei kaotaks reaalseid äratusi. See on loogiline järgmine versioon (nt v17/v18), mis tugevdaks fraasi struktuurikontrolli.

2. **Voogedastuskontekstis raskete negatiivsete näidete genereerimine** – Töö märgib (§\ref{sec:benchmark-gap}, põhjus 3), et klipi-tasemel sarnaste fraaside test ei kajasta voogedastuskonteksti, kus koartikulatsioon ja sisemine olek muudavad pilti. Tehniline edasiarendus on koostada testikomplekt, mille klipid on spetsiaalselt voogedastusrežiimis genereeritud (lause-keskses asendis, varieeruva eelkonteksti ja järelkontekstiga), ning lisada need treeningusse.

3. **Mudeli adaptiivne lävi keskkonna järgi** – Praegu on lävi külmutatud staatiliselt (\texttt{cutoff} $\geq 0{,}97$). Tehniliselt huvitav edasiarendus oleks adaptiivne lävi, mis kohaneb taustaheli olukorraga: vaikuses madalam lävi parema tundlikkuse jaoks, taustamuusika või televisiooni korral kõrgem lävi valeaktiveeringute vältimiseks. See nõuab kasutuskogemuse jaoks mõõdetavat valgustaustaheli klassifikaatorit, kuid võiks lahendada osa tundlikkuse-selektiivsuse kompromissist.

4. **\texttt{openWakeWord} otsast lõpuni eestikeelse versiooni treenimine ja võrdlus} – Töö metoodika kirjeldab \texttt{openWakeWord} kaasamist võrdlusraamistikuna, kuid arutelu jätab selle Raspberry Pi sihtplatvormi kontekstis lahti. Otsast lõpuni treenitud eestikeelse \texttt{openWakeWord} mudeli avaldamine annaks Home Assistanti kogukonnale teise rea (Raspberry Pi 5 hostidele) ning võimaldaks kahe raamistiku otseseid mudelikvaliteedi võrdlusi identsel hindamisprotokollil.

5. **Kvantiseerimise asümmeetriad ja valideerimise dünaamika} – Praegune mudel \texttt{v16c} on 148\,KB, varasemad ${\sim}57$\,KB. Töö ei dokumenteeri kvantiseerimisjärgse skoorinihke süstemaatilist mõõtmist (post-training quantization vs.\ kvantiseerimisteadlik treening). Edasiarenduseks oleks võrdlev katse, mis näitab, kas kvantiseerimisteadlik treening parandab eriti reaalsete \enquote{Kule}-hääldajate tuvastamismäära.

6. **Mitme äratusfraasi tugi (\enquote{Kuule Kratt} + alternatiivne fraas)} – Töö hindab ainult ühte fraasi. Mitme paralleelse äratusfraasi tugi sama mudeli sees võimaldaks kasutajal valida (nt \enquote{Tere Kratt}, \enquote{Kuule Sõber}), mis tõstaks lahenduse atraktiivsust ja annaks ühtlasi metoodilise võrdluse: kas üks fraas üldistub paremini kui teine, ning kas mitme fraasi treenimine ühes mudelis halvendab või parandab üksiku fraasi kvaliteeti.

7. **Energiakulu mõõtmine ESP32-S3-l ja unerežiimi optimeerimine} – Töö dokumenteerib mälunõuded (mudel + tensor\_arena ${<}200$\,KB), kuid ei käsitle energiakulu pikaajalise alati-aktiivse seadme kontekstis. Patareipõhise satelliidi (nt nupuga seinaseade) jaoks on see kriitiline mõõdik. Edasiarendus on konkreetne energiakulu profileering ja unerežiimi-koos-VAD-iga arhitektuuri prototüüp.

## Kasutuskogemuse parendused

1. **Kasutajatesti tulemuste süstemaatiline tagasisidekanal mudelisse} – Töö metoodika (§\ref{sec:user-test-methodology}) selgelt eraldab kasutajatesti heli hindamis- ja treeningandmestiku vahel. Pärast lõputöö kaitsmist on loogiline edasiarendus loa-põhine, GDPR-iga ühilduv tagasisidekanal, mis võimaldab kasutajatesti positiivseid näiteid sihipäraselt treeningusse lisada (näiteks raskeid \enquote{Kule}-hääldajaid). See nõuab eraldi nõusolekuvoogu ja säilitamispoliitikat, kuid on praktiliselt vajalik mudeli pikaajaliseks parandamiseks.

2. **Kohalik veaaruandluse tööriist kasutajatele} – Tööstuses on tavaline, et kasutaja saab \enquote{see ei tuvastanud}/\enquote{see vallandus valesti} tagasisidet anda lokaalsel seadmel ühe nupuvajutusega. Selline lihtne mehhanism (nt füüsiline nupp Korvo-2 plaadil või Home Assistanti automaatika) muudaks kasutajatestile järgnevad tagasisidetsüklid odavaks ja võimaldaks kogukonna-põhise mudelitäiustuse.

3. **Subjektiivse rahulolu pikaajaline mõõtmine (post-deployment uuring)} – Töö plaanitud küsimustik (§\ref{sec:user-test-methodology}) on ühekordne sessioonijärgne. Pärast paigaldust kodusse oleks väärtuslik korrata UMUX-Lite mõõtmist 1, 4 ja 12 nädala järel, et tuvastada \enquote{häiriv valeaktiveering} fenomeni kumulatiivset mõju kasutaja usaldusele.

4. **Häälasenduse pakkumine kasutajaga seotud äratusfraasiks} – Lähtudes kirjandusest \cite{rikhye2021personalized} ning töö enda \enquote{Kule}-leiust, oleks kasutuskogemuse jaoks mõjukas iga kasutaja jaoks lühike kalibreerimisrutiin (3--5 sõna ütlust), mis kohandab läve või lisab isikliku hääle väikeseks teiseks astmeks. See ei nõua täielikku ümbertreenimist, kuid lahendab pere-spetsiifilisi tundlikkuse-erinevusi.

5. **Mitme keele paralleelne tugi ühel seadmel} – Eesti kodude lingvistiline reaalsus on sageli mitmekeelne (eesti + vene + inglise). Lisamõõdikuna võiks uurida, kuidas mudel käitub teiste keelte taustakõnel ning kas multikeelse taustaheli korpus tuleks lisada treeningusse, et vältida keele-spetsiifilist tundlikkuse libisemist.

## Rakendamine uutes valdkondades

1. **Metoodika ülekanne teistele väikeste keelte projektidele (läti, leedu, soome murded)} – Töö ise rõhutab (§\ref{sec:contribution-transferability}), et mitmemõõtmeline valideerimisprotokoll on ülekantav. Konkreetse jätkuprojektina võiks koostöös läti või leedu uurimisrühmaga rakendada sama metoodikat nende keelele ning avaldada võrdlev raport. See tugevdaks metoodika valideerust kahel täiendaval keelel ning looks konkreetse jagatud eesti-läti-leedu äratussõna ressursi.

2. **Domeeniülene rakendamine: tervishoid, tööstus, autonoomsed sõidukid} – Praegune töö keskendub nutikodule. Sama metoodikaga (madala ressursiga keel + piiratud riistvara + pidev helivoog) on otsene rakenduspotentsiaal eesti keelt rääkivate töötajate jaoks tööstuskeskkonnas (nt operaatori käed-vabad-juhitav süsteem) või tervishoius (õdede dokumenteerimine). Iga selline kontekst toob uue domeeninihke (vähene heli, müra), kuid metoodika on otseselt rakendatav.

3. **Hariduslik ja keeletehnoloogia kogukonna platvorm} – Eesti keeletehnoloogia kogukonnas on vähe avaliku lähtekoodiga komplekseid otsast-lõpuni näiteid. Töö raames ehitatud tööriistastik (\texttt{kratt user-test}, hindamisskriptid, agentpõhise arenduse muster) võiks olla aluseks kõrgharidusprogrammide kursusele \enquote{Madala ressursiga keele kõnetehnoloogia praktiline arendus}. See nõuab dokumentatsiooni viimistlust ja seminaride organiseerimist, kuid annaks pikaajalise mõju.

4. **Avalik anonüümistatud andmestik kogukondlikuks edasiarenduseks} – GDPR-iga ühilduv anonüümistamine on keeruline, kuid teostatav: ainult kasutaja nõusolekul lühikesed äratusfraasi klipid + foneetilised sarnased klipid + vaikuse näidised. Avaldatud Creative Commons litsentsi all loob see esimese eestikeelse äratussõna avaliku andmestiku ja vähendab eelkõike tulevaste projektide algkulu.

5. **Lapsesõbralik äratussõna mudel ja lasteaia/kooli pilootuuring} – Lapse kõne on töö enda piiranguks tunnistatud (§\ref{sec:fourth-round}). Eraldi laste-spetsiifiline äratussõna mudel koos lasteaia või kooli pilootuuringuga oleks ühtlasi ühiskondlikult mõjukas (digiõppe tugi) ja teaduslikult uudne, sest lapse kõne ei ole praeguses metoodikas süstemaatiliselt kaetud.

6. **Erivajadustega kasutajate (kõnehäired, dementsus) tundlikkuse kohandamine} – Eraldi rakendusvaldkond on inimesed, kelle kõne erineb tavalisest häälduskontuurist (afaasia, Parkinson, dementsus). Sellele rühmale kohandatud äratussõna ja eriti tundlikkuse-selektiivsuse kompromissi ümberkalibreerimine on iseseisev rakenduslik ja eetiline uurimissuund, mis tugineks töö olemasolevale metoodilisele aluselle.

## Kokkuvõtlik märkus

Töö ise tunnistab kahel kohal --- kasutajatesti puudumine täismahus (§\ref{sec:fourth-round}) ning kaskaadarhitektuuri prototüübi puudumine (§\ref{sec:future-cascade}) --- konkreetseid avatud uurimissuundi. Käesolev arengusuundade kogum laiendab neid süstemaatiliselt nelja teljele. Tähtsuse järjekorras on autori ja teadusliku panuse seisukohalt esmaprioriteetsed: (1) stsenaariumipõhise hindamiskorpuse avaldamine, (2) neljanda valideerimisringi täismahus läbiviimine kasutajatestiga, (3) kaskaadarhitektuuri prototüüp ning (4) metoodika ülekanne vähemalt ühele teisele väikese ressursiga keelele. Need neli sammu muudaksid praeguse \enquote{esimese eesti äratussõna projekti} pikaajaliseks korduvalt tsiteeritavaks metoodiliseks panuseks madala ressursiga keelte kõnetehnoloogias.
