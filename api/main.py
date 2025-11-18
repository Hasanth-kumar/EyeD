"""
FastAPI application entry point.

This module creates and configures the FastAPI application with all routes,
middleware, and error handlers.
"""

import logging
from fastapi import FastAPI

from api.routes import attendance, analytics, leaderboard, users
from api.middleware.cors import setup_cors
from api.middleware.error_handler import (
    domain_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from api.middleware.logging import LoggingMiddleware
from domain.shared.exceptions import DomainException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="EyeD API",
    description="REST API for EyeD AI Attendance System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup CORS
setup_cors(app)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Register exception handlers
app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(
    attendance.router,
    prefix="/api/attendance",
    tags=["attendance"]
)

app.include_router(
    analytics.router,
    prefix="/api/analytics",
    tags=["analytics"]
)

app.include_router(
    leaderboard.router,
    prefix="/api/leaderboard",
    tags=["leaderboard"]
)

app.include_router(
    users.router,
    prefix="/api/users",
    tags=["users"]
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "EyeD API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

