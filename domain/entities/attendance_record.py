"""
Attendance record domain entity.

Represents a single attendance record in the EyeD AI Attendance System.
This is a pure domain entity with no infrastructure dependencies.
"""

from dataclasses import dataclass
from datetime import date, time, datetime
from typing import Optional


# Business rule constants
MIN_CONFIDENCE_THRESHOLD = 0.6
MIN_FACE_QUALITY_SCORE = 0.5


@dataclass(frozen=True)
class AttendanceRecord:
    """
    Immutable attendance record entity.
    
    Attributes:
        record_id: Unique identifier for the attendance record.
        user_id: ID of the user for this attendance record.
        user_name: Name of the user for this attendance record.
        date: Date of the attendance record.
        time: Time of the attendance record.
        confidence: Confidence score for face recognition (0.0 to 1.0).
        liveness_verified: Whether liveness verification passed.
        face_quality_score: Quality score of the face image (0.0 to 1.0).
        processing_time_ms: Processing time in milliseconds.
        verification_stage: Stage of verification process.
        session_id: ID of the attendance session.
        device_info: Information about the device used.
        location: Location where attendance was recorded.
        status: Status of attendance, either 'Present' or 'Absent'.
    
    Examples:
        >>> from datetime import date, time
        >>> record = AttendanceRecord.create(
        ...     record_id="rec_001",
        ...     user_id="user_001",
        ...     user_name="John Doe",
        ...     date=date.today(),
        ...     time=time(9, 0, 0),
        ...     confidence=0.85,
        ...     liveness_verified=True,
        ...     face_quality_score=0.9,
        ...     processing_time_ms=150.0,
        ...     verification_stage="Liveness Verified",
        ...     session_id="session_001",
        ...     device_info="Webcam",
        ...     location="Office"
        ... )
        >>> record.is_valid()
        True
    """
    
    record_id: str
    user_id: str
    user_name: str
    date: date
    time: time
    confidence: float
    liveness_verified: bool
    face_quality_score: float
    processing_time_ms: float
    verification_stage: str
    session_id: str
    device_info: str
    location: str
    status: str
    
    @classmethod
    def create(
        cls,
        record_id: str,
        user_id: str,
        user_name: str,
        date: date,
        time: time,
        confidence: float,
        liveness_verified: bool,
        face_quality_score: float,
        processing_time_ms: float,
        verification_stage: str,
        session_id: str,
        device_info: str,
        location: str,
        status: Optional[str] = None
    ) -> 'AttendanceRecord':
        """
        Factory method to create a new attendance record.
        
        Args:
            record_id: Unique identifier for the attendance record.
            user_id: ID of the user for this attendance record.
            user_name: Name of the user for this attendance record.
            date: Date of the attendance record.
            time: Time of the attendance record.
            confidence: Confidence score for face recognition.
            liveness_verified: Whether liveness verification passed.
            face_quality_score: Quality score of the face image.
            processing_time_ms: Processing time in milliseconds.
            verification_stage: Stage of verification process.
            session_id: ID of the attendance session.
            device_info: Information about the device used.
            location: Location where attendance was recorded.
            status: Optional status of attendance. If not provided, will be
                   determined based on validation rules.
        
        Returns:
            A new AttendanceRecord instance.
        """
        # Determine status if not provided
        if status is None:
            if cls._is_valid_attendance(confidence, liveness_verified, face_quality_score):
                status = "Present"
            else:
                status = "Absent"
        
        return cls(
            record_id=record_id,
            user_id=user_id,
            user_name=user_name,
            date=date,
            time=time,
            confidence=confidence,
            liveness_verified=liveness_verified,
            face_quality_score=face_quality_score,
            processing_time_ms=processing_time_ms,
            verification_stage=verification_stage,
            session_id=session_id,
            device_info=device_info,
            location=location,
            status=status
        )
    
    @staticmethod
    def _is_valid_attendance(
        confidence: float,
        liveness_verified: bool,
        face_quality_score: float
    ) -> bool:
        """
        Check if attendance meets minimum requirements.
        
        Args:
            confidence: Confidence score for face recognition.
            liveness_verified: Whether liveness verification passed.
            face_quality_score: Quality score of the face image.
        
        Returns:
            True if attendance meets minimum requirements, False otherwise.
        """
        return (
            confidence >= MIN_CONFIDENCE_THRESHOLD and
            liveness_verified and
            face_quality_score >= MIN_FACE_QUALITY_SCORE
        )
    
    def is_valid(self) -> bool:
        """
        Validate the attendance record against business rules.
        
        Returns:
            True if the record is valid, False otherwise.
        """
        return self._is_valid_attendance(
            self.confidence,
            self.liveness_verified,
            self.face_quality_score
        )
    
    def is_present(self) -> bool:
        """
        Check if the attendance status is 'Present'.
        
        Returns:
            True if status is 'Present', False otherwise.
        """
        return self.status.lower() == 'present'


