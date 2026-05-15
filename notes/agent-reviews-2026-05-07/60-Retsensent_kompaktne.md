---
source_prompt: /Users/mattias/Downloads/loputoo_viibad_2026_04_28-2/04_Kontrollimine/Üldisem_tagasiside/Retsensent_kompaktne.txt
prompt_type: evaluative
generated: 2026-05-07
---

### Teema aktuaalsus ja uurimisprobleem
* Lõputöö käsitles eestikeelse äratussõna \enquote{Kuule Kratt} tuvastust piiratud ressursiga ESP32-S3-klassi mikrokontrolleril ning kohaliku nutikodu kõnejuhtimise toru integreerimist Home Assistantiga.
* Teema on aktuaalne, sest avalikud äratussõna raamistikud (microWakeWord, openWakeWord, Picovoice Porcupine) eesti keelt ei toeta, mistõttu kohaliku ja privaatsust säilitava väikese keele häälassistendi loomine sõltub just selle komponendi olemasolust.

### Lõputöö vastavus teemale ja püstitatud eesmärgile, teema läbitöötatus
* Töö sisu vastas teemale: kõik peatükid keskendusid äratussõna mudeli arendamisele, hindamisele ja seadmesse paigutamisele ega kaldunud STT/TTS valdkonda kõrvale.
* Pealkiri ja sisu olid omavahel kooskõlas, kuigi lõpliku tootmisküpse mudeli asemel rõhutati metoodilisi ja hindamisalaseid tulemusi, mis pealkirjast otseselt välja ei loe.
* Autor saavutas püstitatud eesmärgi osaliselt: reprodutseeritav treeningu- ja hindamistoru valmis ning ESP32-S3 sobiv mudel quantiseeriti, kuid juurutusotsust toetav lõplik kasutajatest oli töö esitamise hetkel veel käimas, mistõttu osa eesmärgist (\enquote{sobivuse hinnang Home Assistanti lokaalse hääljuhtimise osana}) jäi tinglikuks.
* Teema läbitöötatuse tase oli põhjalik: autor võrdles raamistikke nelja telje kaudu, eristas FAPH-i nelja varianti, dokumenteeris kolm hindamisringi ja sidus leiud rahvusvahelise kirjandusega, mis ületas tavapärase bakalaureusetöö sügavuse.

### Lõputöö tulemused ja järeldused
* Tugevusena tõstis töö esile süstemaatilise lahknevuse standardsete KWS võrdlusaluste ja reaalse kasutusolukorra vahel ning pakkus selle leevendamiseks stsenaariumipõhise hindamisprotokolli, mis on ülekantav teistele madala ressursiga keeltele.
* Tugevusena tuvastas autor varasemates tulemustes andmelekke ning lahendas selle kõrvalejäetud komplektide ja disjointsuskontrolli kaudu, mis tõstis hilisemate hindamistulemuste usaldusväärsust.
* Tugevusena dokumenteeris töö ekspertmudelite konsensuse, mis saavutas Common Voice ET kõrvalejäetud komplektil FAPH = 0,79, ning sidus selle laiema kaskaadarhitektuuri ideega.
* Tugevusena käsitles autor eraldi positiivse klassi sildistusprobleemi (\enquote{kuule}/\enquote{kule} eesliite õppimine) ja lisas selle vastu fraasistruktuuri kontrollivad mõõdikud, mis on äratussõna kirjanduses tunnustatud praktika.
* Tugevusena reflekteeris autor ausalt agentpõhise arenduse rolli, kirjeldades seda töövõimendajana, mitte tõendusmaterjali asendajana.
* Nõrkusena raporteeris autor ise, et päriskõnelejate (\enquote{Kule}-häälduse) tuvastamismäär jäi juurutuslävel TTS-positiivsetest klippidest madalamaks ning lõpliku juurutusotsuse jaoks vajalik kasutajatest 20--30 osalejaga ei olnud töö esitamise hetkeks lõpule viidud.
* Nõrkusena tugines suur osa kvantitatiivsetest järeldustest punkthinnangutele ühel korpusel ja ühel operatsioonipunktil, kuigi Poissoni usaldusvahemik on lai; mitme korpuse paralleelne raporteerimine oleks väiteid kindlustanud.
* Nõrkusena jäi süstemaatiline mittekõneliste helide aktivatsioonimäär eraldi mõõtmata, kuigi autor tunnistas selle olulisust ja tõi anekdootlikke näiteid.
* Nõrkusena ei saavutanud ükski üksikmudel ega kombinatsioon korraga kõiki sihte (FAPH < 1, recall ≥ 0,95, sarnaste fraaside FPR), mistõttu praktiline tervikmudel jäi pigem disainikompromissiks kui tõendatud lahenduseks.
* Nõrkusena oleks lugejat aidanud üks koondtabel või -joonis, mis seoks mudeliversioonid (v6, v6-residual, v16c, expert-a, expert-b2) ja nende kõik mõõdikud ühte vaatesse; praegu olid arvud killustatud üle peatükkide.

### Lõputöö vormistus
* Vormistuse kvaliteet oli üldiselt hea: viitamine järgis akadeemilist tava, terminoloogia oli järjepidev, eesti- ja ingliskeelsed mõisted olid sissetoomisel selgitatud ning peatükkide ja alapeatükkide ülesehitus oli loogiline.

### Märkused
* Töö aktiivse kandidaadi (\texttt{v16c}) staatus jäi kohati ambivalentseks --- kohati nimetati seda \enquote{stabiilseks baasjooneks}, kohati \enquote{aktiivseks demo-kandidaadiks} ---, mis võib lugejat segadusse ajada.
* Mõnes lauses oli tekst tihedalt täidetud sulgudes esitatud lisamõõdikute, viidete ja tingimustega, mis raskendas esmalugemist; mõned sellised laused (nt FAPH-sihtmäära põhjendus sissejuhatuses) oleks võinud jagada kaheks.
* Kokkuvõte ja ülesandepüstitus esitasid eesmärgi kergelt erineva tonaalsusega: ülesandepüstitus rõhutas \enquote{terviklahendust}, samal ajal kui kokkuvõte rõhutas \enquote{metodoloogiliselt korrektset hindamist} --- see tasuks kaitsmisel selgitada.
* Töö viitas korduvalt tulemuste peatüki tabelitele (nt \texttt{tab:expert-consensus}, \texttt{tab:fair-comparison-holdout}), mille sisu antud kompaktne retsensiooni-vaade otseselt ei kontrollinud.

### Retsensendi küsimused lõputöö autorile
* Kuidas kavatses autor kasutajatesti tulemuste põhjal lõplikult otsustada \texttt{v16c}, ekspertkonsensuse ja \texttt{v6-residual} vahel, kui kasutajatest annaks vastuolulise pildi (nt parem recall ühel ja parem FAPH teisel mudelil)?
* Mis oli hinnanguline ülemine piir FAPH-i jaoks, mille juures autor pidanuks lahendust nutikodu igapäevases kasutuses talumatuks, ning kuidas see piir oleks empiiriliselt põhjendatud (kasutajakogemuse uuringud, omasalvestused)?
* Kuivõrd autor uskus, et väljapakutud mitmemõõtmeline hindamisprotokoll on otseselt ülekantav teistele väikese ressursiga keeltele (nt soome, läti) ilma, et iga kriteeriumi tuleks ümber kalibreerida; millised kriteeriumid oleksid keele-spetsiifilised?
* Mis takistas käesolevas töös kaskaadarhitektuuri (esimene aste + teise astme \enquote{kuule}/\enquote{kratt} eraldi kontroll) prototüüpimist, ja milliseid konkreetseid ressursse selle järgmine samm reaalselt nõuaks?
* Kuidas tagas autor, et agentpõhise arenduse abil loodud hindamisskriptid ja andmetöötluse koodibaas ei sisaldanud peidetud vigu, mis ise oleksid võinud tekitada uue, dokumenteerimata \enquote{neljanda ringi} riski (nt vaikne lävi-arvutuse viga, mille agent oli sisse kirjutanud)?
