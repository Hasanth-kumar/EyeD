"""
Value objects for gamification domain services.

Contains immutable value objects used in gamification calculations.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import List


@dataclass(frozen=True)
class StreakBreakdown:
    """
    Immutable value object representing streak calculation results.
    
    Attributes:
        current_streak: Current consecutive day streak (from today backwards).
        max_streak: Maximum consecutive day streak in the record set.
        streak_dates: List of dates that are part of the current streak.
    
    Examples:
        >>> breakdown = StreakBreakdown(
        ...     current_streak=5,
        ...     max_streak=10,
        ...     streak_dates=[date(2025, 1, 1), date(2025, 1, 2)]
        ... )
        >>> breakdown.current_streak
        5
    """
    
    current_streak: int
    max_streak: int
    streak_dates: List[date]
    
    def __post_init__(self):
        """Validate the value object after initialization."""
        if self.current_streak < 0:
            raise ValueError("current_streak must be non-negative")
        if self.max_streak < 0:
            raise ValueError("max_streak must be non-negative")
        if self.max_streak < self.current_streak:
            raise ValueError("max_streak cannot be less than current_streak")
        if len(self.streak_dates) != self.current_streak:
            raise ValueError(
                f"streak_dates length ({len(self.streak_dates)}) "
                f"must match current_streak ({self.current_streak})"
            )


@dataclass(frozen=True)
class UserRankingData:
    """
    Immutable value object representing user data for leaderboard ranking.
    
    Contains pre-calculated metrics for a user that will be used for ranking.
    This is the input to the leaderboard generator.
    
    Attributes:
        user_id: Unique identifier for the user.
        user_name: Display name of the user.
        attendance_rate: Attendance rate percentage (0-100).
        streak: Current consecutive attendance streak.
        total_badges: Total number of badges earned by the user.
    
    Examples:
        >>> user_data = UserRankingData(
        ...     user_id="user123",
        ...     user_name="John Doe",
        ...     attendance_rate=85.5,
        ...     streak=10,
        ...     total_badges=5
        ... )
        >>> user_data.user_id
        'user123'
    """
    
    user_id: str
    user_name: str
    attendance_rate: float
    streak: int
    total_badges: int
    
    def __post_init__(self):
        """Validate the value object after initialization."""
        if not self.user_id:
            raise ValueError("user_id cannot be empty")
        if not self.user_name:
            raise ValueError("user_name cannot be empty")
        if not 0.0 <= self.attendance_rate <= 100.0:
            raise ValueError("attendance_rate must be between 0.0 and 100.0")
        if self.streak < 0:
            raise ValueError("streak must be non-negative")
        if self.total_badges < 0:
            raise ValueError("total_badges must be non-negative")


@dataclass(frozen=True)
class RankedUser:
    """
    Immutable value object representing a single user in a leaderboard ranking.
    
    Attributes:
        rank: The rank position (1-based, where 1 is the highest).
        user_id: Unique identifier for the user.
        user_name: Display name of the user.
        score: The metric score used for ranking.
    
    Examples:
        >>> ranked = RankedUser(
        ...     rank=1,
        ...     user_id="user123",
        ...     user_name="John Doe",
        ...     score=95.5
        ... )
        >>> ranked.rank
        1
    """
    
    rank: int
    user_id: str
    user_name: str
    score: float
    
    def __post_init__(self):
        """Validate the value object after initialization."""
        if self.rank < 1:
            raise ValueError("rank must be at least 1")
        if not self.user_id:
            raise ValueError("user_id cannot be empty")
        if not self.user_name:
            raise ValueError("user_name cannot be empty")


@dataclass(frozen=True)
class Leaderboard:
    """
    Immutable value object representing a generated leaderboard.
    
    Contains the ranked list of users and metadata about the leaderboard.
    
    Attributes:
        ranked_users: List of ranked users, sorted by rank (highest first).
        metric_used: The metric used for ranking (e.g., "attendance_rate", "streak", "total_badges").
        generated_at: Timestamp when the leaderboard was generated.
        total_users: Total number of users in the leaderboard.
    
    Examples:
        >>> leaderboard = Leaderboard(
        ...     ranked_users=[ranked_user1, ranked_user2],
        ...     metric_used="attendance_rate",
        ...     generated_at=datetime.now(),
        ...     total_users=2
        ... )
        >>> leaderboard.metric_used
        'attendance_rate'
    """
    
    ranked_users: List[RankedUser]
    metric_used: str
    generated_at: datetime
    total_users: int
    
    def __post_init__(self):
        """Validate the value object after initialization."""
        if not self.metric_used:
            raise ValueError("metric_used cannot be empty")
        if self.total_users < 0:
            raise ValueError("total_users must be non-negative")
        if len(self.ranked_users) != self.total_users:
            raise ValueError(
                f"ranked_users length ({len(self.ranked_users)}) "
                f"must match total_users ({self.total_users})"
            )
        # Validate ranks are sequential and start at 1
        for i, user in enumerate(self.ranked_users):
            if user.rank != i + 1:
                raise ValueError(
                    f"Rank mismatch: expected rank {i + 1}, got {user.rank}"
                )

