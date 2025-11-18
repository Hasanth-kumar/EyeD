"""
Value objects for liveness detection results.

This module defines the data structures used to represent blink detection results.
These are pure data structures with no business logic or infrastructure dependencies.
"""

from dataclasses import dataclass


@dataclass
class BlinkResult:
    """
    Represents the result of blink detection in a face image.
    
    Attributes:
        is_blinking: Whether a blink was detected in the current frame.
        ear_value: Average Eye Aspect Ratio (EAR) value for both eyes.
        left_ear: Eye Aspect Ratio value for the left eye.
        right_ear: Eye Aspect Ratio value for the right eye.
        blink_count: Total number of blinks detected in the sequence.
    """
    is_blinking: bool
    ear_value: float
    left_ear: float
    right_ear: float
    blink_count: int
    
    def __post_init__(self):
        """Validate that all values are within acceptable ranges."""
        if self.ear_value < 0.0:
            raise ValueError(
                f"ear_value ({self.ear_value}) must be non-negative"
            )
        if self.left_ear < 0.0:
            raise ValueError(
                f"left_ear ({self.left_ear}) must be non-negative"
            )
        if self.right_ear < 0.0:
            raise ValueError(
                f"right_ear ({self.right_ear}) must be non-negative"
            )
        if self.blink_count < 0:
            raise ValueError(
                f"blink_count ({self.blink_count}) must be non-negative"
            )

