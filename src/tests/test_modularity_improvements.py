"""
Test Modularity Improvements - Phase 5 Complete

This test suite verifies that our modularity improvements follow
the Single-Responsibility Principle and proper architecture.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import numpy as np

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.modules.liveness_detection import (
    BlinkDetector,
    HeadMovementDetector,
    EyeMovementDetector,
    MouthMovementDetector,
    DepthAnalyzer,
    TextureAnalyzer,
    LivenessDetection,
    PerformanceTracker,
    LivenessConfigManager
)
from src.modules.face_database import FaceStorage


class TestModularityImprovements(unittest.TestCase):
    """Test that our modularity improvements follow proper principles"""
    
    def test_blink_detector_single_responsibility(self):
        """Test that BlinkDetector only handles blink detection"""
        detector = BlinkDetector()
        
        # Should only have blink-related methods
        methods = [method for method in dir(detector) if not method.startswith('_')]
        blink_methods = ['detect_blink', 'get_blink_count', 'reset_blink_counter', 'update_ear_threshold']
        
        for method in methods:
            self.assertIn(method, blink_methods, f"BlinkDetector has non-blink method: {method}")
    
    def test_performance_tracker_single_responsibility(self):
        """Test that PerformanceTracker only handles performance metrics"""
        tracker = PerformanceTracker()
        
        # Should only have performance-related methods
        methods = [method for method in dir(tracker) if not method.startswith('_')]
        perf_methods = ['start_timer', 'end_timer', 'record_test', 'get_performance_metrics', 
                       'is_healthy', 'reset_metrics', 'get_recent_performance']
        
        for method in methods:
            self.assertIn(method, perf_methods, f"PerformanceTracker has non-performance method: {method}")
    
    def test_config_manager_single_responsibility(self):
        """Test that LivenessConfigManager only handles configuration"""
        config_mgr = LivenessConfigManager()
        
        # Should only have config-related methods
        methods = [method for method in dir(config_mgr) if not method.startswith('_')]
        config_methods = ['get_config', 'update_config', 'get_test_configuration', 'reset_to_defaults']
        
        for method in methods:
            self.assertIn(method, config_methods, f"ConfigManager has non-config method: {method}")
    
    def test_face_storage_single_responsibility(self):
        """Test that FaceStorage only handles file operations"""
        storage = FaceStorage()
        
        # Should only have storage-related methods
        methods = [method for method in dir(storage) if not method.startswith('_')]
        storage_methods = ['save_face_data', 'load_face_data', 'delete_face_data', 
                          'get_face_data', 'list_all_faces', 'is_healthy']
        
        for method in methods:
            self.assertIn(method, storage_methods, f"FaceStorage has non-storage method: {method}")
    
    def test_liveness_detection_orchestration(self):
        """Test that LivenessDetection orchestrates components properly"""
        detector = LivenessDetection()
        
        # Should have focused components
        self.assertIsInstance(detector.blink_detector, BlinkDetector)
        self.assertIsInstance(detector.performance_tracker, PerformanceTracker)
        self.assertIsInstance(detector.config_manager, LivenessConfigManager)
        
        # Should delegate to components
        with patch.object(detector.blink_detector, 'detect_blink') as mock_blink:
            mock_blink.return_value = (True, 0.8)
            
            # Mock landmarks
            mock_landmarks = [Mock() for _ in range(100)]
            for i, landmark in enumerate(mock_landmarks):
                landmark.x = i / 100.0
                landmark.y = i / 100.0
            
            with patch.object(detector, '_extract_landmarks', return_value=mock_landmarks):
                result = detector.detect_blink(np.zeros((100, 100, 3)))
                
                # Should call blink detector
                mock_blink.assert_called_once()
                
                # Should record performance
                self.assertIn('processing_time_ms', result.details)
    
    def test_component_independence(self):
        """Test that components can work independently"""
        # Test blink detector independently
        blink_detector = BlinkDetector()
        mock_landmarks = [Mock() for _ in range(100)]
        for i, landmark in enumerate(mock_landmarks):
            landmark.x = i / 100.0
            landmark.y = i / 100.0
        
        is_blinking, ear_value = blink_detector.detect_blink(mock_landmarks)
        self.assertIsInstance(is_blinking, bool)
        self.assertIsInstance(ear_value, float)
        
        # Test performance tracker independently
        tracker = PerformanceTracker()
        start_time = tracker.start_timer()
        processing_time = tracker.end_timer(start_time)
        self.assertGreater(processing_time, 0)
        
        # Test config manager independently
        config_mgr = LivenessConfigManager()
        blink_config = config_mgr.get_config('blink_detection')
        self.assertIn('ear_threshold', blink_config)
    
    def test_no_cross_contamination(self):
        """Test that components don't have mixed responsibilities"""
        # BlinkDetector should not have performance tracking
        blink_detector = BlinkDetector()
        self.assertFalse(hasattr(blink_detector, 'processing_times'))
        self.assertFalse(hasattr(blink_detector, 'start_timer'))
        
        # PerformanceTracker should not have blink detection
        tracker = PerformanceTracker()
        self.assertFalse(hasattr(tracker, 'detect_blink'))
        self.assertFalse(hasattr(tracker, 'ear_threshold'))
        
        # ConfigManager should not have performance tracking
        config_mgr = LivenessConfigManager()
        self.assertFalse(hasattr(config_mgr, 'processing_times'))
        self.assertFalse(hasattr(config_mgr, 'start_timer'))
    
    def test_clean_dependencies(self):
        """Test that components have clean dependency relationships"""
        # LivenessDetection depends on components
        detector = LivenessDetection()
        
        # Components don't depend on each other
        self.assertFalse(hasattr(detector.blink_detector, 'performance_tracker'))
        self.assertFalse(hasattr(detector.performance_tracker, 'config_manager'))
        self.assertFalse(hasattr(detector.config_manager, 'blink_detector'))
        
        # Each component is focused and independent
        self.assertEqual(len([m for m in dir(detector.blink_detector) if not m.startswith('_')]), 4)
        self.assertEqual(len([m for m in dir(detector.performance_tracker) if not m.startswith('_')]), 7)
        self.assertEqual(len([m for m in dir(detector.config_manager) if not m.startswith('_')]), 4)


if __name__ == '__main__':
    unittest.main()
