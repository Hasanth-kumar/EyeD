"""
Camera Manager for EyeD AI Attendance System

This module provides abstracted camera operations (initialize, capture frame, release)
for the application layer. This component follows SRP by handling ONLY camera I/O operations.

No domain dependencies - pure infrastructure component.
"""

import cv2
import logging
import numpy as np
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class CameraManager:
    """
    Camera manager that provides abstracted camera operations.
    
    This class handles ONLY camera I/O operations following the Single
    Responsibility Principle. No face detection, image processing, or
    business logic is performed here.
    """
    
    def __init__(self, camera_id: int = 0, settings: Optional[Dict[str, Any]] = None):
        """
        Initialize camera manager.
        
        Args:
            camera_id: Camera device ID (default: 0)
            settings: Optional camera settings dictionary with keys:
                     - width: Frame width (default: 640)
                     - height: Frame height (default: 480)
                     - fps: Frames per second (default: 30)
        """
        self.camera_id = camera_id
        self.settings = settings or {}
        
        # Default camera properties
        self._width = self.settings.get('width', 640)
        self._height = self.settings.get('height', 480)
        self._fps = self.settings.get('fps', 30)
        
        # Camera instance (initialized on initialize() call)
        self._camera: Optional[cv2.VideoCapture] = None
        self._is_initialized = False
        
        logger.debug(f"CameraManager initialized for camera_id={camera_id}, "
                    f"settings={self.settings}")
    
    def initialize(self) -> bool:
        """
        Initialize camera connection.
        
        Sets camera properties (width, height, fps) and opens the camera.
        
        Returns:
            True on success, False on failure
        """
        if self._is_initialized:
            logger.warning("Camera already initialized")
            return True
        
        try:
            logger.info(f"Initializing camera {self.camera_id}")
            self._camera = cv2.VideoCapture(self.camera_id)
            
            if not self._camera.isOpened():
                logger.error(f"Failed to open camera {self.camera_id}")
                self._camera = None
                return False
            
            # Set camera properties
            success = True
            if not self._set_property(cv2.CAP_PROP_FRAME_WIDTH, self._width):
                logger.warning(f"Failed to set width to {self._width}")
                success = False
            
            if not self._set_property(cv2.CAP_PROP_FRAME_HEIGHT, self._height):
                logger.warning(f"Failed to set height to {self._height}")
                success = False
            
            if not self._set_property(cv2.CAP_PROP_FPS, self._fps):
                logger.warning(f"Failed to set fps to {self._fps}")
                success = False
            
            self._is_initialized = True
            logger.info(f"Camera {self.camera_id} initialized successfully "
                       f"(width={self._width}, height={self._height}, fps={self._fps})")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing camera {self.camera_id}: {e}")
            self._camera = None
            self._is_initialized = False
            return False
    
    def _set_property(self, prop_id: int, value: float) -> bool:
        """
        Set a camera property.
        
        Args:
            prop_id: OpenCV property ID (e.g., cv2.CAP_PROP_FRAME_WIDTH)
            value: Property value to set
            
        Returns:
            True if property was set successfully, False otherwise
        """
        if not self._camera:
            return False
        
        try:
            result = self._camera.set(prop_id, value)
            if not result:
                logger.debug(f"Camera property {prop_id} may not be supported")
            return result
        except Exception as e:
            logger.debug(f"Error setting camera property {prop_id}: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """
        Check if camera is initialized.
        
        Returns:
            True if initialized, False otherwise
        """
        return self._is_initialized and self._camera is not None and self._camera.isOpened()
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture single frame from camera.
        
        Returns:
            Numpy array (BGR format) or None on failure
        """
        if not self.is_initialized():
            logger.warning("Cannot capture frame: camera not initialized")
            return None
        
        try:
            ret, frame = self._camera.read()
            
            if not ret or frame is None:
                logger.warning("Failed to capture frame from camera")
                return None
            
            return frame
            
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None
    
    def release(self) -> None:
        """
        Release camera resources.
        
        Cleans up OpenCV VideoCapture and resets initialization state.
        """
        if self._camera is not None:
            try:
                self._camera.release()
                logger.info(f"Camera {self.camera_id} released")
            except Exception as e:
                logger.error(f"Error releasing camera {self.camera_id}: {e}")
            finally:
                self._camera = None
                self._is_initialized = False
    
    def set_properties(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fps: Optional[int] = None
    ) -> bool:
        """
        Set camera properties.
        
        Args:
            width: Frame width (optional)
            height: Frame height (optional)
            fps: Frames per second (optional)
            
        Returns:
            True on success, False on failure
        """
        success = True
        
        if width is not None:
            if width > 0:
                self._width = width
                if self.is_initialized():
                    if not self._set_property(cv2.CAP_PROP_FRAME_WIDTH, width):
                        logger.warning(f"Failed to set width to {width}")
                        success = False
                    else:
                        logger.debug(f"Camera width set to {width}")
            else:
                logger.error(f"Invalid width value: {width}")
                success = False
        
        if height is not None:
            if height > 0:
                self._height = height
                if self.is_initialized():
                    if not self._set_property(cv2.CAP_PROP_FRAME_HEIGHT, height):
                        logger.warning(f"Failed to set height to {height}")
                        success = False
                    else:
                        logger.debug(f"Camera height set to {height}")
            else:
                logger.error(f"Invalid height value: {height}")
                success = False
        
        if fps is not None:
            if fps > 0:
                self._fps = fps
                if self.is_initialized():
                    if not self._set_property(cv2.CAP_PROP_FPS, fps):
                        logger.warning(f"Failed to set fps to {fps}")
                        success = False
                    else:
                        logger.debug(f"Camera fps set to {fps}")
            else:
                logger.error(f"Invalid fps value: {fps}")
                success = False
        
        return success
    
    def get_properties(self) -> Dict[str, Any]:
        """
        Get current camera properties.
        
        Returns:
            Dictionary with width, height, fps, and other camera properties
        """
        properties = {
            'camera_id': self.camera_id,
            'width': self._width,
            'height': self._height,
            'fps': self._fps,
            'is_initialized': self.is_initialized(),
        }
        
        if self.is_initialized() and self._camera:
            try:
                # Get actual camera properties
                actual_width = self._camera.get(cv2.CAP_PROP_FRAME_WIDTH)
                actual_height = self._camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
                actual_fps = self._camera.get(cv2.CAP_PROP_FPS)
                
                properties.update({
                    'actual_width': int(actual_width) if actual_width > 0 else None,
                    'actual_height': int(actual_height) if actual_height > 0 else None,
                    'actual_fps': int(actual_fps) if actual_fps > 0 else None,
                    'backend': self._camera.getBackendName(),
                })
            except Exception as e:
                logger.debug(f"Error getting camera properties: {e}")
        
        return properties
    
    def __enter__(self):
        """Context manager entry - initialize camera."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - release camera."""
        self.release()
    
    def __del__(self):
        """Destructor - ensure camera is released."""
        self.release()










