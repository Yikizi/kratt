# openWakeWord diagnostic models

**Status:** diagnostic only; not active demo/default models.

These ONNX models were trained/copied for the 2026-05-15 openWakeWord framework comparison. They are stored separately from the microWakeWord TFLite models because `kratt demo` currently supports the microWakeWord/ESPHome TFLite path, not OWW ONNX.

Models:

- `oww-v4-50k/kuule_kratt_oww_v4_50k.onnx`
- `oww-v6-50k/kuule_kratt_oww_v6_50k.onnx`
- `oww-v17-official-50k/kuule_kratt_oww_v17_official_50k.onnx`
- `oww-v18d-clean96-cap128-50k/kuule_kratt_oww_v18d_clean96_cap128_50k.onnx`

`50k` means 50,000 training steps.

Interpretation:

- OWW can lower ambient FAPH at strict thresholds.
- The same recall/FAPH/confusable tradeoff remains.
- No OWW model currently replaces `v16c` for the demo/user-test baseline.

Main documentation:

- `docs/research/openwakeword-framework-comparison-2026-05-15.md`
- `docs/research/artifacts/openwakeword-comparison-2026-05-15/`
- `wake-word/evaluation/openwakeword-supervisor-full-20260515/`

Live ONNX test path, if needed:

```bash
cd wake-word
.venv-openwakeword/bin/python evaluation/live_test_openwakeword.py \
  --model models/openwakeword/oww-v18d-clean96-cap128-50k/kuule_kratt_oww_v18d_clean96_cap128_50k.onnx \
  --threshold 0.995
```
