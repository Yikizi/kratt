# Best Local LLM for a Latency-Sensitive Estonian Voice Assistant

## Bottom line

The best default choice for Kratt’s live demo is **`qwen2.5:3b-instruct`** in Ollama, run warm, with **schema-constrained JSON output** and a **very small deterministic prompt**. Among the currently practical local models, it has the strongest combination of the traits this task actually needs: explicit improvement on **JSON-style structured outputs**, solid **instruction following**, **multilingual support**, and a small enough footprint to keep warm latency in the live-demo range on an entity["company","Apple","technology company"] Silicon Mac. citeturn16view0turn26view0turn26view3

The best **upgrade candidate** is **Qwen3-4B-Instruct-2507**, but not the stock Ollama `qwen3:4b-instruct` tag unless it is explicitly revalidated in your stack. The official Qwen docs say the **2507 Instruct** line is **non-thinking only** and no longer emits `<think>` blocks, which is exactly what a latency-sensitive JSON parser wants; by contrast, the stock Ollama `qwen3:4b-instruct` page is still the earlier Qwen3 family with **thinking-mode support**. That makes the **custom GGUF route** materially better than the stock tag for this use case. citeturn25view0turn25view1turn15view0

For this specific Estonian noisy-STT-to-JSON task, the models to avoid as primary live-demo parsers are **stock `gemma3:4b` in your current setup**, **Llama 3.2 1B/3B**, **24B-class Mistral Small 3.1/3.2**, and **TinyLlama/SmolLM-class general models**. Gemma 3 is strong on paper but has already shown a dangerous failure mode in your stack; Llama 3.2 officially supports eight languages, and Estonian is not one of them; Mistral Small 3.x is far too large for a snappy laptop demo loop; and the very small general models do not leave enough headroom for noisy morphology-heavy command parsing with strict JSON guarantees. citeturn16view3turn18view0turn17search11

## Ranked recommendations

### qwen2.5:3b-instruct

**Exact names/tags**
- Ollama: `qwen2.5:3b-instruct`
- GGUF repo on entity["company","Hugging Face","ml platform"]: `bartowski/Qwen2.5-3B-Instruct-GGUF`

This is the best overall fit because Qwen2.5 explicitly markets improvements in **instruction following**, **structured data understanding**, and **generating structured outputs, especially JSON**, while also offering **multilingual support** and a compact 3B size. For a voice assistant that must emit one strict JSON object with short Estonian text, those traits matter more than broad chat quality. The GGUF options are also straightforward: **Q4_K_M 1.93GB**, **Q5_K_M 2.22GB**, **Q8_0 3.29GB**. citeturn16view0turn21view0turn21view1turn21view2

Its main weakness is that public summaries do **not** call out Estonian specifically. So the recommendation is not “Qwen definitely knows Estonian best”; it is “Qwen2.5 has the best documented mix of multilingual ability, JSON friendliness, and small-model practicality.” For Kratt, that is enough to make it the safest default, provided you benchmark it against your own noisy transcripts. citeturn16view0

**Recommended quant**
- **Mac default:** `Q5_K_M`
- **Mac low-memory / fastest:** `Q4_K_M`
- **Do not default to Q8_0** unless you have plenty of unified memory and still meet the latency target

### Qwen3-4B-Instruct-2507

**Exact names/tags**
- Best route: custom GGUF with `bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF`
- If testing stock Ollama anyway: `qwen3:4b-instruct` **with explicit validation and `think:false`**
- Suggested local alias after import: `qwen3-4b-2507`

This is the most interesting alternative because the **2507 Instruct** line is explicitly **non-thinking only**, adds stronger **instruction following**, **tool usage**, and **multilingual gains**, and avoids the biggest latency/compliance problem of older hybrid-thinking models. Qwen’s own docs say `Qwen3-Instruct-2507` does not generate `<think>` blocks, and the 4B variant highlights gains in instruction following, logical reasoning, tool usage, and multilingual performance. The GGUF sizes are still manageable: **Q4_K_M 2.50GB**, **Q5_K_M 2.89GB**, **Q8_0 4.28GB**. citeturn25view0turn25view1turn24view0turn24view1turn24view2

The caveat is important: the stock Ollama `qwen3:4b-instruct` page is still the older Qwen3 family page with **thinking support**, not a clear pointer to the newer 2507 non-thinking Instruct weights. For a strict-JSON parser, that ambiguity is enough reason to prefer the **custom GGUF**. If you want the strongest small multilingual model and can tolerate a little extra setup, this is the first model to test against Qwen2.5 3B. citeturn15view0turn25view0turn25view1turn26view3

**Recommended quant**
- **Mac default:** `Q4_K_M`
- **Mac accuracy-leaning:** `Q5_K_M`

### gemma3:4b

**Exact names/tags**
- Ollama: `gemma3:4b`
- Optional Ollama QAT variant: `gemma3:4b-it-qat`
- GGUF repo: `bartowski/google_gemma-3-4b-it-GGUF`

Gemma 3 is strong on paper for this job. It is a compact model family with **structured outputs**, **function calling**, **128K context**, and **support for over 140 languages**. The 4B size is practical, and the quant options are healthy: **Q4_K_M 2.49GB**, **Q5_K_M 2.83GB**, with a QAT path also available. If this were a paper-only ranking, Gemma 3 would place higher. citeturn30view0turn30view1turn30view2turn16view1turn22search0turn22search1

It is not the top recommendation because your real stack matters more than paper features. In Kratt today, `gemma3:4b` has already shown the exact failure mode you most need to avoid: **empty `actions` with a success-claiming `response`**. Since this is a smart-light executor, that is not a cosmetic bug; it is a trust-breaking bug. Gemma 3 is worth retesting **only** with runtime schema enforcement and a stricter prompt than the one you are currently using. Until it clears that bar, it should not be the live default. The one Gemma-specific runtime note worth remembering is that some GGUF packs expose **Q4_1** as an Apple-Silicon-friendly legacy format with improved tokens-per-watt, but for correctness-first testing the safer first pass is still `Q4_K_M` or `Q5_K_M`. citeturn26view0turn26view3turn22search0

**Recommended quant**
- **First retest:** `Q4_K_M`
- **If still close but slightly error-prone:** `Q5_K_M`
- **If using Ollama-only and comparing QAT:** `gemma3:4b-it-qat`

### phi4-mini

**Exact names/tags**
- Ollama: `phi4-mini` or `phi4-mini:3.8b-q4_K_M`
- GGUF repo: `bartowski/microsoft_Phi-4-mini-instruct-GGUF`

Phi-4-mini is the best non-Qwen candidate if the priority is **instruction adherence under tight compute budgets**. Its own model card says it is intended for **memory/compute constrained environments** and **latency-bound scenarios**, and the release notes emphasize improved **multilingual support**, instruction following, and **function calling**. The quant sizes are easy to work with: **Q4_K_M 2.49GB**, **Q5_K_M 2.85GB**, **Q8_0 4.08GB**. citeturn29view0turn29view1turn19search0turn20view0turn20view1turn20view2

The reason it ranks below Qwen and Gemma for Kratt is language confidence, not raw model quality. Phi-4-mini explicitly warns that the family still has **quality disparities across non-English languages**, and that developers should expect worse performance outside English. For Estonian noisy STT, that warning matters. It may still do very well on the constrained JSON task, but it is a weaker linguistic bet than the stronger multilingual families. citeturn29view0

**Recommended quant**
- **Mac default:** `Q5_K_M` if you can afford it
- **Mac low-memory:** `Q4_K_M`

### EuroLLM control models

**Exact names/tags**
- Edge experiment: `utter-project/EuroLLM-1.7B-Instruct` with a GGUF such as `QuantFactory/EuroLLM-1.7B-Instruct-GGUF`
- Accuracy control on Mac: `utter-project/EuroLLM-9B-Instruct` with `bartowski/EuroLLM-9B-Instruct-GGUF`

EuroLLM deserves a special category because it is the only family in this short list with **explicit Estonian support in the model card** and a stated mission around **all official EU languages**. The 1.7B model is intentionally positioned for edge devices; the 9B model has much stronger multilingual credentials and is explicitly competitive on multilingual benchmarks. This makes EuroLLM very valuable as a **language-control benchmark**: if Qwen and Gemma disagree on an Estonian phrasing, EuroLLM is an excellent tiebreaker model to test offline. citeturn31view0turn31view1turn31view2turn33view0

They are not the live default for two reasons. First, the **1.7B instruct** card says it has **not been aligned to human preferences**, which is not what you want for schema-critical production behavior. Second, the **9B** model is probably too large for your latency target on many laptops, even though it is the best “linguistic sanity-check” option in this set. The useful way to think about EuroLLM is: **excellent Estonian-aware benchmark model, not first-choice demo parser**. The 1.7B GGUF sizes are light enough for experiments—**Q4_K_M 1.09GB**, **Q5_K_M 1.26GB**, **Q8_0 1.76GB**—but that speed advantage does not fully compensate for the structural-risk caveat. citeturn33view0turn35view0turn35view1turn35view2turn34search8

## Performance expectations on Apple Silicon and Pi 5

On Apple Silicon Macs, the warm-latency target is realistic for **3B–4B Q4/Q5 models**. The llama.cpp Apple Silicon benchmark thread shows **7B Q4** text generation at roughly **36.4 tok/s on M1 Pro** and **65.9 tok/s on M3 Max**. Since your response object should usually stay well under about 80 generated tokens, smaller **3B/4B** models should usually land inside the demo envelope after warmup on a modern Mac, especially with `keep_alive` enabled. That is the core reason the recommendation centers on the **Qwen 3B / 4B class** instead of 7B+ models. citeturn8view0turn26view3

On a Pi 5 CPU alone, the picture is much worse. The official Raspberry Pi AI HAT+ 2 article reports **Qwen2.5-1.5B** needing about **2039 ms just for 96-token CPU prefill** on a Pi 5, while the accelerator reduces that to 320 ms. In other words, even a small model already burns around two seconds before generation on the CPU-only path. A separate Pi 5 benchmark summary puts **Phi-3 Mini / 3.8B Q4** roughly in the **4–7 tok/s** class, which is far outside your preferred live-demo feel once you add JSON generation and the rest of the pipeline. For the current thesis/demo architecture, the Pi 5 is fine as an always-on node, but **not** as the best place to run the main local parser model unless you add an accelerator or accept much slower turns. citeturn10view0turn7search16

In practice that means:
- **Mac host:** use the best small dense multilingual model you can keep warm
- **Pi host:** only use a local LLM if you are willing to accept an “offline survives, but demo feels slow” fallback mode
- **If Pi-only matters**, benchmark EuroLLM-1.7B-Instruct and Qwen2.5 1.5B/3B, but expect a material accuracy hit versus the Mac-hosted default citeturn31view0turn33view0turn10view0

## Quantization and runtime settings

For this task, the best quant strategy is straightforward. On the Mac, use **Q5_K_M** when the model still fits comfortably and stays under target latency; otherwise use **Q4_K_M**. Those are the default “recommended” quality/speed tradeoffs on the common GGUF packs for Qwen2.5 3B, Qwen3 4B Instruct 2507, Gemma 3 4B, and Phi-4-mini. citeturn21view0turn24view0turn22search0turn20view0

For CPU-oriented ARM runs in llama.cpp, some GGUF repos expose **ARM-optimized Q4_0 variants**. On the Qwen2.5 3B pack, for example, `Q4_0_4_4` is explicitly described as a safe ARM pick, while `Q4_0_4_8` and `Q4_0_8_8` target specific ARM features. Those are relevant for Pi-class CPU inference, not for Metal-offloaded Mac usage. citeturn21view0

For runtime behavior, the most important recommendation is to let the runtime—not the model alone—enforce the JSON contract. Ollama supports **JSON mode** and **JSON schema structured outputs** through the `format` parameter, and the docs explicitly recommend also including the schema in the prompt to ground the model. llama.cpp and llama-cpp-python also support JSON schema constrained decoding; importantly, llama.cpp notes that the schema constrains output but is **not injected into the prompt**, so the prompt still has to describe the response shape. citeturn26view0turn26view1turn26view2turn26view3

Recommended settings for the live parser:

- `temperature`: **0.0 to 0.2**  
- `top_p`: **0.8 to 0.9**  
- `top_k`: **20 to 40**  
- `repeat_penalty`: **1.05 to 1.1**  
- `num_predict`: **96** normally, **128** if you allow two actions plus a response  
- `num_ctx`: **1024 to 2048**; there is no reason to pay long-context costs for a short STT transcript  
- `stream`: **false** for evaluation and simplest parsing  
- `keep_alive`: **30m** or longer during the demo so the model stays resident  
- `seed`: fixed during benchmarking, unset or fixed in production depending on how deterministic you want the parser to be

On stock Ollama Qwen3 tags, add **`think:false`** because thinking-mode support exists in the runtime API and only hurts this workload’s latency/compliance profile. citeturn26view3turn27view0

One extra engineering recommendation is worth stating plainly: **do not trust the `response` field blindly**. Even with schema enforcement, the application should hard-check the invariant **“if `actions` is empty, the response must not claim success.”** That should be a post-parse guard in Python, not only a prompt rule.

## Minimal prompt and schema

A good prompt for this task should be **short, explicit, domain-limited, and deterministic**. The model does not need to chat. It needs to classify a noisy utterance into a tiny action space and return one strict object.

### Recommended system prompt

```text
You are an Estonian smart-light command parser.

Return ONLY one JSON object that matches the schema.

Task:
- Read one short Estonian STT transcript.
- Infer the user's intended smart-light command even if the transcript is noisy.
- Use only these actions:
  turn_on, turn_off, set_brightness, set_color, get_state, list_devices
- If the user does not specify a lamp, use entity_id = "all".
- If the command is unclear, unsafe, or too ambiguous, return actions = [].
- If actions = [], response must NOT claim success.

Normalization rules:
- "kustu", "välja", "off", "pane tuli kustu", noisy forms like "pantuli kustu" usually mean turn_off.
- "põlema", "sisse", "tööle" usually mean turn_on.
- "mul on pime", "liiga pime", "heledamaks" mean set_brightness to 192 unless a clearer value is spoken.
- "liiga hele", "hämaramaks", "võta vähemaks" mean set_brightness to 96 unless a clearer value is spoken.
- Brightness spoken as percent must be converted to 0..255 and rounded.
- Canonical color names:
  white, warm_white, cool_white, red, green, blue, purple, pink, yellow, orange.
- If color is requested, use set_color and include the canonical color string.
- The response must be short Estonian suitable for TTS.
- Never include markdown, explanations, or extra text.
```

### Recommended schema

```json
{
  "type": "object",
  "properties": {
    "actions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "action": {
            "type": "string",
            "enum": [
              "turn_on",
              "turn_off",
              "set_brightness",
              "set_color",
              "get_state",
              "list_devices"
            ]
          },
          "entity_id": {
            "type": "string",
            "enum": ["all", "light.wiz_1", "light.wiz_2"]
          },
          "brightness": {
            "type": "integer",
            "minimum": 0,
            "maximum": 255
          },
          "color": {
            "type": "string",
            "enum": [
              "white",
              "warm_white",
              "cool_white",
              "red",
              "green",
              "blue",
              "purple",
              "pink",
              "yellow",
              "orange"
            ]
          }
        },
        "required": ["action", "entity_id"],
        "additionalProperties": false
      }
    },
    "response": {
      "type": "string"
    }
  },
  "required": ["actions", "response"],
  "additionalProperties": false
}
```

This is intentionally narrower than your informal target schema. Narrowing the color vocabulary and defining fallback brightness values will improve exact-match reliability more than switching among similarly sized models.

## Eval set and local comparison procedure

### Small benchmark set

Use this as the first pass. It mixes clean commands, Estonian morphology, pragmatic intent, and obvious STT noise.

```json
[
  {
    "transcript": "pane tuli kustu",
    "expected": {"actions":[{"action":"turn_off","entity_id":"all"}],"response":"Panen tuled kustu."}
  },
  {
    "transcript": "pantuli kustu",
    "expected": {"actions":[{"action":"turn_off","entity_id":"all"}],"response":"Panen tuled kustu."}
  },
  {
    "transcript": "pane tuli põlema",
    "expected": {"actions":[{"action":"turn_on","entity_id":"all"}],"response":"Panen tuled põlema."}
  },
  {
    "transcript": "pane tööle",
    "expected": {"actions":[{"action":"turn_on","entity_id":"all"}],"response":"Panen tuled tööle."}
  },
  {
    "transcript": "pane tuli siniseks",
    "expected": {"actions":[{"action":"set_color","entity_id":"all","color":"blue"}],"response":"Panen tuled siniseks."}
  },
  {
    "transcript": "tuli lillaks",
    "expected": {"actions":[{"action":"set_color","entity_id":"all","color":"purple"}],"response":"Panen tuled lillaks."}
  },
  {
    "transcript": "liiga hele",
    "expected": {"actions":[{"action":"set_brightness","entity_id":"all","brightness":96}],"response":"Teen tuled hämaramaks."}
  },
  {
    "transcript": "mul on pime",
    "expected": {"actions":[{"action":"set_brightness","entity_id":"all","brightness":192}],"response":"Teen tuled heledamaks."}
  },
  {
    "transcript": "pane heledus viiekümne peale",
    "expected": {"actions":[{"action":"set_brightness","entity_id":"all","brightness":128}],"response":"Panen heleduse viiekümne protsendi peale."}
  },
  {
    "transcript": "mis seisus tuled on",
    "expected": {"actions":[{"action":"get_state","entity_id":"all"}],"response":"Kohe vaatan tulede seisu."}
  },
  {
    "transcript": "näita seadmeid",
    "expected": {"actions":[{"action":"list_devices","entity_id":"all"}],"response":"Loetlen seadmed."}
  },
  {
    "transcript": "tuli kosta",
    "expected": {"actions":[],"response":"Ma ei saanud kindlast käsust aru."}
  }
]
```

The last case is deliberate. It protects against over-eager “kustu” correction when the transcript is too ambiguous.

### What to measure

Collect these metrics for every model and quant:

- **JSON-valid rate**
- **Schema-valid rate**
- **Exact action match rate**
- **Argument exact-match rate** for `entity_id`, `brightness`, `color`
- **False-success rate** when `actions=[]`
- **Warm p50 / p95 wall-clock latency**
- **Cold-start latency**
- **Prompt eval duration**
- **Generation duration**
- **Generated token count**
- **Tokens/sec** from `eval_count / eval_duration`

Ollama’s API returns `total_duration`, `load_duration`, `prompt_eval_count`, `prompt_eval_duration`, `eval_count`, and `eval_duration`, which is enough to compute warm/cold behavior and tokens/sec cleanly. citeturn26view3

### Ollama test procedure

Pull the baseline models:

```bash
ollama pull qwen2.5:3b-instruct
ollama pull phi4-mini:3.8b-q4_K_M
ollama pull gemma3:4b
ollama pull llama3.2
```

Import Qwen3-4B-Instruct-2507 as a custom model if you want the stronger alternative:

```bash
huggingface-cli download bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF \
  --include "Qwen3-4B-Instruct-2507-Q4_K_M.gguf" \
  --local-dir ./models/qwen3-4b-2507

cat > Modelfile <<'EOF'
FROM ./models/qwen3-4b-2507/Qwen3-4B-Instruct-2507-Q4_K_M.gguf
PARAMETER temperature 0.1
PARAMETER top_p 0.8
PARAMETER top_k 20
PARAMETER repeat_penalty 1.05
PARAMETER num_ctx 2048
EOF

ollama create qwen3-4b-2507 -f Modelfile
```

The custom import path is recommended because the Qwen 2507 instruct line is explicitly non-thinking, while the stock `qwen3:4b-instruct` tag still exposes the older Qwen3 family behavior. citeturn25view0turn25view1turn15view0

Send requests with schema-constrained output and `stream:false`. For Qwen3 stock tags, add `"think": false`.

```bash
curl -s http://localhost:11434/api/chat -d @request.json
```

Structure each `request.json` like this:

```json
{
  "model": "qwen2.5:3b-instruct",
  "stream": false,
  "keep_alive": "30m",
  "options": {
    "temperature": 0.1,
    "top_p": 0.8,
    "top_k": 20,
    "repeat_penalty": 1.05,
    "num_predict": 96,
    "num_ctx": 2048,
    "seed": 42
  },
  "messages": [
    {"role": "system", "content": "PASTE SYSTEM PROMPT HERE"},
    {"role": "user", "content": "Transcript: pantuli kustu"}
  ],
  "format": { "PASTE JSON SCHEMA HERE": true }
}
```

### llama.cpp test procedure

If you want the lowest-friction custom GGUF path, run a local server with the model fully offloaded on the Mac GPU layers if possible and use JSON schema constrained decoding through the OpenAI-compatible endpoint.

```bash
./llama-server \
  -m ./Qwen2.5-3B-Instruct-Q5_K_M.gguf \
  -ngl 999 \
  -c 2048 \
  --host 127.0.0.1 \
  --port 8080
```

llama.cpp supports JSON-schema-constrained outputs through `response_format` / `json_schema`, and its grammar docs warn to keep grammars simple because complex optional structures can slow sampling. Your schema is small enough that this is a good fit. citeturn26view1turn26view2

## Final recommendation

**Default live-demo model:** **`qwen2.5:3b-instruct`**, using **Q5_K_M on the Mac if it still clears the latency target**, otherwise **Q4_K_M**. Run it warm, enforce the JSON schema at the runtime layer, use a tiny prompt, and keep the app-side invariant check that forbids success text when `actions=[]`. This is the best balance of speed, structured-output reliability, and multilingual practicality documented in the currently available local small-model options. citeturn16view0turn21view0turn21view1turn26view0turn26view3

**Fallback model:** **Qwen3-4B-Instruct-2507**, imported from GGUF as a custom local model. Choose **Q4_K_M** first, then **Q5_K_M** if you have headroom. This is the best second choice because it gives you a newer non-thinking instruct model with stronger multilingual/tool-use behavior, but without the ambiguity of the older stock Ollama Qwen3 tag. citeturn25view0turn25view1turn24view0turn24view1

**Language-control benchmark model:** **EuroLLM-9B-Instruct Q4_K_M** on the Mac, not for the live demo but for offline bake-offs on tricky Estonian phrases. If the top two models disagree on noisy morphology-heavy inputs, EuroLLM is the best explicit-Estonian sanity check to include in the shootout. citeturn31view0turn31view1turn31view2turn34search8

**Pi-specific emergency fallback:** **EuroLLM-1.7B-Instruct Q4_K_M** only if you must stay fully local on the Pi and accept lower reliability. It is the best explicit-Estonian edge-sized option found here, but it should not replace the Mac-hosted default for the live demo. citeturn33view0turn35view0

**Do not use as primary live-demo parser:**
- **stock `gemma3:4b`** until it clears your own JSON/invariant evals
- **`llama3.2` / `llama3.2:1b`** for primary Estonian parsing, because Estonian is not in the officially supported language set
- **`mistral-small3.1` / `mistral-small3.2`** for live parsing, because 24B/15GB is the wrong latency class for this demo loop
- **TinyLlama / SmolLM-class general models** as the main parser, because the task is too reliability-sensitive and too morphology/noise-heavy for that size class to be a safe first choice citeturn16view3turn18view0turn17search11