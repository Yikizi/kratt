#import "../style.typ": *

Kaesolev peatukk annab vahekokkuvotte seni saavutatud tulemustest. Kuna projekti eksperimentaalne osa on veel pooleli, keskendub peatukk eelkõige sellele, millised osad pipeline'ist on juba valideeritud ning millised probleemid on avastatud.

== Treeningutoru rekonstrueerimine ja parandused
Esialgne "Kratt" treeningukatse ei andnud usaldusvaarset tulemust. Hilisem sessioonilogide rekonstrueerimine naitas, et probleem ei olnud ainult mudeli kvaliteedis. Protsessis esines vahemalt kolm eri klassi vigu:
- `microWakeWord` treeningukoodis tekkis TensorFlow / NumPy uhilduvusprobleem;
- evaluatsioonis puudus korrektne `testing_ambient` kogum;
- andmestiku domeen erines reaalsest kasutusolukorrast, sest osa positiivsetest naidetest tuli telefonisalvestustest voi teistsugusest akustikast.

Nende leidude pohjal parandati nii treeninguskripte kui ka hindamisloogikat. Eriti oluline oli `ambient` andmete tugi `mmap` genereerimisel ning sellele lisatud automaatne raport, mis teeb probleemid nahtavaks graafikute ja CSV-failidena.

== Avaliku andmestiku sanity-check
Pärast lokaalse toru parandamist käivitati from-scratch sanity-check katse `Speech Commands` korpuse `marvin` sihtsona peal @speechcommands2018. Selle katse eesmärk ei olnud luua lõplikku kasutusmudelit, vaid valideerida, et kohalik treeningu- ja hindamistoru töötab iseseisvalt ka avaliku kontrollitava andmestiku peal.

Katse tulemusena saadi edukalt:
- `mmap` tunnusefailid;
- treenitud `microWakeWord` mudel;
- kvantiseeritud TFLite artefakt;
- automaatselt genereeritud analuusikaust graafikute ja tabelitega.

See on oluline tulemus, sest sellega eraldati infrastruktuuriprobleemid eestikeelse andmestiku probleemidest. Kui avalik `marvin` eksperiment tootas, ei saa enam koiki hilisemaid probleeme kirjutada treeningutoru enda arvele.

== Hindamisprotsessi peamine oppetund
Koige olulisem vahekokkuvote puudutab evaluatsiooni. Varasemas `Kratt` run'is oli ROC analuus sisuliselt degenerate, sest `testing_ambient` oli tuhi. Selle tulemusena saadud `AUC 0.00000` ei viidanud heale mudelile, vaid katkisele hindamisprotsessile. Hilisemad parandused kinnitasid, et ilma pika ambient-signaalita ei ole voimalik usaldusvaarset `FAPH` hinnangut anda.

See tulemus on loputoo seisukohalt oluline, sest see muudab ka uurimiskusimust. Eesmargiks ei ole enam ainult "treenida mudel", vaid "ehitada selline pipeline, mis voimaldab mudelit ausalt hinnata". See metoodiline nihe on kaesoleva too üks keskseid leide.

== Praegune seis
Kaesoleva kirjutamise hetkeks on olemas:
- toimiv kohalik treeningu-, ekspordi- ja raportitoru;
- avalikul andmestikul valideeritud `marvin` baseline;
- allalaadimisel ja ettevalmistamisel suuremad ambient- ning koonekorpused `MUSAN`, `VOiCES` ja `Common Voice`;
- esialgne arusaam, millistest andmeliikidest tuleb eestikeelne `Kratt` andmestik koostada.

Jargmises etapis laiendatakse ambient-evali pikemate avalike korpustega ning seejarel koostatakse sama struktuuriga eestikeelne andmestik. Loppversioonis lisatakse siia peatukki ka koondtabelid threshold'ide, `FAPH`, `FRR` ja valitud cutoff'ide kohta.
