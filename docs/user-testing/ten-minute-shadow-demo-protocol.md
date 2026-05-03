# 10-minute shadow-demo user test protocol

**Status:** current protocol for self-pilot / pilot freeze (updated 2026-04-29)  
**Target duration:** 10 minutes per participant  
**Primary goal:** collect real-speaker wake-word evidence while keeping the session short and engaging through a one-bulb smart-home demo.  
**Recorder:** `./cli/kratt user-test <participant_id> --active-model v16c --new-session-subdir`

## Core design

Each participant interacts with **one active demo system**. In parallel, every utterance is saved as a labelled audio trial so the same audio can later be replayed through multiple wake-word models and consensus combinations.

This separates three concerns:

1. **User-visible UX:** one stable active model controls the demo.
2. **Model comparison:** many models are evaluated offline on identical audio.
3. **Future analysis:** thresholds and MoE combinations can be swept after the session without asking the participant to repeat anything.

## Candidate set to freeze before full collection

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
| 9:00–10:00 | 4 ratings + 1 open comment | subjective UX |

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

### D. Free-form task

Prompt:

> Proovi nüüd oma sõnadega teha valgus selliseks, nagu tahaksid õhtul filmi vaadata.

Rule:

```text
maximum 2 command attempts
```

Purpose:

- natural Estonian smart-home command phrasing;
- repair behaviour;
- subjective system flexibility.

### E. Mini questionnaire

Rate 1–5:

1. Süsteem reageeris piisavalt usaldusväärselt.
2. Süsteem reageeris piisavalt kiiresti.
3. Käskude sõnastamine tundus loomulik.
4. Kasutaksin sellist süsteemi kodus.

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

With 20 participants:

- approximately 220–260 positive wake-containing utterances;
- 100 hard-negative utterances;
- 120 scripted smart-home commands;
- 20–40 natural command attempts.

With 30 participants:

- approximately 330–390 positive wake-containing utterances;
- 150 hard-negative utterances;
- 180 scripted smart-home commands;
- 30–60 natural command attempts.

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

Use two consent levels:

1. **Basic consent:** anonymous metrics and logs may be used in the thesis.
2. **Audio opt-in:** labelled audio clips may be stored and used for wake-word evaluation/model improvement.

Participants who decline audio storage may still contribute UX/questionnaire data. If audio consent is declined, do not retain raw WAV files; retain only aggregate/non-identifying outcomes where allowed by the consent form.

## Methodological guardrails

- Keep controlled wake-word metrics separate from end-to-end demo metrics.
- Do not attribute STT/LLM/WiZ failures to the wake-word model.
- Freeze the final candidate set and main thresholds before full data collection.
- Treat extra threshold sweeps and extra MoE combinations as exploratory.
- Use one smart bulb intentionally to keep tasks repeatable and scope controlled.

## Pilot checklist

Before full data collection:

- [ ] Run one dry-run self-pilot: `kratt user-test TEST --dry-run --new-session-subdir`.
- [ ] Run one real-mic self-pilot with audio consent enabled.
- [ ] Verify every trial creates one WAV and one `trials.jsonl` row.
- [ ] Verify the WiZ commands work manually.
- [ ] Verify active demo logs STT/intent/action latency, or document which fields are manual.
- [ ] Verify replay analysis can score the recorded WAVs.
- [ ] Freeze active model and thresholds.
- [ ] Run 2–3 participant pilots and only then freeze final wording.
