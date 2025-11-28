"""Railpack-compatible entrypoint for the ROMP FastAPI service."""

from romp_pipeline.api.main import app, run_server


if __name__ == "__main__":
    run_server()
