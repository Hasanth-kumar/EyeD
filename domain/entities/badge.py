"""
Badge domain entity.

Represents a badge/achievement in the EyeD AI Attendance System.
This is a pure domain entity with no infrastructure dependencies.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any


class BadgeCategory(str, Enum):
    """
    Enumeration of badge categories.
    
    Attributes:
        ATTENDANCE: Badges related to attendance consistency.
        STREAK: Badges related to consecutive attendance streaks.
        TIMING: Badges related to arrival timing patterns.
        QUALITY: Badges related to face recognition quality.
    """
    
    ATTENDANCE = "attendance"
    STREAK = "streak"
    TIMING = "timing"
    QUALITY = "quality"


@dataclass(frozen=True)
class Badge:
    """
    Immutable badge entity.
    
    Represents a badge/achievement earned by a user in the attendance system.
    
    Attributes:
        badge_id: Unique identifier for the badge.
        name: Name of the badge.
        category: Category of the badge (attendance/streak/timing/quality).
        description: Description of what the badge represents.
        criteria: Dictionary containing the criteria that must be met to earn this badge.
        earned_at: Date and time when the badge was earned.
        user_id: ID of the user who earned this badge.
    
    Examples:
        >>> from datetime import datetime
        >>> badge = Badge(
        ...     badge_id="badge_001",
        ...     name="🌟 Perfect Week",
        ...     category=BadgeCategory.ATTENDANCE,
        ...     description="Attended all 5 days in a week",
        ...     criteria={"total_entries": 5, "required_count": 5},
        ...     earned_at=datetime.now(),
        ...     user_id="user_001"
        ... )
        >>> badge.category
        <BadgeCategory.ATTENDANCE: 'attendance'>
    """
    
    badge_id: str
    name: str
    category: BadgeCategory
    description: str
    criteria: Dict[str, Any]
    earned_at: datetime
    user_id: str
    
    def is_attendance_badge(self) -> bool:
        """
        Check if this is an attendance category badge.
        
        Returns:
            True if category is ATTENDANCE, False otherwise.
        """
        return self.category == BadgeCategory.ATTENDANCE
    
    def is_streak_badge(self) -> bool:
        """
        Check if this is a streak category badge.
        
        Returns:
            True if category is STREAK, False otherwise.
        """
        return self.category == BadgeCategory.STREAK
    
    def is_timing_badge(self) -> bool:
        """
        Check if this is a timing category badge.
        
        Returns:
            True if category is TIMING, False otherwise.
        """
        return self.category == BadgeCategory.TIMING
    
    def is_quality_badge(self) -> bool:
        """
        Check if this is a quality category badge.
        
        Returns:
            True if category is QUALITY, False otherwise.
        """
        return self.category == BadgeCategory.QUALITY













