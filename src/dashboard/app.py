"""
Streamlit Dashboard for EyeD AI Attendance System
Day 10 Implementation: Basic Dashboard Skeleton

This module will provide:
- Main dashboard interface
- Attendance logs view
- Analytics and charts
- User registration interface
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

def main():
    """Main Streamlit dashboard"""
    st.set_page_config(
        page_title="EyeD - AI Attendance System",
        page_icon="👁️",
        layout="wide"
    )
    
    st.title("👁️ EyeD - AI Attendance System")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Attendance Logs", "Analytics", "Register User"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Attendance Logs":
        show_attendance_logs()
    elif page == "Analytics":
        show_analytics()
    elif page == "Register User":
        show_user_registration()
    
    # Footer
    st.markdown("---")
    st.markdown("*EyeD - Making attendance smart, secure, and simple! 🚀*")

def show_dashboard():
    """Show main dashboard"""
    st.header("📊 Dashboard Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", "0", "Not yet implemented")
    
    with col2:
        st.metric("Today's Attendance", "0", "Not yet implemented")
    
    with col3:
        st.metric("Recognition Accuracy", "0%", "Not yet implemented")
    
    with col4:
        st.metric("System Status", "🟡 Setup", "Day 1 Complete")
    
    st.info("🚧 Dashboard features will be implemented in Phase 4 (Days 10-14)")

def show_attendance_logs():
    """Show attendance logs"""
    st.header("📋 Attendance Logs")
    st.info("🚧 Attendance logs will be implemented in Phase 3 (Days 8-9)")

def show_analytics():
    """Show analytics and charts"""
    st.header("📈 Analytics")
    st.info("🚧 Analytics will be implemented in Phase 4 (Days 10-14)")

def show_user_registration():
    """Show user registration form"""
    st.header("👤 User Registration")
    st.info("🚧 User registration will be implemented in Phase 1 (Days 2-3)")

if __name__ == "__main__":
    main()
