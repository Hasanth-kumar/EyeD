"""
Liveness Integration Module for EyeD AI Attendance System
Day 7 Implementation: Multi-stage Verification Pipeline

This module handles:
- Integration of face recognition + liveness detection
- Multi-stage verification pipeline with retry logic
- Enhanced security features and monitoring
- Performance optimization for real-time processing
- Comprehensive logging and debugging capabilities
"""

import cv2
import numpy as np
import time
import random
from typing import Tuple, Optional, Dict, List, NamedTuple
import logging
from pathlib import Path

# Import our existing modules
from .recognition import FaceRecognition
from .liveness import LivenessDetection

# Configure logging
logger = logging.getLogger(__name__)

class VerificationResult(NamedTuple):
    """Result of the verification process"""
    success: bool
    user_name: Optional[str]
    confidence: float
    liveness_verified: bool
    blink_detected: bool
    face_quality_score: float
    processing_time_ms: float
    verification_stage: str
    error_message: Optional[str]

class LivenessIntegration:
    """Integrated liveness detection and face recognition system"""
    
    def __init__(self, 
                 confidence_threshold: float = 0.6,
                 liveness_timeout: float = 30.0,  # Increased timeout for real-time use
                 max_retry_attempts: int = 3,
                 enable_debug: bool = False):
        """
        Initialize the integrated liveness verification system
        
        Args:
            confidence_threshold: Minimum confidence for face recognition
            liveness_timeout: Maximum time to wait for liveness verification
            max_retry_attempts: Maximum number of retry attempts with different parameters
            enable_debug: Enable debug mode with detailed logging
        """
        self.confidence_threshold = confidence_threshold
        self.liveness_timeout = liveness_timeout
        self.max_retry_attempts = max_retry_attempts
        self.enable_debug = enable_debug
        
        # Initialize subsystems
        self.face_recognition = FaceRecognition(
            confidence_threshold=confidence_threshold,
            use_mediapipe=True
        )
        self.liveness_detection = LivenessDetection()
        
        # Verification state
        self.verification_session = None
        self.verification_history = []
        
        # Performance metrics
        self.total_verifications = 0
        self.successful_verifications = 0
        self.avg_processing_time = 0.0
        
        # Load known faces
        self._load_known_faces()
        
        logger.info("[SUCCESS] Liveness Integration System initialized successfully")
        logger.info(f"   Confidence threshold: {confidence_threshold}")
        logger.info(f"   Liveness timeout: {liveness_timeout}s")
        logger.info(f"   Max retry attempts: {max_retry_attempts}")
    
    def _load_known_faces(self) -> bool:
        """Load known faces from database"""
        try:
            # Use pathlib for cross-platform compatibility
            from pathlib import Path
            faces_path = Path("data") / "faces"
            success = self.face_recognition.load_known_faces(str(faces_path))
            if success:
                logger.info(f"[SUCCESS] Loaded {len(self.face_recognition.known_faces)} known faces")
            else:
                logger.warning("[WARNING] No known faces loaded")
            return success
        except Exception as e:
            logger.error(f"[ERROR] Failed to load known faces: {e}")
            return False
    
    def start_verification_session(self) -> str:
        """
        Start a new verification session
        
        Returns:
            Session ID for tracking
        """
        # Use microsecond precision + random component to ensure unique session IDs
        session_id = f"session_{int(time.time() * 1000000)}_{random.randint(1000, 9999)}"
        self.verification_session = {
            'id': session_id,
            'start_time': time.time(),
            'attempts': 0,
            'face_recognized': False,
            'liveness_verified': False,
            'blink_detected': False,
            'best_confidence': 0.0,
            'face_quality_scores': [],
            'processing_times': []
        }
        
        logger.info(f"[SESSION] Started verification session: {session_id}")
        return session_id
    
    def verify_user_live(self, frame: np.ndarray, 
                         session_id: Optional[str] = None) -> VerificationResult:
        """
        Perform complete user verification with liveness detection
        
        Args:
            frame: Input video frame
            session_id: Optional session ID for tracking
            
        Returns:
            VerificationResult with complete verification status
        """
        start_time = time.time()
        
        # Validate input frame
        if frame is None:
            raise ValueError("Frame cannot be None")
        if frame.size == 0:
            raise ValueError("Frame cannot be empty")
        
        # Start new session if none provided
        if session_id is None:
            session_id = self.start_verification_session()
        
        # Validate session
        if not self._validate_session(session_id):
            return VerificationResult(
                success=False,
                user_name=None,
                confidence=0.0,
                liveness_verified=False,
                blink_detected=False,
                face_quality_score=0.0,
                processing_time_ms=0.0,
                verification_stage="session_error",
                error_message="Invalid or expired session"
            )
        
        try:
            # Stage 1: Face Recognition
            recognition_result = self._perform_face_recognition(frame)
            if not recognition_result['success']:
                failure_result = self._create_failure_result(
                    "face_recognition_failed",
                    recognition_result.get('error', 'Unknown face recognition error'),
                    start_time
                )
                # Update session state and log even for failures
                self._update_session_state(session_id, failure_result)
                self._log_verification_success(failure_result)
                return failure_result
            
            # Stage 2: Liveness Detection
            liveness_result = self._perform_liveness_detection(frame)
            if not liveness_result['success']:
                failure_result = self._create_failure_result(
                    "liveness_failed",
                    f"Liveness verification failed: {liveness_result.get('error', 'Unknown error')}",
                    start_time
                )
                # Update session state and log even for failures
                self._update_session_state(session_id, failure_result)
                self._log_verification_success(failure_result)
                return failure_result
            
            # Stage 3: Final Verification
            final_result = self._finalize_verification(
                recognition_result, liveness_result, start_time
            )
            
            # Update session state
            self._update_session_state(session_id, final_result)
            
            # Log successful verification
            self._log_verification_success(final_result)
            
            return final_result
            
        except Exception as e:
            error_msg = f"Verification error: {str(e)}"
            logger.error(f"[ERROR] {error_msg}")
            return self._create_failure_result("verification_error", error_msg, start_time)
    
    def _perform_face_recognition(self, frame: np.ndarray) -> Dict:
        """Perform face recognition on the frame"""
        try:
            # Try with current confidence threshold
            result = self.face_recognition.recognize_user(frame)
            
            if result and len(result) > 0:
                best_match = max(result, key=lambda x: x.get('confidence', 0.0))
                return {
                    'success': True,
                    'user_name': best_match.get('name'),
                    'confidence': best_match.get('confidence', 0.0),
                    'face_location': best_match.get('face_location')
                }
            else:
                # Check if faces were detected but not recognized
                face_boxes = self.face_recognition.detect_faces(frame)
                if face_boxes:
                    return {
                        'success': False, 
                        'error': f'Faces detected but not recognized (detected: {len(face_boxes)})'
                    }
                else:
                    return {'success': False, 'error': 'No faces detected in frame'}
                
        except Exception as e:
            logger.error(f"[ERROR] Face recognition error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _perform_liveness_detection(self, frame: np.ndarray) -> Dict:
        """Perform liveness detection on the frame"""
        try:
            # Check face quality first
            quality_result = self.liveness_detection.assess_face_quality(frame)
            if not quality_result['passed']:
                return {
                    'success': False,
                    'error': f"Face quality check failed: {quality_result.get('issues', [])}"
                }
            
            # Perform blink detection
            blink_result = self.liveness_detection.detect_blink_from_frame(frame)
            
            return {
                'success': True,
                'blink_detected': blink_result['blink_detected'],
                'face_quality_score': quality_result.get('overall_score', 0.0),
                'quality_details': quality_result
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Liveness detection error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _finalize_verification(self, recognition_result: Dict, 
                              liveness_result: Dict, start_time: float) -> VerificationResult:
        """Finalize the verification process"""
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Check if user meets confidence threshold
        if recognition_result['confidence'] < self.confidence_threshold:
            return VerificationResult(
                success=False,
                user_name=recognition_result['user_name'],
                confidence=recognition_result['confidence'],
                liveness_verified=False,
                blink_detected=liveness_result.get('blink_detected', False),
                face_quality_score=liveness_result.get('face_quality_score', 0.0),
                processing_time_ms=processing_time,
                verification_stage="confidence_threshold_failed",
                error_message=f"Confidence {recognition_result['confidence']:.3f} below threshold {self.confidence_threshold}"
            )
        
        # Check if liveness is verified (blink detected)
        if not liveness_result.get('blink_detected', False):
            return VerificationResult(
                success=False,
                user_name=recognition_result['user_name'],
                confidence=recognition_result['confidence'],
                liveness_verified=False,
                blink_detected=False,
                face_quality_score=liveness_result.get('face_quality_score', 0.0),
                processing_time_ms=processing_time,
                verification_stage="liveness_not_verified",
                error_message="No blink detected - liveness verification failed"
            )
        
        # All checks passed - verification successful
        return VerificationResult(
            success=True,
            user_name=recognition_result['user_name'],
            confidence=recognition_result['confidence'],
            liveness_verified=True,
            blink_detected=True,
            face_quality_score=liveness_result.get('face_quality_score', 0.0),
            processing_time_ms=processing_time,
            verification_stage="verification_complete",
            error_message=None
        )
    
    def _create_failure_result(self, stage: str, error_msg: str, start_time: float) -> VerificationResult:
        """Create a failure result"""
        processing_time = (time.time() - start_time) * 1000
        return VerificationResult(
            success=False,
            user_name=None,
            confidence=0.0,
            liveness_verified=False,
            blink_detected=False,
            face_quality_score=0.0,
            processing_time_ms=processing_time,
            verification_stage=stage,
            error_message=error_msg
        )
    
    def _validate_session(self, session_id: str) -> bool:
        """Validate verification session"""
        if not self.verification_session or self.verification_session['id'] != session_id:
            return False
        
        # Check if session has expired
        if time.time() - self.verification_session['start_time'] > self.liveness_timeout:
            logger.warning(f"[WARNING] Session {session_id} expired")
            return False
        
        # Check if max attempts exceeded
        if self.verification_session['attempts'] >= self.max_retry_attempts:
            logger.warning(f"[WARNING] Session {session_id} exceeded max attempts")
            return False
        
        return True
    
    def _update_session_state(self, session_id: str, result: VerificationResult):
        """Update session state with verification result"""
        if self.verification_session and self.verification_session['id'] == session_id:
            self.verification_session['attempts'] += 1
            self.verification_session['face_recognized'] = result.success and result.user_name is not None
            self.verification_session['liveness_verified'] = result.liveness_verified
            self.verification_session['blink_detected'] = result.blink_detected
            self.verification_session['best_confidence'] = max(
                self.verification_session['best_confidence'], 
                result.confidence
            )
            self.verification_session['face_quality_scores'].append(result.face_quality_score)
            self.verification_session['processing_times'].append(result.processing_time_ms)
    
    def _log_verification_success(self, result: VerificationResult):
        """Log successful verification"""
        self.total_verifications += 1
        if result.success:
            self.successful_verifications += 1
        
        # Update average processing time
        if self.total_verifications > 0:
            self.avg_processing_time = (
                (self.avg_processing_time * (self.total_verifications - 1) + result.processing_time_ms) 
                / self.total_verifications
            )
        
        # Log the result
        if result.success:
            logger.info(f"[SUCCESS] User '{result.user_name}' verified successfully in {result.processing_time_ms:.1f}ms")
            logger.info(f"   Confidence: {result.confidence:.3f}, Quality: {result.face_quality_score:.3f}")
        else:
            logger.warning(f"[ERROR] Verification failed at stage: {result.verification_stage}")
            if result.error_message:
                logger.warning(f"   Error: {result.error_message}")
        
        # Always log statistics update
        logger.debug(f"[STATS] Statistics updated - Total: {self.total_verifications}, Success: {self.successful_verifications}")
    
    def get_verification_stats(self) -> Dict:
        """Get verification statistics"""
        return {
            'total_verifications': self.total_verifications,
            'successful_verifications': self.successful_verifications,
            'success_rate': (self.successful_verifications / self.total_verifications * 100) if self.total_verifications > 0 else 0,
            'avg_processing_time_ms': self.avg_processing_time,
            'current_session': self.verification_session
        }
    
    def reset_verification_stats(self):
        """Reset verification statistics"""
        self.total_verifications = 0
        self.successful_verifications = 0
        self.avg_processing_time = 0.0
        self.verification_session = None
        self.verification_history = []
        logger.info("[RESET] Verification statistics reset")
    
    def update_config(self, config: Dict) -> bool:
        """Update configuration parameters"""
        try:
            if 'confidence_threshold' in config:
                self.confidence_threshold = config['confidence_threshold']
                self.face_recognition.confidence_threshold = config['confidence_threshold']
                logger.info(f"[SUCCESS] Confidence threshold updated to: {self.confidence_threshold}")
            
            if 'liveness_timeout' in config:
                self.liveness_timeout = config['liveness_timeout']
                logger.info(f"[SUCCESS] Liveness timeout updated to: {self.liveness_timeout}")
            
            if 'max_retry_attempts' in config:
                self.max_retry_attempts = config['max_retry_attempts']
                logger.info(f"[SUCCESS] Max retry attempts updated to: {self.max_retry_attempts}")
            
            if 'enable_debug' in config:
                self.enable_debug = config['enable_debug']
                logger.info(f"[SUCCESS] Debug mode {'enabled' if self.enable_debug else 'disabled'}")
            
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to update configuration: {e}")
            return False
