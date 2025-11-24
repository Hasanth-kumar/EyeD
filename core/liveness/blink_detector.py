"""
Blink detection module for EyeD AI Attendance System.

This module provides pure blink detection logic using Eye Aspect Ratio (EAR) calculation.
It has no infrastructure dependencies and follows Single Responsibility Principle.
"""

from typing import List, Tuple

from .value_objects import BlinkResult


class BlinkDetector:
    """
    Detects blinks using Eye Aspect Ratio (EAR) calculation.
    
    This class is responsible ONLY for:
    - Calculating EAR for left and right eyes
    - Detecting when eyes are closed (EAR < threshold)
    - Counting blinks (incrementing counter when blink detected)
    - Resetting the blink counter
    
    It does NOT handle:
    - Motion analysis
    - Spoofing detection
    - Landmark extraction (landmarks must be provided)
    """
    
    # MediaPipe FaceMesh eye landmark indices for EAR calculation
    # These are the 6 key points needed for EAR: outer corner, inner corner, top, bottom
    LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
    """Left eye landmark indices: [outer_corner, top_outer, top_inner, inner_corner, bottom_inner, bottom_outer]"""
    
    RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
    """Right eye landmark indices: [outer_corner, top_outer, top_inner, inner_corner, bottom_inner, bottom_outer]"""
    
    def __init__(self, ear_threshold: float = 0.2) -> None:
        """
        Initialize the blink detector.
        
        Args:
            ear_threshold: Threshold below which eyes are considered closed.
                          Default is 0.2 (standard EAR threshold for blink detection).
        """
        self.ear_threshold = ear_threshold
        self._blink_count = 0
        self._previous_eyes_closed = False
        """Track previous frame state to detect blink transitions"""
    
    def detect(self, landmarks: List[Tuple[float, float]]) -> BlinkResult:
        """
        Detect blink from facial landmarks.
        
        This method:
        1. Calculates EAR for left and right eyes
        2. Determines if eyes are currently closed
        3. Detects blink transitions (open -> closed -> open)
        4. Increments blink counter when a blink is detected
        
        Args:
            landmarks: List of (x, y) tuples representing facial landmarks.
                      Must contain at least 468 landmarks (MediaPipe FaceMesh standard).
        
        Returns:
            BlinkResult containing:
            - is_blinking: Whether eyes are currently closed
            - ear_value: Average EAR for both eyes
            - left_ear: EAR value for left eye
            - right_ear: EAR value for right eye
            - blink_count: Total number of blinks detected
        
        Raises:
            ValueError: If landmarks list is too short or invalid
        """
        if not landmarks or len(landmarks) < 468:
            raise ValueError(
                f"Invalid landmarks: expected at least 468 points, got {len(landmarks) if landmarks else 0}"
            )
        
        # Calculate EAR for both eyes
        left_ear = self._calculate_ear(landmarks, self.LEFT_EYE_INDICES)
        right_ear = self._calculate_ear(landmarks, self.RIGHT_EYE_INDICES)
        
        # Average EAR for both eyes
        ear_value = (left_ear + right_ear) / 2.0
        
        # Determine if eyes are currently closed
        is_blinking = ear_value < self.ear_threshold
        
        # Detect blink transition: open -> closed -> open
        # A blink is detected when eyes transition from open to closed
        if is_blinking and not self._previous_eyes_closed:
            # Eyes just closed (start of blink)
            pass
        elif not is_blinking and self._previous_eyes_closed:
            # Eyes just opened (end of blink) - increment counter
            self._blink_count += 1
        
        # Update previous state
        self._previous_eyes_closed = is_blinking
        
        return BlinkResult(
            is_blinking=is_blinking,
            ear_value=ear_value,
            left_ear=left_ear,
            right_ear=right_ear,
            blink_count=self._blink_count
        )
    
    def reset_counter(self) -> None:
        """
        Reset the blink counter to zero.
        
        This method resets the internal blink count and state tracking,
        allowing the detector to start counting from a fresh state.
        """
        self._blink_count = 0
        self._previous_eyes_closed = False
    
    def get_blink_count(self) -> int:
        """
        Get the total number of blinks detected.
        
        Returns:
            Total number of blinks detected since initialization or last reset.
        """
        return self._blink_count
    
    def _calculate_ear(
        self,
        landmarks: List[Tuple[float, float]],
        eye_indices: List[int]
    ) -> float:
        """
        Calculate Eye Aspect Ratio (EAR) for a single eye.
        
        EAR formula: (A + B) / (2.0 * C)
        Where:
        - A = vertical distance between points 1 and 5
        - B = vertical distance between points 2 and 4
        - C = horizontal distance between points 0 and 3
        
        Args:
            landmarks: List of (x, y) tuples representing facial landmarks
            eye_indices: List of 6 eye landmark indices for EAR calculation
        
        Returns:
            EAR value (0.0 if calculation fails)
        """
        if len(eye_indices) != 6:
            return 0.0
        
        try:
            # Extract the 6 key eye landmark coordinates
            eye_points = []
            for idx in eye_indices:
                if idx >= len(landmarks):
                    return 0.0
                eye_points.append(landmarks[idx])
            
            if len(eye_points) != 6:
                return 0.0
            
            # Calculate vertical distances (A and B)
            # A = distance between points 1 and 5
            point_1 = eye_points[1]
            point_5 = eye_points[5]
            A = ((point_1[0] - point_5[0]) ** 2 + (point_1[1] - point_5[1]) ** 2) ** 0.5
            
            # B = distance between points 2 and 4
            point_2 = eye_points[2]
            point_4 = eye_points[4]
            B = ((point_2[0] - point_4[0]) ** 2 + (point_2[1] - point_4[1]) ** 2) ** 0.5
            
            # Calculate horizontal distance (C)
            # C = distance between points 0 and 3
            point_0 = eye_points[0]
            point_3 = eye_points[3]
            C = ((point_0[0] - point_3[0]) ** 2 + (point_0[1] - point_3[1]) ** 2) ** 0.5
            
            # Calculate EAR: (A + B) / (2.0 * C)
            if C > 0:
                ear = (A + B) / (2.0 * C)
                return ear
            else:
                return 0.0
                
        except (IndexError, TypeError, ValueError) as e:
            # Return 0.0 on any calculation error
            return 0.0





