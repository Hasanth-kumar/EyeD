"""
Live Blink Counter Component for EyeD AI Attendance System

This component provides a live camera feed with real-time blink counting over a 10-second period.
It follows the Single Responsibility Principle by focusing solely on live blink detection and counting.

Features:
- Live camera feed display
- Real-time blink counting
- 10-second timer with countdown
- Visual feedback for user
- Integration with existing liveness detection system
"""

import streamlit as st
import cv2
import numpy as np
import time
from typing import Dict, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class BlinkCounterResult:
    """Result of the live blink counter session"""
    total_blinks: int
    session_duration: float
    start_time: datetime
    end_time: datetime
    success: bool
    error_message: Optional[str] = None

class LiveBlinkCounter:
    """
    Live blink counter component with 10-second timer
    
    This component handles:
    - Live camera feed display
    - Real-time blink detection and counting
    - 10-second countdown timer
    - Visual feedback and progress indicators
    """
    
    def __init__(self, 
                 session_duration: float = 10.0,
                 min_blinks_required: int = 1,
                 camera_width: int = 640,
                 camera_height: int = 480):
        """
        Initialize the live blink counter
        
        Args:
            session_duration: Duration of the blink counting session in seconds
            min_blinks_required: Minimum number of blinks required for success
            camera_width: Camera frame width
            camera_height: Camera frame height
        """
        self.session_duration = session_duration
        self.min_blinks_required = min_blinks_required
        self.camera_width = camera_width
        self.camera_height = camera_height
        
        # Session state
        self.session_active = False
        self.start_time = None
        self.blink_count = 0
        self.last_blink_time = None
        self.camera_cap = None
        
        # Visual feedback
        self.progress_bar = None
        self.camera_placeholder = None
        self.status_placeholder = None
        
        logger.info(f"Live Blink Counter initialized - Duration: {session_duration}s, Min blinks: {min_blinks_required}")
    
    def start_blink_counting_session(self, liveness_detector) -> BlinkCounterResult:
        """
        Start a live blink counting session
        
        Args:
            liveness_detector: The liveness detection system to use
            
        Returns:
            BlinkCounterResult with session results
        """
        try:
            # Initialize session state
            self._initialize_session()
            
            # Create UI placeholders
            self._create_ui_placeholders()
            
            # Initialize camera
            if not self._initialize_camera():
                return BlinkCounterResult(
                    total_blinks=0,
                    session_duration=0.0,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    success=False,
                    error_message="Failed to initialize camera"
                )
            
            # Start the counting session
            return self._run_counting_session(liveness_detector)
            
        except Exception as e:
            logger.error(f"Error starting blink counting session: {e}")
            return BlinkCounterResult(
                total_blinks=0,
                session_duration=0.0,
                start_time=datetime.now(),
                end_time=datetime.now(),
                success=False,
                error_message=str(e)
            )
        finally:
            self._cleanup_session()
    
    def _initialize_session(self):
        """Initialize session state variables"""
        self.session_active = True
        self.start_time = time.time()
        self.blink_count = 0
        self.last_blink_time = None
        self.camera_cap = None
        
        logger.info("Blink counting session initialized")
    
    def _create_ui_placeholders(self):
        """Create Streamlit UI placeholders for the session"""
        # Main camera feed placeholder
        self.camera_placeholder = st.empty()
        
        # Status and progress placeholders
        col1, col2 = st.columns([2, 1])
        with col1:
            self.status_placeholder = st.empty()
        with col2:
            self.progress_bar = st.empty()
        
        # Instructions
        st.info("👁️ **Live Blink Counter** - Blink naturally while looking at the camera")
        st.warning("⏱️ **Timer**: 10 seconds - Count as many blinks as you can!")
    
    def _initialize_camera(self) -> bool:
        """Initialize the camera for live feed"""
        try:
            self.camera_cap = cv2.VideoCapture(0)
            if not self.camera_cap.isOpened():
                st.error("❌ Failed to open camera")
                return False
            
            # Set camera properties
            self.camera_cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
            self.camera_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
            self.camera_cap.set(cv2.CAP_PROP_FPS, 30)
            
            logger.info("Camera initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing camera: {e}")
            st.error(f"❌ Camera initialization error: {e}")
            return False
    
    def _run_counting_session(self, liveness_detector) -> BlinkCounterResult:
        """Run the main counting session loop"""
        session_start_time = datetime.now()
        frame_count = 0
        
        try:
            while self.session_active:
                # Check if session time has expired
                elapsed_time = time.time() - self.start_time
                if elapsed_time >= self.session_duration:
                    break
                
                # Read frame from camera
                ret, frame = self.camera_cap.read()
                if not ret:
                    st.error("❌ Failed to read from camera")
                    break
                
                frame_count += 1
                
                # Process frame for blink detection (every 3rd frame for performance)
                if frame_count % 3 == 0:
                    self._process_frame_for_blink(frame, liveness_detector)
                
                # Update UI with current frame and status
                self._update_ui(frame, elapsed_time)
                
                # Small delay to control frame rate
                time.sleep(0.033)  # ~30 FPS
            
            # Calculate final results
            session_end_time = datetime.now()
            total_duration = (session_end_time - session_start_time).total_seconds()
            
            return BlinkCounterResult(
                total_blinks=self.blink_count,
                session_duration=total_duration,
                start_time=session_start_time,
                end_time=session_end_time,
                success=self.blink_count >= self.min_blinks_required
            )
            
        except Exception as e:
            logger.error(f"Error during counting session: {e}")
            return BlinkCounterResult(
                total_blinks=self.blink_count,
                session_duration=time.time() - self.start_time,
                start_time=session_start_time,
                end_time=datetime.now(),
                success=False,
                error_message=str(e)
            )
    
    def _process_frame_for_blink(self, frame: np.ndarray, liveness_detector):
        """Process a single frame for blink detection"""
        try:
            # Use the liveness detector to check for blinks
            liveness_result = liveness_detector.detect_blink(frame)
            
            # Check if a blink was detected
            if liveness_result.is_live:
                current_time = time.time()
                
                # Avoid counting the same blink multiple times
                if (self.last_blink_time is None or 
                    current_time - self.last_blink_time > 0.5):  # 500ms cooldown
                    
                    self.blink_count += 1
                    self.last_blink_time = current_time
                    logger.info(f"Blink detected! Total count: {self.blink_count}")
            
        except Exception as e:
            logger.error(f"Error processing frame for blink: {e}")
    
    def _update_ui(self, frame: np.ndarray, elapsed_time: float):
        """Update the UI with current frame and status"""
        try:
            # Calculate remaining time
            remaining_time = max(0, self.session_duration - elapsed_time)
            progress = (elapsed_time / self.session_duration) * 100
            
            # Add visual overlays to the frame
            frame_with_overlays = self._add_visual_overlays(frame, elapsed_time, remaining_time)
            
            # Update camera feed
            self.camera_placeholder.image(frame_with_overlays, channels="BGR", use_container_width=True)
            
            # Update status
            self.status_placeholder.info(f"""
            **📊 Session Status**
            - **Blinks Counted**: {self.blink_count}
            - **Time Remaining**: {remaining_time:.1f}s
            - **Progress**: {progress:.1f}%
            """)
            
            # Update progress bar
            self.progress_bar.progress(progress / 100)
            
        except Exception as e:
            logger.error(f"Error updating UI: {e}")
    
    def _add_visual_overlays(self, frame: np.ndarray, elapsed_time: float, remaining_time: float) -> np.ndarray:
        """Add visual overlays to the camera frame"""
        try:
            # Create a copy of the frame
            frame_with_overlays = frame.copy()
            
            # Add timer overlay
            timer_text = f"Time: {remaining_time:.1f}s"
            cv2.putText(frame_with_overlays, timer_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            
            # Add blink count overlay
            blink_text = f"Blinks: {self.blink_count}"
            cv2.putText(frame_with_overlays, blink_text, (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            
            # Add progress bar overlay
            bar_width = 300
            bar_height = 20
            bar_x = 10
            bar_y = 100
            
            # Background bar
            cv2.rectangle(frame_with_overlays, (bar_x, bar_y), 
                         (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
            
            # Progress bar
            progress_width = int((elapsed_time / self.session_duration) * bar_width)
            cv2.rectangle(frame_with_overlays, (bar_x, bar_y), 
                         (bar_x + progress_width, bar_y + bar_height), (0, 255, 0), -1)
            
            # Add status indicator
            if self.blink_count >= self.min_blinks_required:
                status_text = "✅ SUCCESS"
                color = (0, 255, 0)
            else:
                status_text = "👁️ Keep Blinking!"
                color = (0, 255, 255)
            
            cv2.putText(frame_with_overlays, status_text, (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            
            return frame_with_overlays
            
        except Exception as e:
            logger.error(f"Error adding visual overlays: {e}")
            return frame
    
    def _cleanup_session(self):
        """Clean up session resources"""
        try:
            self.session_active = False
            
            if self.camera_cap and self.camera_cap.isOpened():
                self.camera_cap.release()
                self.camera_cap = None
            
            logger.info("Blink counting session cleaned up")
            
        except Exception as e:
            logger.error(f"Error during session cleanup: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        if not self.session_active:
            return {}
        
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        remaining_time = max(0, self.session_duration - elapsed_time)
        
        return {
            'session_active': self.session_active,
            'blink_count': self.blink_count,
            'elapsed_time': elapsed_time,
            'remaining_time': remaining_time,
            'progress_percentage': (elapsed_time / self.session_duration) * 100,
            'success': self.blink_count >= self.min_blinks_required
        }
    
    def stop_session(self):
        """Stop the current session"""
        self.session_active = False
        logger.info("Blink counting session stopped by user")

