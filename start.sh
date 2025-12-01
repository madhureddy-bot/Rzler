#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

echo "===== Booting ROMP API via start.sh ====="

# 1) Add possible virtualenv locations to PATH so 'python' and other tools come from venv
if [ -d "/app/venv/bin" ]; then
  echo "Using venv at /app/venv"
  export PATH="/app/venv/bin:${PATH}"
fi

if [ -d "/app/.venv/bin" ]; then
  echo "Using venv at /app/.venv"
  export PATH="/app/.venv/bin:${PATH}"
fi

# 2) Put the app root on PATH so our custom ./romp script is visible
export PATH="/app:${PATH}"

echo "PATH is: $PATH"

# 3) Keep src on PYTHONPATH for imports
export PYTHONPATH="$(pwd)/src:${PYTHONPATH:-}"
echo "PYTHONPATH is: $PYTHONPATH"

echo "Starting up ROMP API (uvicorn)..."

exec python -m uvicorn romp_pipeline.api.main:app --host "$HOST" --port "$PORT"
