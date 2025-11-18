"""
Core liveness detection module for EyeD AI Attendance System.

This module provides pure liveness detection logic with no infrastructure dependencies.
"""

from .blink_detector import BlinkDetector
from .landmark_extractor import LandmarkExtractor
from .value_objects import BlinkResult

__all__ = [
    'BlinkDetector',
    'LandmarkExtractor',
    'BlinkResult',
]

