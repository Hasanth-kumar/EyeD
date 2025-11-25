"""
Users API routes.

This module provides REST API endpoints for user operations.
It acts as a thin adapter between HTTP requests and use cases.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query, Path
from pydantic import BaseModel

from use_cases.get_all_users import GetAllUsersUseCase, GetAllUsersRequest
from use_cases.register_user import RegisterUserRequest, RegisterUserResponse, RegisterUserUseCase
from use_cases.get_user_info import GetUserInfoUseCase, GetUserInfoRequest
from use_cases.get_user_performance import GetUserPerformanceUseCase, GetUserPerformanceRequest
from use_cases.update_user_info import UpdateUserInfoUseCase, UpdateUserInfoRequest
from api.dependencies import (
    get_get_all_users_use_case,
    get_register_user_use_case,
    get_get_user_info_use_case,
    get_get_user_performance_use_case,
    get_update_user_info_use_case
)
from domain.entities.user import User
from infrastructure.utils.image_converter import ImageConverter

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== DTOs ====================

class UserDTO(BaseModel):
    """DTO for user."""
    userId: str
    userName: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    registrationDate: str
    status: str


class GetAllUsersResponseDTO(BaseModel):
    """Response DTO for getting all users."""
    success: bool
    users: list[UserDTO]
    total: int
    error: Optional[str] = None


class RegisterUserRequestDTO(BaseModel):
    """Request DTO for registering a user."""
    userId: str
    userName: str
    frames: list[str]  # Base64 encoded images
    email: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None


class RegisterUserResponseDTO(BaseModel):
    """Response DTO for user registration."""
    success: bool
    user: Optional[UserDTO] = None
    qualityScore: Optional[float] = None
    error: Optional[str] = None


class GetUserInfoResponseDTO(BaseModel):
    """Response DTO for getting user info."""
    success: bool
    user: Optional[UserDTO] = None
    error: Optional[str] = None


class UserPerformanceDTO(BaseModel):
    """DTO for user performance."""
    userId: str
    totalAttendance: int
    attendanceRate: float
    averageConfidence: float
    bestStreak: int
    currentStreak: int


class GetUserPerformanceResponseDTO(BaseModel):
    """Response DTO for getting user performance."""
    success: bool
    performance: Optional[UserPerformanceDTO] = None
    error: Optional[str] = None


class UpdateUserRequestDTO(BaseModel):
    """Request DTO for updating user."""
    userName: Optional[str] = None
    email: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    status: Optional[str] = None


class UpdateUserResponseDTO(BaseModel):
    """Response DTO for updating user."""
    success: bool
    user: Optional[UserDTO] = None
    error: Optional[str] = None


# ==================== Conversion Functions ====================

def _convert_user_to_dto(user: User) -> UserDTO:
    """Convert User entity to DTO."""
    # Ensure registration_date is in ISO 8601 format with timezone
    if user.registration_date:
        reg_date = user.registration_date
        # If datetime is naive (no timezone), make it timezone-aware (UTC)
        if reg_date.tzinfo is None:
            reg_date = reg_date.replace(tzinfo=timezone.utc)
        registration_date_str = reg_date.isoformat()
    else:
        # Use current UTC time if no registration date
        registration_date_str = datetime.now(timezone.utc).isoformat()
    
    return UserDTO(
        userId=user.user_id,
        userName=user.username,
        firstName=user.first_name,
        lastName=user.last_name,
        email=user.email,
        registrationDate=registration_date_str,
        status=user.status
    )


# ==================== Endpoints ====================

@router.get("", response_model=GetAllUsersResponseDTO)
async def get_all_users(
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(10, ge=1, le=100, description="Page size"),
    includeInactive: bool = Query(False, description="Include inactive users"),
    use_case: GetAllUsersUseCase = Depends(get_get_all_users_use_case)
):
    """
    Get all users endpoint.
    
    This endpoint:
    1. Validates request parameters
    2. Converts DTO to use case request
    3. Calls use case (business logic is here)
    4. Converts use case response to DTO
    5. Returns HTTP response
    
    NO business logic here - all in use case.
    """
    try:
        # Create use case request
        use_case_request = GetAllUsersRequest(
            include_inactive=includeInactive
        )
        
        # Call use case
        response = use_case.execute(use_case_request)
        
        if not response.success:
            return GetAllUsersResponseDTO(
                success=False,
                users=[],
                total=0,
                error=response.error
            )
        
        # Convert to DTOs
        user_dtos = [_convert_user_to_dto(user) for user in response.users]
        
        # Apply pagination
        start_idx = (page - 1) * pageSize
        end_idx = start_idx + pageSize
        paginated_users = user_dtos[start_idx:end_idx]
        
        return GetAllUsersResponseDTO(
            success=True,
            users=paginated_users,
            total=len(user_dtos)
        )
        
    except Exception as e:
        logger.exception(f"Unexpected error in get_all_users: {str(e)}")
        return GetAllUsersResponseDTO(
            success=False,
            users=[],
            total=0,
            error="An unexpected error occurred. Please try again."
        )


@router.post("/register", response_model=RegisterUserResponseDTO)
async def register_user(
    request: RegisterUserRequestDTO,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case)
):
    """
    Register user endpoint.
    
    This endpoint:
    1. Validates request (DTO validation)
    2. Converts DTO to use case request (base64 → numpy arrays)
    3. Calls use case (business logic is here)
    4. Converts use case response to DTO
    5. Returns HTTP response
    
    NO business logic here - all in use case.
    """
    try:
        # Convert base64 frames to numpy arrays
        if not request.frames:
            return RegisterUserResponseDTO(
                success=False,
                error="At least one frame is required for registration"
            )
        
        # Use the first frame for registration (or could use all frames)
        face_image = ImageConverter.base64_to_numpy(request.frames[0])
        
        if face_image is None:
            return RegisterUserResponseDTO(
                success=False,
                error="Failed to decode image. Please ensure the image is in a valid format (JPEG, PNG, etc.)"
            )
        
        # Create use case request
        use_case_request = RegisterUserRequest(
            user_id=request.userId,
            user_name=request.userName,
            face_image=face_image,
            email=request.email,
            first_name=request.firstName,
            last_name=request.lastName
        )
        
        # Run CPU-bound face recognition operations in thread pool to avoid blocking
        # This allows the async endpoint to handle other requests while processing
        loop = asyncio.get_event_loop()
        response: RegisterUserResponse = await loop.run_in_executor(
            None,  # Use default ThreadPoolExecutor
            use_case.execute,
            use_case_request
        )
        
        if not response.success:
            return RegisterUserResponseDTO(
                success=False,
                error=response.error
            )
        
        # Convert to DTO
        user_dto = _convert_user_to_dto(response.user) if response.user else None
        
        return RegisterUserResponseDTO(
            success=True,
            user=user_dto,
            qualityScore=response.quality_score
        )
        
    except Exception as e:
        logger.exception(f"Unexpected error in register_user: {str(e)}")
        return RegisterUserResponseDTO(
            success=False,
            error=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/{user_id}", response_model=GetUserInfoResponseDTO)
async def get_user(
    user_id: str = Path(..., description="User ID"),
    use_case: GetUserInfoUseCase = Depends(get_get_user_info_use_case)
):
    """
    Get user by ID endpoint.
    """
    try:
        use_case_request = GetUserInfoRequest(
            user_id=user_id,
            include_performance=False
        )
        
        response = use_case.execute(use_case_request)
        
        if not response.success:
            return GetUserInfoResponseDTO(
                success=False,
                error=response.error
            )
        
        user_dto = _convert_user_to_dto(response.user) if response.user else None
        
        return GetUserInfoResponseDTO(
            success=True,
            user=user_dto
        )
        
    except Exception as e:
        logger.exception(f"Unexpected error in get_user: {str(e)}")
        return GetUserInfoResponseDTO(
            success=False,
            error="An unexpected error occurred. Please try again."
        )


@router.get("/{user_id}/stats", response_model=GetUserPerformanceResponseDTO)
async def get_user_stats(
    user_id: str = Path(..., description="User ID"),
    periodDays: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    use_case: GetUserPerformanceUseCase = Depends(get_get_user_performance_use_case)
):
    """
    Get user performance statistics endpoint.
    """
    try:
        use_case_request = GetUserPerformanceRequest(
            user_id=user_id,
            period_days=periodDays
        )
        
        response = use_case.execute(use_case_request)
        
        if not response.success:
            return GetUserPerformanceResponseDTO(
                success=False,
                error=response.error
            )
        
        performance_dto = None
        if response.performance:
            performance_dto = UserPerformanceDTO(
                userId=response.performance.user_id,
                totalAttendance=response.performance.total_attendance,
                attendanceRate=response.performance.attendance_rate,
                averageConfidence=response.performance.average_confidence,
                bestStreak=response.performance.best_streak,
                currentStreak=response.performance.current_streak
            )
        
        return GetUserPerformanceResponseDTO(
            success=True,
            performance=performance_dto
        )
        
    except Exception as e:
        logger.exception(f"Unexpected error in get_user_stats: {str(e)}")
        return GetUserPerformanceResponseDTO(
            success=False,
            error="An unexpected error occurred. Please try again."
        )


@router.patch("/{user_id}", response_model=UpdateUserResponseDTO)
async def update_user(
    user_id: str = Path(..., description="User ID"),
    request: UpdateUserRequestDTO = ...,
    use_case: UpdateUserInfoUseCase = Depends(get_update_user_info_use_case)
):
    """
    Update user information endpoint.
    """
    try:
        # Convert DTO to updates dict
        updates = {}
        if request.userName is not None:
            updates['user_name'] = request.userName
        if request.email is not None:
            updates['email'] = request.email
        if request.firstName is not None:
            updates['first_name'] = request.firstName
        if request.lastName is not None:
            updates['last_name'] = request.lastName
        if request.status is not None:
            updates['status'] = request.status
        
        if not updates:
            return UpdateUserResponseDTO(
                success=False,
                error="No fields to update"
            )
        
        use_case_request = UpdateUserInfoRequest(
            user_id=user_id,
            updates=updates
        )
        
        response = use_case.execute(use_case_request)
        
        if not response.success:
            return UpdateUserResponseDTO(
                success=False,
                error=response.error
            )
        
        user_dto = _convert_user_to_dto(response.user) if response.user else None
        
        return UpdateUserResponseDTO(
            success=True,
            user=user_dto
        )
        
    except Exception as e:
        logger.exception(f"Unexpected error in update_user: {str(e)}")
        return UpdateUserResponseDTO(
            success=False,
            error="An unexpected error occurred. Please try again."
        )





