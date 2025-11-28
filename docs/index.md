# ROMP Pipeline (API)

FastAPI service for extracting anthropometric measurements from images using ROMP and SMPL body models.

---

## What It Does

- Runs ROMP for monocular 3D pose estimation
- Converts ROMP outputs into SMPL vertices and joints
- Computes normalized body measurements in centimeters
- Exposes the workflow through REST endpoints (`/api/v1/measure`, `/health`)

---

## Quick Start

1. Follow the [installation guide](installation.md) to install dependencies and SMPL assets.
2. Start the API:
   ```bash
   romp-api  # or: uvicorn romp_pipeline.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```
3. Open http://localhost:8000/docs to explore the OpenAPI schema.
4. Call the measure endpoint:
   ```bash
   curl -X POST "http://localhost:8000/measure" \
     -H "Content-Type: application/json" \
     -d '{"image_url":"https://example.com/person.jpg","target_height_cm":176}'
   ```
   If you set `API_V1_STR`, include the prefix (e.g., `/api/v1/measure`).

---

## Project Layout

```
romp_pipeline/
├── docs/                  # Guides and reference
├── src/romp_pipeline/
│   ├── api/               # FastAPI app, routers, services
│   ├── core/              # Measurement logic and definitions
│   └── config/            # Settings and paths
├── data/                  # SMPL assets (downloaded separately)
├── pyproject.toml         # Packaging and dependencies
└── README.md
```

---

## Measurements at a Glance

- Circumferences: chest, waist, hip, biceps, forearm, thigh, calf, neck, wrist, ankle
- Lengths: height, arm length, leg length, inseam, torso length, shoulder width
- Outputs are height-normalized to the provided `target_height_cm`.

See `src/romp_pipeline/core/measurement_definitions.py` for the full catalog.

---

## Support

- Issues: https://github.com/yourusername/romp-pipeline/issues
- Discussions: https://github.com/yourusername/romp-pipeline/discussions
