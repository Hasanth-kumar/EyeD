"""
Streak calculator - pure business logic for calculating attendance streaks.

This module contains pure calculation logic with no side effects and
no dependencies on repositories or infrastructure.
"""

from datetime import date, timedelta
from typing import List

from domain.entities.attendance_record import AttendanceRecord
from domain.services.gamification.value_objects import StreakBreakdown


class StreakCalculator:
    """
    Pure business logic calculator for attendance streaks.
    
    This class contains only calculation logic with no side effects.
    It works with sorted attendance records and calculates streak metrics.
    """
    
    @staticmethod
    def calculate_current_streak(records: List[AttendanceRecord]) -> int:
        """
        Calculate the current consecutive day streak from today backwards.
        
        The current streak is calculated by counting consecutive days
        starting from today and going backwards. Only records with
        status 'Present' are counted.
        
        Args:
            records: List of attendance records, should be sorted by date
                    (most recent first is preferred, but not required).
        
        Returns:
            Current consecutive day streak count (0 if no streak).
        
        Examples:
            >>> from datetime import date, time
            >>> today = date.today()
            >>> records = [
            ...     AttendanceRecord.create(
            ...         record_id="1", user_id="u1", user_name="User",
            ...         date=today, time=time(9, 0), confidence=0.9,
            ...         liveness_verified=True, face_quality_score=0.9,
            ...         processing_time_ms=100, verification_stage="", 
            ...         session_id="s1", device_info="", location=""
            ...     ),
            ...     AttendanceRecord.create(
            ...         record_id="2", user_id="u1", user_name="User",
            ...         date=today - timedelta(days=1), time=time(9, 0),
            ...         confidence=0.9, liveness_verified=True,
            ...         face_quality_score=0.9, processing_time_ms=100,
            ...         verification_stage="", session_id="s2", device_info="", location=""
            ...     )
            ... ]
            >>> StreakCalculator.calculate_current_streak(records)
            2
        """
        if not records:
            return 0
        
        # Filter to only present records and sort by date (most recent first)
        present_records = [
            record for record in records
            if record.is_present()
        ]
        
        if not present_records:
            return 0
        
        # Sort by date descending (most recent first)
        sorted_records = sorted(
            present_records,
            key=lambda r: r.date,
            reverse=True
        )
        
        # Get unique dates from records (most recent first)
        unique_dates = sorted(
            {record.date for record in sorted_records},
            reverse=True
        )
        
        if not unique_dates:
            return 0
        
        # Calculate current streak starting from today
        current_streak = 0
        expected_date = date.today()
        
        for record_date in unique_dates:
            # Only count if the date matches the expected consecutive date
            if record_date == expected_date:
                current_streak += 1
                expected_date = expected_date - timedelta(days=1)
            elif record_date < expected_date:
                # We've found a date that's before the expected date
                # This means there's a gap, so the streak is broken
                break
        
        return current_streak
    
    @staticmethod
    def calculate_max_streak(records: List[AttendanceRecord]) -> int:
        """
        Calculate the maximum consecutive day streak from all records.
        
        This finds the longest sequence of consecutive days with
        'Present' status across the entire record set.
        
        Args:
            records: List of attendance records, should be sorted by date
                    (ascending is preferred, but not required).
        
        Returns:
            Maximum consecutive day streak count (0 if no records).
        
        Examples:
            >>> from datetime import date, time, timedelta
            >>> base_date = date(2025, 1, 1)
            >>> records = [
            ...     AttendanceRecord.create(
            ...         record_id=str(i), user_id="u1", user_name="User",
            ...         date=base_date + timedelta(days=i), time=time(9, 0),
            ...         confidence=0.9, liveness_verified=True,
            ...         face_quality_score=0.9, processing_time_ms=100,
            ...         verification_stage="", session_id=f"s{i}", device_info="", location=""
            ...     )
            ...     for i in range(5)  # 5 consecutive days
            ... ]
            >>> StreakCalculator.calculate_max_streak(records)
            5
        """
        if not records:
            return 0
        
        # Filter to only present records
        present_records = [
            record for record in records
            if record.is_present()
        ]
        
        if not present_records:
            return 0
        
        # Sort by date ascending
        sorted_records = sorted(
            present_records,
            key=lambda r: r.date
        )
        
        if len(sorted_records) == 1:
            return 1
        
        max_streak = 1
        current_streak = 1
        
        for i in range(1, len(sorted_records)):
            prev_date = sorted_records[i - 1].date
            curr_date = sorted_records[i].date
            
            # Check if consecutive days
            days_diff = (curr_date - prev_date).days
            
            if days_diff == 1:
                current_streak += 1
            else:
                max_streak = max(max_streak, current_streak)
                current_streak = 1
        
        # Update max streak with final current streak
        max_streak = max(max_streak, current_streak)
        
        return max_streak
    
    @staticmethod
    def calculate_streak_breakdown(records: List[AttendanceRecord]) -> StreakBreakdown:
        """
        Calculate complete streak breakdown including current streak, max streak, and dates.
        
        This method calculates both current and max streaks, and also collects
        the dates that are part of the current streak.
        
        Args:
            records: List of attendance records, should be sorted by date
                    (most recent first is preferred for current streak calculation).
        
        Returns:
            StreakBreakdown value object with all streak metrics.
        
        Examples:
            >>> from datetime import date, time, timedelta
            >>> today = date.today()
            >>> records = [
            ...     AttendanceRecord.create(
            ...         record_id=str(i), user_id="u1", user_name="User",
            ...         date=today - timedelta(days=i), time=time(9, 0),
            ...         confidence=0.9, liveness_verified=True,
            ...         face_quality_score=0.9, processing_time_ms=100,
            ...         verification_stage="", session_id=f"s{i}", device_info="", location=""
            ...     )
            ...     for i in range(3)  # 3 consecutive days ending today
            ... ]
            >>> breakdown = StreakCalculator.calculate_streak_breakdown(records)
            >>> breakdown.current_streak
            3
            >>> breakdown.max_streak
            3
        """
        if not records:
            return StreakBreakdown(
                current_streak=0,
                max_streak=0,
                streak_dates=[]
            )
        
        # Filter to only present records
        present_records = [
            record for record in records
            if record.is_present()
        ]
        
        if not present_records:
            return StreakBreakdown(
                current_streak=0,
                max_streak=0,
                streak_dates=[]
            )
        
        # Calculate current streak and collect dates
        sorted_records_desc = sorted(
            present_records,
            key=lambda r: r.date,
            reverse=True
        )
        
        # Get unique dates from records (most recent first)
        unique_dates = sorted(
            {record.date for record in sorted_records_desc},
            reverse=True
        )
        
        # Calculate current streak and collect dates
        current_streak = 0
        expected_date = date.today()
        streak_dates: List[date] = []
        
        for record_date in unique_dates:
            # Only count if the date matches the expected consecutive date
            if record_date == expected_date:
                current_streak += 1
                streak_dates.append(record_date)
                expected_date = expected_date - timedelta(days=1)
            elif record_date < expected_date:
                # We've found a date that's before the expected date
                # This means there's a gap, so the streak is broken
                break
        
        # Sort streak dates ascending for consistency
        streak_dates.sort()
        
        # Calculate max streak
        sorted_records_asc = sorted(
            present_records,
            key=lambda r: r.date
        )
        
        max_streak = 1
        current_max_streak = 1
        
        if len(sorted_records_asc) > 1:
            for i in range(1, len(sorted_records_asc)):
                prev_date = sorted_records_asc[i - 1].date
                curr_date = sorted_records_asc[i].date
                
                days_diff = (curr_date - prev_date).days
                
                if days_diff == 1:
                    current_max_streak += 1
                else:
                    max_streak = max(max_streak, current_max_streak)
                    current_max_streak = 1
            
            max_streak = max(max_streak, current_max_streak)
        
        return StreakBreakdown(
            current_streak=current_streak,
            max_streak=max_streak,
            streak_dates=streak_dates
        )

