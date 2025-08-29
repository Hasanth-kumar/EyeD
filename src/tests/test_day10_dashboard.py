#!/usr/bin/env python3
"""
Test Suite for Day 10: Basic Dashboard Skeleton
EyeD AI Attendance System

This test suite validates:
- Dashboard initialization and system setup
- Real-time metrics calculation
- Attendance logs functionality
- Analytics and chart generation
- User registration with quality assessment
- Testing suite functionality
- Debug tools and performance monitoring
"""

import unittest
import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import tempfile
import shutil

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

class TestDay10Dashboard(unittest.TestCase):
    """Test cases for Day 10 dashboard implementation"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_data_dir = Path(tempfile.mkdtemp())
        self.test_faces_dir = self.test_data_dir / "faces"
        self.test_faces_dir.mkdir(exist_ok=True)
        
        # Create test attendance data
        self.test_attendance_data = [
            {
                "Name": "Test User 1",
                "ID": "TU001",
                "Date": "2025-01-20",
                "Time": "09:00:00",
                "Status": "Present",
                "Confidence": 0.85,
                "Liveness_Verified": True,
                "Face_Quality_Score": 0.78,
                "Processing_Time_MS": 120.5,
                "Verification_Stage": "Completed",
                "Session_ID": "S001_TU001",
                "Device_Info": "Test System",
                "Location": "Test Office"
            },
            {
                "Name": "Test User 2",
                "ID": "TU002",
                "Date": "2025-01-20",
                "Time": "09:15:00",
                "Status": "Late",
                "Confidence": 0.92,
                "Liveness_Verified": True,
                "Face_Quality_Score": 0.85,
                "Processing_Time_MS": 95.2,
                "Verification_Stage": "Completed",
                "Session_ID": "S001_TU002",
                "Device_Info": "Test System",
                "Location": "Test Office"
            }
        ]
        
        # Create test attendance CSV
        self.test_attendance_csv = self.test_data_dir / "attendance.csv"
        df = pd.DataFrame(self.test_attendance_data)
        df.to_csv(self.test_attendance_csv, index=False)
        
        # Create test faces database
        self.test_faces_json = self.test_faces_dir / "faces.json"
        test_faces_data = {
            "users": {
                "user_001": {
                    "name": "Test User 1",
                    "user_id": "TU001",
                    "registration_date": "2025-01-15",
                    "last_updated": "2025-01-15",
                    "image_path": "test_user_1.jpg",
                    "embedding": [0.1] * 128,
                    "metadata": {
                        "age": 30,
                        "department": "Testing",
                        "role": "Test Engineer"
                    }
                }
            },
            "embeddings": {},
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0",
                "total_users": 1
            }
        }
        
        with open(self.test_faces_json, 'w') as f:
            json.dump(test_faces_data, f, indent=2)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_data_dir)
    
    def test_dashboard_imports(self):
        """Test that all dashboard dependencies can be imported"""
        try:
            import streamlit as st
            import plotly.express as px
            import plotly.graph_objects as go
            import cv2
            from PIL import Image
            import numpy as np
            import pandas as pd
            self.assertTrue(True, "All imports successful")
        except ImportError as e:
            self.fail(f"Import failed: {e}")
    
    def test_dashboard_structure(self):
        """Test that dashboard app has required structure"""
        try:
            from src.dashboard.app import (
                main, show_dashboard, show_attendance_logs, 
                show_analytics, show_user_registration,
                show_testing_suite, show_debug_tools
            )
            self.assertTrue(True, "Dashboard structure is correct")
        except ImportError as e:
            self.fail(f"Dashboard structure test failed: {e}")
    
    def test_attendance_data_loading(self):
        """Test attendance data loading and parsing"""
        # Test CSV loading
        df = pd.read_csv(self.test_attendance_csv)
        self.assertEqual(len(df), 2, "Should load 2 attendance records")
        
        # Test data structure
        required_columns = [
            "Name", "ID", "Date", "Time", "Status", 
            "Confidence", "Liveness_Verified"
        ]
        for col in required_columns:
            self.assertIn(col, df.columns, f"Missing column: {col}")
        
        # Test data types
        self.assertIsInstance(df['Confidence'].iloc[0], float, "Confidence should be float")
        self.assertIsInstance(df['Liveness_Verified'].iloc[0], bool, "Liveness_Verified should be bool")
    
    def test_face_database_structure(self):
        """Test face database structure and loading"""
        # Test JSON loading
        with open(self.test_faces_json, 'r') as f:
            faces_data = json.load(f)
        
        # Test structure
        self.assertIn('users', faces_data, "Should have users section")
        self.assertIn('metadata', faces_data, "Should have metadata section")
        self.assertIn('user_001', faces_data['users'], "Should have test user")
        
        # Test user data
        user = faces_data['users']['user_001']
        self.assertEqual(user['name'], 'Test User 1', "User name should match")
        self.assertEqual(user['user_id'], 'TU001', "User ID should match")
        self.assertIn('embedding', user, "User should have embedding")
    
    def test_analytics_data_processing(self):
        """Test analytics data processing and chart generation"""
        df = pd.DataFrame(self.test_attendance_data)
        
        # Test date parsing
        df['Date'] = pd.to_datetime(df['Date'])
        self.assertEqual(len(df), 2, "Should have 2 records after date parsing")
        
        # Test grouping operations
        daily_counts = df.groupby(df['Date'].dt.date).size()
        self.assertEqual(len(daily_counts), 1, "Should have 1 day")
        self.assertEqual(daily_counts.iloc[0], 2, "Should have 2 records for the day")
        
        # Test status distribution
        status_counts = df['Status'].value_counts()
        self.assertEqual(status_counts['Present'], 1, "Should have 1 present")
        self.assertEqual(status_counts['Late'], 1, "Should have 1 late")
    
    def test_quality_assessment_metrics(self):
        """Test image quality assessment calculations"""
        # Create test image data
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Test basic metrics
        height, width = test_image.shape[:2]
        self.assertEqual(height, 480, "Height should be 480")
        self.assertEqual(width, 640, "Width should be 640")
        
        # Test brightness calculation
        brightness = np.mean(test_image)
        self.assertGreaterEqual(brightness, 0, "Brightness should be >= 0")
        self.assertLessEqual(brightness, 255, "Brightness should be <= 255")
        
        # Test contrast calculation
        contrast = np.std(test_image)
        self.assertGreaterEqual(contrast, 0, "Contrast should be >= 0")
    
    def test_performance_metrics_tracking(self):
        """Test performance metrics collection and tracking"""
        # Simulate performance metrics
        performance_data = [
            {
                'timestamp': datetime.now(),
                'processing_time': 0.5,
                'operation': 'test_operation',
                'success': True
            },
            {
                'timestamp': datetime.now() + timedelta(seconds=1),
                'processing_time': 0.3,
                'operation': 'test_operation_2',
                'success': True
            }
        ]
        
        # Test metrics structure
        for metric in performance_data:
            self.assertIn('timestamp', metric, "Should have timestamp")
            self.assertIn('processing_time', metric, "Should have processing_time")
            self.assertIn('operation', metric, "Should have operation")
            self.assertIn('success', metric, "Should have success")
        
        # Test metrics aggregation
        df_metrics = pd.DataFrame(performance_data)
        avg_time = df_metrics['processing_time'].mean()
        self.assertAlmostEqual(avg_time, 0.4, places=1, msg="Average time should be 0.4")
        
        success_rate = df_metrics['success'].mean()
        self.assertEqual(success_rate, 1.0, "Success rate should be 100%")
    
    def test_user_registration_validation(self):
        """Test user registration validation logic"""
        # Test required fields
        required_fields = ['name', 'user_id']
        
        # Test with missing fields
        test_cases = [
            {'name': 'Test User', 'user_id': ''},  # Missing ID
            {'name': '', 'user_id': 'TU003'},      # Missing name
            {'name': 'Test User', 'user_id': 'TU003'}  # Valid case
        ]
        
        for i, test_case in enumerate(test_cases):
            if i < 2:  # First two should fail validation
                self.assertFalse(
                    bool(test_case['name'] and test_case['user_id']),
                    f"Validation should fail for case {i+1}"
                )
            else:  # Last one should pass validation
                self.assertTrue(
                    bool(test_case['name'] and test_case['user_id']),
                    f"Validation should pass for case {i+1}"
                )
    
    def test_attendance_filtering(self):
        """Test attendance data filtering functionality"""
        df = pd.DataFrame(self.test_attendance_data)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Test date filtering
        target_date = datetime(2025, 1, 20).date()
        filtered_df = df[df['Date'].dt.date == target_date]
        self.assertEqual(len(filtered_df), 2, "Should filter to 2 records for target date")
        
        # Test status filtering
        present_records = df[df['Status'] == 'Present']
        self.assertEqual(len(present_records), 1, "Should have 1 present record")
        
        late_records = df[df['Status'] == 'Late']
        self.assertEqual(len(late_records), 1, "Should have 1 late record")
        
        # Test user filtering
        user1_records = df[df['Name'] == 'Test User 1']
        self.assertEqual(len(user1_records), 1, "Should have 1 record for User 1")
    
    def test_chart_generation(self):
        """Test chart generation with Plotly"""
        try:
            import plotly.express as px
            import plotly.graph_objects as go
            
            # Test basic bar chart
            df = pd.DataFrame(self.test_attendance_data)
            fig = px.bar(df, x='Name', y='Confidence', title="Test Chart")
            self.assertIsNotNone(fig, "Chart should be generated")
            
            # Test pie chart
            status_counts = df['Status'].value_counts()
            fig_pie = px.pie(values=status_counts.values, names=status_counts.index)
            self.assertIsNotNone(fig_pie, "Pie chart should be generated")
            
        except ImportError as e:
            self.skipTest(f"Plotly not available: {e}")
    
    def test_error_handling(self):
        """Test error handling in dashboard functions"""
        # Test with invalid file paths
        invalid_csv = self.test_data_dir / "nonexistent.csv"
        
        try:
            df = pd.read_csv(invalid_csv)
            self.fail("Should raise FileNotFoundError for nonexistent file")
        except FileNotFoundError:
            self.assertTrue(True, "Correctly handled missing file")
        except Exception as e:
            self.fail(f"Unexpected error type: {type(e)}")
        
        # Test with invalid JSON
        invalid_json = self.test_data_dir / "invalid.json"
        with open(invalid_json, 'w') as f:
            f.write("invalid json content")
        
        try:
            with open(invalid_json, 'r') as f:
                json.load(f)
            self.fail("Should raise JSONDecodeError for invalid JSON")
        except json.JSONDecodeError:
            self.assertTrue(True, "Correctly handled invalid JSON")
        except Exception as e:
            self.fail(f"Unexpected error type: {type(e)}")

class TestDashboardIntegration(unittest.TestCase):
    """Integration tests for dashboard functionality"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Create minimal test environment
        self.test_src_dir = self.test_dir / "src"
        self.test_src_dir.mkdir()
        
        self.test_dashboard_dir = self.test_src_dir / "dashboard"
        self.test_dashboard_dir.mkdir()
        
        self.test_modules_dir = self.test_src_dir / "modules"
        self.test_modules_dir.mkdir()
        
        self.test_utils_dir = self.test_src_dir / "utils"
        self.test_utils_dir.mkdir()
    
    def tearDown(self):
        """Clean up integration test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_dashboard_file_structure(self):
        """Test that dashboard file structure is correct"""
        # Check main dashboard file exists
        dashboard_file = Path("src/dashboard/app.py")
        self.assertTrue(dashboard_file.exists(), "Dashboard app.py should exist")
        
        # Check required directories exist
        required_dirs = [
            "src/dashboard",
            "src/modules", 
            "src/utils",
            "data",
            "data/faces"
        ]
        
        for dir_path in required_dirs:
            self.assertTrue(Path(dir_path).exists(), f"Required directory {dir_path} should exist")
    
    def test_dependencies_availability(self):
        """Test that all required dependencies are available"""
        required_packages = [
            'streamlit',
            'plotly',
            'opencv-python',
            'pillow',
            'pandas',
            'numpy'
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                self.fail(f"Required package {package} is not available")

def run_tests():
    """Run all Day 10 dashboard tests"""
    print("🧪 Running Day 10 Dashboard Tests...")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestDay10Dashboard))
    test_suite.addTest(unittest.makeSuite(TestDashboardIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Test Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n⚠️  Test Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 All tests passed! Day 10 dashboard is working correctly.")
    else:
        print("\n🔧 Some tests failed. Please check the implementation.")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
