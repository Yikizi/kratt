#import "../style.typ": *

Kaesoleva too eesmark on luua alus eestikeelse aratussona tuvastuse realiseerimiseks piiratud ressursiga nutikodu mikrokontrolleril. Seni tehtud toode pohjal on selgunud, et probleemi lahendamisel ei piisa ainult mudeli treenimisest, vaid vaja on terviklikku ja ausalt toimivat hindamispipeline'i.

Too kaigus rekonstrueeriti varasemad ebaonnestunud katsed, parandati `microWakeWord` pohist treeningu- ja evaluatsioonitoru ning valideeriti see avaliku `Speech Commands` andmestiku peal. Selle tulemusena saadi toimiv baseline, mille peale saab ehitada eestikeelse `Kratt` mudeli.

Peamine vahekokkuvote on, et wake word lahenduse kvaliteeti tuleb hinnata positiivsete ja negatiivsete klippide korval ka pika ambient-signaali peal. Ilma selleta voib mudel paista hea, kuigi reaalses kasutuses vallandub ta valesti. Seetottu on ambient-andmete korrektne kogumine ja kasutamine kaesoleva too keskne metoodiline noue.

Jargmiste sammudena laiendatakse avalikke ambient-korpusi, koostatakse eestikeelne `Kratt` andmestik ning viiakse labi samal torul loplikud katsed reaalse seadme akustilises keskkonnas.
