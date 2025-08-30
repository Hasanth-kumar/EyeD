"""
Analytics Interface for EyeD AI Attendance System

This interface defines the contract for analytics and reporting operations including
attendance trends, user performance metrics, and system analytics.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, date, timedelta
import pandas as pd
from enum import Enum


class AnalyticsPeriod(Enum):
    """Enumeration of analytics periods"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class AttendanceTrend:
    """Data class for attendance trend analysis"""
    def __init__(self, period: AnalyticsPeriod, start_date: date, end_date: date,
                 total_attendance: int, unique_users: int, average_confidence: float,
                 liveness_verification_rate: float, trend_direction: str):
        self.period = period
        self.start_date = start_date
        self.end_date = end_date
        self.total_attendance = total_attendance
        self.unique_users = unique_users
        self.average_confidence = average_confidence
        self.liveness_verification_rate = liveness_verification_rate
        self.trend_direction = trend_direction


class UserPerformance:
    """Data class for user performance metrics"""
    def __init__(self, user_id: str, user_name: str, total_attendance: int,
                 average_confidence: float, liveness_verification_rate: float,
                 attendance_consistency: float, last_attendance: Optional[datetime]):
        self.user_id = user_id
        self.user_name = user_name
        self.total_attendance = total_attendance
        self.average_confidence = average_confidence
        self.liveness_verification_rate = liveness_verification_rate
        self.attendance_consistency = attendance_consistency
        self.last_attendance = last_attendance


class SystemMetrics:
    """Data class for system performance metrics"""
    def __init__(self, total_users: int, active_users: int, system_uptime: float,
                 average_response_time: float, recognition_accuracy: float,
                 liveness_detection_accuracy: float, error_rate: float):
        self.total_users = total_users
        self.active_users = active_users
        self.system_uptime = system_uptime
        self.average_response_time = average_response_time
        self.recognition_accuracy = recognition_accuracy
        self.liveness_detection_accuracy = liveness_detection_accuracy
        self.error_rate = error_rate


class AnalyticsInterface(ABC):
    """
    Abstract interface for analytics and reporting operations
    
    This interface defines the contract that all analytics implementations
    must follow, ensuring consistent behavior across different analytics engines.
    """
    
    @abstractmethod
    def get_attendance_trends(self, period: AnalyticsPeriod,
                             start_date: Optional[date] = None,
                             end_date: Optional[date] = None) -> List[AttendanceTrend]:
        """
        Get attendance trends for a specific period
        
        Args:
            period: Analytics period (daily, weekly, monthly, etc.)
            start_date: Optional start date for analysis
            end_date: Optional end date for analysis
            
        Returns:
            List of attendance trends
        """
        pass
    
    @abstractmethod
    def get_user_performance(self, user_id: Optional[str] = None,
                            start_date: Optional[date] = None,
                            end_date: Optional[date] = None) -> List[UserPerformance]:
        """
        Get user performance metrics
        
        Args:
            user_id: Optional user ID to filter by
            start_date: Optional start date for analysis
            end_date: Optional end date for analysis
            
        Returns:
            List of user performance metrics
        """
        pass
    
    @abstractmethod
    def get_system_metrics(self, start_date: Optional[date] = None,
                          end_date: Optional[date] = None) -> SystemMetrics:
        """
        Get system performance metrics
        
        Args:
            start_date: Optional start date for analysis
            end_date: Optional end date for analysis
            
        Returns:
            SystemMetrics object
        """
        pass
    
    @abstractmethod
    def generate_attendance_report(self, report_type: str,
                                 start_date: Optional[date] = None,
                                 end_date: Optional[date] = None,
                                 format: str = "csv") -> Union[str, bytes]:
        """
        Generate attendance report in specified format
        
        Args:
            report_type: Type of report to generate
            start_date: Optional start date for report
            end_date: Optional end date for report
            format: Output format ("csv", "json", "excel", "pdf")
            
        Returns:
            Generated report as string or bytes
        """
        pass
    
    @abstractmethod
    def get_peak_hours_analysis(self, start_date: Optional[date] = None,
                               end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Analyze peak attendance hours
        
        Args:
            start_date: Optional start date for analysis
            end_date: Optional end date for analysis
            
        Returns:
            Dictionary containing peak hours analysis
        """
        pass
    
    @abstractmethod
    def get_geographic_analysis(self, start_date: Optional[date] = None,
                               end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Analyze attendance by geographic location
        
        Args:
            start_date: Optional start date for analysis
            end_date: Optional end date for analysis
            
        Returns:
            Dictionary containing geographic analysis
        """
        pass
    
    @abstractmethod
    def get_device_performance_analysis(self, start_date: Optional[date] = None,
                                      end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Analyze system performance by device
        
        Args:
            start_date: Optional start date for analysis
            end_date: Optional end date for analysis
            
        Returns:
            Dictionary containing device performance analysis
        """
        pass
    
    @abstractmethod
    def get_recognition_accuracy_trends(self, start_date: Optional[date] = None,
                                       end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Analyze face recognition accuracy trends
        
        Args:
            start_date: Optional start date for analysis
            end_date: Optional end date for analysis
            
        Returns:
            Dictionary containing accuracy trends
        """
        pass
    
    @abstractmethod
    def get_liveness_detection_analysis(self, start_date: Optional[date] = None,
                                       end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Analyze liveness detection performance
        
        Args:
            start_date: Optional start date for analysis
            end_date: Optional end date for analysis
            
        Returns:
            Dictionary containing liveness detection analysis
        """
        pass
    
    @abstractmethod
    def export_analytics_data(self, data_type: str,
                             start_date: Optional[date] = None,
                             end_date: Optional[date] = None,
                             format: str = "csv") -> Union[str, bytes]:
        """
        Export analytics data in specified format
        
        Args:
            data_type: Type of data to export
            start_date: Optional start date for export
            end_date: Optional end date for export
            format: Output format ("csv", "json", "excel")
            
        Returns:
            Exported data as string or bytes
        """
        pass
    
    @abstractmethod
    def get_analytics_configuration(self) -> Dict[str, Any]:
        """
        Get current analytics configuration
        
        Returns:
            Dictionary containing current configuration
        """
        pass
    
    @abstractmethod
    def update_analytics_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Update analytics configuration
        
        Args:
            config: New configuration parameters
            
        Returns:
            True if update was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def is_healthy(self) -> bool:
        """
        Check if the analytics system is in a healthy state
        
        Returns:
            True if healthy, False otherwise
        """
        pass
    
    @abstractmethod
    def get_data_quality_metrics(self) -> Dict[str, Any]:
        """
        Get data quality metrics for analytics
        
        Returns:
            Dictionary containing data quality metrics
        """
        pass
