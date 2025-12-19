#!/usr/bin/env python3
"""
Convert HuggingFace Whisper models to CTranslate2 format for faster-whisper.

Usage:
    python convert_model.py TalTechNLP/whisper-medium-et ./whisper-medium-et-ct2
"""

import sys
from pathlib import Path
from transformers import WhisperForConditionalGeneration, WhisperProcessor
import ctranslate2

def convert_whisper_model(model_name: str, output_dir: str, quantization: str = "int8"):
    """
    Convert a HuggingFace Whisper model to CTranslate2 format.

    Args:
        model_name: HuggingFace model ID (e.g., "TalTechNLP/whisper-medium-et")
        output_dir: Directory to save converted model
        quantization: Quantization type (int8, int16, float16, float32)
    """
    print(f"📥 Loading model: {model_name}")
    model = WhisperForConditionalGeneration.from_pretrained(model_name)
    processor = WhisperProcessor.from_pretrained(model_name)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"🔄 Converting to CTranslate2 format ({quantization})...")
    converter = ctranslate2.converters.TransformersConverter(
        model_name_or_path=model_name,
        load_as_float16=False,
    )

    converter.convert(
        output_dir=str(output_path),
        quantization=quantization,
        force=True,
    )

    # Save processor/tokenizer files
    print(f"💾 Saving tokenizer and config...")
    processor.save_pretrained(str(output_path))

    print(f"✅ Model converted successfully to: {output_path}")
    print(f"   Use it with: WhisperModel('{output_path}')")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert_model.py <model_name> <output_dir> [quantization]")
        print("Example: python convert_model.py TalTechNLP/whisper-medium-et ./whisper-medium-et-ct2 int8")
        sys.exit(1)

    model_name = sys.argv[1]
    output_dir = sys.argv[2]
    quantization = sys.argv[3] if len(sys.argv) > 3 else "int8"

    convert_whisper_model(model_name, output_dir, quantization)
