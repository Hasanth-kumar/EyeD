"""
Unit tests for BlinkDetector.

This module tests BlinkDetector in isolation with mocked landmarks data.
All tests are unit tests only - no integration tests.
"""

from typing import List, Tuple
from unittest.mock import Mock, patch

import pytest

from core.liveness.blink_detector import BlinkDetector
from core.liveness.value_objects import BlinkResult


class TestBlinkDetector:
    """Test suite for BlinkDetector class."""

    def test_calculate_ear_with_valid_landmarks(self) -> None:
        """Test EAR calculation with valid landmarks."""
        detector = BlinkDetector(ear_threshold=0.2)
        
        # Create mock landmarks with 468 points (MediaPipe standard)
        # For EAR calculation, we need specific eye landmark points
        landmarks = [(0.0, 0.0)] * 468
        
        # Set up realistic eye landmark coordinates for left eye
        # Left eye indices: [362, 385, 387, 263, 373, 380]
        # Format: [outer_corner, top_outer, top_inner, inner_corner, bottom_inner, bottom_outer]
        landmarks[362] = (0.3, 0.5)  # outer_corner
        landmarks[385] = (0.35, 0.45)  # top_outer
        landmarks[387] = (0.45, 0.45)  # top_inner
        landmarks[263] = (0.5, 0.5)  # inner_corner
        landmarks[373] = (0.45, 0.55)  # bottom_inner
        landmarks[380] = (0.35, 0.55)  # bottom_outer
        
        # Calculate EAR for left eye
        left_ear = detector._calculate_ear(landmarks, BlinkDetector.LEFT_EYE_INDICES)
        
        # EAR should be a positive value
        assert left_ear > 0.0
        assert isinstance(left_ear, float)

    def test_calculate_ear_with_invalid_landmarks(self) -> None:
        """Test EAR calculation returns 0.0 for invalid landmarks."""
        detector = BlinkDetector(ear_threshold=0.2)
        
        # Test with insufficient landmarks
        short_landmarks = [(0.0, 0.0)] * 100
        ear = detector._calculate_ear(short_landmarks, BlinkDetector.LEFT_EYE_INDICES)
        assert ear == 0.0
        
        # Test with empty landmarks
        empty_landmarks: List[Tuple[float, float]] = []
        ear = detector._calculate_ear(empty_landmarks, BlinkDetector.LEFT_EYE_INDICES)
        assert ear == 0.0

    def test_calculate_ear_with_zero_horizontal_distance(self) -> None:
        """Test EAR calculation when horizontal distance is zero."""
        detector = BlinkDetector(ear_threshold=0.2)
        
        # Create landmarks where outer and inner corners are at same x position
        landmarks = [(0.0, 0.0)] * 468
        landmarks[362] = (0.5, 0.5)  # outer_corner
        landmarks[263] = (0.5, 0.5)  # inner_corner (same x as outer)
        landmarks[385] = (0.5, 0.45)  # top_outer
        landmarks[387] = (0.5, 0.45)  # top_inner
        landmarks[373] = (0.5, 0.55)  # bottom_inner
        landmarks[380] = (0.5, 0.55)  # bottom_outer
        
        ear = detector._calculate_ear(landmarks, BlinkDetector.LEFT_EYE_INDICES)
        assert ear == 0.0

    def test_detect_with_valid_landmarks_eyes_open(self) -> None:
        """Test blink detection with valid landmarks and eyes open."""
        detector = BlinkDetector(ear_threshold=0.2)
        
        # Create landmarks with eyes open (high EAR)
        landmarks = self._create_open_eyes_landmarks()
        
        result = detector.detect(landmarks)
        
        assert isinstance(result, BlinkResult)
        assert result.is_blinking is False
        assert result.ear_value > detector.ear_threshold
        assert result.left_ear > 0.0
        assert result.right_ear > 0.0
        assert result.blink_count == 0

    def test_detect_with_valid_landmarks_eyes_closed(self) -> None:
        """Test blink detection with valid landmarks and eyes closed."""
        detector = BlinkDetector(ear_threshold=0.2)
        
        # Create landmarks with eyes closed (low EAR)
        landmarks = self._create_closed_eyes_landmarks()
        
        result = detector.detect(landmarks)
        
        assert isinstance(result, BlinkResult)
        assert result.is_blinking is True
        assert result.ear_value < detector.ear_threshold
        assert result.blink_count == 0  # No blink transition yet

    def test_detect_blink_transition_open_to_closed_to_open(self) -> None:
        """Test blink detection counts blinks on open->closed->open transition."""
        detector = BlinkDetector(ear_threshold=0.2)
        
        # Frame 1: Eyes open
        open_landmarks = self._create_open_eyes_landmarks()
        result1 = detector.detect(open_landmarks)
        assert result1.is_blinking is False
        assert result1.blink_count == 0
        
        # Frame 2: Eyes closed (transition from open to closed)
        closed_landmarks = self._create_closed_eyes_landmarks()
        result2 = detector.detect(closed_landmarks)
        assert result2.is_blinking is True
        assert result2.blink_count == 0  # Not counted yet
        
        # Frame 3: Eyes open again (transition from closed to open - blink detected!)
        result3 = detector.detect(open_landmarks)
        assert result3.is_blinking is False
        assert result3.blink_count == 1  # Blink counted!

    def test_detect_multiple_blinks(self) -> None:
        """Test blink detection counts multiple blinks correctly."""
        detector = BlinkDetector(ear_threshold=0.2)
        
        open_landmarks = self._create_open_eyes_landmarks()
        closed_landmarks = self._create_closed_eyes_landmarks()
        
        # First blink
        detector.detect(open_landmarks)  # Open
        detector.detect(closed_landmarks)  # Closed
        result1 = detector.detect(open_landmarks)  # Open - blink 1
        assert result1.blink_count == 1
        
        # Second blink
        detector.detect(closed_landmarks)  # Closed
        result2 = detector.detect(open_landmarks)  # Open - blink 2
        assert result2.blink_count == 2
        
        # Third blink
        detector.detect(closed_landmarks)  # Closed
        result3 = detector.detect(open_landmarks)  # Open - blink 3
        assert result3.blink_count == 3

    def test_detect_with_invalid_landmarks_raises_error(self) -> None:
        """Test detect raises ValueError with invalid landmarks."""
        detector = BlinkDetector(ear_threshold=0.2)
        
        # Test with insufficient landmarks
        short_landmarks = [(0.0, 0.0)] * 100
        with pytest.raises(ValueError, match="Invalid landmarks"):
            detector.detect(short_landmarks)
        
        # Test with empty landmarks
        empty_landmarks: List[Tuple[float, float]] = []
        with pytest.raises(ValueError, match="Invalid landmarks"):
            detector.detect(empty_landmarks)
        
        # Test with None
        with pytest.raises(ValueError, match="Invalid landmarks"):
            detector.detect(None)  # type: ignore

    def test_reset_counter(self) -> None:
        """Test counter reset functionality."""
        detector = BlinkDetector(ear_threshold=0.2)
        
        open_landmarks = self._create_open_eyes_landmarks()
        closed_landmarks = self._create_closed_eyes_landmarks()
        
        # Count some blinks
        detector.detect(open_landmarks)
        detector.detect(closed_landmarks)
        detector.detect(open_landmarks)  # Blink 1
        
        assert detector.get_blink_count() == 1
        
        # Reset counter
        detector.reset_counter()
        
        assert detector.get_blink_count() == 0
        
        # Verify we can count blinks again after reset
        detector.detect(closed_landmarks)
        result = detector.detect(open_landmarks)  # Blink 1 (after reset)
        assert result.blink_count == 1

    def test_get_blink_count(self) -> None:
        """Test get_blink_count returns current blink count."""
        detector = BlinkDetector(ear_threshold=0.2)
        
        assert detector.get_blink_count() == 0
        
        open_landmarks = self._create_open_eyes_landmarks()
        closed_landmarks = self._create_closed_eyes_landmarks()
        
        detector.detect(open_landmarks)
        detector.detect(closed_landmarks)
        detector.detect(open_landmarks)  # Blink 1
        
        assert detector.get_blink_count() == 1

    def test_custom_ear_threshold(self) -> None:
        """Test BlinkDetector works with custom EAR threshold."""
        detector = BlinkDetector(ear_threshold=0.3)
        
        assert detector.ear_threshold == 0.3
        
        # Create landmarks with EAR between 0.2 and 0.3
        landmarks = self._create_medium_ear_landmarks()
        result = detector.detect(landmarks)
        
        # With threshold 0.3, medium EAR should be considered closed
        assert result.is_blinking is True

    def test_default_ear_threshold(self) -> None:
        """Test BlinkDetector uses default EAR threshold of 0.2."""
        detector = BlinkDetector()
        
        assert detector.ear_threshold == 0.2

    def _create_open_eyes_landmarks(self) -> List[Tuple[float, float]]:
        """Create mock landmarks with eyes open (high EAR)."""
        landmarks = [(0.0, 0.0)] * 468
        
        # Left eye - open (high EAR)
        landmarks[362] = (0.3, 0.5)  # outer_corner
        landmarks[385] = (0.35, 0.45)  # top_outer
        landmarks[387] = (0.45, 0.45)  # top_inner
        landmarks[263] = (0.5, 0.5)  # inner_corner
        landmarks[373] = (0.45, 0.55)  # bottom_inner
        landmarks[380] = (0.35, 0.55)  # bottom_outer
        
        # Right eye - open (high EAR)
        landmarks[33] = (0.5, 0.5)  # outer_corner
        landmarks[160] = (0.55, 0.45)  # top_outer
        landmarks[158] = (0.65, 0.45)  # top_inner
        landmarks[133] = (0.7, 0.5)  # inner_corner
        landmarks[153] = (0.65, 0.55)  # bottom_inner
        landmarks[144] = (0.55, 0.55)  # bottom_outer
        
        return landmarks

    def _create_closed_eyes_landmarks(self) -> List[Tuple[float, float]]:
        """Create mock landmarks with eyes closed (low EAR)."""
        landmarks = [(0.0, 0.0)] * 468
        
        # Left eye - closed (low EAR, all points close together)
        landmarks[362] = (0.4, 0.5)  # outer_corner
        landmarks[385] = (0.4, 0.48)  # top_outer
        landmarks[387] = (0.4, 0.48)  # top_inner
        landmarks[263] = (0.4, 0.5)  # inner_corner
        landmarks[373] = (0.4, 0.52)  # bottom_inner
        landmarks[380] = (0.4, 0.52)  # bottom_outer
        
        # Right eye - closed (low EAR, all points close together)
        landmarks[33] = (0.6, 0.5)  # outer_corner
        landmarks[160] = (0.6, 0.48)  # top_outer
        landmarks[158] = (0.6, 0.48)  # top_inner
        landmarks[133] = (0.6, 0.5)  # inner_corner
        landmarks[153] = (0.6, 0.52)  # bottom_inner
        landmarks[144] = (0.6, 0.52)  # bottom_outer
        
        return landmarks

    def _create_medium_ear_landmarks(self) -> List[Tuple[float, float]]:
        """Create mock landmarks with medium EAR (between 0.2 and 0.3)."""
        landmarks = [(0.0, 0.0)] * 468
        
        # Left eye - medium EAR (~0.25)
        # Horizontal distance C = 0.2 (from 0.3 to 0.5)
        # For EAR = 0.25: (A + B) / (2 * 0.2) = 0.25, so A + B = 0.1
        # Make vertical distances very small
        landmarks[362] = (0.3, 0.5)  # outer_corner
        landmarks[385] = (0.35, 0.495)  # top_outer (very small vertical distance)
        landmarks[387] = (0.4, 0.495)  # top_inner
        landmarks[263] = (0.5, 0.5)  # inner_corner
        landmarks[373] = (0.4, 0.505)  # bottom_inner (very small vertical distance)
        landmarks[380] = (0.35, 0.505)  # bottom_outer
        
        # Right eye - medium EAR (~0.25)
        landmarks[33] = (0.5, 0.5)  # outer_corner
        landmarks[160] = (0.55, 0.495)  # top_outer
        landmarks[158] = (0.6, 0.495)  # top_inner
        landmarks[133] = (0.7, 0.5)  # inner_corner
        landmarks[153] = (0.6, 0.505)  # bottom_inner
        landmarks[144] = (0.55, 0.505)  # bottom_outer
        
        return landmarks

