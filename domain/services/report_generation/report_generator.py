"""
Report generator protocol.

Defines the interface for all report generators.
"""

from typing import Protocol, List, Dict, Any, TYPE_CHECKING
from domain.entities.attendance_record import AttendanceRecord

if TYPE_CHECKING:
    from use_cases.generate_report import GenerateReportRequest


class ReportGenerator(Protocol):
    """Protocol for report generators."""
    
    def generate(
        self,
        records: List[AttendanceRecord],
        request: 'GenerateReportRequest'
    ) -> Dict[str, Any]:
        """
        Generate a report from attendance records.
        
        Args:
            records: List of attendance records to generate report from
            request: Report generation request with filters and parameters
            
        Returns:
            Dictionary containing the generated report data
        """
        ...

