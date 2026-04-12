# android/

24/7 false-trigger logger app for field-testing wake word models on a Pixel 8a.

## Purpose

Runs the microWakeWord TFLite model continuously on-device, logging every
trigger event (timestamp, confidence, audio clip) to Downloads/ for later
analysis. Used to measure real-world FAPH (False Accepts Per Hour).

## Key files

- `app/src/main/assets/kuule_kratt_v11.tflite` — deployed model
- `app/src/main/cpp/microfrontend/` — C audio feature extraction (MFCC)
- `app/src/main/java/.../` — Kotlin service + notification UI

## Build

```bash
(cd android && ./gradlew assembleDebug)
# or open in Android Studio
```

## Updating the model

Replace `app/src/main/assets/kuule_kratt_v11.tflite` with a new version,
update the filename reference in the Kotlin service, rebuild.
