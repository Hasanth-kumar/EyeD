"""
Calculate badges use case.

Orchestrates badge calculation workflow with attendance data.
"""

from dataclasses import dataclass
from typing import Optional, List, Protocol
from datetime import date, timedelta

from domain.entities.badge import Badge
from domain.entities.attendance_record import AttendanceRecord
from domain.services.gamification import (
    BadgeCalculator,
    BadgeDefinitions,
    StreakCalculator
)


@dataclass
class CalculateBadgesRequest:
    """Request for calculating badges."""
    user_id: str
    period_days: int = 30


@dataclass
class CalculateBadgesResponse:
    """Response from badge calculation."""
    success: bool
    badges: Optional[List[Badge]] = None
    total_badges: int = 0
    badge_score: float = 0.0
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


class CalculateBadgesUseCase:
    """
    Orchestrates badge calculation workflow.
    
    This use case coordinates attendance data retrieval, badge definitions,
    badge calculation, and streak calculation to determine badges earned by a user.
    """
    
    def __init__(
        self,
        badge_calculator: BadgeCalculator,
        badge_definitions: BadgeDefinitions,
        streak_calculator: StreakCalculator,
        attendance_repository: AttendanceRepositoryProtocol
    ):
        """
        Initialize CalculateBadgesUseCase.
        
        Args:
            badge_calculator: Service for calculating badges from attendance data.
            badge_definitions: Value object containing badge definitions and criteria.
            streak_calculator: Service for calculating attendance streaks.
            attendance_repository: Attendance data persistence repository.
        """
        self.badge_calculator = badge_calculator
        self.badge_definitions = badge_definitions
        self.streak_calculator = streak_calculator
        self.attendance_repository = attendance_repository
    
    def execute(self, request: CalculateBadgesRequest) -> CalculateBadgesResponse:
        """
        Execute badge calculation workflow.
        
        Args:
            request: Calculate badges request with user_id and period_days.
        
        Returns:
            CalculateBadgesResponse with calculated badges and metrics.
        """
        try:
            # Step 1: Get attendance records for user/period
            attendance_records = self._get_attendance_records(
                request.user_id,
                request.period_days
            )
            
            # Step 2: Get badge definitions (already injected, but validate)
            if not self.badge_definitions:
                return CalculateBadgesResponse(
                    success=False,
                    badges=[],
                    error="Badge definitions not available"
                )
            
            # Step 3: Calculate badges using BadgeCalculator
            badges = self.badge_calculator.calculate(
                attendance_data=attendance_records,
                period_days=request.period_days
            )
            
            # Step 4: Calculate streaks (if needed for badge calculation)
            # Note: BadgeCalculator handles streak badge calculations internally,
            # but we calculate streaks here for potential future use or validation
            _ = self.streak_calculator.calculate_streak_breakdown(
                attendance_records
            )
            
            # Step 5: Calculate badge score using domain service and return response
            badge_score = self.badge_calculator.calculate_badge_score(badges)
            
            return CalculateBadgesResponse(
                success=True,
                badges=badges,
                total_badges=len(badges),
                badge_score=badge_score
            )
            
        except Exception as e:
            # Handle unexpected errors
            return CalculateBadgesResponse(
                success=False,
                badges=[],
                error=f"Unexpected error during badge calculation: {str(e)}"
            )
    
    def _get_attendance_records(
        self,
        user_id: str,
        period_days: int
    ) -> List[AttendanceRecord]:
        """
        Get attendance records for user within the specified period.
        
        Args:
            user_id: User ID to get records for.
            period_days: Number of days to look back from today.
        
        Returns:
            List of AttendanceRecord entities for the user within the period.
        """
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days - 1)
        
        # Retrieve attendance records from repository
        records = self.attendance_repository.get_attendance_history(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return records

