"""
Face Recognition Module for EyeD AI Attendance System
Day 5 Implementation: Live Video Recognition

This module handles:
- Real-time face detection in video frames
- Live face recognition using DeepFace
- Multi-stage detection pipeline (MediaPipe/OpenCV)
- Performance optimization for video streams
- Confidence scoring and frame processing
"""

import cv2
import numpy as np
from typing import Tuple, Optional, Dict, List, Any
from pathlib import Path
import logging
from deepface import DeepFace
import os
import time # Added for performance tracking

# Import interface
try:
    from ..interfaces.recognition_interface import RecognitionInterface, DetectionResult, RecognitionResult
except ImportError:
    # Fallback to absolute imports for testing
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
    from interfaces.recognition_interface import RecognitionInterface, DetectionResult, RecognitionResult

# Try to import MediaPipe for enhanced detection
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
    mp_face_detection = mp.solutions.face_detection
    mp_drawing = mp.solutions.drawing_utils
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    mp_face_detection = None
    mp_drawing = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceRecognition(RecognitionInterface):
    """Face recognition handler for EyeD AI Attendance System"""
    
    def __init__(self, confidence_threshold: float = 0.6, use_mediapipe: bool = True):
        """
        Initialize Face Recognition system
        
        Args:
            confidence_threshold: Minimum confidence for recognition (0.0 to 1.0)
            use_mediapipe: Whether to use MediaPipe as primary detection method
        """
        self.confidence_threshold = confidence_threshold
        self.use_mediapipe = use_mediapipe and MEDIAPIPE_AVAILABLE
        self.known_faces = {}
        self.known_names = {}
        self.face_cascade = None
        self.mediapipe_detector = None
        
        # Performance tracking
        self.processing_times = []
        self.detection_counts = 0
        self.recognition_counts = 0
        
        self._load_face_cascade()
        self._load_mediapipe_detector()
        
        logger.info(f"Face Recognition initialized with confidence threshold: {confidence_threshold}")
        logger.info(f"MediaPipe detection: {'Enabled' if self.use_mediapipe else 'Disabled'}")
    
    def _load_mediapipe_detector(self):
        """Load MediaPipe face detection model"""
        if self.use_mediapipe and MEDIAPIPE_AVAILABLE:
            try:
                self.mediapipe_detector = mp_face_detection.FaceDetection(
                    model_selection=0,  # 0 for short-range, 1 for full-range
                    min_detection_confidence=0.5
                )
                logger.info("MediaPipe face detection model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load MediaPipe detector: {e}")
                self.mediapipe_detector = None
                self.use_mediapipe = False
        else:
            self.mediapipe_detector = None
    
    def _load_face_cascade(self):
        """Load OpenCV face detection cascade classifier"""
        try:
            # Try to load the cascade classifier
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            if os.path.exists(cascade_path):
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
                logger.info("Face cascade classifier loaded successfully")
            else:
                logger.warning("Face cascade classifier not found, face detection may not work")
                self.face_cascade = None
        except Exception as e:
            logger.error(f"Failed to load face cascade: {e}")
            self.face_cascade = None
    
    def detect_faces(self, image: np.ndarray) -> DetectionResult:
        """
        Detect faces in an image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            DetectionResult containing face locations and confidence scores
        """
        start_time = time.time()
        
        try:
            face_locations = []
            confidence_scores = []
            
            if self.use_mediapipe and self.mediapipe_detector:
                # Use MediaPipe for detection
                results = self._detect_with_mediapipe(image)
                if results:
                    face_locations = results['locations']
                    confidence_scores = results['confidences']
            else:
                # Fallback to OpenCV cascade
                results = self._detect_with_opencv(image)
                if results:
                    face_locations = results['locations']
                    confidence_scores = results['confidences']
            
            # Update performance metrics
            processing_time = (time.time() - start_time) * 1000
            self.processing_times.append(processing_time)
            self.detection_counts += 1
            
            # Keep only last 100 processing times for performance tracking
            if len(self.processing_times) > 100:
                self.processing_times.pop(0)
            
            return DetectionResult(face_locations, confidence_scores)
            
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return DetectionResult([], [])
    
    def recognize_face(self, face_image: np.ndarray, 
                      confidence_threshold: float = 0.6) -> Optional[RecognitionResult]:
        """
        Recognize a face from the database
        
        Args:
            face_image: Face image to recognize
            confidence_threshold: Minimum confidence for recognition
            
        Returns:
            RecognitionResult if face is recognized, None otherwise
        """
        start_time = time.time()
        
        try:
            # Extract embeddings from the face image
            embeddings = self.extract_embeddings(face_image)
            if embeddings is None:
                return None
            
            # Find best match among known faces
            best_match = None
            best_confidence = 0.0
            best_user_id = None
            best_user_name = None
            
            for user_id, known_embeddings in self.known_faces.items():
                confidence = self.compare_faces(embeddings, known_embeddings)
                
                if confidence > best_confidence and confidence >= confidence_threshold:
                    best_confidence = confidence
                    best_user_id = user_id
                    best_user_name = self.known_names.get(user_id, "Unknown")
            
            if best_match:
                processing_time = (time.time() - start_time) * 1000
                self.recognition_counts += 1
                
                return RecognitionResult(
                    user_id=best_user_id,
                    user_name=best_user_name,
                    confidence=best_confidence,
                    face_location=(0, 0, face_image.shape[1], face_image.shape[0]),
                    processing_time_ms=processing_time
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Face recognition failed: {e}")
            return None
    
    def extract_embeddings(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face embeddings from an image
        
        Args:
            face_image: Face image to extract embeddings from
            
        Returns:
            Face embeddings as numpy array or None if extraction failed
        """
        try:
            # Preprocess image for better embedding extraction
            processed_image = self.preprocess_image(face_image)
            
            # Use DeepFace to extract embeddings
            embedding_result = DeepFace.represent(
                img_path=processed_image,
                model_name="Facenet512",
                enforce_detection=False,
                align=True
            )
            
            if embedding_result and len(embedding_result) > 0:
                embeddings = np.array(embedding_result[0]["embedding"])
                logger.debug(f"Extracted embeddings with {len(embeddings)} dimensions")
                return embeddings
            else:
                logger.warning("DeepFace failed to extract embeddings")
                return None
                
        except Exception as e:
            logger.error(f"Failed to extract embeddings: {e}")
            return None
    
    def compare_faces(self, face1: np.ndarray, face2: np.ndarray) -> float:
        """
        Compare two face images and return similarity score
        
        Args:
            face1: First face image
            face2: Second face image
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        try:
            # Ensure both are numpy arrays
            emb1 = np.array(face1).flatten()
            emb2 = np.array(face2).flatten()
            
            # Calculate cosine similarity
            dot_product = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            
            # Ensure result is between 0 and 1
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Error comparing faces: {e}")
            return 0.0
    
    def load_known_faces(self, faces_db_path: str) -> bool:
        """
        Load known faces from database
        
        Args:
            faces_db_path: Path to faces database
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            # This method would typically load from a face database
            # For now, we'll assume the faces are already loaded via add_known_face
            logger.info("Known faces loading method called - faces should be added individually")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load known faces: {e}")
            return False
    
    def add_known_face(self, user_id: str, user_name: str, 
                       face_image: np.ndarray) -> bool:
        """
        Add a new known face to the recognition system
        
        Args:
            user_id: Unique identifier for the user
            user_name: Display name for the user
            face_image: Face image to add
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            # Extract embeddings from the face image
            embeddings = self.extract_embeddings(face_image)
            if embeddings is None:
                logger.error(f"Failed to extract embeddings for user {user_id}")
                return False
            
            # Store embeddings and name
            self.known_faces[user_id] = embeddings
            self.known_names[user_id] = user_name
            
            logger.info(f"Added known face for user {user_id} ({user_name})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add known face for user {user_id}: {e}")
            return False
    
    def remove_known_face(self, user_id: str) -> bool:
        """
        Remove a known face from the recognition system
        
        Args:
            user_id: Unique identifier for the user to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        try:
            if user_id in self.known_faces:
                del self.known_faces[user_id]
                del self.known_names[user_id]
                logger.info(f"Removed known face for user {user_id}")
                return True
            else:
                logger.warning(f"User {user_id} not found in known faces")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove known face for user {user_id}: {e}")
            return False
    
    def get_known_faces_count(self) -> int:
        """
        Get the number of known faces in the system
        
        Returns:
            Number of known faces
        """
        return len(self.known_faces)
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better recognition
        
        Args:
            image: Input image
            
        Returns:
            Preprocessed image
        """
        try:
            # Ensure image is in RGB format
            if len(image.shape) == 3 and image.shape[2] == 3:
                # Already RGB
                processed = image.copy()
            elif len(image.shape) == 3 and image.shape[2] == 4:
                # RGBA to RGB
                processed = image[:, :, :3]
            else:
                # Grayscale to RGB
                processed = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            
            # Resize to standard size for better recognition
            target_size = (160, 160)  # Facenet512 standard size
            processed = cv2.resize(processed, target_size)
            
            # Normalize pixel values
            processed = processed.astype(np.float32) / 255.0
            
            return processed
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return image
    
    def get_face_quality_score(self, face_image: np.ndarray) -> float:
        """
        Assess the quality of a face image
        
        Args:
            face_image: Face image to assess
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        try:
            if face_image is None or face_image.size == 0:
                return 0.0
            
            # Convert to grayscale for analysis
            if len(face_image.shape) == 3:
                gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = face_image
            
            # Calculate various quality metrics
            quality_score = 0.0
            
            # 1. Resolution score (higher is better)
            height, width = gray.shape
            resolution_score = min(1.0, (height * width) / (480 * 480))
            quality_score += resolution_score * 0.3
            
            # 2. Brightness score
            mean_brightness = np.mean(gray)
            brightness_score = 1.0 - abs(mean_brightness - 128) / 128
            brightness_score = max(0.0, brightness_score)
            quality_score += brightness_score * 0.25
            
            # 3. Contrast score
            contrast = np.std(gray)
            contrast_score = min(1.0, contrast / 50.0)
            quality_score += contrast_score * 0.25
            
            # 4. Sharpness score (using Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(1.0, laplacian_var / 500.0)
            quality_score += sharpness_score * 0.2
            
            return max(0.0, min(1.0, quality_score))
            
        except Exception as e:
            logger.error(f"Face quality assessment failed: {e}")
            return 0.0
    
    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Update recognition system configuration
        
        Args:
            config: New configuration parameters
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            if 'confidence_threshold' in config:
                self.confidence_threshold = float(config['confidence_threshold'])
                logger.info(f"Updated confidence threshold to {self.confidence_threshold}")
            
            if 'use_mediapipe' in config:
                self.use_mediapipe = bool(config['use_mediapipe'])
                if self.use_mediapipe:
                    self._load_mediapipe_detector()
                logger.info(f"Updated MediaPipe usage to {self.use_mediapipe}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current configuration
        
        Returns:
            Dictionary containing current configuration
        """
        return {
            'confidence_threshold': self.confidence_threshold,
            'use_mediapipe': self.use_mediapipe,
            'mediapipe_available': MEDIAPIPE_AVAILABLE,
            'opencv_cascade_loaded': self.face_cascade is not None
        }
    
    def is_healthy(self) -> bool:
        """
        Check if the recognition system is in a healthy state
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Check if at least one detection method is available
            if not self.face_cascade and not self.mediapipe_detector:
                return False
            
            # Check if we can process a simple test image
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            try:
                self.detect_faces(test_image)
                return True
            except Exception:
                return False
                
        except Exception:
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get recognition system performance metrics
        
        Returns:
            Dictionary containing performance metrics
        """
        try:
            avg_processing_time = np.mean(self.processing_times) if self.processing_times else 0.0
            min_processing_time = np.min(self.processing_times) if self.processing_times else 0.0
            max_processing_time = np.max(self.processing_times) if self.processing_times else 0.0
            
            return {
                'total_detections': self.detection_counts,
                'total_recognitions': self.recognition_counts,
                'average_processing_time_ms': avg_processing_time,
                'min_processing_time_ms': min_processing_time,
                'max_processing_time_ms': max_processing_time,
                'known_faces_count': len(self.known_faces),
                'detection_methods': {
                    'mediapipe': self.use_mediapipe and self.mediapipe_detector is not None,
                    'opencv_cascade': self.face_cascade is not None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {}
    
    def _detect_with_mediapipe(self, image: np.ndarray) -> Optional[Dict[str, Any]]:
        """Detect faces using MediaPipe"""
        try:
            # Convert BGR to RGB for MediaPipe
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            results = self.mediapipe_detector.process(rgb_image)
            
            if results.detections:
                locations = []
                confidences = []
                
                for detection in results.detections:
                    # Get bounding box
                    bbox = detection.location_data.relative_bounding_box
                    h, w, _ = image.shape
                    
                    x = int(bbox.xmin * w)
                    y = int(bbox.ymin * h)
                    width = int(bbox.width * w)
                    height = int(bbox.height * h)
                    
                    locations.append((x, y, width, height))
                    confidences.append(detection.score[0])
                
                return {'locations': locations, 'confidences': confidences}
            
            return None
            
        except Exception as e:
            logger.error(f"MediaPipe detection failed: {e}")
            return None
    
    def _detect_with_opencv(self, image: np.ndarray) -> Optional[Dict[str, Any]]:
        """Detect faces using OpenCV cascade classifier"""
        try:
            # Convert to grayscale for cascade detection
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) > 0:
                locations = []
                confidences = []
                
                for (x, y, w, h) in faces:
                    locations.append((x, y, w, h))
                    # OpenCV doesn't provide confidence scores, so we'll use a default
                    confidences.append(0.8)
                
                return {'locations': locations, 'confidences': confidences}
            
            return None
            
        except Exception as e:
            logger.error(f"OpenCV detection failed: {e}")
            return None
