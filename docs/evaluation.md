# Evaluation summary

Kratt is published as a research prototype, not as a production-grade wake-word
system. The main lesson from the thesis work is that short-clip accuracy is not
enough for wake-word evaluation. A model can work on isolated positive clips and
still trigger too often in continuous speech or on phrase fragments.

## Required metric set

A useful wake-word evaluation must report these dimensions together at a fixed
threshold:

1. **Streaming false accepts per hour (FAPH)** on long negative audio.
2. **Recall** on real or otherwise unseen speakers saying the target phrase.
3. **Hard-negative rejection**, including similar phrases, prefix-only phrases,
   reversed word order, and confusable continuations.

Thresholds should be selected on validation data and then frozen before final
reporting. Threshold sweeps are useful for analysis, but they should not be
presented as final test-set performance unless the operating point was chosen in
advance.

## Current public model status

`v16c` is the public ESPHome baseline included in this repository. It is useful
for demos and integration testing, but it is not production-proven. Later
development experiments showed that no current two-word `Kuule Kratt` model
satisfied all deployment goals at the same time:

- low ambient FAPH,
- high real-speaker recall,
- strong rejection of prefix/confusable phrases.

For that reason, the public package deliberately uses conservative language:
`v16c` is a baseline model and an integration artifact, not a finished consumer
wake word.

## Public release boundary

This public repository includes only consent-safe artifacts:

- source code and configuration,
- the `v16c` TFLite model and ESPHome manifest,
- aggregate model notes and high-level evaluation guidance.

It does not include raw participant audio, private user-test data, local training
runs, or private development history.
