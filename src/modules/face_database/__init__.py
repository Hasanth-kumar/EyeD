"""
Face Database Package for EyeD AI Attendance System

This package provides modular face database components following
the Single-Responsibility Principle.
"""

from .face_storage import FaceStorage
from .embedding_manager import EmbeddingManager
from .face_validator import FaceValidator
from .backup_manager import BackupManager
from .face_database import FaceDatabase

__all__ = [
    'FaceStorage',
    'EmbeddingManager', 
    'FaceValidator',
    'BackupManager',
    'FaceDatabase'
]
