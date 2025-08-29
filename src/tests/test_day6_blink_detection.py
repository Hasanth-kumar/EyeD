"""
Test Suite for Day 6: Blink Detection (MediaPipe)
Core testing of the liveness detection system

This test suite covers:
- MediaPipe initialization
- Basic blink detection logic
- Blink counter management
- Essential liveness verification
"""

import sys
import os
import numpy as np
import cv2
import unittest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.modules.liveness import LivenessDetection

class TestDay6BlinkDetection(unittest.TestCase):
    """Test suite for Day 6 Blink Detection feature"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.liveness = LivenessDetection()
        
        # Create simple test images
        self.test_image = np.ones((480, 480, 3), dtype=np.uint8) * 128
        
        # Mock eye landmarks for testing
        self.mock_eye_landmarks = [
            [0.1, 0.2, 0.0],  # p1
            [0.2, 0.3, 0.0],  # p2
            [0.3, 0.4, 0.0],  # p3
            [0.4, 0.5, 0.0],  # p4
            [0.5, 0.6, 0.0],  # p5
            [0.6, 0.7, 0.0],  # p6
        ]
    
    def test_01_mediapipe_initialization(self):
        """Test MediaPipe initialization"""
        self.assertIsNotNone(self.liveness.mp_face_mesh)
        self.assertIsNotNone(self.liveness.mp_drawing)
        self.assertIsNotNone(self.liveness.mp_drawing_styles)
        print("✅ MediaPipe Initialization: PASSED")
    
    def test_02_eye_landmark_extraction(self):
        """Test eye landmark extraction"""
        # Test landmark indices
        self.assertEqual(len(self.liveness.LEFT_EYE_INDICES), 14)
        self.assertEqual(len(self.liveness.RIGHT_EYE_INDICES), 16)
        
        # Test index validity
        left_valid = all(0 <= idx < 468 for idx in self.liveness.LEFT_EYE_INDICES)
        right_valid = all(0 <= idx < 468 for idx in self.liveness.RIGHT_EYE_INDICES)
        self.assertTrue(left_valid)
        self.assertTrue(right_valid)
        
        print("✅ Eye Landmark Extraction: PASSED")
    
    def test_03_ear_calculation(self):
        """Test EAR calculation"""
        # Test with valid landmarks
        ear = self.liveness.calculate_ear(self.mock_eye_landmarks)
        self.assertIsInstance(ear, float)
        self.assertGreaterEqual(ear, 0)
        
        # Test with insufficient landmarks
        ear_insufficient = self.liveness.calculate_ear(self.mock_eye_landmarks[:3])
        self.assertEqual(ear_insufficient, 0.0)
        
        print("✅ EAR Calculation: PASSED")
    
    def test_04_blink_detection(self):
        """Test blink detection logic"""
        self.liveness.reset_blink_counter()
        
        # Simulate eyes closed (low EAR)
        blink1 = self.liveness.detect_blink(0.1, 0.1)  # First call
        self.assertFalse(blink1)  # Should not detect on first call
        
        blink2 = self.liveness.detect_blink(0.1, 0.1)  # Second call (consecutive)
        self.assertTrue(blink2)  # Should detect on consecutive call
        
        # Simulate eyes open (high EAR)
        blink3 = self.liveness.detect_blink(0.3, 0.3)
        self.assertFalse(blink3)
        
        # Check blink counter
        self.assertEqual(self.liveness.get_blink_count(), 1)
        
        print("✅ Blink Detection Logic: PASSED")
    
    def test_05_blink_counter_management(self):
        """Test blink counter management"""
        self.liveness.reset_blink_counter()
        self.assertEqual(self.liveness.get_blink_count(), 0)
        
        # Simulate a blink
        self.liveness.detect_blink(0.1, 0.1)
        self.liveness.detect_blink(0.1, 0.1)
        
        self.assertEqual(self.liveness.get_blink_count(), 1)
        
        # Reset and verify
        self.liveness.reset_blink_counter()
        self.assertEqual(self.liveness.get_blink_count(), 0)
        
        print("✅ Blink Counter Management: PASSED")
    
    def test_06_basic_liveness_verification(self):
        """Test basic liveness verification"""
        # Test with simple image
        is_live, confidence, quality = self.liveness.verify_liveness(self.test_image)
        self.assertIsInstance(is_live, bool)
        self.assertIsInstance(confidence, float)
        self.assertIsInstance(quality, dict)
        
        print("✅ Basic Liveness Verification: PASSED")

def run_tests():
    """Run all tests and return success status"""
    print("🧪 Running Day 6 Blink Detection Test Suite...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDay6BlinkDetection)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results Summary:")
    print(f"   Total Tests: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("🎉 All tests passed successfully!")
        return True
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
