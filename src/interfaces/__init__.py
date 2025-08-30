"""
Interfaces package for EyeD AI Attendance System

This package contains abstract base classes and interfaces that define
clear contracts for all major system components.
"""

from .face_database_interface import FaceDatabaseInterface
from .attendance_manager_interface import AttendanceManagerInterface
from .recognition_interface import RecognitionInterface
from .liveness_interface import LivenessInterface
from .analytics_interface import AnalyticsInterface

__all__ = [
    'FaceDatabaseInterface',
    'AttendanceManagerInterface', 
    'RecognitionInterface',
    'LivenessInterface',
    'AnalyticsInterface'
]
