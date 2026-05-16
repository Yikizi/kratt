# Kratt TartuNLP Local TTS add-on

Local Estonian text-to-speech for Home Assistant Assist, exposed through the Wyoming protocol on port `10301`.

This add-on does **not** call the public Neurokõne API. It runs the TartuNLP neural TTS worker locally in the user's Home Assistant add-on container and downloads the model files on first start.

## Provenance and attribution

- Upstream code/image: <https://github.com/TartuNLP/text-to-speech-worker>
- Pinned release/image: `v3.1.0` / `ghcr.io/tartunlp/text-to-speech-worker:3.1.0`
- Local checkout used by the Kratt demo: `tools/text-to-speech-worker/`
- Pinned commit observed locally: `14d47bf9af4e562829ccafcc757d93abb2a6412f`
- Model release: <https://github.com/TartuNLP/text-to-speech-worker/releases/tag/v3.1.0>
- Default model asset: `multispeaker.zip`
- License in upstream checkout: MIT, copyright University of Tartu

## Installation

1. In Home Assistant, open **Settings → Add-ons → Add-on Store → ⋮ → Repositories**.
2. Add this repository URL:
   `https://github.com/Yikizi/kratt`
3. Install **Kratt TartuNLP Local TTS**.
4. Start the add-on. First start downloads `multispeaker.zip`, extracts it under `/data/models`, and may also cache NLTK/Hugging Face assets.
5. Home Assistant should discover a Wyoming service. If not, open the add-on **Network** section, map container port `10301` to host port `10301`, restart the add-on, and add Wyoming manually:
   - Host: your Home Assistant host/IP
   - Port: `10301`

## Options

- `model_zip_url`: model ZIP URL, defaulting to TartuNLP `v3.1.0` `multispeaker.zip`.
- `voice`: one of `albert`, `indrek`, `kalev`, `kylli`, `liivika`, `mari`, `meelis`, `peeter`, `tambet`, `vesta`.
- `speed`: speech speed multiplier from `0.5` to `2.0`.
- `max_input_length`: local TTS chunk/input limit. Default `500`.
- `debug_logging`: enable debug logs.

## Architecture note

The upstream published image currently provides an `amd64` Linux image. This add-on is therefore initially marked `amd64` only. ARM/aarch64 support should be validated separately before enabling it for Raspberry Pi Home Assistant installations.

## Status

Experimental research-prototype packaging for the Kratt thesis project. It is the preferred TTS direction over the previous API wrapper because synthesis text stays local after the model/assets have been downloaded.
