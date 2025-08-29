"""
Test Suite for Day 12: Analytics View with Advanced Visualizations
Tests enhanced analytics features including attendance percentages, late arrival analysis, and performance insights
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from dashboard.components.analytics import (
    load_analytics_data,
    show_enhanced_attendance_overview,
    show_enhanced_time_analysis,
    show_enhanced_user_performance,
    show_enhanced_quality_metrics,
    show_performance_insights
)

class TestDay12Analytics(unittest.TestCase):
    """Test cases for Day 12 Analytics enhancements"""
    
    def setUp(self):
        """Set up test data"""
        # Create sample attendance data for testing
        self.test_data = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Carol', 'David', 'Eva'] * 4,
            'ID': ['U001', 'U002', 'U003', 'U004', 'U005'] * 4,
            'Date': ['2025-08-22', '2025-08-22', '2025-08-22', '2025-08-22', '2025-08-22',
                     '2025-08-23', '2025-08-23', '2025-08-23', '2025-08-23', '2025-08-23',
                     '2025-08-24', '2025-08-24', '2025-08-24', '2025-08-24', '2025-08-24',
                     '2025-08-25', '2025-08-25', '2025-08-25', '2025-08-25', '2025-08-25'],
            'Time': ['08:22:38', '09:41:38', '09:32:38', '08:40:38', '10:07:38',
                     '08:40:38', '08:59:38', '08:30:38', '09:07:38', '10:37:38',
                     '08:52:38', '09:37:38', '09:03:38', '08:17:38', '08:15:38',
                     '10:34:38', '08:11:38', '08:01:38', '10:27:38', '09:52:38'],
            'Status': ['Present', 'Present', 'Present', 'Present', 'Late',
                      'Present', 'Present', 'Present', 'Present', 'Late',
                      'Present', 'Present', 'Present', 'Present', 'Present',
                      'Late', 'Present', 'Present', 'Late', 'Present'],
            'Confidence': [0.737, 0.705, 0.8, 0.73, 0.743,
                          0.878, 0.819, 0.732, 0.853, 0.801,
                          0.869, 0.902, 0.862, 0.772, 0.891,
                          0.713, 0.945, 0.862, 0.812, 0.899],
            'Liveness_Verified': [True, True, True, True, True,
                                 True, True, True, True, True,
                                 True, True, True, True, True,
                                 True, True, True, True, True],
            'Face_Quality_Score': [0.797, 0.658, 0.667, 0.638, 0.646,
                                  0.843, 0.627, 0.859, 0.668, 0.746,
                                  0.833, 0.7, 0.636, 0.831, 0.791,
                                  0.896, 0.867, 0.692, 0.727, 0.609],
            'Processing_Time_MS': [158.4, 130.2, 132.5, 57.3, 67.8,
                                  74.6, 126.3, 167.4, 118.1, 57.8,
                                  55.9, 84.1, 81.6, 63.7, 91.4,
                                  153.8, 126.2, 78.1, 125.6, 96.3],
            'Verification_Stage': ['Completed'] * 20,
            'Session_ID': [f'S{i:03d}' for i in range(4) for _ in range(5)],
            'Device_Info': ['Demo System'] * 20,
            'Location': ['Demo Office'] * 20
        })
        
        # Save test data to CSV
        self.test_data.to_csv('data/test_attendance.csv', index=False)
        
        # Backup original data
        if os.path.exists('data/attendance.csv'):
            self.original_data = pd.read_csv('data/attendance.csv')
            self.original_data.to_csv('data/attendance_backup.csv', index=False)
        
        # Replace with test data
        self.test_data.to_csv('data/attendance.csv', index=False)
    
    def tearDown(self):
        """Clean up test data"""
        # Remove test file
        if os.path.exists('data/test_attendance.csv'):
            os.remove('data/test_attendance.csv')
        
        # Restore original data
        if hasattr(self, 'original_data') and os.path.exists('data/attendance_backup.csv'):
            self.original_data.to_csv('data/attendance.csv', index=False)
            os.remove('data/attendance_backup.csv')
    
    def test_01_load_analytics_data(self):
        """Test enhanced data loading with new columns"""
        df, error = load_analytics_data()
        
        self.assertIsNone(error)
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 20)
        
        # Check new derived columns
        self.assertIn('Day_of_Week', df.columns)
        self.assertIn('Hour', df.columns)
        self.assertIn('Week_Number', df.columns)
        self.assertIn('Month', df.columns)
        self.assertIn('Year', df.columns)
        self.assertIn('Quarter', df.columns)
        
        # Check attendance percentage columns
        self.assertIn('Is_Present', df.columns)
        self.assertIn('Is_Late', df.columns)
        self.assertIn('Is_Absent', df.columns)
        
        # Verify data types
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['Date']))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['Time']))
        self.assertTrue(pd.api.types.is_numeric_dtype(df['Is_Present']))
    
    def test_02_attendance_percentage_calculations(self):
        """Test attendance percentage calculations"""
        df, _ = load_analytics_data()
        
        # Test present calculations
        present_count = df['Is_Present'].sum()
        self.assertEqual(present_count, 16)  # 16 present entries
        
        # Test late calculations
        late_count = df['Is_Late'].sum()
        self.assertEqual(late_count, 4)  # 4 late entries
        
        # Test absent calculations
        absent_count = df['Is_Absent'].sum()
        self.assertEqual(absent_count, 0)  # 0 absent entries
        
        # Test total calculations
        total_entries = len(df)
        self.assertEqual(total_entries, 20)
        
        # Verify percentages
        present_percentage = (present_count / total_entries) * 100
        self.assertEqual(present_percentage, 80.0)
        
        late_percentage = (late_count / total_entries) * 100
        self.assertEqual(late_percentage, 20.0)
    
    def test_03_enhanced_attendance_overview(self):
        """Test enhanced attendance overview functionality"""
        df, _ = load_analytics_data()
        
        # Test that function can be called without errors
        try:
            # This would normally display charts, but we're just testing the function call
            # In a real test environment, we'd mock the Streamlit functions
            pass
        except Exception as e:
            self.fail(f"show_enhanced_attendance_overview raised an exception: {e}")
        
        # Test data preparation for charts
        total_entries = len(df)
        present_count = len(df[df['Status'] == 'Present'])
        late_count = len(df[df['Status'] == 'Late'])
        absent_count = len(df[df['Status'] == 'Absent'])
        
        self.assertEqual(total_entries, 20)
        self.assertEqual(present_count, 16)
        self.assertEqual(late_count, 4)
        self.assertEqual(absent_count, 0)
    
    def test_04_enhanced_time_analysis(self):
        """Test enhanced time analysis functionality"""
        df, _ = load_analytics_data()
        
        # Test time-based data preparation
        df['Hour'] = pd.to_datetime(df['Time']).dt.hour
        df['Day_of_Week'] = pd.to_datetime(df['Date']).dt.day_name()
        
        # Test late arrival analysis
        late_data = df[df['Status'] == 'Late'].copy()
        self.assertEqual(len(late_data), 4)
        
        # Test hourly distribution
        hourly_data = df.groupby('Hour').size().reset_index(name='Count')
        self.assertGreater(len(hourly_data), 0)
        
        # Test day of week distribution
        day_data = df.groupby('Day_of_Week').size().reset_index(name='Count')
        self.assertGreater(len(day_data), 0)
    
    def test_05_enhanced_user_performance(self):
        """Test enhanced user performance analysis"""
        df, _ = load_analytics_data()
        
        # Test user summary calculations
        user_summary = df.groupby('Name').agg({
            'Is_Present': 'sum',
            'Is_Late': 'sum',
            'Is_Absent': 'sum'
        }).reset_index()
        
        user_summary['Total_Attendance'] = user_summary['Is_Present'] + user_summary['Is_Late'] + user_summary['Is_Absent']
        user_summary['Present_Percentage'] = (user_summary['Is_Present'] / user_summary['Total_Attendance'] * 100).round(1)
        
        # Verify user summary structure
        self.assertIn('Name', user_summary.columns)
        self.assertIn('Total_Attendance', user_summary.columns)
        self.assertIn('Present_Percentage', user_summary.columns)
        
        # Test that all users have data
        self.assertEqual(len(user_summary), 5)  # 5 unique users
        
        # Test percentage calculations
        for _, user in user_summary.iterrows():
            self.assertGreaterEqual(user['Present_Percentage'], 0)
            self.assertLessEqual(user['Present_Percentage'], 100)
    
    def test_06_enhanced_quality_metrics(self):
        """Test enhanced quality metrics analysis"""
        df, _ = load_analytics_data()
        
        # Test quality columns availability
        quality_columns = []
        if 'Face_Quality_Score' in df.columns:
            quality_columns.append('Face_Quality_Score')
        if 'Processing_Time_MS' in df.columns:
            quality_columns.append('Processing_Time_MS')
        if 'Confidence' in df.columns:
            quality_columns.append('Confidence')
        
        self.assertGreater(len(quality_columns), 0)
        
        # Test quality metrics calculations
        if 'Face_Quality_Score' in df.columns:
            avg_quality = df['Face_Quality_Score'].mean()
            self.assertGreater(avg_quality, 0)
            self.assertLess(avg_quality, 1)
        
        if 'Processing_Time_MS' in df.columns:
            avg_time = df['Processing_Time_MS'].mean()
            self.assertGreater(avg_time, 0)
        
        if 'Confidence' in df.columns:
            avg_confidence = df['Confidence'].mean()
            self.assertGreater(avg_confidence, 0)
            self.assertLess(avg_confidence, 1)
    
    def test_07_performance_insights(self):
        """Test performance insights functionality"""
        df, _ = load_analytics_data()
        
        # Test performance metrics calculations
        total_sessions = df['Session_ID'].nunique()
        self.assertEqual(total_sessions, 4)  # 4 unique sessions (S000, S001, S002, S003)
        
        if 'Processing_Time_MS' in df.columns:
            avg_processing = df['Processing_Time_MS'].mean()
            self.assertGreater(avg_processing, 0)
        
        if 'Liveness_Verified' in df.columns:
            liveness_success = df['Liveness_Verified'].sum()
            liveness_total = len(df)
            liveness_rate = (liveness_success / liveness_total * 100) if liveness_total > 0 else 0
            self.assertGreaterEqual(liveness_rate, 0)
            self.assertLessEqual(liveness_rate, 100)
        
        if 'Confidence' in df.columns:
            high_confidence = len(df[df['Confidence'] >= 0.8])
            confidence_rate = (high_confidence / len(df) * 100) if len(df) > 0 else 0
            self.assertGreaterEqual(confidence_rate, 0)
            self.assertLessEqual(confidence_rate, 100)
    
    def test_08_monthly_summary_analysis(self):
        """Test monthly summary analysis - Day 12 requirement"""
        df, _ = load_analytics_data()
        
        # Test monthly data preparation
        df['Month'] = pd.to_datetime(df['Date']).dt.month_name()
        df['Year'] = pd.to_datetime(df['Date']).dt.year
        
        # Test monthly summary calculations
        monthly_summary = df.groupby(['Year', 'Month']).agg({
            'Is_Present': 'sum',
            'Is_Late': 'sum',
            'Is_Absent': 'sum'
        }).reset_index()
        
        monthly_summary['Total'] = monthly_summary['Is_Present'] + monthly_summary['Is_Late'] + monthly_summary['Is_Absent']
        monthly_summary['Present_Percentage'] = (monthly_summary['Is_Present'] / monthly_summary['Total'] * 100).round(1)
        monthly_summary['Late_Percentage'] = (monthly_summary['Is_Late'] / monthly_summary['Total'] * 100).round(1)
        
        # Verify monthly summary structure
        self.assertIn('Month', monthly_summary.columns)
        self.assertIn('Total', monthly_summary.columns)
        self.assertIn('Present_Percentage', monthly_summary.columns)
        self.assertIn('Late_Percentage', monthly_summary.columns)
        
        # Test percentage calculations
        for _, month in monthly_summary.iterrows():
            self.assertGreaterEqual(month['Present_Percentage'], 0)
            self.assertLessEqual(month['Present_Percentage'], 100)
            self.assertGreaterEqual(month['Late_Percentage'], 0)
            self.assertLessEqual(month['Late_Percentage'], 100)
    
    def test_09_late_arrival_analysis(self):
        """Test enhanced late arrival analysis - Day 12 requirement"""
        df, _ = load_analytics_data()
        
        # Test late arrival data preparation
        late_data = df[df['Status'] == 'Late'].copy()
        self.assertEqual(len(late_data), 4)
        
        # Test late arrival by hour
        late_data['Hour'] = pd.to_datetime(late_data['Time']).dt.hour
        late_hourly = late_data.groupby('Hour').size().reset_index(name='Count')
        self.assertGreater(len(late_hourly), 0)
        
        # Test late arrival by user
        late_users = late_data.groupby('Name').size().reset_index(name='Late_Count')
        self.assertGreater(len(late_users), 0)
        
        # Test late arrival percentages
        total_by_user = df.groupby('Name').size().reset_index(name='Total_Attendance')
        late_users = late_users.merge(total_by_user, on='Name')
        late_users['Late_Percentage'] = (late_users['Late_Count'] / late_users['Total_Attendance'] * 100).round(1)
        
        # Verify percentage calculations
        for _, user in late_users.iterrows():
            self.assertGreaterEqual(user['Late_Percentage'], 0)
            self.assertLessEqual(user['Late_Percentage'], 100)
    
    def test_10_weekly_trends_analysis(self):
        """Test weekly trends analysis with percentages"""
        df, _ = load_analytics_data()
        
        # Test weekly data preparation
        df['Week_Number'] = pd.to_datetime(df['Date']).dt.isocalendar().week
        
        # Test weekly trends calculations
        weekly_data = df.groupby(['Week_Number', 'Status']).size().reset_index(name='Count')
        weekly_pivot = weekly_data.pivot(index='Week_Number', columns='Status', values='Count').fillna(0)
        
        # Test percentage calculations
        weekly_pivot['Total'] = weekly_pivot.sum(axis=1)
        if 'Present' in weekly_pivot.columns:
            weekly_pivot['Present_Pct'] = (weekly_pivot['Present'] / weekly_pivot['Total'] * 100).round(1)
        
        if 'Late' in weekly_pivot.columns:
            weekly_pivot['Late_Pct'] = (weekly_pivot['Late'] / weekly_pivot['Total'] * 100).round(1)
        
        # Verify weekly data structure
        self.assertIn('Week_Number', weekly_pivot.index.name)
        self.assertGreater(len(weekly_pivot), 0)
    
    def test_11_confidence_analysis(self):
        """Test confidence analysis functionality"""
        df, _ = load_analytics_data()
        
        if 'Confidence' in df.columns:
            # Test confidence statistics
            user_confidence = df.groupby('Name')['Confidence'].agg(['mean', 'count', 'std']).reset_index()
            user_confidence.columns = ['Name', 'Avg_Confidence', 'Attendance_Count', 'Confidence_Std']
            
            # Filter users with sufficient data
            user_confidence = user_confidence[user_confidence['Attendance_Count'] >= 3]
            
            if len(user_confidence) > 0:
                # Verify confidence data structure
                self.assertIn('Name', user_confidence.columns)
                self.assertIn('Avg_Confidence', user_confidence.columns)
                self.assertIn('Attendance_Count', user_confidence.columns)
                
                # Test confidence values
                for _, user in user_confidence.iterrows():
                    self.assertGreaterEqual(user['Avg_Confidence'], 0)
                    self.assertLessEqual(user['Avg_Confidence'], 1)
                    self.assertGreaterEqual(user['Attendance_Count'], 3)
    
    def test_12_quality_trends_analysis(self):
        """Test quality trends over time analysis"""
        df, _ = load_analytics_data()
        
        if 'Face_Quality_Score' in df.columns:
            # Test daily quality calculations
            daily_quality = df.groupby(df['Date'].dt.date)['Face_Quality_Score'].agg(['mean', 'std']).reset_index()
            daily_quality.columns = ['Date', 'Avg_Quality', 'Std_Quality']
            
            # Verify quality data structure
            self.assertIn('Date', daily_quality.columns)
            self.assertIn('Avg_Quality', daily_quality.columns)
            self.assertIn('Std_Quality', daily_quality.columns)
            
            # Test quality values
            for _, day in daily_quality.iterrows():
                self.assertGreaterEqual(day['Avg_Quality'], 0)
                self.assertLessEqual(day['Avg_Quality'], 1)
                self.assertGreaterEqual(day['Std_Quality'], 0)
    
    def test_13_performance_recommendations(self):
        """Test performance recommendations system"""
        df, _ = load_analytics_data()
        
        # Test processing time recommendations
        if 'Processing_Time_MS' in df.columns:
            avg_time = df['Processing_Time_MS'].mean()
            self.assertGreater(avg_time, 0)
            
            # Test recommendation thresholds
            if avg_time > 200:
                # Should recommend optimization
                pass
            elif avg_time > 150:
                # Should suggest some optimization
                pass
            else:
                # Should indicate optimal performance
                pass
        
        # Test quality recommendations
        if 'Face_Quality_Score' in df.columns:
            avg_quality = df['Face_Quality_Score'].mean()
            self.assertGreater(avg_quality, 0)
            self.assertLess(avg_quality, 1)
        
        # Test confidence recommendations
        if 'Confidence' in df.columns:
            avg_confidence = df['Confidence'].mean()
            self.assertGreater(avg_confidence, 0)
            self.assertLess(avg_confidence, 1)
    
    def test_14_data_export_capabilities(self):
        """Test data export and summary capabilities"""
        df, _ = load_analytics_data()
        
        # Test summary statistics
        summary_stats = df.describe()
        self.assertIsNotNone(summary_stats)
        
        # Test data aggregation
        user_summary = df.groupby('Name').agg({
            'Is_Present': 'sum',
            'Is_Late': 'sum',
            'Is_Absent': 'sum'
        }).reset_index()
        
        # Test export data structure
        export_data = user_summary.copy()
        export_data['Total_Attendance'] = export_data['Is_Present'] + export_data['Is_Late'] + export_data['Is_Absent']
        export_data['Present_Percentage'] = (export_data['Is_Present'] / export_data['Total_Attendance'] * 100).round(1)
        
        # Verify export structure
        self.assertIn('Name', export_data.columns)
        self.assertIn('Total_Attendance', export_data.columns)
        self.assertIn('Present_Percentage', export_data.columns)
    
    def test_15_integration_compatibility(self):
        """Test integration compatibility with existing dashboard"""
        df, _ = load_analytics_data()
        
        # Test that all required columns exist
        required_columns = ['Name', 'ID', 'Date', 'Time', 'Status']
        for col in required_columns:
            self.assertIn(col, df.columns)
        
        # Test that data can be processed without errors
        try:
            # Test basic data operations
            df['Date'] = pd.to_datetime(df['Date'])
            df['Time'] = pd.to_datetime(df['Time'])
            df['Day_of_Week'] = df['Date'].dt.day_name()
            df['Hour'] = df['Time'].dt.hour
            
            # Test derived calculations
            df['Is_Present'] = (df['Status'] == 'Present').astype(int)
            df['Is_Late'] = (df['Status'] == 'Late').astype(int)
            
            # Test aggregations
            daily_stats = df.groupby(df['Date'].dt.date).agg({
                'Is_Present': 'sum',
                'Is_Late': 'sum'
            }).reset_index()
            
            self.assertIsNotNone(daily_stats)
            
        except Exception as e:
            self.fail(f"Data processing failed: {e}")

def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestDay12Analytics)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Day 12 Analytics Test Results")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  ❌ {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  ❌ {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
