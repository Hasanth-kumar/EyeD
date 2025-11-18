"""
Pure face detection logic with no infrastructure dependencies.

This module provides the FaceDetector class which is responsible solely for
detecting faces in images. It supports multiple detection strategies through
dependency injection (MediaPipe, OpenCV).
"""

from typing import List, Optional, Protocol
import numpy as np

from .value_objects import FaceLocation, DetectionResult
from .strategies import (
    MediaPipeDetectionStrategy,
    OpenCVDetectionStrategy,
    MEDIAPIPE_AVAILABLE,
    OPENCV_AVAILABLE
)


class DetectionStrategy(Protocol):
    """Protocol for face detection strategies."""
    
    def detect(self, image: np.ndarray) -> List[tuple[FaceLocation, float]]:
        """
        Detect faces in an image.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of tuples containing (FaceLocation, confidence_score)
        """
        ...


class FaceDetector:
    """
    Pure face detection logic with no infrastructure dependencies.
    
    This class is responsible solely for detecting faces in images. It uses
    dependency injection to support different detection strategies (MediaPipe, OpenCV).
    """
    
    def __init__(self, detection_strategy: Optional[DetectionStrategy] = None):
        """
        Initialize FaceDetector.
        
        Matches old system behavior: OpenCV primary, MediaPipe fallback.
        - Tries OpenCV first
        - If OpenCV finds faces, returns immediately
        - If OpenCV fails or finds no faces, tries MediaPipe as fallback
        
        Args:
            detection_strategy: Detection strategy to use. If None, will attempt to
                               use OpenCV first, with MediaPipe as fallback.
        """
        if detection_strategy is None:
            # Auto-select strategy based on availability
            # Store both primary (OpenCV) and fallback (MediaPipe) strategies
            self.primary_strategy = None  # OpenCV
            self.fallback_strategy = None  # MediaPipe
            
            # Initialize OpenCV as primary (matches old system)
            if OPENCV_AVAILABLE:
                try:
                    self.primary_strategy = OpenCVDetectionStrategy()
                    print(f"[FaceDetector] Initialized OpenCV as primary strategy")
                except Exception as e:
                    print(f"[FaceDetector] OpenCV initialization failed: {e}")
                    self.primary_strategy = None
            
            # Initialize MediaPipe as fallback (matches old system)
            if MEDIAPIPE_AVAILABLE:
                try:
                    self.fallback_strategy = MediaPipeDetectionStrategy()
                    print(f"[FaceDetector] Initialized MediaPipe as fallback strategy")
                except Exception as e:
                    print(f"[FaceDetector] MediaPipe initialization failed: {e}")
                    self.fallback_strategy = None
            
            # Set the active strategy (prefer OpenCV, fallback to MediaPipe)
            if self.primary_strategy is not None:
                self.detection_strategy = self.primary_strategy
            elif self.fallback_strategy is not None:
                self.detection_strategy = self.fallback_strategy
            else:
                raise ImportError(
                    "Neither MediaPipe nor OpenCV is available. "
                    "Install at least one: pip install mediapipe opencv-python"
                )
        else:
            self.detection_strategy = detection_strategy
            self.primary_strategy = None
            self.fallback_strategy = None
    
    def detect(self, image: np.ndarray) -> DetectionResult:
        """
        Detect faces in an image.
        
        Args:
            image: Input image as numpy array
        
        Returns:
            DetectionResult containing face detection information
        """
        # Preprocess image
        processed_image = self._preprocess_image(image)
        
        # Debug: Log detection attempt
        strategy_name = type(self.detection_strategy).__name__
        print(f"[FaceDetector] Using strategy: {strategy_name}")
        print(f"[FaceDetector] Image shape: {processed_image.shape}, dtype: {processed_image.dtype}")
        
        # Detect faces using the strategy with fallback
        # Matches old system: OpenCV first, MediaPipe fallback
        detections = []
        strategy_used = None
        
        # Try OpenCV first (primary strategy, matches old system)
        if self.primary_strategy is not None:
            try:
                detections = self.primary_strategy.detect(processed_image)
                strategy_used = "OpenCVDetectionStrategy"
                print(f"[FaceDetector] OpenCV returned {len(detections)} detections")
                
                # If OpenCV found faces, return immediately (matches old system behavior)
                if len(detections) > 0:
                    print(f"[FaceDetector] OpenCV detected faces, returning immediately")
                else:
                    # OpenCV found no faces, try MediaPipe fallback
                    print(f"[FaceDetector] OpenCV found no faces, trying MediaPipe fallback...")
                    if self.fallback_strategy is not None:
                        try:
                            fallback_detections = self.fallback_strategy.detect(processed_image)
                            if len(fallback_detections) > 0:
                                detections = fallback_detections
                                strategy_used = "MediaPipeDetectionStrategy (fallback)"
                                print(f"[FaceDetector] MediaPipe fallback found {len(detections)} detections")
                            else:
                                print(f"[FaceDetector] MediaPipe fallback also found no faces")
                        except Exception as fallback_error:
                            print(f"[FaceDetector] MediaPipe fallback failed: {fallback_error}")
                            
            except Exception as e:
                print(f"[FaceDetector] OpenCV failed: {e}")
                # Try MediaPipe fallback if OpenCV fails
                if self.fallback_strategy is not None:
                    print(f"[FaceDetector] Falling back to MediaPipe detection...")
                    try:
                        detections = self.fallback_strategy.detect(processed_image)
                        strategy_used = "MediaPipeDetectionStrategy (fallback)"
                        print(f"[FaceDetector] MediaPipe fallback returned {len(detections)} detections")
                    except Exception as fallback_error:
                        print(f"[FaceDetector] MediaPipe fallback also failed: {fallback_error}")
                        import traceback
                        traceback.print_exc()
                        detections = []
                else:
                    import traceback
                    traceback.print_exc()
                    detections = []
        elif self.fallback_strategy is not None:
            # Only MediaPipe available, use it directly
            try:
                detections = self.fallback_strategy.detect(processed_image)
                strategy_used = "MediaPipeDetectionStrategy"
                print(f"[FaceDetector] MediaPipe returned {len(detections)} detections")
            except Exception as e:
                print(f"[FaceDetector] MediaPipe failed: {e}")
                import traceback
                traceback.print_exc()
                detections = []
        
        if not detections:
            print(f"[FaceDetector] No detections found")
            return DetectionResult(
                faces_detected=False,
                face_count=0,
                faces=[],
                confidence_scores=[]
            )
        
        # Extract faces and confidence scores
        faces = [face_location for face_location, _ in detections]
        confidence_scores = [confidence for _, confidence in detections]
        
        print(f"[FaceDetector] Successfully detected {len(faces)} face(s)")
        return DetectionResult(
            faces_detected=True,
            face_count=len(faces),
            faces=faces,
            confidence_scores=confidence_scores
        )
    
    def detect_multiple(self, image: np.ndarray) -> List[DetectionResult]:
        """
        Detect faces in an image, returning a list of DetectionResult objects.
        
        This method is provided for compatibility but currently returns a single
        DetectionResult in a list, as detection already handles multiple faces.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of DetectionResult objects (currently contains one result)
        """
        result = self.detect(image)
        return [result]
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for face detection.
        
        This private helper method ensures the image is in the correct format
        for detection algorithms.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image as numpy array
        """
        if image is None or image.size == 0:
            raise ValueError("Image cannot be None or empty")
        
        # Ensure image is a numpy array
        if not isinstance(image, np.ndarray):
            raise TypeError(f"Image must be a numpy array, got {type(image)}")
        
        # Ensure image has valid dimensions
        if len(image.shape) < 2:
            raise ValueError(f"Image must have at least 2 dimensions, got shape {image.shape}")
        
        # Ensure image has valid data type
        if image.dtype != np.uint8:
            # Convert to uint8 if needed
            if image.dtype == np.float32 or image.dtype == np.float64:
                # Assume normalized [0, 1] range
                if image.max() <= 1.0:
                    image = (image * 255).astype(np.uint8)
                else:
                    image = image.astype(np.uint8)
            else:
                image = image.astype(np.uint8)
        
        return image

