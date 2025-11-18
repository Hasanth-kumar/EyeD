"""
Weekly report generator.

Generates weekly attendance summary reports.
"""

from typing import List, Dict, Any, TYPE_CHECKING
from datetime import timedelta
from collections import defaultdict
from domain.entities.attendance_record import AttendanceRecord
from domain.services.analytics.metrics_calculator import MetricsCalculator

if TYPE_CHECKING:
    from use_cases.generate_report import GenerateReportRequest


class WeeklyReportGenerator:
    """Generates weekly attendance summary reports."""
    
    def __init__(self, metrics_calculator: MetricsCalculator):
        """
        Initialize weekly report generator.
        
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
        Generate weekly attendance summary report.
        
        Args:
            records: List of attendance records
            request: Report generation request
            
        Returns:
            Dictionary containing weekly report data
        """
        if not records:
            return {"report_type": "weekly", "weekly_summary": {}, "total_records": 0}
        
        # Group records by week
        weekly_data = defaultdict(list)
        for record in records:
            week_start = record.date - timedelta(days=record.date.weekday())
            weekly_data[week_start.isoformat()].append(record)
        
        # Generate summary for each week
        weekly_summary = {}
        for week_key, week_records in weekly_data.items():
            daily_stats = self.metrics_calculator.calculate_daily_statistics(week_records)
            weekly_summary[week_key] = {
                "week_start": week_key,
                "total_entries": sum(s.total_entries for s in daily_stats.values()),
                "unique_users": len(set(r.user_id for r in week_records)),
                "average_confidence": self.metrics_calculator.calculate_average_confidence(week_records),
                "days_with_attendance": len(daily_stats)
            }
        
        return {
            "report_type": "weekly",
            "weekly_summary": weekly_summary,
            "total_records": len(records)
        }

