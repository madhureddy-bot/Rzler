import time
import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class RequestMiddleware(BaseHTTPMiddleware):
    """
    Middleware for:
    - Correlation ID generation
    - Request/Response logging
    - Performance tracking
    """
    async def dispatch(self, request: Request, call_next):
        # Generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        
        # Start timer
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"Client: {request.client.host if request.client else 'unknown'}",
            extra={"correlation_id": correlation_id}
        )
        
        try:
            response = await call_next(request)
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            # Calculate duration
            process_time = (time.time() - start_time) * 1000
            
            # Log response
            logger.info(
                f"Response: {response.status_code} "
                f"Duration: {process_time:.2f}ms",
                extra={"correlation_id": correlation_id}
            )
            
            return response
            
        except Exception as e:
            # Log error with duration
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {str(e)} "
                f"Duration: {process_time:.2f}ms",
                extra={"correlation_id": correlation_id}
            )
            raise
