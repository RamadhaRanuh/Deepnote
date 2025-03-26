from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
import uuid
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate request ID for tracking
        request_id = str(uuid.uuid4())
        
        # Add request ID to request state for later use
        request.state.request_id = request_id
        
        # Start timer for request duration
        start_time = time.time()
        
        # Log request details
        logger.info(f"Request started | ID: {request_id} | Method: {request.method} | Path: {request.url.path}")
        
        # Process the request
        response = await call_next(request)
        
        # Calculate request duration
        process_time = time.time() - start_time
        
        # Log response details
        logger.info(
            f"Request completed | ID: {request_id} | Method: {request.method} | "
            f"Path: {request.url.path} | Status: {response.status_code} | "
            f"Duration: {process_time:.4f}s"
        )
        
        # Add request ID to response headers for tracking
        response.headers["X-Request-ID"] = request_id
        
        return response

class RequestBodyLoggerMiddleware(BaseHTTPMiddleware):
    """Log request bodies for debugging (use cautiously in production)"""
    async def dispatch(self, request: Request, call_next):
        # Only log request body for specific content types
        if request.headers.get("content-type") == "application/json":
            request_body = await request.body()
            
            # Reset the request body stream
            async def receive():
                return {"type": "http.request", "body": request_body}
            request._receive = receive
            
            # Log request body (be careful with sensitive data)
            try:
                body_str = request_body.decode()
                logger.debug(f"Request body: {body_str}")
            except Exception as e:
                logger.error(f"Failed to decode request body: {str(e)}")
                
        # Continue with the request
        return await call_next(request)

def add_logging_middleware(app: FastAPI):
    """Add logging middleware to the FastAPI app"""
    app.add_middleware(LoggingMiddleware)
    
    # Optional: Add request body logger for development environments
    # app.add_middleware(RequestBodyLoggerMiddleware)