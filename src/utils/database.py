"""
Database utilities for EyeD AI Attendance System
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .config import ATTENDANCE_FILE, FACES_DIR
from .logger import logger

class AttendanceDB:
    """Attendance database manager"""
    
    def __init__(self):
        self.attendance_file = ATTENDANCE_FILE
        self.faces_dir = FACES_DIR
        self.faces_db_file = FACES_DIR / "faces.json"
        
        # Initialize database files
        self._init_database()
    
    def _init_database(self):
        """Initialize database files if they don't exist"""
        try:
            # Create attendance CSV if it doesn't exist
            if not self.attendance_file.exists():
                attendance_df = pd.DataFrame(columns=[
                    'Name', 'ID', 'Date', 'Time', 'Status', 
                    'Confidence', 'Liveness_Verified', 'Face_Quality_Score',
                    'Processing_Time_MS', 'Verification_Stage', 'Session_ID',
                    'Device_Info', 'Location'
                ])
                attendance_df.to_csv(self.attendance_file, index=False)
                logger.info(f"Created attendance database: {self.attendance_file}")
            
            # Create faces database if it doesn't exist
            if not self.faces_db_file.exists():
                faces_db = {
                    "users": {},
                    "embeddings": {},
                    "metadata": {
                        "created": datetime.now().isoformat(),
                        "version": "1.0"
                    }
                }
                with open(self.faces_db_file, 'w') as f:
                    json.dump(faces_db, f, indent=2)
                logger.info(f"Created faces database: {self.faces_db_file}")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def log_attendance(self, name: str, user_id: str, status: str = "Present", 
                      confidence: float = 0.0, liveness_verified: bool = False,
                      face_quality_score: float = 0.0, processing_time_ms: float = 0.0,
                      verification_stage: str = "Unknown", session_id: str = "",
                      device_info: str = "Unknown", location: str = "Unknown"):
        """Log attendance entry with comprehensive metadata"""
        try:
            now = datetime.now()
            new_entry = {
                'Name': name,
                'ID': user_id,
                'Date': now.strftime('%Y-%m-%d'),
                'Time': now.strftime('%H:%M:%S'),
                'Status': status,
                'Confidence': confidence,
                'Liveness_Verified': liveness_verified,
                'Face_Quality_Score': face_quality_score,
                'Processing_Time_MS': processing_time_ms,
                'Verification_Stage': verification_stage,
                'Session_ID': session_id,
                'Device_Info': device_info,
                'Location': location
            }
            
            # Read existing data
            attendance_df = pd.read_csv(self.attendance_file)
            
            # Add new entry
            attendance_df = pd.concat([attendance_df, pd.DataFrame([new_entry])], 
                                    ignore_index=True)
            
            # Save back to file
            attendance_df.to_csv(self.attendance_file, index=False)
            
            logger.info(f"Logged attendance: {name} - {status} at {now.strftime('%H:%M:%S')}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging attendance: {e}")
            return False
    
    def get_attendance_data(self, date: Optional[str] = None, 
                           user_id: Optional[str] = None) -> pd.DataFrame:
        """Get attendance data with optional filters"""
        try:
            attendance_df = pd.read_csv(self.attendance_file)
            
            if date:
                attendance_df = attendance_df[attendance_df['Date'] == date]
            
            if user_id:
                attendance_df = attendance_df[attendance_df['ID'] == user_id]
            
            return attendance_df
            
        except Exception as e:
            logger.error(f"Error reading attendance data: {e}")
            return pd.DataFrame()
    
    def get_user_embeddings(self) -> Dict:
        """Get stored user face embeddings"""
        try:
            if self.faces_db_file.exists():
                with open(self.faces_db_file, 'r') as f:
                    faces_db = json.load(f)
                return faces_db.get('embeddings', {})
            return {}
        except Exception as e:
            logger.error(f"Error reading user embeddings: {e}")
            return {}
    
    def save_user_embedding(self, user_id: str, name: str, 
                           embedding: List[float], image_path: str):
        """Save user face embedding"""
        try:
            faces_db = {}
            if self.faces_db_file.exists():
                with open(self.faces_db_file, 'r') as f:
                    faces_db = json.load(f)
            
            # Add user data
            faces_db['users'][user_id] = {
                'name': name,
                'image_path': image_path,
                'registered': datetime.now().isoformat()
            }
            
            faces_db['embeddings'][user_id] = embedding
            
            # Save back to file
            with open(self.faces_db_file, 'w') as f:
                json.dump(faces_db, f, indent=2)
            
            logger.info(f"Saved embedding for user: {name} ({user_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error saving user embedding: {e}")
            return False
    
    def export_attendance_data(self, format: str = 'csv', date_range: Optional[Tuple[str, str]] = None) -> str:
        """Export attendance data in specified format"""
        try:
            attendance_data = self.get_attendance_data()
            
            # Apply date filter if specified
            if date_range:
                start_date, end_date = date_range
                if 'Date' in attendance_data.columns:
                    attendance_data = attendance_data[
                        (attendance_data['Date'] >= start_date) & 
                        (attendance_data['Date'] <= end_date)
                    ]
            
            if format.lower() == 'csv':
                export_path = self.attendance_file.parent / f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                attendance_data.to_csv(export_path, index=False)
                logger.info(f"Exported attendance data to: {export_path}")
                return str(export_path)
            
            elif format.lower() == 'json':
                export_path = self.attendance_file.parent / f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                attendance_data.to_json(export_path, orient='records', indent=2)
                logger.info(f"Exported attendance data to: {export_path}")
                return str(export_path)
            
            elif format.lower() == 'excel':
                try:
                    import openpyxl
                    export_path = self.attendance_file.parent / f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    attendance_data.to_excel(export_path, index=False, engine='openpyxl')
                    logger.info(f"Exported attendance data to: {export_path}")
                    return str(export_path)
                except ImportError:
                    logger.error("openpyxl not available for Excel export")
                    return ""
            
            else:
                logger.error(f"Unsupported export format: {format}")
                return ""
                
        except Exception as e:
            logger.error(f"Error exporting attendance data: {e}")
            return ""

# Global database instance
attendance_db = AttendanceDB()
