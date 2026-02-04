#!/usr/bin/env python3
"""
Test Neurokõne API and generate sample wake word audio.
"""

import requests
import json
from pathlib import Path

def test_neurokone_api(base_url="https://api.neurokone.ee"):
    """
    Test Neurokõne API with different endpoints and configurations.

    API Documentation from TartuNLP:
    - Endpoint: POST /v2
    - Body: {"text": "...", "speaker": "...", "speed": 1.0}
    - Response: WAV audio
    """

    print("🧪 Testing Neurokõne API...")
    print(f"Base URL: {base_url}\n")

    # Test data
    test_cases = [
        {"text": "Kratt", "speaker": "mari", "speed": 1.0},
        {"text": "Kuule Kratt", "speaker": "mari", "speed": 1.0},
        {"text": "Kratt", "speaker": "albert", "speed": 1.0},
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['text']} (speaker: {test_case['speaker']})")

        try:
            # Try /v2 endpoint (from GitHub docs)
            response = requests.post(
                f"{base_url}/v2",
                json=test_case,
                timeout=30
            )

            if response.status_code == 200:
                print(f"  ✅ Success! Received {len(response.content)} bytes")
                print(f"  Content-Type: {response.headers.get('Content-Type', 'unknown')}")

                # Save test audio
                output_dir = Path("../raw/neurokone_test")
                output_dir.mkdir(parents=True, exist_ok=True)

                filename = f"test_{i}_{test_case['speaker']}_{test_case['text'].replace(' ', '_')}.wav"
                output_path = output_dir / filename

                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"  💾 Saved: {output_path}\n")

                return True  # At least one test succeeded
            else:
                print(f"  ❌ Error {response.status_code}: {response.text}\n")

        except requests.exceptions.ConnectionError:
            print(f"  ⚠️  Connection failed to {base_url}")
            print(f"  This might be because:")
            print(f"     - API needs authentication")
            print(f"     - API is self-hosted only")
            print(f"     - Different endpoint URL")
            break
        except Exception as e:
            print(f"  ❌ Error: {e}\n")

    return False

def try_alternative_endpoints():
    """Try alternative API endpoints."""
    print("\n🔍 Trying alternative endpoints...")

    alternatives = [
        "https://neurokone.ee/api",
        "https://api.neurokone.ee",
        "https://neurokone.tartunlp.ai",
    ]

    for url in alternatives:
        print(f"\nTrying: {url}")
        if test_neurokone_api(url):
            return url

    return None

def main():
    print("="*60)
    print("NEUROKÕNE API TEST")
    print("="*60)
    print()

    # Try main endpoint
    if not test_neurokone_api():
        # Try alternatives
        working_url = try_alternative_endpoints()

        if not working_url:
            print("\n" + "="*60)
            print("⚠️  Could not connect to Neurokõne API")
            print("="*60)
            print("\n💡 Next steps:")
            print("1. Check if API requires authentication/API key")
            print("2. Contact TartuNLP for access: https://tartunlp.ai")
            print("3. Consider self-hosting via Docker:")
            print("   git clone https://github.com/TartuNLP/text-to-speech-api")
            print("   docker-compose up")
            print("\n4. Alternative: Use web interface at https://neurokone.ee")
            print("   and download samples manually")
            return

    print("\n" + "="*60)
    print("✅ SUCCESS! Neurokõne API is working")
    print("="*60)
    print("\nNext: Run generate_neurokone_samples.py to create training data")

if __name__ == "__main__":
    main()
