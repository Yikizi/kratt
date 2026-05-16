# Documentation

## What it provides

A local Wyoming TTS server at `tcp://0.0.0.0:10301` for Estonian speech synthesis.

The add-on uses TartuNLP `text-to-speech-worker` inside the Home Assistant add-on container.

## Pipeline setup

After the add-on is running:

1. Open **Settings → Devices & services**.
2. Confirm the Wyoming integration was discovered. If not, map container port `10301` to host port `10301` in the add-on **Network** section and add the Wyoming integration manually with your Home Assistant host/IP and port `10301`.
3. Create/edit an Assist pipeline:
   - Text-to-speech: Kratt TartuNLP Local TTS / Wyoming TTS
   - Language: Estonian (`et` / `et-EE`)

## Voices

Voices exposed by the local TartuNLP multispeaker model:

- `albert`
- `indrek`
- `kalev`
- `kylli`
- `liivika`
- `mari`
- `meelis`
- `peeter`
- `tambet`
- `vesta`

## Provenance

- Upstream: <https://github.com/TartuNLP/text-to-speech-worker>
- Release/image: `v3.1.0`
- Model asset: <https://github.com/TartuNLP/text-to-speech-worker/releases/tag/v3.1.0>
- License in upstream checkout: MIT, University of Tartu

## Privacy and dependency note

Synthesis runs locally after the model/assets have been downloaded. First start requires network access to download the model ZIP and may cache NLTK/Hugging Face assets.
