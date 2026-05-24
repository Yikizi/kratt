# New wake-word wizard implementation report

## Summary

Implemented an MVP `kratt new-wake-word` workflow for creating a conservative, auditable starter dataset for a new wake-word phrase. The main command can now continue into local training and benchmarking in one guided flow, producing a playable TFLite model. The one-shot defaults were later tightened after the first `hei maja` run showed a prefix-trigger failure mode: fewer TTS positives, more confusable negatives, separate hard-negative staging, stronger negative loss weight, and SpecAugment by default.

## Files changed

- `cli/commands/kratt-new-wake-word`
  - Adds the CLI wrapper and help metadata.
- `wake-word/data/collection/new_wake_word_wizard.py`
  - Creates output layout, manifest, prompt files, smoke split metadata, config, command plan, README, and reproducibility checklist.
  - Supports `--manifest`, `--phrase`, `--slug`, `--speaker`, `--count`, `--device`, `--check`, `--list-devices`, `--recorder`, fixed-duration recording, `--output`, `--no-docker`, `--no-stt`, `--no-tts`, TTS voice/count controls, `--dry-run`, `--end-to-end`, `--train`, `--benchmark`, `--model`, `--tag`, local training limits, `--negative-class-weight`, `--hard-negative-mode`, `--no-spec-augment`, `--local-smoke-train`, `--hpc-plan`, `--fixture-audio`, and safe timestamped non-overwrite behavior.
  - Dry-run prints the plan and creates no files/directories/media.
  - Docker is checked via Compose config and local ports, but services are not started automatically.
- `wake-word/training/scripts/train_new_wake_word.py`
  - Internal local training implementation used by `kratt new-wake-word --train/--end-to-end`; stages positives/negatives and copies the exported `.tflite` model back to the wizard output. It now keeps `eval-smoke` out of training when split metadata is present, caps TTS positives to a default 3:1 ratio against real training positives, uses `negative_class_weight=20` by default, enables SpecAugment by default, and stages sufficiently many confusable negatives as a separate hard-negative feature set.
- `wake-word/evaluation/benchmark_new_wake_word.py`
  - Internal benchmark implementation used by `kratt new-wake-word --benchmark`; scores eval-smoke or positive-real clips, confusable negatives, and optional streaming FAPH.
- `docs/automation/new-wake-word-wizard-spec-2026-05-16.md`
  - Implementation spec used for the MVP.

## Validation run

```bash
./cli/kratt help new-wake-word
./cli/kratt new-wake-word --phrase "Tere Maja" --count 1 --no-stt --no-tts --dry-run
./cli/kratt new-wake-word --phrase "Tere Maja" --count 0 --no-stt --no-tts --output /tmp/kratt-new-ww-test
python3 -m py_compile wake-word/data/collection/new_wake_word_wizard.py
python3 -m py_compile wake-word/training/scripts/train_new_wake_word.py
python3 -m py_compile wake-word/evaluation/benchmark_new_wake_word.py
./cli/kratt new-wake-word --phrase "Tere Maja" --count 1 --no-stt --no-tts --end-to-end --steps 10,5 --negative-limit 10 --ambient-limit 0 --dry-run
./cli/kratt new-wake-word --manifest output/new-wake-word/tere-maja/manifest.json --train --benchmark --steps 10,5 --negative-limit 10 --ambient-limit 0 --dry-run
docker compose -f docker/kratt-stack.yml config
```

Results: all non-training validation commands passed. The `/tmp/kratt-new-ww-test` command used a timestamped safe alternative because that path already existed.

## Clean-onboarding audit

A clean-ish sandbox audit was added in `docs/automation/new-wake-word-onboarding-audit-2026-05-17.md`. It validated help, missing-`uv` behavior, `--check`, device listing, no-media dry-run, fixture-audio import, and resume training dry-run from a copy without local virtualenvs, `output/`, `external-repos/`, or large data corpora. Fixes from that audit:

- added `kratt new-wake-word --check`;
- exported `UV` from the wrapper for child setup scripts;
- allowed `setup_microwakeword_env.sh` to create Python 3.10--3.12 venvs through `uv` when only newer/system Python is present;
- made onboarding checks aware of sibling main-checkout data when running from `.claude/worktrees/...`.

## Caveats

- Live recording uses a continuous fixed-duration stream by default; if PortAudio is unavailable it can fall back to ffmpeg. Fixed-duration sounddevice capture runs in an isolated child process with a timeout so a CoreAudio/PortAudio hang cannot freeze the full wizard. Use `--fixture-audio` or `--dry-run` for non-interactive checks.
- STT integration is a placeholder/manual-review guardrail in this MVP; it does not yet implement a full Wyoming client.
- TTS audio generation prefers local Wyoming TartuNLP on port 10301 and falls back to the API when reachable. One-shot defaults intentionally keep positive TTS modest (`2` per voice) and generate more confusable TTS (`4` per voice) so the model does not learn prefix-only triggers.
- The wizard generates a smoke workflow and command plan only; it does not start training jobs by default.
- Fresh public checkouts usually lack the broad speech/background negative corpora needed for a good personalized model. The trainer can generate starter non-speech negatives for smoke testing, but useful models should pass a real segmented `--negative-dir`.
- The local training stage may duplicate very tiny positive sets to satisfy microWakeWord split requirements and can overfit badly. False-accept mining is the recommended next iteration feature: train once, mine high-scoring negative windows, then retrain with mined hard negatives.
- The benchmark stage is useful for quick iteration, but its positive score may be non-held-out if the wizard output does not contain an `eval-smoke` split.

## Subagent note

The first implementation attempt was interrupted because the worker ran `ls -R` over the full repository, producing a very large tree walk/output. The implementation was then reviewed and patched manually to keep dry-run and Docker behavior safe.
