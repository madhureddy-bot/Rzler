#!/usr/bin/env bash
set -euo pipefail

# Railpack calls this script to boot the FastAPI app.
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

exec python -m uvicorn romp_pipeline.api.main:app --host "$HOST" --port "$PORT"

