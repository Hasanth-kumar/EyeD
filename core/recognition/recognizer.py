"""
Pure face recognition/matching logic.

This module provides face recognition by matching embeddings using cosine similarity.
No file I/O, no database access, no embedding extraction - pure matching logic only.
"""

import logging
from typing import Dict, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

from .value_objects import RecognitionResult


class FaceRecognizer:
    """
    Pure face recognition by matching embeddings.
    
    Single Responsibility: Recognize faces by matching embeddings ONLY.
    No file I/O, no database access, no embedding extraction.
    """
    
    def __init__(self, similarity_metric: str = "cosine"):
        """
        Initialize the face recognizer.
        
        Args:
            similarity_metric: Similarity metric to use ("cosine" is currently the only supported option)
        """
        if similarity_metric != "cosine":
            raise ValueError(f"Unsupported similarity metric: {similarity_metric}. Only 'cosine' is supported.")
        self.similarity_metric = similarity_metric
    
    def recognize(
        self,
        face_embedding: np.ndarray,
        known_embeddings: Dict[str, np.ndarray],
        threshold: float,
        user_names: Optional[Dict[str, str]] = None
    ) -> Optional[RecognitionResult]:
        """
        Recognize a face by matching its embedding against known embeddings.
        
        Args:
            face_embedding: The embedding of the face to recognize
            known_embeddings: Dictionary mapping user_id to their embedding(s)
                            Can be single embedding (np.ndarray) or list of embeddings
            threshold: Minimum similarity threshold for recognition
            user_names: Optional dictionary mapping user_id to user_name.
                       If None, user_name will be set to user_id.
        
        Returns:
            RecognitionResult if a match is found above threshold, None otherwise
        """
        if user_names is None:
            user_names = {}
        
        # Find the best match
        best_match = self.find_best_match(face_embedding, known_embeddings, threshold)
        
        if best_match is None:
            return None
        
        user_id, match_score = best_match
        
        # Get user name (default to user_id if not provided)
        user_name = user_names.get(user_id, user_id)
        
        # Confidence is the same as match_score for now
        # (could be normalized differently in the future)
        confidence = match_score
        
        return RecognitionResult(
            user_id=user_id,
            user_name=user_name,
            confidence=confidence,
            match_score=match_score
        )
    
    def compare_embeddings(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Compare two embeddings and return similarity score.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
        
        Returns:
            Similarity score between 0.0 and 1.0 (cosine similarity)
        """
        if self.similarity_metric == "cosine":
            return self._cosine_similarity(embedding1, embedding2)
        else:
            raise ValueError(f"Unsupported similarity metric: {self.similarity_metric}")
    
    def find_best_match(
        self,
        embedding: np.ndarray,
        candidates: Dict[str, np.ndarray],
        threshold: float
    ) -> Optional[Tuple[str, float]]:
        """
        Find the best matching candidate for the given embedding.
        
        Args:
            embedding: The embedding to match
            candidates: Dictionary mapping user_id to their embedding(s)
                       Can be single embedding (np.ndarray) or list/array of embeddings
            threshold: Minimum similarity threshold for a match
        
        Returns:
            Tuple of (user_id, similarity_score) if match found above threshold, None otherwise
        """
        best_user_id = None
        best_score = 0.0
        
        logger.info(f"Finding best match: {len(candidates)} candidates, threshold={threshold}")
        logger.info(f"Input embedding shape: {embedding.shape}, dtype: {embedding.dtype}, norm: {np.linalg.norm(embedding):.6f}")
        
        if len(candidates) == 0:
            logger.error("No candidates provided for matching!")
            return None
        
        for user_id, candidate_embedding in candidates.items():
            # Handle both single embedding and multiple embeddings per user
            if isinstance(candidate_embedding, (list, tuple)):
                # If user has multiple embeddings, compare with all and take the best
                scores = [
                    self.compare_embeddings(embedding, np.array(emb))
                    for emb in candidate_embedding
                ]
                similarity = max(scores) if scores else 0.0
            else:
                # Single embedding per user
                candidate_array = np.array(candidate_embedding)
                logger.info(f"Candidate {user_id}: shape={candidate_array.shape}, dtype={candidate_array.dtype}, norm={np.linalg.norm(candidate_array):.6f}")
                similarity = self.compare_embeddings(embedding, candidate_array)
            
            logger.info(f"Similarity with {user_id}: {similarity:.6f} (threshold: {threshold})")
            
            # Update best match if this is better and above threshold
            if similarity > best_score and similarity >= threshold:
                best_score = similarity
                best_user_id = user_id
        
        if best_user_id is None:
            logger.warning(f"No match found above threshold {threshold}. Best score was {best_score:.6f}")
            return None
        
        return (best_user_id, best_score)
    
    def _cosine_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
        
        Returns:
            Cosine similarity score between 0.0 and 1.0
        """
        # Ensure both are numpy arrays and flattened
        emb1 = np.array(embedding1).flatten()
        emb2 = np.array(embedding2).flatten()
        
        # Check if dimensions match
        if emb1.shape != emb2.shape:
            logger.error(f"Dimension mismatch in cosine similarity: {emb1.shape} vs {emb2.shape}")
            return 0.0
        
        # Calculate cosine similarity: dot product / (norm1 * norm2)
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        # Handle zero norm case
        if norm1 == 0 or norm2 == 0:
            logger.error(f"Zero norm detected in cosine similarity: norm1={norm1:.6f}, norm2={norm2:.6f}")
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Ensure result is between 0 and 1
        # Cosine similarity ranges from -1 to 1, but for normalized embeddings
        # it should be between 0 and 1. Clamp to ensure valid range.
        result = max(0.0, min(1.0, similarity))
        logger.info(f"Cosine similarity: {result:.6f} (dot={dot_product:.6f}, norm1={norm1:.6f}, norm2={norm2:.6f})")
        return result






