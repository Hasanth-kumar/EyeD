"""
Shared domain components for EyeD AI Attendance System.

This module exports all shared domain constants, enums, and exceptions
that are used across the domain layer.

All components are immutable and have no infrastructure dependencies.
"""

from .constants import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    MIN_BLINKS_REQUIRED,
    MIN_FACE_QUALITY_SCORE,
    HIGH_QUALITY_THRESHOLD,
    MAX_DAILY_ATTENDANCE_ENTRIES,
    PERFECT_ATTENDANCE_THRESHOLD,
    EARLY_BIRD_HOUR,
    LATE_COMER_HOUR,
    PERFECT_WEEK_ENTRIES,
    PERFECT_MONTH_ENTRIES,
    CONSISTENCY_MASTER_ENTRIES,
    DEDICATION_CHAMPION_ENTRIES,
    WEEK_WARRIOR_STREAK,
    MONTH_MASTER_STREAK,
    STREAK_LEGEND_STREAK,
    EARLY_BIRD_COUNT,
    PUNCTUALITY_PRO_COUNT,
    TIME_MASTER_COUNT,
    QUALITY_SEEKER_COUNT,
    QUALITY_MASTER_COUNT,
    PERFECTIONIST_COUNT,
)

from .enums import (
    AttendanceStatus,
    BadgeCategory,
    VerificationStage,
    UserStatus,
)

from .exceptions import (
    DomainException,
    InvalidAttendanceRecordError,
    InvalidConfidenceError,
    DailyLimitExceededError,
    LivenessVerificationFailedError,
    FaceNotRecognizedError,
    FaceDetectionFailedError,
    InsufficientQualityError,
    EmbeddingExtractionFailedError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

from .attendance_value_objects import (
    ValidationResult,
    EligibilityResult,
    AttendanceRules,
)

__all__ = [
    # Constants
    'DEFAULT_CONFIDENCE_THRESHOLD',
    'MIN_BLINKS_REQUIRED',
    'MIN_FACE_QUALITY_SCORE',
    'HIGH_QUALITY_THRESHOLD',
    'MAX_DAILY_ATTENDANCE_ENTRIES',
    'PERFECT_ATTENDANCE_THRESHOLD',
    'EARLY_BIRD_HOUR',
    'LATE_COMER_HOUR',
    'PERFECT_WEEK_ENTRIES',
    'PERFECT_MONTH_ENTRIES',
    'CONSISTENCY_MASTER_ENTRIES',
    'DEDICATION_CHAMPION_ENTRIES',
    'WEEK_WARRIOR_STREAK',
    'MONTH_MASTER_STREAK',
    'STREAK_LEGEND_STREAK',
    'EARLY_BIRD_COUNT',
    'PUNCTUALITY_PRO_COUNT',
    'TIME_MASTER_COUNT',
    'QUALITY_SEEKER_COUNT',
    'QUALITY_MASTER_COUNT',
    'PERFECTIONIST_COUNT',
    # Enums
    'AttendanceStatus',
    'BadgeCategory',
    'VerificationStage',
    'UserStatus',
    # Exceptions
    'DomainException',
    'InvalidAttendanceRecordError',
    'InvalidConfidenceError',
    'DailyLimitExceededError',
    'LivenessVerificationFailedError',
    'FaceNotRecognizedError',
    'FaceDetectionFailedError',
    'InsufficientQualityError',
    'EmbeddingExtractionFailedError',
    'UserAlreadyExistsError',
    'UserNotFoundError',
    # Attendance Value Objects
    'ValidationResult',
    'EligibilityResult',
    'AttendanceRules',
]


