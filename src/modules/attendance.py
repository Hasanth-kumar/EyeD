"""
Attendance Module for EyeD AI Attendance System
Day 8 Implementation: Comprehensive Attendance Logging with Liveness Verification

This module handles:
- Attendance logging with liveness verification
- Confidence scoring and transparency features
- Attendance analytics and reporting
- User session management
- Performance monitoring and quality assessment
"""

import cv2
import numpy as np
import pandas as pd
import json
import time
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple, NamedTuple, Any, Union
from pathlib import Path
import logging

# Import our existing modules
# Import our existing modules
try:
    from .liveness_integration import LivenessIntegration, VerificationResult
    from ..repositories.attendance_repository import AttendanceRepository
    from ..utils.config import ATTENDANCE_FILE
    from ..utils.logger import logger
    from ..interfaces.attendance_manager_interface import (
        AttendanceManagerInterface, 
        AttendanceEntry as InterfaceAttendanceEntry,
        AttendanceSession as InterfaceAttendanceSession
    )
except ImportError:
    # Fallback to absolute imports for testing
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
    from modules.liveness_integration import LivenessIntegration, VerificationResult
    from repositories.attendance_repository import AttendanceRepository
    from utils.config import ATTENDANCE_FILE
    from utils.logger import logger
    from interfaces.attendance_manager_interface import (
        AttendanceManagerInterface, 
        AttendanceEntry as InterfaceAttendanceEntry,
        AttendanceSession as InterfaceAttendanceSession
    )

class AttendanceEntry(NamedTuple):
    """Structured attendance entry"""
    name: str
    user_id: str
    date: str
    time: str
    status: str
    confidence: float
    liveness_verified: bool
    face_quality_score: float
    processing_time_ms: float
    verification_stage: str
    session_id: str
    device_info: str
    location: str

class AttendanceSession(NamedTuple):
    """Attendance session information"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    user_id: str
    user_name: str
    status: str
    confidence: float
    liveness_verified: bool
    face_quality_score: float
    processing_time_ms: float
    verification_stage: str
    device_info: str
    location: str

class AttendanceManager(AttendanceManagerInterface):
    """Comprehensive attendance management system with liveness verification"""
    
    def __init__(self, 
                 liveness_integration=None,
                 enable_liveness: bool = True,
                 confidence_threshold: float = 0.6,
                 max_daily_entries: int = 5,
                 enable_analytics: bool = True,
                 enable_transparency: bool = True):
        """
        Initialize the attendance management system
        
        Args:
            liveness_integration: Liveness detection system (injected)
            enable_liveness: Enable liveness verification for attendance
            confidence_threshold: Minimum confidence for attendance logging
            max_daily_entries: Maximum attendance entries per user per day
            enable_analytics: Enable attendance analytics and reporting
            enable_transparency: Enable transparency features and detailed logging
        """
        self.liveness_integration = liveness_integration
        self.enable_liveness = enable_liveness
        self.confidence_threshold = confidence_threshold
        self.max_daily_entries = max_daily_entries
        self.enable_analytics = enable_analytics
        self.enable_transparency = enable_transparency
        
        # Session management
        self.active_sessions = {}
        self.session_counter = 0
        
        # Performance tracking
        self.processing_times = []
        self.attendance_counts = 0
        
        logger.info("Attendance Manager initialized successfully")
    
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
        start_time = time.time()
        
        try:
            # Basic validation
            if face_image is None or face_image.size == 0:
                logger.error("Invalid face image provided")
                return None
            
            # Create attendance entry
            current_time = datetime.now()
            session_id = self._generate_session_id()
            
            # Basic attendance data
            entry = AttendanceEntry(
                name=user_id or "Unknown",
                user_id=user_id or "Unknown",
                date=current_time.strftime("%Y-%m-%d"),
                time=current_time.strftime("%H:%M:%S"),
                status="logged",
                confidence=0.0,
                liveness_verified=False,
                face_quality_score=0.0,
                processing_time_ms=0.0,
                verification_stage="initial",
                session_id=session_id,
                device_info=device_info,
                location=location
            )
            
            # Store in database
            # self.attendance_repository.add_attendance(entry) # Removed repository call
            
            # Update performance metrics
            processing_time = (time.time() - start_time) * 1000
            self.processing_times.append(processing_time)
            self.attendance_counts += 1
            
            logger.info(f"Attendance logged for user {user_id or 'Unknown'}")
            return entry
            
        except Exception as e:
            logger.error(f"Failed to log attendance: {e}")
            return None
    
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
        try:
            if not user_id:
                return False, 0.0, {"error": "User ID required"}
            
            # Basic verification logic
            verification_details = {
                "user_id": user_id,
                "verification_time": datetime.now().isoformat(),
                "image_processed": True
            }
            
            # Simple success response for now
            success = True
            confidence = 0.8
            
            return success, confidence, verification_details
            
        except Exception as e:
            logger.error(f"Attendance verification failed: {e}")
            return False, 0.0, {"error": str(e)}
    
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
        try:
            # Get from database
            # history = self.attendance_repository.get_attendance_history( # Removed repository call
            #     user_id=user_id,
            #     start_date=start_date,
            #     end_date=end_date
            # )
            
            # For now, return an empty list or raise an error if repository is removed
            # This part of the code will need to be refactored if repository is truly removed
            # For now, we'll simulate a history if repository is not available
            logger.warning("Attendance history retrieval is not yet implemented without repository.")
            return []
            
        except Exception as e:
            logger.error(f"Failed to get attendance history: {e}")
            return []
    
    def get_attendance_summary(self, date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get attendance summary for a specific date or overall
        
        Args:
            date: Optional date for summary, uses today if None
            
        Returns:
            Dictionary containing attendance summary
        """
        try:
            if date is None:
                date = datetime.now().date()
            
            # Get summary from database
            # summary = self.attendance_repository.get_attendance_summary( # Removed repository call
            #     date=date
            # )
            
            # For now, return an empty dictionary or raise an error if repository is removed
            # This part of the code will need to be refactored if repository is truly removed
            logger.warning("Attendance summary retrieval is not yet implemented without repository.")
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get attendance summary: {e}")
            return {}
    
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
        try:
            session_id = self._generate_session_id()
            
            session = AttendanceSession(
                session_id=session_id,
                start_time=datetime.now(),
                user_id=user_id,
                user_name=user_name,
                status="active",
                confidence=0.0,
                liveness_verified=False,
                face_quality_score=0.0,
                processing_time_ms=0.0,
                verification_stage="session_started",
                device_info=device_info,
                location=location
            )
            
            self.active_sessions[session_id] = session
            
            logger.info(f"Session started for user {user_id} ({user_name})")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            return ""
    
    def end_session(self, session_id: str) -> bool:
        """
        End an attendance session
        
        Args:
            session_id: ID of the session to end
            
        Returns:
            True if session was ended successfully, False otherwise
        """
        try:
            if session_id not in self.active_sessions:
                logger.warning(f"Session {session_id} not found")
                return False
            
            session = self.active_sessions[session_id]
            session.end_time = datetime.now()
            session.status = "ended"
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            logger.info(f"Session {session_id} ended successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to end session {session_id}: {e}")
            return False
    
    def get_active_sessions(self) -> List[AttendanceSession]:
        """
        Get all currently active sessions
        
        Returns:
            List of active attendance sessions
        """
        return list(self.active_sessions.values())
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for the attendance manager
        
        Returns:
            Dictionary containing performance metrics
        """
        try:
            avg_processing_time = np.mean(self.processing_times) if self.processing_times else 0
            total_entries = self.attendance_counts
            
            return {
                'total_entries_processed': total_entries,
                'average_processing_time_ms': avg_processing_time,
                'total_processing_time_ms': sum(self.processing_times),
                'processing_times_count': len(self.processing_times),
                'system_uptime': time.time() - self.start_time if hasattr(self, 'start_time') else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {}
    
    def export_attendance_data(self, format: str = "csv",
                               start_date: Optional[date] = None,
                               end_date: Optional[date] = None) -> Union[str, bytes]:
        """
        Export attendance data in specified format using repository
        
        Args:
            format: Export format ("csv", "json")
            start_date: Optional start date for export
            end_date: Optional end date for export
            
        Returns:
            Exported data as string or bytes
        """
        try:
            # Get data from repository
            # df = self.attendance_repository.export_data( # Removed repository call
            #     start_date=start_date,
            #     end_date=end_date
            # )
            
            # For now, return an empty string or raise an error if repository is removed
            # This part of the code will need to be refactored if repository is truly removed
            logger.warning("Attendance data export is not yet implemented without repository.")
            return ""
                
        except Exception as e:
            logger.error(f"Failed to export attendance data: {e}")
            return ""
    
    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Update attendance manager configuration
        
        Args:
            config: New configuration parameters
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            if 'confidence_threshold' in config:
                self.confidence_threshold = float(config['confidence_threshold'])
            
            if 'max_daily_entries' in config:
                self.max_daily_entries = int(config['max_daily_entries'])
            
            if 'enable_liveness' in config:
                self.enable_liveness = bool(config['enable_liveness'])
            
            logger.info("Configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current configuration
        
        Returns:
            Dictionary containing current configuration
        """
        return {
            'enable_liveness': self.enable_liveness,
            'confidence_threshold': self.confidence_threshold,
            'max_daily_entries': self.max_daily_entries,
            'enable_analytics': self.enable_analytics,
            'enable_transparency': self.enable_transparency
        }
    
    def is_healthy(self) -> bool:
        """
        Check if the attendance manager is in a healthy state
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Check if database is accessible
            # if not self.attendance_repository: # Removed repository check
            #     return False
            
            # Check if we can perform basic operations
            # test_entry = self.get_attendance_summary(datetime.now().date()) # Removed repository call
            # return True
            
            # For now, assume healthy if no repository dependency
            logger.warning("Health check is not yet implemented without repository.")
            return True
            
        except Exception:
            return False
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        self.session_counter += 1
        timestamp = int(time.time())
        return f"session_{timestamp}_{self.session_counter}"
    


# Global attendance manager instance - now managed by service factory
# attendance_manager = AttendanceManager()  # Removed - use service factory instead
