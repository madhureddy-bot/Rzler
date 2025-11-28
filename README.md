# ROMP Pipeline

FastAPI service that runs ROMP (Regression of Multiple People) and SMPL models to turn a single image into normalized anthropometric measurements.

---

## Features
- 🎯 **ROMP-backed inference** – launches the `romp` CLI, validates availability, and surfaces clear errors when the binary is missing.
- 📏 **Measurement extraction** – loads SMPL vertices, computes 20+ length and circumference metrics, and normalizes them to a target height.
- 🌐 **JSON REST interface** – `/measure` accepts either `image_url` or uploaded files; `/health` reports readiness and ROMP availability.
- 🛡️ **Production middleware** – request IDs, structured logging, timeout-aware subprocess execution, and clean resource teardown.
- ⚙️ **Configurable** – environment variables control timeouts, upload size, logging level, and optional API prefixes via `API_V1_STR`.

---

## Requirements
- Python 3.8+
- PyTorch 1.10+
- ROMP binary from `simple-romp`
- SMPL model files downloaded from [smpl.is.tue.mpg.de](https://smpl.is.tue.mpg.de/)
- CUDA GPU recommended (CPU mode works but is slower)

---

## Installation

```bash
# 1. Clone
git clone https://github.com/yourusername/romp-pipeline.git
cd romp-pipeline

# 2. Create and activate virtualenv
python3 -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# 3. Install build prerequisites (needed before smplx/simple-romp)
pip install numpy Cython wheel setuptools

# 4. Install PyTorch/torchvision (pick the build matching your CUDA setup)
pip install torch torchvision

# 5. Install simple-romp (provides the `romp` CLI)
pip install simple-romp

# 6. Install ROMP Pipeline
pip install -e .
```

### Prepare SMPL assets
```bash
romp.prepare_smpl
```
Download the official SMPL models, then place them under `data/smpl_models/` (keep the gender-specific folders intact).

---

## Configuration
- Copy `.env.example` to `.env` (if provided) or set environment variables directly.
- Key settings (see `src/romp_pipeline/api/config.py`):
  - `API_V1_STR`: optional prefix, e.g. `/api/v1`
  - `MAX_UPLOAD_SIZE_BYTES`: defaults to 20 MB
  - `DOWNLOAD_TIMEOUT`, `ROMP_TIMEOUT`: request and subprocess timeouts
  - `BACKEND_CORS_ORIGINS`: comma-separated origins list

---

## Running the API
```bash
romp-api  # or: uvicorn romp_pipeline.api.main:app --host 0.0.0.0 --port 8000 --reload
```
Visit `http://localhost:8000/docs` (or `/{API_V1_STR}/docs`) for interactive Swagger UI.

### Request examples
```bash
# 1) JSON body with image URL
curl -X POST "http://localhost:8000/measure" \
  -H "Content-Type: application/json" \
  -d '{"image_url":"https://example.com/person.jpg","target_height_cm":176}'

# 2) Multipart upload
curl -X POST "http://localhost:8000/measure" \
  -F "image=@person.jpg" \
  -F "target_height_cm=176"

# 3) Health check
curl http://localhost:8000/health
```
If you set `API_V1_STR=/api/v1`, adjust the paths accordingly (`/api/v1/measure`).

---

## Response format
```json
{
  "measurements": {
    "chest_circumference": 96.12,
    "waist_circumference": 82.77,
    "hip_circumference": 96.68,
    "biceps_circumference": 27.17,
    "thigh_circumference": 48.79,
    "calf_circumference": 35.08
  }
}
```
All values are centimeters and normalized to the supplied `target_height_cm`.

---

## Project layout
```
romp_pipeline/
├── docs/                      # Installation + API guides
├── src/
│   └── romp_pipeline/
│       ├── api/               # FastAPI app, routers, dependencies
│       ├── core/              # Measurement logic and SMPL helpers
│       └── config/            # Shared configuration utilities
├── data/                      # Place SMPL assets here
├── pyproject.toml             # Packaging + dependencies
└── README.md
```

---

## Development
```bash
pip install -e ".[dev]"
pre-commit install  # optional hooks
pytest               # run unit tests
```
Additional tooling:
- `black src/` – formatting
- `ruff check src/` – linting
- `mypy src/` – optional typing pass

---

## Documentation
- [Installation](docs/installation.md)
- [API Usage](docs/api_usage.md)
- [API Architecture](docs/api_architecture.md)
- [Measurement Notes](docs/crotch_measurement_fix.md)

---

## Acknowledgements
- **ROMP** – [github.com/Arthur151/ROMP](https://github.com/Arthur151/ROMP)
- **SMPL / SMPL-X** – [smpl.is.tue.mpg.de](https://smpl.is.tue.mpg.de/)

Please review the upstream licenses before deploying commercially.
