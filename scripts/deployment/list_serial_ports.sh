#!/usr/bin/env bash
set -euo pipefail

echo "Ports under /dev/cu.*:"
ls -1 /dev/cu.* 2>/dev/null || true
echo
echo "Ports under /dev/tty.*:"
ls -1 /dev/tty.* 2>/dev/null || true

