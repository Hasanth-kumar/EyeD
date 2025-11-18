"""
Get user info use case.

Orchestrates user information retrieval workflow with optional performance metrics.
"""

from dataclasses import dataclass
from typing import Optional, Protocol, Dict, Any, List
from datetime import datetime, date, timedelta

from domain.entities.user import User
from domain.entities.attendance_record import AttendanceRecord
from domain.services.analytics import MetricsCalculator, UserPerformance
from domain.shared.exceptions import UserNotFoundError


@dataclass
class GetUserInfoRequest:
    """Request for getting user information."""
    user_id: str
    include_performance: bool = False


@dataclass
class GetUserInfoResponse:
    """Response from getting user information."""
    success: bool
    user: Optional[User] = None
    performance: Optional[UserPerformance] = None
    error: Optional[str] = None


class UserRepositoryProtocol(Protocol):
    """Protocol for user repository operations."""
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user by ID. Returns dict with 'success' and 'data' keys."""
        ...


class AttendanceRepositoryProtocol(Protocol):
    """Protocol for attendance repository operations."""
    
    def get_attendance_history(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[AttendanceRecord]:
        """Get attendance history. Returns list of AttendanceRecord domain entities."""
        ...


class GetUserInfoUseCase:
    """
    Orchestrates user information retrieval workflow.
    
    This use case coordinates user data retrieval and optional performance
    metrics calculation to provide comprehensive user information.
    """
    
    def __init__(
        self,
        user_repository: UserRepositoryProtocol,
        attendance_repository: AttendanceRepositoryProtocol,
        metrics_calculator: Optional[MetricsCalculator] = None
    ):
        """
        Initialize GetUserInfoUseCase.
        
        Args:
            user_repository: User data persistence repository.
            attendance_repository: Attendance data persistence repository.
            metrics_calculator: Optional metrics calculator for performance metrics.
                               If None, MetricsCalculator will be used as static class.
        """
        self.user_repository = user_repository
        self.attendance_repository = attendance_repository
        self.metrics_calculator = metrics_calculator
    
    def execute(self, request: GetUserInfoRequest) -> GetUserInfoResponse:
        """
        Execute user information retrieval workflow.
        
        Args:
            request: Get user info request with user_id and optional performance flag.
        
        Returns:
            GetUserInfoResponse with user information and optional performance data.
        """
        try:
            # Step 1: Get user from repository
            user = self._get_user(request.user_id)
            if user is None:
                raise UserNotFoundError(user_id=request.user_id)
            
            # Step 2-3: Get attendance records and calculate performance (if requested)
            performance = None
            if request.include_performance:
                attendance_records = self._get_attendance_records(request.user_id)
                performance = self._calculate_performance(request.user_id, attendance_records)
            
            # Step 4: Return user info with optional performance data
            return GetUserInfoResponse(
                success=True,
                user=user,
                performance=performance
            )
            
        except UserNotFoundError:
            # Re-raise domain exceptions
            raise
        except Exception as e:
            # Handle unexpected errors
            return GetUserInfoResponse(
                success=False,
                error=f"Unexpected error during user info retrieval: {str(e)}"
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
    
    def _get_attendance_records(self, user_id: str) -> List[AttendanceRecord]:
        """
        Get attendance records for the user.
        
        Args:
            user_id: ID of the user to get attendance records for.
        
        Returns:
            List of AttendanceRecord domain entities.
        """
        # Get attendance records for the last 30 days for performance calculation
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        return self.attendance_repository.get_attendance_history(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
    
    def _calculate_performance(
        self,
        user_id: str,
        records: List[AttendanceRecord]
    ) -> UserPerformance:
        """
        Calculate performance metrics for the user.
        
        Args:
            user_id: ID of the user to calculate performance for.
            records: List of attendance records for the user.
        
        Returns:
            UserPerformance value object with calculated metrics.
        """
        # Use provided metrics calculator or static method
        if self.metrics_calculator is not None:
            return self.metrics_calculator.calculate_user_performance(
                user_id=user_id,
                records=records,
                period_days=30
            )
        else:
            return MetricsCalculator.calculate_user_performance(
                user_id=user_id,
                records=records,
                period_days=30
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
        
        return User(
            user_id=user_data.get('user_id', ''),
            username=user_data.get('user_name') or user_data.get('username', ''),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            email=user_data.get('email'),
            registration_date=registration_date,
            status=user_data.get('status', 'active')
        )

