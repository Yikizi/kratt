#!/usr/bin/env python3
"""Background FPR test - logs all detections with timestamps to file.

Runs silently, logging only false positives. Designed to run for hours
during normal conversation to measure real-world FAPH.

Usage:
    python fpr_test.py --model path/to/model.tflite --threshold 0.9 --log fpr_logs/v7.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

try:
    import sounddevice as sd
except ImportError:
    print("pip install sounddevice")
    sys.exit(1)

try:
    from pymicro_features import MicroFrontend
except ImportError:
    print("pip install 'git+https://github.com/puddly/pymicro-features@puddly/minimum-cpp-version'")
    sys.exit(1)

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    import tensorflow.lite as tflite


def main():
    parser = argparse.ArgumentParser(description="Background FPR logger")
    parser.add_argument("--model", required=True)
    parser.add_argument("--threshold", type=float, default=0.9)
    parser.add_argument("--log", required=True, help="Output JSONL log file")
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--cooldown", type=float, default=2.0)
    parser.add_argument("--name", default=None)
    args = parser.parse_args()

    if args.name is None:
        args.name = Path(args.model).stem

    log_path = Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    interp = tflite.Interpreter(model_path=args.model)
    interp.allocate_tensors()
    input_details = interp.get_input_details()
    output_details = interp.get_output_details()

    frontend = MicroFrontend()
    process_fn = getattr(frontend, "process_samples", None) or getattr(frontend, "ProcessSamples", None)

    frame_samples = int(args.sample_rate * 10 / 1000)
    frame_bytes = frame_samples * 2

    for detail in input_details:
        interp.set_tensor(detail['index'], np.zeros(detail['shape'], dtype=detail['dtype']))

    audio_buffer = bytearray()
    detection_count = 0
    last_detection_time = 0.0
    frame_count = 0
    start_time = time.time()
    start_dt = datetime.now()

    # Write session header
    with open(log_path, "a") as f:
        f.write(json.dumps({
            "event": "session_start",
            "model": args.name,
            "threshold": args.threshold,
            "timestamp": start_dt.isoformat(),
        }) + "\n")

    print(f"FPR test: {args.name} @ {args.threshold}")
    print(f"Log: {log_path}")
    print(f"Started: {start_dt.strftime('%H:%M:%S')}")
    print(f"Listening... (Ctrl+C to stop)")

    def callback(indata, frames, time_info, status):
        nonlocal audio_buffer
        int16 = (indata[:, 0] * 32768).clip(-32768, 32767).astype(np.int16)
        audio_buffer.extend(int16.tobytes())

    with sd.InputStream(samplerate=args.sample_rate, channels=1, dtype='float32',
                        blocksize=frame_samples, callback=callback):
        try:
            while True:
                while len(audio_buffer) >= frame_bytes:
                    chunk = bytes(audio_buffer[:frame_bytes])
                    del audio_buffer[:frame_bytes]

                    result = process_fn(chunk)
                    if not result.features:
                        continue

                    features = np.array(result.features, dtype=np.float32)
                    expected_shape = input_details[0]['shape']
                    features = features.reshape(expected_shape)

                    inp_dtype = input_details[0]['dtype']
                    if inp_dtype == np.int8:
                        scale, zp = input_details[0]['quantization']
                        features = (features / scale + zp).clip(-128, 127).astype(np.int8)

                    interp.set_tensor(input_details[0]['index'], features)
                    interp.invoke()
                    frame_count += 1

                    if frame_count <= 50:
                        continue

                    output = interp.get_tensor(output_details[0]['index'])
                    out_dtype = output_details[0]['dtype']
                    if out_dtype in (np.int8, np.uint8):
                        scale, zp = output_details[0]['quantization']
                        prob = float(((output.astype(np.float32) - zp) * scale).flat[0])
                    else:
                        prob = float(output.flatten()[0])

                    now = time.monotonic()
                    in_cooldown = (now - last_detection_time) < args.cooldown

                    if prob > args.threshold and not in_cooldown:
                        detection_count += 1
                        last_detection_time = now
                        elapsed_h = (time.time() - start_time) / 3600
                        faph = detection_count / elapsed_h if elapsed_h > 0 else 0
                        ts = datetime.now()

                        entry = {
                            "event": "detection",
                            "model": args.name,
                            "prob": round(prob, 4),
                            "count": detection_count,
                            "elapsed_h": round(elapsed_h, 3),
                            "faph": round(faph, 1),
                            "timestamp": ts.isoformat(),
                        }
                        with open(log_path, "a") as f:
                            f.write(json.dumps(entry) + "\n")

                        print(f"  [{ts.strftime('%H:%M:%S')}] #{detection_count} prob={prob:.3f} FAPH={faph:.1f}")

                time.sleep(0.005)

        except KeyboardInterrupt:
            elapsed_h = (time.time() - start_time) / 3600
            faph = detection_count / elapsed_h if elapsed_h > 0 else 0
            end_dt = datetime.now()

            summary = {
                "event": "session_end",
                "model": args.name,
                "threshold": args.threshold,
                "detections": detection_count,
                "elapsed_h": round(elapsed_h, 3),
                "faph": round(faph, 1),
                "timestamp": end_dt.isoformat(),
            }
            with open(log_path, "a") as f:
                f.write(json.dumps(summary) + "\n")

            print(f"\n{'='*50}")
            print(f"Session: {start_dt.strftime('%H:%M:%S')} - {end_dt.strftime('%H:%M:%S')} ({elapsed_h:.1f}h)")
            print(f"Detections: {detection_count}")
            print(f"FAPH: {faph:.1f}")
            print(f"Log: {log_path}")


if __name__ == "__main__":
    main()
