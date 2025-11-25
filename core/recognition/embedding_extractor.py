"""
Face embedding extraction module for EyeD AI Attendance System.

This module provides pure embedding extraction logic with no infrastructure dependencies.
"""

import time
import logging
from typing import Optional, List
import numpy as np

logger = logging.getLogger(__name__)

# Import DeepFace - environment should be properly configured via requirements.txt
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
    logger.info("DeepFace imported successfully")
except ImportError as e:
    logger.error(f"Failed to import DeepFace: {e}", exc_info=True)
    DEEPFACE_AVAILABLE = False
    DeepFace = None
except Exception as e:
    logger.warning(f"Error importing DeepFace: {e}", exc_info=True)
    DEEPFACE_AVAILABLE = False
    DeepFace = None

from .value_objects import EmbeddingResult

# Embedding dimensions for known models (no need to run inference to determine)
EMBEDDING_DIMENSIONS = {
    'ArcFace': 512,
    'VGG-Face': 4096,
    'Facenet': 128,
    'Facenet512': 512,
    'OpenFace': 128,
    'DeepFace': 4096,
    'DeepID': 160,
    'Dlib': 128,
    'SFace': 128,
}

__all__ = ['EmbeddingExtractor', 'DEEPFACE_AVAILABLE']


class EmbeddingExtractor:
    """
    Pure face embedding extraction logic.
    
    Uses ArcFace model by default for improved recognition accuracy, especially
    for smaller/distant faces in group photos.
    
    Single Responsibility: Extract face embeddings ONLY.
    No file I/O, no database access, no matching logic.
    """
    
    def __init__(self, model_name: str = "ArcFace", enforce_detection: bool = False, align: bool = True):
        """
        Initialize the embedding extractor.
        
        Args:
            model_name: DeepFace model name (default: "ArcFace")
            enforce_detection: Whether to enforce face detection (default: False)
            align: Whether to align faces (default: True)
        """
        if not DEEPFACE_AVAILABLE:
            error_msg = (
                "DeepFace is not available. Please install dependencies:\n"
                "pip install deepface==0.0.95 tensorflow==2.15.0 tf-keras==2.15.0\n"
                "Check application logs for detailed error messages."
            )
            logger.error(error_msg)
            raise ImportError(error_msg)
        
        self.model_name = model_name
        self.enforce_detection = enforce_detection
        self.align = align
        self._embedding_dimension = None
    
    def _normalize_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """
        Normalize embedding vector to unit length.
        
        Args:
            embedding: Raw embedding vector
            
        Returns:
            Normalized embedding vector
        """
        norm = np.linalg.norm(embedding)
        if norm > 0:
            return embedding / norm
        return embedding
    
    def extract(self, face_image: np.ndarray) -> Optional[EmbeddingResult]:
        """
        Extract face embeddings from a single face image.
        
        Args:
            face_image: Face image as numpy array (cropped face)
            
        Returns:
            EmbeddingResult with embedding, dimension, and extraction time, or None if extraction failed
        """
        if face_image is None or face_image.size == 0:
            return None
        
        start_time = time.time()
        
        try:
            # DeepFace handles all preprocessing internally (resize, color conversion, etc.)
            embedding_result = DeepFace.represent(
                img_path=face_image,
                model_name=self.model_name,
                enforce_detection=self.enforce_detection,
                align=self.align
            )
            
            if embedding_result and len(embedding_result) > 0:
                # Extract embedding vector
                raw_embedding = np.array(embedding_result[0]["embedding"], dtype=np.float32)
                
                # Normalize embedding
                normalized_embedding = self._normalize_embedding(raw_embedding)
                
                # Calculate extraction time
                extraction_time_ms = (time.time() - start_time) * 1000
                
                # Cache dimension for future calls
                self._embedding_dimension = len(normalized_embedding)
                
                return EmbeddingResult(
                    embedding=normalized_embedding,
                    dimension=len(normalized_embedding),
                    extraction_time_ms=extraction_time_ms
                )
            else:
                return None
                
        except Exception as e:
            # Re-raise exception with context for better error handling at service layer
            # This maintains pure extraction logic while allowing proper error propagation
            error_msg = (
                f"Embedding extraction failed with {self.model_name} model: "
                f"{type(e).__name__}: {str(e)}"
            )
            raise RuntimeError(error_msg) from e
    
    def extract_batch(self, face_images: List[np.ndarray]) -> List[Optional[EmbeddingResult]]:
        """
        Extract face embeddings from multiple face images.
        
        Args:
            face_images: List of face images as numpy arrays
            
        Returns:
            List of EmbeddingResult objects (None for failed extractions)
        """
        results = []
        for face_image in face_images:
            result = self.extract(face_image)
            results.append(result)
        return results
    
    def get_embedding_dimension(self) -> Optional[int]:
        """
        Get the dimension of embeddings produced by this extractor.
        
        Returns:
            Embedding dimension, or None if model is not in known dimensions
        """
        # Return cached dimension if available
        if self._embedding_dimension is not None:
            return self._embedding_dimension
        
        # Look up dimension from known model dimensions (fast dictionary lookup)
        return EMBEDDING_DIMENSIONS.get(self.model_name)

