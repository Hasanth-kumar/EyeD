"""
Attendance session domain entity.

Represents an attendance session in the EyeD AI Attendance System.
This is a pure domain entity with no infrastructure dependencies.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from domain.entities.attendance_record import MIN_CONFIDENCE_THRESHOLD


@dataclass(frozen=True)
class AttendanceSession:
    """
    Immutable attendance session entity.
    
    Represents a session during which a user attempts to mark attendance.
    A session can be active (ongoing) or completed.
    
    Attributes:
        session_id: Unique identifier for the session.
        user_id: ID of the user for this session.
        user_name: Name of the user for this session.
        start_time: Date and time when the session started.
        end_time: Optional date and time when the session ended.
        status: Status of the session (e.g., 'active', 'completed', 'failed').
        confidence: Confidence score for face recognition in this session.
        liveness_verified: Whether liveness verification passed in this session.
    
    Examples:
        >>> from datetime import datetime
        >>> session = AttendanceSession(
        ...     session_id="session_001",
        ...     user_id="user_001",
        ...     user_name="John Doe",
        ...     start_time=datetime.now(),
        ...     end_time=None,
        ...     status="active",
        ...     confidence=0.85,
        ...     liveness_verified=True
        ... )
        >>> session.is_active()
        True
    """
    
    session_id: str
    user_id: str
    user_name: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    confidence: float
    liveness_verified: bool
    
    def is_active(self) -> bool:
        """
        Check if the session is currently active.
        
        Returns:
            True if status is 'active' and end_time is None, False otherwise.
        """
        return self.status.lower() == 'active' and self.end_time is None
    
    def is_completed(self) -> bool:
        """
        Check if the session is completed.
        
        Returns:
            True if end_time is set, False otherwise.
        """
        return self.end_time is not None
    
    def get_duration_seconds(self) -> Optional[float]:
        """
        Get the duration of the session in seconds.
        
        Returns:
            Duration in seconds if session is completed, None otherwise.
        """
        if self.end_time is None:
            return None
        
        delta = self.end_time - self.start_time
        return delta.total_seconds()
    
    def is_verified(self) -> bool:
        """
        Check if the session has passed verification.
        
        Returns:
            True if liveness_verified is True and confidence is above threshold, False otherwise.
        """
        return self.liveness_verified and self.confidence >= MIN_CONFIDENCE_THRESHOLD

