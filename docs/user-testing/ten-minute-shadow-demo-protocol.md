# 10-minute shadow-demo user test protocol

**Status:** current protocol for self-pilot / pilot freeze (updated 2026-05-12)
**Target duration:** 10 minutes per participant
**Target sample:** up to 10 participants
**Primary goal:** check the usefulness and UX of the complete local voice-assistant loop while collecting limited real-speaker wake-word evidence through a one-bulb smart-home demo.
**Recorder:** `./cli/kratt user-test <participant_id> --active-model v16c --new-session-subdir`

## Core design

Each participant interacts with **one active demo system**. In parallel, every utterance is saved as a labelled audio trial so the same audio can later be replayed through multiple wake-word models and consensus combinations.

This separates three concerns:

1. **User-visible UX:** one stable active model controls the demo.
2. **Model comparison:** many models are evaluated offline on identical audio.
3. **Future analysis:** thresholds and MoE combinations can be swept after the session without asking the participant to repeat anything.

## Candidate set to freeze before pilot collection

Primary candidates for final reporting:

- `v16c` — stable single-model baseline / recommended active demo model.
- `expert-a` — field/recall reference candidate.
- `expert-a + expert-b2` — historical consensus/MoE milestone.

Baselines / anchors:

- `v6-residual` — ultra-conservative low-FAPH anchor.
- `v10` — earlier moderate-FAPH fallback.
- `v15` — real-life balance reference from earlier findings.

Recommended active system for the first pilot:

```text
active_model = v16c
```

Optional final A/B UX setup, if the pilot is stable:

```text
50% participants: active_model = v16c
50% participants: active_model = expert-a
```

Offline replay models stay identical for all participants.

## Threshold policy

Pilot freeze candidate: `docs/user-testing/frozen-threshold-policy.md`.

Before final analysis, freeze one deployment threshold per model for the main table. Threshold sweeps may still be reported as exploratory.

Suggested initial reporting thresholds:

| Model | Initial threshold note |
|---|---|
| `v16c` | Android/runtime comparison threshold or selected deployment threshold |
| `expert-a` | same policy as `v16c` |
| `expert-b2` | only as verifier/consensus unless reporting standalone |
| `v6-residual` | baseline threshold matching existing eval where possible |
| `v10` | baseline threshold matching existing eval where possible |
| `v15` | baseline threshold matching existing eval where possible |

The thesis should clearly distinguish:

- **pre-registered/frozen** operating points used for the main comparison;
- **exploratory** DET/threshold sweeps used for interpretation.

## 10-minute session timeline

| Time | Block | Output |
|---:|---|---|
| 0:00–1:00 | Consent + minimal metadata | participant ID, consent level |
| 1:00–2:30 | 5 positive wake trials | clean wake recall |
| 2:30–3:30 | 5 hard negatives | confusable-phrase rejection |
| 3:30–7:30 | 6 scripted bulb commands | end-to-end task success + more positive wake attempts |
| 7:30–9:00 | 1 free-form bulb task | natural Estonian smart-home phrasing |
| 9:00–10:00 | locked mini questionnaire | UMUX-Lite, SEQ, diagnostic UX |

## Trial script

### A. Positive wake trials

The participant reads/says:

1. `Kuule Kratt`
2. `Kuule Kratt`
3. `Kuule Kratt`
4. `Kuule Kratt, pane tuli põlema`
5. `Kuule Kratt, muuda tuli siniseks`

Purpose:

- clean real-speaker recall;
- score distributions and trigger latency;
- model comparison on the same speaker and room.

### B. Hard-negative trials

The participant reads:

1. `Kuule rott`
2. `Tere Kratt`
3. `Kratt kuule`
4. `Kuule robot`
5. `Kuule, kas sa kuuled?`

Purpose:

- human-spoken confusable phrase rejection;
- hard-negative FPR per model and consensus.

### C. Scripted one-bulb commands

The participant controls the lamp:

1. `Kuule Kratt, pane tuli põlema.`
2. `Kuule Kratt, pane tuli punaseks.`
3. `Kuule Kratt, muuda tuli siniseks.`
4. `Kuule Kratt, vähenda heledust.`
5. `Kuule Kratt, pane tuli valgeks.`
6. `Kuule Kratt, pane tuli kustu.`

Rule:

```text
maximum 2 attempts per task
```

Purpose:

- end-to-end UX;
- wake + STT + intent + action decomposition;
- additional positive wake attempts.

### D. Free-form exploration task

Prompt:

> Nüüd on avastamise osa. Proovi ühte toetatud, aga loomulikult sõnastatud või veidi poolikut käsku. Hea siht on valgus: värv, heledus, efekt või olek. Näiteks: "tuba on liiga hele", "tee diskot", "vilguta roosalt", "mis värvi tuli on" või "pane tuli teist värvi" ja vasta Krati täpsustusele ilma uut äratussõna ütlemata. Võid küsida ka infot, näiteks "mis ilm homme Tartus on" või "mis päev kahe päeva pärast on", või ühe lühikese üldküsimuse. Taimerid, muusika, uksed ja muud seadmed ei ole selle demo võimekused.

Rule:

```text
maximum 2 command attempts
```

Purpose:

- natural Estonian smart-home command phrasing;
- light repair behaviour and follow-up commands;
- subjective system flexibility;
- richer edge cases than repeated simple bulb commands.

### E. Locked mini questionnaire

Use the short form in `docs/user-testing/mini-questionnaire-form-v1.md`.

Comparable measures:

- UMUX-Lite, two 7-point items.
- SEQ, one 7-point post-task ease item.

Diagnostic Kratt-specific ratings, 1–5:

- Süsteem reageeris piisavalt usaldusväärselt.
- Süsteem reageeris piisavalt kiiresti.
- Käskude sõnastamine tundus loomulik.
- Kasutaksin sellist süsteemi kodus.

Open question:

- Mis oli kõige häirivam või üllatavam?

## Data yield

Per participant:

- 5 standalone positive wake trials;
- 5 hard-negative trials;
- 6 scripted command trials;
- 1–2 free-form command attempts;
- 11–13 wake-containing positive utterances total;
- one short subjective UX response set.

With up to 10 participants:

- approximately 110–130 positive wake-containing utterances;
- 50 hard-negative utterances;
- 60 scripted smart-home commands;
- 10–20 natural command attempts.

This is intentionally a pilot-sized UX and usefulness check, not a replacement for the main wake-word validation protocol. The main model-quality claims remain tied to frozen thresholds, streaming FAPH, real-speaker recall, and hard-negative/confusable FPR.

## Logging schema

Minimum per trial in `trials.jsonl`:

```json
{
  "participant_id": "P01",
  "trial_id": "CMD_RED",
  "trial_type": "scripted_command",
  "expected_wake": true,
  "expected_text": "Kuule Kratt, pane tuli punaseks.",
  "expected_intent": "set_color_red",
  "attempt_number": 1,
  "active_model": "v16c",
  "audio_file": "audio/P01_CMD_RED_attempt1.wav",
  "sample_rate": 16000,
  "duration_s": 5.0,
  "timestamp_start": "...",
  "timestamp_end": "..."
}
```

Active demo telemetry may add:

```text
wake_detected_active
wake_latency_ms
stt_text
predicted_intent
action_success
user_visible_success
e2e_latency_ms
```

Offline replay should add separate per-model rows:

```text
model_name
max_score
triggered
trigger_time_ms
threshold
consensus_combo
```

Implemented recorder output:

```bash
./cli/kratt user-test P01 --active-model v16c --new-session-subdir
```

This creates a session directory with `session.json`, `trials.jsonl`, and optional `audio/*.wav` files depending on consent.

Before real recording, pick and smoke-test the input device:

```bash
./cli/kratt user-test --list-devices
./cli/kratt user-test --mic-smoke-test --device <input_device_id>
```

Synthetic fixture smoke test (TTS/macOS `say`; infrastructure only, not user-study evidence):

```bash
./cli/kratt user-test-fixtures --output-dir output/user-test-fixtures/ten-minute-v1
./cli/kratt user-test SYNTH01 \
  --audio-fixture-dir output/user-test-fixtures/ten-minute-v1 \
  --auto-advance \
  --new-session-subdir
```

Validate every pilot/full session immediately after recording:

```bash
./cli/kratt validate-user-test output/user-tests/P01/<session_dir>
```

The validator checks trial counts, JSONL schema, consent handling, WAV existence, sample rate/channel count, duration, and very-low-RMS microphone warnings.

Replay consented WAVs through the frozen shadow set after each audio-consent session:

```bash
./cli/kratt replay-user-test output/user-tests/P01/<session_dir>
```

Default replay models are `v16c`, `expert-a`, `expert-b2`, `v6-residual`, `v10`, and `v15`; default consensus is `expert-a+expert-b2`; default replay threshold is `0.996` with a 5-frame moving average and 0.5s prepended silence for streaming-state warmup. This writes `output/user-test-replay/<participant>/<session_id>/replay_scores.jsonl` and `replay_summary.csv` with per-model/per-combo trigger decisions and trigger times.

Aggregate replayed sessions into thesis-ready tables with Wilson intervals. By default this excludes dry-run and synthetic fixture rows; use `--include-smoke` only for infrastructure debugging.

```bash
./cli/kratt summarize-user-test output/user-test-replay
```

## Metrics

### Wake-word metrics

- positive recall per model;
- hard-negative FPR per model;
- recall/FPR for consensus combinations;
- trigger latency distribution;
- optional DET/threshold sweep.

### End-to-end metrics

For each command task:

- wake success;
- STT transcript correct enough;
- intent correct;
- bulb action success;
- first-attempt success;
- success within 2 attempts;
- total latency.

### UX metrics

- reliability rating;
- perceived speed;
- command naturalness;
- willingness to use;
- qualitative complaint/surprise.

## Consent model

Participant-facing consent draft: `docs/user-testing/consent-script-v1.md`. Mini questionnaire form: `docs/user-testing/mini-questionnaire-form-v1.md`.

Use two consent levels:

1. **Ainult mõõdikud:** anonymous metrics and logs may be used in the thesis.
2. **Mõõdikud + helisalvestis:** labelled audio clips may be stored and used for wake-word evaluation/model improvement.

Participants who decline audio storage may still contribute UX/questionnaire data. If audio consent is declined, do not retain raw WAV files; retain only aggregate/non-identifying outcomes where allowed by the consent form.

## Methodological guardrails

- Keep controlled wake-word metrics separate from end-to-end demo metrics.
- Do not attribute STT/LLM/WiZ failures to the wake-word model.
- Freeze the final candidate set and main thresholds before pilot data collection.
- Treat extra threshold sweeps and extra MoE combinations as exploratory.
- Use one smart bulb intentionally to keep tasks repeatable and scope controlled.

## Pilot checklist

Before pilot data collection:

- [x] Run one dry-run recorder smoke test: `kratt user-test TEST_AUTO --dry-run --new-session-subdir` (2026-05-04).
- [x] Verify dry-run creates 17 WAVs + 17 `trial` JSONL rows (2026-05-04, `kratt validate-user-test`).
- [x] Verify `--audio-consent no` retains no WAVs but keeps trial metadata (2026-05-04).
- [x] Add microphone smoke-test command: `kratt user-test --mic-smoke-test --device <id>` (2026-05-04).
- [x] Add synthetic fixture injection path: `kratt user-test-fixtures` + `kratt user-test --audio-fixture-dir ... --auto-advance` (2026-05-04).
- [x] Prepare ESPHome local active model copy as `v16c` at cutoff `0.996` with `kratt prepare-esphome-model v16c --cutoff 0.996` (2026-05-04; firmware build and ESP32 upload still required before ESP32 demo).
- [ ] Run one real-mic self-pilot with audio consent enabled.
- [ ] Validate real-mic self-pilot immediately with `kratt validate-user-test <session_dir>`.
- [ ] Replay real-mic self-pilot with `kratt replay-user-test <session_dir>`.
- [ ] Aggregate replay outputs with `kratt summarize-user-test output/user-test-replay`.
- [ ] Verify the WiZ commands work manually.
- [ ] Verify active demo logs STT/intent/action latency, or document which fields are manual.
- [x] Verify replay analysis can score dry-run WAVs (2026-05-04, `kratt replay-user-test`).
- [ ] Verify replay analysis can score real-mic WAVs.
- [ ] Freeze active model and thresholds.
- [ ] Run 2–3 participant pilots and only then freeze final wording.
