"""
Badge calculator - pure business logic for calculating badges.

This module contains pure calculation logic with no side effects and
no dependencies on repositories or infrastructure.
"""

from datetime import datetime
from typing import List
import uuid

from domain.entities.attendance_record import AttendanceRecord
from domain.entities.badge import Badge, BadgeCategory
from domain.services.gamification.badge_definitions import BadgeDefinitions
from domain.services.gamification.streak_calculator import StreakCalculator


# Business rule constants
MIN_WEEK_DAYS = 7
MIN_MONTH_DAYS = 30
EARLY_BIRD_HOUR = 8
PUNCTUALITY_HOUR = 9
PUNCTUALITY_MAX_MINUTE = 15
HIGH_QUALITY_THRESHOLD = 0.8

# Badge score calculation weights
BADGE_SCORE_WEIGHTS = {
    'attendance': 1.0,
    'streak': 1.5,  # Streak badges are harder to earn
    'timing': 1.2,  # Timing badges require consistency
    'quality': 1.1   # Quality badges reflect recognition quality
}


class BadgeCalculator:
    """
    Pure business logic calculator for badges.
    
    This class contains only calculation logic with no side effects.
    It does not depend on repositories, databases, or any infrastructure.
    All methods are pure functions that take inputs and return results.
    """
    
    def __init__(self, badge_definitions: BadgeDefinitions):
        """
        Initialize badge calculator with badge definitions.
        
        Args:
            badge_definitions: BadgeDefinitions value object containing badge criteria.
        """
        self.badge_definitions = badge_definitions
    
    def calculate(
        self,
        attendance_data: List[AttendanceRecord],
        period_days: int
    ) -> List[Badge]:
        """
        Calculate all badges for the given attendance data.
        
        Args:
            attendance_data: List of attendance records for badge calculation.
            period_days: Number of days in the evaluation period.
        
        Returns:
            List of Badge entities earned by the user.
        """
        if not attendance_data:
            return []
        
        # Extract user_id from the first record (all records should be for the same user)
        user_id = attendance_data[0].user_id
        
        all_badges: List[Badge] = []
        
        # Calculate badges for each category
        all_badges.extend(
            self._calculate_attendance_badges(attendance_data, period_days, user_id)
        )
        all_badges.extend(
            self._calculate_streak_badges(attendance_data, user_id)
        )
        all_badges.extend(
            self._calculate_timing_badges(attendance_data, user_id)
        )
        all_badges.extend(
            self._calculate_quality_badges(attendance_data, user_id)
        )
        
        return all_badges
    
    def calculate_badge_score(self, badges: List[Badge]) -> float:
        """
        Calculate badge score based on earned badges.
        
        The score is calculated as a weighted sum of badges, with different
        categories having different weights to reflect their difficulty/importance.
        
        Args:
            badges: List of earned badges.
        
        Returns:
            Badge score as a float.
        """
        if not badges:
            return 0.0
        
        # Calculate weighted score
        total_score = 0.0
        for badge in badges:
            category = badge.category.value if hasattr(badge.category, 'value') else str(badge.category)
            weight = BADGE_SCORE_WEIGHTS.get(category, 1.0)
            total_score += weight
        
        return round(total_score, 2)
    
    def _calculate_attendance_badges(
        self,
        records: List[AttendanceRecord],
        period_days: int,
        user_id: str
    ) -> List[Badge]:
        """
        Calculate attendance-based badges.
        
        Args:
            records: List of attendance records.
            period_days: Number of days in the evaluation period.
            user_id: ID of the user.
        
        Returns:
            List of attendance badges earned.
        """
        badges: List[Badge] = []
        total_entries = len(records)
        
        # Check perfect week badge
        perfect_week_def = self.badge_definitions.attendance['perfect_week']
        if period_days >= MIN_WEEK_DAYS and total_entries >= perfect_week_def.criteria:
            badges.append(self._create_badge(
                badge_id=self._generate_badge_id(),
                name=perfect_week_def.name,
                category=BadgeCategory.ATTENDANCE,
                description=perfect_week_def.description,
                criteria={'total_entries': total_entries, 'required_count': perfect_week_def.criteria},
                user_id=user_id
            ))
        
        # Check perfect month badge
        perfect_month_def = self.badge_definitions.attendance['perfect_month']
        if period_days >= MIN_MONTH_DAYS and total_entries >= perfect_month_def.criteria:
            badges.append(self._create_badge(
                badge_id=self._generate_badge_id(),
                name=perfect_month_def.name,
                category=BadgeCategory.ATTENDANCE,
                description=perfect_month_def.description,
                criteria={'total_entries': total_entries, 'required_count': perfect_month_def.criteria},
                user_id=user_id
            ))
        
        # Check consistency master badge
        consistency_master_def = self.badge_definitions.attendance['consistency_master']
        if total_entries >= consistency_master_def.criteria:
            badges.append(self._create_badge(
                badge_id=self._generate_badge_id(),
                name=consistency_master_def.name,
                category=BadgeCategory.ATTENDANCE,
                description=consistency_master_def.description,
                criteria={'total_entries': total_entries, 'required_count': consistency_master_def.criteria},
                user_id=user_id
            ))
        
        # Check dedication champion badge
        dedication_champion_def = self.badge_definitions.attendance['dedication_champion']
        if total_entries >= dedication_champion_def.criteria:
            badges.append(self._create_badge(
                badge_id=self._generate_badge_id(),
                name=dedication_champion_def.name,
                category=BadgeCategory.ATTENDANCE,
                description=dedication_champion_def.description,
                criteria={'total_entries': total_entries, 'required_count': dedication_champion_def.criteria},
                user_id=user_id
            ))
        
        return badges
    
    def _calculate_streak_badges(
        self,
        records: List[AttendanceRecord],
        user_id: str
    ) -> List[Badge]:
        """
        Calculate streak-based badges.
        
        Args:
            records: List of attendance records.
            user_id: ID of the user.
        
        Returns:
            List of streak badges earned.
        """
        badges: List[Badge] = []
        
        if not records:
            return badges
        
        # Calculate maximum streak using StreakCalculator
        # StreakCalculator handles filtering for present records internally
        max_streak = StreakCalculator.calculate_max_streak(records)
        
        # Check week warrior badge
        week_warrior_def = self.badge_definitions.streak['week_warrior']
        if max_streak >= week_warrior_def.criteria:
            badges.append(self._create_badge(
                badge_id=self._generate_badge_id(),
                name=week_warrior_def.name,
                category=BadgeCategory.STREAK,
                description=week_warrior_def.description,
                criteria={'max_streak': max_streak, 'required_count': week_warrior_def.criteria},
                user_id=user_id
            ))
        
        # Check month master badge
        month_master_def = self.badge_definitions.streak['month_master']
        if max_streak >= month_master_def.criteria:
            badges.append(self._create_badge(
                badge_id=self._generate_badge_id(),
                name=month_master_def.name,
                category=BadgeCategory.STREAK,
                description=month_master_def.description,
                criteria={'max_streak': max_streak, 'required_count': month_master_def.criteria},
                user_id=user_id
            ))
        
        # Check streak legend badge
        streak_legend_def = self.badge_definitions.streak['streak_legend']
        if max_streak >= streak_legend_def.criteria:
            badges.append(self._create_badge(
                badge_id=self._generate_badge_id(),
                name=streak_legend_def.name,
                category=BadgeCategory.STREAK,
                description=streak_legend_def.description,
                criteria={'max_streak': max_streak, 'required_count': streak_legend_def.criteria},
                user_id=user_id
            ))
        
        return badges
    
    def _calculate_timing_badges(
        self,
        records: List[AttendanceRecord],
        user_id: str
    ) -> List[Badge]:
        """
        Calculate timing-based badges.
        
        Args:
            records: List of attendance records.
            user_id: ID of the user.
        
        Returns:
            List of timing badges earned.
        """
        badges: List[Badge] = []
        
        if not records:
            return badges
        
        # Analyze arrival times
        arrival_hours = []
        for record in records:
            if record.time:
                arrival_hours.append(record.time.hour)
        
        if not arrival_hours:
            return badges
        
        # Check early bird badge (arrivals at or before EARLY_BIRD_HOUR)
        early_bird_def = self.badge_definitions.timing['early_bird']
        early_bird_count = len([h for h in arrival_hours if h <= EARLY_BIRD_HOUR])
        if early_bird_count >= early_bird_def.criteria:
            badges.append(self._create_badge(
                badge_id=self._generate_badge_id(),
                name=early_bird_def.name,
                category=BadgeCategory.TIMING,
                description=early_bird_def.description,
                criteria={'early_arrivals': early_bird_count, 'required_count': early_bird_def.criteria},
                user_id=user_id
            ))
        
        # Check punctuality pro badge (arrivals between PUNCTUALITY_HOUR:00-PUNCTUALITY_HOUR:PUNCTUALITY_MAX_MINUTE)
        punctuality_pro_def = self.badge_definitions.timing['punctuality_pro']
        on_time_count = 0
        for record in records:
            if record.time:
                hour = record.time.hour
                minute = record.time.minute
                if hour == PUNCTUALITY_HOUR and minute <= PUNCTUALITY_MAX_MINUTE:
                    on_time_count += 1
        
        if on_time_count >= punctuality_pro_def.criteria:
            badges.append(self._create_badge(
                badge_id=self._generate_badge_id(),
                name=punctuality_pro_def.name,
                category=BadgeCategory.TIMING,
                description=punctuality_pro_def.description,
                criteria={'on_time_arrivals': on_time_count, 'required_count': punctuality_pro_def.criteria},
                user_id=user_id
            ))
        
        return badges
    
    def _calculate_quality_badges(
        self,
        records: List[AttendanceRecord],
        user_id: str
    ) -> List[Badge]:
        """
        Calculate quality-based badges.
        
        Args:
            records: List of attendance records.
            user_id: ID of the user.
        
        Returns:
            List of quality badges earned.
        """
        badges: List[Badge] = []
        
        if not records:
            return badges
        
        # Count high-quality entries (face_quality_score >= HIGH_QUALITY_THRESHOLD)
        high_quality_count = 0
        for record in records:
            if record.face_quality_score and record.face_quality_score >= HIGH_QUALITY_THRESHOLD:
                high_quality_count += 1
        
        # Check quality seeker badge
        quality_seeker_def = self.badge_definitions.quality['quality_seeker']
        if high_quality_count >= quality_seeker_def.criteria:
            badges.append(self._create_badge(
                badge_id=self._generate_badge_id(),
                name=quality_seeker_def.name,
                category=BadgeCategory.QUALITY,
                description=quality_seeker_def.description,
                criteria={'high_quality_entries': high_quality_count, 'required_count': quality_seeker_def.criteria},
                user_id=user_id
            ))
        
        # Check quality master badge
        quality_master_def = self.badge_definitions.quality['quality_master']
        if high_quality_count >= quality_master_def.criteria:
            badges.append(self._create_badge(
                badge_id=self._generate_badge_id(),
                name=quality_master_def.name,
                category=BadgeCategory.QUALITY,
                description=quality_master_def.description,
                criteria={'high_quality_entries': high_quality_count, 'required_count': quality_master_def.criteria},
                user_id=user_id
            ))
        
        # Check perfectionist badge
        perfectionist_def = self.badge_definitions.quality['perfectionist']
        if high_quality_count >= perfectionist_def.criteria:
            badges.append(self._create_badge(
                badge_id=self._generate_badge_id(),
                name=perfectionist_def.name,
                category=BadgeCategory.QUALITY,
                description=perfectionist_def.description,
                criteria={'high_quality_entries': high_quality_count, 'required_count': perfectionist_def.criteria},
                user_id=user_id
            ))
        
        return badges
    
    def _create_badge(
        self,
        badge_id: str,
        name: str,
        category: BadgeCategory,
        description: str,
        criteria: dict,
        user_id: str
    ) -> Badge:
        """
        Create a Badge entity.
        
        Args:
            badge_id: Unique identifier for the badge.
            name: Name of the badge.
            category: Category of the badge.
            description: Description of the badge.
            criteria: Criteria that were met to earn the badge.
            user_id: ID of the user who earned the badge.
        
        Returns:
            Badge entity instance.
        """
        return Badge(
            badge_id=badge_id,
            name=name,
            category=category,
            description=description,
            criteria=criteria,
            earned_at=datetime.now(),
            user_id=user_id
        )
    
    @staticmethod
    def _generate_badge_id() -> str:
        """
        Generate a unique badge ID.
        
        Returns:
            Unique badge identifier.
        """
        return f"badge_{uuid.uuid4().hex[:12]}"

