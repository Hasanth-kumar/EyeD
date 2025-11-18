"""
Attendance API routes.

This module provides REST API endpoints for attendance operations.
It acts as a thin adapter between HTTP requests and use cases.
"""

import base64
import logging
from typing import List, Optional
from datetime import date, time, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
import numpy as np
from PIL import Image
import io

from use_cases.mark_attendance import MarkAttendanceUseCase, MarkAttendanceRequest
from use_cases.recognize_face import RecognizeFaceUseCase, RecognizeFaceRequest
from use_cases.get_attendance_records import GetAttendanceRecordsUseCase, GetAttendanceRecordsRequest
from use_cases.get_all_users import GetAllUsersUseCase, GetAllUsersRequest
from api.dependencies import (
    get_mark_attendance_use_case,
    get_recognize_face_use_case,
    get_get_attendance_records_use_case,
    get_get_all_users_use_case
)
from core.recognition.quality_assessor import QualityAssessor
from domain.shared.exceptions import (
    DailyLimitExceededError,
    InvalidAttendanceRecordError
)

logger = logging.getLogger(__name__)

router = APIRouter()


class RecognizeFaceRequestDTO(BaseModel):
    """Request DTO for recognizing a face."""
    frame: str  # Base64 encoded single frame


class RecognizeFaceResponseDTO(BaseModel):
    """Response DTO for face recognition."""
    success: bool
    userId: Optional[str] = None
    userName: Optional[str] = None
    confidence: Optional[float] = None
    message: str
    dailyLimitReached: bool = False


class MarkAttendanceRequestDTO(BaseModel):
    """Request DTO for marking attendance."""
    frames: List[str]  # Base64 encoded frames for blink detection
    landmarks: Optional[List[List[List[float]]]] = None  # Optional landmarks from frontend: [[[x, y], ...], ...]
    userId: str  # REQUIRED - from Phase 1
    userName: str  # REQUIRED - from Phase 1
    faceImage: str  # REQUIRED - Base64 encoded single frame from Phase 1
    confidence: float  # REQUIRED - Recognition confidence from Phase 1
    faceQualityScore: Optional[float] = None  # Optional - Quality score from Phase 1, will be recalculated if not provided
    location: Optional[str] = None
    blinkCount: Optional[int] = None  # Optional - Blink count from frontend (trusted if >= 3)


class MarkAttendanceResponseDTO(BaseModel):
    """Response DTO for marking attendance."""
    success: bool
    userId: str
    userName: str
    timestamp: str
    confidence: float
    message: str


class AttendanceRecordDTO(BaseModel):
    """DTO for attendance record."""
    id: str
    userId: str
    userName: str
    timestamp: str
    status: str
    confidence: Optional[float] = None
    imageUrl: Optional[str] = None
    location: Optional[str] = None


class PaginatedDataDTO(BaseModel):
    """DTO for paginated data."""
    data: List[AttendanceRecordDTO]
    total: int
    page: int
    pageSize: int
    totalPages: int


class PaginatedResponseDTO(BaseModel):
    """DTO for paginated response wrapped in ApiResponse format."""
    data: PaginatedDataDTO
    success: bool
    message: Optional[str] = None


class AttendanceStatsDataDTO(BaseModel):
    """DTO for attendance statistics data."""
    totalPresent: int
    totalAbsent: int
    totalLate: int
    attendanceRate: float  # 0-1 decimal
    averageCheckInTime: Optional[str] = None


class AttendanceStatsDTO(BaseModel):
    """DTO for attendance statistics wrapped in ApiResponse format."""
    data: AttendanceStatsDataDTO
    success: bool
    message: Optional[str] = None


def _base64_to_numpy(base64_string: str) -> np.ndarray:
    """
    Convert base64 encoded image string to numpy array.
    
    Args:
        base64_string: Base64 encoded image string (with or without data URL prefix)
    
    Returns:
        Numpy array representing the image (RGB format)
    """
    try:
        # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,...")
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64
        image_bytes = base64.b64decode(base64_string)
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        return np.array(image)
    except Exception as e:
        logger.error(f"Error converting base64 to numpy: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image format: {str(e)}"
        )


def _convert_to_use_case_request(dto: MarkAttendanceRequestDTO) -> MarkAttendanceRequest:
    """
    Convert DTO to use case request.
    
    Extracts user info from Phase 1 (userId, userName, faceImage, confidence)
    and converts base64 images to numpy arrays for use case processing.
    
    Args:
        dto: Request DTO from frontend with user info from Phase 1
    
    Returns:
        Use case request with numpy arrays, landmarks, and user info from Phase 1
    """
    # Convert base64 frames to numpy arrays
    frames_sequence = [_base64_to_numpy(frame) for frame in dto.frames]
    
    # Convert faceImage from Phase 1 to numpy array
    face_image = _base64_to_numpy(dto.faceImage)
    
    # Note: Landmarks are extracted server-side by LivenessService.verify_liveness()
    # Frontend landmarks are not used to avoid inconsistencies and ensure server-side validation
    if dto.landmarks and len(dto.landmarks) == len(dto.frames):
        logger.info(f"Frontend provided {len(dto.landmarks)} landmark sets, but extracting server-side for consistency")
    else:
        logger.info("Extracting landmarks server-side (frontend landmarks not provided or invalid)")
    
    # Calculate face quality score if not provided from Phase 1
    face_quality_score = dto.faceQualityScore
    if face_quality_score is None:
        logger.info("Face quality score not provided from Phase 1, recalculating from faceImage")
        quality_assessor = QualityAssessor()
        quality_result = quality_assessor.assess(face_image)
        face_quality_score = quality_result.overall_score
    
    # Use default device info if not provided
    device_info = dto.userId or "web"
    
    # Use default location if not provided
    location = dto.location or "unknown"
    
    return MarkAttendanceRequest(
        frames_sequence=frames_sequence,
        user_id=dto.userId,
        user_name=dto.userName,
        face_image=face_image,
        face_quality_score=face_quality_score,
        confidence=dto.confidence,
        device_info=device_info,
        location=location,
        frontend_blink_count=dto.blinkCount
    )


def _convert_record_to_dto(
    response,
    request: Optional[MarkAttendanceRequestDTO] = None
) -> MarkAttendanceResponseDTO:
    """
    Convert use case response to DTO.
    
    Args:
        response: MarkAttendanceResponse from use case
        request: Optional request DTO to preserve user info in error cases
    
    Returns:
        Response DTO for frontend
    """
    if response.success and response.attendance_record:
        record = response.attendance_record
        # Combine date and time into ISO timestamp
        from datetime import datetime
        timestamp = datetime.combine(record.date, record.time).isoformat()
        
        return MarkAttendanceResponseDTO(
            success=True,
            userId=record.user_id,
            userName=record.user_name,
            timestamp=timestamp,
            confidence=record.confidence,
            message=f"Attendance marked successfully for {record.user_name}"
        )
    else:
        # Error case - use error message from use case response
        error_message = response.error or "Failed to mark attendance"
        return MarkAttendanceResponseDTO(
            success=False,
            userId=request.userId if request else "",
            userName=request.userName if request else "",
            timestamp="",
            confidence=request.confidence if request else 0.0,
            message=error_message
        )


@router.post("/recognize", response_model=RecognizeFaceResponseDTO)
async def recognize_face(
    request: RecognizeFaceRequestDTO,
    use_case: RecognizeFaceUseCase = Depends(get_recognize_face_use_case)
):
    """
    Recognize face endpoint for Phase 1.
    
    This endpoint:
    1. Validates request (DTO validation)
    2. Converts DTO to use case request (base64 → numpy array)
    3. Calls use case (business logic is here)
    4. Converts use case response to DTO
    5. Returns HTTP response
    
    NO business logic here - all in use case.
    """
    try:
        # Convert base64 frame to numpy array
        frame_array = _base64_to_numpy(request.frame)
        
        # Create use case request
        use_case_request = RecognizeFaceRequest(frame=frame_array)
        
        # Call use case (business logic is here)
        response = use_case.execute(use_case_request)
        
        # Convert to DTO
        if response.success:
            return RecognizeFaceResponseDTO(
                success=True,
                userId=response.user_id,
                userName=response.user_name,
                confidence=response.confidence,
                message=f"Face recognized: {response.user_name}",
                dailyLimitReached=response.daily_limit_reached
            )
        else:
            # Error case - use case already handled exceptions internally
            return RecognizeFaceResponseDTO(
                success=False,
                userId=response.user_id,
                userName=response.user_name,
                confidence=response.confidence,
                message=response.error or "Face recognition failed",
                dailyLimitReached=response.daily_limit_reached
            )
    
    except Exception as e:
        logger.exception(f"Unexpected error in recognize_face: {str(e)}")
        return RecognizeFaceResponseDTO(
            success=False,
            message="An unexpected error occurred. Please try again.",
            dailyLimitReached=False
        )


@router.post("/mark", response_model=MarkAttendanceResponseDTO)
async def mark_attendance(
    request: MarkAttendanceRequestDTO,
    use_case: MarkAttendanceUseCase = Depends(get_mark_attendance_use_case)
):
    """
    Mark attendance endpoint for Phase 2 (liveness verification).
    
    This endpoint handles liveness verification only. Face recognition is handled
    in Phase 1 (recognize_face endpoint) before this endpoint is called.
    
    This endpoint:
    1. Validates request (DTO validation)
    2. Converts DTO to use case request (base64 → numpy arrays, extracts user info from Phase 1)
    3. Calls use case (business logic is here)
    4. Converts use case response to DTO
    5. Returns HTTP response
    
    NO business logic here - all in use case.
    The use case handles liveness verification and returns the exact error message
    "Unable to verify Liveness and we detected less than 3 blinks" if verification fails.
    """
    try:
        # Convert DTO to use case request
        use_case_request = _convert_to_use_case_request(request)
        
        # Call use case (business logic is here)
        response = use_case.execute(use_case_request)
        
        # Convert to DTO (uses error message from use case response)
        return _convert_record_to_dto(response, request)
        
    except DailyLimitExceededError as e:
        logger.warning(f"Daily limit exceeded: {e.message}")
        return MarkAttendanceResponseDTO(
            success=False,
            userId=request.userId,
            userName=request.userName,
            timestamp="",
            confidence=request.confidence,
            message="Daily attendance limit exceeded. You have already marked attendance today."
        )
    
    except InvalidAttendanceRecordError as e:
        logger.error(f"Invalid attendance record: {e.message}")
        return MarkAttendanceResponseDTO(
            success=False,
            userId=request.userId,
            userName=request.userName,
            timestamp="",
            confidence=request.confidence,
            message=f"Failed to create attendance record: {e.message}"
        )
    
    except Exception as e:
        logger.exception(f"Unexpected error in mark_attendance: {str(e)}")
        return MarkAttendanceResponseDTO(
            success=False,
            userId=request.userId if hasattr(request, 'userId') else "",
            userName=request.userName if hasattr(request, 'userName') else "",
            timestamp="",
            confidence=request.confidence if hasattr(request, 'confidence') else 0.0,
            message="An unexpected error occurred. Please try again."
        )


@router.get("", response_model=PaginatedResponseDTO, response_model_exclude_none=True)
async def get_attendance_records(
    startDate: Optional[str] = Query(None, description="Start date (ISO format: YYYY-MM-DD)"),
    endDate: Optional[str] = Query(None, description="End date (ISO format: YYYY-MM-DD)"),
    userId: Optional[str] = Query(None, description="Filter by user ID"),
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(10, ge=1, le=100, description="Page size"),
    use_case: GetAttendanceRecordsUseCase = Depends(get_get_attendance_records_use_case)
):
    """
    Get attendance records endpoint.
    
    This endpoint:
    1. Validates request parameters
    2. Converts DTO to use case request
    3. Calls use case (business logic is here)
    4. Converts use case response to DTO
    5. Returns HTTP response
    
    NO business logic here - all in use case.
    """
    try:
        # Parse dates if provided
        start_date = None
        end_date = None
        
        if startDate:
            start_date = datetime.fromisoformat(startDate).date()
        if endDate:
            end_date = datetime.fromisoformat(endDate).date()
        
        # Create use case request
        use_case_request = GetAttendanceRecordsRequest(
            user_id=userId,
            start_date=start_date,
            end_date=end_date,
            limit=None  # We'll handle pagination in the endpoint
        )
        
        # Call use case
        response = use_case.execute(use_case_request)
        
        if not response.success:
            return PaginatedResponseDTO(
                data=PaginatedDataDTO(
                    data=[],
                    total=0,
                    page=page,
                    pageSize=pageSize,
                    totalPages=0
                ),
                success=False,
                message=response.error or "Failed to retrieve attendance records"
            )
        
        # Convert records to DTOs
        records = response.records
        total = len(records)
        
        # Apply pagination
        start_idx = (page - 1) * pageSize
        end_idx = start_idx + pageSize
        paginated_records = records[start_idx:end_idx]
        
        # Convert to DTOs
        record_dtos = []
        for record in paginated_records:
            timestamp = datetime.combine(record.date, record.time).isoformat()
            record_dtos.append(AttendanceRecordDTO(
                id=record.record_id,
                userId=record.user_id,
                userName=record.user_name,
                timestamp=timestamp,
                status=record.status,
                confidence=record.confidence,
                location=record.location
            ))
        
        total_pages = (total + pageSize - 1) // pageSize if total > 0 else 0
        
        return PaginatedResponseDTO(
            data=PaginatedDataDTO(
                data=record_dtos,
                total=total,
                page=page,
                pageSize=pageSize,
                totalPages=total_pages
            ),
            success=True
        )
        
    except ValueError as e:
        logger.warning(f"Invalid date format: {str(e)}")
        return PaginatedResponseDTO(
            data=PaginatedDataDTO(
                data=[],
                total=0,
                page=page,
                pageSize=pageSize,
                totalPages=0
            ),
            success=False,
            message=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_attendance_records: {str(e)}")
        return PaginatedResponseDTO(
            data=PaginatedDataDTO(
                data=[],
                total=0,
                page=page,
                pageSize=pageSize,
                totalPages=0
            ),
            success=False,
            message="An unexpected error occurred. Please try again."
        )


@router.get("/stats", response_model=AttendanceStatsDTO, response_model_exclude_none=True)
async def get_attendance_stats(
    startDate: Optional[str] = Query(None, description="Start date (ISO format: YYYY-MM-DD)"),
    endDate: Optional[str] = Query(None, description="End date (ISO format: YYYY-MM-DD)"),
    use_case: GetAttendanceRecordsUseCase = Depends(get_get_attendance_records_use_case),
    get_users_use_case: GetAllUsersUseCase = Depends(get_get_all_users_use_case)
):
    """
    Get attendance statistics endpoint.
    
    This endpoint:
    1. Validates request parameters
    2. Gets attendance records for the date range (defaults to today)
    3. Gets all users to calculate expected attendance
    4. Calculates statistics
    5. Returns HTTP response
    
    NO business logic here - all in use case.
    """
    try:
        # Parse dates or use defaults (today)
        if startDate:
            start_date = datetime.fromisoformat(startDate).date()
        else:
            start_date = date.today()
        
        if endDate:
            end_date = datetime.fromisoformat(endDate).date()
        else:
            end_date = date.today()
        
        # Get attendance records for the date range
        use_case_request = GetAttendanceRecordsRequest(
            user_id=None,
            start_date=start_date,
            end_date=end_date,
            limit=None
        )
        
        records_response = use_case.execute(use_case_request)
        
        if not records_response.success:
            return AttendanceStatsDTO(
                data=AttendanceStatsDataDTO(
                    totalPresent=0,
                    totalAbsent=0,
                    totalLate=0,
                    attendanceRate=0.0
                ),
                success=False,
                message=records_response.error or "Failed to retrieve attendance records"
            )
        
        records = records_response.records
        
        # Get all users to calculate expected attendance
        users_request = GetAllUsersRequest(include_inactive=False)
        users_response = get_users_use_case.execute(users_request)
        total_users = len(users_response.users) if users_response.success else 0
        
        # Filter records for the date range
        today_records = [r for r in records if start_date <= r.date <= end_date]
        
        # Calculate statistics
        present_records = [r for r in today_records if r.is_present()]
        total_present = len(present_records)
        
        # Count late (check-in after 9:00 AM)
        late_threshold = time(9, 0, 0)
        late_records = [
            r for r in present_records
            if r.time > late_threshold
        ]
        total_late = len(late_records)
        
        # Calculate absent (users who should have attended but didn't)
        # Get unique user IDs who attended today
        present_user_ids = set(r.user_id for r in present_records)
        total_absent = max(0, total_users - len(present_user_ids))
        
        # Calculate attendance rate (as decimal 0-1, not percentage)
        if total_users > 0:
            attendance_rate = total_present / total_users
        else:
            attendance_rate = 0.0
        
        # Calculate average check-in time
        average_check_in_time = None
        if present_records:
            total_seconds = sum(
                r.time.hour * 3600 + r.time.minute * 60 + r.time.second
                for r in present_records
            )
            avg_seconds = total_seconds // len(present_records)
            hours = avg_seconds // 3600
            minutes = (avg_seconds % 3600) // 60
            average_check_in_time = f"{hours:02d}:{minutes:02d}"
        
        return AttendanceStatsDTO(
            data=AttendanceStatsDataDTO(
                totalPresent=total_present,
                totalAbsent=total_absent,
                totalLate=total_late,
                attendanceRate=attendance_rate,
                averageCheckInTime=average_check_in_time
            ),
            success=True
        )
        
    except ValueError as e:
        logger.warning(f"Invalid date format: {str(e)}")
        return AttendanceStatsDTO(
            data=AttendanceStatsDataDTO(
                totalPresent=0,
                totalAbsent=0,
                totalLate=0,
                attendanceRate=0.0
            ),
            success=False,
            message=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_attendance_stats: {str(e)}")
        return AttendanceStatsDTO(
            data=AttendanceStatsDataDTO(
                totalPresent=0,
                totalAbsent=0,
                totalLate=0,
                attendanceRate=0.0
            ),
            success=False,
            message="An unexpected error occurred. Please try again."
        )

