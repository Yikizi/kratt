# New wake-word wizard — implementation spec (2026-05-16)

## Purpose

Add a public-repo workflow that lets a technically competent user create a first diagnostic wake-word model for a new Estonian phrase without rediscovering the mistakes found during Kratt development.

The feature is not a promise that 10 recordings plus TTS produce a production model. It is a guided, auditable starting point that:

- creates the correct directory structure and manifest;
- records a small set of real positives;
- optionally checks recordings with Kiirkirjutaja STT;
- generates TTS positives and phrase-selective negative candidates;
- runs local smoke training when feasible, or prints exact next commands;
- prevents common failure modes: prefix-only positives, untracked data, missing hard negatives, test/train mixing, and unlabelled thresholds.

## User-facing command

Add a CLI command:

```bash
./cli/kratt new-wake-word --phrase "Tere Maja" [options]
```

Proposed aliases are optional; one command is enough for MVP.

### MVP options

```text
--phrase TEXT              Target phrase, required unless interactive.
--slug SLUG                Output slug; default derived from phrase, e.g. tere-maja.
--speaker NAME             Real speaker label; default current OS username or "speaker1".
--count N                  Number of real positive recordings; default 10.
--device ID                Microphone device id passed to recorder.
--check                    Check first-run prerequisites and recommended next steps.
--list-devices             List available recording devices.
--recorder BACKEND         auto|sounddevice|ffmpeg.
--record-seconds N         Continuous fixed-duration capture after START.
--output DIR               Output root; default output/new-wake-word/<slug>.
--no-docker                Do not start/check docker services.
--no-stt                   Skip STT verification.
--no-tts                   Skip TTS generation.
--tts-per-voice N          Positive TTS clips per voice; default 2.
--tts-confusable-per-voice N Confusable TTS clips per voice; default 4.
--dry-run                  Print actions without recording/generating/training.
--train                    Attempt local microWakeWord training after data prep.
--benchmark                Run local benchmark after training or for --model.
--negative-class-weight N  Local false-accept penalty; default 20.
--max-tts-positive-ratio N Max TTS positives per real training positive; default 3.
--hard-negative-mode MODE  auto|mixed|separate confusable staging.
--no-spec-augment          Disable default SpecAugment.
--hpc-plan                 Print kratt train/HPC-style follow-up commands.
```

Non-goal for MVP: fully general production training on arbitrary phrase with guaranteed quality.

Clean-onboarding audit: `docs/automation/new-wake-word-onboarding-audit-2026-05-17.md` records a sandbox check from a copy without local virtualenvs, output artifacts, external repos, or large data corpora. The main remaining onboarding gap is data availability: a fresh checkout can smoke-test with generated starter negatives, but useful models require a real segmented broad-negative pack.

## Output layout

For phrase `Tere Maja` and slug `tere-maja`:

```text
output/new-wake-word/tere-maja/
├── README.md
├── manifest.json
├── texts/
│   ├── target.txt
│   ├── positive-prompts.txt
│   ├── confusable-negatives.txt
│   └── stt-review.jsonl
├── audio/
│   ├── positive-real/
│   ├── positive-tts/
│   ├── negative-confusable-tts/
│   └── eval-smoke/
├── training/
│   ├── config.yaml              # generated smoke config or command notes
│   └── commands.sh              # exact next commands
└── reports/
    ├── data-summary.json
    └── reproducibility-checklist.md
```

The generated `README.md` must state clearly:

- this is a diagnostic starter dataset;
- real deployment quality requires more speakers and held-out evaluation;
- user-test/eval audio must not be mixed into training unless explicitly separated;
- FAPH, real-speaker recall, and prefix/confusable FPR must be reported together.

## Docker services

Use existing Docker Compose support instead of inventing a new service stack.

Existing file:

```bash
docker compose -f docker/kratt-stack.yml --profile stt --profile neurokone up -d
```

Important caveat: the current Neurokõne container is a Wyoming wrapper around the Tartu Neurokõne API, not a fully offline local TTS model. The wizard should say this in logs and README. Kiirkirjutaja STT is local once model files are downloaded.

MVP should:

1. check whether Docker is available;
2. if not `--no-docker`, start/check profiles `stt` and `neurokone`;
3. continue gracefully if services are unavailable, offering `--no-stt` / `--no-tts` paths;
4. avoid hard failure after audio recording if TTS/STT is unavailable.

## Recording flow

The wizard should record `--count` target phrase clips from the microphone. Reuse existing recording utilities where practical, but do not force output into the historical `wake-word/data/raw/<name>/positive` tree; this workflow should be self-contained under `output/new-wake-word/<slug>/`.

Minimum acceptable recording UX:

```text
Target phrase: "Tere Maja"
Recording 1/10. Press ENTER, say phrase once, press ENTER to stop...
Saved audio/positive-real/speaker1_0001.wav
```

If reusing existing `record_session.py` is too tightly coupled to `Kuule Kratt`, implement a small wrapper script using `sounddevice`/`soundfile` or Python stdlib-compatible WAV writing, depending on current project dependencies.

Recording validation:

- WAV exists;
- mono 16 kHz preferred; convert/resample if helper exists, otherwise document actual format;
- duration roughly between 0.4 s and 4.0 s by default;
- RMS not near silence;
- manifest row created for each clip.

## STT verification

The STT check is a guardrail, not a hard source of truth.

MVP behavior:

- if Kiirkirjutaja service is reachable, transcribe each real positive;
- print target phrase and transcript;
- ask user to accept/reject or mark uncertain;
- rejected clips stay in output but are excluded from the generated training positive list;
- write `texts/stt-review.jsonl` with clip path, transcript, decision, timestamp.

If direct Wyoming client code is not already available, provide a minimal placeholder interface that can be swapped in, and implement manual review fallback.

## TTS generation

MVP should support two levels:

1. generate text prompts always;
2. generate audio only if a working Neurokõne/Wyoming path or existing script path is available.

Prompt files:

`positive-prompts.txt` should include exact target variants only, for example:

```text
Tere Maja
tere maja
Tere, Maja
```

But the training manifest must label only clean full-phrase audio as positive.

`confusable-negatives.txt` should include:

- first word only;
- last word only;
- reversed order;
- common wake prefixes with the noun/name if applicable (`kuule`, `tere`, `hei`);
- near phrases produced by simple deterministic templates.

For `Tere Maja`, examples:

```text
Tere
Maja
Maja tere
Tere Maria
Tere majja
Tere majra
Tere Maja palun
Hei Maja
Kuule Maja
```

The first generated confusables should prioritize prefix-only and near-full-phrase traps, because the one-shot failure mode is often learning the first word rather than the full phrase.

Do not generate semantically unrelated large negative corpora in MVP. Point users to existing negative corpus preparation docs/scripts.

## Training integration

MVP should not promise successful full local training on every machine. It should provide:

- a smoke data summary;
- a generated `commands.sh` with next steps;
- optional `--local-smoke-train` path if microWakeWord env is available;
- optional `--hpc-plan` instructions.

One-shot local training defaults should be conservative against false accepts:

- keep TTS positives modest so they do not swamp real microphone positives, including a default TTS-positive cap relative to real training positives;
- generate more confusable negatives than positive TTS per voice;
- keep `eval-smoke` out of training when split metadata exists;
- use stronger negative loss weight (`negative_class_weight` around 20, not 5);
- enable SpecAugment by default;
- stage confusables as a separate hard-negative set when enough clips exist.

The command script should include references to existing project commands/scripts, such as:

```bash
# setup
(cd wake-word && uv sync)
./wake-word/training/scripts/setup_microwakeword_env.sh

# feature generation / training notes
# Use generated positive-real, positive-tts, negative-confusable-tts directories.
# Add broad negative speech/background corpora before making any quality claim.
```

If existing `train_microwakeword_experiment.sh` is too `Kuule Kratt`-specific, the MVP can stop at a validated dataset + generated command plan and clearly mark local training as future enhancement. However, implement as much smoke training as feasible without destabilizing current thesis code.

## Guardrails from Kratt development

The wizard must encode these lessons:

1. **No hidden positives**: every accepted positive clip must appear in manifest.
2. **Exact phrase only**: prefix-only, suffix-only, reversed-order, and full-command tails are not positives.
3. **Held-out split exists from day one**: at least mark eval-smoke separately; never mix user-test/eval clips into training silently.
4. **Confusables are first-class negatives**: generate them even for a starter model.
5. **FAPH is required for claims**: generated README must say clip accuracy alone is insufficient.
6. **TTS is not enough**: TTS positives are augmentation/prototyping material, not a substitute for diverse real speakers.
7. **No deletion/regeneration of data dirs**: create timestamped/slugged output directories; refuse overwrite unless `--force` is implemented explicitly.

## Implementation files

Preferred additions:

```text
cli/commands/kratt-new-wake-word
wake-word/data/collection/new_wake_word_wizard.py
```

Optional if needed:

```text
wake-word/data/collection/new_wake_word_templates.py
wake-word/data/collection/wyoming_client.py
```

Follow repo convention: CLI wrapper in `cli/commands/`, Python in snake_case.

## Acceptance criteria

A reviewer should be able to run:

```bash
./cli/kratt new-wake-word --phrase "Tere Maja" --count 1 --no-stt --no-tts --dry-run
./cli/kratt new-wake-word --phrase "Tere Maja" --count 1 --no-stt --no-tts
```

and see:

- output directory created;
- manifest and README created;
- target and confusable prompt files created;
- no overwrite of existing output without clear refusal or timestamped alternative;
- `kratt help new-wake-word` shows useful usage;
- no thesis files modified by implementation unless explicitly needed;
- no long training job started by default.

If audio recording cannot be run in CI/headless mode, provide a `--dry-run` and/or `--fixture-audio DIR` path for validation.

## Validation commands

Minimum validation after implementation:

```bash
./cli/kratt help new-wake-word
./cli/kratt new-wake-word --phrase "Tere Maja" --count 1 --no-stt --no-tts --dry-run
./cli/kratt new-wake-word --phrase "Tere Maja" --count 0 --no-stt --no-tts --output /tmp/kratt-new-ww-test
python3 -m py_compile wake-word/data/collection/new_wake_word_wizard.py
```

If the implementation includes service checks:

```bash
docker compose -f docker/kratt-stack.yml config
```

## Thesis-facing statement enabled by this feature

After this MVP exists, the thesis can safely state:

> The public repository does not make a new wake word a one-command production model. It does, however, provide a guided workflow for creating a new phrase dataset, recording real positives, generating phrase-selective negative prompts, tracking provenance in a manifest, and producing reproducible training/evaluation next steps. Thus the reusable contribution is procedural and auditable: it reduces the chance that a new user repeats the same data-leakage, prefix-positive, and missing-confusable mistakes found during Kratt development.
