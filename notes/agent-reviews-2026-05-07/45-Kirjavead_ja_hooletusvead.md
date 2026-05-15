---
source_prompt: 04_Kontrollimine/Konkreetsed_vead/Vorm/Kirjavead_ja_hooletusvead.txt
prompt_type: evaluative
generated: 2026-05-07
---

# Kirjavigade ja hooletusvigade audit

Audit hõlmab faile: introduction.tex, first_chapter.tex, second_chapter.tex, third_chapter.tex, summary.tex, abstract-estonian.tex, abstract-english.tex, ylesandepystitus.tex.

Märkus: lõplikku PDF-vormingut ja leheküljepiire ei olnud käesoleva auditi käigus võimalik tuvastada (audit põhineb LaTeX-lähtefailidel), mistõttu tüpograafilisi orve (lehe lõpus rippuv tabeli- või jooniseallkiri) ei saa siin kontrollida. Asukohad on toodud peatükkide ja alapeatükkide pealkirjade kaudu.

### 1. Nimekiri kirjavigadest

*   **Asukoht:** introduction.tex, lõik 7 (FAPH-mõõdikut tutvustav lause)
    *   **Vigane tekst:** "nt v6-residual 0{,}58~FAPH vs.\ expert-a parima üldise tasakaalu juures 2{,}79~FAPH 98{,}97~h jooksul"
    *   **Parandus:** "nt v6-residual 0{,}58~FAPH \emph{vs.} expert-a parima üldise tasakaalu juures 2{,}79~FAPH 98{,}97~h jooksul" — lühend "vs." on ladina laen ja akadeemilises eestikeelses tekstis kirjutatakse see kursiivis; alternatiivina asendada eestikeelse väljendiga "võrreldes".

*   **Asukoht:** third_chapter.tex, §"Põhjus 1: klipitaseme tuvastamismäär ei kajasta reaalse kõneleja käitumist"
    *   **Vigane tekst:** "Park et al.~\cite{park2024adversarial} on näidanud" (samuti "Dubois et al.", "Sch{\"o}nherr et al.", "Choi~et~al." second_chapter.tex-is)
    *   **Parandus:** Eestikeelses akadeemilises tekstis kirjutatakse "et al." kursiivis ("\emph{et al.}") või asendatakse väljendiga "jt" (näiteks "Park jt"). Käesoleva töö siseselt tuleb valida üks lähenemine ja seda järjepidevalt rakendada — praegu varieerub kasutus.

*   **Asukoht:** third_chapter.tex, §"Empiiriline tõendus lahknevusest", lõik 2
    *   **Vigane tekst:** "kahe kuuekoht\-numbrelise suurusjärgu erinevus prognoosist"
    *   **Parandus:** "kahe suurusjärgu erinevus prognoosist" — väljend "kuuekoht\-numbrelise suurusjärgu" on tõenäoliselt ekslik kombinatsioon ("suurusjärk" tähendab juba kümnendsuurusjärku, mitte numbrikohtade arvu); kui silmas on peetud kahekordset kümnendsuurusjärku ($\sim$0{,}4\% vs. $\sim$50/h), siis korrektne sõnastus on "kahe suurusjärgu erinevus".

*   **Asukoht:** third_chapter.tex, §"Üldine printsiip: hindamise piirid kui treenitavad lühiteed"
    *   **Vigane tekst:** "klipi-tasemel FPR \emph{tahtis} mõõta generalisatsiooni klassidisruptsioonile"
    *   **Parandus:** Sõna "klassidisruptsioonile" tähendus on ebaselge ja tundub olevat trükiviga või kohatu termin (võimalik, et silmas peetud "klasside diskrimineerimist" või "klassieristust"). Soovitus: "klipi-tasemel FPR \emph{tahtis} mõõta generalisatsiooni klasside eristamisel".

*   **Asukoht:** third_chapter.tex, §"Töö-tasemel panus ja selle ülekantavus"
    *   **Vigane tekst:** "Kasvab seega väide:" (lõigu algus)
    *   **Parandus:** "Sellest kasvab välja väide:" või "Siit järeldub:" — tegusõna "kasvab" üksi ilma subjektita on ebaloomulik (eelmises sama alampeatüki lõigus on samas mõttes kasutatud "Sellest kasvab konkreetne disainiprintsiip", mis on grammatiliselt korrektsem).

*   **Asukoht:** third_chapter.tex, §"Põhjus 2: FAPH tihedal kõnel ei ennusta FAPH reaalses keskkonnas"
    *   **Vigane tekst:** "Sensory, kes arendab Samsung'i äratussõna mudeleid"
    *   **Parandus:** "Sensory, kes arendab Samsungi äratussõna mudeleid" — eesti keele ülakomareegel: ülakoma kasutatakse pärisnime käänamisel ainult juhul, kui sõnalõpp ei hääldu nii nagu kirjutatakse. "Samsung" hääldatakse [samsung], omastav kääne on "Samsungi" (ilma ülakomata).

*   **Asukoht:** third_chapter.tex, §"Põhjus 2: FAPH tihedal kõnel ei ennusta FAPH reaalses keskkonnas"
    *   **Vigane tekst:** "Sch{\"o}nherr et al.\ \cite{schoenherr2022accidental} kinnitavad seda mustrit eraldi katsega, näidates et juhuslike aktiveerumiste määr"
    *   **Parandus:** "...näidates, et juhuslike aktiveerumiste määr..." — koma puudub kõrvallause ees ("näidates, et").

*   **Asukoht:** second_chapter.tex, §"Mudeli arhitektuur" (sissejuhatav lõik)
    *   **Vigane tekst:** "Selline mitme\-skaalaline lähenemine"
    *   **Parandus:** "Selline mitmeskaalaline lähenemine" — sõna "mitmeskaalaline" on liitsõna, mis kirjutatakse ühe sõnana ilma sidekriipsuta; "\\-" on LaTeX-i pehme silbituspunkt, mis on käsitsi sisestatud, kuid liitsõna jagamine on selles kohas ebaloomulik (LaTeX paneb murdmiskoha ise). Eemaldada "\\-".

*   **Asukoht:** second_chapter.tex, §"Kasutajatesti metoodika ja subjektiivse rahulolu mõõtmine"
    *   **Vigane tekst:** "Lõpphindamise kasutajatest on kavandatud lühikese, umbes 10-minutilise ühe-nutipirni stsenaariumina"
    *   **Parandus:** "ühe-nutipirni" on harukordne moodustus; ortograafiliselt korrektsem on "ühe nutipirni stsenaariumina" (ilma sidekriipsuta), kuna eesti keeles ei kirjutata atributiivset "ühe + nimisõna" konstruktsiooni sidekriipsuga.

*   **Asukoht:** introduction.tex, lõik 7
    *   **Vigane tekst:** "openWakeWord raporteerib oma dokumentatsioonis $<\!0{,}5$~FA/h subjektiivse \enquote{piisava} sihina"
    *   **Parandus:** Mõõtühik "FA/h" tuleks ühtlustada: kogu töös kasutatakse läbivalt "FAPH" (false accepts per hour) kui standardit, kuid siin on äkki "FA/h". Asendada "FA/h" → "FAPH" järjepidevuse huvides.

*   **Asukoht:** third_chapter.tex, §"Empiiriline tõendus lahknevusest"
    *   **Vigane tekst:** "Reaalajas testimine näitas aga vastupidist pilti: mudel aktiveerus sageli sarnastel fraasidel nagu \enquote{kuule rott} ja \enquote{kuule kraam}"
    *   **Parandus:** Kontrollida väiketähe/suurtähe järjepidevust — töös on äratusfraas "Kuule Kratt" (suurtähtedega), kuid jutumärkides olevad varianti-fraasid algavad väiketähega. Kuna tegemist on tsiteeritud ütlustega lause sees, on väiketäht aktsepteeritav, ent kogu töö ulatuses tuleks järjepidevus üle vaadata (nt summary.tex ja abstract-estonian.tex kasutavad suurtähti, kuid third_chapter.tex sama lõik segiläbi).

*   **Asukoht:** third_chapter.tex, §"Empiiriline tõendus lahknevusest"
    *   **Vigane tekst:** "Reaalsete ütluste silutud skoorid jäid katseprotokolli alusel juurutamislävega võrreldava suurusjärku juurde"
    *   **Parandus:** "...võrreldavasse suurusjärku..." — sõna "suurusjärku" eeldab eelnevat omadussõna sisseütlevas käändes ("võrreldavasse"), mitte saavas ("võrreldava ... juurde").

### 2. Nimekiri hooletusvigadest

*   **Asukoht:** Kogu töö ulatuses (eestikeelsed peatükid)
    *   **Probleem:** Inglise keelest pärit lühendite kursiivivormistus on ebajärjekindel. Mõnes kohas on kasutatud kursiivi (nt "ingl \emph{wake word}", "ingl \emph{streaming evaluation}", "(\emph{vanishing gradients})"), teisal mitte (nt "vs.\", "et al." ilma kursiivita). Lisaks on osas kohtades inglisekeelne termin antud kursiivis ja sulgudes, teisal jutumärkides.
    *   **Parandus:** Otsustada üks vormistusreegel ja rakendada kogu tekstis (TalTech bakalaureusetöö juhend soovitab inglisekeelsed terminid panna kursiivi sulgudes pärast eestikeelset terminit kujul "(ingl \emph{termin})"). Üle vaadata vähemalt: introduction.tex (FA/h, vs.), second_chapter.tex (kõik "(ingl ...)" konstruktsioonid), third_chapter.tex ("et al.").

*   **Asukoht:** introduction.tex, lõik 7
    *   **Probleem:** Sümbol "$\approx$" ja sõna "umbes" / "ligikaudu" on töös segiläbi kasutuses (nt "FAPH~$\approx$~50" introduction.tex-is, "$\sim 3/T$" hilisemates lõikudes, "umbes 1{,}5~sekundi" second_chapter.tex-is, "${\sim}107$\,KB" second_chapter.tex-is). Sama tähendusega märkide segikasutus loob ebajärjekindla mulje.
    *   **Parandus:** Valida üks teostus (kas $\approx$ + arv või sõnaline "umbes"/"ligikaudu") matemaatiliste hinnangute jaoks ja teine sõnalise lähenduse jaoks; rakendada järjepidevalt.

*   **Asukoht:** Kogu töö ulatuses
    *   **Probleem:** Mõõtühikute ja arvude vahelise tühiku järjepidevus. Teatud kohtades on kasutatud LaTeX-i kitsast tühikut "\\,~" (nt "1500\,ms", "300--700\,ms", "57\,KB"), teisal tavalist tilde-tühikut "~" (nt "98{,}97~h", "0{,}996/0{,}996", "$\sim$~50"), ning veel teisal tavalist tühikut ("40 minutilisel" ehk "40-minutilisel"). 
    *   **Parandus:** Kogu töö ulatuses kasutada arvude ja mõõtühikute vahel ühtset murdmatut tühikut "\\,". Vrd. introduction.tex "MacBook~Pro mikrofoni 40-minutilisel" vs. "${\sim}99$~h" vs. second_chapter.tex "1500\,ms". Vajab toimetuskäiku.

*   **Asukoht:** Kogu töö ulatuses
    *   **Probleem:** Kümnendmurdude eraldajana kasutatakse järjepidevalt koma (nt "0{,}79", "0{,}996", "0{,}58~FAPH"), mis on eesti keeles korrektne. Erandina aga: ylesandepystitus.tex viite [1]–[4] aastad (22.02.2026) on punktidega, mis on kuupäevaformaat ja seega õige. Tarkvarapaketi versioonid (nt "Python 3.9") puuduvad eraldi vormingunõuet rikkuvalt — see on prompti reegli kohaselt korrektne. Eraldi probleemi siin pole, kuid soovitus säilitada teadlikkus.
    *   **Parandus:** Kontrollida, et üheski tabelinumeri- või joonisandmes ei oleks ekslikult ingliskeelseid punkti-eraldajaid (näiteks tabelis~\ref{tab:checkpoint-headline} viidatav "0,4\%" peab olema komaga). Auditi käigus lähtefailis ühtegi rikkumist ei leitud, kuid kompileeritud PDF-tabeleid ei nähtud.

*   **Asukoht:** introduction.tex, lõik 7 — sama lõigu sees mõõdikute esitus
    *   **Probleem:** Sama mõõdiku FAPH puhul on osa väärtustest jutumärkides ja osa mitte: "FAPH~$\approx$~50", "0{,}58~FAPH", "2{,}79~FAPH 98{,}97~h jooksul". Esimeses on FAPH tagaküljel sõnalisena; teises ja kolmandas on järjekord "arv FAPH".
    *   **Parandus:** Ühtlustada: kas alati "FAPH = arv" või "arv FAPH" (käesolev töö pigem teisel kujul).

*   **Asukoht:** introduction.tex, lõik 7
    *   **Probleem:** Lause "Picovoice'i avalikud võrdlusalused kasutavad rangemat 1 valeaktiveeringu / 10~h punkti" — väljend "1 valeaktiveeringu / 10~h" on segase grammatikaga, segades arvu ja jagamist.
    *   **Parandus:** "Picovoice'i avalikud võrdlusalused kasutavad rangemat sihti 1 valeaktiveering 10~h kohta" või "1/(10~h)".

*   **Asukoht:** second_chapter.tex, §"Mudeli arhitektuur" (sissejuhatav lõik)
    *   **Probleem:** Tuumade suuruste loend on esitatud kahel erineval kujul: matemaatikarežiimis "$[5], [9], [13], [21]$" (sulgude paaridena) ja sama lause järgmises pooles tühisõnalist "tuuma suurusega 3". Lisaks on numbrid ühel juhul nurksulgudes (nagu Pythoni listid), teisel mitte.
    *   **Parandus:** Kasutada teadustekstis kas "$\{5,9,13,21\}$" (komplekt) või sõnalist "tuumadega 5, 9, 13 ja 21". Praegune nurksulgude vorm meenutab koodi, mitte matemaatilist objekti.

*   **Asukoht:** second_chapter.tex, §"FAPH-i variandid ja loendusreegel" \label{subsec:faph-variants}
    *   **Probleem:** Nimekirja punktid sisaldavad ingliskeelseid termineid ladusalt (nt "scripted offline", "field", "user-study replay"), mis on osaliselt kursiivis ja osaliselt mitte ("\\textbf{skriptitud taasmängu FAPH (scripted offline)}" ilma kursiivita; "\\textbf{välitingimuste FAPH (field)}" ilma kursiivita).
    *   **Parandus:** Inglisekeelsed sulgudes terminid kursiivi ühtsel kujul: "(\\emph{scripted offline})", "(\\emph{field})", "(\\emph{user-study replay})".

*   **Asukoht:** second_chapter.tex, §"Kvantiseerimine"
    *   **Probleem:** "Piloodi aktiivseks kandidaadiks valitud \\texttt{v16c} kvantiseeritud TFLite-mudeli maht on 148\\,KB; varasemad väiksemad mudelid olid umbes 57\\,KB." Sama lehekülje võrdlusraamistiku osas on aga kirjas: "käesolevas töös 57\\,KB ning ${\\sim}107$\\,KB koos töömäluga". Tekib küsimus, milline number on autoriteetne — 107 KB või 57 + 45-50 KB ($\\approx$ 102-107 KB).
    *   **Parandus:** Kontrollida, et arvud (mudel + tensor_arena) langevad omavahel kokku, ja valida üks esitusviis — kas "57 KB mudel + 45-50 KB tensor_arena $\\approx$ 102-107 KB" või lihtsustatud "${\\sim}107$ KB". Praegu tekitavad eri kohad lugejas ebakindlust.

*   **Asukoht:** third_chapter.tex, §"Mida saab juba praegu väita"
    *   **Probleem:** Loetelu punktide lõpus on osa kirjeid lõpetatud semikooloniga, viimane punktiga ("...päris kasutuskeskkonnaga."). Vahepealsetel kirjetel on semikoolon, viimasel punkt — see on klassikaline LaTeX/eesti loendi vormindamise reegel ja korrektne. Kontrollida tuleks vaid, et sama reegel kehtib ka teistes loetelu kohtades (nt introduction.tex itemize alamküsimuste loend lõpeb iga rida ilma semikoolonita: "...juurde liikumist;" + "...kvaliteedi hindamisel;" + "...tehnilistest piirangutest;" + lõpus "...sihi." — see on järjepidev).
    *   **Parandus:** Vea pole, kuid soovitus auditeerida kõik itemize/enumerate loendid, et lõppvorming oleks ühtne.

*   **Asukoht:** third_chapter.tex, §"Üldine printsiip: hindamise piirid kui treenitavad lühiteed", loetelu kolmas punkt
    *   **Probleem:** Pikk lause "või sihtväärtuse lõdvendamisel mudeli, mille tuvastamismäär paranes ainult osaliselt ja mille valeaktiveeringute sagedus muutus taas liiga kõrgeks" on grammatiliselt korrektne, kuid raskestiloetav (sisaldab kahte "mille"-kõrvallauset järjest).
    *   **Parandus:** Kaaluda lause poolitamist või "ja"-konjunktsiooniga ümbersõnastust, näiteks: "...kõikide võõraste signaalide suhtes (sealhulgas reaalsete sihtkõnelejate); kui sihtväärtust lõdvendati, tõusis valeaktiveeringute sagedus kiiresti tagasi liiga kõrgeks ning tuvastamismäär paranes ainult osaliselt."

*   **Asukoht:** ylesandepystitus.tex, peatükk "Esialgsed allikad"
    *   **Probleem:** Allikate kuupäevad on kõik "viimati vaadatud 22.02.2026", mis on kindlasti vana ja ei kajasta tegelikku viimast vaatamiskuupäeva töö lõplikus versioonis (käesoleva auditi kuupäev on 2026-05-07).
    *   **Parandus:** Uuendada kuupäevad enne lõpliku versiooni esitamist tegeliku viimase külastuse kuupäevaks, või kasutada "(külastatud [kuupäev])" konsekventses vormingus.

*   **Asukoht:** ylesandepystitus.tex, peatükk "Metoodika", §"Andmestiku koostamine ja mudeli arendamine"
    *   **Probleem:** "Arenduses rakendatakse MixConv kihtidel põhinevat mixednet arhitektuuri" — sama termini kahesugune kirjapilt: "MixConv" (suure C-ga, kompaktselt) ja "mixednet" (väikese m-ga, ilma sidekriipsuta), samas kui second_chapter.tex kasutab läbivalt "MixedNet" ja "MixedConv".
    *   **Parandus:** Ühtlustada nimetused kogu töös: "MixedNet" (arhitektuur) ja "MixedConv" (plokid), nagu second_chapter.tex teeb.

*   **Asukoht:** abstract-estonian.tex, lõik 1
    *   **Probleem:** "Töö praktiline lähtekoht on väikeste keelte häälassistentide toe lünk: eestikeelse kõnetuvastuse jaoks leidub juba sobivaid mudeleid, kuid kohalik äratussõna tuvastus määrab kogu hääljuhtimise kasutatavuse."
    *   **Parandus:** Lause on selge, kuid puudub väike viitamiskoht: kogu töös kasutatakse "äratussõna tuvastust" (käändevorm), kuid mõnes kohas "äratussõna" üksikuna. Kontrollida, et kasutus on järjepidev (eelistatud "äratussõna tuvastus" kui kogu valdkonna nimi, "äratussõna" kui konkreetne fraas).

*   **Asukoht:** Kogu töö ulatuses
    *   **Probleem:** Tüpograafiliselt nii ladusas akadeemilises tekstis on töö läbivalt kvaliteetne, kuid ühe stilistilise kalduvusena tuleb märkida: kolmemõtteliste sõnade ("seetõttu", "seega", "samas", "siiski", "lisaks") tihe kasutus ühe lõigu sees mõnel pool tekitab täidisõnade mulje. Näiteks third_chapter.tex §"Töö-tasemel panus..." — neljas kõrvuti olevas lõigus algab "Töö-tasemel muster ei ole...", "Käesoleva töö dokumenteeritud protokoll...", "Kasvab seega väide:", "Tööstusliku praktikaga võrreldes...". 
    *   **Parandus:** Kuigi see ei ole otsene kirjaviga, soovitatakse toimetuskäik üleliigsete sidesõnade vähendamiseks. Tegemist on stilistilise hooletusveaga, mitte ortograafilise veaga.

*   **Asukoht:** Joonised ja tabelid (lähtefailides ei sisaldu, kuid mainitud ristviited)
    *   **Probleem:** Lähtefailide alusel ei saa kontrollida, kas joonistele ja tabelitele tehtud ristviited (\ref{...}) lahenduvad korrektselt — paljud viited on tehtud peatükkidele ja tabelitele, mille definitsioone käesolevas auditeeritud failipargis ei sisaldu (nt \ref{chapter:results}, \ref{tab:full-comparison}, \ref{tab:checkpoint-headline}, \ref{tab:expert-consensus}, \ref{tab:fair-comparison-holdout}, \ref{tab:model-versions}, \ref{tab:expert-consensus}).
    *   **Parandus:** Kompileerida lõpliku PDF-vorming ja kontrollida, et iga "vt ptk~\\ref{...}" / "vt §\\ref{...}" / "vt tabel~\\ref{...}" lahendub korrektse numbrilise viiteni, mitte "??" sümboliks. Kui tabel on määratletud teises chapterfailis (nt results.tex), peab \\label seal asuma.
