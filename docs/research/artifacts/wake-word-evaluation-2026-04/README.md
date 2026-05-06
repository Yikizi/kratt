# Wake-word evaluation artifacts — April 2026

Curated CSV/HTML/PNG artifacts from April 2026 wake-word evaluation runs.

These files were originally produced under `wake-word/evaluation/` during model comparison, false-trigger analysis, supervisor-table generation, and visual inspection. They are kept here because they are small, thesis-relevant evidence rather than raw/private data.

## Contents

- `benchmark_*.csv` — benchmark summaries for model families, retraining ablations, supervisor comparisons, and confusable-filter runs.
- `model_comparison*.csv` — smaller comparison snapshots at selected thresholds.
- `false_accepts_*.csv` and `kratt_false_live_scores.csv` — false-trigger analysis tables.
- `ohem_expert_a_cv_et.csv` — OHEM mining/analysis output for Expert A.
- `supervisor_table.csv` and `supervisor_report.html` — supervisor-facing evaluation table/report.
  The mega report source `benchmark_results_supervisor.csv` is the post-v17 supervisor CSV
  with appended v18 clean/consensus/checkpoint rows and the v19a Kratt-only target-policy
  benchmark for cross-version browsing.
- `kratt_false_live_timeline.png` and `kratt_music_vs_positive_mel_grid.png` — selected diagnostic figures.

## Notes

- Raw Android captures and audio snippets stay in ignored `output/` / `wake-word/data/` paths.
- Large DET curve JSON files are not included here by default; if needed for the thesis, export a compact CSV/figure and document it in this folder.
- When regenerating these results, prefer writing new curated runs to a dated subdirectory instead of overwriting this one.
