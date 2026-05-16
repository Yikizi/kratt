# Changelog

## 0.2.0

- Replaced the public Neurokõne API wrapper path with a local TartuNLP `text-to-speech-worker` based Wyoming TTS server.
- Pinned upstream TartuNLP worker image/release to `v3.1.0`.
- Added first-start download of the `multispeaker.zip` model release into `/data/models`.
- Restricted initial add-on architecture to `amd64`, matching the upstream published worker image.

## 0.1.0

- Initial Home Assistant add-on packaging for the Wyoming Neurokõne API wrapper.
