"""
Streamlit Dashboard for EyeD AI Attendance System
Day 11 Implementation: Enhanced Attendance Table with Modular Architecture

This module provides:
- Main dashboard interface with modular components
- Enhanced attendance table view (Day 11)
- Analytics and charts
- User registration interface
- Testing suite
- Debug tools
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import time
from datetime import datetime
import cv2
import numpy as np
import io
from PIL import Image

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import modular components
from src.dashboard.components.overview import show_dashboard
from src.dashboard.components.attendance_table import show_attendance_table
from src.dashboard.components.analytics import show_analytics
from src.dashboard.components.registration import show_registration
from src.dashboard.components.testing import show_testing
from src.dashboard.components.debug import show_debug
from src.dashboard.components.gamification import show_gamification

# Import mock systems
from src.dashboard.utils.mock_systems import MockFaceDatabase, MockAttendanceManager

# Page configuration - MUST be called first before any other Streamlit commands
st.set_page_config(
    page_title="EyeD AI Attendance Dashboard",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'face_db' not in st.session_state:
        st.session_state.face_db = None
    if 'attendance_manager' not in st.session_state:
        st.session_state.attendance_manager = None
    if 'performance_metrics' not in st.session_state:
        st.session_state.performance_metrics = []
    if 'debug_logs' not in st.session_state:
        st.session_state.debug_logs = []

def initialize_systems():
    """Initialize all required systems"""
    try:
        # Always use mock systems for now
        if st.session_state.face_db is None:
            st.session_state.face_db = MockFaceDatabase()
        if st.session_state.attendance_manager is None:
            st.session_state.attendance_manager = MockAttendanceManager()
        return True
    except Exception as e:
        st.error(f"Failed to initialize systems: {e}")
        return False

def main():
    """Main dashboard application"""
    # Initialize session state
    initialize_session_state()
    
    # Sidebar navigation
    st.sidebar.title("👁️ EyeD Dashboard")
    st.sidebar.markdown("**AI Attendance System**")
    
    # Navigation menu
    page = st.sidebar.selectbox(
        "Navigation",
        [
            "📊 Dashboard Overview",
            "📋 Enhanced Attendance Table",
            "📈 Analytics & Insights", 
            "👤 User Registration",
            "🧪 Testing Suite",
            "🐛 Debug Tools",
            "🎮 Gamification"
        ]
    )
    
    # System status in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("System Status")
    
    if initialize_systems():
        # Get system metrics
        face_db = st.session_state.face_db
        attendance_manager = st.session_state.attendance_manager
        
        total_users = len(face_db.users_db) if face_db else 0
        today_attendance = attendance_manager.get_today_attendance_count() if attendance_manager else 0
        
        st.sidebar.metric("Total Users", total_users)
        st.sidebar.metric("Today's Attendance", today_attendance)
        st.sidebar.success("🟢 System Operational")
    else:
        st.sidebar.error("🔴 System Error")
    
    # Quick actions
    st.sidebar.markdown("---")
    st.sidebar.subheader("Quick Actions")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    with col2:
        if st.button("📊 Export Data"):
            st.info("Export functionality available in individual sections")
    
    # Main content area
    if page == "📊 Dashboard Overview":
        show_dashboard()
    
    elif page == "📋 Enhanced Attendance Table":
        show_attendance_table()
    
    elif page == "📈 Analytics & Insights":
        show_analytics()
    
    elif page == "👤 User Registration":
        show_registration()
    
    elif page == "🧪 Testing Suite":
        show_testing()
    
    elif page == "🐛 Debug Tools":
        show_debug()
    
    elif page == "🎮 Gamification":
        show_gamification()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>👁️ EyeD AI Attendance System | Day 14 Implementation | Gamification & User Engagement</p>
            <p>Built with Streamlit, OpenCV, and DeepFace</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
