"""
Face Storage Component

This module handles only face image storage operations,
following the Single-Responsibility Principle.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class FaceStorage:
    """Handles face image file storage operations"""
    
    def __init__(self, data_dir: str = "data/faces"):
        """
        Initialize face storage
        
        Args:
            data_dir: Directory for storing face data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.faces_file = self.data_dir / "faces.json"
        self.embeddings_file = self.data_dir / "embeddings.json"
        
        logger.info(f"Face storage initialized with directory: {self.data_dir}")
    
    def save_face_data(self, face_data: Dict[str, Any]) -> bool:
        """
        Save face data to JSON file
        
        Args:
            face_data: Face data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load existing data
            existing_data = self.load_face_data()
            
            # Add new face data
            if 'faces' not in existing_data:
                existing_data['faces'] = []
            
            existing_data['faces'].append(face_data)
            
            # Save back to file
            with open(self.faces_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            logger.info(f"Face data saved for user: {face_data.get('user_id', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save face data: {e}")
            return False
    
    def load_face_data(self) -> Dict[str, Any]:
        """
        Load face data from JSON file
        
        Returns:
            Dictionary containing face data
        """
        try:
            if self.faces_file.exists():
                with open(self.faces_file, 'r') as f:
                    return json.load(f)
            else:
                # Create empty structure
                empty_data = {
                    'faces': [],
                    'metadata': {
                        'created': '2025-01-01',
                        'version': '1.0'
                    }
                }
                self.save_face_data(empty_data)
                return empty_data
                
        except Exception as e:
            logger.error(f"Failed to load face data: {e}")
            return {'faces': [], 'metadata': {}}
    
    def delete_face_data(self, user_id: str) -> bool:
        """
        Delete face data for a specific user
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            existing_data = self.load_face_data()
            
            # Filter out the user to delete
            if 'faces' in existing_data:
                existing_data['faces'] = [
                    face for face in existing_data['faces'] 
                    if face.get('user_id') != user_id
                ]
            
            # Save updated data
            with open(self.faces_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            logger.info(f"Face data deleted for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete face data: {e}")
            return False
    
    def get_face_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get face data for a specific user
        
        Args:
            user_id: User ID to retrieve
            
        Returns:
            Face data dictionary or None if not found
        """
        try:
            existing_data = self.load_face_data()
            
            if 'faces' in existing_data:
                for face in existing_data['faces']:
                    if face.get('user_id') == user_id:
                        return face
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get face data: {e}")
            return None
    
    def list_all_faces(self) -> List[Dict[str, Any]]:
        """
        Get list of all face data
        
        Returns:
            List of face data dictionaries
        """
        try:
            existing_data = self.load_face_data()
            return existing_data.get('faces', [])
            
        except Exception as e:
            logger.error(f"Failed to list faces: {e}")
            return []
    
    def is_healthy(self) -> bool:
        """Check if storage system is healthy"""
        try:
            # Check if directory exists and is writable
            if not self.data_dir.exists():
                return False
            
            # Try to create a test file
            test_file = self.data_dir / "test.txt"
            test_file.write_text("test")
            test_file.unlink()
            
            return True
            
        except Exception as e:
            logger.error(f"Storage health check failed: {e}")
            return False
