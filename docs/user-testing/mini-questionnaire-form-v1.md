# Kratt mini questionnaire for 10-minute user test v1

**Status:** short form for `ten-minute-shadow-demo-protocol.md`. Use when participant burden must stay under ~1 minute. The longer question bank remains `questionnaire-v1.md`.

## Required fields

### Metadata

- `participant_id` — same pseudonymous ID as recorder session, e.g. `P01`.
- `session_id` — optional; copy from `session.json` if convenient.
- `date` — YYYY-MM-DD.

### Diagnostic ratings

Scale for all four: **1 = üldse ei nõustu**, **5 = nõustun täielikult**.

1. Süsteem reageeris piisavalt usaldusväärselt.
2. Süsteem reageeris piisavalt kiiresti.
3. Käskude sõnastamine tundus loomulik.
4. Kasutaksin sellist süsteemi kodus.

### Open comment

5. Mis oli kõige häirivam või üllatavam?

## Optional metadata if time allows

- Eesti keele tase: emakeel / C1-C2 / B1-B2 / A1-A2 / muu / ei soovi öelda.
- Varasem häälassistendi kasutus: mitte kunagi / harva / iganädalaselt / iga päev.
- Nutikodu kasutus: ei kasuta / aeg-ajalt / regulaarselt.

## Optional UMUX-Lite add-on

Use only if the form can keep the session short. Scale: **1 = ei nõustu üldse**, **7 = nõustun täielikult**.

- Selle süsteemi võimekused vastavad mu nõudmistele.
- Seda süsteemi on lihtne kasutada.

Scoring:

```text
UMUX-Lite normalized = ((mean(item1, item2) - 1) / 6) * 100
```

If these two items are not collected, do **not** report a UMUX-Lite score; report the four required diagnostic ratings separately instead.

## Reporting guidance

- For N≈20-30, report median + interquartile range for each rating.
- Treat the four required ratings as diagnostic project-specific feedback, not as a validated UX scale.
- Link subjective reliability to objective wake recall / task success, but do not merge them into one score.
