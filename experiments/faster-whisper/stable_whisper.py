#!/usr/bin/env python3
"""
Quick interactive test of Estonian Whisper with microphone
Requires: pip install transformers torch sounddevice soundfile numpy
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
from transformers import pipeline
import tempfile
import os
import json
import requests
import asyncio
from pywizlight import wizlight, PilotBuilder

print("🎤 Estonian Whisper Voice Test")
print("=" * 50)

# Configuration
SAMPLE_RATE = 16000
DURATION = 5  # seconds
LAMP_IP = "172.20.10.5"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"

# Show available audio input devices
print("\n🎙️  Available input devices:")
devices = sd.query_devices()
input_devices = [
    (i, dev) for i, dev in enumerate(devices) if dev["max_input_channels"] > 0
]

for i, dev in input_devices:
    default_marker = " (DEFAULT)" if i == sd.default.device[0] else ""
    print(f"   [{i}] {dev['name']}{default_marker}")

# Let user select microphone
print("\nSelect input device number (or press Enter for default):")
device_input = input("> ").strip()
DEVICE_ID = int(device_input) if device_input else None

if DEVICE_ID is not None:
    print(f"✅ Using device: {devices[DEVICE_ID]['name']}\n")
else:
    print(f"✅ Using default device\n")

# Estonian color names to RGB mapping
ESTONIAN_COLORS = {
    "punane": (255, 0, 0),
    "roheline": (0, 255, 0),
    "sinine": (0, 0, 255),
    "kollane": (255, 255, 0),
    "oranž": (255, 165, 0),
    "oranžid": (255, 165, 0),
    "lilla": (128, 0, 128),
    "roosa": (255, 192, 203),
    "valge": (255, 255, 255),
    "must": (0, 0, 0),
    "hall": (128, 128, 128),
    "pruun": (165, 42, 42),
    "tsüaan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "türkiis": (64, 224, 208),
    "beež": (245, 245, 220),
}

print("\nLoading TalTech Estonian Whisper model...")
pipe = pipeline(
    "automatic-speech-recognition",
    model="TalTechNLP/whisper-medium-et",
    device="mps",  # Apple Silicon GPU
)
print("✅ Model loaded!\n")


async def send_color_to_lamp(lamp, r, g, b):
    """Send RGB color command to the lamp using pywizlight"""
    try:
        await lamp.turn_on(PilotBuilder(rgb=(r, g, b)))
        print(f"💡 Sent color to lamp: RGB({r}, {g}, {b})")
        return True
    except Exception as e:
        print(f"❌ Failed to send color to lamp: {e}")
        return False


def parse_color_with_llm(text):
    """Use Google Gemini API to extract color or command from Estonian text"""
    prompt = f"""Parse this Estonian voice command: "{text}"

Return ONLY valid JSON with one of these formats:

For colors: {{"action": "color", "color_name": "estonian name", "r": 0-255, "g": 0-255, "b": 0-255}}
For turning on: {{"action": "on"}}
For turning off: {{"action": "off"}}
For no command: {{"action": null}}

Estonian colors: punane=red, sinine=blue, roheline=green, kollane=yellow, oranž=orange, lilla=purple, roosa=pink, valge=white, must=black, hall=gray, pruun=brown.
Modifiers: hele=light, tume=dark.

Estonian commands:
- "sisse" or "peal" or "põlema" = turn on
- "välja" or "kinni" or "ära" = turn off"""

    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 100,
                },
            },
            timeout=10,
        )

        if response.status_code != 200:
            print(f"❌ Gemini API error: {response.status_code}")
            return None, None

        result = response.json()
        response_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()

        # Remove markdown code blocks if present
        response_text = (
            response_text.replace("```json", "")
            .replace("```", "")
            .replace("JSON:", "")
            .strip()
        )

        # Try to find JSON in the response
        if "{" in response_text:
            json_start = response_text.index("{")
            json_end = response_text.rindex("}") + 1
            response_text = response_text[json_start:json_end]

        command_data = json.loads(response_text)
        return command_data

    except requests.Timeout:
        print("❌ Gemini API timeout")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse response: {e}")
        print(f"   Response was: {response_text[:200]}")
        return None
    except Exception as e:
        print(f"❌ Error calling Gemini API: {e}")
        return None


def record_and_transcribe():
    print(f"🔴 Recording for {DURATION} seconds...")
    print("   Say something in Estonian!")

    # Record audio from selected device
    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype=np.float32,
        device=DEVICE_ID,
    )
    sd.wait()
    print("⏹️  Recording stopped.\n")

    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_file = f.name
        sf.write(temp_file, audio, SAMPLE_RATE)

    # Transcribe
    print("🔄 Transcribing...")
    result = pipe(temp_file)

    # Cleanup
    os.unlink(temp_file)

    return result["text"]


async def main():
    """Main loop for voice control"""
    # Initialize WiZ lamp inside async context
    lamp = wizlight(LAMP_IP)

    try:
        while True:
            input("Press Enter to start recording (Ctrl+C to quit)...")
            transcription = record_and_transcribe()
            print("\n" + "=" * 50)
            print("📝 TRANSCRIPTION:")
            print(f"   {transcription}")
            print("=" * 50)

            # Parse and execute command using LLM
            print("🤖 Analyzing command with Gemini API...")
            command = parse_color_with_llm(transcription)

            if command and command.get("action") == "color":
                color_name = command.get("color_name")
                r, g, b = command.get("r"), command.get("g"), command.get("b")
                if color_name and r is not None:
                    print(f"🎨 Detected color: {color_name}")
                    await send_color_to_lamp(lamp, r, g, b)
                else:
                    print("⚠️  Invalid color data")

            elif command and command.get("action") == "on":
                print("💡 Turning lamp ON...")
                try:
                    await lamp.turn_on()
                    print("✅ Lamp turned on")
                except Exception as e:
                    print(f"❌ Failed to turn on lamp: {e}")

            elif command and command.get("action") == "off":
                print("🌙 Turning lamp OFF...")
                try:
                    await lamp.turn_off()
                    print("✅ Lamp turned off")
                except Exception as e:
                    print(f"❌ Failed to turn off lamp: {e}")

            else:
                print("⚠️  No command detected in transcription")

            print()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")


# Run main loop
if __name__ == "__main__":
    asyncio.run(main())
