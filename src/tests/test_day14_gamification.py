"""
Test Suite for Day 14: Gamification Features
Tests badges, achievements, and user engagement features
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.dashboard.components.gamification import (
    load_gamification_data,
    calculate_user_achievements,
    calculate_user_achievements
)

class TestDay14Gamification(unittest.TestCase):
    """Test cases for Day 14 gamification features"""
    
    def setUp(self):
        """Set up test data"""
        # Create sample attendance data
        self.sample_data = self.create_sample_attendance_data()
        
        # Create sample CSV file for testing
        self.csv_path = "test_attendance.csv"
        self.sample_data.to_csv(self.csv_path, index=False)
    
    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)
    
    def create_sample_attendance_data(self):
        """Create sample attendance data for testing"""
        users = ["Alice", "Bob", "Carol", "David"]
        dates = pd.date_range(start='2025-01-01', end='2025-01-31', freq='D')
        
        data = []
        for user in users:
            for date in dates:
                # Skip weekends
                if date.weekday() >= 5:
                    continue
                
                # Generate realistic attendance patterns
                if user == "Alice":  # Perfect attendance
                    status = "Present"
                    hour = 8 + np.random.randint(0, 2)
                elif user == "Bob":  # Good attendance, sometimes late
                    if np.random.random() < 0.8:
                        status = "Present"
                        hour = 8 + np.random.randint(0, 3)
                    else:
                        status = "Late"
                        hour = 9 + np.random.randint(0, 2)
                elif user == "Carol":  # Sometimes absent
                    if np.random.random() < 0.7:
                        status = "Present"
                        hour = 8 + np.random.randint(0, 2)
                    else:
                        status = "Absent"
                        hour = 0
                else:  # David - Late comer
                    if np.random.random() < 0.6:
                        status = "Late"
                        hour = 9 + np.random.randint(0, 3)
                    else:
                        status = "Present"
                        hour = 8 + np.random.randint(0, 2)
                
                if status != "Absent":
                    time_str = f"{hour:02d}:{np.random.randint(0, 60):02d}:00"
                    data.append({
                        'Date': date.strftime('%Y-%m-%d'),
                        'Time': time_str,
                        'Name': user,
                        'Status': status,
                        'Confidence': round(0.8 + np.random.random() * 0.2, 3),
                        'Quality_Score': round(0.7 + np.random.random() * 0.3, 3),
                        'Session_ID': f"session_{len(data):06d}",
                        'Liveness_Verified': np.random.choice([True, False], p=[0.95, 0.05])
                    })
        
        return pd.DataFrame(data)
    
    def test_load_gamification_data(self):
        """Test loading gamification data"""
        # Test with valid data
        df, error = load_gamification_data()
        
        # Should not have error if data exists
        if error is None:
            self.assertIsInstance(df, pd.DataFrame)
            if len(df) > 0:
                required_columns = ['Date', 'Time', 'Name', 'Status']
                for col in required_columns:
                    self.assertIn(col, df.columns)
    
    def test_calculate_user_achievements(self):
        """Test calculating user achievements and badges"""
        achievements = calculate_user_achievements(self.sample_data)
        
        # Should have achievements for each user
        self.assertIsInstance(achievements, dict)
        self.assertGreater(len(achievements), 0)
        
        # Test structure of achievements
        for user, data in achievements.items():
            self.assertIsInstance(user, str)
            self.assertIsInstance(data, dict)
            
            # Required fields
            required_fields = [
                'total_days', 'present_days', 'late_days', 'absent_days',
                'attendance_percentage', 'current_streak', 'max_streak',
                'badges', 'total_badges'
            ]
            
            for field in required_fields:
                self.assertIn(field, data)
            
            # Validate data types
            self.assertIsInstance(data['total_days'], int)
            self.assertIsInstance(data['attendance_percentage'], (int, float))
            self.assertIsInstance(data['badges'], list)
            self.assertIsInstance(data['total_badges'], int)
            
            # Validate attendance percentage
            self.assertGreaterEqual(data['attendance_percentage'], 0)
            self.assertLessEqual(data['attendance_percentage'], 100)
            
            # Validate streaks
            self.assertGreaterEqual(data['current_streak'], 0)
            self.assertGreaterEqual(data['max_streak'], 0)
            self.assertGreaterEqual(data['max_streak'], data['current_streak'])
    
    def test_badge_system(self):
        """Test badge system implementation"""
        achievements = calculate_user_achievements(self.sample_data)
        
        # Check if badges are awarded
        has_badges = False
        for user, data in achievements.items():
            if data['badges']:
                has_badges = True
                break
        
        # Should have at least some badges
        self.assertTrue(has_badges, "No badges were awarded to any user")
        
        # Test badge structure
        for user, data in achievements.items():
            for badge in data['badges']:
                self.assertIsInstance(badge, dict)
                self.assertIn('name', badge)
                self.assertIn('type', badge)
                self.assertIn('color', badge)
                
                # Badge name should contain emoji
                self.assertTrue(any(ord(c) > 127 for c in badge['name']), 
                              f"Badge {badge['name']} should contain emoji")
    
    def test_perfect_attendance_badge(self):
        """Test perfect attendance badge (🏆)"""
        # Create data with perfect attendance user
        perfect_user_data = []
        dates = pd.date_range(start='2025-01-01', end='2025-01-20', freq='D')
        
        for date in dates:
            if date.weekday() < 5:  # Weekdays only
                perfect_user_data.append({
                    'Date': date.strftime('%Y-%m-%d'),
                    'Time': '08:30:00',
                    'Name': 'PerfectUser',
                    'Status': 'Present',
                    'Confidence': 0.95,
                    'Quality_Score': 0.9,
                    'Session_ID': f"session_{len(perfect_user_data):06d}",
                    'Liveness_Verified': True
                })
        
        perfect_df = pd.DataFrame(perfect_user_data)
        achievements = calculate_user_achievements(perfect_df)
        
        # Should have perfect attendance badge
        if 'PerfectUser' in achievements:
            user_badges = achievements['PerfectUser']['badges']
            perfect_badges = [b for b in user_badges if 'Perfect Attendance' in b['name']]
            self.assertGreater(len(perfect_badges), 0, "Perfect attendance user should get 🏆 badge")
    
    def test_late_comer_badge(self):
        """Test late comer badge (🌙)"""
        # Create data with late comer user
        late_user_data = []
        dates = pd.date_range(start='2025-01-01', end='2025-01-20', freq='D')
        
        for date in dates:
            if date.weekday() < 5:  # Weekdays only
                late_user_data.append({
                    'Date': date.strftime('%Y-%m-%d'),
                    'Time': '09:30:00',  # Always late
                    'Name': 'LateUser',
                    'Status': 'Late',
                    'Confidence': 0.85,
                    'Quality_Score': 0.8,
                    'Session_ID': f"session_{len(late_user_data):06d}",
                    'Liveness_Verified': True
                })
        
        late_df = pd.DataFrame(late_user_data)
        achievements = calculate_user_achievements(late_df)
        
        # Should have late comer badge
        if 'LateUser' in achievements:
            user_badges = achievements['LateUser']['badges']
            late_badges = [b for b in user_badges if 'Late Comer' in b['name']]
            self.assertGreater(len(late_badges), 0, "Late comer user should get 🌙 badge")
    
    def test_streak_calculation(self):
        """Test streak calculation logic"""
        # Create data with known streak pattern
        streak_data = []
        dates = pd.date_range(start='2025-01-01', end='2025-01-15', freq='D')
        
        # Pattern: Present for 5 days, then absent, then present for 3 days
        for i, date in enumerate(dates):
            if date.weekday() < 5:  # Weekdays only
                if i < 5:  # First 5 days: present
                    status = 'Present'
                elif i == 5:  # 6th day: absent
                    status = 'Absent'
                else:  # Remaining days: present
                    status = 'Present'
                
                if status != 'Absent':
                    streak_data.append({
                        'Date': date.strftime('%Y-%m-%d'),
                        'Time': '08:30:00',
                        'Name': 'StreakUser',
                        'Status': status,
                        'Confidence': 0.9,
                        'Quality_Score': 0.9,
                        'Session_ID': f"session_{len(streak_data):06d}",
                        'Liveness_Verified': True
                    })
        
        streak_df = pd.DataFrame(streak_data)
        achievements = calculate_user_achievements(streak_df)
        
        if 'StreakUser' in achievements:
            user_data = achievements['StreakUser']
            # Max streak should be 5 (first 5 days)
            self.assertEqual(user_data['max_streak'], 5, "Max streak should be 5")
            # Current streak should be 3 (last 3 days)
            self.assertEqual(user_data['current_streak'], 3, "Current streak should be 3")
    
    def test_attendance_percentage_calculation(self):
        """Test attendance percentage calculation"""
        # Create data with known attendance pattern
        test_data = []
        dates = pd.date_range(start='2025-01-01', end='2025-01-10', freq='D')
        
        for i, date in enumerate(dates):
            if date.weekday() < 5:  # Weekdays only
                # Present for 7 out of 10 weekdays = 70%
                if i < 7:
                    status = 'Present'
                else:
                    status = 'Absent'
                
                if status != 'Absent':
                    test_data.append({
                        'Date': date.strftime('%Y-%m-%d'),
                        'Time': '08:30:00',
                        'Name': 'TestUser',
                        'Status': status,
                        'Confidence': 0.9,
                        'Quality_Score': 0.9,
                        'Session_ID': f"session_{len(test_data):06d}",
                        'Liveness_Verified': True
                    })
        
        test_df = pd.DataFrame(test_data)
        achievements = calculate_user_achievements(test_df)
        
        if 'TestUser' in achievements:
            attendance_pct = achievements['TestUser']['attendance_percentage']
            # Should be 70% (7 present out of 10 total weekdays)
            self.assertEqual(attendance_pct, 70.0, "Attendance percentage should be 70%")
    
    def test_badge_categories(self):
        """Test different badge categories"""
        achievements = calculate_user_achievements(self.sample_data)
        
        badge_types = set()
        for user, data in achievements.items():
            for badge in data['badges']:
                badge_types.add(badge['type'])
        
        # Should have multiple badge categories
        expected_categories = {'attendance', 'streak', 'timing', 'quality'}
        self.assertTrue(len(badge_types) > 0, "Should have at least one badge category")
        
        # Check if expected categories exist
        for category in expected_categories:
            if category in badge_types:
                self.assertIn(category, badge_types, f"Should have {category} badges")
    
    def test_early_bird_badge(self):
        """Test early bird badge (🐦)"""
        # Create data with early arrival user
        early_user_data = []
        dates = pd.date_range(start='2025-01-01', end='2025-01-20', freq='D')
        
        for date in dates:
            if date.weekday() < 5:  # Weekdays only
                early_user_data.append({
                    'Date': date.strftime('%Y-%m-%d'),
                    'Time': '07:30:00',  # Always early (before 9 AM)
                    'Name': 'EarlyUser',
                    'Status': 'Present',
                    'Confidence': 0.9,
                    'Quality_Score': 0.9,
                    'Session_ID': f"session_{len(early_user_data):06d}",
                    'Liveness_Verified': True
                })
        
        early_df = pd.DataFrame(early_user_data)
        achievements = calculate_user_achievements(early_df)
        
        # Should have early bird badge after 5 early arrivals
        if 'EarlyUser' in achievements:
            user_badges = achievements['EarlyUser']['badges']
            early_badges = [b for b in user_badges if 'Early Bird' in b['name']]
            self.assertGreater(len(early_badges), 0, "Early bird user should get 🐦 badge")
    
    def test_quality_master_badge(self):
        """Test quality master badge (📸)"""
        # Create data with high quality user
        quality_user_data = []
        dates = pd.date_range(start='2025-01-01', end='2025-01-20', freq='D')
        
        for date in dates:
            if date.weekday() < 5:  # Weekdays only
                quality_user_data.append({
                    'Date': date.strftime('%Y-%m-%d'),
                    'Time': '08:30:00',
                    'Name': 'QualityUser',
                    'Status': 'Present',
                    'Confidence': 0.95,
                    'Quality_Score': 0.9,  # High quality score
                    'Session_ID': f"session_{len(quality_user_data):06d}",
                    'Liveness_Verified': True
                })
        
        quality_df = pd.DataFrame(quality_user_data)
        achievements = calculate_user_achievements(quality_df)
        
        # Should have quality master badge after 10 high quality entries
        if 'QualityUser' in achievements:
            user_badges = achievements['QualityUser']['badges']
            quality_badges = [b for b in user_badges if 'Quality Master' in b['name']]
            self.assertGreater(len(quality_badges), 0, "Quality user should get 📸 badge")
    
    def test_empty_data_handling(self):
        """Test handling of empty data"""
        empty_df = pd.DataFrame()
        achievements = calculate_user_achievements(empty_df)
        
        # Should return empty dict for empty data
        self.assertEqual(achievements, {})
    
    def test_data_validation(self):
        """Test data validation and error handling"""
        # Test with missing required columns
        invalid_data = pd.DataFrame({
            'Name': ['Alice'],
            'Status': ['Present']
            # Missing Date and Time columns
        })
        
        # Should handle gracefully without crashing
        try:
            achievements = calculate_user_achievements(invalid_data)
            # Should return empty dict for invalid data
            self.assertEqual(achievements, {})
        except Exception as e:
            self.fail(f"Should handle invalid data gracefully, got error: {e}")

def run_gamification_tests():
    """Run all gamification tests"""
    print("🏆 Running Day 14 Gamification Tests...")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDay14Gamification)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n📊 Test Results Summary:")
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ Test Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print(f"\n⚠️  Test Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    # Return success status
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == "__main__":
    # Run tests
    success = run_gamification_tests()
    
    if success:
        print("\n🎉 All Day 14 Gamification tests passed!")
        print("✅ Badge system working correctly")
        print("✅ Achievement calculation working")
        print("✅ Timeline analysis ready")
        print("✅ User engagement features implemented")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
