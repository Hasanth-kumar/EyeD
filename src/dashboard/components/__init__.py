"""
Dashboard components package
"""

from .overview import show_dashboard
from .attendance_table import show_attendance_table
from .analytics import show_analytics
from .registration import show_registration
from .testing import show_testing
from .debug import show_debug
from .gamification import show_gamification

__all__ = [
    'show_dashboard',
    'show_attendance_table', 
    'show_analytics',
    'show_registration',
    'show_testing',
    'show_debug',
    'show_gamification'
]

