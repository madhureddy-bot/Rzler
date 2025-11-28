import numpy as np
import torch
from pathlib import Path
from logging import Logger
from typing import Dict, Any

from romp_pipeline.core.measure import MeasureBody
from romp_pipeline.api.exceptions import MeasurementExtractionError

class MeasurementService:
    """Service for extracting measurements from ROMP output"""
    
    EXCLUDED_MEASUREMENTS = {"head circumference", "height", "inside leg height"}
    
    def extract_measurements(self, npz_path: Path, target_height: float, logger: Logger) -> Dict[str, float]:
        """
        Extract measurements from NPZ file.
        
        Args:
            npz_path: Path to NPZ file
            target_height: Target height for normalization
            logger: Logger instance
            
        Returns:
            Dictionary of measurements
        """
        try:
            # Load data
            data = np.load(str(npz_path), allow_pickle=True)
            results = data['results'][()]
            
            if 'verts' not in results:
                raise MeasurementExtractionError("No 'verts' key found in NPZ file")
            
            verts = results['verts']
            
            # Handle shapes
            if len(verts.shape) == 3:  # (frames, vertices, 3)
                verts = verts[0]
            elif len(verts.shape) != 2:
                raise MeasurementExtractionError(f"Unexpected verts shape: {verts.shape}")
            
            # Convert to tensor
            if isinstance(verts, np.ndarray):
                verts = torch.from_numpy(verts).float()
            
            # Measure
            measurer = MeasureBody('smpl')
            measurer.from_verts(verts=verts)
            measurer.measure(measurer.all_possible_measurements)
            
            # Normalize
            measurer.height_normalize_measurements(target_height)
            raw_measurements = measurer.height_normalized_measurements
            
            # Filter and format
            measurements = {
                k: round(float(v), 2)
                for k, v in raw_measurements.items()
                if k not in self.EXCLUDED_MEASUREMENTS
            }
            
            logger.info(f"Extracted {len(measurements)} measurements")
            return measurements
            
        except Exception as e:
            if isinstance(e, MeasurementExtractionError): raise
            logger.exception("Measurement extraction failed")
            raise MeasurementExtractionError(str(e))
        finally:
            # Cleanup GPU memory if needed
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
