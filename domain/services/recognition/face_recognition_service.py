"""
Face Recognition Service - Composite service for face recognition operations.

This service groups related face recognition operations (detection, extraction,
recognition, quality assessment) to reduce coupling in use cases.

This service is used in Phase 1 of the two-phase attendance marking workflow:
- Phase 1: Face recognition from a single frame (this service)
- Phase 2: Liveness verification with real-time blink detection (LivenessService)

The service supports single-frame recognition, which is used in Phase 1 to
identify the user before proceeding to liveness verification.
"""

from typing import Optional, Tuple, Dict, Any, List
import numpy as np
import logging

from core.recognition.detector import FaceDetector
from core.recognition.embedding_extractor import EmbeddingExtractor
from core.recognition.recognizer import FaceRecognizer
from core.recognition.quality_assessor import QualityAssessor
from core.recognition.value_objects import (
    FaceLocation,
    DetectionResult,
    EmbeddingResult,
    RecognitionResult,
    QualityResult
)
from domain.shared.exceptions import (
    FaceDetectionFailedError,
    InsufficientQualityError,
    FaceNotRecognizedError
)
from domain.shared.constants import DEFAULT_CONFIDENCE_THRESHOLD


class FaceRecognitionService:
    """
    Composite service for face recognition operations.
    
    This service coordinates face detection, quality assessment, embedding extraction,
    and face recognition. It encapsulates the workflow of recognizing a face from an image.
    
    Uses ArcFace model for embedding extraction, which provides improved accuracy
    especially for multi-face scenarios and smaller/distant faces in group photos.
    """
    
    def __init__(
        self,
        face_detector: FaceDetector,
        embedding_extractor: EmbeddingExtractor,
        face_recognizer: FaceRecognizer,
        quality_assessor: QualityAssessor,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
        min_quality_threshold: float = 0.5
    ):
        """
        Initialize face recognition service.
        
        Args:
            face_detector: Face detection service.
            embedding_extractor: Face embedding extraction service.
            face_recognizer: Face recognition service.
            quality_assessor: Face quality assessment service.
            confidence_threshold: Minimum confidence threshold for recognition.
            min_quality_threshold: Minimum quality threshold for face images.
        """
        self.face_detector = face_detector
        self.embedding_extractor = embedding_extractor
        self.face_recognizer = face_recognizer
        self.quality_assessor = quality_assessor
        self.confidence_threshold = confidence_threshold
        self.min_quality_threshold = min_quality_threshold
    
    def detect_and_assess_face(
        self,
        image: np.ndarray
    ) -> Tuple[np.ndarray, QualityResult]:
        """
        Detect face in image, extract face region, and assess quality.
        
        This method is used in Phase 1 of the attendance workflow to process
        a single frame for face recognition. It supports single-frame processing
        and does not require a sequence of frames.
        
        Args:
            image: Full image containing the face (single frame).
        
        Returns:
            Tuple of (face_image, quality_result).
        
        Raises:
            FaceDetectionFailedError: If no face detected.
            InsufficientQualityError: If quality below threshold.
        """
        # Step 1: Detect face
        detection_result = self.face_detector.detect(image)
        if not detection_result.faces_detected or detection_result.face_count == 0:
            raise FaceDetectionFailedError()
        
        # Get the first detected face (assumes single face)
        face_location = detection_result.faces[0]
        face_image = self._extract_face_region(image, face_location)
        
        # Step 2: Assess quality
        quality_result = self.quality_assessor.assess(face_image)
        if not quality_result.is_suitable:
            raise InsufficientQualityError(
                quality_score=quality_result.overall_score,
                threshold=self.min_quality_threshold
            )
        
        return face_image, quality_result
    
    def recognize_face(
        self,
        face_image: np.ndarray,
        known_embeddings: Dict[str, np.ndarray],
        user_names: Dict[str, str]
    ) -> RecognitionResult:
        """
        Extract embedding and recognize face from known embeddings.
        
        This method is used in Phase 1 of the attendance workflow to recognize
        a user from a single face image. It processes a single frame and does
        not require a sequence of frames.
        
        Uses ArcFace model for embedding extraction, providing improved recognition
        accuracy compared to previous models.
        
        Args:
            face_image: Cropped face image (single frame from Phase 1).
            known_embeddings: Dictionary mapping user_id to embedding arrays.
            user_names: Dictionary mapping user_id to user names.
        
        Returns:
            RecognitionResult with user_id, user_name, and confidence.
        
        Raises:
            FaceNotRecognizedError: If recognition fails.
        """
        # Step 1: Extract embedding
        embedding_result = self.embedding_extractor.extract(face_image)
        if embedding_result is None:
            raise FaceNotRecognizedError(message="Failed to extract face embedding")
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Extracted embedding: shape={embedding_result.embedding.shape}, dtype={embedding_result.embedding.dtype}, norm={np.linalg.norm(embedding_result.embedding):.6f}")
        
        # Step 2: Recognize face
        recognition_result = self.face_recognizer.recognize(
            face_embedding=embedding_result.embedding,
            known_embeddings=known_embeddings,
            threshold=self.confidence_threshold,
            user_names=user_names
        )
        
        if recognition_result is None:
            raise FaceNotRecognizedError(
                confidence=0.0,
                threshold=self.confidence_threshold
            )
        
        return recognition_result
    
    def recognize_multiple_faces(
        self,
        image: np.ndarray,
        known_embeddings: Dict[str, np.ndarray],
        user_names: Dict[str, str]
    ) -> List[Optional[RecognitionResult]]:
        """
        Detect and recognize all faces in an image.
        
        This method processes a single image containing multiple faces, detecting
        each face and attempting recognition. Used for class attendance where
        a single photo contains multiple students.
        
        Uses ArcFace model for embedding extraction, which provides superior
        performance for smaller and more distant faces. This is especially
        beneficial for class attendance photos where students may be at varying
        distances from the camera.
        
        Args:
            image: Full image containing multiple faces.
            known_embeddings: Dictionary mapping user_id to embedding arrays.
            user_names: Dictionary mapping user_id to user names.
        
        Returns:
            List of RecognitionResult objects (one per detected face).
            Returns None for faces that fail detection, quality check, or recognition.
        """
        logger = logging.getLogger(__name__)
        results: List[Optional[RecognitionResult]] = []
        
        # Step 1: Detect all faces
        detection_result = self.face_detector.detect(image)
        if not detection_result.faces_detected or detection_result.face_count == 0:
            logger.info("No faces detected in image")
            return results
        
        logger.info(f"Detected {detection_result.face_count} face(s) in image")
        
        # Step 2: Process each detected face
        for face_location in detection_result.faces:
            try:
                # Extract face region
                face_image = self._extract_face_region(image, face_location)
                
                # Assess quality
                quality_result = self.quality_assessor.assess(face_image)
                if quality_result.overall_score < self.min_quality_threshold:
                    logger.debug(f"Face quality insufficient: {quality_result.overall_score:.3f} < {self.min_quality_threshold}")
                    results.append(None)
                    continue
                
                # Extract embedding
                embedding_result = self.embedding_extractor.extract(face_image)
                if embedding_result is None:
                    logger.debug("Failed to extract embedding for face")
                    results.append(None)
                    continue
                
                # Recognize face
                recognition_result = self.face_recognizer.recognize(
                    face_embedding=embedding_result.embedding,
                    known_embeddings=known_embeddings,
                    threshold=self.confidence_threshold,
                    user_names=user_names
                )
                
                results.append(recognition_result)
                
            except Exception as e:
                logger.warning(f"Error processing face: {str(e)}")
                results.append(None)
        
        return results
    
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






