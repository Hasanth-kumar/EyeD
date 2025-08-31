"""
Navigation Utilities for EyeD Dashboard
Provides consistent navigation and page switching functionality
"""

import streamlit as st
from typing import Optional
import os

def get_current_page() -> str:
    """Determine the current page based on the script path"""
    try:
        # Get the current script path from Streamlit
        import inspect
        frame = inspect.currentframe()
        while frame:
            filename = frame.f_code.co_filename
            if 'pages' in filename:
                if 'Dashboard.py' in filename:
                    return "dashboard"
                elif 'Attendance.py' in filename:
                    return "attendance"
                elif 'Daily_Attendance.py' in filename:
                    return "daily_attendance"
                elif 'Registration.py' in filename:
                    return "registration"
                elif 'Analytics.py' in filename:
                    return "analytics"
                elif 'Gamification.py' in filename:
                    return "gamification"
                elif 'Testing.py' in filename:
                    return "testing"
                elif 'Debug.py' in filename:
                    return "debug"
            elif 'app.py' in filename:
                return "home"
            frame = frame.f_back
        
        # Fallback: check session state for page info
        page_name = st.session_state.get('current_page', '')
        if page_name:
            return page_name.lower()
        
        return "home"  # Default to home
    except Exception:
        return "home"  # Default to home on error

def show_navigation_sidebar():
    """Display professional navigation sidebar across all pages"""
    
    # Get current page to highlight active navigation
    current_page = get_current_page()
    
    # Hide Streamlit's built-in page navigation
    st.markdown("""
    <style>
        /* Hide Streamlit's built-in page navigation */
        .stSidebar .stSelectbox {
            display: none !important;
        }
        
        /* Hide the page navigation section */
        .stSidebar [data-testid="stSidebarNav"] {
            display: none !important;
        }
        
        /* Alternative selector for page navigation */
        .stSidebar .css-1d391kg {
            display: none !important;
        }
        
        /* Modern navigation button styling */
        .stSidebar .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            margin: 4px 0 !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
            transition: all 0.3s ease !important;
            text-align: left !important;
            width: 100% !important;
        }
        
        .stSidebar .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
        }
        
        /* Active navigation button styling */
        .stSidebar .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #1f77b4 0%, #17a2b8 100%) !important;
            color: white !important;
            border: 2px solid #1f77b4 !important;
            font-weight: 600 !important;
            box-shadow: 0 6px 20px rgba(31, 119, 180, 0.4) !important;
        }
        
        .stSidebar .stButton > button[kind="secondary"] {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
            color: #495057 !important;
            border: 1px solid #dee2e6 !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        }
        
        .stSidebar .stButton > button[kind="secondary"]:hover {
            background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%) !important;
            color: #343a40 !important;
        }
        
        /* Navigation section styling */
        .stSidebar .element-container:has(.stMarkdown) h3 {
            color: #495057 !important;
            font-weight: 600 !important;
            margin-bottom: 12px !important;
            padding-bottom: 8px !important;
            border-bottom: 2px solid #e9ecef !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Modern professional header with enhanced styling
    st.sidebar.markdown("""
    <div style='
        text-align: center; 
        padding: 1.5rem 1rem; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    '>
        <h2 style='color: white; margin: 0; font-size: 1.8rem; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.3);'>👁️ EyeD</h2>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.95rem; font-weight: 500;'>AI Attendance System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main navigation menu
    st.sidebar.markdown("### 🧭 Navigation")
    
    # Core pages - organized by priority
    if st.sidebar.button("🏠 Home", use_container_width=True, key="nav_home", 
                        type="primary" if current_page == "home" else "secondary"):
        st.switch_page("app.py")
    
    if st.sidebar.button("📊 Dashboard", use_container_width=True, key="nav_dashboard",
                        type="primary" if current_page == "dashboard" else "secondary"):
        st.switch_page("pages/Dashboard.py")
    
    if st.sidebar.button("📋 Attendance", use_container_width=True, key="nav_attendance",
                        type="primary" if current_page == "attendance" else "secondary"):
        st.switch_page("pages/Attendance.py")
    
    if st.sidebar.button("📅 Daily Attendance", use_container_width=True, key="nav_daily_attendance",
                        type="primary" if current_page == "daily_attendance" else "secondary"):
        st.switch_page("pages/Daily_Attendance.py")
    
    if st.sidebar.button("👤 Registration", use_container_width=True, key="nav_registration",
                        type="primary" if current_page == "registration" else "secondary"):
        st.switch_page("pages/Registration.py")
    
    # Secondary pages
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Analytics & Tools")
    
    if st.sidebar.button("📈 Analytics", use_container_width=True, key="nav_analytics",
                        type="primary" if current_page == "analytics" else "secondary"):
        st.switch_page("pages/Analytics.py")
    
    if st.sidebar.button("🎮 Gamification", use_container_width=True, key="nav_gamification",
                        type="primary" if current_page == "gamification" else "secondary"):
        st.switch_page("pages/Gamification.py")
    
    # System tools
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔧 System Tools")
    
    if st.sidebar.button("🧪 Testing", use_container_width=True, key="nav_testing",
                        type="primary" if current_page == "testing" else "secondary"):
        st.switch_page("pages/Testing.py")
    
    if st.sidebar.button("🐛 Debug", use_container_width=True, key="nav_debug",
                        type="primary" if current_page == "debug" else "secondary"):
        st.switch_page("pages/Debug.py")
    
    # System status - modern and professional
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 System Status")
    
    try:
        if 'services_initialized' in st.session_state and st.session_state.services_initialized:
            attendance_service = st.session_state.get('attendance_service')
            face_database = st.session_state.get('face_database')
            
            if attendance_service and face_database:
                total_users = len(face_database.users_db) if face_database else 0
                today_attendance = attendance_service.get_attendance_report_by_type("today_count") if attendance_service else 0
                
                # Modern metrics display with enhanced styling
                st.sidebar.markdown("""
                <div style='
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                    padding: 1rem;
                    border-radius: 10px;
                    margin: 0.5rem 0;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                '>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    st.sidebar.metric("👥 Users", total_users, help="Total registered users")
                with col2:
                    st.sidebar.metric("📅 Today", today_attendance, help="Today's attendance count")
                
                st.sidebar.markdown("</div>", unsafe_allow_html=True)
                st.sidebar.success("🟢 System Online")
            else:
                st.sidebar.warning("⚠️ Services Loading")
        else:
            st.sidebar.info("🔄 Initializing...")
    except Exception as e:
        st.sidebar.error("🔴 System Error")
    
    # Quick actions - modern and useful
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ Quick Actions")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.sidebar.button("🔄", key="sidebar_refresh_btn", help="Refresh page", 
                            type="secondary"):
            st.rerun()
    with col2:
        if st.sidebar.button("ℹ️", key="sidebar_info_btn", help="System info", 
                            type="secondary"):
            st.sidebar.info("Use individual pages for detailed actions")

def show_page_header(title: str, description: str, icon: str):
    """Display professional page header across all pages"""
    
    # Professional page header with styling
    st.markdown(f"""
    <div style='background: linear-gradient(90deg, #1f77b4, #17a2b8); padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; color: white;'>
        <h1 style='color: white; margin: 0; font-size: 2.5rem;'>{icon} {title}</h1>
        <p style='color: #e8f4f8; margin: 0.5rem 0 0 0; font-size: 1.1rem;'>{description}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation indicator in sidebar
    st.sidebar.markdown(f"""
    <div style='background: #e8f4f8; padding: 0.5rem; border-radius: 5px; margin-bottom: 1rem; text-align: center;'>
        <strong style='color: #1f77b4;'>📍 Current Page</strong><br>
        <span style='color: #666;'>{icon} {title}</span>
    </div>
    """, unsafe_allow_html=True)

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


