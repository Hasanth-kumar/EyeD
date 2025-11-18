"""
Face detection strategies for different detection algorithms.

This module provides implementations of detection strategies for MediaPipe and OpenCV.
"""

from typing import List
import numpy as np

from .value_objects import FaceLocation

# Try to import MediaPipe for enhanced detection
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
    mp_face_detection = mp.solutions.face_detection
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    mp_face_detection = None

# Try to import OpenCV
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None

__all__ = [
    'MediaPipeDetectionStrategy',
    'OpenCVDetectionStrategy',
    'MEDIAPIPE_AVAILABLE',
    'OPENCV_AVAILABLE'
]


class MediaPipeDetectionStrategy:
    """MediaPipe-based face detection strategy."""
    
    def __init__(self, min_detection_confidence: float = 0.5, model_selection: int = 0):
        """
        Initialize MediaPipe detection strategy.
        
        Args:
            min_detection_confidence: Minimum confidence threshold for detection
            model_selection: 0 for short-range, 1 for full-range detection
        """
        if not MEDIAPIPE_AVAILABLE:
            raise ImportError("MediaPipe is not available. Install it with: pip install mediapipe")
        
        self.detector = mp_face_detection.FaceDetection(
            model_selection=model_selection,
            min_detection_confidence=min_detection_confidence
        )
    
    def detect(self, image: np.ndarray) -> List[tuple[FaceLocation, float]]:
        """
        Detect faces using MediaPipe.
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            List of tuples containing (FaceLocation, confidence_score)
        """
        if not MEDIAPIPE_AVAILABLE:
            return []
        
        try:
            # Convert BGR to RGB for MediaPipe
            if len(image.shape) == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                print(f"[MediaPipe] Converted BGR to RGB, image shape: {rgb_image.shape}")
            else:
                rgb_image = image
                print(f"[MediaPipe] Image is not 3-channel, using as-is")
            
            # Detect faces
            print(f"[MediaPipe] Processing image for face detection...")
            results = self.detector.process(rgb_image)
            
            if not results.detections:
                print(f"[MediaPipe] No detections found")
                return []
            
            print(f"[MediaPipe] Found {len(results.detections)} detection(s)")
            
            detections = []
            h, w = image.shape[:2]
            
            for detection in results.detections:
                # Get bounding box (relative coordinates)
                bbox = detection.location_data.relative_bounding_box
                
                # Convert to absolute coordinates
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                # Ensure coordinates are within image bounds
                x = max(0, min(x, w - 1))
                y = max(0, min(y, h - 1))
                width = max(1, min(width, w - x))
                height = max(1, min(height, h - y))
                
                face_location = FaceLocation(x=x, y=y, width=width, height=height)
                confidence = float(detection.score[0])
                
                detections.append((face_location, confidence))
            
            return detections
            
        except Exception as e:
            # Log exception for debugging
            print(f"[MediaPipe] Exception during detection: {e}")
            import traceback
            traceback.print_exc()
            return []


class OpenCVDetectionStrategy:
    """OpenCV cascade classifier-based face detection strategy."""
    
    def __init__(self, scale_factor: float = 1.1, min_neighbors: int = 5, 
                 min_size: tuple[int, int] = (30, 30)):
        """
        Initialize OpenCV detection strategy.
        
        Args:
            scale_factor: Parameter specifying how much the image size is reduced at each scale
            min_neighbors: Minimum number of neighbors required for detection
            min_size: Minimum face size (width, height)
        """
        if not OPENCV_AVAILABLE:
            raise ImportError("OpenCV is not available. Install it with: pip install opencv-python")
        
        # Load the cascade classifier
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                raise ValueError("Failed to load OpenCV cascade classifier")
        except Exception:
            raise ValueError("OpenCV cascade classifier not available")
        
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        self.min_size = min_size
        self.default_confidence = 0.8  # OpenCV doesn't provide confidence scores
    
    def detect(self, image: np.ndarray) -> List[tuple[FaceLocation, float]]:
        """
        Detect faces using OpenCV cascade classifier.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of tuples containing (FaceLocation, confidence_score)
        """
        if not OPENCV_AVAILABLE or self.face_cascade is None:
            return []
        
        try:
            # Convert to grayscale for cascade detection
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                print(f"[OpenCV] Converted to grayscale, shape: {gray.shape}")
            else:
                gray = image
                print(f"[OpenCV] Image is already grayscale")
            
            # Detect faces
            print(f"[OpenCV] Processing image for face detection...")
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=self.scale_factor,
                minNeighbors=self.min_neighbors,
                minSize=self.min_size
            )
            
            print(f"[OpenCV] Found {len(faces)} face(s)")
            if len(faces) == 0:
                return []
            
            detections = []
            for (x, y, w, h) in faces:
                face_location = FaceLocation(x=int(x), y=int(y), width=int(w), height=int(h))
                detections.append((face_location, self.default_confidence))
            
            return detections
            
        except Exception as e:
            # Log exception for debugging
            print(f"[OpenCV] Exception during detection: {e}")
            import traceback
            traceback.print_exc()
            return []

