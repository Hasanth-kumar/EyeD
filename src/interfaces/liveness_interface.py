"""
Liveness Detection Interface for EyeD AI Attendance System

This interface defines the contract for liveness detection operations including
blink detection, head movement analysis, and anti-spoofing measures.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
from enum import Enum


class LivenessTestType(Enum):
    """Enumeration of liveness test types"""
    BLINK_DETECTION = "blink_detection"
    HEAD_MOVEMENT = "head_movement"
    EYE_MOVEMENT = "eye_movement"
    MOUTH_MOVEMENT = "mouth_movement"
    DEPTH_ANALYSIS = "depth_analysis"
    TEXTURE_ANALYSIS = "texture_analysis"


class LivenessResult:
    """Data class for liveness detection results"""
    def __init__(self, is_live: bool, confidence: float, test_type: LivenessTestType,
                 details: Dict[str, Any], processing_time_ms: float):
        self.is_live = is_live
        self.confidence = confidence
        self.test_type = test_type
        self.details = details
        self.processing_time_ms = processing_time_ms


class LivenessInterface(ABC):
    """
    Abstract interface for liveness detection operations
    
    This interface defines the contract that all liveness detection implementations
    must follow, ensuring consistent behavior across different liveness engines.
    """
    
    @abstractmethod
    def detect_blink(self, face_image: np.ndarray) -> LivenessResult:
        """
        Detect blinking in a face image
        
        Args:
            face_image: Face image to analyze
            
        Returns:
            LivenessResult indicating if blink was detected
        """
        pass
    
    @abstractmethod
    def detect_head_movement(self, face_images: List[np.ndarray]) -> LivenessResult:
        """
        Detect head movement across multiple frames
        
        Args:
            face_images: List of face images from consecutive frames
            
        Returns:
            LivenessResult indicating if head movement was detected
        """
        pass
    
    @abstractmethod
    def detect_eye_movement(self, face_images: List[np.ndarray]) -> LivenessResult:
        """
        Detect eye movement across multiple frames
        
        Args:
            face_images: List of face images from consecutive frames
            
        Returns:
            LivenessResult indicating if eye movement was detected
        """
        pass
    
    @abstractmethod
    def detect_mouth_movement(self, face_images: List[np.ndarray]) -> LivenessResult:
        """
        Detect mouth movement across multiple frames
        
        Args:
            face_images: List of face images from consecutive frames
            
        Returns:
            LivenessResult indicating if mouth movement was detected
        """
        pass
    
    @abstractmethod
    def analyze_depth(self, face_image: np.ndarray) -> LivenessResult:
        """
        Analyze depth information to detect 2D spoofing attempts
        
        Args:
            face_image: Face image to analyze
            
        Returns:
            LivenessResult indicating if depth analysis suggests liveness
        """
        pass
    
    @abstractmethod
    def analyze_texture(self, face_image: np.ndarray) -> LivenessResult:
        """
        Analyze texture patterns to detect spoofing attempts
        
        Args:
            face_image: Face image to analyze
            
        Returns:
            LivenessResult indicating if texture analysis suggests liveness
        """
        pass
    
    @abstractmethod
    def run_comprehensive_test(self, face_images: List[np.ndarray],
                             test_types: Optional[List[LivenessTestType]] = None) -> LivenessResult:
        """
        Run a comprehensive liveness test using multiple detection methods
        
        Args:
            face_images: List of face images for analysis
            test_types: Optional list of specific test types to run
            
        Returns:
            LivenessResult with comprehensive analysis
        """
        pass
    
    @abstractmethod
    def get_required_frames(self, test_type: LivenessTestType) -> int:
        """
        Get the number of frames required for a specific test type
        
        Args:
            test_type: Type of liveness test
            
        Returns:
            Number of frames required
        """
        pass
    
    @abstractmethod
    def preprocess_for_liveness(self, face_image: np.ndarray) -> np.ndarray:
        """
        Preprocess face image for liveness detection
        
        Args:
            face_image: Input face image
            
        Returns:
            Preprocessed image optimized for liveness detection
        """
        pass
    
    @abstractmethod
    def get_test_configuration(self, test_type: LivenessTestType) -> Dict[str, Any]:
        """
        Get configuration for a specific test type
        
        Args:
            test_type: Type of liveness test
            
        Returns:
            Configuration dictionary for the test
        """
        pass
    
    @abstractmethod
    def update_test_configuration(self, test_type: LivenessTestType,
                                config: Dict[str, Any]) -> bool:
        """
        Update configuration for a specific test type
        
        Args:
            test_type: Type of liveness test
            config: New configuration parameters
            
        Returns:
            True if update was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_supported_tests(self) -> List[LivenessTestType]:
        """
        Get list of supported liveness test types
        
        Returns:
            List of supported test types
        """
        pass
    
    @abstractmethod
    def is_test_available(self, test_type: LivenessTestType) -> bool:
        """
        Check if a specific test type is available
        
        Args:
            test_type: Type of liveness test to check
            
        Returns:
            True if test is available, False otherwise
        """
        pass
    
    @abstractmethod
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get liveness detection performance metrics
        
        Returns:
            Dictionary containing performance metrics
        """
        pass
    
    @abstractmethod
    def is_healthy(self) -> bool:
        """
        Check if the liveness detection system is in a healthy state
        
        Returns:
            True if healthy, False otherwise
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the underlying liveness detection models
        
        Returns:
            Dictionary containing model information
        """
        pass
