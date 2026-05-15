# English→Estonian MT benchmark for Kratt demo responses (2026-05-10)

Goal: test whether the demo pipeline can keep the small fast LLM focused on JSON/tool use and generate flexible English spoken replies, then translate those replies to Estonian before TTS. This is explicitly **not** a template-based runtime plan; the fixed sentences below are only a benchmark/regression set.

## Command

```bash
kratt translation-bench --models opus-ct2-int8 opus opus-big \
  --threads 4 --protect-placeholders \
  --output-dir output/translation-bench/latest-small

kratt translation-bench --models nllb-600m \
  --threads 4 --protect-placeholders \
  --output-dir output/translation-bench/latest-nllb
```

Tooling added:

- `tools/demo-pipeline/bench_translation_models.py`
- `cli/commands/kratt-translation-bench`

Dependencies installed into the existing project venv with `uv pip`: `sentencepiece`, `sacremoses`, `protobuf`, `ctranslate2`.

## Results

Measured on this host CPU, 4 Torch threads, 30 short smart-home/helper responses, greedy decoding (`--beams 1`).

| model | backend | load s | RSS MB | p50 ms | p95 ms | corpus chrF | placeholder ok |
|---|---:|---:|---:|---:|---:|---:|---:|
| `opus-ct2-int8` | CTranslate2 Marian/SPM | 1.15 | 313.7 | 36.5 | 57.1 | 60.25 | 1.0 |
| `opus` | Transformers Marian | 7.79 | 1102.1 | 127.5 | 182.0 | 58.88 | 1.0 |
| `opus-big` | Transformers Marian | 4.30 | 1895.0 | 293.5 | 409.6 | 59.44 | 1.0 |
| `nllb-600m` | Transformers NLLB | 8.41 | 1804.1 | 1068.5 | 1513.0 | 46.94 | 1.0 |

Raw detailed outputs:

- `output/translation-bench/latest-small/summary.md`
- `output/translation-bench/latest-small/outputs.tsv`
- `output/translation-bench/latest-nllb/summary.md`
- `output/translation-bench/latest-nllb/outputs.tsv`

## Interpretation

Best latency/quality tradeoff: **`opus-ct2-int8`**.

- Adds roughly **40–60 ms** per short reply on this host.
- Keeps memory much lower than Transformers Marian.
- Output is usually understandable Estonian and much better than small LLM broken direct Estonian.
- Quality is not perfect; source wording matters a lot.

`opus` gives almost identical translations but is ~3–4× slower and uses ~1.1 GB RSS. `opus-big` is slower and not clearly better. `nllb-600m` is too slow and worse for this narrow EN→ET smart-home style.

Beam size 4 was also tested (`output/translation-bench/latest-small-beam4`). It roughly doubled latency for `opus-ct2-int8` and did not improve enough to justify it for the hot path.

## Important source-style finding

MT works best if the response LLM writes **simple translation-friendly English**, not arbitrary idiomatic English. This can preserve LLM flexibility without using Estonian templates.

Examples from a quick `opus-ct2-int8` source-style probe:

| English source | Estonian MT output |
|---|---|
| `I turned <x1/> on.` | `Ma lülitasin sisse <x1/>.` |
| `<x1/> is now on.` | `<x1/> on nüüd sisse lülitatud.` |
| `I changed the light to blue.` | `Ma muutsin valguse siniseks.` |
| `I changed <x1/> to blue.` | `Ma muutsin <x1/> siniseks.` |
| `The bulb is not responding right now.` | `Pirn ei vasta praegu.` |
| `I cannot connect to the bulb right now.` | `Ma ei saa praegu pirniga ühendust.` |
| `It is seven fifteen.` | `Kell on seitse viisteist.` |
| `Turn it off with the wall switch first.` | `Lülita see enne seinalülitiga välja.` |

Bad/fragile source patterns observed:

- `Done — <LIGHT_1> is on now.` → `Tehtud ~ <LIGHT_1> on nüüd.` (awkward/incomplete)
- `I have set <LIGHT_1> to <COLOR_1>.` → `Ma olen määranud <LIGHT_1> kuni <COLOR_1>.` (bad preposition)
- `I couldn't reach the bulb right now.` → `Ma ei jõudnud praegu pirninini.` (bad inflection)
- `The time is quarter past seven.` → `Kell on veerand seitse.` (wrong Estonian time convention for 7:15)

## Runtime recommendation without templates

Keep runtime flexible:

1. Small LLM returns tool JSON plus a short **English** `say_en` candidate.
2. Prompt constrains `say_en` style, not content:
   - short, one sentence if possible;
   - plain English;
   - active or simple state sentences;
   - avoid idioms, em dashes, slashy punctuation;
   - preserve device placeholders like `<x1/>`;
   - use actual color words where possible, not color placeholders.
3. MT translates `say_en` with `opus-ct2-int8`.
4. Restore protected placeholders and run cheap validators:
   - placeholder count unchanged;
   - no obvious English leakage;
   - output length TTS-safe;
   - no `~` / weird punctuation if we choose to block it.
5. If validation fails, ask the LLM for a simpler English paraphrase and translate again, or fall back to a larger Estonian rewrite/helper model.

This avoids fixed Estonian response templates while still preventing the small JSON/tool model from directly producing broken Estonian TTS text.

## Quick direct-Estonian vs English→MT A/B (same day)

After the MT-only benchmark, a small response-generation A/B was run to answer whether this actually improves the assistant output compared with asking local Qwen models to speak Estonian directly. This was an 8-case event-to-reply test, not a final human study. Output files:

- `output/translation-bench/response-ab-quick/results.json`
- `output/translation-bench/response-ab-quick/outputs.tsv`
- `output/translation-bench/response-ab-quick/summary.json`

Automatic chrF is only a rough proxy because natural alternative wordings are penalized, but the qualitative difference was large for the small models.

| model | direct ET mean chrF | EN→MT mean chrF | direct chrF≥45 | EN→MT chrF≥45 | result |
|---|---:|---:|---:|---:|---|
| `qwen2.5:0.5b` | 6.7 | 0.0 | 0/8 | 0/8 | Too small; even English prompt came back in Chinese. |
| `qwen2.5:1.5b` | 14.1 | 41.7 | 0/8 | 5/8 | Major improvement, still needs validation. |
| `qwen2.5:3b` | 25.5 | 51.5 | 1/8 | 6/8 | Major improvement; best small-model tradeoff so far. |
| `qwen2.5:7b` | 28.6 | 37.0 | 1/8 | 2/8 | Better but not solved; prompt/source style still matters. |

Examples:

- `qwen2.5:1.5b` direct ET: `Tulime linnas külaline värv.`
  - English→MT: `Tuled muutuvad nüüd siniseks.`
- `qwen2.5:3b` direct ET: `Paneetbild on polepärast vastunud. Proovige seni uuestlitada.`
  - English→MT: `Pirn ei vasta.`
- `qwen2.5:3b` direct ET: `Tallinna ilm on kiiu ja läbi on 5 astmeaast. Ilmkoostuseks on kiiu.`
  - English→MT: `Tallinnas on pilvine temperatuur 5 °C.`

Current intent-benchmark direct-Estonian outputs also confirm the issue in the real prompt family:

- `qwen2.5:1.5b`: intent success 12%, JSON valid 100%, median 0.8 s; responses include `Praegu üksikasjad puutese.`, `Pannin maailma magamistona.`, `Kohvita lampas ebaseidis.`
- `qwen2.5:3b`: intent success 38%, JSON valid 100%, median 1.4 s; responses include `Elutoa lamp on aaktivne.`, `Magamistoo lamp on akele jaoks akeletud.`, `Kohv on käinud ja elutoa lamp on küljapõlema`.
- `qwen2.5:7b`: intent success 38%, JSON valid 100%, median 2.0 s; responses include `Tulit on pöörnud poolema.`, `Elutoa tõusis hämari.`, `Elutoa tuba on aegnähtud valgelonnaks lülitatud.`

Interpretation: for `qwen2.5:1.5b` and `qwen2.5:3b`, English response generation plus `opus-ct2-int8` is not a cosmetic improvement; it often changes unusable Estonian into TTS-usable Estonian. It does **not** fix wrong tool semantics or bad English source sentences, so the runtime still needs a small validator and retry/rewrite path.

## Demo integration

Integrated as an opt-in demo mode:

```bash
kratt demo --translate-responses --llm qwen2.5:3b
# equivalent:
kratt demo --response-mode en-mt --llm qwen2.5:3b
```

Runtime behavior in `en-mt` mode:

1. The existing intent parser still decides route/actions.
2. After non-local device actions execute, a short English response is generated from the executed event JSON using `SYSTEM_PROMPT_RESPONSE_EN`.
3. `tools.demo_pipeline.translation.EnglishToEstonianTranslator` translates that English sentence with `manancode/opus-mt-en-et-ctranslate2-android`.
4. The translated Estonian is printed/spoken, and telemetry logs `response_source`, `response_en`, `response_gen_latency_ms`, and `response_mt_latency_ms`.

Time/date/weather/capability/helper responses remain on the existing Estonian runtime path for now because those already contain computed Estonian facts and should not be blindly back-translated.
