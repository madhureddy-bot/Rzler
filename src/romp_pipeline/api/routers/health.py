from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
import torch

from romp_pipeline.api.models.schemas import HealthResponse
from romp_pipeline.api.dependencies import get_romp_service
from romp_pipeline.api.services.romp_service import ROMPService
from romp_pipeline.api.config import settings

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check(
    romp_service: ROMPService = Depends(get_romp_service)
):
    """
    General health check.
    """
    romp_available = romp_service.check_availability()
    
    return HealthResponse(
        status="ready" if romp_available else "degraded",
        romp_available=romp_available,
        device="GPU" if torch.cuda.is_available() else "CPU",
        version=settings.VERSION
    )

@router.get("/health/live")
async def liveness_probe():
    """
    Liveness probe for Kubernetes.
    Returns 200 if the service is running.
    """
    return {"status": "alive"}

@router.get("/health/ready")
async def readiness_probe(
    romp_service: ROMPService = Depends(get_romp_service)
):
    """
    Readiness probe for Kubernetes.
    Returns 200 if the service is ready to accept traffic (ROMP is available).
    """
    if not romp_service.check_availability():
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "detail": "ROMP not available"}
        )
    return {"status": "ready"}
