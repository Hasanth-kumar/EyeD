"""
Dashboard Overview Component
Handles main dashboard metrics and system health display
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from src.dashboard.utils.mock_systems import MockFaceDatabase, MockAttendanceManager

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

def get_dashboard_metrics():
    """Get real-time dashboard metrics"""
    try:
        face_db = st.session_state.face_db
        attendance_manager = st.session_state.attendance_manager
        
        # Get user count
        total_users = len(face_db.users_db) if face_db else 0
        
        # Get today's attendance
        today_attendance = attendance_manager.get_today_attendance_count() if attendance_manager else 0
        
        # Get recognition accuracy
        recognition_accuracy = attendance_manager.get_recognition_accuracy() if attendance_manager else "0%"
        
        # Get system status
        system_status = "🟢 Operational" if face_db and attendance_manager else "🟡 Setup"
        
        return {
            'total_users': total_users,
            'today_attendance': today_attendance,
            'recognition_accuracy': recognition_accuracy,
            'system_status': system_status
        }
    except Exception as e:
        return {
            'total_users': 0,
            'today_attendance': 0,
            'recognition_accuracy': "0%",
            'system_status': "🔴 Error"
        }

def show_dashboard():
    """Show main dashboard with real-time metrics"""
    st.header("📊 Dashboard Overview")
    
    # Initialize systems
    if not initialize_systems():
        return
    
    # Get metrics
    metrics = get_dashboard_metrics()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", metrics['total_users'], 
                 delta=f"{metrics['total_users']} registered")
    
    with col2:
        st.metric("Today's Attendance", metrics['today_attendance'], 
                 delta=f"{metrics['today_attendance']} present")
    
    with col3:
        st.metric("Recognition Accuracy", metrics['recognition_accuracy'], 
                 delta="85% target")
    
    with col4:
        st.metric("System Status", metrics['system_status'], 
                 delta="All systems operational")
    
    # Performance monitoring section
    st.subheader("🚀 Performance Monitoring")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # System performance chart
        if st.session_state.performance_metrics:
            df_perf = pd.DataFrame(st.session_state.performance_metrics)
            fig_perf = px.line(df_perf, x='timestamp', y='processing_time', 
                              title="Processing Time Over Time")
            st.plotly_chart(fig_perf, use_container_width=True)
        else:
            st.info("No performance data available yet. Run some tests to see metrics.")
    
    with col2:
        # System health indicators
        st.subheader("System Health")
        
        # Face database health
        db_health = "🟢 Healthy" if st.session_state.face_db else "🔴 Not Initialized"
        st.metric("Face Database", db_health)
        
        # Attendance system health
        att_health = "🟢 Healthy" if st.session_state.attendance_manager else "🔴 Not Initialized"
        st.metric("Attendance System", att_health)
        
        # Storage usage
        try:
            faces_dir = Path("data/faces")
            if faces_dir.exists():
                total_size = sum(f.stat().st_size for f in faces_dir.rglob('*') if f.is_file())
                size_mb = total_size / (1024 * 1024)
                st.metric("Storage Usage", f"{size_mb:.1f} MB")
            else:
                st.metric("Storage Usage", "0 MB")
        except:
            st.metric("Storage Usage", "Unknown")

