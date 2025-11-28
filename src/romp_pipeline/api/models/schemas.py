from typing import Dict, Optional
from pydantic import BaseModel, Field, HttpUrl

class MeasureRequest(BaseModel):
    """
    JSON request body for /measure endpoint.
    """
    image_url: HttpUrl = Field(..., description="URL to image file")
    target_height_cm: float = Field(..., ge=30, le=300, description="Target height in cm (30-300)")

class MeasurementResponse(BaseModel):
    """
    Response model for measurements.
    """
    measurements: Dict[str, float] = Field(..., description="Dictionary of body measurements in cm")

class HealthResponse(BaseModel):
    """
    Response model for health check.
    """
    status: str
    romp_available: bool
    device: str
    version: str

class ErrorDetail(BaseModel):
    """
    Standard error detail model.
    """
    detail: str
    code: Optional[str] = None
