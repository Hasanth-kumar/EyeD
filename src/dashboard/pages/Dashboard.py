"""
Dashboard Overview Page - EyeD AI Attendance System
Page 1: Main dashboard with overview metrics and system status
"""

import streamlit as st
from src.dashboard.components.overview import show_dashboard
from src.dashboard.utils.navigation import show_navigation_sidebar, show_page_header, show_page_footer

# Page configuration
st.set_page_config(
    page_title="Dashboard Overview - EyeD",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services if not already done
def initialize_services():
    """Initialize services for this page"""
    if 'services_initialized' not in st.session_state or not st.session_state.services_initialized:
        try:
            from src.services import (
                get_attendance_service,
                get_attendance_repository,
                get_attendance_manager,
                get_face_database
            )
            
            # Initialize services
            attendance_service = get_attendance_service()
            attendance_repository = get_attendance_repository()
            attendance_manager = get_attendance_manager()
            face_database = get_face_database()
            
            # Store in session state
            st.session_state.attendance_service = attendance_service
            st.session_state.attendance_repository = attendance_repository
            st.session_state.attendance_manager = attendance_manager
            st.session_state.face_database = face_database
            st.session_state.services_initialized = True
            
        except Exception as e:
            st.error(f"Failed to initialize services: {e}")
            return False
    return True

# Initialize services
initialize_services()

# Show navigation sidebar
show_navigation_sidebar()

# Page header
show_page_header(
    title="Dashboard Overview",
    description="AI Attendance System - Real-time Insights & System Status",
    icon="📊"
)

# Show the dashboard overview component
show_dashboard()

# Page footer
show_page_footer("Dashboard Overview")
