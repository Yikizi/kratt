from __future__ import annotations

import re
import sys
import time
from pathlib import Path

import numpy as np

from tools.demo_pipeline.paths import MODELS_DIR

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    try:
        import tensorflow.lite as tflite
    except ImportError:
        tflite = None

TFLITE_AVAILABLE = tflite is not None
MA_WINDOW = 5

class StreamingModel:
    """Single TFLite wake word model with moving-average smoothing."""

    def __init__(
        self,
        name: str,
        tflite_path: str,
        threshold: float,
        color: str = "",
        use_ma: bool = True,
    ):
        self.name = name
        self.tflite_path = tflite_path
        self.threshold = threshold
        self.color = color
        self.use_ma = use_ma
        self.audio_input_idx = 0
        self._load_interpreter()
        self.detection_count = 0
        self.last_detection_time = 0.0
        self.cooldown_s = 2.0
        self.warmup_frames = 50
        self.required_consecutive = 1
        self.consecutive_hits = 0
        self.frame_count = 0
        self.scores: list[float] = []

        self.reset(clear_cooldown=True)

    def _load_interpreter(self) -> None:
        self.interpreter = tflite.Interpreter(model_path=self.tflite_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def reset(self, *, hard: bool = False, clear_cooldown: bool = False):
        """Reset model state and counters for a fresh detection cycle.

        Always recreate the TFLite interpreter instead of calling
        reset_all_variables(). In live testing, reset_all_variables() left a hot
        state/context window that re-triggered immediately after a valid wake.
        The model is tiny, so interpreter reload is safer for the demo.
        """
        self._load_interpreter()
        for detail in self.input_details:
            self.interpreter.set_tensor(
                detail["index"],
                np.zeros(detail["shape"], dtype=detail["dtype"]),
            )
        if clear_cooldown:
            self.last_detection_time = 0.0
        self.frame_count = 0
        self.consecutive_hits = 0
        self.scores.clear()

    def process_features(self, features: np.ndarray) -> float | None:
        """Process one spectrogram frame. Returns MA probability on detection."""
        expected_shape = self.input_details[self.audio_input_idx]["shape"]
        features = features.reshape(expected_shape)

        inp_dtype = self.input_details[self.audio_input_idx]["dtype"]
        if inp_dtype == np.int8:
            scale, zp = self.input_details[self.audio_input_idx]["quantization"]
            features = (features / scale + zp).clip(-128, 127).astype(np.int8)

        self.interpreter.set_tensor(
            self.input_details[self.audio_input_idx]["index"], features
        )
        self.interpreter.invoke()
        self.frame_count += 1

        if self.frame_count <= self.warmup_frames:
            return None

        output = self.interpreter.get_tensor(self.output_details[0]["index"])
        out_dtype = self.output_details[0]["dtype"]
        if out_dtype in (np.int8, np.uint8):
            scale, zp = self.output_details[0]["quantization"]
            prob = float(((output.astype(np.float32) - zp) * scale).flat[0])
        else:
            prob = float(output.flatten()[0])

        # Moving average (only when use_ma is set, i.e. multi-model mode)
        self.scores.append(prob)
        if len(self.scores) > MA_WINDOW:
            self.scores.pop(0)
        check_prob = sum(self.scores) / len(self.scores) if self.use_ma else prob

        now = time.monotonic()
        if check_prob >= self.threshold:
            self.consecutive_hits += 1
        else:
            self.consecutive_hits = 0

        if (
            self.consecutive_hits >= self.required_consecutive
            and (now - self.last_detection_time) >= self.cooldown_s
        ):
            self.detection_count += 1
            self.last_detection_time = now
            self.consecutive_hits = 0
            return check_prob

        return None


def resolve_models(tags: list[str]) -> list[tuple[str, Path]]:
    """Resolve version tags to (tag, tflite_path) pairs."""
    results = []
    for tag in tags:
        tflite_path = MODELS_DIR / f"kuule-kratt-{tag}" / f"kuule_kratt_{tag}.tflite"
        if not tflite_path.exists():
            print(f"  Model not found: {tflite_path}")
            available = sorted(
                d.name.replace("kuule-kratt-", "")
                for d in MODELS_DIR.glob("kuule-kratt-v*")
                if (
                    d / f"kuule_kratt_{d.name.replace('kuule-kratt-', '')}.tflite"
                ).exists()
            )
            print(f"  Available: {', '.join(available)}")
            sys.exit(1)
        results.append((tag, tflite_path))
    return results


def _version_sort_key(d):
    """Sort key for version directories: v1, v2, ..., v9, v10, v11, ..., v6-residual."""
    import re

    tag = d.name.replace("kuule-kratt-", "")
    m = re.match(r"v(\d+)(.*)", tag)
    if m:
        return (int(m.group(1)), m.group(2))
    return (0, tag)


def find_latest_model() -> str:
    """Find latest version tag by version sort (matches `sort -V`)."""
    dirs = sorted(MODELS_DIR.glob("kuule-kratt-v*"), key=_version_sort_key)
    for d in reversed(dirs):
        tag = d.name.replace("kuule-kratt-", "")
        if (d / f"kuule_kratt_{tag}.tflite").exists():
            return tag
    sys.exit("No wake word models found in " + str(MODELS_DIR))
