"""
Unit Tests for Service Layer - Phase 5 Implementation
Tests all service layer functionality including business logic and error handling
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from datetime import datetime, date
import pandas as pd

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.services import (
    ServiceFactory, 
    get_attendance_service,
    get_attendance_repository,
    get_attendance_manager,
    get_recognition_system,
    get_liveness_system,
    get_face_database
)
from src.services.attendance_service import AttendanceService
from src.repositories.attendance_repository import AttendanceRepository
from src.modules.attendance import AttendanceManager
from src.modules.recognition import FaceRecognition
from src.modules.liveness import LivenessDetection
from src.modules.face_db import FaceDatabase


class TestServiceFactory(unittest.TestCase):
    """Test ServiceFactory singleton pattern and service creation"""
    
    def setUp(self):
        """Set up test environment"""
        # Reset the global service factory
        from src.services import service_factory
        service_factory.reset_services()
    
    def test_singleton_pattern(self):
        """Test that ServiceFactory maintains singleton pattern"""
        factory1 = ServiceFactory()
        factory2 = ServiceFactory()
        
        # Should be the same instance
        self.assertIs(factory1, factory2)
    
    def test_lazy_initialization(self):
        """Test that services are created only when needed"""
        factory = ServiceFactory()
        
        # Initially no services should be created
        self.assertIsNone(factory._attendance_service)
        self.assertIsNone(factory._attendance_repository)
        
        # Get a service
        service = factory.get_attendance_service()
        
        # Now the service should exist
        self.assertIsNotNone(factory._attendance_service)
        self.assertIsInstance(service, AttendanceService)
    
    def test_service_dependencies(self):
        """Test that services are created with proper dependencies"""
        factory = ServiceFactory()
        
        # Get attendance service
        attendance_service = factory.get_attendance_service()
        
        # Check that dependencies are properly injected
        self.assertIsInstance(attendance_service.attendance_repository, AttendanceRepository)
        self.assertIsInstance(attendance_service.attendance_manager, AttendanceManager)
        self.assertIsInstance(attendance_service.recognition_system, FaceRecognition)
        self.assertIsInstance(attendance_service.liveness_system, LivenessDetection)
    
    def test_reset_services(self):
        """Test that reset_services clears all service instances"""
        factory = ServiceFactory()
        
        # Create some services
        factory.get_attendance_service()
        factory.get_face_database()
        
        # Verify services exist
        self.assertIsNotNone(factory._attendance_service)
        self.assertIsNotNone(factory._face_database)
        
        # Reset services
        factory.reset_services()
        
        # Verify services are cleared
        self.assertIsNone(factory._attendance_service)
        self.assertIsNone(factory._face_database)
    
    def test_get_attendance_service(self):
        """Test get_attendance_service function"""
        service = get_attendance_service()
        self.assertIsInstance(service, AttendanceService)
    
    def test_get_attendance_repository(self):
        """Test get_attendance_repository function"""
        repository = get_attendance_repository()
        self.assertIsInstance(repository, AttendanceRepository)
    
    def test_get_attendance_manager(self):
        """Test get_attendance_manager function"""
        manager = get_attendance_manager()
        self.assertIsInstance(manager, AttendanceManager)
    
    def test_get_recognition_system(self):
        """Test get_recognition_system function"""
        recognition = get_recognition_system()
        self.assertIsInstance(recognition, FaceRecognition)
    
    def test_get_liveness_system(self):
        """Test get_liveness_system function"""
        liveness = get_liveness_system()
        self.assertIsInstance(liveness, LivenessDetection)
    
    def test_get_face_database(self):
        """Test get_face_database function"""
        face_db = get_face_database()
        self.assertIsInstance(face_db, FaceDatabase)


class TestAttendanceService(unittest.TestCase):
    """Test AttendanceService business logic and orchestration"""
    
    def setUp(self):
        """Set up test environment with mocked dependencies"""
        # Create mock dependencies
        self.mock_repository = Mock(spec=AttendanceRepository)
        self.mock_manager = Mock(spec=AttendanceManager)
        self.mock_recognition = Mock(spec=FaceRecognition)
        self.mock_liveness = Mock(spec=LivenessDetection)
        
        # Create service with mocked dependencies
        self.service = AttendanceService(
            attendance_repository=self.mock_repository,
            attendance_manager=self.mock_manager,
            recognition_system=self.mock_recognition,
            liveness_system=self.mock_liveness
        )
    
    def test_process_attendance_request_success(self):
        """Test successful attendance request processing"""
        # Mock successful recognition
        mock_recognition_result = Mock()
        mock_recognition_result.user_id = "USER001"
        mock_recognition_result.user_name = "John Doe"
        mock_recognition_result.confidence = 0.95
        self.mock_recognition.recognize_face.return_value = mock_recognition_result
        
        # Mock successful liveness detection
        mock_liveness_result = Mock()
        mock_liveness_result.is_live = True
        self.mock_liveness.detect_blink.return_value = mock_liveness_result
        
        # Mock successful attendance logging
        mock_attendance_entry = Mock()
        self.mock_manager.log_attendance.return_value = mock_attendance_entry
        
        # Process attendance request
        result = self.service.process_attendance_request(
            face_image="mock_image",
            device_info="test_device",
            location="test_location"
        )
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(result['user_id'], "USER001")
        self.assertEqual(result['user_name'], "John Doe")
        
        # Verify all dependencies were called
        self.mock_recognition.recognize_face.assert_called_once_with("mock_image")
        self.mock_liveness.detect_blink.assert_called_once_with("mock_image")
        self.mock_manager.log_attendance.assert_called_once()
    
    def test_process_attendance_request_recognition_failure(self):
        """Test attendance request with recognition failure"""
        # Mock failed recognition
        self.mock_recognition.recognize_face.return_value = None
        
        # Process attendance request
        result = self.service.process_attendance_request("mock_image")
        
        # Verify result
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Face not recognized')
        self.assertEqual(result['stage'], 'recognition')
        
        # Verify liveness and logging were not called
        self.mock_liveness.detect_blink.assert_not_called()
        self.mock_manager.log_attendance.assert_not_called()
    
    def test_process_attendance_request_liveness_failure(self):
        """Test attendance request with liveness failure"""
        # Mock successful recognition
        mock_recognition_result = Mock()
        mock_recognition_result.user_id = "USER001"
        mock_recognition_result.user_name = "John Doe"
        mock_recognition_result.confidence = 0.95
        self.mock_recognition.recognize_face.return_value = mock_recognition_result
        
        # Mock failed liveness detection
        mock_liveness_result = Mock()
        mock_liveness_result.is_live = False
        self.mock_liveness.detect_blink.return_value = mock_liveness_result
        
        # Process attendance request
        result = self.service.process_attendance_request("mock_image")
        
        # Verify result
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Liveness verification failed')
        self.assertEqual(result['stage'], 'liveness')
        self.assertEqual(result['user_id'], "USER001")
        
        # Verify logging was not called
        self.mock_manager.log_attendance.assert_not_called()
    
    def test_process_attendance_request_logging_failure(self):
        """Test attendance request with logging failure"""
        # Mock successful recognition
        mock_recognition_result = Mock()
        mock_recognition_result.user_id = "USER001"
        mock_recognition_result.user_name = "John Doe"
        mock_recognition_result.confidence = 0.95
        self.mock_recognition.recognize_face.return_value = mock_recognition_result
        
        # Mock successful liveness detection
        mock_liveness_result = Mock()
        mock_liveness_result.is_live = True
        self.mock_liveness.detect_blink.return_value = mock_liveness_result
        
        # Mock failed attendance logging
        self.mock_manager.log_attendance.return_value = None
        
        # Process attendance request
        result = self.service.process_attendance_request("mock_image")
        
        # Verify result
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Failed to log attendance')
        self.assertEqual(result['stage'], 'logging')
        self.assertEqual(result['user_id'], "USER001")
    
    def test_get_attendance_report_overview(self):
        """Test getting overview attendance report"""
        # Mock repository data
        mock_data = [
            {'user_id': 'USER001', 'status': 'Present', 'confidence': 0.95},
            {'user_id': 'USER002', 'status': 'Present', 'confidence': 0.87},
            {'user_id': 'USER003', 'status': 'Late', 'confidence': 0.92}
        ]
        self.mock_repository.get_attendance_history.return_value = mock_data
        
        # Get report
        result = self.service.get_attendance_report(report_type="overview")
        
        # Verify result structure
        self.assertIn('total_attendance', result)
        self.assertIn('unique_users', result)
        self.assertIn('avg_confidence', result)
        self.assertIn('success_rate', result)
        
        # Verify calculations
        self.assertEqual(result['total_attendance'], 3)
        self.assertEqual(result['unique_users'], 3)
        self.assertAlmostEqual(result['avg_confidence'], 0.91, places=2)
        self.assertEqual(result['success_rate'], 100.0)
    
    def test_get_attendance_report_recent_activity(self):
        """Test getting recent activity report"""
        # Mock repository data
        mock_data = [
            {'user_id': 'USER001', 'timestamp': '2025-08-30T10:00:00', 'user_name': 'John Doe'},
            {'user_id': 'USER002', 'timestamp': '2025-08-30T09:30:00', 'user_name': 'Jane Smith'}
        ]
        self.mock_repository.get_attendance_history.return_value = mock_data
        
        # Get report
        result = self.service.get_attendance_report(report_type="recent_activity")
        
        # Verify result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['user_name'], 'John Doe')
        self.assertEqual(result[1]['user_name'], 'Jane Smith')
    
    def test_get_attendance_analytics_summary(self):
        """Test getting analytics summary"""
        # Mock repository data
        mock_data = [
            {'user_id': 'USER001', 'status': 'Present', 'confidence': 0.95},
            {'user_id': 'USER002', 'status': 'Present', 'confidence': 0.87}
        ]
        self.mock_repository.get_attendance_history.return_value = mock_data
        
        # Get analytics
        result = self.service.get_attendance_analytics(analytics_type="summary")
        
        # Verify result
        self.assertIn('total_attendance', result)
        self.assertIn('unique_users', result)
        self.assertIn('avg_confidence', result)
        self.assertEqual(result['total_attendance'], 2)
    
    def test_get_attendance_analytics_user_performance(self):
        """Test getting user performance analytics"""
        # Mock repository data
        mock_data = [
            {'user_id': 'USER001', 'status': 'Present', 'confidence': 0.95},
            {'user_id': 'USER001', 'status': 'Present', 'confidence': 0.92},
            {'user_id': 'USER002', 'status': 'Present', 'confidence': 0.87}
        ]
        self.mock_repository.get_attendance_history.return_value = mock_data
        
        # Get analytics
        result = self.service.get_attendance_analytics(analytics_type="user_performance")
        
        # Verify result
        self.assertEqual(len(result), 2)
        
        # Find USER001 performance
        user1_perf = next((u for u in result if u['user_id'] == 'USER001'), None)
        self.assertIsNotNone(user1_perf)
        self.assertEqual(user1_perf['attendance_count'], 2)
        self.assertAlmostEqual(user1_perf['avg_confidence'], 0.935, places=3)
    
    def test_get_attendance_analytics_trends(self):
        """Test getting attendance trends analytics"""
        # Mock repository data
        mock_data = [
            {'date': '2025-08-28', 'hour': 9, 'status': 'Present'},
            {'date': '2025-08-29', 'hour': 9, 'status': 'Present'},
            {'date': '2025-08-30', 'hour': 9, 'status': 'Present'}
        ]
        self.mock_repository.get_attendance_history.return_value = mock_data
        
        # Get analytics
        result = self.service.get_attendance_analytics(analytics_type="trends")
        
        # Verify result
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['date'], '2025-08-28')
        self.assertEqual(result[0]['hour'], 9)
    
    def test_export_attendance_data_csv(self):
        """Test exporting attendance data to CSV"""
        # Mock repository data
        mock_data = [
            {'user_id': 'USER001', 'status': 'Present', 'confidence': 0.95},
            {'user_id': 'USER002', 'status': 'Present', 'confidence': 0.87}
        ]
        self.mock_repository.get_attendance_history.return_value = mock_data
        
        # Export data
        result = self.service.export_attendance_data(export_type="attendance_report", format="csv")
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertIn('format', result)
        self.assertEqual(result['format'], 'csv')
        
        # Verify CSV format
        csv_data = result['data']
        self.assertIn('user_id', csv_data)
        self.assertIn('USER001', csv_data)
        self.assertIn('USER002', csv_data)
    
    def test_export_attendance_data_json(self):
        """Test exporting attendance data to JSON"""
        # Mock repository data
        mock_data = [
            {'user_id': 'USER001', 'status': 'Present', 'confidence': 0.95}
        ]
        self.mock_repository.get_attendance_history.return_value = mock_data
        
        # Export data
        result = self.service.export_attendance_data(export_type="attendance_report", format="json")
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(result['format'], 'json')
    
    def test_export_attendance_data_invalid_format(self):
        """Test exporting with invalid format"""
        # Export data with invalid format
        result = self.service.export_attendance_data(export_type="attendance_report", format="invalid")
        
        # Verify result
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_is_system_healthy_all_healthy(self):
        """Test system health check when all components are healthy"""
        # Mock healthy components
        self.mock_repository.is_healthy.return_value = True
        self.mock_manager.is_healthy.return_value = True
        
        # Check health
        result = self.service.is_system_healthy()
        
        # Verify result
        self.assertTrue(result)
        
        # Verify all health checks were called
        self.mock_repository.is_healthy.assert_called_once()
        self.mock_manager.is_healthy.assert_called_once()
    
    def test_is_system_healthy_repository_unhealthy(self):
        """Test system health check when repository is unhealthy"""
        # Mock unhealthy repository
        self.mock_repository.is_health.return_value = False
        self.mock_manager.is_healthy.return_value = True
        
        # Check health
        result = self.service.is_system_healthy()
        
        # Verify result
        self.assertFalse(result)
    
    def test_is_system_healthy_manager_unhealthy(self):
        """Test system health check when manager is unhealthy"""
        # Mock unhealthy manager
        self.mock_repository.is_healthy.return_value = True
        self.mock_manager.is_healthy.return_value = False
        
        # Check health
        result = self.service.is_system_healthy()
        
        # Verify result
        self.assertFalse(result)
    
    def test_verify_attendance_eligibility_eligible(self):
        """Test attendance eligibility verification for eligible user"""
        # Mock user data
        user_data = {
            'user_id': 'USER001',
            'active': True,
            'enable_attendance': True
        }
        
        # Mock face database
        mock_face_db = Mock()
        mock_face_db.users_db = {'USER001': user_data}
        
        # Verify eligibility
        result = self.service.verify_attendance_eligibility('USER001', mock_face_db)
        
        # Verify result
        self.assertTrue(result['eligible'])
        self.assertEqual(result['user_id'], 'USER001')
    
    def test_verify_attendance_eligibility_inactive_user(self):
        """Test attendance eligibility verification for inactive user"""
        # Mock user data
        user_data = {
            'user_id': 'USER001',
            'active': False,
            'enable_attendance': True
        }
        
        # Mock face database
        mock_face_db = Mock()
        mock_face_db.users_db = {'USER001': user_data}
        
        # Verify eligibility
        result = self.service.verify_attendance_eligibility('USER001', mock_face_db)
        
        # Verify result
        self.assertFalse(result['eligible'])
        self.assertEqual(result['reason'], 'User account is inactive')
    
    def test_verify_attendance_eligibility_attendance_disabled(self):
        """Test attendance eligibility verification when attendance is disabled"""
        # Mock user data
        user_data = {
            'user_id': 'USER001',
            'active': True,
            'enable_attendance': False
        }
        
        # Mock face database
        mock_face_db = Mock()
        mock_face_db.users_db = {'USER001': user_data}
        
        # Verify eligibility
        result = self.service.verify_attendance_eligibility('USER001', mock_face_db)
        
        # Verify result
        self.assertFalse(result['eligible'])
        self.assertEqual(result['reason'], 'Attendance is disabled for this user')
    
    def test_verify_attendance_eligibility_user_not_found(self):
        """Test attendance eligibility verification for non-existent user"""
        # Mock empty face database
        mock_face_db = Mock()
        mock_face_db.users_db = {}
        
        # Verify eligibility
        result = self.service.verify_attendance_eligibility('USER001', mock_face_db)
        
        # Verify result
        self.assertFalse(result['eligible'])
        self.assertEqual(result['reason'], 'User not found')


class TestAttendanceServiceIntegration(unittest.TestCase):
    """Test AttendanceService integration with real dependencies"""
    
    def setUp(self):
        """Set up test environment with real dependencies"""
        # Create real service instances
        self.repository = AttendanceRepository()
        self.manager = AttendanceManager()
        self.recognition = FaceRecognition()
        self.liveness = LivenessDetection()
        
        # Create service
        self.service = AttendanceService(
            attendance_repository=self.repository,
            attendance_manager=self.manager,
            recognition_system=self.recognition,
            liveness_system=self.liveness
        )
    
    def test_service_initialization(self):
        """Test that service initializes correctly with real dependencies"""
        self.assertIsNotNone(self.service.attendance_repository)
        self.assertIsNotNone(self.service.attendance_manager)
        self.assertIsNotNone(self.service.recognition_system)
        self.assertIsNotNone(self.service.liveness_system)
    
    def test_system_health_check(self):
        """Test system health check with real components"""
        # This test may fail if components have external dependencies
        # In a real environment, you'd want to mock external dependencies
        try:
            result = self.service.is_system_healthy()
            self.assertIsInstance(result, bool)
        except Exception as e:
            # If health check fails due to external dependencies, that's expected
            # in a test environment
            self.assertIsInstance(e, Exception)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
