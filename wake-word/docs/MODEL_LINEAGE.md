# Kratt model lineage summary

This file is a public, shortened lineage summary for the models relevant to the
`v0.1.0-alpha` release. The public repository keeps only the information needed to use and understand
the released baseline.

## Released baseline

### `kuule-kratt-v16c`

- **Role:** stable single-model demo/baseline and ESPHome integration artifact.
- **Target phrase:** `Kuule Kratt` / `Kule Kratt`.
- **Format:** INT8 TensorFlow Lite model for ESPHome `micro_wake_word`.
- **Public files:**
  - `wake-word/models/kuule-kratt-v16c/kuule_kratt_v16c.tflite`
  - `wake-word/models/kuule-kratt-v16c/kuule_kratt_v16c.json`
  - `wake-word/models/kuule-kratt-v16c/NOTES.md`
- **Status:** useful for demos and integration testing, but not
  production-proven.

The public ESPHome reference is:

```yaml
micro_wake_word:
  models:
    - model: github://Yikizi/kratt/wake-word/models/kuule-kratt-v16c/kuule_kratt_v16c.json@main
      id: kuule_kratt_model
```

## Why the caveat matters

The thesis experiments showed that a wake-word model should not be judged by a
single headline number. A detector can have good recall on some positive clips
and still fail in deployment because it triggers on ordinary speech, on the
prefix word `kuule`, on the isolated word `Kratt`, or on similar phrases.

For Kratt, the relevant evaluation dimensions are:

1. streaming false accepts per hour (FAPH),
2. recall on real or otherwise unseen speakers,
3. hard-negative, prefix, reversed-order, and confusable-phrase rejection.

No current two-word `Kuule Kratt` model is claimed to satisfy all of those goals
simultaneously. The public `v16c` model is therefore released as a baseline for
experimentation and Home Assistant integration, not as a consumer-ready detector.

## Diagnostic model families not included in this public release

The development history contains many intermediate and diagnostic model families:

- early `v1`-`v15` experiments used to debug data collection and evaluation;
- expert/consensus models that reduced ambient FAPH but hurt recall or phrase
  selectivity;
- `v17`/`v18` experiments that exposed positive-label quality and exact-phrase
  selectivity problems;
- checkpoint-FAPH experiments showing that optimizing one metric can produce a
  model that is quiet but not useful;
- a `Kratt`-only single-word ablation, which uses a different target policy and
  is not a replacement for the two-word wake phrase.

These models are useful research evidence, but they are intentionally not part
of the minimal public Home Assistant package.

## Recommended public wording

Use:

> `v16c` is the current public demo/baseline wake-word model for Kratt.

Do not use:

> Kratt is a production-ready Estonian wake-word detector.
