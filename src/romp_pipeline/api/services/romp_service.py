import os
import subprocess
from pathlib import Path
from logging import Logger
from typing import Optional

from romp_pipeline.api.config import settings
from romp_pipeline.api.exceptions import ROMPProcessingError, ROMPNotAvailableError

class ROMPService:
    """Service for running ROMP inference"""
    
    _available: Optional[bool] = None
    
    def check_availability(self) -> bool:
        """Check if ROMP command is available (cached)"""
        if self._available is not None:
            return self._available
            
        try:
            result = subprocess.run(['romp', '--help'], 
                                  capture_output=True, 
                                  timeout=5)
            self._available = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self._available = False
            
        return self._available

    def run_inference(self, image_path: Path, output_dir: Path, logger: Logger) -> Path:
        """
        Run ROMP on image and return path to NPZ output.
        
        Args:
            image_path: Input image path
            output_dir: Output directory
            logger: Logger instance
            
        Returns:
            Path to generated NPZ file
        """
        if not self.check_availability():
            raise ROMPNotAvailableError()
            
        romp_cmd = [
            "romp",
            "--mode=image",
            "--calc_smpl",
            "--render_mesh",  # Required for verts generation
            f"-i={image_path}",
            f"-o={output_dir}"
        ]
        
        logger.info(f"Running ROMP: {' '.join(romp_cmd)}")
        
        try:
            result = subprocess.run(
                romp_cmd, 
                check=True, 
                capture_output=True, 
                timeout=settings.ROMP_TIMEOUT
            )
            
            if result.stdout:
                logger.debug(f"ROMP stdout: {result.stdout.decode()}")
            if result.stderr:
                logger.debug(f"ROMP stderr: {result.stderr.decode()}")
                
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else "Unknown error"
            logger.error(f"ROMP failed: {error_msg}")
            
            if "out of memory" in error_msg.lower():
                raise ROMPProcessingError("GPU out of memory")
            raise ROMPProcessingError(error_msg)
            
        except subprocess.TimeoutExpired:
            logger.error("ROMP timed out")
            raise ROMPProcessingError("Processing timed out")
            
        # Verify output
        basename = os.path.splitext(os.path.basename(image_path))[0]
        npz_path = output_dir / f"{basename}.npz"
        
        if not npz_path.exists():
            files = list(output_dir.glob("*"))
            logger.error(f"ROMP output missing. Found files: {files}")
            raise ROMPProcessingError("Output file not generated")
            
        # Cleanup PNG
        png_path = output_dir / f"{basename}.png"
        if png_path.exists():
            try:
                os.remove(png_path)
            except Exception:
                pass
                
        return npz_path
