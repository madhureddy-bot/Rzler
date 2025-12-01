import os
import subprocess
import sys
import sysconfig
from pathlib import Path
from logging import Logger
from shutil import which
from typing import List, Optional

from romp_pipeline.api.config import settings
from romp_pipeline.api.exceptions import ROMPProcessingError, ROMPNotAvailableError

class ROMPService:
    """Service for running ROMP inference"""

    def __init__(self) -> None:
        self._available: Optional[bool] = None
        self._romp_command: Optional[List[str]] = None

    def _resolve_command_path(self) -> Optional[List[str]]:
        """
        Locate the ROMP executable even when it isn't on PATH.
        Falls back to python -m romp/simple_romp if a console script is missing.
        """
        if self._romp_command:
            head = self._romp_command[0]
            if Path(head).exists():
                return self._romp_command

        candidates = []

        env_cmd = os.environ.get("ROMP_COMMAND")
        if env_cmd:
            expanded = Path(env_cmd).expanduser()
            if expanded.exists():
                candidates.append(expanded)
            else:
                resolved_env = which(env_cmd)
                if resolved_env:
                    candidates.append(Path(resolved_env))

        which_cmd = which("romp")
        if which_cmd:
            candidates.append(Path(which_cmd))

        scripts_dir = sysconfig.get_path("scripts")
        if scripts_dir:
            candidates.append(Path(scripts_dir) / "romp")

            candidates.append(Path(sys.executable).with_name("romp"))

        for candidate in candidates:
            if candidate.exists():
                self._romp_command = [str(candidate)]
                return self._romp_command

        # No CLI shim detected; try module invocation as a fallback
        for module_name in ("romp", "simple_romp"):
            try:
                __import__(module_name)
                self._romp_command = [sys.executable, "-m", module_name]
                return self._romp_command
            except ImportError:
                continue

        self._romp_command = None
        return None

    def check_availability(self) -> bool:
        """Check if ROMP command is available (cached)"""
        if self._available is not None:
            return self._available

        command = self._resolve_command_path()
        if not command:
            self._available = False
            return False

        if not os.access(command[0], os.X_OK):
            self._available = False
            return False

        self._available = True
        return True

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

        command = self._resolve_command_path()
        if not command:
            raise ROMPNotAvailableError()

        romp_cmd = command + [
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
