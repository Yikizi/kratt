#import "../style.typ": *

Nutikodu haaliidesed on liikunud aina vaiksemate, odavamate ja energiasaastlikumate seadmete poole, kuid eestikeelsete aratussonade tugi on endiselt killustatud. Praktikas tähendab see, et paljud valmis lahendused eeldavad pilveteenust, suuremat arvutusressurssi voi ingliskeelset kasutusmustrid. Kohaliku ja eestikeelse lahenduse loomine on seetottu korraga nii tehniline kui ka kasutajakogemuse probleem.

Kaesoleva too eesmargiks on uurida, kas eestikeelset aratussona on voimalik tuvastada piiratud ressursiga nutikodu mikrokontrolleril nii, et lahendus oleks praktiliselt kasutatav. Too keskmes on ESP32-S3 pohine seade, ESPHome tarkvarakiht (`voice_assistant` kaudu live integraatsioonis) ja `microWakeWord` treeninguraamistik @esphome2026 @microwakeword2026. Eraldi fookuses on asjaolu, et wake word lahendus peab toimima pidevas voos, mitte ainult luhikeste eeltoodeldud heliklipi peal.

Probleemi muudab keeruliseks kaks asjaolu. Esiteks on eestikeelseid valmis korpusi ja mudelitorusid selles valdkonnas vahe. Teiseks voib sama mudel anda hea tulemuse laborioludes, kuid hakata reaalses ruumis valesti vallanduma. Seetottu ei piisa ainult klassifikatsioonitapsusest; vaja on hinnata ka valepositiivseid trigger'eid pika ambient-signaali peal ning valida laevend `threshold`, mis tasakaalustab tabamuste ja valehairete suhte.

Too praktiline sisend on projekt "Kratt", mille eesmargiks on ehitada eestikeelne haalega juhitav nutikodu toru. Selles too osas keskendutakse kitsamalt aratussona tuvastusele, mitte kogu STT-LLM-TTS ahelale. Selline kitsendus on tahtlik, sest just wake word on kogu kasutuskogemuse esimene filter ning samal ajal koht, kus valehaired ja vahelejaamised on koige kiiremini tajutavad.

Too ulesanded on jargmised:
- koondada kokku lokaalne treeningu- ja hindamispipeline mikrokontrollerile sobiva wake word mudeli jaoks;
- valideerida pipeline avaliku andmestiku peal enne eestikeelse sihtsona juurde minekut;
- analuusida, millist rolli mangivad positiivsed, negatiivsed ja ambient-andmed mudeli hindamisel;
- kirjeldada, millised probleemid tekivad domeeninihke, andmekvaliteedi ja katkise evaluatsiooniprotsessi korral;
- luua alus, mille peale saab hiljem ehitada eestikeelse "Kratt" mudeli.

Too peamine uurimiskusimus on jargmine: kuidas ehitada ja hinnata eestikeelset aratussona tuvastust nii, et lahendus oleks usaldusvaarne piiratud ressursiga nutikodu mikrokontrolleril? Sellest tulenevad abikusimused puudutavad andmestiku koostamist, hindamismetoodikat ning seda, millises jarjekorras on mottekas pipeline'i valideerida.

Too struktuur on jargmine. Metoodika peatukk kirjeldab kasutatud tarkvarakomponente, andmekorpusi, treeningut ja hindamisloogikat. Tulemuste peatukk annab vahekokkuvotte seni loodud pipeline'ist ning avaliku sanity-check eksperimendi tulemustest. Arutelu peatukk seob tehnilised leiud praktiliste kitsaskohtadega ning toob valja, mida tuleb eestikeelse mudeli jaoks teisiti teha.
