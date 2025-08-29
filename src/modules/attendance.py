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
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, NamedTuple
from pathlib import Path
import logging

# Import our existing modules
# Import our existing modules
try:
    from .liveness_integration import LivenessIntegration, VerificationResult
    from ..utils.database import AttendanceDB
    from ..utils.config import ATTENDANCE_FILE
    from ..utils.logger import logger
except ImportError:
    # Fallback to absolute imports for testing
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
    from modules.liveness_integration import LivenessIntegration, VerificationResult
    from utils.database import AttendanceDB
    from utils.config import ATTENDANCE_FILE
    from utils.logger import logger

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

class AttendanceManager:
    """Comprehensive attendance management system with liveness verification"""
    
    def __init__(self, 
                 enable_liveness: bool = True,
                 confidence_threshold: float = 0.6,
                 max_daily_entries: int = 5,
                 enable_analytics: bool = True,
                 enable_transparency: bool = True):
        """
        Initialize the attendance management system
        
        Args:
            enable_liveness: Enable liveness verification for attendance
            confidence_threshold: Minimum confidence for attendance logging
            max_daily_entries: Maximum attendance entries per user per day
            enable_analytics: Enable attendance analytics and reporting
            enable_transparency: Enable transparency features and detailed logging
        """
        self.enable_liveness = enable_liveness
        self.confidence_threshold = confidence_threshold
        self.max_daily_entries = max_daily_entries
        self.enable_analytics = enable_analytics
        self.enable_transparency = enable_transparency
        
        # Initialize subsystems
        self.attendance_db = AttendanceDB()
        self.liveness_integration = LivenessIntegration(
            confidence_threshold=confidence_threshold,
            enable_debug=enable_transparency
        ) if enable_liveness else None
        
        # Session management
        self.active_sessions: Dict[str, AttendanceSession] = {}
        self.session_counter = 0
        
        # Performance metrics
        self.total_attendance_logs = 0
        self.successful_logs = 0
        self.liveness_verifications = 0
        self.avg_processing_time = 0.0
        
        # Quality metrics
        self.quality_thresholds = {
            'min_confidence': 0.6,
            'min_face_quality': 70.0,
            'max_processing_time': 5000.0  # 5 seconds
        }
        
        logger.info("[SUCCESS] Attendance Manager initialized successfully")
        logger.info(f"   Liveness verification: {'enabled' if enable_liveness else 'disabled'}")
        logger.info(f"   Confidence threshold: {confidence_threshold}")
        logger.info(f"   Max daily entries: {max_daily_entries}")
        logger.info(f"   Analytics: {'enabled' if enable_analytics else 'disabled'}")
        logger.info(f"   Transparency: {'enabled' if enable_transparency else 'disabled'}")
    
    def start_attendance_session(self, user_id: str, user_name: str, 
                                device_info: str = "Unknown", location: str = "Unknown") -> str:
        """
        Start a new attendance session for a user
        
        Args:
            user_id: Unique user identifier
            user_name: User's display name
            device_info: Device information (e.g., "Webcam", "Mobile")
            location: Location information (e.g., "Office", "Home")
            
        Returns:
            Session ID for tracking
        """
        session_id = f"attendance_{int(time.time())}_{self.session_counter}"
        self.session_counter += 1
        
        session = AttendanceSession(
            session_id=session_id,
            start_time=datetime.now(),
            end_time=None,
            user_id=user_id,
            user_name=user_name,
            status="In Progress",
            confidence=0.0,
            liveness_verified=False,
            face_quality_score=0.0,
            processing_time_ms=0.0,
            verification_stage="Session Started",
            device_info=device_info,
            location=location
        )
        
        self.active_sessions[session_id] = session
        
        if self.enable_transparency:
            logger.info(f"[SESSION] Started attendance session {session_id} for {user_name} ({user_id})")
            logger.info(f"   Device: {device_info}, Location: {location}")
        
        return session_id
    
    def process_attendance_frame(self, frame: np.ndarray, session_id: str) -> Dict:
        """
        Process a frame for attendance verification
        
        Args:
            frame: Video frame to process
            session_id: Active session ID
            
        Returns:
            Processing result with verification details
        """
        if session_id not in self.active_sessions:
            return {'success': False, 'error': 'Invalid session ID'}
        
        session = self.active_sessions[session_id]
        start_time = time.time()
        
        try:
            # Perform liveness verification if enabled
            if self.enable_liveness and self.liveness_integration:
                verification_result = self.liveness_integration.verify_frame(frame, session_id)
                
                if verification_result.success:
                    # Update session with verification results
                    self._update_session_with_verification(session_id, verification_result)
                    
                    # Check if we can log attendance
                    if self._can_log_attendance(session.user_id):
                        attendance_result = self._log_attendance_from_session(session_id)
                        return {
                            'success': True,
                            'verification_success': True,
                            'attendance_logged': attendance_result['success'],
                            'session_id': session_id,
                            'user_name': session.user_name,
                            'confidence': verification_result.confidence,
                            'liveness_verified': verification_result.liveness_verified,
                            'face_quality_score': verification_result.face_quality_score,
                            'processing_time_ms': verification_result.processing_time_ms,
                            'verification_stage': verification_result.verification_stage
                        }
                    else:
                        return {
                            'success': True,
                            'verification_success': True,
                            'attendance_logged': False,
                            'session_id': session_id,
                            'user_name': session.user_name,
                            'confidence': verification_result.confidence,
                            'liveness_verified': verification_result.liveness_verified,
                            'face_quality_score': verification_result.face_quality_score,
                            'processing_time_ms': verification_result.processing_time_ms,
                            'verification_stage': verification_result.verification_stage,
                            'message': 'Daily attendance limit reached'
                        }
                else:
                    # Verification failed
                    self._update_session_with_verification(session_id, verification_result)
                    return {
                        'success': False,
                        'verification_success': False,
                        'attendance_logged': False,
                        'session_id': session_id,
                        'user_name': session.user_name,
                        'error_message': verification_result.error_message,
                        'verification_stage': verification_result.verification_stage
                    }
            else:
                # Liveness verification disabled - use basic face recognition
                return self._process_basic_attendance(frame, session_id)
                
        except Exception as e:
            error_msg = f"Frame processing error: {str(e)}"
            logger.error(f"[ERROR] {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'session_id': session_id
            }
    
    def _process_basic_attendance(self, frame: np.ndarray, session_id: str) -> Dict:
        """Process attendance without liveness verification"""
        session = self.active_sessions[session_id]
        
        # Use basic face recognition
        recognition_result = self.liveness_integration.face_recognition.recognize_user(frame)
        
        if recognition_result and len(recognition_result) > 0:
            best_match = max(recognition_result, key=lambda x: x.get('confidence', 0.0))
            confidence = best_match.get('confidence', 0.0)
            
            if confidence >= self.confidence_threshold:
                # Update session
                self.active_sessions[session_id] = session._replace(
                    confidence=confidence,
                    verification_stage="Basic Recognition",
                    processing_time_ms=0.0
                )
                
                # Check if we can log attendance
                if self._can_log_attendance(session.user_id):
                    attendance_result = self._log_attendance_from_session(session_id)
                    return {
                        'success': True,
                        'verification_success': True,
                        'attendance_logged': attendance_result['success'],
                        'session_id': session_id,
                        'user_name': session.user_name,
                        'confidence': confidence,
                        'liveness_verified': False,
                        'face_quality_score': 0.0,
                        'processing_time_ms': 0.0,
                        'verification_stage': "Basic Recognition"
                    }
                else:
                    return {
                        'success': True,
                        'verification_success': True,
                        'attendance_logged': False,
                        'session_id': session_id,
                        'user_name': session.user_name,
                        'confidence': confidence,
                        'liveness_verified': False,
                        'face_quality_score': 0.0,
                        'processing_time_ms': 0.0,
                        'verification_stage': "Basic Recognition",
                        'message': 'Daily attendance limit reached'
                    }
            else:
                return {
                    'success': False,
                    'verification_success': False,
                    'attendance_logged': False,
                    'session_id': session_id,
                    'user_name': session.user_name,
                    'error_message': f'Confidence {confidence:.3f} below threshold {self.confidence_threshold}',
                    'verification_stage': "Confidence Threshold Failed"
                }
        else:
            return {
                'success': False,
                'verification_success': False,
                'attendance_logged': False,
                'session_id': session_id,
                'user_name': session.user_name,
                'error_message': 'No faces detected or recognized',
                'verification_stage': "No Face Detection"
            }
    
    def _update_session_with_verification(self, session_id: str, verification_result: VerificationResult):
        """Update session with verification results"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            self.active_sessions[session_id] = session._replace(
                confidence=verification_result.confidence,
                liveness_verified=verification_result.liveness_verified,
                face_quality_score=verification_result.face_quality_score,
                processing_time_ms=verification_result.processing_time_ms,
                verification_stage=verification_result.verification_stage
            )
    
    def _can_log_attendance(self, user_id: str) -> bool:
        """Check if attendance can be logged for user today"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            today_data = self.attendance_db.get_attendance_data(date=today, user_id=user_id)
            
            # Check if user has already reached the daily limit
            if len(today_data) >= self.max_daily_entries:
                logger.info(f"User {user_id} has reached daily limit of {self.max_daily_entries} entries")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking attendance eligibility: {e}")
            return False
    
    def _log_attendance_from_session(self, session_id: str) -> Dict:
        """Log attendance from session data"""
        if session_id not in self.active_sessions:
            return {'success': False, 'error': 'Session not found'}
        
        session = self.active_sessions[session_id]
        
        try:
            # Create attendance entry
            entry = AttendanceEntry(
                name=session.user_name,
                user_id=session.user_id,
                date=session.start_time.strftime('%Y-%m-%d'),
                time=session.start_time.strftime('%H:%M:%S'),
                status="Present",
                confidence=session.confidence,
                liveness_verified=session.liveness_verified,
                face_quality_score=session.face_quality_score,
                processing_time_ms=session.processing_time_ms,
                verification_stage=session.verification_stage,
                session_id=session_id,
                device_info=session.device_info,
                location=session.location
            )
            
            # Log to database with comprehensive metadata
            success = self.attendance_db.log_attendance(
                name=entry.name,
                user_id=entry.user_id,
                status=entry.status,
                confidence=entry.confidence,
                liveness_verified=entry.liveness_verified,
                face_quality_score=entry.face_quality_score,
                processing_time_ms=entry.processing_time_ms,
                verification_stage=entry.verification_stage,
                session_id=entry.session_id,
                device_info=entry.device_info,
                location=entry.location
            )
            
            if success:
                # Update session status
                self.active_sessions[session_id] = session._replace(
                    status="Completed",
                    end_time=datetime.now()
                )
                
                # Update performance metrics
                self.total_attendance_logs += 1
                self.successful_logs += 1
                if session.liveness_verified:
                    self.liveness_verifications += 1
                
                # Update average processing time
                if self.total_attendance_logs > 0:
                    self.avg_processing_time = (
                        (self.avg_processing_time * (self.total_attendance_logs - 1) + session.processing_time_ms) 
                        / self.total_attendance_logs
                    )
                
                if self.enable_transparency:
                    logger.info(f"[SUCCESS] Attendance logged successfully for {session.user_name}")
                    logger.info(f"   Session: {session_id}, Confidence: {session.confidence:.3f}")
                    logger.info(f"   Liveness: {'verified' if session.liveness_verified else 'not verified'}")
                    logger.info(f"   Quality: {session.face_quality_score:.1f}, Time: {session.processing_time_ms:.1f}ms")
                
                return {'success': True, 'entry': entry}
            else:
                return {'success': False, 'error': 'Failed to log to database'}
                
        except Exception as e:
            error_msg = f"Error logging attendance: {str(e)}"
            logger.error(f"[ERROR] {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def end_attendance_session(self, session_id: str) -> bool:
        """End an attendance session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            if session.end_time is None:
                self.active_sessions[session_id] = session._replace(
                    status="Abandoned",
                    end_time=datetime.now()
                )
            
            if self.enable_transparency:
                logger.info(f"[SESSION] Ended attendance session {session_id} for {session.user_name}")
                logger.info(f"   Final status: {self.active_sessions[session_id].status}")
            
            # Remove from active sessions when ended
            del self.active_sessions[session_id]
            
            return True
        return False
    
    def get_attendance_analytics(self, date: Optional[str] = None, 
                                user_id: Optional[str] = None) -> Dict:
        """Get comprehensive attendance analytics"""
        if not self.enable_analytics:
            return {'error': 'Analytics disabled'}
        
        try:
            # Get attendance data
            attendance_data = self.attendance_db.get_attendance_data(date=date, user_id=user_id)
            
            if attendance_data.empty:
                return {
                    'total_entries': 0,
                    'unique_users': 0,
                    'success_rate': 0.0,
                    'avg_confidence': 0.0,
                    'liveness_verification_rate': 0.0,
                    'quality_metrics': {},
                    'performance_metrics': {}
                }
            
            # Calculate analytics
            total_entries = len(attendance_data)
            unique_users = attendance_data['ID'].nunique()
            
            # Success rate (entries with confidence above threshold)
            successful_entries = attendance_data[attendance_data['Confidence'] >= self.confidence_threshold]
            success_rate = (len(successful_entries) / total_entries * 100) if total_entries > 0 else 0
            
            # Average confidence
            avg_confidence = attendance_data['Confidence'].mean()
            
            # Liveness verification rate
            if 'Liveness_Verified' in attendance_data.columns:
                liveness_verified = attendance_data['Liveness_Verified'].sum()
                liveness_rate = (liveness_verified / total_entries * 100) if total_entries > 0 else 0
            else:
                liveness_rate = 0.0
            
            # Quality metrics
            quality_metrics = {}
            if 'Confidence' in attendance_data.columns:
                quality_metrics['confidence_distribution'] = {
                    'high': len(attendance_data[attendance_data['Confidence'] >= 0.8]),
                    'medium': len(attendance_data[(attendance_data['Confidence'] >= 0.6) & (attendance_data['Confidence'] < 0.8)]),
                    'low': len(attendance_data[attendance_data['Confidence'] < 0.6])
                }
            
            # Performance metrics
            performance_metrics = {
                'total_attendance_logs': self.total_attendance_logs,
                'successful_logs': self.successful_logs,
                'liveness_verifications': self.liveness_verifications,
                'avg_processing_time_ms': self.avg_processing_time,
                'active_sessions': len(self.active_sessions)
            }
            
            return {
                'total_entries': total_entries,
                'unique_users': unique_users,
                'success_rate': success_rate,
                'avg_confidence': avg_confidence,
                'liveness_verification_rate': liveness_rate,
                'quality_metrics': quality_metrics,
                'performance_metrics': performance_metrics,
                'date_range': {
                    'start': attendance_data['Date'].min() if 'Date' in attendance_data.columns else None,
                    'end': attendance_data['Date'].max() if 'Date' in attendance_data.columns else None
                }
            }
            
        except Exception as e:
            error_msg = f"Error generating analytics: {str(e)}"
            logger.error(f"[ERROR] {error_msg}")
            return {'error': error_msg}
    
    def get_date_range_analytics(self, start_date: str, end_date: str) -> Dict:
        """Get comprehensive analytics for a specific date range"""
        if not self.enable_analytics:
            return {'error': 'Analytics disabled'}
        
        try:
            # Get attendance data for the date range
            attendance_data = self.attendance_db.get_attendance_data()
            
            # Filter by date range
            if 'Date' in attendance_data.columns:
                attendance_data = attendance_data[
                    (attendance_data['Date'] >= start_date) & 
                    (attendance_data['Date'] <= end_date)
                ]
            
            if attendance_data.empty:
                return {
                    'date_range': {'start': start_date, 'end': end_date},
                    'total_entries': 0,
                    'unique_users': 0,
                    'daily_breakdown': {},
                    'user_breakdown': {},
                    'quality_trends': {}
                }
            
            # Calculate comprehensive analytics
            total_entries = len(attendance_data)
            unique_users = attendance_data['ID'].nunique()
            
            # Daily breakdown
            daily_breakdown = attendance_data.groupby('Date').agg({
                'ID': 'count',
                'Confidence': 'mean',
                'Liveness_Verified': 'sum'
            }).rename(columns={'ID': 'entries', 'Confidence': 'avg_confidence', 'Liveness_Verified': 'liveness_verified'})
            
            # User breakdown
            user_breakdown = attendance_data.groupby('ID').agg({
                'Name': 'first',
                'Date': 'count',
                'Confidence': 'mean',
                'Liveness_Verified': 'sum'
            }).rename(columns={'Date': 'total_entries', 'Confidence': 'avg_confidence', 'Liveness_Verified': 'liveness_verified'})
            
            # Quality trends
            quality_trends = {
                'confidence_distribution': {
                    'high': len(attendance_data[attendance_data['Confidence'] >= 0.8]),
                    'medium': len(attendance_data[(attendance_data['Confidence'] >= 0.6) & (attendance_data['Confidence'] < 0.8)]),
                    'low': len(attendance_data[attendance_data['Confidence'] < 0.6])
                },
                'liveness_verification_rate': (attendance_data['Liveness_Verified'].sum() / total_entries * 100) if total_entries > 0 else 0,
                'avg_confidence': attendance_data['Confidence'].mean()
            }
            
            return {
                'date_range': {'start': start_date, 'end': end_date},
                'total_entries': total_entries,
                'unique_users': unique_users,
                'daily_breakdown': daily_breakdown.to_dict('index'),
                'user_breakdown': user_breakdown.to_dict('index'),
                'quality_trends': quality_trends
            }
            
        except Exception as e:
            error_msg = f"Error generating date range analytics: {str(e)}"
            logger.error(f"[ERROR] {error_msg}")
            return {'error': error_msg}
    
    def get_transparency_report(self, session_id: str) -> Dict:
        """Get detailed transparency report for a session"""
        if not self.enable_transparency:
            return {'error': 'Transparency features disabled'}
        
        if session_id not in self.active_sessions:
            return {'error': 'Session not found'}
        
        session = self.active_sessions[session_id]
        
        # Get verification history if available
        verification_history = []
        if self.liveness_integration:
            verification_history = self.liveness_integration.verification_history
        
        return {
            'session_info': {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'user_name': session.user_name,
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'status': session.status,
                'device_info': session.device_info,
                'location': session.location
            },
            'verification_details': {
                'confidence': session.confidence,
                'liveness_verified': session.liveness_verified,
                'face_quality_score': session.face_quality_score,
                'processing_time_ms': session.processing_time_ms,
                'verification_stage': session.verification_stage
            },
            'quality_assessment': {
                'meets_confidence_threshold': session.confidence >= self.quality_thresholds['min_confidence'],
                'meets_quality_threshold': session.face_quality_score >= self.quality_thresholds['min_face_quality'],
                'meets_performance_threshold': session.processing_time_ms <= self.quality_thresholds['max_processing_time']
            },
            'verification_history': verification_history,
            'system_metrics': {
                'total_verifications': self.total_attendance_logs,
                'success_rate': (self.successful_logs / self.total_attendance_logs * 100) if self.total_attendance_logs > 0 else 0,
                'avg_processing_time': self.avg_processing_time
            }
        }
    
    def update_config(self, config: Dict) -> bool:
        """Update configuration parameters"""
        try:
            if 'confidence_threshold' in config:
                self.confidence_threshold = config['confidence_threshold']
                if self.liveness_integration:
                    self.liveness_integration.update_config({'confidence_threshold': config['confidence_threshold']})
                logger.info(f"[SUCCESS] Confidence threshold updated to: {self.confidence_threshold}")
            
            if 'max_daily_entries' in config:
                self.max_daily_entries = config['max_daily_entries']
                logger.info(f"[SUCCESS] Max daily entries updated to: {self.max_daily_entries}")
            
            if 'enable_liveness' in config:
                self.enable_liveness = config['enable_liveness']
                logger.info(f"[SUCCESS] Liveness verification {'enabled' if self.enable_liveness else 'disabled'}")
            
            if 'enable_analytics' in config:
                self.enable_analytics = config['enable_analytics']
                logger.info(f"[SUCCESS] Analytics {'enabled' if self.enable_analytics else 'disabled'}")
            
            if 'enable_transparency' in config:
                self.enable_transparency = config['enable_transparency']
                logger.info(f"[SUCCESS] Transparency features {'enabled' if self.enable_transparency else 'disabled'}")
            
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to update configuration: {e}")
            return False
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        return {
            'total_attendance_logs': self.total_attendance_logs,
            'successful_logs': self.successful_logs,
            'success_rate': (self.successful_logs / self.total_attendance_logs * 100) if self.total_attendance_logs > 0 else 0,
            'liveness_verifications': self.liveness_verifications,
            'liveness_rate': (self.liveness_verifications / self.total_attendance_logs * 100) if self.total_attendance_logs > 0 else 0,
            'avg_processing_time_ms': self.avg_processing_time,
            'active_sessions': len(self.active_sessions),
            'total_sessions': self.session_counter
        }
    
    def reset_performance_stats(self):
        """Reset performance statistics"""
        self.total_attendance_logs = 0
        self.successful_logs = 0
        self.liveness_verifications = 0
        self.avg_processing_time = 0.0
        self.session_counter = 0
        self.active_sessions.clear()
        logger.info("[RESET] Performance statistics reset")

# Global attendance manager instance
attendance_manager = AttendanceManager()
