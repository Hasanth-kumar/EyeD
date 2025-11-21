"""
Export formatter for attendance data.

This module provides formatting functionality for exporting attendance records
in various formats (CSV, JSON, Excel). It implements the ExportFormatterProtocol
from the use case layer.
"""

import io
import json
import logging
from datetime import datetime
from typing import List, Tuple, Union

import pandas as pd

from domain.entities.attendance_record import AttendanceRecord

logger = logging.getLogger(__name__)


class ExportFormatter:
    """
    Formatter for exporting attendance records in various formats.
    
    This class implements the ExportFormatterProtocol and handles ONLY
    data formatting operations. No business logic or data access is performed here.
    """
    
    def format(
        self,
        records: List[AttendanceRecord],
        format_type: str
    ) -> Tuple[Union[bytes, str], str]:
        """
        Format attendance records into specified format.
        
        Args:
            records: List of AttendanceRecord domain entities to format.
            format_type: Format type ("csv", "json", or "excel").
        
        Returns:
            Tuple of (formatted_data, filename).
            
        Raises:
            ValueError: If format_type is not supported.
        """
        format_type_lower = format_type.lower()
        
        if format_type_lower == "csv":
            return self._format_csv(records)
        elif format_type_lower == "json":
            return self._format_json(records)
        elif format_type_lower == "excel":
            return self._format_excel(records)
        else:
            raise ValueError(
                f"Unsupported format: {format_type}. Supported formats: csv, json, excel"
            )
    
    def _format_csv(self, records: List[AttendanceRecord]) -> Tuple[str, str]:
        """
        Format records as CSV string.
        
        Args:
            records: List of AttendanceRecord entities.
        
        Returns:
            Tuple of (CSV string, filename).
        """
        # Convert records to list of dictionaries
        data = self._records_to_dict_list(records)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Convert to CSV string
        csv_string = df.to_csv(index=False)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"attendance_export_{timestamp}.csv"
        
        logger.info(f"Formatted {len(records)} records as CSV")
        
        return csv_string, filename
    
    def _format_json(self, records: List[AttendanceRecord]) -> Tuple[str, str]:
        """
        Format records as JSON string.
        
        Args:
            records: List of AttendanceRecord entities.
        
        Returns:
            Tuple of (JSON string, filename).
        """
        # Convert records to list of dictionaries
        data = self._records_to_dict_list(records)
        
        # Convert to JSON string with indentation for readability
        json_string = json.dumps(data, indent=2, default=str)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"attendance_export_{timestamp}.json"
        
        logger.info(f"Formatted {len(records)} records as JSON")
        
        return json_string, filename
    
    def _format_excel(self, records: List[AttendanceRecord]) -> Tuple[bytes, str]:
        """
        Format records as Excel file bytes.
        
        Args:
            records: List of AttendanceRecord entities.
        
        Returns:
            Tuple of (Excel bytes, filename).
        """
        # Convert records to list of dictionaries
        data = self._records_to_dict_list(records)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Convert to Excel bytes
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Attendance Records')
        excel_bytes = excel_buffer.getvalue()
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"attendance_export_{timestamp}.xlsx"
        
        logger.info(f"Formatted {len(records)} records as Excel")
        
        return excel_bytes, filename
    
    def _records_to_dict_list(self, records: List[AttendanceRecord]) -> List[dict]:
        """
        Convert list of AttendanceRecord entities to list of dictionaries.
        
        Args:
            records: List of AttendanceRecord entities.
        
        Returns:
            List of dictionaries representing attendance records.
        """
        return [
            {
                "Record ID": record.record_id,
                "User ID": record.user_id,
                "User Name": record.user_name,
                "Date": record.date.isoformat() if record.date else "",
                "Time": record.time.strftime("%H:%M:%S") if record.time else "",
                "Status": record.status,
                "Confidence": f"{record.confidence:.4f}",
                "Liveness Verified": "Yes" if record.liveness_verified else "No",
                "Face Quality Score": f"{record.face_quality_score:.4f}",
                "Processing Time (ms)": f"{record.processing_time_ms:.2f}",
                "Verification Stage": record.verification_stage,
                "Session ID": record.session_id,
                "Device Info": record.device_info,
                "Location": record.location
            }
            for record in records
        ]












