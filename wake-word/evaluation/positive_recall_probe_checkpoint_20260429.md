# Positive recall probe — checkpoint models (2026-04-29)

Source CSV: `positive_recall_probe_checkpoint_20260429.csv` (ignored by git).

Important caveat: this is a broad positive-source recall probe, not a clean final held-out table for every model. Some sources are training or near-training sources for some model families (especially Mattias/TTS sources). Cleanest external recall anchors remain `pos_isa_xtts`, `pos_ode_real`, and `pos_friend1_real_145`; `pos_mattias_mac_30` is mainly a cross-device / same-author probe.

## Threshold 0.995

| model | Isa XTTS 48 | Ode real 11 | Mattias Mac 30 | Mattias short 362 | Friend1 real 145 | Strict TTS 709 | Neurokõne p1 758 | Neurokõne p2 948 | Kule/Kuule 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `checkpoint-faph-v18d-clean96-pw96x4` | 4.2% | 0.0% | 63.3% | 60.5% | 0.7% | 86.0% | 52.0% | 78.4% | 100.0% |
| `checkpoint-faph10-v18d-clean96-pw96x4` | 72.9% | 100.0% | 100.0% | 72.7% | 22.1% | 100.0% | 88.0% | 99.9% | 100.0% |
| `v16c` | 100.0% | 90.9% | 100.0% | 89.8% | 87.6% | 100.0% | 52.4% | 100.0% | 100.0% |
| `v18d-clean96` | 91.7% | 100.0% | 100.0% | 100.0% | 97.9% | 100.0% | 99.7% | 100.0% | 100.0% |
| `v18b-clean48-sa` | 89.6% | 90.9% | 100.0% | 99.7% | 92.4% | 100.0% | 100.0% | 100.0% | 100.0% |
| `v6-residual` | 100.0% | 100.0% | 100.0% | 78.5% | 95.2% | 100.0% | 64.2% | 100.0% | 100.0% |
| `expert-a` | 79.2% | 90.9% | 100.0% | 92.3% | 95.9% | 100.0% | 99.9% | 100.0% | 100.0% |

## Threshold 0.97

| model | Isa XTTS 48 | Ode real 11 | Mattias Mac 30 | Mattias short 362 | Friend1 real 145 | Strict TTS 709 | Neurokõne p1 758 | Neurokõne p2 948 | Kule/Kuule 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `checkpoint-faph-v18d-clean96-pw96x4` | 4.2% | 54.5% | 86.7% | 76.2% | 4.8% | 96.6% | 80.3% | 91.0% | 100.0% |
| `checkpoint-faph10-v18d-clean96-pw96x4` | 81.2% | 100.0% | 100.0% | 74.9% | 27.6% | 100.0% | 92.0% | 100.0% | 100.0% |
| `v16c` | 100.0% | 100.0% | 100.0% | 90.3% | 89.0% | 100.0% | 56.6% | 100.0% | 100.0% |
| `v18d-clean96` | 91.7% | 100.0% | 100.0% | 100.0% | 97.9% | 100.0% | 99.9% | 100.0% | 100.0% |
| `v18b-clean48-sa` | 93.8% | 100.0% | 100.0% | 99.7% | 93.8% | 100.0% | 100.0% | 100.0% | 100.0% |
| `v6-residual` | 100.0% | 100.0% | 100.0% | 81.2% | 97.2% | 100.0% | 72.0% | 100.0% | 100.0% |
| `expert-a` | 81.2% | 100.0% | 100.0% | 93.9% | 96.5% | 100.0% | 100.0% | 100.0% | 100.0% |

## Interpretation

- `checkpoint-faph-v18d-clean96-pw96x4` is confirmed to be over-conservative on external voices: it can still fire on Mattias/TTS-like sources, but fails Isa/Ode/Friend1 badly at deployment thresholds.
- `checkpoint-faph10-v18d-clean96-pw96x4` is not universally dead: it gets 100% on Mattias Mac and Ode, and 72.9–81.2% on Isa depending on threshold. However, it fails Friend1 badly (22.1% @0.995; 27.6% @0.97), which is the strongest real-speaker warning.
- Compared with `v16c`, `v6-residual`, `expert-a`, `v18b`, and `v18d`, the faph10 checkpoint has much better ambient FAPH but clearly worse real-speaker generalization.
- This strengthens the earlier conclusion: the checkpoint objective improved ambient false accepts, but not the full wake-word deployment objective.
