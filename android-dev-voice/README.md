# Kratt Dev Voice Android MVP

Tiny Android app for testing Android -> Termux voice dispatch without Docker.
It started as a text dispatch MVP and now also contains an experimental
on-device STT path:

```text
AudioRecord -> sherpa-onnx Android AAR -> Kiirkirjutaja INT8 assets -> localhost bridge
```

See the session write-up for detailed lessons:

- `docs/automation/android-dev-voice-session-lessons-2026-05-08.md`

## Runtime flow

In Termux, start the coding target pane and bridge:

```bash
kratt dev-voice pane
kratt dev-voice bridge
```

The app also exposes a small phone-local speech API while its foreground service
is running:

```bash
curl -X POST --data 'Tere, see on Kratt Dev Voice kõne API.' http://127.0.0.1:8766/speak
curl http://127.0.0.1:8766/health
./cli/kratt dev-voice speak 'Tere Androidi kõne API kaudu.'
```

In the app:

- `Send to localhost bridge` sends the text box to Termux.
- `Start foreground dictation` starts Android microphone capture inside a
  foreground service with a persistent notification and partial wakelock, so
  Android is less likely to stop listening while the app is backgrounded.
- `Auto-dispatch final transcript to bridge` controls whether final STT results
  are sent automatically or only spoken/logged for review.
- The phone uses Android TextToSpeech for short status feedback and for the
  local `/speak` API. It intentionally does not read the recognized transcript
  back verbatim.

## Permissions

If Android does not show the microphone permission prompt, grant it via Shizuku
`rish`:

```bash
rish -c 'pm grant ee.taltech.kratt.devvoice android.permission.RECORD_AUDIO'
```

The background listening path also declares `FOREGROUND_SERVICE`,
`FOREGROUND_SERVICE_MICROPHONE`, `POST_NOTIFICATIONS`, and `WAKE_LOCK`. If OEM
battery management still stops the service, disable battery optimization for
“Kratt Dev Voice” in Android settings.

## Build on Android/Termux

Install basics once:

```bash
pkg install openjdk-21 aapt d8 apksigner android-tools
```

The manual build needs a real Android platform jar at
`$ANDROID_HOME/platforms/android-35/android.jar` (tested with Google
`platform-35_r02.zip`) plus the local sherpa AAR extraction under
`android-dev-voice/libs/sherpa-aar/`.

Build:

```bash
kratt dev-voice-android build
```

Install via rish:

```bash
cp android-dev-voice/build-manual/kratt-dev-voice-debug.apk \
  /sdcard/Download/KrattDevVoice/KrattDevVoice.apk
rish -c 'cp /sdcard/Download/KrattDevVoice/KrattDevVoice.apk /data/local/tmp/KrattDevVoice.apk && chmod 644 /data/local/tmp/KrattDevVoice.apk && pm install -r -t /data/local/tmp/KrattDevVoice.apk'
```

Open the app:

```bash
rish -c 'monkey -p ee.taltech.kratt.devvoice 1'
```
