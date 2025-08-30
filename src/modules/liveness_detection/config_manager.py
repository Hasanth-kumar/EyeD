"""
Liveness Detection Configuration Manager

This module handles configuration management for liveness detection,
following the Single-Responsibility Principle.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class LivenessConfigManager:
    """Manages configuration for liveness detection components"""
    
    def __init__(self):
        """Initialize with default configuration"""
        self.config = {
            'blink_detection': {
                'ear_threshold': 0.21,
                'min_consecutive_frames': 2,
                'blink_counter': 0
            },
            'face_quality': {
                'min_resolution': (480, 480),
                'min_brightness': 30,
                'max_brightness': 250,
                'min_contrast': 20,
                'min_sharpness': 100
            },
            'mediapipe': {
                'min_detection_confidence': 0.5,
                'min_tracking_confidence': 0.5,
                'max_num_faces': 1,
                'refine_landmarks': True
            },
            'performance': {
                'enable_debug_mode': False,
                'enable_visualization': False,
                'frame_skip_rate': 1
            }
        }
        
        logger.info("Liveness configuration manager initialized")
    
    def get_config(self, section: str) -> Dict[str, Any]:
        """Get configuration for a specific section"""
        return self.config.get(section, {})
    
    def update_config(self, section: str, key: str, value: Any) -> bool:
        """Update a specific configuration value"""
        try:
            if section in self.config and key in self.config[section]:
                self.config[section][key] = value
                logger.info(f"Updated config: {section}.{key} = {value}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update config: {e}")
            return False
    
    def get_test_configuration(self, test_type: str) -> Dict[str, Any]:
        """Get configuration for a specific test type"""
        test_configs = {
            'blink': self.config['blink_detection'],
            'head_movement': self.config['mediapipe'],
            'eye_movement': self.config['mediapipe'],
            'mouth_movement': self.config['mediapipe'],
            'depth': self.config['face_quality'],
            'texture': self.config['face_quality']
        }
        return test_configs.get(test_type, {})
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values"""
        try:
            self.__init__()
            logger.info("Configuration reset to defaults")
            return True
        except Exception as e:
            logger.error(f"Failed to reset config: {e}")
            return False
