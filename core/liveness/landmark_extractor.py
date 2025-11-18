"""
Landmark extraction module for EyeD AI Attendance System.

This module provides pure landmark extraction logic using MediaPipe FaceMesh.
It has no infrastructure dependencies and follows Single Responsibility Principle.
"""

from typing import List, Optional, Tuple

import numpy as np

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    mp = None


class LandmarkExtractor:
    """
    Extracts facial landmarks from images using MediaPipe FaceMesh.
    
    This class is responsible ONLY for:
    - Extracting facial landmarks from face images
    - Returning landmarks as list of (x, y) tuples
    - Handling MediaPipe initialization
    
    It does NOT handle:
    - Blink detection
    - Motion analysis
    - Spoofing detection
    - Face detection (assumes face image is already provided)
    """
    
    def __init__(self, min_detection_confidence: float = 0.3) -> None:
        """
        Initialize the landmark extractor.
        
        Args:
            min_detection_confidence: Minimum confidence threshold for face detection.
                                     Default is 0.3 (standard MediaPipe threshold).
        
        Raises:
            ImportError: If MediaPipe is not available.
        """
        if not MEDIAPIPE_AVAILABLE:
            raise ImportError(
                "MediaPipe is not available. Install it with: pip install mediapipe"
            )
        
        self.min_detection_confidence = min_detection_confidence
        self._mp_face_mesh = mp.solutions.face_mesh
    
    def extract(
        self, face_image: np.ndarray
    ) -> Optional[List[Tuple[float, float]]]:
        """
        Extract facial landmarks from a face image.
        
        This method:
        1. Converts image to RGB (MediaPipe expects RGB)
        2. Processes image with MediaPipe FaceMesh
        3. Extracts landmarks and converts to (x, y) tuples
        4. Returns list of landmarks or None if no face detected
        
        Args:
            face_image: Face image as numpy array (BGR format expected, RGB also supported).
                       Shape should be (height, width, 3).
                       If BGR format (OpenCV default), will be converted to RGB.
                       If RGB format, will be converted to BGR (MediaPipe handles both).
        
        Returns:
            List of (x, y) tuples representing facial landmarks.
            Returns None if no face is detected in the image.
            MediaPipe FaceMesh standard is 468 landmarks.
        
        Raises:
            ValueError: If face_image is invalid or empty.
        """
        if face_image is None or face_image.size == 0:
            raise ValueError("face_image cannot be None or empty")
        
        if len(face_image.shape) != 3 or face_image.shape[2] != 3:
            raise ValueError(
                f"face_image must be 3-channel (BGR/RGB), got shape: {face_image.shape}"
            )
        
        try:
            # Convert BGR to RGB (MediaPipe works best with RGB)
            # Assumes BGR input (common from OpenCV)
            rgb_image = self._convert_to_rgb(face_image)
            
            # Create MediaPipe FaceMesh instance
            # Using context manager ensures proper cleanup
            with self._mp_face_mesh.FaceMesh(
                min_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=self.min_detection_confidence,
                max_num_faces=1,
                refine_landmarks=True
            ) as face_mesh:
                # Process image with MediaPipe
                results = face_mesh.process(rgb_image)
                
                # Extract landmarks if face detected
                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0].landmark
                    # Convert MediaPipe landmarks to list of (x, y) tuples
                    return [
                        (landmark.x, landmark.y) for landmark in landmarks
                    ]
                else:
                    return None
                    
        except Exception as e:
            # Return None on any error (allows caller to handle gracefully)
            return None
    
    def _convert_to_rgb(self, image: np.ndarray) -> np.ndarray:
        """
        Convert image to RGB format using numpy.
        
        MediaPipe works best with RGB images. This method converts
        from BGR (OpenCV default) to RGB using numpy array operations.
        This avoids infrastructure dependencies (no OpenCV required).
        
        Note: This method assumes BGR input (common from OpenCV).
        If RGB is provided, it will be converted to BGR, but MediaPipe
        can handle both formats.
        
        Args:
            image: Input image as numpy array (assumed BGR format).
        
        Returns:
            RGB image as numpy array (or BGR if input was RGB).
        """
        # Convert BGR to RGB by swapping channels using numpy (no OpenCV needed)
        # BGR: [B, G, R] -> RGB: [R, G, B]
        # Reverse the channel order: [:, :, ::-1]
        rgb_image = image[:, :, ::-1]
        return rgb_image

