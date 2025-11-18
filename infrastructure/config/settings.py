"""
Configuration Management System

This module provides a centralized configuration management system that loads
settings from environment variables and configuration files. It follows the
Single Responsibility Principle by handling ONLY configuration management.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Optional, Dict

logger = logging.getLogger(__name__)


class Settings:
    """
    Configuration management system that loads settings from:
    1. Environment variables (highest priority)
    2. Configuration file (if provided)
    3. Default values (lowest priority)
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize settings from environment variables and optional config file.
        
        Args:
            config_file: Optional path to configuration file (JSON or YAML)
        """
        self._config: Dict[str, Any] = {}
        self._project_root = self._get_project_root()
        
        # Load defaults first
        self._load_defaults()
        
        # Load from config file if provided (before environment variables to allow env override)
        if config_file:
            self._load_from_file(config_file)
        
        # Load from environment variables (highest priority)
        self._load_from_environment()
        
        logger.info("Configuration loaded successfully")
        logger.debug(f"Configuration source: env vars={len(self._get_env_vars())} keys, "
                    f"config file={'loaded' if config_file else 'none'}, "
                    f"defaults={len(self._config)} keys")
    
    def _get_project_root(self) -> Path:
        """Get the project root directory."""
        # Try to find project root by looking for common markers
        current = Path(__file__).resolve()
        while current != current.parent:
            if (current / "main.py").exists() or (current / "requirements.txt").exists():
                return current
            current = current.parent
        # Fallback to current directory
        return Path.cwd()
    
    def _load_defaults(self) -> None:
        """Load default configuration values."""
        self._config = {
            'data_dir': str(self._project_root / "data"),
            'faces_dir': str(self._project_root / "data" / "faces"),
            'attendance_file': str(self._project_root / "data" / "attendance.csv"),
            'camera_id': 0,
            'frame_width': 640,
            'frame_height': 480,
            'fps': 30,
            'confidence_threshold': 0.45,
            'liveness_threshold': 0.2,
        }
    
    def _load_from_file(self, config_file: str) -> None:
        """
        Load configuration from a JSON or YAML file.
        
        Args:
            config_file: Path to configuration file
        """
        config_path = Path(config_file)
        
        if not config_path.exists():
            logger.warning(f"Configuration file not found: {config_file}, using defaults")
            return
        
        try:
            if config_path.suffix.lower() == '.json':
                with open(config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._config.update(file_config)
                    logger.info(f"Loaded configuration from JSON file: {config_file}")
            
            elif config_path.suffix.lower() in ['.yaml', '.yml']:
                try:
                    import yaml
                    with open(config_path, 'r', encoding='utf-8') as f:
                        file_config = yaml.safe_load(f)
                        if file_config:
                            self._config.update(file_config)
                            logger.info(f"Loaded configuration from YAML file: {config_file}")
                except ImportError:
                    logger.warning("YAML support not available (PyYAML not installed), skipping YAML config file")
            
            else:
                logger.warning(f"Unsupported configuration file format: {config_file}, expected .json or .yaml/.yml")
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON configuration file {config_file}: {e}")
        except Exception as e:
            logger.error(f"Failed to load configuration file {config_file}: {e}")
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'EYED_DATA_DIR': 'data_dir',
            'EYED_FACES_DIR': 'faces_dir',
            'EYED_ATTENDANCE_FILE': 'attendance_file',
            'EYED_CAMERA_ID': 'camera_id',
            'EYED_FRAME_WIDTH': 'frame_width',
            'EYED_FRAME_HEIGHT': 'frame_height',
            'EYED_FPS': 'fps',
            'EYED_CONFIDENCE_THRESHOLD': 'confidence_threshold',
            'EYED_LIVENESS_THRESHOLD': 'liveness_threshold',
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                self._config[config_key] = value
                logger.debug(f"Loaded {config_key} from environment variable {env_var}")
    
    def _get_env_vars(self) -> Dict[str, str]:
        """Get all EyeD-related environment variables."""
        return {k: v for k, v in os.environ.items() if k.startswith('EYED_')}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default if not found
        """
        return self._config.get(key, default)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """
        Get configuration value as integer.
        
        Args:
            key: Configuration key
            default: Default value if key not found or conversion fails
            
        Returns:
            Integer value or default
        """
        value = self._config.get(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            logger.warning(f"Failed to convert {key}={value} to int, using default {default}")
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """
        Get configuration value as float.
        
        Args:
            key: Configuration key
            default: Default value if key not found or conversion fails
            
        Returns:
            Float value or default
        """
        value = self._config.get(key, default)
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"Failed to convert {key}={value} to float, using default {default}")
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        Get configuration value as boolean.
        
        Args:
            key: Configuration key
            default: Default value if key not found or conversion fails
            
        Returns:
            Boolean value or default
        """
        value = self._config.get(key, default)
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
        
        return bool(value)
    
    def get_path(self, key: str, default: Optional[Path] = None) -> Path:
        """
        Get configuration value as Path.
        
        Args:
            key: Configuration key
            default: Default Path if key not found
            
        Returns:
            Path object or default
        """
        value = self._config.get(key)
        if value is None:
            return default if default is not None else Path.cwd()
        
        try:
            path = Path(value)
            # Expand user directory (~) and environment variables
            path = path.expanduser()
            if '$' in str(path) or '%' in str(path):
                path = Path(os.path.expandvars(str(path)))
            return path
        except Exception as e:
            logger.warning(f"Failed to convert {key}={value} to Path: {e}, using default")
            return default if default is not None else Path.cwd()
    
    @property
    def data_dir(self) -> Path:
        """Return data directory path."""
        return self.get_path('data_dir', self._project_root / "data")
    
    @property
    def faces_dir(self) -> Path:
        """Return faces directory path."""
        return self.get_path('faces_dir', self.data_dir / "faces")
    
    @property
    def attendance_file(self) -> Path:
        """Return attendance file path."""
        return self.get_path('attendance_file', self.data_dir / "attendance.csv")
    
    @property
    def camera_id(self) -> int:
        """Return camera device ID."""
        return self.get_int('camera_id', 0)
    
    @property
    def frame_width(self) -> int:
        """Return camera frame width."""
        return self.get_int('frame_width', 640)
    
    @property
    def frame_height(self) -> int:
        """Return camera frame height."""
        return self.get_int('frame_height', 480)
    
    @property
    def fps(self) -> int:
        """Return camera FPS."""
        return self.get_int('fps', 30)
    
    @property
    def confidence_threshold(self) -> float:
        """Return confidence threshold."""
        return self.get_float('confidence_threshold', 0.45)
    
    @property
    def liveness_threshold(self) -> float:
        """Return liveness threshold."""
        return self.get_float('liveness_threshold', 0.2)






