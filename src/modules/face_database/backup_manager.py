"""
Backup Manager Component

This module handles only backup operations,
following the Single-Responsibility Principle.
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BackupManager:
    """Manages backup operations for face database"""
    
    def __init__(self, backup_dir: str = "data/faces/backups"):
        """
        Initialize backup manager
        
        Args:
            backup_dir: Directory for storing backups
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Backup manager initialized with directory: {self.backup_dir}")
    
    def create_backup(self, source_files: List[str], backup_name: str = None) -> str:
        """
        Create a backup of source files
        
        Args:
            source_files: List of file paths to backup
            backup_name: Optional custom backup name
            
        Returns:
            Path to created backup
        """
        try:
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_{timestamp}"
            
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            
            for source_file in source_files:
                source_path = Path(source_file)
                if source_path.exists():
                    dest_path = backup_path / source_path.name
                    shutil.copy2(source_path, dest_path)
                    logger.info(f"Backed up: {source_file} -> {dest_path}")
            
            logger.info(f"Backup created successfully: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return ""
    
    def restore_backup(self, backup_path: str, restore_dir: str = None) -> bool:
        """
        Restore files from a backup
        
        Args:
            backup_path: Path to backup directory
            restore_dir: Directory to restore to (defaults to original location)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                logger.error(f"Backup path does not exist: {backup_path}")
                return False
            
            if not restore_dir:
                restore_dir = "data/faces"
            
            restore_path = Path(restore_dir)
            restore_path.mkdir(parents=True, exist_ok=True)
            
            # Copy all files from backup
            for backup_file in backup_path.iterdir():
                if backup_file.is_file():
                    dest_file = restore_path / backup_file.name
                    shutil.copy2(backup_file, dest_file)
                    logger.info(f"Restored: {backup_file} -> {dest_file}")
            
            logger.info(f"Backup restored successfully to: {restore_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups
        
        Returns:
            List of backup information dictionaries
        """
        try:
            backups = []
            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.is_dir():
                    backup_info = {
                        'name': backup_dir.name,
                        'path': str(backup_dir),
                        'created': backup_dir.stat().st_mtime,
                        'files': [f.name for f in backup_dir.iterdir() if f.is_file()]
                    }
                    backups.append(backup_info)
            
            return sorted(backups, key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []
    
    def delete_backup(self, backup_name: str) -> bool:
        """
        Delete a specific backup
        
        Args:
            backup_name: Name of backup to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            backup_path = self.backup_dir / backup_name
            if backup_path.exists() and backup_path.is_dir():
                shutil.rmtree(backup_path)
                logger.info(f"Backup deleted: {backup_name}")
                return True
            else:
                logger.warning(f"Backup not found: {backup_name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete backup: {e}")
            return False
    
    def cleanup_old_backups(self, keep_count: int = 5) -> int:
        """
        Clean up old backups, keeping only the specified number
        
        Args:
            keep_count: Number of recent backups to keep
            
        Returns:
            Number of backups deleted
        """
        try:
            backups = self.list_backups()
            if len(backups) <= keep_count:
                return 0
            
            to_delete = backups[keep_count:]
            deleted_count = 0
            
            for backup in to_delete:
                if self.delete_backup(backup['name']):
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old backups")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
            return 0
