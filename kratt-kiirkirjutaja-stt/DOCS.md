# Documentation

## What it provides

A Wyoming ASR server at `tcp://0.0.0.0:10300` for Estonian speech recognition.

Home Assistant can use it in an Assist pipeline as the STT engine. The wake word can run separately on ESPHome/microWakeWord hardware using the Kratt v16c model.

## First start

The first start downloads the INT8 Kiirkirjutaja model files from Hugging Face into persistent add-on data:

- `encoder.int8.onnx`
- `decoder.int8.onnx`
- `joiner.int8.onnx`
- `tokens.txt`

This can take a few minutes depending on hardware and network speed.

## Pipeline setup

After the add-on is running:

1. Open **Settings → Devices & services**.
2. Confirm the Wyoming integration was discovered. If not, map container port `10300` to host port `10300` in the add-on **Network** section and add the Wyoming integration manually with your Home Assistant host/IP and port `10300`.
3. Create/edit an Assist pipeline:
   - Conversation agent: Home Assistant
   - Speech-to-text: Kiirkirjutaja / Wyoming STT
   - Language: Estonian (`et`)

## Privacy

Recognition runs locally on the device running the add-on. Model download uses Hugging Face on first start unless you set `model_base_url` to another mirror.
