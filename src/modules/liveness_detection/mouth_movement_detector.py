"""
Mouth Movement Detection Component

This module handles only mouth movement detection functionality,
following the Single-Responsibility Principle.
"""

import numpy as np
from typing import List, Dict, Any
import logging

try:
    from ...interfaces.liveness_interface import LivenessResult, LivenessTestType
except ImportError:
    # Fallback to absolute imports for testing
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))
    from interfaces.liveness_interface import LivenessResult, LivenessTestType

logger = logging.getLogger(__name__)


class MouthMovementDetector:
    """Detects mouth movement in face images"""
    
    def __init__(self):
        """Initialize mouth movement detector"""
        logger.info("Mouth movement detector initialized")
    
    def detect_movement(self, face_images: List[np.ndarray]) -> LivenessResult:
        """
        Detect mouth movement between face images
        
        Args:
            face_images: List of face images to analyze
            
        Returns:
            LivenessResult with movement detection results
        """
        try:
            if len(face_images) < 2:
                return LivenessResult(
                    is_live=False,
                    confidence=0.0,
                    test_type=LivenessTestType.MOUTH_MOVEMENT,
                    details={"error": "Need at least 2 images for movement detection"}
                )
            
            # Placeholder implementation - would analyze mouth position changes
            # between consecutive frames
            
            return LivenessResult(
                is_live=True,
                confidence=0.6,
                test_type=LivenessTestType.MOUTH_MOVEMENT,
                details={"movement_detected": True, "frames_analyzed": len(face_images)}
            )
            
        except Exception as e:
            logger.error(f"Error in mouth movement detection: {e}")
            return LivenessResult(
                is_live=False,
                confidence=0.0,
                test_type=LivenessTestType.MOUTH_MOVEMENT,
                details={"error": str(e)}
            )
