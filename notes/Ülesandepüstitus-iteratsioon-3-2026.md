TALLINNA TEHNIKAÜLIKOOL
Infotehnoloogia teaduskond
Mattias Linholm 233408IAIB
Eestikeelse äratussõna mudeli arendus ja lõimimine Home Assistanti lokaalsesse hääljuhtimisse
Bakalaureusetöö ülesandepüstitus
Juhendaja: Tanel Alumäe
Tallinn

## 1 Sissejuhatus

### 1.1 Probleem

Lokaalse nutikodu hääljuhtimise kasutatavus sõltub suurel määral sellest, kas äratussõna tuvastus on stabiilne ja usaldusväärne. Eesti keele ja teiste väikeste keeleruumide kontekstis on tegemist olulise probleemiga, kuna spetsiifiliste treeningandmete vähesus takistab olemasolevate lahenduste otsekasutamist ja need ei taga samaaegselt piisavat mudeli kvaliteeti, süsteemi lihtsat lõimitavust ja reprodutseeritavat kasutuselevõttu.

Käesoleva töö keskne uurimisküsimus on, kuidas töötada välja eestikeelse äratussõna lahendus, mis on ühtaegu tehniliselt täpne, süsteemselt lõimitav ja praktiliseks kasutuseks sobiv. Eesmärk ei ole üksnes näidata mudeli tööd isoleeritud testkeskkonnas, vaid luua standardsetele protokollidele, nagu Wyoming [4], toetuv terviklahendus, mis on kasutatav modulaarse nutikodu komponendina.

### 1.2 Töö eesmärk

Töö eesmärk on töötada välja eestikeelne äratussõna mudel fraasile „Kuule Kratt” ja hinnata selle sobivust Home Assistanti lokaalse hääljuhtimise osana.

Eesmärgi saavutamiseks käsitletakse töös kolme omavahel seotud osa:
- **mudeliarendus** – eestikeelse treeningandmestiku koostamine ja äratussõna mudeli treenimine,
- **süsteemi lõimimine** – mudeli rakendamine demonstreerival riistvaral ja integreerimine Home Assistanti lokaalsesse kõnetöötlusahelasse standardiseeritud protokollide abil,
- **empiiriline valideerimine** – lahenduse tehniline mõõtmine ja kasutajapõhine hindamine mudeli edukuse määramiseks erinevate kõnelejatega.

## 2 Metoodika

### 2.1 Olemasolevate lahenduste analüüs

Töös analüüsitakse olemasolevaid avatud lähtekoodiga äratussõna tuvastuse lähenemisi, nagu `microWakeWord` [2] ja `openWakeWord` [3], ning hinnatakse nende sobivust väikese keeleruumi tingimustes. Eraldi käsitletakse süsteemseid nõudeid, mis tulenevad Home Assistanti hääljuhtimise arhitektuurist.

### 2.2 Andmestiku koostamine ja mudeli arendamine

Töö käigus koostatakse eestikeelne treeningmaterjal. Andmepuuduse ületamiseks kombineeritakse inimeste häälenäidiseid lokaalsete kõnesünteesi lahendustega, kasutades muuhulgas Tartu Neurokõne mudelit, ning rakendatakse andmete rikastamise tehnikate abil nende sünteetilist paljundamist. Pärast genereeritud andmete kvaliteedikontrolli treenitakse mikrokontrolleritele optimeeritud ja reaalajas voogedastust toetav äratussõna mudel. Arenduses rakendatakse MixConv kihtidel põhinevat `mixednet` arhitektuuri, et saavutada mälupiirangutega seadmetel piisav tuvastustäpsus. Mudeli loomisel käsitletakse parameetrite valikut, tundlikkuse häälestamist ja tulemuste reprodutseeritavust.

### 2.3 Tehniline teostus ja süsteemi lõimimine

Mudeli arenduse järel kvantiseeritakse mudeli kaalud, et muuta see käivitatavaks ESP32-S3-Korvo-2 arendusplaadil. Seejärel lõimitakse valminud mudel Wyoming protokolli abil Home Assistanti kõnetöötlusahelasse. Tehnilise teostuse eesmärk on tagada, et lahendus oleks rakendatav ilma erilahendusi nõudva käsitööta.

### 2.4 Tulemuste valideerimine

Valideerimine toimub kahel tasandil.

Esimene tasand on tehniline valideerimine, mille käigus hinnatakse tuvastuse kvaliteeti, valekäivituste ja möödalaskmiste esinemissagedust, latentsust ning töökindlust erinevates tingimustes.

Teine tasand on kasutuspõhine valideerimine, mille käigus hinnatakse lahenduse äratundmisvõimet laiemas kõnelejate valimis, esitades mudelile erinevate inimeste häälenäidiseid ja mõõtes tuvastuse täpsust mürarikkas igapäevakeskkonnas. Eesmärk on kindlustada süsteemi paindlikkus, et mudel töötaks ootuspäraselt ka treeningandmetes esindamata kõnelejatega.

Lisaks valideerimise tulemustele tuuakse välja ka lahenduse piirangud, riskid ja üldistatavuse ulatus.

## 3 Oodatav panus

Töö panus on kahetine.

Esiteks annab töö tehnilise panuse eestikeelse äratussõna tuvastuse ja Home Assistanti lõimimise valdkonda.

Teiseks loob töö praktilise väärtuse, pakkudes avatud lähtekoodiga treenitud mudelit, sünteesitud andmete genereerimise koodibaasi ning valmis integratsioonilahendusi, vältides toorsalvestuste avalikustamisest tulenevaid privaatsusriske. See on kindlaks alguspunktiks teistele nutikodu huvilistele sarnase eestikeelse süsteemi seadistamisel.

## 4 Töö piiritlemine

Töö fookus on äratussõna tuvastusel ja selle süsteemsel hindamisel.

Töö ei käsitle uute kõnetuvastuse ega kõnesünteesi mudelite algusest peale välja töötamist. Neid, eeskätt Kiirkirjutaja kõnetuvastusmudelit [1], kasutatakse toetavate komponentidena ulatuses, mis on vajalik terviklahenduse valideerimiseks.

## 5 Esialgsed allikad

1. T. Alumäe, „Kiirkirjutaja: Real-time Estonian Speech Recognition,” 2024. [Võrguteavik]. Saadaval: https://github.com/alumae/kiirkirjutaja
2. K. Ahrendt, „microWakeWord,” 2024. [Võrguteavik]. Saadaval: https://github.com/kahrendt/microWakeWord
3. D. Scripka, „openWakeWord,” 2024. [Võrguteavik]. Saadaval: https://github.com/dscripka/openWakeWord
4. Nabu Casa, „Home Assistant Voice Control ja Wyoming protokoll.” [Võrguteavik]. Saadaval: https://www.home-assistant.io/voice_control/
