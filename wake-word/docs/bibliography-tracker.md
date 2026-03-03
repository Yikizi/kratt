# Wake Word Bibliography Tracker

This file tracks dataset and tooling references as they are introduced into the wake word workflow.

## Active references

### `speechcommands2018`
- Role: public sanity-check dataset for validating the microWakeWord training and evaluation pipeline.
- Citation target: Pete Warden, "Speech Commands: A Dataset for Limited-Vocabulary Speech Recognition", 2018.
- Access path used in practice: TensorFlow Speech Commands dataset documentation and mirrored corpus downloads.
- Primary URL: https://arxiv.org/abs/1804.03209
- Notes: used for the `marvin` baseline experiment.

### `musan2015`
- Role: ambient noise, music, and speech negatives for false accept evaluation.
- Citation target: David Snyder, Guoguo Chen, Daniel Povey, "MUSAN: A Music, Speech, and Noise Corpus", 2015.
- Download URL: https://www.openslr.org/resources/17/musan.tar.gz
- License: CC BY 4.0
- Primary URL: https://arxiv.org/abs/1510.08484
- Notes: preferred public ambient source because the license is clean and the corpus is large.

### `voices2018`
- Role: far-field noisy speech and room acoustics for more realistic ambient evaluation.
- Citation target: Colleen Richey et al., "Voices Obscured in Complex Environmental Settings (VOICES) Corpus", 2018.
- Download URL: https://lab41openaudiocorpus.s3.amazonaws.com/VOiCES_devkit.tar.gz
- License: CC BY 4.0
- Primary URL: https://arxiv.org/abs/1804.05053
- Notes: closer to smart-speaker conditions than clean command corpora.

### `commonvoice2020`
- Role: multilingual speech negatives, especially useful for Estonian hard negatives.
- Citation target: Rosana Ardila et al., "Common Voice: A Massively-Multilingual Speech Corpus", LREC 2020.
- Download path used in practice: public Hugging Face mirror `malaysia-ai/common_voice_17_0`
- Original project URL: https://commonvoice.mozilla.org/
- Paper URL: https://aclanthology.org/2020.lrec-1.520/
- License: CC0 1.0
- Notes: cite the original corpus paper, not the mirror.

### `tensorflow2015`
- Role: main training framework used underneath `microWakeWord`.
- Citation target: Mart{\'i}n Abadi et al., "TensorFlow: Large-Scale Machine Learning on Heterogeneous Systems".
- Primary URL: https://www.tensorflow.org/
- Citation source used: TensorFlow official citation page.
- Notes: this is the software citation, not a wake-word-specific paper.

### `microwakeword2026`
- Role: wake word training and evaluation framework used for our experiments.
- Citation target: Kevin Ahrendt, `microWakeWord` GitHub repository.
- Primary URL: https://github.com/kahrendt/microWakeWord
- Local source used in practice: `/Users/mattias/kratt/external-repos/microWakeWord`
- Notes: no separate paper found; repository citation is the correct fallback.

### `openwakeword2026`
- Role: comparison framework for custom wake word prototyping and training workflow evaluation.
- Citation target: David Scripka, `openWakeWord` GitHub repository.
- Primary URL: https://github.com/dscripka/openWakeWord
- Notes: included as a practical comparison point against `microWakeWord`, especially for training ergonomics and iteration speed.

### `esphome2026`
- Role: deployment target and runtime integration layer for ESP32 wake word inference.
- Citation target: ESPHome official documentation / project site.
- Primary URL: https://esphome.io/
- Supporting repo URL: https://github.com/esphome/esphome
- Notes: practical software/platform citation.

### `homeassistant2026`
- Role: downstream smart home platform that receives wake word events and orchestrates automations.
- Citation target: Home Assistant official project site.
- Primary URL: https://www.home-assistant.io/
- Supporting repo URL: https://github.com/home-assistant/core
- Notes: platform citation rather than an ML-method citation.

## Working rule

When a new dataset, library, model, or benchmark enters the workflow:

1. Add a BibTeX entry to both thesis bibliography files.
2. Add a short row here with role, source URL, license, and why we used it.
3. Record the access date in the BibTeX `note` field.
