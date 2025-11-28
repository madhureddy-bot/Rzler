import os
import tempfile
import shutil
from pathlib import Path
from urllib.parse import urlparse
import requests
from fastapi import UploadFile
from logging import Logger

from romp_pipeline.api.config import settings
from romp_pipeline.api.exceptions import ImageDownloadError, ImageValidationError

class ImageService:
    """Service for handling image operations"""
    
    def __init__(self):
        pass

    def _validate_url(self, url: str) -> None:
        """Validate URL scheme"""
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ImageValidationError("image_url must be http or https")

    def _get_suffix(self, content_type: str) -> str:
        """Get file extension from content type"""
        if "png" in content_type: return ".png"
        if "webp" in content_type: return ".webp"
        if "jpeg" in content_type or "jpg" in content_type: return ".jpg"
        return ".jpg"  # Default

    def download_image(self, url: str, logger: Logger) -> Path:
        """
        Download image from URL to temporary file.
        
        Args:
            url: Image URL
            logger: Logger instance
            
        Returns:
            Path to downloaded file
        """
        self._validate_url(url)
        
        try:
            with requests.get(url, stream=True, timeout=settings.DOWNLOAD_TIMEOUT) as r:
                if r.status_code != 200:
                    raise ImageDownloadError(f"HTTP {r.status_code}")

                suffix = self._get_suffix(r.headers.get("content-type", ""))
                fd, tmp_path = tempfile.mkstemp(suffix=suffix)
                tmp_path = Path(tmp_path)
                
                total = 0
                with os.fdopen(fd, "wb") as f:
                    for chunk in r.iter_content(8192):
                        if not chunk:
                            continue
                        total += len(chunk)
                        if total > settings.MAX_UPLOAD_SIZE_BYTES:
                            try: os.remove(tmp_path)
                            except Exception: pass
                            raise ImageDownloadError(f"Image too large (>{settings.MAX_UPLOAD_SIZE_BYTES/1024/1024}MB)")
                        f.write(chunk)
                        
            logger.info(f"Downloaded image from {url} to {tmp_path} ({total} bytes)")
            return tmp_path
            
        except requests.RequestException as e:
            raise ImageDownloadError(str(e))
        except Exception as e:
            if isinstance(e, ImageDownloadError): raise
            raise ImageDownloadError(f"Unexpected error: {str(e)}")

    async def save_uploaded_file(self, upload: UploadFile, logger: Logger) -> Path:
        """
        Save uploaded file to temporary path.
        
        Args:
            upload: Uploaded file
            logger: Logger instance
            
        Returns:
            Path to saved file
        """
        if upload.content_type and not upload.content_type.startswith('image/'):
            raise ImageValidationError("File must be an image")
            
        suffix = self._get_suffix(upload.content_type or "")
        fd, tmp_path = tempfile.mkstemp(suffix=suffix)
        tmp_path = Path(tmp_path)
        
        try:
            with os.fdopen(fd, "wb") as f:
                content = await upload.read()
                if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
                    raise ImageValidationError(f"Image too large (>{settings.MAX_UPLOAD_SIZE_BYTES/1024/1024}MB)")
                f.write(content)
                
            logger.info(f"Saved uploaded file to {tmp_path} ({len(content)} bytes)")
            return tmp_path
        except Exception as e:
            if tmp_path.exists():
                try: os.remove(tmp_path)
                except Exception: pass
            if isinstance(e, ImageValidationError): raise
            raise ImageValidationError(f"Failed to save upload: {str(e)}")

    def cleanup_file(self, path: Path) -> None:
        """Safe file cleanup"""
        if path and path.exists():
            try:
                os.remove(path)
            except Exception:
                pass

    def cleanup_dir(self, path: Path) -> None:
        """Safe directory cleanup"""
        if path and path.exists():
            try:
                shutil.rmtree(path)
            except Exception:
                pass
