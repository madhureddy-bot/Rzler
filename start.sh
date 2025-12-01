#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

# Make sure Railpack's venv scripts (including `romp`) are discoverable
if [ -d "/app/.venv/bin" ]; then
  export PATH="/app/.venv/bin:${PATH}"
fi

# Ensure the src package path is importable without pip-installing the project
export PYTHONPATH="$(pwd)/src:${PYTHONPATH:-}"

exec python -m uvicorn romp_pipeline.api.main:app --host "$HOST" --port "$PORT"
