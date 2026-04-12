# Android 24/7 False-Trigger Logger (MVP Plan)

## 1) Goal
Build a **minimal Android app** (Pixel 8a target) that runs continuously, listens for wake-word triggers, and stores only detection snippets for later false-accept analysis.

## 2) MVP Scope (strict)
- Jetpack Compose UI with one simple screen (Start/Stop + small config).
- Foreground service with persistent notification.
- Continuous microphone capture (`AudioRecord`, 16 kHz mono PCM16).
- In-memory fixed-size ring buffer: **4s pre-roll**.
- Detection output snippet: **4s pre + 1s post** to WAV.
- Event metadata log to `events.jsonl`.
- No database.
- Files written to app-specific storage only.

## 3) Non-goals
- No cloud sync.
- No analytics backend.
- No advanced UI charts.
- No model training in-app.
- No complex settings system.

## 4) Reliability Model (realistic)
Target is **practically always-on**, not mathematically guaranteed never-killed.

Required for stable 24/7 behavior:
1. Foreground service (persistent notification).
2. `RECORD_AUDIO` permission granted.
3. Battery mode set to **Unrestricted** for the app.
4. Auto-restart on boot.
5. Defensive restart policy if service is reclaimed.

## 5) App Architecture (minimal)

### 5.1 Modules / responsibilities
- `MainActivity` (Compose):
  - shows running state + latest event summary;
  - Start/Stop buttons;
  - basic config inputs.
- `DetectorService` (ForegroundService):
  - owns audio capture + inference loop;
  - owns snippet writer + event logger.
- `AudioRingBuffer`:
  - fixed-size circular buffer for PCM16 pre-roll (4s).
- `WakeDetector`:
  - wraps TFLite interpreter and scoring API.
- `SnippetWriter`:
  - writes WAV snippets and returns file path.
- `EventLogger`:
  - appends JSONL event rows (`events.jsonl`).

### 5.2 Thread model
- Audio thread: ingest PCM into ring buffer.
- Inference thread: consume frames, compute score, trigger events.
- File I/O thread (or lightweight dispatch): write WAV/JSONL off hot path.

## 6) Runtime Config (MVP)
Expose only these fields:
- `threshold` (float)
- `preRollSec` (default 4)
- `postRollSec` (default 1)
- `cooldownSec` (default 2)
- `modelAsset` (single selected model for MVP)

All other parameters are hardcoded for reproducibility.

## 7) Detection Logic (MVP)
1. Stream audio continuously to ring buffer.
2. Compute wake score each step.
3. If `score > threshold` and not in cooldown:
   - mark detection;
   - collect current 4s pre-roll + 1s post-roll;
   - write `*.wav`;
   - append JSONL event row;
   - optionally play short alert sound.

## 8) Storage Layout
Use app-specific external files dir:

```text
Android/data/<package>/files/
  captures/
    2026-.._p0.953_c12.wav
  logs/
    events.jsonl
```

### JSONL schema (one event per line)
```json
{
  "ts": "2026-04-10T20:18:08.592Z",
  "model": "kuule_kratt_v9.tflite",
  "threshold": 0.90,
  "score": 0.953,
  "cooldown_sec": 2.0,
  "pre_roll_sec": 4.0,
  "post_roll_sec": 1.0,
  "wav": "captures/2026...wav",
  "device": "Pixel 8a",
  "app_version": "0.1.0"
}
```

## 9) Permissions & Manifest Essentials
- `RECORD_AUDIO`
- `FOREGROUND_SERVICE`
- Foreground service type: microphone (Android 14+ compatible declaration)
- `RECEIVE_BOOT_COMPLETED`

## 10) Testing Protocol (methodology-first)

### 10.1 Functional
- Start service -> notification visible.
- Detection creates WAV + JSONL row.
- Stop service -> recording stops cleanly.

### 10.2 Long-run
- 8h run with screen off.
- Overnight run (>= 12h).
- Verify no corrupted WAVs, no memory growth trend, no missing metadata rows.

### 10.3 Reproducibility
- Fixed model + fixed threshold per run block.
- Log config at service start in JSONL header event.
- Change only one variable between experiments.

## 11) Risks and Mitigations
- **OS kills service** -> foreground + unrestricted battery + restart policy.
- **Storage growth** -> optional daily cap/retention after MVP.
- **False positives burst** -> cooldown + optional score floor histogram review.
- **UI complexity creep** -> keep one-screen constraint.

## 12) Done Criteria (MVP)
- App can run overnight on Pixel 8a.
- Detection snippets are correctly saved as WAV (4s+1s).
- JSONL log is complete and parseable.
- No DB introduced.
- UI remains minimal (single screen, core controls only).

## 13) Immediate Build Plan
1. Create Android project skeleton (Compose + service wiring).
2. Implement `AudioRingBuffer` + `AudioRecord` pipeline.
3. Integrate TFLite model inference.
4. Implement snippet writer + JSONL logger.
5. Add Start/Stop UI and config fields.
6. Run 1h, then overnight stability test.
