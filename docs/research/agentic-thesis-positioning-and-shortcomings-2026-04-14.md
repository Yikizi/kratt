# Agentic thesis positioning and current shortcomings (2026-04-14)

> **Historical but still required context:** methodological cautions remain relevant, but current model/user-test status is in `docs/research/source-of-truth-apr-2026.md` and `docs/PROJECT_TODO.md`.

Purpose: give future agents a compact, explicit view of the main scientific/methodological weaknesses in the current Kratt project state, and how to frame them productively in the thesis.

This is not a rejection of the project direction. It is a calibration note.

## Core position

Kratt is strong enough to support a very good bachelor's thesis, but the strongest contribution is probably **not** "we solved the Estonian wake word problem completely".

The strongest current contribution is closer to:

> building a realistic low-resource Estonian wake-word pipeline, correcting misleading evaluation methodology, instrumenting real-world collection/deployment loops, and mapping the true recall/FAPH/hard-negative trade space.

A practical extension on top of that is:

> showing how agentic engineering accelerated the pace of iteration across ML, Android, firmware, deployment tooling, and documentation.

## Important clarification about agentic engineering

Agentic coding meaningfully changes project throughput.

Things that are now genuinely plausible in a short time:
- building one-off tooling such as the Android false-trigger logger
- parallelizing repo audit, benchmark scripting, data ingestion, plotting, and doc maintenance
- moving faster across multiple fronts (Android, ESP32, ML, thesis text, deployment)
- exploring architecture variants and automation paths that would have been unrealistic for a solo bachelor's student a few years ago

This is a **real project strength**, not marketing fluff.

However, agentic engineering accelerates **implementation and iteration**, not the laws of evidence.

Agents can help create value 10x faster in:
- code generation
- refactoring
- instrumentation
- experiment orchestration
- analysis synthesis
- documentation

But they do **not** automatically solve:
- limited real speaker diversity
- missing held-out domains
- small-N recall estimates
- benchmark overfitting
- external validity
- the need for real user testing and final frozen evaluation sets

So the best thesis stance is:

> agentic engineering changed what one student could build and iterate within the available time,
> but rigorous evaluation and real-world evidence still remained the bottleneck.

That is a strong, modern, defensible position.

## Main current shortcomings

### 1. Real positive speaker diversity is still too small
The project has become much stronger on evaluation and tooling than on truly broad real-speaker evidence.

Risks:
- speaker overfitting
- prosody/style overfitting
- weak confidence in unseen-speaker recall claims

Important nuance:
- XTTS/TTS can help training and exploratory evaluation
- XTTS unseen-speaker recall is still a proxy, not a substitute for real unseen speakers

### 2. Benchmark ecology may be overused for too many roles
The same hold-out families are currently doing several jobs at once:
- model comparison
- threshold intuition
- architecture direction
- regression monitoring

Risk:
- practical benchmark overfitting, even after fixing explicit data leakage

Needed distinction:
- training set
- dev/tuning set
- final frozen test set
- regression canaries

### 3. The project center of gravity is currently more mature on false accepts than on positive variability
This is understandable because the main methodology breakthrough came from FAPH and real-world false-trigger analysis.

But the current balance risks becoming:
- very sophisticated negative engineering
- comparatively weak positive generalization evidence

Symptoms:
- strong reasoning around FAPH, hard negatives, same-device negatives, canaries
- much thinner evidence around real unseen-speaker recall

### 4. Consensus / expert models are promising, but should not become an escape hatch
The consensus result is interesting and likely worth including.

But it should not implicitly mean:
- "single-model learning/data problems remain unresolved, so add more models"

Current best interpretation:
- consensus is a valid practical extension
- consensus is not yet the cleanest primary thesis claim
- single-model baseline quality still matters

### 5. Hypothesis framing needs updating to match actual results
Original simplified hypotheses like:
- same-device negatives help
- learned content features generalize across microphones

are now too coarse.

What the repo actually shows is more nuanced:
- same-device negatives help only with sufficient quantity/composition
- too little in-domain negative data can hurt (degradation valley / unstable decision boundary)
- cross-device generalization is asymmetric: recall generalizes more easily than false-positive rejection

### 6. Too many concurrent threads can still weaken the thesis, even in the agent era
Agentic engineering makes multi-front execution far more realistic.
That part is true.

But thesis strength is still limited by:
- how clearly the contribution is framed
- whether evidence is sufficient for each claim
- whether the final story is coherent

So the right conclusion is **not** "scope no longer matters".
The better conclusion is:

> agents increase feasible execution scope, but they do not remove the need to prioritize claims and evidence.

## Recommended thesis framing

A strong framing would be something like:

> Developing and evaluating an Estonian wake-word detector for constrained hardware: a case study in low-resource data, realistic evaluation, deployment tradeoffs, and agent-accelerated engineering.

This allows the thesis to say all of the following honestly:
- the project built substantial real tooling and infrastructure
- agentic methods accelerated progress materially
- evaluation methodology turned out to be a major scientific contribution
- the final deployment problem is still constrained by real data and external validity

## Strongest current claims

These are the safest and strongest claims to defend:

1. Naive wake-word evaluation was misleading; held-out streaming evaluation changed the model ranking and the project direction.
2. Same-device negatives and hard negatives matter, but their effect depends strongly on composition and amount.
3. Real-world deployment quality is not predicted well enough by standard clip-level or narrow benchmark results alone.
4. Agentic engineering materially accelerated implementation across tooling and experiments, but rigorous evidence remained the bottleneck.
5. Expert-consensus can reduce false activations substantially, but current recall on real unseen speakers remains the main blocker.

## Suggested priorities for future work

### Highest thesis value
- collect more real unseen-speaker positives
- create/freeze a stricter dev vs final test split
- add a truly held-out same-device negative session
- sharpen thesis framing around methodology + deployment tradeoffs + agentic acceleration

### Useful but secondary
- continue consensus only if it stays tightly tied to deployment questions
- scale real Estonian negatives (e.g. Riigikogu) when they improve the core claim
- keep Android logger as a field evidence tool, not just an engineering side project

### Lower priority unless directly thesis-critical
- broad Home Assistant polish
- deep openWakeWord branch work
- side explorations like speaker identification unless they directly strengthen the thesis argument

## Guidance for future agents

When proposing work, prefer tasks that strengthen:
- real-world evidence
- final thesis argument clarity
- clean evaluation protocol
- explicit distinction between exploratory and final claims

Do not assume that faster implementation alone resolves scientific uncertainty.

Agents should treat "agentic acceleration" as a project advantage, but not as a reason to weaken methodological discipline.
