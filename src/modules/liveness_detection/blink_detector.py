"""
Blink Detection Component

This module handles only blink detection functionality,
following the Single-Responsibility Principle.
"""

import numpy as np
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class BlinkDetector:
    """Detects blinking in face images using Eye Aspect Ratio (EAR)"""
    
    # Eye landmark indices (MediaPipe FaceMesh) - Class constants
    LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380, 381, 382, 381, 374, 386, 387, 388, 466]
    RIGHT_EYE_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
    
    def __init__(self, ear_threshold: float = 0.21, min_consecutive_frames: int = 2):
        """
        Initialize blink detector
        
        Args:
            ear_threshold: Eye Aspect Ratio threshold for blink detection
            min_consecutive_frames: Minimum frames for blink confirmation
        """
        self.ear_threshold = ear_threshold
        self.min_consecutive_frames = min_consecutive_frames
        self.blink_counter = 0
        self.consecutive_frames = 0
        
        logger.info(f"Blink detector initialized with EAR threshold: {ear_threshold}")
    
    def detect_blink(self, landmarks: List) -> Tuple[bool, float]:
        """
        Detect if eyes are closed (blinking)
        
        Args:
            landmarks: Face landmarks from MediaPipe
            
        Returns:
            Tuple of (is_blinking, ear_value)
        """
        try:
            # Calculate EAR for both eyes
            left_ear = self._calculate_ear(landmarks, self.LEFT_EYE_INDICES)
            right_ear = self._calculate_ear(landmarks, self.RIGHT_EYE_INDICES)
            
            # Average EAR value
            ear = (left_ear + right_ear) / 2.0
            
            # Check if eyes are closed
            is_blinking = ear < self.ear_threshold
            
            # Update blink counter
            if is_blinking:
                self.consecutive_frames += 1
                if self.consecutive_frames >= self.min_consecutive_frames:
                    self.blink_counter += 1
                    self.consecutive_frames = 0
            else:
                self.consecutive_frames = 0
            
            return is_blinking, ear
            
        except Exception as e:
            logger.error(f"Error in blink detection: {e}")
            return False, 0.0
    
    def _calculate_ear(self, landmarks: List, eye_indices: List[int]) -> float:
        """
        Calculate Eye Aspect Ratio (EAR)
        
        Args:
            landmarks: Face landmarks
            eye_indices: Indices for eye landmarks
            
        Returns:
            EAR value
        """
        try:
            # Extract eye landmark coordinates
            eye_points = []
            for idx in eye_indices:
                if idx < len(landmarks):
                    x, y = landmarks[idx].x, landmarks[idx].y
                    eye_points.append((x, y))
            
            if len(eye_points) < 6:
                return 0.0
            
            # Calculate vertical distances
            A = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
            B = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
            
            # Calculate horizontal distance
            C = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
            
            # Calculate EAR
            if C > 0:
                ear = (A + B) / (2.0 * C)
                return ear
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculating EAR: {e}")
            return 0.0
    
    def get_blink_count(self) -> int:
        """Get total number of blinks detected"""
        return self.blink_counter
    
    def reset_blink_counter(self) -> None:
        """Reset blink counter"""
        self.blink_counter = 0
        self.consecutive_frames = 0
        logger.debug("Blink counter reset")
    
    def update_ear_threshold(self, new_threshold: float) -> bool:
        """Update EAR threshold for blink detection"""
        if 0.0 < new_threshold < 1.0:
            self.ear_threshold = new_threshold
            logger.info(f"EAR threshold updated to: {new_threshold}")
            return True
        else:
            logger.warning(f"Invalid EAR threshold: {new_threshold}")
            return False
