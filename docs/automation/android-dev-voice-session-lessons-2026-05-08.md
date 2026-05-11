# Android Dev Voice MVP session lessons (2026-05-08)

Purpose: capture the practical lessons from building a phone-local voice-to-agent
MVP on the Pixel 8a/Termux setup. This is operational documentation, not a thesis
claim.

## Final working architecture

```text
Kratt Dev Voice Android app
  -> foreground service + notification + partial wakelock
  -> AudioRecord microphone capture (16 kHz mono PCM)
  -> sherpa-onnx Android AAR
  -> TalTechNLP / Kiirkirjutaja INT8 transducer assets
  -> final transcript
  -> optional short Android TextToSpeech status feedback
  -> HTTP POST http://127.0.0.1:8765/dispatch
  -> Termux: kratt dev-voice bridge
  -> kratt dev-voice send <text>
  -> tmux target agent
```

The key result of the session: **on-device Android STT with Kiirkirjutaja was
made to hear live speech and dispatch text into the coding-agent workflow**.

## Components added

- `kratt dev-voice` — development-focused wrapper around the thesis voice
  dispatcher.
- `kratt dev-voice bridge` — localhost HTTP bridge for Android -> Termux
  dispatch.
- `kratt dev-voice-android` — build/open/install helper for the Android MVP.
- `android-dev-voice/` — small pure-Java Android MVP app.
- `android-dev-voice/patch_manifest_ids.py` — workaround for Termux `aapt`
  binary manifest limitations.

## What worked

### 1. Termux can build a small Android APK on-device

A minimal Java-only APK can be built directly on Android/Termux with:

- `openjdk-21`
- `aapt`
- `d8`
- `apksigner`
- `zipalign`
- `android-tools`
- Google Android platform jar (`platform-35_r02.zip`) for compile-time classes

The Gradle Android Plugin can partially run on Termux, but it is brittle because
it downloads x86_64 build tools (`aapt2`) unless overridden.

### 2. Shizuku/rish is the best local install path

Normal package installer and Termux `pm install` both hit restrictions. `rish`
worked because it runs as Android shell:

```bash
rish -c 'pm install -r -t /data/local/tmp/KrattDevVoice.apk'
```

Important detail: installing from `/sdcard` failed because `system_server` cannot
read the FUSE context. Copy APK to `/data/local/tmp` first:

```bash
rish -c 'cp /sdcard/Download/KrattDevVoice/KrattDevVoice.apk /data/local/tmp/KrattDevVoice.apk && chmod 644 /data/local/tmp/KrattDevVoice.apk'
```

### 3. Package verifier can hang installs

`pm install` hung until verifier settings were disabled via shell:

```bash
rish -c 'settings put global verifier_verify_adb_installs 0'
rish -c 'settings put global package_verifier_enable 0'
```

After that, direct install succeeded.

### 4. Wireless debugging from the same device is possible, but annoying

ADB pairing worked only with the non-interactive syntax:

```bash
adb pair <ip>:<pairing-port> <six-digit-code>
```

The `printf '<code>\n' | adb pair ...` path produced a protocol fault in this
Termux setup. After pairing, `adb connect <ip>:<debug-port>` worked once, but was
less reliable than `rish` for local installs.

### 5. Localhost HTTP bridge is better than Termux RUN_COMMAND here

The original plan was Android app -> Termux `RunCommandService`. This failed in
practice because this Termux build did not expose/grant
`com.termux.permission.RUN_COMMAND` as expected:

```text
pm grant ... com.termux.permission.RUN_COMMAND
-> Unknown permission
```

The working replacement is:

```text
Android app -> http://127.0.0.1:8765/dispatch -> kratt dev-voice bridge
```

This also avoids app-to-app permission complexity.

### 6. Cleartext traffic must be enabled for localhost HTTP

The first bridge attempt failed with "cleartext not allowed". The manual manifest
patch now adds:

```xml
android:usesCleartextTraffic="true"
```

Because the old Termux `aapt` does not know that attribute, it is inserted by
`patch_manifest_ids.py` at binary XML level.

### 7. Microphone permission may need shell grant

The app requested `RECORD_AUDIO`, but the runtime permission popup did not appear
reliably. Granting it via rish fixed live mic capture:

```bash
rish -c 'pm grant ee.taltech.kratt.devvoice android.permission.RECORD_AUDIO'
```

## What was hard / surprising

### Docker on Android/Termux is not the right path

Docker packages install from Termux root-repo, but the daemon needs root/kernel
cgroups. Without a rooted/kernel-prepared Android device, `dockerd` is not a
practical path for live STT.

### Python `sherpa-onnx` on Termux is not the right path

`uv` worked, but Python `sherpa-onnx` tried to build for Android and failed in
its onnxruntime download/configuration path. Android AAR is the right packaging
format.

### Termux `ffmpeg` is not enough for live mic

`ffmpeg` installed, but the Termux build had no useful Android mic input device
for this workflow. Android `AudioRecord` is the correct mic layer.

### Old Termux `aapt` produced malformed framework attribute IDs

The initial manually built APK installed incorrectly because the binary manifest
used wrong framework attribute resource IDs, e.g. `android:name` came out as
`0x0101056c` instead of canonical `0x01010003`. Android PackageManager then
reported:

```text
INSTALL_PARSE_FAILED_MANIFEST_MALFORMED:
<activity> does not specify android:name
```

`patch_manifest_ids.py` fixes the resource map for known framework attrs.

### targetSdk/minSdk must be present

Android rejected the APK with:

```text
INSTALL_FAILED_DEPRECATED_SDK_VERSION:
App package must target at least SDK version 24, but found 0
```

The patcher now inserts:

```text
minSdkVersion = 24
targetSdkVersion = 30
```

### Gradle nearly worked, but not enough

Gradle/AGP reached resource processing after installing a real platform and build
tools, but failed because Maven-provided `aapt2` was x86_64. Overriding
`android.aapt2FromMavenOverride=/data/data/com.termux/files/usr/bin/aapt2` got
further, but then Termux `aapt2` could not load the Google platform jar resource
include. Manual build stayed more controllable for the MVP.

## Current limitations

- The app is an MVP, not a polished Android product.
- `auto-dispatch` should default off or be gated; otherwise every endpoint final
  transcript can be sent to the coding agent.
- Endpointing is whatever sherpa-onnx default config currently does; it needs UX
  tuning.
- Foreground-service listening is more robust than an Activity thread, but OEM
  battery management can still require disabling battery optimization for the app.
- No wake-word gate yet. This is dictation, not safe always-on voice control.
- Model assets make the APK large (~63 MB).
- AAR and model files are local/vendor-like dependencies; avoid committing large
  generated build outputs.

## Operational recipe

Start the target agent pane:

```bash
kratt dev-voice pane
# attach and start the desired agent in that pane
```

Start the Termux bridge:

```bash
kratt dev-voice bridge
```

Build/install the app through rish when needed:

```bash
kratt dev-voice-android build
cp android-dev-voice/build-manual/kratt-dev-voice-debug.apk \
  /sdcard/Download/KrattDevVoice/KrattDevVoice.apk
rish -c 'cp /sdcard/Download/KrattDevVoice/KrattDevVoice.apk /data/local/tmp/KrattDevVoice.apk && chmod 644 /data/local/tmp/KrattDevVoice.apk && pm install -r -t /data/local/tmp/KrattDevVoice.apk'
rish -c 'pm grant ee.taltech.kratt.devvoice android.permission.RECORD_AUDIO'
```

Run the app:

```bash
rish -c 'monkey -p ee.taltech.kratt.devvoice 1'
```

## Next improvements

1. Add a clear push-to-talk mode: hold/tap start, tap stop, then review final
   transcript before sending.
2. Add explicit `auto-dispatch` toggle defaulting to off.
3. Add a visible bridge status check (`GET /health`) before starting dictation.
4. Add a wake/control word only after the manual workflow is stable.
5. Persist endpointing/speaker settings in app preferences.
6. Consider a proper Gradle-on-Termux SDK setup only if manual build becomes too
   painful.
