# Android false-trigger logger field run — 2026-04-21 analysis

## Context

On 2026-04-21 the Android false-trigger logger data was pulled from the attached Pixel 8a using:

```bash
kratt android devices
kratt android pull
kratt faph-log output/android-captures-20260421-1357/events.jsonl --cotrigger
```

Pulled artifacts:
- `output/android-captures-20260421-1357/events.jsonl`
- `output/android-captures-20260421-1357/index.jsonl`
- `output/android-captures-20260421-1357/*.wav`

Device observations at pull time:
- package installed: `ee.taltech.kratt.falselog`
- app not currently running (`pidof` empty)
- last capture timestamp on device: `2026-04-19 01:36:36 +03:00`

## Raw field measurement summary

- **4 sessions**
- **107.86 h total listening**
- **6977 trigger events / WAV snippets**
- logger events file: **6984 JSONL lines**

### Sessions

1. `2026-04-14T08:27:42Z` — 0.55 h — exploratory 16-model run
2. `2026-04-14T09:00:59Z` — 0.02 h — very short 26-model run, FAPH not meaningful
3. `2026-04-14T09:02:27Z` — 8.32 h — broad 23-model run
4. `2026-04-14T19:38:29Z` — **98.97 h** — main long-run deployment with 8 models

The **98.97 h session** is the most useful field evidence because it is long enough for stable false-trigger ranking.

## Main result: Session 4 (98.97 h)

Models running:
- `ex3a`
- `expert-a`
- `v10`
- `v11`
- `v14`
- `v16c`
- `v6`
- `v6-residual`

Field FAPH at Android logger threshold `0.90`:

| Model | Above threshold events | FAPH | Notes |
|---|---:|---:|---|
| `v6-residual` | 57 | **0.58** | best field false-trigger result |
| `ex3a` | 268 | **2.71** | low-FAPH cluster |
| `expert-a` | 276 | **2.79** | low-FAPH cluster |
| `v10` | 305 | **3.08** | moderate |
| `v16c` | 402 | **4.06** | moderate |
| `v6` | 443 | **4.48** | moderate |
| `v11` | 1038 | **10.49** | poor in field |
| `v14` | 1270 | **12.83** | worst among long-run finalists |

Immediate interpretation:
- `v11` and `v14` are too noisy for deployment in this field setup.
- `v6-residual` is extremely conservative in the field.
- `ex3a`, `expert-a`, and `v10` form the most interesting practical cluster after `v6-residual`.

## Recall cross-check against earlier offline benchmarks

Important caveat:
- Android field FAPH above was measured at runtime threshold **0.90**.
- Earlier offline benchmark recall tables are mainly reported at thresholds **0.97 / 0.99 / 0.995**.
- Therefore the comparison below is **not same-threshold apples-to-apples**. It is still useful as a ranking aid for the precision/recall trade-off.

For fair comparison across the Session 4 models, the cleanest shared earlier recall slice is:
- **`pos_mattias_short_v2`**, `n=135`
- threshold **0.99**

### Shared recall comparison (`pos_mattias_short_v2`, threshold 0.99)

| Model | Android FAPH (98.97 h) | Earlier recall @0.99 | Comment |
|---|---:|---:|---|
| `expert-a` | **2.79** | **0.970** | best overall balance |
| `v10` | 3.08 | 0.933 | good, but dominated by `expert-a` |
| `v16c` | 4.06 | 0.896 | usable middle ground |
| `v6` | 4.48 | 0.844 | weaker than `v16c` on both axes |
| `v11` | 10.49 | 0.837 | recall okay-ish, field FAPH too high |
| `ex3a` | 2.71 | 0.830 | low FAPH, but recall behind `expert-a` |
| `v14` | 12.83 | 0.807 | poor trade-off |
| `v6-residual` | **0.58** | 0.733 | lowest FAPH, but clear recall sacrifice |

### Pareto interpretation on the shared comparison

Using:
- **minimize** Android field FAPH
- **maximize** earlier recall on `pos_mattias_short_v2 @0.99`

the visible Pareto front is:
- **`expert-a`** — best practical balance
- **`v6-residual`** — extreme low-FAPH / lower-recall option

Everything else is dominated by one of those two, especially by `expert-a`.

## Additional broader recall evidence where available

Some older benchmark tables also include broader positive sets (`pos_isa_xtts`, `pos_ode`, `pos_mattias_short`) for a subset of models. On those broader earlier slices:

- `expert-a` remains very strong:
  - weighted recall @0.97 ≈ **0.991**
  - weighted recall @0.99 ≈ **0.991**
- `ex3a` is decent but clearly behind:
  - weighted recall @0.99 ≈ **0.936**
- `v10` is acceptable but drops more at stricter thresholds:
  - weighted recall @0.99 ≈ **0.817**
- `v6-residual` stays conservative:
  - weighted recall @0.99 ≈ **0.899** on the older three-set slice
  - but on the later shared `pos_mattias_short_v2` slice it is only **0.733**
- `v11` had strong earlier weighted recall on some older sets, but the new Android field result is bad enough that it should not be considered a balanced deployment winner.

## Recommendation from combined evidence

### Best overall balance right now

**`expert-a`**

Reason:
- Android field run: **2.79 FAPH** over a **98.97 h** run
- Earlier shared recall: **0.970** on `pos_mattias_short_v2 @0.99`
- On the available broader earlier recall tables it is also the strongest of the low-FAPH candidates

### Best ultra-conservative option

**`v6-residual`**

Reason:
- clearly best field FAPH: **0.58**
- but recall penalty is substantial, so it is attractive only if false accepts matter more than missed wakes

### Secondary fallback / comparison candidate

**`v10`**

Reason:
- still reasonably low field FAPH: **3.08**
- recall is decent, but `expert-a` is better on both axes in the shared comparison

## Thesis-relevant wording

This Android deployment provided the first long-duration same-device field comparison where multiple candidate models were evaluated under identical real-world background conditions. The main 98.97-hour session showed that low offline false-positive metrics did not automatically transfer to the field, and that the best deployment trade-off was not the most conservative model. In particular, `v6-residual` achieved the lowest observed field false accepts per hour (0.58 FAPH), but `expert-a` provided the strongest overall balance when field FAPH was considered together with earlier hold-out recall measurements.

## Next steps

1. Treat `expert-a` and `v6-residual` as the two key deployment trade-off anchors.
2. Mine and label the false-trigger WAVs from Session 4, especially:
   - `expert-a`
   - `v6-residual`
   - `v11`
   - `v14`
3. Add a thesis figure/table combining:
   - Android Session 4 FAPH
   - earlier shared recall (`pos_mattias_short_v2 @0.99`)
   - optional note for broader recall evidence where available.
