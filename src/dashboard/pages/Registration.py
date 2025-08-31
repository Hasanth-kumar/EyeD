"""
User Registration Page - EyeD AI Attendance System
Page 4: User registration with face capture and quality assessment
"""

import streamlit as st
from pathlib import Path
from src.dashboard.components.registration import show_registration
from src.dashboard.utils.navigation import show_navigation_sidebar, show_page_header, show_page_footer

# Page configuration
st.set_page_config(
    page_title="User Registration - EyeD",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set current page in session state for navigation highlighting
st.session_state.current_page = "registration"

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
            st.info("🔄 Initializing services...")
            
            # Check if data directory exists
            data_dir = Path("data/faces")
            if not data_dir.exists():
                st.warning(f"⚠️ Data directory {data_dir} does not exist. Creating it...")
                data_dir.mkdir(parents=True, exist_ok=True)
                st.success(f"✅ Created data directory: {data_dir}")
            
            from src.services import (
                get_attendance_service,
                get_attendance_repository,
                get_attendance_manager,
                get_face_database
            )
            
            # Initialize services with error handling
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
    return True

# Initialize services
if not initialize_services():
    st.error("❌ Service initialization failed!")
    st.info("This could be due to missing dependencies or configuration issues.")
    
    # Add retry button
    if st.button("🔄 Retry Service Initialization"):
        st.rerun()
    
    # Show troubleshooting info
    st.subheader("🔧 Troubleshooting")
    st.markdown("""
    1. **Check Console**: Look for detailed error messages in the browser console
    2. **Verify Dependencies**: Ensure all required packages are installed
    3. **Check File Paths**: Verify that data directories exist
    4. **Restart Application**: Try refreshing the page or restarting the app
    """)
    
    st.stop()

# Show navigation sidebar
show_navigation_sidebar()

# Page header
show_page_header(
    title="User Registration",
    description="Add New Users with Face Capture & Quality Assessment",
    icon="👤"
)

# Show the registration component
show_registration()

# Page footer
show_page_footer("User Registration")
