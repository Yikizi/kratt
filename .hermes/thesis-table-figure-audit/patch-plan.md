# Thesis table/figure readability patch plan

Planning only. No thesis source edits were applied in this audit.

## Inputs inspected

- LaTeX source: `docs/thesis/thesis-tex-estonian/main.tex`, `thesis.sty`, `chapters/second_chapter.tex`, `chapters/third_chapter.tex`
- Build log: `docs/thesis/thesis-tex-estonian/main.log`
- Current figures: `docs/thesis/thesis-tex-estonian/figures/{faph_recall_pareto.pdf,det_v6_v15_v16c_expertA.pdf}`
- Existing figure/evaluation artifacts: `wake-word/evaluation/generate_thesis_figures.py`, `wake-word/evaluation/benchmark_*.csv`, `docs/research/artifacts/wake-word-evaluation-2026-04/`

## Main problems found

### Log-driven overfull table issues

`main.log` reports the largest table-related overfull boxes in `chapters/second_chapter.tex`:

| Log lines | Source lines | Likely object | Issue |
|---:|---:|---|---|
| 2362 | 249--257 | Table `tab:cross-language-faph` | Long corpus label in fixed `l` column. |
| 2367 | 313--322 | Table `tab:expert-individual` | Long model/header text in fixed columns. |
| 2382 | 405--413 | Table `tab:residual-ablation` | Many long headers across 7 columns. |
| 2387 | 430--440 | Table `tab:specaug-ablation` | Many long headers across 6 columns. |
| 2398 | 477--489 | Table `tab:positive-pollution` | Long directory paths in fixed `l` columns. |

### Tables hidden by `\resizebox`

These do not show as overfull, but readability is poor because the table is squeezed to fit:

- `tab:fair-comparison-holdout` around lines 173--204
- `tab:v18-family-results` around lines 530--551
- `tab:checkpoint-headline` around lines 595--614
- `tab:checkpoint-consensus` around lines 629--647

These should be split into two readable panels instead of scaled.

### Captions/list entries

`main.lot`/`main.lof` contain very long entries for Tables 4, 7, 11, 12, 13 and Figure 1. Use optional short captions and move repeated Wilson/Poisson details into table notes or nearby prose.

## Patch principles

1. Do **not** scale tables with `\resizebox{\textwidth}{!}{...}`.
2. Use `tabularx`, `p{}`/`X` columns, and multiline headers.
3. Prefer `\small` or default table size; avoid `\scriptsize` except as a last resort.
4. Keep one caption/label per logical table so existing references remain stable.
5. Avoid landscape for now. Splitting wide tables into stacked panels should be enough; `pdflscape` is easy but should be last resort.
6. Add short optional captions for LoT/LoF, but keep body captions/notes readable.

## Shared LaTeX support changes

File: `docs/thesis/thesis-tex-estonian/thesis.sty`

Add to the table package block:

```tex
\usepackage{array}
\usepackage{tabularx}
\usepackage{makecell}
\usepackage{ragged2e}
\newcolumntype{Y}{>{\RaggedRight\arraybackslash}X}
\newcolumntype{C}{>{\Centering\arraybackslash}X}
\newcolumntype{R}{>{\RaggedLeft\arraybackslash}X}
```

Also fix the table font hook so it actually selects the requested font:

```tex
\AtBeginEnvironment{table}{\fontsize{11}{12}\selectfont}
```

Keep `longtable` support unchanged.

## Table-by-table patch plan

File for all table body changes: `docs/thesis/thesis-tex-estonian/chapters/second_chapter.tex`

### 1. Tables that are already acceptable

Leave these alone except optional short captions if desired:

- `tab:model-versions`
- `tab:fair-comparison`
- `tab:full-comparison`

### 2. `tab:fair-comparison-holdout` — split the resized table into two stacked panels

Current issue: `\scriptsize + \resizebox` around a 9-column table with long CI values.

Patch shape:

- Keep the existing `table` environment and label `tab:fair-comparison-holdout`.
- Remove `\resizebox` and the single 9-column `tabular`.
- Use two `tabularx` blocks inside the same table:
  1. Recall panel: `Mudel`, `Kõneleja A XTTS (N=48)`, `Mac mic (N=30)`.
  2. False-accept/FAPH panel: `Mudel`, `HN Mac`, `HN Kõneleja A`, `FAPH CV`.
- Use `\small`, `\setlength{\tabcolsep}{3pt}`, and multiline headers via `\makecell`.
- Add optional short caption, e.g.

```tex
\caption[Kõrvalejäetud komplektide võrdlus v1--v8]{...full caption...}
```

This preserves all current references to `tab:fair-comparison-holdout`.

### 3. `tab:cross-language-faph` — replace fixed first column with wrapping column

Current issue: overfull 79 pt from `Common Voice ET (kõrvalejäetud, 3,65 h toorheli + klipivahed)`.

Patch shape:

```tex
\begin{tabularx}{\textwidth}{Y l r r l}
```

Move the long raw/streaming duration note to caption or note, and keep the first cell short:

```tex
Common Voice ET (kõrvalejäetud) & Eesti & 3,82 & 44,5 & \cite{commonvoice2020} \\
```

### 4. `tab:expert-individual` — wrap model column and headers

Current issue: overfull 107 pt from long model names and headers.

Patch shape:

```tex
\setlength{\tabcolsep}{3pt}
\begin{tabularx}{\textwidth}{Y r r r C C}
\textbf{Mudel} & \textbf{Maht} & \makecell{\textbf{FAPH}\\\textbf{CV}} & ...
```

Use `\makecell` for `Recall (Kõneleja B)` and `HN Mac`. Keep the explanatory footnote below the table.

### 5. `tab:expert-consensus` — keep body, shorten caption/LoT

Current body fits, but caption is too large and dominates `main.lot`.

Patch shape:

- Keep table body as-is unless final compile shows overfull.
- Add optional short caption.
- Move repeated Wilson/Poisson/u95 explanation into a `\begin{flushleft}\footnotesize \emph{Märkus.} ...\end{flushleft}` note below the table.

### 6. `tab:residual-ablation` — multiline headers, no scaling

Current issue: overfull 93 pt from 7 long headers.

Patch shape:

```tex
\setlength{\tabcolsep}{3pt}
\begin{tabularx}{\textwidth}{l c C C C C C}
\textbf{Mudel} & \textbf{Res.} & \makecell{\textbf{Rec}\\\textbf{Kõn. A}} & ...
```

Values are short, so header wrapping should fix this without splitting.

### 7. `tab:specaug-ablation` — multiline headers, no scaling

Current issue: overfull 104 pt from long headers.

Patch shape:

```tex
\setlength{\tabcolsep}{3pt}
\begin{tabularx}{\textwidth}{l C C C C C}
```

Use `\makecell` for all metric headers. Keep the delta row.

### 8. `tab:positive-pollution` — wrapping path columns and `\path{}`

Current issue: overfull 169 pt from directory paths.

Patch shape:

```tex
\small
\setlength{\tabcolsep}{3pt}
\begin{tabularx}{\textwidth}{>{\RaggedRight\arraybackslash}p{0.42\textwidth} Y r r}
```

Use `\path{...}` for directory names instead of `\texttt{...}` where possible, e.g.

```tex
\path{raw/xtts_clones/{speaker_x1,speaker_x2,speaker_x3}/positive_16k}
```

`hyperref` already loads URL/path support, so this is safe.

### 9. `tab:v18-family-results` — replace `\resizebox` with stacked panels

Current issue: 12 columns plus CI intervals; currently hidden by `\scriptsize + \resizebox`.

Patch shape:

- Keep one `table` environment and label `tab:v18-family-results`.
- Use short caption + readable note.
- Replace with two or three `tabularx` panels:
  1. Recall panel: `Mudel`, `Kõneleja A (N=48, 95% UV)`, `Kõneleja D (N=145, 95% UV)`.
  2. Rejection panel: `Mudel`, `HN Mac`, `HN Kõneleja A`, `Pre-FPR`, `1K-FPR`, `Rev-FPR`, `Conf-FPR`.
  3. Optional one-column/short panel for `FAPH CV`, or include it in panel 2 if it still fits.
- Use `\small`, not `\scriptsize`.
- For long model names, either use a wrapping `Y` model column or short aliases (`v18a`, ..., `v18f`) with full names in a note.

### 10. `tab:checkpoint-headline` — split recall/rejection from FAPH

Current issue: 12 columns, currently hidden by `\scriptsize + \resizebox`.

Patch shape:

- Keep label `tab:checkpoint-headline`.
- Panel A: `Mudel`, `Rec A [UV]`, `Rec D [UV]`, `HN Mac`, `HN Kõneleja A`, `Pre-FPR`, `Conf-FPR`.
- Panel B: `Mudel`, `FAPH CV`, `FAPH LS`, `FAPH Mac`.
- Use short aliases in the model column: `tm=2`, `tm=10`, `tm=20`, `v16c`, `v6-res.`; define them in a table note.

### 11. `tab:checkpoint-consensus` — split metrics from FAPH corpora

Current issue: 9 columns, currently hidden by `\scriptsize + \resizebox`.

Patch shape:

- Keep label `tab:checkpoint-consensus`.
- Panel A: `Konfiguratsioon`, `Rec A`, `Rec D`, `Pre-FPR`, `Conf-FPR`.
- Panel B: `Konfiguratsioon`, `FAPH CV`, `FAPH LS`, `FAPH Mac`, `FAPH DiPCo`.
- Keep `0,00 [<u95]` values, but explain `u95` once in a table note.

## Figure readability plan

### Existing figures

Files:

- `docs/thesis/thesis-tex-estonian/figures/faph_recall_pareto.pdf`
- `docs/thesis/thesis-tex-estonian/figures/det_v6_v15_v16c_expertA.pdf`
- Generator: `wake-word/evaluation/generate_thesis_figures.py`

Patch plan:

1. In `second_chapter.tex`, change both `\includegraphics[width=0.85\linewidth]` to `width=\linewidth` for larger in-page labels.
2. Add optional short captions:

```tex
\caption[Ühe läve FAPH--recall operatsioonipunktid]{...}
\caption[DET-kõverad valitud mudeliperekondadele]{...}
```

3. In `generate_thesis_figures.py`, prefer Estonian/public labels:
   - `Recall, Isa XTTS` -> `Tuvastamismäär, Kõneleja A XTTS`
   - `FRR (%) — pos\_isa\_xtts ja pos\_ode agregeeritult` -> `Valetõrjumismäär (%) — Kõneleja A XTTS + Kõneleja B`
4. If labels still look small, increase `FIG_WIDTH_IN` from 12 cm to 14 cm equivalent and set annotation font from 7 to 8 pt. Because output is vector PDF, scaling is safe.

### Landscape decision

Do not add landscape initially. All wide tables above can be represented as stacked panels. If a final compile still shows unavoidable wide output, add `\usepackage{pdflscape}` and wrap only one table, but this should be the fallback, not the primary fix.

## High-value additional figures from existing artifacts/scripts

Prioritize only if they replace/summarize wide tables or strengthen the final thesis story.

### A. V18 phrase-selectivity heatmap — high priority

- Source: `wake-word/evaluation/benchmark_v18_clean_20260428_0214.csv`
- Suggested output: `docs/thesis/thesis-tex-estonian/figures/v18_phrase_selectivity_heatmap.pdf`
- Implement by extending `wake-word/evaluation/generate_thesis_figures.py`.
- Plot: rows `v18a`--`v18f`; columns `Rec Kõneleja D`, `Pre-FPR`, `1K-FPR`, `Rev-FPR`, `Conf-FPR`; add small side bar or annotation for `FAPH CV`.
- Value: visually shows that cleaned positives preserved recall but did not solve prefix/confusable failures. This can reduce dependence on the very wide Table 11.

### B. Checkpoint-FAPH trade-off scatter — high priority

- Sources:
  - `wake-word/evaluation/benchmark_checkpoint_models_20260429.csv`
  - `wake-word/evaluation/benchmark_checkpoint_faph20_20260429.csv`
- Suggested output: `docs/thesis/thesis-tex-estonian/figures/checkpoint_faph_recall_tradeoff.pdf`
- Plot: x-axis `FAPH CV` on log scale, y-axis `Kõneleja D recall`; label `tm=2`, `tm=10`, `tm=20`, `v16c`, `v6-residual`; optionally color/marker by `Conf-FPR`.
- Value: one figure explains the core lesson of the checkpoint experiment: optimizing FAPH alone can collapse real-speaker recall.

### C. Android field FAPH vs recall scatter — medium/high priority if space allows

- Sources:
  - Curated summary: `docs/research/android-field-run-2026-04-21.md`
  - Raw event source if regenerating: `output/android-captures-20260421-1357/events.jsonl`
  - Existing script: `wake-word/evaluation/analyze_android_events.py`
- Suggested output: `docs/thesis/thesis-tex-estonian/figures/android_field_faph_recall.pdf`
- Plot: x-axis Android Session 4 FAPH over 98.97 h at threshold 0.90; y-axis earlier shared recall on `pos_mattias_short_v2 @0.99`; highlight `expert-a` and `v6-residual`.
- Caveat in caption: thresholds differ, so this is deployment trade-off evidence, not a same-threshold benchmark.
- Value: supports the thesis claim that field behavior can reorder candidates.

### D. User-test replay figure — highest priority once real user-test data exists

- Source script: `tools/user-testing/summarize_user_test_replay.py`
- Expected input: `output/user-test-replay/**/replay_scores.jsonl`
- Expected summary: `output/user-test-analysis/user_test_replay_summary.csv`
- Suggested output: `docs/thesis/thesis-tex-estonian/figures/user_test_replay_recall_fpr_latency.pdf`
- Plot: per-model recall and hard-negative FPR with Wilson 95% CIs; optional second panel for median trigger latency.
- Value: directly fills final §5 user-test results. Do this after thresholds are frozen and participant data exists; do not tune thresholds on this figure.

Optional lower-priority diagnostic figure: regenerate/relabel the curated false-trigger spectrogram artifact (`docs/research/artifacts/wake-word-evaluation-2026-04/kratt_music_vs_positive_mel_grid.png`) or use `wake-word/evaluation/visualize_trigger_windows.py` to create an Estonian-labeled PDF. Useful only if there is room in the discussion of false-trigger acoustics.

## Secondary non-table overfull cleanup

`main.log` also reports overfull lines caused by long code paths/flags in normal prose, especially in `second_chapter.tex` lines 462, 496, 593 and `third_chapter.tex` lines 48, 57, 94, 119. These are not table/figure readability problems, but if doing a final formatting pass:

- Use `\path{...}` for file paths and long CLI flags.
- Add explicit `\allowbreak` in very long model paths if `\path{}` is not enough.
- Consider splitting the long augmentation parameter list in `third_chapter.tex` into shorter bullet subitems.

## Validation after applying patches

From `docs/thesis/thesis-tex-estonian/`:

```bash
latexmk -pdf -interaction=nonstopmode main.tex
rg -n "Overfull \\hbox|Underfull \\hbox|LaTeX Warning" main.log
```

Expected outcome:

- No table-related overfull boxes over ~5 pt.
- No remaining `\resizebox{\textwidth}{!}{%` around tables.
- Tables 4, 11, 12, 13 remain readable at `\small`/default size.
- `main.lot` and `main.lof` have short, readable entries for long-caption objects.
