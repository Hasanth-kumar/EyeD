"""
Analytics Component - Enhanced Implementation
Comprehensive analytics dashboard with attendance trends, user performance, 
performance distribution, and user comparison features
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, date
from typing import Dict, Any, Optional, List
import numpy as np

def add_analytics_styling() -> None:
    """Add minimal CSS styling for clean analytics page design"""
    st.markdown("""
    <style>
    /* Analytics Page Styling - Clean Minimal Design */
    
    /* Better button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.4rem 0.8rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.2);
    }
    
    /* Data table styling - Subtle */
    .stDataFrame {
        border-radius: 6px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* Section dividers - Subtle */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        margin: 1.5rem 0;
        opacity: 0.6;
    }
    </style>
    """, unsafe_allow_html=True)

def get_analytics_data() -> tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Get analytics data through the service layer
    
    Returns:
        Tuple of (analytics_data, error_message)
    """
    try:
        # Check if services are initialized
        if 'services_initialized' not in st.session_state or not st.session_state.services_initialized:
            return None, "Services not initialized. Please refresh the page or navigate to another page first."
        
        if 'attendance_service' not in st.session_state:
            return None, "Attendance service not available. Please refresh the page."
        
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
    Show comprehensive analytics dashboard with enhanced features and improved design
    """
    # Get analytics data through service layer
    analytics_data, error = get_analytics_data()
    if error:
        st.error(error)
        if "Services not initialized" in error:
            st.info("Please refresh the page to initialize services.")
        return
    
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
    
    # Add custom CSS for improved styling
    add_analytics_styling()
    
    # Add date range filter
    show_date_range_filter()
    
    # Add section divider
    st.markdown("---")
    
    # 1. OVERVIEW METRICS
    show_overview_metrics(analytics_data)
    
    # Add section divider
    st.markdown("---")
    
    # 2. ATTENDANCE TRENDS
    show_attendance_trends(analytics_data)
    
    # Add section divider
    st.markdown("---")
    
    # 3. USER PERFORMANCE
    show_user_performance(analytics_data)
    
    # Add section divider
    st.markdown("---")
    
    # 4. PERFORMANCE DISTRIBUTION
    show_performance_distribution(analytics_data)
    
    # Add section divider
    st.markdown("---")
    
    # 5. USER COMPARISON
    show_user_comparison(analytics_data)
    
    # Add section divider
    st.markdown("---")
    
    # 6. EXPORT FUNCTIONALITY
    show_export_options(analytics_data)

def show_date_range_filter() -> None:
    """Display date range filter for analytics with clean design"""
    st.subheader("📅 Date Range Filter")
    
    # Create a more balanced layout
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    
    with col1:
        start_date = st.date_input(
            "📅 Start Date",
            value=date.today() - timedelta(days=30),
            help="Select the start date for analytics",
            key="analytics_start_date_input"
        )
    
    with col2:
        end_date = st.date_input(
            "📅 End Date",
            value=date.today(),
            help="Select the end date for analytics",
            key="analytics_end_date_input"
        )
    
    with col3:
        st.write("")  # Spacing
        if st.button("🔄 Apply Filter", key="apply_date_filter", help="Apply the selected date range"):
            st.session_state.analytics_start_date = start_date
            st.session_state.analytics_end_date = end_date
            st.success(f"✅ Filter applied: {start_date} to {end_date}")
    
    with col4:
        st.write("")  # Spacing
        if st.button("🔄 Reset", key="reset_date_filter", help="Reset to default date range"):
            st.session_state.analytics_start_date = date.today() - timedelta(days=30)
            st.session_state.analytics_end_date = date.today()
            st.success("✅ Filter reset to last 30 days")
    
    # Store in session state for use in other functions
    if 'analytics_start_date' not in st.session_state:
        st.session_state.analytics_start_date = start_date
    if 'analytics_end_date' not in st.session_state:
        st.session_state.analytics_end_date = end_date
    
    # Show current filter status
    current_start = st.session_state.get('analytics_start_date', start_date)
    current_end = st.session_state.get('analytics_end_date', end_date)
    
    st.info(f"📊 **Current Filter:** {current_start} to {current_end} ({(current_end - current_start).days + 1} days)")

def show_overview_metrics(analytics_data: Dict[str, Any]) -> None:
    """Display key overview metrics with clean design"""
    st.subheader("📈 Overview Metrics")
    
    summary = analytics_data.get('attendance_summary', {})
    
    if summary:
        # Create metrics in columns with better spacing
        col1, col2, col3, col4 = st.columns(4, gap="large")
        
        with col1:
            st.metric(
                label="📊 Total Attendance",
                value=summary.get('total_attendance', 0),
                delta=summary.get('attendance_change', 0),
                help="Total number of attendance entries recorded"
            )
        
        with col2:
            st.metric(
                label="👥 Unique Users",
                value=summary.get('unique_users', 0),
                delta=summary.get('user_change', 0),
                help="Number of unique users with attendance records"
            )
        
        with col3:
            avg_confidence = summary.get('avg_confidence', 0)
            st.metric(
                label="🎯 Average Confidence",
                value=f"{avg_confidence:.1%}",
                delta=f"{summary.get('confidence_change', 0):.1%}",
                help="Average confidence score across all recognition attempts"
            )
        
        with col4:
            success_rate = summary.get('success_rate', 0)
            st.metric(
                label="✅ Success Rate",
                value=f"{success_rate:.1f}%",
                delta=f"{summary.get('success_change', 0):.1f}%",
                help="Percentage of successful recognition attempts"
            )
        
        # Add additional insights row
        st.markdown("### 💡 Key Insights")
        
        col1, col2, col3 = st.columns(3, gap="large")
        
        with col1:
            if summary.get('total_attendance', 0) > 0:
                avg_per_user = summary.get('total_attendance', 0) / max(summary.get('unique_users', 1), 1)
                st.info(f"📈 **Average per User:** {avg_per_user:.1f} entries")
        
        with col2:
            if summary.get('avg_confidence', 0) > 0.8:
                st.success("🎯 **High Quality:** Recognition confidence is excellent")
            elif summary.get('avg_confidence', 0) > 0.6:
                st.warning("⚠️ **Moderate Quality:** Recognition confidence could be improved")
            else:
                st.error("❌ **Low Quality:** Recognition confidence needs attention")
        
        with col3:
            if summary.get('success_rate', 0) > 90:
                st.success("🏆 **Excellent Performance:** System is working very well")
            elif summary.get('success_rate', 0) > 75:
                st.info("👍 **Good Performance:** System is performing well")
            else:
                st.warning("🔧 **Needs Improvement:** System performance could be better")
    else:
        st.info("📊 No summary data available")

def show_attendance_trends(analytics_data: Dict[str, Any]) -> None:
    """Display attendance trends and patterns with clean design"""
    st.subheader("📈 Attendance Trends")
    
    trends_data = analytics_data.get('trends', [])
    
    if trends_data:
        trends_df = pd.DataFrame(trends_data)
        

        
        if not trends_df.empty:
            # Trend analysis options
            trend_options = st.multiselect(
                "Select Trend Views",
                ["Daily Trends", "Hourly Patterns", "Weekly Patterns", "Late Arrivals", "Attendance Quality"],
                default=["Daily Trends", "Hourly Patterns"]
            )
            
            # Daily attendance trend
            if "Daily Trends" in trend_options:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.write("### 📅 Daily Attendance Trends")
                daily_data = trends_df[trends_df['date'].notna()] if 'date' in trends_df.columns else pd.DataFrame()
                if not daily_data.empty and 'attendance_count' in daily_data.columns:
                    # Create subplot with secondary y-axis for late arrivals
                    fig = make_subplots(
                        rows=2, cols=1,
                        subplot_titles=("Daily Attendance Count", "Daily Late Arrivals"),
                        vertical_spacing=0.1
                    )
                    
                    # Daily attendance line with improved styling
                    fig.add_trace(
                        go.Scatter(
                            x=daily_data['date'],
                            y=daily_data['attendance_count'],
                            mode='lines+markers',
                            name='Attendance Count',
                            line=dict(color='#667eea', width=3),
                            marker=dict(size=8, color='#667eea', line=dict(width=2, color='white'))
                        ),
                        row=1, col=1
                    )
                    
                    # Late arrivals if available with improved styling
                    if 'late_arrivals' in daily_data.columns:
                        fig.add_trace(
                            go.Bar(
                                x=daily_data['date'],
                                y=daily_data['late_arrivals'],
                                name='Late Arrivals',
                                marker_color='#ff7f0e',
                                marker_line=dict(color='white', width=1)
                            ),
                            row=2, col=1
                        )
                    
                    # Improved layout styling
                    fig.update_layout(
                        height=600, 
                        showlegend=True,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=12),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    fig.update_xaxes(title_text="Date", row=2, col=1, gridcolor='rgba(128,128,128,0.2)')
                    fig.update_yaxes(title_text="Attendance Count", row=1, col=1, gridcolor='rgba(128,128,128,0.2)')
                    fig.update_yaxes(title_text="Late Arrivals", row=2, col=1, gridcolor='rgba(128,128,128,0.2)')
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Trend statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        avg_daily = daily_data['attendance_count'].mean()
                        st.metric("Average Daily Attendance", f"{avg_daily:.1f}")
                    with col2:
                        max_daily = daily_data['attendance_count'].max()
                        st.metric("Peak Daily Attendance", max_daily)
                    with col3:
                        trend_direction = "📈 Increasing" if daily_data['attendance_count'].iloc[-1] > daily_data['attendance_count'].iloc[0] else "📉 Decreasing"
                        st.metric("Trend Direction", trend_direction)
                else:
                    st.info("No daily trend data available")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Hourly patterns
            if "Hourly Patterns" in trend_options:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.write("### 🕐 Hourly Attendance Patterns")
                hourly_data = trends_df[trends_df['hour'].notna()] if 'hour' in trends_df.columns else pd.DataFrame()
                if not hourly_data.empty and 'attendance_count' in hourly_data.columns:
                    # Sort by hour for better visualization
                    hourly_data = hourly_data.sort_values('hour')
                    
                    fig = px.bar(
                        hourly_data,
                        x='hour',
                        y='attendance_count',
                        title="Hourly Attendance Distribution",
                        labels={'hour': 'Hour of Day', 'attendance_count': 'Attendance Count'},
                        color='attendance_count',
                        color_continuous_scale='Viridis'
                    )
                    
                    # Improved styling
                    fig.update_layout(
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=12),
                        title_font_size=16
                    )
                    fig.update_xaxes(tickmode='linear', dtick=1, gridcolor='rgba(128,128,128,0.2)')
                    fig.update_yaxes(gridcolor='rgba(128,128,128,0.2)')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Peak hours analysis
                    peak_hour = hourly_data.loc[hourly_data['attendance_count'].idxmax()]
                    st.info(f"🏆 Peak attendance hour: {int(peak_hour['hour'])}:00 with {peak_hour['attendance_count']} entries")
                else:
                    st.info("No hourly trend data available")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Weekly patterns
            if "Weekly Patterns" in trend_options:
                st.write("### 📊 Weekly Attendance Patterns")
                # This would require additional data processing to group by day of week
                st.info("Weekly pattern analysis requires additional data processing. Feature coming soon!")
            
            # Late arrivals analysis
            if "Late Arrivals" in trend_options:
                st.write("### ⏰ Late Arrival Analysis")
                if 'late_arrivals' in trends_df.columns and not trends_df['late_arrivals'].isna().all():
                    late_data = trends_df[trends_df['late_arrivals'].notna()]
                    if not late_data.empty:
                        fig = px.area(
                            late_data,
                            x='date',
                            y='late_arrivals',
                            title="Late Arrivals Trend Over Time",
                            labels={'date': 'Date', 'late_arrivals': 'Late Arrivals'}
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Late arrival statistics
                        col1, col2 = st.columns(2)
                        with col1:
                            avg_late = late_data['late_arrivals'].mean()
                            st.metric("Average Late Arrivals per Day", f"{avg_late:.1f}")
                        with col2:
                            max_late = late_data['late_arrivals'].max()
                            st.metric("Maximum Late Arrivals", max_late)
                else:
                    st.info("No late arrival data available")
            
            # Attendance quality trends
            if "Attendance Quality" in trend_options:
                st.write("### 🎯 Attendance Quality Trends")
                st.info("Quality trend analysis requires confidence and quality score data. Feature coming soon!")
        else:
            st.info("No trend data available")
    else:
        st.info("No trends data available")

def show_user_performance(analytics_data: Dict[str, Any]) -> None:
    """Display user performance analytics with clean design"""
    st.subheader("👥 User Performance")
    
    user_perf_data = analytics_data.get('user_performance', [])
    
    if user_perf_data:
        user_perf_df = pd.DataFrame(user_perf_data)
        

        
        if not user_perf_df.empty:
            # Check if required columns exist and handle missing data
            required_columns = ['user_name', 'attendance_count', 'avg_confidence']
            missing_columns = [col for col in required_columns if col not in user_perf_df.columns]
            
            if missing_columns:
                st.warning(f"⚠️ Some data columns are missing: {missing_columns}")
                st.write("Available columns:", list(user_perf_df.columns))
                
                # Show raw data if columns are missing
                st.write("**Raw User Performance Data:**")
                st.dataframe(user_perf_df, use_container_width=True)
                return
            
            # Filter out users with 'Unknown' name and handle data quality
            original_count = len(user_perf_df)
            user_perf_df = user_perf_df[user_perf_df['user_name'] != 'Unknown']
            filtered_count = len(user_perf_df)
            
            if original_count > filtered_count:
                st.info(f"Filtered out {original_count - filtered_count} entries with unknown user names")
            
            if user_perf_df.empty:
                st.info("No valid user performance data available after filtering")
                return
            
            # Calculate additional metrics
            total_days = 30  # Default period
            user_perf_df['attendance_rate'] = (user_perf_df['attendance_count'] / total_days * 100).round(1)
            user_perf_df['performance_category'] = user_perf_df['attendance_count'].apply(categorize_performance)
            user_perf_df['confidence_category'] = user_perf_df['avg_confidence'].apply(categorize_confidence)
            
            # Performance overview metrics
            st.write("### 📊 Performance Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_users = len(user_perf_df)
                st.metric("Total Users", total_users)
            
            with col2:
                avg_attendance = user_perf_df['attendance_count'].mean()
                st.metric("Average Attendance", f"{avg_attendance:.1f}")
            
            with col3:
                top_performer = user_perf_df.loc[user_perf_df['attendance_count'].idxmax(), 'user_name']
                st.metric("Top Performer", top_performer)
            
            with col4:
                avg_confidence = user_perf_df['avg_confidence'].mean()
                st.metric("Avg Confidence", f"{avg_confidence:.1%}")
            
            # Performance categories
            st.write("### 🏆 Performance Categories")
            performance_summary = user_perf_df['performance_category'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Performance category pie chart with improved styling
                fig = px.pie(
                    values=performance_summary.values,
                    names=performance_summary.index,
                    title="Performance Distribution by Category",
                    color_discrete_sequence=['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
                )
                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    title_font_size=16,
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.01
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Top performers table with improved styling
                st.write("**🏆 Top Performers**")
                top_performers = user_perf_df.nlargest(5, 'attendance_count')
                display_df = top_performers[['user_name', 'attendance_count', 'avg_confidence', 'attendance_rate', 'performance_category']].copy()
                display_df['avg_confidence'] = display_df['avg_confidence'].apply(lambda x: f"{x:.1%}")
                display_df['attendance_rate'] = display_df['attendance_rate'].apply(lambda x: f"{x:.1f}%")
                
                # Rename columns for better display
                display_df.columns = ['User Name', 'Attendance Count', 'Avg Confidence', 'Attendance Rate', 'Performance Category']
                
                st.dataframe(
                    display_df, 
                    use_container_width=True,
                    hide_index=True
                )
            
            # Detailed performance analysis
            st.write("### 📈 Detailed Performance Analysis")
            
            # Performance vs Confidence scatter plot with improved styling
            fig = px.scatter(
                user_perf_df,
                x='attendance_count',
                y='avg_confidence',
                color='performance_category',
                size='attendance_count',
                hover_data=['user_name', 'attendance_rate'],
                title="Performance vs Confidence Analysis",
                labels={
                    'attendance_count': 'Attendance Count',
                    'avg_confidence': 'Average Confidence',
                    'performance_category': 'Performance Category'
                },
                color_discrete_sequence=['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
            )
            fig.update_layout(
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                title_font_size=16,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            fig.update_xaxes(gridcolor='rgba(128,128,128,0.2)')
            fig.update_yaxes(gridcolor='rgba(128,128,128,0.2)')
            st.plotly_chart(fig, use_container_width=True)
            
            # Performance insights
            st.write("### 💡 Performance Insights")
            
            # Calculate insights
            high_performers = user_perf_df[user_perf_df['performance_category'] == 'Excellent']
            low_performers = user_perf_df[user_perf_df['performance_category'] == 'Needs Improvement']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🎯 High Performers Analysis**")
                if not high_performers.empty:
                    st.write(f"• {len(high_performers)} users are performing excellently")
                    st.write(f"• Average confidence: {high_performers['avg_confidence'].mean():.1%}")
                    st.write(f"• Average attendance: {high_performers['attendance_count'].mean():.1f}")
                else:
                    st.write("No high performers identified")
            
            with col2:
                st.write("**⚠️ Areas for Improvement**")
                if not low_performers.empty:
                    st.write(f"• {len(low_performers)} users need improvement")
                    st.write(f"• Average confidence: {low_performers['avg_confidence'].mean():.1%}")
                    st.write(f"• Average attendance: {low_performers['attendance_count'].mean():.1f}")
                else:
                    st.write("All users are performing well!")
        else:
            st.info("No user performance data available")
    else:
        st.info("No user performance data available")

def categorize_performance(attendance_count: int) -> str:
    """Categorize user performance based on attendance count"""
    if attendance_count >= 25:
        return "Excellent"
    elif attendance_count >= 20:
        return "Good"
    elif attendance_count >= 15:
        return "Average"
    elif attendance_count >= 10:
        return "Below Average"
    else:
        return "Needs Improvement"

def categorize_confidence(confidence: float) -> str:
    """Categorize confidence level"""
    if confidence >= 0.9:
        return "Very High"
    elif confidence >= 0.8:
        return "High"
    elif confidence >= 0.7:
        return "Medium"
    elif confidence >= 0.6:
        return "Low"
    else:
        return "Very Low"

def show_performance_distribution(analytics_data: Dict[str, Any]) -> None:
    """Display performance distribution analysis focusing on attendance count distribution with clean design"""
    st.subheader("📊 Performance Distribution Analysis")
    
    user_perf_data = analytics_data.get('user_performance', [])
    
    if user_perf_data:
        user_perf_df = pd.DataFrame(user_perf_data)
        
        if not user_perf_df.empty and 'attendance_count' in user_perf_df.columns:
            # Attendance count distribution
            st.write("### 📈 Attendance Count Distribution")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Histogram with distribution curve and improved styling
                fig = px.histogram(
                    user_perf_df,
                    x='attendance_count',
                    nbins=10,
                    title="Attendance Count Distribution",
                    labels={'attendance_count': 'Attendance Count', 'count': 'Number of Users'},
                    color_discrete_sequence=['#667eea']
                )
                
                # Add distribution curve
                x_range = np.linspace(user_perf_df['attendance_count'].min(), user_perf_df['attendance_count'].max(), 100)
                mean_att = user_perf_df['attendance_count'].mean()
                std_att = user_perf_df['attendance_count'].std()
                y_curve = len(user_perf_df) * (1/(std_att * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_range - mean_att) / std_att) ** 2)
                
                fig.add_trace(go.Scatter(
                    x=x_range,
                    y=y_curve,
                    mode='lines',
                    name='Normal Distribution',
                    line=dict(color='#f5576c', width=3)
                ))
                
                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    title_font_size=16
                )
                fig.update_xaxes(gridcolor='rgba(128,128,128,0.2)')
                fig.update_yaxes(gridcolor='rgba(128,128,128,0.2)')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Box plot for distribution analysis with improved styling
                fig = px.box(
                    user_perf_df,
                    y='attendance_count',
                    title="Attendance Count Box Plot",
                    labels={'attendance_count': 'Attendance Count'},
                    color_discrete_sequence=['#667eea']
                )
                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    title_font_size=16
                )
                fig.update_xaxes(gridcolor='rgba(128,128,128,0.2)')
                fig.update_yaxes(gridcolor='rgba(128,128,128,0.2)')
                st.plotly_chart(fig, use_container_width=True)
            
            # Distribution statistics
            st.write("### 📊 Distribution Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                mean_att = user_perf_df['attendance_count'].mean()
                st.metric("Mean", f"{mean_att:.1f}")
            
            with col2:
                median_att = user_perf_df['attendance_count'].median()
                st.metric("Median", f"{median_att:.1f}")
            
            with col3:
                std_att = user_perf_df['attendance_count'].std()
                st.metric("Standard Deviation", f"{std_att:.1f}")
            
            with col4:
                range_att = user_perf_df['attendance_count'].max() - user_perf_df['attendance_count'].min()
                st.metric("Range", f"{range_att:.1f}")
            
            # Percentile analysis
            st.write("### 📈 Percentile Analysis")
            
            percentiles = [25, 50, 75, 90, 95, 99]
            percentile_values = [np.percentile(user_perf_df['attendance_count'], p) for p in percentiles]
            
            percentile_df = pd.DataFrame({
                'Percentile': [f'{p}th' for p in percentiles],
                'Attendance Count': percentile_values
            })
            
            fig = px.bar(
                percentile_df,
                x='Percentile',
                y='Attendance Count',
                title="Attendance Count Percentiles",
                color='Attendance Count',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                title_font_size=16
            )
            fig.update_xaxes(gridcolor='rgba(128,128,128,0.2)')
            fig.update_yaxes(gridcolor='rgba(128,128,128,0.2)')
            st.plotly_chart(fig, use_container_width=True)
            
            # Distribution insights
            st.write("### 💡 Distribution Insights")
            
            # Calculate insights
            q1 = np.percentile(user_perf_df['attendance_count'], 25)
            q3 = np.percentile(user_perf_df['attendance_count'], 75)
            iqr = q3 - q1
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**📊 Distribution Characteristics**")
                st.write(f"• **Skewness**: {'Right-skewed' if mean_att > median_att else 'Left-skewed' if mean_att < median_att else 'Symmetric'}")
                st.write(f"• **IQR**: {iqr:.1f} (Q3-Q1)")
                st.write(f"• **Coefficient of Variation**: {(std_att/mean_att)*100:.1f}%")
                
                # Outlier detection
                outliers = user_perf_df[
                    (user_perf_df['attendance_count'] < q1 - 1.5 * iqr) |
                    (user_perf_df['attendance_count'] > q3 + 1.5 * iqr)
                ]
                st.write(f"• **Outliers**: {len(outliers)} users")
            
            with col2:
                st.write("**🎯 Performance Segments**")
                excellent = len(user_perf_df[user_perf_df['attendance_count'] >= 25])
                good = len(user_perf_df[(user_perf_df['attendance_count'] >= 20) & (user_perf_df['attendance_count'] < 25)])
                average = len(user_perf_df[(user_perf_df['attendance_count'] >= 15) & (user_perf_df['attendance_count'] < 20)])
                below_avg = len(user_perf_df[(user_perf_df['attendance_count'] >= 10) & (user_perf_df['attendance_count'] < 15)])
                poor = len(user_perf_df[user_perf_df['attendance_count'] < 10])
                
                st.write(f"• **Excellent** (≥25): {excellent} users")
                st.write(f"• **Good** (20-24): {good} users")
                st.write(f"• **Average** (15-19): {average} users")
                st.write(f"• **Below Average** (10-14): {below_avg} users")
                st.write(f"• **Poor** (<10): {poor} users")
        else:
            st.info("No attendance count data available for distribution analysis")
    else:
        st.info("No user performance data available")

def show_user_comparison(analytics_data: Dict[str, Any]) -> None:
    """Display user comparison analysis with side-by-side comparisons and clean design"""
    st.subheader("👥 User Comparison Analysis")
    
    user_perf_data = analytics_data.get('user_performance', [])
    
    if user_perf_data:
        user_perf_df = pd.DataFrame(user_perf_data)
        
        if not user_perf_df.empty and 'user_name' in user_perf_df.columns:
            # User selection for comparison
            st.write("### 🔍 Select Users for Comparison")
            
            # Get all user names
            all_users = user_perf_df['user_name'].tolist()
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_users = st.multiselect(
                    "Select users to compare (2-4 users recommended)",
                    all_users,
                    default=all_users[:2] if len(all_users) >= 2 else all_users,
                    help="Select 2-4 users for detailed comparison"
                )
            
            with col2:
                comparison_metric = st.selectbox(
                    "Comparison Metric",
                    ["attendance_count", "avg_confidence", "attendance_rate"],
                    format_func=lambda x: {
                        "attendance_count": "Attendance Count",
                        "avg_confidence": "Average Confidence",
                        "attendance_rate": "Attendance Rate"
                    }[x]
                )
            
            if len(selected_users) >= 2:
                # Filter data for selected users
                comparison_df = user_perf_df[user_perf_df['user_name'].isin(selected_users)].copy()
                
                if not comparison_df.empty:
                    # Side-by-side comparison
                    st.write("### 📊 Side-by-Side Comparison")
                    
                    # Create comparison table
                    comparison_metrics = ['user_name', 'attendance_count', 'avg_confidence', 'attendance_rate']
                    available_metrics = [col for col in comparison_metrics if col in comparison_df.columns]
                    
                    display_df = comparison_df[available_metrics].copy()
                    
                    # Format the display
                    if 'avg_confidence' in display_df.columns:
                        display_df['avg_confidence'] = display_df['avg_confidence'].apply(lambda x: f"{x:.1%}")
                    if 'attendance_rate' in display_df.columns:
                        display_df['attendance_rate'] = display_df['attendance_rate'].apply(lambda x: f"{x:.1f}%")
                    
                    st.dataframe(display_df, use_container_width=True)
                    
                    # Visual comparison
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Bar chart comparison with improved styling
                        fig = px.bar(
                            comparison_df,
                            x='user_name',
                            y=comparison_metric,
                            title=f"{comparison_metric.replace('_', ' ').title()} Comparison",
                            color=comparison_metric,
                            color_continuous_scale='Viridis'
                        )
                        fig.update_layout(
                            height=400,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(size=12),
                            title_font_size=16
                        )
                        fig.update_xaxes(tickangle=45, gridcolor='rgba(128,128,128,0.2)')
                        fig.update_yaxes(gridcolor='rgba(128,128,128,0.2)')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Radar chart for multi-metric comparison
                        if len(comparison_df) <= 4:  # Radar chart works best with few users
                            # Normalize metrics for radar chart
                            radar_data = comparison_df[['user_name', 'attendance_count', 'avg_confidence']].copy()
                            
                            # Normalize to 0-1 scale
                            radar_data['attendance_count_norm'] = (radar_data['attendance_count'] - radar_data['attendance_count'].min()) / (radar_data['attendance_count'].max() - radar_data['attendance_count'].min())
                            radar_data['avg_confidence_norm'] = radar_data['avg_confidence']  # Already 0-1
                            
                            fig = go.Figure()
                            
                            colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c']
                            for i, (_, user) in enumerate(radar_data.iterrows()):
                                fig.add_trace(go.Scatterpolar(
                                    r=[user['attendance_count_norm'], user['avg_confidence_norm']],
                                    theta=['Attendance Count', 'Confidence'],
                                    fill='toself',
                                    name=user['user_name'],
                                    line_color=colors[i % len(colors)]
                                ))
                            
                            fig.update_layout(
                                polar=dict(
                                    radialaxis=dict(
                                        visible=True,
                                        range=[0, 1],
                                        gridcolor='rgba(128,128,128,0.2)'
                                    )),
                                showlegend=True,
                                title="Multi-Metric Comparison (Normalized)",
                                height=400,
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(size=12),
                                title_font_size=16
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            # Scatter plot for many users with improved styling
                            fig = px.scatter(
                                comparison_df,
                                x='attendance_count',
                                y='avg_confidence',
                                color='user_name',
                                size='attendance_count',
                                title="Performance Scatter Plot",
                                labels={
                                    'attendance_count': 'Attendance Count',
                                    'avg_confidence': 'Average Confidence'
                                },
                                color_discrete_sequence=['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
                            )
                            fig.update_layout(
                                height=400,
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(size=12),
                                title_font_size=16
                            )
                            fig.update_xaxes(gridcolor='rgba(128,128,128,0.2)')
                            fig.update_yaxes(gridcolor='rgba(128,128,128,0.2)')
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # Detailed comparison insights
                    st.write("### 💡 Comparison Insights")
                    
                    # Calculate insights
                    best_user = comparison_df.loc[comparison_df[comparison_metric].idxmax()]
                    worst_user = comparison_df.loc[comparison_df[comparison_metric].idxmin()]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**🏆 Best Performer**")
                        st.write(f"• **User**: {best_user['user_name']}")
                        st.write(f"• **{comparison_metric.replace('_', ' ').title()}**: {best_user[comparison_metric]:.2f}")
                        if 'avg_confidence' in best_user:
                            st.write(f"• **Confidence**: {best_user['avg_confidence']:.1%}")
                    
                    with col2:
                        st.write("**📈 Improvement Opportunity**")
                        st.write(f"• **User**: {worst_user['user_name']}")
                        st.write(f"• **{comparison_metric.replace('_', ' ').title()}**: {worst_user[comparison_metric]:.2f}")
                        if 'avg_confidence' in worst_user:
                            st.write(f"• **Confidence**: {worst_user['avg_confidence']:.1%}")
                    
                    # Performance gap analysis
                    if len(comparison_df) >= 2:
                        st.write("### 📊 Performance Gap Analysis")
                        
                        metric_values = comparison_df[comparison_metric].values
                        max_val = metric_values.max()
                        min_val = metric_values.min()
                        gap = max_val - min_val
                        gap_percentage = (gap / max_val) * 100 if max_val > 0 else 0
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Performance Gap", f"{gap:.2f}")
                        
                        with col2:
                            st.metric("Gap Percentage", f"{gap_percentage:.1f}%")
                        
                        with col3:
                            st.metric("Average Performance", f"{metric_values.mean():.2f}")
                else:
                    st.warning("No data available for selected users")
            else:
                st.info("Please select at least 2 users for comparison")
        else:
            st.info("No user data available for comparison")
    else:
        st.info("No user performance data available")

def show_export_options(analytics_data: Dict[str, Any]) -> None:
    """Display export functionality with clean design"""
    st.subheader("📤 Export Analytics")
    
    # Export options in a better layout
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        export_format = st.selectbox(
            "📄 Export Format",
            ["CSV", "JSON"],
            help="Choose the file format for your export"
        )
    
    with col2:
        export_type = st.selectbox(
            "📊 Export Type",
            [
                "Complete Analytics Report",
                "Attendance Summary",
                "User Performance",
                "Trends Analysis"
            ],
            help="Choose what data to include in the export"
        )
    
    # Export button with better styling
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("📊 Generate Export", key="export_analytics_btn", help="Generate and download the selected export"):
            export_result = generate_export(analytics_data, export_format, export_type)
            
            if export_result.get('success'):
                st.success("✅ Export generated successfully!")
                
                # Download button
                st.download_button(
                    label=f"📥 Download {export_format}",
                    data=export_result.get('data', ''),
                    file_name=export_result.get('filename', 'analytics_export.csv'),
                    mime=export_result.get('mime_type', 'text/csv'),
                    help=f"Download your {export_type.lower()} in {export_format} format"
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

