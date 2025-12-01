#!/usr/bin/env bash
set -e

# Make sure venv binaries (romp, romp-api, uvicorn, etc.) are on PATH
export PATH="/app/.venv/bin:$PATH"

# romp-api is the console script from [project.scripts] in pyproject.toml
exec romp-api
