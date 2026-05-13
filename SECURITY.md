# Security policy

## Supported versions

This repository currently publishes experimental research-prototype releases. Until a stable release exists, security fixes are handled on the latest public `main` branch and the latest tagged alpha release when practical.

## Reporting a vulnerability

Please do not publish sensitive security issues before the maintainer has had a chance to respond.

Report vulnerabilities through one of these channels:

1. Open a private/security advisory on GitHub if available for the public repository.
2. Otherwise, contact the maintainer through the GitHub profile contact information and include `[Kratt security]` in the subject if email is used.

Include:

- affected component (`kratt-kiirkirjutaja-stt`, `kratt-neurokone-tts`, ESPHome config, Docker Compose, etc.);
- reproduction steps;
- impact;
- whether any credentials, audio, or Home Assistant data may be exposed.

## Secrets

Do not commit:

- `.env` files;
- `secrets.yaml`;
- Home Assistant tokens;
- ESPHome API encryption keys;
- Wi-Fi credentials;
- raw user/participant audio.

Use the provided `secrets.yaml.example` files and local Home Assistant/ESPHome secret storage.
