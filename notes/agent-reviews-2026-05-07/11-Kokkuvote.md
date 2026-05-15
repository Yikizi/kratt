---
source_prompt: Kohustuslikud/Kokkuvõte.txt
prompt_type: generative
generated: 2026-05-07
---

# Alternatiivne mustand: peatükk "Kokkuvõte"

Järgnev on prompti nõuetele vastav alternatiivne mustand olemasoleva `chapters/summary.tex` peatüki kõrvale. Maht on ligikaudu 480 sõna, struktuur järgib nõutud loogilist järjestust (sissejuhatus -- metoodika -- tulemused -- analüüs ja järeldused), tekst on sidus essee, mitte loetelu, ning väldib keelatud sõna "kaardistama" ning toorlaene.

---

Nutikodu hääljuhtimise kasutuskogemuse esmaseks filtriks on äratussõna tuvastus, mis otsustab, kas seade üldse hakkab kasutaja kõnele reageerima. Eesti keele jaoks on olemas töökindlad lokaalsed kõnetuvastusmudelid, kuid äratussõna tasemel on keele- ja riistvaraklassi ristumine seni katmata: ei avatud raamistiku \texttt{openWakeWord} jaotatud mudelid ega lähim kommertsalternatiiv toeta eesti keelt mikrokontrolleri-klassi seadmel. Sellest olukorrast tuleneb käesoleva töö probleemipüstitus: kuidas luua piiratud andmestiku ja piiratud arvutusressursi tingimustes selline eestikeelse äratussõna lahendus, mille kvaliteet on usaldusväärselt mõõdetav ka pidevas helivoo režiimis. Töö eesmärk on välja töötada eestikeelne äratussõna fraasile "Kuule Kratt" ESP32-S3 klassi seadmele ning hinnata selle sobivust Home Assistanti lokaalse hääljuhtimise osana, sealjuures eraldades selgelt töötlustoru tehnilised piirangud andmestikust ja mudeli üldistusvõimest tulenevatest probleemidest.

Metoodiliselt rekonstrueeriti ja täpsustati \texttt{microWakeWord} põhine treeningu- ja hindamistoru ning valideeriti see avaliku \texttt{Speech Commands} andmestiku kontrollkatsega sihtsõnal \texttt{marvin}. Treeningandmed jaotati positiivseteks klippideks, negatiivseteks klippideks ja taustaheli salvestusteks, kus iga andmeliik täidab erinevat rolli mudeli käitumise hindamisel. Negatiivse poole täiendamiseks kasutati \texttt{MUSAN}, \texttt{VOiCES} ja \texttt{Common Voice} korpusi. Mudeliarhitektuurina rakendati \texttt{microWakeWord} vaikimisi MixedNet ülesehitust nelja mitmesuurustega tuumadega plokiga, mille parameetrite arv jääb umbes 22\,000 piiresse ning mis kvantiseeritakse INT8 vormingusse. Hindamisloogika eristab klipi-tasemelisi mõõdikuid (tuvastamismäär, FPR Wilsoni usaldusvahemikuga) ja voogedastushindamise mõõdikut FAPH (valeaktiveeringute arv tunnis Poissoni-Garwoodi vahemikuga). Töö selgitab ja eristab nelja FAPH-i varianti -- raamistiku, skriptitud taasmängu, välitingimuste ja kasutajatesti taasmängu -- et vältida loendusreegli ebakõlast tulenevat reprodutseeritavuse auku.

Tulemustes ilmnes, et esialgne klipi-tasemeline hindamine andis eksitavalt optimistliku pildi: testikomplekt sisaldas treeningus kasutatud Common~Voice klippe, mistõttu hinnatud FPR ei kirjeldanud üldistust, vaid mälu. Pärast sõltumatute kõrvalejäetud komplektide loomist ja disjointsuskontrolli kasutuselevõttu kujunes hindamisprotokoll kolme valideerimiskihi kaudu, mis lisasid omakorda fraasistruktuuri kontrollivad testid (prefiks, üksik sõna, pööratud järjekord, kuule/kule segiajamine). Üksiku mudeli puhul ei õnnestunud korraga saavutada madalat FAPH-i, kõrget reaalsete kõnelejate tuvastamismäära ja tugevat sarnaste negatiivnäidete eristust. Spetsialiseeritud ekspertmudelite konsensus saavutas Common~Voice ET kõrvalejäetud komplektil FAPH~$=$~0,79, kuid tegi seda saagise arvelt; kontrollpunkti-FAPH eksperiment näitas sama kompromissi veelgi teravamalt.

Analüüsina järeldab töö, et väikese keele lokaalse äratussõna arenduses on määrav metodoloogiliselt korrektne hindamine, mitte ainuüksi mudeli treenimine. Töö peamine ülekantav panus on mitmemõõtmeline valideerimisprotokoll: sõltumatu taustaheli FAPH, kõrvalejäetud komplekti audit, positiivse andmestiku sisuline kontroll ja komposiitne kontrollpunkti valikukriteerium. Eestikeelse äratussõna mudel "Kuule Kratt" jääb sellel alusel demonstreeritavaks kandidaadiks, kuid lõplik juurutusotsus sõltub veel käimasolevast 20--30 osalejaga kasutajatestist, mille raames külmutatakse lävi ja võrreldakse mudeleid identse helisisendi peal.

---

## Märkused mustandi kohta

- Maht: ~480 sõna, mis vastab nõutud A4 lehekülje pikkusele.
- Sõna "kaardistama" ja selle pöördeid mustandis ei esine.
- Tekst on sidus essee, mitte loetelu; loogiline järjestus on sissejuhatus → metoodika → tulemused → analüüs ja järeldused.
- Kõik faktilised väited (FAPH 0,79 Common Voice ET kõrvalejäetud komplektil; ~22\,000 parameetrit; \texttt{Speech Commands} \texttt{marvin} kontrollkatse; kolme valideerimiskihi muster; INT8 kvantiseerimine; ESP32-S3 sihtplatvorm; nelja FAPH-variandi eristus; Wilsoni ja Poissoni-Garwoodi usaldusvahemikud) on võetud lõputöö olemasolevatest peatükkidest ning ei lisa uusi numbreid ega väiteid.
- Stiililiselt välditud: "kaardistama", "feature", "supportima", "manuaalne", "fokusseerima", "domineerima", "potentsiaalne", "duplikaat", "äpp", "proge", "bugi", "tšekkama", "jooksutama", "okei", "mingi", "suht", "jube", "feilima", "adresseerima".
- Olemasolev `chapters/summary.tex` katab samad teemad, kuid struktureerib lõike teisiti (alustab eesmärgist, mitte taustast); käesolev mustand järgib rangelt prompti nõutud järjekorda taust → probleem → eesmärk, et anda autorile alternatiiv võrdluseks.
