# Research artifacts

This directory contains curated, thesis-relevant experiment artifacts that are small enough and safe enough to keep in git.

Use this for evidence that should survive beyond one local run:

- benchmark CSV tables;
- manually selected plots (`.png`, `.pdf`);
- static HTML reports;
- short JSON/Markdown summaries;
- per-run README files explaining provenance.

Do **not** put raw/private audio, large model files, local caches, or unsorted run dumps here. Keep those in ignored locations such as `output/`, `wake-word/data/`, or local scratch directories.

Each artifact subdirectory should include a `README.md` with:

1. date and purpose of the run;
2. scripts/commands used, if known;
3. model versions and thresholds;
4. input test sets or field-run source;
5. which files are thesis-facing evidence.
