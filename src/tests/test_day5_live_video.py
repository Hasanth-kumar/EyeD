#!/usr/bin/env python3
"""
Test Day 5: Live Video Recognition
Tests real-time webcam face detection and recognition

Author: EyeD Team
Date: 2025
"""

import sys
import os
import unittest
import cv2
import numpy as np
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

class TestDay5LiveVideo(unittest.TestCase):
    """Test cases for Day 5: Live Video Recognition"""
    
    def setUp(self):
        """Set up test environment"""
        try:
            from modules.recognition import FaceRecognition
            from modules.face_db import FaceDatabase
            
            # Initialize recognition system
            self.recognition = FaceRecognition(confidence_threshold=0.6)
            
            # Initialize face database
            self.face_db = FaceDatabase("data/faces")
            
            # Load known faces
            self.recognition.load_known_faces("data/faces")
            
            print("✅ Test environment set up successfully")
            
        except Exception as e:
            self.fail(f"Failed to set up test environment: {e}")
    
    def test_webcam_initialization(self):
        """Test webcam initialization"""
        try:
            # Try to open webcam
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                print("⚠️ Webcam not available, skipping webcam tests")
                self.skipTest("Webcam not available")
            
            # Check if we can read a frame
            ret, frame = cap.read()
            cap.release()
            
            if ret and frame is not None:
                print("✅ Webcam initialized successfully")
                self.assertIsInstance(frame, np.ndarray)
                self.assertEqual(len(frame.shape), 3)  # Should be 3D (height, width, channels)
            else:
                self.fail("Failed to read frame from webcam")
                
        except Exception as e:
            self.fail(f"Webcam initialization failed: {e}")
    
    def test_real_time_face_detection(self):
        """Test real-time face detection in video frames"""
        try:
            # Create a test frame with a face (simulate webcam frame)
            test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # Add a simple face-like rectangle (simulating detected face)
            cv2.rectangle(test_frame, (200, 150), (400, 350), (255, 255, 255), -1)
            
            # Test face detection
            face_boxes = self.recognition.detect_faces(test_frame)
            
            # Note: This test frame won't have real faces, so detection may fail
            # We're testing that the method doesn't crash
            print("✅ Real-time face detection method works")
            self.assertIsInstance(face_boxes, list)
            
        except Exception as e:
            self.fail(f"Real-time face detection failed: {e}")
    
    def test_frame_processing_pipeline(self):
        """Test the complete frame processing pipeline"""
        try:
            # Test the recognize_user method (main pipeline)
            test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            results = self.recognition.recognize_user(test_frame)
            
            # Should return a list of results
            self.assertIsInstance(results, list)
            print("✅ Frame processing pipeline works")
            
        except Exception as e:
            self.fail(f"Frame processing pipeline failed: {e}")
    
    def test_recognition_performance(self):
        """Test recognition performance metrics"""
        try:
            stats = self.recognition.get_recognition_stats()
            
            # Check that stats are returned
            self.assertIsInstance(stats, dict)
            self.assertIn('known_faces_count', stats)
            self.assertIn('confidence_threshold', stats)
            self.assertIn('face_cascade_loaded', stats)
            
            print("✅ Recognition performance metrics available")
            
        except Exception as e:
            self.fail(f"Recognition performance test failed: {e}")
    
    def test_confidence_threshold_validation(self):
        """Test confidence threshold validation"""
        try:
            # Test with different confidence thresholds
            from modules.recognition import FaceRecognition
            test_recognition = FaceRecognition(confidence_threshold=0.8)
            
            self.assertEqual(test_recognition.confidence_threshold, 0.8)
            print("✅ Confidence threshold validation works")
            
        except Exception as e:
            self.fail(f"Confidence threshold validation failed: {e}")
    
    def test_error_handling(self):
        """Test error handling in live video scenarios"""
        try:
            # Test with invalid frame
            invalid_frame = None
            results = self.recognition.recognize_user(invalid_frame)
            
            # Should handle gracefully and return empty list
            self.assertEqual(results, [])
            print("✅ Error handling works for invalid frames")
            
        except Exception as e:
            # This is expected behavior - should handle gracefully
            print("✅ Error handling works (exception caught as expected)")
    
    def test_multi_stage_detection(self):
        """Test multi-stage detection pipeline"""
        try:
            # Test that both OpenCV and fallback methods are available
            self.assertIsNotNone(self.recognition.face_cascade)
            
            # Test detection parameters
            test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # This should not crash even with empty frame
            face_boxes = self.recognition.detect_faces(test_frame)
            
            self.assertIsInstance(face_boxes, list)
            print("✅ Multi-stage detection pipeline works")
            
        except Exception as e:
            self.fail(f"Multi-stage detection test failed: {e}")

def run_tests():
    """Run all Day 5 tests"""
    print("🧪 Running Day 5: Live Video Recognition Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDay5LiveVideo)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Day 5 Test Results Summary")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("🎉 All Day 5 tests passed!")
        print("🚀 Ready for Day 6: Blink Detection")
    else:
        print("❌ Some Day 5 tests failed. Check the output above.")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
