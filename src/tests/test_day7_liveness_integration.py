"""
Test Suite for Day 7: Liveness Integration
Tests the integrated liveness detection and face recognition system

This test suite covers:
- Multi-stage verification pipeline
- Session management and validation
- Performance metrics and statistics
- Configuration updates and error handling
- Real-time verification scenarios
"""

import unittest
import sys
import os
import time
import numpy as np
import cv2
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from modules.liveness_integration import LivenessIntegration, VerificationResult
from modules.face_db import FaceDatabase

class TestLivenessIntegration(unittest.TestCase):
    """Test cases for the Liveness Integration system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        print("\n🧪 Setting up Day 7 Liveness Integration Test Environment...")
        
        # Create test data directory
        cls.test_data_dir = Path("data/test_db")
        cls.test_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a test face database
        cls.face_db = FaceDatabase(str(cls.test_data_dir))
        
        # Create a test image for verification
        cls.test_image = cls._create_test_image()
        
        print("✅ Test environment setup complete")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        print("\n🧹 Cleaning up test environment...")
        
        # Remove test data
        import shutil
        if cls.test_data_dir.exists():
            shutil.rmtree(cls.test_data_dir)
        
        print("✅ Test environment cleanup complete")
    
    @classmethod
    def _create_test_image(cls):
        """Create a test image for verification"""
        # Create a simple test image (640x480, grayscale)
        image = np.ones((480, 640, 3), dtype=np.uint8) * 128
        
        # Add some features to make it more realistic
        # Add a face-like region
        cv2.rectangle(image, (200, 100), (440, 380), (255, 255, 255), -1)
        
        # Add eyes
        cv2.circle(image, (280, 200), 20, (0, 0, 0), -1)
        cv2.circle(image, (360, 200), 20, (0, 0, 0), -1)
        
        # Add nose
        cv2.circle(image, (320, 250), 15, (0, 0, 0), -1)
        
        # Add mouth
        cv2.ellipse(image, (320, 320), (40, 20), 0, 0, 180, (0, 0, 0), -1)
        
        return image
    
    def setUp(self):
        """Set up each test case"""
        self.liveness_integration = LivenessIntegration(
            confidence_threshold=0.5,
            liveness_timeout=5.0,
            max_retry_attempts=2,
            enable_debug=True
        )
    
    def tearDown(self):
        """Clean up after each test case"""
        if hasattr(self, 'liveness_integration'):
            self.liveness_integration.reset_verification_stats()
    
    def test_01_initialization(self):
        """Test system initialization"""
        print("\n🔧 Testing system initialization...")
        
        # Check if system initialized correctly
        self.assertIsNotNone(self.liveness_integration.face_recognition)
        self.assertIsNotNone(self.liveness_integration.liveness_detection)
        
        # Check default configuration
        self.assertEqual(self.liveness_integration.confidence_threshold, 0.5)
        self.assertEqual(self.liveness_integration.liveness_timeout, 5.0)
        self.assertEqual(self.liveness_integration.max_retry_attempts, 2)
        self.assertTrue(self.liveness_integration.enable_debug)
        
        print("✅ Initialization test passed")
    
    def test_02_session_management(self):
        """Test verification session management"""
        print("\n🔄 Testing session management...")
        
        # Start a new session
        session_id = self.liveness_integration.start_verification_session()
        self.assertIsNotNone(session_id)
        self.assertIsNotNone(self.liveness_integration.verification_session)
        
        # Check session properties
        session = self.liveness_integration.verification_session
        self.assertEqual(session['id'], session_id)
        self.assertEqual(session['attempts'], 0)
        self.assertFalse(session['face_recognized'])
        self.assertFalse(session['liveness_verified'])
        self.assertFalse(session['blink_detected'])
        
        # Start another session (should replace the first)
        new_session_id = self.liveness_integration.start_verification_session()
        self.assertNotEqual(session_id, new_session_id)
        
        print("✅ Session management test passed")
    
    def test_03_session_validation(self):
        """Test session validation logic"""
        print("\n✅ Testing session validation...")
        
        # Start a session
        session_id = self.liveness_integration.start_verification_session()
        
        # Valid session should pass validation
        self.assertTrue(self.liveness_integration._validate_session(session_id))
        
        # Invalid session ID should fail
        self.assertFalse(self.liveness_integration._validate_session("invalid_session"))
        
        # Test expired session (manually set start time to past)
        self.liveness_integration.verification_session['start_time'] = time.time() - 10.0
        self.assertFalse(self.liveness_integration._validate_session(session_id))
        
        # Reset for next test
        self.liveness_integration.start_verification_session()
        
        print("✅ Session validation test passed")
    
    def test_04_configuration_updates(self):
        """Test configuration update functionality"""
        print("\n⚙️ Testing configuration updates...")
        
        # Test updating confidence threshold
        config = {'confidence_threshold': 0.7}
        success = self.liveness_integration.update_config(config)
        self.assertTrue(success)
        self.assertEqual(self.liveness_integration.confidence_threshold, 0.7)
        
        # Test updating multiple parameters
        config = {
            'liveness_timeout': 8.0,
            'max_retry_attempts': 5,
            'enable_debug': False
        }
        success = self.liveness_integration.update_config(config)
        self.assertTrue(success)
        self.assertEqual(self.liveness_integration.liveness_timeout, 8.0)
        self.assertEqual(self.liveness_integration.max_retry_attempts, 5)
        self.assertFalse(self.liveness_integration.enable_debug)
        
        print("✅ Configuration updates test passed")
    
    def test_05_verification_pipeline_stages(self):
        """Test the multi-stage verification pipeline"""
        print("\n🔍 Testing verification pipeline stages...")
        
        # Start verification session
        session_id = self.liveness_integration.start_verification_session()
        
        # Test verification with test image
        result = self.liveness_integration.verify_user_live(self.test_image, session_id)
        
        # Check result structure
        self.assertIsInstance(result, VerificationResult)
        self.assertIsInstance(result.success, bool)
        self.assertIsInstance(result.verification_stage, str)
        self.assertIsInstance(result.processing_time_ms, float)
        
        # Check that processing time is reasonable
        self.assertGreater(result.processing_time_ms, 0)
        self.assertLess(result.processing_time_ms, 10000)  # Should be under 10 seconds
        
        print("✅ Verification pipeline stages test passed")
    
    def test_06_verification_statistics(self):
        """Test verification statistics tracking"""
        print("\n📊 Testing verification statistics...")
        
        # Initial stats should be zero
        stats = self.liveness_integration.get_verification_stats()
        self.assertEqual(stats['total_verifications'], 0)
        self.assertEqual(stats['successful_verifications'], 0)
        self.assertEqual(stats['success_rate'], 0)
        self.assertEqual(stats['avg_processing_time_ms'], 0.0)
        
        # Perform a verification
        session_id = self.liveness_integration.start_verification_session()
        result = self.liveness_integration.verify_user_live(self.test_image, session_id)
        
        # Check that stats were updated
        stats = self.liveness_integration.get_verification_stats()
        self.assertEqual(stats['total_verifications'], 1)
        self.assertGreaterEqual(stats['avg_processing_time_ms'], 0)
        
        print("✅ Verification statistics test passed")
    
    def test_07_error_handling(self):
        """Test error handling and edge cases"""
        print("\n⚠️ Testing error handling...")
        
        # Test with None frame
        with self.assertRaises(Exception):
            self.liveness_integration.verify_user_live(None)
        
        # Test with invalid frame
        invalid_frame = np.array([])
        with self.assertRaises(Exception):
            self.liveness_integration.verify_user_live(invalid_frame)
        
        # Test with expired session
        session_id = self.liveness_integration.start_verification_session()
        self.liveness_integration.verification_session['start_time'] = time.time() - 10.0
        
        result = self.liveness_integration.verify_user_live(self.test_image, session_id)
        self.assertFalse(result.success)
        self.assertEqual(result.verification_stage, "session_error")
        
        print("✅ Error handling test passed")
    
    def test_08_performance_optimization(self):
        """Test performance optimization features"""
        print("\n⚡ Testing performance optimization...")
        
        # Test multiple verifications to check performance
        start_time = time.time()
        
        for i in range(3):
            session_id = self.liveness_integration.start_verification_session()
            result = self.liveness_integration.verify_user_live(self.test_image, session_id)
            self.assertIsInstance(result, VerificationResult)
        
        total_time = time.time() - start_time
        
        # Check that average processing time is reasonable
        stats = self.liveness_integration.get_verification_stats()
        self.assertGreater(stats['total_verifications'], 0)
        self.assertGreater(stats['avg_processing_time_ms'], 0)
        
        # Total time should be reasonable (under 30 seconds for 3 verifications)
        self.assertLess(total_time, 30.0)
        
        print("✅ Performance optimization test passed")
    
    def test_09_retry_logic(self):
        """Test retry logic and fallback mechanisms"""
        print("\n🔄 Testing retry logic...")
        
        # Start session
        session_id = self.liveness_integration.start_verification_session()
        
        # Manually increment attempts to test retry limits
        self.liveness_integration.verification_session['attempts'] = 2
        
        # Should fail due to max attempts exceeded
        result = self.liveness_integration.verify_user_live(self.test_image, session_id)
        self.assertFalse(result.success)
        
        # Start new session and test normal operation
        new_session_id = self.liveness_integration.start_verification_session()
        result = self.liveness_integration.verify_user_live(self.test_image, new_session_id)
        self.assertIsInstance(result, VerificationResult)
        
        print("✅ Retry logic test passed")
    
    def test_10_integration_compatibility(self):
        """Test compatibility with existing modules"""
        print("\n🔗 Testing integration compatibility...")
        
        # Test that face recognition module is accessible
        self.assertIsNotNone(self.liveness_integration.face_recognition)
        self.assertTrue(hasattr(self.liveness_integration.face_recognition, 'recognize_user'))
        
        # Test that liveness detection module is accessible
        self.assertIsNotNone(self.liveness_integration.liveness_detection)
        self.assertTrue(hasattr(self.liveness_integration.liveness_detection, 'detect_blink'))
        
        # Test that both modules can be configured
        self.liveness_integration.face_recognition.confidence_threshold = 0.8
        self.assertEqual(self.liveness_integration.face_recognition.confidence_threshold, 0.8)
        
        print("✅ Integration compatibility test passed")

def run_day7_tests():
    """Run all Day 7 tests"""
    print("\n" + "="*60)
    print("🧪 DAY 7: LIVENESS INTEGRATION TEST SUITE")
    print("="*60)
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestLivenessIntegration)
    
    # Run tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_result = test_runner.run(test_suite)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 DAY 7 TEST RESULTS SUMMARY")
    print("="*60)
    print(f"Tests Run: {test_result.testsRun}")
    print(f"Failures: {len(test_result.failures)}")
    print(f"Errors: {len(test_result.errors)}")
    
    if test_result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in test_result.failures:
            print(f"  - {test}: {traceback}")
    
    if test_result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in test_result.errors:
            print(f"  - {test}: {traceback}")
    
    if test_result.wasSuccessful():
        print("\n🎉 ALL DAY 7 TESTS PASSED!")
        print("✅ Liveness Integration System is working correctly")
    else:
        print("\n⚠️ Some tests failed. Please check the implementation.")
    
    return test_result.wasSuccessful()

if __name__ == "__main__":
    # Run tests
    success = run_day7_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
