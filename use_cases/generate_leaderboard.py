"""
Generate leaderboard use case.

Orchestrates leaderboard generation workflow with metrics calculation and ranking.
"""

from dataclasses import dataclass
from typing import Optional, List, Protocol, Dict, Any
from datetime import date, timedelta, datetime

from domain.entities.attendance_record import AttendanceRecord
from domain.entities.user import User
from domain.services.gamification import (
    LeaderboardGenerator,
    StreakCalculator,
    BadgeCalculator,
    UserRankingData,
    Leaderboard
)
from domain.services.analytics import MetricsCalculator


@dataclass
class GenerateLeaderboardRequest:
    """Request for generating a leaderboard."""
    metric: str
    limit: int = 10
    period_days: int = 30


@dataclass
class GenerateLeaderboardResponse:
    """Response from leaderboard generation."""
    success: bool
    leaderboard: Optional[Leaderboard] = None
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


class UserRepositoryProtocol(Protocol):
    """Protocol for user repository operations."""
    
    def get_all_users(self, include_inactive: bool = True) -> Dict[str, Any]:
        """Get all users. Returns dict with 'success', 'data' (list of user dicts), and optional 'error' keys."""
        ...


class GenerateLeaderboardUseCase:
    """
    Orchestrates leaderboard generation workflow.
    
    This use case coordinates user retrieval, attendance data collection,
    metrics calculation, and leaderboard generation.
    """
    
    def __init__(
        self,
        leaderboard_generator: LeaderboardGenerator,
        metrics_calculator: MetricsCalculator,
        streak_calculator: StreakCalculator,
        badge_calculator: BadgeCalculator,
        attendance_repository: AttendanceRepositoryProtocol,
        user_repository: UserRepositoryProtocol
    ):
        """
        Initialize leaderboard generation use case.
        
        Args:
            leaderboard_generator: Service for generating leaderboards from ranking data.
            metrics_calculator: Service for calculating attendance metrics.
            streak_calculator: Service for calculating attendance streaks.
            badge_calculator: Service for calculating badges.
            attendance_repository: Repository for attendance data.
            user_repository: Repository for user data.
        """
        self.leaderboard_generator = leaderboard_generator
        self.metrics_calculator = metrics_calculator
        self.streak_calculator = streak_calculator
        self.badge_calculator = badge_calculator
        self.attendance_repository = attendance_repository
        self.user_repository = user_repository
    
    def execute(self, request: GenerateLeaderboardRequest) -> GenerateLeaderboardResponse:
        """
        Execute leaderboard generation workflow.
        
        Args:
            request: Generate leaderboard request with metric, limit, and period_days.
        
        Returns:
            GenerateLeaderboardResponse with leaderboard result.
        """
        try:
            # Validate metric
            if request.metric not in ["attendance_rate", "streak", "total_badges"]:
                return GenerateLeaderboardResponse(
                    success=False,
                    error=f"Unsupported metric: {request.metric}. "
                          f"Supported metrics: attendance_rate, streak, total_badges"
                )
            
            # Step 1: Get all users
            result = self.user_repository.get_all_users(include_inactive=False)
            if not result.get('success', False):
                error_msg = result.get('error', 'Failed to retrieve users')
                return GenerateLeaderboardResponse(
                    success=False,
                    error=f"Failed to retrieve users: {error_msg}"
                )
            
            # Extract user dictionaries and convert to User entities
            user_dicts = result.get('data', [])
            if not user_dicts:
                return GenerateLeaderboardResponse(
                    success=False,
                    error="No users found in repository"
                )
            
            # Convert user dicts to User entities
            users = []
            for user_dict in user_dicts:
                # Parse registration_date
                registration_date = datetime.now()
                if 'registration_date' in user_dict:
                    reg_date_str = user_dict['registration_date']
                    if isinstance(reg_date_str, str):
                        try:
                            registration_date = datetime.fromisoformat(reg_date_str)
                        except ValueError:
                            registration_date = datetime.now()
                    elif isinstance(reg_date_str, datetime):
                        registration_date = reg_date_str
                
                user = User(
                    user_id=user_dict.get('user_id', ''),
                    username=user_dict.get('user_name') or user_dict.get('username', ''),
                    first_name=user_dict.get('first_name'),
                    last_name=user_dict.get('last_name'),
                    email=user_dict.get('email'),
                    registration_date=registration_date,
                    status=user_dict.get('status', 'active')
                )
                users.append(user)
            
            # Step 2: Calculate date range for period
            end_date = date.today()
            start_date = end_date - timedelta(days=request.period_days - 1)
            
            # Step 3: For each user, get attendance records and calculate metrics
            users_ranking_data = []
            
            for user in users:
                user_id = user.user_id
                # Get user name from User entity - prefer full name, fallback to username
                if user.first_name and user.last_name:
                    user_name = f"{user.first_name} {user.last_name}".strip()
                elif user.first_name:
                    user_name = user.first_name
                elif user.username:
                    user_name = user.username
                else:
                    user_name = user_id
                
                if not user_id:
                    continue
                
                # Get attendance records for this user in the period
                attendance_records = self.attendance_repository.get_attendance_history(
                    user_id=user_id,
                    start_date=start_date,
                    end_date=end_date
                )
                
                # Step 4: Calculate metrics for this user
                attendance_rate = self.metrics_calculator.calculate_attendance_rate(
                    attendance_records,
                    request.period_days
                )
                
                streak = self.streak_calculator.calculate_current_streak(attendance_records)
                
                badges = self.badge_calculator.calculate(
                    attendance_records,
                    request.period_days
                )
                total_badges = len(badges)
                
                # Step 5: Build UserRankingData object
                try:
                    user_ranking_data = UserRankingData(
                        user_id=user_id,
                        user_name=user_name,
                        attendance_rate=attendance_rate,
                        streak=streak,
                        total_badges=total_badges
                    )
                    users_ranking_data.append(user_ranking_data)
                except ValueError as e:
                    # Skip users with invalid ranking data
                    continue
            
            if not users_ranking_data:
                return GenerateLeaderboardResponse(
                    success=False,
                    error="No valid user ranking data found"
                )
            
            # Step 6: Generate leaderboard
            leaderboard = self.leaderboard_generator.generate(
                users_ranking_data,
                request.metric
            )
            
            # Step 7: Apply limit if specified
            if request.limit > 0 and len(leaderboard.ranked_users) > request.limit:
                limited_users = leaderboard.ranked_users[:request.limit]
                leaderboard = Leaderboard(
                    ranked_users=limited_users,
                    metric_used=leaderboard.metric_used,
                    generated_at=leaderboard.generated_at,
                    total_users=len(limited_users)
                )
            
            return GenerateLeaderboardResponse(
                success=True,
                leaderboard=leaderboard
            )
            
        except ValueError as e:
            return GenerateLeaderboardResponse(
                success=False,
                error=f"Invalid request: {str(e)}"
            )
        except Exception as e:
            return GenerateLeaderboardResponse(
                success=False,
                error=f"Failed to generate leaderboard: {str(e)}"
            )

