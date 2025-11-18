"""
Face embedding extraction module for EyeD AI Attendance System.

This module provides pure embedding extraction logic with no infrastructure dependencies.
"""

import time
from typing import Optional, List
import numpy as np

# Try to import DeepFace
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    DeepFace = None

# Try to import OpenCV for preprocessing
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None

from .value_objects import EmbeddingResult

__all__ = ['EmbeddingExtractor', 'DEEPFACE_AVAILABLE', 'OPENCV_AVAILABLE']


class EmbeddingExtractor:
    """
    Pure face embedding extraction logic.
    
    Single Responsibility: Extract face embeddings ONLY.
    No file I/O, no database access, no matching logic.
    """
    
    def __init__(self, model_name: str = "VGG-Face", enforce_detection: bool = False, align: bool = True):
        """
        Initialize the embedding extractor.
        
        Args:
            model_name: DeepFace model name (default: "VGG-Face")
            enforce_detection: Whether to enforce face detection (default: False)
            align: Whether to align faces (default: True)
        """
        if not DEEPFACE_AVAILABLE:
            raise ImportError("DeepFace is not available. Install it with: pip install deepface")
        
        if not OPENCV_AVAILABLE:
            raise ImportError("OpenCV is not available. Install it with: pip install opencv-python")
        
        self.model_name = model_name
        self.enforce_detection = enforce_detection
        self.align = align
        self._embedding_dimension = None
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for embedding extraction.
        
        Args:
            image: Input face image as numpy array (RGB, RGBA, or grayscale format)
            
        Returns:
            Preprocessed image ready for DeepFace (RGB format, 224x224, uint8)
        """
        if not OPENCV_AVAILABLE:
            raise ImportError("OpenCV is required for image preprocessing")
        
        # Ensure image is in RGB format (matching old preprocess_image behavior)
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Already RGB (or BGR - caller should convert if needed)
            processed = image.copy()
        elif len(image.shape) == 3 and image.shape[2] == 4:
            # RGBA to RGB
            processed = image[:, :, :3]
        elif len(image.shape) == 2:
            # Grayscale to RGB
            processed = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:
            # Unknown format, try to use as-is
            processed = image.copy()
        
        # VGG-Face expects 224x224 images
        target_size = (224, 224)
        processed = cv2.resize(processed, target_size)
        
        # VGG-Face expects pixel values in range [0, 255], not normalized
        if processed.dtype != np.uint8:
            # Normalize to [0, 255] if needed
            if processed.max() <= 1.0:
                processed = (processed * 255).astype(np.uint8)
            else:
                processed = processed.astype(np.uint8)
        
        return processed
    
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
            # Preprocess image
            processed_image = self._preprocess_image(face_image)
            
            # Extract embedding using DeepFace
            embedding_result = DeepFace.represent(
                img_path=processed_image,
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
                
        except Exception:
            # Return None on error (pure extraction logic, no logging)
            return None
    
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
            Embedding dimension, or None if not yet determined
        """
        if self._embedding_dimension is not None:
            return self._embedding_dimension
        
        # Try to determine dimension by extracting from a dummy image
        # This is a fallback if extract() hasn't been called yet
        try:
            # Create a minimal dummy image (224x224 RGB)
            dummy_image = np.zeros((224, 224, 3), dtype=np.uint8)
            result = self.extract(dummy_image)
            if result:
                return result.dimension
        except Exception:
            pass
        
        return None

