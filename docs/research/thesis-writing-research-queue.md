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
- **Out of scope for this entry**: any comparator not already cited in
  `references.bib` (e.g. Hey Snips would require a new citation and is
  therefore deferred).
