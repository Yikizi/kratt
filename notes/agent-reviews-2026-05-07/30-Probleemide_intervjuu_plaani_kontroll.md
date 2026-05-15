---
source_prompt: Probleemide_tuvastamise_intervjuu_plaani_kontrollimine.txt
prompt_type: evaluative (UX-audit, mittesobiv käesolevale tööle)
generated: 2026-05-07
---

# Audit: probleemide tuvastamise intervjuu kava kontroll

## 0. Sobivuse hinnang ja metoodiline lünk

Sissejuhatava avaldusena on vaja fikseerida, et **käesolev prompt ei vasta otseselt antud lõputöö disainile**. Prompt eeldab, et üliõpilane on koostanud kvalitatiivse intervjuukava, mille eesmärk on **tuvastada organisatsiooni olemasoleva (halva) tarkvara kasutatavusprobleeme**, et luua sisend uue süsteemi disainimiseks. Selline kontekst eeldab tüüpilist UCD- või tarkvaraarenduse-projekti, kus klientorganisatsioonil on olemas mingi praegune lahendus, mille puudusi tuleb nüüd intervjuude kaudu välja selgitada.

Käesolev lõputöö on aga olemuselt **tehniline arendustöö** (eestikeelse äratussõna mudeli loomine ja hindamine ESP32-S3 platvormil). Töös ei ole klientorganisatsiooni, ei ole \enquote{olemasolevat halba tarkvara}, mille probleeme tuleks intervjueerimisega välja selgitada, ega ka uue süsteemi disaini lähtepunktiks olevat probleemiintervjuude vooru. Töö lähtekoht ei ole \enquote{kasutaja räägib oma valupunktidest}, vaid kirjanduse-põhine konstateering: \texttt{openWakeWord} ja Picovoice Porcupine ei toeta eesti keelt (vt \texttt{introduction.tex}, lõik 1).

Seega tuleb käesolev audit teostada **lünga-selgitusena ja parima võimaliku ülekandmisena**: mida ütleks UX-uurija nende töö osade kohta, mis intervjuule või küsimustikule kõige lähemale jõuavad?

Töös on tuvastatav **üks** osaliselt sarnane element: paragrahv \enquote{Kasutajatesti metoodika ja subjektiivse rahulolu mõõtmine} (\texttt{second\_chapter.tex}, §\ref{sec:user-test-methodology}). See kirjeldab 20--30 osalejaga lühikest sessiooni, mis sisaldab struktureeritud katsete kõrval ka **sessioonijärgset lühikest küsimustikku** (usaldusväärsuse, kiiruse, käskude loomulikkuse ja kodus kasutamise valmiduse hinnangud ning üks avatud küsimus häiriva või üllatava kogemuse kohta) ning valikuliselt kahte UMUX-Lite väidet \cite{lewis2013umuxlite,sauro2009seq}.

Viimase puhul on tegemist **summatiivse subjektiivse rahulolu mõõtmisega pärast prototüübi kasutamist**, mitte formatiivse probleemiintervjuuga olemasoleva süsteemi puuduste tuvastamiseks. Audit peab seda erinevust kogu aeg silmas pidama. Allpool tehakse parima võimaliku ülekandega audit just selle küsimustiku kohta, kuna see on ainus elunditõenäoline sihtmärk antud promptile lõputöö raames.

---

## 1. Üldine hinnang ja tugevused (parima ülekande kontekstis)

Lõputöö \texttt{user-test} sessioonijärgne küsimustik on **kompaktne, eesmärgistatud ja akadeemiliselt lugupidav** \cite{lewis2013umuxlite,sauro2009seq}. Tugevused, mida UX-uurija positiivsena märgiks:

- **Selge eraldus mõõdetava käitumise ja subjektiivse arvamuse vahel.** Käitumine (äratussõna tabamine, sarnaste fraaside FPR, käsu täitmine) mõõdetakse logitööriistadega \texttt{kratt user-test}, \texttt{kratt validate-user-test}, \texttt{kratt replay-user-test}, \texttt{kratt summarize-user-test}; küsimustik mõõdab eraldi dimensiooni (subjektiivne rahulolu). See on metoodiliselt korrektne ja vastab UX-uuringu hea tava \enquote{ära aja segamini, mida inimene tegi, ja seda, mida ta arvab}.
- **Valideeritud lühiskaala (UMUX-Lite) eraldatud uurija koostatud küsimustest.** Töö ütleb expressis verbis, et UMUX-Lite raporteeritakse \enquote{eraldi valideeritud lühiskaalana} ja et ülejäänud uurija küsimusi käsitletakse \enquote{diagnostiliste, mitte valideeritud koondskaala tulemustena}. See on metoodiliselt küps eristus, mida bakalaureusetöödes harva näeb.
- **Avatud küsimus \enquote{häiriva või üllatava kogemuse kohta}.** See on hea valik: avatud, mittesuunav, käitumiskeskne (palub konkreetset kogemust, mitte ennustust või arvamust).
- **Kaheastmeline nõusolek (minimaalne + audio opt-in).** GDPR-iliselt korrektne, mõjutab ka andmete kvaliteeti, sest osaleja teab, mida ta loovutab.
- **Sessioon on lühike (${\sim}10$ minutit) ja stsenaariumipõhine.** See on UX-uuringutes kuldreegel: \enquote{ära kunagi tee 60-minutilist intervjuud, kui 10-minutiline annab sama vastuse}.

Kui antud prompti rangelt järgida (\enquote{kui küsimustik on juba praegu teaduslikult ja praktiliselt laitmatu, ütle seda kohe siin}), tuleks lõpetada lühikese kiitusega. Käesoleva töö kontekstis aga on aus märkida, et küsimustik **ei ole probleemiintervjuu** ja seetõttu pole ta selle prompti pärisalge auditi sihtmärk; tema enda kontekstis (post-test rahulolu) on ta korralik.

---

## 2. Tuvastatud nõrkused ja kriitika

Kuna prompt eeldab probleemiintervjuu kava ning sellist artefakti töös ei eksisteeri, tuleb suurim nõrkus sõnastada **lünga, mitte vea kaudu**.

### 2.1 Põhilünk: probleemiintervjuude voor puudub töö disainist

- **Probleem:** käitumispõhisuse kriteerium (\enquote{uuritakse reaalset mineviku käitumist ja töövooge}) ei ole töö praegustes mõõtmistes täidetud. Lõputöö ei kogu osalejatelt **eelnevat kasutuskäitumist** (nt \enquote{kuidas te täna oma nutikodu juhite}, \enquote{millal viimati üritasite häälega midagi käivitada ja see ei töötanud}). Mõõdetakse ainult prototüübi-aegset käitumist ja prototüübi-järgset rahulolu.
- **Mõju:** töö ei suuda kvalitatiivselt põhjendada, **miks** eestikeelne lokaalne äratussõna on kasutaja jaoks vajalik. Põhjendus tugineb praegu kirjandusele (Picovoice ei toeta, openWakeWord ei jagata; vt \texttt{introduction.tex}). See on legitiimne argument, kuid retsensent võib küsida: \enquote{kas teil on ka **kasutajate** häält selle kohta, et probleem on päriselt olemas, mitte ainult tehniliselt olemas?} See on ainus koht, kus probleemiintervjuu (kas või 5--6 osalejaga) tugevdaks tööd märkimisväärselt.
- **Mõju lõputöö hindele:** \enquote{suurepärane}-tasemelt kaitsmine ei ole sellest sõltuv (töö tugev panus on hindamismetoodikas, mitte kasutajauuringus), kuid \enquote{kasutajakeskse disaini} pidev väide oleks toetatud tugevamini, kui oleks olemas kas või lühike formatiivne intervjuude voor.

### 2.2 Sessioonijärgse küsimustiku kallutuse-risk

- **Probleem (suunavus):** kavandatud hinnangud \enquote{usaldusväärsus}, \enquote{kiirus}, \enquote{käskude loomulikkus}, \enquote{kodus kasutamise valmidus} on **kõik positiivse polaarsusega rahulolu-mõõdikud}. UX-uuringutes on tuntud probleem, et osaleja, kes just nägi prototüüpi ja räägib selle autoriga, kaldub vastama kõrgemate skooridega kui sõltumatu kasutaja kuu aja pärast (sotsiaalne soovitavus, \emph{social desirability bias}; \emph{acquiescence bias}).
- **Näide kavast:** \texttt{second\_chapter.tex}, lõik §\ref{sec:user-test-methodology}: \enquote{süsteemi usaldusväärsuse, kiiruse, käskude loomulikkuse ja kodus kasutamise valmisoleku hinnangud}.
- **Mõju:** hinnangud kõrguvad tõenäoliselt kõrgemale kui süsteemi tegelik kvaliteet. Kuna töö dokumenteerib mujal **väga ausalt} jääkpiiranguid (\enquote{Kule}-hääldus jääb juurutuslävel madalamaks kui TTS-positiivsed; vt \texttt{third\_chapter.tex}), tekib oht, et küsimustiku tulemused näevad nendega vastuolulised välja, ja retsensent küsib, kummal on õigus.

### 2.3 \enquote{Kodus kasutamise valmisolek} on tulevikku-suunav arvamusküsimus

- **Probleem (käitumispõhisus):** UX-uurijate seas on laialt teada, et inimesed on **halvad ennustajad iseenda tulevasele käitumisele** (\enquote{kas te kasutaksite seda kodus?} korreleerub tegeliku kasutusega kehvasti). See on klassikaline näide rikkumistest, mille vastu prompti kriteerium 2 (käitumispõhisus) just hoiatab.
- **Näide kavast:** \enquote{kodus kasutamise valmisoleku hinnangud}.
- **Mõju:** ainsa subjektiivse \enquote{kasutuselevõtu-tahte} näitaja andmed jäävad nõrgaks ja võivad olla optimistlikult kallutatud.

### 2.4 Avatud küsimus on liiga lai ja ühepoolne

- **Probleem (vastatavus + suunavus):} \enquote{häiriva või üllatava kogemuse kohta} eeldab, et kogemus oli **negatiivne või ootamatu}. See võib jätta lugemata positiivsete üllatuste või neutraalsete \enquote{ei midagi erilist} vastuste varjundi. Lisaks on küsimus mitut sorti kogemuse kohta korraga (\enquote{häiriv} ja \enquote{üllatav} on kaks erinevat asja).
- **Mõju:} kvalitatiivne tagasiside jääb kitsamaks, kui see võiks olla, ja võib retoorikaeesmärgil tunduda \enquote{vea-jaht}, mitte avatud uurimine.

### 2.5 \enquote{Käskude loomulikkus} on tehniliselt mitmetähenduslik

- **Probleem (vastatavus):** \enquote{käsu loomulikkus} võib tähendada (a) sõnastust eesti keeles, (b) intonatsiooni-mugavust, (c) süsteemi vastuse loomulikkust, (d) ülesande loogikat. Tavakasutaja ei pruugi suuta neid eraldada.
- **Mõju:} skoor jääb segaseks kompositsiooniks; raske tõlgendada.

---

## 3. Konkreetsed soovitused ja parandused

### 3.1 Kustuta / väldi
- **Eemalda \enquote{kodus kasutamise valmisolek}** kui isolatsioonis küsitud Likert-skaala. Kui seda kasutada, tuleb see asendada käitumispõhise küsimusega (vt 3.2).
- **Ära raporteeri uurija koostatud küsimusi koondskooriga**; töö ütleb seda juba, aga seda tasub ka tabelite tasandil rangelt järgida.

### 3.2 Sõnasta ümber
Vääratele küsimustele alternatiivid (kõik akadeemiliselt korrektsed, eestikeelsed, käitumiskesksed):

| Algne | Soovitatav alternatiiv |
|---|---|
| \enquote{kodus kasutamise valmisolek} (Likert) | \enquote{Kui see seade oleks teie kodus järgmised seitse päeva, **mis oleks esimene asi, mida te sellega teeksite?}\enquote{} (avatud, käitumispõhine, mineviku kavatsuse asemel konkreetse esimese sammu kohta). |
| \enquote{käskude loomulikkus} (üks Likert) | jaga kaheks: (1) \enquote{Kui kerge oli teil meelde tuletada, **kuidas} käsku öelda?}, (2) \enquote{Kas kasutasite mõnda käsku, **mille te ise välja mõtlesite}, mitte juhendis pakutu?} |
| \enquote{häiriva või üllatava kogemuse kohta} | jaga kaheks: (1) \enquote{Kirjeldage **üht hetke}, kus süsteem teid üllatas --- positiivselt või negatiivselt.}, (2) \enquote{Kas oli mõni hetk, kus teil tekkis tunne, et süsteem **ei mõistnud teid}? Mis sel hetkel täpselt juhtus?} |
| \enquote{usaldusväärsus} (Likert isolatsioonis) | täienda käitumispõhise kontrollküsimusega: \enquote{Kui sageli pidite **ütlust kordama}, et süsteem reageeriks?} (kvantitatiivne enesehinnang, mida saab võrrelda logitud andmetega). |

### 3.3 Lisa
Kui aeg lubab (mis on töö enda piirangu järgi pingul --- 18.05.2026 deadline), kaalu **väikest formatiivset eelvooru} (5--6 mitteformaalset intervjuud, igaüks ${\sim}15$ min) **enne} prototüübi külmutamist. Sisuteemad:

1. **Praegune käitumine:** \enquote{Kuidas te täna oma kodus valgust / muusikat / TV-d juhite? Mis on viimati teile selle juures närvidele käinud?} (mineviku-, mitte tulevikukäitumine; mittesuunav).
2. **Häälkasutuse ajalugu:** \enquote{Kas olete kunagi proovinud Sirit, Alexat, Google'it eesti keeles? Mis juhtus?} (konkreetne sündmus, mitte arvamus).
3. **Privaatsus-mudel:} \enquote{Kui te ütlete \enquote{Hei Siri}, kuhu see hääl teie arvates läheb?} (mentaalse mudeli paljastamine; ei suru ette \enquote{pilve halba} narratiivi).
4. **Eestikeelse häälkasutuse barjäärid:** \enquote{Mille pärast te täna eesti keeles häälega oma kodu ei juhi?} (mineviku põhjused, mitte tuleviku ennustus).

Need annaksid lõputöö sissejuhatusele **kasutajatõenduse motivatsioonisamba**, mis praegu tugineb ainult kirjandusele.

Lisaks on olemasolevasse post-test küsimustikku metoodiliselt kasulik lisada:

- **\enquote{Eelmise nädala} sagedushinnang}: \enquote{Mitu korda eelmise nädala jooksul te häälega midagi käivitasite?} See annab võrdluspunkti subjektiivsele \enquote{kodus kasutamise valmidusele}.
- **\enquote{Mis ajendaks teid seda **mitte} kasutama?}** Sümmeetria-küsimus, mis maandab acquiescence-kallutust.

---

## 4. Keelelised parandused

Kuna **probleemiintervjuu kava kui artefakt eesti keeles ei eksisteeri** (post-test küsimustik on töös kirjeldatud üldsõnaliselt, mitte täisküsimustena), siis tegelikku redaktsioonikontrolli teha ei saa. Üldised tähelepanekud küsimustiku **plaanistuse} kohta:

- **Algne tekst:** \enquote{süsteemi usaldusväärsuse, kiiruse, käskude loomulikkuse ja kodus kasutamise valmisoleku hinnangud}
- **Parandus:} kui see saab konkreetseteks Likert-väideteks, tuleb need formuleerida **stabiilse polaarsusega} (kõik \enquote{nõustun täielikult}--\enquote{ei nõustu üldse}) ja **akadeemilise tühjusega} (\enquote{Süsteem reageeris minu äratusele kiiresti.}, mitte \enquote{Süsteem oli kiire.}).
- **Põhjus:} stabiilne polaarsus vähendab vastusekomplekti kallutust; lauseehitus vähendab tõlgendusvabadust.

- **Algne tekst:} \enquote{üks avatud küsimus häiriva või üllatava kogemuse kohta}
- **Parandus:} \enquote{Palun kirjeldage **ühte konkreetset hetke} tänasest sessioonist, kui süsteem käitus teie ootuste **vastaselt} --- kas paremini või halvemini.}
- **Põhjus:** kohmakas lauseehitus algses sõnastuses (\enquote{häiriva või üllatava} laob kaks erinevat afektitooni kõrvuti); parandus küsib **konkreetset sündmust} (käitumispõhine), mitte üldist hinnangut.

---

## Kokkuvõte auditist

Käesolev prompt eeldab artefakti, mida lõputöös ei ole. Lähim sihtmärk --- post-test rahuloluküsimustik koos UMUX-Lite-ga (\texttt{second\_chapter.tex}, §\ref{sec:user-test-methodology}) --- on **iseenesest metoodiliselt korrektselt sõnastatud}, kuid see ei kata probleemide tuvastamist olemasoleva süsteemi suhtes. Kui üliõpilane soovib promptiga seotud panust **tegelikult tugevdada**, on kõige väiksema kuluga samm 5--6 osalejaga formatiivne intervjuude eelvoor enne prototüübi külmutamist (3.3). Kui see ei mahu deadline'i, tuleks lõputöös selgelt deklareerida, et kasutajatõendus tugineb **summatiivsele post-test andmestikule}, mitte formatiivsetele probleemiintervjuudele, ning et see on töö teadlik metoodiline piirang --- mitte puudus, mille üliõpilane oleks kahe silma vahele jätnud.

Ühtlasi tuleb mainida, et hindamiskriteeriumi 5 (keeleline korrektsus) tähenduses ei ole töös konkreetset intervjuu **teksti}, mille trükivigu või käändelõppu saaks parandada; need parandused on tehtud üldisemal plaanistuse tasandil.
