"""
Face Recognition Interface for EyeD AI Attendance System

This interface defines the contract for face recognition operations including
detection, recognition, and confidence scoring.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
from pathlib import Path


class DetectionResult:
    """Data class for face detection results"""
    def __init__(self, face_locations: List[Tuple[int, int, int, int]],
                 confidence_scores: List[float], landmarks: Optional[List[np.ndarray]] = None):
        self.face_locations = face_locations  # List of (x, y, w, h) bounding boxes
        self.confidence_scores = confidence_scores  # List of confidence scores
        self.landmarks = landmarks  # Optional facial landmarks


class RecognitionResult:
    """Data class for face recognition results"""
    def __init__(self, user_id: str, user_name: str, confidence: float,
                 face_location: Tuple[int, int, int, int], processing_time_ms: float):
        self.user_id = user_id
        self.user_name = user_name
        self.confidence = confidence
        self.face_location = face_location
        self.processing_time_ms = processing_time_ms


class RecognitionInterface(ABC):
    """
    Abstract interface for face recognition operations
    
    This interface defines the contract that all face recognition implementations
    must follow, ensuring consistent behavior across different recognition engines.
    """
    
    @abstractmethod
    def detect_faces(self, image: np.ndarray) -> DetectionResult:
        """
        Detect faces in an image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            DetectionResult containing face locations and confidence scores
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def extract_embeddings(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face embeddings from an image
        
        Args:
            face_image: Face image to extract embeddings from
            
        Returns:
            Face embeddings as numpy array or None if extraction failed
        """
        pass
    
    @abstractmethod
    def compare_faces(self, face1: np.ndarray, face2: np.ndarray) -> float:
        """
        Compare two face images and return similarity score
        
        Args:
            face1: First face image
            face2: Second face image
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        pass
    
    @abstractmethod
    def load_known_faces(self, faces_db_path: str) -> bool:
        """
        Load known faces from database
        
        Args:
            faces_db_path: Path to faces database
            
        Returns:
            True if loaded successfully, False otherwise
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def remove_known_face(self, user_id: str) -> bool:
        """
        Remove a known face from the recognition system
        
        Args:
            user_id: Unique identifier for the user to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def get_known_faces_count(self) -> int:
        """
        Get the number of known faces in the system
        
        Returns:
            Number of known faces
        """
        pass
    
    @abstractmethod
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better recognition
        
        Args:
            image: Input image
            
        Returns:
            Preprocessed image
        """
        pass
    
    @abstractmethod
    def get_face_quality_score(self, face_image: np.ndarray) -> float:
        """
        Assess the quality of a face image
        
        Args:
            face_image: Face image to assess
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        pass
    
    @abstractmethod
    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Update recognition system configuration
        
        Args:
            config: New configuration parameters
            
        Returns:
            True if update was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current configuration
        
        Returns:
            Dictionary containing current configuration
        """
        pass
    
    @abstractmethod
    def is_healthy(self) -> bool:
        """
        Check if the recognition system is in a healthy state
        
        Returns:
            True if healthy, False otherwise
        """
        pass
    
    @abstractmethod
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get recognition system performance metrics
        
        Returns:
            Dictionary containing performance metrics
        """
        pass
