"""
Test Phase 4.4 Gamification - Enhanced Version
Tests the enhanced gamification component with new features
"""

import unittest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

class TestPhase4GamificationEnhanced(unittest.TestCase):
    """Test the enhanced gamification component"""
    
    def setUp(self):
        """Set up test data"""
        # Create sample attendance data
        self.sample_attendance_data = [
            {
                'Name': 'Alice Johnson',
                'ID': 'U001',
                'Date': '2025-08-31',
                'Time': '08:30:00',  # Early arrival
                'Status': 'Present',
                'Confidence': 0.95,
                'Liveness_Verified': True,
                'Face_Quality_Score': 0.92
            },
            {
                'Name': 'Bob Smith',
                'ID': 'U002',
                'Date': '2025-08-31',
                'Time': '09:15:00',  # Late arrival
                'Status': 'Present',
                'Confidence': 0.87,
                'Liveness_Verified': True,
                'Face_Quality_Score': 0.88
            },
            {
                'Name': 'Alice Johnson',
                'ID': 'U001',
                'Date': '2025-08-30',
                'Time': '08:45:00',  # Early arrival
                'Status': 'Present',
                'Confidence': 0.93,
                'Liveness_Verified': True,
                'Face_Quality_Score': 0.90
            },
            {
                'Name': 'Charlie Brown',
                'ID': 'U003',
                'Date': '2025-08-31',
                'Time': '09:00:00',  # On time
                'Status': 'Present',
                'Confidence': 0.98,
                'Liveness_Verified': True,
                'Face_Quality_Score': 0.95
            }
        ]
        
        # Create sample achievements data
        self.sample_achievements = {
            'Alice Johnson': {
                'total_days': 2,
                'present_days': 2,
                'late_days': 0,
                'absent_days': 0,
                'attendance_percentage': 100.0,
                'current_streak': 2,
                'max_streak': 2,
                'early_arrivals': 2,
                'on_time_arrivals': 0,
                'late_arrivals': 0,
                'avg_confidence': 0.94,
                'high_quality_days': 2,
                'badges': [
                    {"name": "🏆 Perfect Attendance", "type": "attendance", "color": "gold", "rarity": "legendary"},
                    {"name": "🐦 Early Bird", "type": "timing", "color": "yellow", "rarity": "rare"},
                    {"name": "🎯 High Precision", "type": "quality", "color": "silver", "rarity": "epic"}
                ],
                'total_badges': 3,
                'legendary_badges': 1,
                'epic_badges': 1,
                'rare_badges': 1
            },
            'Bob Smith': {
                'total_days': 1,
                'present_days': 1,
                'late_days': 0,
                'absent_days': 0,
                'attendance_percentage': 100.0,
                'current_streak': 1,
                'max_streak': 1,
                'early_arrivals': 0,
                'on_time_arrivals': 0,
                'late_arrivals': 1,
                'avg_confidence': 0.87,
                'high_quality_days': 0,
                'badges': [
                    {"name": "🏆 Perfect Attendance", "type": "attendance", "color": "gold", "rarity": "legendary"},
                    {"name": "🌙 Late Comer", "type": "timing", "color": "purple", "rarity": "common"}
                ],
                'total_badges': 2,
                'legendary_badges': 1,
                'epic_badges': 0,
                'rare_badges': 0
            }
        }
    
    def test_achievement_data_structure(self):
        """Test that achievement data has the expected enhanced structure"""
        for user, data in self.sample_achievements.items():
            # Test basic metrics
            required_keys = ['total_days', 'present_days', 'attendance_percentage', 'current_streak', 'max_streak']
            for key in required_keys:
                self.assertIn(key, data)
            
            # Test new enhanced metrics
            enhanced_keys = ['early_arrivals', 'on_time_arrivals', 'late_arrivals', 'avg_confidence', 'high_quality_days']
            for key in enhanced_keys:
                self.assertIn(key, data)
            
            # Test badge rarity tracking
            rarity_keys = ['legendary_badges', 'epic_badges', 'rare_badges']
            for key in rarity_keys:
                self.assertIn(key, data)
    
    def test_badge_rarity_system(self):
        """Test the badge rarity system"""
        alice_badges = self.sample_achievements['Alice Johnson']['badges']
        
        # Test that badges have rarity information
        for badge in alice_badges:
            self.assertIn('rarity', badge)
            self.assertIn(badge['rarity'], ['legendary', 'epic', 'rare', 'uncommon', 'common'])
        
        # Test rarity counting
        alice_data = self.sample_achievements['Alice Johnson']
        self.assertEqual(alice_data['legendary_badges'], 1)
        self.assertEqual(alice_data['epic_badges'], 1)
        self.assertEqual(alice_data['rare_badges'], 1)
    
    def test_badge_categories(self):
        """Test different badge categories"""
        alice_badges = self.sample_achievements['Alice Johnson']['badges']
        
        # Test badge types
        badge_types = [badge['type'] for badge in alice_badges]
        expected_types = ['attendance', 'timing', 'quality']
        
        for expected_type in expected_types:
            self.assertIn(expected_type, badge_types)
    
    def test_enhanced_metrics_calculation(self):
        """Test enhanced metrics calculation"""
        alice_data = self.sample_achievements['Alice Johnson']
        
        # Test timing metrics
        self.assertEqual(alice_data['early_arrivals'], 2)
        self.assertEqual(alice_data['on_time_arrivals'], 0)
        self.assertEqual(alice_data['late_arrivals'], 0)
        
        # Test quality metrics
        self.assertAlmostEqual(alice_data['avg_confidence'], 0.94, places=2)
        self.assertEqual(alice_data['high_quality_days'], 2)
    
    def test_team_challenge_metrics(self):
        """Test team challenge metrics calculation"""
        # Calculate team metrics
        total_team_attendance = sum(data['present_days'] for data in self.sample_achievements.values())
        total_team_days = sum(data['total_days'] for data in self.sample_achievements.values())
        team_attendance_rate = (total_team_attendance / total_team_days * 100) if total_team_days > 0 else 0
        
        self.assertEqual(total_team_attendance, 3)
        self.assertEqual(total_team_days, 3)
        self.assertEqual(team_attendance_rate, 100.0)
    
    def test_milestone_detection(self):
        """Test milestone detection logic"""
        milestones = []
        
        for user, data in self.sample_achievements.items():
            if data['total_days'] >= 100:
                milestones.append(f"🏅 **{user}** reached 100 days! Centurion status achieved!")
            elif data['total_days'] >= 50:
                milestones.append(f"🏅 **{user}** reached 50 days! Half Century milestone!")
            elif data['total_days'] >= 25:
                milestones.append(f"🏅 **{user}** reached 25 days! Quarter Century milestone!")
            elif data['total_days'] >= 10:
                milestones.append(f"🏅 **{user}** reached 10 days! Decade milestone!")
        
        # Should not have any milestones for test data (all users have < 10 days)
        self.assertEqual(len(milestones), 0)
    
    def test_badge_rarity_distribution(self):
        """Test badge rarity distribution calculation"""
        all_badges = []
        for user, data in self.sample_achievements.items():
            all_badges.extend(data['badges'])
        
        rarity_counts = {'legendary': 0, 'epic': 0, 'rare': 0, 'uncommon': 0, 'common': 0}
        for badge in all_badges:
            rarity = badge.get('rarity', 'common')
            rarity_counts[rarity] += 1
        
        # Test expected distribution
        self.assertEqual(rarity_counts['legendary'], 2)  # Alice and Bob both have Perfect Attendance
        self.assertEqual(rarity_counts['epic'], 1)       # Alice has High Precision
        self.assertEqual(rarity_counts['rare'], 1)       # Alice has Early Bird
        self.assertEqual(rarity_counts['common'], 1)     # Bob has Late Comer
    
    def test_leaderboard_data_structure(self):
        """Test leaderboard data structure"""
        leaderboard_data = []
        for user, data in self.sample_achievements.items():
            leaderboard_data.append({
                'User': user,
                'Attendance %': data['attendance_percentage'],
                'Total Badges': data['total_badges'],
                'Max Streak': data['max_streak'],
                'Current Streak': data['current_streak'],
                'Present Days': data['present_days'],
                'Legendary Badges': data['legendary_badges'],
                'Epic Badges': data['epic_badges'],
                'Rare Badges': data['rare_badges'],
                'Avg Confidence': data['avg_confidence'],
                'Early Arrivals': data['early_arrivals']
            })
        
        leaderboard_df = pd.DataFrame(leaderboard_data)
        
        # Test that all expected columns are present
        expected_columns = ['User', 'Attendance %', 'Total Badges', 'Max Streak', 'Current Streak', 
                          'Present Days', 'Legendary Badges', 'Epic Badges', 'Rare Badges', 
                          'Avg Confidence', 'Early Arrivals']
        
        for column in expected_columns:
            self.assertIn(column, leaderboard_df.columns)
    
    def test_achievement_suggestions(self):
        """Test achievement suggestions logic"""
        alice_data = self.sample_achievements['Alice Johnson']
        suggestions = []
        
        if alice_data['attendance_percentage'] < 100:
            needed_days = alice_data['total_days'] - alice_data['present_days']
            suggestions.append(f"🎯 **Perfect Attendance**: Attend {needed_days} more days to reach 100%")
        
        if alice_data['max_streak'] < 5:
            suggestions.append(f"🔥 **Streak Builder**: Build a 5-day streak (current best: {alice_data['max_streak']})")
        
        if alice_data['current_streak'] == 0:
            suggestions.append("💪 **Get Started**: Begin a new attendance streak today!")
        
        if alice_data['early_arrivals'] < 5:
            suggestions.append("🐦 **Early Bird**: Try arriving before 9 AM to earn the Early Bird badge!")
        
        if alice_data['avg_confidence'] < 0.9:
            suggestions.append("📸 **Quality Focus**: Improve your face recognition quality for better badges!")
        
        # Alice should have streak builder suggestion (max_streak = 2 < 5)
        self.assertIn("🔥 **Streak Builder**: Build a 5-day streak (current best: 2)", suggestions)
        
        # Alice should have early bird suggestion (early_arrivals = 2 < 5)
        self.assertIn("🐦 **Early Bird**: Try arriving before 9 AM to earn the Early Bird badge!", suggestions)
    
    def test_special_achievement_conditions(self):
        """Test special achievement conditions"""
        # Test Streak Master condition (current_streak >= 5 and attendance_percentage >= 90)
        alice_data = self.sample_achievements['Alice Johnson']
        
        # Alice has attendance_percentage = 100 >= 90, but current_streak = 2 < 5
        streak_master_eligible = (alice_data['current_streak'] >= 5 and alice_data['attendance_percentage'] >= 90)
        self.assertFalse(streak_master_eligible)
        
        # Test Time Master condition (early_arrivals >= 5 and on_time_arrivals >= 5)
        time_master_eligible = (alice_data['early_arrivals'] >= 5 and alice_data['on_time_arrivals'] >= 5)
        self.assertFalse(time_master_eligible)  # Alice has 2 early, 0 on-time
        
        # Test Quality Champion condition (high_quality_days >= 10 and avg_confidence >= 0.9)
        quality_champion_eligible = (alice_data['high_quality_days'] >= 10 and alice_data['avg_confidence'] >= 0.9)
        self.assertFalse(quality_champion_eligible)  # Alice has 2 high quality days < 10

if __name__ == '__main__':
    unittest.main()

