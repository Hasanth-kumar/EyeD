"""
Live Blink Service for EyeD AI Attendance System

This service handles the business logic for live blink counting sessions,
following the Single Responsibility Principle by focusing on blink counting operations.

Features:
- Session management
- Blink counting logic
- Integration with liveness detection
- Result processing and validation
"""

import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from ..dashboard.components.live_blink_counter import LiveBlinkCounter, BlinkCounterResult
from ..interfaces.liveness_interface import LivenessInterface

logger = logging.getLogger(__name__)

class LiveBlinkService:
    """
    Service for managing live blink counting sessions
    
    This service handles:
    - Session creation and management
    - Blink counting business logic
    - Integration with liveness detection systems
    - Result validation and processing
    """
    
    def __init__(self, 
                 default_session_duration: float = 10.0,
                 default_min_blinks: int = 1):
        """
        Initialize the live blink service
        
        Args:
            default_session_duration: Default duration for blink counting sessions
            default_min_blinks: Default minimum blinks required for success
        """
        self.default_session_duration = default_session_duration
        self.default_min_blinks = default_min_blinks
        
        # Active sessions tracking
        self.active_sessions: Dict[str, LiveBlinkCounter] = {}
        self.session_history: List[BlinkCounterResult] = []
        
        logger.info(f"Live Blink Service initialized - Default duration: {default_session_duration}s")
    
    def create_blink_counting_session(self, 
                                    session_id: str,
                                    liveness_detector: LivenessInterface,
                                    session_duration: Optional[float] = None,
                                    min_blinks_required: Optional[int] = None) -> LiveBlinkCounter:
        """
        Create a new blink counting session
        
        Args:
            session_id: Unique identifier for the session
            liveness_detector: The liveness detection system to use
            session_duration: Duration of the session (uses default if None)
            min_blinks_required: Minimum blinks required (uses default if None)
            
        Returns:
            LiveBlinkCounter instance for the session
        """
        try:
            # Use defaults if not provided
            duration = session_duration or self.default_session_duration
            min_blinks = min_blinks_required or self.default_min_blinks
            
            # Create new blink counter
            blink_counter = LiveBlinkCounter(
                session_duration=duration,
                min_blinks_required=min_blinks
            )
            
            # Store in active sessions
            self.active_sessions[session_id] = blink_counter
            
            logger.info(f"Created blink counting session: {session_id} (Duration: {duration}s, Min blinks: {min_blinks})")
            return blink_counter
            
        except Exception as e:
            logger.error(f"Error creating blink counting session {session_id}: {e}")
            raise
    
    def start_session(self, session_id: str, liveness_detector: LivenessInterface) -> BlinkCounterResult:
        """
        Start a blink counting session
        
        Args:
            session_id: Session identifier
            liveness_detector: Liveness detection system
            
        Returns:
            BlinkCounterResult with session results
        """
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            blink_counter = self.active_sessions[session_id]
            result = blink_counter.start_blink_counting_session(liveness_detector)
            
            # Store result in history
            self.session_history.append(result)
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            logger.info(f"Session {session_id} completed - Blinks: {result.total_blinks}, Success: {result.success}")
            return result
            
        except Exception as e:
            logger.error(f"Error starting session {session_id}: {e}")
            # Clean up session on error
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            raise
    
    def stop_session(self, session_id: str) -> bool:
        """
        Stop an active session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was stopped, False if not found
        """
        try:
            if session_id in self.active_sessions:
                self.active_sessions[session_id].stop_session()
                del self.active_sessions[session_id]
                logger.info(f"Session {session_id} stopped")
                return True
            else:
                logger.warning(f"Session {session_id} not found for stopping")
                return False
                
        except Exception as e:
            logger.error(f"Error stopping session {session_id}: {e}")
            return False
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of an active session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session status dictionary or None if not found
        """
        try:
            if session_id in self.active_sessions:
                return self.active_sessions[session_id].get_session_stats()
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting session status {session_id}: {e}")
            return None
    
    def get_session_history(self, limit: Optional[int] = None) -> List[BlinkCounterResult]:
        """
        Get session history
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of session results
        """
        try:
            if limit:
                return self.session_history[-limit:]
            else:
                return self.session_history.copy()
                
        except Exception as e:
            logger.error(f"Error getting session history: {e}")
            return []
    
    def get_active_sessions(self) -> List[str]:
        """
        Get list of active session IDs
        
        Returns:
            List of active session identifiers
        """
        return list(self.active_sessions.keys())
    
    def clear_session_history(self):
        """Clear all session history"""
        self.session_history.clear()
        logger.info("Session history cleared")
    
    def get_service_stats(self) -> Dict[str, Any]:
        """
        Get service statistics
        
        Returns:
            Dictionary with service statistics
        """
        try:
            total_sessions = len(self.session_history)
            successful_sessions = sum(1 for result in self.session_history if result.success)
            success_rate = (successful_sessions / total_sessions * 100) if total_sessions > 0 else 0
            
            total_blinks = sum(result.total_blinks for result in self.session_history)
            avg_blinks = (total_blinks / total_sessions) if total_sessions > 0 else 0
            
            return {
                'total_sessions': total_sessions,
                'successful_sessions': successful_sessions,
                'success_rate': success_rate,
                'total_blinks_counted': total_blinks,
                'average_blinks_per_session': avg_blinks,
                'active_sessions': len(self.active_sessions),
                'service_uptime': time.time()  # Could be improved with actual start time
            }
            
        except Exception as e:
            logger.error(f"Error getting service stats: {e}")
            return {}
    
    def validate_session_result(self, result: BlinkCounterResult) -> Dict[str, Any]:
        """
        Validate a session result
        
        Args:
            result: Blink counter result to validate
            
        Returns:
            Validation results dictionary
        """
        try:
            validation = {
                'is_valid': True,
                'issues': [],
                'recommendations': []
            }
            
            # Check session duration
            if result.session_duration < 5.0:
                validation['issues'].append("Session duration too short")
                validation['recommendations'].append("Consider longer session for better accuracy")
            
            # Check blink count
            if result.total_blinks == 0:
                validation['issues'].append("No blinks detected")
                validation['recommendations'].append("Ensure good lighting and look directly at camera")
            elif result.total_blinks > 20:
                validation['issues'].append("Unusually high blink count")
                validation['recommendations'].append("Verify detection accuracy")
            
            # Check success criteria
            if not result.success and result.total_blinks > 0:
                validation['issues'].append("Session failed despite blinks detected")
                validation['recommendations'].append("Check minimum blink requirements")
            
            # Overall validation
            if validation['issues']:
                validation['is_valid'] = False
            
            return validation
            
        except Exception as e:
            logger.error(f"Error validating session result: {e}")
            return {
                'is_valid': False,
                'issues': [f"Validation error: {str(e)}"],
                'recommendations': ["Contact support if issue persists"]
            }

