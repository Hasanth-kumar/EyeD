"""
Refactored Face Database System

This module orchestrates face database operations using focused components,
following the Single-Responsibility Principle.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging

from .face_storage import FaceStorage
from .embedding_manager import EmbeddingManager
from .face_validator import FaceValidator
from .backup_manager import BackupManager

# Import interface
try:
    from ...interfaces.face_database_interface import FaceDatabaseInterface
except ImportError:
    # Fallback to absolute imports for testing
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))
    from interfaces.face_database_interface import FaceDatabaseInterface

logger = logging.getLogger(__name__)


class FaceDatabase(FaceDatabaseInterface):
    """Orchestrates face database operations using focused components"""
    
    def __init__(self, data_dir: str = "data/faces"):
        """
        Initialize face database with focused components
        
        Args:
            data_dir: Directory for face data storage
        """
        # Initialize focused components
        self.face_storage = FaceStorage(data_dir)
        self.embedding_manager = EmbeddingManager(f"{data_dir}/embeddings_cache.pkl")
        self.face_validator = FaceValidator()
        self.backup_manager = BackupManager(f"{data_dir}/backups")
        
        logger.info("Refactored Face Database System initialized successfully")
    
    def add_face(self, user_id: str, name: str, image_path: str, 
                 embedding: Any = None) -> bool:
        """
        Add a face to the database using focused components
        
        Args:
            user_id: Unique user identifier
            name: User's name
            image_path: Path to face image
            embedding: Optional face embedding
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate user ID
            is_valid_id, error_msg = self.face_validator.validate_user_id(user_id)
            if not is_valid_id:
                logger.error(f"Invalid user ID: {error_msg}")
                return False
            
            # Prepare face data
            face_data = {
                'user_id': user_id,
                'name': name,
                'image_path': image_path,
                'added_date': '2025-01-01'  # Would be actual date in real implementation
            }
            
            # Validate face data
            is_valid_data, error_msg = self.face_validator.validate_face_data(face_data)
            if not is_valid_data:
                logger.error(f"Invalid face data: {error_msg}")
                return False
            
            # Save face data using storage component
            if not self.face_storage.save_face_data(face_data):
                logger.error("Failed to save face data")
                return False
            
            # Save embedding if provided
            if embedding is not None:
                if not self.embedding_manager.add_embedding(user_id, embedding):
                    logger.warning(f"Failed to save embedding for user {user_id}")
            
            logger.info(f"Face added successfully for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding face: {e}")
            return False
    
    def get_face(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get face data for a specific user
        
        Args:
            user_id: User ID to retrieve
            
        Returns:
            Face data dictionary or None if not found
        """
        try:
            # Get face data from storage
            face_data = self.face_storage.get_face_data(user_id)
            if not face_data:
                return None
            
            # Get embedding if available
            embedding = self.embedding_manager.get_embedding(user_id)
            if embedding:
                face_data['embedding'] = embedding
            
            return face_data
            
        except Exception as e:
            logger.error(f"Error getting face: {e}")
            return None
    
    def remove_face(self, user_id: str) -> bool:
        """
        Remove a face from the database
        
        Args:
            user_id: User ID to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove face data
            if not self.face_storage.delete_face_data(user_id):
                logger.error(f"Failed to remove face data for user {user_id}")
                return False
            
            # Remove embedding
            if not self.embedding_manager.remove_embedding(user_id):
                logger.warning(f"Failed to remove embedding for user {user_id}")
            
            logger.info(f"Face removed successfully for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing face: {e}")
            return False
    
    def list_faces(self) -> List[Dict[str, Any]]:
        """
        List all faces in the database
        
        Returns:
            List of face data dictionaries
        """
        try:
            faces = self.face_storage.list_all_faces()
            
            # Add embeddings to face data
            for face in faces:
                user_id = face.get('user_id')
                if user_id:
                    embedding = self.embedding_manager.get_embedding(user_id)
                    if embedding:
                        face['has_embedding'] = True
                    else:
                        face['has_embedding'] = False
            
            return faces
            
        except Exception as e:
            logger.error(f"Error listing faces: {e}")
            return []
    
    def create_backup(self, backup_name: str = None) -> str:
        """
        Create a backup of the face database
        
        Args:
            backup_name: Optional custom backup name
            
        Returns:
            Path to created backup
        """
        try:
            # Get files to backup
            source_files = [
                str(self.face_storage.faces_file),
                str(self.embedding_manager.cache_file)
            ]
            
            # Create backup using backup manager
            backup_path = self.backup_manager.create_backup(source_files, backup_name)
            
            if backup_path:
                logger.info(f"Face database backup created: {backup_path}")
                return backup_path
            else:
                logger.error("Failed to create backup")
                return ""
                
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return ""
    
    def restore_backup(self, backup_path: str) -> bool:
        """
        Restore face database from backup
        
        Args:
            backup_path: Path to backup directory
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Restore backup using backup manager
            success = self.backup_manager.restore_backup(backup_path)
            
            if success:
                logger.info(f"Face database restored from backup: {backup_path}")
                return True
            else:
                logger.error("Failed to restore backup")
                return False
                
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False
    
    def is_healthy(self) -> bool:
        """Check if the face database system is healthy"""
        try:
            # Check all components
            storage_healthy = self.face_storage.is_healthy()
            embedding_healthy = self.embedding_manager.is_healthy()
            
            return storage_healthy and embedding_healthy
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            faces = self.list_faces()
            embeddings = self.embedding_manager.list_embeddings()
            backups = self.backup_manager.list_backups()
            
            return {
                'total_faces': len(faces),
                'faces_with_embeddings': len(embeddings),
                'total_backups': len(backups),
                'storage_healthy': self.face_storage.is_healthy(),
                'embedding_healthy': self.embedding_manager.is_healthy()
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
