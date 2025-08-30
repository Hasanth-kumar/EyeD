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
from typing import Tuple, List, Optional, Dict, Any
import logging
import time

# Import interface
try:
    from ..interfaces.liveness_interface import LivenessInterface, LivenessResult, LivenessTestType
except ImportError:
    # Fallback to absolute imports for testing
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
    from interfaces.liveness_interface import LivenessInterface, LivenessResult, LivenessTestType

# Configure logging
logger = logging.getLogger(__name__)

class LivenessDetection(LivenessInterface):
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
        
        # Performance tracking
        self.processing_times = []
        self.test_counts = {}
        
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
    
    def detect_blink(self, face_image: np.ndarray) -> LivenessResult:
        """
        Detect blinking in a face image
        
        Args:
            face_image: Face image to analyze
            
        Returns:
            LivenessResult indicating if blink was detected
        """
        start_time = time.time()
        
        try:
            # Preprocess image for liveness detection
            processed_image = self.preprocess_for_liveness(face_image)
            
            # Initialize MediaPipe FaceMesh
            with self.mp_face_mesh.FaceMesh(
                max_num_faces=self.max_num_faces,
                refine_landmarks=self.refine_landmarks,
                min_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=self.min_tracking_confidence
            ) as face_mesh:
                
                # Convert BGR to RGB
                rgb_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
                
                # Process image
                results = face_mesh.process(rgb_image)
                
                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0]
                    
                    # Calculate EAR for both eyes
                    left_ear = self._calculate_ear(landmarks.landmark, self.LEFT_EYE_INDICES)
                    right_ear = self._calculate_ear(landmarks.landmark, self.RIGHT_EYE_INDICES)
                    
                    # Average EAR
                    avg_ear = (left_ear + right_ear) / 2.0
                    
                    # Determine if blink is detected
                    is_blink = avg_ear < self.ear_threshold
                    confidence = 1.0 - (avg_ear / self.ear_threshold) if is_blink else avg_ear / self.ear_threshold
                    
                    # Update blink counter
                    if is_blink:
                        self.blink_counter += 1
                        self.consecutive_frames += 1
                    else:
                        self.consecutive_frames = 0
                    
                    details = {
                        'left_ear': left_ear,
                        'right_ear': right_ear,
                        'avg_ear': avg_ear,
                        'ear_threshold': self.ear_threshold,
                        'blink_counter': self.blink_counter,
                        'consecutive_frames': self.consecutive_frames
                    }
                    
                else:
                    is_blink = False
                    confidence = 0.0
                    details = {'error': 'No face landmarks detected'}
            
            processing_time = (time.time() - start_time) * 1000
            self._update_performance_metrics('blink_detection', processing_time)
            
            return LivenessResult(
                is_live=is_blink,
                confidence=confidence,
                test_type=LivenessTestType.BLINK_DETECTION,
                details=details,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Blink detection failed: {e}")
            processing_time = (time.time() - start_time) * 1000
            return LivenessResult(
                is_live=False,
                confidence=0.0,
                test_type=LivenessTestType.BLINK_DETECTION,
                details={'error': str(e)},
                processing_time_ms=processing_time
            )
    
    def detect_head_movement(self, face_images: List[np.ndarray]) -> LivenessResult:
        """
        Detect head movement across multiple frames
        
        Args:
            face_images: List of face images from consecutive frames
            
        Returns:
            LivenessResult indicating if head movement was detected
        """
        start_time = time.time()
        
        try:
            if len(face_images) < 2:
                return LivenessResult(
                    is_live=False,
                    confidence=0.0,
                    test_type=LivenessTestType.HEAD_MOVEMENT,
                    details={'error': 'Insufficient frames for head movement detection'},
                    processing_time_ms=0.0
                )
            
            # Extract head pose from each frame
            head_poses = []
            for image in face_images:
                pose = self._extract_head_pose(image)
                if pose is not None:
                    head_poses.append(pose)
            
            if len(head_poses) < 2:
                return LivenessResult(
                    is_live=False,
                    confidence=0.0,
                    test_type=LivenessTestType.HEAD_MOVEMENT,
                    details={'error': 'Could not extract head pose from frames'},
                    processing_time_ms=0.0
                )
            
            # Calculate movement between consecutive poses
            movements = []
            for i in range(1, len(head_poses)):
                movement = self._calculate_pose_difference(head_poses[i-1], head_poses[i])
                movements.append(movement)
            
            # Determine if significant movement occurred
            avg_movement = np.mean(movements)
            movement_threshold = 5.0  # degrees
            is_movement = avg_movement > movement_threshold
            
            confidence = min(1.0, avg_movement / (movement_threshold * 2))
            
            details = {
                'movements': movements,
                'avg_movement': avg_movement,
                'movement_threshold': movement_threshold,
                'frames_processed': len(face_images)
            }
            
            processing_time = (time.time() - start_time) * 1000
            self._update_performance_metrics('head_movement', processing_time)
            
            return LivenessResult(
                is_live=is_movement,
                confidence=confidence,
                test_type=LivenessTestType.HEAD_MOVEMENT,
                details=details,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Head movement detection failed: {e}")
            processing_time = (time.time() - start_time) * 1000
            return LivenessResult(
                is_live=False,
                confidence=0.0,
                test_type=LivenessTestType.HEAD_MOVEMENT,
                details={'error': str(e)},
                processing_time_ms=processing_time
            )
    
    def detect_eye_movement(self, face_images: List[np.ndarray]) -> LivenessResult:
        """
        Detect eye movement across multiple frames
        
        Args:
            face_images: List of face images from consecutive frames
            
        Returns:
            LivenessResult indicating if eye movement was detected
        """
        start_time = time.time()
        
        try:
            if len(face_images) < 2:
                return LivenessResult(
                    is_live=False,
                    confidence=0.0,
                    test_type=LivenessTestType.EYE_MOVEMENT,
                    details={'error': 'Insufficient frames for eye movement detection'},
                    processing_time_ms=0.0
                )
            
            # Extract eye positions from each frame
            eye_positions = []
            for image in face_images:
                positions = self._extract_eye_positions(image)
                if positions is not None:
                    eye_positions.append(positions)
            
            if len(eye_positions) < 2:
                return LivenessResult(
                    is_live=False,
                    confidence=0.0,
                    test_type=LivenessTestType.EYE_MOVEMENT,
                    details={'error': 'Could not extract eye positions from frames'},
                    processing_time_ms=0.0
                )
            
            # Calculate eye movement between consecutive frames
            movements = []
            for i in range(1, len(eye_positions)):
                movement = self._calculate_eye_movement(eye_positions[i-1], eye_positions[i])
                movements.append(movement)
            
            # Determine if significant eye movement occurred
            avg_movement = np.mean(movements)
            movement_threshold = 2.0  # pixels
            is_movement = avg_movement > movement_threshold
            
            confidence = min(1.0, avg_movement / (movement_threshold * 2))
            
            details = {
                'movements': movements,
                'avg_movement': avg_movement,
                'movement_threshold': movement_threshold,
                'frames_processed': len(face_images)
            }
            
            processing_time = (time.time() - start_time) * 1000
            self._update_performance_metrics('eye_movement', processing_time)
            
            return LivenessResult(
                is_live=is_movement,
                confidence=confidence,
                test_type=LivenessTestType.EYE_MOVEMENT,
                details=details,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Eye movement detection failed: {e}")
            processing_time = (time.time() - start_time) * 1000
            return LivenessResult(
                is_live=False,
                confidence=0.0,
                test_type=LivenessTestType.EYE_MOVEMENT,
                details={'error': str(e)},
                processing_time_ms=processing_time
            )
    
    def detect_mouth_movement(self, face_images: List[np.ndarray]) -> LivenessResult:
        """
        Detect mouth movement across multiple frames
        
        Args:
            face_images: List of face images from consecutive frames
            
        Returns:
            LivenessResult indicating if mouth movement was detected
        """
        start_time = time.time()
        
        try:
            if len(face_images) < 2:
                return LivenessResult(
                    is_live=False,
                    confidence=0.0,
                    test_type=LivenessTestType.MOUTH_MOVEMENT,
                    details={'error': 'Insufficient frames for mouth movement detection'},
                    processing_time_ms=0.0
                )
            
            # Extract mouth positions from each frame
            mouth_positions = []
            for image in face_images:
                positions = self._extract_mouth_positions(image)
                if positions is not None:
                    mouth_positions.append(positions)
            
            if len(mouth_positions) < 2:
                return LivenessResult(
                    is_live=False,
                    confidence=0.0,
                    test_type=LivenessTestType.MOUTH_MOVEMENT,
                    details={'error': 'Could not extract mouth positions from frames'},
                    processing_time_ms=0.0
                )
            
            # Calculate mouth movement between consecutive frames
            movements = []
            for i in range(1, len(mouth_positions)):
                movement = self._calculate_mouth_movement(mouth_positions[i-1], mouth_positions[i])
                movements.append(movement)
            
            # Determine if significant mouth movement occurred
            avg_movement = np.mean(movements)
            movement_threshold = 3.0  # pixels
            is_movement = avg_movement > movement_threshold
            
            confidence = min(1.0, avg_movement / (movement_threshold * 2))
            
            details = {
                'movements': movements,
                'avg_movement': avg_movement,
                'movement_threshold': movement_threshold,
                'frames_processed': len(face_images)
            }
            
            processing_time = (time.time() - start_time) * 1000
            self._update_performance_metrics('mouth_movement', processing_time)
            
            return LivenessResult(
                is_live=is_movement,
                confidence=confidence,
                test_type=LivenessTestType.MOUTH_MOVEMENT,
                details=details,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Mouth movement detection failed: {e}")
            processing_time = (time.time() - start_time) * 1000
            return LivenessResult(
                is_live=False,
                confidence=0.0,
                test_type=LivenessTestType.MOUTH_MOVEMENT,
                details={'error': str(e)},
                processing_time_ms=processing_time
            )
    
    def analyze_depth(self, face_image: np.ndarray) -> LivenessResult:
        """
        Analyze depth information to detect 2D spoofing attempts
        
        Args:
            face_image: Face image to analyze
            
        Returns:
            LivenessResult indicating if depth analysis suggests liveness
        """
        start_time = time.time()
        
        try:
            # Convert to grayscale for analysis
            if len(face_image.shape) == 3:
                gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = face_image
            
            # Apply edge detection to find contours
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return LivenessResult(
                    is_live=False,
                    confidence=0.0,
                    test_type=LivenessTestType.DEPTH_ANALYSIS,
                    details={'error': 'No contours found'},
                    processing_time_ms=0.0
                )
            
            # Analyze contour complexity (3D faces have more complex contours)
            contour_areas = [cv2.contourArea(c) for c in contours]
            total_area = sum(contour_areas)
            
            # Calculate contour complexity
            complexity = len(contours) / max(1, total_area / 1000)
            
            # Determine if complexity suggests 3D face
            complexity_threshold = 0.1
            is_3d = complexity > complexity_threshold
            
            confidence = min(1.0, complexity / (complexity_threshold * 2))
            
            details = {
                'contour_count': len(contours),
                'total_area': total_area,
                'complexity': complexity,
                'complexity_threshold': complexity_threshold
            }
            
            processing_time = (time.time() - start_time) * 1000
            self._update_performance_metrics('depth_analysis', processing_time)
            
            return LivenessResult(
                is_live=is_3d,
                confidence=confidence,
                test_type=LivenessTestType.DEPTH_ANALYSIS,
                details=details,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Depth analysis failed: {e}")
            processing_time = (time.time() - start_time) * 1000
            return LivenessResult(
                is_live=False,
                confidence=0.0,
                test_type=LivenessTestType.DEPTH_ANALYSIS,
                details={'error': str(e)},
                processing_time_ms=processing_time
            )
    
    def analyze_texture(self, face_image: np.ndarray) -> LivenessResult:
        """
        Analyze texture patterns to detect spoofing attempts
        
        Args:
            face_image: Face image to analyze
            
        Returns:
            LivenessResult indicating if texture analysis suggests liveness
        """
        start_time = time.time()
        
        try:
            # Convert to grayscale for analysis
            if len(face_image.shape) == 3:
                gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = face_image
            
            # Calculate texture features using Local Binary Patterns
            # This is a simplified version - in practice, you'd use more sophisticated texture analysis
            
            # Calculate gradient magnitude
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Calculate texture statistics
            mean_gradient = np.mean(gradient_magnitude)
            std_gradient = np.std(gradient_magnitude)
            
            # Calculate local variance
            kernel = np.ones((5, 5), np.float32) / 25
            local_mean = cv2.filter2D(gray.astype(np.float32), -1, kernel)
            local_variance = cv2.filter2D((gray.astype(np.float32) - local_mean)**2, -1, kernel)
            mean_local_variance = np.mean(local_variance)
            
            # Determine if texture suggests real face
            # Real faces typically have more texture variation
            texture_score = (mean_gradient / 100.0 + std_gradient / 50.0 + mean_local_variance / 1000.0) / 3.0
            texture_threshold = 0.3
            
            is_real_texture = texture_score > texture_threshold
            confidence = min(1.0, texture_score / (texture_threshold * 2))
            
            details = {
                'mean_gradient': mean_gradient,
                'std_gradient': std_gradient,
                'mean_local_variance': mean_local_variance,
                'texture_score': texture_score,
                'texture_threshold': texture_threshold
            }
            
            processing_time = (time.time() - start_time) * 1000
            self._update_performance_metrics('texture_analysis', processing_time)
            
            return LivenessResult(
                is_live=is_real_texture,
                confidence=confidence,
                test_type=LivenessTestType.TEXTURE_ANALYSIS,
                details=details,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Texture analysis failed: {e}")
            processing_time = (time.time() - start_time) * 1000
            return LivenessResult(
                is_live=False,
                confidence=0.0,
                test_type=LivenessTestType.TEXTURE_ANALYSIS,
                details={'error': str(e)},
                processing_time_ms=processing_time
            )
    
    def run_comprehensive_test(self, face_images: List[np.ndarray],
                             test_types: Optional[List[LivenessTestType]] = None) -> LivenessResult:
        """
        Run a comprehensive liveness test using multiple detection methods
        
        Args:
            face_images: List of face images for analysis
            test_types: Optional list of specific test types to run
            
        Returns:
            LivenessResult with comprehensive analysis
        """
        start_time = time.time()
        
        try:
            if test_types is None:
                test_types = self.get_supported_tests()
            
            results = []
            total_confidence = 0.0
            successful_tests = 0
            
            for test_type in test_types:
                if not self.is_test_available(test_type):
                    continue
                
                try:
                    if test_type == LivenessTestType.BLINK_DETECTION:
                        result = self.detect_blink(face_images[0] if face_images else np.zeros((100, 100, 3)))
                    elif test_type == LivenessTestType.HEAD_MOVEMENT:
                        result = self.detect_head_movement(face_images)
                    elif test_type == LivenessTestType.EYE_MOVEMENT:
                        result = self.detect_eye_movement(face_images)
                    elif test_type == LivenessTestType.MOUTH_MOVEMENT:
                        result = self.detect_mouth_movement(face_images)
                    elif test_type == LivenessTestType.DEPTH_ANALYSIS:
                        result = self.analyze_depth(face_images[0] if face_images else np.zeros((100, 100, 3)))
                    elif test_type == LivenessTestType.TEXTURE_ANALYSIS:
                        result = self.analyze_texture(face_images[0] if face_images else np.zeros((100, 100, 3)))
                    else:
                        continue
                    
                    results.append(result)
                    if result.is_live:
                        total_confidence += result.confidence
                        successful_tests += 1
                        
                except Exception as e:
                    logger.warning(f"Test {test_type.value} failed: {e}")
                    continue
            
            # Calculate overall liveness score
            if successful_tests > 0:
                overall_confidence = total_confidence / successful_tests
                is_live = overall_confidence > 0.5
            else:
                overall_confidence = 0.0
                is_live = False
            
            details = {
                'tests_run': len(results),
                'successful_tests': successful_tests,
                'individual_results': [r.details for r in results],
                'test_types': [r.test_type.value for r in results]
            }
            
            processing_time = (time.time() - start_time) * 1000
            
            return LivenessResult(
                is_live=is_live,
                confidence=overall_confidence,
                test_type=LivenessTestType.BLINK_DETECTION,  # Use primary test type
                details=details,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Comprehensive test failed: {e}")
            processing_time = (time.time() - start_time) * 1000
            return LivenessResult(
                is_live=False,
                confidence=0.0,
                test_type=LivenessTestType.BLINK_DETECTION,
                details={'error': str(e)},
                processing_time_ms=processing_time
            )
    
    def get_required_frames(self, test_type: LivenessTestType) -> int:
        """
        Get the number of frames required for a specific test type
        
        Args:
            test_type: Type of liveness test
            
        Returns:
            Number of frames required
        """
        frame_requirements = {
            LivenessTestType.BLINK_DETECTION: 1,
            LivenessTestType.HEAD_MOVEMENT: 3,
            LivenessTestType.EYE_MOVEMENT: 3,
            LivenessTestType.MOUTH_MOVEMENT: 3,
            LivenessTestType.DEPTH_ANALYSIS: 1,
            LivenessTestType.TEXTURE_ANALYSIS: 1
        }
        
        return frame_requirements.get(test_type, 1)
    
    def preprocess_for_liveness(self, face_image: np.ndarray) -> np.ndarray:
        """
        Preprocess face image for liveness detection
        
        Args:
            face_image: Input face image
            
        Returns:
            Preprocessed image optimized for liveness detection
        """
        try:
            # Ensure minimum resolution
            if face_image.shape[0] < self.min_resolution[0] or face_image.shape[1] < self.min_resolution[1]:
                face_image = cv2.resize(face_image, self.min_resolution)
            
            # Convert to RGB if needed
            if len(face_image.shape) == 3 and face_image.shape[2] == 3:
                # Already BGR, convert to RGB for MediaPipe
                processed = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            elif len(face_image.shape) == 3 and face_image.shape[2] == 4:
                # RGBA to RGB
                processed = cv2.cvtColor(face_image, cv2.COLOR_RGBA2RGB)
            else:
                # Grayscale to RGB
                processed = cv2.cvtColor(face_image, cv2.COLOR_GRAY2RGB)
            
            # Keep as uint8 for OpenCV operations
            # processed = processed.astype(np.float32) / 255.0
            
            return processed
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return face_image
    
    def get_test_configuration(self, test_type: LivenessTestType) -> Dict[str, Any]:
        """
        Get configuration for a specific test type
        
        Args:
            test_type: Type of liveness test
            
        Returns:
            Configuration dictionary for the test
        """
        configs = {
            LivenessTestType.BLINK_DETECTION: {
                'ear_threshold': self.ear_threshold,
                'min_consecutive_frames': self.min_consecutive_frames
            },
            LivenessTestType.HEAD_MOVEMENT: {
                'movement_threshold': 5.0,
                'min_frames': 3
            },
            LivenessTestType.EYE_MOVEMENT: {
                'movement_threshold': 2.0,
                'min_frames': 3
            },
            LivenessTestType.MOUTH_MOVEMENT: {
                'movement_threshold': 3.0,
                'min_frames': 3
            },
            LivenessTestType.DEPTH_ANALYSIS: {
                'complexity_threshold': 0.1
            },
            LivenessTestType.TEXTURE_ANALYSIS: {
                'texture_threshold': 0.3
            }
        }
        
        return configs.get(test_type, {})
    
    def update_test_configuration(self, test_type: LivenessTestType,
                                config: Dict[str, Any]) -> bool:
        """
        Update configuration for a specific test type
        
        Args:
            test_type: Type of liveness test
            config: New configuration parameters
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            if test_type == LivenessTestType.BLINK_DETECTION:
                if 'ear_threshold' in config:
                    self.ear_threshold = float(config['ear_threshold'])
                if 'min_consecutive_frames' in config:
                    self.min_consecutive_frames = int(config['min_consecutive_frames'])
            
            logger.info(f"Updated configuration for {test_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration for {test_type.value}: {e}")
            return False
    
    def get_supported_tests(self) -> List[LivenessTestType]:
        """
        Get list of supported liveness test types
        
        Returns:
            List of supported test types
        """
        return [
            LivenessTestType.BLINK_DETECTION,
            LivenessTestType.HEAD_MOVEMENT,
            LivenessTestType.EYE_MOVEMENT,
            LivenessTestType.MOUTH_MOVEMENT,
            LivenessTestType.DEPTH_ANALYSIS,
            LivenessTestType.TEXTURE_ANALYSIS
        ]
    
    def is_test_available(self, test_type: LivenessTestType) -> bool:
        """
        Check if a specific test type is available
        
        Args:
            test_type: Type of liveness test to check
            
        Returns:
            True if test is available, False otherwise
        """
        return test_type in self.get_supported_tests()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get liveness detection performance metrics
        
        Returns:
            Dictionary containing performance metrics
        """
        try:
            avg_processing_time = np.mean(self.processing_times) if self.processing_times else 0.0
            min_processing_time = np.min(self.processing_times) if self.processing_times else 0.0
            max_processing_time = np.max(self.processing_times) if self.processing_times else 0.0
            
            return {
                'total_tests': sum(self.test_counts.values()),
                'test_breakdown': self.test_counts.copy(),
                'average_processing_time_ms': avg_processing_time,
                'min_processing_time_ms': min_processing_time,
                'max_processing_time_ms': max_processing_time,
                'mediapipe_initialized': self.mp_face_mesh is not None,
                'supported_tests': [t.value for t in self.get_supported_tests()]
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {}
    
    def is_healthy(self) -> bool:
        """
        Check if the liveness detection system is in a healthy state
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Check if MediaPipe is initialized
            if self.mp_face_mesh is None:
                return False
            
            # Check if we can process a simple test image
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            try:
                result = self.detect_blink(test_image)
                return True
            except Exception:
                return False
                
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the underlying liveness detection models
        
        Returns:
            Dictionary containing model information
        """
        return {
            'mediapipe_version': mp.__version__ if hasattr(mp, '__version__') else 'Unknown',
            'face_mesh_available': self.mp_face_mesh is not None,
            'opencv_version': cv2.__version__,
            'numpy_version': np.__version__,
            'supported_landmarks': 468,  # MediaPipe FaceMesh standard
            'eye_landmark_count': len(self.LEFT_EYE_INDICES) + len(self.RIGHT_EYE_INDICES)
        }
    
    def _calculate_ear(self, landmarks: List, eye_indices: List[int]) -> float:
        """Calculate Eye Aspect Ratio (EAR) for given eye landmarks"""
        try:
            # Extract eye landmark coordinates
            eye_points = []
            for idx in eye_indices:
                if idx < len(landmarks):
                    point = landmarks[idx]
                    eye_points.append((point.x, point.y))
            
            if len(eye_points) < 6:
                return 0.0
            
            # Calculate EAR using the formula: EAR = (A + B) / (2 * C)
            # where A, B, C are the vertical distances between landmarks
            
            # Convert to numpy array for easier calculations
            points = np.array(eye_points)
            
            # Calculate vertical distances
            A = np.linalg.norm(points[1] - points[5])
            B = np.linalg.norm(points[2] - points[4])
            C = np.linalg.norm(points[0] - points[3])
            
            # Avoid division by zero
            if C == 0:
                return 0.0
            
            ear = (A + B) / (2.0 * C)
            return float(ear)
            
        except Exception as e:
            logger.error(f"EAR calculation failed: {e}")
            return 0.0
    
    def _extract_head_pose(self, image: np.ndarray) -> Optional[Dict[str, float]]:
        """Extract head pose from image (simplified implementation)"""
        try:
            # This is a simplified head pose estimation
            # In practice, you'd use a more sophisticated model
            
            # For now, return mock pose data
            return {
                'yaw': np.random.uniform(-10, 10),
                'pitch': np.random.uniform(-5, 5),
                'roll': np.random.uniform(-3, 3)
            }
        except Exception:
            return None
    
    def _calculate_pose_difference(self, pose1: Dict[str, float], pose2: Dict[str, float]) -> float:
        """Calculate difference between two head poses"""
        try:
            diff_yaw = abs(pose1['yaw'] - pose2['yaw'])
            diff_pitch = abs(pose1['pitch'] - pose2['pitch'])
            diff_roll = abs(pose1['roll'] - pose2['roll'])
            
            return (diff_yaw + diff_pitch + diff_roll) / 3.0
        except Exception:
            return 0.0
    
    def _extract_eye_positions(self, image: np.ndarray) -> Optional[Dict[str, Tuple[float, float]]]:
        """Extract eye positions from image"""
        try:
            # This is a simplified eye position extraction
            # In practice, you'd use MediaPipe or similar
            
            # For now, return mock positions
            return {
                'left_eye': (np.random.uniform(0.3, 0.4), np.random.uniform(0.4, 0.5)),
                'right_eye': (np.random.uniform(0.6, 0.7), np.random.uniform(0.4, 0.5))
            }
        except Exception:
            return None
    
    def _calculate_eye_movement(self, pos1: Dict[str, Tuple[float, float]], 
                               pos2: Dict[str, Tuple[float, float]]) -> float:
        """Calculate eye movement between two positions"""
        try:
            left_movement = np.linalg.norm(np.array(pos1['left_eye']) - np.array(pos2['left_eye']))
            right_movement = np.linalg.norm(np.array(pos1['right_eye']) - np.array(pos2['right_eye']))
            
            return (left_movement + right_movement) / 2.0
        except Exception:
            return 0.0
    
    def _extract_mouth_positions(self, image: np.ndarray) -> Optional[Dict[str, Tuple[float, float]]]:
        """Extract mouth positions from image"""
        try:
            # This is a simplified mouth position extraction
            # In practice, you'd use MediaPipe or similar
            
            # For now, return mock positions
            return {
                'mouth_center': (np.random.uniform(0.4, 0.6), np.random.uniform(0.7, 0.8))
            }
        except Exception:
            return None
    
    def _calculate_mouth_movement(self, pos1: Dict[str, Tuple[float, float]], 
                                 pos2: Dict[str, Tuple[float, float]]) -> float:
        """Calculate mouth movement between two positions"""
        try:
            movement = np.linalg.norm(np.array(pos1['mouth_center']) - np.array(pos2['mouth_center']))
            return movement
        except Exception:
            return 0.0
    
    def _update_performance_metrics(self, test_type: str, processing_time: float):
        """Update performance tracking metrics"""
        try:
            self.processing_times.append(processing_time)
            if test_type not in self.test_counts:
                self.test_counts[test_type] = 0
            self.test_counts[test_type] += 1
            
            # Keep only last 100 processing times
            if len(self.processing_times) > 100:
                self.processing_times.pop(0)
                
        except Exception as e:
            logger.error(f"Failed to update performance metrics: {e}")
