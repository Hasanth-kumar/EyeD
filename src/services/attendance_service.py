"""
Attendance Service for EyeD AI Attendance System

This module orchestrates business logic for attendance operations,
following the Single-Responsibility Principle.
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any, Tuple
import logging
import pandas as pd

from ..repositories.attendance_repository import AttendanceRepository
from ..interfaces.attendance_manager_interface import AttendanceManagerInterface
from ..interfaces.recognition_interface import RecognitionInterface
from ..interfaces.liveness_interface import LivenessInterface

logger = logging.getLogger(__name__)


class AttendanceService:
    """Service for orchestrating attendance business logic"""
    
    def __init__(self, 
                 attendance_repository: AttendanceRepository,
                 attendance_manager: AttendanceManagerInterface,
                 recognition_system: RecognitionInterface,
                 liveness_system: LivenessInterface):
        """
        Initialize attendance service
        
        Args:
            attendance_repository: Repository for data persistence
            attendance_manager: Manager for attendance operations
            recognition_system: System for face recognition
            liveness_system: System for liveness detection
        """
        self.attendance_repository = attendance_repository
        self.attendance_manager = attendance_manager
        self.recognition_system = recognition_system
        self.liveness_system = liveness_system
        
        logger.info("Attendance service initialized successfully")
    
    def process_attendance_request(self, face_image, device_info: str = "", 
                                 location: str = "") -> Dict[str, Any]:
        """
        Process complete attendance request with recognition and liveness
        
        Args:
            face_image: Face image for processing
            device_info: Device information
            location: Location information
            
        Returns:
            Dictionary with attendance result
        """
        try:
            # Step 1: Face recognition
            recognition_result = self.recognition_system.recognize_face(face_image)
            
            if not recognition_result:
                return {
                    'success': False,
                    'error': 'Face not recognized',
                    'stage': 'recognition'
                }
            
            user_id = recognition_result.user_id
            user_name = recognition_result.user_name
            confidence = recognition_result.confidence
            
            # Step 2: Liveness verification
            liveness_result = self.liveness_system.detect_blink(face_image)
            
            if not liveness_result.is_live:
                return {
                    'success': False,
                    'error': 'Liveness verification failed',
                    'stage': 'liveness',
                    'user_id': user_id,
                    'user_name': user_name
                }
            
            # Step 3: Log attendance
            attendance_entry = self.attendance_manager.log_attendance(
                face_image=face_image,
                user_id=user_id,
                device_info=device_info,
                location=location
            )
            
            if not attendance_entry:
                return {
                    'success': False,
                    'error': 'Failed to log attendance',
                    'stage': 'logging',
                    'user_id': user_id,
                    'user_name': user_name
                }
            
            # Step 4: Store in repository
            success = self.attendance_repository.add_attendance(attendance_entry)
            
            if not success:
                return {
                    'success': False,
                    'error': 'Failed to persist attendance',
                    'stage': 'persistence',
                    'user_id': user_id,
                    'user_name': user_name
                }
            
            return {
                'success': True,
                'user_id': user_id,
                'user_name': user_name,
                'confidence': confidence,
                'liveness_verified': liveness_result.is_live,
                'attendance_logged': True,
                'session_id': attendance_entry.session_id
            }
            
        except Exception as e:
            logger.error(f"Attendance processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'stage': 'processing'
            }
    
    def get_attendance_report(self, start_date: Optional[date] = None,
                             end_date: Optional[date] = None,
                             user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive attendance report
        
        Args:
            start_date: Optional start date for report
            end_date: Optional end date for report
            user_id: Optional user ID to filter by
            
        Returns:
            Dictionary containing attendance report
        """
        try:
            # Get attendance data
            attendance_data = self.attendance_repository.get_attendance_history(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Get summary
            summary = self.attendance_repository.get_attendance_summary(
                target_date=start_date if start_date and not end_date else None
            )
            
            # Calculate additional metrics
            report = {
                'summary': summary,
                'attendance_data': attendance_data,
                'report_generated': datetime.now().isoformat(),
                'filters': {
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None,
                    'user_id': user_id
                }
            }
            
            # Add user-specific stats if user_id provided
            if user_id:
                user_stats = self.attendance_repository.get_user_attendance_stats(user_id)
                report['user_stats'] = user_stats
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate attendance report: {e}")
            return {'error': str(e)}
    
    def verify_attendance_eligibility(self, user_id: str, target_date: date) -> Dict[str, Any]:
        """
        Check if user is eligible for attendance on a specific date
        
        Args:
            user_id: User ID to check
            target_date: Date to check eligibility for
            
        Returns:
            Dictionary with eligibility information
        """
        try:
            # Get user's attendance for the date
            user_attendance = self.attendance_repository.get_attendance_history(
                user_id=user_id,
                start_date=target_date,
                end_date=target_date
            )
            
            # Check daily limit (assuming max 1 entry per day)
            daily_entries = len(user_attendance)
            max_daily_entries = 1
            
            is_eligible = daily_entries < max_daily_entries
            
            return {
                'user_id': user_id,
                'date': target_date.isoformat(),
                'is_eligible': is_eligible,
                'daily_entries': daily_entries,
                'max_daily_entries': max_daily_entries,
                'reason': 'Daily limit reached' if not is_eligible else 'Eligible for attendance'
            }
            
        except Exception as e:
            logger.error(f"Failed to check attendance eligibility: {e}")
            return {
                'user_id': user_id,
                'date': target_date.isoformat(),
                'is_eligible': False,
                'error': str(e)
            }
    
    def get_attendance_analytics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Generate attendance analytics for a date range
        
        Args:
            start_date: Start date for analytics
            end_date: End date for analytics
            
        Returns:
            Dictionary containing analytics data
        """
        try:
            # Get attendance data for the period
            attendance_data = self.attendance_repository.get_attendance_history(
                start_date=start_date,
                end_date=end_date
            )
            
            if not attendance_data:
                return {
                    'period': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    },
                    'total_entries': 0,
                    'unique_users': 0,
                    'daily_breakdown': {},
                    'user_breakdown': {}
                }
            
            # Convert to DataFrame for analysis
            import pandas as pd
            df = pd.DataFrame(attendance_data)
            
            # Calculate analytics - filter out zero confidence entries
            valid_df = df[df['Confidence'] > 0] if 'Confidence' in df.columns else df
            total_entries = len(valid_df)
            unique_users = valid_df['ID'].nunique() if 'ID' in valid_df.columns else 0
            
            # Daily breakdown
            daily_breakdown = {}
            if 'Date' in valid_df.columns:
                daily_counts = valid_df.groupby('Date').size()
                daily_breakdown = daily_counts.to_dict()
            
            # User breakdown
            user_breakdown = {}
            if 'ID' in valid_df.columns:
                user_counts = valid_df.groupby('ID').size()
                user_breakdown = user_counts.to_dict()
            
            # Quality metrics - use valid_df which already filters zero confidence
            quality_metrics = {}
            if 'Confidence' in valid_df.columns and not valid_df.empty:
                quality_metrics['avg_confidence'] = valid_df['Confidence'].mean()
                quality_metrics['min_confidence'] = valid_df['Confidence'].min()
                quality_metrics['max_confidence'] = valid_df['Confidence'].max()
            else:
                quality_metrics['avg_confidence'] = 0.0
                quality_metrics['min_confidence'] = 0.0
                quality_metrics['max_confidence'] = 0.0
            
            if 'Liveness_Verified' in valid_df.columns and not valid_df.empty:
                liveness_count = valid_df['Liveness_Verified'].sum()
                quality_metrics['liveness_verification_rate'] = (liveness_count / total_entries * 100) if total_entries > 0 else 0
            else:
                quality_metrics['liveness_verification_rate'] = 0.0
            
            return {
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'total_entries': total_entries,
                'unique_users': unique_users,
                'daily_breakdown': daily_breakdown,
                'user_breakdown': user_breakdown,
                'quality_metrics': quality_metrics
            }
            
        except Exception as e:
            logger.error(f"Failed to generate attendance analytics: {e}")
            return {'error': str(e)}
    
    def export_attendance_data(self, format: str = "csv",
                               start_date: Optional[date] = None,
                               end_date: Optional[date] = None) -> str:
        """
        Export attendance data in specified format
        
        Args:
            format: Export format ("csv", "json")
            start_date: Optional start date for export
            end_date: Optional end date for export
            
        Returns:
            Exported data as string
        """
        try:
            # Get data from repository
            df = self.attendance_repository.export_data(
                start_date=start_date,
                end_date=end_date
            )
            
            if df.empty:
                return ""
            
            # Use repository methods for formatting
            if format.lower() == "csv":
                return self.attendance_repository.export_to_csv(df)
            elif format.lower() == "json":
                return self.attendance_repository.export_to_json(df)
            else:
                logger.warning(f"Unsupported export format: {format}")
                return ""
                
        except Exception as e:
            logger.error(f"Failed to export attendance data: {e}")
            return ""
    
    def is_system_healthy(self) -> bool:
        """
        Check if all components are healthy
        
        Returns:
            True if all components are healthy, False otherwise
        """
        try:
            # Check repository health
            repo_healthy = self.attendance_repository.is_healthy()
            
            # Check manager health
            manager_healthy = self.attendance_manager.is_healthy()
            
            # Check recognition system health
            recognition_healthy = self.recognition_system.is_healthy()
            
            # Check liveness system health
            liveness_healthy = self.liveness_system.is_healthy()
            
            all_healthy = all([
                repo_healthy,
                manager_healthy,
                recognition_healthy,
                liveness_healthy
            ])
            
            if not all_healthy:
                logger.warning("Some components are not healthy")
            
            return all_healthy
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_attendance_report_by_type(self, report_type: str) -> Dict[str, Any]:
        """
        Get attendance report by type for component compatibility
        
        Args:
            report_type: Type of report to generate
            
        Returns:
            Dictionary containing the requested report
        """
        try:
            if report_type == "overview":
                return self._get_overview_report()
            elif report_type == "recent_activity":
                return self._get_recent_activity_report()
            elif report_type == "detailed_history":
                return self._get_detailed_history_report()
            elif report_type == "today_count":
                return self._get_today_count_report()
            else:
                logger.warning(f"Unknown report type: {report_type}")
                return self._get_overview_report()
                
        except Exception as e:
            logger.error(f"Error generating report by type {report_type}: {e}")
            return {}
    
    def get_attendance_analytics_by_type(self, analytics_type: str) -> Dict[str, Any]:
        """
        Get attendance analytics by type for component compatibility
        
        Args:
            analytics_type: Type of analytics to generate
            
        Returns:
            Dictionary containing the requested analytics
        """
        try:
            from datetime import timedelta
            today = date.today()
            month_ago = today - timedelta(days=30)
            
            if analytics_type == "summary":
                analytics_data = self.get_attendance_analytics(month_ago, today)
                # Transform to expected format for analytics component
                avg_confidence = analytics_data.get('quality_metrics', {}).get('avg_confidence', 0.0)
                success_rate = analytics_data.get('quality_metrics', {}).get('liveness_verification_rate', 0.0)
                
                return {
                    'total_attendance': analytics_data.get('total_entries', 0),
                    'unique_users': analytics_data.get('unique_users', 0),
                    'avg_confidence': avg_confidence if avg_confidence > 0 else 0.0,
                    'success_rate': success_rate if success_rate > 0 else 0.0,
                    'attendance_change': 0,  # Placeholder for now
                    'user_change': 0,  # Placeholder for now
                    'confidence_change': 0,  # Placeholder for now
                    'success_change': 0  # Placeholder for now
                }
            elif analytics_type == "user_performance":
                return self.get_user_performance_analytics()
            elif analytics_type == "trends":
                return self.get_trend_analytics()
            else:
                logger.warning(f"Unknown analytics type: {analytics_type}")
                return {}
                
        except Exception as e:
            logger.error(f"Error generating analytics by type {analytics_type}: {e}")
            return {}
    
    def get_recent_activity(self) -> List[Dict[str, Any]]:
        """
        Get recent attendance activity
        
        Returns:
            List of recent attendance entries
        """
        try:
            # Get attendance history and return recent entries
            attendance_data = self.attendance_repository.get_attendance_history()
            
            if not attendance_data:
                return []
            
            # Convert to list of dictionaries and sort by timestamp
            recent_entries = []
            for entry in attendance_data:
                if hasattr(entry, 'to_dict'):
                    entry_dict = entry.to_dict()
                else:
                    entry_dict = entry
                
                recent_entries.append(entry_dict)
            
            # Sort by timestamp (most recent first) and return top 10
            if 'timestamp' in recent_entries[0]:
                recent_entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return recent_entries[:10]
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return []
    
    def get_today_attendance_count(self) -> int:
        """
        Get today's attendance count
        
        Returns:
            Number of attendance entries for today
        """
        try:
            today = date.today()
            attendance_data = self.attendance_repository.get_attendance_history(
                start_date=today,
                end_date=today
            )
            return len(attendance_data) if attendance_data else 0
            
        except Exception as e:
            logger.error(f"Error getting today's attendance count: {e}")
            return 0
    
    def get_user_performance_analytics(self) -> List[Dict[str, Any]]:
        """
        Get user performance analytics
        
        Returns:
            List of user performance data
        """
        try:
            attendance_data = self.attendance_repository.get_attendance_history()
            
            if not attendance_data:
                return []
            
            # Group by user and calculate performance metrics
            user_performance = {}
            
            for entry in attendance_data:
                if hasattr(entry, 'to_dict'):
                    entry_dict = entry.to_dict()
                else:
                    entry_dict = entry
                
                user_name = entry_dict.get('Name', 'Unknown')
                confidence = entry_dict.get('Confidence', 0.0)
                
                # Skip entries with zero confidence (likely test entries)
                if confidence == 0.0:
                    continue
                
                if user_name not in user_performance:
                    user_performance[user_name] = {
                        'user_name': user_name,
                        'attendance_count': 0,
                        'avg_confidence': 0.0,
                        'total_confidence': 0.0
                    }
                
                user_performance[user_name]['attendance_count'] += 1
                user_performance[user_name]['total_confidence'] += confidence
            
            # Calculate averages
            for user_data in user_performance.values():
                if user_data['attendance_count'] > 0:
                    user_data['avg_confidence'] = user_data['total_confidence'] / user_data['attendance_count']
            
            return list(user_performance.values())
            
        except Exception as e:
            logger.error(f"Error getting user performance analytics: {e}")
            return []
    
    def get_trend_analytics(self) -> List[Dict[str, Any]]:
        """Get trend analytics"""
        try:
            attendance_data = self.attendance_repository.get_attendance_history()
            
            if not attendance_data:
                return []
            
            # Group by date and calculate daily trends
            daily_trends = {}
            hourly_trends = {}
            
            for entry in attendance_data:
                if hasattr(entry, 'to_dict'):
                    entry_dict = entry.to_dict()
                else:
                    entry_dict = entry
                
                # Skip entries with zero confidence (likely test entries)
                confidence = entry_dict.get('Confidence', 0.0)
                if confidence == 0.0:
                    continue
                
                # Extract date and time from separate fields
                date_str = entry_dict.get('Date', '')
                time_str = entry_dict.get('Time', '')
                
                if date_str and time_str:
                    try:
                        # Parse date
                        date_obj = pd.to_datetime(date_str).date()
                        date_str = date_obj.isoformat()
                        
                        # Parse time to get hour
                        time_obj = pd.to_datetime(time_str)
                        hour = time_obj.hour
                        
                        # Daily trends
                        if date_str not in daily_trends:
                            daily_trends[date_str] = {
                                'date': date_str,
                                'attendance_count': 0,
                                'late_arrivals': 0
                            }
                        
                        daily_trends[date_str]['attendance_count'] += 1
                        
                        # Count late arrivals (after 9 AM)
                        if hour > 9:
                            daily_trends[date_str]['late_arrivals'] += 1
                        
                        # Hourly trends
                        if hour not in hourly_trends:
                            hourly_trends[hour] = {
                                'hour': hour,
                                'attendance_count': 0
                            }
                        hourly_trends[hour]['attendance_count'] += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to parse date/time for entry: {e}")
                        continue
            
            # Combine daily and hourly trends
            trends_list = list(daily_trends.values())
            trends_list.sort(key=lambda x: x['date'])
            
            # Add hourly data to the first entry for compatibility
            if trends_list:
                hourly_list = list(hourly_trends.values())
                hourly_list.sort(key=lambda x: x['hour'])
                trends_list.extend(hourly_list)
            
            return trends_list
            
        except Exception as e:
            logger.error(f"Error getting trend analytics: {e}")
            return []
    
    # ============================================================================
    # BACKWARD COMPATIBILITY METHODS FOR DASHBOARD COMPONENTS
    # ============================================================================
    
    def _get_overview_report(self) -> Dict[str, Any]:
        """Generate overview report"""
        try:
            today = datetime.now().date()
            summary = self.attendance_repository.get_attendance_summary(today)
            
            # Get overall summary (not just today) for better performance metrics
            overall_summary = self.attendance_repository.get_attendance_summary()
            
            return {
                'total_attendance': overall_summary.get('total_entries', 0),
                'today_attendance': summary.get('total_entries', 0),
                'attendance_rate': 100 if summary.get('total_entries', 0) > 0 else 0,
                'avg_confidence': overall_summary.get('avg_confidence', 0.0),
                'success_rate': overall_summary.get('liveness_verification_rate', 0.0),
                'date': today.isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating overview report: {e}")
            return {}
    
    def _get_recent_activity_report(self) -> List[Dict[str, Any]]:
        """Generate recent activity report"""
        try:
            # Get all attendance records and return last 10
            attendance_data = self.attendance_repository.get_attendance_history()
            if attendance_data and len(attendance_data) > 0:
                return attendance_data[-10:] if len(attendance_data) > 10 else attendance_data
            return []
        except Exception as e:
            logger.error(f"Error generating recent activity report: {e}")
            return []
    
    def _get_detailed_history_report(self) -> Dict[str, Any]:
        """Generate detailed history report"""
        try:
            # Get all attendance history
            attendance_data = self.attendance_repository.get_attendance_history()
            return {
                'attendance_data': attendance_data if attendance_data else [],
                'total_count': len(attendance_data) if attendance_data else 0
            }
        except Exception as e:
            logger.error(f"Error generating detailed history report: {e}")
            return {'attendance_data': [], 'total_count': 0}
    
    def _get_today_count_report(self) -> int:
        """Get today's attendance count"""
        try:
            today = datetime.now().date()
            summary = self.attendance_repository.get_attendance_summary(today)
            return summary.get('total_entries', 0)
        except Exception as e:
            logger.error(f"Error getting today's count: {e}")
            return 0
    
    def is_system_healthy(self) -> bool:
        """Check if the attendance system is healthy"""
        try:
            # Basic health check - can we access the repository?
            test_data = self.attendance_repository.get_attendance_history()
            return True
        except Exception as e:
            logger.error(f"System health check failed: {e}")
            return False
