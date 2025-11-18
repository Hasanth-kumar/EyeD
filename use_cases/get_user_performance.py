"""
Get user performance use case.

Orchestrates user performance metrics calculation workflow.
"""

from dataclasses import dataclass
from typing import Optional, List, Protocol
from datetime import date, timedelta

from domain.entities.attendance_record import AttendanceRecord
from domain.services.analytics import MetricsCalculator, UserPerformance
from domain.services.gamification import StreakCalculator


@dataclass
class GetUserPerformanceRequest:
    """Request for getting user performance metrics."""
    user_id: str
    period_days: int = 30


@dataclass
class GetUserPerformanceResponse:
    """Response from getting user performance metrics."""
    success: bool
    performance: Optional[UserPerformance] = None
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


class GetUserPerformanceUseCase:
    """
    Orchestrates user performance calculation workflow.
    
    This use case coordinates attendance record retrieval, metrics calculation,
    and streak calculation to provide comprehensive user performance metrics.
    """
    
    def __init__(
        self,
        metrics_calculator: MetricsCalculator,
        streak_calculator: StreakCalculator,
        attendance_repository: AttendanceRepositoryProtocol
    ):
        """
        Initialize GetUserPerformanceUseCase.
        
        Args:
            metrics_calculator: Service for calculating attendance metrics.
            streak_calculator: Service for calculating attendance streaks.
            attendance_repository: Repository for attendance data persistence.
        """
        self.metrics_calculator = metrics_calculator
        self.streak_calculator = streak_calculator
        self.attendance_repository = attendance_repository
    
    def execute(self, request: GetUserPerformanceRequest) -> GetUserPerformanceResponse:
        """
        Execute user performance calculation workflow.
        
        Args:
            request: Get user performance request with user_id and period_days.
        
        Returns:
            GetUserPerformanceResponse with performance metrics or error.
        """
        try:
            # Validate request
            if not request.user_id:
                return GetUserPerformanceResponse(
                    success=False,
                    error="user_id is required"
                )
            
            if request.period_days <= 0:
                return GetUserPerformanceResponse(
                    success=False,
                    error="period_days must be greater than 0"
                )
            
            # Step 1: Get attendance records for user
            records = self._get_attendance_records(request)
            
            # Step 2: Calculate attendance rate
            attendance_rate = self.metrics_calculator.calculate_attendance_rate(
                records,
                request.period_days
            )
            
            # Step 3: Calculate average confidence
            average_confidence = self.metrics_calculator.calculate_average_confidence(
                records
            )
            
            # Step 4: Calculate streaks
            current_streak = self.streak_calculator.calculate_current_streak(records)
            best_streak = self.streak_calculator.calculate_max_streak(records)
            
            # Step 5: Build UserPerformance value object
            performance = UserPerformance(
                user_id=request.user_id,
                total_attendance=len(records),
                attendance_rate=attendance_rate,
                average_confidence=average_confidence,
                best_streak=best_streak,
                current_streak=current_streak
            )
            
            # Step 6: Return performance metrics
            return GetUserPerformanceResponse(
                success=True,
                performance=performance
            )
            
        except ValueError as e:
            # Handle validation errors from value objects
            return GetUserPerformanceResponse(
                success=False,
                error=f"Invalid performance data: {str(e)}"
            )
        except Exception as e:
            # Handle unexpected errors
            return GetUserPerformanceResponse(
                success=False,
                error=f"Failed to calculate user performance: {str(e)}"
            )
    
    def _get_attendance_records(
        self,
        request: GetUserPerformanceRequest
    ) -> List[AttendanceRecord]:
        """
        Get attendance records for the user within the specified period.
        
        Args:
            request: Get user performance request with user_id and period_days.
        
        Returns:
            List of AttendanceRecord domain entities for the user.
        """
        # Calculate date range for the period
        end_date = date.today()
        start_date = end_date - timedelta(days=request.period_days - 1)
        
        # Get attendance records from repository
        records = self.attendance_repository.get_attendance_history(
            user_id=request.user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Filter to only valid/present records for calculations
        valid_records = [
            record for record in records
            if record.is_present() and record.confidence > 0
        ]
        
        return valid_records

