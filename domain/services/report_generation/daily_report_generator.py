"""
Daily report generator.

Generates daily attendance summary reports.
"""

from typing import List, Dict, Any, TYPE_CHECKING
from domain.entities.attendance_record import AttendanceRecord
from domain.services.analytics.metrics_calculator import MetricsCalculator

if TYPE_CHECKING:
    from use_cases.generate_report import GenerateReportRequest


class DailyReportGenerator:
    """Generates daily attendance summary reports."""
    
    def __init__(self, metrics_calculator: MetricsCalculator):
        """
        Initialize daily report generator.
        
        Args:
            metrics_calculator: Service for calculating attendance metrics
        """
        self.metrics_calculator = metrics_calculator
    
    def generate(
        self,
        records: List[AttendanceRecord],
        request: 'GenerateReportRequest'
    ) -> Dict[str, Any]:
        """
        Generate daily attendance summary report.
        
        Args:
            records: List of attendance records
            request: Report generation request
            
        Returns:
            Dictionary containing daily report data
        """
        if not records:
            return {"report_type": "daily", "daily_statistics": {}, "total_records": 0}
        
        daily_stats = self.metrics_calculator.calculate_daily_statistics(records)
        formatted_stats = self._format_daily_stats(daily_stats)
        
        return {
            "report_type": "daily",
            "daily_statistics": formatted_stats,
            "total_records": len(records)
        }
    
    def _format_daily_stats(self, daily_stats: Dict) -> Dict[str, Dict[str, Any]]:
        """Format daily statistics for output."""
        return {
            str(d): {
                "date": str(d),
                "total_entries": s.total_entries,
                "unique_users": s.unique_users,
                "average_confidence": s.average_confidence,
                "liveness_verification_rate": s.liveness_verification_rate
            }
            for d, s in daily_stats.items()
        }

