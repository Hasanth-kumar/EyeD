"""
Main Dashboard Application - EyeD AI Attendance System
Simplified main app with page-based navigation
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import service layer
from src.services import (
    get_attendance_service,
    get_attendance_repository,
    get_attendance_manager,
    get_face_database
)

# Page configuration - MUST be called first before any other Streamlit commands
st.set_page_config(
    page_title="EyeD AI Attendance System",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide the top navigation bar completely
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

def initialize_session_state():
    """Initialize session state variables"""
    if 'services_initialized' not in st.session_state:
        st.session_state.services_initialized = False
    if 'performance_metrics' not in st.session_state:
        st.session_state.performance_metrics = []
    if 'debug_logs' not in st.session_state:
        st.session_state.debug_logs = []
    # Set current page for navigation highlighting
    st.session_state.current_page = "home"

def initialize_services():
    """Initialize all required services using dependency injection"""
    try:
        if not st.session_state.services_initialized:
            # Initialize services through the service layer
            attendance_service = get_attendance_service()
            attendance_repository = get_attendance_repository()
            attendance_manager = get_attendance_manager()
            face_database = get_face_database()
            
            # Store services in session state for components to use
            st.session_state.attendance_service = attendance_service
            st.session_state.attendance_repository = attendance_repository
            st.session_state.attendance_manager = attendance_manager
            st.session_state.face_database = face_database
            st.session_state.services_initialized = True
            
            st.success("✅ Services initialized successfully")
            return True
        return True
    except Exception as e:
        st.error(f"Failed to initialize services: {e}")
        return False

def main():
    """Main dashboard application - simplified landing page with navigation"""
    # Initialize session state
    initialize_session_state()
    
    # Show navigation sidebar
    from src.dashboard.utils.navigation import show_navigation_sidebar
    show_navigation_sidebar()
    
    # EyeD Header - Professional styling
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0; background: linear-gradient(90deg, #1f77b4, #17a2b8); border-radius: 10px; margin-bottom: 2rem; color: white;'>
        <h1 style='color: white; margin: 0; font-size: 3rem; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>👁️ EyeD</h1>
        <p style='color: #e8f4f8; margin: 0.5rem 0 0 0; font-size: 1.3rem; font-weight: 500;'>AI Attendance System</p>
        <p style='color: #d1ecf1; margin: 0.5rem 0 0 0; font-size: 1rem;'>Smart, Secure, and Simple Attendance Management with AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome message
    st.markdown("""
    ### Welcome to EyeD AI Attendance System
    
    This intelligent attendance management system uses advanced facial recognition technology 
    to provide secure, accurate, and efficient attendance tracking.
    
    **Key Features:**
    - 🎯 **AI-Powered Recognition**: Advanced facial recognition with liveness detection
    - 📊 **Real-time Analytics**: Comprehensive insights and performance metrics
    - 🔒 **Secure & Private**: Local processing with no cloud dependencies
    - 📱 **User-Friendly**: Intuitive interface for easy management
    - 🎮 **Gamification**: Engagement features to boost participation
    """)
    
    # Initialize services and show status
    st.subheader("🏥 System Status")
    
    if initialize_services():
        try:
            attendance_service = st.session_state.attendance_service
            face_database = st.session_state.face_database
            
            # Get metrics through service methods
            total_users = len(face_database.list_faces()) if face_database else 0
            today_attendance = attendance_service.get_attendance_report_by_type("today_count") if attendance_service else 0
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Users", total_users)
                
            with col2:
                st.metric("Today's Attendance", today_attendance)
                
            with col3:
                st.success("🟢 System Operational")
                
        except Exception as e:
            st.warning(f"⚠️ Limited functionality: {e}")
            st.info("Some features may not be available")
    else:
        st.error("🔴 System Error")
    
    # Navigation instructions
    st.subheader("🚀 Getting Started")
    st.markdown("""
    **Access different features using the page navigation:**
    
    - **📊 Dashboard Overview**: System metrics and performance insights
    - **📋 Attendance Table**: Manage and view attendance records
    - **📅 Daily Attendance**: Real-time face recognition with liveness detection
    - **📈 Analytics**: Charts, trends, and detailed analysis
    - **👤 Registration**: Add new users with face capture
    - **🧪 Testing**: Test system components and functionality
    - **🐛 Debug**: System diagnostics and troubleshooting
    - **🎮 Gamification**: User engagement and rewards
    """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>👁️ EyeD AI Attendance System</p>
            <p>Built with Streamlit, OpenCV, and DeepFace</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
