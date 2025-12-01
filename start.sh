ls -l /app/.venv/bin/romp || true
/app/.venv/bin/python -c "import shutil, sys; print(sys.executable); print(shutil.which('romp'))"

#!/usr/bin/env bash
set -euo pipefail

echo "===== Booting ROMP API via start.sh ====="

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

export PYTHONPATH="$(pwd)/src:${PYTHONPATH:-}"

if [ -d "/app/.venv" ]; then
  echo "Using venv at /app/.venv"
  export VIRTUAL_ENV="/app/.venv"
  export PATH="/app/.venv/bin:${PATH}"
else
  echo "WARN: /app/.venv not found"
fi

export ROMP_COMMAND="${ROMP_COMMAND:-/app/.venv/bin/romp}"

echo "PATH is: ${PATH}"
echo "PYTHONPATH is: ${PYTHONPATH}"
echo "ROMP_COMMAND is: ${ROMP_COMMAND}"

if [ ! -x "${ROMP_COMMAND}" ]; then
  echo "ERROR: ROMP binary not found at ${ROMP_COMMAND}"
  ls -l /app/.venv/bin || true
fi

echo "Starting up ROMP API (uvicorn)..."
exec /app/.venv/bin/python -m uvicorn romp_pipeline.api.main:app --host "${HOST}" --port "${PORT}"
