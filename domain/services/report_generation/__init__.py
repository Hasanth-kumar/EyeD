"""
Report generation services.

Contains report generators for different report types following the Strategy pattern.
"""

# Import only what's needed to avoid circular dependencies
from domain.services.report_generation.report_generator import ReportGenerator
from domain.services.report_generation.report_generator_factory import ReportGeneratorFactory

__all__ = [
    'ReportGenerator',
    'ReportGeneratorFactory',
]

