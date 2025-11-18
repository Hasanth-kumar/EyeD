"""
Value objects for core attendance operations.

Contains data classes for validation results used in core attendance operations.
These are pure data structures with no domain or infrastructure dependencies.
"""

from dataclasses import dataclass
from typing import Optional


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










