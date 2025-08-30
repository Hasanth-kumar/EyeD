"""
Repositories package for EyeD AI Attendance System

This package contains data access layer classes that handle
database operations and data persistence.
"""

from .attendance_repository import AttendanceRepository

__all__ = [
    'AttendanceRepository'
]
