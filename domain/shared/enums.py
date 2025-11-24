"""
Domain enums for EyeD AI Attendance System.

This module contains all shared enumerations used across the domain.
These enums replace string literals and provide type safety.

All enums are immutable and have no infrastructure dependencies.
"""

from enum import Enum


class AttendanceStatus(str, Enum):
    """
    Enumeration of attendance status values.
    
    Attributes:
        PRESENT: User is present and attendance is valid.
        ABSENT: User is absent or attendance is invalid.
        LATE: User arrived late (after the late comer hour).
        EARLY: User arrived early (at or before the early bird hour).
    """
    
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"
    EARLY = "Early"


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


class VerificationStage(str, Enum):
    """
    Enumeration of verification stages in the attendance process.
    
    Attributes:
        INITIAL: Initial stage before any verification.
        RECOGNITION: Face recognition stage.
        LIVENESS: Liveness verification stage.
        COMPLETED: Verification completed successfully.
    """
    
    INITIAL = "Initial"
    RECOGNITION = "Recognition"
    LIVENESS = "Liveness"
    COMPLETED = "Completed"


class UserStatus(str, Enum):
    """
    Enumeration of user account status values.
    
    Attributes:
        ACTIVE: User account is active and can use the system.
        INACTIVE: User account is inactive and cannot use the system.
        SUSPENDED: User account is suspended and cannot use the system.
    """
    
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"















