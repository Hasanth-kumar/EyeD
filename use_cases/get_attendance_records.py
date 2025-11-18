"""
Get attendance records use case.

Orchestrates attendance records retrieval workflow with optional filtering.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Protocol
from datetime import date

from domain.entities.attendance_record import AttendanceRecord


@dataclass
class GetAttendanceRecordsRequest:
    """Request for getting attendance records."""
    user_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    limit: Optional[int] = None


@dataclass
class GetAttendanceRecordsResponse:
    """Response from getting attendance records."""
    success: bool
    records: List[AttendanceRecord] = field(default_factory=list)
    error: Optional[str] = None


class AttendanceRepositoryProtocol(Protocol):
    """Protocol for attendance repository operations."""
    
    def get_attendance_history(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[AttendanceRecord]:
        """Get attendance history. Returns list of AttendanceRecord domain entities."""
        ...


class GetAttendanceRecordsUseCase:
    """
    Orchestrates attendance records retrieval workflow.
    
    This use case coordinates attendance records retrieval from the repository
    with optional filtering by user, date range, and limit.
    """
    
    def __init__(
        self,
        attendance_repository: AttendanceRepositoryProtocol
    ):
        """
        Initialize GetAttendanceRecordsUseCase.
        
        Args:
            attendance_repository: Attendance data persistence repository.
        """
        self.attendance_repository = attendance_repository
    
    def execute(self, request: GetAttendanceRecordsRequest) -> GetAttendanceRecordsResponse:
        """
        Execute attendance records retrieval workflow.
        
        Args:
            request: Get attendance records request with optional filters.
        
        Returns:
            GetAttendanceRecordsResponse with attendance records list.
        """
        try:
            # Step 1: Get attendance records from repository
            records = self.attendance_repository.get_attendance_history(
                user_id=request.user_id,
                start_date=request.start_date,
                end_date=request.end_date
            )
            
            # Step 2: Apply limit if specified
            if request.limit is not None and request.limit > 0:
                records = records[:request.limit]
            
            # Step 3: Return filtered records
            return GetAttendanceRecordsResponse(
                success=True,
                records=records
            )
            
        except Exception as e:
            # Handle unexpected errors
            return GetAttendanceRecordsResponse(
                success=False,
                records=[],
                error=f"Unexpected error during attendance records retrieval: {str(e)}"
            )

