"""
Face Database Module for EyeD AI Attendance System
Day 3 Implementation: Embedding Database

This module handles:
- Efficient embedding storage and retrieval
- User metadata management
- Search and query optimization
- Memory management for large embedding databases
"""

import os
import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import logging
from pathlib import Path
import pickle
import hashlib
import time
import cv2
from PIL import Image

# Import interface
try:
    from ..interfaces.face_database_interface import FaceDatabaseInterface
except ImportError:
    # Fallback to absolute imports for testing
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
    from interfaces.face_database_interface import FaceDatabaseInterface

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceDatabase(FaceDatabaseInterface):
    """
    Efficient Face Embedding Database for EyeD AI Attendance System
    
    Features:
    - Optimized embedding storage and retrieval
    - User metadata management
    - Search and query functions
    - Memory-efficient operations
    - Backup and recovery mechanisms
    """
    
    def __init__(self, face_repository, data_dir: str = "data/faces"):
        """
        Initialize Face Database
        
        Args:
            face_repository: Repository for face data persistence
            data_dir: Directory to store face data and embeddings
        """
        self.face_repository = face_repository
        self.data_dir = Path(data_dir)
        self.embeddings_file = self.data_dir / "faces.json"
        self.embeddings_cache_file = self.data_dir / "embeddings_cache.pkl"
        self.backup_dir = self.data_dir / "backups"
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Initialize database
        self.users_db = {}
        self.embeddings_cache = {}
        self.user_embeddings = {}
        
        # Load existing data
        self._load_database()
        
        logger.info(f"Face Database initialized. Data directory: {self.data_dir}")
    
    def _load_database(self):
        """Load existing database from files"""
        try:
            # Load user metadata
            if self.embeddings_file.exists():
                with open(self.embeddings_file, 'r') as f:
                    self.users_db = json.load(f)
                logger.info(f"Loaded {len(self.users_db)} users from database")
            
            # Load embeddings cache if exists
            if self.embeddings_cache_file.exists():
                try:
                    with open(self.embeddings_cache_file, 'rb') as f:
                        cache_data = pickle.load(f)
                        self.embeddings_cache = cache_data.get('embeddings', {})
                        self.user_embeddings = cache_data.get('user_embeddings', {})
                    logger.info(f"Loaded embeddings cache with {len(self.embeddings_cache)} entries")
                except Exception as e:
                    logger.warning(f"Failed to load embeddings cache: {e}")
                    self._rebuild_cache()
            else:
                self._rebuild_cache()
                
        except Exception as e:
            logger.error(f"Failed to load database: {e}")
            self.users_db = {}
            self.embeddings_cache = {}
            self.user_embeddings = {}
    
    def _rebuild_cache(self):
        """Rebuild embeddings cache from user database"""
        logger.info("Rebuilding embeddings cache...")
        self.embeddings_cache = {}
        self.user_embeddings = {}
        
        for user_id, user_data in self.users_db.items():
            if 'embeddings' in user_data:
                self.user_embeddings[user_id] = np.array(user_data['embeddings'])
                # Create hash for quick lookup
                embedding_hash = hashlib.md5(user_data['embeddings']).hexdigest()
                self.embeddings_cache[embedding_hash] = user_id
        
        self._save_cache()
        logger.info("Embeddings cache rebuilt successfully")
    
    def _save_cache(self):
        """Save embeddings cache to file"""
        try:
            cache_data = {
                'embeddings': self.embeddings_cache,
                'user_embeddings': {k: v.tolist() if isinstance(v, np.ndarray) else v 
                                   for k, v in self.user_embeddings.items()}
            }
            success = self.face_repository.save_embeddings_cache(cache_data)
            if success:
                logger.info("Embeddings cache saved successfully")
            else:
                logger.error("Failed to save embeddings cache through repository")
        except Exception as e:
            logger.error(f"Failed to save embeddings cache: {e}")
    
    def _save_database(self):
        """Save user database to file"""
        try:
            # Convert numpy arrays to lists for JSON serialization
            db_to_save = {}
            for user_id, user_data in self.users_db.items():
                db_to_save[user_id] = user_data.copy()
                if 'embeddings' in db_to_save[user_id]:
                    if isinstance(db_to_save[user_id]['embeddings'], np.ndarray):
                        db_to_save[user_id]['embeddings'] = db_to_save[user_id]['embeddings'].tolist()
            
            with open(self.embeddings_file, 'w') as f:
                json.dump(db_to_save, f, indent=2, default=str)
            
            logger.info(f"Database saved successfully with {len(self.users_db)} users")
        except Exception as e:
            logger.error(f"Failed to save database: {e}")
    
    def add_user(self, user_id: str, user_name: str, face_image: np.ndarray, 
                 metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a new user with face image to the database
        
        Args:
            user_id: Unique identifier for the user
            user_name: Display name for the user
            face_image: Face image as numpy array
            metadata: Optional additional user metadata
            
        Returns:
            True if user was added successfully, False otherwise
        """
        try:
            # Extract embeddings from face image
            embeddings = self._extract_embeddings(face_image)
            if embeddings is None:
                logger.error(f"Failed to extract embeddings for user {user_id}")
                return False
            
            # Create user entry
            user_data = {
                'user_id': user_id,
                'user_name': user_name,
                'embeddings': embeddings.tolist(),
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'face_count': 1
            }
            
            # Add metadata if provided
            if metadata:
                user_data.update(metadata)
            
            # Store in database
            self.users_db[user_id] = user_data
            self.user_embeddings[user_id] = embeddings
            
            # Update cache
            embedding_hash = hashlib.md5(embeddings.tobytes()).hexdigest()
            self.embeddings_cache[embedding_hash] = user_id
            
            # Save to disk
            self._save_database()
            self._save_cache()
            
            logger.info(f"User {user_id} ({user_name}) added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add user {user_id}: {e}")
            return False
    
    def remove_user(self, user_id: str) -> bool:
        """
        Remove a user from the database
        
        Args:
            user_id: Unique identifier for the user to remove
            
        Returns:
            True if user was removed successfully, False otherwise
        """
        try:
            if user_id not in self.users_db:
                logger.warning(f"User {user_id} not found in database")
                return False
            
            # Remove from all storage locations
            user_data = self.users_db.pop(user_id)
            if user_id in self.user_embeddings:
                embeddings = self.user_embeddings.pop(user_id)
                # Remove from cache
                embedding_hash = hashlib.md5(embeddings.tobytes()).hexdigest()
                if embedding_hash in self.embeddings_cache:
                    del self.embeddings_cache[embedding_hash]
            
            # Save changes
            self._save_database()
            self._save_cache()
            
            logger.info(f"User {user_id} removed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove user {user_id}: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user information by ID
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            User data dictionary or None if not found
        """
        return self.users_db.get(user_id)
    
    def get_all_users(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve all users from the database
        
        Returns:
            Dictionary mapping user IDs to user data
        """
        return self.users_db.copy()
    
    def find_face(self, face_image: np.ndarray, 
                  confidence_threshold: float = 0.6) -> Optional[Tuple[str, float]]:
        """
        Find a matching face in the database
        
        Args:
            face_image: Face image to search for
            confidence_threshold: Minimum confidence for a match
            
        Returns:
            Tuple of (user_id, confidence_score) or None if no match found
        """
        try:
            # Extract embeddings from input image
            input_embeddings = self._extract_embeddings(face_image)
            if input_embeddings is None:
                return None
            
            best_match = None
            best_confidence = 0.0
            
            # Compare with all stored embeddings
            for user_id, stored_embeddings in self.user_embeddings.items():
                confidence = self._calculate_similarity(input_embeddings, stored_embeddings)
                
                if confidence > best_confidence and confidence >= confidence_threshold:
                    best_confidence = confidence
                    best_match = user_id
            
            if best_match:
                logger.info(f"Face match found: {best_match} with confidence {best_confidence:.3f}")
                return (best_match, best_confidence)
            else:
                logger.info("No face match found above threshold")
                return None
                
        except Exception as e:
            logger.error(f"Error during face search: {e}")
            return None
    
    def update_user_metadata(self, user_id: str, 
                           metadata: Dict[str, Any]) -> bool:
        """
        Update user metadata
        
        Args:
            user_id: Unique identifier for the user
            metadata: New metadata to update
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            if user_id not in self.users_db:
                logger.warning(f"User {user_id} not found for metadata update")
                return False
            
            # Update metadata
            self.users_db[user_id].update(metadata)
            self.users_db[user_id]['last_updated'] = datetime.now().isoformat()
            
            # Save changes
            self._save_database()
            
            logger.info(f"Metadata updated for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update metadata for user {user_id}: {e}")
            return False
    
    def get_user_embeddings(self, user_id: str) -> Optional[np.ndarray]:
        """
        Get face embeddings for a specific user
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Face embeddings as numpy array or None if not found
        """
        return self.user_embeddings.get(user_id)
    
    def backup_database(self, backup_path: Optional[Path] = None) -> bool:
        """
        Create a backup of the database
        
        Args:
            backup_path: Optional path for backup, uses default if None
            
        Returns:
            True if backup was successful, False otherwise
        """
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.backup_dir / f"backup_{timestamp}"
            
            backup_path = Path(backup_path)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup user database
            backup_db_file = backup_path / "faces.json"
            with open(backup_db_file, 'w') as f:
                json.dump(self.users_db, f, indent=2, default=str)
            
            # Backup embeddings cache
            backup_cache_file = backup_path / "embeddings_cache.pkl"
            with open(backup_cache_file, 'wb') as f:
                pickle.dump({
                    'embeddings': self.embeddings_cache,
                    'user_embeddings': {k: v.tolist() if isinstance(v, np.ndarray) else v 
                                       for k, v in self.user_embeddings.items()}
                }, f)
            
            logger.info(f"Database backed up to {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            return False
    
    def restore_database(self, backup_path: Path) -> bool:
        """
        Restore database from backup
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if restore was successful, False otherwise
        """
        try:
            backup_path = Path(backup_path)
            
            # Restore user database
            backup_db_file = backup_path / "faces.json"
            if backup_db_file.exists():
                with open(backup_db_file, 'r') as f:
                    self.users_db = json.load(f)
            
            # Restore embeddings cache
            backup_cache_file = backup_path / "embeddings_cache.pkl"
            if backup_cache_file.exists():
                with open(backup_cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    self.embeddings_cache = cache_data.get('embeddings', {})
                    self.user_embeddings = cache_data.get('user_embeddings', {})
                    # Convert back to numpy arrays
                    for user_id, embeddings in self.user_embeddings.items():
                        if isinstance(embeddings, list):
                            self.user_embeddings[user_id] = np.array(embeddings)
            
            # Save restored data
            self._save_database()
            self._save_cache()
            
            logger.info(f"Database restored from {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore database: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics and health information
        
        Returns:
            Dictionary containing database statistics
        """
        try:
            total_users = len(self.users_db)
            total_embeddings = len(self.embeddings_cache)
            
            # Calculate storage size
            db_size = self.embeddings_file.stat().st_size if self.embeddings_file.exists() else 0
            cache_size = self.embeddings_cache_file.stat().st_size if self.embeddings_cache_file.exists() else 0
            
            stats = {
                'total_users': total_users,
                'total_embeddings': total_embeddings,
                'database_size_bytes': db_size,
                'cache_size_bytes': cache_size,
                'last_updated': datetime.now().isoformat(),
                'data_directory': str(self.data_dir),
                'backup_directory': str(self.backup_dir)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}
    
    def clear_database(self) -> bool:
        """
        Clear all data from the database
        
        Returns:
            True if clear was successful, False otherwise
        """
        try:
            # Clear all data structures
            self.users_db.clear()
            self.embeddings_cache.clear()
            self.user_embeddings.clear()
            
            # Save empty database
            self._save_database()
            self._save_cache()
            
            logger.info("Database cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear database: {e}")
            return False
    
    def is_healthy(self) -> bool:
        """
        Check if the database is in a healthy state
        
        Returns:
            True if database is healthy, False otherwise
        """
        try:
            # Check if data directory exists and is accessible
            if not self.data_dir.exists() or not self.data_dir.is_dir():
                return False
            
            # Check if we can read/write to the directory
            test_file = self.data_dir / "health_check.tmp"
            try:
                test_file.write_text("health_check")
                test_file.unlink()
            except Exception:
                return False
            
            # Check if database files are accessible
            if self.embeddings_file.exists():
                try:
                    with open(self.embeddings_file, 'r') as f:
                        json.load(f)
                except Exception:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _extract_embeddings(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face embeddings from image using DeepFace
        
        Args:
            face_image: Face image as numpy array
            
        Returns:
            Face embeddings as numpy array or None if extraction failed
        """
        try:
            # This is a simplified embedding extraction
            # In a real implementation, you would use DeepFace or similar
            # For now, we'll create a mock embedding
            if face_image is None or face_image.size == 0:
                return None
            
            # Convert to grayscale if needed
            if len(face_image.shape) == 3:
                gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = face_image
            
            # Resize to standard size
            resized = cv2.resize(gray, (128, 128))
            
            # Create a simple feature vector (this is just for demonstration)
            # In practice, you'd use a pre-trained neural network
            features = resized.flatten()[:512]  # Take first 512 pixels as features
            
            # Normalize features
            features = features.astype(np.float32) / 255.0
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to extract embeddings: {e}")
            return None
    
    def _calculate_similarity(self, embeddings1: np.ndarray, embeddings2: np.ndarray) -> float:
        """
        Calculate similarity between two embedding vectors
        
        Args:
            embeddings1: First embedding vector
            embeddings2: Second embedding vector
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        try:
            # Ensure both are numpy arrays
            emb1 = np.array(embeddings1).flatten()
            emb2 = np.array(embeddings2).flatten()
            
            # Calculate cosine similarity
            dot_product = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            
            # Ensure result is between 0 and 1
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def list_faces(self) -> List[Dict[str, Any]]:
        """
        List all faces in the database
        
        Returns:
            List of face data dictionaries
        """
        try:
            users = []
            for user_id, data in self.users_db.items():
                if isinstance(data, dict) and "user_name" in data:
                    users.append({
                        "user_id": user_id,
                        "name": data.get("user_name", "Unknown"),
                        "registration_date": data.get("created_at", "Unknown"),
                        "image_path": data.get("image_path", "Unknown"),
                        "has_embedding": user_id in self.user_embeddings
                    })
            return users
        except Exception as e:
            logger.error(f"Failed to list faces: {e}")
            return []


