# v5 — TTS positiivid + hard negatives (foneetiline eristus)

**Loodud:** 2026-03-21 13:56 (HPC run `20260321-135615`)

## Hypothesis

v4 lahendas Korvo-2 domeeni FPR-i, aga CV FPR jäi kehvaks. Idee: mudel ei õpi fraasi eristust, ta õpib domeeni eristust. Kui me **lisame foneetiliselt sarnaseid aga valesid fraase** (hard negatives), siis mudel peab õppima **täpset fraasi "Kuule Kratt"** mitte ainult "helid mis sarnanevad K-2-ga".

## Erinevused v4-st

| Parameeter | v4 | v5 |
|------------|-----|-----|
| **Positives (reaalne K-2 mic)** | 915 | **915** |
| **Positives (Neurokõne TTS)** | 0 | **+1560** (12 eesti kõnelejaga) |
| Positives kokku (post-split train) | 915 | **2241** |
| CV negatives | 3928 | 3928 |
| K-2 negatives | 1311 | 1311 |
| **TTS hard negatives** | 0 | **+1644** |
| Negatives kokku | 5239 | **6883** |
| Ambient | 1002 | 1002 |
| Arhitektuur + hyperparams | identne | identne |

**Hard negative fraasid** (TTS-genereerinud):
- "Hei Kratt"
- "Tere Kratt"
- "Kratt" (üksikuna)
- "Kratt kuule" (word order reversed)
- jm foneetilised sugulased

Eesmärk: sundida mudelit eristama **täpset fraasi** "Kuule Kratt", mitte ainult "midagi kus on Kratt-sarnane sõna".

## Tulemus (õiglane võrdlus, identsed test setid, cutoff=0.99)

| Mõõdik | v3 | v4 | **v5** | v5 delta |
|--------|-----|-----|--------|----------|
| Recall (mic1) | 98.8% | 100.0% | **99.6%** | −0.4pp |
| Recall (mic2) | 98.0% | 100.0% | **100.0%** | 0 |
| FPR (CV) | 98.0% | 36.8% | **41.6%** | +4.8pp |
| FPR (Korvo-2) | 24.8% | 7.3% | **1.8%** | **−5.5pp** |

## Tõlgendus

**Võit:** Korvo-2 FPR paranes suuresti (7.3 → 1.8). Hard negatives andsid mudelile fraasi-taseme eristuse — "Kuule Kratt" ≠ "Hei Kratt" isegi samas akustilises domeenis.

**Probleem:** CV FPR läks natuke halvemaks (36.8 → 41.6). TTS lisas uue akustilise distributsiooni (sünteetiline kõne, 12 kõnelejat) mida mudel ei oska eristada CV päris-inimeste kõnest. Treeningusse lisatud TTS kõne võib luua uut tüüpi domain gap.

**Kokkuvõte:** Domeenide tasakaal on ikka ebavõrdne. Korvo-2 domeen lahendatud, CV domeen halvem kui v1.

## Järgnev

v6 lisab **3345 rohkem K-2 negatiivi** (teise sessiooni täispikk 2.8h kõnet, 3-sek chunk'idena). Hypothesis: rohkem ja mitmekesisemat K-2 kõnet → mudel ei õpi kitsast K-2 fingerprinti → parem generaliseerimine laiemalt (sh CV).

Vaata ka: `wake-word/docs/MODEL_LINEAGE.md`
