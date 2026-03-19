#!/usr/bin/env python3
"""Live microphone test for a microWakeWord TFLite model.

Usage:
    python live_test_tflite.py --model path/to/model.tflite [--threshold 0.5]

Press Ctrl+C to stop.
"""

import argparse
import sys
import numpy as np

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    import tensorflow.lite as tflite


def make_interpreter(model_path: str):
    interp = tflite.Interpreter(model_path=model_path)
    interp.allocate_tensors()
    return interp


def main():
    parser = argparse.ArgumentParser(description="Live wake-word test")
    parser.add_argument("--model", required=True, help="Path to .tflite model")
    parser.add_argument("--threshold", type=float, default=0.5, help="Detection threshold")
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--frame-ms", type=int, default=10, help="Frame size in ms (match model step_ms)")
    parser.add_argument("--cooldown", type=float, default=2.0, help="Seconds to suppress after a detection")
    args = parser.parse_args()

    try:
        import sounddevice as sd
    except ImportError:
        print("Install sounddevice: pip install sounddevice")
        sys.exit(1)

    try:
        from pymicro_features import MicroFrontend
    except ImportError:
        print("Install pymicro-features: pip install 'git+https://github.com/puddly/pymicro-features@puddly/minimum-cpp-version'")
        sys.exit(1)

    interpreter = make_interpreter(args.model)
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Print model info
    print(f"Model: {args.model}")
    print(f"Inputs: {len(input_details)}")
    for i, d in enumerate(input_details):
        print(f"  [{i}] {d['name']}: shape={d['shape']} dtype={d['dtype']}")
    print(f"Outputs: {len(output_details)}")
    for i, d in enumerate(output_details):
        print(f"  [{i}] {d['name']}: shape={d['shape']} dtype={d['dtype']}")
    print(f"Threshold: {args.threshold}")
    print()

    # The streaming TFLite model expects one spectrogram frame at a time.
    # Each frame = 1 x num_features (typically 1 x 40).
    # State tensors are carried between invocations.
    frontend = MicroFrontend()
    process_fn = getattr(frontend, "process_samples", None) or getattr(frontend, "ProcessSamples", None)

    frame_samples = int(args.sample_rate * args.frame_ms / 1000)  # 160 samples per 10ms
    frame_bytes = frame_samples * 2  # int16

    # Identify input: the audio feature input vs state inputs
    audio_input_idx = 0  # typically index 0

    # Initialize state tensors
    for i, detail in enumerate(input_details):
        interpreter.set_tensor(detail['index'], np.zeros(detail['shape'], dtype=detail['dtype']))

    print(f"Listening... say 'marvin'! (threshold={args.threshold})")
    print("=" * 50)

    import time

    audio_buffer = bytearray()
    detection_count = 0
    last_detection_time = 0.0

    def audio_callback(indata, frames, time_info, status):
        nonlocal audio_buffer
        if status:
            print(f"  [audio status: {status}]", file=sys.stderr)
        # Convert float32 -> int16 bytes
        int16_data = (indata[:, 0] * 32768).clip(-32768, 32767).astype(np.int16)
        audio_buffer.extend(int16_data.tobytes())

    with sd.InputStream(samplerate=args.sample_rate, channels=1, dtype='float32',
                        blocksize=frame_samples, callback=audio_callback):
        try:
            while True:
                # Process when we have enough audio
                while len(audio_buffer) >= frame_bytes:
                    chunk = bytes(audio_buffer[:frame_bytes])
                    del audio_buffer[:frame_bytes]

                    result = process_fn(chunk)
                    if not result.features:
                        continue

                    features = np.array(result.features, dtype=np.float32)
                    # Reshape to match model input (e.g. [1, 1, 40])
                    expected_shape = input_details[audio_input_idx]['shape']
                    features = features.reshape(expected_shape)

                    # Quantize input if model expects int8
                    inp_dtype = input_details[audio_input_idx]['dtype']
                    if inp_dtype == np.int8:
                        scale, zero_point = input_details[audio_input_idx]['quantization']
                        features = (features / scale + zero_point).clip(-128, 127).astype(np.int8)

                    interpreter.set_tensor(input_details[audio_input_idx]['index'], features)
                    interpreter.invoke()

                    # Get probability output and dequantize
                    output = interpreter.get_tensor(output_details[0]['index'])
                    out_dtype = output_details[0]['dtype']
                    if out_dtype in (np.int8, np.uint8):
                        scale, zero_point = output_details[0]['quantization']
                        prob_val = float((output.astype(np.float32) - zero_point) * scale)
                    else:
                        prob_val = float(output.flatten()[0])

                    now = time.monotonic()
                    in_cooldown = (now - last_detection_time) < args.cooldown

                    if prob_val > args.threshold and not in_cooldown:
                        detection_count += 1
                        last_detection_time = now
                        print(f"  >>> DETECTED 'marvin'! (prob={prob_val:.3f}, count={detection_count}) <<<")
                        # Reset model state to avoid retriggering
                        for i, detail in enumerate(input_details):
                            interpreter.set_tensor(detail['index'], np.zeros(detail['shape'], dtype=detail['dtype']))
                    elif prob_val > 0.1 and not in_cooldown:
                        bar = "█" * int(prob_val * 30)
                        print(f"  {prob_val:.3f} {bar}", end="\r")

                time.sleep(0.005)

        except KeyboardInterrupt:
            print(f"\n\nStopped. Total detections: {detection_count}")


if __name__ == "__main__":
    main()
