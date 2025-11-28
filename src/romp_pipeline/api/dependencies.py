import logging
from logging import Logger

from romp_pipeline.api.services.romp_service import ROMPService
from romp_pipeline.api.services.image_service import ImageService
from romp_pipeline.api.services.measurement_service import MeasurementService

# Singleton instances
_romp_service = ROMPService()
_image_service = ImageService()
_measurement_service = MeasurementService()

def get_logger() -> Logger:
    """
    Get application logger. Correlation IDs are injected by middleware/filter.
    """
    logger = logging.getLogger("romp_pipeline.api")
    return logger

def get_romp_service() -> ROMPService:
    """Get ROMP service instance"""
    return _romp_service

def get_image_service() -> ImageService:
    """Get Image service instance"""
    return _image_service

def get_measurement_service() -> MeasurementService:
    """Get Measurement service instance"""
    return _measurement_service
