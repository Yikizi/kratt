#!/Users/mattias/kratt/.venv-esphome/bin/python
import argparse
import subprocess
import sys
import time

try:
    import serial
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: pyserial. Install with `python3 -m pip install pyserial`."
    ) from exc


MARKER = "DEMO_WAKE_WORD:"


def speak(text: str, voice: str | None) -> None:
    cmd = ["say"]
    if voice:
        cmd.extend(["-v", voice])
    cmd.append(text)
    subprocess.run(cmd, check=False)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Listen for Korvo-2 demo wake-word logs and speak a response."
    )
    parser.add_argument("--port", default="/dev/cu.usbserial-140")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--text", default="Tervist peremees")
    parser.add_argument("--voice", default=None)
    parser.add_argument(
        "--cooldown",
        type=float,
        default=2.5,
        help="Minimum seconds between spoken responses.",
    )
    args = parser.parse_args()

    last_spoken = 0.0

    with serial.Serial(args.port, args.baud, timeout=1) as ser:
        print(f"Listening on {args.port} at {args.baud} baud...", flush=True)
        while True:
            raw = ser.readline()
            if not raw:
                continue
            line = raw.decode("utf-8", errors="replace").strip()
            if line:
                print(line, flush=True)
            if MARKER not in line:
                continue
            now = time.monotonic()
            if now - last_spoken < args.cooldown:
                continue
            last_spoken = now
            speak(args.text, args.voice)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        sys.exit(130)
