#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./lib/kratt_paths.sh
source "${SCRIPT_DIR}/lib/kratt_paths.sh"

ROOT_DIR="$(kratt_project_root)"
VENV_DIR="${ROOT_DIR}/wake-word/.venv-microwakeword"

resolve_microwakeword_src() {
  local local_src="${ROOT_DIR}/external-repos/microWakeWord"
  if [[ -f "${local_src}/pyproject.toml" || -f "${local_src}/setup.py" ]]; then
    printf '%s\n' "${local_src}"
    return 0
  fi

  # Worktrees under <repo>/.claude/worktrees/<name> usually do not contain the
  # external microWakeWord checkout. Reuse the main checkout if it exists so the
  # local Kratt patches are preserved.
  local main_src=""
  case "${ROOT_DIR}" in
    */.claude/worktrees/*)
      main_src="${ROOT_DIR%%/.claude/worktrees/*}/external-repos/microWakeWord"
      ;;
  esac
  if [[ -n "${main_src}" && ( -f "${main_src}/pyproject.toml" || -f "${main_src}/setup.py" ) ]]; then
    printf '%s\n' "${main_src}"
    return 0
  fi

  # Fresh public checkout fallback. This is slower and may lack Kratt-local
  # patches, but avoids an opaque pip editable-requirement failure.
  if command -v git >/dev/null 2>&1; then
    mkdir -p "${ROOT_DIR}/external-repos"
    git clone --depth 1 https://github.com/kahrendt/microWakeWord.git "${local_src}"
    printf '%s\n' "${local_src}"
    return 0
  fi

  return 1
}

MICROWAKEWORD_SRC="$(resolve_microwakeword_src)" || {
  echo "Could not find or clone microWakeWord source." >&2
  exit 2
}

PYTHON_BIN=""
# Prefer 3.10/3.11 for microWakeWord. On a fresh macOS/uv Python 3.12
# environment pymicro-features can fail to build its C extension because its
# setup passes a C++ standard flag to C sources.
for cand in python3.10 python3.11; do
  if command -v "${cand}" >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v "${cand}")"
    break
  fi
done

UV_BIN="${UV:-}"
if [[ -z "${UV_BIN}" || ! -x "${UV_BIN}" ]]; then
  UV_BIN="$(command -v uv 2>/dev/null || true)"
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  if [[ -n "${PYTHON_BIN}" ]]; then
    "${PYTHON_BIN}" -m venv "${VENV_DIR}"
  elif [[ -n "${UV_BIN}" ]]; then
    echo "No python3.10/3.11 executable found; creating Python 3.10 venv via uv."
    "${UV_BIN}" venv --python '3.10' "${VENV_DIR}"
  else
    echo "No suitable python found. Need python3.10/3.11, or install uv so Kratt can create Python 3.10." >&2
    exit 2
  fi
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

# Fast path for already-prepared HPC environments. Multiple SLURM jobs may call
# this script concurrently; avoid repeated editable uninstall/reinstall cycles
# because they can corrupt the shared .venv-microwakeword while another job is
# importing/training.
if python - <<'PY' >/dev/null 2>&1
import microwakeword
import tensorflow
import pandas
import matplotlib
import tensorboard
import sounddevice
PY
then
  echo "microwakeword environment already ready: ${VENV_DIR}"
  exit 0
fi

# Apply small Kratt compatibility patches when using a fresh upstream
# microWakeWord checkout. The main development checkout may already contain
# these local patches; this block is idempotent.
MICROWAKEWORD_SRC="${MICROWAKEWORD_SRC}" python - <<'PY'
from pathlib import Path
import os

root = Path(os.environ["MICROWAKEWORD_SRC"])

def patch(path: Path, old: str, new: str) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        print(f"warning: patch anchor not found in {path}")
        return
    path.write_text(text.replace(old, new), encoding="utf-8")
    print(f"patched {path.relative_to(root)}")

patch(
    root / "microwakeword" / "audio" / "audio_utils.py",
    """        while audio_idx + 160 * 2 < num_audio_bytes:\n            frontend_result = micro_frontend.process_samples(\n                audio_samples[audio_idx : audio_idx + 160 * 2]\n            )\n""",
    """        # pymicro-features has had API variations over time:\n        # - process_samples (snake_case)\n        # - ProcessSamples (PascalCase)\n        process_fn = getattr(micro_frontend, \"process_samples\", None) or getattr(\n            micro_frontend, \"ProcessSamples\", None\n        )\n        if process_fn is None:\n            raise AttributeError(\n                \"pymicro-features MicroFrontend missing process_samples/ProcessSamples\"\n            )\n        while audio_idx + 160 * 2 < num_audio_bytes:\n            frontend_result = process_fn(\n                audio_samples[audio_idx : audio_idx + 160 * 2]\n            )\n""",
)

patch(
    root / "microwakeword" / "audio" / "spectrograms.py",
    """            spectrogram = generate_features_for_clip(augmented_clip, self.step_ms)\n\n            if self.split_spectrogram_duration_s is not None:\n""",
    """            spectrogram = generate_features_for_clip(augmented_clip, self.step_ms)\n\n            if spectrogram.ndim < 2 or spectrogram.shape[0] == 0:\n                continue\n\n            if self.split_spectrogram_duration_s is not None:\n""",
)

train_py = root / "microwakeword" / "train.py"
if train_py.exists():
    text = train_py.read_text(encoding="utf-8")
    if "def _as_numpy(x):" not in text:
        text = text.replace(
            """from tensorflow.python.util import tf_decorator\n\n\n""",
            """from tensorflow.python.util import tf_decorator\n\n\ndef _as_numpy(x):\n    # Some TF/Keras versions return plain numpy arrays for metrics in evaluate().\n    if hasattr(x, \"numpy\"):\n        return x.numpy()\n    return np.asarray(x)\n\n\n""",
        )
    text = text.replace('result["fp"].numpy()', '_as_numpy(result["fp"])')
    text = text.replace('ambient_predictions["tp"].numpy()', '_as_numpy(ambient_predictions["tp"])')
    text = text.replace('ambient_predictions["fp"].numpy()', '_as_numpy(ambient_predictions["fp"])')
    text = text.replace('ambient_predictions["fn"].numpy()', '_as_numpy(ambient_predictions["fn"])')
    text = text.replace("np.trapz", "np.trapezoid")
    anchor = """        (\n            ambient_testing_fingerprints,\n            ambient_testing_ground_truth,\n            _weights,\n        ) = data_processor.get_data(\n            f\"{test_set}_ambient\",\n            0,\n            config[\"background_frequency\"],\n            config[\"background_volume_range_\"],\n            config[\"time_shift_ms\"],\n            mode=\"testing\",\n            get_file_names=False,\n        )\n        ambient_testing_ground_truth = ambient_testing_ground_truth.reshape(-1, 1)\n\n        # XXX: tf no longer provides a way to evaluate a model without updating metrics\n"""
    repl = """        (\n            ambient_testing_fingerprints,\n            ambient_testing_ground_truth,\n            _weights,\n        ) = data_processor.get_data(\n            f\"{test_set}_ambient\",\n            0,\n            config[\"background_frequency\"],\n            config[\"background_volume_range_\"],\n            config[\"time_shift_ms\"],\n            mode=\"testing\",\n            get_file_names=False,\n        )\n        ambient_testing_ground_truth = ambient_testing_ground_truth.reshape(-1, 1)\n\n        if len(ambient_testing_fingerprints) == 0:\n            logging.warning(\n                \"Ambient set '%s_ambient' produced no split spectrograms; skipping ambient validation metrics.\",\n                test_set,\n            )\n            return metrics\n\n        # XXX: tf no longer provides a way to evaluate a model without updating metrics\n"""
    if "produced no split spectrograms" not in text and anchor in text:
        text = text.replace(anchor, repl)
    train_py.write_text(text, encoding="utf-8")

# Patch TFLite ROC helper for empty ambient/positive sets and NumPy 2.x.
test_py = root / "microwakeword" / "test.py"
if test_py.exists():
    text = test_py.read_text(encoding="utf-8")
    text = text.replace("np.trapz", "np.trapezoid")
    # Keep this conservative: train.py/audio patches are enough for most local
    # smoke runs; full test.py patching is intentionally avoided if upstream has drifted.
    test_py.write_text(text, encoding="utf-8")
PY

# Repair pip if a previous interrupted/concurrent setup left the venv half
# upgraded. ensurepip is idempotent and keeps recovery local to this venv.
python -m ensurepip --upgrade || true
python -m pip install --upgrade pip wheel setuptools

# microWakeWord depends on pymicro-features; on macOS this often needs a fork that
# relaxes build constraints. The fork strips C++ std flags from C sources only
# when the compiler name is clang; fresh macOS may invoke /usr/bin/cc, so force
# clang explicitly when available.
if [[ "$(uname -s)" == "Darwin" ]] && command -v clang >/dev/null 2>&1; then
  CC=clang CXX=clang++ python -m pip install "git+https://github.com/puddly/pymicro-features@puddly/minimum-cpp-version"
else
  python -m pip install "git+https://github.com/puddly/pymicro-features@puddly/minimum-cpp-version"
fi

# Install microWakeWord from our vendored/reused external repo.
echo "Installing microWakeWord from: ${MICROWAKEWORD_SRC}"
python -m pip install -e "${MICROWAKEWORD_SRC}"

# Plotting/reporting dependencies for experiment analysis. TensorBoard is also
# required by tf.summary.scalar during microWakeWord training. sounddevice is
# needed for local live tests with evaluation/live_test_tflite.py.
python -m pip install matplotlib pandas tensorboard sounddevice

python -c "import microwakeword; print('microwakeword import OK')"
