# Kratt Kiirkirjutaja STT add-on

Local Estonian speech-to-text for Home Assistant Assist, exposed through the Wyoming protocol.

This add-on packages a minimal Kiirkirjutaja runtime around the TalTech INT8 streaming Zipformer model. It is a supporting component for the Kratt voice stack; it does **not** train a new STT model.

## Installation

1. In Home Assistant, open **Settings → Add-ons → Add-on Store → ⋮ → Repositories**.
2. Add this repository URL:
   `https://github.com/Yikizi/kratt`
3. Install **Kratt Kiirkirjutaja STT**.
4. Start the add-on.
5. Home Assistant should discover a Wyoming service. If not, open the add-on **Network** section, map container port `10300` to host port `10300`, restart the add-on, and add Wyoming manually:
   - Host: your Home Assistant host/IP
   - Port: `10300`

## Options

- `model_base_url`: base URL for `encoder.int8.onnx`, `decoder.int8.onnx`, `joiner.int8.onnx`, and `tokens.txt`.
- `debug_logging`: enables extra Python asyncio debug logging.

Model files are downloaded on first start and stored in `/data/models/sherpa-int8`, so restarts do not re-download them.

## Status

Experimental research-prototype packaging for the Kratt thesis project. Tested target architectures are `amd64` and `aarch64`.
