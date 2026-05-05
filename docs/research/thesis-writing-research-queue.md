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
    - **Split-mode outcome**: if exactly one of {v16c, MoE
      consensus} brackets 0,5 FA/h on the holdout-aligned sweep
      (i.e. satisfies the pass/fail rule above) and the other
      does not, option (a) is taken **only** for the bracketing
      configuration and the non-bracketing one is reported under
      (b) in the same sentence. The drafted comparison sentence
      then reads, e.g., "v16c FRR = X % @ 0,5 FA/h vs.
      microWakeWord's 5 %; MoE consensus reported at cutoff 0,97,
      FAPH = 0,79" (or with the roles reversed). This split-mode
      branch is named explicitly so the next iteration cannot
      stall on a partial sweep: neither configuration is dropped,
      and the asymmetric reporting is treated as the defensible
      outcome rather than a failure mode.
    - **Split-mode clause order**: when the split-mode branch
      fires, the option-(a) half (matched-frame FRR @ 0,5 FA/h
      vs. the microWakeWord 5 % anchor) is reported first and the
      option-(b) half (acknowledged-gap FAPH @ cutoff 0,97 vs. the
      same microWakeWord 0,5 FA/h target) second, regardless of
      whether v16c or the MoE consensus is the bracketing
      configuration. This pins sentence ordering deterministically
      and removes the last drafting degree of freedom before the
      comparison sentence is written.
    - **Authoritative sweep identity**: the pass/fail check uses
      only the `det_curves.json` entries whose model tag is exactly
      `v16c` (single model) and the MoE consensus pair Expert A +
      Expert B2, AND whose negative test set matches the one named
      in `tab:fair-comparison-holdout` (CV ET FAPH holdout,
      `faph_test_cv_et`, ≈ 3,82 h, cf. l. 179). If the artefact
      contains additional sweeps (other model tags, other negative
      sets, or ad-hoc reruns), they are ignored for this decision;
      the holdout-aligned entries are authoritative.
    - **Cutoff-of-record**: each pinned FAPH carries its own
      decision threshold and they are not shared. v16c's 75 FAPH and
      v16c's 0,79-frame readout are reported at cutoff 0,97 per
      `tab:fair-comparison-holdout` (`chapters/second_chapter.tex`
      l. 179–198), whereas the MoE consensus' 0,79 FAPH was achieved
      by the Expert A + Expert B2 pair at cutoff 0,996/0,996 per the
      historical milestone recorded in
      `wake-word/docs/MODEL_LINEAGE.md` (and recapped in this repo's
      CLAUDE.md "Wake Word" section). The option-(b) sentence — and
      the option-(b) half of the split-mode branch — must therefore
      name the per-configuration cutoff (0,97 for v16c; 0,996/0,996
      for the MoE consensus) rather than a single shared "cutoff
      0,97" frame. This disambiguates which threshold anchors each
      half of the (b) readout without introducing a new comparator
      or a new sweep.
    - **Negative-set-of-record (MoE consensus, option (b))**: the
      cutoff-of-record bullet above pins the MoE consensus' 0,79 FAPH
      to cutoff 0,996/0,996 via `wake-word/docs/MODEL_LINEAGE.md` (and
      the CLAUDE.md "Wake Word" recap), but does not pin the negative
      audio set on which that 0,79 was measured. Resolution: inspect
      `MODEL_LINEAGE.md` (and the linked NOTES.md for the Expert A +
      Expert B2 milestone) and confirm whether the historical FAPH
      was measured on `faph_test_cv_et` (CV ET, ≈ 3,82 h, the same
      negative set used by `tab:fair-comparison-holdout` and pinned
      for v16c above) or on a different negative corpus. If the
      milestone set matches `faph_test_cv_et`, the existing per-set
      parenthetical convention covers both halves of the (b) sentence
      unchanged; if it does not, the (b) sentence — and the option-(b)
      half of the split-mode branch — must name v16c's and the MoE
      consensus' negative sets separately (e.g. "v16c FAPH = 75 on
      CV ET @ cutoff 0,97; MoE consensus FAPH = 0,79 on <name> @
      cutoff 0,996/0,996"), mirroring the existing DiPCo / CV ET
      dataset parenthetical rather than implying a shared CV ET frame.
      This entry only names the artefact to consult; it does not
      prescribe the outcome.
    - **Sweep ordering convention**: within the filtered v16c /
      MoE-consensus + `faph_test_cv_et` rows, sweep points are
      ordered by ascending decision threshold (the `thresholds`
      column in `det_curves.json`, produced by
      `generate_det_curve.py` as `np.arange(0.01, 1.001, 0.01)`,
      cf. l. 168). "Neighbouring" in the pass/fail rule means
      adjacent in that threshold ordering — not nearest in FA/h —
      so the bracketing pair around 0,5 FA/h is uniquely defined
      even if the sweep is non-monotone in FA/h. Concretely, the
      bracketing pair is the unique consecutive index pair
      $(i, i{+}1)$ for which $\mathrm{FA/h}_i \le 0{,}5 <
      \mathrm{FA/h}_{i+1}$ or $\mathrm{FA/h}_i > 0{,}5 \ge
      \mathrm{FA/h}_{i+1}$ in threshold order; if multiple such
      crossings exist, the lowest-threshold crossing is used so
      the choice is deterministic across iterations.
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
    - **FRR column convention**: the missing-rate axis at
      0,5 FA/h is read from the same sweep entries identified
      above, preferring an explicit FRR column when present
      (`frr_pooled` in `det_curves.json` produced by
      `generate_det_curve.py`, expressed as a fraction in
      [0, 1]); otherwise it is derived as `1 − recall` from a
      `recall`/`tpr` column. The reported FRR @ 0,5 FA/h is the
      linear interpolation in (FA/h, FRR) space between the two
      bracketing sweep points named in the pass/fail rule, so
      that no extrapolation is performed and the per-set
      breakdown (`frr_per_set`) is ignored unless the pooled
      column is missing. This pins the y-axis the same way the
      FA/h unit convention pins the x-axis, yielding a single
      reproducible value for option (a).
    - **Positive-set convention**: the `frr_pooled` value above is
      computed over the pooled positives from
      `wake-word/evaluation/generate_det_curve.py`'s `POS_TEST_SETS`
      (`isa_xtts` XTTS-synthesised plus `ode_real` and
      `mattias_short` real-speaker clips, scored individually and
      then pooled into one FRR axis), not over a single positive
      subset. The drafted comparison sentence must therefore name
      our positive-set composition parenthetically alongside
      microWakeWord's positive-set-derived 5 % anchor
      (`microwakeword2026`, `references.bib`, cf.
      `sections/wake-word-benchmarks.tex` l. 64), mirroring the
      existing DiPCo / CV ET negative-set parenthetical — e.g.
      "FRR = X % @ 0,5 FA/h on CV ET / pooled XTTS+real positives
      vs. microWakeWord's 5 % on DiPCo / their positive set". This
      pins the y-axis composition the same way the negative-set
      notes pin the x-axis composition, and applies to both option
      (a) and the option-(b) FRR readout. No new comparator is
      introduced.
    - **Comparator anchor for option (a)**: the FRR @ 0,5 FA/h
      obtained above is judged against the microWakeWord
      5 % FRR @ 0,5 FA/h figure (`microwakeword2026`,
      `references.bib`, cf. `sections/wake-word-benchmarks.tex`
      l. 23) as the primary apples-to-apples target, with the
      openWakeWord < 5 % FRR @ < 0,5 FA/h figure
      (`openwakeword2026`, same bib, l. 44) as a softer bound.
      The drafted comparison sentence must therefore report our
      interpolated FRR alongside this 5 % anchor (e.g. "FRR =
      X % @ 0,5 FA/h vs. microWakeWord's 5 %"), rather than as a
      standalone number; this is the criterion by which the
      next-iteration sentence is judged "defensible".
    - **Negative-set dataset note (option (a))**: the
      microWakeWord 5 % FRR @ 0,5 FA/h and openWakeWord
      < 5 % FRR @ < 0,5 FA/h figures are reported on the DiPCo
      dinner-party corpus (`dipco2020`, recapped in
      `chapters/second_chapter.tex` l. 373–374), not on Estonian
      Common Voice. Our holdout-aligned FRR @ 0,5 FA/h is measured
      on `faph_test_cv_et` (CV ET, ≈ 3,82 h, cf. l. 82–86 above),
      so the drafted sentence must either (i) state both negative
      sets parenthetically (e.g. "FRR = X % @ 0,5 FA/h on CV ET
      vs. microWakeWord's 5 % on DiPCo") or (ii) flag the dataset
      mismatch as a residual caveat — without opening any new
      comparator. This closes the apples-to-apples gap left by
      the bare 5 % anchor.
    - **Comparator evaluation-regime note (option (a))**: our
      `frr_pooled` figure is clip-pooled by construction —
      `generate_det_curve.py` l. 68–86 returns one max-smoothed
      score per clip via `score_clips`, and l. 192–203 then forms
      `frr_at_thr = 1 − (pooled ≥ threshold).mean()` over the
      pooled `POS_TEST_SETS` positives, i.e. a clip-level rather
      than streaming readout on the y-axis. The microWakeWord
      5 % FRR @ 0,5 FA/h target (`microwakeword2026`,
      `references.bib`, cf. `sections/wake-word-benchmarks.tex`
      l. 64) is cited via a github URL only and the regime under
      which that 5 % is reported (streaming positives vs.
      clip-pooled positives) is not pinned in this repo.
      Resolution: if the upstream regime can be confirmed from
      `microwakeword2026` to be clip-pooled, the drafted sentence
      reports a regime-matched comparison; otherwise the
      sentence must name the regime mismatch parenthetically
      alongside the existing DiPCo / CV ET dataset note (e.g.
      "FRR = X % @ 0,5 FA/h, clip-pooled, on CV ET vs.
      microWakeWord's 5 % on DiPCo, evaluation regime not pinned
      by us"). No new comparator is introduced; this bullet
      pins our y-axis regime and names the comparator-side gap
      so the next-iteration sentence cannot stall on it.
    - **Comparator anchor for option (b)**: when the cutoff-0,97
      frame is reported (either as the full (b) outcome or as the
      non-bracketing half of the split-mode branch), the FAPH
      figure must be named alongside the same microWakeWord
      0,5 FA/h target (`microwakeword2026`, `references.bib`,
      cf. `sections/wake-word-benchmarks.tex` l. 23) as the
      operating-point gap being acknowledged rather than matched.
      Concretely, the (b) sentence must report the ratio against
      that target — e.g. "FAPH = 0,79 @ cutoff 0,97, ca. 1,6× the
      microWakeWord 0,5 FA/h target reported at FRR ≤ 5 %" — so the
      reader sees the DET-axis offset rather than a bare cutoff-0,97
      number. This mirrors the option (a) anchor and closes the
      split-mode asymmetry without opening a new comparator: the
      same `microwakeword2026` reference anchors both halves, only
      the framing (matched vs. acknowledged gap) differs.
    - **Per-configuration ratio convention (option (b))**: the
      ratio against the microWakeWord 0,5 FA/h target is computed
      per configuration rather than shared, so each (b) half
      carries its own factor at its own cutoff-of-record. When
      v16c is the (b) half, the ratio is ~150× (75 ÷ 0,5) at
      cutoff 0,97 per `tab:fair-comparison-holdout`
      (`chapters/second_chapter.tex` l. 179–198); when the MoE
      consensus is the (b) half, the ratio is ~1,6× (0,79 ÷ 0,5)
      at cutoff 0,996/0,996 per the historical milestone in
      `wake-word/docs/MODEL_LINEAGE.md` (cf. cutoff-of-record
      bullet, l. 87–101 above). Both ratios are taken against the
      same `microwakeword2026` 0,5 FA/h target
      (`references.bib`, cf. `sections/wake-word-benchmarks.tex`
      l. 23), so no new comparator is introduced and the
      split-mode (b) half remains symmetric regardless of which
      configuration is non-bracketing.
    - **FRR readout for option (b)**: each configuration's FAPH
      figure must be paired with its FRR (or recall) read at that
      configuration's own cutoff-of-record, mirroring the
      per-configuration ratio convention above — i.e. "FRR @ cutoff
      0,97" for v16c and "FRR @ cutoff 0,996/0,996" for the MoE
      consensus — read from the same authoritative
      `det_curves.json` row used for the FAPH figure (preferring
      `frr_pooled`, else `1 − recall`). The (b) sentence then
      reports two per-configuration pairs — v16c's (FAPH, FRR) @
      cutoff 0,97 and the MoE consensus' (FAPH, FRR) @ cutoff
      0,996/0,996 — both anchored against microWakeWord's
      (0,5 FA/h, ≤ 5 % FRR), so the split-mode (b) half stays
      symmetric with option (a) on both axes and the y-axis is no
      longer pinned at a single shared cutoff. No new comparator is
      introduced; the same `microwakeword2026` reference still
      anchors both halves.
    - **Comparator evaluation-regime note (option (b))**: each
      configuration's per-cutoff FRR in the (b) readout is read via
      `frr_pooled` from the same authoritative `det_curves.json` row
      used for the FAPH figure, so the (b) y-axis is clip-pooled by
      construction in the same sense pinned for (a) (cf. l. 187–208
      above: `generate_det_curve.py` l. 68–86 returns one max-smoothed
      score per clip via `score_clips`, and l. 192–203 forms
      `frr_at_thr` over the pooled `POS_TEST_SETS` positives). The
      microWakeWord ≤ 5 % FRR regime that anchors the (b) ratio
      (`microwakeword2026`, `references.bib`, cf.
      `sections/wake-word-benchmarks.tex` l. 64) is cited via a github
      URL only and the regime under which that 5 % is reported
      (streaming positives vs. clip-pooled positives) is not pinned in
      this repo, mirroring the (a) gap. The (b) sentence — and the
      option-(b) half of the split-mode branch — must therefore name
      the regime mismatch parenthetically alongside the existing
      DiPCo / CV ET dataset note (e.g. "FAPH = 0,79 on CV ET @ cutoff
      0,996/0,996, FRR clip-pooled, ca. 1,6× the microWakeWord 0,5 FA/h
      DiPCo target reported at FRR ≤ 5 %, evaluation regime not pinned
      by us"). No new comparator is introduced; this bullet pins the
      (b) y-axis regime and names the same comparator-side gap as (a)
      so the split-mode branch closes with the same axis-pinning
      sequence on both halves.
    - **Negative-set dataset note (option (b))**: the same
      DiPCo / CV ET asymmetry applies when the cutoff-0,97 frame
      is reported, since the microWakeWord 0,5 FA/h target is
      also DiPCo-derived (`dipco2020`, cf.
      `chapters/second_chapter.tex` l. 373). The (b) sentence
      must therefore name both negative sets alongside the ratio
      (e.g. "FAPH = 0,79 on CV ET @ cutoff 0,97, ca. 1,6× the
      microWakeWord 0,5 FA/h DiPCo target") or flag the dataset
      mismatch as a residual caveat, mirroring (a) so the
      split-mode branch remains symmetric.
    - **Bracketing-check outcome**: the artefact at
      `wake-word/evaluation/det_curves.json` (gitignored per
      `.gitignore` l. 131, present only in the main working tree,
      not in this worktree) is keyed at top level by model version
      and contains rows for `v1`–`v13b` plus the `v6-residual` and
      `v6-specaug` ablations only; no `v16c` row exists, no MoE
      consensus (Expert A + Expert B2) row exists, and the per-model
      entries carry a single pooled `faph` sweep without a
      `faph_test_cv_et` breakdown. Bracketing of 0,5 FA/h on the
      holdout-aligned sweep is therefore **no for v16c** and **no
      for the MoE consensus**, so per the pass/fail rule (l. 50–55)
      option (a) is infeasible for both configurations and option
      (b) is forced (not split-mode). The drafted comparison
      sentence proceeds under the (b) frame on both halves, anchored
      by the per-configuration ratio and FRR-readout conventions
      already pinned above.
    - **Negative-set-of-record outcome (MoE consensus, option (b))**:
      the artefact lookup pinned by the bullet above (l. 102–121)
      resolves to CV ET. `wake-word/docs/MODEL_LINEAGE.md` (l. 17, 431)
      and `wake-word/models/kuule-kratt-expert-{a,b2}/NOTES.md` recap the
      Expert A + Expert B2 consensus milestone but do not name the
      negative corpus directly; the authoritative source is
      `wake-word/evaluation/model_evaluation_results.json` under
      `consensus_results."expert-a+expert-b2"."0.996/0.996".faph_cv =
      0.79`, where the `faph_cv` key denotes the Common Voice ET
      negative test set used uniformly across the unified benchmark
      (cf. v16c's `FAPH CV=75` at the same key, `MODEL_LINEAGE.md`
      l. 428). The MoE consensus' 0,79 FAPH is therefore measured on
      the same CV ET corpus as v16c's 75 FAPH (i.e. `faph_test_cv_et`
      per l. 82–86 above), so the existing per-set parenthetical
      convention covers both halves of the (b) sentence unchanged and
      no separate negative-set name is required for the MoE half. The
      DiPCo / CV ET parenthetical pinned by l. 299–308 applies
      symmetrically across both configurations; no new comparator and
      no new corpus is introduced.
    - **FRR-readout fallback under forced (b)**: because the
      bracketing-check above shows `det_curves.json` carries no v16c
      row and no MoE consensus (Expert A + Expert B2) row, the
      "same authoritative `det_curves.json` row" source named in the
      FRR-readout bullet (l. 260–267) is unavailable for either
      configuration. The per-configuration FRR readout therefore falls
      back to the same artefact that already pins each configuration's
      FAPH and cutoff-of-record: v16c's FRR @ cutoff 0,97 is read from
      `tab:fair-comparison-holdout` (`chapters/second_chapter.tex`
      l. 179–198, the same source as v16c's FAPH = 75), and the MoE
      consensus' FRR @ cutoff 0,996/0,996 is read from the Expert A +
      Expert B2 milestone in `wake-word/docs/MODEL_LINEAGE.md` (the
      same source already pinned for the 0,79 FAPH and the 0,996/0,996
      cutoff). If either source records recall rather than FRR, the
      readout is `1 − recall`. No new sweep, no new comparator, and no
      new artefact is introduced — this bullet only redirects the FRR
      source to the artefacts already authoritative for each
      configuration's FAPH and cutoff, closing the y-axis gap left by
      the bracketing-check outcome.
    - **FRR-of-record (forced (b))**: applying the FRR-readout
      fallback (l. 344–362) to its named artefacts yields the two
      per-configuration scalars. v16c: `tab:fair-comparison-holdout`
      (`chapters/second_chapter.tex` l. 179–198) covers v1–v8 only
      and carries no v16c row, so no FRR @ cutoff 0,97 scalar is
      retrievable; per the absence-fallback rule this half is
      deferred and the gap is named verbatim ("v16c FRR @ cutoff
      0,97 not pinned in `tab:fair-comparison-holdout`; table covers
      v1–v8 only"). MoE consensus (Expert A + Expert B2):
      `wake-word/evaluation/model_evaluation_results.json` under
      `consensus_results."expert-a+expert-b2"."0.996/0.996"` carries
      no `frr` key and no pooled recall; only per-set
      `recall_ode = "5/11"` (≈ 45,5 %, FRR ≈ 54,5 %) and
      `recall_isa_clip = "16/48"` (≈ 33,3 %, FRR ≈ 66,7 %) are
      present at this cutoff. Per `1 − recall`, the MoE half of the
      (b) sentence reports (FAPH = 0,79, FRR_ode ≈ 54,5 %,
      FRR_isa_clip ≈ 66,7 %) at cutoff 0,996/0,996, with the two FRR
      figures kept side by side rather than pooled since the
      artefact does not pin a single pooled FRR. No new sweep,
      comparator, or artefact is introduced.
- **Out of scope for this entry**: any comparator not already cited in
  `references.bib` (e.g. Hey Snips would require a new citation and is
  therefore deferred).
