from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import traceback
import logging
from starlette.middleware.base import BaseHTTPMiddleware
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors"""
    async def dispatch(self, request: Request, call_next):
        try:
            # Process the request normally
            return await call_next(request)
        
        except SQLAlchemyError as e:
            # Handle database errors
            logger.error(f"Database error: {str(e)}")

            return JSONResponse(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                content = {"detail": "Database error occured", "type": "database_error"}
            )
        
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(traceback.format_exc())

            # Return a user-friendly error message
            return JSONResponse(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                content = {"detail": "An unexpected error occured", "type": "server_error"}
            )
        
class RequestValidationErrorHandler:
    """Handler for request validation errors"""
    def __init__(self, app: FastAPI):
        @app.exception_handler(Exception)
        async def validation_exception_handler(request, exc):
            return JSONResponse(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                content = {"detail": str(exc), "type": "validation_error"}
            )
        
def add_error_middleware(app: FastAPI):
    """Add error handling middleware to the FastAPI app"""
    app.add_middleware(ErrorMiddleware)
    RequestValidationErrorHandler(app)