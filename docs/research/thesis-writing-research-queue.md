# Thesis Writing — Research Queue

Shared backlog for the research-note lane. Each entry is a small, evidence-backed
question whose answer should be distilled into a single thesis sentence. Keep
items minimal: question, target sentence, candidate sources already in the repo,
status. Mark as `done` once the corresponding sentence is drafted.

---

## Q1 — Comparative FAPH baselines for Estonian/low-resource KWS

- **Status**: open
- **Question**: No published Estonian äratussõna (wake word) FAPH baseline
  exists, so v16c's 75 FAPH and the MoE consensus' 0,79 FAPH are currently
  uncontextualized in chapter 2. Which prior open-source baselines can we
  legitimately compare against, and at which operating point?
- **Target sentence**: the FAPH-comparison sentence in
  `docs/thesis/thesis-tex-estonian/chapters/second_chapter.tex` (around the
  `tab:fair-comparison-holdout` discussion, l. 179–198), where v7's FAPH = 96
  and v16c's FAPH = 75 are reported without an external comparator.
- **Candidate sources (already in repo)**:
  - `microwakeword2026` — `docs/thesis/thesis-tex-estonian/references.bib`,
    cited in `sections/wake-word-benchmarks.tex` (0,5 FA/h target, FRR ≤ 5 %).
  - `openwakeword2026` — same bib, cited as the open-source comparator at
    < 0,5 FA/h / < 5 % FRR in `sections/wake-word-benchmarks.tex` l. 44.
  - `docs/research/literature-review-kws-2026.md` §2 (FAPH measurement
    methodology) for canonical operating-point conventions.
- **Operating-point convention**: the candidate comparators report
  FRR @ fixed FA/h (microWakeWord: 0,5 FA/h, FRR ≤ 5 %; openWakeWord:
  < 0,5 FA/h, < 5 % FRR), whereas `tab:fair-comparison-holdout` reports
  FAPH @ fixed cutoff (0,97). The next sentence must therefore report
  our number in the comparators' frame, choosing one of:
  (a) FRR @ 0,5 FA/h interpolated from our DET-style sweep, or
  (b) explicitly flag that v16c's 75 FAPH and the MoE consensus' 0,79
  FAPH are reported at cutoff 0,97 and therefore lie on a different
  DET-axis than the openWakeWord/microWakeWord operating point.
- **Decision needed**: pick (a) or (b) before drafting the comparison
  sentence, so the next iteration produces a defensible apples-to-apples
  claim rather than a raw-number juxtaposition.
  - **Unresolved evidence gap**: it is not yet recorded whether our
    existing DET-style sweep covers FA/h ≈ 0,5 for v16c and the MoE
    consensus, so option (a) cannot currently be evaluated against (b).
    Resolution: inspect `wake-word/evaluation/det_curves.json` (produced
    by `wake-word/evaluation/generate_det_curve.py`, whose
    `TARGET_FAPHS` already includes 0,5) and confirm the sweep reaches
    that point for both configurations; if the artefact is missing or
    truncated above 0,5 FA/h, option (a) is infeasible and (b) becomes
    forced. This entry only names the artefact to check; it does not
    prescribe the outcome.
    - **Pass/fail rule**: option (a) is selected iff
      `det_curves.json` contains, for both v16c and the MoE consensus,
      at least one sweep point with FA/h ≤ 0,5 AND a neighbouring
      point with FA/h > 0,5, so that FRR @ 0,5 FA/h can be obtained
      by linear interpolation rather than extrapolation; otherwise
      (b) is forced.
    - **Authoritative sweep identity**: the pass/fail check uses
      only the `det_curves.json` entries whose model tag is exactly
      `v16c` (single model) and the MoE consensus pair Expert A +
      Expert B2, AND whose negative test set matches the one named
      in `tab:fair-comparison-holdout` (CV ET FAPH holdout,
      `faph_test_cv_et`, ≈ 3,82 h, cf. l. 179). If the artefact
      contains additional sweeps (other model tags, other negative
      sets, or ad-hoc reruns), they are ignored for this decision;
      the holdout-aligned entries are authoritative.
    - **FA/h unit convention**: the 0,5 FA/h threshold is
      interpreted as false-alarms per hour of negative audio, i.e.
      raw sweep counts are normalised by the holdout duration
      (count ÷ 3,82 h for `faph_test_cv_et`), matching the
      microWakeWord/openWakeWord per-hour-of-negative-audio
      convention rather than per-stream-hour. Any
      `det_curves.json` field already expressed in this unit
      (e.g. an `faph` or `fa_per_hour` column) is used as-is;
      raw-count fields (e.g. `false_alarms`) must be divided by
      the holdout duration before the 0,5 FA/h threshold is
      applied. This pins the axis on which (a) vs (b) is decided
      and removes the per-stream-hour reading as a source of
      ambiguity.
- **Out of scope for this entry**: any comparator not already cited in
  `references.bib` (e.g. Hey Snips would require a new citation and is
  therefore deferred).
