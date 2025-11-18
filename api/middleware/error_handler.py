"""
Global error handling middleware for FastAPI.
"""

import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from domain.shared.exceptions import (
    DomainException,
    FaceDetectionFailedError,
    InsufficientQualityError,
    FaceNotRecognizedError,
    LivenessVerificationFailedError,
    DailyLimitExceededError,
    InvalidAttendanceRecordError
)

logger = logging.getLogger(__name__)


# Map domain exceptions to HTTP status codes
EXCEPTION_STATUS_MAP = {
    FaceDetectionFailedError: status.HTTP_400_BAD_REQUEST,
    InsufficientQualityError: status.HTTP_400_BAD_REQUEST,
    FaceNotRecognizedError: status.HTTP_404_NOT_FOUND,
    LivenessVerificationFailedError: status.HTTP_400_BAD_REQUEST,
    DailyLimitExceededError: status.HTTP_429_TOO_MANY_REQUESTS,
    InvalidAttendanceRecordError: status.HTTP_400_BAD_REQUEST,
}


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """
    Handle domain exceptions and convert to HTTP responses.
    
    Maps domain exceptions to appropriate HTTP status codes and formats
    error responses consistently.
    """
    status_code = EXCEPTION_STATUS_MAP.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    logger.error(
        f"Domain exception: {type(exc).__name__} - {exc.message}",
        extra={"error_code": getattr(exc, "error_code", None), "status_code": status_code}
    )
    
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": exc.message,
            "code": getattr(exc, "error_code", type(exc).__name__),
            "data": None
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    """
    logger.warning(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Request validation failed",
            "code": "VALIDATION_ERROR",
            "details": exc.errors(),
            "data": None
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions.
    """
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "code": f"HTTP_{exc.status_code}",
            "data": None
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.
    """
    logger.exception(f"Unexpected error: {type(exc).__name__} - {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "An internal server error occurred",
            "code": "INTERNAL_SERVER_ERROR",
            "data": None
        }
    )





