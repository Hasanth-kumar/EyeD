"""
Analytics Component - Phase 4.3 Implementation
Simple, focused analytics dashboard with attendance trends and user performance
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

def get_analytics_data() -> tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Get analytics data through the service layer
    
    Returns:
        Tuple of (analytics_data, error_message)
    """
    try:
        if 'attendance_service' not in st.session_state:
            return None, "Services not initialized. Please refresh the page."
        
        attendance_service = st.session_state.attendance_service
        
        # Get basic analytics data with error handling
        analytics_data = {}
        
        # Get summary data
        try:
            summary_data = attendance_service.get_attendance_analytics_by_type("summary")
            analytics_data['attendance_summary'] = summary_data if summary_data else {}
        except Exception as e:
            st.warning(f"Could not load summary data: {e}")
            analytics_data['attendance_summary'] = {}
        
        # Get user performance data
        try:
            user_perf_data = attendance_service.get_attendance_analytics_by_type("user_performance")
            analytics_data['user_performance'] = user_perf_data if user_perf_data else []
        except Exception as e:
            st.warning(f"Could not load user performance data: {e}")
            analytics_data['user_performance'] = []
        
        # Get trends data
        try:
            trends_data = attendance_service.get_attendance_analytics_by_type("trends")
            analytics_data['trends'] = trends_data if trends_data else []
        except Exception as e:
            st.warning(f"Could not load trends data: {e}")
            analytics_data['trends'] = []
        
        return analytics_data, None
        
    except Exception as e:
        return None, f"Error loading analytics data: {e}"

def show_analytics() -> None:
    """
    Show comprehensive analytics dashboard - Phase 4.3 Implementation
    """
    # Get analytics data through service layer
    analytics_data, error = get_analytics_data()
    if error:
        st.error(error)
        if "Services not initialized" in error:
            st.info("Please refresh the page to initialize services.")
        return
    
    # Content description
    st.markdown("Comprehensive attendance analysis and performance metrics")
    
    # Check if we have any data
    has_data = any([
        analytics_data.get('attendance_summary'),
        analytics_data.get('user_performance'),
        analytics_data.get('trends')
    ])
    
    if not has_data:
        st.info("📊 No attendance data available yet. Use the Daily Attendance page to log some attendance entries first.")
        st.markdown("""
        **To get started with analytics:**
        1. Go to the **Daily Attendance** page
        2. Log some attendance entries
        3. Return to this page to see your analytics
        """)
        return
    
    # 1. OVERVIEW METRICS
    show_overview_metrics(analytics_data)
    
    # 2. ATTENDANCE TRENDS
    show_attendance_trends(analytics_data)
    
    # 3. USER PERFORMANCE
    show_user_performance(analytics_data)
    
    # 4. EXPORT FUNCTIONALITY
    show_export_options(analytics_data)

def show_overview_metrics(analytics_data: Dict[str, Any]) -> None:
    """Display key overview metrics"""
    st.subheader("📈 Overview Metrics")
    
    summary = analytics_data.get('attendance_summary', {})
    
    if summary:
        # Create metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Attendance",
                value=summary.get('total_attendance', 0),
                delta=summary.get('attendance_change', 0)
            )
        
        with col2:
            st.metric(
                label="Unique Users",
                value=summary.get('unique_users', 0),
                delta=summary.get('user_change', 0)
            )
        
        with col3:
            avg_confidence = summary.get('avg_confidence', 0)
            st.metric(
                label="Average Confidence",
                value=f"{avg_confidence:.1%}",
                delta=f"{summary.get('confidence_change', 0):.1%}"
            )
        
        with col4:
            success_rate = summary.get('success_rate', 0)
            st.metric(
                label="Success Rate",
                value=f"{success_rate:.1f}%",
                delta=f"{summary.get('success_change', 0):.1f}%"
            )
    else:
        st.info("No summary data available")

def show_attendance_trends(analytics_data: Dict[str, Any]) -> None:
    """Display attendance trends and patterns"""
    st.subheader("📅 Attendance Trends")
    
    trends_data = analytics_data.get('trends', [])
    
    if trends_data:
        trends_df = pd.DataFrame(trends_data)
        
        if not trends_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Daily attendance trend
                daily_data = trends_df[trends_df['date'].notna()] if 'date' in trends_df.columns else pd.DataFrame()
                if not daily_data.empty and 'attendance_count' in daily_data.columns:
                    fig = px.line(
                        daily_data,
                        x='date',
                        y='attendance_count',
                        title="Daily Attendance Count",
                        labels={'date': 'Date', 'attendance_count': 'Attendance Count'}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No daily trend data available")
            
            with col2:
                # Hourly patterns
                hourly_data = trends_df[trends_df['hour'].notna()] if 'hour' in trends_df.columns else pd.DataFrame()
                if not hourly_data.empty and 'attendance_count' in hourly_data.columns:
                    fig = px.bar(
                        hourly_data,
                        x='hour',
                        y='attendance_count',
                        title="Hourly Attendance Distribution",
                        labels={'hour': 'Hour', 'attendance_count': 'Attendance Count'}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No hourly trend data available")
            
            # Late arrival analysis
            if 'late_arrivals' in trends_df.columns and not trends_df['late_arrivals'].isna().all():
                st.subheader("🕐 Late Arrival Analysis")
                late_data = trends_df[trends_df['late_arrivals'].notna()]
                if not late_data.empty:
                    fig = px.bar(
                        late_data,
                        x='date',
                        y='late_arrivals',
                        title="Late Arrivals by Date",
                        labels={'date': 'Date', 'late_arrivals': 'Late Arrivals'}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No trend data available")
    else:
        st.info("No trends data available")

def show_user_performance(analytics_data: Dict[str, Any]) -> None:
    """Display user performance analytics"""
    st.subheader("👥 User Performance")
    
    user_perf_data = analytics_data.get('user_performance', [])
    
    if user_perf_data:
        user_perf_df = pd.DataFrame(user_perf_data)
        
        if not user_perf_df.empty:
            # Check if required columns exist
            required_columns = ['user_name', 'attendance_count', 'avg_confidence']
            missing_columns = [col for col in required_columns if col not in user_perf_df.columns]
            
            if missing_columns:
                st.warning(f"⚠️ Some data columns are missing: {missing_columns}")
                st.write("Available columns:", list(user_perf_df.columns))
                
                # Show raw data if columns are missing
                st.write("**Raw User Performance Data:**")
                st.dataframe(user_perf_df, use_container_width=True)
                return
            
            # Calculate attendance rate (assuming 30 days period)
            total_days = 30
            user_perf_df['attendance_rate'] = (user_perf_df['attendance_count'] / total_days * 100).round(1)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top performers table
                st.write("🏆 **Top Performers**")
                top_performers = user_perf_df.nlargest(5, 'attendance_count')
                display_df = top_performers[['user_name', 'attendance_count', 'avg_confidence', 'attendance_rate']].copy()
                display_df['avg_confidence'] = display_df['avg_confidence'].apply(lambda x: f"{x:.1%}")
                display_df['attendance_rate'] = display_df['attendance_rate'].apply(lambda x: f"{x:.1f}%")
                st.dataframe(display_df, use_container_width=True)
            
            with col2:
                # Performance distribution
                st.write("📊 **Performance Distribution**")
                fig = px.histogram(
                    user_perf_df, 
                    x='attendance_count',
                    title="Attendance Count Distribution",
                    labels={'attendance_count': 'Attendance Count', 'count': 'Number of Users'}
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            # User comparison chart
            st.subheader("📊 User Comparison")
            fig = px.bar(
                user_perf_df,
                x='user_name',
                y='attendance_count',
                title="Attendance Count by User",
                labels={'user_name': 'User', 'attendance_count': 'Attendance Count'}
            )
            fig.update_layout(height=400)
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No user performance data available")
    else:
        st.info("No user performance data available")

def show_export_options(analytics_data: Dict[str, Any]) -> None:
    """Display export functionality"""
    st.subheader("📤 Export Analytics")
    
    # Export format selection
    export_format = st.selectbox(
        "Export Format",
        ["CSV", "JSON"]
    )
    
    # Export type selection
    export_type = st.selectbox(
        "Export Type",
        [
            "Complete Analytics Report",
            "Attendance Summary",
            "User Performance",
            "Trends Analysis"
        ]
    )
    
    # Export button
    if st.button("📊 Generate Export", key="export_analytics_btn"):
        export_result = generate_export(analytics_data, export_format, export_type)
        
        if export_result.get('success'):
            st.success("✅ Export generated successfully!")
            
            # Download button
            st.download_button(
                label=f"📥 Download {export_format}",
                data=export_result.get('data', ''),
                file_name=export_result.get('filename', 'analytics_export.csv'),
                mime=export_result.get('mime_type', 'text/csv')
            )
        else:
            st.error(f"Export failed: {export_result.get('error', 'Unknown error')}")

def generate_export(analytics_data: Dict[str, Any], 
                   format_type: str, 
                   export_type: str) -> Dict[str, Any]:
    """
    Generate export based on selected options
    
    Args:
        analytics_data: Dictionary containing analytics data
        format_type: Export format (CSV, JSON)
        export_type: Type of export to generate
        
    Returns:
        Dictionary with export result
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if export_type == "Complete Analytics Report":
            return generate_complete_report(analytics_data, format_type, timestamp)
        elif export_type == "Attendance Summary":
            return generate_attendance_summary(analytics_data, format_type, timestamp)
        elif export_type == "User Performance":
            return generate_user_performance(analytics_data, format_type, timestamp)
        elif export_type == "Trends Analysis":
            return generate_trends_analysis(analytics_data, format_type, timestamp)
        else:
            return {'success': False, 'error': f'Unknown export type: {export_type}'}
            
    except Exception as e:
        return {'success': False, 'error': f'Export generation failed: {str(e)}'}

def generate_complete_report(analytics_data: Dict[str, Any], 
                           format_type: str, 
                           timestamp: str) -> Dict[str, Any]:
    """Generate complete analytics report"""
    try:
        # Combine all analytics data
        report_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_type': 'Complete Analytics Report',
                'data_points': len(analytics_data)
            },
            'attendance_summary': analytics_data.get('attendance_summary', {}),
            'user_performance': analytics_data.get('user_performance', []),
            'trends': analytics_data.get('trends', [])
        }
        
        if format_type == "JSON":
            import json
            data = json.dumps(report_data, indent=2)
            return {
                'success': True,
                'data': data,
                'filename': f'complete_analytics_report_{timestamp}.json',
                'mime_type': 'application/json'
            }
        else:
            # For CSV, create a summary DataFrame
            summary_rows = []
            for key, value in report_data.items():
                if isinstance(value, dict):
                    summary_rows.append({'Category': key, 'Data': str(value)})
                elif isinstance(value, list):
                    summary_rows.append({'Category': key, 'Count': len(value)})
            
            df = pd.DataFrame(summary_rows)
            data = df.to_csv(index=False)
            return {
                'success': True,
                'data': data,
                'filename': f'complete_analytics_report_{timestamp}.csv',
                'mime_type': 'text/csv'
            }
        
    except Exception as e:
        return {'success': False, 'error': f'Complete report generation failed: {str(e)}'}

def generate_attendance_summary(analytics_data: Dict[str, Any], 
                              format_type: str, 
                              timestamp: str) -> Dict[str, Any]:
    """Generate attendance summary export"""
    try:
        if analytics_data.get('attendance_summary'):
            summary = analytics_data['attendance_summary']
            df = pd.DataFrame([summary])
            
            if format_type == "CSV":
                data = df.to_csv(index=False)
                return {
                    'success': True,
                    'data': data,
                    'filename': f'attendance_summary_{timestamp}.csv',
                    'mime_type': 'text/csv'
                }
        else:
            return {'success': False, 'error': 'No attendance summary data available'}
            
    except Exception as e:
        return {'success': False, 'error': f'Attendance summary export failed: {str(e)}'}

def generate_user_performance(analytics_data: Dict[str, Any], 
                            format_type: str, 
                            timestamp: str) -> Dict[str, Any]:
    """Generate user performance export"""
    try:
        if analytics_data.get('user_performance'):
            df = pd.DataFrame(analytics_data['user_performance'])
            
            if format_type == "CSV":
                data = df.to_csv(index=False)
                return {
                    'success': True,
                    'data': data,
                    'filename': f'user_performance_{timestamp}.csv',
                    'mime_type': 'text/csv'
                }
        else:
            return {'success': False, 'error': 'No user performance data available'}
            
    except Exception as e:
        return {'success': False, 'error': f'User performance export failed: {str(e)}'}

def generate_trends_analysis(analytics_data: Dict[str, Any], 
                           format_type: str, 
                           timestamp: str) -> Dict[str, Any]:
    """Generate trends analysis export"""
    try:
        if analytics_data.get('trends'):
            df = pd.DataFrame(analytics_data['trends'])
            
            if format_type == "CSV":
                data = df.to_csv(index=False)
                return {
                    'success': True,
                    'data': data,
                    'filename': f'trends_analysis_{timestamp}.csv',
                    'mime_type': 'text/csv'
                }
        else:
            return {'success': False, 'error': 'No trends data available'}
            
    except Exception as e:
        return {'success': False, 'error': f'Trends analysis export failed: {str(e)}'}

