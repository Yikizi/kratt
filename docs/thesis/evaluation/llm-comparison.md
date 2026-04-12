# LLM-i valik Kratt'i häälassistendi jaoks

**Staatus**: Mustand, ootab mõõtmiste lõppu
**Seotud**: `docs/architecture/decision-records/0001-ekspressiivne-tts-markup.md`, `tools/llm-bench/`

## Eesmärk

Valida LLM mis:
1. Parseerib eestikeelseid käsklusi JSON struktuuri (Kratti tool calling)
2. Toodab loomulikke eestikeelseid vastuseid
3. Jookseb lokaalselt M1 Pro 32GB peal
4. On piisavalt kiire et end-to-end latency jääb alla 5 sekundi

## Metoodika

Hindasime kolme mudelit kolmel mõõdetaval teljel:

| Telg | Mis see on | Kuidas mõõdetud |
|---|---|---|
| **A) Eesti keele kvaliteet** | Kas mudel valdab eesti morfoloogiat, grammatikat, sõnavara | lm-evaluation-harness + TalTechNLP Estonian tasks (published benchmark) |
| **B) JSON instruction-following** | Kas mudel suudab järgida süsteempromptis antud JSON schemat | Kratt-spetsiifiline 8-lausetest, skeema valideerimine |
| **C) Latency** | Tokeni/sek genereerimise kiirus | Ollama `/api/chat` keskmine response time 5 jooksuga |

**Oluline**: A ja B on erinevad teljed. Mudel võib olla tugev ühes ja nõrk teises. Meie kasutusjuht nõuab mõlemat.

### Vaatluse all mudelid

| Mudel | Suurus | Kvantiseerimine | Miks valitud |
|---|---|---|---|
| `gemma3:12b` | 12.2B | Q4_K_M | Hetkel tootmises, multilingual baas |
| `qwen2.5:14b` | 14.7B | Q4_K_M | Tuntud tugev JSON/tool calling'u eest |
| `alibayram/erurollm-9b-instruct` | 9B | Q4 | Spetsiaalselt Euroopa keeltele treenitud, sh eesti keel |
| `gemma4:e4b` | 4.5B eff. | Q4_K_M | Gemma 4 edge variant (apr 2026), natiivne tool calling, 140+ keelt |
| `gemma4:26b` | 26B MoE (3.8B akt.) | Q4_K_M | Gemma 4 MoE variant, 128 eksperti, 256K kontekst |

## Kirjanduse ülevaade — Eesti LLM benchmarkid

### EuroEval Estonian

[EuroEval.com](https://euroeval.com/datasets/estonian/) sisaldab 9 Eesti taski erinevates domeenides: sentiment,
NER, linguistic acceptability (Grammar-et), reading comprehension (MultiWikiQA-et), knowledge (MMLU-et, Trivia-et,
Exam-et, INCLUDE-et), common-sense (Winogrande-et), summarisation (ERRNews), instruction-following (IFEval-et),
European values (ValEU-et).

Meie kasutusjuhu jaoks on relevantsed **Grammar-et** (grammatikakorrektsus) ja **IFEval-et** (juhiste järgimine).

### TalTech Estonian LLM Benchmark (arXiv:2510.21193, 2025)

Tanel Alumäe grupi 2025. aasta oktoobri töö hindas **32 mudelit** (6 base + 26 instruction-tuned) seitsmel
Eesti taskil: Estonian National Exam, Trivia (Eesti-spetsiifiline), Declension (käänamine), Word Meanings
(sõnatähendused), Grammar Correction (grammatikaparandus), News Summarisation (ERRNews), Speaker Name Extraction.

Hindamine toimus nii inimese abiga kui **Claude Sonnet 3.7 LLM-as-judge** meetodil (Pearsoni korrelatsioon
inimesega 0.94).

**Relevantsed skoorid meie kandidaatide jaoks** (keskmine üle 7 taski):

| Mudel | Skoor |
|---|---|
| Gemini 2.5 Pro (tipp) | 0.638 |
| Claude Sonnet 3.7 | 0.626 |
| GPT-4o | 0.616 |
| Gemma-3 27B Instruct | 0.386 |
| **EuroLLM-9B-Instruct** | **0.409** |
| **Gemma-3-12b-It** | **0.354** |
| Qwen2-72B-Instruct | 0.280 |

**Võti**: EuroLLM 9B edestab Gemma 3 12B-d **puhtal eesti keele kvaliteedil**. Qwen 2.5 (meie kandidaat)
paperis ei esinenud, ainult Qwen2 ja Qwen3.

Allikas: TalTech LREC 2026 submission, täis skoorid kõigi 7 taski kohta vt Lisa X.

## Meie lokaalne mõõtmine

### A telg: eesti keele kvaliteet (TalTech benchmark alamhulk)

Kordasime TalTech benchmarki Ollama kaudu meie kolmel konkreetsel kandidaadil. Valisime kolm tasksi
lokaalseks jooksutamiseks (täis 7 oleks võtnud liiga kaua):

- `inflection_et_instr` — 100 näidist käänamise ja morfoloogia kohta
- `grammar_et_instr` — 100 näidist grammatikaparandust
- `word_meanings_et_instr` — 100 näidist leksikaali tundmist

**Käivitamisjuhend reproduktsiooniks**:
```bash
cd tools/estonian-eval-tasks
lm-eval \
  --model "openai-chat-completions" \
  --model_args "base_url=http://localhost:11434/v1/chat/completions,model=<MODEL>,num_concurrent=1,tokenized_requests=False" \
  --tasks inflection_et_instr,grammar_et_instr,word_meanings_et_instr \
  --include_path tasks \
  --apply_chat_template \
  --limit 100 \
  --output_path ../llm-bench/euroeval_results/<MODEL_DIR>
```

**Tulemused** (käivitatud 2026-04-07/10, Ollama Q4_K_M kvantiseerimine, n=100 per task):

| Mudel | inflection exact_match ↑ | grammar lev ↑ | grammar precise ↑ | word_meanings exact_match ↑ |
|---|---|---|---|---|
| gemma3:12b | 0.3600 | 0.2216 | 0.1200 | 0.2800 |
| qwen2.5:14b | 0.0300 | 0.1052 | 0.0200 | 0.0300 |
| **alibayram/erurollm-9b-instruct** | **0.6500** | **0.2749** | **0.1900** | **0.3100** |
| gemma4:e4b (apr 2026) | 0.0200 | 0.1514 | 0.0300 | 0.0700 |
| gemma4:26b (apr 2026) | *(OOM crash)* | *(OOM crash)* | *(OOM crash)* | *(OOM crash)* |

**Exact_match keskmine (inflection + word_meanings)**:
- Gemma 3 12B: 0.32
- Qwen 2.5 14B: 0.03
- **EuroLLM 9B**: **0.48** *(+50% Gemma üle)*
- Gemma 4 E4B: 0.045 *(4.5B efektiivne mudel — liiga väike eesti keele jaoks)*
- Gemma 4 26B MoE: *(ei suutnud lõpetada — Ollama 500 error pärast 35 min, tõenäoliselt OOM M1 Pro 32GB-l)*

**Järeldus**: Meie lokaalne mõõtmine **kinnitab TalTech arxivi paperi tulemust**. EuroLLM 9B on kõige
tugevam meie kandidaatidest puhtal eesti keele kvaliteedil. Qwen 2.5 14B on dramaatiliselt halvem —
inflection'il 3% exact_match tähendab et mudel põhimõtteliselt **ei oska eesti morfoloogiat**.

### B telg: rakenduse-spetsiifiline JSON instruction-following

**Oluline metodoloogiline märkus**: see **ei ole benchmark**. See on Kratt-spetsiifiline **evaluation set**
mille disainisime ise (n=8), et mõõta täpselt seda mida kasutusjuht nõuab: eestikeelse käsklause →
`{"actions": [...], "response": "..."}` teisendust. Tulemusi ei tohi tõlgendada kui üldist mudeli võimekust,
vaid kui "kas see mudel sobib sellesse konkreetsesse pipeline'i".

**Test set** (`tools/llm-bench/bench_estonian_llms.py`, TEST_CASES):

1. T01 `lülita tuli põlema` → turn_on light.elutuba
2. T02 `tee tuli punaseks` → set_color light.elutuba
3. T03 `kui soe toas on` → get_state sensor.temperatuur
4. T04 `mis kell on` → get_state sensor.kellaaeg
5. T05 `pane magamistoa lamp kinni` → turn_off light.magamistuba (tuba-spetsiifika)
6. T06 `tee elutoas hämar` → set_brightness (intensiivsus tuletamine)
7. T07 `elutoas on liiga pime` → turn_on (kaudne käsk, konteksti järeldamine)
8. T08 `pane kohv käima ja elutoa tuli põlema` → mitu actionit ühes lauses

**Tulemused**:

| Mudel | Õiged intent'id | JSON kehtiv | Keskmine latency | Kvalitatiivne märkus |
|---|---|---|---|---|
| gemma3:12b | 6/8 (75%) | 8/8 (100%) | 3.0s | 2 viga: `get_state` schema `{"get_state": "..."}` formaadis (peab olema `{"action": "get_state", "entity_id": "..."}`) |
| qwen2.5:14b | 5/8 (62%) | 8/8 (100%) | 3.3s | Schema õige aga **eesti keel on nõrk** — fabritseeritud sõnu ("mustva", "Magamistoo lamppuga", "Seishestsin", "päin") |
| alibayram/erurollm-9b-instruct | 0/8 (0%) | 8/8 (100%) | 4.1s | JSON on kehtiv aga `actions` array on alati tühi — mudel ei järgi süsteempromptis antud tool schema'd |
| gemma4:e4b (apr 2026) | 7/8 (88%) | 8/8 (100%) | 4.4s | **Parim JSON** — natiivne tool calling. Aga eesti keel nõrk: fabritseeritud sõnu ("Käistan", "heleksema", "all"). T07 valis `set_brightness 255` asemel `turn_on` (piiripealne) |
| gemma4:26b (apr 2026) | 5/8 (62%) | 7/8 (88%) | 15.0s | Liiga aeglane (3× piir). 1 JSON parse error. OOM risk 32GB-l. Fabritseeritud sõnu ("sülitud", "kustetud", "häämar") |

### C telg: latency mõõtmine

Lühike prompt eval + 30 tokenit genereerimist, 5 korduse keskmine:

| Mudel | Prompt eval (cold) | Generation | Genereerimiskiirus |
|---|---|---|---|
| gemma3:12b | ~2.0s | ~2.2s | ~15 tok/s |
| qwen2.5:14b | TBD | TBD | TBD |
| alibayram/erurollm-9b-instruct | ~0.8s | ~2.5s | ~12 tok/s |

## Sünteesitud tulemused

### Telgedel läbitehtud võrdlus

| Kriteerium | Gemma 3 12B | Qwen 2.5 14B | EuroLLM 9B | Gemma 4 E4B | Gemma 4 26B MoE |
|---|---|---|---|---|---|
| A: Eesti keel (arxivi paper, 7 taski keskmine) | 0.354 | *(andmed puuduvad)* | **0.409** | *(andmed puuduvad)* | *(andmed puuduvad)* |
| A: Eesti keel (meie, 2 taski exact_match) | 0.32 | 0.03 | **0.48** | 0.045 | *(OOM crash)* |
| B: Kratt JSON eval | **75%** | 62% | 0% | **88%** | 62% |
| C: Latency (mediaan) | **3.0s** | 3.3s | 4.1s | 4.4s | 15.0s |
| JSON kehtivus | 100% | 100% | 100% | 100% | 88% |
| **Otsuse skoor** | **Valitud** | Välja: eesti keel | Blocked: 0% JSON | Välja: eesti keel 0.045 | Välja: OOM + 15s latency |

### Järeldus

**Valitud mudel kasutajatestideks**: `gemma3:12b`. Viiest testitud mudelist ainus mis pakub mõlemal
teljel (eesti keele kvaliteet + JSON instruction-following) aktsepteeritavat taset.

**Gemma 4 generatsiooni tähelepanek**: Gemma 4 (apr 2026) tõi olulise tool calling paranemise —
E4B saavutas 88% JSON intent skooril (vs Gemma 3 75%) vaatamata väiksemale mudelile. Aga eesti
keele kvaliteet langes dramaatiliselt (inflection 2% vs 36%), mis tähendab et Gemma 4 natiivne
multilinguality ei kata eesti keelt piisavalt väiksemates mudelites. 26B MoE variant on M1 Pro
32GB-l ebastabiilne (OOM pärast 35 min) ja liiga aeglane (15s mediaan vs 5s piir).

**Keskpikaks tulevikuks**: tasub uurida, kas EuroLLM 9B-d saab saada töötama, kui süsteemprompti
täiendada few-shot näidetega või kasutada grammar-guided decoding'ut. Kui see õnnestuks, saaks kasutaja
paremat eesti keelt ja väiksemat mudelit (9B vs 12B → vähem RAM-i, kiirem inference). Samuti väärib
jälgimist Gemma 4 suurem dense variant (31B), mis nõuab rohkem RAM-i kui meie riistvara pakub.

**Pikaajaliselt**: kasutajatestis mõõta user-satisfaction scores
(küsimustik D1 "Süsteem sai hästi aru minu eestikeelsest kõnest" ja D2 "vastused olid
loomuliku kõlaga") — kui osalejad hindavad Gemma vastused madalalt, tuleks tagasi EuroLLM juurde ja
lahendada instruction-following probleem.

## Piirangud ja avatud küsimused

1. **Test set size**: Kratt eval on n=8 lausega, meie EuroEval run on n=100 per task. Lõputöös tuleb
   selgelt märkida et tulemused ei ole üldistatavad — need on sõelunemise tööriistad, mitte lõplikud
   hinnangud.
2. **Q4 kvantiseerimine**: kõik mudelid jooksevad 4-bit kvantiseeritud kujul (Ollama default). Arxiv
   paperi tulemused on tõenäoliselt full-precision. Meie tulemused võivad olla 1-3 protsendipunkti
   madalamad kvantiseerimise tõttu. See on mainida.
3. **Temperatuur ja sampling**: Ollama default'is temperature=0.8. LM-eval harness võib kasutada
   deterministlikumat sampling'ut. See mõjutab korratavust.
4. **Qwen 2.5 puudub arxivi paperist**: me ei saa meie enda mõõtmist otse kirjanduse vastu kõrvutada.
5. **Süsteemprompt pole identne**: arxivi paper kasutab lühikest ekspertprompti, meie kasutame
   Kratt-spetsiifilist. See tähendab et meie numbrid ei ole otse paperiga võrreldavad — peame jooksutama
   samal süsteempromptil et teha fair võrdlust.

## Viited

- Alumäe, T. et al. (2025). "Estonian Native Large Language Model Benchmark." arXiv:2510.21193.
- EuroEval Estonian: https://euroeval.com/datasets/estonian/
- TalTech lm-eval tasks: https://github.com/taltechnlp/lm-eval-harness-tasks-estonian
- EleutherAI lm-evaluation-harness: https://github.com/EleutherAI/lm-evaluation-harness
- Meie Kratt-spetsiifiline eval set: `tools/llm-bench/bench_estonian_llms.py`
- Google DeepMind (2026). "Gemma 4." https://deepmind.google/models/gemma/gemma-4/
- Gemma 4 Ollama: https://ollama.com/library/gemma4
