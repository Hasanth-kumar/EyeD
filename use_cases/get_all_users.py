"""
Get all users use case.

Orchestrates retrieval of all users workflow.
"""

from dataclasses import dataclass, field
from typing import Optional, Protocol, Dict, Any, List
from datetime import datetime

from domain.entities.user import User


@dataclass
class GetAllUsersRequest:
    """Request for getting all users."""
    include_inactive: bool = False


@dataclass
class GetAllUsersResponse:
    """Response from getting all users."""
    success: bool
    users: List[User] = field(default_factory=list)
    error: Optional[str] = None


class UserRepositoryProtocol(Protocol):
    """Protocol for user repository operations."""
    
    def get_all_users(self, include_inactive: bool = True) -> Dict[str, Any]:
        """Get all users. Returns dict with 'success', 'data' (list of user dicts), and optional 'error' keys."""
        ...


class GetAllUsersUseCase:
    """
    Orchestrates all users retrieval workflow.
    
    This use case coordinates user data retrieval from the repository
    and converts the data to User domain entities.
    """
    
    def __init__(self, user_repository: UserRepositoryProtocol):
        """
        Initialize GetAllUsersUseCase.
        
        Args:
            user_repository: User data persistence repository.
        """
        self.user_repository = user_repository
    
    def execute(self, request: GetAllUsersRequest) -> GetAllUsersResponse:
        """
        Execute all users retrieval workflow.
        
        Args:
            request: Get all users request with optional include_inactive flag.
        
        Returns:
            GetAllUsersResponse with list of User entities.
        """
        try:
            # Step 1: Get all users from repository
            result = self.user_repository.get_all_users(
                include_inactive=request.include_inactive
            )
            
            if not result.get('success', False):
                error_msg = result.get('error', 'Failed to retrieve users')
                return GetAllUsersResponse(
                    success=False,
                    users=[],
                    error=error_msg
                )
            
            # Step 2: Convert user dicts to User entities
            user_data_list = result.get('data', [])
            users = [self._dict_to_user_entity(user_data) for user_data in user_data_list]
            
            # Step 3: Return list of users
            return GetAllUsersResponse(
                success=True,
                users=users
            )
            
        except Exception as e:
            # Handle unexpected errors
            return GetAllUsersResponse(
                success=False,
                users=[],
                error=f"Unexpected error during users retrieval: {str(e)}"
            )
    
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

