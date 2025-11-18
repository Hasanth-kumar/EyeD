"""
User report generator.

Generates user-specific attendance reports.
"""

from typing import List, Dict, Any, Protocol, TYPE_CHECKING
from domain.entities.attendance_record import AttendanceRecord
from domain.services.analytics.metrics_calculator import MetricsCalculator

if TYPE_CHECKING:
    from use_cases.generate_report import GenerateReportRequest


class UserRepositoryProtocol(Protocol):
    """Protocol for user repository operations."""
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user by ID. Returns dict with 'success' and 'data' keys."""
        ...


class UserReportGenerator:
    """Generates user-specific attendance reports."""
    
    def __init__(
        self,
        metrics_calculator: MetricsCalculator,
        user_repository: UserRepositoryProtocol
    ):
        """
        Initialize user report generator.
        
        Args:
            metrics_calculator: Service for calculating attendance metrics
            user_repository: Repository for user data
        """
        self.metrics_calculator = metrics_calculator
        self.user_repository = user_repository
    
    def generate(
        self,
        records: List[AttendanceRecord],
        request: 'GenerateReportRequest'
    ) -> Dict[str, Any]:
        """
        Generate user-specific attendance report.
        
        Args:
            records: List of attendance records
            request: Report generation request (must include user_id)
            
        Returns:
            Dictionary containing user report data
            
        Raises:
            ValueError: If user_id is not provided in request
        """
        if not request.user_id:
            raise ValueError("user_id is required for user report")
        
        if not records:
            return {
                "report_type": "user",
                "user_id": request.user_id,
                "user_performance": None,
                "total_records": 0
            }
        
        # Calculate period days
        period_days = 30  # Default
        if request.start_date and request.end_date:
            period_days = (request.end_date - request.start_date).days + 1
        
        # Calculate user performance
        user_performance = self.metrics_calculator.calculate_user_performance(
            request.user_id, records, period_days
        )
        
        # Get user info
        user_info = None
        user_result = self.user_repository.get_user(request.user_id)
        if user_result.get('success', False) and user_result.get('data'):
            user_info = user_result['data']
        
        return {
            "report_type": "user",
            "user_id": request.user_id,
            "user_info": user_info,
            "user_performance": {
                "user_id": user_performance.user_id,
                "total_attendance": user_performance.total_attendance,
                "attendance_rate": user_performance.attendance_rate,
                "average_confidence": user_performance.average_confidence,
                "best_streak": user_performance.best_streak,
                "current_streak": user_performance.current_streak
            },
            "total_records": len(records)
        }

