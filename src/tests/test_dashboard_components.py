"""
Unit Tests for Dashboard Components - Phase 5 Implementation
Tests all dashboard components and their integration with the service layer
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile
import shutil
from datetime import datetime, date
import pandas as pd
import streamlit as st

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

# Import dashboard components
from src.dashboard.components.overview import show_dashboard, get_overview_data
from src.dashboard.components.attendance_table import show_attendance_table, load_attendance_data
from src.dashboard.components.analytics import show_analytics, get_analytics_data
from src.dashboard.components.registration import show_registration, process_registration


class TestDashboardOverviewComponent(unittest.TestCase):
    """Test Overview component functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock session state
        self.mock_session_state = {
            'attendance_service': Mock(),
            'face_database': Mock()
        }
        
        # Patch streamlit session state
        self.patcher = patch('streamlit.session_state', self.mock_session_state)
        self.patcher.start()
    
    def tearDown(self):
        """Clean up test environment"""
        self.patcher.stop()
    
    def test_get_overview_data_success(self):
        """Test successful overview data retrieval"""
        # Mock service responses
        mock_attendance_service = Mock()
        mock_attendance_service.get_attendance_report.side_effect = [
            {'total_attendance': 100, 'unique_users': 25, 'avg_confidence': 0.92, 'success_rate': 95.0},  # overview
            [{'timestamp': '2025-08-30T10:00:00', 'user_name': 'John Doe'}],  # recent_activity
        ]
        mock_attendance_service.is_system_healthy.return_value = True
        
        mock_face_database = Mock()
        mock_face_database.users_db = {'USER001': {}, 'USER002': {}}
        
        # Set up session state
        self.mock_session_state['attendance_service'] = mock_attendance_service
        self.mock_session_state['face_database'] = mock_face_database
        
        # Get overview data
        result, error = get_overview_data()
        
        # Verify result
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIn('attendance_summary', result)
        self.assertIn('recent_activity', result)
        self.assertIn('system_health', result)
        self.assertIn('user_count', result)
        
        # Verify service calls
        mock_attendance_service.get_attendance_report.assert_called()
        mock_attendance_service.is_system_healthy.assert_called_once()
    
    def test_get_overview_data_service_unavailable(self):
        """Test overview data retrieval when services unavailable"""
        # Clear session state
        self.mock_session_state.clear()
        
        # Get overview data
        result, error = get_overview_data()
        
        # Verify error
        self.assertIsNone(result)
        self.assertIsNotNone(error)
        self.assertIn("Services not initialized", error)
    
    def test_get_overview_data_service_error(self):
        """Test overview data retrieval when service throws error"""
        # Mock service that throws error
        mock_attendance_service = Mock()
        mock_attendance_service.get_attendance_report.side_effect = Exception("Service error")
        
        self.mock_session_state['attendance_service'] = mock_attendance_service
        
        # Get overview data
        result, error = get_overview_data()
        
        # Verify error
        self.assertIsNone(result)
        self.assertIsNotNone(error)
        self.assertIn("Error loading overview data", error)
    
    def test_show_dashboard_calls_get_overview_data(self):
        """Test that show_dashboard calls get_overview_data"""
        # Mock get_overview_data to return test data
        with patch('src.dashboard.components.overview.get_overview_data') as mock_get_data:
            mock_get_data.return_value = (
                {
                    'attendance_summary': {'total_attendance': 100},
                    'recent_activity': [],
                    'system_health': True,
                    'user_count': 25
                },
                None
            )
            
            # Call show_dashboard
            show_dashboard()
            
            # Verify get_overview_data was called
            mock_get_data.assert_called_once()


class TestDashboardAttendanceTableComponent(unittest.TestCase):
    """Test Attendance Table component functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock session state
        self.mock_session_state = {
            'attendance_service': Mock()
        }
        
        # Patch streamlit session state
        self.patcher = patch('streamlit.session_state', self.mock_session_state)
        self.patcher.start()
    
    def tearDown(self):
        """Clean up test environment"""
        self.patcher.stop()
    
    def test_load_attendance_data_success(self):
        """Test successful attendance data loading"""
        # Mock service response
        mock_attendance_service = Mock()
        mock_attendance_service.get_attendance_report.return_value = [
            {
                'Date': '2025-08-30', 'Time': '10:00:00', 'Name': 'John Doe',
                'ID': 'USER001', 'Status': 'Present', 'Confidence': 0.95
            },
            {
                'Date': '2025-08-30', 'Time': '11:00:00', 'Name': 'Jane Smith',
                'ID': 'USER002', 'Status': 'Present', 'Confidence': 0.87
            }
        ]
        
        # Set up session state
        self.mock_session_state['attendance_service'] = mock_attendance_service
        
        # Load attendance data
        result, error = load_attendance_data()
        
        # Verify result
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        
        # Verify service call
        mock_attendance_service.get_attendance_report.assert_called_once_with(
            report_type="detailed_history"
        )
    
    def test_load_attendance_data_service_unavailable(self):
        """Test attendance data loading when services unavailable"""
        # Clear session state
        self.mock_session_state.clear()
        
        # Load attendance data
        result, error = load_attendance_data()
        
        # Verify error
        self.assertIsNone(result)
        self.assertIsNotNone(error)
        self.assertIn("Services not initialized", error)
    
    def test_load_attendance_data_empty_result(self):
        """Test attendance data loading when service returns empty data"""
        # Mock service that returns empty data
        mock_attendance_service = Mock()
        mock_attendance_service.get_attendance_report.return_value = []
        
        self.mock_session_state['attendance_service'] = mock_attendance_service
        
        # Load attendance data
        result, error = load_attendance_data()
        
        # Verify error
        self.assertIsNone(result)
        self.assertIsNotNone(error)
        self.assertIn("No attendance data available", error)
    
    def test_load_attendance_data_missing_columns(self):
        """Test attendance data loading when data has missing columns"""
        # Mock service that returns data with missing columns
        mock_attendance_service = Mock()
        mock_attendance_service.get_attendance_report.return_value = [
            {'Date': '2025-08-30'}  # Missing required columns
        ]
        
        self.mock_session_state['attendance_service'] = mock_attendance_service
        
        # Load attendance data
        result, error = load_attendance_data()
        
        # Verify error
        self.assertIsNone(result)
        self.assertIsNotNone(error)
        self.assertIn("Missing required columns", error)
    
    def test_show_attendance_table_calls_load_attendance_data(self):
        """Test that show_attendance_table calls load_attendance_data"""
        # Mock load_attendance_data to return test data
        with patch('src.dashboard.components.attendance_table.load_attendance_data') as mock_load_data:
            mock_load_data.return_value = (
                pd.DataFrame({
                    'Date': ['2025-08-30'],
                    'Time': ['10:00:00'],
                    'Name': ['John Doe'],
                    'ID': ['USER001'],
                    'Status': ['Present'],
                    'Confidence': [0.95]
                }),
                None
            )
            
            # Call show_attendance_table
            show_attendance_table()
            
            # Verify load_attendance_data was called
            mock_load_data.assert_called_once()


class TestDashboardAnalyticsComponent(unittest.TestCase):
    """Test Analytics component functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock session state
        self.mock_session_state = {
            'attendance_service': Mock()
        }
        
        # Patch streamlit session state
        self.patcher = patch('streamlit.session_state', self.mock_session_state)
        self.patcher.start()
    
    def tearDown(self):
        """Clean up test environment"""
        self.patcher.stop()
    
    def test_get_analytics_data_success(self):
        """Test successful analytics data retrieval"""
        # Mock service response
        mock_attendance_service = Mock()
        mock_attendance_service.get_attendance_analytics.side_effect = [
            {'total_attendance': 100, 'unique_users': 25, 'avg_confidence': 0.92, 'success_rate': 95.0},  # summary
            [{'user_name': 'John Doe', 'attendance_count': 10, 'avg_confidence': 0.95}],  # user_performance
            [{'date': '2025-08-30', 'attendance_count': 25}]  # trends
        ]
        
        # Set up session state
        self.mock_session_state['attendance_service'] = mock_attendance_service
        
        # Get analytics data
        result, error = get_analytics_data()
        
        # Verify result
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIn('attendance_summary', result)
        self.assertIn('user_performance', result)
        self.assertIn('trends', result)
        
        # Verify service calls
        self.assertEqual(mock_attendance_service.get_attendance_analytics.call_count, 3)
    
    def test_get_analytics_data_service_unavailable(self):
        """Test analytics data retrieval when services unavailable"""
        # Clear session state
        self.mock_session_state.clear()
        
        # Get analytics data
        result, error = get_analytics_data()
        
        # Verify error
        self.assertIsNone(result)
        self.assertIsNotNone(error)
        self.assertIn("Services not initialized", error)
    
    def test_get_analytics_data_service_error(self):
        """Test analytics data retrieval when service throws error"""
        # Mock service that throws error
        mock_attendance_service = Mock()
        mock_attendance_service.get_attendance_analytics.side_effect = Exception("Service error")
        
        self.mock_session_state['attendance_service'] = mock_attendance_service
        
        # Get analytics data
        result, error = get_analytics_data()
        
        # Verify error
        self.assertIsNone(result)
        self.assertIsNotNone(error)
        self.assertIn("Error loading analytics data", error)
    
    def test_show_analytics_calls_get_analytics_data(self):
        """Test that show_analytics calls get_analytics_data"""
        # Mock get_analytics_data to return test data
        with patch('src.dashboard.components.analytics.get_analytics_data') as mock_get_data:
            mock_get_data.return_value = (
                {
                    'attendance_summary': {'total_attendance': 100},
                    'user_performance': [],
                    'trends': []
                },
                None
            )
            
            # Call show_analytics
            show_analytics()
            
            # Verify get_analytics_data was called
            mock_get_data.assert_called_once()


class TestDashboardRegistrationComponent(unittest.TestCase):
    """Test Registration component functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock session state
        self.mock_session_state = {
            'attendance_service': Mock(),
            'face_database': Mock()
        }
        
        # Patch streamlit session state
        self.patcher = patch('streamlit.session_state', self.mock_session_state)
        self.patcher.start()
    
    def tearDown(self):
        """Clean up test environment"""
        self.patcher.stop()
    
    def test_process_registration_success(self):
        """Test successful user registration processing"""
        # Mock dependencies
        mock_attendance_service = Mock()
        mock_face_database = Mock()
        mock_face_database.users_db = {}
        
        # Test data
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
        result = process_registration(mock_attendance_service, mock_face_database, user_data)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(result['user_id'], 'USER001')
        self.assertEqual(result['message'], 'User registered successfully')
        
        # Verify user was added to database
        self.assertIn('USER001', mock_face_database.users_db)
        user_info = mock_face_database.users_db['USER001']
        self.assertEqual(user_info['first_name'], 'John')
        self.assertEqual(user_info['last_name'], 'Doe')
        self.assertEqual(user_info['email'], 'john.doe@example.com')
        self.assertEqual(user_info['department'], 'Engineering')
        self.assertEqual(user_info['role'], 'Software Engineer')
        self.assertTrue(user_info['active'])
        self.assertTrue(user_info['enable_liveness'])
        self.assertTrue(user_info['auto_attendance'])
    
    def test_process_registration_failure(self):
        """Test user registration processing failure"""
        # Mock dependencies
        mock_attendance_service = Mock()
        mock_face_database = Mock()
        mock_face_database.users_db = {}
        
        # Test data that will cause error
        user_data = {
            'user_id': 'USER001',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'department': 'Engineering',
            'role': 'Software Engineer',
            'face_image': None,  # This will cause an error
            'enable_liveness': True,
            'auto_attendance': True,
            'notification_email': True,
            'create_backup': True
        }
        
        # Process registration
        result = process_registration(mock_attendance_service, mock_face_database, user_data)
        
        # Verify result
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_show_registration_service_unavailable(self):
        """Test registration display when services unavailable"""
        # Clear session state
        self.mock_session_state.clear()
        
        # Mock streamlit.error and streamlit.info
        with patch('streamlit.error') as mock_error, patch('streamlit.info') as mock_info:
            # Call show_registration
            show_registration()
            
            # Verify error message
            mock_error.assert_called_with("Services not initialized. Please refresh the page.")
            mock_info.assert_called_with("The registration system requires the service layer to be active.")
    
    def test_show_registration_with_services(self):
        """Test registration display when services are available"""
        # Mock services
        mock_attendance_service = Mock()
        mock_face_database = Mock()
        mock_face_database.users_db = {}
        
        self.mock_session_state['attendance_service'] = mock_attendance_service
        self.mock_session_state['face_database'] = mock_face_database
        
        # Mock streamlit components
        with patch('streamlit.header') as mock_header, \
             patch('streamlit.markdown') as mock_markdown, \
             patch('streamlit.info') as mock_info:
            
            # Call show_registration
            show_registration()
            
            # Verify components were called
            mock_header.assert_called()
            mock_markdown.assert_called()
            mock_info.assert_called()


class TestDashboardComponentIntegration(unittest.TestCase):
    """Test dashboard components integration with service layer"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Mock session state
        self.mock_session_state = {
            'attendance_service': Mock(),
            'face_database': Mock()
        }
        
        # Patch streamlit session state
        self.patcher = patch('streamlit.session_state', self.mock_session_state)
        self.patcher.start()
    
    def tearDown(self):
        """Clean up test environment"""
        self.patcher.stop()
        shutil.rmtree(self.test_dir)
    
    def test_component_service_dependency(self):
        """Test that all components depend on service layer"""
        # Test overview component
        with patch('src.dashboard.components.overview.get_overview_data') as mock_get_data:
            mock_get_data.return_value = (None, "Services not initialized")
            show_dashboard()
            mock_get_data.assert_called_once()
        
        # Test attendance table component
        with patch('src.dashboard.components.attendance_table.load_attendance_data') as mock_load_data:
            mock_load_data.return_value = (None, "Services not initialized")
            show_attendance_table()
            mock_load_data.assert_called_once()
        
        # Test analytics component
        with patch('src.dashboard.components.analytics.get_analytics_data') as mock_get_data:
            mock_get_data.return_value = (None, "Services not initialized")
            show_analytics()
            mock_get_data.assert_called_once()
        
        # Test registration component
        with patch('streamlit.error') as mock_error:
            show_registration()
            mock_error.assert_called_with("Services not initialized. Please refresh the page.")
    
    def test_component_error_handling(self):
        """Test that all components handle service errors gracefully"""
        # Mock services that throw errors
        mock_attendance_service = Mock()
        mock_attendance_service.get_attendance_report.side_effect = Exception("Service error")
        mock_attendance_service.get_attendance_analytics.side_effect = Exception("Service error")
        
        self.mock_session_state['attendance_service'] = mock_attendance_service
        
        # Test overview component error handling
        with patch('streamlit.error') as mock_error:
            show_dashboard()
            mock_error.assert_called()
        
        # Test analytics component error handling
        with patch('streamlit.error') as mock_error:
            show_analytics()
            mock_error.assert_called()
    
    def test_component_data_flow(self):
        """Test data flow from services to components"""
        # Mock successful service responses
        mock_attendance_service = Mock()
        mock_attendance_service.get_attendance_report.return_value = [
            {'Date': '2025-08-30', 'Name': 'John Doe', 'Status': 'Present'}
        ]
        mock_attendance_service.get_attendance_analytics.return_value = {
            'total_attendance': 100, 'unique_users': 25
        }
        
        mock_face_database = Mock()
        mock_face_database.users_db = {'USER001': {'name': 'John Doe'}}
        
        self.mock_session_state['attendance_service'] = mock_attendance_service
        self.mock_session_state['face_database'] = mock_face_database
        
        # Test that components can process service data
        with patch('streamlit.dataframe') as mock_dataframe, \
             patch('streamlit.metric') as mock_metric:
            
            # Test attendance table
            show_attendance_table()
            mock_dataframe.assert_called()
            
            # Test analytics
            show_analytics()
            mock_metric.assert_called()
            
            # Test registration
            show_registration()
            # Should display user list without errors


class TestDashboardComponentMocking(unittest.TestCase):
    """Test dashboard components with mocked services"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock session state
        self.mock_session_state = {
            'attendance_service': Mock(),
            'face_database': Mock()
        }
        
        # Patch streamlit session state
        self.patcher = patch('streamlit.session_state', self.mock_session_state)
        self.patcher.start()
    
    def tearDown(self):
        """Clean up test environment"""
        self.patcher.stop()
    
    def test_mock_service_integration(self):
        """Test components with fully mocked services"""
        # Create comprehensive mock services
        mock_attendance_service = Mock()
        mock_attendance_service.get_attendance_report.return_value = [
            {
                'Date': '2025-08-30', 'Time': '10:00:00', 'Name': 'John Doe',
                'ID': 'USER001', 'Status': 'Present', 'Confidence': 0.95
            }
        ]
        mock_attendance_service.get_attendance_analytics.return_value = {
            'total_attendance': 100, 'unique_users': 25, 'avg_confidence': 0.92, 'success_rate': 95.0
        }
        mock_attendance_service.is_system_healthy.return_value = True
        
        mock_face_database = Mock()
        mock_face_database.users_db = {
            'USER001': {
                'first_name': 'John', 'last_name': 'Doe',
                'email': 'john.doe@example.com', 'department': 'Engineering'
            }
        }
        
        self.mock_session_state['attendance_service'] = mock_attendance_service
        self.mock_session_state['face_database'] = mock_face_database
        
        # Test all components with mocked services
        with patch('streamlit.header') as mock_header, \
             patch('streamlit.dataframe') as mock_dataframe, \
             patch('streamlit.metric') as mock_metric, \
             patch('streamlit.plotly_chart') as mock_chart:
            
            # Test overview component
            show_dashboard()
            mock_header.assert_called()
            mock_metric.assert_called()
            
            # Test attendance table component
            show_attendance_table()
            mock_dataframe.assert_called()
            
            # Test analytics component
            show_analytics()
            mock_chart.assert_called()
            
            # Test registration component
            show_registration()
            mock_dataframe.assert_called()


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
