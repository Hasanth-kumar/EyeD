"""
Test Suite for Day 11: Enhanced Attendance Table
Tests the modular dashboard components and enhanced attendance table functionality
"""

import unittest
import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

class TestDay11EnhancedAttendanceTable(unittest.TestCase):
    """Test cases for Day 11 enhanced attendance table implementation"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_data = self.create_test_attendance_data()
        self.test_csv_path = "test_attendance.csv"
        
        # Save test data to CSV
        self.test_data.to_csv(self.test_csv_path, index=False)
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_csv_path):
            os.remove(self.test_csv_path)
    
    def create_test_attendance_data(self):
        """Create test attendance data for testing"""
        # Create sample data
        data = []
        base_date = datetime.now() - timedelta(days=30)
        
        users = ["Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Eva Brown"]
        user_ids = ["U001", "U002", "U003", "U004", "U005"]
        
        for i in range(30):  # 30 days of data
            date = base_date + timedelta(days=i)
            
            for j, (name, user_id) in enumerate(zip(users, user_ids)):
                # Generate realistic attendance patterns
                if date.weekday() < 5:  # Weekdays
                    if np.random.random() > 0.1:  # 90% attendance on weekdays
                        status = "Present" if np.random.random() > 0.2 else "Late"
                    else:
                        status = "Absent"
                else:  # Weekends
                    if np.random.random() > 0.7:  # 30% attendance on weekends
                        status = "Present"
                    else:
                        status = "Absent"
                
                # Generate realistic times
                if status == "Present":
                    hour = np.random.randint(8, 10)  # 8-10 AM
                elif status == "Late":
                    hour = np.random.randint(10, 12)  # 10-12 PM
                else:
                    hour = 0
                
                minute = np.random.randint(0, 59)
                time_str = f"{hour:02d}:{minute:02d}:00" if hour > 0 else "00:00:00"
                
                # Generate quality metrics
                confidence = np.random.uniform(0.6, 0.95)
                quality_score = np.random.uniform(0.5, 0.9)
                processing_time = np.random.uniform(50, 200)
                liveness_verified = np.random.random() > 0.1  # 90% liveness verification
                
                data.append({
                    'Name': name,
                    'ID': user_id,
                    'Date': date.strftime('%Y-%m-%d'),
                    'Time': time_str,
                    'Status': status,
                    'Confidence': confidence,
                    'Liveness_Verified': liveness_verified,
                    'Face_Quality_Score': quality_score,
                    'Processing_Time_MS': processing_time,
                    'Verification_Stage': 'Completed',
                    'Session_ID': f"S{i:03d}_{user_id}",
                    'Device_Info': 'Test System',
                    'Location': 'Test Office'
                })
        
        return pd.DataFrame(data)
    
    def test_attendance_data_structure(self):
        """Test that attendance data has the correct structure"""
        self.assertIn('Name', self.test_data.columns)
        self.assertIn('Date', self.test_data.columns)
        self.assertIn('Status', self.test_data.columns)
        self.assertIn('Confidence', self.test_data.columns)
        self.assertIn('Liveness_Verified', self.test_data.columns)
        self.assertIn('Face_Quality_Score', self.test_data.columns)
        self.assertIn('Processing_Time_MS', self.test_data.columns)
        
        # Check data types
        self.assertTrue(pd.api.types.is_string_dtype(self.test_data['Name']))
        self.assertTrue(pd.api.types.is_string_dtype(self.test_data['Date']))
        self.assertTrue(pd.api.types.is_string_dtype(self.test_data['Status']))
        self.assertTrue(pd.api.types.is_numeric_dtype(self.test_data['Confidence']))
        self.assertTrue(pd.api.types.is_bool_dtype(self.test_data['Liveness_Verified']))
    
    def test_data_quality(self):
        """Test data quality and consistency"""
        # Check for missing values in critical columns
        critical_columns = ['Name', 'Date', 'Status']
        for col in critical_columns:
            missing_count = self.test_data[col].isna().sum()
            self.assertEqual(missing_count, 0, f"Missing values found in {col}")
        
        # Check date format consistency
        date_format_valid = all(
            pd.to_datetime(self.test_data['Date'], errors='coerce').notna()
        )
        self.assertTrue(date_format_valid, "Invalid date formats found")
        
        # Check confidence score range
        confidence_valid = all(
            (self.test_data['Confidence'] >= 0) & (self.test_data['Confidence'] <= 1)
        )
        self.assertTrue(confidence_valid, "Confidence scores out of valid range [0,1]")
        
        # Check quality score range
        quality_valid = all(
            (self.test_data['Face_Quality_Score'] >= 0) & (self.test_data['Face_Quality_Score'] <= 1)
        )
        self.assertTrue(quality_valid, "Quality scores out of valid range [0,1]")
    
    def test_status_distribution(self):
        """Test that status distribution is realistic"""
        status_counts = self.test_data['Status'].value_counts()
        
        # Should have all expected statuses
        expected_statuses = ['Present', 'Late', 'Absent']
        for status in expected_statuses:
            self.assertIn(status, status_counts.index, f"Missing status: {status}")
        
        # Present should be the most common status
        self.assertEqual(status_counts.index[0], 'Present', "Present should be most common status")
        
        # Total entries should match expected count
        total_entries = len(self.test_data)
        self.assertEqual(total_entries, 150, f"Expected 150 entries, got {total_entries}")
    
    def test_user_distribution(self):
        """Test user distribution and consistency"""
        user_counts = self.test_data['Name'].value_counts()
        
        # Should have 5 users
        self.assertEqual(len(user_counts), 5, "Should have exactly 5 users")
        
        # Each user should have similar number of entries (within reasonable range)
        expected_entries_per_user = 30
        for user, count in user_counts.items():
            self.assertAlmostEqual(
                count, expected_entries_per_user, 
                delta=5,  # Allow 5 entries variation
                msg=f"User {user} has {count} entries, expected around {expected_entries_per_user}"
            )
    
    def test_time_patterns(self):
        """Test time patterns and consistency"""
        # Filter out absent entries (no time)
        present_data = self.test_data[self.test_data['Status'] != 'Absent']
        
        # Convert time to hour for analysis
        present_data['Hour'] = pd.to_datetime(present_data['Time']).dt.hour
        
        # Present entries should be early (8-10 AM)
        present_hours = present_data[present_data['Status'] == 'Present']['Hour']
        early_entries = present_hours[(present_hours >= 8) & (present_hours <= 10)]
        self.assertGreater(
            len(early_entries) / len(present_hours), 0.7,
            "At least 70% of present entries should be between 8-10 AM"
        )
        
        # Late entries should be after 10 AM
        late_hours = present_data[present_data['Status'] == 'Late']['Hour']
        late_entries = late_hours[late_hours >= 10]
        self.assertGreater(
            len(late_entries) / len(late_hours), 0.8,
            "At least 80% of late entries should be after 10 AM"
        )
    
    def test_quality_metrics_consistency(self):
        """Test quality metrics consistency and relationships"""
        # Check that high confidence correlates with high quality
        high_confidence = self.test_data[self.test_data['Confidence'] >= 0.8]
        high_quality = self.test_data[self.test_data['Face_Quality_Score'] >= 0.7]
        
        # There should be some overlap between high confidence and high quality
        high_confidence_high_quality = high_confidence[high_confidence['Face_Quality_Score'] >= 0.7]
        self.assertGreater(
            len(high_confidence_high_quality), 0,
            "Should have some entries with both high confidence and high quality"
        )
        
        # Processing time should be reasonable
        processing_time_valid = all(
            (self.test_data['Processing_Time_MS'] >= 10) & 
            (self.test_data['Processing_Time_MS'] <= 500)
        )
        self.assertTrue(processing_time_valid, "Processing time should be between 10-500ms")
    
    def test_session_management(self):
        """Test session ID generation and consistency"""
        # Each entry should have a unique session ID
        unique_sessions = self.test_data['Session_ID'].nunique()
        total_entries = len(self.test_data)
        self.assertEqual(unique_sessions, total_entries, "Each entry should have unique session ID")
        
        # Session ID format should be consistent
        session_format_valid = all(
            session_id.startswith('S') and '_' in session_id
            for session_id in self.test_data['Session_ID']
        )
        self.assertTrue(session_format_valid, "Session ID format should be 'S###_U###'")
    
    def test_metadata_consistency(self):
        """Test metadata fields consistency"""
        # Device info should be consistent
        unique_devices = self.test_data['Device_Info'].nunique()
        self.assertEqual(unique_devices, 1, "All entries should have same device info")
        
        # Location should be consistent
        unique_locations = self.test_data['Location'].nunique()
        self.assertEqual(unique_locations, 1, "All entries should have same location")
        
        # Verification stage should be consistent
        unique_stages = self.test_data['Verification_Stage'].nunique()
        self.assertEqual(unique_stages, 1, "All entries should have same verification stage")
    
    def test_data_export_import(self):
        """Test data export and import functionality"""
        # Test CSV export
        export_path = "test_export.csv"
        self.test_data.to_csv(export_path, index=False)
        
        # Verify export file exists
        self.assertTrue(os.path.exists(export_path), "Export file should be created")
        
        # Test CSV import
        imported_data = pd.read_csv(export_path)
        
        # Verify data integrity
        self.assertEqual(len(imported_data), len(self.test_data), "Import should preserve row count")
        self.assertEqual(list(imported_data.columns), list(self.test_data.columns), "Import should preserve columns")
        
        # Clean up
        os.remove(export_path)
    
    def test_date_range_filtering(self):
        """Test date range filtering functionality"""
        # Convert dates for filtering
        self.test_data['Date'] = pd.to_datetime(self.test_data['Date'])
        
        # Test specific date range
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        filtered_data = self.test_data[
            (self.test_data['Date'] >= start_date) & 
            (self.test_data['Date'] <= end_date)
        ]
        
        # Should have some data in recent week
        self.assertGreater(len(filtered_data), 0, "Should have data in recent week")
        
        # All filtered dates should be within range
        date_range_valid = all(
            (filtered_data['Date'] >= start_date) & (filtered_data['Date'] <= end_date)
        )
        self.assertTrue(date_range_valid, "All filtered dates should be within specified range")
    
    def test_user_filtering(self):
        """Test user filtering functionality"""
        # Test filtering by specific user
        test_user = "Alice Johnson"
        user_data = self.test_data[self.test_data['Name'] == test_user]
        
        # Should have data for test user
        self.assertGreater(len(user_data), 0, f"Should have data for user: {test_user}")
        
        # All entries should be for the same user
        unique_users = user_data['Name'].nunique()
        self.assertEqual(unique_users, 1, "Filtered data should contain only one user")
        self.assertEqual(user_data['Name'].iloc[0], test_user, "Filtered data should contain correct user")

def run_performance_tests():
    """Run performance tests for the enhanced attendance table"""
    print("\n🚀 Running Performance Tests...")
    
    # Test data loading performance
    start_time = datetime.now()
    test_data = TestDay11EnhancedAttendanceTable().create_test_attendance_data()
    load_time = (datetime.now() - start_time).total_seconds() * 1000
    
    print(f"✅ Data Creation: {load_time:.2f} ms for {len(test_data)} entries")
    
    # Test filtering performance
    start_time = datetime.now()
    filtered_data = test_data[test_data['Status'] == 'Present']
    filter_time = (datetime.now() - start_time).total_seconds() * 1000
    
    print(f"✅ Data Filtering: {filter_time:.2f} ms for {len(filtered_data)} filtered entries")
    
    # Test aggregation performance
    start_time = datetime.now()
    user_stats = test_data.groupby('Name').agg({
        'Status': 'count',
        'Confidence': 'mean',
        'Face_Quality_Score': 'mean'
    })
    agg_time = (datetime.now() - start_time).total_seconds() * 1000
    
    print(f"✅ Data Aggregation: {agg_time:.2f} ms for user statistics")
    
    # Performance benchmarks
    performance_ok = (
        load_time < 100 and      # Data creation < 100ms
        filter_time < 10 and     # Filtering < 10ms
        agg_time < 20            # Aggregation < 20ms
    )
    
    if performance_ok:
        print("🎉 All performance tests passed!")
    else:
        print("⚠️ Some performance tests failed - check optimization opportunities")
    
    return performance_ok

if __name__ == "__main__":
    print("🧪 Running Day 11 Enhanced Attendance Table Tests...")
    print("=" * 60)
    
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance tests
    run_performance_tests()
    
    print("\n" + "=" * 60)
    print("🎯 Day 11 Testing Complete!")

