"""
Attendance logging core module.

This module provides pure attendance record creation logic without
infrastructure dependencies.
"""

from .attendance_logger import AttendanceLogger
from .attendance_validator import AttendanceValidator
from .value_objects import ValidationResult

__all__ = ['AttendanceLogger', 'AttendanceValidator', 'ValidationResult']

