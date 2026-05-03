# OHEM mining: v16c on held-out CV ET

Generated: 2026-04-25

Command:

```bash
cd wake-word
.venv-microwakeword/bin/python evaluation/ohem_mine_false_triggers.py \
  --model models/kuule-kratt-v16c/kuule_kratt_v16c.tflite \
  --clips data/processed/faph_test_cv_et \
  --top 50 \
  --out-csv ../docs/research/artifacts/wake-word-evaluation-2026-04/ohem_v16c_cv_et.csv

.venv-microwakeword/bin/python evaluation/ohem_mine_false_triggers.py \
  --model models/kuule-kratt-v16c/kuule_kratt_v16c.tflite \
  --clips data/processed/faph_test_cv_et \
  --top 10000 \
  --threshold 0.97 \
  --out-csv ../docs/research/artifacts/wake-word-evaluation-2026-04/ohem_v16c_cv_et_threshold097.csv \
  --copy-to data/mined/ohem_v16c_all_097
```

Input set:

- `wake-word/data/processed/faph_test_cv_et`
- 2000 held-out Common Voice Estonian WAV clips

Outputs:

- Full ranking: `docs/research/artifacts/wake-word-evaluation-2026-04/ohem_v16c_cv_et.csv`
- Thresholded ranking: `docs/research/artifacts/wake-word-evaluation-2026-04/ohem_v16c_cv_et_threshold097.csv`
- Copied clips above 0.97: `wake-word/data/mined/ohem_v16c_all_097/` (578 WAVs, data artifact)
- Copied top 50: `wake-word/data/mined/ohem_v16c_top50/` (data artifact)

## Score distribution

Clip-level max-score mining, not canonical streaming FAPH:

| Threshold | Count / 2000 |
|---:|---:|
| >= 0.50 | 830 |
| >= 0.90 | 664 |
| >= 0.97 | 578 |
| >= 0.99 | 578 |
| >= 0.997 | 498 |
| == 1.0 | 498 |

## Comparison to earlier expert-a OHEM run

Earlier artifact:

- `docs/research/artifacts/wake-word-evaluation-2026-04/ohem_expert_a_cv_et.csv`

At clip-level max score >= 0.97:

| Model | Count >= 0.97 |
|---|---:|
| expert-a | 449 |
| v16c | 578 |

Overlap at >= 0.97:

| Set | Count |
|---|---:|
| both expert-a and v16c | 263 |
| v16c only | 315 |
| expert-a only | 186 |

## Interpretation notes

- This script ranks clips by max frame/window confidence; it is useful for hard-example mining and listening, but it is not the same as canonical continuous-stream FAPH.
- v16c has more high-confidence CV ET clip-level triggers than expert-a in this held-out set, consistent with v16c's weaker CV benchmark FAPH.
- The `v16c only` subset is likely the most useful next listening/mining set for diagnosing what v16c specifically over-triggers on.
- Impulsive non-speech sounds such as hammering/nail impacts are not represented by CV ET; those need a separate real-device negative capture category.
