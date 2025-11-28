#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

# Ensure the src package path is importable without pip-installing the project
export PYTHONPATH="$(pwd)/src:${PYTHONPATH:-}"

exec python -m uvicorn romp_pipeline.api.main:app --host "$HOST" --port "$PORT"

