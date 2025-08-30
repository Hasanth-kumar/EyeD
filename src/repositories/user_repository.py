"""
User Repository for EyeD AI Attendance System

This module handles data persistence for user operations,
following the Single-Responsibility Principle.
"""

import json
import pandas as pd
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for user data persistence"""
    
    def __init__(self, data_file: str = "data/faces/faces.json"):
        """
        Initialize user repository
        
        Args:
            data_file: Path to user data file
        """
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize empty file if it doesn't exist
        if not self.data_file.exists():
            self._create_empty_file()
        
        logger.info(f"User repository initialized with file: {self.data_file}")
    
    def _create_empty_file(self):
        """Create empty user file with basic structure"""
        initial_data = {
            "users": {},
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "total_users": 0
            }
        }
        
        with open(self.data_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
        
        logger.info("Created empty user file with basic structure")
    
    def add_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new user to the repository
        
        Args:
            user_data: User data dictionary
            
        Returns:
            Dictionary with operation result
        """
        try:
            # Load existing data
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            user_id = user_data['user_id']
            
            # Check if user already exists
            if user_id in data['users']:
                return {
                    'success': False,
                    'error': f'User {user_id} already exists'
                }
            
            # Add user with metadata
            user_data['created_at'] = datetime.now().isoformat()
            user_data['updated_at'] = datetime.now().isoformat()
            user_data['status'] = 'active'
            
            data['users'][user_id] = user_data
            data['metadata']['total_users'] = len(data['users'])
            data['metadata']['last_updated'] = datetime.now().isoformat()
            
            # Save back to file
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"User {user_id} added successfully")
            return {
                'success': True,
                'user_id': user_id,
                'message': f'User {user_id} added successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to add user: {e}")
            return {
                'success': False,
                'error': f'Failed to add user: {str(e)}'
            }
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user information
        
        Args:
            user_id: User ID to update
            updates: Dictionary of fields to update
            
        Returns:
            Dictionary with operation result
        """
        try:
            # Load existing data
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            # Check if user exists
            if user_id not in data['users']:
                return {
                    'success': False,
                    'error': f'User {user_id} not found'
                }
            
            # Update user data
            for key, value in updates.items():
                if key in data['users'][user_id]:
                    data['users'][user_id][key] = value
            
            # Update metadata
            data['users'][user_id]['updated_at'] = datetime.now().isoformat()
            data['metadata']['last_updated'] = datetime.now().isoformat()
            
            # Save back to file
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"User {user_id} updated successfully")
            return {
                'success': True,
                'user_id': user_id,
                'updated_fields': list(updates.keys()),
                'message': f'User {user_id} updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            return {
                'success': False,
                'error': f'Failed to update user: {str(e)}'
            }
    
    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """
        Delete a user from the repository
        
        Args:
            user_id: User ID to delete
            
        Returns:
            Dictionary with operation result
        """
        try:
            # Load existing data
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            # Check if user exists
            if user_id not in data['users']:
                return {
                    'success': False,
                    'error': f'User {user_id} not found'
                }
            
            # Remove user
            deleted_user = data['users'].pop(user_id)
            data['metadata']['total_users'] = len(data['users'])
            data['metadata']['last_updated'] = datetime.now().isoformat()
            
            # Save back to file
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"User {user_id} deleted successfully")
            return {
                'success': True,
                'user_id': user_id,
                'deleted_user': deleted_user,
                'message': f'User {user_id} deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            return {
                'success': False,
                'error': f'Failed to delete user: {str(e)}'
            }
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        Get user information by ID
        
        Args:
            user_id: User ID to retrieve
            
        Returns:
            Dictionary with user information
        """
        try:
            # Load existing data
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            # Check if user exists
            if user_id not in data['users']:
                return {
                    'success': False,
                    'error': f'User {user_id} not found'
                }
            
            user_data = data['users'][user_id]
            
            logger.info(f"User {user_id} retrieved successfully")
            return {
                'success': True,
                'data': user_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return {
                'success': False,
                'error': f'Failed to get user: {str(e)}'
            }
    
    def get_all_users(self, include_inactive: bool = True) -> Dict[str, Any]:
        """
        Get all users from the repository
        
        Args:
            include_inactive: Whether to include inactive users
            
        Returns:
            Dictionary with all users
        """
        try:
            # Load existing data
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            users = data['users']
            
            # Filter inactive users if requested
            if not include_inactive:
                users = {uid: user for uid, user in users.items() 
                        if user.get('status', 'active') == 'active'}
            
            # Convert to list format
            user_list = []
            for user_id, user_data in users.items():
                user_data['user_id'] = user_id
                user_list.append(user_data)
            
            logger.info(f"Retrieved {len(user_list)} users")
            return {
                'success': True,
                'data': user_list,
                'total_count': len(user_list)
            }
            
        except Exception as e:
            logger.error(f"Failed to get all users: {e}")
            return {
                'success': False,
                'error': f'Failed to get all users: {str(e)}'
            }
    
    def search_users(self, search_term: str, search_fields: List[str] = None) -> Dict[str, Any]:
        """
        Search users by various criteria
        
        Args:
            search_term: Term to search for
            search_fields: Fields to search in (default: ['user_id', 'user_name'])
            
        Returns:
            Dictionary with search results
        """
        try:
            if search_fields is None:
                search_fields = ['user_id', 'user_name']
            
            # Get all users
            all_users_result = self.get_all_users()
            if not all_users_result['success']:
                return all_users_result
            
            users = all_users_result['data']
            search_term_lower = search_term.lower()
            
            # Filter users based on search term
            matching_users = []
            for user in users:
                for field in search_fields:
                    if field in user and user[field]:
                        field_value = str(user[field]).lower()
                        if search_term_lower in field_value:
                            matching_users.append(user)
                            break
            
            logger.info(f"Search for '{search_term}' returned {len(matching_users)} results")
            return {
                'success': True,
                'search_term': search_term,
                'search_fields': search_fields,
                'results': matching_users,
                'total_matches': len(matching_users)
            }
            
        except Exception as e:
            logger.error(f"User search failed: {e}")
            return {
                'success': False,
                'error': f'User search failed: {str(e)}'
            }
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """
        Get user repository statistics
        
        Returns:
            Dictionary with repository statistics
        """
        try:
            # Load existing data
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            users = data['users']
            
            # Calculate statistics
            total_users = len(users)
            active_users = len([u for u in users.values() if u.get('status') == 'active'])
            inactive_users = total_users - active_users
            
            # Count users by registration month
            registration_months = {}
            for user in users.values():
                if 'created_at' in user:
                    try:
                        month = datetime.fromisoformat(user['created_at']).strftime('%Y-%m')
                        registration_months[month] = registration_months.get(month, 0) + 1
                    except:
                        continue
            
            # Get recent activity
            recent_users = []
            for user_id, user in users.items():
                if 'updated_at' in user:
                    try:
                        updated_at = datetime.fromisoformat(user['updated_at'])
                        if (datetime.now() - updated_at).days <= 7:
                            recent_users.append(user_id)
                    except:
                        continue
            
            stats = {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': inactive_users,
                'registration_by_month': registration_months,
                'recently_active_users': len(recent_users),
                'repository_metadata': data.get('metadata', {})
            }
            
            logger.info(f"User statistics generated: {total_users} total users")
            return {
                'success': True,
                'statistics': stats
            }
            
        except Exception as e:
            logger.error(f"Failed to generate user statistics: {e}")
            return {
                'success': False,
                'error': f'Failed to generate user statistics: {str(e)}'
            }
    
    def export_user_data(self, export_format: str = "json", 
                         include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Export user data in various formats
        
        Args:
            export_format: Export format ("json", "csv")
            include_sensitive: Whether to include sensitive data
            
        Returns:
            Dictionary with export result
        """
        try:
            # Get all users
            all_users_result = self.get_all_users()
            if not all_users_result['success']:
                return all_users_result
            
            users = all_users_result['data']
            
            # Filter sensitive data if requested
            if not include_sensitive:
                for user in users:
                    # Remove sensitive fields
                    sensitive_fields = ['face_embeddings', 'face_quality_score']
                    for field in sensitive_fields:
                        if field in user:
                            del user[field]
            
            # Export based on format
            if export_format == "json":
                export_data = json.dumps(users, indent=2, default=str)
                filename = f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            elif export_format == "csv":
                df = pd.DataFrame(users)
                export_data = df.to_csv(index=False)
                filename = f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            else:
                return {
                    'success': False,
                    'error': f'Unsupported export format: {export_format}'
                }
            
            # Save export file
            export_path = Path("data/exports") / filename
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, 'w') as f:
                f.write(export_data)
            
            logger.info(f"User data exported to {filename}")
            return {
                'success': True,
                'filename': filename,
                'export_path': str(export_path),
                'export_format': export_format,
                'total_users': len(users),
                'include_sensitive': include_sensitive
            }
            
        except Exception as e:
            logger.error(f"User data export failed: {e}")
            return {
                'success': False,
                'error': f'User data export failed: {str(e)}'
            }
    
    def backup_user_data(self, backup_name: str = None) -> Dict[str, Any]:
        """
        Create a backup of user data
        
        Args:
            backup_name: Optional name for the backup
            
        Returns:
            Dictionary with backup result
        """
        try:
            if backup_name is None:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create backup directory
            backup_dir = Path("data/faces/backups")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy current file to backup
            backup_path = backup_dir / f"{backup_name}.json"
            
            import shutil
            shutil.copy2(self.data_file, backup_path)
            
            logger.info(f"User data backed up to {backup_path}")
            return {
                'success': True,
                'backup_name': backup_name,
                'backup_path': str(backup_path),
                'backup_size': backup_path.stat().st_size,
                'backup_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"User data backup failed: {e}")
            return {
                'success': False,
                'error': f'User data backup failed: {str(e)}'
            }
    
    def restore_user_data(self, backup_path: str) -> Dict[str, Any]:
        """
        Restore user data from backup
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            Dictionary with restore result
        """
        try:
            backup_file = Path(backup_path)
            
            if not backup_file.exists():
                return {
                    'success': False,
                    'error': f'Backup file not found: {backup_path}'
                }
            
            # Create current backup before restore
            current_backup = self.backup_user_data("pre_restore_backup")
            if not current_backup['success']:
                return {
                    'success': False,
                    'error': f'Failed to create current backup: {current_backup["error"]}'
                }
            
            # Restore from backup
            import shutil
            shutil.copy2(backup_file, self.data_file)
            
            logger.info(f"User data restored from {backup_path}")
            return {
                'success': True,
                'restored_from': backup_path,
                'current_backup': current_backup['backup_path'],
                'restore_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"User data restore failed: {e}")
            return {
                'success': False,
                'error': f'User data restore failed: {str(e)}'
            }
