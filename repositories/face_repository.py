"""
Face Repository for EyeD AI Attendance System

This module handles data persistence for face images and embeddings,
following the Single-Responsibility Principle and Dependency Injection.

This repository works with the FaceEmbedding domain entity and uses
FileStorage for all file operations.
"""

import pickle
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

import numpy as np
import cv2

from domain.entities.face_embedding import FaceEmbedding
from domain.shared.exceptions import DomainException
from infrastructure.storage.file_storage import FileStorage

logger = logging.getLogger(__name__)


class FaceRepository:
    """
    Repository for face data persistence.
    
    This class handles ONLY face data persistence (images and embeddings).
    It uses dependency injection for file operations and works with
    domain entities (FaceEmbedding).
    """
    
    def __init__(
        self,
        file_storage: FileStorage,
        faces_dir: str = "data/faces",
        embeddings_file: str = "data/faces/embeddings_cache.pkl",
        faces_json_file: str = "data/faces/faces.json"
    ):
        """
        Initialize face repository.
        
        Args:
            file_storage: Injected file storage handler for file operations
            faces_dir: Directory for face images
            embeddings_file: Path to embeddings cache (pickle format) - for backward compatibility
            faces_json_file: Path to faces.json file (contains legacy format embeddings)
        """
        if file_storage is None:
            raise ValueError("file_storage cannot be None")
        
        self.file_storage = file_storage
        self.faces_dir = faces_dir
        self.embeddings_file = embeddings_file
        self.faces_json_file = faces_json_file
        
        # Ensure directories exist
        if not self.file_storage.directory_exists(self.faces_dir):
            if not self.file_storage.create_directory(self.faces_dir):
                logger.warning(f"Failed to create faces directory: {self.faces_dir}")
        
        # Initialize embeddings cache if it doesn't exist
        self._initialize_embeddings_cache()
        
        logger.info(f"FaceRepository initialized with faces_dir: {self.faces_dir}, embeddings_file: {self.embeddings_file}, faces_json_file: {self.faces_json_file}")
    
    def _initialize_embeddings_cache(self) -> None:
        """Initialize embeddings cache file if it doesn't exist."""
        if not self.file_storage.file_exists(self.embeddings_file):
            initial_cache = {
                "embeddings": {},
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0",
                    "total_embeddings": 0
                }
            }
            
            # Serialize to bytes
            cache_bytes = pickle.dumps(initial_cache)
            
            # Write using FileStorage
            if self.file_storage.write_file(self.embeddings_file, cache_bytes):
                logger.info("Created empty embeddings cache file")
            else:
                logger.error("Failed to create embeddings cache file")
    
    def _normalize_cache_structure(self, cache: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure cache has expected structure (handles old format migration).
        
        Args:
            cache: Cache dictionary loaded from file
            
        Returns:
            Normalized cache dictionary with required keys
        """
        if "embeddings" not in cache:
            cache["embeddings"] = {}
        if "metadata" not in cache:
            cache["metadata"] = {
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "total_embeddings": len(cache.get("embeddings", {}))
            }
        return cache
    
    def store_face_image(
        self,
        user_id: str,
        face_image: np.ndarray,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Store face image file.
        
        Args:
            user_id: ID of the user
            face_image: Face image as numpy array
            metadata: Optional metadata dictionary
        
        Returns:
            File path on success
        
        Raises:
            DomainException: If storage fails
        """
        if user_id is None or user_id.strip() == "":
            raise ValueError("user_id cannot be None or empty")
        
        if face_image is None or not isinstance(face_image, np.ndarray):
            raise ValueError("face_image must be a numpy array")
        
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"user_{user_id}_{timestamp}.jpg"
            image_path = str(Path(self.faces_dir) / filename)
            
            # Encode numpy array to JPG bytes
            success, encoded_image = cv2.imencode('.jpg', face_image)
            if not success:
                error_msg = f"Failed to encode face image for user {user_id}"
                logger.error(error_msg)
                raise DomainException(error_msg, "IMAGE_ENCODING_FAILED")
            
            image_bytes = encoded_image.tobytes()
            
            # Store using FileStorage
            if not self.file_storage.write_file(image_path, image_bytes):
                error_msg = f"Failed to store face image for user {user_id}"
                logger.error(error_msg)
                raise DomainException(error_msg, "IMAGE_STORAGE_FAILED")
            
            logger.info(f"Face image stored for user {user_id}: {image_path}")
            return image_path
            
        except DomainException:
            raise
        except Exception as e:
            error_msg = f"Unexpected error storing face image for user {user_id}: {str(e)}"
            logger.error(error_msg)
            raise DomainException(error_msg, "IMAGE_STORAGE_ERROR") from e
    
    def get_face_image(self, user_id: str, image_path: str) -> Optional[np.ndarray]:
        """
        Retrieve face image by path.
        
        Args:
            user_id: ID of the user
            image_path: Path to the image file
        
        Returns:
            Numpy array with image data, or None if not found
        """
        if user_id is None or user_id.strip() == "":
            logger.warning("get_face_image called with empty user_id")
            return None
        
        if image_path is None or image_path.strip() == "":
            logger.warning("get_face_image called with empty image_path")
            return None
        
        try:
            # Read file using FileStorage
            if not self.file_storage.file_exists(image_path):
                logger.warning(f"Face image not found: {image_path}")
                return None
            
            image_bytes = self.file_storage.read_file(image_path)
            
            # Decode bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                logger.warning(f"Failed to decode image: {image_path}")
                return None
            
            logger.debug(f"Face image retrieved for user {user_id}: {image_path}")
            return image
            
        except FileNotFoundError:
            logger.warning(f"Face image not found: {image_path}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving face image {image_path}: {e}")
            return None
    
    def store_face_embeddings(
        self,
        user_id: str,
        embeddings: np.ndarray,
        embedding_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store face embeddings in legacy format (faces.json).
        
        Args:
            user_id: ID of the user
            embeddings: Face embedding as numpy array
            embedding_metadata: Optional metadata dictionary (may contain:
                - 'quality_score': float
                - 'created_at': str or datetime
                - 'image_path': str (filename only, e.g., "user_id_Name.jpg")
                - 'face_bbox': list [x, y, width, height] or None
                - 'name': str (full name for legacy format)
        
        Returns:
            Dictionary with 'success' (bool) key, and optionally 'error' (str) key
        """
        if user_id is None or user_id.strip() == "":
            return {
                "success": False,
                "error": "user_id cannot be None or empty"
            }
        
        if embeddings is None or not isinstance(embeddings, np.ndarray):
            return {
                "success": False,
                "error": "embeddings must be a numpy array"
            }
        
        try:
            # Load existing faces.json
            if self.file_storage.file_exists(self.faces_json_file):
                content = self.file_storage.read_text_file(self.faces_json_file)
                data = json.loads(content)
            else:
                data = {"metadata": {}}
            
            # Ensure user entry exists (create if not)
            if user_id not in data:
                data[user_id] = {}
            
            # Convert numpy array to list for JSON storage
            embedding_list = embeddings.tolist()
            
            # Update user entry with embedding
            data[user_id]["embedding"] = embedding_list
            
            # Update name if provided (for legacy format)
            if embedding_metadata and "name" in embedding_metadata:
                data[user_id]["name"] = embedding_metadata["name"]
            
            # Update image_path if provided
            if embedding_metadata and "image_path" in embedding_metadata:
                # Store just the filename, not full path
                image_path = embedding_metadata["image_path"]
                if isinstance(image_path, str):
                    # Extract just filename if full path provided
                    filename = Path(image_path).name
                    data[user_id]["image_path"] = filename
                else:
                    data[user_id]["image_path"] = str(image_path)
            
            # Update face_bbox if provided
            if embedding_metadata and "face_bbox" in embedding_metadata:
                face_bbox = embedding_metadata["face_bbox"]
                if face_bbox is not None:
                    data[user_id]["face_bbox"] = face_bbox
            
            # Update registration_date if provided
            if embedding_metadata and "created_at" in embedding_metadata:
                created_at_str = embedding_metadata["created_at"]
                if isinstance(created_at_str, str):
                    data[user_id]["registration_date"] = created_at_str
                elif isinstance(created_at_str, datetime):
                    data[user_id]["registration_date"] = created_at_str.isoformat()
            elif "registration_date" not in data[user_id]:
                data[user_id]["registration_date"] = datetime.now().isoformat()
            
            # Ensure metadata exists
            if "metadata" not in data:
                data["metadata"] = {}
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Save to faces.json
            json_content = json.dumps(data, indent=2, default=str)
            if self.file_storage.write_text_file(self.faces_json_file, json_content):
                logger.info(f"Face embedding stored for user {user_id} in legacy format")
                return {
                    "success": True
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to save face embedding to faces.json"
                }
            
        except Exception as e:
            logger.error(f"Error storing face embeddings for user {user_id}: {e}")
            return {
                "success": False,
                "error": f"Failed to store face embeddings: {str(e)}"
            }
    
    def store_face_embedding(
        self,
        user_id: str,
        embedding: FaceEmbedding
    ) -> bool:
        """
        Store face embedding.
        
        Args:
            user_id: ID of the user
            embedding: FaceEmbedding domain entity
        
        Returns:
            True on success, False on failure
        """
        if user_id is None or user_id.strip() == "":
            logger.error("store_face_embedding called with empty user_id")
            return False
        
        if embedding is None:
            logger.error("store_face_embedding called with None embedding")
            return False
        
        if embedding.user_id != user_id:
            logger.warning(f"Embedding user_id ({embedding.user_id}) doesn't match provided user_id ({user_id})")
        
        try:
            # Load existing cache
            if not self.file_storage.file_exists(self.embeddings_file):
                self._initialize_embeddings_cache()
            
            cache_bytes = self.file_storage.read_file(self.embeddings_file)
            cache = pickle.loads(cache_bytes)
            
            # Ensure cache has expected structure (handle old format)
            cache = self._normalize_cache_structure(cache)
            
            # Convert FaceEmbedding entity to storage format
            embedding_data = {
                "embedding": embedding.embedding,
                "quality_score": embedding.quality_score,
                "created_at": embedding.created_at.isoformat(),
                "user_id": embedding.user_id
            }
            
            # Store embedding
            cache["embeddings"][user_id] = embedding_data
            
            # Update metadata
            cache["metadata"]["total_embeddings"] = len(cache["embeddings"])
            cache["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Save back using FileStorage
            updated_cache_bytes = pickle.dumps(cache)
            if not self.file_storage.write_file(self.embeddings_file, updated_cache_bytes):
                logger.error(f"Failed to write embeddings cache for user {user_id}")
                return False
            
            logger.info(f"Face embedding stored for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing face embedding for user {user_id}: {e}")
            return False
    
    def get_face_embedding(self, user_id: str) -> Optional[FaceEmbedding]:
        """
        Retrieve face embedding for user from legacy format or pickle cache.
        
        Args:
            user_id: ID of the user
        
        Returns:
            FaceEmbedding entity or None if not found
        """
        if user_id is None or user_id.strip() == "":
            logger.warning("get_face_embedding called with empty user_id")
            return None
        
        try:
            # Check legacy format first (faces.json)
            if self.file_storage.file_exists(self.faces_json_file):
                content = self.file_storage.read_text_file(self.faces_json_file)
                data = json.loads(content)
                
                if user_id in data and isinstance(data[user_id], dict):
                    user_data = data[user_id]
                    if "embedding" in user_data and "name" in user_data:
                        try:
                            embedding_list = user_data["embedding"]
                            if isinstance(embedding_list, list):
                                embedding_array = np.array(embedding_list, dtype=np.float32)
                                
                                registration_date = user_data.get("registration_date")
                                if isinstance(registration_date, str):
                                    try:
                                        created_at = datetime.fromisoformat(registration_date)
                                    except ValueError:
                                        created_at = datetime.now()
                                else:
                                    created_at = datetime.now()
                                
                                embedding = FaceEmbedding(
                                    user_id=user_id,
                                    embedding=embedding_array,
                                    quality_score=0.0,  # Legacy format default
                                    created_at=created_at
                                )
                                
                                logger.debug(f"Face embedding retrieved for user {user_id} from legacy format")
                                return embedding
                        except Exception as e:
                            logger.warning(f"Error loading legacy embedding for user {user_id}: {e}")
            
            # Fallback to pickle cache
            if self.file_storage.file_exists(self.embeddings_file):
                cache_bytes = self.file_storage.read_file(self.embeddings_file)
                cache = pickle.loads(cache_bytes)
                
                if user_id in cache.get("embeddings", {}):
                    embedding_data = cache["embeddings"][user_id]
                    
                    embedding = FaceEmbedding(
                        user_id=embedding_data.get("user_id", user_id),
                        embedding=embedding_data["embedding"],
                        quality_score=embedding_data["quality_score"],
                        created_at=datetime.fromisoformat(embedding_data["created_at"])
                    )
                    
                    logger.debug(f"Face embedding retrieved for user {user_id} from pickle cache")
                    return embedding
            
            logger.debug(f"No embeddings found for user {user_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving face embedding for user {user_id}: {e}")
            return None
    
    def _load_legacy_embeddings_from_json(self) -> Dict[str, FaceEmbedding]:
        """
        Load embeddings from legacy format in faces.json.
        
        Returns:
            Dictionary mapping user_id to FaceEmbedding entities
        """
        embeddings = {}
        
        try:
            if not self.file_storage.file_exists(self.faces_json_file):
                logger.debug(f"Faces JSON file not found: {self.faces_json_file}")
                return {}
            
            content = self.file_storage.read_text_file(self.faces_json_file)
            data = json.loads(content)
            
            # Iterate through top-level keys (legacy format users)
            for user_id, user_data in data.items():
                if user_id in ["users", "metadata"]:
                    continue
                
                if not isinstance(user_data, dict):
                    continue
                
                # Check if this is a legacy user with embedding
                if "embedding" in user_data and "name" in user_data:
                    try:
                        embedding_list = user_data["embedding"]
                        if not isinstance(embedding_list, list):
                            continue
                        
                        # Convert list to numpy array
                        embedding_array = np.array(embedding_list, dtype=np.float32)
                        
                        # Parse registration_date for created_at
                        registration_date = user_data.get("registration_date")
                        if isinstance(registration_date, str):
                            try:
                                created_at = datetime.fromisoformat(registration_date)
                            except ValueError:
                                created_at = datetime.now()
                        else:
                            created_at = datetime.now()
                        
                        # Legacy format doesn't have quality_score, default to 0.0
                        quality_score = 0.0
                        
                        # Create FaceEmbedding entity
                        face_embedding = FaceEmbedding(
                            user_id=user_id,
                            embedding=embedding_array,
                            quality_score=quality_score,
                            created_at=created_at
                        )
                        embeddings[user_id] = face_embedding
                        
                    except Exception as e:
                        logger.warning(f"Error loading legacy embedding for user {user_id}: {e}")
                        continue
            
            logger.debug(f"Loaded {len(embeddings)} embeddings from legacy format")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error loading legacy embeddings from JSON: {e}")
            return {}
    
    def get_all_face_embeddings(self) -> Dict[str, FaceEmbedding]:
        """
        Retrieve all face embeddings from legacy format (faces.json) and pickle cache.
        
        Returns:
            Dictionary mapping user_id to FaceEmbedding entities
        """
        embeddings = {}
        
        # Load from legacy format (faces.json) - primary source
        legacy_embeddings = self._load_legacy_embeddings_from_json()
        embeddings.update(legacy_embeddings)
        
        # Load from pickle cache (for backward compatibility)
        try:
            if self.file_storage.file_exists(self.embeddings_file):
                cache_bytes = self.file_storage.read_file(self.embeddings_file)
                cache = pickle.loads(cache_bytes)
                
                for user_id, embedding_data in cache.get("embeddings", {}).items():
                    # Skip if already loaded from legacy format
                    if user_id in embeddings:
                        continue
                    
                    try:
                        # Handle different pickle cache formats
                        if isinstance(embedding_data, dict):
                            # Standard format with metadata
                            embedding = FaceEmbedding(
                                user_id=embedding_data.get("user_id", user_id),
                                embedding=embedding_data["embedding"],
                                quality_score=embedding_data.get("quality_score", 0.0),
                                created_at=datetime.fromisoformat(embedding_data.get("created_at", datetime.now().isoformat()))
                            )
                        elif isinstance(embedding_data, np.ndarray):
                            # Direct numpy array format (old format)
                            embedding = FaceEmbedding(
                                user_id=user_id,
                                embedding=embedding_data,
                                quality_score=0.0,
                                created_at=datetime.now()
                            )
                        else:
                            logger.warning(f"Unknown embedding format for user {user_id}: {type(embedding_data)}")
                            continue
                        
                        embeddings[user_id] = embedding
                    except Exception as e:
                        logger.warning(f"Error converting embedding for user {user_id}: {e}")
                        continue
        except Exception as e:
            logger.warning(f"Error loading embeddings from pickle cache: {e}")
        
        logger.info(f"Retrieved {len(embeddings)} face embeddings (legacy + cache)")
        return embeddings
    
    def delete_face_data(self, user_id: str) -> bool:
        """
        Delete all face data for a user (images and embeddings).
        
        Args:
            user_id: ID of the user
        
        Returns:
            True on success, False on failure
        """
        if user_id is None or user_id.strip() == "":
            logger.warning("delete_face_data called with empty user_id")
            return False
        
        try:
            deleted_count = 0
            
            # Delete face images
            image_paths = self.get_face_images(user_id)
            for image_path in image_paths:
                if self.file_storage.delete_file(image_path):
                    deleted_count += 1
                    logger.debug(f"Deleted face image: {image_path}")
                else:
                    logger.warning(f"Failed to delete face image: {image_path}")
            
            # Delete embedding from cache
            if self.file_storage.file_exists(self.embeddings_file):
                cache_bytes = self.file_storage.read_file(self.embeddings_file)
                cache = pickle.loads(cache_bytes)
                
                # Ensure cache has expected structure (handle old format)
                cache = self._normalize_cache_structure(cache)
                
                if user_id in cache.get("embeddings", {}):
                    del cache["embeddings"][user_id]
                    cache["metadata"]["total_embeddings"] = len(cache["embeddings"])
                    cache["metadata"]["last_updated"] = datetime.now().isoformat()
                    
                    # Save updated cache
                    updated_cache_bytes = pickle.dumps(cache)
                    if self.file_storage.write_file(self.embeddings_file, updated_cache_bytes):
                        deleted_count += 1
                        logger.debug(f"Deleted embedding for user {user_id}")
            
            if deleted_count > 0:
                logger.info(f"Deleted {deleted_count} items for user {user_id}")
                return True
            else:
                logger.warning(f"No face data found to delete for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting face data for user {user_id}: {e}")
            return False
    
    def get_face_images(self, user_id: str) -> List[str]:
        """
        Get list of face image paths for a user.
        
        Args:
            user_id: ID of the user
        
        Returns:
            List of file paths
        """
        if user_id is None or user_id.strip() == "":
            logger.warning("get_face_images called with empty user_id")
            return []
        
        try:
            # List files in faces directory
            pattern = f"user_{user_id}_*.jpg"
            files = self.file_storage.list_files(self.faces_dir, pattern)
            
            # Filter to only JPG files and return full paths
            image_paths = [
                str(Path(self.faces_dir) / Path(f).name)
                for f in files
                if f.endswith('.jpg')
            ]
            
            logger.debug(f"Found {len(image_paths)} face images for user {user_id}")
            return image_paths
            
        except Exception as e:
            logger.error(f"Error getting face images for user {user_id}: {e}")
            return []


