"""
Enhanced Liveness Detection Module for EyeD AI Attendance System
Implements anti-spoofing measures through blink sequence detection and motion analysis
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, Any, List, Tuple, Optional
import time
from dataclasses import dataclass
from collections import deque
import logging

logger = logging.getLogger(__name__)

@dataclass
class LivenessResult:
    """Result of liveness detection"""
    is_live: bool
    confidence: float
    blink_count: int
    blink_duration: float
    motion_score: float
    spoofing_indicators: List[str]
    processing_time: float

class EnhancedLivenessDetection:
    """
    Enhanced liveness detection with anti-spoofing measures
    
    Features:
    - Real-time blink sequence detection
    - Motion analysis for anti-spoofing
    - Temporal consistency checks
    - Natural blink pattern validation
    """
    
    def __init__(self, 
                 min_blinks: int = 2,
                 blink_timeout: float = 10.0,
                 min_blink_duration: float = 0.1,
                 max_blink_duration: float = 0.5,
                 motion_threshold: float = 0.02):
        """
        Initialize enhanced liveness detection
        
        Args:
            min_blinks: Minimum blinks required for verification
            blink_timeout: Maximum time to wait for blinks
            min_blink_duration: Minimum blink duration (seconds)
            max_blink_duration: Maximum blink duration (seconds)
            motion_threshold: Minimum motion required to detect liveness
        """
        self.min_blinks = min_blinks
        self.blink_timeout = blink_timeout
        self.min_blink_duration = min_blink_duration
        self.max_blink_duration = max_blink_duration
        self.motion_threshold = motion_threshold
        
        # Initialize MediaPipe FaceMesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Face mesh with high accuracy
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Correct MediaPipe FaceMesh eye landmark indices for EAR calculation
        # These are the 6 key points needed for EAR calculation
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]  # 6 key points for EAR
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]  # 6 key points for EAR
        
        # Blink detection state
        self.blink_history = deque(maxlen=50)  # Store last 50 frames
        self.last_blink_time = None
        self.blink_start_time = None
        self.blink_count = 0
        self.motion_history = deque(maxlen=30)  # Store motion scores
        
        # Anti-spoofing state
        self.spoofing_indicators = []
        self.verification_start_time = None
        
        logger.info("[SUCCESS] Enhanced Liveness Detection initialized successfully")
    
    def detect_blink_sequence(self, frame: np.ndarray, timeout: float = None) -> LivenessResult:
        """
        Detect blink sequence in real-time with anti-spoofing measures
        
        Args:
            frame: Input video frame
            timeout: Maximum time to wait for verification
            
        Returns:
            LivenessResult with verification status and details
        """
        if timeout is None:
            timeout = self.blink_timeout
        
        start_time = time.time()
        self.verification_start_time = start_time
        self.reset_state()
        
        logger.info("Starting blink sequence detection...")
        
        try:
            # Process frame for blink detection
            blink_detected = self._process_frame_for_blink(frame)
            
            # Wait for minimum blinks with timeout
            while (self.blink_count < self.min_blinks and 
                   (time.time() - start_time) < timeout):
                
                # Check for spoofing indicators
                self._check_spoofing_indicators()
                
                # If spoofing detected, return immediately
                if self.spoofing_indicators:
                    return self._create_result(False, start_time)
                
                # Small delay to avoid excessive processing
                time.sleep(0.1)
            
            # Calculate final results
            return self._create_result(True, start_time)
            
        except Exception as e:
            logger.error(f"Error in blink sequence detection: {e}")
            return LivenessResult(
                is_live=False,
                confidence=0.0,
                blink_count=0,
                blink_duration=0.0,
                motion_score=0.0,
                spoofing_indicators=["Processing error"],
                processing_time=time.time() - start_time
            )
    
    def _process_frame_for_blink(self, frame: np.ndarray) -> bool:
        """Process a single frame for blink detection"""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Create a new MediaPipe instance each time (they can't be reused)
            with self.mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.3,  # Lower threshold for better detection
                min_tracking_confidence=0.3
            ) as face_mesh:
                # Process with MediaPipe
                results = face_mesh.process(rgb_frame)
                
                if not results.multi_face_landmarks:
                    return False
                
                # Get face landmarks
                face_landmarks = results.multi_face_landmarks[0]
                
                # Calculate eye aspect ratio
                left_ear = self._calculate_eye_aspect_ratio(face_landmarks, self.LEFT_EYE)
                right_ear = self._calculate_eye_aspect_ratio(face_landmarks, self.RIGHT_EYE)
                
                # Average EAR for both eyes
                ear = (left_ear + right_ear) / 2.0
                
                # Calculate motion score
                motion_score = self._calculate_motion_score(frame)
                self.motion_history.append(motion_score)
                
                # Detect blink
                blink_detected = self._detect_blink(ear)
                
                # Store in history
                self.blink_history.append({
                    'ear': ear,
                    'timestamp': time.time(),
                    'motion': motion_score,
                    'blink_detected': blink_detected
                })
                
                return blink_detected
                
        except Exception as e:
            logger.error(f"Error processing frame for blink: {e}")
            return False
    
    def _calculate_eye_aspect_ratio(self, landmarks, eye_indices: List[int]) -> float:
        """Calculate Eye Aspect Ratio (EAR) for blink detection"""
        try:
            # Get eye landmark coordinates
            eye_points = []
            for idx in eye_indices:
                landmark = landmarks.landmark[idx]
                x = landmark.x
                y = landmark.y
                eye_points.append((x, y))
            
            # Calculate vertical distances
            A = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
            B = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
            
            # Calculate horizontal distance
            C = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
            
            # Eye Aspect Ratio
            ear = (A + B) / (2.0 * C)
            
            return ear
            
        except Exception as e:
            logger.error(f"Error calculating EAR: {e}")
            return 0.0
    
    def _detect_blink(self, ear: float) -> bool:
        """Detect blink based on EAR threshold and timing"""
        try:
            current_time = time.time()
            
            # EAR threshold for blink detection (standard MediaPipe threshold)
            BLINK_THRESHOLD = 0.21  # Standard threshold for MediaPipe FaceMesh
            
            if ear < BLINK_THRESHOLD:  # Eyes are closed
                if self.blink_start_time is None:
                    # Start of blink
                    self.blink_start_time = current_time
                    logger.debug("Blink started")
                return True  # Return True when eyes are closed (blinking)
            else:  # Eyes are open
                if self.blink_start_time is not None:
                    # End of blink
                    blink_duration = current_time - self.blink_start_time
                    
                    # Validate blink duration
                    if (self.min_blink_duration <= blink_duration <= self.max_blink_duration):
                        # Valid blink detected
                        self.blink_count += 1
                        self.last_blink_time = current_time
                        logger.info(f"Blink {self.blink_count} detected (duration: {blink_duration:.3f}s, EAR: {ear:.3f})")
                    
                    # Reset blink start time
                    self.blink_start_time = None
                
                return False  # Return False when eyes are open
                
        except Exception as e:
            logger.error(f"Error in blink detection: {e}")
            return False
    
    def _calculate_motion_score(self, frame: np.ndarray) -> float:
        """Calculate motion score to detect movement"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # Calculate Laplacian variance (measure of image sharpness/motion)
            laplacian_var = cv2.Laplacian(blurred, cv2.CV_64F).var()
            
            # Normalize motion score
            motion_score = min(laplacian_var / 1000.0, 1.0)
            
            return motion_score
            
        except Exception as e:
            logger.error(f"Error calculating motion score: {e}")
            return 0.0
    
    def _check_spoofing_indicators(self):
        """Check for potential spoofing indicators"""
        try:
            # Check for insufficient motion
            if len(self.motion_history) >= 10:
                avg_motion = np.mean(list(self.motion_history))
                if avg_motion < self.motion_threshold:
                    self.spoofing_indicators.append("Insufficient motion detected")
            
            # Check for unnatural blink patterns
            if len(self.blink_history) >= 20:
                # Check if blinks are too regular (suspicious)
                blink_times = [entry['timestamp'] for entry in self.blink_history if entry['blink_detected']]
                if len(blink_times) >= 3:
                    intervals = [blink_times[i+1] - blink_times[i] for i in range(len(blink_times)-1)]
                    if len(intervals) >= 2:
                        # Check if intervals are too regular (within 0.1s)
                        if max(intervals) - min(intervals) < 0.1:
                            self.spoofing_indicators.append("Unnatural blink pattern detected")
            
            # Check for static face (no movement)
            if len(self.blink_history) >= 30:
                recent_motion = [entry['motion'] for entry in list(self.blink_history)[-30:]]
                if np.std(recent_motion) < 0.01:
                    self.spoofing_indicators.append("Static face detected (possible photo)")
            
            # Remove duplicates
            self.spoofing_indicators = list(set(self.spoofing_indicators))
            
        except Exception as e:
            logger.error(f"Error checking spoofing indicators: {e}")
    
    def _create_result(self, is_live: bool, start_time: float) -> LivenessResult:
        """Create final liveness result"""
        processing_time = time.time() - start_time
        
        # Calculate confidence based on various factors
        confidence = self._calculate_confidence()
        
        # Calculate average blink duration
        blink_duration = 0.0
        if self.blink_count > 0:
            # Estimate from blink history
            blink_duration = 0.3  # Typical blink duration
        
        # Calculate motion score
        motion_score = 0.0
        if self.motion_history:
            motion_score = np.mean(list(self.motion_history))
        
        return LivenessResult(
            is_live=is_live,
            confidence=confidence,
            blink_count=self.blink_count,
            blink_duration=blink_duration,
            motion_score=motion_score,
            spoofing_indicators=self.spoofing_indicators.copy(),
            processing_time=processing_time
        )
    
    def _calculate_confidence(self) -> float:
        """Calculate confidence score based on verification quality"""
        try:
            confidence = 0.0
            
            # Base confidence from blink count
            blink_confidence = min(self.blink_count / self.min_blinks, 1.0)
            confidence += blink_confidence * 0.6
            
            # Motion confidence
            if self.motion_history:
                motion_confidence = min(np.mean(list(self.motion_history)) / 0.1, 1.0)
                confidence += motion_confidence * 0.3
            
            # Spoofing penalty
            spoofing_penalty = len(self.spoofing_indicators) * 0.1
            confidence = max(0.0, confidence - spoofing_penalty)
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.0
    
    def reset_state(self):
        """Reset detection state for new verification"""
        self.blink_history.clear()
        self.motion_history.clear()
        self.blink_count = 0
        self.last_blink_time = None
        self.blink_start_time = None
        self.spoofing_indicators.clear()
        self.verification_start_time = None
    
    def get_verification_status(self) -> Dict[str, Any]:
        """Get current verification status"""
        return {
            'blink_count': self.blink_count,
            'min_blinks_required': self.min_blinks,
            'spoofing_indicators': self.spoofing_indicators.copy(),
            'motion_score': np.mean(list(self.motion_history)) if self.motion_history else 0.0,
            'verification_active': self.verification_start_time is not None
        }

# Backward compatibility
class LivenessDetection(EnhancedLivenessDetection):
    """Backward compatibility wrapper"""
    
    def detect_blink(self, frame: np.ndarray) -> LivenessResult:
        """Fast, real-time blink detection for continuous video processing"""
        start_time = time.time()
        
        try:
            # Process frame for blink detection (fast version)
            blink_detected = self._process_frame_for_blink_fast(frame)
            
            # Create result with current state
            processing_time = time.time() - start_time
            
            # Get current EAR value for debugging
            current_ear = 0.0
            if self.blink_history:
                current_ear = self.blink_history[-1]['ear']
            
            # Create a result object with details
            result = LivenessResult(
                is_live=blink_detected,
                confidence=self._calculate_confidence(),
                blink_count=self.blink_count,
                blink_duration=0.3,  # Typical blink duration
                motion_score=np.mean(list(self.motion_history)) if self.motion_history else 0.0,
                spoofing_indicators=self.spoofing_indicators.copy(),
                processing_time=processing_time
            )
            
            # Add details for debugging
            result.details = {
                'ear_value': current_ear,
                'threshold': 0.21,
                'blink_detected': blink_detected,
                'motion_score': np.mean(list(self.motion_history)) if self.motion_history else 0.0
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in fast blink detection: {e}")
            result = LivenessResult(
                is_live=False,
                confidence=0.0,
                blink_count=self.blink_count,
                blink_duration=0.0,
                motion_score=0.0,
                spoofing_indicators=["Processing error"],
                processing_time=time.time() - start_time
            )
            result.details = {
                'ear_value': 0.0,
                'threshold': 0.21,
                'blink_detected': False,
                'motion_score': 0.0,
                'error': str(e)
            }
            return result
    
    def _process_frame_for_blink_fast(self, frame: np.ndarray) -> bool:
        """Fast frame processing for real-time blink detection"""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Use existing face_mesh instance (more efficient)
            results = self.face_mesh.process(rgb_frame)
            
            if not results.multi_face_landmarks:
                return False
            
            # Get face landmarks
            face_landmarks = results.multi_face_landmarks[0]
            
            # Calculate eye aspect ratio
            left_ear = self._calculate_eye_aspect_ratio(face_landmarks, self.LEFT_EYE)
            right_ear = self._calculate_eye_aspect_ratio(face_landmarks, self.RIGHT_EYE)
            
            # Average EAR for both eyes
            ear = (left_ear + right_ear) / 2.0
            
            # Calculate motion score (simplified for speed)
            motion_score = self._calculate_motion_score_fast(frame)
            self.motion_history.append(motion_score)
            
            # Detect blink
            blink_detected = self._detect_blink(ear)
            
            # Debug: Print EAR values occasionally
            if len(self.blink_history) % 30 == 0:  # Every 30 frames
                logger.debug(f"EAR: {ear:.3f}, Blink: {blink_detected}, Count: {self.blink_count}")
            
            # Store in history (limit size for performance)
            if len(self.blink_history) >= 50:
                self.blink_history.popleft()
            
            self.blink_history.append({
                'ear': ear,
                'timestamp': time.time(),
                'motion': motion_score,
                'blink_detected': blink_detected
            })
            
            return blink_detected
            
        except Exception as e:
            logger.error(f"Error in fast frame processing: {e}")
            return False
    
    def _calculate_motion_score_fast(self, frame: np.ndarray) -> float:
        """Fast motion score calculation"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Resize for faster processing
            small_gray = cv2.resize(gray, (160, 120))
            
            # Calculate Laplacian variance (measure of image sharpness/motion)
            laplacian_var = cv2.Laplacian(small_gray, cv2.CV_64F).var()
            
            # Normalize motion score
            motion_score = min(laplacian_var / 500.0, 1.0)
            
            return motion_score
            
        except Exception as e:
            logger.error(f"Error calculating fast motion score: {e}")
            return 0.0
