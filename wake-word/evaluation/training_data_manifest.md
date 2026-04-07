# Training data manifest per model version

This document records EXACTLY what each model version was trained on.
Source: `processed/experiments/kuule_kratt_v*/manifest.json` on HPC.
A test set is considered TRULY HELD-OUT for a model only if it shares
zero files with this model's training pool.

All models use:
- `seed=42`, `test_split=0.15` (positives only)
- `negative_limit=5000` (CV ET clips)
- exclude_words = `["kratt", "kuule"]`

## Positives

| Ver | Source dirs | pos_train | pos_test (held out) |
|-----|-------------|-----------|---------------------|
| v1  | mic1+mic2                                      | 915  | 161 |
| v2  | mic1+mic2                                      | 915  | 161 |
| v3  | mic1+mic2                                      | 915  | 161 |
| v4  | mic1+mic2                                      | 915  | 161 |
| v5  | mic1+mic2 + positive_tts                       | 2241 | 395 |
| v6  | mic1+mic2 + positive_tts                       | 2241 | 395 |
| v7  | mic1+mic2 + positive_tts + positive_tts_ssml   | 3067 | 541 |
| v8  | mic1+mic2 + positive_tts + positive_tts_ssml + raw/mattias/positive + augmented/positive_mattias_mac + xtts_clones/{marta,annam,ema}/positive | 3343 | 589 |

**IMPORTANT**: Because the file LIST passed to `random.shuffle(seed=42)` differs per
model (different sources combined), the held-out 15% set is **DIFFERENT for each
model**. Each model's `test_positive_samples` dir is its own canonical hold-out.

## Negatives (NO train/test split — all of these were trained on)

| Ver | CV ET | KORVO-2 | KORVO-2 extra | KORVO-2 sess2 | TTS hard | TTS hard v2 | XTTS hard (sep set) | Mac hard (sep set) | Total |
|-----|-------|---------|---------------|---------------|----------|-------------|---------------------|---------------------|-------|
| v1  | 3928  | 0       | 0             | 0             | 0        | 0           | 0                   | 0                   | 3928  |
| v2  | 3928  | 0       | 0             | 0             | 0        | 0           | 0                   | 0                   | 3928  |
| v3  | 3928  | 109     | 0             | 0             | 0        | 0           | 0                   | 0                   | 4037  |
| v4  | 3928  | 109     | 1311          | 0             | 0        | 0           | 0                   | 0                   | 5348  |
| v5  | 3928  | 109     | 1311          | 0             | 1644     | 0           | 0                   | 0                   | 6992  |
| v6  | 3928  | 109     | 1311          | 3345          | 1644     | 0           | 0                   | 0                   | 10337 |
| v7  | 3928  | 109     | 1311          | 3345          | 1644     | 6090        | 0                   | 0                   | 16427 |
| v8  | 3928  | 109     | 1311          | 3345          | 0        | 0           | 180                 | 300                 | 9173  |

**v8 details:**
- Removed `negative_tts_hard` and `negative_tts_hard_v2` from main negative pool
- Added 480 clips in a SEPARATE `hard_negative` feature set with penalty_weight=3.0:
  - `augmented/hard_neg_mattias_mac_train` (300 clips, real Mac voice augmented)
  - `xtts_clones/marta/negative` (60), `annam/negative` (60), `ema/negative` (60)
- Held out from training: 15 Mac hard neg + 60 Isa XTTS hard neg

## Ambient (no train/test split)

| Ver | MUSAN noise | KORVO-2 ambient | Total |
|-----|-------------|-----------------|-------|
| v1-v2 | 930 | 0  | 930  |
| v3+   | 930 | 72 | 1002 |

## Implications for evaluation

A test set is **truly held out** for a model only if it contains files
that this model's training pool does NOT include.

### Truly held out for ALL models (v1-v8)

| Test set | Source | What it tests |
|---|---|---|
| `pos_test_isa_xtts` | data/processed/test_pos_xtts_isa (48) | Recall on unseen male speaker (XTTS clone) |
| `hard_neg_test_mac` | data/processed/hard_neg_test (15) | FPR on real recorded hard negatives (held out from v8) |
| `hard_neg_test_isa` | data/processed/test_hard_neg_xtts_isa (60) | FPR on unseen-speaker XTTS hard negatives |
| `faph_cv_et` | data/processed/faph_test_cv_et (2000, 3.65h) | FAPH on unseen Estonian speech (CV ET clips 5000-7000) |

### Held out for SOME models

| Test set | Held out for | Trained on by |
|---|---|---|
| `pos_test_mac_mattias` (Mac mic, real voice) | v1-v7 | v8 |
| `hard_neg_test_mac` (Mac voice augmented) | v1-v7 | NONE in training (always test) |

### Not yet available — needs new collection

| Test set | Source | Status |
|---|---|---|
| `neg_test_korvo2` (held-out KORVO-2 speech) | new recording session, never in training | **TODO**: user records ~30 min |
| `pos_test_mattias_korvo2_canonical` | files outside ALL models' training shuffles | derived from intersection of held-out sets across models |

## Notes

- The Mattias mic1+mic2 positive recordings are **all in training** for at least
  some portion (since seed=42 differs per version). For an honest cross-version
  recall comparison, we use `pos_test_isa_xtts` which is guaranteed unseen everywhere.
- The CV ET 3928 clips (after exclusion of "kratt"/"kuule" sentences) are the
  same set in every model. Clips beyond #5000 (in the same shuffle) are unseen.
