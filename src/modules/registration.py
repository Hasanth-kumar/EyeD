"""
Face Registration Module for EyeD AI Attendance System
Day 2 Implementation: Face Registration (Selfie Capture)

This module will handle:
- Webcam snapshot capture
- Image upload functionality  
- Face embedding extraction using DeepFace
- Storage of user data and embeddings
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import uuid

# TODO: Implement on Day 2
class FaceRegistration:
    """Face registration handler"""
    
    def __init__(self):
        self.camera_id = 0
        self.faces_dir = Path("data/faces")
        self.faces_dir.mkdir(exist_ok=True)
    
    def capture_selfie(self, user_name: str) -> Optional[str]:
        """
        Capture selfie from webcam
        
        Args:
            user_name: Name of the user to register
            
        Returns:
            Path to saved image or None if failed
        """
        # TODO: Implement webcam capture
        print(f"📸 Selfie capture for {user_name} - Not yet implemented (Day 2)")
        return None
    
    def upload_image(self, image_path: str, user_name: str) -> Optional[str]:
        """
        Process uploaded image for registration
        
        Args:
            image_path: Path to uploaded image
            user_name: Name of the user to register
            
        Returns:
            Path to saved image or None if failed
        """
        # TODO: Implement image upload processing
        print(f"📁 Image upload for {user_name} - Not yet implemented (Day 2)")
        return None
    
    def extract_embedding(self, image_path: str) -> Optional[np.ndarray]:
        """
        Extract face embedding using DeepFace
        
        Args:
            image_path: Path to face image
            
        Returns:
            Face embedding vector or None if failed
        """
        # TODO: Implement DeepFace embedding extraction
        print(f"🧠 Embedding extraction - Not yet implemented (Day 2)")
        return None
    
    def register_user(self, user_name: str, image_path: str) -> bool:
        """
        Complete user registration process
        
        Args:
            user_name: Name of the user
            image_path: Path to user's face image
            
        Returns:
            True if registration successful, False otherwise
        """
        # TODO: Implement complete registration workflow
        print(f"👤 User registration for {user_name} - Not yet implemented (Day 2)")
        return False

# Global registration instance
face_registration = FaceRegistration()
