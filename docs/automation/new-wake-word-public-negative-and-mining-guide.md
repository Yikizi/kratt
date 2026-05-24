# Public negatives + live mining guide for `kratt new-wake-word`

This is the practical path from a fresh phrase to a useful personalized wake-word model.

## Why the one-shot model is not enough

A fresh public checkout does not contain the private/local negative data used in the `hei toomas` experiment. The first model can be trained, but without broad speech/background negatives it is only a smoke model.

The recommended public workflow is two-stage:

1. **Round 1**: record positives, download public broad negatives, train a starter model.
2. **Round 2**: run the starter model in the target room/device, mine false accepts, retrain with mined false positives as hard negatives.

## Round 1: download public starter negatives

When no local broad-negative corpus is found, the wizard can offer an opt-in public negative pack. You can also force it:

```bash
./cli/kratt new-wake-word \
  --manifest output/new-wake-word/hei-toomas/manifest.json \
  --train --skip-benchmark \
  --download-negatives starter-public \
  --negative-pack-clips 10000 \
  --tag hei-toomas-round1
```

Current profile: `starter-public-v1`.

- Source: LibriSpeech test-clean via OpenSLR direct URL.
- Default output: `output/new-wake-word/<slug>/training/negative-packs/starter-public-v1/`.
- Default size: up to 10,000 clips × 2 s ≈ 5.6 clip-hours.
- Provenance: `MANIFEST.json` in the pack directory.

Caveat: once this source is used for training, it is not a held-out FAPH source for that model.

## Round 2: live false-accept mining

Run the trained model in the target environment:

```bash
./cli/kratt new-wake-word \
  --manifest output/new-wake-word/hei-toomas/manifest.json \
  --mine \
  --model output/new-wake-word/hei-toomas/models/hei-toomas-round1.fp32.tflite \
  --mine-hours 50 \
  --mine-threshold 0.99
```

Mining behavior:

- each detection is saved as `false-positive` by default;
- press `SPACE`/`p` within the label window if the detection was a real wake phrase;
- press `SPACE` when there is no pending detection to save a `missed-positive` from the rolling buffer;
- press `f` to explicitly keep the pending detection as false-positive.

Output layout:

```text
output/new-wake-word/<slug>/mining/<timestamp>/
├── false-positive/
├── true-positive/
├── missed-positive/
└── events.jsonl
```

## Retrain with mined false positives

```bash
./cli/kratt new-wake-word \
  --manifest output/new-wake-word/hei-toomas/manifest.json \
  --train --skip-benchmark \
  --download-negatives starter-public \
  --hard-negative-dir output/new-wake-word/hei-toomas/mining/<timestamp>/false-positive \
  --tag hei-toomas-round2-mined
```

Use `true-positive` and `missed-positive` only after manual review. Do not feed them as negatives.

## What remains outside public bundling

The `hei toomas` experiment also benefited from private/local negatives (Mac/Korvo/live mined clips). These cannot be bundled in the public repository. The public starter pack plus target-environment mining is the replacement path.
