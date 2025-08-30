"""
Analytics Component - Phase 4 Implementation
Provides comprehensive analytics and insights using service layer architecture
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

def get_analytics_data():
    """Get analytics data through the service layer"""
    try:
        if 'attendance_service' not in st.session_state:
            return None, "Services not initialized. Please refresh the page."
        
        attendance_service = st.session_state.attendance_service
        
        # Get various analytics reports through service
        analytics_data = {
            'attendance_summary': attendance_service.get_attendance_analytics_by_type("summary"),
            'user_performance': attendance_service.get_attendance_analytics_by_type("user_performance"),
            'trends': attendance_service.get_attendance_analytics_by_type("trends")
        }
        
        return analytics_data, None
        
    except Exception as e:
        return None, f"Error loading analytics data: {e}"

def show_analytics():
    """Show comprehensive analytics dashboard"""
    st.header("📈 Analytics & Insights - Phase 4")
    st.markdown("**Service Layer Architecture with Advanced Analytics**")
    
    # Architecture info
    st.info("""
    🏗️ **New Architecture**: Analytics now use the service layer for data access and business logic.
    - **Service Layer**: Orchestrates analytics calculations
    - **Repository Layer**: Provides clean data access
    - **Business Logic**: Centralized in services, not scattered in UI components
    """)
    
    # Get analytics data through service layer
    analytics_data, error = get_analytics_data()
    if error:
        st.error(error)
        if "Services not initialized" in error:
            st.info("Please refresh the page to initialize services.")
        return
    
    # Display analytics overview
    st.subheader("📊 Analytics Overview")
    
    # Summary metrics
    if analytics_data.get('attendance_summary'):
        summary = analytics_data['attendance_summary']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Attendance", summary.get('total_attendance', 0))
        
        with col2:
            st.metric("Unique Users", summary.get('unique_users', 0))
        
        with col3:
            st.metric("Average Confidence", f"{summary.get('avg_confidence', 0):.2f}")
        
        with col4:
            st.metric("Success Rate", f"{summary.get('success_rate', 0):.1f}%")
    
    # User performance analytics
    if analytics_data.get('user_performance'):
        st.subheader("👥 User Performance Analytics")
        
        user_perf_df = pd.DataFrame(analytics_data['user_performance'])
        
        if not user_perf_df.empty:
            # Top performers
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("🏆 Top Performers")
                top_performers = user_perf_df.nlargest(5, 'attendance_count')
                st.dataframe(top_performers[['user_name', 'attendance_count', 'avg_confidence']])
            
            with col2:
                st.write("📈 Performance Distribution")
                fig = px.histogram(
                    user_perf_df, 
                    x='attendance_count',
                    title="Attendance Count Distribution",
                    labels={'attendance_count': 'Attendance Count', 'count': 'Number of Users'}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Trends analytics
    if analytics_data.get('trends'):
        st.subheader("📈 Attendance Trends")
        
        trends_df = pd.DataFrame(analytics_data['trends'])
        
        if not trends_df.empty:
            # Time series trends
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("📅 Daily Trends")
                if 'date' in trends_df.columns and 'attendance_count' in trends_df.columns:
                    fig = px.line(
                        trends_df,
                        x='date',
                        y='attendance_count',
                        title="Daily Attendance Trends"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.write("🕐 Hourly Patterns")
                if 'hour' in trends_df.columns and 'attendance_count' in trends_df.columns:
                    fig = px.bar(
                        trends_df,
                        x='hour',
                        y='attendance_count',
                        title="Hourly Attendance Patterns"
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    # Export functionality
    st.subheader("📤 Export Analytics")
    
    if st.button("📊 Export Analytics Report"):
        try:
            # Use service layer to export data
            if 'attendance_service' in st.session_state:
                attendance_service = st.session_state.attendance_service
                
                # Export analytics data
                export_result = attendance_service.export_attendance_data(
                    export_type="analytics_report",
                    format="csv"
                )
                
                if export_result.get('success'):
                    st.success("✅ Analytics report exported successfully!")
                    st.download_button(
                        label="📥 Download Report",
                        data=export_result.get('data', ''),
                        file_name=f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.error(f"Export failed: {export_result.get('error', 'Unknown error')}")
            else:
                st.error("Services not available for export")
        except Exception as e:
            st.error(f"Export error: {e}")
    
    # Architecture benefits
    st.subheader("🏗️ Architecture Benefits")
    
    st.success("""
    **Phase 4 Achievements:**
    - ✅ **Service Layer**: Business logic centralized in services
    - ✅ **Repository Layer**: Clean data access through repositories
    - ✅ **Dependency Injection**: Components depend on interfaces, not implementations
    - ✅ **Single Responsibility**: Each layer has one clear purpose
    - ✅ **Testability**: Services can be easily mocked for testing
    - ✅ **Maintainability**: Changes isolated to specific layers
    """)

