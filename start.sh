#!/usr/bin/env bash
set -euo pipefail

echo "===== Booting ROMP API via start.sh ====="

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

# Ensure src is importable without pip install
export PYTHONPATH="$(pwd)/src:${PYTHONPATH:-}"

# Prefer the Railpack virtualenv
if [ -d "/app/.venv" ]; then
  echo "Using venv at /app/.venv"
  export VIRTUAL_ENV="/app/.venv"
  export PATH="/app/.venv/bin:${PATH}"
else
  echo "WARN: /app/.venv not found"
fi

# Install OpenCV runtime libraries if missing (needed for cv2)
if command -v apt-get >/dev/null 2>&1; then
  need_pkg=false
  for pkg in libgl1 libglib2.0-0; do
    if ! dpkg -s "${pkg}" >/dev/null 2>&1; then
      need_pkg=true
      break
    fi
  done
  if [ "${need_pkg}" = true ]; then
    echo "Installing libgl1/libglib2.0-0..."
    apt-get update -y
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0
    rm -rf /var/lib/apt/lists/*
  fi
fi

# Tell the service where to find ROMP
export ROMP_COMMAND="${ROMP_COMMAND:-/app/.venv/bin/romp}"

# Ensure ROMP model cache exists
ROMP_CACHE_DIR="${HOME}/.romp"
SMPL_SRC="/app/data/smpl_models/smpl"
if [ ! -f "${ROMP_CACHE_DIR}/SMPL_NEUTRAL.pth" ]; then
  echo "Preparing ROMP models..."
  mkdir -p "${ROMP_CACHE_DIR}"
  /app/.venv/bin/python -m simple_romp.prepare_models --models smpl --model-dir "${SMPL_SRC}" || true
fi

echo "PATH is: ${PATH}"
echo "PYTHONPATH is: ${PYTHONPATH}"
echo "ROMP_COMMAND is: ${ROMP_COMMAND}"

# Preflight: confirm romp exists and is executable
if [ ! -x "${ROMP_COMMAND}" ]; then
  echo "ERROR: ROMP binary not found at ${ROMP_COMMAND}"
  ls -l /app/.venv/bin || true
fi

echo "Starting up ROMP API (uvicorn)..."
exec /app/.venv/bin/python -m uvicorn romp_pipeline.api.main:app --host "${HOST}" --port "${PORT}"
