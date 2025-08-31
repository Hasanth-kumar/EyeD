"""
Analytics & Insights Page - EyeD AI Attendance System
Page 3: Comprehensive analytics, charts, and trend analysis
"""

import streamlit as st
from src.dashboard.components.analytics import show_analytics
from src.dashboard.utils.navigation import show_navigation_sidebar, show_page_header, show_page_footer

# Page configuration
st.set_page_config(
    page_title="Analytics & Insights - EyeD",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set current page in session state for navigation highlighting
st.session_state.current_page = "analytics"

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
    """Initialize services for this page with proper feedback"""
    if 'services_initialized' not in st.session_state or not st.session_state.services_initialized:
        # Show loading indicator
        with st.spinner("🔄 Initializing services..."):
            try:
                from src.services import (
                    get_attendance_service,
                    get_attendance_repository,
                    get_attendance_manager,
                    get_face_database
                )
                
                # Initialize services with individual feedback
                try:
                    attendance_service = get_attendance_service()
                    st.success("✅ Attendance service initialized")
                except Exception as e:
                    st.error(f"❌ Failed to initialize attendance service: {e}")
                    return False
                    
                try:
                    attendance_repository = get_attendance_repository()
                    st.success("✅ Attendance repository initialized")
                except Exception as e:
                    st.error(f"❌ Failed to initialize attendance repository: {e}")
                    return False
                    
                try:
                    attendance_manager = get_attendance_manager()
                    st.success("✅ Attendance manager initialized")
                except Exception as e:
                    st.error(f"❌ Failed to initialize attendance manager: {e}")
                    return False
                    
                try:
                    face_database = get_face_database()
                    st.success("✅ Face database initialized")
                except Exception as e:
                    st.error(f"❌ Failed to initialize face database: {e}")
                    return False
                
                # Store in session state
                st.session_state.attendance_service = attendance_service
                st.session_state.attendance_repository = attendance_repository
                st.session_state.attendance_manager = attendance_manager
                st.session_state.face_database = face_database
                st.session_state.services_initialized = True
                
                st.success("🎉 All services initialized successfully!")
                return True
                
            except Exception as e:
                st.error(f"❌ Failed to initialize services: {e}")
                st.error("Please check the console for detailed error information")
                return False
    else:
        # Services already initialized
        st.success("✅ Services already initialized")
        return True

# Initialize services
if not initialize_services():
    st.error("⚠️ Services Loading Failed")
    st.stop()

# Show navigation sidebar
show_navigation_sidebar()

# Page header
show_page_header(
    title="Analytics & Insights",
    description="Comprehensive Data Analysis, Trends & Performance Metrics",
    icon="📈"
)

# Show the analytics component
show_analytics()

# Page footer
show_page_footer("Analytics & Insights")
