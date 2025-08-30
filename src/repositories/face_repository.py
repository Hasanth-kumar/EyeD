"""
Face Repository for EyeD AI Attendance System

This module handles data persistence for face-related operations,
following the Single-Responsibility Principle.
"""

import json
import pickle
import numpy as np
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
import logging
import cv2

logger = logging.getLogger(__name__)


class FaceRepository:
    """Repository for face data persistence"""
    
    def __init__(self, 
                 faces_dir: str = "data/faces",
                 embeddings_file: str = "data/faces/embeddings_cache.pkl"):
        """
        Initialize face repository
        
        Args:
            faces_dir: Directory for face images and metadata
            embeddings_file: File for face embeddings cache
        """
        self.faces_dir = Path(faces_dir)
        self.embeddings_file = Path(embeddings_file)
        
        # Create directories if they don't exist
        self.faces_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize embeddings cache
        self._initialize_embeddings_cache()
        
        logger.info(f"Face repository initialized with directory: {self.faces_dir}")
    
    def _initialize_embeddings_cache(self):
        """Initialize embeddings cache file"""
        if not self.embeddings_file.exists():
            initial_cache = {
                "embeddings": {},
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0",
                    "total_embeddings": 0
                }
            }
            
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(initial_cache, f)
            
            logger.info("Created empty embeddings cache file")
    
    def store_face_image(self, user_id: str, face_image: np.ndarray, 
                        image_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Store a face image for a user
        
        Args:
            user_id: User ID to store image for
            face_image: Face image as numpy array
            image_metadata: Additional metadata for the image
            
        Returns:
            Dictionary with operation result
        """
        try:
            if image_metadata is None:
                image_metadata = {}
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"user_{user_id}_{timestamp}.jpg"
            image_path = self.faces_dir / filename
            
            # Save image
            success = cv2.imwrite(str(image_path), face_image)
            if not success:
                return {
                    'success': False,
                    'error': 'Failed to save face image'
                }
            
            # Store metadata
            metadata = {
                'user_id': user_id,
                'filename': filename,
                'file_path': str(image_path),
                'image_size': face_image.shape,
                'stored_at': datetime.now().isoformat(),
                **image_metadata
            }
            
            # Save metadata to JSON file
            metadata_file = self.faces_dir / f"{filename}.metadata.txt"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Face image stored for user {user_id}: {filename}")
            return {
                'success': True,
                'user_id': user_id,
                'filename': filename,
                'file_path': str(image_path),
                'metadata_file': str(metadata_file),
                'image_size': face_image.shape
            }
            
        except Exception as e:
            logger.error(f"Failed to store face image for user {user_id}: {e}")
            return {
                'success': False,
                'error': f'Failed to store face image: {str(e)}'
            }
    
    def store_face_embeddings(self, user_id: str, embeddings: np.ndarray,
                             embedding_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Store face embeddings for a user
        
        Args:
            user_id: User ID to store embeddings for
            embeddings: Face embeddings as numpy array
            embedding_metadata: Additional metadata for embeddings
            
        Returns:
            Dictionary with operation result
        """
        try:
            if embedding_metadata is None:
                embedding_metadata = {}
            
            # Load existing cache
            with open(self.embeddings_file, 'rb') as f:
                cache = pickle.load(f)
            
            # Store embeddings
            cache['embeddings'][user_id] = {
                'embeddings': embeddings,
                'stored_at': datetime.now().isoformat(),
                'embedding_shape': embeddings.shape,
                **embedding_metadata
            }
            
            # Update metadata
            cache['metadata']['total_embeddings'] = len(cache['embeddings'])
            cache['metadata']['last_updated'] = datetime.now().isoformat()
            
            # Save back to file
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(cache, f)
            
            logger.info(f"Face embeddings stored for user {user_id}")
            return {
                'success': True,
                'user_id': user_id,
                'embeddings_shape': embeddings.shape,
                'total_embeddings_stored': cache['metadata']['total_embeddings']
            }
            
        except Exception as e:
            logger.error(f"Failed to store face embeddings for user {user_id}: {e}")
            return {
                'success': False,
                'error': f'Failed to store face embeddings: {str(e)}'
            }
    
    def get_face_embeddings(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve face embeddings for a user
        
        Args:
            user_id: User ID to retrieve embeddings for
            
        Returns:
            Dictionary with embeddings data
        """
        try:
            # Load embeddings cache
            with open(self.embeddings_file, 'rb') as f:
                cache = pickle.load(f)
            
            # Check if user has embeddings
            if user_id not in cache['embeddings']:
                return {
                    'success': False,
                    'error': f'No embeddings found for user {user_id}'
                }
            
            embedding_data = cache['embeddings'][user_id]
            
            logger.info(f"Face embeddings retrieved for user {user_id}")
            return {
                'success': True,
                'user_id': user_id,
                'embeddings': embedding_data['embeddings'],
                'metadata': embedding_data
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve face embeddings for user {user_id}: {e}")
            return {
                'success': False,
                'error': f'Failed to retrieve face embeddings: {str(e)}'
            }
    
    def get_all_face_embeddings(self) -> Dict[str, Any]:
        """
        Retrieve all face embeddings
        
        Returns:
            Dictionary with all embeddings data
        """
        try:
            # Load embeddings cache
            with open(self.embeddings_file, 'rb') as f:
                cache = pickle.load(f)
            
            embeddings = cache['embeddings']
            
            logger.info(f"Retrieved {len(embeddings)} face embeddings")
            return {
                'success': True,
                'embeddings': embeddings,
                'total_count': len(embeddings),
                'metadata': cache['metadata']
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve all face embeddings: {e}")
            return {
                'success': False,
                'error': f'Failed to retrieve face embeddings: {str(e)}'
            }
    
    def delete_face_data(self, user_id: str) -> Dict[str, Any]:
        """
        Delete all face data for a user
        
        Args:
            user_id: User ID to delete face data for
            
        Returns:
            Dictionary with operation result
        """
        try:
            deleted_files = []
            
            # Delete face images
            for image_file in self.faces_dir.glob(f"user_{user_id}_*.jpg"):
                try:
                    image_file.unlink()
                    deleted_files.append(str(image_file))
                    
                    # Delete corresponding metadata file
                    metadata_file = image_file.with_suffix('.jpg.metadata.txt')
                    if metadata_file.exists():
                        metadata_file.unlink()
                        deleted_files.append(str(metadata_file))
                        
                except Exception as e:
                    logger.warning(f"Failed to delete image file {image_file}: {e}")
            
            # Delete embeddings
            with open(self.embeddings_file, 'rb') as f:
                cache = pickle.load(f)
            
            if user_id in cache['embeddings']:
                del cache['embeddings'][user_id]
                cache['metadata']['total_embeddings'] = len(cache['embeddings'])
                cache['metadata']['last_updated'] = datetime.now().isoformat()
                
                with open(self.embeddings_file, 'wb') as f:
                    pickle.dump(cache, f)
                
                deleted_files.append("embeddings")
            
            logger.info(f"Face data deleted for user {user_id}: {len(deleted_files)} items")
            return {
                'success': True,
                'user_id': user_id,
                'deleted_files': deleted_files,
                'total_deleted': len(deleted_files)
            }
            
        except Exception as e:
            logger.error(f"Failed to delete face data for user {user_id}: {e}")
            return {
                'success': False,
                'error': f'Failed to delete face data: {str(e)}'
            }
    
    def get_face_images(self, user_id: str) -> Dict[str, Any]:
        """
        Get all face images for a user
        
        Args:
            user_id: User ID to get images for
            
        Returns:
            Dictionary with face images data
        """
        try:
            image_files = []
            
            # Find all image files for the user
            for image_file in self.faces_dir.glob(f"user_{user_id}_*.jpg"):
                try:
                    # Load image
                    image = cv2.imread(str(image_file))
                    if image is not None:
                        # Load metadata if available
                        metadata_file = image_file.with_suffix('.jpg.metadata.txt')
                        metadata = {}
                        if metadata_file.exists():
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                        
                        image_files.append({
                            'filename': image_file.name,
                            'file_path': str(image_file),
                            'image': image,
                            'image_size': image.shape,
                            'metadata': metadata
                        })
                        
                except Exception as e:
                    logger.warning(f"Failed to load image file {image_file}: {e}")
            
            logger.info(f"Retrieved {len(image_files)} face images for user {user_id}")
            return {
                'success': True,
                'user_id': user_id,
                'images': image_files,
                'total_count': len(image_files)
            }
            
        except Exception as e:
            logger.error(f"Failed to get face images for user {user_id}: {e}")
            return {
                'success': False,
                'error': f'Failed to get face images: {str(e)}'
            }
    
    def get_face_statistics(self) -> Dict[str, Any]:
        """
        Get face repository statistics
        
        Returns:
            Dictionary with repository statistics
        """
        try:
            # Count image files
            image_files = list(self.faces_dir.glob("*.jpg"))
            total_images = len(image_files)
            
            # Count metadata files
            metadata_files = list(self.faces_dir.glob("*.metadata.txt"))
            total_metadata = len(metadata_files)
            
            # Get embeddings statistics
            with open(self.embeddings_file, 'rb') as f:
                cache = pickle.load(f)
            
            embeddings_count = len(cache['embeddings'])
            
            # Calculate storage size
            total_size = sum(f.stat().st_size for f in image_files)
            total_size_mb = total_size / (1024 * 1024)
            
            # Get user distribution
            users_with_images = set()
            for image_file in image_files:
                # Extract user ID from filename
                parts = image_file.stem.split('_')
                if len(parts) >= 2:
                    users_with_images.add(parts[1])
            
            stats = {
                'total_images': total_images,
                'total_metadata_files': total_metadata,
                'total_embeddings': embeddings_count,
                'users_with_images': len(users_with_images),
                'total_storage_mb': round(total_size_mb, 2),
                'repository_metadata': cache['metadata']
            }
            
            logger.info(f"Face repository statistics generated: {total_images} images, {embeddings_count} embeddings")
            return {
                'success': True,
                'statistics': stats
            }
            
        except Exception as e:
            logger.error(f"Failed to generate face repository statistics: {e}")
            return {
                'success': False,
                'error': f'Failed to generate face repository statistics: {str(e)}'
            }
    
    def backup_face_data(self, backup_name: str = None) -> Dict[str, Any]:
        """
        Create a backup of face data
        
        Args:
            backup_name: Optional name for the backup
            
        Returns:
            Dictionary with backup result
        """
        try:
            if backup_name is None:
                backup_name = f"face_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create backup directory
            backup_dir = self.faces_dir / "backups" / backup_name
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy face images
            images_copied = 0
            for image_file in self.faces_dir.glob("*.jpg"):
                try:
                    import shutil
                    shutil.copy2(image_file, backup_dir / image_file.name)
                    images_copied += 1
                except Exception as e:
                    logger.warning(f"Failed to backup image {image_file}: {e}")
            
            # Copy metadata files
            metadata_copied = 0
            for metadata_file in self.faces_dir.glob("*.metadata.txt"):
                try:
                    import shutil
                    shutil.copy2(metadata_file, backup_dir / metadata_file.name)
                    metadata_copied += 1
                except Exception as e:
                    logger.warning(f"Failed to backup metadata {metadata_file}: {e}")
            
            # Copy embeddings cache
            embeddings_backup_path = backup_dir / "embeddings_cache.pkl"
            import shutil
            shutil.copy2(self.embeddings_file, embeddings_backup_path)
            
            logger.info(f"Face data backed up to {backup_dir}: {images_copied} images, {metadata_copied} metadata files")
            return {
                'success': True,
                'backup_name': backup_name,
                'backup_path': str(backup_dir),
                'images_copied': images_copied,
                'metadata_copied': metadata_copied,
                'embeddings_backed_up': True,
                'backup_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Face data backup failed: {e}")
            return {
                'success': False,
                'error': f'Face data backup failed: {str(e)}'
            }
    
    def cleanup_orphaned_files(self) -> Dict[str, Any]:
        """
        Clean up orphaned files (metadata without images, etc.)
        
        Returns:
            Dictionary with cleanup result
        """
        try:
            cleaned_files = []
            
            # Find orphaned metadata files (no corresponding image)
            for metadata_file in self.faces_dir.glob("*.metadata.txt"):
                # Extract image filename from metadata filename
                image_filename = metadata_file.stem.replace('.metadata', '')
                image_path = self.faces_dir / f"{image_filename}.jpg"
                
                if not image_path.exists():
                    try:
                        metadata_file.unlink()
                        cleaned_files.append(f"orphaned_metadata: {metadata_file.name}")
                    except Exception as e:
                        logger.warning(f"Failed to delete orphaned metadata {metadata_file}: {e}")
            
            # Find orphaned images (no corresponding metadata)
            for image_file in self.faces_dir.glob("*.jpg"):
                metadata_path = image_file.with_suffix('.jpg.metadata.txt')
                
                if not metadata_path.exists():
                    try:
                        image_file.unlink()
                        cleaned_files.append(f"orphaned_image: {image_file.name}")
                    except Exception as e:
                        logger.warning(f"Failed to delete orphaned image {image_file}: {e}")
            
            logger.info(f"Face data cleanup completed: {len(cleaned_files)} files cleaned")
            return {
                'success': True,
                'cleaned_files': cleaned_files,
                'total_cleaned': len(cleaned_files)
            }
            
        except Exception as e:
            logger.error(f"Face data cleanup failed: {e}")
            return {
                'success': False,
                'error': f'Face data cleanup failed: {str(e)}'
            }
    
    def validate_face_data_integrity(self) -> Dict[str, Any]:
        """
        Validate integrity of face data
        
        Returns:
            Dictionary with validation results
        """
        try:
            validation_results = {
                'total_images': 0,
                'total_metadata': 0,
                'total_embeddings': 0,
                'orphaned_files': [],
                'corrupted_files': [],
                'validation_passed': True
            }
            
            # Validate images
            for image_file in self.faces_dir.glob("*.jpg"):
                validation_results['total_images'] += 1
                
                try:
                    # Try to load image
                    image = cv2.imread(str(image_file))
                    if image is None:
                        validation_results['corrupted_files'].append(f"corrupted_image: {image_file.name}")
                        validation_results['validation_passed'] = False
                except Exception as e:
                    validation_results['corrupted_files'].append(f"unreadable_image: {image_file.name}")
                    validation_results['validation_passed'] = False
            
            # Validate metadata files
            for metadata_file in self.faces_dir.glob("*.metadata.txt"):
                validation_results['total_metadata'] += 1
                
                try:
                    with open(metadata_file, 'r') as f:
                        json.load(f)
                except Exception as e:
                    validation_results['corrupted_files'].append(f"corrupted_metadata: {metadata_file.name}")
                    validation_results['validation_passed'] = False
            
            # Validate embeddings
            try:
                with open(self.embeddings_file, 'rb') as f:
                    cache = pickle.load(f)
                validation_results['total_embeddings'] = len(cache['embeddings'])
            except Exception as e:
                validation_results['corrupted_files'].append(f"corrupted_embeddings_cache")
                validation_results['validation_passed'] = False
            
            # Check for orphaned files
            orphaned_check = self.cleanup_orphaned_files()
            if orphaned_check['success']:
                validation_results['orphaned_files'] = orphaned_check['cleaned_files']
            
            logger.info(f"Face data integrity validation completed: {'PASSED' if validation_results['validation_passed'] else 'FAILED'}")
            return {
                'success': True,
                'validation_results': validation_results
            }
            
        except Exception as e:
            logger.error(f"Face data integrity validation failed: {e}")
            return {
                'success': False,
                'error': f'Face data integrity validation failed: {str(e)}'
            }
    
    def is_healthy(self) -> bool:
        """Check if repository is healthy"""
        try:
            # Test file access
            test_data = self.get_face_metadata()
            return True
        except Exception as e:
            logger.error(f"Repository health check failed: {e}")
            return False
    
    def save_face_data(self, user_id: str, face_data: Dict[str, Any]) -> bool:
        """
        Save face data for a user
        
        Args:
            user_id: User ID
            face_data: Face data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load existing data
            if self.embeddings_file.exists():
                with open(self.embeddings_file, 'rb') as f:
                    cache_data = pickle.load(f)
            else:
                cache_data = {"embeddings": {}, "metadata": {}}
            
            # Update user data
            cache_data["embeddings"][user_id] = face_data
            
            # Save back to file
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            logger.info(f"Face data saved for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save face data for user {user_id}: {e}")
            return False
    
    def load_face_data(self) -> Dict[str, Any]:
        """
        Load all face data
        
        Returns:
            Dictionary containing all face data
        """
        try:
            if not self.embeddings_file.exists():
                return {}
            
            with open(self.embeddings_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            logger.info(f"Loaded face data for {len(cache_data.get('embeddings', {}))} users")
            return cache_data
            
        except Exception as e:
            logger.error(f"Failed to load face data: {e}")
            return {}
    
    def save_embeddings_cache(self, cache_data: Dict[str, Any]) -> bool:
        """
        Save embeddings cache
        
        Args:
            cache_data: Cache data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            logger.info("Embeddings cache saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save embeddings cache: {e}")
            return False
    
    def load_embeddings_cache(self) -> Dict[str, Any]:
        """
        Load embeddings cache
        
        Returns:
            Cache data dictionary
        """
        try:
            if not self.embeddings_file.exists():
                return {}
            
            with open(self.embeddings_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            logger.info("Embeddings cache loaded successfully")
            return cache_data
            
        except Exception as e:
            logger.error(f"Failed to load embeddings cache: {e}")
            return {}
    
    def create_backup(self, backup_path: str) -> bool:
        """
        Create backup of face data
        
        Args:
            backup_path: Path for backup
            
        Returns:
            True if successful, False otherwise
        """
        try:
            backup_path = Path(backup_path)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup main data file
            backup_db_file = backup_path / "faces_backup.json"
            faces_json_file = self.faces_dir / "faces.json"
            if faces_json_file.exists():
                import shutil
                shutil.copy2(faces_json_file, backup_db_file)
            
            # Backup cache file
            backup_cache_file = backup_path / "embeddings_cache_backup.pkl"
            if self.embeddings_file.exists():
                import shutil
                shutil.copy2(self.embeddings_file, backup_cache_file)
            
            logger.info(f"Face data backup created at {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create face data backup: {e}")
            return False
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """
        Restore face data from backup
        
        Args:
            backup_path: Path to backup
            
        Returns:
            True if successful, False otherwise
        """
        try:
            backup_path = Path(backup_path)
            
            # Restore main data file
            backup_db_file = backup_path / "faces_backup.json"
            faces_json_file = self.faces_dir / "faces.json"
            if backup_db_file.exists():
                import shutil
                shutil.copy2(backup_db_file, faces_json_file)
            
            # Restore cache file
            backup_cache_file = backup_path / "embeddings_cache_backup.pkl"
            if backup_cache_file.exists():
                import shutil
                shutil.copy2(backup_cache_file, self.embeddings_file)
            
            logger.info(f"Face data restored from backup at {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore face data from backup: {e}")
            return False
