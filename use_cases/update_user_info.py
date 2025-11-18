"""
Update user info use case.

Orchestrates user information update workflow.
"""

from dataclasses import dataclass
from typing import Optional, Protocol, Dict, Any
from datetime import datetime

from domain.entities.user import User
from domain.shared.exceptions import UserNotFoundError


@dataclass
class UpdateUserInfoRequest:
    """Request for updating user information."""
    user_id: str
    updates: Dict[str, Any]


@dataclass
class UpdateUserInfoResponse:
    """Response from updating user information."""
    success: bool
    user: Optional[User] = None
    error: Optional[str] = None


class UserRepositoryProtocol(Protocol):
    """Protocol for user repository operations."""
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user by ID. Returns dict with 'success' and 'data' keys."""
        ...
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user. Returns dict with 'success' key."""
        ...


class UpdateUserInfoUseCase:
    """
    Orchestrates user information update workflow.
    
    This use case coordinates user data retrieval, validation, update,
    and persistence to update user information.
    """
    
    # Allowed fields that can be updated
    ALLOWED_UPDATE_FIELDS = {
        'username',
        'user_name',  # Support both naming conventions
        'first_name',
        'last_name',
        'email',
        'status'
    }
    
    # Fields that cannot be updated
    PROTECTED_FIELDS = {
        'user_id',
        'registration_date',
        'created_at',
        'updated_at'
    }
    
    def __init__(self, user_repository: UserRepositoryProtocol):
        """
        Initialize UpdateUserInfoUseCase.
        
        Args:
            user_repository: User data persistence repository.
        """
        self.user_repository = user_repository
    
    def execute(self, request: UpdateUserInfoRequest) -> UpdateUserInfoResponse:
        """
        Execute user information update workflow.
        
        Args:
            request: Update user info request with user_id and updates dict.
        
        Returns:
            UpdateUserInfoResponse with updated user information.
        """
        try:
            # Step 1: Get existing user
            user = self._get_user(request.user_id)
            if user is None:
                raise UserNotFoundError(user_id=request.user_id)
            
            # Step 2: Validate updates
            validation_result = self._validate_updates(request.updates)
            if not validation_result['valid']:
                return UpdateUserInfoResponse(
                    success=False,
                    error=validation_result['error']
                )
            
            # Step 3: Update user entity (create new immutable instance)
            updated_user = self._update_user_entity(user, request.updates)
            
            # Step 4: Save updated user (convert entity to dict for repository)
            update_dict = self._prepare_update_dict(request.updates)
            update_result = self.user_repository.update_user(
                request.user_id,
                update_dict
            )
            
            if not update_result.get('success', False):
                error_msg = update_result.get('error', 'Failed to update user')
                return UpdateUserInfoResponse(
                    success=False,
                    error=error_msg
                )
            
            # Step 5: Return updated user
            return UpdateUserInfoResponse(
                success=True,
                user=updated_user
            )
            
        except UserNotFoundError:
            # Re-raise domain exceptions
            raise
        except Exception as e:
            # Handle unexpected errors
            return UpdateUserInfoResponse(
                success=False,
                error=f"Unexpected error during user update: {str(e)}"
            )
    
    def _get_user(self, user_id: str) -> Optional[User]:
        """
        Get user from repository and convert to User entity.
        
        Args:
            user_id: ID of the user to retrieve.
        
        Returns:
            User domain entity, or None if not found.
        """
        result = self.user_repository.get_user(user_id)
        if not result.get('success', False) or result.get('data') is None:
            return None
        
        user_data = result['data']
        return self._dict_to_user_entity(user_data)
    
    def _validate_updates(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that updates only contain allowed fields.
        
        Args:
            updates: Dictionary of fields to update.
        
        Returns:
            Dictionary with 'valid' boolean and optional 'error' message.
        """
        if not updates:
            return {
                'valid': False,
                'error': 'No updates provided'
            }
        
        # Check for protected fields
        protected_in_updates = set(updates.keys()) & self.PROTECTED_FIELDS
        if protected_in_updates:
            return {
                'valid': False,
                'error': f"Cannot update protected fields: {', '.join(protected_in_updates)}"
            }
        
        # Check for allowed fields (support both naming conventions)
        allowed_keys = set(updates.keys())
        # Normalize 'user_name' to 'username' for validation
        normalized_keys = {k if k != 'user_name' else 'username' for k in allowed_keys}
        
        invalid_fields = normalized_keys - self.ALLOWED_UPDATE_FIELDS
        if invalid_fields:
            return {
                'valid': False,
                'error': f"Invalid fields for update: {', '.join(invalid_fields)}"
            }
        
        # Validate status values if status is being updated
        if 'status' in updates:
            status_value = updates['status']
            if status_value not in ['active', 'inactive']:
                return {
                    'valid': False,
                    'error': f"Invalid status value: {status_value}. Must be 'active' or 'inactive'"
                }
        
        return {'valid': True}
    
    def _update_user_entity(self, user: User, updates: Dict[str, Any]) -> User:
        """
        Create updated User entity with new values.
        
        Since User is immutable (frozen dataclass), we create a new instance.
        
        Args:
            user: Existing User entity.
            updates: Dictionary of fields to update.
        
        Returns:
            Updated User domain entity.
        """
        # Build new user data from existing user
        user_data = {
            'user_id': user.user_id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'registration_date': user.registration_date,
            'status': user.status
        }
        
        # Apply updates
        for key, value in updates.items():
            if key == 'user_name':
                # Normalize 'user_name' to 'username'
                user_data['username'] = value
            elif key in self.ALLOWED_UPDATE_FIELDS:
                user_data[key] = value
        
        # Create new User entity
        return User(
            user_id=user_data['user_id'],
            username=user_data['username'],
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            email=user_data.get('email'),
            registration_date=user_data['registration_date'],
            status=user_data.get('status', 'active')
        )
    
    def _prepare_update_dict(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare update dictionary for repository.
        
        Normalizes field names and ensures proper format for repository.
        
        Args:
            updates: Dictionary of fields to update.
        
        Returns:
            Dictionary formatted for repository update.
        """
        update_dict = {}
        
        for key, value in updates.items():
            if key == 'user_name':
                # Normalize to repository format
                update_dict['user_name'] = value
            elif key in self.ALLOWED_UPDATE_FIELDS:
                update_dict[key] = value
        
        return update_dict
    
    def _dict_to_user_entity(self, user_data: Dict[str, Any]) -> User:
        """
        Convert user dictionary to User entity.
        
        Args:
            user_data: Dictionary representation of user.
        
        Returns:
            User domain entity.
        """
        # Parse registration date
        registration_date = datetime.now()
        if 'registration_date' in user_data:
            reg_date_str = user_data['registration_date']
            if isinstance(reg_date_str, str):
                try:
                    registration_date = datetime.fromisoformat(reg_date_str)
                except ValueError:
                    registration_date = datetime.now()
            elif isinstance(reg_date_str, datetime):
                registration_date = reg_date_str
        elif 'created_at' in user_data:
            # Fallback to created_at if registration_date not available
            created_at_str = user_data['created_at']
            if isinstance(created_at_str, str):
                try:
                    registration_date = datetime.fromisoformat(created_at_str)
                except ValueError:
                    registration_date = datetime.now()
            elif isinstance(created_at_str, datetime):
                registration_date = created_at_str
        
        return User(
            user_id=user_data.get('user_id', ''),
            username=user_data.get('user_name') or user_data.get('username', ''),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            email=user_data.get('email'),
            registration_date=registration_date,
            status=user_data.get('status', 'active')
        )

