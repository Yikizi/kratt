# Kratt public repository plan

Status: draft, 2026-05-12.

## Recommendation

Use a **clean public repository with no private history** as the public face of the project.

Licensing decision: **Apache License 2.0** for Kratt-owned code/config/docs/model artifacts, with third-party components preserved under their own licenses and Kratt branding reserved via `TRADEMARK.md`.

Preferred public URL:

```text
https://github.com/Yikizi/kratt
```

If the existing `Yikizi/kratt` GitHub repository already contains private monorepo history that should not become public, create a temporary clean repository instead:

```text
https://github.com/Yikizi/kratt-public
```

and later rename it to `kratt` after the private/backup repo is moved or deleted.

Do **not** flip the current development monorepo public as-is.

## Public positioning

Public tagline:

> Kratt is a research prototype for Estonian Home Assistant voice control: a `Kuule Kratt` ESPHome wake-word model plus modular Estonian STT/TTS add-ons.

Required caveat:

> The v16c wake-word model is a demo/baseline model, not a production-proven detector. Later experiments showed unresolved prefix/confusable phrase-selectivity risks.

## Repository roles

### Private development monorepo

Keep this repository/private remote for:

- thesis drafts and automation;
- raw/processed audio and user-test outputs;
- local secrets and device-specific notes;
- experiments, dead ends, agent scratch, and HPC-specific tooling.

### Public repository

The public repo should contain only:

- Home Assistant add-on repository metadata;
- Kiirkirjutaja STT add-on;
- Neurokõne TTS add-on;
- ESPHome Kratt v16c model manifest and model artifact;
- portable ESPHome examples;
- Docker Compose stack;
- public user guide and validation notes;
- curated model/evaluation documentation;
- license, privacy, and status disclaimers.

## Proposed public tree

```text
kratt/
├── README.md
├── LICENSE          # Apache-2.0
├── NOTICE
├── TRADEMARK.md
├── SECURITY.md
├── PRIVACY.md
├── repository.yaml
│
├── kratt-kiirkirjutaja-stt/
│   ├── config.yaml
│   ├── build.yaml
│   ├── Dockerfile
│   ├── run.sh
│   ├── main.py
│   ├── asr.py
│   ├── wyoming_handler.py
│   ├── requirements.txt
│   ├── README.md
│   ├── DOCS.md
│   ├── CHANGELOG.md
│   └── LICENSE
│
├── kratt-neurokone-tts/
│   ├── config.yaml
│   ├── build.yaml
│   ├── Dockerfile
│   ├── run.sh
│   ├── wyoming_neurokone.py
│   ├── requirements.txt
│   ├── README.md
│   ├── DOCS.md
│   └── CHANGELOG.md
│
├── wake-word/
│   ├── models/kuule-kratt-v16c/
│   │   ├── kuule_kratt_v16c.tflite
│   │   ├── kuule_kratt_v16c.json
│   │   └── NOTES.md
│   └── docs/MODEL_LINEAGE.md
│
├── hardware/esp32/esphome/
│   ├── README.md
│   ├── secrets.yaml.example
│   ├── models/kratt.example.json
│   ├── voice-satellite-esp32-s3-korvo2.yaml
│   ├── voice-satellite-esp32-s3-korvo2-demo.yaml
│   └── voice-satellite-esp32-s3.yaml
│
├── home-assistant/
│   ├── README.md
│   └── VALIDATION.md
│
├── docker/
│   └── kratt-stack.yml
│
└── docs/
    ├── user-guide/home-assistant-quickstart.md
    └── research/
        ├── source-of-truth-apr-2026.md
        └── wake-word-evaluation-methodology.md
```

## Exclude from public repo

Never export:

- `.env`, `**/secrets.yaml`, keys, tokens;
- `.git`, private history, stashes;
- `.hermes/`, `.claude/`, `.serena/`, local agent/session automation;
- `output/`, user-test audio, Android capture WAVs;
- `wake-word/data/` raw/processed/augmented audio;
- `wake-word/training/runs/`, feature caches, checkpoints;
- thesis LaTeX/Typst drafts unless explicitly decided;
- local absolute-path launchd plists;
- private notes with personal paths or usernames;
- `android-dev-voice/` large STT binaries unless separately licensed/reviewed.

## First public release scope

Tag: `v0.1.0-alpha`

Release title:

```text
Kratt v0.1.0-alpha — Estonian Home Assistant voice prototype
```

Contains:

1. Kratt v16c ESPHome wake-word model and manifest.
2. Kiirkirjutaja STT Home Assistant add-on.
3. Neurokõne TTS Home Assistant add-on.
4. Modular Docker Compose stack.
5. ESPHome Korvo-2 and generic ESP32-S3 examples.
6. Validation notes from local Docker/ESPHome checks.
7. Clear caveats about model quality and privacy.

Does not claim:

- production-ready wake-word quality;
- official Home Assistant Add-on Store publication;
- fully offline TTS when Neurokõne API is used;
- public release of any participant/user-test audio.

## Hugging Face plan

Create a separate model repository:

```text
https://huggingface.co/Yikizi/kuule-kratt-v16c
```

Contents:

- `kuule_kratt_v16c.tflite`
- `kuule_kratt_v16c.json`
- model card copied/adapted from `wake-word/models/kuule-kratt-v16c/NOTES.md`
- checksum and size

Do not publish datasets/audio without separate consent and license review.

## Minimum release checklist

Before making public:

- [ ] Choose final public GitHub URL (`Yikizi/kratt` vs `Yikizi/kratt-public`).
- [x] Add root `LICENSE` (Apache-2.0 for Kratt-owned code/config/docs/model artifacts; preserve third-party licenses where copied).
- [x] Add `NOTICE` with third-party attribution notes.
- [x] Add `TRADEMARK.md` reserving Kratt branding while keeping the code open.
- [x] Add `PRIVACY.md` explaining that raw audio is not published and STT is local, while Neurokõne TTS uses an external API.
- [x] Add `SECURITY.md` or minimal issue-reporting note.
- [ ] Export via whitelist, not `git push` from the private monorepo.
- [ ] Run secret scan on exported public tree.
- [ ] Run validation commands from `home-assistant/VALIDATION.md`.
- [ ] Create `v0.1.0-alpha` tag/release.
- [ ] Update Home Assistant add-on docs if the final URL is not `https://github.com/Yikizi/kratt`.
- [ ] Create Hugging Face model card or defer explicitly.

## Suggested export workflow

Use a clean export directory:

```bash
mkdir -p ../kratt-public-export
# copy only the allowlisted files/directories
cd ../kratt-public-export
git init -b main
git add .
git commit -m "feat: initial Kratt Home Assistant prototype release"
git remote add origin git@github.com:Yikizi/kratt.git
git push -u origin main
```

If the final URL is `Yikizi/kratt-public`, update all GitHub URLs in:

- `repository.yaml`
- `home-assistant/README.md`
- `docs/user-guide/home-assistant-quickstart.md`
- `hardware/esp32/esphome/README.md`
- `wake-word/models/kuule-kratt-v16c/kuule_kratt_v16c.json`
- `wake-word/models/kuule-kratt-v16c/NOTES.md`
