"""
Core shared components for EyeD AI Attendance System.

This module exports all shared core constants and value objects
that are used across the core layer.

All components are immutable and have no domain or infrastructure dependencies.
"""

from .constants import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_LIVENESS_THRESHOLD,
    MIN_FACE_QUALITY_SCORE,
)

__all__ = [
    'DEFAULT_CONFIDENCE_THRESHOLD',
    'DEFAULT_LIVENESS_THRESHOLD',
    'MIN_FACE_QUALITY_SCORE',
]












