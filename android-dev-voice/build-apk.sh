#!/usr/bin/env bash
# Build the pure-Java Kratt Dev Voice MVP APK on Termux/Android without Gradle/NDK.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="$ROOT/app/src/main"
OUT="$ROOT/build-manual"
SDK="${ANDROID_HOME:-$HOME/android-sdk-termux}"
AAPT_JAR="/data/data/com.termux/files/usr/share/aapt/android.jar"
ANDROID_JAR="$SDK/platforms/android-35/android.jar"
SHERPA_AAR_DIR="$ROOT/libs/sherpa-aar"
SHERPA_CLASSES="$SHERPA_AAR_DIR/classes.jar"
KOTLIN_STDLIB="${KOTLIN_STDLIB:-$HOME/.gradle/caches/modules-2/files-2.1/org.jetbrains.kotlin/kotlin-stdlib/2.0.21/618b539767b4899b4660a83006e052b63f1db551/kotlin-stdlib-2.0.21.jar}"

if [[ ! -f "$AAPT_JAR" ]]; then
  echo "Missing Termux aapt android.jar: $AAPT_JAR" >&2
  echo "Install: pkg install aapt" >&2
  exit 1
fi
if [[ ! -f "$ANDROID_JAR" ]]; then
  echo "Missing Android platform jar: $ANDROID_JAR" >&2
  echo "This repo was tested with platform-35_r02 extracted under $SDK/platforms/android-35" >&2
  exit 1
fi
if [[ ! -f "$SHERPA_CLASSES" ]]; then
  echo "Missing sherpa AAR extraction: $SHERPA_CLASSES" >&2
  echo "Expected: android-dev-voice/libs/sherpa-aar from sherpa-onnx Android AAR" >&2
  exit 1
fi
if [[ ! -f "$KOTLIN_STDLIB" ]]; then
  echo "Missing Kotlin stdlib: $KOTLIN_STDLIB" >&2
  exit 1
fi
for tool in aapt javac d8 keytool zipalign apksigner; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Missing tool: $tool" >&2
    echo "Install basics: pkg install openjdk-21 aapt d8 apksigner" >&2
    exit 1
  fi
done

rm -rf "$OUT"
mkdir -p "$OUT/gen" "$OUT/classes" "$OUT/dex"

aapt package -f -m \
  -M "$APP/AndroidManifest.xml" \
  -S "$APP/res" \
  -A "$APP/assets" \
  -I "$AAPT_JAR" \
  -J "$OUT/gen" \
  -F "$OUT/resources.apk"

javac -source 8 -target 8 \
  -cp "$ANDROID_JAR:$SHERPA_CLASSES:$KOTLIN_STDLIB" \
  -d "$OUT/classes" \
  $(find "$APP/java" "$OUT/gen" -name '*.java')

d8 --release --min-api 23 \
  --lib "$ANDROID_JAR" \
  --output "$OUT/dex" \
  $(find "$OUT/classes" -name '*.class') \
  "$SHERPA_CLASSES" "$KOTLIN_STDLIB"

cp "$OUT/resources.apk" "$OUT/app-unsigned.apk"
(cd "$OUT/dex" && aapt add "../app-unsigned.apk" classes.dex >/dev/null)
mkdir -p "$OUT/native/lib/arm64-v8a"
cp "$SHERPA_AAR_DIR"/jni/arm64-v8a/*.so "$OUT/native/lib/arm64-v8a/"
(cd "$OUT/native" && aapt add "../app-unsigned.apk" lib/arm64-v8a/*.so >/dev/null)
python3 "$ROOT/patch_manifest_ids.py" "$OUT/app-unsigned.apk"

KEY="$ROOT/.debug.keystore"
if [[ ! -f "$KEY" ]]; then
  keytool -genkeypair -v \
    -keystore "$KEY" \
    -storepass android \
    -keypass android \
    -alias androiddebugkey \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -dname "CN=Android Debug,O=Android,C=US" >/dev/null
fi

zipalign -f 4 "$OUT/app-unsigned.apk" "$OUT/app-aligned.apk"
apksigner sign \
  --ks "$KEY" \
  --ks-pass pass:android \
  --key-pass pass:android \
  --out "$OUT/kratt-dev-voice-debug.apk" \
  "$OUT/app-aligned.apk"

apksigner verify --verbose "$OUT/kratt-dev-voice-debug.apk"
echo "$OUT/kratt-dev-voice-debug.apk"
