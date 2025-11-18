"""
Value objects for attendance validation.

Contains data classes for validation results and business rules.
These will be used by core/attendance/ when it is built.
"""

from dataclasses import dataclass
from datetime import time
from typing import List, Optional


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of a single validation check.
    
    Attributes:
        is_valid: Whether the validation passed.
        message: Human-readable message describing the validation result.
        error_code: Optional error code for programmatic handling.
    """
    is_valid: bool
    message: str
    error_code: Optional[str] = None
    
    @classmethod
    def success(cls, message: str = "Validation passed") -> 'ValidationResult':
        """Create a successful validation result."""
        return cls(is_valid=True, message=message)
    
    @classmethod
    def failure(cls, message: str, error_code: Optional[str] = None) -> 'ValidationResult':
        """Create a failed validation result."""
        return cls(is_valid=False, message=message, error_code=error_code)


@dataclass(frozen=True)
class EligibilityResult:
    """
    Result of attendance eligibility validation.
    
    Attributes:
        is_eligible: Whether the user is eligible for attendance.
        user_id: ID of the user being validated.
        date: Date being validated.
        validation_results: List of individual validation results.
        reason: Human-readable reason for eligibility or ineligibility.
        daily_entries: Number of existing attendance entries for the date.
        max_daily_entries: Maximum allowed entries per day.
    """
    is_eligible: bool
    user_id: str
    date: str  # ISO format date string
    validation_results: List[ValidationResult]
    reason: str
    daily_entries: int
    max_daily_entries: int
    
    @classmethod
    def eligible(
        cls,
        user_id: str,
        date: str,
        validation_results: List[ValidationResult],
        daily_entries: int,
        max_daily_entries: int,
        reason: str = "Eligible for attendance"
    ) -> 'EligibilityResult':
        """Create an eligible result."""
        return cls(
            is_eligible=True,
            user_id=user_id,
            date=date,
            validation_results=validation_results,
            reason=reason,
            daily_entries=daily_entries,
            max_daily_entries=max_daily_entries
        )
    
    @classmethod
    def ineligible(
        cls,
        user_id: str,
        date: str,
        validation_results: List[ValidationResult],
        daily_entries: int,
        max_daily_entries: int,
        reason: str
    ) -> 'EligibilityResult':
        """Create an ineligible result."""
        return cls(
            is_eligible=False,
            user_id=user_id,
            date=date,
            validation_results=validation_results,
            reason=reason,
            daily_entries=daily_entries,
            max_daily_entries=max_daily_entries
        )


@dataclass(frozen=True)
class AttendanceRules:
    """
    Business rules for attendance validation.
    
    This is a value object containing all configurable business rules
    for attendance validation. It is immutable and has no behavior.
    
    Attributes:
        max_daily_entries: Maximum number of attendance entries allowed per day.
        confidence_threshold: Minimum confidence score required for attendance.
        liveness_required: Whether liveness verification is required.
        start_time: Optional start time for attendance window (None means no restriction).
        end_time: Optional end time for attendance window (None means no restriction).
    """
    max_daily_entries: int = 5
    confidence_threshold: float = 0.6
    liveness_required: bool = True
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    
    def __post_init__(self):
        """Validate rule values."""
        if self.max_daily_entries < 1:
            raise ValueError("max_daily_entries must be at least 1")
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be between 0.0 and 1.0")
        if self.start_time is not None and self.end_time is not None:
            if self.start_time >= self.end_time:
                raise ValueError("start_time must be before end_time")










