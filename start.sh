#!/usr/bin/env bash
set -euo pipefail

# Host/port (Railway will inject PORT)
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

echo "===== Booting ROMP API via start.sh ====="

# 1) Add possible virtualenv locations to PATH so 'romp' CLI is visible
if [ -d "/app/venv/bin" ]; then
  echo "Using venv at /app/venv"
  export PATH="/app/venv/bin:${PATH}"
fi

if [ -d "/app/.venv/bin" ]; then
  echo "Using venv at /app/.venv"
  export PATH="/app/.venv/bin:${PATH}"
fi

echo "PATH is: $PATH"

# 2) Make sure the src/ directory is importable as a package
export PYTHONPATH="$(pwd)/src:${PYTHONPATH:-}"
echo "PYTHONPATH is: $PYTHONPATH"

echo "Starting up ROMP API (uvicorn)..."

# 3) Run the FastAPI app
exec python -m uvicorn romp_pipeline.api.main:app --host "$HOST" --port "$PORT"
