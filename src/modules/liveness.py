"""
Liveness Detection Module for EyeD AI Attendance System
Day 6 Implementation: Blink Detection (MediaPipe)

This module handles:
- MediaPipe FaceMesh integration (468 landmarks)
- Eye landmark extraction and EAR calculation
- Blink detection using Eye Aspect Ratio (EAR)
- Face quality assessment (brightness, contrast, alignment)
- Minimum resolution requirements (480x480)
- Enhanced error handling and logging
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Tuple, List, Optional, Dict
import logging

# Configure logging
logger = logging.getLogger(__name__)

class LivenessDetection:
    """Liveness detection using MediaPipe FaceMesh with enhanced features"""
    
    def __init__(self):
        """Initialize liveness detection system"""
        self.mp_face_mesh = None
        self.mp_drawing = None
        self.mp_drawing_styles = None
        
        # Blink detection parameters (configurable)
        self.ear_threshold = 0.21  # Eye Aspect Ratio threshold for blink detection
        self.blink_counter = 0
        self.consecutive_frames = 0
        self.min_consecutive_frames = 2  # Minimum frames for blink confirmation
        
        # Face quality parameters (configurable)
        self.min_resolution = (480, 480)
        self.min_brightness = 30
        self.max_brightness = 250
        self.min_contrast = 20
        self.min_sharpness = 100
        
        # MediaPipe parameters (configurable)
        self.min_detection_confidence = 0.5
        self.min_tracking_confidence = 0.5
        self.max_num_faces = 1
        self.refine_landmarks = True
        
        # Performance parameters (configurable)
        self.enable_debug_mode = False
        self.enable_visualization = False
        self.frame_skip_rate = 1  # Process every Nth frame for performance
        
        # Eye landmark indices (MediaPipe FaceMesh)
        self.LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380, 381, 382, 381, 374, 386, 387, 388, 466]
        self.RIGHT_EYE_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        
        # Initialize MediaPipe
        self.initialize_mediapipe()
    
    def initialize_mediapipe(self) -> bool:
        """
        Initialize MediaPipe FaceMesh
        
        Returns:
            True if initialized successfully, False otherwise
        """
        try:
            self.mp_face_mesh = mp.solutions.face_mesh
            self.mp_drawing = mp.solutions.drawing_utils
            self.mp_drawing_styles = mp.solutions.drawing_styles
            
            logger.info("[SUCCESS] MediaPipe FaceMesh initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize MediaPipe: {str(e)}")
            return False
    
    def update_config(self, config: Dict) -> bool:
        """
        Update configuration parameters at runtime
        
        Args:
            config: Dictionary with configuration parameters
            
        Returns:
            True if configuration updated successfully
        """
        try:
            # Update blink detection parameters
            if 'ear_threshold' in config:
                self.ear_threshold = config['ear_threshold']
                logger.info(f"[SUCCESS] EAR threshold updated to: {self.ear_threshold}")
            
            if 'min_consecutive_frames' in config:
                self.min_consecutive_frames = config['min_consecutive_frames']
                logger.info(f"[SUCCESS] Min consecutive frames updated to: {self.min_consecutive_frames}")
            
            # Update face quality parameters
            if 'min_resolution' in config:
                self.min_resolution = config['min_resolution']
                logger.info(f"[SUCCESS] Min resolution updated to: {self.min_resolution}")
            
            if 'min_brightness' in config:
                self.min_brightness = config['min_brightness']
                logger.info(f"[SUCCESS] Min brightness updated to: {self.min_brightness}")
            
            if 'min_contrast' in config:
                self.min_contrast = config['min_contrast']
                logger.info(f"[SUCCESS] Min contrast updated to: {self.min_contrast}")
            
            if 'min_sharpness' in config:
                self.min_sharpness = config['min_sharpness']
                logger.info(f"[SUCCESS] Min sharpness updated to: {self.min_sharpness}")
            
            # Update MediaPipe parameters
            if 'min_detection_confidence' in config:
                self.min_detection_confidence = config['min_detection_confidence']
                logger.info(f"[SUCCESS] Min detection confidence updated to: {self.min_detection_confidence}")
            
            if 'min_tracking_confidence' in config:
                self.min_tracking_confidence = config['min_tracking_confidence']
                logger.info(f"[SUCCESS] Min tracking confidence updated to: {self.min_tracking_confidence}")
            
            # Update performance parameters
            if 'enable_debug_mode' in config:
                self.enable_debug_mode = config['enable_debug_mode']
                logger.info(f"[SUCCESS] Debug mode {'enabled' if self.enable_debug_mode else 'disabled'}")
            
            if 'enable_visualization' in config:
                self.enable_visualization = config['enable_visualization']
                logger.info(f"[SUCCESS] Visualization {'enabled' if self.enable_visualization else 'disabled'}")
            
            if 'frame_skip_rate' in config:
                self.frame_skip_rate = max(1, config['frame_skip_rate'])
                logger.info(f"[SUCCESS] Frame skip rate updated to: {self.frame_skip_rate}")
            
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Configuration update failed: {str(e)}")
            return False
    
    def get_config(self) -> Dict:
        """
        Get current configuration parameters
        
        Returns:
            Dictionary with current configuration
        """
        return {
            'ear_threshold': self.ear_threshold,
            'min_consecutive_frames': self.min_consecutive_frames,
            'min_resolution': self.min_resolution,
            'min_brightness': self.min_brightness,
            'min_contrast': self.min_contrast,
            'min_sharpness': self.min_sharpness,
            'min_detection_confidence': self.min_detection_confidence,
            'min_tracking_confidence': self.min_tracking_confidence,
            'max_num_faces': self.max_num_faces,
            'refine_landmarks': self.refine_landmarks,
            'enable_debug_mode': self.enable_debug_mode,
            'enable_visualization': self.enable_visualization,
            'frame_skip_rate': self.frame_skip_rate
        }
    
    def assess_face_quality(self, frame: np.ndarray) -> Dict[str, any]:
        """
        Assess face quality for liveness detection
        
        Args:
            frame: Input frame
            
        Returns:
            Dictionary with quality metrics and overall score
        """
        try:
            # Check if frame is None
            if frame is None:
                raise ValueError("Frame is None")
            
            # Check if frame has the expected shape
            if len(frame.shape) < 2:
                raise ValueError(f"Invalid frame shape: {frame.shape}")
            
            # Check if frame has valid dimensions
            if frame.shape[0] == 0 or frame.shape[1] == 0:
                raise ValueError(f"Invalid frame dimensions: {frame.shape}")
            
            height, width = frame.shape[:2]
            
            # Check resolution
            resolution_ok = height >= self.min_resolution[0] and width >= self.min_resolution[1]
            
            # Convert to grayscale for quality assessment
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame
            
            # Calculate brightness
            brightness = np.mean(gray)
            brightness_ok = self.min_brightness <= brightness <= self.max_brightness
            
            # Calculate contrast
            contrast = np.std(gray)
            contrast_ok = contrast >= self.min_contrast
            
            # Calculate sharpness (Laplacian variance)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = np.var(laplacian)
            sharpness_ok = sharpness > self.min_sharpness
            
            # Overall quality score (0-100)
            quality_score = 0
            if resolution_ok: quality_score += 25
            if brightness_ok: quality_score += 25
            if contrast_ok: quality_score += 25
            if sharpness_ok: quality_score += 25
            
            quality_assessment = {
                'passed': quality_score >= 50,  # Pass if at least 50% quality
                'overall_score': quality_score,
                'resolution_ok': resolution_ok,
                'brightness_ok': brightness_ok,
                'contrast_ok': contrast_ok,
                'sharpness_ok': sharpness_ok,
                'quality_score': quality_score,
                'brightness': brightness,
                'contrast': contrast,
                'sharpness': sharpness,
                'resolution': (width, height),
                'issues': []
            }
            
            # Add issues if quality checks fail
            if not resolution_ok:
                quality_assessment['issues'].append('Low resolution')
            if not brightness_ok:
                quality_assessment['issues'].append('Poor brightness')
            if not contrast_ok:
                quality_assessment['issues'].append('Low contrast')
            if not sharpness_ok:
                quality_assessment['issues'].append('Blurry image')
            
            logger.debug(f"Face quality assessment: {quality_assessment}")
            return quality_assessment
            
        except Exception as e:
            logger.error(f"[ERROR] Face quality assessment failed: {str(e)}")
            return {
                'passed': False,
                'overall_score': 0,
                'resolution_ok': False,
                'brightness_ok': False,
                'contrast_ok': False,
                'sharpness_ok': False,
                'quality_score': 0,
                'issues': [str(e)]
            }
    
    def detect_faces_mediapipe(self, frame: np.ndarray) -> List:
        """
        Detect faces using MediaPipe as fallback
        
        Args:
            frame: Input frame
            
        Returns:
            List of detected faces
        """
        try:
            if self.mp_face_mesh is None:
                logger.error("[ERROR] MediaPipe not initialized")
                return []
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame with MediaPipe
            with self.mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=self.max_num_faces,
                refine_landmarks=self.refine_landmarks,
                min_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=self.min_tracking_confidence
            ) as face_mesh:
                results = face_mesh.process(rgb_frame)
                
                if results.multi_face_landmarks:
                    logger.debug(f"[SUCCESS] MediaPipe detected {len(results.multi_face_landmarks)} face(s)")
                    return results.multi_face_landmarks
                else:
                    logger.debug("[ERROR] No faces detected by MediaPipe")
                    return []
                    
        except Exception as e:
            logger.error(f"[ERROR] MediaPipe face detection failed: {str(e)}")
            return []
    
    def extract_eye_landmarks(self, face_landmarks) -> Tuple[List, List]:
        """
        Extract eye landmarks from MediaPipe results
        
        Args:
            face_landmarks: MediaPipe face landmarks
            
        Returns:
            Tuple of (left_eye_landmarks, right_eye_landmarks)
        """
        try:
            # Extract left eye landmarks
            left_eye = []
            for idx in self.LEFT_EYE_INDICES:
                landmark = face_landmarks.landmark[idx]
                left_eye.append([landmark.x, landmark.y, landmark.z])
            
            # Extract right eye landmarks
            right_eye = []
            for idx in self.RIGHT_EYE_INDICES:
                landmark = face_landmarks.landmark[idx]
                right_eye.append([landmark.x, landmark.y, landmark.z])
            
            logger.debug(f"[SUCCESS] Extracted {len(left_eye)} left eye and {len(right_eye)} right eye landmarks")
            return left_eye, right_eye
            
        except Exception as e:
            logger.error(f"[ERROR] Eye landmark extraction failed: {str(e)}")
            return [], []
    
    def calculate_ear(self, eye_landmarks: List) -> float:
        """
        Calculate Eye Aspect Ratio (EAR)
        
        EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
        
        Args:
            eye_landmarks: List of eye landmark coordinates
            
        Returns:
            EAR value (lower = more closed)
        """
        try:
            if len(eye_landmarks) < 6:
                logger.warning(f"[ERROR] Insufficient eye landmarks: {len(eye_landmarks)}")
                return 0.0
            
            # Convert to numpy array for easier calculations
            eye_points = np.array(eye_landmarks)
            
            # Calculate distances
            # Vertical distances
            A = np.linalg.norm(eye_points[1] - eye_points[5])
            B = np.linalg.norm(eye_points[2] - eye_points[4])
            
            # Horizontal distance
            C = np.linalg.norm(eye_points[0] - eye_points[3])
            
            # Avoid division by zero
            if C == 0:
                logger.warning("[ERROR] Division by zero in EAR calculation")
                return 0.0
            
            # Calculate EAR
            ear = (A + B) / (2.0 * C)
            
            logger.debug(f"[SUCCESS] EAR calculated: {ear:.4f}")
            return ear
            
        except Exception as e:
            logger.error(f"[ERROR] EAR calculation failed: {str(e)}")
            return 0.0
    
    def detect_blink(self, left_ear: float, right_ear: float) -> bool:
        """
        Detect blink based on EAR values
        
        Args:
            left_ear: Left eye EAR value
            right_ear: Right eye EAR value
            
        Returns:
            True if blink detected, False otherwise
        """
        try:
            # Use average EAR of both eyes
            avg_ear = (left_ear + right_ear) / 2.0
            
            # Check if eyes are closed (EAR below threshold)
            if avg_ear < self.ear_threshold:
                self.consecutive_frames += 1
                logger.debug(f"[INFO] Eyes closed: EAR={avg_ear:.4f}, consecutive frames={self.consecutive_frames}")
                
                # Confirm blink after minimum consecutive frames
                if self.consecutive_frames >= self.min_consecutive_frames:
                    self.blink_counter += 1
                    logger.info(f"[SUCCESS] Blink detected! Count: {self.blink_counter}")
                    # Reset consecutive frames after blink detection to allow for next blink
                    self.consecutive_frames = 0
                    return True
            else:
                # Reset consecutive frame counter when eyes are open
                if self.consecutive_frames > 0:
                    logger.debug(f"[INFO] Eyes opened: EAR={avg_ear:.4f}")
                self.consecutive_frames = 0
            
            return False
            
        except Exception as e:
            logger.error(f"[ERROR] Blink detection failed: {str(e)}")
            return False
    
    def detect_blink_from_frame(self, frame: np.ndarray) -> Dict:
        """
        Detect blink from a frame (wrapper for liveness integration)
        
        Args:
            frame: Input frame
            
        Returns:
            Dictionary with blink detection results
        """
        try:
            # Detect faces using MediaPipe
            faces = self.detect_faces_mediapipe(frame)
            
            if not faces:
                return {
                    'blink_detected': False,
                    'error': 'No faces detected',
                    'ear_values': None
                }
            
            # Process first detected face
            face_landmarks = faces[0]
            
            # Extract eye landmarks
            left_eye, right_eye = self.extract_eye_landmarks(face_landmarks)
            
            if not left_eye or not right_eye:
                return {
                    'blink_detected': False,
                    'error': 'Failed to extract eye landmarks',
                    'ear_values': None
                }
            
            # Calculate EAR for both eyes
            left_ear = self.calculate_ear(left_eye)
            right_ear = self.calculate_ear(right_eye)
            
            # Detect blink
            blink_detected = self.detect_blink(left_ear, right_ear)
            
            return {
                'blink_detected': blink_detected,
                'error': None,
                'ear_values': (left_ear, right_ear),
                'blink_count': self.blink_counter
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Blink detection from frame failed: {str(e)}")
            return {
                'blink_detected': False,
                'error': str(e),
                'ear_values': None
            }
    
    def verify_liveness(self, frame: np.ndarray) -> Tuple[bool, float, Dict]:
        """
        Verify liveness of person in frame
        
        Args:
            frame: Input frame
            
        Returns:
            Tuple of (is_live, confidence, quality_metrics)
        """
        try:
            # Assess face quality first
            quality_metrics = self.assess_face_quality(frame)
            
            # Check if quality is sufficient
            if quality_metrics['quality_score'] < 75:
                logger.warning(f"[ERROR] Insufficient face quality: {quality_metrics['quality_score']}/100")
                return False, 0.0, quality_metrics
            
            # Detect faces using MediaPipe
            faces = self.detect_faces_mediapipe(frame)
            
            if not faces:
                logger.warning("[ERROR] No faces detected for liveness verification")
                return False, 0.0, quality_metrics
            
            # Process first detected face
            face_landmarks = faces[0]
            
            # Extract eye landmarks
            left_eye, right_eye = self.extract_eye_landmarks(face_landmarks)
            
            if not left_eye or not right_eye:
                logger.warning("[ERROR] Failed to extract eye landmarks")
                return False, 0.0, quality_metrics
            
            # Calculate EAR for both eyes
            left_ear = self.calculate_ear(left_eye)
            right_ear = self.calculate_ear(right_eye)
            
            # Detect blink
            blink_detected = self.detect_blink(left_ear, right_ear)
            
            # Calculate confidence based on quality and blink detection
            confidence = quality_metrics['quality_score'] / 100.0
            
            if blink_detected:
                confidence = min(confidence + 0.2, 1.0)  # Boost confidence for blink detection
                logger.info(f"[SUCCESS] Liveness verified with blink detection! Confidence: {confidence:.2f}")
                return True, confidence, quality_metrics
            else:
                logger.info(f"[INFO] No blink detected yet. Confidence: {confidence:.2f}")
                return False, confidence, quality_metrics
                
        except Exception as e:
            logger.error(f"[ERROR] Liveness verification failed: {str(e)}")
            return False, 0.0, {}
    
    def get_blink_count(self) -> int:
        """Get total blink count for current session"""
        return self.blink_counter
    
    def reset_blink_counter(self):
        """Reset blink counter for new session"""
        self.blink_counter = 0
        self.consecutive_frames = 0
        logger.info("[RESET] Blink counter reset")
    
    def draw_face_mesh(self, frame: np.ndarray, face_landmarks) -> np.ndarray:
        """
        Draw MediaPipe face mesh on frame for visualization
        
        Args:
            frame: Input frame
            face_landmarks: MediaPipe face landmarks
            
        Returns:
            Frame with face mesh drawn
        """
        try:
            if self.mp_drawing is None:
                return frame
            
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Draw face mesh
            annotated_frame = rgb_frame.copy()
            self.mp_drawing.draw_landmarks(
                image=annotated_frame,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style()
            )
            
            # Convert back to BGR
            annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)
            
            return annotated_frame
            
        except Exception as e:
            logger.error(f"[ERROR] Face mesh drawing failed: {str(e)}")
            return frame
    
    def assess_face_alignment(self, face_landmarks) -> Dict:
        """
        Assess face alignment and pose for better quality assessment
        
        Args:
            face_landmarks: MediaPipe face landmarks
            
        Returns:
            Dictionary with alignment metrics
        """
        try:
            # Get key facial points for alignment assessment
            nose_tip = face_landmarks.landmark[4]  # Nose tip
            left_eye_center = face_landmarks.landmark[33]  # Left eye center
            right_eye_center = face_landmarks.landmark[263]  # Right eye center
            left_ear = face_landmarks.landmark[234]  # Left ear
            right_ear = face_landmarks.landmark[454]  # Right ear
            
            # Calculate face symmetry (left-right balance)
            left_eye_to_nose = np.linalg.norm([
                left_eye_center.x - nose_tip.x,
                left_eye_center.y - nose_tip.y
            ])
            right_eye_to_nose = np.linalg.norm([
                right_eye_center.x - nose_tip.x,
                right_eye_center.y - nose_tip.y
            ])
            
            symmetry_score = min(left_eye_to_nose, right_eye_to_nose) / max(left_eye_to_nose, right_eye_to_nose)
            symmetry_ok = symmetry_score > 0.8  # 80% symmetry threshold
            
            # Calculate head pose (simple estimation)
            eye_center_x = (left_eye_center.x + right_eye_center.x) / 2
            eye_center_y = (left_eye_center.y + right_eye_center.y) / 2
            
            # Check if face is roughly centered (simple approach)
            face_centered = 0.3 < eye_center_x < 0.7 and 0.3 < eye_center_y < 0.7
            
            # Calculate face size relative to frame
            face_width = abs(left_ear.x - right_ear.x)
            face_height = abs(left_ear.y - nose_tip.y)
            face_size_ok = face_width > 0.3 and face_height > 0.3  # Face should occupy reasonable portion of frame
            
            # Overall alignment score
            alignment_score = 0
            if symmetry_ok: alignment_score += 25
            if face_centered: alignment_score += 25
            if face_size_ok: alignment_score += 25
            
            # Additional 25 points for good overall alignment
            if alignment_score >= 50: alignment_score += 25
            
            return {
                'symmetry_score': symmetry_score,
                'symmetry_ok': symmetry_ok,
                'face_centered': face_centered,
                'face_size_ok': face_size_ok,
                'alignment_score': alignment_score,
                'face_width': face_width,
                'face_height': face_height,
                'eye_center_x': eye_center_x,
                'eye_center_y': eye_center_y
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Face alignment assessment failed: {str(e)}")
            return {
                'symmetry_score': 0.0,
                'symmetry_ok': False,
                'face_centered': False,
                'face_size_ok': False,
                'alignment_score': 0,
                'error': str(e)
            }
    
    def draw_eye_landmarks(self, frame: np.ndarray, face_landmarks) -> np.ndarray:
        """
        Draw eye landmarks specifically for blink detection debugging
        
        Args:
            frame: Input frame
            face_landmarks: MediaPipe face landmarks
            
        Returns:
            Frame with eye landmarks highlighted
        """
        try:
            if self.mp_drawing is None:
                return frame
            
            annotated_frame = frame.copy()
            
            # Draw left eye landmarks
            for idx in self.LEFT_EYE_INDICES:
                landmark = face_landmarks.landmark[idx]
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                cv2.circle(annotated_frame, (x, y), 3, (0, 255, 0), -1)  # Green for left eye
            
            # Draw right eye landmarks
            for idx in self.RIGHT_EYE_INDICES:
                landmark = face_landmarks.landmark[idx]
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                cv2.circle(annotated_frame, (x, y), 3, (255, 0, 0), -1)  # Blue for right eye
            
            return annotated_frame
            
        except Exception as e:
            logger.error(f"[ERROR] Eye landmark drawing failed: {str(e)}")
            return frame
    
    def draw_debug_info(self, frame: np.ndarray, face_landmarks, ear_values: Dict = None) -> np.ndarray:
        """
        Draw comprehensive debug information on frame
        
        Args:
            frame: Input frame
            face_landmarks: MediaPipe face landmarks
            ear_values: Dictionary with EAR values for display
            
        Returns:
            Frame with debug information drawn
        """
        try:
            debug_frame = frame.copy()
            
            # Draw face mesh
            debug_frame = self.draw_face_mesh(debug_frame, face_landmarks)
            
            # Draw eye landmarks
            debug_frame = self.draw_eye_landmarks(debug_frame, face_landmarks)
            
            # Add EAR values if provided
            if ear_values:
                left_ear = ear_values.get('left_ear', 0)
                right_ear = ear_values.get('right_ear', 0)
                avg_ear = ear_values.get('average_ear', 0)
                threshold = ear_values.get('threshold', 0)
                
                # Draw EAR information
                cv2.putText(debug_frame, f"Left EAR: {left_ear:.4f}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(debug_frame, f"Right EAR: {right_ear:.4f}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(debug_frame, f"Avg EAR: {avg_ear:.4f}", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(debug_frame, f"Threshold: {threshold:.4f}", (10, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Add blink status
                eyes_closed = avg_ear < threshold
                status_color = (0, 0, 255) if eyes_closed else (0, 255, 0)  # Red if closed, Green if open
                status_text = "Eyes CLOSED" if eyes_closed else "Eyes OPEN"
                cv2.putText(debug_frame, status_text, (10, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            
            return debug_frame
            
        except Exception as e:
            logger.error(f"[ERROR] Debug info drawing failed: {str(e)}")
            return frame
    
    def assess_face_alignment(self, face_landmarks) -> Dict:
        """
        Assess face alignment and pose for better quality assessment
        
        Args:
            face_landmarks: MediaPipe face landmarks
            
        Returns:
            Dictionary with alignment metrics
        """
        try:
            # Get key facial points for alignment assessment
            nose_tip = face_landmarks.landmark[4]  # Nose tip
            left_eye_center = face_landmarks.landmark[33]  # Left eye center
            right_eye_center = face_landmarks.landmark[263]  # Right eye center
            left_ear = face_landmarks.landmark[234]  # Left ear
            right_ear = face_landmarks.landmark[454]  # Right ear
            
            # Calculate face symmetry (left-right balance)
            left_eye_to_nose = np.linalg.norm([
                left_eye_center.x - nose_tip.x,
                left_eye_center.y - nose_tip.y
            ])
            right_eye_to_nose = np.linalg.norm([
                right_eye_center.x - nose_tip.x,
                right_eye_center.y - nose_tip.y
            ])
            
            symmetry_score = min(left_eye_to_nose, right_eye_to_nose) / max(left_eye_to_nose, right_eye_to_nose)
            symmetry_ok = symmetry_score > 0.8  # 80% symmetry threshold
            
            # Calculate head pose (simple estimation)
            eye_center_x = (left_eye_center.x + right_eye_center.x) / 2
            eye_center_y = (left_eye_center.y + right_eye_center.y) / 2
            
            # Check if face is roughly centered (simple approach)
            face_centered = 0.3 < eye_center_x < 0.7 and 0.3 < eye_center_y < 0.7
            
            # Calculate face size relative to frame
            face_width = abs(left_ear.x - right_ear.x)
            face_height = abs(left_ear.y - nose_tip.y)
            face_size_ok = face_width > 0.3 and face_height > 0.3  # Face should occupy reasonable portion of frame
            
            # Overall alignment score
            alignment_score = 0
            if symmetry_ok: alignment_score += 25
            if face_centered: alignment_score += 25
            if face_size_ok: alignment_score += 25
            
            # Additional 25 points for good overall alignment
            if alignment_score >= 50: alignment_score += 25
            
            return {
                'symmetry_score': symmetry_score,
                'symmetry_ok': symmetry_ok,
                'face_centered': face_centered,
                'face_size_ok': face_size_ok,
                'alignment_score': alignment_score,
                'face_width': face_width,
                'face_height': face_height,
                'eye_center_x': eye_center_x,
                'eye_center_y': eye_center_y
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Face alignment assessment failed: {str(e)}")
            return {
                'symmetry_score': 0.0,
                'symmetry_ok': False,
                'face_centered': False,
                'face_size_ok': False,
                'alignment_score': 0,
                'error': str(e)
            }
    
    def assess_advanced_quality(self, frame: np.ndarray, face_landmarks) -> Dict:
        """
        Advanced quality assessment with face symmetry and lighting analysis
        
        Args:
            frame: Input frame
            face_landmarks: MediaPipe face landmarks
            
        Returns:
            Dictionary with advanced quality metrics
        """
        try:
            # Get basic quality metrics
            basic_quality = self.assess_face_quality(frame)
            alignment_metrics = self.assess_face_alignment(face_landmarks)
            
            # Advanced lighting analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
            
            # Analyze lighting uniformity
            face_region = self._extract_face_region(frame, face_landmarks)
            if face_region is not None:
                face_gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY) if len(face_region.shape) == 3 else face_region
                
                # Calculate lighting uniformity (lower std dev = more uniform)
                lighting_std = np.std(face_gray)
                lighting_uniformity = max(0, 100 - lighting_std * 2)  # Scale to 0-100
                
                # Calculate histogram spread for lighting quality
                hist = cv2.calcHist([face_gray], [0], None, [256], [0, 256])
                hist_spread = np.std(hist)
                
                # Detect overexposure and underexposure
                overexposed_pixels = np.sum(face_gray > 240) / face_gray.size * 100
                underexposed_pixels = np.sum(face_gray < 20) / face_gray.size * 100
                
                exposure_ok = overexposed_pixels < 10 and underexposed_pixels < 10
            else:
                lighting_uniformity = 0
                hist_spread = 0
                overexposed_pixels = 0
                underexposed_pixels = 0
                exposure_ok = False
            
            # Combined advanced quality score
            advanced_score = (
                basic_quality['quality_score'] * 0.4 +
                alignment_metrics['alignment_score'] * 0.3 +
                lighting_uniformity * 0.2 +
                (100 if exposure_ok else 0) * 0.1
            )
            
            return {
                'basic_quality': basic_quality,
                'alignment_metrics': alignment_metrics,
                'lighting_uniformity': lighting_uniformity,
                'histogram_spread': hist_spread,
                'overexposed_pixels': overexposed_pixels,
                'underexposed_pixels': underexposed_pixels,
                'exposure_ok': exposure_ok,
                'advanced_quality_score': advanced_score,
                'quality_grade': self._get_quality_grade(advanced_score)
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Advanced quality assessment failed: {str(e)}")
            return {
                'error': str(e),
                'advanced_quality_score': 0,
                'quality_grade': 'ERROR'
            }
    
    def _extract_face_region(self, frame: np.ndarray, face_landmarks) -> Optional[np.ndarray]:
        """Extract face region from frame using landmarks"""
        try:
            h, w = frame.shape[:2]
            
            # Get face boundary landmarks
            landmarks = []
            for landmark in face_landmarks.landmark:
                landmarks.append([int(landmark.x * w), int(landmark.y * h)])
            
            landmarks = np.array(landmarks)
            
            # Create bounding box
            x_min, y_min = np.min(landmarks, axis=0)
            x_max, y_max = np.max(landmarks, axis=0)
            
            # Add padding
            padding = 20
            x_min = max(0, x_min - padding)
            y_min = max(0, y_min - padding)
            x_max = min(w, x_max + padding)
            y_max = min(h, y_max + padding)
            
            return frame[y_min:y_max, x_min:x_max]
            
        except Exception as e:
            logger.error(f"[ERROR] Face region extraction failed: {str(e)}")
            return None
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade"""
        if score >= 90: return 'A+'
        elif score >= 85: return 'A'
        elif score >= 80: return 'B+'
        elif score >= 75: return 'B'
        elif score >= 70: return 'C+'
        elif score >= 65: return 'C'
        elif score >= 60: return 'D+'
        elif score >= 55: return 'D'
        else: return 'F'

# Global liveness detection instance
liveness_detection = LivenessDetection()
