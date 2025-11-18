"""
Value objects for face detection and recognition results.

This module defines the data structures used to represent face detection and embedding extraction results.
"""

from dataclasses import dataclass
from typing import List, Optional
import numpy as np


@dataclass
class FaceLocation:
    """Represents the location of a detected face in an image."""
    x: int
    y: int
    width: int
    height: int


@dataclass
class DetectionResult:
    """Represents the result of face detection in an image."""
    faces_detected: bool
    face_count: int
    faces: List[FaceLocation]
    confidence_scores: List[float]
    
    def __post_init__(self):
        """Validate that face_count matches the length of faces and confidence_scores."""
        if self.face_count != len(self.faces):
            raise ValueError(
                f"face_count ({self.face_count}) must match length of faces ({len(self.faces)})"
            )
        if self.face_count != len(self.confidence_scores):
            raise ValueError(
                f"face_count ({self.face_count}) must match length of confidence_scores "
                f"({len(self.confidence_scores)})"
            )


@dataclass
class EmbeddingResult:
    """Represents the result of face embedding extraction."""
    embedding: np.ndarray
    dimension: int
    extraction_time_ms: float
    
    def __post_init__(self):
        """Validate that dimension matches the embedding length."""
        if self.dimension != len(self.embedding):
            raise ValueError(
                f"dimension ({self.dimension}) must match length of embedding ({len(self.embedding)})"
            )


@dataclass
class RecognitionResult:
    """Represents the result of face recognition/matching."""
    user_id: str
    user_name: str
    confidence: float
    match_score: float
    
    def __post_init__(self):
        """Validate that confidence and match_score are in valid range."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"confidence ({self.confidence}) must be between 0.0 and 1.0"
            )
        if not 0.0 <= self.match_score <= 1.0:
            raise ValueError(
                f"match_score ({self.match_score}) must be between 0.0 and 1.0"
            )


@dataclass
class QualityResult:
    """Represents the result of face quality assessment."""
    overall_score: float
    resolution_score: float
    brightness_score: float
    contrast_score: float
    sharpness_score: float
    is_suitable: bool
    reason: Optional[str] = None
    
    def __post_init__(self):
        """Validate that all scores are in valid range."""
        if not 0.0 <= self.overall_score <= 1.0:
            raise ValueError(
                f"overall_score ({self.overall_score}) must be between 0.0 and 1.0"
            )
        if not 0.0 <= self.resolution_score <= 1.0:
            raise ValueError(
                f"resolution_score ({self.resolution_score}) must be between 0.0 and 1.0"
            )
        if not 0.0 <= self.brightness_score <= 1.0:
            raise ValueError(
                f"brightness_score ({self.brightness_score}) must be between 0.0 and 1.0"
            )
        if not 0.0 <= self.contrast_score <= 1.0:
            raise ValueError(
                f"contrast_score ({self.contrast_score}) must be between 0.0 and 1.0"
            )
        if not 0.0 <= self.sharpness_score <= 1.0:
            raise ValueError(
                f"sharpness_score ({self.sharpness_score}) must be between 0.0 and 1.0"
            )
