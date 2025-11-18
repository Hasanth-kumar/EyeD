"""
Core face detection and recognition module for EyeD AI Attendance System.

This module provides pure face detection and embedding extraction logic with no infrastructure dependencies.
"""

from .detector import FaceDetector
from .embedding_extractor import EmbeddingExtractor
from .recognizer import FaceRecognizer
from .quality_assessor import QualityAssessor
from .value_objects import (
    FaceLocation,
    DetectionResult,
    EmbeddingResult,
    RecognitionResult,
    QualityResult
)

__all__ = [
    'FaceDetector',
    'EmbeddingExtractor',
    'FaceRecognizer',
    'QualityAssessor',
    'FaceLocation',
    'DetectionResult',
    'EmbeddingResult',
    'RecognitionResult',
    'QualityResult'
]

