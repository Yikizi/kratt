# Kratt Android false-trigger logger

Android app for field-testing Kratt wake-word models on a Pixel/Android device.
It runs bundled microWakeWord TFLite models continuously, logs trigger events to
`events.jsonl`, and saves WAV snippets for later FAPH analysis.

## Build requirement

**Use JDK17.** Newer JDKs can fail during Gradle/Kotlin script initialization
(observed with Java `25.0.2`: `IllegalArgumentException: 25.0.2`).

Preferred install path from repo root:

```bash
./cli/kratt android install
```

The CLI wrapper sets `JAVA_HOME` to the local JDK17 path used by this project.

Manual build:

```bash
export JAVA_HOME="$HOME/.sdkman/candidates/java/17.0.10-tem"
cd android
./gradlew assembleDebug
```

Or configure Android Studio to use JDK17.

## Useful commands

From repo root:

```bash
./cli/kratt android install   # build + install debug APK
./cli/kratt android logs      # filtered logcat
./cli/kratt android pull      # pull WAV snippets + events.jsonl and summarize FAPH
```

## Key files

- `app/src/main/assets/kuule_kratt_*.tflite` — bundled wake-word models
- `app/src/main/java/ee/taltech/kratt/falselog/detect/MultiDetector.kt` — parallel multi-model inference
- `app/src/main/java/ee/taltech/kratt/falselog/log/EventLogger.kt` — JSONL logging
- `app/src/main/java/ee/taltech/kratt/falselog/Settings.kt` — defaults and presets
