from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings using Pydantic BaseSettings.
    Reads from environment variables and/or .env file.
    """
    # Project Info
    PROJECT_NAME: str = "ROMP Body Measurement API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = ""
    
    # Environment
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    
    # CORS
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["*"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # File Upload Limits
    MAX_UPLOAD_SIZE_BYTES: int = 20 * 1024 * 1024  # 20 MB
    
    # Timeouts (seconds)
    DOWNLOAD_TIMEOUT: int = 20
    ROMP_TIMEOUT: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True,
        env_file_encoding='utf-8'
    )

settings = Settings()
