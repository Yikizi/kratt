#!/usr/bin/env python3
"""Benchmark local English→Estonian MT models for the Kratt demo pipeline.

The intended runtime shape is flexible, not templated:
    small LLM writes a short canonical English TTS response
    → local MT translates it to Estonian
    → TTS speaks the translated response

This script measures whether the MT step is cheap enough and whether the
translated Estonian is good enough for spoken smart-home replies.
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import re
import statistics
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import psutil
except Exception:  # pragma: no cover - optional dependency
    psutil = None

try:
    import sacrebleu
except Exception:  # pragma: no cover - optional dependency
    sacrebleu = None


ROOT = Path(os.environ.get("KRATT_ROOT", Path(__file__).resolve().parents[2]))
DEFAULT_OUTPUT_ROOT = ROOT / "output" / "translation-bench"


@dataclass(frozen=True)
class TranslationModelSpec:
    key: str
    backend: str
    model_id: str
    label: str
    size_note: str
    default_compute_type: str = "default"


MODEL_SPECS: dict[str, TranslationModelSpec] = {
    "opus": TranslationModelSpec(
        key="opus",
        backend="transformers-marian",
        model_id="Helsinki-NLP/opus-mt-en-et",
        label="OPUS-MT en→et",
        size_note="~300 MB weights",
    ),
    "opus-big": TranslationModelSpec(
        key="opus-big",
        backend="transformers-marian",
        model_id="Helsinki-NLP/opus-mt-tc-big-en-et",
        label="OPUS-MT TC-big en→et",
        size_note="~470 MB safetensors",
    ),
    "opus-ct2-int8": TranslationModelSpec(
        key="opus-ct2-int8",
        backend="ctranslate2-marian-spm",
        model_id="manancode/opus-mt-en-et-ctranslate2-android",
        label="OPUS-MT CTranslate2 int8 en→et",
        size_note="~76 MB CT2 int8 model.bin",
        default_compute_type="int8",
    ),
    "nllb-600m": TranslationModelSpec(
        key="nllb-600m",
        backend="transformers-nllb",
        model_id="facebook/nllb-200-distilled-600M",
        label="NLLB-200 distilled 600M en→et",
        size_note="~2.5 GB weights",
    ),
}


@dataclass(frozen=True)
class BenchCase:
    id: str
    source_en: str
    reference_et: str
    tags: tuple[str, ...] = ()


BENCH_CASES: list[BenchCase] = [
    BenchCase("light_on_1", "Sure, I turned the lights on.", "Jah, panin tuled põlema.", ("light",)),
    BenchCase("light_on_2", "Done — <LIGHT_1> is on now.", "Valmis, <LIGHT_1> põleb nüüd.", ("light", "placeholder")),
    BenchCase("light_off_1", "All set, I switched the bedroom light off.", "Valmis, lülitasin magamistoa lambi välja.", ("light",)),
    BenchCase("dim_1", "I made the lights a little dimmer.", "Tegin tuled natuke hämaramaks.", ("light",)),
    BenchCase("brightness_1", "I set the brightness to twenty percent.", "Seadsin heleduse kahekümne protsendi peale.", ("light",)),
    BenchCase("brightness_2", "<ROOM_1> is already at the requested brightness.", "<ROOM_1> on juba soovitud heledusega.", ("light", "placeholder")),
    BenchCase("warm_white", "I changed the light to warm white.", "Muutsin tule sooja valge peale.", ("light",)),
    BenchCase("blue", "I made the lights blue.", "Panin tuled siniseks.", ("light", "color")),
    BenchCase("placeholder_color", "I have set <LIGHT_1> to <COLOR_1>.", "Seadsin <LIGHT_1> värviks <COLOR_1>.", ("light", "placeholder", "color")),
    BenchCase("unreachable", "I couldn't reach the bulb right now.", "Ma ei saanud pirniga praegu ühendust.", ("error",)),
    BenchCase("not_found", "I couldn't find that device. Which light did you mean?", "Ma ei leidnud seda seadet. Millist lampi sa mõtlesid?", ("error", "clarify")),
    BenchCase("ambiguous", "I found two lights. Do you mean the living room or the bedroom?", "Leidsin kaks lampi. Kas mõtled elutuba või magamistuba?", ("clarify",)),
    BenchCase("already_off", "The light is already off.", "Tuli on juba kustus.", ("state",)),
    BenchCase("state", "The living room light is on at half brightness.", "Elutoa lamp põleb poole heledusega.", ("state",)),
    BenchCase("weather_hold", "One moment, I'm checking the weather.", "Üks hetk, vaatan ilma.", ("weather",)),
    BenchCase("weather_state", "In Tallinn it is currently five degrees and cloudy.", "Tallinnas on praegu viis kraadi ja pilves.", ("weather",)),
    BenchCase("rain", "It looks like rain later today.", "Tundub, et täna hiljem võib vihma tulla.", ("weather",)),
    BenchCase("jacket", "You probably do not need a jacket.", "Tõenäoliselt pole sul jopet vaja.", ("weather",)),
    BenchCase("time", "The time is quarter past seven.", "Kell on veerand kaheksa.", ("time",)),
    BenchCase("date", "Tomorrow is Monday.", "Homme on esmaspäev.", ("date",)),
    BenchCase("capabilities_1", "I can control lights, brightness, colors, and simple effects.", "Ma saan juhtida tulesid, heledust, värve ja lihtsaid efekte.", ("capabilities",)),
    BenchCase("capabilities_2", "I can also tell the time, date, and weather.", "Saan öelda ka kellaaega, kuupäeva ja ilma.", ("capabilities",)),
    BenchCase("repeat", "I didn't quite catch that. Could you say it again?", "Ma ei saanud päris aru. Kas sa saaksid seda korrata?", ("clarify",)),
    BenchCase("specific", "I can help, but please ask that a bit more specifically.", "Saan aidata, aga küsi palun veidi täpsemalt.", ("clarify",)),
    BenchCase("unsupported", "I can't do that yet, but I can control the lights.", "Seda ma veel teha ei saa, aga saan tulesid juhtida.", ("error",)),
    BenchCase("effect_start", "I started a short disco effect.", "Käivitasin lühikese diskoefekti.", ("effect",)),
    BenchCase("effect_stop", "I stopped the effect.", "Peatasin efekti.", ("effect",)),
    BenchCase("helper", "I'll ask the helper model and keep the answer short.", "Küsin abimudelilt ja hoian vastuse lühikese.", ("helper",)),
    BenchCase("advice", "Here's a short answer: turn it off at the wall first.", "Lühike vastus: lülita see kõigepealt seinast välja.", ("helper",)),
    BenchCase("unsupported_color", "I found <DEVICE_1>, but it does not support color changes.", "Leidsin <DEVICE_1>, aga see ei toeta värvi muutmist.", ("error", "placeholder")),
]


PLACEHOLDER_RE = re.compile(r"<[A-Z][A-Z0-9_]*>")
ENGLISH_LEAK_RE = re.compile(
    r"\b(sure|done|light|lights|room|device|brightness|color|weather|time|date|"
    r"please|sorry|could|would|turn|turned|switch|switched|already|currently)\b",
    flags=re.I,
)


@dataclass
class CaseResult:
    id: str
    source_en: str
    reference_et: str
    output_et: str
    latency_ms: int
    chrf: float | None
    placeholders_expected: list[str] = field(default_factory=list)
    placeholders_found: list[str] = field(default_factory=list)
    placeholder_ok: bool = True
    english_leak: bool = False
    too_long_for_tts: bool = False
    tags: list[str] = field(default_factory=list)


@dataclass
class ModelResult:
    key: str
    label: str
    backend: str
    model_id: str
    size_note: str
    device: str
    compute_type: str | None
    load_ms: int
    rss_after_load_mb: float | None
    cases: list[CaseResult]
    error: str | None = None

    def summary(self) -> dict[str, Any]:
        latencies = [c.latency_ms for c in self.cases]
        chrf_scores = [c.chrf for c in self.cases if c.chrf is not None]
        placeholder_cases = [c for c in self.cases if c.placeholders_expected]
        return {
            "key": self.key,
            "label": self.label,
            "backend": self.backend,
            "model_id": self.model_id,
            "device": self.device,
            "compute_type": self.compute_type,
            "size_note": self.size_note,
            "load_ms": self.load_ms,
            "rss_after_load_mb": self.rss_after_load_mb,
            "n_cases": len(self.cases),
            "latency_p50_ms": percentile(latencies, 50),
            "latency_p95_ms": percentile(latencies, 95),
            "latency_mean_ms": round(statistics.mean(latencies), 1) if latencies else None,
            "chrf_mean": round(statistics.mean(chrf_scores), 2) if chrf_scores else None,
            "chrf_corpus": corpus_chrf([c.output_et for c in self.cases], [c.reference_et for c in self.cases]),
            "placeholder_ok_rate": round(sum(c.placeholder_ok for c in placeholder_cases) / len(placeholder_cases), 3)
            if placeholder_cases
            else None,
            "english_leak_count": sum(c.english_leak for c in self.cases),
            "too_long_count": sum(c.too_long_for_tts for c in self.cases),
            "error": self.error,
        }


class BaseEngine:
    def translate(self, text: str) -> str:
        raise NotImplementedError


class TransformersEngine(BaseEngine):
    def __init__(self, spec: TranslationModelSpec, device: str, beams: int, max_new_tokens: int):
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        self.spec = spec
        self.device = resolve_torch_device(device)
        self.beams = beams
        self.max_new_tokens = max_new_tokens
        self.is_nllb = spec.backend == "transformers-nllb"
        tokenizer_kwargs = {"src_lang": "eng_Latn"} if self.is_nllb else {}
        self.tokenizer = AutoTokenizer.from_pretrained(spec.model_id, **tokenizer_kwargs)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(spec.model_id)
        self.model.eval()
        self.model.to(self.device)
        self.torch = torch
        self.nllb_bos = None
        if self.is_nllb:
            self.nllb_bos = self.tokenizer.convert_tokens_to_ids("est_Latn")

    def translate(self, text: str) -> str:
        with self.torch.inference_mode():
            inputs = self.tokenizer([text], return_tensors="pt", truncation=True, padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            generate_kwargs: dict[str, Any] = {
                "max_new_tokens": self.max_new_tokens,
                "num_beams": self.beams,
            }
            if self.nllb_bos is not None:
                generate_kwargs["forced_bos_token_id"] = self.nllb_bos
            output_ids = self.model.generate(**inputs, **generate_kwargs)
            return self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0].strip()


class CTranslate2MarianSpmEngine(BaseEngine):
    def __init__(self, spec: TranslationModelSpec, device: str, compute_type: str, beams: int, max_new_tokens: int):
        import ctranslate2
        import sentencepiece as spm
        from huggingface_hub import snapshot_download

        self.spec = spec
        self.beams = beams
        self.max_new_tokens = max_new_tokens
        self.device = "cpu" if device == "auto" else device
        if self.device not in {"cpu", "cuda"}:
            # CTranslate2 does not use PyTorch MPS; keep this path portable.
            self.device = "cpu"
        self.model_dir = Path(snapshot_download(spec.model_id))
        self.source_sp = spm.SentencePieceProcessor(model_file=str(self.model_dir / "source.spm"))
        self.target_sp = spm.SentencePieceProcessor(model_file=str(self.model_dir / "target.spm"))
        self.translator = ctranslate2.Translator(str(self.model_dir), device=self.device, compute_type=compute_type)

    def translate(self, text: str) -> str:
        pieces = self.source_sp.encode(text, out_type=str) + ["</s>"]
        result = self.translator.translate_batch(
            [pieces],
            beam_size=self.beams,
            max_decoding_length=self.max_new_tokens,
        )[0]
        hyp = [piece for piece in result.hypotheses[0] if piece not in {"</s>", "<pad>"}]
        return self.target_sp.decode(hyp).strip()


def resolve_torch_device(device: str) -> str:
    if device != "auto":
        return device
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


def percentile(values: list[int], p: int) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return float(values[0])
    vals = sorted(values)
    k = (len(vals) - 1) * (p / 100)
    lower = int(k)
    upper = min(lower + 1, len(vals) - 1)
    if lower == upper:
        return float(vals[lower])
    return round(vals[lower] + (vals[upper] - vals[lower]) * (k - lower), 1)


def sentence_chrf(hypothesis: str, reference: str) -> float | None:
    if sacrebleu is None:
        return None
    return round(float(sacrebleu.sentence_chrf(hypothesis, [reference]).score), 2)


def corpus_chrf(hypotheses: list[str], references: list[str]) -> float | None:
    if sacrebleu is None or not hypotheses:
        return None
    return round(float(sacrebleu.corpus_chrf(hypotheses, [references]).score), 2)


def current_rss_mb() -> float | None:
    if psutil is None:
        return None
    return round(psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024), 1)


def protect_placeholders(text: str) -> tuple[str, dict[str, str]]:
    """Replace XML-ish placeholders with short XML tags before MT.

    This is not a response template. It is a safety guard so entity names are not
    translated or mangled by the MT model. Short XML tags such as <x1/> are much
    more stable for OPUS/NLLB than long all-caps sentinel words.
    """
    mapping: dict[str, str] = {}
    protected = text
    for idx, placeholder in enumerate(dict.fromkeys(PLACEHOLDER_RE.findall(text)), start=1):
        token = f"<x{idx}/>"
        mapping[token] = placeholder
        protected = protected.replace(placeholder, token)
    return re.sub(r"\s+", " ", protected).strip(), mapping


def normalize_placeholder_spacing(text: str) -> str:
    # SentencePiece models sometimes detokenize '< LIGHT_1>', '<ROOM_ 1>', or '< x1 />'.
    text = re.sub(r"<\s*([A-Za-z0-9]+)_\s+([A-Za-z0-9]+)\s*/\s*>", r"<\1_\2/>", text)
    text = re.sub(r"<\s*([A-Za-z0-9]+)_\s+([A-Za-z0-9]+)\s*>", r"<\1_\2>", text)
    text = re.sub(r"<\s*([A-Za-z0-9_]+)\s*/\s*>", r"<\1/>", text)
    text = re.sub(r"<\s*([A-Za-z0-9_]+)\s*>", r"<\1>", text)
    return text


def restore_placeholders(text: str, mapping: dict[str, str]) -> str:
    restored = normalize_placeholder_spacing(text)
    for token, placeholder in mapping.items():
        restored = restored.replace(token, placeholder)
    return re.sub(r"\s+([,.!?])", r"\1", restored).strip()


def build_engine(spec: TranslationModelSpec, device: str, compute_type: str | None, beams: int, max_new_tokens: int) -> BaseEngine:
    if spec.backend in {"transformers-marian", "transformers-nllb"}:
        return TransformersEngine(spec, device=device, beams=beams, max_new_tokens=max_new_tokens)
    if spec.backend == "ctranslate2-marian-spm":
        return CTranslate2MarianSpmEngine(
            spec,
            device=device,
            compute_type=compute_type or spec.default_compute_type,
            beams=beams,
            max_new_tokens=max_new_tokens,
        )
    raise ValueError(f"Unsupported backend: {spec.backend}")


def run_model(
    spec: TranslationModelSpec,
    cases: list[BenchCase],
    *,
    device: str,
    compute_type: str | None,
    beams: int,
    max_new_tokens: int,
    repeat: int,
    protect: bool,
) -> ModelResult:
    print(f"\n=== {spec.key}: {spec.label} ===", flush=True)
    print(f"model: {spec.model_id} ({spec.size_note}); backend={spec.backend}", flush=True)
    load_start = time.perf_counter()
    engine = build_engine(spec, device=device, compute_type=compute_type, beams=beams, max_new_tokens=max_new_tokens)
    load_ms = int((time.perf_counter() - load_start) * 1000)
    rss = current_rss_mb()
    print(f"loaded in {load_ms / 1000:.2f}s; rss={rss} MB", flush=True)

    results: list[CaseResult] = []
    for idx, case in enumerate(cases, start=1):
        latencies: list[int] = []
        output = ""
        source = case.source_en
        mapping: dict[str, str] = {}
        if protect:
            source, mapping = protect_placeholders(source)
        for _ in range(repeat):
            t0 = time.perf_counter()
            output = engine.translate(source)
            latency_ms = int((time.perf_counter() - t0) * 1000)
            if mapping:
                output = restore_placeholders(output, mapping)
            else:
                output = normalize_placeholder_spacing(output)
            latencies.append(latency_ms)
        placeholders_expected = PLACEHOLDER_RE.findall(case.source_en)
        placeholders_found = PLACEHOLDER_RE.findall(output)
        placeholder_ok = sorted(placeholders_expected) == sorted(placeholders_found)
        english_leak = ENGLISH_LEAK_RE.search(output) is not None
        too_long = len(output) > 180 or output.count(".") + output.count("!") + output.count("?") > 3
        result = CaseResult(
            id=case.id,
            source_en=case.source_en,
            reference_et=case.reference_et,
            output_et=output,
            latency_ms=int(statistics.median(latencies)),
            chrf=sentence_chrf(output, case.reference_et),
            placeholders_expected=placeholders_expected,
            placeholders_found=placeholders_found,
            placeholder_ok=placeholder_ok,
            english_leak=english_leak,
            too_long_for_tts=too_long,
            tags=list(case.tags),
        )
        results.append(result)
        print(
            f"[{idx:02d}/{len(cases)}] {case.id:<18} {result.latency_ms:>5} ms  "
            f"chrF={result.chrf if result.chrf is not None else '-':>5}  {output}",
            flush=True,
        )

    # Best effort cleanup before the next model.
    del engine
    gc.collect()
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            torch.mps.empty_cache()
    except Exception:
        pass

    return ModelResult(
        key=spec.key,
        label=spec.label,
        backend=spec.backend,
        model_id=spec.model_id,
        size_note=spec.size_note,
        device=device,
        compute_type=compute_type or spec.default_compute_type if spec.backend.startswith("ctranslate2") else compute_type,
        load_ms=load_ms,
        rss_after_load_mb=rss,
        cases=results,
    )


def write_outputs(results: list[ModelResult], out_dir: Path, args: argparse.Namespace) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    args_dict = {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()}
    payload = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "args": args_dict,
        "summaries": [r.summary() for r in results],
        "models": [asdict(r) for r in results],
    }
    (out_dir / "results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    with (out_dir / "outputs.tsv").open("w", encoding="utf-8") as f:
        f.write("model\tcase_id\tlatency_ms\tchrf\tplaceholder_ok\tenglish_leak\tsource_en\treference_et\toutput_et\n")
        for r in results:
            for c in r.cases:
                f.write(
                    "\t".join(
                        [
                            r.key,
                            c.id,
                            str(c.latency_ms),
                            "" if c.chrf is None else str(c.chrf),
                            str(c.placeholder_ok),
                            str(c.english_leak),
                            c.source_en.replace("\t", " "),
                            c.reference_et.replace("\t", " "),
                            c.output_et.replace("\t", " "),
                        ]
                    )
                    + "\n"
                )

    lines = [
        "# Kratt translation benchmark",
        "",
        f"Created: `{payload['created_at']}`",
        f"Cases: {len(results[0].cases) if results else 0}; repeat: {args.repeat}; beams: {args.beams}; placeholder protection: {args.protect_placeholders}",
        "",
        "| model | backend | load s | RSS MB | p50 ms | p95 ms | chrF corpus | placeholders | English leaks |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for summary in payload["summaries"]:
        lines.append(
            "| {key} | {backend} | {load:.2f} | {rss} | {p50} | {p95} | {chrf} | {ph} | {leaks} |".format(
                key=summary["key"],
                backend=summary["backend"],
                load=(summary["load_ms"] or 0) / 1000,
                rss=summary["rss_after_load_mb"],
                p50=summary["latency_p50_ms"],
                p95=summary["latency_p95_ms"],
                chrf=summary["chrf_corpus"],
                ph=summary["placeholder_ok_rate"],
                leaks=summary["english_leak_count"],
            )
        )
    lines += ["", "## Sample outputs", ""]
    for r in results:
        lines += [f"### {r.key}", ""]
        for c in r.cases[: min(8, len(r.cases))]:
            lines.append(f"- `{c.id}` EN: {c.source_en}")
            lines.append(f"  - ET: {c.output_et}")
        lines.append("")
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--models",
        nargs="+",
        default=["opus-ct2-int8", "opus", "opus-big"],
        choices=sorted(MODEL_SPECS),
        help="Model keys to benchmark. Default: opus-ct2-int8 opus opus-big",
    )
    parser.add_argument("--include-large", action="store_true", help="Also benchmark nllb-600m (~2.5 GB download).")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of benchmark cases (0 = all).")
    parser.add_argument("--repeat", type=int, default=1, help="Translate each case N times and report median latency.")
    parser.add_argument("--beams", type=int, default=1, help="Beam size for generation/decoding. 1 is fastest.")
    parser.add_argument("--max-new-tokens", type=int, default=96, help="Max output tokens/pieces.")
    parser.add_argument("--device", default="cpu", choices=["cpu", "auto", "cuda", "mps"], help="Inference device. Default: cpu.")
    parser.add_argument("--threads", type=int, default=0, help="Set torch CPU threads (0 = leave default).")
    parser.add_argument("--compute-type", default=None, help="CTranslate2 compute type, e.g. int8, int8_float32, default.")
    parser.add_argument("--protect-placeholders", action="store_true", help="Guard <ENTITY_1>-style placeholders before MT.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Output directory. Default: output/translation-bench/<timestamp>")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.include_large and "nllb-600m" not in args.models:
        args.models.append("nllb-600m")
    if args.threads:
        try:
            import torch

            torch.set_num_threads(args.threads)
            torch.set_num_interop_threads(max(1, min(args.threads, 4)))
        except Exception as exc:
            print(f"warning: could not set torch threads: {exc}", file=sys.stderr)

    cases = BENCH_CASES[: args.limit] if args.limit else BENCH_CASES
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = args.output_dir or DEFAULT_OUTPUT_ROOT / timestamp

    print("Kratt English→Estonian translation benchmark")
    print(f"cases={len(cases)} repeat={args.repeat} beams={args.beams} device={args.device} output={out_dir}")
    if not args.protect_placeholders:
        print("placeholder protection: OFF (raw model behaviour)")
    else:
        print("placeholder protection: ON")

    results: list[ModelResult] = []
    for key in args.models:
        spec = MODEL_SPECS[key]
        try:
            result = run_model(
                spec,
                cases,
                device=args.device,
                compute_type=args.compute_type,
                beams=args.beams,
                max_new_tokens=args.max_new_tokens,
                repeat=args.repeat,
                protect=args.protect_placeholders,
            )
        except Exception as exc:
            print(f"ERROR benchmarking {key}: {exc}", file=sys.stderr)
            result = ModelResult(
                key=spec.key,
                label=spec.label,
                backend=spec.backend,
                model_id=spec.model_id,
                size_note=spec.size_note,
                device=args.device,
                compute_type=args.compute_type,
                load_ms=0,
                rss_after_load_mb=current_rss_mb(),
                cases=[],
                error=str(exc),
            )
        results.append(result)

    write_outputs(results, out_dir, args)

    print("\nSummary")
    for result in results:
        summary = result.summary()
        if result.error:
            print(f"- {result.key}: ERROR {result.error}")
            continue
        print(
            f"- {result.key}: p50={summary['latency_p50_ms']}ms p95={summary['latency_p95_ms']}ms "
            f"chrF={summary['chrf_corpus']} placeholders={summary['placeholder_ok_rate']} "
            f"leaks={summary['english_leak_count']} load={summary['load_ms']/1000:.2f}s"
        )
    print(f"\nWrote: {out_dir / 'summary.md'}")
    print(f"       {out_dir / 'results.json'}")
    print(f"       {out_dir / 'outputs.tsv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
