"""
User Registration Service - Composite service for user registration operations.

This service groups related face recognition operations needed for user registration
(detection, quality assessment, embedding extraction) to reduce coupling in use cases.
"""

from typing import Tuple
import numpy as np

from core.recognition.detector import FaceDetector
from core.recognition.embedding_extractor import EmbeddingExtractor
from core.recognition.quality_assessor import QualityAssessor
from core.recognition.value_objects import (
    FaceLocation,
    EmbeddingResult,
    QualityResult
)
from domain.shared.exceptions import (
    FaceDetectionFailedError,
    InsufficientQualityError,
    EmbeddingExtractionFailedError
)


class UserRegistrationService:
    """
    Composite service for user registration operations.
    
    This service coordinates face detection, quality assessment, and embedding extraction
    needed for registering a new user with face recognition. It encapsulates the workflow
    of processing a face image for registration.
    """
    
    def __init__(
        self,
        face_detector: FaceDetector,
        embedding_extractor: EmbeddingExtractor,
        quality_assessor: QualityAssessor,
        min_quality_threshold: float = 0.5
    ):
        """
        Initialize user registration service.
        
        Args:
            face_detector: Face detection service.
            embedding_extractor: Face embedding extraction service.
            quality_assessor: Face quality assessment service.
            min_quality_threshold: Minimum quality threshold for face images.
        """
        self.face_detector = face_detector
        self.embedding_extractor = embedding_extractor
        self.quality_assessor = quality_assessor
        self.min_quality_threshold = min_quality_threshold
    
    def process_registration_image(
        self,
        image: np.ndarray
    ) -> Tuple[np.ndarray, QualityResult, EmbeddingResult]:
        """
        Process image for user registration: detect face, assess quality, extract embedding.
        
        Args:
            image: Full image containing the face.
        
        Returns:
            Tuple of (face_image, quality_result, embedding_result).
        
        Raises:
            FaceDetectionFailedError: If no face detected.
            InsufficientQualityError: If quality below threshold.
            EmbeddingExtractionFailedError: If embedding extraction fails.
        """
        # Step 1: Detect face
        detection_result = self.face_detector.detect(image)
        if not detection_result.faces_detected or detection_result.face_count == 0:
            raise FaceDetectionFailedError()
        
        # Get the first detected face (assumes single face registration)
        face_location = detection_result.faces[0]
        face_image = self._extract_face_region(image, face_location)
        
        # Step 2: Assess quality
        quality_result = self.quality_assessor.assess(face_image)
        if not quality_result.is_suitable:
            raise InsufficientQualityError(
                quality_score=quality_result.overall_score,
                threshold=self.min_quality_threshold
            )
        
        # Step 3: Extract embedding
        embedding_result = self.embedding_extractor.extract(face_image)
        if embedding_result is None:
            raise EmbeddingExtractionFailedError()
        
        return face_image, quality_result, embedding_result
    
    def _extract_face_region(
        self,
        image: np.ndarray,
        face_location: FaceLocation
    ) -> np.ndarray:
        """
        Extract face region from image using face location.
        
        Args:
            image: Full image containing the face.
            face_location: Location of the face in the image.
        
        Returns:
            Cropped face image as numpy array.
        """
        # Ensure coordinates are within image bounds
        height, width = image.shape[:2]
        x = max(0, face_location.x)
        y = max(0, face_location.y)
        x_end = min(width, x + face_location.width)
        y_end = min(height, y + face_location.height)
        
        # Extract face region
        face_image = image[y:y_end, x:x_end]
        
        return face_image












