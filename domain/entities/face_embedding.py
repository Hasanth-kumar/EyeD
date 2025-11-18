"""
Face embedding domain entity.

Represents a face embedding in the EyeD AI Attendance System.
This is a pure domain entity with no infrastructure dependencies.
"""

from dataclasses import dataclass
from datetime import datetime

import numpy as np


@dataclass(frozen=True)
class FaceEmbedding:
    """
    Immutable face embedding entity.
    
    This entity represents a face embedding vector extracted from a face image.
    It contains no file I/O operations, just data representation.
    
    Attributes:
        user_id: ID of the user this embedding belongs to.
        embedding: Face embedding vector as numpy array.
        quality_score: Quality score of the embedding (0.0 to 1.0).
        created_at: Date and time when the embedding was created.
    
    Examples:
        >>> import numpy as np
        >>> from datetime import datetime
        >>> embedding_vector = np.array([0.1, 0.2, 0.3, ...])
        >>> face_embedding = FaceEmbedding(
        ...     user_id="user_001",
        ...     embedding=embedding_vector,
        ...     quality_score=0.9,
        ...     created_at=datetime.now()
        ... )
        >>> face_embedding.user_id
        'user_001'
    """
    
    user_id: str
    embedding: np.ndarray
    quality_score: float
    created_at: datetime
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vector.
        
        Returns:
            The dimension (size) of the embedding vector.
        """
        return self.embedding.shape[0] if len(self.embedding.shape) == 1 else self.embedding.size
    
    def is_high_quality(self, threshold: float = 0.8) -> bool:
        """
        Check if the embedding has high quality.
        
        Args:
            threshold: Quality threshold (default: 0.8).
        
        Returns:
            True if quality_score is above threshold, False otherwise.
        """
        return self.quality_score >= threshold

