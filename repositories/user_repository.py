"""
User Repository for EyeD AI Attendance System.

This module handles data persistence for user operations,
following the Single-Responsibility Principle and Dependency Injection.

The repository implements the UserRepositoryProtocol and works with
the User domain entity from domain/entities/user.py.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from domain.entities.user import User
from infrastructure.storage.file_storage import FileStorage

logger = logging.getLogger(__name__)


class UserRepository:
    """
    Repository for user data persistence.
    
    This class handles ONLY user data persistence (CRUD operations).
    It follows SRP by delegating file I/O to FileStorage and working
    with User domain entities.
    """
    
    def __init__(self, storage_handler: FileStorage, data_file: str = "data/faces/faces.json"):
        """
        Initialize user repository.
        
        Args:
            storage_handler: Injected file storage handler for file operations
            data_file: Path to user data file (JSON format)
        """
        if storage_handler is None:
            raise ValueError("storage_handler cannot be None")
        
        self.storage_handler = storage_handler
        self.data_file = data_file
        
        # Initialize file if it doesn't exist
        if not self.storage_handler.file_exists(self.data_file):
            self._initialize_file()
        
        logger.info(f"UserRepository initialized with file: {self.data_file}")
    
    def _initialize_file(self) -> None:
        """
        Initialize empty user file with basic structure.
        
        Creates a JSON file with the structure:
        {
            "users": {},
            "metadata": {}
        }
        """
        initial_data = {
            "users": {},
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "total_users": 0
            }
        }
        
        json_content = json.dumps(initial_data, indent=2)
        success = self.storage_handler.write_text_file(self.data_file, json_content)
        
        if not success:
            logger.error(f"Failed to initialize user data file: {self.data_file}")
            raise IOError(f"Failed to initialize user data file: {self.data_file}")
        
        logger.debug(f"Initialized empty user data file: {self.data_file}")
    
    def _load_data(self) -> Dict[str, Any]:
        """
        Load user data from file.
        
        Returns:
            Dictionary containing user data (preserves all top-level keys for legacy format)
            
        Raises:
            IOError: If file cannot be read or parsed
        """
        try:
            content = self.storage_handler.read_text_file(self.data_file)
            data = json.loads(content)
            
            # Ensure metadata exists (but preserve all other top-level keys for legacy format)
            if "metadata" not in data:
                data["metadata"] = {}
            
            # Keep "users" section for backward compatibility during migration
            if "users" not in data:
                data["users"] = {}
            
            return data
        except FileNotFoundError:
            # File doesn't exist, initialize it
            self._initialize_file()
            return self._load_data()
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {self.data_file}: {e}")
            raise IOError(f"Invalid JSON format in {self.data_file}: {e}")
        except Exception as e:
            logger.error(f"Failed to load user data from {self.data_file}: {e}")
            raise IOError(f"Failed to load user data: {e}")
    
    def _save_data(self, data: Dict[str, Any]) -> bool:
        """
        Save user data to file.
        
        Args:
            data: Dictionary containing user data to save
            
        Returns:
            True on success, False on failure
        """
        try:
            # Update metadata
            if "metadata" not in data:
                data["metadata"] = {}
            
            # Count legacy format users (top-level keys with "name" and "embedding")
            legacy_users = [k for k in data.keys() 
                          if k not in ["users", "metadata"] 
                          and isinstance(data.get(k), dict)
                          and "name" in data.get(k, {})
                          and "embedding" in data.get(k, {})]
            
            # Count new format users in "users" section
            new_format_users = len(data.get("users", {}))
            
            # Total users = legacy + new format
            total_users = len(legacy_users) + new_format_users
            
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            data["metadata"]["total_users"] = total_users
            
            json_content = json.dumps(data, indent=2, default=str)
            return self.storage_handler.write_text_file(self.data_file, json_content)
        except Exception as e:
            logger.error(f"Failed to save user data to {self.data_file}: {e}")
            return False
    
    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """
        Convert User entity to storage format dictionary.
        
        Args:
            user: User domain entity
            
        Returns:
            Dictionary representation for storage
        """
        return {
            "user_id": user.user_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "registration_date": user.registration_date.isoformat(),
            "status": user.status
        }
    
    def _is_legacy_user(self, user_data: Dict[str, Any]) -> bool:
        """
        Check if user data is in legacy format.
        
        Args:
            user_data: User data dictionary
            
        Returns:
            True if legacy format (has "name" and "embedding"), False otherwise
        """
        return isinstance(user_data, dict) and "name" in user_data and "embedding" in user_data
    
    def _legacy_to_user_dict(self, user_id: str, legacy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert legacy format to User entity format.
        
        Args:
            user_id: User ID (top-level key)
            legacy_data: Legacy format user data with "name", "embedding", etc.
            
        Returns:
            Dictionary in User entity format
        """
        # Parse name into first_name and last_name
        name = legacy_data.get("name", "")
        name_parts = name.split(maxsplit=1) if name else []
        first_name = name_parts[0] if len(name_parts) > 0 else None
        last_name = name_parts[1] if len(name_parts) > 1 else None
        
        # Parse registration_date
        registration_date = legacy_data.get("registration_date")
        if isinstance(registration_date, str):
            try:
                registration_date = datetime.fromisoformat(registration_date)
            except ValueError:
                registration_date = datetime.now()
        elif not isinstance(registration_date, datetime):
            registration_date = datetime.now()
        
        return {
            "user_id": user_id,
            "username": name,  # Use full name as username in legacy format
            "first_name": first_name,
            "last_name": last_name,
            "email": None,  # Legacy format doesn't have email
            "registration_date": registration_date.isoformat() if isinstance(registration_date, datetime) else registration_date,
            "status": "active"  # Default status for legacy users
        }
    
    def _user_dict_to_legacy(self, user_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert User entity format to legacy format.
        
        Args:
            user_dict: User data in entity format
            
        Returns:
            Dictionary in legacy format
        """
        # Combine first_name and last_name into name
        first_name = user_dict.get("first_name", "")
        last_name = user_dict.get("last_name", "")
        if first_name and last_name:
            name = f"{first_name} {last_name}"
        elif first_name:
            name = first_name
        elif last_name:
            name = last_name
        else:
            name = user_dict.get("username", user_dict.get("user_id", ""))
        
        registration_date = user_dict.get("registration_date")
        if isinstance(registration_date, str):
            try:
                registration_date = datetime.fromisoformat(registration_date).isoformat()
            except ValueError:
                registration_date = datetime.now().isoformat()
        elif isinstance(registration_date, datetime):
            registration_date = registration_date.isoformat()
        else:
            registration_date = datetime.now().isoformat()
        
        return {
            "name": name,
            "registration_date": registration_date,
            # Note: embedding and image_path should be added separately by FaceRepository
            # face_bbox can be added if available
        }
    
    def _dict_to_user(self, user_dict: Dict[str, Any]) -> User:
        """
        Convert storage format dictionary to User entity.
        
        Args:
            user_dict: Dictionary from storage (either legacy or new format)
        
        Returns:
            User domain entity
        """
        # Parse registration_date
        registration_date = user_dict.get("registration_date")
        if isinstance(registration_date, str):
            try:
                registration_date = datetime.fromisoformat(registration_date)
            except ValueError:
                registration_date = datetime.now()
        elif not isinstance(registration_date, datetime):
            # Fallback to current time if invalid
            registration_date = datetime.now()
        
        return User(
            user_id=user_dict.get("user_id", ""),
            username=user_dict.get("username", ""),
            first_name=user_dict.get("first_name"),
            last_name=user_dict.get("last_name"),
            email=user_dict.get("email"),
            registration_date=registration_date,
            status=user_dict.get("status", "active")
        )
    
    def add_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Persist new user data in legacy format (top-level key).
        
        Args:
            user_data: Dictionary containing user data to persist
            
        Returns:
            Dictionary with 'success' (bool) key, and optionally 'error' (str) key
        """
        try:
            data = self._load_data()
            
            # Extract user_id from user_data
            user_id = user_data.get("user_id")
            if not user_id:
                return {
                    "success": False,
                    "error": "user_id is required"
                }
            
            # Check if user already exists (legacy format or new format)
            if user_id in data and self._is_legacy_user(data[user_id]):
                logger.warning(f"User {user_id} already exists in legacy format")
                return {
                    "success": False,
                    "error": f"User {user_id} already exists"
                }
            
            if user_id in data.get("users", {}):
                logger.warning(f"User {user_id} already exists in new format")
                return {
                    "success": False,
                    "error": f"User {user_id} already exists"
                }
            
            # Convert to legacy format and save as top-level key
            legacy_data = self._user_dict_to_legacy(user_data)
            data[user_id] = legacy_data
            
            # Save to file
            success = self._save_data(data)
            
            if success:
                logger.info(f"User {user_id} added successfully in legacy format")
                return {
                    "success": True
                }
            else:
                logger.error(f"Failed to save user {user_id}")
                return {
                    "success": False,
                    "error": "Failed to save user data"
                }
            
        except Exception as e:
            logger.error(f"Failed to add user: {e}")
            return {
                "success": False,
                "error": f"Failed to add user: {str(e)}"
            }
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve user by ID from legacy format (top-level key) or new format ("users" section).
        
        Returns dict with 'success' and 'data' keys (per UserRepositoryProtocol).
        
        Args:
            user_id: User ID to retrieve
            
        Returns:
            Dictionary with 'success' (bool) and 'data' (user dict or None) keys
        """
        try:
            data = self._load_data()
            
            # Check legacy format first (top-level key)
            if user_id in data and self._is_legacy_user(data[user_id]):
                legacy_data = data[user_id]
                user_dict = self._legacy_to_user_dict(user_id, legacy_data)
                logger.debug(f"User {user_id} retrieved from legacy format")
                return {
                    "success": True,
                    "data": user_dict
                }
            
            # Check new format ("users" section)
            if user_id in data.get("users", {}):
                user_dict = data["users"][user_id]
                logger.debug(f"User {user_id} retrieved from new format")
                return {
                    "success": True,
                    "data": user_dict
                }
            
            logger.debug(f"User {user_id} not found")
            return {
                "success": False,
                "data": None
            }
            
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return {
                "success": False,
                "data": None
            }
    
    def update_user(self, user_id: str, user: User) -> bool:
        """
        Update existing user in legacy format.
        
        Args:
            user_id: User ID to update
            user: Updated User domain entity
        
        Returns:
            True on success, False on failure
        """
        try:
            data = self._load_data()
            
            # Ensure user_id matches
            if user.user_id != user_id:
                logger.warning(f"User ID mismatch: {user_id} != {user.user_id}")
                return False
            
            # Check if user exists in legacy format
            if user_id in data and self._is_legacy_user(data[user_id]):
                # Update legacy format user (preserve embedding and image_path)
                legacy_data = data[user_id]
                updated_legacy = self._user_dict_to_legacy(self._user_to_dict(user))
                # Preserve existing embedding and image_path
                if "embedding" in legacy_data:
                    updated_legacy["embedding"] = legacy_data["embedding"]
                if "image_path" in legacy_data:
                    updated_legacy["image_path"] = legacy_data["image_path"]
                if "face_bbox" in legacy_data:
                    updated_legacy["face_bbox"] = legacy_data["face_bbox"]
                
                data[user_id] = updated_legacy
            # Check if user exists in new format
            elif user_id in data.get("users", {}):
                # Migrate from new format to legacy format
                user_dict = self._user_to_dict(user)
                legacy_data = self._user_dict_to_legacy(user_dict)
                data[user_id] = legacy_data
                # Remove from "users" section
                del data["users"][user_id]
            else:
                logger.warning(f"User {user_id} not found for update")
                return False
            
            # Save to file
            success = self._save_data(data)
            
            if success:
                logger.info(f"User {user_id} updated successfully in legacy format")
            else:
                logger.error(f"Failed to save updated user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete user by ID from legacy format or new format.
        
        Args:
            user_id: User ID to delete
        
        Returns:
            True on success, False on failure
        """
        try:
            data = self._load_data()
            
            deleted = False
            
            # Check if user exists in legacy format (top-level key)
            if user_id in data and self._is_legacy_user(data[user_id]):
                del data[user_id]
                deleted = True
            # Check if user exists in new format ("users" section)
            elif user_id in data.get("users", {}):
                del data["users"][user_id]
                deleted = True
            
            if not deleted:
                logger.warning(f"User {user_id} not found for deletion")
                return False
            
            # Save to file
            success = self._save_data(data)
            
            if success:
                logger.info(f"User {user_id} deleted successfully")
            else:
                logger.error(f"Failed to save after deleting user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            return False
    
    def get_all_users(self, include_inactive: bool = True) -> Dict[str, Any]:
        """
        Retrieve all users from legacy format (top-level keys) and new format ("users" section).
        
        Args:
            include_inactive: Whether to include inactive users (legacy users are always active)
        
        Returns:
            Dictionary with 'success', 'data' (list of user dicts), and optional 'error' keys.
            Format: {'success': bool, 'data': [dict, ...], 'error': str | None}
        """
        try:
            data = self._load_data()
            users = []
            
            # Read legacy format users (top-level keys with "name" and "embedding")
            for key, value in data.items():
                if key in ["users", "metadata"]:
                    continue
                
                if self._is_legacy_user(value):
                    # Convert legacy format to User entity
                    try:
                        user_dict = self._legacy_to_user_dict(key, value)
                        user = self._dict_to_user(user_dict)
                        # Legacy users are always active, so skip inactive filter
                        users.append(user)
                    except Exception as e:
                        logger.warning(f"Failed to convert legacy user {key} to entity: {e}")
                        continue
            
            # Read new format users from "users" section (for backward compatibility during migration)
            for user_id, user_dict in data.get("users", {}).items():
                # Skip if already added as legacy user
                if any(u.user_id == user_id for u in users):
                    continue
                
                # Filter inactive users if requested
                if not include_inactive:
                    status = user_dict.get("status", "active")
                    if status.lower() != "active":
                        continue
                
                # Convert to User entity
                try:
                    user = self._dict_to_user(user_dict)
                    users.append(user)
                except Exception as e:
                    logger.warning(f"Failed to convert user {user_id} to entity: {e}")
                    continue
            
            # Convert User entities to dictionaries for the use case
            user_dicts = []
            for user in users:
                # Ensure registration_date is in ISO 8601 format with timezone
                if user.registration_date:
                    # If datetime is naive (no timezone), make it timezone-aware (UTC)
                    reg_date = user.registration_date
                    if reg_date.tzinfo is None:
                        # Naive datetime - assume UTC
                        reg_date = reg_date.replace(tzinfo=timezone.utc)
                    registration_date_str = reg_date.isoformat()
                else:
                    # Use current UTC time
                    registration_date_str = datetime.now(timezone.utc).isoformat()
                
                user_dict = {
                    'user_id': user.user_id,
                    'user_name': user.username,  # Use 'user_name' for compatibility
                    'username': user.username,    # Also include 'username'
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'registration_date': registration_date_str,
                    'status': user.status
                }
                user_dicts.append(user_dict)
            
            logger.info(f"Retrieved {len(user_dicts)} users (include_inactive={include_inactive})")
            return {
                'success': True,
                'data': user_dicts,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Failed to get all users: {e}")
            return {
                'success': False,
                'data': [],
                'error': str(e)
            }
    
    def search_users(self, search_term: str, search_fields: List[str] = None) -> List[User]:
        """
        Search users by various criteria.
        
        Args:
            search_term: Term to search for
            search_fields: Fields to search in (default: ['user_id', 'username', 'first_name', 'last_name', 'email'])
            
        Returns:
            List of matching User domain entities
        """
        try:
            if search_fields is None:
                search_fields = ['user_id', 'username', 'first_name', 'last_name', 'email']
            
            # Get all users (now returns dict with 'success', 'data', 'error')
            result = self.get_all_users(include_inactive=True)
            
            if not result.get('success', False):
                logger.warning(f"Failed to get users for search: {result.get('error', 'Unknown error')}")
                return []
            
            # Extract user dictionaries and convert to User entities
            user_dicts = result.get('data', [])
            all_users = [self._dict_to_user(user_dict) for user_dict in user_dicts]
            
            search_term_lower = search_term.lower()
            matching_users = []
            
            for user in all_users:
                for field in search_fields:
                    field_value = None
                    
                    if field == 'user_id':
                        field_value = user.user_id
                    elif field == 'username':
                        field_value = user.username
                    elif field == 'first_name':
                        field_value = user.first_name
                    elif field == 'last_name':
                        field_value = user.last_name
                    elif field == 'email':
                        field_value = user.email
                    
                    if field_value and search_term_lower in str(field_value).lower():
                        matching_users.append(user)
                        break  # Found a match, no need to check other fields
            
            logger.info(f"Search for '{search_term}' returned {len(matching_users)} results")
            return matching_users
            
        except Exception as e:
            logger.error(f"User search failed: {e}")
            return []
    
    def user_exists(self, user_id: str) -> bool:
        """
        Check if user exists in legacy format or new format.
        
        Args:
            user_id: User ID to check
        
        Returns:
            True if exists, False otherwise
        """
        try:
            data = self._load_data()
            
            # Check legacy format (top-level key)
            if user_id in data and self._is_legacy_user(data[user_id]):
                logger.debug(f"User {user_id} exists in legacy format")
                return True
            
            # Check new format ("users" section)
            exists = user_id in data.get("users", {})
            logger.debug(f"User {user_id} exists: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Failed to check if user {user_id} exists: {e}")
            return False

