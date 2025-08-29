"""
Face Recognition Module for EyeD AI Attendance System
Day 4 Implementation: Face Recognition (Basic)

This module handles:
- Face detection in frames
- Face recognition using DeepFace
- Matching with stored embeddings
- Confidence scoring
"""

import cv2
import numpy as np
from typing import Tuple, Optional, Dict, List
from pathlib import Path
import logging
from deepface import DeepFace
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceRecognition:
    """Face recognition handler for EyeD AI Attendance System"""
    
    def __init__(self, confidence_threshold: float = 0.6):
        """
        Initialize Face Recognition system
        
        Args:
            confidence_threshold: Minimum confidence for recognition (0.0 to 1.0)
        """
        self.confidence_threshold = confidence_threshold
        self.known_faces = {}
        self.known_names = {}
        self.face_cascade = None
        self._load_face_cascade()
        
        logger.info(f"Face Recognition initialized with confidence threshold: {confidence_threshold}")
    
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
    
    def load_known_faces(self, faces_db_path: str = "data/faces") -> bool:
        """
        Load known face embeddings from database
        
        Args:
            faces_db_path: Path to faces database
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            from modules.face_db import FaceDatabase
            
            # Initialize face database
            face_db = FaceDatabase(faces_db_path)
            
            # Load embeddings
            embeddings = face_db.load_embeddings()
            
            if not embeddings:
                logger.warning("No embeddings found in database")
                return False
            
            # Store embeddings and names
            self.known_faces = {}
            self.known_names = {}
            
            for user_id, embedding in embeddings.items():
                user_data = face_db.get_user_data(user_id)
                if user_data:
                    self.known_faces[user_id] = embedding
                    self.known_names[user_id] = user_data.get('name', user_id)
            
            logger.info(f"Loaded {len(self.known_faces)} known faces from database")
            return True
            
        except ImportError as e:
            logger.error(f"Failed to import face database module: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load known faces: {e}")
            return False
    
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in a frame using OpenCV
        
        Args:
            frame: Input frame/image (BGR format)
            
        Returns:
            List of face bounding boxes (x, y, w, h)
        """
        if self.face_cascade is None:
            logger.warning("Face cascade not loaded, cannot detect faces")
            return []
        
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Convert to list of tuples
            face_boxes = [(x, y, w, h) for (x, y, w, h) in faces]
            
            logger.debug(f"Detected {len(face_boxes)} faces in frame")
            return face_boxes
            
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return []
    
    def extract_face_embedding(self, face_img: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face embedding using DeepFace
        
        Args:
            face_img: Cropped face image (BGR format)
            
        Returns:
            Face embedding vector or None if extraction failed
        """
        try:
            # Ensure face image is in the right format
            if len(face_img.shape) == 3:
                # Convert BGR to RGB for DeepFace
                face_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            else:
                face_rgb = face_img
            
            # Extract embedding using DeepFace
            embedding = DeepFace.represent(
                img_path=face_rgb,
                model_name="VGG-Face",
                enforce_detection=False
            )
            
            if embedding and len(embedding) > 0:
                # Convert to numpy array
                embedding_array = np.array(embedding[0]["embedding"], dtype=np.float32)
                logger.debug(f"Extracted embedding with shape: {embedding_array.shape}")
                return embedding_array
            else:
                logger.warning("DeepFace failed to extract embedding")
                return None
                
        except Exception as e:
            logger.error(f"Face embedding extraction failed: {e}")
            return None
    
    def compare_embeddings(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compare two face embeddings using cosine similarity
        
        Args:
            embedding1: First face embedding
            embedding2: Second face embedding
            
        Returns:
            Similarity score (0.0 to 1.0, higher is more similar)
        """
        try:
            # Normalize embeddings
            emb1_norm = embedding1 / np.linalg.norm(embedding1)
            emb2_norm = embedding2 / np.linalg.norm(embedding2)
            
            # Calculate cosine similarity
            similarity = np.dot(emb1_norm, emb2_norm)
            
            # Ensure result is between 0 and 1
            similarity = max(0.0, min(1.0, similarity))
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Embedding comparison failed: {e}")
            return 0.0
    
    def recognize_face(self, face_img: np.ndarray) -> Tuple[str, float]:
        """
        Recognize a face using stored embeddings
        
        Args:
            face_img: Cropped face image
            
        Returns:
            Tuple of (name, confidence)
        """
        if not self.known_faces:
            logger.warning("No known faces loaded, cannot perform recognition")
            return ("Unknown", 0.0)
        
        try:
            # Extract embedding from the face image
            face_embedding = self.extract_face_embedding(face_img)
            
            if face_embedding is None:
                return ("Unknown", 0.0)
            
            # Compare with all known faces
            best_match = ("Unknown", 0.0)
            
            for user_id, known_embedding in self.known_faces.items():
                similarity = self.compare_embeddings(face_embedding, known_embedding)
                
                if similarity > best_match[1] and similarity >= self.confidence_threshold:
                    best_match = (self.known_names.get(user_id, user_id), similarity)
            
            logger.debug(f"Face recognition result: {best_match[0]} (confidence: {best_match[1]:.3f})")
            return best_match
            
        except Exception as e:
            logger.error(f"Face recognition failed: {e}")
            return ("Unknown", 0.0)
    
    def recognize_user(self, frame: np.ndarray) -> List[Dict]:
        """
        Recognize users in a frame through face detection and recognition
        
        Args:
            frame: Input frame
            
        Returns:
            List of recognition results with bounding boxes and names
        """
        try:
            # Detect faces in the frame
            face_boxes = self.detect_faces(frame)
            
            if not face_boxes:
                return []
            
            results = []
            
            # Process each detected face
            for (x, y, w, h) in face_boxes:
                # Extract face region
                face_img = frame[y:y+h, x:x+w]
                
                # Recognize the face
                name, confidence = self.recognize_face(face_img)
                
                # Create result dictionary
                result = {
                    'bbox': (x, y, w, h),
                    'name': name,
                    'confidence': confidence,
                    'recognized': confidence >= self.confidence_threshold
                }
                
                results.append(result)
                
                logger.debug(f"Processed face: {name} at ({x}, {y}) with confidence {confidence:.3f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Frame processing failed: {e}")
            return []
    
    def recognize_from_image(self, image_path: str) -> List[Dict]:
        """
        Recognize faces from an image file
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of recognition results
        """
        try:
            # Load image
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return []
            
            frame = cv2.imread(image_path)
            if frame is None:
                logger.error(f"Failed to load image: {image_path}")
                return []
            
            # Process the frame
            results = self.recognize_user(frame)
            
            logger.info(f"Recognized {len(results)} faces from image: {image_path}")
            return results
            
        except Exception as e:
            logger.error(f"Image recognition failed: {e}")
            return []
    
    def get_recognition_stats(self) -> Dict:
        """
        Get recognition system statistics
        
        Returns:
            Dictionary with recognition statistics
        """
        return {
            'known_faces_count': len(self.known_faces),
            'confidence_threshold': self.confidence_threshold,
            'face_cascade_loaded': self.face_cascade is not None,
            'total_known_names': len(self.known_names)
        }

# Global recognition instance
face_recognition = FaceRecognition()
