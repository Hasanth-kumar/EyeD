"""
Attendance Table Page - EyeD AI Attendance System
Page 2: Advanced attendance management with filtering, search, and export
"""

import streamlit as st
from src.dashboard.components.attendance_table import show_attendance_table
from src.dashboard.utils.navigation import show_navigation_sidebar, show_page_header, show_page_footer

# Page configuration
st.set_page_config(
    page_title="Attendance Table - EyeD",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set current page in session state for navigation highlighting
st.session_state.current_page = "attendance"

# Hide the top navigation bar
st.markdown("""
<style>
    /* Hide the top navigation bar completely */
    .stApp > header {
        display: none !important;
    }
    
    /* Hide the hamburger menu button */
    .stApp > div[data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* Professional spacing */
    .stApp > div[data-testid="stAppViewContainer"] {
        padding-top: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize services if not already done
def initialize_services():
    """Initialize services for this page"""
    if 'services_initialized' not in st.session_state or not st.session_state.services_initialized:
        try:
            from src.services import (
                get_attendance_service,
                get_attendance_repository,
                get_attendance_manager,
                get_recognition_system
            )
            
            # Initialize services
            attendance_service = get_attendance_service()
            attendance_repository = get_attendance_repository()
            attendance_manager = get_attendance_manager()
            recognition_system = get_recognition_system()
            
            # Store in session state
            st.session_state.attendance_service = attendance_service
            st.session_state.attendance_repository = attendance_repository
            st.session_state.attendance_manager = attendance_manager
            st.session_state.recognition_system = recognition_system
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
    title="Attendance Table",
    description="Advanced Attendance Management with Filtering & Analytics",
    icon="📋"
)

# Show the attendance table component
show_attendance_table()

# Page footer
show_page_footer("Attendance Table")
