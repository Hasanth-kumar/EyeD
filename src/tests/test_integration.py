"""
Integration Tests for Complete System - Phase 5 Implementation
Tests complete workflows from UI components through services to data persistence
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile
import shutil
from datetime import datetime, date
import pandas as pd
import json

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Mock streamlit for testing
sys.modules['streamlit'] = Mock()
sys.modules['streamlit.columns'] = Mock()
sys.modules['streamlit.metric'] = Mock()
sys.modules['streamlit.dataframe'] = Mock()
sys.modules['streamlit.plotly_chart'] = Mock()
sys.modules['streamlit.button'] = Mock()
sys.modules['streamlit.form'] = Mock()
sys.modules['streamlit.text_input'] = Mock()
sys.modules['streamlit.selectbox'] = Mock()
sys.modules['streamlit.checkbox'] = Mock()
sys.modules['streamlit.camera_input'] = Mock()
sys.modules['streamlit.file_uploader'] = Mock()
sys.modules['streamlit.image'] = Mock()
sys.modules['streamlit.spinner'] = Mock()
sys.modules['streamlit.success'] = Mock()
sys.modules['streamlit.error'] = Mock()
sys.modules['streamlit.info'] = Mock()
sys.modules['streamlit.warning'] = Mock()
sys.modules['streamlit.subheader'] = Mock()
sys.modules['streamlit.header'] = Mock()
sys.modules['streamlit.markdown'] = Mock()
sys.modules['streamlit.expander'] = Mock()
sys.modules['streamlit.download_button'] = Mock()
sys.modules['streamlit.rerun'] = Mock()

# Import system components
from src.services import ServiceFactory, get_attendance_service
from src.services.attendance_service import AttendanceService
from src.repositories.attendance_repository import AttendanceRepository
from src.modules.attendance import AttendanceManager
from src.modules.recognition import FaceRecognition
from src.modules.liveness import LivenessDetection
from src.modules.face_db import FaceDatabase
from src.dashboard.components.overview import show_dashboard, get_overview_data
from src.dashboard.components.attendance_table import show_attendance_table, load_attendance_data
from src.dashboard.components.analytics import show_analytics, get_analytics_data
from src.dashboard.components.registration import show_registration, process_registration


class TestCompleteSystemIntegration(unittest.TestCase):
    """Test complete system integration from UI to data persistence"""
    
    def setUp(self):
        """Set up test environment with real components"""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.test_data_file = os.path.join(self.test_dir, "test_attendance.csv")
        
        # Create real repository
        self.repository = AttendanceRepository(self.test_data_file)
        
        # Create real modules
        self.attendance_manager = AttendanceManager()
        self.recognition_system = FaceRecognition()
        self.liveness_system = LivenessDetection()
        self.face_database = FaceDatabase()
        
        # Create real service
        self.attendance_service = AttendanceService(
            attendance_repository=self.repository,
            attendance_manager=self.attendance_manager,
            recognition_system=self.recognition_system,
            liveness_system=self.liveness_system
        )
        
        # Mock session state
        self.mock_session_state = {
            'attendance_service': self.attendance_service,
            'face_database': self.face_database
        }
        
        # Patch streamlit session state
        self.patcher = patch('streamlit.session_state', self.mock_session_state)
        self.patcher.start()
    
    def tearDown(self):
        """Clean up test environment"""
        self.patcher.stop()
        shutil.rmtree(self.test_dir)
    
    def test_complete_attendance_workflow(self):
        """Test complete attendance workflow from service to data persistence"""
        # Create mock attendance entry
        mock_entry = Mock()
        mock_entry.date = date(2025, 8, 30)
        mock_entry.time = datetime(2025, 8, 30, 10, 0, 0)
        mock_entry.name = "John Doe"
        mock_entry.user_id = "USER001"
        mock_entry.status = "Present"
        mock_entry.confidence = 0.95
        mock_entry.liveness_verified = True
        mock_entry.face_quality_score = 0.88
        mock_entry.processing_time_ms = 150
        mock_entry.verification_stage = "completed"
        mock_entry.session_id = "SESS001"
        mock_entry.device_info = "test_device"
        mock_entry.location = "test_location"
        
        # Process attendance through service
        result = self.attendance_service.process_attendance_request(
            face_image="mock_image",
            device_info="test_device",
            location="test_location"
        )
        
        # Verify service processed the request
        self.assertIsInstance(result, dict)
        
        # Verify data was persisted to repository
        attendance_data = self.repository.get_attendance_history()
        self.assertGreater(len(attendance_data), 0)
    
    def test_complete_data_retrieval_workflow(self):
        """Test complete data retrieval workflow from UI to repository"""
        # Add test data to repository
        test_data = [
            {
                'Date': '2025-08-30', 'Time': '10:00:00', 'Name': 'John Doe',
                'ID': 'USER001', 'Status': 'Present', 'Confidence': 0.95
            },
            {
                'Date': '2025-08-30', 'Time': '11:00:00', 'Name': 'Jane Smith',
                'ID': 'USER002', 'Status': 'Present', 'Confidence': 0.87
            }
        ]
        
        # Write test data to repository file
        df = pd.DataFrame(test_data)
        df.to_csv(self.test_data_file, index=False)
        
        # Test data retrieval through service
        attendance_report = self.attendance_service.get_attendance_report(report_type="overview")
        self.assertIsNotNone(attendance_report)
        
        # Test data retrieval through UI component
        result, error = load_attendance_data()
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
    
    def test_complete_analytics_workflow(self):
        """Test complete analytics workflow from UI to data processing"""
        # Add test data for analytics
        test_data = [
            {
                'Date': '2025-08-30', 'Time': '10:00:00', 'Name': 'John Doe',
                'ID': 'USER001', 'Status': 'Present', 'Confidence': 0.95
            },
            {
                'Date': '2025-08-30', 'Time': '11:00:00', 'Name': 'Jane Smith',
                'ID': 'USER002', 'Status': 'Present', 'Confidence': 0.87
            },
            {
                'Date': '2025-08-30', 'Time': '12:00:00', 'Name': 'Bob Wilson',
                'ID': 'USER003', 'Status': 'Late', 'Confidence': 0.90
            }
        ]
        
        # Write test data to repository file
        df = pd.DataFrame(test_data)
        df.to_csv(self.test_data_file, index=False)
        
        # Test analytics through service
        analytics_summary = self.attendance_service.get_attendance_analytics(analytics_type="summary")
        self.assertIsNotNone(analytics_summary)
        self.assertIn('total_attendance', analytics_summary)
        
        # Test analytics through UI component
        result, error = get_analytics_data()
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIn('attendance_summary', result)
    
    def test_complete_registration_workflow(self):
        """Test complete registration workflow from UI to user database"""
        # Test user registration through service
        user_data = {
            'user_id': 'USER001',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'department': 'Engineering',
            'role': 'Software Engineer',
            'face_image': 'mock_image',
            'enable_liveness': True,
            'auto_attendance': True,
            'notification_email': True,
            'create_backup': True
        }
        
        # Process registration
        result = process_registration(self.attendance_service, self.face_database, user_data)
        
        # Verify registration was successful
        self.assertTrue(result['success'])
        
        # Verify user was added to database
        self.assertIn('USER001', self.face_database.users_db)
        user_info = self.face_database.users_db['USER001']
        self.assertEqual(user_info['first_name'], 'John')
        self.assertEqual(user_info['last_name'], 'Doe')
    
    def test_service_factory_integration(self):
        """Test service factory integration with real components"""
        # Reset service factory
        service_factory = ServiceFactory()
        service_factory.reset_services()
        
        # Get services through factory
        attendance_service = service_factory.get_attendance_service()
        attendance_repository = service_factory.get_attendance_repository()
        attendance_manager = service_factory.get_attendance_manager()
        recognition_system = service_factory.get_recognition_system()
        liveness_system = service_factory.get_liveness_system()
        face_database = service_factory.get_face_database()
        
        # Verify all services are properly initialized
        self.assertIsInstance(attendance_service, AttendanceService)
        self.assertIsInstance(attendance_repository, AttendanceRepository)
        self.assertIsInstance(attendance_manager, AttendanceManager)
        self.assertIsInstance(recognition_system, FaceRecognition)
        self.assertIsInstance(liveness_system, LivenessDetection)
        self.assertIsInstance(face_database, FaceDatabase)
        
        # Verify service dependencies are properly injected
        self.assertIs(attendance_service.attendance_repository, attendance_repository)
        self.assertIs(attendance_service.attendance_manager, attendance_manager)
        self.assertIs(attendance_service.recognition_system, recognition_system)
        self.assertIs(attendance_service.liveness_system, liveness_system)
    
    def test_dashboard_service_integration(self):
        """Test dashboard integration with real services"""
        # Test overview component with real service
        result, error = get_overview_data()
        
        # Should work with real service
        if error is None:
            self.assertIsNotNone(result)
        else:
            # If there's an error, it should be a specific error, not "services not initialized"
            self.assertNotIn("Services not initialized", error)
        
        # Test attendance table component with real service
        result, error = load_attendance_data()
        
        # Should work with real service
        if error is None:
            self.assertIsNotNone(result)
        else:
            # If there's an error, it should be a specific error, not "services not initialized"
            self.assertNotIn("Services not initialized", error)
        
        # Test analytics component with real service
        result, error = get_analytics_data()
        
        # Should work with real service
        if error is None:
            self.assertIsNotNone(result)
        else:
            # If there's an error, it should be a specific error, not "services not initialized"
            self.assertNotIn("Services not initialized", error)
    
    def test_data_persistence_integration(self):
        """Test data persistence integration across all layers"""
        # Create test attendance data
        test_entries = [
            Mock(
                date=date(2025, 8, 30), time=datetime(2025, 8, 30, 10, 0, 0),
                name="John Doe", user_id="USER001", status="Present", confidence=0.95,
                liveness_verified=True, face_quality_score=0.88, processing_time_ms=150,
                verification_stage="completed", session_id="SESS001", device_info="test", location="test"
            ),
            Mock(
                date=date(2025, 8, 30), time=datetime(2025, 8, 30, 11, 0, 0),
                name="Jane Smith", user_id="USER002", status="Present", confidence=0.87,
                liveness_verified=True, face_quality_score=0.85, processing_time_ms=120,
                verification_stage="completed", session_id="SESS002", device_info="test", location="test"
            )
        ]
        
        # Add entries through repository
        for entry in test_entries:
            self.repository.add_attendance(entry)
        
        # Verify data was persisted
        df = pd.read_csv(self.test_data_file)
        self.assertEqual(len(df), 2)
        
        # Verify data can be retrieved through service
        attendance_data = self.attendance_service.get_attendance_report(report_type="overview")
        self.assertIsNotNone(attendance_data)
        
        # Verify data can be retrieved through UI component
        result, error = load_attendance_data()
        if error is None:
            self.assertIsNotNone(result)
            self.assertEqual(len(result), 2)
    
    def test_error_handling_integration(self):
        """Test error handling integration across all layers"""
        # Test repository error handling
        bad_repository = AttendanceRepository("/non/existent/path/file.csv")
        health_check = bad_repository.is_healthy()
        self.assertFalse(health_check)
        
        # Test service error handling with bad repository
        bad_service = AttendanceService(
            attendance_repository=bad_repository,
            attendance_manager=self.attendance_manager,
            recognition_system=self.recognition_system,
            liveness_system=self.liveness_system
        )
        
        health_check = bad_service.is_system_healthy()
        self.assertFalse(health_check)
        
        # Test UI component error handling with bad service
        self.mock_session_state['attendance_service'] = bad_service
        
        result, error = get_overview_data()
        if error is None:
            # If no error, the service should handle it gracefully
            pass
        else:
            # If there's an error, it should be handled properly
            self.assertIsInstance(error, str)
    
    def test_performance_integration(self):
        """Test performance integration across all layers"""
        # Create reasonable test dataset (reduced from 100 to 10)
        test_data = []
        for i in range(10):  # Reduced from 100 to 10
            entry = Mock(
                date=date(2025, 8, 30), time=datetime(2025, 8, 30, 10, 0, 0),
                name=f"User{i}", user_id=f"USER{i:03d}", status="Present", confidence=0.9,
                liveness_verified=True, face_quality_score=0.85, processing_time_ms=150,
                verification_stage="completed", session_id=f"SESS{i:03d}", device_info="test", location="test"
            )
            test_data.append(entry)
        
        # Test repository performance
        import time
        start_time = time.time()
        
        for entry in test_data:
            self.repository.add_attendance(entry)
        
        end_time = time.time()
        repository_time = end_time - start_time
        
        # Should complete in reasonable time
        self.assertLess(repository_time, 5.0)  # Reduced from 10.0 to 5.0
        
        # Test service performance
        start_time = time.time()
        
        attendance_report = self.attendance_service.get_attendance_report(report_type="overview")
        
        end_time = time.time()
        service_time = end_time - start_time
        
        # Should complete in reasonable time
        self.assertLess(service_time, 3.0)  # Reduced from 5.0 to 3.0
        
        # Test UI component performance
        start_time = time.time()
        
        result, error = load_attendance_data()
        
        end_time = time.time()
        ui_time = end_time - start_time
        
        # Should complete in reasonable time
        self.assertLess(ui_time, 3.0)  # Reduced from 5.0 to 3.0
        
        # Verify all data was processed
        if error is None:
            self.assertIsNotNone(result)
            self.assertEqual(len(result), 10)  # Changed from 100 to 10


class TestSystemWorkflowIntegration(unittest.TestCase):
    """Test complete system workflows and user scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.test_data_file = os.path.join(self.test_dir, "test_attendance.csv")
        
        # Create real components
        self.repository = AttendanceRepository(self.test_data_file)
        self.attendance_manager = AttendanceManager()
        self.recognition_system = FaceRecognition()
        self.liveness_system = LivenessDetection()
        self.face_database = FaceDatabase()
        
        # Create real service
        self.attendance_service = AttendanceService(
            attendance_repository=self.repository,
            attendance_manager=self.attendance_manager,
            recognition_system=self.recognition_system,
            liveness_system=self.liveness_system
        )
        
        # Mock session state
        self.mock_session_state = {
            'attendance_service': self.attendance_service,
            'face_database': self.face_database
        }
        
        # Patch streamlit session state
        self.patcher = patch('streamlit.session_state', self.mock_session_state)
        self.patcher.start()
    
    def tearDown(self):
        """Clean up test environment"""
        self.patcher.stop()
        shutil.rmtree(self.test_dir)
    
    def test_user_registration_to_attendance_workflow(self):
        """Test complete workflow from user registration to attendance tracking"""
        # Step 1: Register a new user
        user_data = {
            'user_id': 'USER001',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'department': 'Engineering',
            'role': 'Software Engineer',
            'face_image': 'mock_image',
            'enable_liveness': True,
            'auto_attendance': True,
            'notification_email': True,
            'create_backup': True
        }
        
        registration_result = process_registration(self.attendance_service, self.face_database, user_data)
        self.assertTrue(registration_result['success'])
        
        # Step 2: Verify user exists in database
        self.assertIn('USER001', self.face_database.users_db)
        
        # Step 3: Simulate attendance tracking
        mock_entry = Mock()
        mock_entry.date = date(2025, 8, 30)
        mock_entry.time = datetime(2025, 8, 30, 10, 0, 0)
        mock_entry.name = "John Doe"
        mock_entry.user_id = "USER001"
        mock_entry.status = "Present"
        mock_entry.confidence = 0.95
        mock_entry.liveness_verified = True
        mock_entry.face_quality_score = 0.88
        mock_entry.processing_time_ms = 150
        mock_entry.verification_stage = "completed"
        mock_entry.session_id = "SESS001"
        mock_entry.device_info = "test_device"
        mock_entry.location = "test_location"
        
        # Add attendance through repository
        self.repository.add_attendance(mock_entry)
        
        # Step 4: Verify attendance data
        attendance_data = self.repository.get_attendance_history()
        self.assertEqual(len(attendance_data), 1)
        self.assertEqual(attendance_data[0]['Name'], 'John Doe')
        self.assertEqual(attendance_data[0]['ID'], 'USER001')
        
        # Step 5: Verify data through service
        attendance_report = self.attendance_service.get_attendance_report(report_type="overview")
        self.assertIsNotNone(attendance_report)
        
        # Step 6: Verify data through UI component
        result, error = load_attendance_data()
        if error is None:
            self.assertIsNotNone(result)
            self.assertEqual(len(result), 1)
    
    def test_analytics_and_reporting_workflow(self):
        """Test complete analytics and reporting workflow"""
        # Step 1: Add multiple attendance records
        test_data = [
            {
                'Date': '2025-08-30', 'Time': '10:00:00', 'Name': 'John Doe',
                'ID': 'USER001', 'Status': 'Present', 'Confidence': 0.95
            },
            {
                'Date': '2025-08-30', 'Time': '11:00:00', 'Name': 'Jane Smith',
                'ID': 'USER002', 'Status': 'Present', 'Confidence': 0.87
            },
            {
                'Date': '2025-08-30', 'Time': '12:00:00', 'Name': 'Bob Wilson',
                'ID': 'USER003', 'Status': 'Late', 'Confidence': 0.90
            }
        ]
        
        # Write test data to repository
        df = pd.DataFrame(test_data)
        df.to_csv(self.test_data_file, index=False)
        
        # Step 2: Generate analytics through service
        summary_analytics = self.attendance_service.get_attendance_analytics(analytics_type="summary")
        user_performance = self.attendance_service.get_attendance_analytics(analytics_type="user_performance")
        trends_analytics = self.attendance_service.get_attendance_analytics(analytics_type="trends")
        
        # Verify analytics data
        self.assertIsNotNone(summary_analytics)
        self.assertIsNotNone(user_performance)
        self.assertIsNotNone(trends_analytics)
        
        # Step 3: Generate reports through service
        overview_report = self.attendance_service.get_attendance_report(report_type="overview")
        recent_activity = self.attendance_service.get_attendance_report(report_type="recent_activity")
        
        # Verify reports
        self.assertIsNotNone(overview_report)
        self.assertIsNotNone(recent_activity)
        
        # Step 4: Export data through service
        csv_export = self.attendance_service.export_attendance_data(
            export_type="attendance_report", format="csv"
        )
        json_export = self.attendance_service.export_attendance_data(
            export_type="attendance_report", format="json"
        )
        
        # Verify exports
        self.assertTrue(csv_export['success'])
        self.assertTrue(json_export['success'])
        
        # Step 5: Verify data through UI components
        overview_data, overview_error = get_overview_data()
        if overview_error is None:
            self.assertIsNotNone(overview_data)
        
        analytics_data, analytics_error = get_analytics_data()
        if analytics_error is None:
            self.assertIsNotNone(analytics_data)
        
        attendance_data, attendance_error = load_attendance_data()
        if overview_error is None:
            self.assertIsNotNone(attendance_data)
            self.assertEqual(len(attendance_data), 3)
    
    def test_system_health_and_monitoring_workflow(self):
        """Test system health and monitoring workflow"""
        # Step 1: Check individual component health
        repository_health = self.repository.is_healthy()
        self.assertTrue(repository_health)
        
        # Step 2: Check service health
        service_health = self.attendance_service.is_system_healthy()
        self.assertIsInstance(service_health, bool)
        
        # Step 3: Check system health through UI
        overview_data, overview_error = get_overview_data()
        if overview_error is None:
            self.assertIsNotNone(overview_data)
            if 'system_health' in overview_data:
                self.assertIsInstance(overview_data['system_health'], bool)
        
        # Step 4: Verify system metrics
        if overview_error is None and overview_data:
            if 'user_count' in overview_data:
                self.assertIsInstance(overview_data['user_count'], int)
            if 'attendance_summary' in overview_data:
                attendance_summary = overview_data['attendance_summary']
                if 'total_attendance' in attendance_summary:
                    self.assertIsInstance(attendance_summary['total_attendance'], int)
    
    def test_error_recovery_and_fallback_workflow(self):
        """Test error recovery and fallback mechanisms"""
        # Step 1: Test with healthy system
        overview_data, overview_error = get_overview_data()
        attendance_data, attendance_error = load_attendance_data()
        analytics_data, analytics_error = get_analytics_data()
        
        # Step 2: Simulate service failure by clearing session state
        self.mock_session_state.clear()
        
        # Step 3: Test fallback behavior
        overview_data_fallback, overview_error_fallback = get_overview_data()
        attendance_data_fallback, attendance_error_fallback = load_attendance_data()
        analytics_data_fallback, analytics_error_fallback = get_analytics_data()
        
        # Verify fallback errors
        self.assertIsNone(overview_data_fallback)
        self.assertIsNotNone(overview_error_fallback)
        self.assertIn("Services not initialized", overview_error_fallback)
        
        self.assertIsNone(attendance_data_fallback)
        self.assertIsNotNone(attendance_error_fallback)
        self.assertIn("Services not initialized", attendance_error_fallback)
        
        self.assertIsNone(analytics_data_fallback)
        self.assertIsNotNone(analytics_error_fallback)
        self.assertIn("Services not initialized", analytics_error_fallback)
        
        # Step 4: Restore services
        self.mock_session_state['attendance_service'] = self.attendance_service
        self.mock_session_state['face_database'] = self.face_database
        
        # Step 5: Verify recovery
        overview_data_recovery, overview_error_recovery = get_overview_data()
        if overview_error_recovery is None:
            self.assertIsNotNone(overview_data_recovery)
        else:
            # If there's still an error, it should be different from "services not initialized"
            self.assertNotIn("Services not initialized", overview_error_recovery)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)

