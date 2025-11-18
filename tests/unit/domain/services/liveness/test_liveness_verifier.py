"""
Unit tests for LivenessVerifier.

This module tests LivenessVerifier in isolation with mocked BlinkDetector.
All tests are unit tests only - no integration tests.
"""

from typing import List, Tuple
from unittest.mock import Mock, MagicMock

import numpy as np
import pytest

from core.liveness.blink_detector import BlinkDetector
from core.liveness.value_objects import BlinkResult
from domain.services.liveness.liveness_verifier import LivenessVerifier


class TestLivenessVerifier:
    """Test suite for LivenessVerifier class."""

    def test_verify_with_three_blinks_returns_true(self) -> None:
        """Test verification returns True when blink count >= 3."""
        # Create mock BlinkDetector
        mock_detector = Mock(spec=BlinkDetector)
        mock_detector.get_blink_count.return_value = 3
        
        verifier = LivenessVerifier(mock_detector, min_blinks=3)
        
        # Create mock frames and landmarks
        frames = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(10)]
        landmarks = [[(0.0, 0.0)] * 468 for _ in range(10)]
        
        # Mock detect to return BlinkResult
        mock_detector.detect.return_value = BlinkResult(
            is_blinking=False,
            ear_value=0.25,
            left_ear=0.25,
            right_ear=0.25,
            blink_count=3
        )
        
        result = verifier.verify(frames, landmarks)
        
        assert result is True
        mock_detector.reset_counter.assert_called_once()
        assert mock_detector.detect.call_count == len(landmarks)

    def test_verify_with_four_blinks_returns_true(self) -> None:
        """Test verification returns True when blink count > min_blinks."""
        mock_detector = Mock(spec=BlinkDetector)
        mock_detector.get_blink_count.return_value = 4
        
        verifier = LivenessVerifier(mock_detector, min_blinks=3)
        
        frames = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(10)]
        landmarks = [[(0.0, 0.0)] * 468 for _ in range(10)]
        
        mock_detector.detect.return_value = BlinkResult(
            is_blinking=False,
            ear_value=0.25,
            left_ear=0.25,
            right_ear=0.25,
            blink_count=4
        )
        
        result = verifier.verify(frames, landmarks)
        
        assert result is True

    def test_verify_with_two_blinks_returns_false(self) -> None:
        """Test verification returns False when blink count < 3."""
        mock_detector = Mock(spec=BlinkDetector)
        mock_detector.get_blink_count.return_value = 2
        
        verifier = LivenessVerifier(mock_detector, min_blinks=3)
        
        frames = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(10)]
        landmarks = [[(0.0, 0.0)] * 468 for _ in range(10)]
        
        mock_detector.detect.return_value = BlinkResult(
            is_blinking=False,
            ear_value=0.25,
            left_ear=0.25,
            right_ear=0.25,
            blink_count=2
        )
        
        result = verifier.verify(frames, landmarks)
        
        assert result is False
        mock_detector.reset_counter.assert_called_once()

    def test_verify_with_zero_blinks_returns_false(self) -> None:
        """Test verification returns False when blink count is 0."""
        mock_detector = Mock(spec=BlinkDetector)
        mock_detector.get_blink_count.return_value = 0
        
        verifier = LivenessVerifier(mock_detector, min_blinks=3)
        
        frames = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(10)]
        landmarks = [[(0.0, 0.0)] * 468 for _ in range(10)]
        
        mock_detector.detect.return_value = BlinkResult(
            is_blinking=False,
            ear_value=0.25,
            left_ear=0.25,
            right_ear=0.25,
            blink_count=0
        )
        
        result = verifier.verify(frames, landmarks)
        
        assert result is False

    def test_verify_with_one_blink_returns_false(self) -> None:
        """Test verification returns False when blink count is 1."""
        mock_detector = Mock(spec=BlinkDetector)
        mock_detector.get_blink_count.return_value = 1
        
        verifier = LivenessVerifier(mock_detector, min_blinks=3)
        
        frames = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(10)]
        landmarks = [[(0.0, 0.0)] * 468 for _ in range(10)]
        
        mock_detector.detect.return_value = BlinkResult(
            is_blinking=False,
            ear_value=0.25,
            left_ear=0.25,
            right_ear=0.25,
            blink_count=1
        )
        
        result = verifier.verify(frames, landmarks)
        
        assert result is False

    def test_verify_resets_detector_counter(self) -> None:
        """Test verify resets blink detector counter before processing."""
        mock_detector = Mock(spec=BlinkDetector)
        mock_detector.get_blink_count.return_value = 3
        
        verifier = LivenessVerifier(mock_detector, min_blinks=3)
        
        frames = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(5)]
        landmarks = [[(0.0, 0.0)] * 468 for _ in range(5)]
        
        mock_detector.detect.return_value = BlinkResult(
            is_blinking=False,
            ear_value=0.25,
            left_ear=0.25,
            right_ear=0.25,
            blink_count=3
        )
        
        verifier.verify(frames, landmarks)
        
        # Verify reset_counter was called before detect
        assert mock_detector.reset_counter.called
        # Verify detect was called for each landmark
        assert mock_detector.detect.call_count == len(landmarks)

    def test_verify_processes_all_landmarks(self) -> None:
        """Test verify processes all landmark sequences."""
        mock_detector = Mock(spec=BlinkDetector)
        mock_detector.get_blink_count.return_value = 3
        
        verifier = LivenessVerifier(mock_detector, min_blinks=3)
        
        frames = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(5)]
        landmarks = [[(0.0, 0.0)] * 468 for _ in range(5)]
        
        mock_detector.detect.return_value = BlinkResult(
            is_blinking=False,
            ear_value=0.25,
            left_ear=0.25,
            right_ear=0.25,
            blink_count=3
        )
        
        verifier.verify(frames, landmarks)
        
        assert mock_detector.detect.call_count == 5

    def test_verify_with_empty_frames_returns_false(self) -> None:
        """Test verify returns False when frames list is empty."""
        mock_detector = Mock(spec=BlinkDetector)
        
        verifier = LivenessVerifier(mock_detector, min_blinks=3)
        
        frames: List[np.ndarray] = []
        landmarks: List[List[Tuple[float, float]]] = []
        
        result = verifier.verify(frames, landmarks)
        
        assert result is False
        # Should not call reset_counter or detect on empty input
        mock_detector.reset_counter.assert_not_called()
        mock_detector.detect.assert_not_called()

    def test_verify_with_empty_landmarks_returns_false(self) -> None:
        """Test verify returns False when landmarks list is empty."""
        mock_detector = Mock(spec=BlinkDetector)
        
        verifier = LivenessVerifier(mock_detector, min_blinks=3)
        
        frames = [np.zeros((100, 100, 3), dtype=np.uint8)]
        landmarks: List[List[Tuple[float, float]]] = []
        
        result = verifier.verify(frames, landmarks)
        
        assert result is False

    def test_verify_with_mismatched_lengths_raises_error(self) -> None:
        """Test verify raises ValueError when frames and landmarks have different lengths."""
        mock_detector = Mock(spec=BlinkDetector)
        
        verifier = LivenessVerifier(mock_detector, min_blinks=3)
        
        frames = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(5)]
        landmarks = [[(0.0, 0.0)] * 468 for _ in range(3)]  # Different length
        
        with pytest.raises(ValueError, match="Frames and landmarks lists must have the same length"):
            verifier.verify(frames, landmarks)

    def test_verify_skips_invalid_landmarks(self) -> None:
        """Test verify skips invalid landmarks that raise ValueError."""
        mock_detector = Mock(spec=BlinkDetector)
        mock_detector.get_blink_count.return_value = 3
        
        verifier = LivenessVerifier(mock_detector, min_blinks=3)
        
        frames = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(3)]
        landmarks = [
            [(0.0, 0.0)] * 468,  # Valid
            [(0.0, 0.0)] * 100,  # Invalid (too short)
            [(0.0, 0.0)] * 468,  # Valid
        ]
        
        # First and third calls succeed, second raises ValueError
        def side_effect(landmark_seq: List[Tuple[float, float]]) -> BlinkResult:
            if len(landmark_seq) < 468:
                raise ValueError("Invalid landmarks")
            return BlinkResult(
                is_blinking=False,
                ear_value=0.25,
                left_ear=0.25,
                right_ear=0.25,
                blink_count=3
            )
        
        mock_detector.detect.side_effect = side_effect
        
        result = verifier.verify(frames, landmarks)
        
        # Should still return True if final count is >= min_blinks
        assert result is True
        # Should have called detect 3 times (one raises error but is caught)
        assert mock_detector.detect.call_count == 3

    def test_verify_with_custom_min_blinks(self) -> None:
        """Test verify works with custom min_blinks threshold."""
        mock_detector = Mock(spec=BlinkDetector)
        mock_detector.get_blink_count.return_value = 5
        
        verifier = LivenessVerifier(mock_detector, min_blinks=5)
        
        frames = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(10)]
        landmarks = [[(0.0, 0.0)] * 468 for _ in range(10)]
        
        mock_detector.detect.return_value = BlinkResult(
            is_blinking=False,
            ear_value=0.25,
            left_ear=0.25,
            right_ear=0.25,
            blink_count=5
        )
        
        result = verifier.verify(frames, landmarks)
        
        assert result is True

    def test_verify_with_custom_min_blinks_returns_false(self) -> None:
        """Test verify returns False when blink count < custom min_blinks."""
        mock_detector = Mock(spec=BlinkDetector)
        mock_detector.get_blink_count.return_value = 4
        
        verifier = LivenessVerifier(mock_detector, min_blinks=5)
        
        frames = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(10)]
        landmarks = [[(0.0, 0.0)] * 468 for _ in range(10)]
        
        mock_detector.detect.return_value = BlinkResult(
            is_blinking=False,
            ear_value=0.25,
            left_ear=0.25,
            right_ear=0.25,
            blink_count=4
        )
        
        result = verifier.verify(frames, landmarks)
        
        assert result is False

    def test_init_with_invalid_min_blinks_raises_error(self) -> None:
        """Test LivenessVerifier raises ValueError when min_blinks < 1."""
        mock_detector = Mock(spec=BlinkDetector)
        
        with pytest.raises(ValueError, match="min_blinks must be at least 1"):
            LivenessVerifier(mock_detector, min_blinks=0)
        
        with pytest.raises(ValueError, match="min_blinks must be at least 1"):
            LivenessVerifier(mock_detector, min_blinks=-1)

    def test_init_with_valid_min_blinks(self) -> None:
        """Test LivenessVerifier initializes correctly with valid min_blinks."""
        mock_detector = Mock(spec=BlinkDetector)
        
        verifier = LivenessVerifier(mock_detector, min_blinks=1)
        assert verifier.min_blinks == 1
        assert verifier.blink_detector == mock_detector
        
        verifier = LivenessVerifier(mock_detector, min_blinks=5)
        assert verifier.min_blinks == 5

    def test_init_with_default_min_blinks(self) -> None:
        """Test LivenessVerifier uses default min_blinks of 3."""
        mock_detector = Mock(spec=BlinkDetector)
        
        verifier = LivenessVerifier(mock_detector)
        assert verifier.min_blinks == 3

