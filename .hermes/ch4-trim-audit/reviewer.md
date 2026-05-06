Ma ei saa selles sessioonis faili kirjutada: olemasolevad tööriistad on ainult lugemiseks ning bash on piiratud read-only käskudele. Allpool on `reviewer.md` sisu, mille saab salvestada sihtteele.

```markdown
## Files Reviewed
- `docs/thesis/thesis-tex-estonian/chapters/third_chapter.tex` (lines 1-243)

## P0 (must cut/rewrite)
- `third_chapter.tex:18-119` - Peatüki keskne argument mattub metoodika-README alla. Positiivsete/negatiivsete kogumisprotokollid, Androidi logija, augmentatsioon, streaming-parameetrid, MoE ja ESP32 konfiguratsioon tuleks tõsta lisasse või koondada 1 tabeliks. Peatükki jäta ainult kaitstav metoodiline tuum: andmeallikas, sõltumatus/hold-out, kõnelejate arv, mõõdik ja peamine piirang.
- `third_chapter.tex:44-52` - Androidi valevallandumiste logija lõik on praegu rakenduse dokumentatsioon, mitte väite tõendus. Lõika Kotlini paketitee, `Settings.kt`, `AudioCapture.kt`, `EventLogger.kt`, `Build.MODEL`, JSONL-väljad ja eelseadistuste detailid. Jäta 2-3 lauset: seade, miks koguti, kuidas käsitsi valideeriti, kuidas see mõjutas negatiivset klassi.
- `third_chapter.tex:54-73` - Augmentatsiooni ja arhitektuuri parameetrid on liiga detailsed ning loovad mulje, et peatükk on konfiguratsioonifaili seletus. Tõsta lisasse. Peatükis piisab: “treening kasutas microWakeWordi mixednet-mudelit, SpecAugmenti ning piiratud müra-/RIR-augmentatsiooni; täpne konfiguratsioon lisas X.”
- `third_chapter.tex:171-179` - Agentpõhise arenduse osa on sisuliselt kõrvalteema ja kordab, et tööriistad aitasid kiiremini protokolli ehitada. Kui see pole töö uurimisküsimus, lõika tervikuna või vähenda üheks lõiguks peatüki lõpus.

## P1 (should cut)
- `third_chapter.tex:3-11` - Avaliku `marvin` kontrollkatse ja kahe raamistiku võrdluse põhjendus on liiga üldsõnaline. Mõlemad võiks koondada üheks lühikeseks lõiguks: “avalik sanity-check eristas toruvea keele-/andmeveast; raamistikuvõrdlus kinnitas, et valik oli sihtseadme kompromiss.” Praegused read kõlavad kaitsekõnena, mitte analüüsina.
- `third_chapter.tex:13-31` - Domeeninihke lõik algab hüpoteetilise “telefon vs kaugmikrofon” näitega, kuid seejärel ütleb, et praegune korpus seda probleemi ei sisalda. See nõrgestab argumenti. Alusta otse tegelikest jääkriskidest: üks kõneleja, üks ruum, piiratud kaugused, TTS ei asenda päriskõnelejate varieeruvust.
- `third_chapter.tex:33-41` - Sarnaste negatiivnäidete protokoll on kaitstav, kuid liiga pikk. Säilita sisukriteerium, maht, train/eval lahusus ja hold-out. Lõika Silero VAD-i täpsed parameetrid, 5-min chunkimine ja failinimed lisasse.
- `third_chapter.tex:75-99` - Streaming- ja MoE-hindamine on metoodiliselt oluline, kuid tekst on ülekoormatud skriptide, CLI-käskude ja mudelifailide teedega. Tee 1 kompaktne tabel: korpused, tunnid, lävi, silumine, refraktoorperiood, FAPH-valem. Failiteed lisasse.
- `third_chapter.tex:121-169` ja `third_chapter.tex:181-226` - Need kaks plokki kordavad sama põhiargumenti: standardsed mõõdikud ei ennusta kasutust, vaja on mitmemõõtmelist protokolli. Ühenda need üheks “Kolm valideerimisringi” narratiiviks, kus iga ring sisaldab: vana mõõdik → avastatud lühitee → parandus.
- `third_chapter.tex:228-238` - “Mida saab juba praegu väita” kordab juba eelnevat panuse sõnastust. Lõika või muuda väga lühikeseks kokkuvõtteks, maksimaalselt 3 bullet’it.

## P2 (consider)
- `third_chapter.tex:1` - Ava kohe peatüki panusega, mitte üldise väitega. Soovitus: “Peatükk näitab, kuidas ühe mõõdiku põhine hindamine asendus kolme auditiringi tulemusel mitmemõõtmelise protokolliga.”
- `third_chapter.tex:24-31` - TTS-i rolli sõnastus on liiga rahustav. Lisa piirang: TTS laiendab akustilist varieeruvust, kuid ei tõenda üldistumist päriskõnelejatele.
- `third_chapter.tex:101-115` - Reaalajas seadmetesti protokoll on kasulik, kuid statistiliselt nõrk. Hoia ainult selleks, et põhjendada, miks tulemused on illustratiivsed, mitte lõplikud.
- `third_chapter.tex:117-119` - ESP32 konfiguratsioon on väga tihe ühe-lõiguline YAML-seletus. Kui juurutus pole peatüki põhiargument, tõsta lisasse ja jäta ainult “lävi ja silumine vastasid hindamisprotokollile”.
- `third_chapter.tex:240-242` - Kaskaadarhitektuuri lõik on hea edasise töö materjal, kuid liiga tihe kirjanduse loetelu. Lühenda või vii eraldi “Edasine töö” peatükki.

## Summary
Peatüki kaitstav tuum on tugev: töö panus on mitmemõõtmeline hindamisprotokoll, mitte üks konkreetne mudel. Praegu varjavad seda liiga pikad konfiguratsiooni-, failitee- ja rakendusdetailid. Soovitan agressiivselt lühendada umbes 40-50% võrra: peatükki jäägu argument ja metoodika piirangud, lisasse kogu taastootmiseks vajalik konfiguratsioon.
```