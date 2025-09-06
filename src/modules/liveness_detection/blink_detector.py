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
    
    # Correct MediaPipe FaceMesh eye landmark indices for EAR calculation
    # These are the 6 key points needed for EAR calculation
    LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]  # 6 key points for EAR
    RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]  # 6 key points for EAR
    
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
        Calculate Eye Aspect Ratio (EAR) using correct formula
        
        Args:
            landmarks: Face landmarks from MediaPipe
            eye_indices: 6 key eye landmark indices for EAR calculation
            
        Returns:
            EAR value
        """
        try:
            # Extract the 6 key eye landmark coordinates
            eye_points = []
            for idx in eye_indices:
                if idx < len(landmarks):
                    # Handle both landmark objects and direct landmark lists
                    if hasattr(landmarks, 'landmark'):
                        landmark = landmarks.landmark[idx]
                    else:
                        landmark = landmarks[idx]
                    x, y = landmark.x, landmark.y
                    eye_points.append((x, y))
            
            if len(eye_points) < 6:
                return 0.0
            
            # Calculate vertical distances (A and B)
            # A = distance between points 1 and 5
            A = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
            # B = distance between points 2 and 4  
            B = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
            
            # Calculate horizontal distance (C)
            # C = distance between points 0 and 3
            C = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
            
            # Calculate EAR: (A + B) / (2.0 * C)
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
