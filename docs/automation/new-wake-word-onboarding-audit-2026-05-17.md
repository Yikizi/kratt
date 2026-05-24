# `kratt new-wake-word` onboarding audit — 2026-05-17

Purpose: validate the new wake-word workflow from a fresh-developer / fresh-checkout perspective, not only from Mattias's prepared research machine.

## Scope

Audited command:

```bash
./cli/kratt new-wake-word
```

The audit focused on:

- dependency bootstrap;
- first-run clarity;
- recording-device discovery;
- data-preparation flow;
- training prerequisites;
- quality caveats for reaching a model comparable to the `hei toomas` personalized demo.

This was first checked in a clean-ish local sandbox copied from the active worktree to `/tmp/kratt-clean-onboard/repo`, excluding local virtualenvs, `output/`, `external-repos/`, and large `wake-word/data/raw|processed` corpora. A second validation was then run over SSH on `mattiass-macbook-air` using `/Users/mattias/kratt-onboarding-clean-20260517` with an isolated `HOME` under that directory.

## Checks run

### 1. Command-specific help

```bash
./cli/kratt help new-wake-word
```

Result: pass. The command is discoverable from the root CLI and lists the main one-shot, resume, training, benchmark, fixture, and FAPH options.

### 2. Missing `uv` behavior

```bash
PATH=/bin:/usr/bin \
HOME=/tmp/kratt-clean-onboard/no-uv-home \
KRATT_NO_UV_INSTALL=1 \
./cli/kratt new-wake-word --check
```

Result: pass. The command fails early with a clear message:

```text
Could not install/find uv. Set UV=/path/to/uv or install uv manually.
```

Normal mode installs `uv` automatically if `curl` is available.

### 3. Onboarding check

```bash
HOME=/tmp/kratt-clean-onboard/home ./cli/kratt new-wake-word --check
```

Result: pass. The check reports:

- core tools (`uv`, `git`, `curl`, `docker`, `ffmpeg`);
- Python runtime dependencies loaded by the wrapper;
- recorder/playback availability;
- optional local STT/TTS service ports;
- local training/evaluation data availability;
- microWakeWord environment/source status;
- free disk;
- recommended first commands.

In a fresh checkout without corpora it correctly warns that broad speech/background negatives are missing and that generated starter negatives are only for smoke testing.

### 4. Device listing

```bash
HOME=/tmp/kratt-clean-onboard/home ./cli/kratt new-wake-word --list-devices
```

Result: pass. It lists both sounddevice/PortAudio and ffmpeg/AVFoundation devices on macOS.

### 5. No-media dry-run

```bash
HOME=/tmp/kratt-clean-onboard/home ./cli/kratt new-wake-word \
  --phrase "test maja" \
  --count 0 \
  --no-docker --no-stt --no-tts \
  --dry-run \
  --output /tmp/kratt-clean-onboard/out/test-maja
```

Result: pass. It prints the planned layout, positive prompts, and confusable prompts without creating files or starting services.

### 6. Fixture-audio data preparation

Synthetic 16 kHz WAV fixtures were generated and imported with:

```bash
HOME=/tmp/kratt-clean-onboard/home ./cli/kratt new-wake-word \
  --phrase "test maja" \
  --count 3 \
  --fixture-audio /tmp/kratt-clean-onboard/fixtures \
  --no-docker --no-stt --no-tts \
  --output /tmp/kratt-clean-onboard/out/fixture-test
```

Result: pass. The wizard created an output directory and manifest, accepted 3/3 fixtures, and reserved 1 eval-smoke clip.

### 7. Resume dry-run for training

```bash
HOME=/tmp/kratt-clean-onboard/home ./cli/kratt new-wake-word \
  --manifest /tmp/kratt-clean-onboard/out/fixture-test/manifest.json \
  --train --skip-benchmark --dry-run \
  --tag clean-dry-train \
  --negative-limit 20 \
  --ambient-limit 0 \
  --steps 10,5
```

Result: pass. Resume mode reports the planned local training without creating a microWakeWord environment or training run.

## SSH validation on `mattiass-macbook-air`

The Air was useful because it was closer to a fresh developer machine:

- `git` and `curl` existed;
- `uv`, `ffmpeg`, and `docker` were not on the default PATH;
- local STT/TTS ports were closed;
- no broad negative corpora existed in the sandbox checkout.

Commands exercised:

```bash
ssh mattiass-macbook-air 'cd /Users/mattias/kratt-onboarding-clean-20260517 && \
  PATH=/bin:/usr/bin HOME=$PWD/home ./cli/kratt new-wake-word --check'

ssh mattiass-macbook-air 'cd /Users/mattias/kratt-onboarding-clean-20260517 && \
  PATH=/bin:/usr/bin HOME=$PWD/home ./cli/kratt new-wake-word --list-devices'

ssh mattiass-macbook-air 'cd /Users/mattias/kratt-onboarding-clean-20260517 && \
  PATH=/bin:/usr/bin HOME=$PWD/home ./cli/kratt new-wake-word \
    --phrase "test maja" --count 5 --fixture-audio fixtures \
    --no-docker --no-stt --no-tts --output output/new-wake-word/test-maja-clean --force'

ssh mattiass-macbook-air 'cd /Users/mattias/kratt-onboarding-clean-20260517 && \
  PATH=/bin:/usr/bin HOME=$PWD/home ./cli/kratt new-wake-word \
    --manifest output/new-wake-word/test-maja-clean/manifest.json \
    --train --skip-benchmark --tag clean-smoke5 \
    --steps 10,5 --negative-limit 20 --ambient-limit 0'
```

Results:

- `uv` auto-installed into the isolated temp HOME.
- `uv` downloaded a managed Python.
- `--check` correctly warned about missing `docker`, `ffmpeg`, local STT/TTS, broad negatives, ambient data, and FAPH data.
- `--list-devices` found the MacBook Air microphone through sounddevice/PortAudio even over SSH.
- A direct 0.7 s hidden sounddevice recording smoke test over SSH produced a valid 16 kHz mono WAV. This means SSH can technically launch local-mic capture on that Mac, but real enrollment still requires the speaker to be physically near that machine and macOS microphone permissions may vary by host.
- Fixture data preparation succeeded.
- A tiny local training smoke run succeeded and exported both:
  - `clean-smoke5.tflite`
  - `clean-smoke5.fp32.tflite`
- A benchmark smoke run succeeded. It skipped FAPH with a clear note because the fresh sandbox had no FAPH directory.

Heavy temporary runtime artifacts were removed from the Air after the test (`.venv-microwakeword`, feature cache, uv cache), leaving only the sandbox, reports, and small model outputs.

## Fixes made during audit

1. Added `--check` to `kratt new-wake-word`.
2. Exported `UV` from the CLI wrapper so child setup scripts can find the same `uv` binary.
3. Hardened `setup_microwakeword_env.sh`: if `python3.10` or `python3.11` is not on PATH but `uv` is available, it creates `.venv-microwakeword` with `uv venv --python '3.10'`.
4. Forced `CC=clang CXX=clang++` for `pymicro-features` on macOS so the fork strips the C++ standard flag from C source compilation.
5. Added compatibility patches for fresh upstream `microWakeWord` clones, including the `process_samples`/`ProcessSamples` API difference and empty-spectrogram handling.
6. Moved generated starter negatives outside the per-run work directory so a fresh no-corpus training run does not create the work dir before the overwrite guard.
7. `--check` now recognizes sibling main-checkout data/source paths when running from a `.claude/worktrees/...` worktree.

## Main UX finding

The first-run software bootstrap is now reasonably smooth: a user can run help, checks, device listing, dry-run, and fixture import without a pre-existing project venv.

The main remaining gap is **data onboarding**, not Python onboarding. A fresh public checkout does not contain the broad negative corpora needed for results like `hei toomas`. Without a real speech/background negative pack, the trainer falls back to generated non-speech starter negatives; this is useful for smoke testing but should not be presented as a quality path.

## What a new user still needs to reach a useful personalized model

Minimum practical path:

```bash
./cli/kratt new-wake-word --check
./cli/kratt new-wake-word --list-devices
./cli/kratt new-wake-word --phrase "Hei Toomas" --count 10 --no-stt --no-tts
./cli/kratt new-wake-word \
  --manifest output/new-wake-word/hei-toomas/manifest.json \
  --train --skip-benchmark \
  --negative-dir /path/to/segmented-negative-wavs \
  --negative-limit 10000
```

To match the current `hei toomas` demo quality, the user needs:

- roughly 10 clean real positive recordings from the target speaker;
- confusable negatives from TTS or real recordings;
- thousands of 1–2 second broad negative speech/background clips;
- enough free disk for microWakeWord features and TensorFlow dependencies;
- a benchmark set that was not used as training negatives.

## Remaining backlog

- Add a documented public negative-pack preparation helper instead of expecting users to know how to create segmented negatives.
- Add a guided false-accept mining pass.
- Add an explicit disjointness/leakage report to benchmark output.
- Add a minimal CI/smoke script that runs `--check`, `--dry-run`, fixture import, and training dry-run in a temp HOME.
- Consider a one-page `docs/automation/new-wake-word-quickstart.md` for users who are not familiar with the thesis repository.
