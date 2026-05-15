# Kratt Google Forms build sheet v1

**Status:** locked collection form spec for first pilot participants, 2026-05-07. Exploration cue added 2026-05-12; rating question wording unchanged. Build the Google Form from this sheet and keep question wording unchanged unless a pilot failure forces a documented revision.

Use Google Forms for participant answers. Keep `docs/user-testing/mini-questionnaire-form-v1.md` as the source-of-truth wording and thesis/reporting note.

## Form settings

- Title: `Kratt kasutajatesti tagasiside`
- Description: `TalTechi bakalaureusetöö kasutajatest. Vastused salvestatakse pseudonüümse osaleja ID-ga. Ära sisesta nime ega muid otseseid isikuandmeid. Kratt juhib selles demos ühte WiZ lampi ning oskab kõrvalt kellaaega, kuupäeva, ilma ja lühikesi üldküsimusi abimudeli kaudu. Proovi toetatud piire: värvid, heledus, efektid, tule olek, homne ilm teises linnas või poolik käsk nagu "pane tuli teist värvi". Taimerid, muusika, uksed ja muud seadmed ei ole selle demo võimekused.`
- Collect email addresses: off
- Limit to 1 response: off
- Allow response editing: off
- Show progress bar: on
- Make every question below required except the final open comment.

## Section 1 - Session

1. `participant_id`
   - Type: short answer
   - Required: yes
   - Help text: `Sama ID, mida kasutatakse salvestussessioonis, nt P01. Ära sisesta nime.`

2. `session_id`
   - Type: short answer
   - Required: yes for pilot if available
   - Help text: `Kopeeri session.json või operaatori lehelt. Kui seda veel ei tea, kirjuta "unknown".`

3. `consent_level`
   - Type: multiple choice
   - Required: yes
   - Options:
     - `metrics only`
     - `audio opt-in`

## Section 2 - Background

4. `estonian_level`
   - Type: multiple choice
   - Required: yes
   - Options:
     - `emakeel`
     - `C1-C2`
     - `B1-B2`
     - `A1-A2`
     - `muu`
     - `ei soovi öelda`

5. `voice_assistant_use`
   - Type: multiple choice
   - Required: yes
   - Options:
     - `mitte kunagi`
     - `harva`
     - `iganädalaselt`
     - `iga päev`

6. `smart_home_use`
   - Type: multiple choice
   - Required: yes
   - Options:
     - `ei kasuta`
     - `aeg-ajalt`
     - `regulaarselt`

## Section 3 - UMUX-Lite

Scale for both questions:

- Type: linear scale
- Range: 1 to 7
- Left label: `ei nõustu üldse`
- Right label: `nõustun täielikult`
- Required: yes

7. `umux_capabilities`
   - Question: `Selle süsteemi võimekused vastavad mu nõudmistele.`

8. `umux_easy`
   - Question: `Seda süsteemi on lihtne kasutada.`

## Section 4 - Single Ease Question

9. `seq_task_ease`
   - Type: linear scale
   - Range: 1 to 7
   - Left label: `väga raske`
   - Right label: `väga lihtne`
   - Required: yes
   - Question: `Kui lihtne oli Kratiga etteantud ülesandeid lõpule viia?`

## Section 5 - Kratt diagnostics

Scale for all four questions:

- Type: linear scale
- Range: 1 to 5
- Left label: `üldse ei nõustu`
- Right label: `nõustun täielikult`
- Required: yes

10. `diag_reliable`
    - Question: `Süsteem reageeris piisavalt usaldusväärselt.`

11. `diag_fast`
    - Question: `Süsteem reageeris piisavalt kiiresti.`

12. `diag_natural_commands`
    - Question: `Käskude sõnastamine tundus loomulik.`

13. `diag_home_use`
    - Question: `Kasutaksin sellist süsteemi kodus.`

## Section 6 - Open comment

14. `open_surprising_or_annoying`
    - Type: paragraph
    - Required: no
    - Question: `Mis oli kõige häirivam või üllatavam?`

## Response export

After the first pilot, export responses to CSV and store a copy under a local, non-public analysis path before thesis aggregation. Do not commit raw participant response exports unless they have been anonymized and explicitly prepared as thesis artifacts.
