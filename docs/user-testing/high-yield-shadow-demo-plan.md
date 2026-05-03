# High-yield 10-minute user test plan

> **Merged / superseded (2026-04-29):** current protocol is `docs/user-testing/ten-minute-shadow-demo-protocol.md`. Keep this file as an earlier planning note.

Purpose: collect maximum thesis value from a short participant session by combining controlled wake-word testing, smart-bulb UX, and multi-model shadow evaluation on the same audio.

## Core idea

Each participant interacts with one visible demo system, while the same audio is logged for offline/shadow evaluation across multiple wake-word models.

- **Visible/active system:** one deployed model, e.g. `v16c` or counterbalanced `v16c`/`expert-a`.
- **Shadow/offline models:** `v16c`, `expert-a`, `expert-b2`, `v10`, `v6-residual`, `v15`.
- **Offline combinations:** `expert-a + expert-b2`, `v16c + expert-b2`, `expert-a + v16c`.
- **Main principle:** user workload stays low; model comparison happens in logs/replay.

## Target duration

Ideal session length: **10 minutes**. Acceptable range: **5–15 minutes**.

| Segment | Time | Purpose |
|---|---:|---|
| Consent + metadata | 1 min | participant ID, language background, audio consent |
| Scripted wake positives | 1.5 min | clean wake-word recall |
| Hard negatives | 1 min | confusable phrase rejection |
| Scripted bulb demo | 4 min | end-to-end task success + extra wake trials |
| Free-form mini task | 1.5 min | natural Estonian command phrasing |
| Mini questionnaire | 1 min | subjective UX |

## Session script

### 1. Consent + minimal metadata

Collect only what is needed:

- participant ID
- Estonian native / second language / other
- smart-home experience: yes/no
- audio recording consent: metrics only / metrics + audio
- optional: accent/dialect note

### 2. Scripted wake positives

Participant says five short positives:

1. `Kuule Kratt`
2. `Kuule Kratt`
3. `Kuule Kratt`
4. `Kuule Kratt, pane tuli põlema`
5. `Kuule Kratt, muuda tuli siniseks`

Metrics:

- wake detected yes/no
- wake latency
- per-model trigger/max score in shadow replay

### 3. Hard-negative/confusable phrases

Participant reads five negatives:

1. `Kuule rott`
2. `Tere Kratt`
3. `Kratt kuule`
4. `Kuule robot`
5. `Kuule, kas sa kuuled?`

Metrics:

- false trigger per model
- hard-negative FPR on real human voices

### 4. Scripted smart-bulb demo

Use one controllable bulb. Maximum two attempts per task.

1. `Kuule Kratt, pane tuli põlema.`
2. `Kuule Kratt, pane tuli punaseks.`
3. `Kuule Kratt, muuda tuli siniseks.`
4. `Kuule Kratt, vähenda heledust.`
5. `Kuule Kratt, pane tuli valgeks.`
6. `Kuule Kratt, pane tuli kustu.`

For each task, log pipeline stages separately:

- wake detected
- STT transcript
- intent parsed correctly
- bulb action succeeded
- total latency
- first-attempt success / success within two attempts / failed

### 5. Free-form mini task

Give one natural task, max two attempts:

> Proovi oma sõnadega teha valgus selliseks, nagu tahaksid õhtul filmi vaadata.

Purpose:

- collect natural Estonian smart-home command phrasing
- observe repair behavior
- test perceived flexibility

### 6. Mini questionnaire

Likert 1–5:

1. Süsteem reageeris piisavalt usaldusväärselt.
2. Süsteem reageeris piisavalt kiiresti.
3. Käskude sõnastamine tundus loomulik.
4. Kasutaksin sellist süsteemi kodus.

Open question:

- Mis oli kõige häirivam või üllatavam?

## Logging requirements

Minimum per trial:

```text
participant_id
trial_id
trial_type
expected_phrase
active_model
audio_file_or_time_range
wake_detected_active
wake_latency_ms
stt_text
expected_intent
predicted_intent
action_success
attempt_number
user_visible_success
```

Preferred additional fields:

```text
room_noise_condition
distance_condition
shadow_model_max_scores
shadow_model_triggered
moe_combo_triggered
pipeline_timestamps
```

Pipeline timestamps for demo tasks:

```text
t0 audio/trial start
t1 wake detected
t2 command recording start
t3 command recording end
t4 STT result
t5 intent result
t6 bulb API/action sent
t7 visible/confirmed state change
```

## Analysis outputs

From the same sessions, produce:

1. **Wake-word recall** on real users for all shadowed models.
2. **Hard-negative FPR** on real user voices.
3. **End-to-end demo task success** for the active system.
4. **Latency breakdown**: wake, STT, intent/action, total.
5. **Natural command corpus**: common Estonian phrasings for smart-light control.
6. **Trade-off table** combining user-test recall, hard-negative FPR, and Android field FAPH.

Example final table:

| Model | User-test recall | Hard-neg FPR | Android field FAPH | Role |
|---|---:|---:|---:|---|
| `v16c` | TBD | TBD | 4.06 | stable baseline / active-demo candidate |
| `expert-a` | TBD | TBD | 2.79 | field/recall reference |
| `expert-a+b2` | TBD | TBD | TBD | historical consensus milestone |
| `v6-residual` | TBD | TBD | 0.58 | conservative baseline |
| `v10` | TBD | TBD | 3.08 | fallback baseline |

## Methodological guardrails

- Keep **wake-word metrics** separate from **full-demo UX metrics**.
- Do not treat a bulb failure as a wake-word failure unless the wake stage failed.
- Freeze primary candidate list before final analysis.
- Report threshold sweeps as exploratory unless thresholds were fixed beforehand.
- Audio storage must follow participant consent level.
- If audio consent is missing, retain only anonymized metrics/logs.

## Recommended active-model setup

Simple version:

```text
Active: v16c
Shadow/offline: expert-a, expert-b2, v10, v6-residual, v15
```

Stronger UX A/B version:

```text
Half participants active = v16c
Half participants active = expert-a
Shadow/offline for all participants = same model set
```

Use the simple version for pilot. Move to counterbalanced A/B only if setup is stable.
