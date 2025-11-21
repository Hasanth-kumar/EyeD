"""
Liveness Verifier - Domain Service for liveness verification.

This service verifies liveness by checking if the blink count meets the minimum threshold.
It uses BlinkDetector to count blinks across a sequence of frames and landmarks.
"""

from typing import List, Tuple

import numpy as np

from core.liveness.blink_detector import BlinkDetector


class LivenessVerifier:
    """
    Verifies liveness by checking if blink count >= minimum threshold.
    
    This service is responsible ONLY for:
    - Processing frames and landmarks sequences
    - Using BlinkDetector to count blinks
    - Verifying if blink count meets minimum threshold (default: 3)
    
    It does NOT handle:
    - Motion analysis
    - Spoofing detection
    - Landmark extraction (landmarks must be provided)
    """
    
    def __init__(self, blink_detector: BlinkDetector, min_blinks: int = 3) -> None:
        """
        Initialize the liveness verifier.
        
        Args:
            blink_detector: BlinkDetector instance for counting blinks.
            min_blinks: Minimum number of blinks required for liveness verification.
                       Default is 3.
        
        Raises:
            ValueError: If min_blinks is less than 1.
        """
        if min_blinks < 1:
            raise ValueError(
                f"min_blinks must be at least 1, got {min_blinks}"
            )
        
        self.blink_detector = blink_detector
        self.min_blinks = min_blinks
    
    def verify(
        self,
        frames: List[np.ndarray],
        landmarks: List[List[Tuple[float, float]]]
    ) -> bool:
        """
        Verify liveness by checking if blink count >= minimum threshold.
        
        This method:
        1. Resets the blink detector counter
        2. Processes each frame/landmark pair to count blinks
        3. Returns True if blink_count >= min_blinks, False otherwise
        
        Args:
            frames: List of frame images (numpy arrays).
                   Note: Frames are not directly used but must match landmarks length.
            landmarks: List of landmark sequences, where each element is a list of
                      (x, y) tuples representing facial landmarks for one frame.
        
        Returns:
            True if blink_count >= min_blinks, False otherwise.
        
        Raises:
            ValueError: If frames and landmarks lists have different lengths or are empty.
        """
        if not frames or not landmarks:
            return False
        
        if len(frames) != len(landmarks):
            raise ValueError(
                f"Frames and landmarks lists must have the same length. "
                f"Got {len(frames)} frames and {len(landmarks)} landmark sequences."
            )
        
        # Reset blink detector to start fresh counting
        self.blink_detector.reset_counter()
        
        # Process each frame/landmark pair to count blinks
        for landmark_sequence in landmarks:
            try:
                # BlinkDetector.detect() will increment the counter internally
                # when it detects blink transitions
                self.blink_detector.detect(landmark_sequence)
            except ValueError:
                # Skip invalid landmarks (BlinkDetector will raise ValueError
                # for invalid landmarks)
                continue
        
        # Check if blink count meets minimum threshold
        blink_count = self.blink_detector.get_blink_count()
        return blink_count >= self.min_blinks



