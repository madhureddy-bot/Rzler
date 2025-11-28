# API Usage Guide

This guide covers how to run the FastAPI server, call the endpoints, and interpret responses.

---

## Starting the server
```bash
# Simplest option
romp-api

# Custom host/port + autoreload
uvicorn romp_pipeline.api.main:app --host 0.0.0.0 --port 8000 --reload
```
Set environment variables (see `config.py`) before launching if you need a prefix (`API_V1_STR`), stricter upload size, or different CORS origins.

---

## Endpoints
| Method | Path            | Description                                 |
|--------|-----------------|---------------------------------------------|
| POST   | `/measure`      | Run ROMP on an image and return measurements |
| GET    | `/health`       | Report ROMP availability and device info    |
| GET    | `/health/live`  | Liveness probe (always 200 if process up)   |
| GET    | `/health/ready` | Readiness probe (503 when ROMP unavailable) |

If `API_V1_STR` is set (e.g., `/api/v1`), prepend it to each path.

---

## Calling `/measure`
You must provide either an uploaded file or an `image_url`, plus `target_height_cm` (30–300).

### JSON via curl
```bash
curl -X POST "http://localhost:8000/measure" \
  -H "Content-Type: application/json" \
  -d '{
        "image_url": "https://example.com/person.jpg",
        "target_height_cm": 176
      }'
```

### Multipart upload
```bash
curl -X POST "http://localhost:8000/measure" \
  -F "image=@person.jpg" \
  -F "target_height_cm=176"
```

### Python `requests`
```python
import requests

with open("person.jpg", "rb") as fh:
    resp = requests.post(
        "http://localhost:8000/measure",
        files={"image": fh},
        data={"target_height_cm": 176},
    )
print(resp.json())
```

---

## Responses
```json
{
  "measurements": {
    "chest_circumference": 96.12,
    "waist_circumference": 82.77,
    "hip_circumference": 96.68
  }
}
```
Values are expressed in centimeters and normalized to `target_height_cm`.

### Common errors
| Status | Reason                             |
|--------|------------------------------------|
| 400    | Missing file/url or invalid height |
| 413    | File exceeds `MAX_UPLOAD_SIZE_BYTES` |
| 422    | Validation error from FastAPI      |
| 503    | ROMP CLI missing or not reachable  |

Errors use the shared exception handlers defined in `exceptions.py`.

---

## Health probes
```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```
Use `/health/ready` for readiness checks in Kubernetes; it returns 503 if ROMP cannot be executed.

---

## Interactive docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Both reflect the Pydantic schemas under `api/models/schemas.py`.

---

## Deployment notes
- Run `uvicorn` (or `gunicorn -k uvicorn.workers.UvicornWorker`) behind a reverse proxy such as nginx.
- Pin `ROMP_TIMEOUT` based on average processing time; keep it below your ingress timeout.
- Mount a persistent volume containing the SMPL models (`data/smpl_models/`).
- Collect logs via stdout/stderr; each request is tagged with a `correlation_id` by the middleware.

---

## Related docs
- [Installation](installation.md)
- [Architecture](api_architecture.md)
