from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import api_router

from .middleware.auth_middleware import add_auth_middleware
from .middleware.error_middleware import add_error_middleware
from .middleware.logging_middleware import add_logging_middleware

def create_app():
    # Create FastAPI app
    app = FastAPI(
        title="PDF Retrieval DeepSeek API",
        description="API for retrieving and processing PDF documents, URLs, and YouTube videos",
        version="0.1.0",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Update this with your frontend URL in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add middleware (in order)
    add_logging_middleware(app)  # First to log all requests
    add_error_middleware(app)    # Second to catch errors
    add_auth_middleware(app)     # Third to authenticate requests
    
    # Include routers
    app.include_router(api_router, prefix="/api")
    
    @app.get("/health")
    def health_check():
        """Health check endpoint"""
        return {"status": "healthy"}
    
    return app

app = create_app()