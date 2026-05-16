# Privacy

Kratt is designed as a privacy-first Estonian voice-assistant prototype. This file explains what the public project does and does not publish or process.

## What is not published

The public Kratt repository must not contain:

- raw participant audio;
- user-test WAV files;
- Android false-trigger audio captures;
- private Home Assistant logs;
- Wi-Fi credentials, API tokens, encryption keys, or `.env` files;
- raw/processed local training datasets that contain personal voice recordings.

Public model/evaluation artifacts are limited to code, model files, manifests, aggregate metrics, documentation, and consent-safe summaries.

## Wake word

The ESPHome/microWakeWord Kratt wake-word model runs locally on the user's ESP32-S3 class device. Wake-word detection does not require cloud processing.

The public `v16c` model is a research-prototype baseline, not a production-proven detector. Users should review the model caveats before relying on it in privacy- or safety-sensitive environments.

## Speech-to-text

The Kratt Kiirkirjutaja STT add-on runs recognition locally on the device that runs the add-on after downloading the model files. The add-on downloads model artifacts from Hugging Face on first start unless the user configures another `model_base_url`.

Audio sent from Home Assistant to the STT add-on is processed locally by the add-on.

## Text-to-speech

The active Kratt TartuNLP Local TTS add-on path runs synthesis locally using TartuNLP `text-to-speech-worker` after downloading model/assets on first start. Synthesis text is not sent to the public Neurokõne API by this local path.

Historical API-wrapper code was removed from the active add-on path because the public Neurokõne API should not be integrated as a default application backend without explicit permission and clear data-handling terms.

## Home Assistant and ESPHome

Users are responsible for their own Home Assistant, ESPHome, network, and voice-pipeline configuration. The public examples avoid committing secrets and use `secrets.yaml.example` placeholders.

## User testing

If Kratt is used for future studies, participants should be offered separate consent choices for metrics-only logging and raw-audio retention. Raw audio should not be published without separate explicit consent and a compatible data license.
