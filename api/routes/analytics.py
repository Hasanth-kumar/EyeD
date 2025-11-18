"""
Analytics API routes.

This module provides REST API endpoints for analytics operations.
It acts as a thin adapter between HTTP requests and use cases.
"""

import logging
from typing import Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from use_cases.get_analytics import GetAnalyticsUseCase, GetAnalyticsRequest
from api.dependencies import get_get_analytics_use_case
from domain.services.analytics import DailyStatistics, ArrivalPatterns, PeriodSummary

logger = logging.getLogger(__name__)

router = APIRouter()


class DailyStatisticsDTO(BaseModel):
    """DTO for daily statistics."""
    date: str
    total_entries: int
    unique_users: int
    average_confidence: float
    liveness_verification_rate: float


class ArrivalPatternsDTO(BaseModel):
    """DTO for arrival patterns."""
    peak_hour: int
    average_arrival_time: str
    late_arrivals_count: int
    earliest_arrival_minutes: float
    latest_arrival_minutes: float
    hourly_distribution: dict[int, int]
    early_bird_count: int
    on_time_count: int


class PeriodSummaryDTO(BaseModel):
    """DTO for period summary."""
    total_entries: int
    unique_users: int
    average_confidence: float
    liveness_verification_rate: float


class GetAnalyticsResponseDTO(BaseModel):
    """Response DTO for getting analytics."""
    success: bool
    dailyAttendance: list[DailyStatisticsDTO]
    weeklyTrend: Optional[list] = None  # Can be expanded later
    departmentStats: Optional[list] = None  # Can be expanded later
    peakHours: Optional[list] = None  # Can be expanded later
    arrivalPatterns: Optional[ArrivalPatternsDTO] = None
    periodSummary: Optional[PeriodSummaryDTO] = None
    weeklyAttendanceRate: Optional[float] = None
    error: Optional[str] = None


def _convert_daily_statistics_to_dto(
    daily_stats: dict[date, DailyStatistics]
) -> list[DailyStatisticsDTO]:
    """Convert daily statistics to DTOs."""
    result = []
    for stat_date, stats in sorted(daily_stats.items()):
        result.append(DailyStatisticsDTO(
            date=stat_date.isoformat(),
            total_entries=stats.total_entries,
            unique_users=stats.unique_users,
            average_confidence=stats.average_confidence,
            liveness_verification_rate=stats.liveness_verification_rate
        ))
    return result


def _convert_arrival_patterns_to_dto(
    patterns: Optional[ArrivalPatterns]
) -> Optional[ArrivalPatternsDTO]:
    """Convert arrival patterns to DTO."""
    if patterns is None:
        return None
    
    # Calculate peak hour from hourly distribution (hour with max count)
    peak_hour = 0
    if patterns.hourly_distribution:
        peak_hour = max(patterns.hourly_distribution.items(), key=lambda x: x[1])[0]
    
    # Convert average_arrival_time_minutes to time string (HH:MM format)
    hours = int(patterns.average_arrival_time_minutes // 60)
    minutes = int(patterns.average_arrival_time_minutes % 60)
    average_arrival_time_str = f"{hours:02d}:{minutes:02d}"
    
    return ArrivalPatternsDTO(
        peak_hour=peak_hour,
        average_arrival_time=average_arrival_time_str,
        late_arrivals_count=patterns.late_count,
        earliest_arrival_minutes=patterns.earliest_arrival_minutes,
        latest_arrival_minutes=patterns.latest_arrival_minutes,
        hourly_distribution=patterns.hourly_distribution,
        early_bird_count=patterns.early_bird_count,
        on_time_count=patterns.on_time_count
    )


def _convert_period_summary_to_dto(
    summary: Optional[PeriodSummary]
) -> Optional[PeriodSummaryDTO]:
    """Convert period summary to DTO."""
    if summary is None:
        return None
    
    return PeriodSummaryDTO(
        total_entries=summary.total_entries,
        unique_users=summary.unique_users,
        average_confidence=summary.average_confidence,
        liveness_verification_rate=summary.liveness_verification_rate
    )


@router.get("", response_model=GetAnalyticsResponseDTO)
async def get_analytics(
    startDate: Optional[str] = Query(None, description="Start date (ISO format: YYYY-MM-DD)"),
    endDate: Optional[str] = Query(None, description="End date (ISO format: YYYY-MM-DD)"),
    includeTimeline: bool = Query(False, description="Include arrival patterns analysis"),
    use_case: GetAnalyticsUseCase = Depends(get_get_analytics_use_case)
):
    """
    Get analytics data endpoint.
    
    This endpoint:
    1. Validates request parameters
    2. Converts DTO to use case request
    3. Calls use case (business logic is here)
    4. Converts use case response to DTO
    5. Returns HTTP response
    
    NO business logic here - all in use case.
    """
    try:
        # Parse dates or use defaults
        if startDate:
            start_date = datetime.fromisoformat(startDate).date()
        else:
            # Default to 30 days ago
            from datetime import timedelta
            start_date = date.today() - timedelta(days=30)
        
        if endDate:
            end_date = datetime.fromisoformat(endDate).date()
        else:
            end_date = date.today()
        
        # Create use case request
        use_case_request = GetAnalyticsRequest(
            start_date=start_date,
            end_date=end_date,
            include_timeline=includeTimeline,
            active_users_count=None  # Can be added later if needed
        )
        
        # Call use case
        response = use_case.execute(use_case_request)
        
        if not response.success:
            return GetAnalyticsResponseDTO(
                success=False,
                dailyAttendance=[],
                error=response.error
            )
        
        # Convert to DTOs
        daily_attendance = _convert_daily_statistics_to_dto(response.daily_statistics)
        arrival_patterns = _convert_arrival_patterns_to_dto(response.arrival_patterns)
        period_summary = _convert_period_summary_to_dto(response.period_summary)
        
        return GetAnalyticsResponseDTO(
            success=True,
            dailyAttendance=daily_attendance,
            arrivalPatterns=arrival_patterns,
            periodSummary=period_summary,
            weeklyAttendanceRate=response.weekly_attendance_rate
        )
        
    except ValueError as e:
        logger.warning(f"Invalid date format: {str(e)}")
        return GetAnalyticsResponseDTO(
            success=False,
            dailyAttendance=[],
            error=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_analytics: {str(e)}")
        return GetAnalyticsResponseDTO(
            success=False,
            dailyAttendance=[],
            error="An unexpected error occurred. Please try again."
        )

