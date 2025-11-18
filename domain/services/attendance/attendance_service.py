"""
Attendance Service - Composite service for attendance operations.

This service groups related attendance operations (logging and validation)
to reduce coupling in use cases.
"""

from typing import Optional
import numpy as np

from core.attendance.attendance_logger import AttendanceLogger
from core.attendance.attendance_validator import AttendanceValidator
from domain.entities.attendance_record import AttendanceRecord
from domain.shared.exceptions import InvalidAttendanceRecordError


class AttendanceService:
    """
    Composite service for attendance operations.
    
    This service coordinates attendance record creation and validation.
    It encapsulates the workflow of creating and validating attendance records.
    """
    
    def __init__(
        self,
        attendance_logger: AttendanceLogger,
        attendance_validator: AttendanceValidator
    ):
        """
        Initialize attendance service.
        
        Args:
            attendance_logger: Attendance record creation service.
            attendance_validator: Attendance validation service.
        """
        self.attendance_logger = attendance_logger
        self.attendance_validator = attendance_validator
    
    def create_and_validate_record(
        self,
        user_id: str,
        user_name: str,
        face_image: np.ndarray,
        confidence: float,
        liveness_verified: bool,
        face_quality_score: float,
        device_info: str,
        location: str,
        verification_stage: Optional[str] = None,
        session_id: Optional[str] = None,
        start_time: Optional[float] = None
    ) -> AttendanceRecord:
        """
        Create and validate an attendance record.
        
        NOTE: When called from MarkAttendanceUseCase, liveness_verified should ALWAYS be True.
        The mark attendance workflow requires 3+ blinks to pass liveness verification before
        creating any attendance record. If liveness_verified=False, this indicates a workflow
        violation and will raise an error.
        
        Args:
            user_id: ID of the user for this attendance record.
            user_name: Name of the user for this attendance record.
            face_image: Face image array (used for processing time calculation).
            confidence: Confidence score for face recognition (0.0 to 1.0).
            liveness_verified: Whether liveness verification passed. Must be True when called
                from MarkAttendanceUseCase (workflow requires 3+ blinks before marking attendance).
            face_quality_score: Quality score of the face image (0.0 to 1.0).
            device_info: Information about the device used.
            location: Location where attendance was recorded.
            verification_stage: Optional stage of verification process.
            session_id: Optional session ID. If not provided, a new one is generated.
            start_time: Optional start time for processing time calculation.
        
        Returns:
            Created and validated AttendanceRecord.
        
        Raises:
            InvalidAttendanceRecordError: If validation fails or if liveness_verified=False
                (defensive check for mark attendance workflow).
        """
        # Defensive check: In the mark attendance workflow, liveness_verified must be True.
        # This ensures data integrity - attendance records should never be created with
        # liveness_verified=False when the workflow requires liveness to pass first.
        if not liveness_verified:
            raise InvalidAttendanceRecordError(
                message="Cannot create attendance record with liveness_verified=False. "
                        "The mark attendance workflow requires liveness verification to pass "
                        "(3+ blinks) before creating any attendance record.",
                error_code="LIVENESS_NOT_VERIFIED"
            )
        
        # Step 1: Create attendance record data (returns dictionary)
        record_data = self.attendance_logger.create_record(
            user_id=user_id,
            user_name=user_name,
            face_image=face_image,
            confidence=confidence,
            liveness_verified=liveness_verified,
            face_quality_score=face_quality_score,
            device_info=device_info,
            location=location,
            verification_stage=verification_stage,
            session_id=session_id,
            start_time=start_time
        )
        
        # Step 2: Validate attendance record data
        validation_result = self.attendance_validator.validate_record(record_data)
        if not validation_result.is_valid:
            raise InvalidAttendanceRecordError(
                message=validation_result.message or "Attendance record validation failed",
                error_code=validation_result.error_code
            )
        
        # Step 3: Convert dictionary to domain entity
        attendance_record = AttendanceRecord.create(
            record_id=record_data['record_id'],
            user_id=record_data['user_id'],
            user_name=record_data['user_name'],
            date=record_data['date'],
            time=record_data['time'],
            confidence=record_data['confidence'],
            liveness_verified=record_data['liveness_verified'],
            face_quality_score=record_data['face_quality_score'],
            processing_time_ms=record_data['processing_time_ms'],
            verification_stage=record_data['verification_stage'],
            session_id=record_data['session_id'],
            device_info=record_data['device_info'],
            location=record_data['location'],
            status=record_data['status']  # Will be determined by factory method if None
        )
        
        return attendance_record

