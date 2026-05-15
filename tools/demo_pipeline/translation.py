from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path

DEFAULT_EN_ET_CT2_MODEL = "manancode/opus-mt-en-et-ctranslate2-android"

PLACEHOLDER_RE = re.compile(r"<[A-Z][A-Z0-9_]*>")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")


@dataclass
class TranslationResult:
    source_text: str
    text: str
    latency_s: float
    ok: bool
    error: str | None = None


class EnglishToEstonianTranslator:
    """Small local EN→ET MT runtime for spoken demo replies.

    Uses a CTranslate2-converted OPUS-MT model. Imports and model download are
    lazy so the normal demo path does not pay for MT unless explicitly enabled.
    """

    def __init__(
        self,
        *,
        model_id: str = DEFAULT_EN_ET_CT2_MODEL,
        device: str = "cpu",
        compute_type: str = "int8",
        beam_size: int = 1,
        max_decoding_length: int = 96,
    ) -> None:
        self.model_id = model_id
        self.device = device
        self.compute_type = compute_type
        self.beam_size = beam_size
        self.max_decoding_length = max_decoding_length
        self.model_dir: Path | None = None
        self._source_sp = None
        self._target_sp = None
        self._translator = None

    @property
    def loaded(self) -> bool:
        return self._translator is not None

    def load(self) -> float:
        """Load/download the MT model. Returns load latency in seconds."""
        if self.loaded:
            return 0.0
        started = time.monotonic()
        import ctranslate2
        import sentencepiece as spm
        from huggingface_hub import snapshot_download

        model_dir = Path(snapshot_download(self.model_id))
        self.model_dir = model_dir
        self._source_sp = spm.SentencePieceProcessor(model_file=str(model_dir / "source.spm"))
        self._target_sp = spm.SentencePieceProcessor(model_file=str(model_dir / "target.spm"))
        device = self.device if self.device in {"cpu", "cuda"} else "cpu"
        self._translator = ctranslate2.Translator(
            str(model_dir),
            device=device,
            compute_type=self.compute_type,
        )
        return time.monotonic() - started

    def translate(self, text: str) -> TranslationResult:
        source_text = (text or "").strip()
        if not source_text:
            return TranslationResult(source_text=source_text, text="", latency_s=0.0, ok=False, error="empty_source")
        if CJK_RE.search(source_text):
            return TranslationResult(source_text=source_text, text="", latency_s=0.0, ok=False, error="source_contains_cjk")
        self.load()
        assert self._source_sp is not None
        assert self._target_sp is not None
        assert self._translator is not None

        protected, placeholders = protect_placeholders(source_text)
        started = time.monotonic()
        try:
            pieces = self._source_sp.encode(protected, out_type=str) + ["</s>"]
            result = self._translator.translate_batch(
                [pieces],
                beam_size=self.beam_size,
                max_decoding_length=self.max_decoding_length,
            )[0]
            hypothesis = [piece for piece in result.hypotheses[0] if piece not in {"</s>", "<pad>"}]
            translated = self._target_sp.decode(hypothesis).strip()
            translated = restore_placeholders(translated, placeholders)
            translated = clean_spoken_translation(translated)
            error = validate_translation(source_text, translated)
            return TranslationResult(
                source_text=source_text,
                text=translated,
                latency_s=time.monotonic() - started,
                ok=error is None,
                error=error,
            )
        except Exception as exc:
            return TranslationResult(
                source_text=source_text,
                text="",
                latency_s=time.monotonic() - started,
                ok=False,
                error=str(exc),
            )


def protect_placeholders(text: str) -> tuple[str, dict[str, str]]:
    mapping: dict[str, str] = {}
    protected = text
    for idx, placeholder in enumerate(dict.fromkeys(PLACEHOLDER_RE.findall(text)), start=1):
        token = f"<x{idx}/>"
        mapping[token] = placeholder
        protected = protected.replace(placeholder, token)
    return re.sub(r"\s+", " ", protected).strip(), mapping


def normalize_placeholder_spacing(text: str) -> str:
    text = re.sub(r"<\s*([A-Za-z0-9]+)_\s+([A-Za-z0-9]+)\s*/\s*>", r"<\1_\2/>", text)
    text = re.sub(r"<\s*([A-Za-z0-9]+)_\s+([A-Za-z0-9]+)\s*>", r"<\1_\2>", text)
    text = re.sub(r"<\s*([A-Za-z0-9_]+)\s*/\s*>", r"<\1/>", text)
    text = re.sub(r"<\s*([A-Za-z0-9_]+)\s*>", r"<\1>", text)
    return text


def restore_placeholders(text: str, mapping: dict[str, str]) -> str:
    restored = normalize_placeholder_spacing(text)
    for token, placeholder in mapping.items():
        restored = restored.replace(token, placeholder)
    return restored


def clean_spoken_translation(text: str) -> str:
    text = normalize_placeholder_spacing(text or "")
    text = text.replace("~", ",")
    text = re.sub(r"\s+([,.!?])", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def validate_translation(source_text: str, translated: str) -> str | None:
    if not translated:
        return "empty_translation"
    if CJK_RE.search(translated):
        return "translation_contains_cjk"
    expected = sorted(PLACEHOLDER_RE.findall(source_text))
    found = sorted(PLACEHOLDER_RE.findall(translated))
    if expected != found:
        return f"placeholder_mismatch expected={expected} found={found}"
    if len(translated) > 260:
        return "translation_too_long"
    return None
