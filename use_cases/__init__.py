"""
Application use cases for EyeD AI Attendance System.

This package contains all application layer use cases that orchestrate
domain services and infrastructure to fulfill user requirements.
"""

from .register_user import (
    RegisterUserRequest,
    RegisterUserResponse,
    RegisterUserUseCase
)

from .mark_attendance import (
    MarkAttendanceRequest,
    MarkAttendanceResponse,
    MarkAttendanceUseCase
)

from .generate_report import (
    GenerateReportRequest,
    GenerateReportResponse,
    GenerateReportUseCase
)

from .export_attendance_data import (
    ExportAttendanceDataRequest,
    ExportAttendanceDataResponse,
    ExportAttendanceDataUseCase
)

__all__ = [
    'RegisterUserRequest',
    'RegisterUserResponse',
    'RegisterUserUseCase',
    'MarkAttendanceRequest',
    'MarkAttendanceResponse',
    'MarkAttendanceUseCase',
    'GenerateReportRequest',
    'GenerateReportResponse',
    'GenerateReportUseCase',
    'ExportAttendanceDataRequest',
    'ExportAttendanceDataResponse',
    'ExportAttendanceDataUseCase'
]

