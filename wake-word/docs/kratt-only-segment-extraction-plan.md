# Kratt-only segment extraction plan

**Status:** active diagnostic side-branch state document; summarized in `docs/PROJECT_TODO.md` and `docs/research/source-of-truth-apr-2026.md` as of 2026-05-04.  
**Created:** 2026-05-03  
**Goal:** build an auditable, conservative pipeline for deriving single-word `Kratt` positive clips from existing clean `Kuule/Kule Kratt` audio, without introducing boundary-label noise.

> **Scope warning:** this is not the current user-test/demo target and not a replacement for exact two-word `Kuule/Kule Kratt` detection. Treat it as a diagnostic ablation unless a later explicit thesis decision promotes a different target policy.

## Why this exists

Recent experiments suggest that exact two-word `Kuule/Kule Kratt` detection may be asking too much from a tiny binary wake-word model: the model must learn the phrase, word order, prefix rejection, and confusable rejection at once. A controlled `Kratt`-only ablation tests whether the rare name `Kratt` is a better acoustic anchor.

This is risky because `Kratt` is only one syllable. Therefore the data pipeline must be stricter than previous positive generation: a bad cut can teach the model `ratt`, `le kratt`, or other boundary artifacts.

## Non-goals

- Do not train on user-test audio before final evaluation unless consent and train/test separation are explicit.
- Do not bulk-delete or overwrite existing data directories.
- Do not treat automatically cut clips as trusted until manual review has passed.
- Do not silently change the global target policy from `Kuule Kratt` to `Kratt`; this is an ablation unless explicitly promoted later.

## Target output

A generated dataset such as:

```text
wake-word/data/processed/positive_kratt_only_v19a/
├── manifest.jsonl
├── summary.json
├── accepted/*.wav
├── rejected/*.wav              # optional symlinks/copies for diagnostics
└── review/
    ├── random_sample/
    ├── low_confidence/
    ├── shortest/
    ├── longest/
    ├── possible_prefix_leak/
    ├── possible_clipped_onset/
    └── review.csv              # human labels: accept/reject/adjust
```

Each accepted clip should contain a clean single word `Kratt`, with enough pre-roll to preserve the /k/ closure/burst and enough post-roll to preserve the final /tː/, but without audible `kuule/kule` leakage.

## Candidate source policy v1

Start conservative:

- include only sources whose transcript/filename policy indicates standalone final-word `Kuule Kratt` or `Kule Kratt`;
- exclude SSML/XML, filler-prefix, reversed-order, command-tail, and full-sentence XTTS positives;
- prefer clean generated strict positives and real clips that were already audited;
- initially skip clips where `Kratt` is followed by a command tail, because they require both start and end boundary detection.

## Extractor design v1

The extractor should create candidate cuts and score confidence; it should not pretend to be perfect.

1. Load audio as mono 16 kHz.
2. Compute frame-level RMS/log-energy with a 10 ms hop.
3. Estimate coarse speech start/end.
4. Search for the `kuule/kule | kratt` boundary in the middle/back half of the speech region.
5. Prefer a local energy valley followed by a consonant burst/onset.
6. Add cautious pre-roll/post-roll, e.g. `60–90 ms` before boundary and `80–140 ms` after speech end.
7. Emit confidence and flags:
   - `too_short`, `too_long`
   - `low_boundary_confidence`
   - `no_energy_valley`
   - `fallback_ratio_used`
   - `possible_prefix_leak`
   - `possible_clipped_onset`
   - `speech_end_uncertain`
8. Build review folders from random samples and all suspicious clips.

Future fallback if energy/onset is insufficient: optional template/DTW matching from a few manually accepted `Kratt` templates.

## Manifest requirements

Each output row must include at least:

```json
{
  "source_file": "...",
  "source_sha256": "...",
  "output_file": "accepted/kratt_000123.wav",
  "source_duration_ms": 1040,
  "speech_start_ms": 120,
  "speech_end_ms": 1010,
  "boundary_ms": 610,
  "crop_start_ms": 540,
  "crop_end_ms": 1120,
  "crop_duration_ms": 580,
  "method": "energy_valley",
  "confidence": 0.87,
  "flags": [],
  "review_status": "pending"
}
```

## Manual review policy

Before training with the generated set:

- review all low-confidence clips;
- review all `possible_prefix_leak` and `possible_clipped_onset` clips;
- review the 20 shortest and 20 longest clips;
- review at least 50 random accepted clips, or 10% of accepted clips if the set is small;
- record decisions in `review/review.csv`.

Only clips marked accepted or not flagged after audit may be used for `v19-kratt-only` training.

## Evaluation implications

If `Kratt` becomes the ablation target, several old negative sets change meaning:

- `Kuule Kratt`, `Tere Kratt`, and `Kratt kuule` contain the target word and should trigger.
- New hard negatives must focus on `Kratt`-like but target-free words/phrases, e.g. `kurat`, `krt`, `kraam`, `kraan`, `kraad`, `krats`, `ratas`, `rattad`, `rattaga`, `rott`, `kaart`, `kart`.

The `v19-kratt-only` evaluation must therefore report a separate target policy and should not be mixed blindly with `Kuule Kratt` exact-phrase tables.

## TODO / state

### Planning and source inventory

- [x] Create this stateful plan document.
- [x] Inventory candidate source directories and count likely usable `Kuule/Kule Kratt` clips.
- [x] Decide the first conservative source allowlist for extractor smoke tests.
- [x] Define initial duration bounds for single-word `Kratt` cuts.

### Extractor implementation

- [x] Implement `wake-word/data/validation/extract_kratt_segments.py` with dry-run mode.
- [x] Add detailed JSONL manifest and summary output.
- [x] Add review-folder generation: random, low-confidence, shortest, longest, prefix-leak, clipped-onset.
- [x] Add safe defaults: no overwrite unless `--force`, no command-tail sources by default.
- [x] Add `--reject-flag` support so known-bad flagged cuts can go to `rejected/` instead of `accepted/`.
- [x] Add `--reject-index` support for manual review rejects from a specific extraction run.
- [x] Add CLI wrapper `cli/commands/kratt-extract-kratt-segments`.
- [x] Add review HTML index with browser audio controls.
- [x] Add keyboard review UI: `j/k` navigation, autoplay, `o` replay, `r/a/u` row marking, reject-index helper.
- [x] Add fast terminal reviewer for extraction outputs: `wake-word/data/validation/review_kratt_segments_terminal.py` and `kratt review-kratt-segments`.

### Validation and review

- [x] Run syntax checks / py_compile for the extractor.
- [x] Run a small smoke extraction on a limited source subset.
- [x] Inspect generated summary and flag distribution.
- [x] Manually listen to the first review batch.
- [x] Tune boundary/pre-roll/post-roll parameters if manual review finds systematic errors.
- [x] Record manual-review outcome in this document.

### Dataset and experiment handoff

- [x] Generate `positive_kratt_only_v19a` only after smoke review passes.
- [x] Manually review full `positive_kratt_only_v19a` review batch before training.
- [ ] Build a matching `Kratt`-like hard-negative set plan.
- [x] Add a dedicated `Kratt`-only training wrapper/dry-run path.
- [ ] Add the generated dataset to training manifests if used.
- [ ] Add `v19-kratt-only` entry to `wake-word/docs/MODEL_LINEAGE.md` only if a model is trained.
- [ ] Keep thesis/user-test priority gate: do not let this experiment displace critical writing/testing work.

## Current notes

- `Kratt`-only is promising because it removes the common prefix word `kuule/kule` from the acoustic target.
- Main risk: one-syllable target may be too short and may fire on `kurat`/`kraam`/`ratt-*`-like speech.
- Data quality is the critical path; fewer high-quality cuts are better than many questionable cuts.

## Inventory snapshot — 2026-05-03

Command used:

```bash
cd wake-word && uv run python - <<'PY'
# counted WAVs and filename candidates matching (kuule|kule).*kratt
PY
```

Conservative candidate counts:

| Source | WAVs | name candidates | duration notes | decision |
|---|---:|---:|---|---|
| `data/processed/positive_strict_kuule_kule` | 709 | 603 | 1.660–2.601s, median 2.020s | **first smoke-test allowlist** |
| `data/raw/neurokone_phase1` | 758 | 57 | 1.765–2.438s, median 1.997s | already represented through strict set; do not duplicate initially |
| `data/raw/neurokone_phase2` | 948 | 391 | 1.660–2.485s, median 1.997s | already represented through strict set; do not duplicate initially |
| `data/raw/kule_vs_kuule_test` | 8 | 8 | 1.776–2.090s | useful tiny sanity source; include only for smoke/review unless final policy says otherwise |
| `data/processed/positive_tts` | 956 | 956 | 1.660–2.786s, median 2.067s | broad historical TTS; skip first pass because strict set is cleaner |
| `data/raw/ode_kuule_kratt` | 11 | 11 | 2.000–3.500s | real recall/eval source; do **not** train on by default |
| `data/raw/friend1_20260414` | 145 | 0 by filename | no filename transcript match | keep as evaluation/warning set |
| `data/raw/mattias-short` | 362 | 0 by filename | no filename transcript match | skip until transcript/source policy is explicit |
| `data/raw/mattias` | 40 | 0 by filename | no filename transcript match | skip until transcript/source policy is explicit |

First extractor smoke-test allowlist:

```text
data/processed/positive_strict_kuule_kule
```

Optional tiny sanity add-on:

```text
data/raw/kule_vs_kuule_test
```

Initial single-word `Kratt` cut duration policy:

- hard reject/flag if `<0.30s` or `>1.20s`;
- suspicious if `<0.40s` or `>0.90s`;
- these are review gates, not final phonetic truth.

## Implementation snapshot — 2026-05-03

Implemented:

- `wake-word/data/validation/extract_kratt_segments.py`
- `cli/commands/kratt-extract-kratt-segments`

Core algorithm v1:

- loads mono 16 kHz audio;
- computes smoothed RMS/log-energy frames;
- estimates coarse speech start/end;
- searches the middle/back half of the speech span for an inter-word energy valley followed by an onset rise;
- cuts around the detected `Kratt` onset with pre-roll/post-roll;
- writes `manifest.jsonl`, `summary.json`, `accepted/*.wav`, review buckets, `review/review.csv`, and `review/index.html`.

Validation commands run:

```bash
bash -n cli/commands/kratt-extract-kratt-segments
cd wake-word && uv run python -m py_compile data/validation/extract_kratt_segments.py
./cli/kratt extract-kratt-segments --sample 25 \
  --output-dir wake-word/data/processed/positive_kratt_only_smoke_25 \
  --force
./cli/kratt extract-kratt-segments \
  --output-dir wake-word/data/processed/positive_kratt_only_v19a_dryrun \
  --dry-run --force
```

Smoke output:

- `wake-word/data/processed/positive_kratt_only_smoke_25/`
- 25 source WAVs, 25 candidates, 0 errors;
- flags: `possible_clipped_onset=1`, `suspicious_short=3`;
- manual review entrypoint: `wake-word/data/processed/positive_kratt_only_smoke_25/review/index.html`.

Full dry-run on first allowlist:

- `wake-word/data/processed/positive_kratt_only_v19a_dryrun/`
- 603 source WAVs, 603 candidates, 0 errors;
- flags: `possible_clipped_onset=9`, `suspicious_short=40`;
- no audio cuts written because this was dry-run only.

Manual review outcome — 2026-05-03:

- User listened to the first smoke review batch.
- Correction: `suspicious_short` clips were **correctly flagged as too short**, not valid. I initially misread this; keep `suspicious_short` as a real review/reject signal.
- Remaining non-short clips were judged good.
- Requested tweak: cut slightly longer on both sides.
- Extractor defaults updated from `pre_roll_ms=80`, `post_roll_ms=120` to `pre_roll_ms=110`, `post_roll_ms=160`.
- Flag logic was corrected: high energy at crop start is not automatically `possible_clipped_onset`; clipped onset now means insufficient kept pre-roll.
- User review update: `suspicious_long` was a false flag; those cuts sounded fine. Extractor `suspicious_max_s` default raised from `0.90s` to `1.05s`.
- User review update: short/cutoff examples should be rejected. Confirmed manual rejects first included `index=477`, `index=492`, `index=523`.
- User review update: all `suspicious_short` cuts are only/mostly `tt` and should be rejected as a class.

Regenerated v2 smoke set:

```bash
./cli/kratt extract-kratt-segments --sample 25 \
  --output-dir wake-word/data/processed/positive_kratt_only_smoke_25_v2 \
  --force
```

Result: 25 candidates, 0 errors, no flags.

Full v2 dry-run:

```bash
./cli/kratt extract-kratt-segments \
  --output-dir wake-word/data/processed/positive_kratt_only_v19a_dryrun_v2 \
  --dry-run --force
```

Result: 603 candidates, 0 errors, flags: `suspicious_long=6`, `suspicious_short=1`.

Revised cutter to fix late `tt`-only cuts instead of rejecting all short clips:

- Added earlier-boundary search constraints: `search_max_fraction=0.66`, `boundary_target_fraction=0.50`, `min_boundary_tail_s=0.38`.
- Added `boundary_pre_roll_ms=30` so crop start is anchored near the detected inter-word boundary, not only the later onset.
- Added `desired_min_cut_s=0.60`; if a cut would be too short, the extractor extends the start earlier before flagging/rejecting.

Generated full candidate audio set with revised cutter:

```bash
./cli/kratt extract-kratt-segments \
  --output-dir wake-word/data/processed/positive_kratt_only_v19a \
  --force
```

Result: 603 accepted candidates, 0 rejected, 0 errors. Previously bad short examples now recut longer:

- `477`: 860 ms
- `492`: 670 ms
- `523`: 660 ms

Current flags are review-only diagnostics, not auto-rejects:

- `low_boundary_confidence=43`
- `no_energy_valley=41`
- `possible_prefix_leak=36`
- `fallback_ratio_used=2`

Review UI entrypoint:

```bash
open wake-word/data/processed/positive_kratt_only_v19a/review/index.html
```

Keyboard UI:

- `j` / down: next row and autoplay;
- `k` / up: previous row and autoplay;
- `o`, Enter, or Space: replay selected row;
- `r`: mark selected row as reject in the browser UI;
- `a`: mark selected row as accept;
- `u`: clear mark;
- reject-index helper textarea collects `--reject-index N` arguments for a later extractor rerun;
- browser marks now persist in localStorage for the same review page;
- `Copy reject args` copies the current reject list;
- `Download review CSV` exports browser marks to a CSV.

Important limitation: browser markings still do not automatically update repo files. To make labels visible to the agent, paste the copied reject args, provide the downloaded CSV path, or edit/save `review/review.csv`.

Manual review update — 2026-05-04:

- User reviewed diagnostic buckets with keyboard UI.
- Interpretation: low-boundary/low-confidence cuts were often still full `kuule kratt`, not clean `kratt`.
- Other rejected cuts sounded like prefix-leaked `e-kratt` / `a-kratt` rather than clean `kratt`.
- Browser reject export initially duplicated indices because the same index can appear in multiple buckets; UI fixed to deduplicate reject indices.
- Applied 52 unique manual reject indices:

```text
21 22 23 24 25 83 88 180 181 234 235 236 237 238 239 240 241 242 243 244 245 246 247 248 249 250 251 261 262 263 264 265 266 267 268 269 270 271 272 273 274 275 276 277 278 288 346 426 443 447 451 474
```

Regeneration command:

```bash
./cli/kratt extract-kratt-segments \
  --output-dir wake-word/data/processed/positive_kratt_only_v19a \
  --reject-index 21 --reject-index 22 --reject-index 23 --reject-index 24 --reject-index 25 \
  --reject-index 83 --reject-index 88 --reject-index 180 --reject-index 181 \
  --reject-index 234 --reject-index 235 --reject-index 236 --reject-index 237 --reject-index 238 \
  --reject-index 239 --reject-index 240 --reject-index 241 --reject-index 242 --reject-index 243 \
  --reject-index 244 --reject-index 245 --reject-index 246 --reject-index 247 --reject-index 248 \
  --reject-index 249 --reject-index 250 --reject-index 251 --reject-index 261 --reject-index 262 \
  --reject-index 263 --reject-index 264 --reject-index 265 --reject-index 266 --reject-index 267 \
  --reject-index 268 --reject-index 269 --reject-index 270 --reject-index 271 --reject-index 272 \
  --reject-index 273 --reject-index 274 --reject-index 275 --reject-index 276 --reject-index 277 \
  --reject-index 278 --reject-index 288 --reject-index 346 --reject-index 426 --reject-index 443 \
  --reject-index 447 --reject-index 451 --reject-index 474 \
  --force
```

Result: 551 accepted candidates, 52 rejected, 0 errors. After these rejects, review buckets are random/shortest/longest over remaining accepted clips only.

Final TTS-strict review update — 2026-05-04:

- User reported remaining accepted review batch is OK: zero additional rejects.
- `positive_kratt_only_v19a` has been marked reviewed.
- Final reviewed TTS-strict candidate counts: 551 accepted, 52 rejected, 0 errors.
- `wake-word/data/processed/positive_kratt_only_v19a/REVIEW_NOTES.md` records generation and review state.

Full positive-source probe — 2026-05-04:

User requested running the cutter over broader positive data to see behavior on real voices, not only TTS. Generated exploratory dataset:

```bash
./cli/kratt extract-kratt-segments \
  --source-dir wake-word/data/processed/positive_strict_kuule_kule \
  --source-dir wake-word/data/processed/positive \
  --source-dir wake-word/data/raw/ode_kuule_kratt \
  --source-dir wake-word/data/raw/friend1_20260414 \
  --source-dir wake-word/data/raw/mattias/positive \
  --include-pattern '.*' \
  --output-dir wake-word/data/processed/positive_kratt_only_all_positive_probe \
  --force
```

Result: 1971 candidates, 0 rejected, 0 errors. This is **exploratory only**, not a training source yet.

Source breakdown:

| Source group | Count | Notes |
|---|---:|---|
| `data/processed/positive/` | 1076 | real/Korvo positive set; many short/uncertain flags, needs review |
| `data/processed/positive_strict_kuule_kule` | 709 | strict generated source family |
| `data/raw/friend1_20260414` | 145 | real unseen-speaker eval/warning source; validation only unless split policy changes |
| `data/raw/mattias/positive` | 30 | real Mac positives; long/context risk |
| `data/raw/ode_kuule_kratt` | 11 | real eval source; validation only by default |

Review entrypoint:

```bash
open wake-word/data/processed/positive_kratt_only_all_positive_probe/review/index.html
```

Real-source review UI `k` navigation issue and k-guard probe — 2026-05-04:

- User reported something is wrong with `k` while reviewing the broad real-source probe.
- I initially interpreted this as the acoustic initial /k/ in `Kratt` and generated a useful but separate k-guard audio probe. User clarified the audio is fine; the actual issue was the keyboard `k` shortcut for moving upward being too slow for rapid review.
- Audio/cutter-side diagnosis from the initial interpretation: the broad `all_positive_probe` blindly included many already-short positive crops. `data/processed/positive` contains 1147 matched files under 1.0s in the broader real-source pool; some are as short as 100–380ms. The inter-word cutter cannot recover a clean initial /k/ if the source is already too short or already starts after the /k/ closure.
- Extractor updated with source-duration filters:
  - `--min-source-duration-s`
  - `--max-source-duration-s`
- Review UI source column now shows a repo-relative path, not only basename, so broad-source review is auditable.
- Review UI keyboard navigation optimized:
  - selected-row update no longer loops over every row on each keypress;
  - `scrollIntoView` now uses `nearest` instead of recentering every row;
  - j/k movement is instant while autoplay is debounced by 120ms, so holding `j` or `k` can skip quickly and only plays after movement settles;
  - keydown listener uses capture phase so shortcuts still work when browser focus is on an audio control.
- Generated a safer real-voice exploratory probe with short sources skipped and extra /k/-guard pre-roll:

```bash
./cli/kratt extract-kratt-segments \
  --source-dir wake-word/data/processed/positive \
  --source-dir wake-word/data/processed/positive_samples \
  --source-dir wake-word/data/raw/friend1_20260414 \
  --source-dir wake-word/data/raw/mattias/positive \
  --source-dir wake-word/data/raw/mattias-short/positive \
  --source-dir wake-word/data/raw/ode_kuule_kratt \
  --include-pattern '.*' \
  --exclude-pattern '^(albert|indrek|kalev|kylli|lee|liivika|luukas|mari|meelis|peeter|tambet|vesta)_' \
  --min-source-duration-s 1.0 \
  --boundary-pre-roll-ms 90 \
  --pre-roll-ms 160 \
  --desired-min-cut-s 0.70 \
  --output-dir wake-word/data/processed/positive_kratt_only_real_voice_probe_kguard \
  --force
```

Result: 1757 matched before duration filter, 1147 skipped as too short, 610 candidates, 0 rejected, 0 errors.

Review entrypoint:

```bash
open wake-word/data/processed/positive_kratt_only_real_voice_probe_kguard/review/index.html
```

Terminal reviewer implementation — 2026-05-04:

Browser review remained too laggy/annoying for rapid pass-through. Added:

- `wake-word/data/validation/review_kratt_segments_terminal.py`
- `cli/commands/kratt-review-kratt-segments`

Terminal workflow:

```bash
./cli/kratt review-kratt-segments \
  --dataset wake-word/data/processed/positive_kratt_only_real_voice_probe_kguard \
  --start-index 472
```

Keybindings:

- `j` / down: next;
- `k` / up: previous;
- `o` / space / Enter: replay current;
- `r`: mark reject and advance;
- `a`: mark accept and advance;
- `+` / `-`: raise/lower temporary preview gain;
- `u`: unmark;
- `g`: jump to source index;
- `s`: save;
- `q`: save and quit.

Terminal labels are persisted to:

- `review/terminal-labels.json`
- `review/terminal-review.csv`
- `review/reject-args.txt`

Terminal playback update:

- User reported terminal audio was too quiet.
- Reviewer now creates temporary normalized preview WAVs only for playback; dataset WAVs are not modified.
- Default preview boost: `--preview-gain-db 24` with target peak `--preview-target-peak 0.95`.
- If needed, start louder with e.g. `--preview-gain-db 36`, or adjust live with `+` / `-`.

Real-source probe review progress — 2026-05-04:

- User clarified audio itself was fine; issue was browser keyboard review speed.
- User reached about source index `00471` in browser review.
- User observation: extractor flags are mostly accurate; many flagged rows contain prefix leakage.
- Persisted 22 reject labels provided by user:

```text
75 107 116 118 140 147 148 253 254 255 303 319 380 457 465 481 486 506 524 528 569 605
```

Persist command used:

```bash
./cli/kratt review-kratt-segments \
  --dataset wake-word/data/processed/positive_kratt_only_real_voice_probe_kguard \
  --reject-index 75 --reject-index 107 --reject-index 116 --reject-index 118 \
  --reject-index 140 --reject-index 147 --reject-index 148 \
  --reject-index 253 --reject-index 254 --reject-index 255 \
  --reject-index 303 --reject-index 319 --reject-index 380 \
  --reject-index 457 --reject-index 465 --reject-index 481 \
  --reject-index 486 --reject-index 506 --reject-index 524 \
  --reject-index 528 --reject-index 569 --reject-index 605 \
  --export-only
```

Current terminal-label state for `positive_kratt_only_real_voice_probe_kguard`: 610 rows, 22 rejects, labels saved under `review/`.

Browser lazy-audio review update — 2026-05-04:

User preferred returning to browser review, but without loading all audio controls at once. Updated generated review HTML:

- no static `<audio src=...>` tags are emitted in the page;
- rows store only `data-audio-src` until needed;
- a sliding window mounts audio controls only around the selected row (`6` before, `10` after);
- moving with `j/k` unmounts audio outside the window;
- `all_by_index` bucket is now first, so sequential source-index review is possible;
- `g` jumps to a source index; URL hash also works, e.g. `index.html#472`;
- existing `review/terminal-labels.json` reject/accept labels are seeded as browser row classes when rebuilding review HTML.

Active page rebuilt and opened at source index `00472`:

```text
wake-word/data/processed/positive_kratt_only_real_voice_probe_kguard/review/index.html#472
```

Static HTML check for active page: 0 static `<audio>` tags; 1311 lazy rows with `data-audio-src`.

Finder review fallback — 2026-05-04:

The browser and terminal reviewers became unproductive for rapid listening. Created a Finder-friendly symlink view:

```text
wake-word/data/processed/positive_kratt_only_real_voice_probe_kguard/finder_review/
```

Folder counts:

- `00-continue-from-00472`: 131 remaining candidate clips after current rejects;
- `01-current-rejects`: 22 clips rejected so far;
- `02-all-accepted-candidates`: 588 candidate clips excluding current rejects;
- `03-flagged-prefix-leak`: 336 current non-rejected clips with `possible_prefix_leak`;
- `04-flagged-long`: 70 current non-rejected clips with `suspicious_long` or `too_long`;
- `05-clean-no-flags`: 40 current non-rejected clips with no flags.

This Finder folder contains symlinks only; original audio remains under `accepted/`.

Final real-source probe review — 2026-05-04:

User completed browser review and exported final reject args. Final labels applied to `positive_kratt_only_real_voice_probe_kguard`:

- Total reviewable cuts: 610
- Rejected: 465
- Accepted: 145

Accepted by source:

| Source | Accepted | Training policy |
|---|---:|---|
| `data/processed/positive_samples` | 79 | potentially useful real/device positives, but separate from clean core |
| `data/raw/friend1_20260414` | 37 | held-out/eval-style; do not train by default |
| `data/processed/positive` | 24 | Mattias mic processed; likely noisy/context-dependent, use cautiously |
| `data/raw/mattias/positive` | 3 | Mattias real; noisy/context risk |
| `data/raw/mattias-short/positive` | 2 | Mattias real; noisy/context risk |
| `data/raw/ode_kuule_kratt` | 0 | all rejected |

Persisted final labels:

- `wake-word/data/processed/positive_kratt_only_real_voice_probe_kguard/review/terminal-labels.json`
- `wake-word/data/processed/positive_kratt_only_real_voice_probe_kguard/review/terminal-review.csv`
- `wake-word/data/processed/positive_kratt_only_real_voice_probe_kguard/review/final-reject-args-2026-05-04.txt`

Created reviewed symlink dataset:

```text
wake-word/data/processed/positive_kratt_only_real_voice_probe_kguard_reviewed
```

This reviewed real-source set is **not** a default training source. Use it as probe/eval or selectively include only after explicit source/split policy.

Noisy real-positive source policy — 2026-05-04:

User noted that some Mattias real clips were recorded in a car and contain beeps/other non-speech noise. Decision: do **not** use such clips as core positive training data for `v19-kratt-only`.

Rationale:

- A positive clip should teach the acoustic target `Kratt`, not car beeps, cabin acoustics, or recording-session artifacts.
- If the same beep/noise consistently co-occurs with positive labels, a tiny KWS model may learn the context/noise as a shortcut.
- The thesis/home-assistant target environment is a home voice satellite, not an in-car assistant.
- Noisy positives can still be useful as a stress-test / robustness evaluation set, or later as carefully balanced augmentation only if matching noise-only negatives are present.

Current policy:

- `positive_kratt_only_v19a` remains the clean reviewed positive source candidate.
- `positive_kratt_only_real_voice_probe_kguard` remains exploratory/probe data, not a training source.
- Car/noisy Mattias clips should be treated as evaluation/stress-test material by default.
- Only clean real-speaker clips with no prominent non-speech artifacts should be considered for future training inclusion, and only after explicit train/eval split review.

Training readiness — 2026-05-04:

We can start a **preliminary** `v19-kratt-only` ablation from the clean core positives, but should not treat it as final until hard negatives are added.

Recommended first training source:

- positives: `wake-word/data/processed/positive_kratt_only_v19a/accepted` (551 reviewed clean cuts)
- do **not** include the full real-source reviewed probe by default;
- optional later real add-on: only non-held-out/non-noisy accepted cuts, after explicit policy.

Important: the existing `kratt train`/`submit_hpc_kuule_kratt.sh` path is still a `Kuule Kratt` two-word training path and always includes old base positive dirs unless adapted. Do **not** launch it unchanged for `Kratt`-only, or it will train the wrong target policy. Need a `Kratt`-only preset/wrapper first, plus data sync to HPC if training there.

Kratt-only training wrapper dry-run — 2026-05-04:

Implemented a separate training path so the old two-word `Kuule Kratt` preset is not reused accidentally:

- `wake-word/training/scripts/submit_hpc_kratt_only.sh`
- `cli/commands/kratt-train-kratt-only`

Dry-run command executed:

```bash
./cli/kratt train-kratt-only v19a-kratt-only --dry-run
```

Dry-run plan:

- job name: `kratt-only-v19a-kratt-only`
- target policy: single word `Kratt`; two-word exact phrase policy not used
- positive dir: `data/processed/positive_kratt_only_v19a/accepted`
- positive duration filter: 0.40–1.20s
- CV exclude words: `kratt` only (`kuule` remains ordinary negative speech)
- negative limit: 5000
- extra negative dirs: KORVO2 negative sets, MacBook segmented negatives, mined false accepts, optional MUSAN/Riigikogu if present
- held-out CV/FAPH exclusion preserved
- hard-negative feature set: disabled by default for first Kratt-only ablation to avoid old target-policy traps
- clip duration: 1000 ms
- training steps: `15000,5000`
- recall profile: on
- spec augment: on
- pointwise filters: `96,96,96,96`
- target minimization: 20

Actual submit status:

- Synced to HPC:
  - `cli/commands/kratt-train-kratt-only`
  - `wake-word/training/scripts/submit_hpc_kratt_only.sh`
  - `/gpfs/mariana/smbhome/malinh/kratt-data/processed/positive_kratt_only_v19a`
- Remote dataset count verified: 551 accepted, 52 rejected.
- First submit requested 8h on default `short` partition and became pending with `PartitionTimeLimit`; cancelled job `923300`.
- Submit script updated to default `PARTITION=common` and accept `--partition`.
- Running submit command:

```bash
./cli/kratt train-kratt-only v19a-kratt-only \
  --steps 15000,5000 \
  --time 08:00:00 \
  --partition common
```

Submitted SLURM job:

```text
job_id: 923301
partition: common
state at submit check: R on green30
log: /gpfs/mariana/smbhome/malinh/kratt-data/training/runs/logs/kratt-only-v19a-kratt-only-923301.out
```

Training completion — 2026-05-05:

```text
job_id: 923301
state: COMPLETED
elapsed: 03:54:42
run_dir: /gpfs/mariana/smbhome/malinh/kratt-data/training/runs/microwakeword-kratt-only-v19a-kratt-only-20260504-203253
```

Downloaded local model artifacts:

```text
wake-word/models/kuule-kratt-v19a-kratt-only/model.tflite
wake-word/models/kuule-kratt-v19a-kratt-only/kuule_kratt_v19a-kratt-only.tflite
wake-word/models/kuule-kratt-v19a-kratt-only/analysis/
wake-word/models/kuule-kratt-v19a-kratt-only/NOTES.md
```

Internal streaming TFLite eval:

| cutoff | FRR | FAPH |
|---:|---:|---:|
| 0.99 | 0.0435 | 2.0 |
| 1.00 | 1.0000 | 0.0 |

Build `Kratt`-like hard negatives (`kurat`, `kraam`, `kraan`, `kraad`, `krats`, `ratas`, `rattad`, etc.) before calling any resulting model final.

Context-aware positive dataset — 2026-05-06:

After live/manual analysis of `v19a-kratt-only`, we identified a likely windowing shortcut: v19a positives were isolated `Kratt` cuts shorter than 1s, and microWakeWord left-padded short positives to the 1000ms training window. This can teach `[silence] + Kratt` rather than `Kratt` in natural phrase context.

Implemented a context-aware dataset builder:

- `wake-word/data/validation/build_kratt_context_dataset.py`
- `cli/commands/kratt-build-kratt-context`

Generated local dataset:

```text
wake-word/data/processed/positive_kratt_context_v19b
```

Counts / policy:

- source: `positive_strict_kuule_kule` clean generated positives;
- source WAVs: 709;
- output clips: 2836 fixed 1000ms WAVs;
- four variants per source with `Kratt` target offsets 40/160/280/400ms from crop start;
- prefix variants included from filenames: `kule` 113, `kuule` 384, `kuulee` 106, `kuuule` 106;
- all output clips are exactly 1.0s, so the normal 1000ms Kratt-only training path should not introduce new left padding;
- review symlink samples are under `positive_kratt_context_v19b/review/`.

Dry-run command for a possible later training run:

```bash
./cli/kratt train-kratt-only v19b-context \
  --positive-dir data/processed/positive_kratt_context_v19b/accepted \
  --clip-duration-ms 1000 \
  --dry-run
```

Do not submit this as a new training run unless user testing/writing budget is explicitly protected. If trained later, keep it a `Kratt`-only target-policy ablation and pair it with target-free `Kratt`-like hard negatives before making quality claims.
