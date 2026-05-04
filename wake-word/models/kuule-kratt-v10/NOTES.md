# v10 — residual ON + massive neg scale + MUSAN bug

**Loodud:** 2026-04-10 18:36 (`microwakeword-kuule-kratt-v10-20260410-183655`)

**Metadata:** `analysis/dataset_summary.json`, `analysis/training_config_snapshot.json`, and `training_config.yaml` restored from HPC on 2026-05-03.

## Hypothesis

Scale up kõike: residual ON (v6-residual ablation näitas −37% FAPH), suur ühendatud neg pool (MUSAN + Riigikogu + kõik olemasolevad), 0% eraldi hard neg feature set.

## Andmed

| Parameeter | Väärtus |
|------------|---------|
| Positives | 3343 |
| Negatives | 16782 |
| Hard neg eraldi | **0** (puudub eraldi feature set) |
| Ambient | 1002 |
| **Residual** | **ON** (esimest korda main sequence'is) |
| SpecAugment | ON in restored config (`freq_mask_count: [2]`, `time_mask_count: [2]`) |
| Architecture | mixednet 4×48f |
| Checkpoint objective | accuracy (`target_minimization: 0.0`, `maximization_metric: accuracy`) |

## KRIITLINE BUG: MUSAN non-recursive glob

`prepare_kuule_kratt_experiment.py` kasutas `glob("*.wav")` (non-recursive). MUSAN speech/music kaustad sisaldavad alamkaustasid (`speech/librivox/`, `music/fma/`).

**Tulemus: 0 MUSAN speech/music faili jõudis treeningusse**, kuigi logid väitsid teisiti.

Session-findings: "v10's MUSAN advantage was illusory — it succeeded for other reasons."

v10 tegelik edu tuleneb tõenäoliselt **residual ON** + mined false accepts + large K-2+CV pool, MITTE MUSAN-ist.

## Tulemus

| Mõõdik | Väärtus | Kommentaar |
|--------|---------|------------|
| FAPH CV @0.997 | **15.7** | Väga hea (v8 oli ~141 @0.97) |
| FAPH Mac @0.997 | **4.3** | Väga hea |
| Recall Ode @0.97 | 8/11 (73%) | |
| Recall Isa @0.997 | 56% | Kehv |
| FPR Mac hard neg @0.997 | 53% | Keskmine |
| FRR@1FA/h | **45.3%** | Väga kõrge — pool kasutajaid ei saa teenust |
| Android @0.9 | 13% | |

## Tõlgendus

v10 = **sama trade-off nagu v7**: hea FAPH, halb recall. Residual ON annab konservatiivse mudeli mis triggerib harva (hea FAPH) aga ka ei triggeri real kasutajatele piisavalt (kõrge FRR).

Hard neg ratio 46% pool sees oli liiga kõrge (session-findings §2.3). Hou et al.: optimal 10-20%.

## v10 oluline roll

1. **Mined false accepts** — live testing v10-ga andis canary set (5 klippi: keyboard tapping, muusika patterns) + training set (21 klippi)
2. **Consensus building block** — v10+v15 = 6.8 FAPH, 7/11 recall (esimene multi-model katse)
3. **SpecAugment ablation base** — v13a/v13b kasutavad v10 andmeid SA ON/OFF testimiseks
4. **MUSAN bug discovery** — viis glob fixi (recursive) hilisemate versioonide jaoks

Vaata ka: `wake-word/docs/MODEL_LINEAGE.md`
