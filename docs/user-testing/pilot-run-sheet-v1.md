# Kratt pilot user-test run sheet v1

**Status:** locked script for first real pilot participants, updated 2026-05-12.

Use one pseudonymous participant ID, for example `P01`. Do not write the participant's name into the session files.

## Before the participant starts

1. Start the recorder with the chosen participant ID:

   ```bash
   ./cli/kratt user-test P01 --active-model v16c --new-session-subdir --audio-consent yes
   ```

   If the participant chooses metrics-only consent, use `--audio-consent no`.

2. Read the consent summary:

   Tere! See on umbes 10-minutiline TalTechi bakalaureusetöö kasutajatest. Testime eestikeelset äratussõna "Kuule Kratt" ja ühe nutipirni hääljuhtimist. Palun ütled mõned etteantud fraasid, mõned sarnased fraasid, mis ei tohiks süsteemi käivitada, ja mõned lihtsad pirnikäsud. Lõpus on lühike küsimustik. Osalemine on vabatahtlik ja võid igal ajal katkestada.

3. Ask and record:

   - Kas lubad kasutada pseudonüümseid testitulemusi ja tehnilisi logisid lõputöös?
   - Kas lubad säilitada lühikesed märgendatud heliklipid äratussõna mudelite hindamiseks?

## Participant instructions

Say this before the first trial:

Räägi loomulikult, umbes nii nagu kodus nutiseadmega räägiksid. Kui süsteem ei reageeri, ära hakka ise kohe parandama; ma ütlen, kas proovime sama ülesannet teist korda. Sarnaste negatiivfraaside plokis ei pea süsteem reageerima. Vabas osas proovi toetatud võimekusi: valguse värv, heledus, efektid, olek, kellaaeg, kuupäev, ilm või lühike üldküsimus. Võid anda ka pooliku käsu ja vaadata, kas Kratt küsib täpsustust.

## Trial script

### A. Positive wake trials

Ask the participant to say:

1. Kuule Kratt
2. Kuule Kratt
3. Kuule Kratt
4. Kuule Kratt, pane tuli põlema
5. Kuule Kratt, muuda tuli siniseks

### B. Hard-negative trials

Say first:

Järgmised fraasid on meelega sarnased, aga need ei peaks süsteemi käivitama. Palun loe need loomulikult ette.

Ask the participant to say:

1. Kuule rott
2. Tere Kratt
3. Kratt kuule
4. Kuule robot
5. Kuule, kas sa kuuled?

### C. Scripted bulb commands

Say first:

Nüüd proovime kuut pirnikäsku. Iga ülesande jaoks on maksimaalselt kaks katset.

Ask the participant to complete:

1. Kuule Kratt, pane tuli põlema.
2. Kuule Kratt, pane tuli punaseks.
3. Kuule Kratt, muuda tuli siniseks.
4. Kuule Kratt, vähenda heledust.
5. Kuule Kratt, pane tuli valgeks.
6. Kuule Kratt, pane tuli kustu.

### D. Free-form exploration task

Say:

Nüüd on avastamise osa. Proovi ühte toetatud, aga loomulikult sõnastatud või veidi poolikut käsku. Hea siht on valgus: värv, heledus, efekt või olek. Näiteks: "tuba on liiga hele", "tee diskot", "vilguta roosalt", "mis värvi tuli on" või "pane tuli teist värvi" ja vasta Krati täpsustusele ilma uut äratussõna ütlemata. Võid küsida ka infot, näiteks "mis ilm homme Tartus on" või "mis päev kahe päeva pärast on", või ühe lühikese üldküsimuse. Taimerid, muusika, uksed ja muud seadmed ei ole selle demo võimekused.

Allow at most two attempts.

## Locked post-test questionnaire

Use `docs/user-testing/mini-questionnaire-form-v1.md`.

Required background:

1. Eesti keele tase: emakeel / C1-C2 / B1-B2 / A1-A2 / muu / ei soovi öelda.
2. Varasem häälassistendi kasutus: mitte kunagi / harva / iganädalaselt / iga päev.
3. Nutikodu kasutus: ei kasuta / aeg-ajalt / regulaarselt.

UMUX-Lite, scale **1 = ei nõustu üldse**, **7 = nõustun täielikult**:

4. Selle süsteemi võimekused vastavad mu nõudmistele.
5. Seda süsteemi on lihtne kasutada.

SEQ, scale **1 = väga raske**, **7 = väga lihtne**:

6. Kui lihtne oli Kratiga etteantud ülesandeid lõpule viia?

Kratt-specific diagnostics, scale **1 = üldse ei nõustu**, **5 = nõustun täielikult**:

7. Süsteem reageeris piisavalt usaldusväärselt.
8. Süsteem reageeris piisavalt kiiresti.
9. Käskude sõnastamine tundus loomulik.
10. Kasutaksin sellist süsteemi kodus.

Open comment:

11. Mis oli kõige häirivam või üllatavam?

## Immediately after the session

Validate the session before running the next participant:

```bash
./cli/kratt validate-user-test <session_dir>
```

If validation fails, mark the session as pilot/debug and do not use it in the main participant table without a clear note.
