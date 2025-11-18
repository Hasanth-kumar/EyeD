"""
Protocol definitions for domain services.

This module defines structural protocols (using typing.Protocol) for domain services
to enable dependency inversion. These protocols define contracts that implementations
must follow, allowing the domain layer to depend on abstractions rather than concrete
implementations.

Following the Interface Segregation Principle, each protocol is small and focused
on a single responsibility.
"""

from datetime import date, datetime, time
from typing import Protocol, List, Dict, Optional

from domain.entities.attendance_record import AttendanceRecord
from domain.entities.badge import Badge
from domain.shared.attendance_value_objects import (
    ValidationResult,
    EligibilityResult,
    AttendanceRules
)
from domain.services.analytics.value_objects import (
    DailyStatistics,
    UserPerformance
)
from domain.services.gamification.value_objects import (
    StreakBreakdown,
    UserRankingData,
    Leaderboard
)


class BadgeCalculatorProtocol(Protocol):
    """
    Protocol for badge calculation service.
    
    Defines the contract for calculating badges based on attendance data.
    """
    
    def calculate(
        self,
        attendance_data: List[AttendanceRecord],
        period_days: int
    ) -> List[Badge]:
        """
        Calculate all badges for the given attendance data.
        
        Args:
            attendance_data: List of attendance records for badge calculation.
            period_days: Number of days in the evaluation period.
        
        Returns:
            List of Badge entities earned by the user.
        """
        ...


class StreakCalculatorProtocol(Protocol):
    """
    Protocol for streak calculation service.
    
    Defines the contract for calculating attendance streaks.
    """
    
    def calculate_current_streak(
        self,
        records: List[AttendanceRecord]
    ) -> int:
        """
        Calculate the current consecutive day streak from today backwards.
        
        Args:
            records: List of attendance records, should be sorted by date
                    (most recent first is preferred, but not required).
        
        Returns:
            Current consecutive day streak count (0 if no streak).
        """
        ...
    
    def calculate_max_streak(
        self,
        records: List[AttendanceRecord]
    ) -> int:
        """
        Calculate the maximum consecutive day streak from all records.
        
        Args:
            records: List of attendance records, should be sorted by date
                    (ascending is preferred, but not required).
        
        Returns:
            Maximum consecutive day streak count (0 if no records).
        """
        ...
    
    def calculate_streak_breakdown(
        self,
        records: List[AttendanceRecord]
    ) -> StreakBreakdown:
        """
        Calculate complete streak breakdown including current streak, max streak, and dates.
        
        Args:
            records: List of attendance records, should be sorted by date
                    (most recent first is preferred for current streak calculation).
        
        Returns:
            StreakBreakdown value object with all streak metrics.
        """
        ...


class MetricsCalculatorProtocol(Protocol):
    """
    Protocol for metrics calculation service.
    
    Defines the contract for calculating attendance metrics.
    """
    
    def calculate_attendance_rate(
        self,
        records: List[AttendanceRecord],
        period_days: int
    ) -> float:
        """
        Calculate attendance rate as a percentage.
        
        Args:
            records: List of attendance records to analyze.
            period_days: Number of days in the evaluation period.
        
        Returns:
            Attendance rate percentage (0.0 to 100.0).
        """
        ...
    
    def calculate_average_confidence(
        self,
        records: List[AttendanceRecord]
    ) -> float:
        """
        Calculate average confidence score across all records.
        
        Args:
            records: List of attendance records to analyze.
        
        Returns:
            Average confidence score (0.0 to 1.0), or 0.0 if no valid records.
        """
        ...
    
    def calculate_liveness_verification_rate(
        self,
        records: List[AttendanceRecord]
    ) -> float:
        """
        Calculate liveness verification rate as a percentage.
        
        Args:
            records: List of attendance records to analyze.
        
        Returns:
            Liveness verification rate percentage (0.0 to 100.0).
        """
        ...
    
    def calculate_daily_statistics(
        self,
        records: List[AttendanceRecord]
    ) -> Dict[date, DailyStatistics]:
        """
        Calculate daily statistics for all dates in the records.
        
        Args:
            records: List of attendance records to analyze.
        
        Returns:
            Dictionary mapping date to DailyStatistics value object.
        """
        ...
    
    def calculate_user_performance(
        self,
        user_id: str,
        records: List[AttendanceRecord],
        period_days: int = 30
    ) -> UserPerformance:
        """
        Calculate performance metrics for a specific user.
        
        Args:
            user_id: ID of the user to calculate performance for.
            records: List of attendance records (should include records for this user).
            period_days: Number of days in the evaluation period (default: 30).
        
        Returns:
            UserPerformance value object with calculated metrics.
        """
        ...


class AttendanceValidatorProtocol(Protocol):
    """
    Protocol for attendance validation service.
    
    Defines the contract for validating attendance business rules.
    """
    
    def validate_daily_limit(
        self,
        records: List[AttendanceRecord],
        max_entries: int
    ) -> ValidationResult:
        """
        Validate that the number of attendance records does not exceed the daily limit.
        
        Args:
            records: List of attendance records for a given day.
            max_entries: Maximum number of entries allowed per day.
        
        Returns:
            ValidationResult indicating whether the daily limit is satisfied.
        """
        ...
    
    def validate_confidence_threshold(
        self,
        confidence: float,
        threshold: float
    ) -> ValidationResult:
        """
        Validate that the confidence score meets the minimum threshold.
        
        Args:
            confidence: Confidence score from face recognition (0.0 to 1.0).
            threshold: Minimum required confidence threshold.
        
        Returns:
            ValidationResult indicating whether the confidence threshold is met.
        """
        ...
    
    def validate_liveness_required(
        self,
        liveness_verified: bool,
        required: bool
    ) -> ValidationResult:
        """
        Validate that liveness verification is satisfied if required.
        
        Args:
            liveness_verified: Whether liveness verification passed.
            required: Whether liveness verification is required.
        
        Returns:
            ValidationResult indicating whether liveness requirements are met.
        """
        ...
    
    def validate_time_window(
        self,
        timestamp: datetime,
        start_time: Optional[time],
        end_time: Optional[time]
    ) -> ValidationResult:
        """
        Validate that the timestamp falls within the allowed time window.
        
        Args:
            timestamp: The datetime to validate.
            start_time: Start time of the allowed window (None means no restriction).
            end_time: End time of the allowed window (None means no restriction).
        
        Returns:
            ValidationResult indicating whether the timestamp is within the window.
        """
        ...
    
    def validate_eligibility(
        self,
        user_id: str,
        target_date: date,
        existing_records: List[AttendanceRecord],
        rules: AttendanceRules
    ) -> EligibilityResult:
        """
        Validate overall eligibility for attendance on a specific date.
        
        Args:
            user_id: ID of the user to validate.
            target_date: Date to check eligibility for.
            existing_records: List of all existing attendance records (will be filtered).
            rules: AttendanceRules containing business rules to apply.
        
        Returns:
            EligibilityResult with comprehensive validation results.
        """
        ...


class LeaderboardGeneratorProtocol(Protocol):
    """
    Protocol for leaderboard generation service.
    
    Defines the contract for generating leaderboards from user ranking data.
    """
    
    def generate(
        self,
        users_data: List[UserRankingData],
        metric: str
    ) -> Leaderboard:
        """
        Generate a leaderboard based on the specified metric.
        
        Args:
            users_data: List of user ranking data with pre-calculated metrics.
            metric: The metric to use for ranking. Must be one of:
                - "attendance_rate"
                - "streak"
                - "total_badges"
        
        Returns:
            Leaderboard value object containing ranked users.
        
        Raises:
            ValueError: If metric is not supported or users_data is empty.
        """
        ...
    
    def rank_by_attendance_rate(
        self,
        users_data: List[UserRankingData]
    ) -> Leaderboard:
        """
        Rank users by attendance rate (highest first).
        
        Args:
            users_data: List of user ranking data with pre-calculated metrics.
        
        Returns:
            Leaderboard value object with users ranked by attendance_rate.
        """
        ...
    
    def rank_by_streak(
        self,
        users_data: List[UserRankingData]
    ) -> Leaderboard:
        """
        Rank users by current streak (highest first).
        
        Args:
            users_data: List of user ranking data with pre-calculated metrics.
        
        Returns:
            Leaderboard value object with users ranked by streak.
        """
        ...
    
    def rank_by_total_badges(
        self,
        users_data: List[UserRankingData]
    ) -> Leaderboard:
        """
        Rank users by total badges earned (highest first).
        
        Args:
            users_data: List of user ranking data with pre-calculated metrics.
        
        Returns:
            Leaderboard value object with users ranked by total_badges.
        """
        ...

