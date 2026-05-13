# Kratt Neurokõne TTS add-on

Estonian text-to-speech for Home Assistant Assist, exposed through the Wyoming protocol.

This add-on wraps the Tartu Neurokõne API and returns 16 kHz PCM audio to Home Assistant.

> Privacy note: unlike the Kiirkirjutaja STT add-on, this add-on currently calls the external TartuNLP Neurokõne API. Use Piper or another local TTS service if you need a fully offline stack.

## Installation

1. In Home Assistant, open **Settings → Add-ons → Add-on Store → ⋮ → Repositories**.
2. Add this repository URL:
   `https://github.com/Yikizi/kratt`
3. Install **Kratt Neurokõne TTS**.
4. Start the add-on.
5. Home Assistant should discover a Wyoming service. If not, open the add-on **Network** section, map container port `10301` to host port `10301`, restart the add-on, and add Wyoming manually:
   - Host: your Home Assistant host/IP
   - Port: `10301`

## Options

- `voice`: Neurokõne speaker name, for example `mari`, `meelis`, `albert`, `kalev`.
- `speed`: speech speed multiplier from `0.5` to `2.0`.
- `debug_logging`: enable debug logs.

## Status

Experimental research-prototype packaging for the Kratt thesis project.
