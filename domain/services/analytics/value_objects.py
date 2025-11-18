"""
Value objects for analytics domain services.

Contains immutable value objects used in metrics calculations.
"""

from dataclasses import dataclass
from datetime import date
from typing import Dict


@dataclass(frozen=True)
class DailyStatistics:
    """
    Immutable value object representing daily attendance statistics.
    
    Attributes:
        date: The date for these statistics.
        total_entries: Total number of attendance entries for this date.
        unique_users: Number of unique users with attendance on this date.
        average_confidence: Average confidence score for entries on this date.
        liveness_verification_rate: Percentage of entries with liveness verification (0-100).
    
    Examples:
        >>> stats = DailyStatistics(
        ...     date=date(2025, 1, 1),
        ...     total_entries=10,
        ...     unique_users=8,
        ...     average_confidence=0.85,
        ...     liveness_verification_rate=95.0
        ... )
        >>> stats.total_entries
        10
    """
    
    date: date
    total_entries: int
    unique_users: int
    average_confidence: float
    liveness_verification_rate: float
    
    def __post_init__(self):
        """Validate the value object after initialization."""
        if self.total_entries < 0:
            raise ValueError("total_entries must be non-negative")
        if self.unique_users < 0:
            raise ValueError("unique_users must be non-negative")
        if self.unique_users > self.total_entries:
            raise ValueError("unique_users cannot exceed total_entries")
        if not 0.0 <= self.average_confidence <= 1.0:
            raise ValueError("average_confidence must be between 0.0 and 1.0")
        if not 0.0 <= self.liveness_verification_rate <= 100.0:
            raise ValueError("liveness_verification_rate must be between 0.0 and 100.0")


@dataclass(frozen=True)
class UserPerformance:
    """
    Immutable value object representing user performance metrics.
    
    Attributes:
        user_id: Unique identifier for the user.
        total_attendance: Total number of attendance records for this user.
        attendance_rate: Attendance rate percentage (0-100).
        average_confidence: Average confidence score across all records.
        best_streak: Maximum consecutive day streak.
        current_streak: Current consecutive day streak from today backwards.
    
    Examples:
        >>> performance = UserPerformance(
        ...     user_id="user123",
        ...     total_attendance=25,
        ...     attendance_rate=83.3,
        ...     average_confidence=0.87,
        ...     best_streak=10,
        ...     current_streak=5
        ... )
        >>> performance.user_id
        'user123'
    """
    
    user_id: str
    total_attendance: int
    attendance_rate: float
    average_confidence: float
    best_streak: int
    current_streak: int
    
    def __post_init__(self):
        """Validate the value object after initialization."""
        if not self.user_id:
            raise ValueError("user_id cannot be empty")
        if self.total_attendance < 0:
            raise ValueError("total_attendance must be non-negative")
        if not 0.0 <= self.attendance_rate <= 100.0:
            raise ValueError("attendance_rate must be between 0.0 and 100.0")
        if not 0.0 <= self.average_confidence <= 1.0:
            raise ValueError("average_confidence must be between 0.0 and 1.0")
        if self.best_streak < 0:
            raise ValueError("best_streak must be non-negative")
        if self.current_streak < 0:
            raise ValueError("current_streak must be non-negative")
        if self.best_streak < self.current_streak:
            raise ValueError("best_streak cannot be less than current_streak")


@dataclass(frozen=True)
class PeriodSummary:
    """
    Immutable value object representing aggregated statistics for a time period.
    
    Attributes:
        total_entries: Total number of attendance entries in the period.
        unique_users: Number of unique users with attendance in the period.
        average_confidence: Weighted average confidence score across all entries (0.0 to 1.0).
        liveness_verification_rate: Weighted average liveness verification rate (0.0 to 100.0).
    
    Examples:
        >>> summary = PeriodSummary(
        ...     total_entries=150,
        ...     unique_users=25,
        ...     average_confidence=0.85,
        ...     liveness_verification_rate=92.5
        ... )
        >>> summary.total_entries
        150
    """
    
    total_entries: int
    unique_users: int
    average_confidence: float
    liveness_verification_rate: float
    
    def __post_init__(self):
        """Validate the value object after initialization."""
        if self.total_entries < 0:
            raise ValueError("total_entries must be non-negative")
        if self.unique_users < 0:
            raise ValueError("unique_users must be non-negative")
        if self.unique_users > self.total_entries:
            raise ValueError("unique_users cannot exceed total_entries")
        if not 0.0 <= self.average_confidence <= 1.0:
            raise ValueError("average_confidence must be between 0.0 and 1.0")
        if not 0.0 <= self.liveness_verification_rate <= 100.0:
            raise ValueError("liveness_verification_rate must be between 0.0 and 100.0")


@dataclass(frozen=True)
class ArrivalPatterns:
    """
    Immutable value object representing arrival time patterns analysis.
    
    Attributes:
        average_arrival_time_minutes: Average arrival time in minutes since midnight.
        earliest_arrival_minutes: Earliest arrival time in minutes since midnight.
        latest_arrival_minutes: Latest arrival time in minutes since midnight.
        hourly_distribution: Dictionary mapping hour (0-23) to count of arrivals.
        early_bird_count: Number of arrivals at or before threshold hour (default 8).
        on_time_count: Number of arrivals at 9:00-9:15.
        late_count: Number of arrivals after 9:15.
    
    Examples:
        >>> patterns = ArrivalPatterns(
        ...     average_arrival_time_minutes=540.0,
        ...     earliest_arrival_minutes=480.0,
        ...     latest_arrival_minutes=600.0,
        ...     hourly_distribution={8: 5, 9: 10, 10: 2},
        ...     early_bird_count=5,
        ...     on_time_count=8,
        ...     late_count=4
        ... )
        >>> patterns.average_arrival_time_minutes
        540.0
    """
    
    average_arrival_time_minutes: float
    earliest_arrival_minutes: float
    latest_arrival_minutes: float
    hourly_distribution: Dict[int, int]
    early_bird_count: int
    on_time_count: int
    late_count: int
    
    def __post_init__(self):
        """Validate the value object after initialization."""
        if self.average_arrival_time_minutes < 0:
            raise ValueError("average_arrival_time_minutes must be non-negative")
        if self.earliest_arrival_minutes < 0:
            raise ValueError("earliest_arrival_minutes must be non-negative")
        if self.latest_arrival_minutes < 0:
            raise ValueError("latest_arrival_minutes must be non-negative")
        if self.earliest_arrival_minutes > self.latest_arrival_minutes:
            raise ValueError("earliest_arrival_minutes cannot exceed latest_arrival_minutes")
        if not (0 <= self.average_arrival_time_minutes <= 1440):
            raise ValueError("average_arrival_time_minutes must be between 0 and 1440 (24 hours)")
        if any(hour < 0 or hour > 23 for hour in self.hourly_distribution.keys()):
            raise ValueError("hourly_distribution keys must be between 0 and 23")
        if any(count < 0 for count in self.hourly_distribution.values()):
            raise ValueError("hourly_distribution values must be non-negative")
        if self.early_bird_count < 0:
            raise ValueError("early_bird_count must be non-negative")
        if self.on_time_count < 0:
            raise ValueError("on_time_count must be non-negative")
        if self.late_count < 0:
            raise ValueError("late_count must be non-negative")
