---
source_prompt: /Users/mattias/Downloads/loputoo_viibad_2026_04_28-2/03_Lõputöö_alamosad/Kohustuslikud/Sissejuhatus.txt
prompt_type: generative
generated: 2026-05-07
---

# Alternatiivne sissejuhatuse mustand (ülesandepüstituse põhjal)

Allolev tekst on prompti tüübi kohaselt genereeriv alternatiiv: see on kirjutatud ülesandepüstituse (`ylesandepystitus.tex`) põhjal, järgides prompti nõutud struktuuri ning eesti akadeemilise keele juhiseid. Tekst on esitatud puhta tekstina, ilma Markdowni vorminduseta pealkirjades, ning ei ole mõeldud praeguse `introduction.tex` sisu asendamiseks. Generaator ei lisa fakte, mida ülesandepüstituses ei ole; spetsiifilised tulemused, mõõdikud ja arvulised sihid (nt FAPH-i konkreetne sihtväärtus, kõnelejate arv, mudeli versioonid) on jäetud sisse toomata, kuna ülesandepüstituses neid ei esinenud.

---

1. Sissejuhatus

Lokaalse nutikodu hääljuhtimine on viimastel aastatel liikunud aina rohkem servaseadmete suunas, kus kõnetuvastuse esimene aste – äratussõna tuvastus – peab töötama pidevas helivoos, väikese energiakuluga ja võimalikult väikese viiteajaga. Sellise lahenduse usaldusväärsus on kogu hääljuhtimise kasutatavuse eelduseks: kui süsteem ei reageeri ootuspäraselt äratussõnale või vallandub valesti, kannatab kasutuskogemus sõltumata sellest, kui hea on kõnetuvastuse järgnev aste. Eesti keele ja teiste väikeste keeleruumide kontekstis süvendab seda probleemi spetsiifiliste treeningandmete vähesus, mis takistab juba olemasolevate avatud lähtekoodiga lahenduste otsest taaskasutamist. Käesolev töö käsitleb seda lünka, keskendudes eestikeelse äratussõna „Kuule Kratt“ tuvastusele lokaalsel mikrokontrolleril ja selle lõimimisele Home Assistanti hääljuhtimise ahelasse.

1.1 Taust ja probleem

Lokaalse nutikodu hääljuhtimise kasutatavus sõltub suurel määral sellest, kas äratussõna tuvastus on stabiilne ja usaldusväärne. Kui see esimene aste ei tööta ootuspäraselt, ei aita ka tugev kõnetuvastuse mudel hilisemates astmetes – kasutaja kogeb süsteemi ebausaldusväärsena ning loobub selle kasutamisest. Eesti keele ja teiste väiksemate keeleruumide kontekstis on tegemist olulise probleemiga, kuna spetsiifiliste treeningandmete vähesus piirab valikut: avatud lähtekoodiga raamistike juures jaotatud mudelid ei kata eesti keelt ning olemasolevate lahenduste otsekasutamine eeldaks treeningandmete kogumist mahus, mis on väikese keeleruumi tingimustes harva realistlik.

Praegune olukord on puudulik mitmes mõttes. Esiteks ei taga olemasolevad lahendused eesti keele puhul samaaegselt piisavat mudeli kvaliteeti, süsteemi lihtsat lõimitavust ja reprodutseeritavat kasutuselevõttu – iga neist tahust nõuab eraldi tööd, mille tulemused ei ole praegu süsteemselt dokumenteeritud. Teiseks tähendab spetsiifiliste treeningandmete puudumine, et lahenduse arendamine ei saa piirduda mudeli treenimisega, vaid peab hõlmama ka andmestiku koostamise metoodikat ning sünteetiliselt rikastatud andmete kvaliteedikontrolli. Kolmandaks on terviklik integreerimine nutikodu raamistikuga senini tõendatud üksnes konkreetse tehnoloogiakombinatsiooni – ESPHome ja Home Assistanti `voice_assistant` liidese – kaudu, mistõttu on vajalik selle integreerimisraja süstemaatiline kirjeldus, et lahendus oleks ka väljaspool käesolevat tööd korratav. Need kolm aspekti koos põhjendavad, miks eestikeelne äratussõna tuvastus vajab eraldi käsitlust ega lahene olemasolevate komponentide pelga liitmise teel.

1.2 Ülesandepüstitus

Töö eesmärk on töötada välja eestikeelne äratussõna mudel fraasile „Kuule Kratt“ ning hinnata selle sobivust Home Assistanti lokaalse hääljuhtimise osana. Eesmärk ei ole näidata mudeli tööd üksnes isoleeritud testkeskkonnas, vaid luua standardsetele protokollidele toetuv terviklahendus, mis on kasutatav modulaarse nutikodu komponendina.

Eesmärgi saavutamiseks käsitletakse töös kolme omavahel seotud osa. Esiteks mudeliarendus, mille raames koostatakse eestikeelne treeningandmestik ja treenitakse äratussõna mudel. Andmepuuduse ületamiseks kombineeritakse inimeste häälenäidiseid lokaalsete kõnesünteesi lahendustega, sealhulgas Tartu Neurokõne mudeliga, ning rakendatakse andmete rikastamise tehnikaid sünteetiliseks paljundamiseks; pärast kvaliteedikontrolli treenitakse mikrokontrolleritele optimeeritud ja reaalajas voogedastust toetav mudel, kasutades MixConv kihtidel põhinevat mixednet arhitektuuri.

Teiseks süsteemi lõimimine, mille käigus kvantiseeritakse mudeli kaalud, et muuta see käivitatavaks ESP32-S3-Korvo-2 arendusplaadil, ning lõimitakse mudel ESPHome'i `voice_assistant` liidese abil Home Assistanti kõnetöötlusahelasse. Lõimimise eesmärk on tagada, et lahendus oleks rakendatav ilma erilahendusi nõudva käsitööta, vaid standardiseeritud protokollide kaudu.

Kolmandaks empiiriline valideerimine, mis toimub kahel tasandil: tehnilise valideerimise käigus hinnatakse tuvastuse kvaliteeti, valekäivituste ja möödalaskmiste esinemissagedust, latentsust ning töökindlust erinevates tingimustes; kasutuspõhise valideerimise käigus hinnatakse lahenduse äratundmisvõimet laiemas kõnelejate valimis, esitades mudelile erinevate inimeste häälenäidiseid ja mõõtes tuvastuse täpsust mürarikkas igapäevakeskkonnas. Lisaks valideerimise tulemustele tuuakse välja lahenduse piirangud, riskid ja üldistatavuse ulatus.

1.3 Töö struktuur
