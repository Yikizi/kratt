# android/

24/7 false-trigger logger app for field-testing wake word models on a Pixel 8a.

## Purpose

Runs the microWakeWord TFLite model continuously on-device, logging every
trigger event (timestamp, confidence, audio clip) to Downloads/ for later
analysis. Used to measure real-world FAPH (False Accepts Per Hour).

## Key files

- `app/src/main/assets/kuule_kratt_*.tflite` — bundled candidate models
- `app/src/main/cpp/microfrontend/` — C audio feature extraction (MFCC)
- `app/src/main/java/.../detect/MultiDetector.kt` — parallel multi-model inference
- `app/src/main/java/.../log/EventLogger.kt` — `events.jsonl` session/detection logging
- `app/src/main/java/.../Settings.kt` — default model/config presets

## Build

**Android build requires JDK17.** Newer JDKs can fail during Gradle/Kotlin script
initialization (observed with Java `25.0.2`: `IllegalArgumentException: 25.0.2`).
Use the repo CLI wrapper when possible; it pins `JAVA_HOME` to the local JDK17:

```bash
./cli/kratt android install
```

Manual build:

```bash
export JAVA_HOME="$HOME/.sdkman/candidates/java/17.0.10-tem"
(cd android && ./gradlew assembleDebug)
# or open in Android Studio configured with JDK17
```

## Updating models

Add or replace `app/src/main/assets/kuule_kratt_<tag>.tflite`, then rebuild.
The app UI can select one or more bundled models; defaults/presets live in
`app/src/main/java/ee/taltech/kratt/falselog/Settings.kt`.
