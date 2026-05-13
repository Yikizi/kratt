# Documentation

## What it provides

A Wyoming TTS server at `tcp://0.0.0.0:10301` for Estonian speech synthesis.

## Pipeline setup

After the add-on is running:

1. Open **Settings → Devices & services**.
2. Confirm the Wyoming integration was discovered. If not, map container port `10301` to host port `10301` in the add-on **Network** section and add the Wyoming integration manually with your Home Assistant host/IP and port `10301`.
3. Create/edit an Assist pipeline:
   - Text-to-speech: Neurokõne / Wyoming TTS
   - Language: Estonian (`et` / `et-EE`)

## Voices

Known Neurokõne voices exposed by the server include:

- `mari`
- `albert`
- `indrek`
- `kalev`
- `kylli`
- `lee`
- `liivika`
- `luukas`
- `meelis`
- `peeter`
- `tambet`
- `vesta`

## Privacy and dependency note

This wrapper calls `https://api.tartunlp.ai/text-to-speech/v2` at synthesis time. It is useful for a convenient Estonian TTS demo, but it is not a fully offline TTS component.
