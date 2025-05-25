"""
TheRegiment - FastAPI Main Application
Phase 3: API Layer Implementation
"""

import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv
import logging
from typing import Dict, Any

# Load environment variables
load_dotenv()

# Import route modules
from .routes import clients, meals, training, cardio, checkins, job_cards, templates

# Import structured logger
from ..core.logging.logger import setup_logger, log_event

# Setup logger for API module
logger = setup_logger("api.main", os.getenv("LOG_LEVEL", "INFO"))

# Initialize FastAPI app
app = FastAPI(
    title="TheRegiment API",
    description="Military-grade fitness coaching system API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://127.0.0.1:3000",
        # Add production origins here
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle 422 validation errors with detailed response."""
    log_event(
        level="WARNING",
        message="Request validation failed",
        context={
            "url": str(request.url),
            "method": request.method,
            "errors": exc.errors(),
            "body": exc.body if hasattr(exc, 'body') else None
        }
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "message": "Request data does not match required schema"
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with logging."""
    log_event(
        level="WARNING" if exc.status_code < 500 else "ERROR",
        message=f"HTTP {exc.status_code}: {exc.detail}",
        context={
            "url": str(request.url),
            "method": request.method,
            "status_code": exc.status_code
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected 500 errors with logging."""
    log_event(
        level="ERROR",
        message="Unexpected server error",
        context={
            "url": str(request.url),
            "method": request.method,
            "error": str(exc),
            "error_type": type(exc).__name__
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "TheRegiment API",
        "version": "1.0.0"
    }

# Mount route modules
app.include_router(clients.router, prefix="/api/v1/clients", tags=["clients"])
app.include_router(meals.router, prefix="/api/v1/meals", tags=["meals"])
app.include_router(training.router, prefix="/api/v1/training", tags=["training"])
app.include_router(cardio.router, prefix="/api/v1/cardio", tags=["cardio"])
app.include_router(checkins.router, prefix="/api/v1/checkins", tags=["checkins"])
app.include_router(job_cards.router, prefix="/api/v1/job-cards", tags=["job-cards"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["templates"])

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    log_event(
        level="INFO",
        message="TheRegiment API starting up",
        context={
            "port": os.getenv("PORT", "8000"),
            "environment": os.getenv("ENV", "development")
        }
    )

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    log_event(
        level="INFO",
        message="TheRegiment API shutting down",
        context={}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 