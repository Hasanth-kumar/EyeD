"""
Face Database Interface for EyeD AI Attendance System

This interface defines the contract for face database operations including
user management, embedding storage, and search functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
import numpy as np
from datetime import datetime


class FaceDatabaseInterface(ABC):
    """
    Abstract interface for face database operations
    
    This interface defines the contract that all face database implementations
    must follow, ensuring consistent behavior across different storage backends.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def remove_user(self, user_id: str) -> bool:
        """
        Remove a user from the database
        
        Args:
            user_id: Unique identifier for the user to remove
            
        Returns:
            True if user was removed successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user information by ID
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            User data dictionary or None if not found
        """
        pass
    
    @abstractmethod
    def get_all_users(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve all users from the database
        
        Returns:
            Dictionary mapping user IDs to user data
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_user_embeddings(self, user_id: str) -> Optional[np.ndarray]:
        """
        Get face embeddings for a specific user
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Face embeddings as numpy array or None if not found
        """
        pass
    
    @abstractmethod
    def backup_database(self, backup_path: Optional[Path] = None) -> bool:
        """
        Create a backup of the database
        
        Args:
            backup_path: Optional path for backup, uses default if None
            
        Returns:
            True if backup was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def restore_database(self, backup_path: Path) -> bool:
        """
        Restore database from backup
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if restore was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics and health information
        
        Returns:
            Dictionary containing database statistics
        """
        pass
    
    @abstractmethod
    def clear_database(self) -> bool:
        """
        Clear all data from the database
        
        Returns:
            True if clear was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def is_healthy(self) -> bool:
        """
        Check if the database is in a healthy state
        
        Returns:
            True if database is healthy, False otherwise
        """
        pass
