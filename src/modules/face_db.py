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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceDatabase:
    """
    Efficient Face Embedding Database for EyeD AI Attendance System
    
    Features:
    - Optimized embedding storage and retrieval
    - User metadata management
    - Search and query functions
    - Memory-efficient operations
    - Backup and recovery mechanisms
    """
    
    def __init__(self, data_dir: str = "data/faces"):
        """
        Initialize Face Database
        
        Args:
            data_dir: Directory to store face data and embeddings
        """
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
            if 'embedding' in user_data:
                embedding = np.array(user_data['embedding'])
                self.embeddings_cache[user_id] = embedding
                self.user_embeddings[user_id] = user_data
        
        logger.info(f"Cache rebuilt with {len(self.embeddings_cache)} embeddings")
        self._save_cache()
    
    def _save_cache(self):
        """Save embeddings cache to file"""
        try:
            cache_data = {
                'embeddings': self.embeddings_cache,
                'user_embeddings': self.user_embeddings,
                'timestamp': datetime.now().isoformat()
            }
            with open(self.embeddings_cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            logger.debug("Embeddings cache saved")
        except Exception as e:
            logger.error(f"Failed to save embeddings cache: {e}")
    
    def _save_database(self):
        """Save user database to JSON file"""
        try:
            with open(self.embeddings_file, 'w') as f:
                json.dump(self.users_db, f, indent=2)
            logger.debug("User database saved")
        except Exception as e:
            logger.error(f"Failed to save user database: {e}")
    
    def register_user(self, name: str, user_id: str, image: np.ndarray, metadata: Optional[Dict] = None) -> bool:
        """
        Register a new user with face image and metadata
        
        Args:
            name: User's full name
            user_id: Unique user identifier
            image: Face image as numpy array
            metadata: Additional user metadata (optional)
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        try:
            # Check if user already exists
            if user_id in self.users_db:
                logger.warning(f"User {user_id} already exists. Updating information.")
            
            # Generate face embedding
            embedding = self._generate_embedding(image)
            if embedding is None:
                logger.error(f"Failed to generate embedding for user {user_id}")
                return False
            
            # Prepare user data
            user_data = {
                'name': name,
                'user_id': user_id,
                'registration_date': datetime.now().isoformat(),
                'status': 'active',
                'embedding': embedding.tolist(),
                'last_updated': datetime.now().isoformat()
            }
            
            # Add metadata if provided
            if metadata:
                user_data.update(metadata)
            
            # Save image to disk
            image_path = self._save_user_image(user_id, image)
            if image_path:
                user_data['image_path'] = str(image_path)
            
            # Store in database
            self.users_db[user_id] = user_data
            
            # Update embeddings cache
            self.embeddings_cache[user_id] = embedding
            self.user_embeddings[user_id] = embedding
            
            # Save to disk
            self._save_database()
            
            logger.info(f"User {name} ({user_id}) registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register user {user_id}: {e}")
            return False
    
    def load_embeddings(self) -> Dict[str, np.ndarray]:
        """
        Load all face embeddings into memory
        
        Returns:
            Dict mapping user_id to embedding array
        """
        try:
            # Ensure cache is up to date
            if not self.embeddings_cache:
                self._rebuild_cache()
            
            logger.info(f"Loaded {len(self.embeddings_cache)} embeddings into memory")
            return self.embeddings_cache.copy()
            
        except Exception as e:
            logger.error(f"Failed to load embeddings: {e}")
            return {}
    
    def get_user_embedding(self, user_id: str) -> Optional[np.ndarray]:
        """
        Get embedding for specific user
        
        Args:
            user_id: User identifier
            
        Returns:
            Embedding array or None if not found
        """
        return self.embeddings_cache.get(user_id)
    
    def get_user_data(self, user_id: str) -> Optional[Dict]:
        """
        Get complete user data
        
        Args:
            user_id: User identifier
            
        Returns:
            User data dictionary or None if not found
        """
        return self.user_embeddings.get(user_id)
    
    def search_users(self, query: str) -> List[Dict]:
        """
        Search users by name or ID
        
        Args:
            query: Search query string
            
        Returns:
            List of matching user data
        """
        results = []
        query_lower = query.lower()
        
        for user_id, user_data in self.users_db.items():
            if (query_lower in user_data.get('name', '').lower() or 
                query_lower in user_id.lower()):
                results.append(user_data)
        
        return results
    
    def update_user(self, user_id: str, updates: Dict) -> bool:
        """
        Update user information
        
        Args:
            user_id: User identifier
            updates: Dictionary of fields to update
            
        Returns:
            bool: True if update successful
        """
        try:
            if user_id not in self.users_db:
                logger.error(f"User {user_id} not found")
                return False
            
            # Update user data
            self.users_db[user_id].update(updates)
            self.users_db[user_id]['last_updated'] = datetime.now().isoformat()
            
            # Update cache if embedding changed
            if 'embedding' in updates:
                self.embeddings_cache[user_id] = np.array(updates['embedding'])
                self.user_embeddings[user_id] = self.users_db[user_id]
            
            # Save changes
            self._save_database()
            self._save_cache()
            
            logger.info(f"User {user_id} updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete user from database
        
        Args:
            user_id: User identifier
            
        Returns:
            bool: True if deletion successful
        """
        try:
            if user_id not in self.users_db:
                logger.error(f"User {user_id} not found")
                return False
            
            # Remove from all storage
            user_data = self.users_db.pop(user_id)
            self.embeddings_cache.pop(user_id, None)
            self.user_embeddings.pop(user_id, None)
            
            # Try to remove image file
            image_path = user_data.get('image_path')
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    logger.info(f"Removed image file: {image_path}")
                except Exception as e:
                    logger.warning(f"Could not remove image file: {e}")
            
            # Save changes
            self._save_database()
            self._save_cache()
            
            logger.info(f"User {user_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dictionary with database statistics
        """
        total_users = len(self.users_db)
        total_embeddings = len(self.embeddings_cache)
        
        # Calculate database size
        db_size = 0
        if self.embeddings_file.exists():
            db_size += self.embeddings_file.stat().st_size
        
        if self.embeddings_cache_file.exists():
            db_size += self.embeddings_cache_file.stat().st_size
        
        # Get recent registrations
        recent_users = []
        for user_id, user_data in self.users_db.items():
            if 'registration_date' in user_data:
                recent_users.append({
                    'user_id': user_id,
                    'name': user_data.get('name', 'Unknown'),
                    'registration_date': user_data['registration_date']
                })
        
        # Sort by registration date (newest first)
        recent_users.sort(key=lambda x: x['registration_date'], reverse=True)
        
        return {
            'total_users': total_users,
            'total_embeddings': total_embeddings,
            'database_size_bytes': db_size,
            'recent_registrations': recent_users[:5],  # Last 5 registrations
            'last_updated': datetime.now().isoformat()
        }
    
    def create_backup(self) -> str:
        """
        Create database backup
        
        Returns:
            str: Path to backup file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"eyed_backup_{timestamp}.zip"
            
            import zipfile
            with zipfile.ZipFile(backup_file, 'w') as zipf:
                # Add database files
                if self.embeddings_file.exists():
                    zipf.write(self.embeddings_file, self.embeddings_file.name)
                if self.embeddings_cache_file.exists():
                    zipf.write(self.embeddings_cache_file, self.embeddings_cache_file.name)
                
                # Add face images
                for user_data in self.users_db.values():
                    image_path = user_data.get('image_path')
                    if image_path and os.path.exists(image_path):
                        zipf.write(image_path, f"faces/{os.path.basename(image_path)}")
            
            logger.info(f"Database backup created: {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return ""
    
    def verify_embeddings(self) -> Dict[str, Any]:
        """
        Verify database integrity and embedding quality
        
        Returns:
            Dictionary with verification results
        """
        results = {
            'total_users': len(self.users_db),
            'total_embeddings': len(self.embeddings_cache),
            'integrity_check': True,
            'issues': [],
            'warnings': []
        }
        
        try:
            # Check for missing embeddings
            for user_id in self.users_db:
                if user_id not in self.embeddings_cache:
                    results['issues'].append(f"Missing embedding for user {user_id}")
                    results['integrity_check'] = False
            
            # Check for orphaned embeddings
            for user_id in self.embeddings_cache:
                if user_id not in self.users_db:
                    results['warnings'].append(f"Orphaned embedding for user {user_id}")
            
            # Check embedding dimensions
            expected_dim = 4096  # VGG-Face embedding dimension
            for user_id, embedding in self.embeddings_cache.items():
                if embedding.shape[0] != expected_dim:
                    results['issues'].append(
                        f"Invalid embedding dimension for user {user_id}: {embedding.shape[0]} != {expected_dim}"
                    )
                    results['integrity_check'] = False
            
            # Check image file existence
            for user_id, user_data in self.users_db.items():
                image_path = user_data.get('image_path')
                if image_path and not os.path.exists(image_path):
                    results['warnings'].append(f"Missing image file for user {user_id}: {image_path}")
            
            logger.info(f"Database verification completed. Integrity: {results['integrity_check']}")
            return results
            
        except Exception as e:
            logger.error(f"Database verification failed: {e}")
            results['integrity_check'] = False
            results['issues'].append(f"Verification error: {e}")
            return results
    
    def cleanup_orphaned_files(self) -> int:
        """
        Remove orphaned image files that are not referenced in database
        
        Returns:
            int: Number of files removed
        """
        try:
            removed_count = 0
            referenced_files = set()
            
            # Get all referenced image files
            for user_data in self.users_db.values():
                image_path = user_data.get('image_path')
                if image_path:
                    referenced_files.add(os.path.abspath(image_path))
            
            # Check for orphaned files in faces directory
            faces_dir = self.data_dir / "faces"
            if faces_dir.exists():
                for file_path in faces_dir.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                        abs_path = os.path.abspath(str(file_path))
                        if abs_path not in referenced_files:
                            try:
                                file_path.unlink()
                                removed_count += 1
                                logger.info(f"Removed orphaned file: {file_path}")
                            except Exception as e:
                                logger.warning(f"Could not remove orphaned file {file_path}: {e}")
            
            logger.info(f"Cleanup completed. Removed {removed_count} orphaned files")
            return removed_count
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0

    def _save_user_image(self, user_id: str, image: np.ndarray) -> Optional[Path]:
        """Save user image to disk"""
        try:
            # Create filename with timestamp
            timestamp = int(time.time())
            filename = f"user_{user_id}_{timestamp}.jpg"
            filepath = self.data_dir / filename
            
            # Convert numpy array to PIL Image and save
            if len(image.shape) == 3:
                # RGB image
                pil_image = Image.fromarray(image)
            else:
                # Grayscale image
                pil_image = Image.fromarray(image, mode='L')
            
            pil_image.save(filepath, "JPEG", quality=95)
            logger.info(f"User image saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save user image: {e}")
            return None
    
    def _generate_embedding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Generate face embedding using DeepFace"""
        try:
            # Import DeepFace here to avoid circular imports
            from deepface import DeepFace
            
            # Ensure image is in RGB format
            if len(image.shape) == 3 and image.shape[2] == 3:
                # Already RGB
                rgb_image = image
            elif len(image.shape) == 3 and image.shape[2] == 4:
                # RGBA to RGB
                rgb_image = image[:, :, :3]
            else:
                # Grayscale to RGB
                rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            
            # Generate embedding using DeepFace
            embedding = DeepFace.represent(
                img_path=rgb_image,
                model_name="Facenet512",
                enforce_detection=False,
                align=True
            )
            
            if embedding and len(embedding) > 0:
                # Convert to numpy array
                embedding_array = np.array(embedding[0]["embedding"])
                logger.info(f"Generated embedding with {len(embedding_array)} dimensions")
                return embedding_array
            else:
                logger.error("DeepFace failed to generate embedding")
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None


