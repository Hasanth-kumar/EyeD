"""
Get analytics use case.

Orchestrates analytics data retrieval workflow with metrics calculation and timeline analysis.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Protocol, List
from datetime import date

from domain.entities.attendance_record import AttendanceRecord
from domain.services.analytics import (
    MetricsCalculator,
    TimelineAnalyzer,
    DailyStatistics,
    ArrivalPatterns,
    PeriodSummary
)


@dataclass
class GetAnalyticsRequest:
    """Request for getting analytics data."""
    start_date: date
    end_date: date
    include_timeline: bool = False
    active_users_count: Optional[int] = None  # Optional: for calculating weekly attendance rate


@dataclass
class GetAnalyticsResponse:
    """Response from getting analytics data."""
    success: bool
    daily_statistics: Dict[date, DailyStatistics]
    period_summary: Optional[PeriodSummary] = None  # Optional: aggregated summary for the period
    arrival_patterns: Optional[ArrivalPatterns] = None
    weekly_attendance_rate: Optional[float] = None  # Optional: calculated if active_users_count provided
    error: Optional[str] = None


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


class GetAnalyticsUseCase:
    """
    Orchestrates analytics data retrieval workflow.
    
    This use case coordinates attendance data retrieval, metrics calculation,
    and optional timeline analysis to provide comprehensive analytics.
    
    Single Responsibility: Orchestrate analytics data calculation ONLY.
    All business logic is delegated to domain services.
    """
    
    def __init__(
        self,
        metrics_calculator: MetricsCalculator,
        timeline_analyzer: TimelineAnalyzer,
        attendance_repository: AttendanceRepositoryProtocol
    ):
        """
        Initialize GetAnalyticsUseCase.
        
        Args:
            metrics_calculator: Service for calculating attendance metrics.
            timeline_analyzer: Service for analyzing arrival patterns.
            attendance_repository: Repository for attendance data persistence.
        """
        self.metrics_calculator = metrics_calculator
        self.timeline_analyzer = timeline_analyzer
        self.attendance_repository = attendance_repository
    
    def execute(self, request: GetAnalyticsRequest) -> GetAnalyticsResponse:
        """
        Execute analytics data retrieval workflow.
        
        Workflow Steps:
        1. Get attendance records from repository (filtered by date range)
        2. Calculate daily statistics using MetricsCalculator
        3. Analyze arrival patterns using TimelineAnalyzer (if requested)
        4. Build analytics response
        5. Return analytics data
        
        Args:
            request: Get analytics request with date range and optional timeline flag.
        
        Returns:
            GetAnalyticsResponse with daily statistics and optional arrival patterns.
        """
        try:
            # Validate request
            if request.start_date > request.end_date:
                return GetAnalyticsResponse(
                    success=False,
                    daily_statistics={},
                    error="start_date cannot be after end_date"
                )
            
            # Step 1: Get attendance records from repository
            records = self._get_attendance_records(request)
            
            # Step 2: Calculate daily statistics using MetricsCalculator
            daily_statistics = self._calculate_daily_statistics(records)
            
            # Step 3: Calculate period summary using MetricsCalculator
            period_summary = self._calculate_period_summary(records)
            
            # Step 4: Analyze arrival patterns using TimelineAnalyzer (if requested)
            arrival_patterns = None
            if request.include_timeline:
                arrival_patterns = self._analyze_arrival_patterns(records)
            
            # Step 5: Calculate weekly attendance rate (if active_users_count provided)
            weekly_attendance_rate = None
            if request.active_users_count is not None and request.active_users_count > 0:
                weekly_attendance_rate = self._calculate_weekly_attendance_rate(
                    daily_statistics,
                    request.active_users_count
                )
            
            # Step 6: Build and return analytics response
            return GetAnalyticsResponse(
                success=True,
                daily_statistics=daily_statistics,
                period_summary=period_summary,
                arrival_patterns=arrival_patterns,
                weekly_attendance_rate=weekly_attendance_rate
            )
            
        except ValueError as e:
            return GetAnalyticsResponse(
                success=False,
                daily_statistics={},
                error=f"Invalid request: {str(e)}"
            )
        except Exception as e:
            return GetAnalyticsResponse(
                success=False,
                daily_statistics={},
                error=f"Unexpected error during analytics retrieval: {str(e)}"
            )
    
    def _get_attendance_records(
        self,
        request: GetAnalyticsRequest
    ) -> List[AttendanceRecord]:
        """
        Get attendance records from repository filtered by date range.
        
        Args:
            request: Get analytics request with date range.
        
        Returns:
            List of AttendanceRecord domain entities within the date range.
        """
        return self.attendance_repository.get_attendance_history(
            user_id=None,  # Get all users for analytics
            start_date=request.start_date,
            end_date=request.end_date
        )
    
    def _calculate_daily_statistics(
        self,
        records: List[AttendanceRecord]
    ) -> Dict[date, DailyStatistics]:
        """
        Calculate daily statistics using MetricsCalculator.
        
        Args:
            records: List of attendance records to analyze.
        
        Returns:
            Dictionary mapping date to DailyStatistics value object.
        """
        # Use injected metrics calculator (supports both instance and static method calls)
        return self.metrics_calculator.calculate_daily_statistics(records)
    
    def _calculate_period_summary(
        self,
        records: List[AttendanceRecord]
    ) -> PeriodSummary:
        """
        Calculate period summary using MetricsCalculator.
        
        Args:
            records: List of attendance records to analyze.
        
        Returns:
            PeriodSummary value object with aggregated statistics.
        """
        return self.metrics_calculator.calculate_period_summary(records)
    
    def _analyze_arrival_patterns(
        self,
        records: List[AttendanceRecord]
    ) -> Optional[ArrivalPatterns]:
        """
        Analyze arrival patterns using TimelineAnalyzer.
        
        Args:
            records: List of attendance records to analyze.
        
        Returns:
            ArrivalPatterns value object, or None if no records available.
        """
        if not records:
            return None
        
        try:
            return self.timeline_analyzer.analyze_arrival_patterns(records)
        except ValueError:
            # TimelineAnalyzer raises ValueError for empty records, but we already checked
            # Return None if analysis fails
            return None
    
    def _calculate_weekly_attendance_rate(
        self,
        daily_statistics: Dict[date, DailyStatistics],
        active_users_count: int
    ) -> float:
        """
        Calculate weekly attendance rate using MetricsCalculator.
        
        Args:
            daily_statistics: Dictionary mapping date to DailyStatistics value object.
            active_users_count: Total number of active users in the system.
        
        Returns:
            Weekly attendance rate percentage (0.0 to 100.0).
        """
        return self.metrics_calculator.calculate_weekly_attendance_rate(
            daily_statistics,
            active_users_count
        )

