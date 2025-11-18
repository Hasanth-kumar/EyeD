"""
Overview report generator.

Generates system overview attendance reports.
"""

from typing import List, Dict, Any, TYPE_CHECKING
from domain.entities.attendance_record import AttendanceRecord
from domain.services.analytics.metrics_calculator import MetricsCalculator
from domain.services.analytics.timeline_analyzer import TimelineAnalyzer

if TYPE_CHECKING:
    from use_cases.generate_report import GenerateReportRequest


class OverviewReportGenerator:
    """Generates system overview attendance reports."""
    
    def __init__(
        self,
        metrics_calculator: MetricsCalculator,
        timeline_analyzer: TimelineAnalyzer
    ):
        """
        Initialize overview report generator.
        
        Args:
            metrics_calculator: Service for calculating attendance metrics
            timeline_analyzer: Service for analyzing arrival patterns
        """
        self.metrics_calculator = metrics_calculator
        self.timeline_analyzer = timeline_analyzer
    
    def generate(
        self,
        records: List[AttendanceRecord],
        request: 'GenerateReportRequest'
    ) -> Dict[str, Any]:
        """
        Generate system overview attendance report.
        
        Args:
            records: List of attendance records
            request: Report generation request
            
        Returns:
            Dictionary containing overview report data
        """
        if not records:
            return {
                "report_type": "overview",
                "summary": {
                    "total_records": 0,
                    "unique_users": 0,
                    "average_confidence": 0.0,
                    "liveness_verification_rate": 0.0
                },
                "daily_statistics": {},
                "arrival_patterns": None
            }
        
        # Calculate daily statistics
        daily_stats = self.metrics_calculator.calculate_daily_statistics(records)
        formatted_daily_stats = self._format_daily_stats(daily_stats)
        
        # Calculate arrival patterns
        arrival_patterns = None
        try:
            arrival_patterns = self.timeline_analyzer.analyze_arrival_patterns(records)
        except ValueError:
            pass
        
        return {
            "report_type": "overview",
            "summary": {
                "total_records": len(records),
                "unique_users": len(set(r.user_id for r in records)),
                "average_confidence": self.metrics_calculator.calculate_average_confidence(records),
                "liveness_verification_rate": self.metrics_calculator.calculate_liveness_verification_rate(records)
            },
            "daily_statistics": formatted_daily_stats,
            "arrival_patterns": {
                "average_arrival_time_minutes": arrival_patterns.average_arrival_time_minutes,
                "earliest_arrival_minutes": arrival_patterns.earliest_arrival_minutes,
                "latest_arrival_minutes": arrival_patterns.latest_arrival_minutes,
                "hourly_distribution": arrival_patterns.hourly_distribution,
                "early_bird_count": arrival_patterns.early_bird_count,
                "on_time_count": arrival_patterns.on_time_count,
                "late_count": arrival_patterns.late_count
            } if arrival_patterns else None
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

