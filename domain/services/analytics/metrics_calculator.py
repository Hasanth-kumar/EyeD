"""
Metrics calculator - pure business logic for calculating attendance metrics.

This module contains pure calculation logic with no side effects and
no dependencies on repositories or infrastructure.
"""

from collections import defaultdict
from datetime import date
from typing import List, Dict, Optional, Any

from domain.entities.attendance_record import AttendanceRecord
from domain.services.analytics.value_objects import (
    DailyStatistics,
    UserPerformance,
    PeriodSummary
)
from domain.services.gamification.streak_calculator import StreakCalculator


class MetricsCalculator:
    """
    Pure business logic calculator for attendance metrics.
    
    This class contains only calculation logic with no side effects.
    It works with attendance records and calculates various metrics.
    """
    
    @staticmethod
    def calculate_attendance_rate(
        records: List[AttendanceRecord],
        period_days: int
    ) -> float:
        """
        Calculate attendance rate as a percentage.
        
        Attendance rate is calculated as: (unique days with attendance / period_days) * 100
        The result is capped at 100%.
        
        Args:
            records: List of attendance records to analyze.
            period_days: Number of days in the evaluation period.
        
        Returns:
            Attendance rate percentage (0.0 to 100.0).
        
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
            ...     )
            ... ]
            >>> MetricsCalculator.calculate_attendance_rate(records, 30)
            3.33...
        """
        if not records or period_days <= 0:
            return 0.0
        
        # Filter to only valid/present records
        valid_records = [
            record for record in records
            if record.is_present() and record.confidence > 0
        ]
        
        if not valid_records:
            return 0.0
        
        # Count unique days with attendance
        unique_days = set()
        for record in valid_records:
            unique_days.add(record.date)
        
        # Calculate attendance rate
        attendance_rate = (len(unique_days) / period_days) * 100.0
        return min(attendance_rate, 100.0)  # Cap at 100%
    
    @staticmethod
    def calculate_average_confidence(
        records: List[AttendanceRecord]
    ) -> float:
        """
        Calculate average confidence score across all records.
        
        Only records with confidence > 0 are included in the calculation.
        
        Args:
            records: List of attendance records to analyze.
        
        Returns:
            Average confidence score (0.0 to 1.0), or 0.0 if no valid records.
        
        Examples:
            >>> from datetime import date, time
            >>> records = [
            ...     AttendanceRecord.create(
            ...         record_id="1", user_id="u1", user_name="User",
            ...         date=date.today(), time=time(9, 0), confidence=0.8,
            ...         liveness_verified=True, face_quality_score=0.9,
            ...         processing_time_ms=100, verification_stage="",
            ...         session_id="s1", device_info="", location=""
            ...     ),
            ...     AttendanceRecord.create(
            ...         record_id="2", user_id="u1", user_name="User",
            ...         date=date.today(), time=time(10, 0), confidence=0.9,
            ...         liveness_verified=True, face_quality_score=0.9,
            ...         processing_time_ms=100, verification_stage="",
            ...         session_id="s2", device_info="", location=""
            ...     )
            ... ]
            >>> MetricsCalculator.calculate_average_confidence(records)
            0.85
        """
        if not records:
            return 0.0
        
        # Filter to only records with confidence > 0
        valid_records = [
            record for record in records
            if record.confidence > 0
        ]
        
        if not valid_records:
            return 0.0
        
        # Calculate average
        total_confidence = sum(record.confidence for record in valid_records)
        return total_confidence / len(valid_records)
    
    @staticmethod
    def calculate_liveness_verification_rate(
        records: List[AttendanceRecord]
    ) -> float:
        """
        Calculate liveness verification rate as a percentage.
        
        Liveness verification rate is calculated as:
        (records with liveness_verified=True / total records) * 100
        
        Args:
            records: List of attendance records to analyze.
        
        Returns:
            Liveness verification rate percentage (0.0 to 100.0).
        
        Examples:
            >>> from datetime import date, time
            >>> records = [
            ...     AttendanceRecord.create(
            ...         record_id="1", user_id="u1", user_name="User",
            ...         date=date.today(), time=time(9, 0), confidence=0.9,
            ...         liveness_verified=True, face_quality_score=0.9,
            ...         processing_time_ms=100, verification_stage="",
            ...         session_id="s1", device_info="", location=""
            ...     ),
            ...     AttendanceRecord.create(
            ...         record_id="2", user_id="u1", user_name="User",
            ...         date=date.today(), time=time(10, 0), confidence=0.9,
            ...         liveness_verified=False, face_quality_score=0.9,
            ...         processing_time_ms=100, verification_stage="",
            ...         session_id="s2", device_info="", location=""
            ...     )
            ... ]
            >>> MetricsCalculator.calculate_liveness_verification_rate(records)
            50.0
        """
        if not records:
            return 0.0
        
        # Count records with liveness verification
        liveness_verified_count = sum(
            1 for record in records
            if record.liveness_verified
        )
        
        # Calculate rate
        if len(records) == 0:
            return 0.0
        
        return (liveness_verified_count / len(records)) * 100.0
    
    @staticmethod
    def calculate_daily_statistics(
        records: List[AttendanceRecord]
    ) -> Dict[date, DailyStatistics]:
        """
        Calculate daily statistics for all dates in the records.
        
        Groups records by date and calculates statistics for each day.
        
        Args:
            records: List of attendance records to analyze.
        
        Returns:
            Dictionary mapping date to DailyStatistics value object.
        
        Examples:
            >>> from datetime import date, time
            >>> today = date.today()
            >>> records = [
            ...     AttendanceRecord.create(
            ...         record_id="1", user_id="u1", user_name="User1",
            ...         date=today, time=time(9, 0), confidence=0.8,
            ...         liveness_verified=True, face_quality_score=0.9,
            ...         processing_time_ms=100, verification_stage="",
            ...         session_id="s1", device_info="", location=""
            ...     ),
            ...     AttendanceRecord.create(
            ...         record_id="2", user_id="u2", user_name="User2",
            ...         date=today, time=time(10, 0), confidence=0.9,
            ...         liveness_verified=True, face_quality_score=0.9,
            ...         processing_time_ms=100, verification_stage="",
            ...         session_id="s2", device_info="", location=""
            ...     )
            ... ]
            >>> stats = MetricsCalculator.calculate_daily_statistics(records)
            >>> len(stats)
            1
        """
        if not records:
            return {}
        
        # Group records by date
        records_by_date: Dict[date, List[AttendanceRecord]] = defaultdict(list)
        for record in records:
            records_by_date[record.date].append(record)
        
        # Calculate statistics for each date
        daily_stats: Dict[date, DailyStatistics] = {}
        
        for stat_date, date_records in records_by_date.items():
            # Filter to valid records (confidence > 0)
            valid_records = [
                record for record in date_records
                if record.confidence > 0
            ]
            
            if not valid_records:
                continue
            
            # Calculate metrics
            total_entries = len(valid_records)
            unique_users = len(set(record.user_id for record in valid_records))
            
            # Average confidence
            total_confidence = sum(record.confidence for record in valid_records)
            average_confidence = total_confidence / total_entries
            
            # Liveness verification rate
            liveness_verified_count = sum(
                1 for record in valid_records
                if record.liveness_verified
            )
            liveness_verification_rate = (
                (liveness_verified_count / total_entries) * 100.0
                if total_entries > 0 else 0.0
            )
            
            # Create value object
            daily_stats[stat_date] = DailyStatistics(
                date=stat_date,
                total_entries=total_entries,
                unique_users=unique_users,
                average_confidence=average_confidence,
                liveness_verification_rate=liveness_verification_rate
            )
        
        return daily_stats
    
    @staticmethod
    def calculate_user_performance(
        user_id: str,
        records: List[AttendanceRecord],
        period_days: int = 30
    ) -> UserPerformance:
        """
        Calculate performance metrics for a specific user.
        
        Args:
            user_id: ID of the user to calculate performance for.
            records: List of attendance records (should include records for this user).
            period_days: Number of days in the evaluation period (default: 30).
        
        Returns:
            UserPerformance value object with calculated metrics.
        
        Examples:
            >>> from datetime import date, time
            >>> today = date.today()
            >>> records = [
            ...     AttendanceRecord.create(
            ...         record_id="1", user_id="u1", user_name="User",
            ...         date=today, time=time(9, 0), confidence=0.8,
            ...         liveness_verified=True, face_quality_score=0.9,
            ...         processing_time_ms=100, verification_stage="",
            ...         session_id="s1", device_info="", location=""
            ...     )
            ... ]
            >>> perf = MetricsCalculator.calculate_user_performance("u1", records, 30)
            >>> perf.user_id
            'u1'
        """
        # Filter to records for this user
        user_records = [
            record for record in records
            if record.user_id == user_id
        ]
        
        if not user_records:
            return UserPerformance(
                user_id=user_id,
                total_attendance=0,
                attendance_rate=0.0,
                average_confidence=0.0,
                best_streak=0,
                current_streak=0
            )
        
        # Filter to valid/present records
        valid_records = [
            record for record in user_records
            if record.is_present() and record.confidence > 0
        ]
        
        # Calculate total attendance
        total_attendance = len(valid_records)
        
        # Calculate attendance rate
        attendance_rate = MetricsCalculator.calculate_attendance_rate(
            valid_records,
            period_days
        )
        
        # Calculate average confidence
        average_confidence = MetricsCalculator.calculate_average_confidence(
            valid_records
        )
        
        # Calculate streaks using StreakCalculator
        current_streak = StreakCalculator.calculate_current_streak(valid_records)
        best_streak = StreakCalculator.calculate_max_streak(valid_records)
        
        return UserPerformance(
            user_id=user_id,
            total_attendance=total_attendance,
            attendance_rate=attendance_rate,
            average_confidence=average_confidence,
            best_streak=best_streak,
            current_streak=current_streak
        )
    
    @staticmethod
    def calculate_attendance_summary(
        records: List[AttendanceRecord],
        target_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calculate summary statistics for attendance records.
        
        Provides an aggregated summary of attendance data, optionally filtered
        by a specific date. This is pure calculation logic with no side effects.
        
        Args:
            records: List of attendance records to analyze.
            target_date: Optional date to filter records. If provided, only records
                        matching this date are included. If None, all records are used.
        
        Returns:
            Dictionary containing summary metrics:
            - total_entries: Total number of attendance entries
            - unique_users: Number of unique users
            - date: Target date string or 'all' if no date filter
            - avg_confidence: Average confidence score (0.0 to 1.0)
            - min_confidence: Minimum confidence score
            - max_confidence: Maximum confidence score
            - liveness_verified_count: Number of records with liveness verified
            - liveness_verification_rate: Percentage of records with liveness verified
        
        Examples:
            >>> from datetime import date, time
            >>> today = date.today()
            >>> records = [
            ...     AttendanceRecord.create(
            ...         record_id="1", user_id="u1", user_name="User1",
            ...         date=today, time=time(9, 0), confidence=0.8,
            ...         liveness_verified=True, face_quality_score=0.9,
            ...         processing_time_ms=100, verification_stage="",
            ...         session_id="s1", device_info="", location=""
            ...     ),
            ...     AttendanceRecord.create(
            ...         record_id="2", user_id="u2", user_name="User2",
            ...         date=today, time=time(10, 0), confidence=0.9,
            ...         liveness_verified=True, face_quality_score=0.9,
            ...         processing_time_ms=100, verification_stage="",
            ...         session_id="s2", device_info="", location=""
            ...     )
            ... ]
            >>> summary = MetricsCalculator.calculate_attendance_summary(records, today)
            >>> summary['total_entries']
            2
            >>> summary['unique_users']
            2
        """
        # Filter by target_date if provided
        if target_date:
            filtered_records = [
                record for record in records
                if record.date == target_date
            ]
        else:
            filtered_records = records
        
        if not filtered_records:
            return {
                'total_entries': 0,
                'unique_users': 0,
                'date': target_date.strftime('%Y-%m-%d') if target_date else 'all',
                'avg_confidence': 0.0,
                'min_confidence': 0.0,
                'max_confidence': 0.0,
                'liveness_verified_count': 0,
                'liveness_verification_rate': 0.0
            }
        
        # Calculate basic metrics
        total_entries = len(filtered_records)
        unique_users = len(set(record.user_id for record in filtered_records))
        
        # Calculate confidence statistics (only for records with confidence > 0)
        confidences = [r.confidence for r in filtered_records if r.confidence > 0]
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            min_confidence = min(confidences)
            max_confidence = max(confidences)
        else:
            avg_confidence = 0.0
            min_confidence = 0.0
            max_confidence = 0.0
        
        # Calculate liveness verification statistics
        liveness_verified_count = sum(
            1 for r in filtered_records
            if r.liveness_verified
        )
        liveness_verification_rate = (
            (liveness_verified_count / total_entries * 100) if total_entries > 0 else 0.0
        )
        
        return {
            'total_entries': total_entries,
            'unique_users': unique_users,
            'date': target_date.strftime('%Y-%m-%d') if target_date else 'all',
            'avg_confidence': round(avg_confidence, 3),
            'min_confidence': round(min_confidence, 3),
            'max_confidence': round(max_confidence, 3),
            'liveness_verified_count': liveness_verified_count,
            'liveness_verification_rate': round(liveness_verification_rate, 2)
        }
    
    @staticmethod
    def calculate_period_summary(
        records: List[AttendanceRecord]
    ) -> PeriodSummary:
        """
        Calculate aggregated summary statistics for a period from attendance records.
        
        This method aggregates all records to provide period-level statistics:
        - Total entries across all records
        - Unique users (count of distinct user_ids)
        - Weighted average confidence
        - Weighted average liveness verification rate
        
        Args:
            records: List of attendance records to analyze.
        
        Returns:
            PeriodSummary value object with aggregated statistics.
        
        Examples:
            >>> from datetime import date, time
            >>> today = date.today()
            >>> records = [
            ...     AttendanceRecord.create(
            ...         record_id="1", user_id="u1", user_name="User1",
            ...         date=today, time=time(9, 0), confidence=0.8,
            ...         liveness_verified=True, face_quality_score=0.9,
            ...         processing_time_ms=100, verification_stage="",
            ...         session_id="s1", device_info="", location=""
            ...     ),
            ...     AttendanceRecord.create(
            ...         record_id="2", user_id="u2", user_name="User2",
            ...         date=today, time=time(10, 0), confidence=0.9,
            ...         liveness_verified=True, face_quality_score=0.9,
            ...         processing_time_ms=100, verification_stage="",
            ...         session_id="s2", device_info="", location=""
            ...     )
            ... ]
            >>> summary = MetricsCalculator.calculate_period_summary(records)
            >>> summary.total_entries
            2
            >>> summary.unique_users
            2
        """
        if not records:
            return PeriodSummary(
                total_entries=0,
                unique_users=0,
                average_confidence=0.0,
                liveness_verification_rate=0.0
            )
        
        # Filter to valid records (confidence > 0)
        valid_records = [
            record for record in records
            if record.confidence > 0
        ]
        
        if not valid_records:
            return PeriodSummary(
                total_entries=0,
                unique_users=0,
                average_confidence=0.0,
                liveness_verification_rate=0.0
            )
        
        # Calculate basic metrics
        total_entries = len(valid_records)
        unique_users = len(set(record.user_id for record in valid_records))
        
        # Calculate weighted average confidence
        total_confidence = sum(record.confidence for record in valid_records)
        average_confidence = total_confidence / total_entries
        
        # Calculate liveness verification rate
        liveness_verified_count = sum(
            1 for record in valid_records
            if record.liveness_verified
        )
        liveness_verification_rate = (
            (liveness_verified_count / total_entries) * 100.0
            if total_entries > 0 else 0.0
        )
        
        return PeriodSummary(
            total_entries=total_entries,
            unique_users=unique_users,
            average_confidence=average_confidence,
            liveness_verification_rate=liveness_verification_rate
        )
    
    @staticmethod
    def calculate_weekly_attendance_rate(
        daily_statistics: Dict[date, 'DailyStatistics'],
        active_users_count: int
    ) -> float:
        """
        Calculate weekly attendance rate based on daily statistics.
        
        Weekly attendance rate is calculated as the average of daily attendance rates,
        where each daily rate is: (unique_users / active_users_count) * 100
        
        This represents the average percentage of active users who attended each day
        during the week.
        
        Args:
            daily_statistics: Dictionary mapping date to DailyStatistics value object.
            active_users_count: Total number of active users in the system.
        
        Returns:
            Weekly attendance rate percentage (0.0 to 100.0).
        
        Examples:
            >>> from datetime import date
            >>> from domain.services.analytics.value_objects import DailyStatistics
            >>> today = date.today()
            >>> daily_stats = {
            ...     today: DailyStatistics(
            ...         date=today,
            ...         total_entries=5,
            ...         unique_users=3,
            ...         average_confidence=0.8,
            ...         liveness_verification_rate=100.0
            ...     )
            ... }
            >>> MetricsCalculator.calculate_weekly_attendance_rate(daily_stats, 10)
            30.0
        """
        if not daily_statistics or active_users_count <= 0:
            return 0.0
        
        # Calculate daily attendance rates
        daily_rates = []
        for daily_stats in daily_statistics.values():
            if daily_stats.unique_users > 0:
                # Daily attendance rate = (unique_users / active_users) * 100
                daily_rate = (daily_stats.unique_users / active_users_count) * 100.0
                daily_rates.append(min(daily_rate, 100.0))  # Cap at 100%
        
        # Return average of daily rates
        if not daily_rates:
            return 0.0
        
        return sum(daily_rates) / len(daily_rates)


