#import "../style.typ": *

Metoodika eesmargiks on kirjeldada selline arendus- ja hindamisprotsess, mille abil on voimalik eristada toru tehnilisi vigu andmestikust voi mudelist tulenevatest probleemidest. Praktikas on see oluline, sest vastasel juhul voib ebaonnestunud tulemus jaada valesti kas andmete, mudeli voi integraerimise taha.

== Kasutatud tehnoloogiad
Katsetuste keskmes on `microWakeWord`, mis on TensorFlow peal ehitatud wake word treeninguraamistik mikrokontrollerite jaoks @tensorflow2015 @microwakeword2026. Mudeli kasutuselevott toimub ESP32-S3 pohisel seadmel ning live integreerimiseks kasutatakse ESPHome'i (`voice_assistant` liidest) @esphome2026. Nutikodu koostoime sihtplatvorm on Home Assistant @homeassistant2026.

Selline valik ei ole juhuslik. `microWakeWord` annab kontrolli nii andmesisestuse, treeningu kui ka TFLite ekspordi ule. ESPHome omakorda lubab sama mudelit kasutada reaalsel seadmel ilma eraldi firmware't nullist kirjutamata. Seega on voimalik siduda kokku uurimuslik pool ja praktiline kasutus.

== Andmestiku rollid
Wake word mudeli puhul ei piisa ainult jagamisest treening- ja testandmeteks. Kaesolevas toos eristatakse kolme andmeliiki:
- positiivsed klipid, kus aratussona on kohal;
- negatiivsed klipid, kus aratussona ei ole kohal, kuid heli sisaldab koonet voi muid segavaid mustreid;
- ambient-salvestused, mis on pikad pidevad taustahelid ilma aratussonata.

Positiivsed klipid on vajalikud selleks, et mudel oppiks sihtsona akustilist mustrit. Negatiivsed klipid aitavad mudelil oppida, mida mitte pidada aratussonaks. Ambient-andmed on aga vajalikud hoopis hindamiseks, sest just nende pealt saab hinnata valepositiivsete vallandumiste sagedust ajayhiku kohta. See vahe osutus too kaigus kriitiliseks.

== Avalikud andmekorpused ja nende kasutus
Enne eestikeelse "Kratt" mudeli juurde liikumist otsustati pipeline valideerida avaliku andmestiku peal. Selleks valiti `Speech Commands` korpus ja sihtsona `marvin` @speechcommands2018. Valiku pohjuseks oli see, et tegemist on laialt kasutatava ja kontrollitava baasandmestikuga, mille peal saab hinnata, kas treening, eksport ja eval toimivad otsast lopuni.

Ambient- ja hard-negative allikatena lisati protsessi `MUSAN`, `VOiCES` ning `Common Voice` @musan2015 @voices2018 @commonvoice2020. Nende rollid on erinevad. `MUSAN` annab palju muusikat, myra ja koonet. `VOiCES` lisab kaugkoone ja ruumiakustika, mis on nutikodu seadme jaoks realistlikum. `Common Voice` on oluline eelkõige koonepohiste negatiivsete naidete allikana ning hiljem ka eestikeelse mudeli taustamaterjalina.

== Treeningu ja hindamise toru
Andmed teisendatakse spektraalseteks tunnusteks ning salvestatakse `mmap` vormingus. `mmap` ehk memory-mapped file voimaldab suuri andmehulkasid lugeda kettalt ilma, et kogu korpus tuleks korraga RAM-i laadida. See on oluline nii treeningukiiruse kui ka stabiilsuse jaoks.

Toru peamised etapid on jargmised:
- andmete ettevalmistus ja jagamine rollide kaupa;
- tunnuste genereerimine ning `training`, `validation`, `testing`, `validation_ambient` ja `testing_ambient` kogumite moodustamine;
- mudeli treenimine `microWakeWord` raamistikus;
- voogedastuse jaoks sobiva TFLite mudeli eksport;
- hindamine nii luhikeste klippide kui ka pika ambient-signaali peal;
- raporti ja graafikute genereerimine.

Oluline metoodiline otsus oli lisada torusse automaatne raportikiht, mis toodab ROC-kovera, skoorejaotused ning threshold-mootdikud. See lihtsustab nii arendustood kui ka hilisemat loputoo tulemuste esitamist.

== Hindamismootdikud
Wake word mudeli hindamine erineb tavalisest klassifikatsioonist selle poolest, et olulised on nii tabamused kui ka valevallandumised pidevas voos. Seetottu kasutatakse siin lisaks recall'ile ja precision'ile ka streaming-eval'i mootdikuid:
- `FRR` ehk false rejection rate, mis naitab kui suur osa tegelikest aratussona juhtudest jaab tabamata;
- `FAPH` ehk false accepts per hour, mis naitab kui palju valevallandumisi tekib tunni kohta;
- ROC-laadne kover, kus vaadeldakse `FRR` ja `FAPH` vahelist seost eri threshold'ide korral.
- Mudelivõrdluste puhul hoitakse võrdlusfaasis threshold ühtsena ja raporteeritakse lisaks `FAPH`-le ning `recall`ile ka hard-negative `FPR`; väikesem valim või lühiajalised ambient-sektsioonid lisavad tulemuste juurde ebakindlust, mistõttu väärtused loetakse eelkõige võrdluslikult, mitte absoluutsete väidetena.

Too kaigus selgus, et just ambient-andmete puudumine voi vigane moodustamine voib muuta kogu evaluatsiooni sisuliselt kasutuks. Kui `testing_ambient` on tuhi, ei kirjelda saadud AUC enam mudeli kvaliteeti, vaid peegeldab katkist hindamisprotsessi. Seetottu on andmestiku rollide korrektne eristamine selle too keskne metoodiline element.
