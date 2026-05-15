# Kratt locked mini questionnaire for pilot user test v1

**Status:** locked pilot rating items for the first real participant runs, 2026-05-07. Exploration cue added 2026-05-12; core question wording unchanged. Use this form for every pilot participant unless a pilot failure forces a documented change.

**Purpose:** collect one comparable short usability score plus Kratt-specific diagnostic feedback. The UMUX-Lite and SEQ items are the defensible comparable measures; the Kratt-specific ratings are reported separately and are not a validated combined scale.

## Participant-facing exploration cue

Use this as a short intro before the free-form part of the demo, or as the first text on the questionnaire:

> Kratt juhib selles demos ühte WiZ lampi ja oskab kõrvalt väikseid infopäringuid. Proovi toetatud piire: pane tuli põlema või kustu; muuda värvi (sinine, punane, roosa, soe valge, külm valge, neutraalne); ütle heleduse kohta loomulikult "liiga hele", "tee hämaramaks" või "tee valgemaks"; proovi efekte "tee diskot", "käi värvid läbi" või "vilguta roosalt"; küsi tule olekut, kellaaega, kuupäeva või ilma teise päeva ja linna kohta (nt "mis ilm homme Tartus on?"). Üks hea test on anda poolik käsk "pane tuli teist värvi" ja vaadata, kas Kratt küsib täpsustust. Soovi korral küsi ka lühike üldküsimus, näiteks retsepti või nõu, see läheb abimudelile ja võib olla aeglasem. Taimerid, muusika, uksed ja muud seadmed ei ole selles demos toetatud.

## Required fields

### Metadata

- `participant_id` — same pseudonymous ID as recorder session, e.g. `P01`.
- `date` — YYYY-MM-DD.
- `session_id` — copy from `session.json` if convenient.
- nõusoleku tase — ainult mõõdikud / mõõdikud + helisalvestis.

### Background

- Eesti keele tase: emakeel / C1-C2 / B1-B2 / A1-A2 / muu / ei soovi öelda.
- Varasem häälassistendi kasutus: mitte kunagi / harva / iganädalaselt / iga päev.
- Nutikodu kasutus: ei kasuta / aeg-ajalt / regulaarselt.

### UMUX-Lite usability items

Scale for both: **1 = ei nõustu üldse**, **7 = nõustun täielikult**.

1. Selle süsteemi võimekused vastavad mu nõudmistele.
2. Seda süsteemi on lihtne kasutada.

Scoring:

```text
UMUX-Lite normalized = ((mean(item1, item2) - 1) / 6) * 100
```

### Single Ease Question

Scale: **1 = väga raske**, **7 = väga lihtne**.

3. Kui lihtne oli Kratiga etteantud ülesandeid lõpule viia?

### Diagnostic ratings

Scale for all four: **1 = üldse ei nõustu**, **5 = nõustun täielikult**.

4. Süsteem reageeris piisavalt usaldusväärselt.
5. Süsteem reageeris piisavalt kiiresti.
6. Käskude sõnastamine tundus loomulik.
7. Kasutaksin sellist süsteemi kodus.

### Open comment

8. Mis oli kõige häirivam või üllatavam?

## Reporting guidance

- Report UMUX-Lite as the comparable short usability measure.
- Report SEQ as the post-task ease measure.
- For N≈10 pilot participants, report median + interquartile range for each item; for smaller N, treat the values as descriptive pilot evidence.
- Treat the four Kratt-specific ratings as diagnostic project-specific feedback, not as a validated UX scale.
- Link subjective reliability to objective wake recall / task success, but do not merge them into one score.
