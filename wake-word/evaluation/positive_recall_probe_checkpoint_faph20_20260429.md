# Positive recall probe — checkpoint-faph20 (2026-04-29)

Source CSV: `positive_recall_probe_checkpoint_faph20_20260429.csv`.

Important caveat: broad positive-source recall probe, not a clean final held-out table for every source. Cleanest external recall anchors remain Isa XTTS, Ode real, and Friend1 real; Mattias/TTS sources may overlap training/domain for some model families.

## Threshold 0.995

| model | Isa XTTS 48 | Ode real 11 | Mattias Mac 30 | Mattias short 362 | Friend1 real 145 | Strict TTS 709 | Neurokõne p1 758 | Neurokõne p2 948 | Kule/Kuule 8 |
|---|---|---|---|---|---|---|---|---|---|
| `checkpoint-faph-v18d-clean96-pw96x4` | 4.2% | 0.0% | 63.3% | 60.5% | 0.7% | 86.0% | 52.0% | 78.4% | 100.0% |
| `checkpoint-faph10-v18d-clean96-pw96x4` | 72.9% | 100.0% | 100.0% | 72.7% | 22.1% | 100.0% | 88.0% | 99.9% | 100.0% |
| `checkpoint-faph20-v18d-clean96-pw96x4` | 72.9% | 90.9% | 100.0% | 81.5% | 42.1% | 100.0% | 93.3% | 100.0% | 100.0% |
| `v16c` | 100.0% | 90.9% | 100.0% | 89.8% | 87.6% | 100.0% | 52.4% | 100.0% | 100.0% |
| `v18d-clean96` | 91.7% | 100.0% | 100.0% | 100.0% | 97.9% | 100.0% | 99.7% | 100.0% | 100.0% |
| `v18b-clean48-sa` | 89.6% | 90.9% | 100.0% | 99.7% | 92.4% | 100.0% | 100.0% | 100.0% | 100.0% |
| `v6-residual` | 100.0% | 100.0% | 100.0% | 78.5% | 95.2% | 100.0% | 64.2% | 100.0% | 100.0% |
| `expert-a` | 79.2% | 90.9% | 100.0% | 92.3% | 95.9% | 100.0% | 99.9% | 100.0% | 100.0% |
| `expert-b2` | 20.8% | 63.6% | 100.0% | 76.2% | 15.2% | 100.0% | 46.3% | 100.0% | 100.0% |
| `v15` | 66.7% | 54.5% | 100.0% | 72.1% | 37.9% | 100.0% | 81.8% | 100.0% | 100.0% |

## Threshold 0.97

| model | Isa XTTS 48 | Ode real 11 | Mattias Mac 30 | Mattias short 362 | Friend1 real 145 | Strict TTS 709 | Neurokõne p1 758 | Neurokõne p2 948 | Kule/Kuule 8 |
|---|---|---|---|---|---|---|---|---|---|
| `checkpoint-faph-v18d-clean96-pw96x4` | 4.2% | 54.5% | 86.7% | 76.2% | 4.8% | 96.6% | 80.3% | 91.0% | 100.0% |
| `checkpoint-faph10-v18d-clean96-pw96x4` | 81.2% | 100.0% | 100.0% | 74.9% | 27.6% | 100.0% | 92.0% | 100.0% | 100.0% |
| `checkpoint-faph20-v18d-clean96-pw96x4` | 75.0% | 90.9% | 100.0% | 85.1% | 50.3% | 100.0% | 94.5% | 100.0% | 100.0% |
| `v16c` | 100.0% | 100.0% | 100.0% | 90.3% | 89.0% | 100.0% | 56.6% | 100.0% | 100.0% |
| `v18d-clean96` | 91.7% | 100.0% | 100.0% | 100.0% | 97.9% | 100.0% | 99.9% | 100.0% | 100.0% |
| `v18b-clean48-sa` | 93.8% | 100.0% | 100.0% | 99.7% | 93.8% | 100.0% | 100.0% | 100.0% | 100.0% |
| `v6-residual` | 100.0% | 100.0% | 100.0% | 81.2% | 97.2% | 100.0% | 72.0% | 100.0% | 100.0% |
| `expert-a` | 81.2% | 100.0% | 100.0% | 93.9% | 96.6% | 100.0% | 100.0% | 100.0% | 100.0% |
| `expert-b2` | 29.2% | 81.8% | 100.0% | 82.0% | 24.1% | 100.0% | 67.5% | 100.0% | 100.0% |
| `v15` | 75.0% | 54.5% | 100.0% | 74.9% | 53.1% | 100.0% | 90.0% | 100.0% | 100.0% |
