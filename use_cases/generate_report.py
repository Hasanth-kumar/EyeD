"""
Generate report use case.

Orchestrates report generation workflow with metrics calculation and timeline analysis.
"""

from dataclasses import dataclass
from typing import Optional, List, Protocol, Dict, Any
from datetime import date, datetime

from domain.entities.attendance_record import AttendanceRecord
from domain.services.report_generation import ReportGeneratorFactory


@dataclass
class GenerateReportRequest:
    """Request for generating a report."""
    report_type: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    user_id: Optional[str] = None


@dataclass
class GenerateReportResponse:
    """Response from report generation."""
    success: bool
    report_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
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


class UserRepositoryProtocol(Protocol):
    """Protocol for user repository operations."""
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user by ID. Returns dict with 'success' and 'data' keys."""
        ...


class GenerateReportUseCase:
    """Orchestrates report generation workflow."""
    
    def __init__(
        self,
        report_generator_factory: ReportGeneratorFactory,
        attendance_repository: AttendanceRepositoryProtocol
    ):
        """
        Initialize report generation use case.
        
        Args:
            report_generator_factory: Factory for creating report generators
            attendance_repository: Repository for attendance data
        """
        self.report_generator_factory = report_generator_factory
        self.attendance_repository = attendance_repository
    
    def execute(self, request: GenerateReportRequest) -> GenerateReportResponse:
        """Execute report generation workflow."""
        try:
            # Get filtered records from repository
            records = self._get_and_filter_records(request)
            
            # Get appropriate report generator and generate report
            generator = self.report_generator_factory.create(request.report_type)
            report_data = generator.generate(records, request)
            
            # Format report with filters
            formatted_report = self._format_report(report_data, request)
            
            return GenerateReportResponse(
                success=True,
                report_data=formatted_report,
                metadata=self._generate_metadata(request, len(records))
            )
        except ValueError as e:
            return GenerateReportResponse(success=False, error=f"Invalid request: {str(e)}")
        except Exception as e:
            return GenerateReportResponse(success=False, error=f"Failed to generate report: {str(e)}")
    
    def _get_and_filter_records(self, request: GenerateReportRequest) -> List[AttendanceRecord]:
        """Get attendance records from repository (already filtered and converted to domain entities)."""
        # Repository handles filtering and conversion, so we just get the records
        # Additional filtering is already done by repository based on request parameters
        records = self.attendance_repository.get_attendance_history(
            user_id=request.user_id, start_date=request.start_date, end_date=request.end_date
        )
        # Repository already applies filters, but we do a final check for edge cases
        return [r for r in records if self._should_include_record(r, request)]
    
    def _should_include_record(self, record: AttendanceRecord, request: GenerateReportRequest) -> bool:
        """Check if record should be included based on filters (additional validation)."""
        # Repository already filters, but this provides extra safety
        if request.user_id and record.user_id != request.user_id:
            return False
        if request.start_date and record.date < request.start_date:
            return False
        if request.end_date and record.date > request.end_date:
            return False
        return True
    
    
    def _format_report(self, report_data: Dict[str, Any], request: GenerateReportRequest) -> Dict[str, Any]:
        """Format report data for output."""
        formatted = report_data.copy()
        formatted["filters"] = {
            "start_date": request.start_date.isoformat() if request.start_date else None,
            "end_date": request.end_date.isoformat() if request.end_date else None,
            "user_id": request.user_id
        }
        return formatted
    
    def _generate_metadata(self, request: GenerateReportRequest, record_count: int) -> Dict[str, Any]:
        """Generate report metadata."""
        return {
            "report_type": request.report_type, "generated_at": datetime.now().isoformat(), "record_count": record_count,
            "filters_applied": {
                "start_date": request.start_date.isoformat() if request.start_date else None,
                "end_date": request.end_date.isoformat() if request.end_date else None, "user_id": request.user_id
            }
        }
