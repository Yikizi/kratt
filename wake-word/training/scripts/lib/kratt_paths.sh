#!/usr/bin/env bash

set -euo pipefail

kratt_project_root() {
  local script_dir
  script_dir="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  if [[ -n "${KRATT_ROOT:-}" ]]; then
    printf '%s\n' "${KRATT_ROOT}"
  else
    printf '%s\n' "$(cd -- "${script_dir}/../../../.." && pwd)"
  fi
}

kratt_data_root() {
  local project_root
  project_root="$(kratt_project_root)"
  if [[ -n "${KRATT_DATA:-}" ]]; then
    printf '%s\n' "${KRATT_DATA}"
  else
    printf '%s\n' "${project_root}/wake-word/data"
  fi
}

kratt_processed_dir() {
  local project_root data_root
  project_root="$(kratt_project_root)"
  data_root="$(kratt_data_root)"
  if [[ -n "${KRATT_PROCESSED_DIR:-}" ]]; then
    printf '%s\n' "${KRATT_PROCESSED_DIR}"
  elif [[ -n "${KRATT_DATA:-}" ]]; then
    printf '%s\n' "${data_root}/processed"
  else
    printf '%s\n' "${project_root}/wake-word/data/processed"
  fi
}

kratt_datasets_dir() {
  local project_root data_root
  project_root="$(kratt_project_root)"
  data_root="$(kratt_data_root)"
  if [[ -n "${KRATT_DATASETS_DIR:-}" ]]; then
    printf '%s\n' "${KRATT_DATASETS_DIR}"
  elif [[ -n "${KRATT_DATA:-}" ]]; then
    printf '%s\n' "${data_root}/datasets"
  else
    printf '%s\n' "${project_root}/wake-word/data/external"
  fi
}

kratt_training_features_dir() {
  local project_root data_root
  project_root="$(kratt_project_root)"
  data_root="$(kratt_data_root)"
  if [[ -n "${KRATT_FEATURES_DIR:-}" ]]; then
    printf '%s\n' "${KRATT_FEATURES_DIR}"
  elif [[ -n "${KRATT_DATA:-}" ]]; then
    printf '%s\n' "${data_root}/training/features"
  else
    printf '%s\n' "${project_root}/wake-word/training/features"
  fi
}

kratt_training_runs_dir() {
  local project_root data_root
  project_root="$(kratt_project_root)"
  data_root="$(kratt_data_root)"
  if [[ -n "${KRATT_RUNS_DIR:-}" ]]; then
    printf '%s\n' "${KRATT_RUNS_DIR}"
  elif [[ -n "${KRATT_DATA:-}" ]]; then
    printf '%s\n' "${data_root}/training/runs"
  else
    printf '%s\n' "${project_root}/wake-word/training/runs"
  fi
}

kratt_training_configs_dir() {
  local project_root
  project_root="$(kratt_project_root)"
  if [[ -n "${KRATT_CONFIGS_DIR:-}" ]]; then
    printf '%s\n' "${KRATT_CONFIGS_DIR}"
  else
    printf '%s\n' "${project_root}/wake-word/training/configs"
  fi
}
