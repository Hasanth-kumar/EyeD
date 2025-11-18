"""
Monthly report generator.

Generates monthly attendance summary reports.
"""

from typing import List, Dict, Any, TYPE_CHECKING
from collections import defaultdict
from domain.entities.attendance_record import AttendanceRecord
from domain.services.analytics.metrics_calculator import MetricsCalculator

if TYPE_CHECKING:
    from use_cases.generate_report import GenerateReportRequest


class MonthlyReportGenerator:
    """Generates monthly attendance summary reports."""
    
    def __init__(self, metrics_calculator: MetricsCalculator):
        """
        Initialize monthly report generator.
        
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
        Generate monthly attendance summary report.
        
        Args:
            records: List of attendance records
            request: Report generation request
            
        Returns:
            Dictionary containing monthly report data
        """
        if not records:
            return {"report_type": "monthly", "monthly_summary": {}, "total_records": 0}
        
        # Group records by month
        monthly_data = defaultdict(list)
        for record in records:
            month_key = f"{record.date.year}-{record.date.month:02d}"
            monthly_data[month_key].append(record)
        
        # Generate summary for each month
        monthly_summary = {}
        for month_key, month_records in monthly_data.items():
            daily_stats = self.metrics_calculator.calculate_daily_statistics(month_records)
            first_date = min(r.date for r in month_records)
            last_date = max(r.date for r in month_records)
            period_days = (last_date - first_date).days + 1
            
            monthly_summary[month_key] = {
                "month": month_key,
                "total_entries": sum(s.total_entries for s in daily_stats.values()),
                "unique_users": len(set(r.user_id for r in month_records)),
                "average_confidence": self.metrics_calculator.calculate_average_confidence(month_records),
                "attendance_rate": self.metrics_calculator.calculate_attendance_rate(month_records, period_days),
                "days_with_attendance": len(daily_stats)
            }
        
        return {
            "report_type": "monthly",
            "monthly_summary": monthly_summary,
            "total_records": len(records)
        }

