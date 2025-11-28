# ROMP API Architecture

ROMP Pipeline separates concerns into configuration, transport (FastAPI), services, and core measurement logic. This document maps those layers so you know where to add new routes or extend functionality.

---

## Directory overview
```
src/romp_pipeline/api/
├── config.py           # Settings + environment parsing
├── logging_config.py   # Structured logging setup
├── middleware.py       # Correlation IDs, timing, request logging
├── dependencies.py     # FastAPI dependency providers
├── exceptions.py       # Custom exception classes + handlers
├── models/schemas.py   # Pydantic request/response models
├── routers/
│   ├── measurement.py  # /measure endpoint
│   └── health.py       # /health, /health/live, /health/ready
└── services/
    ├── image_service.py        # Download/save/cleanup images
    ├── measurement_service.py  # Load ROMP output and compute metrics
    └── romp_service.py         # Wrap the `romp` subprocess
```
`src/romp_pipeline/core/` contains the SMPL measurement logic shared across services.

---

## Request flow
1. **Middleware (`middleware.py`)** attaches a `correlation_id`, records timing, and logs the start/end of each request.
2. **Router (`routers/measurement.py`)** validates the transport layer (JSON vs. multipart) and delegates to services via `Depends` providers from `dependencies.py`.
3. **Services layer** performs the heavy lifting:
   - `ImageService` downloads or stores the uploaded file and enforces size/format rules.
   - `ROMPService` ensures the `romp` CLI is available, runs it with timeouts, and verifies the `.npz` output.
   - `MeasurementService` loads the `.npz`, converts verts to tensors, computes measurements, and normalizes them.
4. **Response models (`models/schemas.py`)** serialize the measurement dictionary and hand it back to FastAPI.

Errors raised anywhere in the chain bubble up to the global handlers defined in `exceptions.py`, guaranteeing consistent JSON responses (status code + `detail`).

---

## Configuration (`config.py`)
- Central place for environment variables (prefix `ROMP_PIPELINE__` if using `.env`).
- Provides typed settings for API metadata, upload limits, timeouts, and logging level.
- Used by `main.py` during app creation and by services such as `ROMPService` (timeouts) and `ImageService` (size limits).

---

## Logging (`logging_config.py`)
- Uses Python's logging config dict to set JSON or plaintext formatting (depending on `LOG_LEVEL`).
- Injects `correlation_id` from the request context to every log entry.
- Called once at import time from `main.py`.

---

## Extending the API
1. **Add a new service** if you need additional business logic (e.g., storing measurements, queuing jobs).
2. **Expose it via a router**: create a new file in `routers/`, define endpoints, and include it in `main.py` with `app.include_router`.
3. **Define schemas** for requests/responses to keep documentation accurate.
4. **Document dependencies** in `dependencies.py` so they can be overridden in tests.

Because services are pure Python classes, you can reuse them in workers or tests without importing FastAPI.

---

## Health endpoints
`routers/health.py` demonstrates how to build lightweight probes:
- `GET /health` uses `ROMPService.check_availability()` and reports GPU/CPU status (via `torch.cuda.is_available()`).
- `GET /health/live` returns `{"status": "alive"}`; use it for liveness probes.
- `GET /health/ready` returns 503 when ROMP is unavailable, making it suitable for readiness gates.

---

## Measurement core
The `measurement_service` ultimately calls `MeasureBody` from `src/romp_pipeline/core/measure.py`. That module:
- Loads SMPL vertices/joints
- Computes defined measurements from `measurement_definitions.py`
- Supports height normalization and measurement filtering

If you need to expose new anthropometric outputs, update the definitions/core first, then surface them via `MeasurementService`.
