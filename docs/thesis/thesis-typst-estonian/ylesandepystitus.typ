#import "config/config.typ": cfg
#import "style.typ": *

#align(center)[
  TALLINNA TEHNIKAÜLIKOOL#linebreak()
  Infotehnoloogia teaduskond

  #v(4.5cm)
  Mattias Linholm 233408IAIB

  #v(1.5cm)
  #text(size: 20pt, weight: "bold")[Kratt: eestikeelne äratussõnatuvastus nutikodu mikrokontrolleritele]

  #v(1.5cm)
  Bakalaureusetöö ülesandepüstitus
]

#v(0.6cm)
#align(right)[
  Juhendaja: Tanel Alumäe
]

#v(5cm)
#align(center)[Tallinn #cfg.year]

#pagebreak()
#set heading(numbering: "1.")

#heading(level: 1)[Sissejuhatus]
<sissejuhatus>

#heading(level: 2)[Probleem]
<probleem>
Lokaalse nutikodu hääljuhtimise kasutatavus sõltub suurel määral sellest, kas äratussõna tuvastus on stabiilne ja usaldusväärne. Eesti keele ja teiste väikeste keeleruumide kontekstis on tegemist olulise probleemiga, kuna spetsiifiliste treeningandmete vähesus takistab olemasolevate lahenduste otsekasutamist ja need ei taga samaaegselt piisavat mudeli kvaliteeti, süsteemi lihtsat lõimitavust ja reprodutseeritavat kasutuselevõttu.

Käesoleva töö keskne uurimisküsimus on, kuidas töötada välja eestikeelse äratussõna lahendus, mis on ühtaegu tehniliselt täpne, süsteemselt lõimitav ja praktiliseks kasutuseks sobiv. Eesmärk ei ole üksnes näidata mudeli tööd isoleeritud testkeskkonnas, vaid luua standardsetele protokollidele, nagu Wyoming @nabucasa2024wyoming, toetuv terviklahendus, mis on kasutatav modulaarse nutikodu komponendina.

#heading(level: 2)[Töö eesmärk]
<töö-eesmärk>
Töö eesmärk on töötada välja eestikeelne äratussõna mudel fraasile „Kuule Kratt” ja hinnata selle sobivust Home Assistanti lokaalse hääljuhtimise osana.

Eesmärgi saavutamiseks käsitletakse töös kolme omavahel seotud osa:
- *mudeliarendus* – eestikeelse treeningandmestiku koostamine ja äratussõna mudeli treenimine,
- *süsteemi lõimimine* – mudeli rakendamine demonstreerival riistvaral ja integreerimine Home Assistanti lokaalsesse kõnetöötlusahelasse standardiseeritud protokollide abil,
- *empiiriline valideerimine* – lahenduse tehniline mõõtmine ja kasutajapõhine hindamine mudeli edukuse määramiseks erinevate kõnelejatega.

#heading(level: 1)[Metoodika]
<metoodika>

#heading(level: 2)[Olemasolevate lahenduste analüüs]
<olemasolevate-lahenduste-analüüs>
Töös analüüsitakse olemasolevaid avatud lähtekoodiga äratussõna tuvastuse lähenemisi, nagu `microWakeWord` @ahrendt2024microwakeword ja `openWakeWord` @scripka2024openwakeword, ning hinnatakse nende sobivust väikese keeleruumi tingimustes. Eraldi käsitletakse süsteemseid nõudeid, mis tulenevad Home Assistanti hääljuhtimise arhitektuurist.

#heading(level: 2)[Andmestiku koostamine ja mudeli arendamine]
<andmestiku-koostamine-ja-mudeli-arendamine>
Töö käigus koostatakse eestikeelne treeningmaterjal. Andmepuuduse ületamiseks kombineeritakse inimeste häälenäidiseid lokaalsete kõnesünteesi lahendustega, kasutades muuhulgas Tartu Neurokõne mudelit, ning rakendatakse andmete rikastamise (*data augmentation*) tehnikate abil nende sünteetilist paljundamist. Pärast genereeritud andmete kvaliteedikontrolli treenitakse mikrokontrolleritele optimeeritud ja reaalajas voogedastust toetav äratussõna mudel. Arenduses rakendatakse MixConv kihtidel põhinevat `mixednet` arhitektuuri, et saavutada mälupiirangutega seadmetel piisav tuvastustäpsus. Mudeli loomisel käsitletakse parameetrite valikut, tundlikkuse häälestamist ja tulemuste reprodutseeritavust.

#heading(level: 2)[Tehniline teostus ja süsteemi lõimimine]
<tehniline-teostus-ja-süsteemi-lõimimine>
Mudeli arenduse järel kvantiseeritakse mudeli kaalud, et muuta see käivitatavaks ESP32-S3-Korvo-2 arendusplaadi sarnasel madala ressursiga seadmel. Seejärel lõimitakse valminud mudel Wyoming protokolli abil Home Assistanti kõnetöötlusahelasse. Tehnilise teostuse eesmärk on tagada, et lahendus oleks rakendatav ilma erilahendusi nõudva käsitööta.

#heading(level: 2)[Tulemuste valideerimine]
<tulemuste-valideerimine>
Valideerimine toimub kahel tasandil.

Esimene tasand on tehniline valideerimine, mille käigus hinnatakse tuvastuse kvaliteeti, valekäivituste ja möödalaskmiste esinemissagedust, latentsust ning töökindlust erinevates tingimustes.

Teine tasand on kasutuspõhine valideerimine, mille käigus hinnatakse lahenduse äratundmisvõimet laiemas kõnelejate valimis, esitades mudelile erinevate inimeste häälenäidiseid ja mõõtes tuvastuse täpsust mürarikkas igapäevakeskkonnas. Eesmärk on kindlustada süsteemi paindlikkus, et mudel töötaks ootuspäraselt ka treeningandmetes esindamata kõnelejatega.

Lisaks valideerimise tulemustele tuuakse välja ka lahenduse piirangud, riskid ja üldistatavuse ulatus.

#heading(level: 1)[Oodatav panus]
<oodatav-panus>
Töö panus on kahetine.

Esiteks annab töö tehnilise panuse eestikeelse äratussõna tuvastuse ja Home Assistanti lõimimise valdkonda.

Teiseks loob töö praktilise väärtuse, pakkudes avatud lähtekoodiga treenitud mudelit, sünteesitud andmete genereerimise koodibaasi ning valmis integratsioonilahendusi, vältides toorsalvestuste avalikustamisest tulenevaid privaatsusriske. See on kindlaks alguspunktiks teistele nutikodu huvilistele sarnase eestikeelse süsteemi seadistamisel.

#heading(level: 1)[Töö piiritlemine]
<töö-piiritlemine>
Töö fookus on äratussõna tuvastusel ja selle süsteemsel hindamisel.

Töö ei käsitle uute kõnetuvastuse ega kõnesünteesi mudelite algusest peale välja töötamist. Neid, eeskätt Kiirkirjutaja kõnetuvastusmudelit @alumae2024kiirkirjutaja, kasutatakse toetavate komponentidena ulatuses, mis on vajalik terviklahenduse valideerimiseks.

#pagebreak()
#bibliography("ylesandepystitus.bib", title: [Kasutatud kirjandus])
