"""
ROMP Pipeline - Body Measurement Pipeline using ROMP and SMPL

This package provides tools for extracting detailed body measurements from images
using ROMP (Regression of Multiple People) and SMPL body models.
"""

__version__ = "1.0.0"

from romp_pipeline.core.measure import MeasureBody

__all__ = ["MeasureBody"]
