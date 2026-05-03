# High-yield 10-minute user test plan

> **Merged / superseded (2026-04-29):** current protocol is `docs/user-testing/ten-minute-shadow-demo-protocol.md`. Keep this file as an earlier planning note.

Purpose: compress one participant session into a short, engaging smart-home demo while extracting maximum evidence for wake-word evaluation, UX, command handling, and future offline model comparison.

## Core idea

Each participant interacts with **one active system**, but the same timestamped audio is also evaluated by multiple **shadow models** offline/live.

This separates:

- user-visible UX: one stable demo system
- model comparison: many models on the exact same audio
- future analysis: threshold sweeps and MoE combinations via replay

## Recommended active/shadow setup

### Simple final setup

- **Active model:** `v16c`
- **Shadow models:** `expert-a`, `expert-b2`, `v10`, `v6-residual`, `v15`
- **Offline combinations:**
  - `expert-a + expert-b2`
  - `v16c + expert-b2`
  - `expert-a + v16c`

### Optional A/B UX setup

If logistics allow:

- 50% participants: active `v16c`
- 50% participants: active `expert-a`
- shadow/replay models stay identical for all participants

## 10-minute session structure

| Time | Block | Purpose |
|---:|---|---|
| 0:00–1:00 | Consent + minimal metadata | ethics, participant context |
| 1:00–2:30 | 5 positive wake trials | clean wake recall |
| 2:30–3:30 | 5 hard negatives | confusable phrase rejection |
| 3:30–7:30 | 6 smart-bulb commands | end-to-end demo + command success |
| 7:30–9:00 | 1 free-form task | natural Estonian command phrasing |
| 9:00–10:00 | 4 ratings + 1 comment | subjective UX |

## Participant script

### 1. Positive wake trials

Participant says five times:

1. `Kuule Kratt`
2. `Kuule Kratt`
3. `Kuule Kratt`
4. `Kuule Kratt, pane tuli põlema`
5. `Kuule Kratt, muuda tuli siniseks`

### 2. Hard-negative trials

Participant reads:

1. `Kuule rott`
2. `Tere Kratt`
3. `Kratt kuule`
4. `Kuule robot`
5. `Kuule, kas sa kuuled?`

### 3. Scripted bulb commands

Participant controls one smart bulb:

1. `Kuule Kratt, pane tuli põlema.`
2. `Kuule Kratt, pane tuli punaseks.`
3. `Kuule Kratt, muuda tuli siniseks.`
4. `Kuule Kratt, vähenda heledust.`
5. `Kuule Kratt, pane tuli valgeks.`
6. `Kuule Kratt, pane tuli kustu.`

Rule: maximum **2 attempts per task**.

### 4. Free-form task

Prompt:

> Proovi nüüd oma sõnadega teha valgus selliseks, nagu tahaksid õhtul filmi vaadata.

Rule: maximum **2 command attempts**.

### 5. Mini questionnaire

Rate 1–5:

1. Süsteem reageeris piisavalt usaldusväärselt.
2. Süsteem reageeris piisavalt kiiresti.
3. Käskude sõnastamine tundus loomulik.
4. Kasutaksin sellist süsteemi kodus.

Open question:

- Mis oli kõige häirivam või üllatavam?

## Data yield

Per participant, approximately:

- 5 clean positive wake trials
- 5 hard-negative trials
- 6 scripted end-to-end command trials
- 1–2 natural free-form command trials
- 11–13 total positive wake-containing utterances
- subjective UX ratings

With 20 participants:

- ~220–260 positive wake-containing utterances
- 100 hard-negative utterances
- 120 scripted smart-home commands
- 20–40 natural Estonian smart-home commands

With 30 participants:

- ~330–390 positive wake-containing utterances
- 150 hard-negative utterances
- 180 scripted smart-home commands
- 30–60 natural commands

## Metrics to compute

### Wake-word metrics

- recall per model on positive trials
- hard-negative FPR per model
- latency to wake trigger
- threshold sweep per model, offline
- MoE/consensus recall and FPR, offline

### End-to-end demo metrics

For each smart-bulb command:

- wake detected: yes/no
- STT transcript correct enough: yes/no
- intent parsed correctly: yes/no
- bulb action succeeded: yes/no
- first-attempt success: yes/no
- success within 2 attempts: yes/no
- total latency

### UX metrics

- reliability rating
- speed rating
- naturalness rating
- willingness-to-use rating
- qualitative complaint/surprise

## Logging requirements

Minimum per trial:

```text
participant_id
trial_id
trial_type
expected_phrase_or_task
active_model
audio_file_or_timestamp_range
wake_detected_active
wake_latency_ms
stt_text
expected_intent
predicted_intent
action_success
attempt_number
user_visible_success
```

For shadow/replay analysis:

```text
model_name
max_score
triggered
trigger_time_ms
threshold
```

## Consent structure

Use two consent levels:

1. **Basic:** anonymous metrics and logs may be used in thesis.
2. **Audio opt-in:** audio clips may be stored and used for wake-word evaluation/model improvement.

Participants who decline audio storage can still contribute UX and aggregate metrics.

## Methodological notes

- Keep controlled wake-word metrics separate from full-demo UX metrics.
- Do not make the main model claim depend on STT/LLM/bulb success.
- Freeze the primary candidate list before final analysis.
- Treat threshold sweeps and extra MoE combinations as exploratory unless pre-registered.
- One smart bulb is intentional scope control: it keeps the E2E task understandable and repeatable.

## Thesis wording

A concise description:

> The user study was designed as a short high-information session. Each participant performed controlled wake-word trials, phonetically similar negative phrases, and smart-bulb control tasks. The participant interacted with one active system, while timestamped audio enabled multiple wake-word models and consensus combinations to be evaluated on the same input in shadow mode. This allowed user experience and model comparison to be separated while keeping participant burden low.
