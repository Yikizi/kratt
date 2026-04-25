# v4 — K-2 scale-up (orust välja osaliselt)

**Loodud:** 2026-03-21 12:19 (HPC run `20260321-121959`)

## Hypothesis

Kui v3 langes 2.7% K-2 osakaaluga *valley of degradation*-i, siis skaleerimine **25%-le** (üle Park et al. 10% künnise) peaks orust välja tooma.

## Erinevused v3-st

| Parameeter | v3 | v4 |
|------------|-----|-----|
| Positives | 915 | **identne** |
| CV negatives | 3928 | **identne** |
| **K-2 negatives** | 109 | **1311** (+1202) |
| K-2 osakaal | 2.7% | **25.0%** |
| Ambient | 1002 | **identne** |
| Arhitektuur + hyperparams | mixednet 32+48×4, residual OFF, 10k steps | **identne** |

Lisatud 1202 K-2 negatiivset tulid sessioon 1 **6.2h taustakõnest**, mis Silero VAD-iga segmenteeriti kõnesegmentideks. Kokku sessioon 1 andis 1311 segmenti (= 109 tahtlik + ~1202 ambient-speech).

## Andmestik

- Pos: 915 (silence-trimmed real Korvo-2)
- Neg: 5239 (3928 CV + **1311 K-2**)
- Ambient: 1002 (930 MUSAN + 72 K-2 ambient)

## Tulemus (õiglane võrdlus, identsed test setid, cutoff=0.99)

| Mõõdik | v1 (baseline) | v3 (org) | **v4** | Delta v3→v4 |
|--------|-----|-----|--------|---|
| Recall (mic1) | 92.8% | 98.8% | **100.0%** | +1.2pp |
| Recall (mic2) | 94.8% | 98.0% | **100.0%** | +2.0pp |
| FPR (CV) | 8.0% | 98.0% | **36.8%** | **−61.2pp** |
| FPR (Korvo-2) | 13.8% | 24.8% | **7.3%** | **−17.5pp** |

## Tõlgendus

**Osaline võit:**
- K-2 FPR **parem kui baseline** (7.3% vs v1 13.8%) — sama-seadme skaleerimine töötas
- Recall saturated 100%-ni

**Osaline ebaõnnestumine:**
- CV FPR **endiselt 4.5× halvem kui v1** (36.8% vs 8%) — domeenist väljapoole (Common Voice üldkõne) generaliseerimine on kehv
- Mudel pole päris orust välja — ta on lahendanud **Korvo-2 poole**, jättes CV poole haigena

## Metodoloogiline tõlgendus

Valley of degradation ei olnud üks mono-dimensiooniline org. K-2 skaleerimine ravis K-2 sümptomi aga tekitas teise: mudel õppis tugevalt K-2 akustilist fingerprinti ning CV-domeen jäi alla-eristatavaks. Tegelik lahendus nõuab fraaside **sisulist** eristumist, mitte domeeni-põhist.

## Järgnev

v5 tegeleb sellega: lisab Neurokõne TTS positiivid (1560) ning TTS hard negatives (1644) nagu "Hei Kratt", "Tere Kratt", "Kratt kuule" jm. Idee on et mudel õpiks täpset fraasi *Kuule Kratt* eristama lähisugulastest (semantic/phonetic discrimination, mitte ainult domain discrimination).

Vaata ka: `wake-word/docs/MODEL_LINEAGE.md`
