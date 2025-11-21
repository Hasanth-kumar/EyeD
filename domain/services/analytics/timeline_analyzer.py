"""
Timeline analyzer domain service.

Pure business logic for analyzing arrival patterns and timelines from attendance records.
This service focuses solely on analysis - no data formatting or infrastructure concerns.
"""

from typing import List, Dict
from datetime import time

from domain.entities.attendance_record import AttendanceRecord
from domain.services.analytics.value_objects import ArrivalPatterns


class TimelineAnalyzer:
    """
    Analyzer for attendance timeline and arrival patterns.
    
    Single Responsibility: Analyze timelines ONLY.
    No data formatting or infrastructure dependencies.
    
    Examples:
        >>> from datetime import date, time
        >>> from domain.entities.attendance_record import AttendanceRecord
        >>> 
        >>> records = [
        ...     AttendanceRecord.create(
        ...         record_id="rec1",
        ...         user_id="user1",
        ...         user_name="John",
        ...         date=date(2025, 1, 1),
        ...         time=time(8, 30),
        ...         confidence=0.9,
        ...         liveness_verified=True,
        ...         face_quality_score=0.85,
        ...         processing_time_ms=150.0,
        ...         verification_stage="Verified",
        ...         session_id="sess1",
        ...         device_info="Webcam",
        ...         location="Office"
        ...     )
        ... ]
        >>> analyzer = TimelineAnalyzer()
        >>> patterns = analyzer.analyze_arrival_patterns(records)
        >>> patterns.early_bird_count
        1
    """
    
    def analyze_arrival_patterns(self, records: List[AttendanceRecord]) -> ArrivalPatterns:
        """
        Analyze arrival time patterns from attendance records.
        
        Args:
            records: List of attendance records to analyze.
        
        Returns:
            ArrivalPatterns value object containing analysis results.
        
        Raises:
            ValueError: If records list is empty.
        """
        if not records:
            raise ValueError("Cannot analyze patterns from empty records list")
        
        # Extract arrival times in minutes since midnight
        arrival_minutes = []
        for record in records:
            minutes = self._time_to_minutes(record.time)
            arrival_minutes.append(minutes)
        
        if not arrival_minutes:
            # Return empty patterns if no valid times
            return ArrivalPatterns(
                average_arrival_time_minutes=0.0,
                earliest_arrival_minutes=0.0,
                latest_arrival_minutes=0.0,
                hourly_distribution={},
                early_bird_count=0,
                on_time_count=0,
                late_count=0
            )
        
        # Calculate statistics
        average_arrival = sum(arrival_minutes) / len(arrival_minutes)
        earliest_arrival = min(arrival_minutes)
        latest_arrival = max(arrival_minutes)
        
        # Calculate hourly distribution
        hourly_distribution = self.calculate_hourly_distribution(records)
        
        # Count early birds (arrival at or before 8:00)
        early_bird_count = len([m for m in arrival_minutes if m <= 8 * 60])
        
        # Count on-time arrivals (9:00-9:15)
        on_time_count = len([
            m for m in arrival_minutes 
            if 9 * 60 <= m <= 9 * 60 + 15
        ])
        
        # Count late arrivals (after 9:15)
        late_count = len([m for m in arrival_minutes if m > 9 * 60 + 15])
        
        return ArrivalPatterns(
            average_arrival_time_minutes=average_arrival,
            earliest_arrival_minutes=earliest_arrival,
            latest_arrival_minutes=latest_arrival,
            hourly_distribution=hourly_distribution,
            early_bird_count=early_bird_count,
            on_time_count=on_time_count,
            late_count=late_count
        )
    
    def identify_early_birds(
        self, 
        records: List[AttendanceRecord], 
        threshold_hour: int
    ) -> List[str]:
        """
        Identify users who arrive at or before the threshold hour.
        
        Args:
            records: List of attendance records to analyze.
            threshold_hour: Hour threshold (0-23). Arrivals at or before this hour are considered early.
        
        Returns:
            List of user_ids who are early birds (arrive at or before threshold_hour).
        
        Raises:
            ValueError: If threshold_hour is not between 0 and 23.
        """
        if not 0 <= threshold_hour <= 23:
            raise ValueError("threshold_hour must be between 0 and 23")
        
        threshold_minutes = threshold_hour * 60
        early_bird_user_ids = set()
        
        for record in records:
            arrival_minutes = self._time_to_minutes(record.time)
            if arrival_minutes <= threshold_minutes:
                early_bird_user_ids.add(record.user_id)
        
        return sorted(list(early_bird_user_ids))
    
    def identify_late_comers(
        self, 
        records: List[AttendanceRecord], 
        threshold_hour: int
    ) -> List[str]:
        """
        Identify users who arrive after the threshold hour.
        
        Args:
            records: List of attendance records to analyze.
            threshold_hour: Hour threshold (0-23). Arrivals after this hour are considered late.
        
        Returns:
            List of user_ids who are late comers (arrive after threshold_hour).
        
        Raises:
            ValueError: If threshold_hour is not between 0 and 23.
        """
        if not 0 <= threshold_hour <= 23:
            raise ValueError("threshold_hour must be between 0 and 23")
        
        threshold_minutes = threshold_hour * 60
        late_comer_user_ids = set()
        
        for record in records:
            arrival_minutes = self._time_to_minutes(record.time)
            if arrival_minutes > threshold_minutes:
                late_comer_user_ids.add(record.user_id)
        
        return sorted(list(late_comer_user_ids))
    
    def calculate_hourly_distribution(
        self, 
        records: List[AttendanceRecord]
    ) -> Dict[int, int]:
        """
        Calculate distribution of arrivals by hour of day.
        
        Args:
            records: List of attendance records to analyze.
        
        Returns:
            Dictionary mapping hour (0-23) to count of arrivals in that hour.
        """
        hourly_distribution: Dict[int, int] = {}
        
        for record in records:
            hour = record.time.hour
            hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
        
        # Ensure all hours 0-23 are present (with 0 count if no arrivals)
        # Actually, let's just return the hours that have arrivals (as per original implementation)
        return hourly_distribution
    
    @staticmethod
    def _time_to_minutes(t: time) -> int:
        """
        Convert time to minutes since midnight.
        
        Args:
            t: Time object to convert.
        
        Returns:
            Minutes since midnight (0-1439).
        """
        return t.hour * 60 + t.minute













