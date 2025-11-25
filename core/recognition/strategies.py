"""
Face detection strategies for different detection algorithms.

This module provides implementations of detection strategies for MediaPipe, OpenCV, and YOLO.
"""

from typing import List
import logging
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

# Try to import Ultralytics YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    YOLO = None

__all__ = [
    'MediaPipeDetectionStrategy',
    'OpenCVDetectionStrategy',
    'YOLODetectionStrategy',
    'MEDIAPIPE_AVAILABLE',
    'OPENCV_AVAILABLE',
    'YOLO_AVAILABLE'
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


class YOLODetectionStrategy:
    """YOLO-based face detection strategy using Ultralytics YOLO."""
    
    def __init__(self, model_path: str = "yolov8n.pt", conf_threshold: float = 0.25):
        """
        Initialize YOLO detection strategy.
        
        Args:
            model_path: Path to YOLO model file. Tries face-specific models first,
                       falls back to general YOLO model if face models unavailable.
            conf_threshold: Confidence threshold for detection (default: 0.25)
        """
        if not YOLO_AVAILABLE:
            raise ImportError("YOLO is not available. Install it with: pip install ultralytics")
        
        self.conf_threshold = conf_threshold
        self.logger = logging.getLogger(__name__)
        
        # If default model path, try face-specific models first, then fallback
        if model_path == "yolov8n.pt":
            # Try face-specific models first, then fallback to general YOLO
            face_models = ["yolov8n-face.pt", "yolov11n-face.pt", "yolov8n.pt"]
            model_loaded = False
            for model_name in face_models:
                try:
                    self.model = YOLO(model_name)
                    self.logger.info(f"YOLO model loaded: {model_name}")
                    model_loaded = True
                    break
                except Exception as e:
                    self.logger.debug(f"Failed to load {model_name}: {e}")
                    continue
            
            if not model_loaded:
                raise ValueError("Failed to load any YOLO model. Please check your installation.")
        else:
            # Use the specified model path directly
            try:
                self.model = YOLO(model_path)
                self.logger.info(f"YOLO model loaded from {model_path}")
            except Exception as e:
                self.logger.error(f"Failed to load YOLO model from {model_path}: {e}")
                raise ValueError(f"Failed to load YOLO model from {model_path}: {e}")
    
    def detect(self, image: np.ndarray) -> List[tuple[FaceLocation, float]]:
        """
        Detect faces using YOLO.
        
        Args:
            image: Input image as numpy array (BGR or RGB format)
            
        Returns:
            List of tuples containing (FaceLocation, confidence_score)
        """
        if not YOLO_AVAILABLE:
            return []
        
        try:
            # Validate image input
            if not isinstance(image, np.ndarray):
                self.logger.warning("Invalid image: not a numpy array")
                return []
            
            if image.size == 0:
                self.logger.warning("Invalid image: empty array")
                return []
            
            if len(image.shape) < 2:
                self.logger.warning(f"Invalid image: insufficient dimensions (shape: {image.shape})")
                return []
            
            # Get image dimensions for validation
            h, w = image.shape[:2]
            if h <= 0 or w <= 0:
                self.logger.warning(f"Invalid image: invalid dimensions (h={h}, w={w})")
                return []
            
            # Convert BGR to RGB if needed (YOLO expects RGB)
            if len(image.shape) == 3:
                # Check if image is BGR (OpenCV format) or RGB
                # YOLO can handle both, but RGB is preferred
                rgb_image = image.copy()
                # If image came from OpenCV, it's likely BGR
                if cv2 is not None:
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    self.logger.debug("Converted BGR to RGB for YOLO")
            else:
                rgb_image = image
                self.logger.debug("Image is not 3-channel, using as-is")
            
            # Run YOLO prediction
            self.logger.debug("Processing image for face detection with YOLO...")
            results = self.model.predict(
                rgb_image,
                conf=self.conf_threshold,
                verbose=False
            )
            
            if not results or len(results) == 0:
                self.logger.debug("YOLO returned no results")
                return []
            
            # Extract detections from first result (YOLO returns list of results)
            result = results[0]
            
            if result.boxes is None or len(result.boxes) == 0:
                self.logger.debug("YOLO found no detections")
                return []
            
            self.logger.debug(f"YOLO found {len(result.boxes)} detection(s)")
            
            detections = []
            # Image dimensions (h, w) already extracted and validated above
            
            # Check if we're using a face-specific model by checking the model path
            # Face-specific models only detect faces, so no class filtering needed
            is_face_model = False
            try:
                model_path_str = str(self.model.ckpt_path).lower()
                is_face_model = 'face' in model_path_str
            except (AttributeError, Exception):
                # If we can't determine, assume it's a general model
                is_face_model = False
            
            for box in result.boxes:
                # Get bounding box coordinates (YOLO returns xyxy format: x1, y1, x2, y2)
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                # Extract and validate confidence score (ensure it's between 0.0 and 1.0)
                confidence = float(box.conf[0].cpu().numpy())
                confidence = max(0.0, min(1.0, confidence))  # Clamp to [0.0, 1.0]
                
                # Get class ID (0 is typically person class in general YOLO models)
                # For face-specific models, all detections are faces
                class_id = int(box.cls[0].cpu().numpy())
                
                # Filter for person/face class (class 0) if using general YOLO model
                # Face-specific models don't need filtering as they only detect faces
                if not is_face_model and class_id != 0:
                    # Skip non-person detections in general YOLO models
                    continue
                
                # Convert from xyxy to (x, y, width, height) format
                x = int(x1)
                y = int(y1)
                width = int(x2 - x1)
                height = int(y2 - y1)
                
                # Ensure coordinates are within image bounds
                x = max(0, min(x, w - 1))
                y = max(0, min(y, h - 1))
                width = max(1, min(width, w - x))
                height = max(1, min(height, h - y))
                
                face_location = FaceLocation(x=x, y=y, width=width, height=height)
                detections.append((face_location, confidence))
            
            return detections
            
        except Exception as e:
            # Log exception for debugging
            self.logger.error(f"Exception during YOLO detection: {e}", exc_info=True)
            return []

