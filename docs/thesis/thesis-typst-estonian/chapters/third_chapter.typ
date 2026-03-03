#import "../style.typ": *

Kaesoleva too seni koige olulisem jareldus on, et wake word projekti puhul voib tehniline edu olla petlik, kui hindamismetoodika on puudulik. Luhikeste klippide peal saadud head skoorid ei taga, et mudel toimib pidevas reaalses helivoolus. See sai selgeks hetkel, kui varasemad `Kratt` tulemused naitasid klippide peal kasutatavat kvaliteeti, kuid streaming-eval osutus katkise `ambient` sisendi tottu sisutuhjaks.

== Mida valideeritud pipeline tegelikult annab
`marvin` sanity-check ei lahendanud eestikeelset wake word probleemi, kuid ta lahendas teise, veel fundamentaalsema probleemi: kas meie kohalik toru on usaldusvaarne. Kui see samm oleks vahele jaanud, oleks iga jargnev ebaonnestumine voinud naida kui "halb eesti keel" voi "liiga vaike andmestik", kuigi tegelik probleem oleks voinud peituda hoopis evaluatsioonis voi eksporttorus.

Sellest vaatepunktist oli avaliku andmestiku peal tehtud kontroll eksperiment mitte lisatöö, vaid vajalik kontrollkiht. See on hea naide sellest, kuidas inseneritood tuleb teha jarjestusega, mis eemaldab ebaselgust, mitte ei kogu seda juurde.

== Andmestiku kvaliteet ja domeeninihe
Eestikeelse `Kratt` mudeli puhul tuleb eraldi arvestada domeeninihke riskiga. Kui positiivsed klipid on salvestatud telefoniga, aga loplik kasutus toimub kaugmikrofoniga nutikodu seadmel, siis on treeningu- ja kasutusjaotused erinevad. Sellisel juhul voib mudel oppida mustreid, mis ei kordu loplikus keskkonnas.

Sama kehtib ambient-andmete kohta. Kui ambient koosneb ainult vaikusest voi liiga puhastest naidetest, siis ei kirjelda see reaalset kodukeskkonda. Seepärast on metoodiliselt oluline, et loppfaasis lisataks avalikele korpustele ka samast mikrofonist ja samast akustilisest keskkonnast kogutud salvestused.

== Tulemuste esitlemise piirid
Kaesoleva versiooni tulemused on ausalt oeldes vahetulemused. See ei ole puudus, kui see on tekstis selgelt markeeritud. Vastupidi, loputoo tugevamaks osaks voib kujuneda just see, et too dokumenteerib mitte ainult loplikku mudelit, vaid ka seda, kuidas korrektne hindamisprotsess ules ehitati ning milliseid valesid jareldusi katkine eval tekitada voib.

See tahendab, et lopputekstis tuleb teadlikult eristada:
- mida on juba empiiriliselt kontrollitud;
- mida alles valmistatakse ette;
- millised vahekokkuvotted on juba piisavalt tugevad, et neid kasutada jareldustena.

Selline eristus aitab valta uletootlgendamist ning muudab too kaitstavaks ka siis, kui loplik eestikeelne mudel vajab veel mitut iteratsiooni.
