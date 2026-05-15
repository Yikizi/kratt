---
source_prompt: /Users/mattias/Downloads/loputoo_viibad_2026_04_28-2/04_Kontrollimine/Konkreetsed_vead/Sisu/Kontrolli_tulemusi.txt
prompt_type: evaluative (ISO/IEC 25010 + innovatsiooni audit)
generated: 2026-05-07
---

# Sõltumatu audit: ISO/IEC 25010 ja uudsuse hinnang

**Auditi objekt:** projekt "Kratt" --- eestikeelne äratussõna tuvastus ESP32-S3 mikrokontrolleril ja konsensus-ekspertmudelite süsteem.
**Allikas:** lõputöö sissejuhatus, esimene, teine ja kolmas peatükk, kokkuvõte ning eesti- ja ingliskeelne resümee.
**Toon:** kuiv, faktipõhine, tõendusele toetuv. Kõik hinnangud on antud üksnes selle põhjal, mis töös on \emph{kirjas}.

---

### Funktsionaalne sobivus (Functional Suitability)
*   **Hinnang:** 4/10
*   **Põhjendus:** Töö on selge funktsionaalse väitega: tuvastada fraas "Kuule Kratt" ESP32-S3 sihtseadmel ja siduda see Home Assistanti `voice_assistant` liidesega. Operatsioonilised sihid on numbriliselt sõnastatud (FAPH < 1 pidevvool, lähikõne tuvastamismäär ≥ 0,95). Funktsionaalne katvus on osaliselt täidetud:
    *   madala FAPH-i siht on \emph{ühe} korpuse (Common~Voice ET kõrvalejäetud, 3,82~h) ja \emph{ühe} operatsioonipunkti juures saavutatud (FAPH = 0,79 ekspert-A + ekspert-B~v2 konsensusega, lävi 0,997/0,997);
    *   tuvastamismäära siht ≥ 0,95 ei ole reaalsetel kõnelejatel saavutatud --- konsensuse hind on 31% (15/48) Kõneleja~A XTTS kõrvalejäetud komplektil ja 5/11 Kõneleja~B kohta;
    *   töö ise tunnistab eksplitsiitselt, et "ükski praegune mudel ega kombinatsioon ei täitnud korraga kõiki eesmärke" (eestikeelne resümee), ning et v16c on "stabiilne üksikmudeli baasjoon, mitte lõplik tootmiskvaliteedi väide".
    Funktsionaalne täpsus (correctness) on seega operatsioonipunkti-spetsiifiline ning kogusüsteemi tasemel mittetäielik. Hinnet 5 ei õigusta, sest peamine kasutusele suunatud kriteerium (recall ≥ 0,95 päris kõnelejatel juurutuslävel) jääb dokumenteeritult täitmata.

### Jõudlus ja tõhusus (Performance Efficiency)
*   **Hinnang:** 6/10
*   **Põhjendus:** Ressursikasutuse piirid on numbriliselt sõnastatud ja sihtriistvara klassi piirangutega seotud:
    *   üksikmudeli (v16c) TFLite INT8 maht 148~KB, varasemad ~57~KB; tensor-arena 45--50~KB; kogusumma alla 200~KB ESP32-S3 4~MB flash / 512~KB SRAM piirangus;
    *   ekspertmudelite konsensus 148 + 55 = 203~KB flash;
    *   voogedastusrežiimi arvutuslik kulu kirjeldatud kui konstantne (üks 10~ms kaader korraga);
    *   parameetreid ~22~000 üksikmudelis, ~44~000 konsensuses.
    Puudused, mis takistavad kõrgemat hinnet:
    *   ekspertmudelite konsensuse \emph{tegelikku} tensor-arena töömälu mikrokontrolleril autor ise tunnistab mõõtmata ("ESP32-S3 teostatavuse seisukohast on tulemus paljulubav... Tensor-arena tegelik töömälu... on veel mõõtmata");
    *   latentsust (esimene aktiveerimisaeg, otsast lõpuni viive Home Assistantis) ei ole peatükkide tekstis numbriliselt esitatud;
    *   kompileerimise/flash-i lõplik kontroll v16c tegelikus pilootkonfiguratsioonis on töös eksplitsiitselt edasi lükatud;
    *   reaalne CPU-koormus seadmel pole raporteeritud.
    Jõudluse \emph{argumendid} on olemas, aga \emph{mõõdetud} jõudlusprofiil sihtseadmel on poolik.

### Ühilduvus (Compatibility)
*   **Hinnang:** 5/10
*   **Põhjendus:** Koostalitlus on sõnastatud arhitektuuriliselt, kuid mitte mõõdetult.
    *   Liidesetasandil tugineb töö dokumenteeritud avalikele standarditele: ESPHome (`voice_assistant`), Home Assistant, microWakeWord TFLite eksport, Wyoming protokoll on viidatud (kuigi protokolli enda tehniline integratsioon põhitekstis ei ole sisuliselt avatud).
    *   Töö taandub eksplitsiitselt sellele, et "reaalne integreerimisrada on siiani tõendatud ESPHome + `home_assistant`/`voice_assistant` liidesega" --- ehk ühilduvuse tõestus on \emph{olemasolu} tasemel, mitte \emph{kvaliteedi} tasemel.
    *   Mitme mudeli konsensuse käivitamine reaalsel ESP32-S3 + ESPHome + Home Assistant ahelal ei ole töös demonstreeritud; mõõdetud konsensus on toimunud taasmängu (offline scripted) torul.
    *   Süsteemide vaheline koos eksisteerimine (co-existence) ja andmevahetus on viidatud, kuid mitte testitud konfliktide, viivituste ega versioonimismatchide suhtes.
    Hinne 5 vastab "olemas, kuid mõõtmata" tasemele.

### Kasutatavus (Usability)
*   **Hinnang:** Ei ole hinnatav (osaliselt: 3/10 selle väikese osa kohta, mis on dokumenteeritud)
*   **Põhjendus:** Lõpphindamise kasutajatest (20--30 osalejat, ~10-min stsenaarium, viis äratussõna ütlust, foneetiliselt sarnased negatiivid, skriptitud käsud, vabas vormis ülesanne, sessioonijärgne küsimustik, valikuline UMUX-Lite) on metoodikas \emph{kavandatud} ja kirjeldatud. Tööriistad (`kratt user-test`, `kratt validate-user-test`, `kratt replay-user-test`, `kratt summarize-user-test`) on olemas. Aga:
    *   reaalseid osalejate andmeid kogutud või analüüsitud ei ole (resümee: "kasutajatestid reaalses nutikodu kasutusolukorras" on edasine samm);
    *   õpitavuse, ligipääsetavuse, kasutajakogemuse hinnete kohta puudub mõõdetud tõend;
    *   eksplitsiitselt on kirjas, et juurutusotsus "sõltub veel käimasolevast kasutajatestist".
    ISO/IEC 25010 mõttes on usability \emph{kriteerium} kavandatud, aga \emph{tulemus} pole olemas. Kuna prompt nõuab, et kui aspekti pole töös eraldi tõendatud, tuleb märkida "Ei ole hinnatav", on see hinnang formaalselt korrektne. Kavandatud küsimustiku ja tööriistastiku eest annab metoodiline pingutus väikese krediidi (3/10), kuid see ei ole sisuline kasutatavuse hinnang.

### Usaldusväärsus (Reliability)
*   **Hinnang:** 4/10
*   **Põhjendus:** Tõendusbaas on selgelt asümmeetriline:
    *   tugev pool: kolm valideerimisringi (klipi-tasemeline FPR → kolme-mõõdiku → kontrollpunkti valikukriteerium), andmelekke avastamine (`compare_models.py` kasutas treeningus olnud 5000 CV ET klippi), kõrvalejäetud komplektide ehitamine, `assert_disjoint_from_training()` tripwire, neli FAPH-i varianti dokumenteeritult eristatud, Wilsoni ja Poissoni-Garwoodi usaldusvahemikud iga raporteeritud mõõdiku juures, "kolmereegli" kasutamine $k=0$ juures;
    *   nõrk pool: tuvastamismäär ei generaliseeru reaalsetele kõnelejatele juurutuslävel ("jääkpiiranguna jääb tuvastamismäär reaalsetel \enquote{Kule}-hääldustel juurutuslävel madalamaks kui TTS-positiivsetel klippidel"); valimimahud on väikesed ($N=11$, $N=48$), Wilsoni UV-d on töö enda sõnul nii laiad, et konsensuskonfiguratsioonide järjekorda ei saa statistiliselt eristada; "ristmikrofoni generaliseerumise asümmeetria" tähendab, et FPR ei generaliseeru kolmandale akustilisele domeenile; Common~Voice ET FAPH 0,79 ümber on Poissoni 95% UV [0,16, 2,30], st sub-1 sihti pole statistiliselt välistatuna kinnitatud;
    *   veataluvus, taastatavus, krahhi/restardi käitumine ESPHome ahelas pole teksti tasemel käsitletud.
    Reliability \emph{hindamise distsipliin} on tugev (auditi-protokoll, tripwired hindamine), kuid \emph{mõõdetud reliability tase} on madal ja ebakindel.

### Turvalisus (Security)
*   **Hinnang:** Ei ole hinnatav
*   **Põhjendus:** Lõputöö tekstis pole turvalisust kui eraldi kvaliteediomadust käsitletud. Mainitud on:
    *   privaatsuse aspekt --- süsteem on lokaalne, ilma pilveteenuseta, mis on \emph{operatsiooniline disainivalik}, mitte turvaargument;
    *   kasutajatesti kaheastmeline nõusolekumudel ja pseudonümiseerimine, mis kuulub eelkõige andmekaitse alla;
    *   ülesandepüstituses on viide "privaatsusriskide vältimisele toorsalvestuste avalikustamisest".
    Konfidentsiaalsuse, terviklikkuse, autentsuse, autoriseerimise, sõnumi puutumatuse, mikrokontrolleri tarkvara turvalise värskendamise, vahemällu salvestatud audio kaitse vms turvameetmete osas töös arutelu pole. Reegli järgi --- kui turvalisust pole mainitud, ei oletata --- on see kategooria mittehinnatav.

### Hooldatavus (Maintainability)
*   **Hinnang:** 7/10
*   **Põhjendus:** Hooldatavuse mõttes annab töö tugevalt rohkem konkreetseid jälgi kui enamik kategooriaid:
    *   modulaarsus: eraldi `evaluation/test_sets.py`, `compare_models.py`, `kratt user-test`, `kratt replay-user-test`, `kratt summarize-user-test`, `kratt validate-user-test`;
    *   reprodutseeritavus: `microWakeWord` põhine treenimistoru on auditeeritud, avalikul `Speech Commands marvin` korpusel kontrollkatsega valideeritud, RNG seemnete (`seed=42`) ja indeksite (5000--7000) tasemel kirjeldatud;
    *   testitavus: `assert_disjoint_from_training()` tripwire kompenseerib varasemat andmelekke viga; FAPH-i variantide eristamine on dokumenteeritud (raamistiku, scripted, field, user-study replay);
    *   versioonihaldus: 8 + ekspertmudeli versiooni dokumenteeritud, treeningandmete koosseis tabelina (tabel mudeliversioonidest) ning iga versiooni hüpoteesi-delta;
    *   piirangud, mis takistavad 8/10: lõputöö tekstis ei ole kasutatud koodi modulaarsuse, testkatte ega CI/CD vms metoodika kohta süstemaatilist tõendust; "kratt CLI" mainimine on funktsionaalne, mitte arhitektuurne tõend.
    Praegune dokumenteerimispraktika ületab tüüpilist bakalaureusetaseme tehnilist hooldatavust, kuid jääb alla "eeskujuliku tarkvarainsenerlikule" tasemele, mis nõuaks eraldi testikatte/staatilise analüüsi raportit.

### Kaasaskantavus (Portability)
*   **Hinnang:** 5/10
*   **Põhjendus:**
    *   töö arutleb eksplitsiitselt kahe sihtkonteksti üle (microWakeWord MCU jaoks, openWakeWord Pi/ONNX jaoks) ja \emph{teadlikult} jätab Picovoice Porcupine litsentsi- ja keelepiirangute tõttu välja --- see on portatiivsuse osa nõudeline analüüs;
    *   sihtplatvormid ESP32-S3-Korvo-2 ja ESPHome on nimetatud, INT8 kvantiseerimine TFLite Micro jaoks tehtud;
    *   "ristmikrofoni asümmeetria" tähendab dokumenteeritud kaasaskantavuse \emph{piirangut}: tuvastamismäär kandub üle (positiivne tunnetabamine teistel mikrofonidel toimib), FPR aga \emph{ei kandu üle} --- iga uue sihtseadme puhul tuleb lisada vastav negatiivne treeningmaterjal (autori enda formuleering);
    *   paigaldatavuse (installability) ja kohandatavuse (adaptability) tegelik mõõtmine peale ühe sihtseadme on tegemata.
    Hinne 5 vastab sellele, et portatiivsuse \emph{piirangud} on ausalt sõnastatud, kuid \emph{positiivne} portatiivsuse tõend on ühe seadmeklassi piires.

---

### Innovatsioon ja uudsus
*   **Hinnang:** 6/10
*   **Põhjendus (tehnoloogiline uudsus):**
    *   Kasutatud tehnoloogiad ise (microWakeWord, openWakeWord, MixedNet/SVDF, ESPHome, Home Assistant, Wyoming, INT8 kvantiseerimine, SpecAugment, residuaalühendused) ei ole uudsed --- need on olemasolevad ja viidatud avatud lähtekoodiga komponendid. \emph{Buzzword compliance} riski töös ei ole, sest autor ei väida tehnoloogiate ise-leiutamist; vastupidi, ülesandepüstitus piiritleb selgelt, et uusi STT/TTS mudeleid algusest peale ei ehitata.
    *   Tegelik tehnoloogiline panus on \emph{rakendusstsenaariumi uudsus}: töö ise dokumenteerib otsingutulemuse, et "teadaolevalt pole eestikeelset äratussõna- ega väikesemahulist KWS-süsteemi avaldatud" ja et eesti ASR-mastaabi korpuste KWS-negatiividena ümberkasutamine on selle töö enda sõnul esmakordne. See on legitiimne keele-spetsiifiline esmasus, kuid mitte üldine algoritmiline uudsus.
*   **Põhjendus (protsessi-/metoodikainnovatsioon):**
    *   Kõige kindlamini kaitstav uudsus, mille autor ise välja toob, on \emph{mitmemõõtmeline valideerimisprotokoll}: (a) sõltumatu kõrvalejäetud komplekti audit, (b) positiivse andmestiku sisuline audit, (c) kontrollpunkti komposiitne valikukriteerium ja (d) FAPH-i nelja variandi eksplitsiitne eristamine. Töö esitab seda kui ülekantavat protokolli teistele madala ressursiga keelte projektidele. See on metoodiline panus, mis on aus ja kontrollitav, kuid \emph{kaskaadarhitektuur ja konsensus} ise on äratussõna kirjanduses tuntud (Apple Hey~Siri, HEiMDaL, Google KWS), mida töö ka ise tunnistab.
    *   "Agentpõhine arendus kui töövõimendaja" alapeatükk on aus refleksioon, mitte iseseisev innovatsiooniväide; autor ise rõhutab, et tehisagendid "ei vähenda samal määral tõendusmaterjali hankimise kulu". See enesepiiritlus tugevdab töö metoodilist usaldusväärsust, kuid ei tõsta innovatsioonihinnet.
    *   "Degradatsiooni org" rakendamine konkreetse domeeni-osakaalu (2,7%) selgitusena ja "ristmikrofoni generaliseerumise asümmeetria" eraldi raporteerimine on kasulikud diagnostilised leiud, kuid kirjandusele nõjatuvad (Park~et~al., Apple, Sensory).
    Hinne 6 vastab sellele, et tegemist ei ole "haibiga", vaid sisulise rakendus- ja metoodikainnovatsiooniga, kuid mitte algoritmilise või arhitektuurilise läbimurdega. 7+ nõuaks kas (a) avaldatud mudelit, mille FAPH/recall on sõltumatutel korpustel reprodutseeritud kolmandate isikute poolt, või (b) sihtuudset arhitektuurset komponenti.

---

## Üldine kokkuvõte

| Aspekt | Hinnang |
| --- | --- |
| Funktsionaalne sobivus | 4/10 |
| Jõudlus ja tõhusus | 6/10 |
| Ühilduvus | 5/10 |
| Kasutatavus | Ei ole hinnatav (kavand 3/10) |
| Usaldusväärsus | 4/10 |
| Turvalisus | Ei ole hinnatav |
| Hooldatavus | 7/10 |
| Kaasaskantavus | 5/10 |
| Innovatsioon ja uudsus | 6/10 |

**Keskmine (kus hinnatav):** ≈ 5,3/10 --- vastab ISO/IEC 25010 \emph{keskpärasele} kuni \emph{üle keskmise} tasemele, kus tugevused on metoodiline distsipliin (audit, tripwired hindamine, FAPH-i variantide eristus, dokumenteeritud kompromissid) ja peamised nõrkused on (a) operatsionaalse sihi (recall ≥ 0,95 päris kõnelejatel) täitmata jäämine, (b) turvalisuse ja kasutatavuse mõõdetud tõenduse puudumine ning (c) tegeliku riistvara-jõudluse osaline mõõtmine.

**Auditi reegel:** kõik "Ei ole hinnatav" hinnangud kajastavad reaalset tõendite puudumist tekstis ja \emph{ei ole} negatiivsed --- need on neutraalsed kategooriad, mille kohta lõputöö ei väida ega esita andmeid. Lugeja, kes vajab hinnangut nendes kategooriates, peab konsulteerima väljaspool seda lõputööd asuva tehnilise dokumentatsiooniga (nt repositoorium, ADR-id, manifest), mis ei ole käesoleva auditi skoobis.
