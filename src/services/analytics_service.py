"""
Analytics Service for EyeD AI Attendance System

This module handles analytics and reporting operations with clear separation of concerns.
Following SRP: Each method has a single, focused responsibility.
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Tuple
import logging
import pandas as pd

from ..repositories.attendance_repository import AttendanceRepository
from ..interfaces.face_database_interface import FaceDatabaseInterface

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service for analytics and reporting operations.
    
    Responsibilities:
    - Report generation (daily, weekly, monthly, custom)
    - Data analysis and aggregation
    - Export functionality
    - Performance metrics calculation
    """
    
    def __init__(self, 
                 attendance_repository: AttendanceRepository,
                 face_database: FaceDatabaseInterface):
        """Initialize analytics service with dependencies"""
        self.attendance_repository = attendance_repository
        self.face_database = face_database
        logger.info("Analytics service initialized successfully")
    
    # ============================================================================
    # REPORT GENERATION METHODS
    # ============================================================================
    
    def generate_attendance_report(self, report_type: str = "daily",
                                  start_date: Optional[date] = None,
                                  end_date: Optional[date] = None,
                                  user_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive attendance report"""
        try:
            # Set default dates if not provided
            start_date, end_date = self._set_default_dates(start_date, end_date, report_type)
            
            # Get attendance data
            attendance_data = self._get_attendance_data(user_id, start_date, end_date)
            if not attendance_data:
                return {'success': False, 'error': 'No attendance data found for the specified period'}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(attendance_data)
            
            # Generate report based on type
            report_data = self._generate_report_by_type(df, report_type, start_date, end_date)
            if not report_data:
                return {'success': False, 'error': f'Invalid report type: {report_type}'}
            
            # Add metadata
            report_data['metadata'] = self._create_report_metadata(
                report_type, start_date, end_date, user_id, len(attendance_data)
            )
            
            logger.info(f"Attendance report generated: {report_type} for period {start_date} to {end_date}")
            return {'success': True, 'report_data': report_data}
            
        except Exception as e:
            logger.error(f"Attendance report generation failed: {e}")
            return {'success': False, 'error': f'Report generation failed: {str(e)}'}
    
    def generate_user_report(self, user_id: str,
                            start_date: Optional[date] = None,
                            end_date: Optional[date] = None) -> Dict[str, Any]:
        """Generate user-specific attendance report"""
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Get user attendance data
            attendance_data = self._get_attendance_data(user_id, start_date, end_date)
            if not attendance_data:
                return {'success': False, 'error': f'No attendance data found for user {user_id}'}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(attendance_data)
            
            # Generate user report
            user_report = {
                'user_id': user_id,
                'user_name': self._get_user_name(user_id),
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'total_days': (end_date - start_date).days + 1
                },
                'attendance_summary': self._calculate_attendance_summary(df, start_date, end_date),
                'quality_summary': self._calculate_quality_summary(df),
                'timing_summary': self._analyze_user_timing(df),
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info(f"User report generated for user {user_id}")
            return {'success': True, 'user_report': user_report}
            
        except Exception as e:
            logger.error(f"User report generation failed for user {user_id}: {e}")
            return {'success': False, 'error': f'User report generation failed: {str(e)}'}
    
    def export_data(self, data: List, format_type: str = "csv", filename: Optional[str] = None) -> Dict[str, Any]:
        """Export data in specified format"""
        try:
            if not data:
                return {'success': False, 'error': 'No data to export'}
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"attendance_export_{timestamp}.{format_type}"
            
            # Export based on format
            if format_type.lower() == "csv":
                export_path = f"data/exports/{filename}"
                df.to_csv(export_path, index=False)
            elif format_type.lower() == "json":
                export_path = f"data/exports/{filename}"
                df.to_json(export_path, orient='records', indent=2)
            else:
                return {'success': False, 'error': f'Unsupported export format: {format_type}'}
            
            logger.info(f"Data exported successfully to {export_path}")
            return {
                'success': True,
                'export_path': export_path,
                'filename': filename,
                'format': format_type,
                'records_exported': len(data)
            }
            
        except Exception as e:
            logger.error(f"Data export failed: {e}")
            return {'success': False, 'error': f'Export failed: {str(e)}'}
    
    # ============================================================================
    # PRIVATE HELPER METHODS - REPORT GENERATION
    # ============================================================================
    
    def _set_default_dates(self, start_date: Optional[date], end_date: Optional[date], report_type: str) -> Tuple[date, date]:
        """Set default dates based on report type"""
        if not end_date:
            end_date = date.today()
        if not start_date:
            if report_type == "daily":
                start_date = end_date
            elif report_type == "weekly":
                start_date = end_date - timedelta(days=7)
            elif report_type == "monthly":
                start_date = end_date - timedelta(days=30)
            else:  # custom
                start_date = end_date - timedelta(days=30)
        
        return start_date, end_date
    
    def _get_attendance_data(self, user_id: Optional[str], start_date: date, end_date: date) -> List:
        """Get attendance data for specified period and user"""
        return self.attendance_repository.get_attendance_history(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
    
    def _generate_report_by_type(self, df: pd.DataFrame, report_type: str, start_date: date, end_date: date) -> Optional[Dict[str, Any]]:
        """Generate report based on type"""
        if report_type == "daily":
            return self._generate_daily_report(df, start_date, end_date)
        elif report_type == "weekly":
            return self._generate_weekly_report(df, start_date, end_date)
        elif report_type == "monthly":
            return self._generate_monthly_report(df, start_date, end_date)
        elif report_type == "custom":
            return self._generate_custom_report(df, start_date, end_date)
        else:
            return None
    
    def _create_report_metadata(self, report_type: str, start_date: date, end_date: date, user_id: Optional[str], total_records: int) -> Dict[str, Any]:
        """Create report metadata"""
        return {
            'report_type': report_type,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'user_id': user_id,
            'generated_at': datetime.now().isoformat(),
            'total_records': total_records
        }
    
    def _generate_daily_report(self, df: pd.DataFrame, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate daily attendance report"""
        try:
            # Group by date
            daily_stats = df.groupby(df['Date'].dt.date).agg({
                'ID': 'count',
                'Status': lambda x: (x == 'Present').sum(),
                'Confidence': 'mean',
                'Face_Quality_Score': 'mean'
            }).rename(columns={
                'ID': 'total_entries',
                'Status': 'present_count',
                'Confidence': 'avg_confidence',
                'Face_Quality_Score': 'avg_quality_score'
            })
            
            # Calculate daily metrics
            daily_stats['attendance_rate'] = daily_stats['present_count'] / daily_stats['total_entries']
            daily_stats['absent_count'] = daily_stats['total_entries'] - daily_stats['present_count']
            
            return {
                'daily_statistics': daily_stats.to_dict('index'),
                'summary': {
                    'total_days': len(daily_stats),
                    'total_entries': daily_stats['total_entries'].sum(),
                    'total_present': daily_stats['present_count'].sum(),
                    'overall_attendance_rate': daily_stats['present_count'].sum() / daily_stats['total_entries'].sum()
                }
            }
        except Exception as e:
            logger.error(f"Daily report generation failed: {e}")
            return {}
    
    def _generate_weekly_report(self, df: pd.DataFrame, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate weekly attendance report"""
        try:
            # Add week number column
            df['Week'] = df['Date'].dt.isocalendar().week
            
            # Group by week
            weekly_stats = df.groupby('Week').agg({
                'ID': 'count',
                'Status': lambda x: (x == 'Present').sum(),
                'Confidence': 'mean'
            }).rename(columns={
                'ID': 'total_entries',
                'Status': 'present_count',
                'Confidence': 'avg_confidence'
            })
            
            weekly_stats['attendance_rate'] = weekly_stats['present_count'] / weekly_stats['total_entries']
            
            return {
                'weekly_statistics': weekly_stats.to_dict('index'),
                'summary': {
                    'total_weeks': len(weekly_stats),
                    'total_entries': weekly_stats['total_entries'].sum()
                }
            }
        except Exception as e:
            logger.error(f"Weekly report generation failed: {e}")
            return {}
    
    def _generate_monthly_report(self, df: pd.DataFrame, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate monthly attendance report"""
        try:
            # Add month column
            df['Month'] = df['Date'].dt.month
            df['Year'] = df['Date'].dt.year
            
            # Group by month
            monthly_stats = df.groupby(['Year', 'Month']).agg({
                'ID': 'count',
                'Status': lambda x: (x == 'Present').sum(),
                'Confidence': 'mean',
                'Face_Quality_Score': 'mean'
            }).rename(columns={
                'ID': 'total_entries',
                'Status': 'present_count',
                'Confidence': 'avg_confidence',
                'Face_Quality_Score': 'avg_quality_score'
            })
            
            monthly_stats['attendance_rate'] = monthly_stats['present_count'] / monthly_stats['total_entries']
            
            return {
                'monthly_statistics': monthly_stats.to_dict('index'),
                'summary': {
                    'total_months': len(monthly_stats),
                    'total_entries': monthly_stats['total_entries'].sum()
                }
            }
        except Exception as e:
            logger.error(f"Monthly report generation failed: {e}")
            return {}
    
    def _generate_custom_report(self, df: pd.DataFrame, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate custom attendance report"""
        try:
            # Calculate overall statistics
            total_entries = len(df)
            unique_users = df['ID'].nunique() if 'ID' in df.columns else 0
            
            # Daily breakdown
            daily_breakdown = {}
            if 'Date' in df.columns:
                daily_counts = df.groupby('Date').size()
                daily_breakdown = daily_counts.to_dict()
            
            # User breakdown
            user_breakdown = {}
            if 'ID' in df.columns:
                user_counts = df.groupby('ID').size()
                user_breakdown = user_counts.to_dict()
            
            # Quality metrics
            quality_metrics = {}
            if 'Confidence' in df.columns:
                quality_metrics['avg_confidence'] = df['Confidence'].mean()
                quality_metrics['min_confidence'] = df['Confidence'].min()
                quality_metrics['max_confidence'] = df['Confidence'].max()
            
            if 'Face_Quality_Score' in df.columns:
                quality_metrics['avg_face_quality'] = df['Face_Quality_Score'].mean()
                quality_metrics['min_face_quality'] = df['Face_Quality_Score'].min()
                quality_metrics['max_face_quality'] = df['Face_Quality_Score'].max()
            
            return {
                'overall_statistics': {
                    'total_entries': total_entries,
                    'unique_users': unique_users,
                    'date_range': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    }
                },
                'daily_breakdown': daily_breakdown,
                'user_breakdown': user_breakdown,
                'quality_metrics': quality_metrics
            }
            
        except Exception as e:
            logger.error(f"Custom report generation failed: {e}")
            return {}
    
    # ============================================================================
    # PRIVATE HELPER METHODS - USER ANALYSIS
    # ============================================================================
    
    def _get_user_name(self, user_id: str) -> str:
        """Get user name from face database"""
        user_info = self.face_database.get_user_info(user_id)
        return user_info.data.get('user_name', user_id) if user_info.success else user_id
    
    def _calculate_attendance_summary(self, df: pd.DataFrame, start_date: date, end_date: date) -> Dict[str, Any]:
        """Calculate attendance summary for user report"""
        try:
            total_entries = len(df)
            unique_days = len(df['Date'].unique()) if 'Date' in df.columns else 0
            total_days = (end_date - start_date).days + 1
            
            return {
                'total_entries': total_entries,
                'unique_days': unique_days,
                'attendance_rate': (unique_days / total_days * 100) if total_days > 0 else 0
            }
        except Exception as e:
            logger.error(f"Attendance summary calculation failed: {e}")
            return {}
    
    def _calculate_quality_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate quality summary for user report"""
        try:
            return {
                'avg_confidence': df['Confidence'].mean() if 'Confidence' in df.columns else 0,
                'avg_face_quality': df['Face_Quality_Score'].mean() if 'Face_Quality_Score' in df.columns else 0
            }
        except Exception as e:
            logger.error(f"Quality summary calculation failed: {e}")
            return {}
    
    def _analyze_user_timing(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze user timing patterns"""
        try:
            if 'Time' not in df.columns:
                return {}
            
            # Convert time to hour
            df['Hour'] = pd.to_datetime(df['Time']).dt.hour
            df['Minute'] = pd.to_datetime(df['Time']).dt.minute
            
            # Calculate timing metrics
            timing_summary = {
                'early_arrivals': len(df[df['Hour'] <= 8]),
                'on_time_arrivals': len(df[(df['Hour'] == 9) & (df['Minute'] <= 15)]),
                'late_arrivals': len(df[(df['Hour'] > 9) | ((df['Hour'] == 9) & (df['Minute'] > 15))]),
                'avg_arrival_hour': df['Hour'].mean(),
                'earliest_arrival': df['Hour'].min(),
                'latest_arrival': df['Hour'].max()
            }
            
            return timing_summary
            
        except Exception as e:
            logger.error(f"User timing analysis failed: {e}")
            return {}
    
    # ============================================================================
    # PRIVATE HELPER METHODS - UTILITY FUNCTIONS
    # ============================================================================
    
    def get_available_report_types(self) -> List[Dict[str, Any]]:
        """Get available report types and their descriptions"""
        try:
            report_types = [
                {
                    'id': 'daily',
                    'name': 'Daily Report',
                    'description': 'Daily attendance statistics and breakdown',
                    'default_period': 1,
                    'suitable_for': ['Daily monitoring', 'Quick overview']
                },
                {
                    'id': 'weekly',
                    'name': 'Weekly Report',
                    'description': 'Weekly attendance trends and patterns',
                    'default_period': 7,
                    'suitable_for': ['Weekly review', 'Trend analysis']
                },
                {
                    'id': 'monthly',
                    'name': 'Monthly Report',
                    'description': 'Monthly attendance summary and insights',
                    'default_period': 30,
                    'suitable_for': ['Monthly review', 'Performance analysis']
                },
                {
                    'id': 'custom',
                    'name': 'Custom Report',
                    'description': 'Custom date range attendance analysis',
                    'default_period': 30,
                    'suitable_for': ['Specific periods', 'Detailed analysis']
                }
            ]
            
            return report_types
            
        except Exception as e:
            logger.error(f"Report types retrieval failed: {e}")
            return []
    
    def validate_report_parameters(self, report_type: str,
                                  start_date: Optional[date] = None,
                                  end_date: Optional[date] = None) -> Dict[str, Any]:
        """Validate report generation parameters"""
        try:
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Validate report type
            valid_types = ['daily', 'weekly', 'monthly', 'custom']
            if report_type not in valid_types:
                validation_result['valid'] = False
                validation_result['errors'].append(f'Invalid report type: {report_type}')
            
            # Validate dates
            if start_date and end_date:
                if start_date > end_date:
                    validation_result['valid'] = False
                    validation_result['errors'].append('Start date cannot be after end date')
                
                if start_date > date.today():
                    validation_result['warnings'].append('Start date is in the future')
                
                if end_date > date.today():
                    validation_result['warnings'].append('End date is in the future')
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Report parameter validation failed: {e}")
            return {
                'valid': False,
                'errors': [f'Validation failed: {str(e)}'],
                'warnings': []
            }
