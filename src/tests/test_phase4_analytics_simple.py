"""
Test Phase 4 Analytics - Simplified Version
Tests the simplified analytics component functionality
"""

import unittest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

class TestPhase4AnalyticsSimple(unittest.TestCase):
    """Test the simplified analytics component"""
    
    def setUp(self):
        """Set up test data"""
        # Create sample attendance data
        self.sample_attendance_data = [
            {
                'Name': 'Alice Johnson',
                'ID': 'U001',
                'Date': '2025-08-31',
                'Time': '09:15:00',
                'Status': 'Present',
                'Confidence': 0.95,
                'Liveness_Verified': True,
                'Face_Quality_Score': 0.92
            },
            {
                'Name': 'Bob Smith',
                'ID': 'U002',
                'Date': '2025-08-31',
                'Time': '09:30:00',
                'Status': 'Present',
                'Confidence': 0.87,
                'Liveness_Verified': True,
                'Face_Quality_Score': 0.88
            },
            {
                'Name': 'Alice Johnson',
                'ID': 'U001',
                'Date': '2025-08-30',
                'Time': '09:10:00',
                'Status': 'Present',
                'Confidence': 0.93,
                'Liveness_Verified': True,
                'Face_Quality_Score': 0.90
            }
        ]
        
        # Create sample analytics data
        self.sample_analytics_data = {
            'attendance_summary': {
                'total_attendance': 3,
                'unique_users': 2,
                'avg_confidence': 0.92,
                'success_rate': 100.0,
                'attendance_change': 1,
                'user_change': 0,
                'confidence_change': 0.02,
                'success_change': 0.0
            },
            'user_performance': [
                {
                    'user_name': 'Alice Johnson',
                    'attendance_count': 2,
                    'avg_confidence': 0.94,
                    'attendance_rate': 100.0,
                    'avg_quality_score': 0.91
                },
                {
                    'user_name': 'Bob Smith',
                    'attendance_count': 1,
                    'avg_confidence': 0.87,
                    'attendance_rate': 100.0,
                    'avg_quality_score': 0.88
                }
            ],
            'trends': [
                {
                    'date': '2025-08-30',
                    'attendance_count': 1,
                    'hour': 9,
                    'late_arrivals': 0
                },
                {
                    'date': '2025-08-31',
                    'attendance_count': 2,
                    'hour': 9,
                    'late_arrivals': 1
                }
            ]
        }
    
    def test_analytics_data_structure(self):
        """Test that analytics data has the expected structure"""
        self.assertIn('attendance_summary', self.sample_analytics_data)
        self.assertIn('user_performance', self.sample_analytics_data)
        self.assertIn('trends', self.sample_analytics_data)
        
        # Test attendance summary structure
        summary = self.sample_analytics_data['attendance_summary']
        required_keys = ['total_attendance', 'unique_users', 'avg_confidence', 'success_rate']
        for key in required_keys:
            self.assertIn(key, summary)
    
    def test_user_performance_data(self):
        """Test user performance data structure"""
        user_perf = self.sample_analytics_data['user_performance']
        self.assertIsInstance(user_perf, list)
        self.assertGreater(len(user_perf), 0)
        
        # Test first user performance entry
        first_user = user_perf[0]
        required_keys = ['user_name', 'attendance_count', 'avg_confidence', 'attendance_rate']
        for key in required_keys:
            self.assertIn(key, first_user)
    
    def test_trends_data(self):
        """Test trends data structure"""
        trends = self.sample_analytics_data['trends']
        self.assertIsInstance(trends, list)
        self.assertGreater(len(trends), 0)
        
        # Test first trend entry
        first_trend = trends[0]
        required_keys = ['date', 'attendance_count']
        for key in required_keys:
            self.assertIn(key, first_trend)
    
    def test_export_functionality(self):
        """Test export functionality with mock data"""
        from src.dashboard.components.analytics import generate_export
        
        # Test complete report export
        result = generate_export(self.sample_analytics_data, "CSV", "Complete Analytics Report")
        self.assertTrue(result['success'])
        self.assertIn('complete_analytics_report_', result['filename'])
        self.assertEqual(result['mime_type'], 'text/csv')
        
        # Test JSON export
        result = generate_export(self.sample_analytics_data, "JSON", "Complete Analytics Report")
        self.assertTrue(result['success'])
        self.assertIn('complete_analytics_report_', result['filename'])
        self.assertEqual(result['mime_type'], 'application/json')
    
    def test_attendance_summary_export(self):
        """Test attendance summary export"""
        from src.dashboard.components.analytics import generate_attendance_summary
        
        result = generate_attendance_summary(self.sample_analytics_data, "CSV", "test_timestamp")
        self.assertTrue(result['success'])
        self.assertIn('attendance_summary_test_timestamp.csv', result['filename'])
    
    def test_user_performance_export(self):
        """Test user performance export"""
        from src.dashboard.components.analytics import generate_user_performance
        
        result = generate_user_performance(self.sample_analytics_data, "CSV", "test_timestamp")
        self.assertTrue(result['success'])
        self.assertIn('user_performance_test_timestamp.csv', result['filename'])
    
    def test_trends_analysis_export(self):
        """Test trends analysis export"""
        from src.dashboard.components.analytics import generate_trends_analysis
        
        result = generate_trends_analysis(self.sample_analytics_data, "CSV", "test_timestamp")
        self.assertTrue(result['success'])
        self.assertIn('trends_analysis_test_timestamp.csv', result['filename'])
    
    def test_error_handling(self):
        """Test error handling for missing data"""
        from src.dashboard.components.analytics import generate_attendance_summary
        
        # Test with missing attendance summary
        empty_data = {'user_performance': [], 'trends': []}
        result = generate_attendance_summary(empty_data, "CSV", "test_timestamp")
        self.assertFalse(result['success'])
        self.assertIn('No attendance summary data available', result['error'])

if __name__ == '__main__':
    unittest.main()

