# microWakeWord Sanity Check

## Goal

Before training another Estonian wake word, verify that our local
microWakeWord pipeline works end-to-end on a public, reproducible target.

This sanity check uses:

- Dataset: `Speech Commands v0.02`
- Positive class: `marvin`
- Negative class: all other spoken word folders except `_background_noise_`
- Ambient set: `_background_noise_`

If this setup produces a reasonable model and a non-degenerate ROC file, then
the pipeline is likely correct and later failures are more likely to come from
our custom data rather than the infrastructure.

## Core Concepts

### `positive`

Short clips that contain the wake word. In this experiment that means files from
`speech_commands/marvin`.

### `negative`

Short clips that do not contain the wake word. These train the classifier to
distinguish `marvin` from other spoken words.

### `ambient`

Long background recordings that also do not contain the wake word. These are not
mainly for learning the word boundary. They are for estimating how often the
model would trigger by accident in a continuous audio stream.

This distinction matters because a model can look good on short negatives and
still false-trigger on long background audio.

## Step 1: Prepare an Experiment Dataset

Command:

```bash
python3 /Users/mattias/kratt/wake-word/training/scripts/prepare_speech_commands_experiment.py \
  --target-word marvin \
  --output-dir /Users/mattias/kratt/wake-word/data/processed/experiments/speech_commands_marvin \
  --force
```

What this does:

- Creates `positive_samples/` from `marvin`
- Creates `negative_samples/` from the other Speech Commands labels
- Creates `ambient_samples/` from `_background_noise_`
- Writes `manifest.json` so the exact experiment is documented

Expected result:

- About 2100 positive files
- A deterministic negative subset
- 6 ambient background tracks

What failure would mean:

- Missing folders means the Speech Commands dataset is incomplete locally
- A zero-count ambient set means ROC/FAPH evaluation will fall back and become
  untrustworthy

## Step 2: Generate RaggedMmap Features

This happens automatically inside the training script, but conceptually it is a
separate stage.

What this does:

- Converts WAV files into spectrogram feature sequences
- Stores them on disk as RaggedMmap folders
- Creates the split structure expected by microWakeWord:
  - `training`
  - `validation`
  - `testing`
  - `validation_ambient`
  - `testing_ambient`

Why it exists:

- Training reads features faster from disk than repeatedly decoding raw audio
- Ambient sets stay as longer spectrogram tracks, which lets microWakeWord
  simulate streaming false accepts later

Expected result:

- A feature tree under `/Users/mattias/kratt/wake-word/training/features/<experiment>`
- Non-empty `negative/validation_ambient/` and `negative/testing_ambient/`

## Step 3: Train and Export the Model

Command:

```bash
/Users/mattias/kratt/wake-word/training/scripts/train_microwakeword_experiment.sh \
  --experiment-name microwakeword-sanity-marvin \
  --positive-dir /Users/mattias/kratt/wake-word/data/processed/experiments/speech_commands_marvin/positive_samples \
  --negative-dir /Users/mattias/kratt/wake-word/data/processed/experiments/speech_commands_marvin/negative_samples \
  --ambient-dir /Users/mattias/kratt/wake-word/data/processed/experiments/speech_commands_marvin/ambient_samples
```

What this does:

- Builds or reuses mmaps
- Writes an experiment-specific training config
- Trains the non-streaming model
- Exports the quantized streaming TFLite model
- Runs streaming ROC evaluation on the test split
- Generates an analysis report with plots and CSV summaries

Expected result:

- A new run directory under `/Users/mattias/kratt/wake-word/training/runs/`
- A quantized model under `tflite_stream_state_internal_quant/`
- A `tflite_streaming_roc.txt` file with several cutoffs and non-trivial FAPH
  values
- An `analysis/` folder with plots and summary tables

What failure would mean:

- Training crash means the environment or code is still broken
- `Ambient set ... is empty` means the dataset preparation is still wrong
- `AUC 0.00000` together with an empty ambient warning means evaluation is still
  degenerate

## Step 4: Interpret the Outputs

Files to inspect:

- Training config:
  `/Users/mattias/kratt/wake-word/training/configs/microwakeword-sanity-marvin.yaml`
- Run directory:
  `/Users/mattias/kratt/wake-word/training/runs/microwakeword-sanity-marvin-<timestamp>/`
- ROC summary:
  `.../tflite_stream_state_internal_quant/tflite_streaming_roc.txt`
- Analysis outputs:
  - `.../analysis/roc_faph_vs_frr.png`
  - `.../analysis/score_distribution.png`
  - `.../analysis/clip_threshold_metrics.csv`
  - `.../analysis/dataset_summary.json`

What we want to see:

- The model recalls many positive `marvin` samples
- FAPH changes when the cutoff changes
- ROC output contains multiple meaningful thresholds

What we do not conclude from this run:

- It does not prove the same hyperparameters will work for Estonian
- It does not prove far-field microphone data will behave like close-talk
- It only proves the local pipeline can train and evaluate a public target

## Why This Is a Better Next Step Than Jumping Back to `kratt`

- The data source is public and reproducible
- The positive class is clean and already segmented
- The ambient source is already bundled in the same dataset
- If this run works, our next debugging target becomes data quality and domain
  mismatch, not the pipeline itself
