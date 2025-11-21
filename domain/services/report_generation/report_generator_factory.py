"""
Report generator factory.

Creates appropriate report generators based on report type.
"""

from typing import Dict, Protocol
from domain.services.report_generation.report_generator import ReportGenerator
from domain.services.report_generation.daily_report_generator import DailyReportGenerator
from domain.services.report_generation.weekly_report_generator import WeeklyReportGenerator
from domain.services.report_generation.monthly_report_generator import MonthlyReportGenerator
from domain.services.report_generation.user_report_generator import UserReportGenerator, UserRepositoryProtocol
from domain.services.report_generation.overview_report_generator import OverviewReportGenerator
from domain.services.analytics.metrics_calculator import MetricsCalculator
from domain.services.analytics.timeline_analyzer import TimelineAnalyzer


class ReportGeneratorFactory:
    """Factory for creating report generators."""
    
    def __init__(
        self,
        metrics_calculator: MetricsCalculator,
        timeline_analyzer: TimelineAnalyzer,
        user_repository: UserRepositoryProtocol
    ):
        """
        Initialize report generator factory.
        
        Args:
            metrics_calculator: Service for calculating attendance metrics
            timeline_analyzer: Service for analyzing arrival patterns
            user_repository: Repository for user data
        """
        self.metrics_calculator = metrics_calculator
        self.timeline_analyzer = timeline_analyzer
        self.user_repository = user_repository
        
        # Pre-create generators for each report type
        self._generators: Dict[str, ReportGenerator] = {
            "daily": DailyReportGenerator(metrics_calculator),
            "weekly": WeeklyReportGenerator(metrics_calculator),
            "monthly": MonthlyReportGenerator(metrics_calculator),
            "user": UserReportGenerator(metrics_calculator, user_repository),
            "overview": OverviewReportGenerator(metrics_calculator, timeline_analyzer),
        }
    
    def create(self, report_type: str) -> ReportGenerator:
        """
        Create a report generator for the specified report type.
        
        Args:
            report_type: Type of report to generate (daily, weekly, monthly, user, overview)
            
        Returns:
            Report generator instance
            
        Raises:
            ValueError: If report_type is not recognized
        """
        generator = self._generators.get(report_type)
        if not generator:
            raise ValueError(f"Unknown report type: {report_type}")
        return generator












