"""
Domain entities for EyeD AI Attendance System.

This module exports all domain entities that represent core business concepts.
All entities are immutable and have no infrastructure dependencies.
"""

from .user import User
from .attendance_record import AttendanceRecord
from .face_embedding import FaceEmbedding
from .badge import Badge, BadgeCategory
from .attendance_session import AttendanceSession

__all__ = [
    'User',
    'AttendanceRecord',
    'FaceEmbedding',
    'Badge',
    'BadgeCategory',
    'AttendanceSession',
]















