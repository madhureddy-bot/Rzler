#!/usr/bin/env bash
set -euo pipefail

# Railpack calls this script to boot the FastAPI app.
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

# Ensure the src package path is importable without pip-installing the project
export PYTHONPATH="$(pwd)/src:${PYTHONPATH:-}"

# Prefer the Railpack virtualenv so uvicorn, romp, and deps are available
if [ -d "/app/.venv" ]; then
  export VIRTUAL_ENV="/app/.venv"
  export PATH="/app/.venv/bin:${PATH}"
fi

# Optionally force ROMP binary location for the service resolver
export ROMP_COMMAND="${ROMP_COMMAND:-/app/.venv/bin/romp}"

# Start the API
exec python -m uvicorn romp_pipeline.api.main:app --host "${HOST}" --port "${PORT}"
