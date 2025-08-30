"""
Navigation Utilities for EyeD Dashboard
Provides consistent navigation and page switching functionality
"""

import streamlit as st
from typing import Optional

def show_navigation_sidebar():
    """Display consistent navigation sidebar across all pages"""
    
    st.sidebar.title("👁️ EyeD Navigation")
    st.sidebar.markdown("**AI Attendance System**")
    
    # Navigation menu
    st.sidebar.markdown("---")
    st.sidebar.subheader("📱 Pages")
    
    # Page navigation buttons
    if st.sidebar.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")
    
    if st.sidebar.button("📊 Dashboard Overview", use_container_width=True):
        st.switch_page("pages/Dashboard.py")
    
    if st.sidebar.button("📋 Attendance Table", use_container_width=True):
        st.switch_page("pages/Attendance.py")
    
    if st.sidebar.button("📈 Analytics", use_container_width=True):
        st.switch_page("pages/Analytics.py")
    
    if st.sidebar.button("👤 Registration", use_container_width=True):
        st.switch_page("pages/Registration.py")
    
    if st.sidebar.button("🧪 Testing", use_container_width=True):
        st.switch_page("pages/Testing.py")
    
    if st.sidebar.button("🐛 Debug", use_container_width=True):
        st.switch_page("pages/Debug.py")
    
    if st.sidebar.button("🎮 Gamification", use_container_width=True):
        st.switch_page("pages/Gamification.py")
    
    # System status
    st.sidebar.markdown("---")
    st.sidebar.subheader("🏥 System Status")
    
    try:
        if 'services_initialized' in st.session_state and st.session_state.services_initialized:
            attendance_service = st.session_state.get('attendance_service')
            face_database = st.session_state.get('face_database')
            
            if attendance_service and face_database:
                total_users = len(face_database.users_db) if face_database else 0
                today_attendance = attendance_service.get_attendance_report_by_type("today_count") if attendance_service else 0
                
                st.sidebar.metric("👥 Users", total_users)
                st.sidebar.metric("📅 Today", today_attendance)
                st.sidebar.success("🟢 Operational")
            else:
                st.sidebar.warning("⚠️ Services Loading")
        else:
            st.sidebar.info("🔄 Initializing...")
    except Exception as e:
        st.sidebar.error("🔴 Error")
    
    # Quick actions
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚡ Quick Actions")
    
    if st.sidebar.button("🔄 Refresh", use_container_width=True):
        st.rerun()
    
    if st.sidebar.button("📊 Export", use_container_width=True):
        st.info("Export available in individual pages")
    
    # Architecture info
    st.sidebar.markdown("---")
    st.sidebar.subheader("🏗️ Architecture")
    st.sidebar.info("""
    **Page-Based Design:**
    - 7 Focused Pages ✅
    - Service Layer ✅
    - Clean Architecture ✅
    """)

def show_page_header(title: str, description: str, icon: str):
    """Display consistent page header across all pages"""
    
    st.title(f"{icon} {title}")
    st.markdown(f"**{description}**")
    
    # Navigation indicator
    st.sidebar.success(f"📍 **Current Page**: {title}")
    st.sidebar.info("Use sidebar to navigate between pages")

def show_page_footer(page_name: str):
    """Display consistent page footer across all pages"""
    
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: #666;'>
            <p>{page_name} | EyeD AI Attendance System</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def create_breadcrumb(current_page: str):
    """Create breadcrumb navigation for better UX"""
    
    st.markdown(f"**🏠 Home** > **{current_page}**")
    st.markdown("---")
