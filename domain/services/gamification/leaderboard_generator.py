"""
Leaderboard generator - pure business logic for generating leaderboards.

This module contains pure ranking logic with no side effects and
no dependencies on repositories or infrastructure.
"""

from datetime import datetime
from typing import List

from domain.services.gamification.value_objects import (
    UserRankingData,
    RankedUser,
    Leaderboard
)


class LeaderboardGenerator:
    """
    Pure business logic generator for leaderboards.
    
    This class contains only ranking logic with no side effects.
    It does not depend on repositories, databases, or any infrastructure.
    All methods are pure functions that take pre-calculated user metrics
    and return ranked leaderboards.
    
    The generator takes UserRankingData (pre-calculated metrics) as input
    and produces Leaderboard value objects as output.
    """
    
    def generate(
        self,
        users_data: List[UserRankingData],
        metric: str
    ) -> Leaderboard:
        """
        Generate a leaderboard based on the specified metric.
        
        This is the main entry point that delegates to specific ranking methods
        based on the metric type.
        
        Args:
            users_data: List of user ranking data with pre-calculated metrics.
            metric: The metric to use for ranking. Must be one of:
                - "attendance_rate"
                - "streak"
                - "total_badges"
        
        Returns:
            Leaderboard value object containing ranked users.
        
        Raises:
            ValueError: If metric is not supported or users_data is empty.
        
        Examples:
            >>> generator = LeaderboardGenerator()
            >>> users = [
            ...     UserRankingData("user1", "Alice", 85.0, 10, 5),
            ...     UserRankingData("user2", "Bob", 90.0, 15, 3)
            ... ]
            >>> leaderboard = generator.generate(users, "attendance_rate")
            >>> leaderboard.ranked_users[0].user_name
            'Bob'
        """
        if not users_data:
            raise ValueError("users_data cannot be empty")
        
        if metric == "attendance_rate":
            return self.rank_by_attendance_rate(users_data)
        elif metric == "streak":
            return self.rank_by_streak(users_data)
        elif metric == "total_badges":
            return self.rank_by_total_badges(users_data)
        else:
            raise ValueError(
                f"Unsupported metric: {metric}. "
                f"Supported metrics: attendance_rate, streak, total_badges"
            )
    
    def rank_by_attendance_rate(
        self,
        users_data: List[UserRankingData]
    ) -> Leaderboard:
        """
        Rank users by attendance rate (highest first).
        
        Args:
            users_data: List of user ranking data with pre-calculated metrics.
        
        Returns:
            Leaderboard value object with users ranked by attendance_rate.
        
        Examples:
            >>> generator = LeaderboardGenerator()
            >>> users = [
            ...     UserRankingData("user1", "Alice", 85.0, 10, 5),
            ...     UserRankingData("user2", "Bob", 90.0, 15, 3)
            ... ]
            >>> leaderboard = generator.rank_by_attendance_rate(users)
            >>> leaderboard.ranked_users[0].user_name
            'Bob'
            >>> leaderboard.ranked_users[0].score
            90.0
        """
        if not users_data:
            raise ValueError("users_data cannot be empty")
        
        # Sort by attendance_rate in descending order
        sorted_users = sorted(
            users_data,
            key=lambda u: u.attendance_rate,
            reverse=True
        )
        
        # Create ranked users with sequential ranks
        ranked_users = [
            RankedUser(
                rank=i + 1,
                user_id=user.user_id,
                user_name=user.user_name,
                score=user.attendance_rate
            )
            for i, user in enumerate(sorted_users)
        ]
        
        return Leaderboard(
            ranked_users=ranked_users,
            metric_used="attendance_rate",
            generated_at=datetime.now(),
            total_users=len(ranked_users)
        )
    
    def rank_by_streak(
        self,
        users_data: List[UserRankingData]
    ) -> Leaderboard:
        """
        Rank users by current streak (highest first).
        
        Args:
            users_data: List of user ranking data with pre-calculated metrics.
        
        Returns:
            Leaderboard value object with users ranked by streak.
        
        Examples:
            >>> generator = LeaderboardGenerator()
            >>> users = [
            ...     UserRankingData("user1", "Alice", 85.0, 10, 5),
            ...     UserRankingData("user2", "Bob", 90.0, 15, 3)
            ... ]
            >>> leaderboard = generator.rank_by_streak(users)
            >>> leaderboard.ranked_users[0].user_name
            'Bob'
            >>> leaderboard.ranked_users[0].score
            15.0
        """
        if not users_data:
            raise ValueError("users_data cannot be empty")
        
        # Sort by streak in descending order
        sorted_users = sorted(
            users_data,
            key=lambda u: u.streak,
            reverse=True
        )
        
        # Create ranked users with sequential ranks
        ranked_users = [
            RankedUser(
                rank=i + 1,
                user_id=user.user_id,
                user_name=user.user_name,
                score=float(user.streak)
            )
            for i, user in enumerate(sorted_users)
        ]
        
        return Leaderboard(
            ranked_users=ranked_users,
            metric_used="streak",
            generated_at=datetime.now(),
            total_users=len(ranked_users)
        )
    
    def rank_by_total_badges(
        self,
        users_data: List[UserRankingData]
    ) -> Leaderboard:
        """
        Rank users by total badges earned (highest first).
        
        Args:
            users_data: List of user ranking data with pre-calculated metrics.
        
        Returns:
            Leaderboard value object with users ranked by total_badges.
        
        Examples:
            >>> generator = LeaderboardGenerator()
            >>> users = [
            ...     UserRankingData("user1", "Alice", 85.0, 10, 5),
            ...     UserRankingData("user2", "Bob", 90.0, 15, 3)
            ... ]
            >>> leaderboard = generator.rank_by_total_badges(users)
            >>> leaderboard.ranked_users[0].user_name
            'Alice'
            >>> leaderboard.ranked_users[0].score
            5.0
        """
        if not users_data:
            raise ValueError("users_data cannot be empty")
        
        # Sort by total_badges in descending order
        sorted_users = sorted(
            users_data,
            key=lambda u: u.total_badges,
            reverse=True
        )
        
        # Create ranked users with sequential ranks
        ranked_users = [
            RankedUser(
                rank=i + 1,
                user_id=user.user_id,
                user_name=user.user_name,
                score=float(user.total_badges)
            )
            for i, user in enumerate(sorted_users)
        ]
        
        return Leaderboard(
            ranked_users=ranked_users,
            metric_used="total_badges",
            generated_at=datetime.now(),
            total_users=len(ranked_users)
        )















