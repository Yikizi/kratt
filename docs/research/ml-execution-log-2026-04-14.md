# ML Execution Log — 2026-04-14

Praktiline töölogi tänaste muudatuste ja jooksude kohta.

## 1. microWakeWord recall-run

Muudetud failid:
- `wake-word/training/configs/microwakeword-kratt.yaml`
- `wake-word/training/scripts/train_microwakeword_experiment.sh`
- `wake-word/training/scripts/submit_hpc_kuule_kratt.sh`

Tehtud:
- lisatud `--recall-profile`
- vaikimisi recall-run profiil:
  - `training_steps=[15000, 5000]`
  - `learning_rates=[0.001, 0.0001]`
  - `negative_class_weight=[5, 5]`
  - residual ON
- VTLP parameetrid toodud CLI-sse:
  - `--vtlp-prob`
  - `--vtlp-alpha-min`
  - `--vtlp-alpha-max`
- mmap cache stamp sisaldab nüüd ka recall-run profiili ja VTLP parameetreid

Kontroll:
- `bash -n wake-word/training/scripts/train_microwakeword_experiment.sh`
- `bash -n wake-word/training/scripts/submit_hpc_kuule_kratt.sh`

Soovitatud jooks:
- `./wake-word/training/scripts/submit_hpc_kuule_kratt.sh --tag recall-r1 --dataset-preset v6-plus --recall-profile`

## 2. openWakeWord HPC path

Muudetud failid:
- `wake-word/training/scripts/train_openwakeword.py`
- `wake-word/training/scripts/submit_hpc_openwakeword.sh`
- `wake-word/training/configs/openwakeword-kuule-kratt.yaml`

Tehtud:
- lisatud `--preflight-only`
- rangem data/config validation
- stale feature cache eemaldamine vaikimisi enne rerun'i
- resource lipud:
  - `--partition`
  - `--time`
  - `--mem`
  - `--gres`
  - `--reuse-features`

Kontroll:
- `python3 -m py_compile wake-word/training/scripts/train_openwakeword.py`
- `bash -n wake-word/training/scripts/submit_hpc_openwakeword.sh`

Staatus:
- lokaalselt `sbatch` puudub
- submit käivitati üle SSH login-node'ile:
  - `ssh malinh@base.hpc.taltech.ee 'cd ~/kratt && bash wake-word/training/scripts/submit_hpc_openwakeword.sh --tag oww-r1'`

## 3. Android capture auto-labeling

Muudetud fail:
- `wake-word/evaluation/stt_label_captures.py`

Tehtud:
- lisatud optional Silero VAD
- STT jookseb eelistatult VAD speech envelope'i peal
- proposal JSONL sisaldab nüüd:
  - `speech_ratio`
  - `speech_duration_s`
  - `vad_segments`
  - `stt_source`
  - Android `index.jsonl` metadata

Kontroll:
- `python3 -m py_compile wake-word/evaluation/stt_label_captures.py`
- 5-klipine smoke test läks läbi

Täisjooks:
- `wake-word/.venv/bin/python wake-word/evaluation/stt_label_captures.py --input output/android-captures-20260414-1115 output/android-captures-20260414-2014 --out wake-word/data/processed/_labeling/android_capture_proposals.jsonl`

Vahepealne seis:
- proposal failis oli kontrolli hetkel `3840` kirjet
- jooks leidis nii `positive`, `hard_negative` kui `garbage` juhtumeid

## 4. XTTS recall-set expansion

Muudetud failid:
- `wake-word/data/collection/generate_xtts_clones.py`
- `wake-word/data/collection/resume_xtts_clones.py`

Tehtud:
- lisatud `--positive-target`
- lisatud `--seed`
- lisatud `generation_manifest.json`
- jooksud on resumable/idempotent

Smoke test:
- `isa`: OK
- `ode`: OK

Täisjooksud:
- `wake-word/.venv/bin/python wake-word/data/collection/generate_xtts_clones.py --name isa --ref-dir wake-word/data/raw/voice_references/isa --output wake-word/data/raw/xtts_clones/isa --positive-target 200 --skip-negatives --delay 0.2`
- `wake-word/.venv/bin/python wake-word/data/collection/generate_xtts_clones.py --name ode --ref-dir wake-word/data/raw/voice_references/ode --output wake-word/data/raw/xtts_clones/ode --positive-target 200 --skip-negatives --delay 0.2`

Vahepealne seis kontrolli hetkel:
- `isa`: 25 uut target-skeemi faili nähtaval
- `ode`: 26 uut target-skeemi faili nähtaval

## 5. Garbage label logic

Praegune loogika `stt_label_captures.py` sees:
- kui VAD järgi speech ratio on alla `--min-speech-ratio` piiri, läheb klipp `garbage`
- vaikimisi piir: `0.12`
- samuti kui speech duration on alla `--min-speech-ms`, läheb klipp `garbage`
- vaikimisi piir: `250 ms`

Oluline:
- `garbage` ei tähenda "mudel ei triggerdanud"
- `garbage` tähendab "triggerdatud klipp ei sisalda piisavalt kasulikku kõnelaadset sisu, et sellest recall/hard-negative andmestikku ehitada"
- näited:
  - vaikus
  - mehaaniline heli
  - väga lühike kõnejupp
  - ebastabiilne VAD-jääk ilma sisuka transkriptita

