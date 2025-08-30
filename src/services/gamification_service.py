"""
Gamification Service for EyeD AI Attendance System

This module handles gamification operations with clear separation of concerns.
Following SRP: Each method has a single, focused responsibility.
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
import logging
import pandas as pd

from ..repositories.attendance_repository import AttendanceRepository
from ..interfaces.face_database_interface import FaceDatabaseInterface

logger = logging.getLogger(__name__)


class GamificationService:
    """
    Service for gamification operations.
    
    Responsibilities:
    - Badge calculation and management
    - Leaderboard generation
    - Achievement progress tracking
    - Timeline analysis and insights
    """
    
    def __init__(self, 
                 attendance_repository: AttendanceRepository,
                 face_database: FaceDatabaseInterface):
        """Initialize gamification service with dependencies"""
        self.attendance_repository = attendance_repository
        self.face_database = face_database
        self.badge_definitions = self._initialize_badge_definitions()
        logger.info("Gamification service initialized successfully")
    
    # ============================================================================
    # BADGE MANAGEMENT METHODS
    # ============================================================================
    
    def calculate_user_badges(self, user_id: str, period_days: int = 30) -> Dict[str, Any]:
        """Calculate all badges for a specific user"""
        try:
            # Get user attendance data
            attendance_data = self._get_user_attendance_data(user_id, period_days)
            if not attendance_data:
                return {'success': False, 'error': f'No attendance data found for user {user_id}'}
            
            # Calculate badges for each category
            all_badges = {
                'attendance': self._calculate_attendance_badges(attendance_data, period_days),
                'streak': self._calculate_streak_badges(attendance_data),
                'timing': self._calculate_timing_badges(attendance_data),
                'quality': self._calculate_quality_badges(attendance_data)
            }
            
            # Calculate summary metrics
            total_badges = sum(len(badges) for badges in all_badges.values())
            badge_score = self._calculate_badge_score(all_badges)
            
            # Get user info
            user_name = self._get_user_name(user_id)
            
            return {
                'success': True,
                'user_id': user_id,
                'user_name': user_name,
                'period_days': period_days,
                'badges': all_badges,
                'total_badges': total_badges,
                'badge_score': badge_score,
                'badge_summary': self._generate_badge_summary(all_badges),
                'calculated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Badge calculation failed for user {user_id}: {e}")
            return {'success': False, 'error': f'Badge calculation failed: {str(e)}'}
    
    def get_leaderboard(self, metric: str = "total_badges", limit: int = 10, period_days: int = 30) -> Dict[str, Any]:
        """Get leaderboard based on specified metric"""
        try:
            all_users = self.face_database.get_all_users()
            if not all_users.success:
                return {'success': False, 'error': f'Failed to get users: {all_users.error}'}
            
            # Calculate metrics for each user
            user_rankings = []
            for user in all_users.data:
                user_id = user['user_id']
                score = self._calculate_user_metric(user_id, metric, period_days)
                
                user_rankings.append({
                    'user_id': user_id,
                    'user_name': user.get('user_name', user_id),
                    'score': score,
                    'rank': 0
                })
            
            # Sort and rank users
            user_rankings.sort(key=lambda x: x['score'], reverse=True)
            for i, user in enumerate(user_rankings):
                user['rank'] = i + 1
            
            return {
                'success': True,
                'leaderboard': {
                    'metric': metric,
                    'period_days': period_days,
                    'total_users': len(user_rankings),
                    'rankings': user_rankings[:limit],
                    'generated_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Leaderboard generation failed: {e}")
            return {'success': False, 'error': f'Leaderboard generation failed: {str(e)}'}
    
    def get_user_progress(self, user_id: str, period_days: int = 30) -> Dict[str, Any]:
        """Get comprehensive progress summary for a user"""
        try:
            attendance_data = self._get_user_attendance_data(user_id, period_days)
            if not attendance_data:
                return {'success': False, 'error': f'No attendance data found for user {user_id}'}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(attendance_data)
            
            # Generate progress data
            progress_data = {
                'user_id': user_id,
                'user_name': self._get_user_name(user_id),
                'period_days': period_days,
                'timeline_data': self._generate_timeline_data(df, user_id),
                'arrival_patterns': self._analyze_arrival_patterns(df),
                'insights': self._generate_timeline_insights(df),
                'progress_summary': self._calculate_progress_summary(df),
                'generated_at': datetime.now().isoformat()
            }
            
            return {'success': True, 'progress_data': progress_data}
            
        except Exception as e:
            logger.error(f"Progress generation failed for user {user_id}: {e}")
            return {'success': False, 'error': f'Progress generation failed: {str(e)}'}
    
    # ============================================================================
    # PRIVATE HELPER METHODS - BADGE CALCULATIONS
    # ============================================================================
    
    def _initialize_badge_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize badge definitions and criteria"""
        return {
            'attendance': {
                'perfect_week': {'name': '🌟 Perfect Week', 'criteria': 5, 'type': 'weekly'},
                'perfect_month': {'name': '🏆 Perfect Month', 'criteria': 20, 'type': 'monthly'},
                'consistency_master': {'name': '📅 Consistency Master', 'criteria': 50, 'type': 'total'},
                'dedication_champion': {'name': '💪 Dedication Champion', 'criteria': 100, 'type': 'total'}
            },
            'streak': {
                'week_warrior': {'name': '🔥 Week Warrior', 'criteria': 7, 'type': 'consecutive'},
                'month_master': {'name': '📆 Month Master', 'criteria': 30, 'type': 'consecutive'},
                'streak_legend': {'name': '⚡ Streak Legend', 'criteria': 60, 'type': 'consecutive'}
            },
            'timing': {
                'early_bird': {'name': '🐦 Early Bird', 'criteria': 5, 'type': 'early_arrivals'},
                'punctuality_pro': {'name': '⏰ Punctuality Pro', 'criteria': 10, 'type': 'on_time'},
                'time_master': {'name': '⌚ Time Master', 'criteria': 20, 'type': 'consistent_timing'}
            },
            'quality': {
                'quality_seeker': {'name': '📸 Quality Seeker', 'criteria': 5, 'type': 'high_quality'},
                'quality_master': {'name': '🎯 Quality Master', 'criteria': 15, 'type': 'high_quality'},
                'perfectionist': {'name': '✨ Perfectionist', 'criteria': 30, 'type': 'high_quality'}
            }
        }
    
    def _calculate_attendance_badges(self, attendance_data: List, period_days: int) -> List[Dict[str, Any]]:
        """Calculate attendance-based badges"""
        badges = []
        try:
            total_entries = len(attendance_data)
            
            # Check perfect week badge (5 entries in a week)
            if period_days >= 7 and total_entries >= 5:
                badges.append({
                    'name': self.badge_definitions['attendance']['perfect_week']['name'],
                    'category': 'attendance',
                    'earned_at': datetime.now().isoformat(),
                    'criteria_met': {'total_entries': total_entries, 'required_count': 5}
                })
            
            # Check perfect month badge (20 entries in a month)
            if period_days >= 30 and total_entries >= 20:
                badges.append({
                    'name': self.badge_definitions['attendance']['perfect_month']['name'],
                    'category': 'attendance',
                    'earned_at': datetime.now().isoformat(),
                    'criteria_met': {'total_entries': total_entries, 'required_count': 20}
                })
            
            # Check consistency master badge (50 total entries)
            if total_entries >= 50:
                badges.append({
                    'name': self.badge_definitions['attendance']['consistency_master']['name'],
                    'category': 'attendance',
                    'earned_at': datetime.now().isoformat(),
                    'criteria_met': {'total_entries': total_entries, 'required_count': 50}
                })
            
            # Check dedication champion badge (100 total entries)
            if total_entries >= 100:
                badges.append({
                    'name': self.badge_definitions['attendance']['dedication_champion']['name'],
                    'category': 'attendance',
                    'earned_at': datetime.now().isoformat(),
                    'criteria_met': {'total_entries': total_entries, 'required_count': 100}
                })
            
            return badges
            
        except Exception as e:
            logger.error(f"Attendance badge calculation failed: {e}")
            return []
    
    def _calculate_streak_badges(self, attendance_data: List) -> List[Dict[str, Any]]:
        """Calculate streak-based badges"""
        badges = []
        try:
            if not attendance_data:
                return badges
            
            # Sort by date to calculate streaks
            sorted_data = sorted(attendance_data, key=lambda x: x.date)
            
            # Calculate current streak
            current_streak = 0
            max_streak = 0
            temp_streak = 0
            
            for i, entry in enumerate(sorted_data):
                if i == 0:
                    temp_streak = 1
                    continue
                
                # Check if consecutive days
                prev_date = sorted_data[i-1].date
                curr_date = entry.date
                
                try:
                    prev_dt = datetime.strptime(prev_date, '%Y-%m-%d').date()
                    curr_dt = datetime.strptime(curr_date, '%Y-%m-%d').date()
                    
                    if (curr_dt - prev_dt).days == 1:
                        temp_streak += 1
                    else:
                        max_streak = max(max_streak, temp_streak)
                        temp_streak = 1
                except:
                    continue
            
            # Update max streak with final temp streak
            max_streak = max(max_streak, temp_streak)
            
            # Check week warrior badge (7 consecutive days)
            if max_streak >= 7:
                badges.append({
                    'name': self.badge_definitions['streak']['week_warrior']['name'],
                    'category': 'streak',
                    'earned_at': datetime.now().isoformat(),
                    'criteria_met': {'max_streak': max_streak, 'required_count': 7}
                })
            
            # Check month master badge (30 consecutive days)
            if max_streak >= 30:
                badges.append({
                    'name': self.badge_definitions['streak']['month_master']['name'],
                    'category': 'streak',
                    'earned_at': datetime.now().isoformat(),
                    'criteria_met': {'max_streak': max_streak, 'required_count': 30}
                })
            
            # Check streak legend badge (60 consecutive days)
            if max_streak >= 60:
                badges.append({
                    'name': self.badge_definitions['streak']['streak_legend']['name'],
                    'category': 'streak',
                    'earned_at': datetime.now().isoformat(),
                    'criteria_met': {'max_streak': max_streak, 'required_count': 60}
                })
            
            return badges
            
        except Exception as e:
            logger.error(f"Streak badge calculation failed: {e}")
            return []
    
    def _calculate_timing_badges(self, attendance_data: List) -> List[Dict[str, Any]]:
        """Calculate timing-based badges"""
        badges = []
        try:
            if not attendance_data:
                return badges
            
            # Analyze arrival times
            arrival_hours = []
            for entry in attendance_data:
                if hasattr(entry, 'time') and entry.time:
                    try:
                        hour = datetime.strptime(entry.time, '%H:%M:%S').hour
                        arrival_hours.append(hour)
                    except:
                        continue
            
            if not arrival_hours:
                return badges
            
            # Check early bird badge
            early_bird_count = len([h for h in arrival_hours if h <= 8])
            if early_bird_count >= 5:
                badges.append({
                    'name': self.badge_definitions['timing']['early_bird']['name'],
                    'category': 'timing',
                    'earned_at': datetime.now().isoformat(),
                    'criteria_met': {'early_arrivals': early_bird_count, 'required_count': 5}
                })
            
            return badges
            
        except Exception as e:
            logger.error(f"Timing badge calculation failed: {e}")
            return []
    
    def _calculate_quality_badges(self, attendance_data: List) -> List[Dict[str, Any]]:
        """Calculate quality-based badges"""
        badges = []
        try:
            if not attendance_data:
                return badges
            
            # Count high-quality entries
            high_quality_count = 0
            for entry in attendance_data:
                if hasattr(entry, 'face_quality_score') and entry.face_quality_score:
                    if entry.face_quality_score >= 0.8:
                        high_quality_count += 1
            
            # Check quality master badge
            if high_quality_count >= 10:
                badges.append({
                    'name': self.badge_definitions['quality']['quality_master']['name'],
                    'category': 'quality',
                    'earned_at': datetime.now().isoformat(),
                    'criteria_met': {'high_quality_entries': high_quality_count, 'required_count': 10}
                })
            
            return badges
            
        except Exception as e:
            logger.error(f"Quality badge calculation failed: {e}")
            return []
    
    # ============================================================================
    # PRIVATE HELPER METHODS - UTILITY FUNCTIONS
    # ============================================================================
    
    def _get_user_attendance_data(self, user_id: str, period_days: int) -> List:
        """Get user attendance data for specified period"""
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)
        
        return self.attendance_repository.get_attendance_history(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
    
    def _get_user_name(self, user_id: str) -> str:
        """Get user name from face database"""
        user_info = self.face_database.get_user_info(user_id)
        return user_info.data.get('user_name', user_id) if user_info.success else user_id
    
    def _calculate_user_metric(self, user_id: str, metric: str, period_days: int) -> float:
        """Calculate user metric for leaderboard ranking"""
        if metric == "attendance_rate":
            return self._calculate_attendance_rate(user_id, period_days)
        elif metric == "streak":
            return self._calculate_current_streak(user_id)
        else:
            return 0.0
    
    def _calculate_attendance_rate(self, user_id: str, period_days: int) -> float:
        """Calculate attendance rate for a user over a period"""
        try:
            attendance_data = self._get_user_attendance_data(user_id, period_days)
            if not attendance_data:
                return 0.0
            
            # Count unique days with attendance
            unique_days = set()
            for entry in attendance_data:
                if hasattr(entry, 'date') and entry.date:
                    unique_days.add(entry.date)
            
            # Calculate attendance rate
            attendance_rate = (len(unique_days) / period_days) * 100
            return min(attendance_rate, 100.0)  # Cap at 100%
            
        except Exception as e:
            logger.error(f"Attendance rate calculation failed for user {user_id}: {e}")
            return 0.0
    
    def _calculate_current_streak(self, user_id: str) -> int:
        """Calculate current consecutive attendance streak for a user"""
        try:
            attendance_data = self._get_user_attendance_data(user_id, 90)  # Last 90 days
            if not attendance_data:
                return 0
            
            return self._calculate_current_streak_from_data(attendance_data)
            
        except Exception as e:
            logger.error(f"Current streak calculation failed for user {user_id}: {e}")
            return 0
    
    def _calculate_current_streak_from_data(self, attendance_data: List) -> int:
        """Calculate current streak from attendance data"""
        try:
            if not attendance_data:
                return 0
            
            # Sort by date (most recent first)
            sorted_data = sorted(attendance_data, key=lambda x: x.date, reverse=True)
            
            # Calculate current streak
            current_streak = 0
            current_date = date.today()
            
            for entry in sorted_data:
                if not hasattr(entry, 'date') or not entry.date:
                    continue
                
                try:
                    entry_date = datetime.strptime(entry.date, '%Y-%m-%d').date()
                    
                    # Check if this entry is for the current date or consecutive
                    if entry_date == current_date:
                        current_streak += 1
                        current_date = current_date - timedelta(days=1)
                    elif entry_date == current_date + timedelta(days=1):
                        # Found a gap, streak continues
                        current_date = entry_date
                        current_streak += 1
                    else:
                        # Streak broken
                        break
                        
                except Exception:
                    continue
            
            return current_streak
            
        except Exception as e:
            logger.error(f"Streak calculation from data failed: {e}")
            return 0
    
    def _calculate_badge_score(self, all_badges: Dict[str, List]) -> int:
        """Calculate total badge score"""
        try:
            score = 0
            for category, badges in all_badges.items():
                score += len(badges) * 10  # 10 points per badge
            return score
        except Exception as e:
            logger.error(f"Badge score calculation failed: {e}")
            return 0
    
    def _generate_badge_summary(self, all_badges: Dict[str, List]) -> Dict[str, Any]:
        """Generate summary of earned badges"""
        try:
            summary = {
                'total_badges': 0,
                'category_breakdown': {},
                'recent_badges': [],
                'top_category': None
            }
            
            # Calculate totals
            for category, badges in all_badges.items():
                summary['total_badges'] += len(badges)
                summary['category_breakdown'][category] = len(badges)
            
            # Find top category
            if summary['category_breakdown']:
                summary['top_category'] = max(summary['category_breakdown'], 
                                           key=summary['category_breakdown'].get)
            
            # Get recent badges (last 5)
            all_badges_flat = []
            for category, badges in all_badges.items():
                for badge in badges:
                    all_badges_flat.append({
                        'name': badge['name'],
                        'category': category,
                        'earned_at': badge['earned_at']
                    })
            
            # Sort by earned date and take last 5
            all_badges_flat.sort(key=lambda x: x['earned_at'], reverse=True)
            summary['recent_badges'] = all_badges_flat[:5]
            
            return summary
            
        except Exception as e:
            logger.error(f"Badge summary generation failed: {e}")
            return {}
    
    # ============================================================================
    # PRIVATE HELPER METHODS - TIMELINE AND ANALYSIS
    # ============================================================================
    
    def _generate_timeline_data(self, df: pd.DataFrame, user_id: Optional[str]) -> List[Dict[str, Any]]:
        """Generate timeline data for visualization"""
        try:
            timeline_data = []
            
            for _, row in df.iterrows():
                entry = {
                    'date': row['Date'],
                    'time': row['Time'],
                    'user_id': row['ID'],
                    'user_name': row['Name'],
                    'status': row['Status'],
                    'confidence': row.get('Confidence', 0),
                    'quality_score': row.get('Face_Quality_Score', 0)
                }
                timeline_data.append(entry)
            
            return timeline_data
            
        except Exception as e:
            logger.error(f"Timeline data generation failed: {e}")
            return []
    
    def _analyze_arrival_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze arrival time patterns"""
        try:
            if 'Time' not in df.columns:
                return {}
            
            # Convert time to hour
            df['Hour'] = pd.to_datetime(df['Time']).dt.hour
            df['Minute'] = pd.to_datetime(df['Time']).dt.minute
            
            # Calculate arrival time in minutes since midnight
            df['Minutes_Since_Midnight'] = df['Hour'] * 60 + df['Minute']
            
            # Analyze patterns
            patterns = {
                'average_arrival_time': df['Minutes_Since_Midnight'].mean(),
                'earliest_arrival': df['Minutes_Since_Midnight'].min(),
                'latest_arrival': df['Minutes_Since_Midnight'].max(),
                'arrival_distribution': df['Hour'].value_counts().sort_index().to_dict(),
                'early_bird_count': len(df[df['Hour'] <= 8]),
                'on_time_count': len(df[(df['Hour'] == 9) & (df['Minute'] <= 15)]),
                'late_count': len(df[(df['Hour'] > 9) | ((df['Hour'] == 9) & (df['Minute'] > 15))])
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Arrival pattern analysis failed: {e}")
            return {}
    
    def _generate_timeline_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate insights from timeline analysis"""
        insights = []
        
        try:
            if 'Time' not in df.columns:
                return insights
            
            # Convert time to hour for analysis
            df['Hour'] = pd.to_datetime(df['Time']).dt.hour
            
            # Analyze arrival patterns
            early_bird_count = len(df[df['Hour'] <= 8])
            late_count = len(df[df['Hour'] > 9])
            on_time_count = len(df[(df['Hour'] == 9)])
            
            if early_bird_count > late_count:
                insights.append("You're mostly an early bird - great for productivity!")
            elif late_count > early_bird_count:
                insights.append("Consider arriving earlier to improve your attendance pattern")
            
            if on_time_count > 0:
                insights.append("Good on-time arrival consistency")
            
            return insights
            
        except Exception as e:
            logger.error(f"Timeline insight generation failed: {e}")
            return ["Unable to generate timeline insights due to data issues"]
    
    def _calculate_progress_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate progress summary from DataFrame"""
        try:
            summary = {
                'total_entries': len(df),
                'date_range': {
                    'start': df['Date'].min() if 'Date' in df.columns else None,
                    'end': df['Date'].max() if 'Date' in df.columns else None
                },
                'insights_count': len(self._generate_timeline_insights(df))
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Progress summary calculation failed: {e}")
            return {}
