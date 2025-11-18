"""
Liveness Service - Composite Domain Service for liveness verification workflow.

This service coordinates landmark extraction and liveness verification.
It orchestrates the complete liveness verification workflow by:
1. Extracting landmarks from frames using LandmarkExtractor
2. Verifying liveness using LivenessVerifier
3. Raising appropriate exceptions on failure
"""

from typing import List, Optional, Tuple

import numpy as np

from core.liveness.landmark_extractor import LandmarkExtractor
from domain.services.liveness.liveness_verifier import LivenessVerifier
from domain.shared.exceptions import LivenessVerificationFailedError


class LivenessService:
    """
    Coordinates liveness verification workflow.
    
    This service is responsible ONLY for:
    - Extracting landmarks from frames using LandmarkExtractor
    - Calling LivenessVerifier.verify() with frames and landmarks
    - Returning boolean result
    - Raising LivenessVerificationFailedError if verification fails
    
    It does NOT handle:
    - Blink detection (delegated to LivenessVerifier)
    - Landmark extraction logic (delegated to LandmarkExtractor)
    - Motion analysis
    - Spoofing detection
    """
    
    def __init__(
        self,
        landmark_extractor: LandmarkExtractor,
        liveness_verifier: LivenessVerifier
    ) -> None:
        """
        Initialize the liveness service.
        
        Args:
            landmark_extractor: LandmarkExtractor instance for extracting landmarks from frames.
            liveness_verifier: LivenessVerifier instance for verifying liveness.
        
        Raises:
            ValueError: If any dependency is None.
        """
        if landmark_extractor is None:
            raise ValueError("landmark_extractor cannot be None")
        
        if liveness_verifier is None:
            raise ValueError("liveness_verifier cannot be None")
        
        self.landmark_extractor = landmark_extractor
        self.liveness_verifier = liveness_verifier
    
    def verify_liveness(
        self, 
        frames: List[np.ndarray], 
        frontend_blink_count: Optional[int] = None
    ) -> bool:
        """
        Verify liveness by extracting landmarks and checking blink count.
        
        This method:
        1. If frontend_blink_count >= 3: Trust frontend count and do basic validation
           (verify landmarks exist in frames)
        2. Otherwise: Extract landmarks and re-count blinks server-side
        3. Returns True if verification passes, False otherwise
        4. Raises LivenessVerificationFailedError if verification fails
        
        Args:
            frames: List of frame images (numpy arrays) to verify liveness for.
            frontend_blink_count: Optional blink count from frontend. If >= 3, 
                                trust it and skip strict re-counting.
        
        Returns:
            True if liveness verification passes (blink_count >= 3), False otherwise.
        
        Raises:
            ValueError: If frames list is empty or None.
            LivenessVerificationFailedError: If liveness verification fails.
        """
        if not frames:
            raise ValueError("frames cannot be empty or None")
        
        # If frontend reports 3+ blinks, trust it and do basic validation
        if frontend_blink_count is not None and frontend_blink_count >= 3:
            # Extract landmarks to verify they exist (basic validation)
            landmarks_sequence: List[List[Tuple[float, float]]] = []
            
            for frame in frames:
                landmarks = self.landmark_extractor.extract(frame)
                if landmarks is None:
                    landmarks_sequence.append([])
                else:
                    landmarks_sequence.append(landmarks)
            
            # Verify at least some frames have valid landmarks
            valid_landmarks_count = sum(1 for lm in landmarks_sequence if len(lm) > 0)
            if valid_landmarks_count < 1:
                raise LivenessVerificationFailedError(
                    message="Liveness verification failed. Unable to verify liveness and we detected less than 3 blinks."
                )
            
            # Frontend reported 3+ blinks and we have valid landmarks - trust it
            return True
        
        # Otherwise, do full server-side verification (re-count blinks)
        # Extract landmarks from each frame
        landmarks_sequence: List[List[Tuple[float, float]]] = []
        
        for frame in frames:
            landmarks = self.landmark_extractor.extract(frame)
            
            # If landmarks extraction fails for a frame, skip it
            # (LivenessVerifier will handle empty landmarks gracefully)
            if landmarks is None:
                # Use empty list as placeholder to maintain frame-landmark alignment
                landmarks_sequence.append([])
            else:
                landmarks_sequence.append(landmarks)
        
        # Verify liveness using extracted landmarks
        is_verified = self.liveness_verifier.verify(frames, landmarks_sequence)
        
        # Raise exception if verification fails
        if not is_verified:
            raise LivenessVerificationFailedError(
                message="Liveness verification failed. Unable to verify liveness and we detected less than 3 blinks."
            )
        
        return is_verified

