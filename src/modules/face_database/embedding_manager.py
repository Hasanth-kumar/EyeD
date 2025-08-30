"""
Embedding Manager Component

This module handles only face embedding operations,
following the Single-Responsibility Principle.
"""

import pickle
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Manages face embeddings storage and retrieval"""
    
    def __init__(self, cache_file: str = "data/faces/embeddings_cache.pkl"):
        """
        Initialize embedding manager
        
        Args:
            cache_file: Path to embeddings cache file
        """
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Embedding manager initialized with cache: {self.cache_file}")
    
    def save_embeddings(self, embeddings: Dict[str, Any]) -> bool:
        """Save embeddings to cache file"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(embeddings, f)
            logger.info("Embeddings saved to cache")
            return True
        except Exception as e:
            logger.error(f"Failed to save embeddings: {e}")
            return False
    
    def load_embeddings(self) -> Dict[str, Any]:
        """Load embeddings from cache file"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'rb') as f:
                    return pickle.load(f)
            return {}
        except Exception as e:
            logger.error(f"Failed to load embeddings: {e}")
            return {}
    
    def add_embedding(self, user_id: str, embedding: Any) -> bool:
        """Add a single embedding for a user"""
        try:
            embeddings = self.load_embeddings()
            embeddings[user_id] = embedding
            return self.save_embeddings(embeddings)
        except Exception as e:
            logger.error(f"Failed to add embedding: {e}")
            return False
    
    def get_embedding(self, user_id: str) -> Optional[Any]:
        """Get embedding for a specific user"""
        try:
            embeddings = self.load_embeddings()
            return embeddings.get(user_id)
        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            return None
    
    def remove_embedding(self, user_id: str) -> bool:
        """Remove embedding for a specific user"""
        try:
            embeddings = self.load_embeddings()
            if user_id in embeddings:
                del embeddings[user_id]
                return self.save_embeddings(embeddings)
            return True
        except Exception as e:
            logger.error(f"Failed to remove embedding: {e}")
            return False
    
    def list_embeddings(self) -> List[str]:
        """List all user IDs with embeddings"""
        try:
            embeddings = self.load_embeddings()
            return list(embeddings.keys())
        except Exception as e:
            logger.error(f"Failed to list embeddings: {e}")
            return []
    
    def is_healthy(self) -> bool:
        """Check if embedding manager is healthy"""
        try:
            # Test write and read
            test_data = {"test": "data"}
            self.save_embeddings(test_data)
            loaded_data = self.load_embeddings()
            return loaded_data == test_data
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
