"""
Attendance Repository for EyeD AI Attendance System

This module handles data persistence for attendance operations,
following the Single-Responsibility Principle.
"""

import pandas as pd
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AttendanceRepository:
    """Repository for attendance data persistence"""
    
    def __init__(self, data_file: str = "data/attendance.csv"):
        """
        Initialize attendance repository
        
        Args:
            data_file: Path to attendance data file
        """
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize empty file if it doesn't exist
        if not self.data_file.exists():
            self._create_empty_file()
        
        logger.info(f"Attendance repository initialized with file: {self.data_file}")
    
    def _create_empty_file(self):
        """Create empty attendance file with headers"""
        headers = [
            'Date', 'Time', 'Name', 'ID', 'Status', 'Confidence',
            'Liveness_Verified', 'Face_Quality_Score', 'Processing_Time_MS',
            'Verification_Stage', 'Session_ID', 'Device_Info', 'Location'
        ]
        
        df = pd.DataFrame(columns=headers)
        df.to_csv(self.data_file, index=False)
        logger.info("Created empty attendance file with headers")
    
    def add_attendance(self, entry) -> bool:
        """
        Add attendance entry to repository
        
        Args:
            entry: Attendance entry object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert entry to dictionary
            data = {
                'Date': entry.date,
                'Time': entry.time,
                'Name': entry.name,
                'ID': entry.user_id,
                'Status': entry.status,
                'Confidence': entry.confidence,
                'Liveness_Verified': entry.liveness_verified,
                'Face_Quality_Score': entry.face_quality_score,
                'Processing_Time_MS': entry.processing_time_ms,
                'Verification_Stage': entry.verification_stage,
                'Session_ID': entry.session_id,
                'Device_Info': entry.device_info,
                'Location': entry.location
            }
            
            # Read existing data
            df = pd.read_csv(self.data_file)
            
            # Add new entry
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
            
            # Save back to file
            df.to_csv(self.data_file, index=False)
            
            logger.info(f"Attendance entry added for user {entry.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add attendance entry: {e}")
            return False
    
    def get_attendance_history(self, user_id: Optional[str] = None,
                              start_date: Optional[date] = None,
                              end_date: Optional[date] = None) -> List:
        """
        Get attendance history with optional filters
        
        Args:
            user_id: Optional user ID to filter by
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List of attendance entries
        """
        try:
            # Read data
            df = pd.read_csv(self.data_file)
            
            if df.empty:
                return []
            
            # Apply filters
            if user_id:
                df = df[df['ID'] == user_id]
            
            if start_date:
                # Convert start_date to datetime for comparison
                start_datetime = pd.to_datetime(start_date)
                df = df[pd.to_datetime(df['Date']) >= start_datetime]
            
            if end_date:
                # Convert end_date to datetime for comparison
                end_datetime = pd.to_datetime(end_date)
                df = df[pd.to_datetime(df['Date']) <= end_datetime]
            
            # Convert to list of dictionaries
            return df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Failed to get attendance history: {e}")
            return []
    
    def get_attendance_summary(self, target_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get attendance summary for a specific date or overall
        
        Args:
            target_date: Optional date for summary, uses today if None
            
        Returns:
            Dictionary containing attendance summary
        """
        try:
            # Read data
            df = pd.read_csv(self.data_file)
            
            if df.empty:
                return {
                    'total_entries': 0,
                    'unique_users': 0,
                    'date': target_date.strftime('%Y-%m-%d') if target_date else 'all'
                }
            
            # Filter by date if specified
            if target_date:
                # Convert target_date to datetime for comparison
                target_datetime = pd.to_datetime(target_date)
                df = df[pd.to_datetime(df['Date']) == target_datetime]
            
            # Calculate summary
            total_entries = len(df)
            unique_users = df['ID'].nunique() if 'ID' in df.columns else 0
            
            summary = {
                'total_entries': total_entries,
                'unique_users': unique_users,
                'date': target_date.strftime('%Y-%m-%d') if target_date else 'all'
            }
            
            # Add additional metrics if data exists - filter out zero confidence entries
            if 'Confidence' in df.columns and not df.empty:
                # Filter out zero confidence entries for quality metrics
                valid_confidence_df = df[df['Confidence'] > 0]
                if not valid_confidence_df.empty:
                    summary['avg_confidence'] = valid_confidence_df['Confidence'].mean()
                    summary['min_confidence'] = valid_confidence_df['Confidence'].min()
                    summary['max_confidence'] = valid_confidence_df['Confidence'].max()
                else:
                    summary['avg_confidence'] = 0.0
                    summary['min_confidence'] = 0.0
                    summary['max_confidence'] = 0.0
            
            if 'Liveness_Verified' in df.columns and not df.empty:
                # Only count liveness verification for entries with valid confidence
                valid_entries = df[df['Confidence'] > 0] if 'Confidence' in df.columns else df
                liveness_count = valid_entries['Liveness_Verified'].sum() if not valid_entries.empty else 0
                valid_total = len(valid_entries) if not valid_entries.empty else 0
                summary['liveness_verified_count'] = liveness_count
                summary['liveness_verification_rate'] = (liveness_count / valid_total * 100) if valid_total > 0 else 0
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get attendance summary: {e}")
            return {}
    
    def update_attendance(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update attendance entry by session ID
        
        Args:
            session_id: Session ID to update
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read data
            df = pd.read_csv(self.data_file)
            
            if df.empty:
                return False
            
            # Find entry by session ID
            mask = df['Session_ID'] == session_id
            if not mask.any():
                logger.warning(f"Session ID {session_id} not found")
                return False
            
            # Update fields
            for field, value in updates.items():
                if field in df.columns:
                    df.loc[mask, field] = value
            
            # Save back to file
            df.to_csv(self.data_file, index=False)
            
            logger.info(f"Updated attendance entry for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update attendance: {e}")
            return False
    
    def delete_attendance(self, session_id: str) -> bool:
        """
        Delete attendance entry by session ID
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read data
            df = pd.read_csv(self.data_file)
            
            if df.empty:
                return False
            
            # Find and remove entry
            mask = df['Session_ID'] == session_id
            if not mask.any():
                logger.warning(f"Session ID {session_id} not found")
                return False
            
            df = df[~mask]
            
            # Save back to file
            df.to_csv(self.data_file, index=False)
            
            logger.info(f"Deleted attendance entry for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete attendance: {e}")
            return False
    
    def get_user_attendance_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get attendance statistics for a specific user
        
        Args:
            user_id: User ID to get stats for
            
        Returns:
            Dictionary containing user attendance statistics
        """
        try:
            # Read data
            df = pd.read_csv(self.data_file)
            
            if df.empty:
                return {'user_id': user_id, 'total_entries': 0}
            
            # Filter by user
            user_df = df[df['ID'] == user_id]
            
            if user_df.empty:
                return {'user_id': user_id, 'total_entries': 0}
            
            # Calculate stats
            total_entries = len(user_df)
            unique_dates = user_df['Date'].nunique()
            
            stats = {
                'user_id': user_id,
                'total_entries': total_entries,
                'unique_dates': unique_dates,
                'attendance_rate': (unique_dates / 30) * 100  # Assuming monthly basis
            }
            
            # Add additional metrics if available
            if 'Confidence' in user_df.columns:
                stats['avg_confidence'] = user_df['Confidence'].mean()
                stats['min_confidence'] = user_df['Confidence'].min()
                stats['max_confidence'] = user_df['Confidence'].max()
            
            if 'Liveness_Verified' in user_df.columns:
                liveness_count = user_df['Liveness_Verified'].sum()
                stats['liveness_verified_count'] = liveness_count
                stats['liveness_verification_rate'] = (liveness_count / total_entries * 100)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get user attendance stats: {e}")
            return {'user_id': user_id, 'error': str(e)}
    
    def is_healthy(self) -> bool:
        """Check if repository is healthy"""
        try:
            # Test file access
            test_data = self.get_attendance_history(limit=1)
            return True
        except Exception as e:
            logger.error(f"Repository health check failed: {e}")
            return False
    
    def export_data(self, format: str = "csv", 
                   start_date: Optional[date] = None,
                   end_date: Optional[date] = None) -> pd.DataFrame:
        """
        Export attendance data as DataFrame for further processing
        
        Args:
            format: Export format (currently only DataFrame supported)
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            DataFrame containing filtered attendance data
        """
        try:
            # Get filtered data
            data = self.get_attendance_history(
                start_date=start_date,
                end_date=end_date
            )
            
            if not data:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df_data = []
            for entry in data:
                df_data.append({
                    'Date': entry.date,
                    'Time': entry.time,
                    'Name': entry.name,
                    'ID': entry.user_id,
                    'Status': entry.status,
                    'Confidence': entry.confidence,
                    'Liveness_Verified': entry.liveness_verified,
                    'Face_Quality_Score': entry.face_quality_score,
                    'Processing_Time_MS': entry.processing_time_ms,
                    'Verification_Stage': entry.verification_stage,
                    'Session_ID': entry.session_id,
                    'Device_Info': entry.device_info,
                    'Location': entry.location
                })
            
            df = pd.DataFrame(df_data)
            logger.info(f"Exported {len(df)} attendance records")
            return df
            
        except Exception as e:
            logger.error(f"Failed to export attendance data: {e}")
            return pd.DataFrame()
    
    def export_to_csv(self, data: pd.DataFrame) -> str:
        """
        Export DataFrame to CSV format
        
        Args:
            data: DataFrame to export
            
        Returns:
            CSV string
        """
        try:
            if data.empty:
                return ""
            return data.to_csv(index=False)
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            return ""
    
    def export_to_json(self, data: pd.DataFrame) -> str:
        """
        Export DataFrame to JSON format
        
        Args:
            data: DataFrame to export
            
        Returns:
            JSON string
        """
        try:
            if data.empty:
                return "[]"
            return data.to_json(orient='records', indent=2)
        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            return "[]"
