from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from romp_pipeline.api.config import settings
from romp_pipeline.api.logging_config import setup_logging
from romp_pipeline.api.middleware import RequestMiddleware
from romp_pipeline.api.routers import measurement, health
from romp_pipeline.api.exceptions import (
    APIException, 
    api_exception_handler, 
    validation_exception_handler,
    general_exception_handler
)
from romp_pipeline.api.dependencies import get_romp_service

# Setup logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    """
    # Startup
    logger.info("Starting up ROMP API...")
    romp_service = get_romp_service()
    if romp_service.check_availability():
        logger.info("ROMP is available")
    else:
        logger.warning("ROMP command not found! API will be degraded.")
        
    yield
    
    # Shutdown
    logger.info("Shutting down ROMP API...")

def create_app() -> FastAPI:
    """
    Application factory.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestMiddleware)

    # Exception Handlers
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Routers
    app.include_router(measurement.router, tags=["measurements"])
    app.include_router(health.router, tags=["health"])

    return app

app = create_app()

def run_server():
    """Run the API server"""
    import uvicorn
    uvicorn.run(
        "romp_pipeline.api.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.DEBUG
    )

if __name__ == "__main__":
    run_server()
