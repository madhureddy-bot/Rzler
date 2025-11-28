from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

class APIException(Exception):
    """Base class for API exceptions"""
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ROMPNotAvailableError(APIException):
    """Raised when ROMP command is not available"""
    def __init__(self):
        super().__init__("ROMP is not installed or not available", status.HTTP_503_SERVICE_UNAVAILABLE)

class ImageDownloadError(APIException):
    """Raised when image download fails"""
    def __init__(self, detail: str):
        super().__init__(f"Failed to download image: {detail}", status.HTTP_400_BAD_REQUEST)

class ImageValidationError(APIException):
    """Raised when image validation fails"""
    def __init__(self, detail: str):
        super().__init__(f"Invalid image: {detail}", status.HTTP_400_BAD_REQUEST)

class MeasurementExtractionError(APIException):
    """Raised when measurement extraction fails"""
    def __init__(self, detail: str):
        super().__init__(f"Measurement extraction failed: {detail}", status.HTTP_500_INTERNAL_SERVER_ERROR)

class ROMPProcessingError(APIException):
    """Raised when ROMP processing fails"""
    def __init__(self, detail: str):
        super().__init__(f"ROMP processing failed: {detail}", status.HTTP_500_INTERNAL_SERVER_ERROR)

async def api_exception_handler(request: Request, exc: APIException):
    """Handle custom API exceptions"""
    logger.error(f"API Exception: {exc.message} (Status: {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.exception("Unexpected error occurred")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )
