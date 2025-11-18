"""
Mark attendance use case.

Orchestrates attendance marking workflow with liveness verification.
Face recognition is handled in Phase 1 (RecognizeFaceUseCase).
"""

from dataclasses import dataclass
from typing import Optional, List, Protocol
from datetime import date
import time
import logging
import numpy as np

logger = logging.getLogger(__name__)

from domain.entities.attendance_record import AttendanceRecord
from domain.services.liveness import LivenessService
from domain.services.attendance import AttendanceService
from domain.shared.exceptions import (
    LivenessVerificationFailedError,
    InvalidAttendanceRecordError
)


@dataclass
class MarkAttendanceRequest:
    """Request for marking attendance with liveness verification."""
    frames_sequence: List[np.ndarray]  # Frames for liveness verification
    user_id: str  # From Phase 1
    user_name: str  # From Phase 1
    face_image: np.ndarray  # Single frame from Phase 1 for attendance record
    face_quality_score: float  # Quality score from Phase 1
    confidence: float  # Recognition confidence from Phase 1
    device_info: str
    location: str
    frontend_blink_count: Optional[int] = None  # Optional blink count from frontend


@dataclass
class MarkAttendanceResponse:
    """Response from marking attendance."""
    success: bool
    attendance_record: Optional[AttendanceRecord] = None
    user: Optional[object] = None  # Deprecated: user info is in attendance_record
    error: Optional[str] = None
    stage: Optional[str] = None


class AttendanceRepositoryProtocol(Protocol):
    """Protocol for attendance repository operations."""
    
    def add_attendance(self, record: AttendanceRecord) -> bool:
        """Add attendance entry. Returns True if successful."""
        ...
    
    def get_attendance_history(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List:
        """Get attendance history. Returns list of attendance entries."""
        ...




class MarkAttendanceUseCase:
    """
    Orchestrates attendance marking workflow with liveness verification.
    
    This use case handles:
    - Liveness verification using frame sequence (requires 3+ blinks)
    - Attendance record creation and persistence
    
    Face recognition and eligibility validation are handled in Phase 1
    (RecognizeFaceUseCase) before this use case is called.
    """
    
    def __init__(
        self,
        liveness_service: LivenessService,
        attendance_service: AttendanceService,
        attendance_repository: AttendanceRepositoryProtocol
    ):
        """
        Initialize MarkAttendanceUseCase.
        
        Args:
            liveness_service: Composite service for liveness verification.
            attendance_service: Composite service for attendance operations.
            attendance_repository: Attendance data persistence repository.
        """
        self.liveness_service = liveness_service
        self.attendance_service = attendance_service
        self.attendance_repository = attendance_repository
    
    def execute(self, request: MarkAttendanceRequest) -> MarkAttendanceResponse:
        """
        Execute attendance marking workflow with liveness verification.
        
        Workflow:
        1. Validate inputs
        2. Call liveness_service.verify_liveness(frames)
        3. If True: Create attendance record and save
        4. If False: Return error response
        
        Attendance is ONLY marked if liveness verification passes (3+ blinks detected).
        If liveness verification fails, no attendance record is created or saved.
        
        Note: Face recognition and eligibility validation are handled in Phase 1
        (RecognizeFaceUseCase) before this use case is called.
        
        Args:
            request: Mark attendance request with user info from Phase 1, frame sequence,
                    and metadata.
        
        Returns:
            MarkAttendanceResponse with attendance marking result.
        """
        start_time = time.time()
        stage = None
        
        try:
            # Step 1: Validate inputs
            stage = "validation"
            if not request.frames_sequence:
                return MarkAttendanceResponse(
                    success=False,
                    error="Frames sequence cannot be empty",
                    stage=stage
                )
            
            if not request.user_id or not request.user_name:
                return MarkAttendanceResponse(
                    success=False,
                    error="User ID and user name are required from Phase 1",
                    stage=stage
                )
            
            # Step 2: Call liveness_service.verify_liveness(frames)
            stage = "liveness_verification"
            liveness_verified = self.liveness_service.verify_liveness(
                request.frames_sequence,
                frontend_blink_count=request.frontend_blink_count
            )
            
            # Step 3: If True, create attendance record and save
            # NOTE: verify_liveness() returns True if verification passes (3+ blinks),
            # and raises LivenessVerificationFailedError if it fails. So if we reach here,
            # liveness_verified is guaranteed to be True.
            stage = "creating_attendance_record"
            attendance_record = self._create_and_save_record(
                request,
                liveness_verified,  # This is always True at this point
                start_time
            )
            
            # Success
            return MarkAttendanceResponse(
                success=True,
                attendance_record=attendance_record,
                user=None,  # User info not needed in response, already in attendance_record
                stage="completed"
            )
            
        except LivenessVerificationFailedError:
            # Step 4: If False, return error response with exact message
            return MarkAttendanceResponse(
                success=False,
                error="Unable to verify Liveness and we detected less than 3 blinks",
                stage=stage or "liveness_verification"
            )
        except InvalidAttendanceRecordError as e:
            # Handle validation errors
            return MarkAttendanceResponse(
                success=False,
                error=str(e.message) if hasattr(e, 'message') else str(e),
                stage=stage
            )
        except Exception as e:
            # Handle unexpected errors
            logger.exception("Unexpected error during attendance marking")
            return MarkAttendanceResponse(
                success=False,
                error=f"Unexpected error during attendance marking: {str(e)}",
                stage=stage or "unknown"
            )
    
    def _create_and_save_record(
        self,
        request: MarkAttendanceRequest,
        liveness_verified: bool,
        start_time: float
    ) -> AttendanceRecord:
        """
        Create, validate, and save attendance record.
        
        Args:
            request: Mark attendance request with user info and face image from Phase 1.
            liveness_verified: Whether liveness was verified (should always be True).
            start_time: Start time for processing time calculation.
        
        Returns:
            Created and saved AttendanceRecord.
        
        Raises:
            InvalidAttendanceRecordError: If validation fails.
        """
        # Create and validate attendance record using composite service
        attendance_record = self.attendance_service.create_and_validate_record(
            user_id=request.user_id,
            user_name=request.user_name,
            face_image=request.face_image,
            confidence=request.confidence,
            liveness_verified=liveness_verified,
            face_quality_score=request.face_quality_score,
            device_info=request.device_info,
            location=request.location,
            verification_stage="completed",
            session_id=None,  # Will be generated by logger
            start_time=start_time
        )
        
        # Save attendance record (repository handles domain-to-persistence mapping)
        save_success = self.attendance_repository.add_attendance(attendance_record)
        if not save_success:
            raise InvalidAttendanceRecordError(
                message="Failed to save attendance record",
                error_code="SAVE_FAILED"
            )
        
        return attendance_record
    

