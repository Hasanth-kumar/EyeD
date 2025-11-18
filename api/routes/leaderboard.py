"""
Leaderboard API routes.

This module provides REST API endpoints for leaderboard operations.
It acts as a thin adapter between HTTP requests and use cases.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from use_cases.generate_leaderboard import GenerateLeaderboardUseCase, GenerateLeaderboardRequest
from api.dependencies import get_generate_leaderboard_use_case
from domain.services.gamification import Leaderboard

logger = logging.getLogger(__name__)

router = APIRouter()


class LeaderboardEntryDTO(BaseModel):
    """DTO for leaderboard entry."""
    rank: int
    userId: str
    userName: str
    value: float
    metric: str


class LeaderboardResponseDTO(BaseModel):
    """Response DTO for leaderboard."""
    success: bool
    entries: list[LeaderboardEntryDTO]
    metric: str
    totalUsers: int
    error: Optional[str] = None


def _convert_leaderboard_to_dto(leaderboard: Optional[Leaderboard]) -> list[LeaderboardEntryDTO]:
    """Convert leaderboard to DTOs."""
    if leaderboard is None:
        return []
    
    entries = []
    for user_ranking in leaderboard.ranked_users:
        # RankedUser already has the rank, user_id, user_name, and score
        # The score field contains the metric value (attendance_rate, streak, or total_badges)
        entries.append(LeaderboardEntryDTO(
            rank=user_ranking.rank,
            userId=user_ranking.user_id,
            userName=user_ranking.user_name,
            value=user_ranking.score,
            metric=leaderboard.metric_used
        ))
    
    return entries


@router.get("", response_model=LeaderboardResponseDTO)
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    metric: str = Query("attendance_rate", description="Metric to rank by: attendance_rate, streak, or total_badges"),
    periodDays: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    use_case: GenerateLeaderboardUseCase = Depends(get_generate_leaderboard_use_case)
):
    """
    Get leaderboard endpoint.
    
    This endpoint:
    1. Validates request parameters
    2. Converts DTO to use case request
    3. Calls use case (business logic is here)
    4. Converts use case response to DTO
    5. Returns HTTP response
    
    NO business logic here - all in use case.
    """
    try:
        # Validate metric
        if metric not in ["attendance_rate", "streak", "total_badges"]:
            return LeaderboardResponseDTO(
                success=False,
                entries=[],
                metric=metric,
                totalUsers=0,
                error=f"Unsupported metric: {metric}. Supported metrics: attendance_rate, streak, total_badges"
            )
        
        # Create use case request
        use_case_request = GenerateLeaderboardRequest(
            metric=metric,
            limit=limit,
            period_days=periodDays
        )
        
        # Call use case
        response = use_case.execute(use_case_request)
        
        if not response.success:
            return LeaderboardResponseDTO(
                success=False,
                entries=[],
                metric=metric,
                totalUsers=0,
                error=response.error
            )
        
        # Convert to DTOs
        entries = _convert_leaderboard_to_dto(response.leaderboard)
        total_users = response.leaderboard.total_users if response.leaderboard else 0
        
        return LeaderboardResponseDTO(
            success=True,
            entries=entries,
            metric=metric,
            totalUsers=total_users
        )
        
    except Exception as e:
        logger.exception(f"Unexpected error in get_leaderboard: {str(e)}")
        return LeaderboardResponseDTO(
            success=False,
            entries=[],
            metric=metric,
            totalUsers=0,
            error="An unexpected error occurred. Please try again."
        )

