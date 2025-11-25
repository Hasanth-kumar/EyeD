"""
Value objects for core attendance operations.

Contains data classes for validation results used in core attendance operations.
These are pure data structures with no domain or infrastructure dependencies.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of a single validation check in core attendance operations.
    
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
class IndividualAttendanceResult:
    """
    Result of attendance marking for a single individual in class attendance.
    
    Attributes:
        user_id: Unique identifier for the user.
        user_name: Display name of the user.
        confidence: Confidence score of the face recognition (0.0 to 1.0).
        success: Whether attendance was successfully marked.
        error_message: Optional error message if attendance marking failed.
    
    Examples:
        >>> result = IndividualAttendanceResult(
        ...     user_id="user123",
        ...     user_name="John Doe",
        ...     confidence=0.85,
        ...     success=True,
        ...     error_message=None
        ... )
        >>> result.success
        True
    """
    
    user_id: str
    user_name: str
    confidence: float
    success: bool
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Validate the value object after initialization."""
        if not self.user_id:
            raise ValueError("user_id cannot be empty")
        if not self.user_name:
            raise ValueError("user_name cannot be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not self.success and not self.error_message:
            raise ValueError("error_message must be provided when success is False")


@dataclass(frozen=True)
class ClassAttendanceResult:
    """
    Result of class attendance marking containing all individual results.
    
    Attributes:
        results: List of individual attendance results for each recognized face.
    
    Examples:
        >>> individual_results = [
        ...     IndividualAttendanceResult(
        ...         user_id="user123",
        ...         user_name="John Doe",
        ...         confidence=0.85,
        ...         success=True
        ...     )
        ... ]
        >>> class_result = ClassAttendanceResult(results=individual_results)
        >>> len(class_result.results)
        1
    """
    
    results: List[IndividualAttendanceResult]
    
    def __post_init__(self):
        """Validate the value object after initialization."""
        if not isinstance(self.results, list):
            raise ValueError("results must be a list")








