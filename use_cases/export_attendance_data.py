"""
Export attendance data use case.

Orchestrates attendance data export workflow with format conversion.
"""

from dataclasses import dataclass
from typing import Optional, List, Protocol, Union, Tuple
from datetime import date

from domain.entities.attendance_record import AttendanceRecord


@dataclass
class ExportAttendanceDataRequest:
    """Request for exporting attendance data."""
    format: str  # "csv", "json", or "excel"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    user_id: Optional[str] = None


@dataclass
class ExportAttendanceDataResponse:
    """Response from exporting attendance data."""
    success: bool
    data: Optional[Union[bytes, str]] = None
    filename: Optional[str] = None
    error: Optional[str] = None


class AttendanceRepositoryProtocol(Protocol):
    """Protocol for attendance repository operations."""
    
    def get_attendance_history(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[AttendanceRecord]:
        """Get attendance history. Returns list of AttendanceRecord domain entities."""
        ...


class ExportFormatterProtocol(Protocol):
    """Protocol for export formatter operations."""
    
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
        """
        ...


class ExportAttendanceDataUseCase:
    """
    Orchestrates attendance data export workflow.
    
    This use case coordinates data retrieval from repository and formatting
    through formatter interface to export attendance data in various formats.
    """
    
    def __init__(
        self,
        attendance_repository: AttendanceRepositoryProtocol,
        export_formatter: ExportFormatterProtocol
    ):
        """
        Initialize export attendance data use case.
        
        Args:
            attendance_repository: Repository for attendance data retrieval.
            export_formatter: Formatter for converting records to export formats.
        """
        self.attendance_repository = attendance_repository
        self.export_formatter = export_formatter
    
    def execute(
        self,
        request: ExportAttendanceDataRequest
    ) -> ExportAttendanceDataResponse:
        """
        Execute attendance data export workflow.
        
        Args:
            request: Export request with format and filter parameters.
        
        Returns:
            ExportAttendanceDataResponse with formatted data or error information.
        """
        try:
            # Step 1: Validate format
            if request.format.lower() not in ["csv", "json", "excel"]:
                return ExportAttendanceDataResponse(
                    success=False,
                    error=f"Unsupported format: {request.format}. Supported formats: csv, json, excel"
                )
            
            # Step 2: Get attendance records from repository (with filtering)
            records = self.attendance_repository.get_attendance_history(
                user_id=request.user_id,
                start_date=request.start_date,
                end_date=request.end_date
            )
            
            # Step 3: Check if there are records to export
            if not records:
                return ExportAttendanceDataResponse(
                    success=False,
                    error="No attendance records found matching the specified criteria"
                )
            
            # Step 4: Format data using formatter interface
            formatted_data, filename = self.export_formatter.format(
                records=records,
                format_type=request.format.lower()
            )
            
            # Step 5: Return formatted data
            return ExportAttendanceDataResponse(
                success=True,
                data=formatted_data,
                filename=filename
            )
            
        except ValueError as e:
            return ExportAttendanceDataResponse(
                success=False,
                error=f"Invalid request: {str(e)}"
            )
        except Exception as e:
            return ExportAttendanceDataResponse(
                success=False,
                error=f"Failed to export attendance data: {str(e)}"
            )

