"""
Dashboard Overview Component - Phase 4 Implementation
Provides comprehensive dashboard overview using service layer architecture
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

def get_overview_data():
    """Get overview data through the service layer"""
    try:
        if 'attendance_service' not in st.session_state:
            return None, "Services not initialized. Please refresh the page."
        
        attendance_service = st.session_state.attendance_service
        face_database = st.session_state.face_database
        
        # Get overview data through service
        overview_data = {
            'attendance_summary': attendance_service.get_attendance_report_by_type("overview"),
            'recent_activity': attendance_service.get_attendance_report_by_type("recent_activity"),
            'system_health': attendance_service.is_system_healthy(),
            'user_count': len(face_database.users_db) if face_database else 0
        }
        
        return overview_data, None
        
    except Exception as e:
        return None, f"Error loading overview data: {e}"

def show_dashboard():
    """Show comprehensive dashboard overview"""
    st.header("📊 Dashboard Overview - Phase 4")
    st.markdown("**Service Layer Architecture with Real-time Insights**")
    
    # Architecture info
    st.info("""
    🏗️ **New Architecture**: Dashboard overview now uses the service layer for all data access.
    - **Service Layer**: Orchestrates data retrieval and business logic
    - **Repository Layer**: Provides clean data access
    - **Real-time Updates**: Live data through service methods
    """)
    
    # Get overview data through service layer
    overview_data, error = get_overview_data()
    if error:
        st.error(error)
        if "Services not initialized" in error:
            st.info("Please refresh the page to initialize services.")
        return
    
    # Key metrics row
    st.subheader("🎯 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if overview_data.get('attendance_summary'):
            total_attendance = overview_data['attendance_summary'].get('total_attendance', 0)
            st.metric("Total Attendance", total_attendance)
    
    with col2:
        if overview_data.get('user_count'):
            st.metric("Registered Users", overview_data['user_count'])
    
    with col3:
        if overview_data.get('attendance_summary'):
            today_count = overview_data['attendance_summary'].get('today_attendance', 0)
            st.metric("Today's Attendance", today_count)
    
    with col4:
        if overview_data.get('system_health'):
            health_status = "🟢 Healthy" if overview_data['system_health'] else "🔴 Issues"
            st.metric("System Health", health_status)
    
    # System status
    st.subheader("🏥 System Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Service health status
        st.write("**Service Layer Status**")
        
        if overview_data.get('system_health'):
            st.success("✅ All services operational")
            
            # Service details
            services = [
                "Attendance Service",
                "Attendance Repository", 
                "Face Database",
                "Recognition System",
                "Liveness System"
            ]
            
            for service in services:
                st.write(f"🟢 {service}")
        else:
            st.error("❌ Some services have issues")
    
    with col2:
        # Performance metrics
        st.write("**Performance Metrics**")
        
        if overview_data.get('attendance_summary'):
            summary = overview_data['attendance_summary']
            
            # Calculate performance indicators
            avg_confidence = summary.get('avg_confidence', 0)
            success_rate = summary.get('success_rate', 0)
            
            st.metric("Avg Confidence", f"{avg_confidence:.2f}")
            st.metric("Success Rate", f"{success_rate:.1f}%")
            
            # Performance indicators
            if avg_confidence >= 0.8:
                st.success("✅ High recognition confidence")
            elif avg_confidence >= 0.6:
                st.warning("⚠️ Moderate confidence - consider improvements")
            else:
                st.error("❌ Low confidence - immediate attention needed")
    
    # Recent activity
    if overview_data.get('recent_activity'):
        st.subheader("📈 Recent Activity")
        
        recent_df = pd.DataFrame(overview_data['recent_activity'])
        
        if not recent_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Recent Attendance**")
                
                # Show recent entries
                if 'timestamp' in recent_df.columns and 'user_name' in recent_df.columns:
                    recent_df['timestamp'] = pd.to_datetime(recent_df['timestamp'])
                    recent_df = recent_df.sort_values('timestamp', ascending=False)
                    
                    for _, row in recent_df.head(5).iterrows():
                        time_str = row['timestamp'].strftime('%H:%M')
                        st.write(f"🕐 {time_str} - {row['user_name']}")
            
            with col2:
                st.write("**Activity Trends**")
                
                # Simple activity chart
                if 'timestamp' in recent_df.columns:
                    recent_df['hour'] = recent_df['timestamp'].dt.hour
                    hourly_activity = recent_df.groupby('hour').size().reset_index(name='count')
                    
                    if not hourly_activity.empty:
                        fig = px.bar(
                            hourly_activity,
                            x='hour',
                            y='count',
                            title="Hourly Activity (Today)"
                        )
                        st.plotly_chart(fig, use_container_width=True)
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    with col2:
        if st.button("📊 Export Report"):
            try:
                if 'attendance_service' in st.session_state:
                    attendance_service = st.session_state.attendance_service
                    
                    export_result = attendance_service.export_attendance_data(
                        export_type="overview_report",
                        format="csv"
                    )
                    
                    if export_result.get('success'):
                        st.success("✅ Report exported successfully!")
                        st.download_button(
                            label="📥 Download",
                            data=export_result.get('data', ''),
                            file_name=f"overview_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.error(f"Export failed: {export_result.get('error', 'Unknown error')}")
                else:
                    st.error("Services not available")
            except Exception as e:
                st.error(f"Export error: {e}")
    
    with col3:
        if st.button("🔍 System Check"):
            try:
                if 'attendance_service' in st.session_state:
                    attendance_service = st.session_state.attendance_service
                    
                    health_result = attendance_service.is_system_healthy()
                    
                    if health_result:
                        st.success("✅ System health check passed")
                    else:
                        st.error("❌ System health check failed")
                else:
                    st.error("Services not available")
            except Exception as e:
                st.error(f"Health check error: {e}")
    
    # Architecture benefits
    st.subheader("🏗️ Architecture Benefits")
    
    st.success("""
    **Phase 4 Achievements:**
    - ✅ **Service Layer**: All data access goes through services
    - ✅ **Repository Layer**: Clean data persistence
    - ✅ **Dependency Injection**: Components depend on interfaces
    - ✅ **Single Responsibility**: Each layer has one clear purpose
    - ✅ **Real-time Data**: Live updates through service methods
    - ✅ **Error Handling**: Centralized error handling in services
    """)
    
    # Next steps
    st.subheader("🚀 Next Steps")
    
    st.info("""
    **Ready for Phase 5:**
    - Comprehensive unit testing
    - Performance optimization
    - Advanced analytics
    - User experience improvements
    """)

