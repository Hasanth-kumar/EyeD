"""
User domain entity.

Represents a user in the EyeD AI Attendance System.
This is a pure domain entity with no infrastructure dependencies.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class User:
    """
    Immutable user entity.
    
    Attributes:
        user_id: Unique identifier for the user.
        username: Username for the user.
        first_name: Optional first name of the user.
        last_name: Optional last name of the user.
        email: Optional email address of the user.
        registration_date: Date and time when the user was registered.
        status: User status, either 'active' or 'inactive'.
    
    Examples:
        >>> from datetime import datetime
        >>> user = User(
        ...     user_id="user_001",
        ...     username="john_doe",
        ...     first_name="John",
        ...     last_name="Doe",
        ...     email="john@example.com",
        ...     registration_date=datetime.now(),
        ...     status="active"
        ... )
        >>> user.user_id
        'user_001'
    """
    
    user_id: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    registration_date: datetime
    status: str
    
    def is_active(self) -> bool:
        """
        Check if the user is active.
        
        Returns:
            True if user status is 'active', False otherwise.
        """
        return self.status.lower() == 'active'
    
    def get_full_name(self) -> str:
        """
        Get the full name of the user.
        
        Returns:
            Full name combining first_name and last_name, or username if names are not available.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username













