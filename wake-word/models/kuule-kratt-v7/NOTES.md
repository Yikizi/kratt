# v7 — parim FAPH, katastroofiline recall trade-off

**Loodud:** 2026-03-24 16:39 (HPC run `20260324-163905`)

## Hypothesis

Laiendatud hard neg set (SSML prosodic variants + foneetilised sugulased) **pluss** SpecAugment regulariseerimine peaks langetama FAPH-i edasi, säilitades recall'i.

## Erinevused v6-st (3 muutust korraga — diagnostikaline viga)

| Parameeter | v6 | v7 |
|------------|-----|-----|
| Positives | 2241 | **3067** (+826 SSML TTS variants) |
| CV neg | 3928 | identne |
| K-2 neg | 4656 | identne |
| **TTS hard neg** | 1644 | **7734** (+6090 v2 SSML variants) |
| Neg kokku | 10228 | **16227** (+59%) |
| **SpecAugment freq** | OFF (0, 0) | **ON (count=2, size=3)** |
| **SpecAugment time** | OFF (0, 0) | **ON (count=2, size=10)** |
| Arhitektuur | mixednet 32+48×4 | identne |
| Residual | OFF | OFF |

## Tulemus (hold-out, cutoff=0.97)

| Mõõdik | v6 | **v7** | Delta |
|--------|-----|--------|-------|
| **FAPH CV ET (3.82h)** | 154 | **96** | **−38%** ⭐ parim v1-v8 seas |
| Recall Mac unseen device | 100% | 100% | säilis |
| **Recall Isa XTTS unseen speaker** | 100% | **43.8%** | **−56pp** ⚠ katastroof |
| FPR Isa XTTS hard neg | 63.3% | **25%** | −38pp ⭐ parim |
| FPR Mac hard neg real | 100% | 80% | −20pp |

## Tõlgendus

**Võidud:**
- **Parim FAPH (96)** kogu v1-v8 seeriast — hard neg set + SpecAugment tõesti langetavad false accept rate'i
- **Parim Isa XTTS hard neg FPR (25%)** — mudel õpib foneetilist eristust hoolsalt
- Mac unseen device recall säilis — sinu treeningukomplekti-sarnastel häältel töötab

**Kaotused:**
- **Unseen speaker recall kukkus 100 → 43.8%** — pooled uued hääled ei triggeri enam. See on **deployment-blocker** — päris assistent peab töötama kõigile, mitte ainult treenitud speakeritele.
- Mudel on liiga konservatiivne uutel helidel

## Diagnoos: "kolm muutust korraga" probleem

v7 muutis:
1. Hard neg setti (+59%)
2. Positives set (SSML variants)
3. SpecAugment (ON esimest korda)

**Ei saa teada millist efekti põhjustas mis muutus.** Kas recall'i kukkumine tuleb SpecAugment'ist, hard neg laienemisest, või kombineerimisest?

See oli **methodological learning** mis viis hiljem v6-residual, v6-specaug ablatsioon-eksperimentideni (2026-04-12) — **üks muutus korraga**.

## v7 production staatus

**Mitte-deployable assistendi jaoks:**
- Unseen speaker recall 43.8% = pool kasutajaid ei saa teenust kasutada
- Assistent peab töötama **kõigile**, mitte ainult sulle

**Kasulik:**
- Kui kasutaja hääl on treeningus (nt sinu Mac) — töötab hästi
- Hard neg diskrimineerimise parim referentspunkt
- Thesis'is näide kuidas "parim FAPH" pole võrdne "parim mudel"

## Metodoloogiline õppetund

**Mitme muutuse korraga testimine = invalid ablation.** v7 on ühine eksperiment kus me ei tea mis mida teeb. Edaspidised eksperimendid (alates v8, eriti v6-residual/specaug) lähtuvad põhimõttest "üks muutus korraga".

## Järgnev

v8 proovib radikaalset lähenemist: **dropsi kõik TTS hard neg, kasuta päris salvestusi + voice clones'e**:
- +300 augmented Mac Mattias hard neg
- +180 XTTS family (3 speakerit × 60) hard neg
- Eraldi `hard_negative` feature set penalty_weight=3.0

Hypothesis: sünteetiline hard neg õpetab sünteetilist eristust, päris hard neg õpetab päris eristust.

Vaata ka: `wake-word/docs/MODEL_LINEAGE.md`, `docs/research/session-findings-apr-2026.md`
