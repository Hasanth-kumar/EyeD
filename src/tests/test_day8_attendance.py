"""
Test Suite for Day 8: Attendance Logging
Tests the comprehensive attendance management system with liveness verification
"""

import sys
import os
import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import numpy as np
import cv2
from modules.attendance import AttendanceManager, AttendanceEntry, AttendanceSession
from modules.liveness_integration import LivenessIntegration
from utils.database import AttendanceDB

class TestAttendanceModule(unittest.TestCase):
    """Test cases for the attendance module"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary test directory
        self.test_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.test_dir / "data"
        self.faces_dir = self.data_dir / "faces"
        self.attendance_file = self.data_dir / "attendance.csv"
        
        # Create directory structure
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.faces_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test attendance CSV
        import pandas as pd
        test_data = pd.DataFrame({
            'Name': ['Test User'],
            'ID': ['test_001'],
            'Date': ['2025-01-01'],
            'Time': ['09:00:00'],
            'Status': ['Present'],
            'Confidence': [0.85],
            'Liveness_Verified': [True]
        })
        test_data.to_csv(self.attendance_file, index=False)
        
        # Create test faces database
        import json
        faces_db = {
            "users": {
                "test_001": {
                    "name": "Test User",
                    "image_path": str(self.faces_dir / "test_user.jpg"),
                    "registered": datetime.now().isoformat()
                }
            },
            "embeddings": {
                "test_001": [0.1] * 4096  # Mock embedding
            },
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        with open(self.faces_dir / "faces.json", 'w') as f:
            json.dump(faces_db, f, indent=2)
        
        # Mock frame for testing
        self.test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Initialize attendance manager with test paths
        self.attendance_manager = AttendanceManager(
            enable_liveness=False,  # Disable for testing
            confidence_threshold=0.6,
            max_daily_entries=3,
            enable_analytics=True,
            enable_transparency=True
        )
        
        # Override database paths for testing
        self.attendance_manager.attendance_db.attendance_file = self.attendance_file
        self.attendance_manager.attendance_db.faces_dir = self.faces_dir
        self.attendance_manager.attendance_db.faces_db_file = self.faces_dir / "faces.json"
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_attendance_manager_initialization(self):
        """Test attendance manager initialization"""
        self.assertIsNotNone(self.attendance_manager)
        self.assertEqual(self.attendance_manager.confidence_threshold, 0.6)
        self.assertEqual(self.attendance_manager.max_daily_entries, 3)
        self.assertTrue(self.attendance_manager.enable_analytics)
        self.assertTrue(self.attendance_manager.enable_transparency)
        self.assertFalse(self.attendance_manager.enable_liveness)
    
    def test_start_attendance_session(self):
        """Test starting an attendance session"""
        session_id = self.attendance_manager.start_attendance_session(
            user_id="test_001",
            user_name="Test User",
            device_info="Test Webcam",
            location="Test Office"
        )
        
        self.assertIsNotNone(session_id)
        self.assertIn(session_id, self.attendance_manager.active_sessions)
        
        session = self.attendance_manager.active_sessions[session_id]
        self.assertEqual(session.user_id, "test_001")
        self.assertEqual(session.user_name, "Test User")
        self.assertEqual(session.device_info, "Test Webcam")
        self.assertEqual(session.location, "Test Office")
        self.assertEqual(session.status, "In Progress")
        self.assertIsNone(session.end_time)
    
    def test_session_management(self):
        """Test session management functionality"""
        # Start session
        session_id = self.attendance_manager.start_attendance_session(
            user_id="test_001",
            user_name="Test User"
        )
        
        # Verify session exists
        self.assertIn(session_id, self.attendance_manager.active_sessions)
        
        # Get session before ending it
        session = self.attendance_manager.active_sessions[session_id]
        self.assertEqual(session.status, "In Progress")
        self.assertIsNone(session.end_time)
        
        # End session
        success = self.attendance_manager.end_attendance_session(session_id)
        self.assertTrue(success)
        
        # Verify session was removed from active sessions
        self.assertNotIn(session_id, self.attendance_manager.active_sessions)
    
    def test_attendance_eligibility_check(self):
        """Test attendance eligibility checking"""
        # Test with no existing entries
        can_log = self.attendance_manager._can_log_attendance("new_user")
        self.assertTrue(can_log)
        
        # Test with existing entries (should allow up to max_daily_entries)
        # First, we need to actually log some attendance entries to test the limit
        for i in range(3):  # Max daily entries
            # Create a mock attendance entry in the database
            success = self.attendance_manager.attendance_db.log_attendance(
                name=f"Test User {i}",
                user_id="test_001",
                status="Present",
                confidence=0.8,
                liveness_verified=True
            )
            self.assertTrue(success)
        
        # Now test that the 4th attempt is denied
        can_log = self.attendance_manager._can_log_attendance("test_001")
        self.assertFalse(can_log)
    
    def test_attendance_analytics(self):
        """Test attendance analytics functionality"""
        analytics = self.attendance_manager.get_attendance_analytics()
        
        self.assertNotIn('error', analytics)
        self.assertEqual(analytics['total_entries'], 1)
        self.assertEqual(analytics['unique_users'], 1)
        self.assertGreater(analytics['success_rate'], 0)
        self.assertGreater(analytics['avg_confidence'], 0)
    
    def test_transparency_report(self):
        """Test transparency report generation"""
        # Start a session first
        session_id = self.attendance_manager.start_attendance_session(
            user_id="test_001",
            user_name="Test User"
        )
        
        # Get transparency report
        report = self.attendance_manager.get_transparency_report(session_id)
        
        self.assertNotIn('error', report)
        self.assertIn('session_info', report)
        self.assertIn('verification_details', report)
        self.assertIn('quality_assessment', report)
        self.assertIn('system_metrics', report)
        
        # Verify session info
        session_info = report['session_info']
        self.assertEqual(session_info['user_id'], 'test_001')
        self.assertEqual(session_info['user_name'], 'Test User')
        self.assertEqual(session_info['status'], 'In Progress')
    
    def test_performance_statistics(self):
        """Test performance statistics tracking"""
        # Start and end a session
        session_id = self.attendance_manager.start_attendance_session(
            user_id="test_001",
            user_name="Test User"
        )
        
        # Get initial stats
        initial_stats = self.attendance_manager.get_performance_stats()
        self.assertEqual(initial_stats['total_sessions'], 1)
        self.assertEqual(initial_stats['active_sessions'], 1)
        
        # End session
        self.attendance_manager.end_attendance_session(session_id)
        
        # Get updated stats
        updated_stats = self.attendance_manager.get_performance_stats()
        self.assertEqual(updated_stats['active_sessions'], 0)
        
        # Test reset functionality
        self.attendance_manager.reset_performance_stats()
        reset_stats = self.attendance_manager.get_performance_stats()
        self.assertEqual(reset_stats['total_sessions'], 0)
        self.assertEqual(reset_stats['active_sessions'], 0)
    
    def test_configuration_updates(self):
        """Test configuration update functionality"""
        # Update confidence threshold
        success = self.attendance_manager.update_config({
            'confidence_threshold': 0.8
        })
        self.assertTrue(success)
        self.assertEqual(self.attendance_manager.confidence_threshold, 0.8)
        
        # Update max daily entries
        success = self.attendance_manager.update_config({
            'max_daily_entries': 5
        })
        self.assertTrue(success)
        self.assertEqual(self.attendance_manager.max_daily_entries, 5)
        
        # Test invalid config
        success = self.attendance_manager.update_config({
            'invalid_setting': 'value'
        })
        self.assertTrue(success)  # Should not fail for unknown settings
    
    def test_error_handling(self):
        """Test error handling in attendance module"""
        # Test with invalid session ID
        result = self.attendance_manager.process_attendance_frame(
            self.test_frame, "invalid_session_id"
        )
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Invalid session ID')
        
        # Test transparency report for non-existent session
        report = self.attendance_manager.get_transparency_report("invalid_session")
        self.assertIn('error', report)
        self.assertEqual(report['error'], 'Session not found')
    
    def test_attendance_entry_structure(self):
        """Test attendance entry data structure"""
        entry = AttendanceEntry(
            name="Test User",
            user_id="test_001",
            date="2025-01-01",
            time="09:00:00",
            status="Present",
            confidence=0.85,
            liveness_verified=True,
            face_quality_score=85.0,
            processing_time_ms=150.0,
            verification_stage="Liveness Verified",
            session_id="test_session",
            device_info="Test Webcam",
            location="Test Office"
        )
        
        self.assertEqual(entry.name, "Test User")
        self.assertEqual(entry.user_id, "test_001")
        self.assertEqual(entry.confidence, 0.85)
        self.assertTrue(entry.liveness_verified)
        self.assertEqual(entry.face_quality_score, 85.0)
        self.assertEqual(entry.processing_time_ms, 150.0)
    
    def test_attendance_session_structure(self):
        """Test attendance session data structure"""
        now = datetime.now()
        session = AttendanceSession(
            session_id="test_session",
            start_time=now,
            end_time=None,
            user_id="test_001",
            user_name="Test User",
            status="In Progress",
            confidence=0.0,
            liveness_verified=False,
            face_quality_score=0.0,
            processing_time_ms=0.0,
            verification_stage="Session Started",
            device_info="Test Webcam",
            location="Test Office"
        )
        
        self.assertEqual(session.session_id, "test_session")
        self.assertEqual(session.start_time, now)
        self.assertIsNone(session.end_time)
        self.assertEqual(session.user_id, "test_001")
        self.assertEqual(session.status, "In Progress")

def run_attendance_tests():
    """Run all attendance tests"""
    print("🧪 Running Day 8 Attendance Module Tests...")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAttendanceModule)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results Summary:")
    print(f"   Tests Run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")
    
    if result.errors:
        print(f"\n⚠️ Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")
    
    if result.wasSuccessful():
        print(f"\n✅ All {result.testsRun} tests passed!")
        return True
    else:
        print(f"\n❌ {len(result.failures) + len(result.errors)} tests failed!")
        return False

if __name__ == "__main__":
    success = run_attendance_tests()
    sys.exit(0 if success else 1)
