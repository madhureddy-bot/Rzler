#!/usr/bin/env bash
set -euo pipefail

echo "===== Booting ROMP API via start.sh ====="

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

# Install OpenCV runtime libraries if they’re missing
need_pkg=false
for pkg in libgl1 libglib2.0-0; do
  if ! dpkg -s "${pkg}" >/dev/null 2>&1; then
    need_pkg=true
    break
  fi
done

if [ "${need_pkg}" = true ]; then
  echo "Installing libgl1/libglib2.0-0 for OpenCV..."
  apt-get update -y
  apt-get install -y --no-install-recommends libgl1 libglib2.0-0
  rm -rf /var/lib/apt/lists/*
fi

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

# Tell the service where to find ROMP
export ROMP_COMMAND="${ROMP_COMMAND:-/app/.venv/bin/romp}"

# Prepare ROMP models if they’re missing (/root/.romp by default)
ROMP_CACHE_DIR="${HOME}/.romp"
if [ ! -f "${ROMP_CACHE_DIR}/SMPL_NEUTRAL.pth" ]; then
  echo "Preparing ROMP models..."
  /app/.venv/bin/python -m romp.prepare_models --models smpl
fi

echo "PATH is: ${PATH}"
echo "PYTHONPATH is: ${PYTHONPATH}"
echo "ROMP_COMMAND is: ${ROMP_COMMAND}"

echo "Starting up ROMP API (uvicorn)..."
exec /app/.venv/bin/python -m uvicorn romp_pipeline.api.main:app --host "${HOST}" --port "${PORT}"
