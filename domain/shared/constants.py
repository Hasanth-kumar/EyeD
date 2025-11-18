"""
Domain constants for EyeD AI Attendance System.

This module contains all shared domain constants used across the system.
These constants represent business rules and thresholds that are central
to the domain logic.

All constants are immutable and have no infrastructure dependencies.
"""

# Face Recognition Constants
DEFAULT_CONFIDENCE_THRESHOLD = 0.45
"""Default minimum confidence score required for face recognition (0.0 to 1.0)."""

MIN_BLINKS_REQUIRED = 3
"""Minimum number of blinks required for liveness verification."""

MIN_FACE_QUALITY_SCORE = 0.5
"""Minimum face quality score required for attendance (0.0 to 1.0)."""

HIGH_QUALITY_THRESHOLD = 0.8
"""Threshold for high-quality face recognition scores (0.0 to 1.0)."""

# Attendance Constants
MAX_DAILY_ATTENDANCE_ENTRIES = 5
"""Maximum number of attendance entries allowed per user per day."""

PERFECT_ATTENDANCE_THRESHOLD = 0.95
"""Threshold for perfect attendance percentage (0.0 to 1.0)."""

# Timing Constants
EARLY_BIRD_HOUR = 8
"""Hour threshold for early bird arrivals (0-23). Arrivals at or before this hour are considered early."""

LATE_COMER_HOUR = 9
"""Hour threshold for late comers (0-23). Arrivals after this hour are considered late."""

# Badge Thresholds - Attendance
PERFECT_WEEK_ENTRIES = 5
"""Number of entries required for perfect week badge."""

PERFECT_MONTH_ENTRIES = 20
"""Number of entries required for perfect month badge."""

CONSISTENCY_MASTER_ENTRIES = 50
"""Total entries required for consistency master badge."""

DEDICATION_CHAMPION_ENTRIES = 100
"""Total entries required for dedication champion badge."""

# Badge Thresholds - Streak
WEEK_WARRIOR_STREAK = 7
"""Consecutive days required for week warrior badge."""

MONTH_MASTER_STREAK = 30
"""Consecutive days required for month master badge."""

STREAK_LEGEND_STREAK = 60
"""Consecutive days required for streak legend badge."""

# Badge Thresholds - Timing
EARLY_BIRD_COUNT = 5
"""Number of early arrivals required for early bird badge."""

PUNCTUALITY_PRO_COUNT = 10
"""Number of on-time arrivals required for punctuality pro badge."""

TIME_MASTER_COUNT = 20
"""Number of consistent timing arrivals required for time master badge."""

# Badge Thresholds - Quality
QUALITY_SEEKER_COUNT = 5
"""Number of high-quality entries required for quality seeker badge."""

QUALITY_MASTER_COUNT = 15
"""Number of high-quality entries required for quality master badge."""

PERFECTIONIST_COUNT = 30
"""Number of high-quality entries required for perfectionist badge."""


