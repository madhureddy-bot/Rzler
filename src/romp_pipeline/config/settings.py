"""Configuration module for ROMP pipeline"""

from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
SMPL_MODELS_DIR = DATA_DIR / "smpl_models"
BODY_MEASUREMENTS_DIR = DATA_DIR / "body_measurements"

# Output directory (default)
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs"

# Measurement settings
DEFAULT_TARGET_HEIGHT_CM = 176.0
MIN_HEIGHT_CM = 30.0
MAX_HEIGHT_CM = 300.0

# API settings
DEFAULT_API_HOST = "0.0.0.0"
DEFAULT_API_PORT = 8000
MAX_UPLOAD_SIZE_MB = 20

# ROMP settings
ROMP_TIMEOUT_SECONDS = 60
