"""
File Storage Handler for EyeD AI Attendance System

This module provides abstracted file operations (read, write, delete, exists)
for the repositories. This component follows SRP by handling ONLY file I/O operations.

No domain dependencies - pure infrastructure component.
"""

import os
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class FileStorage:
    """
    File storage handler that provides abstracted file operations.
    
    This class handles ONLY file I/O operations following the Single
    Responsibility Principle. No business logic, data parsing, or
    format conversion is performed here.
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize file storage.
        
        Args:
            base_path: Optional base directory for all operations.
                      If provided, all file paths will be relative to this.
        """
        self.base_path = Path(base_path) if base_path else None
        logger.debug(f"FileStorage initialized with base_path: {self.base_path}")
    
    def _resolve_path(self, file_path: str) -> Path:
        """
        Resolve file path relative to base_path if set.
        
        Args:
            file_path: File path (relative or absolute)
            
        Returns:
            Resolved Path object
        """
        path = Path(file_path)
        if self.base_path and not path.is_absolute():
            return self.base_path / path
        return path
    
    def read_file(self, file_path: str) -> bytes:
        """
        Read file as bytes.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File contents as bytes
            
        Raises:
            FileNotFoundError: If file does not exist
            PermissionError: If file cannot be read due to permissions
            IOError: For other I/O errors
        """
        resolved_path = self._resolve_path(file_path)
        
        if not resolved_path.exists():
            error_msg = f"File not found: {resolved_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        if not resolved_path.is_file():
            error_msg = f"Path is not a file: {resolved_path}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            with open(resolved_path, 'rb') as f:
                content = f.read()
            logger.debug(f"Read {len(content)} bytes from {resolved_path}")
            return content
        except PermissionError as e:
            error_msg = f"Permission denied reading file: {resolved_path}"
            logger.error(error_msg)
            raise PermissionError(error_msg) from e
        except IOError as e:
            error_msg = f"I/O error reading file: {resolved_path}"
            logger.error(error_msg)
            raise IOError(error_msg) from e
    
    def write_file(self, file_path: str, content: bytes) -> bool:
        """
        Write content to file.
        
        Args:
            file_path: Path to the file to write
            content: Content to write as bytes
            
        Returns:
            True on success, False on failure
        """
        resolved_path = self._resolve_path(file_path)
        
        try:
            # Create parent directories if needed
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(resolved_path, 'wb') as f:
                f.write(content)
            
            logger.debug(f"Wrote {len(content)} bytes to {resolved_path}")
            return True
        except PermissionError as e:
            logger.error(f"Permission denied writing file: {resolved_path} - {e}")
            return False
        except IOError as e:
            logger.error(f"I/O error writing file: {resolved_path} - {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error writing file: {resolved_path} - {e}")
            return False
    
    def read_text_file(self, file_path: str, encoding: str = "utf-8") -> str:
        """
        Read text file.
        
        Args:
            file_path: Path to the file to read
            encoding: Text encoding (default: utf-8)
            
        Returns:
            File contents as string
            
        Raises:
            FileNotFoundError: If file does not exist
            PermissionError: If file cannot be read due to permissions
            UnicodeDecodeError: If file cannot be decoded with specified encoding
            IOError: For other I/O errors
        """
        resolved_path = self._resolve_path(file_path)
        
        if not resolved_path.exists():
            error_msg = f"File not found: {resolved_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        if not resolved_path.is_file():
            error_msg = f"Path is not a file: {resolved_path}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            with open(resolved_path, 'r', encoding=encoding) as f:
                content = f.read()
            logger.debug(f"Read text file: {resolved_path} ({len(content)} characters)")
            return content
        except PermissionError as e:
            error_msg = f"Permission denied reading file: {resolved_path}"
            logger.error(error_msg)
            raise PermissionError(error_msg) from e
        except UnicodeDecodeError as e:
            error_msg = f"Encoding error reading file: {resolved_path} - {e}"
            logger.error(error_msg)
            raise UnicodeDecodeError(error_msg) from e
        except IOError as e:
            error_msg = f"I/O error reading file: {resolved_path}"
            logger.error(error_msg)
            raise IOError(error_msg) from e
    
    def write_text_file(self, file_path: str, content: str, encoding: str = "utf-8") -> bool:
        """
        Write text content to file.
        
        Args:
            file_path: Path to the file to write
            content: Content to write as string
            encoding: Text encoding (default: utf-8)
            
        Returns:
            True on success, False on failure
        """
        resolved_path = self._resolve_path(file_path)
        
        try:
            # Create parent directories if needed
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(resolved_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            logger.debug(f"Wrote text file: {resolved_path} ({len(content)} characters)")
            return True
        except PermissionError as e:
            logger.error(f"Permission denied writing file: {resolved_path} - {e}")
            return False
        except UnicodeEncodeError as e:
            logger.error(f"Encoding error writing file: {resolved_path} - {e}")
            return False
        except IOError as e:
            logger.error(f"I/O error writing file: {resolved_path} - {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error writing file: {resolved_path} - {e}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """
        Check if file exists.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if exists, False otherwise
        """
        resolved_path = self._resolve_path(file_path)
        exists = resolved_path.exists() and resolved_path.is_file()
        logger.debug(f"File exists check: {resolved_path} -> {exists}")
        return exists
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete file.
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            True on success, False on failure
        """
        resolved_path = self._resolve_path(file_path)
        
        if not resolved_path.exists():
            logger.warning(f"File does not exist for deletion: {resolved_path}")
            return False
        
        if not resolved_path.is_file():
            logger.error(f"Path is not a file: {resolved_path}")
            return False
        
        try:
            resolved_path.unlink()
            logger.debug(f"Deleted file: {resolved_path}")
            return True
        except PermissionError as e:
            logger.error(f"Permission denied deleting file: {resolved_path} - {e}")
            return False
        except IOError as e:
            logger.error(f"I/O error deleting file: {resolved_path} - {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting file: {resolved_path} - {e}")
            return False
    
    def create_directory(self, dir_path: str) -> bool:
        """
        Create directory and parent directories.
        
        Args:
            dir_path: Path to the directory to create
            
        Returns:
            True on success, False on failure
        """
        resolved_path = self._resolve_path(dir_path)
        
        try:
            resolved_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {resolved_path}")
            return True
        except PermissionError as e:
            logger.error(f"Permission denied creating directory: {resolved_path} - {e}")
            return False
        except IOError as e:
            logger.error(f"I/O error creating directory: {resolved_path} - {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating directory: {resolved_path} - {e}")
            return False
    
    def directory_exists(self, dir_path: str) -> bool:
        """
        Check if directory exists.
        
        Args:
            dir_path: Path to the directory to check
            
        Returns:
            True if exists, False otherwise
        """
        resolved_path = self._resolve_path(dir_path)
        exists = resolved_path.exists() and resolved_path.is_dir()
        logger.debug(f"Directory exists check: {resolved_path} -> {exists}")
        return exists
    
    def list_files(self, dir_path: str, pattern: str = "*") -> List[str]:
        """
        List files in directory matching pattern.
        
        Args:
            dir_path: Path to the directory to list
            pattern: Glob pattern to match files (default: "*")
            
        Returns:
            List of file paths (as strings)
        """
        resolved_path = self._resolve_path(dir_path)
        
        if not resolved_path.exists():
            logger.warning(f"Directory does not exist: {resolved_path}")
            return []
        
        if not resolved_path.is_dir():
            logger.error(f"Path is not a directory: {resolved_path}")
            return []
        
        try:
            files = [str(f) for f in resolved_path.glob(pattern) if f.is_file()]
            logger.debug(f"Listed {len(files)} files in {resolved_path} matching pattern '{pattern}'")
            return files
        except PermissionError as e:
            logger.error(f"Permission denied listing directory: {resolved_path} - {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing directory: {resolved_path} - {e}")
            return []












