"""
Attendance Manager Interface for EyeD AI Attendance System

This interface defines the contract for attendance management operations including
logging, verification, analytics, and session management.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
import numpy as np
from datetime import datetime, date


class AttendanceEntry:
    """Data class for attendance entries"""
    def __init__(self, name: str, user_id: str, date: str, time: str, 
                 status: str, confidence: float, liveness_verified: bool,
                 face_quality_score: float, processing_time_ms: float,
                 verification_stage: str, session_id: str, device_info: str,
                 location: str):
        self.name = name
        self.user_id = user_id
        self.date = date
        self.time = time
        self.status = status
        self.confidence = confidence
        self.liveness_verified = liveness_verified
        self.face_quality_score = face_quality_score
        self.processing_time_ms = processing_time_ms
        self.verification_stage = verification_stage
        self.session_id = session_id
        self.device_info = device_info
        self.location = location


class AttendanceSession:
    """Data class for attendance sessions"""
    def __init__(self, session_id: str, start_time: datetime, user_id: str,
                 user_name: str, status: str, confidence: float,
                 liveness_verified: bool, face_quality_score: float,
                 processing_time_ms: float, verification_stage: str,
                 device_info: str, location: str):
        self.session_id = session_id
        self.start_time = start_time
        self.end_time: Optional[datetime] = None
        self.user_id = user_id
        self.user_name = user_name
        self.status = status
        self.confidence = confidence
        self.liveness_verified = liveness_verified
        self.face_quality_score = face_quality_score
        self.processing_time_ms = processing_time_ms
        self.verification_stage = verification_stage
        self.device_info = device_info
        self.location = location


class AttendanceManagerInterface(ABC):
    """
    Abstract interface for attendance management operations
    
    This interface defines the contract that all attendance manager implementations
    must follow, ensuring consistent behavior across different implementations.
    """
    
    @abstractmethod
    def log_attendance(self, face_image: np.ndarray, user_id: Optional[str] = None,
                      device_info: str = "", location: str = "") -> Optional[AttendanceEntry]:
        """
        Log attendance for a detected face
        
        Args:
            face_image: Face image for recognition
            user_id: Optional user ID if known
            device_info: Information about the device used
            location: Location where attendance was logged
            
        Returns:
            AttendanceEntry if successful, None otherwise
        """
        pass
    
    @abstractmethod
    def verify_attendance(self, face_image: np.ndarray, 
                         user_id: str) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Verify attendance for a specific user
        
        Args:
            face_image: Face image for verification
            user_id: User ID to verify
            
        Returns:
            Tuple of (success, confidence, verification_details)
        """
        pass
    
    @abstractmethod
    def get_attendance_history(self, user_id: Optional[str] = None,
                              start_date: Optional[date] = None,
                              end_date: Optional[date] = None) -> List[AttendanceEntry]:
        """
        Get attendance history for a user or all users
        
        Args:
            user_id: Optional user ID to filter by
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List of attendance entries
        """
        pass
    
    @abstractmethod
    def get_attendance_summary(self, date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get attendance summary for a specific date or overall
        
        Args:
            date: Optional date for summary, uses today if None
            
        Returns:
            Dictionary containing attendance summary
        """
        pass
    
    @abstractmethod
    def start_session(self, user_id: str, user_name: str,
                     device_info: str = "", location: str = "") -> str:
        """
        Start a new attendance session
        
        Args:
            user_id: User ID for the session
            user_name: User name for the session
            device_info: Information about the device
            location: Location for the session
            
        Returns:
            Session ID for the new session
        """
        pass
    
    @abstractmethod
    def end_session(self, session_id: str) -> bool:
        """
        End an attendance session
        
        Args:
            session_id: ID of the session to end
            
        Returns:
            True if session was ended successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def get_active_sessions(self) -> List[AttendanceSession]:
        """
        Get all currently active sessions
        
        Returns:
            List of active attendance sessions
        """
        pass
    
    @abstractmethod
    def export_attendance_data(self, format: str = "csv",
                              start_date: Optional[date] = None,
                              end_date: Optional[date] = None) -> Union[str, bytes]:
        """
        Export attendance data in specified format
        
        Args:
            format: Export format ("csv", "json", "excel")
            start_date: Optional start date for export
            end_date: Optional end date for export
            
        Returns:
            Exported data as string or bytes
        """
        pass
    
    @abstractmethod
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get system performance metrics
        
        Returns:
            Dictionary containing performance metrics
        """
        pass
    
    @abstractmethod
    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Update attendance manager configuration
        
        Args:
            config: New configuration parameters
            
        Returns:
            True if update was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current configuration
        
        Returns:
            Dictionary containing current configuration
        """
        pass
    
    @abstractmethod
    def is_healthy(self) -> bool:
        """
        Check if the attendance manager is in a healthy state
        
        Returns:
            True if healthy, False otherwise
        """
        pass
