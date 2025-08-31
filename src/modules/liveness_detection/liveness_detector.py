"""
Refactored Liveness Detection System

This module orchestrates liveness detection using focused components,
following the Single-Responsibility Principle.
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import List, Optional, Dict, Any
import logging

from .blink_detector import BlinkDetector
from .head_movement_detector import HeadMovementDetector
from .eye_movement_detector import EyeMovementDetector
from .mouth_movement_detector import MouthMovementDetector
from .depth_analyzer import DepthAnalyzer
from .texture_analyzer import TextureAnalyzer
from .config_manager import LivenessConfigManager
from .performance_tracker import PerformanceTracker

# Import interface
try:
    from ...interfaces.liveness_interface import LivenessInterface, LivenessResult, LivenessTestType
except ImportError:
    # Fallback to absolute imports for testing
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))
    from interfaces.liveness_interface import LivenessInterface, LivenessResult, LivenessTestType

logger = logging.getLogger(__name__)


class LivenessDetection(LivenessInterface):
    """Orchestrates liveness detection using focused components"""
    
    def __init__(self):
        """Initialize liveness detection system with focused components"""
        # Initialize MediaPipe
        self.mp_face_mesh = None
        self.mp_drawing = None
        self.mp_drawing_styles = None
        
        # Initialize focused components
        self.config_manager = LivenessConfigManager()
        self.performance_tracker = PerformanceTracker()
        self.blink_detector = BlinkDetector()
        self.head_movement_detector = HeadMovementDetector()
        self.eye_movement_detector = EyeMovementDetector()
        self.mouth_movement_detector = MouthMovementDetector()
        self.depth_analyzer = DepthAnalyzer()
        self.texture_analyzer = TextureAnalyzer()
        
        # Initialize MediaPipe
        self.initialize_mediapipe()
        
        logger.info("Refactored Liveness Detection System initialized successfully")
    
    def initialize_mediapipe(self) -> bool:
        """Initialize MediaPipe FaceMesh"""
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
        """Detect blinking using the focused blink detector"""
        start_time = self.performance_tracker.start_timer()
        
        try:
            # Get MediaPipe landmarks
            landmarks = self._extract_landmarks(face_image)
            if not landmarks:
                return LivenessResult(
                    is_live=False,
                    confidence=0.0,
                    test_type=LivenessTestType.BLINK_DETECTION,
                    details={"error": "No face landmarks detected"},
                    processing_time_ms=0.0
                )
            
            # Use focused blink detector
            is_blinking, ear_value = self.blink_detector.detect_blink(landmarks)
            
            # Record performance
            processing_time = self.performance_tracker.end_timer(start_time)
            self.performance_tracker.record_test("blink", processing_time)
            
            return LivenessResult(
                is_live=is_blinking,
                confidence=ear_value,
                test_type=LivenessTestType.BLINK_DETECTION,
                details={
                    "ear_value": ear_value,
                    "threshold": self.blink_detector.ear_threshold,
                    "blink_count": self.blink_detector.get_blink_count()
                },
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error in blink detection: {e}")
            return LivenessResult(
                is_live=False,
                confidence=0.0,
                test_type=LivenessTestType.BLINK_DETECTION,
                details={"error": str(e)},
                processing_time_ms=0.0
            )
    
    def detect_head_movement(self, face_images: List[np.ndarray]) -> LivenessResult:
        """Detect head movement using the focused head movement detector"""
        start_time = self.performance_tracker.start_timer()
        
        try:
            # Use focused head movement detector
            result = self.head_movement_detector.detect_movement(face_images)
            
            # Record performance
            processing_time = self.performance_tracker.end_timer(start_time)
            self.performance_tracker.record_test("head_movement", processing_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in head movement detection: {e}")
            return LivenessResult(
                is_live=False,
                confidence=0.0,
                test_type=LivenessTestType.HEAD_MOVEMENT,
                details={"error": str(e)}
            )
    
    def detect_eye_movement(self, face_images: List[np.ndarray]) -> LivenessResult:
        """Detect eye movement using the focused eye movement detector"""
        start_time = self.performance_tracker.start_timer()
        
        try:
            # Use focused eye movement detector
            result = self.eye_movement_detector.detect_movement(face_images)
            
            # Record performance
            processing_time = self.performance_tracker.end_timer(start_time)
            self.performance_tracker.record_test("eye_movement", processing_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in eye movement detection: {e}")
            return LivenessResult(
                is_live=False,
                confidence=0.0,
                test_type=LivenessTestType.EYE_MOVEMENT,
                details={"error": str(e)}
            )
    
    def detect_mouth_movement(self, face_images: List[np.ndarray]) -> LivenessResult:
        """Detect mouth movement using the focused mouth movement detector"""
        start_time = self.performance_tracker.start_timer()
        
        try:
            # Use focused mouth movement detector
            result = self.mouth_movement_detector.detect_movement(face_images)
            
            # Record performance
            processing_time = self.performance_tracker.end_timer(start_time)
            self.performance_tracker.record_test("mouth_movement", processing_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in mouth movement detection: {e}")
            return LivenessResult(
                is_live=False,
                confidence=0.0,
                test_type=LivenessTestType.MOUTH_MOVEMENT,
                details={"error": str(e)}
            )
    
    def analyze_depth(self, face_image: np.ndarray) -> LivenessResult:
        """Analyze depth using the focused depth analyzer"""
        start_time = self.performance_tracker.start_timer()
        
        try:
            # Use focused depth analyzer
            result = self.depth_analyzer.analyze(face_image)
            
            # Record performance
            processing_time = self.performance_tracker.end_timer(start_time)
            self.performance_tracker.record_test("depth", processing_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in depth analysis: {e}")
            return LivenessResult(
                is_live=False,
                confidence=0.0,
                test_type=LivenessTestType.DEPTH,
                details={"error": str(e)}
            )
    
    def analyze_texture(self, face_image: np.ndarray) -> LivenessResult:
        """Analyze texture using the focused texture analyzer"""
        start_time = self.performance_tracker.start_timer()
        
        try:
            # Use focused texture analyzer
            result = self.texture_analyzer.analyze(face_image)
            
            # Record performance
            processing_time = self.performance_tracker.end_timer(start_time)
            self.performance_tracker.record_test("texture", processing_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in texture analysis: {e}")
            return LivenessResult(
                is_live=False,
                confidence=0.0,
                test_type=LivenessTestType.TEXTURE,
                details={"error": str(e)}
            )
    
    def run_comprehensive_test(self, face_images: List[np.ndarray],
                             test_types: List[LivenessTestType] = None) -> LivenessResult:
        """Run comprehensive liveness test using focused components"""
        if test_types is None:
            test_types = [LivenessTestType.BLINK_DETECTION, LivenessTestType.HEAD_MOVEMENT]
        
        start_time = self.performance_tracker.start_timer()
        results = []
        
        try:
            for test_type in test_types:
                if test_type == LivenessTestType.BLINK_DETECTION and face_images:
                    result = self.detect_blink(face_images[0])
                elif test_type == LivenessTestType.HEAD_MOVEMENT:
                    result = self.detect_head_movement(face_images)
                elif test_type == LivenessTestType.EYE_MOVEMENT:
                    result = self.detect_eye_movement(face_images)
                elif test_type == LivenessTestType.MOUTH_MOVEMENT:
                    result = self.detect_mouth_movement(face_images)
                elif test_type == LivenessTestType.DEPTH_ANALYSIS and face_images:
                    result = self.analyze_depth(face_images[0])
                elif test_type == LivenessTestType.TEXTURE_ANALYSIS and face_images:
                    result = self.analyze_texture(face_images[0])
                else:
                    continue
                
                results.append(result)
            
            # Record comprehensive test performance
            processing_time = self.performance_tracker.end_timer(start_time)
            self.performance_tracker.record_test("comprehensive", processing_time)
            
            # Aggregate results
            if results:
                overall_confidence = sum(r.confidence for r in results) / len(results)
                overall_liveness = any(r.is_live for r in results)
                
                return LivenessResult(
                    is_live=overall_liveness,
                    confidence=overall_confidence,
                    test_type=LivenessTestType.COMPREHENSIVE,
                    details={
                        "individual_results": results,
                        "processing_time_ms": processing_time,
                        "test_types": [t.value for t in test_types]
                    }
                )
            else:
                return LivenessResult(
                    is_live=False,
                    confidence=0.0,
                    test_type=LivenessTestType.COMPREHENSIVE,
                    details={"error": "No valid tests executed"}
                )
                
        except Exception as e:
            logger.error(f"Error in comprehensive test: {e}")
            return LivenessResult(
                is_live=False,
                confidence=0.0,
                test_type=LivenessTestType.COMPREHENSIVE,
                details={"error": str(e)}
            )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from the performance tracker"""
        return self.performance_tracker.get_performance_metrics()
    
    def is_healthy(self) -> bool:
        """Check if the system is healthy using the performance tracker"""
        return self.performance_tracker.is_healthy()
    
    def get_required_frames(self, test_type: LivenessTestType) -> int:
        """Get the number of frames required for a specific test type"""
        frame_requirements = {
            LivenessTestType.BLINK_DETECTION: 1,
            LivenessTestType.HEAD_MOVEMENT: 3,
            LivenessTestType.EYE_MOVEMENT: 3,
            LivenessTestType.MOUTH_MOVEMENT: 3,
            LivenessTestType.DEPTH_ANALYSIS: 1,
            LivenessTestType.TEXTURE_ANALYSIS: 1,
            LivenessTestType.COMPREHENSIVE: 3
        }
        return frame_requirements.get(test_type, 1)
    
    def preprocess_for_liveness(self, face_image: np.ndarray) -> np.ndarray:
        """Preprocess face image for liveness detection"""
        try:
            # Convert to RGB if needed
            if len(face_image.shape) == 3 and face_image.shape[2] == 3:
                if face_image.dtype != np.uint8:
                    face_image = (face_image * 255).astype(np.uint8)
            else:
                logger.warning("Invalid image format for preprocessing")
                return face_image
            
            # Resize if too large (MediaPipe works better with smaller images)
            height, width = face_image.shape[:2]
            if width > 640 or height > 640:
                scale = min(640 / width, 640 / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                face_image = cv2.resize(face_image, (new_width, new_height))
            
            return face_image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return face_image
    
    def get_test_configuration(self, test_type: LivenessTestType) -> Dict[str, Any]:
        """Get configuration for a specific test type"""
        return self.config_manager.get_test_configuration(test_type)
    
    def update_test_configuration(self, test_type: LivenessTestType, config: Dict[str, Any]) -> bool:
        """Update configuration for a specific test type"""
        return self.config_manager.update_test_configuration(test_type, config)
    
    def get_supported_tests(self) -> List[LivenessTestType]:
        """Get list of supported liveness test types"""
        return [
            LivenessTestType.BLINK_DETECTION,
            LivenessTestType.HEAD_MOVEMENT,
            LivenessTestType.EYE_MOVEMENT,
            LivenessTestType.MOUTH_MOVEMENT,
            LivenessTestType.DEPTH_ANALYSIS,
            LivenessTestType.TEXTURE_ANALYSIS,
            LivenessTestType.COMPREHENSIVE
        ]
    
    def is_test_available(self, test_type: LivenessTestType) -> bool:
        """Check if a specific test type is available"""
        try:
            if test_type == LivenessTestType.BLINK_DETECTION:
                return self.blink_detector is not None
            elif test_type == LivenessTestType.HEAD_MOVEMENT:
                return self.head_movement_detector is not None
            elif test_type == LivenessTestType.EYE_MOVEMENT:
                return self.eye_movement_detector is not None
            elif test_type == LivenessTestType.MOUTH_MOVEMENT:
                return self.mouth_movement_detector is not None
            elif test_type == LivenessTestType.DEPTH_ANALYSIS:
                return self.depth_analyzer is not None
            elif test_type == LivenessTestType.TEXTURE_ANALYSIS:
                return self.texture_analyzer is not None
            elif test_type == LivenessTestType.COMPREHENSIVE:
                return all([
                    self.blink_detector is not None,
                    self.head_movement_detector is not None
                ])
            return False
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the underlying liveness detection models"""
        return {
            'mediapipe_version': mp.__version__ if hasattr(mp, '__version__') else 'Unknown',
            'face_mesh_available': self.mp_face_mesh is not None,
            'opencv_version': cv2.__version__,
            'numpy_version': np.__version__,
            'supported_landmarks': 468,  # MediaPipe FaceMesh standard
            'components': {
                'blink_detector': self.blink_detector is not None,
                'head_movement_detector': self.head_movement_detector is not None,
                'eye_movement_detector': self.eye_movement_detector is not None,
                'mouth_movement_detector': self.mouth_movement_detector is not None,
                'depth_analyzer': self.depth_analyzer is not None,
                'texture_analyzer': self.texture_analyzer is not None
            }
        }

    def _extract_landmarks(self, face_image: np.ndarray) -> Optional[List]:
        """Extract face landmarks using MediaPipe"""
        try:
            logger.debug(f"Extracting landmarks from image: shape={face_image.shape}, dtype={face_image.dtype}")
            
            # Use the working approach: no resizing, just convert to RGB
            # Convert BGR to RGB (MediaPipe expects RGB)
            rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            logger.debug(f"Converted to RGB: shape={rgb_image.shape}, dtype={rgb_image.dtype}")
            
            # Create a new MediaPipe instance each time with working configuration
            with self.mp_face_mesh.FaceMesh(
                min_detection_confidence=0.3,  # Use working threshold
                min_tracking_confidence=0.3,   # Use working threshold
                max_num_faces=1,
                refine_landmarks=True
            ) as face_mesh:
                logger.debug("MediaPipe FaceMesh instance created")
                results = face_mesh.process(rgb_image)
                logger.debug(f"MediaPipe results: {results}")
                
                if results.multi_face_landmarks:
                    logger.debug(f"Face detected with {len(results.multi_face_landmarks[0].landmark)} landmarks")
                    return results.multi_face_landmarks[0].landmark
                else:
                    logger.debug("No face landmarks detected")
                    return None
                
        except Exception as e:
            logger.error(f"Error extracting landmarks: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
