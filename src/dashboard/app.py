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
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'services_initialized' not in st.session_state:
        st.session_state.services_initialized = False
    if 'performance_metrics' not in st.session_state:
        st.session_state.performance_metrics = []
    if 'debug_logs' not in st.session_state:
        st.session_state.debug_logs = []

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
    """Main dashboard application - simplified for page-based navigation"""
    # Initialize session state
    initialize_session_state()
    
    # Main title and description
    st.title("👁️ EyeD AI Attendance System")
    st.markdown("**Smart, Secure, and Simple Attendance Management with AI**")
    
    # Architecture info
    st.info("""
    🏗️ **New Page-Based Architecture**: 
    - **7 Dedicated Pages**: Each feature has its own focused page
    - **Faster Navigation**: Independent page loading for better performance
    - **Cleaner Code**: Smaller, maintainable files
    - **Service Layer**: Maintains clean architecture with dependency injection
    """)
    
    # Quick navigation guide
    st.subheader("🚀 Quick Navigation")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📊 Dashboard Overview**")
        st.markdown("System metrics, performance, and status")
        
    with col2:
        st.markdown("**📋 Attendance Table**")
        st.markdown("Manage and view attendance records")
        
    with col3:
        st.markdown("**📈 Analytics**")
        st.markdown("Charts, trends, and insights")
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("**👤 Registration**")
        st.markdown("Add new users with face capture")
        
    with col5:
        st.markdown("**🧪 Testing**")
        st.markdown("Quality assessment tools")
        
    with col6:
        st.markdown("**🎮 Gamification**")
        st.markdown("Badges, achievements, leaderboards")
    
    # System status
    st.subheader("🏥 System Status")
    
    if initialize_services():
        try:
            attendance_service = st.session_state.attendance_service
            face_database = st.session_state.face_database
            
            # Get metrics through service methods
            total_users = len(face_database.users_db) if face_database else 0
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
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh System"):
            st.rerun()
    
    with col2:
        if st.button("📊 View Dashboard"):
            st.switch_page("src/dashboard/pages/Dashboard.py")
    
    with col3:
        if st.button("👤 Add User"):
            st.switch_page("src/dashboard/pages/Registration.py")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>👁️ EyeD AI Attendance System | Page-Based Architecture | Service Layer Implementation</p>
            <p>Built with Streamlit, OpenCV, and DeepFace | Clean Architecture & Modular Design</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
