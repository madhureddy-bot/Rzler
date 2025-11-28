import tempfile
from pathlib import Path
from typing import Optional
from logging import Logger

from fastapi import APIRouter, Depends, File, UploadFile, Form, Request

from romp_pipeline.api.models.schemas import MeasureRequest, MeasurementResponse
from romp_pipeline.api.dependencies import (
    get_logger, 
    get_image_service, 
    get_romp_service, 
    get_measurement_service
)
from romp_pipeline.api.services.image_service import ImageService
from romp_pipeline.api.services.romp_service import ROMPService
from romp_pipeline.api.services.measurement_service import MeasurementService
from romp_pipeline.api.exceptions import ImageValidationError

router = APIRouter()

@router.post("/measure", response_model=MeasurementResponse)
async def measure_body(
    request: Request,
    image: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None),
    target_height_cm: Optional[float] = Form(None),
    logger: Logger = Depends(get_logger),
    image_service: ImageService = Depends(get_image_service),
    romp_service: ROMPService = Depends(get_romp_service),
    measurement_service: MeasurementService = Depends(get_measurement_service)
):
    """
    Extract body measurements from an image.
    Supports both JSON (image_url) and multipart/form-data (file upload).
    """
    tmp_path: Optional[Path] = None
    output_dir: Optional[Path] = None
    
    try:
        # 1. Input Parsing & Validation
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            # JSON Request
            try:
                data = await request.json()
                req_model = MeasureRequest(**data)
                url = str(req_model.image_url)
                height = req_model.target_height_cm
                
                tmp_path = image_service.download_image(url, logger)
            except Exception as e:
                raise ImageValidationError(f"Invalid JSON request: {str(e)}")
        else:
            # Form Data / File Upload
            if image:
                if not target_height_cm:
                    raise ImageValidationError("target_height_cm is required")
                height = float(target_height_cm)
                tmp_path = await image_service.save_uploaded_file(image, logger)
            elif image_url:
                if not target_height_cm:
                    raise ImageValidationError("target_height_cm is required")
                height = float(target_height_cm)
                tmp_path = image_service.download_image(image_url, logger)
            else:
                raise ImageValidationError("Either 'image' file or 'image_url' is required")

        # Validate height range
        if not (30.0 <= height <= 300.0):
            raise ImageValidationError("target_height_cm must be between 30 and 300")

        # 2. ROMP Inference
        output_dir = Path(tempfile.mkdtemp())
        npz_path = romp_service.run_inference(tmp_path, output_dir, logger)
        
        # 3. Measurement Extraction
        measurements = measurement_service.extract_measurements(npz_path, height, logger)
        
        return MeasurementResponse(measurements=measurements)

    finally:
        # 4. Cleanup
        if tmp_path:
            image_service.cleanup_file(tmp_path)
        if output_dir:
            image_service.cleanup_dir(output_dir)
