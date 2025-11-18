"""
Image Converter Utility - EyeD AI Attendance System

This module provides image format conversion utilities for converting between
different image formats (PIL, Streamlit camera input, numpy arrays).

This component follows SRP by handling ONLY image format conversion.
No business logic, no domain dependencies.
"""

import numpy as np
from typing import Optional, Union
from PIL import Image
import cv2
import logging
import base64
import io

logger = logging.getLogger(__name__)


class ImageConverter:
    """
    Utility for converting images between different formats.
    
    Single Responsibility: Convert image formats ONLY.
    No business logic, no domain dependencies.
    """
    
    @staticmethod
    def camera_input_to_numpy(
        camera_input: Union[Image.Image, bytes, any]
    ) -> Optional[np.ndarray]:
        """
        Convert Streamlit camera input to numpy array in BGR format.
        
        Streamlit's camera_input can return either:
        - PIL Image object
        - BytesIO object (file-like)
        
        This method handles both cases and converts to OpenCV-compatible
        BGR numpy array.
        
        Args:
            camera_input: Streamlit camera input (PIL Image, bytes, or file-like object).
        
        Returns:
            Numpy array in BGR format (OpenCV format) or None if conversion fails.
        
        Example:
            >>> camera_image = st.camera_input("Take photo")
            >>> if camera_image:
            ...     frame = ImageConverter.camera_input_to_numpy(camera_image)
            ...     if frame is not None:
            ...         # Use frame with OpenCV
            ...         pass
        """
        try:
            # Handle PIL Image
            if isinstance(camera_input, Image.Image):
                image_array = np.array(camera_input)
            else:
                # Handle bytes or file-like object
                # Reset file pointer if it's a file-like object
                if hasattr(camera_input, 'seek'):
                    camera_input.seek(0)
                
                # Open as PIL Image
                image = Image.open(camera_input)
                image_array = np.array(image)
            
            # Convert RGB to BGR for OpenCV compatibility
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                # Assume RGB, convert to BGR
                bgr_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                return bgr_array
            
            return image_array
        
        except Exception as e:
            logger.error(f"Error converting camera image to numpy array: {e}")
            return None
    
    @staticmethod
    def pil_to_numpy(
        pil_image: Image.Image,
        convert_to_bgr: bool = True
    ) -> Optional[np.ndarray]:
        """
        Convert PIL Image to numpy array.
        
        Args:
            pil_image: PIL Image object.
            convert_to_bgr: If True, convert RGB to BGR for OpenCV compatibility.
        
        Returns:
            Numpy array in BGR format (if convert_to_bgr=True) or RGB format,
            or None if conversion fails.
        """
        try:
            # Convert PIL Image to numpy array
            image_array = np.array(pil_image)
            
            # Convert RGB to BGR if requested
            if convert_to_bgr and len(image_array.shape) == 3 and image_array.shape[2] == 3:
                bgr_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                return bgr_array
            
            return image_array
        
        except Exception as e:
            logger.error(f"Error converting PIL image to numpy array: {e}")
            return None
    
    @staticmethod
    def base64_to_numpy(
        base64_string: str,
        convert_to_bgr: bool = False
    ) -> Optional[np.ndarray]:
        """
        Convert base64 encoded image string to numpy array.
        
        This method handles base64 encoded images (with or without data URL prefix)
        and converts them to numpy arrays suitable for image processing.
        
        Args:
            base64_string: Base64 encoded image string (with or without data URL prefix).
            convert_to_bgr: If True, convert RGB to BGR for OpenCV compatibility.
                          Default is False (returns RGB format).
        
        Returns:
            Numpy array representing the image (RGB format by default, BGR if convert_to_bgr=True),
            or None if conversion fails.
        
        Example:
            >>> base64_img = "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
            >>> image_array = ImageConverter.base64_to_numpy(base64_img)
            >>> if image_array is not None:
            ...     # Use image_array for processing
            ...     pass
        """
        try:
            # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,...")
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(base64_string)
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array
            image_array = np.array(image)
            
            # Convert RGB to BGR if requested (for OpenCV compatibility)
            if convert_to_bgr and len(image_array.shape) == 3 and image_array.shape[2] == 3:
                bgr_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                return bgr_array
            
            return image_array
        
        except Exception as e:
            logger.error(f"Error converting base64 to numpy array: {e}")
            return None










