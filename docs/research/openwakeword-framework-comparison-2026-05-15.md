# openWakeWord diagnostic framework comparison (2026-05-15)

**Status:** thesis-facing diagnostic note. Use as evidence that `openWakeWord` was tested as an alternative path, not as proof of a comprehensive framework benchmark.

## Purpose

The April supervisor table compared `microWakeWord` model families on the same held-out benchmark families. Because thesis §4.2 discusses the value of comparing two wake-word frameworks, we ran a matching `openWakeWord` diagnostic pass on the same benchmark families where possible.

Primary question:

> Does `openWakeWord` improve the recall / ambient-FAPH / hard-confusable tradeoff enough to replace the current `microWakeWord` baseline (`v16c`) or historical balanced anchor (`v6-residual`)?

Short answer: **no clear replacement**. `openWakeWord` can reduce ambient FAPH at strict thresholds, but recall becomes uneven or collapses, and phrase/confusable rejection remains poor.

## Artifacts

Local artifacts:

- Raw OWW supervisor-style CSVs: `wake-word/evaluation/openwakeword-supervisor-full-20260515/`
- Earlier OWW HPC benchmark CSVs: `wake-word/evaluation/openwakeword-hpc-20260515/`
- Combined supervisor CSV + HTML including mWW and OWW rows:
  - `docs/research/artifacts/openwakeword-comparison-2026-05-15/benchmark_results_supervisor_plus_openwakeword.csv`
  - `docs/research/artifacts/openwakeword-comparison-2026-05-15/supervisor_table_plus_openwakeword.md`
  - `docs/research/artifacts/openwakeword-comparison-2026-05-15/supervisor_report_plus_openwakeword.html`
- Local ONNX models:
  - `wake-word/models/openwakeword/oww-v4-50k/kuule_kratt_oww_v4_50k.onnx`
  - `wake-word/models/openwakeword/oww-v6-50k/kuule_kratt_oww_v6_50k.onnx`
  - `wake-word/models/openwakeword/oww-v17-official-50k/kuule_kratt_oww_v17_official_50k.onnx`
  - `wake-word/models/openwakeword/oww-v18d-clean96-cap128-50k/kuule_kratt_oww_v18d_clean96_cap128_50k.onnx`

HPC source directory:

- `/gpfs/mariana/smbhome/malinh/kratt-data/training/runs/oww-supervisor-full-20260515/`

## Models tested

| Model | Purpose | Internal OWW result | Thesis interpretation |
|---|---|---:|---|
| `oww-v4-50k` | OWW retrain on older v4-style data | recall 72.8%, internal FP/h 234.1 | High recall only at very high FAPH; diagnostic only. |
| `oww-v6-50k` | OWW retrain around v6-style data | recall 73.3%, internal FP/h 76.1 | Better low-threshold FAPH option, but external recall/confusables fail. |
| `oww-v17-official-50k` | Existing official v17 OWW run | recall 58.7%, internal FP/h 77.9 | Likely affected by v17 positive-data quality incident; diagnostic only. |
| `oww-v18d-clean96-cap128-50k` | Cleaner positive set, larger OWW head (`layer_size=128`) | recall 63.9%, internal FP/h 55.7 | Label cleanup helps FAPH, but recall and phrase selectivity still fail. |

`50k` means **50,000 OWW training steps**, not 50k positive clips.

## Key external operating points

Selected points from the supervisor-style OWW CSVs. Recall/FPR are proportions; FAPH is false accepts per hour.

| Model @ threshold | Isa rec | Mat rec | Ode rec | Friend rec | Confusable FPR | CV FAPH | Libri FAPH | DiPCo FAPH | MacBG FAPH | Interpretation |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `oww-v17-official-50k @0.02` | 0.917 | 0.948 | 0.909 | 0.924 | 0.983 | 79.8 | 32.0 | 60.2 | 61.7 | Recall usable, but FAPH/confusables too high. |
| `oww-v17-official-50k @0.97` | 0.042 | 0.319 | 0.818 | 0.069 | 0.718 | 16.0 | 5.0 | 7.2 | 6.0 | Lower FAPH, but recall collapses. |
| `oww-v18d-clean96-cap128-50k @0.5` | 0.438 | 0.926 | 0.909 | 0.986 | 0.908 | 44.0 | 21.2 | 23.2 | 50.5 | Good real-speaker recall only with high FAPH and bad confusables. |
| `oww-v18d-clean96-cap128-50k @0.995` | 0.021 | 0.741 | 0.909 | 0.745 | 0.747 | 7.33 | 2.31 | 0.90 | 1.71 | Ambient FAPH improves, but unseen-speaker recall is not defensible. |
| `oww-v6-50k @0.99` | 0.312 | 0.741 | 0.909 | 0.628 | 0.718 | 2.09 | 2.31 | 0.30 | 2.57 | Low-ish FAPH, but recall too weak and confusables high. |
| `oww-v4-50k @0.995` | 0.396 | 0.874 | 0.909 | 0.897 | 0.772 | 12.0 | 5.87 | 12.0 | 66.8 | Recall uneven; MacBG and confusables poor. |

Comparison anchors from the April supervisor table at threshold 0.97:

| mWW anchor | Isa rec | Mat rec | Ode rec | Friend rec | CV FAPH | MacBG FAPH | Note |
|---|---:|---:|---:|---:|---:|---:|---|
| `v16c` | 1.000 | 0.904 | 0.909 | 0.883 | 94.0 | 21.4 | Stable demo/baseline candidate; still not exact-phrase selective. |
| `v6-residual` | 1.000 | 0.763 | 0.909 | 0.972 | 23.6 | 5.14 | Historical balanced anchor; still fails hard negatives. |

## Interpretation

The OWW runs do **not** show a clean framework-level win. The same three-way tension remains:

1. **Recall:** acceptable recall appears only at permissive thresholds for some speakers.
2. **Ambient FAPH:** strict thresholds reduce FAPH, but usually collapse recall.
3. **Phrase selectivity:** `kuule/kule` confusables, reversed phrases, and partial/prefix-like phrases still trigger too often.

The most likely root cause is not simply “not enough training steps”. It is a data/objective bottleneck:

- too few **clean, diverse, real-speaker positives** for the exact two-word target;
- `v17` positives were partly contaminated by the known positive-data incident;
- `v18d` is cleaner, but smaller and under strong negative/FAPH pressure;
- binary wake-word training does not sufficiently force the exact phrase structure (`kuule/kule` + `kratt` in order) unless partial/reversed/confusable phrases are first-class negatives or the objective enforces phrase order.

## Thesis wording recommendation

Defensible phrasing:

> openWakeWord was evaluated as a diagnostic alternative to microWakeWord using the same benchmark families. The results did not provide a replacement for the current microWakeWord baseline: although strict OWW thresholds can lower ambient FAPH, this comes with uneven or collapsed recall and poor confusable rejection. The comparison supports the methodological claim that framework changes alone do not remove the data-quality and phrase-selectivity bottleneck.

Avoid wording like:

- “openWakeWord is worse overall” without threshold caveats;
- “the project completed a full framework benchmark”;
- “OWW failed only because the positive dataset was small”.

Better short conclusion:

> The remaining bottleneck is clean/diverse positive data plus phrase-selective hard negatives, not just model capacity or training convergence.

## Caveats

- This is a supervisor-style diagnostic comparison, not a full framework benchmark under identical training recipes.
- The OWW script approximates some provenance subsets: `pos_mattias_short` as `duration_s >= 1.2`, and `pos_friend1_n37` as the first sorted 37 files.
- `neg_kuule_kule_confusables_target_free` currently uses the same file set as `neg_kuule_kule_confusables`; verify before using it as a separate thesis claim.
- `kratt demo` currently supports microWakeWord TFLite only. OWW ONNX live testing uses `wake-word/evaluation/live_test_openwakeword.py` unless a separate backend is implemented.
