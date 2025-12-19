#!/usr/bin/env python3
"""
Convert TalTechNLP Estonian Whisper model to CTranslate2 format.
"""
import os
from pathlib import Path

# Use the CTranslate2 converter directly
import ctranslate2

model_name = "TalTechNLP/whisper-medium-et"
output_dir = "./whisper-medium-et-ct2"

print(f"📥 Converting {model_name} to CTranslate2 format...")
print(f"📁 Output directory: {output_dir}")

converter = ctranslate2.converters.TransformersConverter(
    model_name,
    activation_scales=None,
    copy_files=["tokenizer_config.json", "preprocessor_config.json"],
)

output_path = Path(output_dir)
output_path.mkdir(parents=True, exist_ok=True)

print("🔄 Converting (this may take a few minutes)...")
converter.convert(
    output_dir=str(output_path),
    quantization="int8",
    force=True,
)

print(f"✅ Conversion complete!")
print(f"   Model saved to: {output_path.absolute()}")
print(f"\n   Update asr-test.py to use:")
print(f'   WhisperModel("{output_path}", device="cpu", compute_type="int8")')
