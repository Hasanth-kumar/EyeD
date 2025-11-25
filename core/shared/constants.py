"""
Core constants for EyeD AI Attendance System.

This module contains constants used by the core layer for face recognition,
liveness detection, and quality assessment. These are technical thresholds
used in core operations, separate from domain business rules.

All constants are immutable and have no domain or infrastructure dependencies.
"""

# Face Recognition Constants
DEFAULT_EMBEDDING_MODEL = "ArcFace"
"""Default embedding model name. ArcFace provides better accuracy than VGG-Face, especially for smaller/distant faces in group photos. Can be overridden via EmbeddingExtractor parameter.
Requires TensorFlow 2.15.0 for full compatibility with DeepFace 0.0.95."""

DEFAULT_CONFIDENCE_THRESHOLD = 0.45
"""Default minimum confidence score required for face recognition (0.0 to 1.0)."""

DEFAULT_LIVENESS_THRESHOLD = 0.2
"""Default minimum liveness score (EAR threshold) required for verification (0.0 to 1.0)."""

MIN_FACE_QUALITY_SCORE = 0.5
"""Minimum face quality score required for attendance (0.0 to 1.0)."""






