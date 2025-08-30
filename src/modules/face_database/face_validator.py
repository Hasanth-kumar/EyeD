"""
Face Validator Component

This module handles only face validation operations,
following the Single-Responsibility Principle.
"""

import numpy as np
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class FaceValidator:
    """Validates face images and data"""
    
    def __init__(self):
        """Initialize face validator"""
        logger.info("Face validator initialized")
    
    def validate_face_image(self, image: np.ndarray) -> Tuple[bool, str]:
        """
        Validate face image quality
        
        Args:
            image: Face image to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if image is None:
                return False, "Image is None"
            
            if len(image.shape) != 3:
                return False, "Image must be 3D (height, width, channels)"
            
            height, width = image.shape[:2]
            if height < 100 or width < 100:
                return False, f"Image too small: {width}x{height}, minimum 100x100"
            
            if height > 2000 or width > 2000:
                return False, f"Image too large: {width}x{height}, maximum 2000x2000"
            
            return True, "Image is valid"
            
        except Exception as e:
            logger.error(f"Error validating image: {e}")
            return False, f"Validation error: {str(e)}"
    
    def validate_face_data(self, face_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate face data structure
        
        Args:
            face_data: Face data dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            required_fields = ['user_id', 'name', 'image_path']
            
            for field in required_fields:
                if field not in face_data:
                    return False, f"Missing required field: {field}"
                
                if not face_data[field]:
                    return False, f"Field {field} cannot be empty"
            
            return True, "Face data is valid"
            
        except Exception as e:
            logger.error(f"Error validating face data: {e}")
            return False, f"Validation error: {str(e)}"
    
    def validate_user_id(self, user_id: str) -> Tuple[bool, str]:
        """
        Validate user ID format
        
        Args:
            user_id: User ID to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not user_id:
                return False, "User ID cannot be empty"
            
            if len(user_id) < 3:
                return False, "User ID too short, minimum 3 characters"
            
            if len(user_id) > 50:
                return False, "User ID too long, maximum 50 characters"
            
            # Check for valid characters (alphanumeric, underscore, hyphen)
            import re
            if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
                return False, "User ID contains invalid characters"
            
            return True, "User ID is valid"
            
        except Exception as e:
            logger.error(f"Error validating user ID: {e}")
            return False, f"Validation error: {str(e)}"
