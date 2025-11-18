"""
Attendance Repository for EyeD AI Attendance System.

This module handles data persistence for attendance operations,
following the Single-Responsibility Principle and Dependency Injection.

The repository works with the AttendanceRecord domain entity from
domain/entities/attendance_record.py and delegates CSV operations to CSVHandler.
"""

import logging
from datetime import date, time, datetime
from typing import List, Optional, Dict, Any

from domain.entities.attendance_record import AttendanceRecord
from domain.shared.exceptions import DomainException
from infrastructure.storage.csv_handler import CSVHandler

logger = logging.getLogger(__name__)


class AttendanceRepository:
    """
    Repository for attendance data persistence.
    
    This class handles ONLY attendance data persistence (CRUD operations).
    It follows SRP by delegating CSV operations to CSVHandler and working
    with AttendanceRecord domain entities.
    """
    
    # CSV column names
    CSV_COLUMNS = [
        'Date', 'Time', 'Name', 'ID', 'Status', 'Confidence',
        'Liveness_Verified', 'Face_Quality_Score', 'Processing_Time_MS',
        'Verification_Stage', 'Session_ID', 'Device_Info', 'Location'
    ]
    
    def __init__(self, csv_handler: CSVHandler, data_file: str = "data/attendance.csv"):
        """
        Initialize attendance repository.
        
        Args:
            csv_handler: Injected CSV handler for CSV operations
            data_file: Path to attendance CSV file
        """
        if csv_handler is None:
            raise ValueError("csv_handler cannot be None")
        
        self.csv_handler = csv_handler
        self.data_file = data_file
        
        # Initialize CSV file with headers if it doesn't exist
        if not self.csv_handler.csv_exists(self.data_file):
            self._initialize_csv_file()
        
        logger.info(f"AttendanceRepository initialized with file: {self.data_file}")
    
    def _initialize_csv_file(self) -> None:
        """Initialize CSV file with headers if it doesn't exist."""
        try:
            # Create empty file with headers only
            empty_row = {col: '' for col in self.CSV_COLUMNS}
            success = self.csv_handler.write_csv(
                self.data_file,
                [],
                headers=self.CSV_COLUMNS
            )
            if success:
                logger.info(f"Initialized CSV file with headers: {self.data_file}")
            else:
                logger.error(f"Failed to initialize CSV file: {self.data_file}")
        except Exception as e:
            logger.error(f"Error initializing CSV file: {e}")
    
    def add_attendance(self, record: AttendanceRecord) -> bool:
        """
        Persist new attendance record.
        
        Args:
            record: AttendanceRecord domain entity to persist
            
        Returns:
            True on success, False on failure
        """
        try:
            # Convert AttendanceRecord entity to CSV row format
            csv_row = self._entity_to_csv_row(record)
            
            # Append to CSV file
            success = self.csv_handler.append_csv(self.data_file, csv_row)
            
            if success:
                logger.info(f"Attendance record added: {record.record_id} for user {record.user_id}")
            else:
                logger.error(f"Failed to add attendance record: {record.record_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error adding attendance record: {e}")
            return False
    
    def get_attendance_history(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[AttendanceRecord]:
        """
        Retrieve attendance records with optional filters.
        
        Args:
            user_id: Optional user ID to filter by
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List of AttendanceRecord domain entities
        """
        try:
            # Read all data from CSV
            csv_data = self.csv_handler.read_csv(self.data_file)
            
            if not csv_data:
                return []
            
            # Apply filters
            filtered_data = csv_data
            
            if user_id:
                filtered_data = [row for row in filtered_data if row.get('ID') == user_id]
            
            if start_date:
                filtered_data = [
                    row for row in filtered_data
                    if self._parse_date_from_csv(row.get('Date')) >= start_date
                ]
            
            if end_date:
                filtered_data = [
                    row for row in filtered_data
                    if self._parse_date_from_csv(row.get('Date')) <= end_date
                ]
            
            # Convert CSV rows to AttendanceRecord entities
            records = []
            for row in filtered_data:
                try:
                    record = self._csv_row_to_entity(row)
                    records.append(record)
                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(f"Failed to convert CSV row to entity: {e}, row: {row}")
                    continue
            
            logger.debug(f"Retrieved {len(records)} attendance records")
            return records
            
        except Exception as e:
            logger.error(f"Error retrieving attendance history: {e}")
            return []
    
    def get_attendance_by_id(self, record_id: str) -> Optional[AttendanceRecord]:
        """
        Retrieve single attendance record by ID.
        
        Uses Session_ID column to match record_id.
        
        Args:
            record_id: Record ID to retrieve
            
        Returns:
            AttendanceRecord entity or None if not found
        """
        try:
            # Read all data from CSV
            csv_data = self.csv_handler.read_csv(self.data_file)
            
            if not csv_data:
                return None
            
            # Find record by Session_ID (used as record identifier)
            for row in csv_data:
                if row.get('Session_ID') == record_id:
                    try:
                        return self._csv_row_to_entity(row)
                    except (KeyError, ValueError, TypeError) as e:
                        logger.warning(f"Failed to convert CSV row to entity: {e}")
                        return None
            
            logger.debug(f"Attendance record not found: {record_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving attendance record by ID: {e}")
            return None
    
    def update_attendance(self, record_id: str, record: AttendanceRecord) -> bool:
        """
        Update existing attendance record.
        
        Args:
            record_id: ID of the record to update
            record: Updated AttendanceRecord entity
            
        Returns:
            True on success, False on failure
        """
        try:
            # Read all data from CSV
            csv_data = self.csv_handler.read_csv(self.data_file)
            
            if not csv_data:
                logger.warning(f"Cannot update: no data in CSV file")
                return False
            
            # Find and update the record
            updated = False
            for i, row in enumerate(csv_data):
                if row.get('Session_ID') == record_id:
                    # Convert entity to CSV row and update
                    updated_row = self._entity_to_csv_row(record)
                    csv_data[i] = updated_row
                    updated = True
                    break
            
            if not updated:
                logger.warning(f"Attendance record not found for update: {record_id}")
                return False
            
            # Write updated data back to CSV
            headers = self.csv_handler.get_headers(self.data_file)
            if not headers:
                headers = self.CSV_COLUMNS
            
            success = self.csv_handler.write_csv(self.data_file, csv_data, headers=headers)
            
            if success:
                logger.info(f"Attendance record updated: {record_id}")
            else:
                logger.error(f"Failed to update attendance record: {record_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating attendance record: {e}")
            return False
    
    def delete_attendance(self, record_id: str) -> bool:
        """
        Delete attendance record by ID.
        
        Args:
            record_id: ID of the record to delete
            
        Returns:
            True on success, False on failure
        """
        try:
            # Read all data from CSV
            csv_data = self.csv_handler.read_csv(self.data_file)
            
            if not csv_data:
                logger.warning(f"Cannot delete: no data in CSV file")
                return False
            
            # Find and remove the record
            original_count = len(csv_data)
            csv_data = [row for row in csv_data if row.get('Session_ID') != record_id]
            
            if len(csv_data) == original_count:
                logger.warning(f"Attendance record not found for deletion: {record_id}")
                return False
            
            # Write updated data back to CSV
            headers = self.csv_handler.get_headers(self.data_file)
            if not headers:
                headers = self.CSV_COLUMNS
            
            success = self.csv_handler.write_csv(self.data_file, csv_data, headers=headers)
            
            if success:
                logger.info(f"Attendance record deleted: {record_id}")
            else:
                logger.error(f"Failed to delete attendance record: {record_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting attendance record: {e}")
            return False
    
    def _entity_to_csv_row(self, record: AttendanceRecord) -> Dict[str, Any]:
        """
        Convert AttendanceRecord domain entity to CSV row format.
        
        Maps domain entity fields to CSV columns:
        - user_name (domain) -> Name (CSV)
        - user_id (domain) -> ID (CSV)
        - record_id (domain) -> Session_ID (CSV) for identification/lookups
        
        Args:
            record: AttendanceRecord domain entity
            
        Returns:
            Dictionary representing CSV row
        """
        return {
            'Date': record.date.strftime('%Y-%m-%d'),
            'Time': record.time.strftime('%H:%M:%S'),
            'Name': record.user_name,  # Map user_name (domain) to Name (CSV)
            'ID': record.user_id,  # Map user_id (domain) to ID (CSV)
            'Status': record.status,
            'Confidence': record.confidence,
            'Liveness_Verified': record.liveness_verified,
            'Face_Quality_Score': record.face_quality_score,
            'Processing_Time_MS': record.processing_time_ms,
            'Verification_Stage': record.verification_stage,
            'Session_ID': record.record_id,  # Use record_id as Session_ID for identification/lookups
            'Device_Info': record.device_info,
            'Location': record.location
        }
    
    def _csv_row_to_entity(self, row: Dict[str, Any]) -> AttendanceRecord:
        """
        Convert CSV row to AttendanceRecord domain entity.
        
        Args:
            row: Dictionary representing CSV row
            
        Returns:
            AttendanceRecord domain entity
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Parse date
        record_date = self._parse_date_from_csv(row.get('Date'))
        
        # Parse time
        record_time = self._parse_time_from_csv(row.get('Time'))
        
        # Use Session_ID as record_id (or generate one if missing)
        record_id = row.get('Session_ID', '')
        if not record_id:
            # Fallback: generate ID from date, time, and user_id
            record_id = f"{record_date}_{record_time}_{row.get('ID', 'unknown')}"
        
        # Parse boolean values (handle string representations)
        liveness_verified = self._parse_boolean(row.get('Liveness_Verified', False))
        
        # Create AttendanceRecord entity
        return AttendanceRecord.create(
            record_id=record_id,
            user_id=row.get('ID', ''),
            user_name=row.get('Name', ''),  # Map Name (CSV) to user_name (domain)
            date=record_date,
            time=record_time,
            confidence=float(row.get('Confidence', 0.0)),
            liveness_verified=liveness_verified,
            face_quality_score=float(row.get('Face_Quality_Score', 0.0)),
            processing_time_ms=float(row.get('Processing_Time_MS', 0.0)),
            verification_stage=row.get('Verification_Stage', ''),
            session_id=row.get('Session_ID', record_id),  # Use Session_ID from CSV, fallback to record_id
            device_info=row.get('Device_Info', ''),
            location=row.get('Location', ''),
            status=row.get('Status', 'Present')
        )
    
    def _parse_date_from_csv(self, date_value: Any) -> date:
        """
        Parse date from CSV value (ISO 8601 format: YYYY-MM-DD).
        
        The repository enforces a standard date format. Data should be
        normalized to ISO 8601 format before persistence.
        
        Args:
            date_value: Date value from CSV (string in ISO format, date, or datetime)
            
        Returns:
            date object
            
        Raises:
            ValueError: If date is not in ISO 8601 format (YYYY-MM-DD)
        """
        if isinstance(date_value, date):
            return date_value
        if isinstance(date_value, datetime):
            return date_value.date()
        if isinstance(date_value, str):
            # Enforce ISO 8601 format (YYYY-MM-DD)
            try:
                return datetime.strptime(date_value, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError(
                    f"Invalid date format: {date_value}. Expected ISO 8601 format (YYYY-MM-DD)"
                )
        raise ValueError(f"Cannot parse date: {date_value}. Expected ISO 8601 format (YYYY-MM-DD)")
    
    def _parse_time_from_csv(self, time_value: Any) -> time:
        """
        Parse time from CSV value (ISO 8601 format: HH:MM:SS).
        
        The repository enforces a standard time format. Data should be
        normalized to ISO 8601 format before persistence.
        
        Args:
            time_value: Time value from CSV (string in ISO format, time, or datetime)
            
        Returns:
            time object
            
        Raises:
            ValueError: If time is not in ISO 8601 format (HH:MM:SS)
        """
        if isinstance(time_value, time):
            return time_value
        if isinstance(time_value, datetime):
            return time_value.time()
        if isinstance(time_value, str):
            # Enforce ISO 8601 format (HH:MM:SS)
            try:
                return datetime.strptime(time_value, '%H:%M:%S').time()
            except ValueError:
                # Also accept HH:MM format (common variant)
                try:
                    return datetime.strptime(time_value, '%H:%M').time()
                except ValueError:
                    raise ValueError(
                        f"Invalid time format: {time_value}. Expected ISO 8601 format (HH:MM:SS or HH:MM)"
                    )
        raise ValueError(f"Cannot parse time: {time_value}. Expected ISO 8601 format (HH:MM:SS)")
    
    def _parse_boolean(self, value: Any) -> bool:
        """
        Parse boolean from CSV value (handles various formats).
        
        Args:
            value: Boolean value from CSV (bool, string, int, etc.)
            
        Returns:
            bool value
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ('true', '1', 'yes', 'y', 'on'):
                return True
            if value_lower in ('false', '0', 'no', 'n', 'off', ''):
                return False
        return False

