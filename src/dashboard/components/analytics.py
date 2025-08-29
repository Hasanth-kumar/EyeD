"""
Analytics Component - Day 12 Enhanced
Handles advanced charts, insights, and data visualization with enhanced features
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

def load_analytics_data():
    """Load data for analytics"""
    try:
        df = pd.read_csv("data/attendance.csv")
        df = df[~df['Name'].str.startswith('#', na=False)]
        
        if len(df) == 0:
            return None, "No attendance data available yet."
        
        # Convert date and time columns
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
        
        # Add derived columns
        df['Day_of_Week'] = df['Date'].dt.day_name()
        df['Hour'] = df['Time'].dt.hour
        df['Week_Number'] = df['Date'].dt.isocalendar().week
        df['Month'] = df['Date'].dt.month_name()
        df['Year'] = df['Date'].dt.year
        df['Quarter'] = df['Date'].dt.quarter
        
        # Add attendance percentage calculations
        df['Is_Present'] = (df['Status'] == 'Present').astype(int)
        df['Is_Late'] = (df['Status'] == 'Late').astype(int)
        df['Is_Absent'] = (df['Status'] == 'Absent').astype(int)
        
        return df, None
    except Exception as e:
        return None, f"Error loading data: {e}"

def show_analytics():
    """Show enhanced analytics and charts"""
    st.header("📈 Advanced Analytics & Insights - Day 12")
    
    # Load data
    df, error = load_analytics_data()
    if error:
        st.error(error)
        st.info("Start using the system to see analytics.")
        return
    
    # Create enhanced analytics tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Attendance Overview", 
        "⏰ Time Analysis", 
        "👥 User Performance", 
        "🔍 Quality Metrics",
        "🚀 Performance Insights"
    ])
    
    with tab1:
        show_enhanced_attendance_overview(df)
    
    with tab2:
        show_enhanced_time_analysis(df)
    
    with tab3:
        show_enhanced_user_performance(df)
    
    with tab4:
        show_enhanced_quality_metrics(df)
    
    with tab5:
        show_performance_insights(df)

def show_enhanced_attendance_overview(df):
    """Show enhanced attendance overview with percentage charts"""
    st.subheader("🎯 Enhanced Attendance Overview")
    
    # Key metrics at the top
    col1, col2, col3, col4 = st.columns(4)
    
    total_entries = len(df)
    present_count = len(df[df['Status'] == 'Present'])
    late_count = len(df[df['Status'] == 'Late'])
    absent_count = len(df[df['Status'] == 'Absent'])
    
    with col1:
        st.metric("Total Entries", total_entries)
    with col2:
        st.metric("Present", present_count, f"+{present_count}")
    with col3:
        st.metric("Late", late_count, f"-{late_count}")
    with col4:
        st.metric("Absent", absent_count, f"-{absent_count}")
    
    # Attendance percentage chart - Day 12 requirement
    st.subheader("📈 Attendance Percentage Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily attendance percentage
        daily_stats = df.groupby(df['Date'].dt.date).agg({
            'Is_Present': 'sum',
            'Is_Late': 'sum',
            'Is_Absent': 'sum'
        }).reset_index()
        
        daily_stats['Total'] = daily_stats['Is_Present'] + daily_stats['Is_Late'] + daily_stats['Is_Absent']
        daily_stats['Present_Percentage'] = (daily_stats['Is_Present'] / daily_stats['Total'] * 100).round(1)
        daily_stats['Late_Percentage'] = (daily_stats['Is_Late'] / daily_stats['Total'] * 100).round(1)
        daily_stats['Absent_Percentage'] = (daily_stats['Is_Absent'] / daily_stats['Total'] * 100).round(1)
        
        fig_daily_pct = go.Figure()
        fig_daily_pct.add_trace(go.Scatter(
            x=daily_stats['Date'], 
            y=daily_stats['Present_Percentage'],
            mode='lines+markers',
            name='Present %',
            line=dict(color='green', width=3)
        ))
        fig_daily_pct.add_trace(go.Scatter(
            x=daily_stats['Date'], 
            y=daily_stats['Late_Percentage'],
            mode='lines+markers',
            name='Late %',
            line=dict(color='orange', width=3)
        ))
        fig_daily_pct.update_layout(
            title="Daily Attendance Percentage Trends",
            xaxis_title="Date",
            yaxis_title="Percentage (%)",
            yaxis=dict(range=[0, 100]),
            hovermode='x unified'
        )
        st.plotly_chart(fig_daily_pct, use_container_width=True)
    
    with col2:
        # Overall attendance distribution with percentages
        status_counts = df['Status'].value_counts()
        total = len(df)
        percentages = [(count/total*100) for count in status_counts.values]
        
        fig_pct_dist = go.Figure(data=[go.Pie(
            labels=[f"{name} ({pct:.1f}%)" for name, pct in zip(status_counts.index, percentages)],
            values=status_counts.values,
            hole=0.4,
            marker_colors=['#2E8B57', '#FF8C00', '#DC143C']
        )])
        fig_pct_dist.update_layout(
            title="Overall Attendance Distribution (%)",
            showlegend=True
        )
        st.plotly_chart(fig_pct_dist, use_container_width=True)
    
    # Weekly trends with percentages
    st.subheader("📅 Weekly Attendance Trends")
    weekly_data = df.groupby(['Week_Number', 'Status']).size().reset_index(name='Count')
    weekly_pivot = weekly_data.pivot(index='Week_Number', columns='Status', values='Count').fillna(0)
    
    # Calculate weekly percentages
    weekly_pivot['Total'] = weekly_pivot.sum(axis=1)
    weekly_pivot['Present_Pct'] = (weekly_pivot['Present'] / weekly_pivot['Total'] * 100).round(1)
    weekly_pivot['Late_Pct'] = (weekly_pivot['Late'] / weekly_pivot['Total'] * 100).round(1)
    
    fig_weekly_pct = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Weekly Counts', 'Weekly Percentages'),
        vertical_spacing=0.1
    )
    
    # Counts subplot
    for status in ['Present', 'Late', 'Absent']:
        if status in weekly_pivot.columns:
            fig_weekly_pct.add_trace(
                go.Bar(x=weekly_pivot.index, y=weekly_pivot[status], name=f'{status} Count'),
                row=1, col=1
            )
    
    # Percentages subplot
    if 'Present_Pct' in weekly_pivot.columns:
        fig_weekly_pct.add_trace(
            go.Scatter(x=weekly_pivot.index, y=weekly_pivot['Present_Pct'], 
                      name='Present %', mode='lines+markers'),
            row=2, col=1
        )
    if 'Late_Pct' in weekly_pivot.columns:
        fig_weekly_pct.add_trace(
            go.Scatter(x=weekly_pivot.index, y=weekly_pivot['Late_Pct'], 
                      name='Late %', mode='lines+markers'),
            row=2, col=1
        )
    
    fig_weekly_pct.update_layout(height=600, title_text="Weekly Attendance Analysis")
    fig_weekly_pct.update_yaxes(title_text="Count", row=1, col=1)
    fig_weekly_pct.update_yaxes(title_text="Percentage (%)", row=2, col=1)
    fig_weekly_pct.update_xaxes(title_text="Week Number", row=2, col=1)
    
    st.plotly_chart(fig_weekly_pct, use_container_width=True)

def show_enhanced_time_analysis(df):
    """Show enhanced time-based analysis with late arrival focus"""
    st.subheader("⏰ Enhanced Time Analysis")
    
    # Late arrival analysis - Day 12 requirement
    st.subheader("🚨 Late Arrival Analysis")
    
    late_data = df[df['Status'] == 'Late'].copy()
    
    if len(late_data) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Late arrivals by hour with trend line
            late_hourly = late_data.groupby('Hour').size().reset_index(name='Count')
            late_hourly = late_hourly.sort_values('Hour')
            
            fig_late_hourly = px.bar(
                late_hourly, 
                x='Hour', 
                y='Count', 
                title="Late Arrivals by Hour",
                color='Count',
                color_continuous_scale='reds'
            )
            fig_late_hourly.update_layout(
                xaxis_title="Hour of Day",
                yaxis_title="Late Arrival Count"
            )
            st.plotly_chart(fig_late_hourly, use_container_width=True)
        
        with col2:
            # Late arrivals by user with percentages
            late_users = late_data.groupby('Name').size().reset_index(name='Late_Count')
            late_users = late_users.sort_values('Late_Count', ascending=False).head(10)
            
            # Calculate total attendance per user for percentage
            total_by_user = df.groupby('Name').size().reset_index(name='Total_Attendance')
            late_users = late_users.merge(total_by_user, on='Name')
            late_users['Late_Percentage'] = (late_users['Late_Count'] / late_users['Total_Attendance'] * 100).round(1)
            
            fig_late_users = px.bar(
                late_users, 
                x='Name', 
                y='Late_Percentage',
                title="Top 10 Users by Late Arrival Percentage",
                color='Late_Percentage',
                color_continuous_scale='reds',
                text='Late_Percentage'
            )
            fig_late_users.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_late_users.update_xaxes(tickangle=45)
            fig_late_users.update_layout(
                xaxis_title="User Name",
                yaxis_title="Late Arrival Percentage (%)"
            )
            st.plotly_chart(fig_late_users, use_container_width=True)
        
        # Late arrival patterns over time
        st.subheader("📊 Late Arrival Patterns Over Time")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Daily late arrival trends
            daily_late = late_data.groupby(df['Date'].dt.date).size().reset_index(name='Late_Count')
            daily_late.columns = ['Date', 'Late_Count']
            
            fig_daily_late = px.line(
                daily_late, 
                x='Date', 
                y='Late_Count',
                title="Daily Late Arrival Trends",
                markers=True
            )
            fig_daily_late.update_layout(
                xaxis_title="Date",
                yaxis_title="Late Arrival Count"
            )
            st.plotly_chart(fig_daily_late, use_container_width=True)
        
        with col2:
            # Day of week late arrival analysis
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_late = late_data.groupby('Day_of_Week').size().reset_index(name='Late_Count')
            day_late['Day_of_Week'] = pd.Categorical(day_late['Day_of_Week'], categories=day_order, ordered=True)
            day_late = day_late.sort_values('Day_of_Week')
            
            fig_day_late = px.bar(
                day_late, 
                x='Day_of_Week', 
                y='Late_Count',
                title="Late Arrivals by Day of Week",
                color='Late_Count',
                color_continuous_scale='reds'
            )
            fig_day_late.update_layout(
                xaxis_title="Day of Week",
                yaxis_title="Late Arrival Count"
            )
            st.plotly_chart(fig_day_late, use_container_width=True)
    
    else:
        st.info("🎉 No late arrivals recorded in the current dataset!")
    
    # Enhanced hourly distribution
    st.subheader("🕐 Enhanced Hourly Attendance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly distribution with status breakdown
        hourly_status = df.groupby(['Hour', 'Status']).size().reset_index(name='Count')
        hourly_pivot = hourly_status.pivot(index='Hour', columns='Status', values='Count').fillna(0)
        
        fig_hourly_status = px.bar(
            hourly_pivot,
            title="Hourly Attendance by Status",
            barmode='stack'
        )
        fig_hourly_status.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Attendance Count"
        )
        st.plotly_chart(fig_hourly_status, use_container_width=True)
    
    with col2:
        # Peak attendance hours
        hourly_total = df.groupby('Hour').size().reset_index(name='Total_Count')
        hourly_total = hourly_total.sort_values('Total_Count', ascending=False)
        
        fig_peak_hours = px.bar(
            hourly_total.head(8), 
            x='Hour', 
            y='Total_Count',
            title="Peak Attendance Hours (Top 8)",
            color='Total_Count',
            color_continuous_scale='viridis'
        )
        fig_peak_hours.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Total Attendance Count"
        )
        st.plotly_chart(fig_peak_hours, use_container_width=True)

def show_enhanced_user_performance(df):
    """Show enhanced user performance analysis"""
    st.subheader("👥 Enhanced User Performance Analysis")
    
    # User attendance summary with percentages
    st.subheader("📊 User Attendance Summary")
    
    user_summary = df.groupby('Name').agg({
        'Is_Present': 'sum',
        'Is_Late': 'sum',
        'Is_Absent': 'sum'
    }).reset_index()
    
    user_summary['Total_Attendance'] = user_summary['Is_Present'] + user_summary['Is_Late'] + user_summary['Is_Absent']
    user_summary['Present_Percentage'] = (user_summary['Is_Present'] / user_summary['Total_Attendance'] * 100).round(1)
    user_summary['Late_Percentage'] = (user_summary['Is_Late'] / user_summary['Total_Attendance'] * 100).round(1)
    user_summary['Absent_Percentage'] = (user_summary['Is_Absent'] / user_summary['Total_Attendance'] * 100).round(1)
    
    # Display user summary table
    st.dataframe(
        user_summary[['Name', 'Total_Attendance', 'Present_Percentage', 'Late_Percentage', 'Absent_Percentage']]
        .sort_values('Present_Percentage', ascending=False),
        use_container_width=True
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # User attendance counts with percentages
        fig_user_counts = px.bar(
            user_summary, 
            x='Name', 
            y='Total_Attendance',
            title="Total Attendance by User",
            color='Present_Percentage',
            color_continuous_scale='viridis',
            text='Total_Attendance'
        )
        fig_user_counts.update_traces(textposition='outside')
        fig_user_counts.update_xaxes(tickangle=45)
        fig_user_counts.update_layout(
            xaxis_title="User Name",
            yaxis_title="Total Attendance Count"
        )
        st.plotly_chart(fig_user_counts, use_container_width=True)
    
    with col2:
        # User performance radar chart
        top_users = user_summary.head(5)  # Top 5 users
        
        fig_radar = go.Figure()
        
        for _, user in top_users.iterrows():
            fig_radar.add_trace(go.Scatterpolar(
                r=[user['Present_Percentage'], user['Late_Percentage'], user['Absent_Percentage']],
                theta=['Present %', 'Late %', 'Absent %'],
                fill='toself',
                name=user['Name']
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Top 5 Users Performance Radar Chart"
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    
    # User confidence analysis
    if 'Confidence' in df.columns:
        st.subheader("🎯 User Confidence Analysis")
        
        user_confidence = df.groupby('Name')['Confidence'].agg(['mean', 'count', 'std']).reset_index()
        user_confidence.columns = ['Name', 'Avg_Confidence', 'Attendance_Count', 'Confidence_Std']
        user_confidence = user_confidence[user_confidence['Attendance_Count'] >= 3]  # Only users with 3+ entries
        
        if len(user_confidence) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # Confidence vs Attendance scatter
                fig_confidence = px.scatter(
                    user_confidence, 
                    x='Avg_Confidence', 
                    y='Attendance_Count', 
                    size='Avg_Confidence',
                    color='Confidence_Std',
                    hover_name='Name',
                    title="User Confidence vs Attendance Count",
                    color_continuous_scale='viridis'
                )
                fig_confidence.update_layout(
                    xaxis_title="Average Confidence",
                    yaxis_title="Attendance Count"
                )
                st.plotly_chart(fig_confidence, use_container_width=True)
            
            with col2:
                # Confidence distribution by user
                fig_conf_dist = px.box(
                    df[df['Name'].isin(user_confidence['Name'])], 
                    x='Name', 
                    y='Confidence',
                    title="Confidence Distribution by User"
                )
                fig_conf_dist.update_xaxes(tickangle=45)
                fig_conf_dist.update_layout(
                    xaxis_title="User Name",
                    yaxis_title="Confidence Score"
                )
                st.plotly_chart(fig_conf_dist, use_container_width=True)

def show_enhanced_quality_metrics(df):
    """Show enhanced quality metrics analysis"""
    st.subheader("🔍 Enhanced Quality Metrics Analysis")
    
    # Check which quality columns are available
    quality_columns = []
    if 'Face_Quality_Score' in df.columns:
        quality_columns.append('Face_Quality_Score')
    if 'Processing_Time_MS' in df.columns:
        quality_columns.append('Processing_Time_MS')
    if 'Confidence' in df.columns:
        quality_columns.append('Confidence')
    
    if not quality_columns:
        st.info("No quality metrics available in the current dataset.")
        return
    
    # Quality metrics overview
    st.subheader("📊 Quality Metrics Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'Face_Quality_Score' in df.columns:
            avg_quality = df['Face_Quality_Score'].mean()
            st.metric("Average Face Quality", f"{avg_quality:.2f}")
    
    with col2:
        if 'Processing_Time_MS' in df.columns:
            avg_time = df['Processing_Time_MS'].mean()
            st.metric("Average Processing Time", f"{avg_time:.1f} ms")
    
    with col3:
        if 'Confidence' in df.columns:
            avg_confidence = df['Confidence'].mean()
            st.metric("Average Confidence", f"{avg_confidence:.3f}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Face_Quality_Score' in df.columns:
            # Enhanced quality score distribution
            fig_quality = px.histogram(
                df, 
                x='Face_Quality_Score', 
                nbins=20,
                title="Face Quality Score Distribution",
                color_discrete_sequence=['lightblue'],
                marginal='box'
            )
            fig_quality.update_layout(
                xaxis_title="Quality Score",
                yaxis_title="Frequency"
            )
            st.plotly_chart(fig_quality, use_container_width=True)
    
    with col2:
        if 'Processing_Time_MS' in df.columns:
            # Enhanced processing time distribution
            fig_time = px.histogram(
                df, 
                x='Processing_Time_MS', 
                nbins=20,
                title="Processing Time Distribution",
                color_discrete_sequence=['lightgreen'],
                marginal='box'
            )
            fig_time.update_layout(
                xaxis_title="Processing Time (ms)",
                yaxis_title="Frequency"
            )
            st.plotly_chart(fig_time, use_container_width=True)
    
    # Quality trends over time
    if 'Face_Quality_Score' in df.columns:
        st.subheader("📈 Quality Trends Over Time")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Daily average quality with confidence interval
            daily_quality = df.groupby(df['Date'].dt.date)['Face_Quality_Score'].agg(['mean', 'std']).reset_index()
            daily_quality.columns = ['Date', 'Avg_Quality', 'Std_Quality']
            
            fig_quality_trend = go.Figure()
            fig_quality_trend.add_trace(go.Scatter(
                x=daily_quality['Date'], 
                y=daily_quality['Avg_Quality'],
                mode='lines+markers',
                name='Average Quality',
                line=dict(color='blue', width=3)
            ))
            
            # Add confidence interval
            fig_quality_trend.add_trace(go.Scatter(
                x=daily_quality['Date'],
                y=daily_quality['Avg_Quality'] + daily_quality['Std_Quality'],
                mode='lines',
                line=dict(width=0),
                showlegend=False
            ))
            fig_quality_trend.add_trace(go.Scatter(
                x=daily_quality['Date'],
                y=daily_quality['Avg_Quality'] - daily_quality['Std_Quality'],
                mode='lines',
                line=dict(width=0),
                fill='tonexty',
                fillcolor='rgba(0,0,255,0.2)',
                showlegend=False
            ))
            
            fig_quality_trend.update_layout(
                title="Daily Average Quality Score with Standard Deviation",
                xaxis_title="Date",
                yaxis_title="Average Quality Score"
            )
            st.plotly_chart(fig_quality_trend, use_container_width=True)
        
        with col2:
            # Quality by day of week
            day_quality = df.groupby('Day_of_Week')['Face_Quality_Score'].mean().reset_index()
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_quality['Day_of_Week'] = pd.Categorical(day_quality['Day_of_Week'], categories=day_order, ordered=True)
            day_quality = day_quality.sort_values('Day_of_Week')
            
            fig_day_quality = px.bar(
                day_quality, 
                x='Day_of_Week', 
                y='Face_Quality_Score',
                title="Average Quality Score by Day of Week",
                color='Face_Quality_Score',
                color_continuous_scale='viridis'
            )
            fig_day_quality.update_layout(
                xaxis_title="Day of Week",
                yaxis_title="Average Quality Score"
            )
            st.plotly_chart(fig_day_quality, use_container_width=True)
    
    # Quality vs Performance correlation
    if 'Face_Quality_Score' in df.columns and 'Confidence' in df.columns:
        st.subheader("🔗 Quality vs Confidence Correlation")
        
        # Remove rows with missing values
        quality_conf_df = df[['Face_Quality_Score', 'Confidence']].dropna()
        
        if len(quality_conf_df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # Scatter plot with trend line
                fig_correlation = px.scatter(
                    quality_conf_df, 
                    x='Face_Quality_Score', 
                    y='Confidence',
                    title="Face Quality vs Recognition Confidence",
                    trendline="ols",
                    color_discrete_sequence=['blue']
                )
                fig_correlation.update_layout(
                    xaxis_title="Face Quality Score",
                    yaxis_title="Recognition Confidence"
                )
                st.plotly_chart(fig_correlation, use_container_width=True)
            
            with col2:
                # Correlation heatmap
                correlation_matrix = quality_conf_df.corr()
                fig_heatmap = px.imshow(
                    correlation_matrix,
                    title="Quality Metrics Correlation Matrix",
                    color_continuous_scale='RdBu',
                    aspect='auto'
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Calculate and display correlation coefficient
            correlation = quality_conf_df['Face_Quality_Score'].corr(quality_conf_df['Confidence'])
            st.metric("Correlation Coefficient", f"{correlation:.3f}")
            
            # Interpretation
            if correlation > 0.7:
                st.success("Strong positive correlation: Higher quality images lead to higher confidence recognition.")
            elif correlation > 0.3:
                st.info("Moderate positive correlation: Quality has some impact on recognition confidence.")
            elif correlation > -0.3:
                st.warning("Weak correlation: Quality has minimal impact on recognition confidence.")
            else:
                st.error("Negative correlation: Higher quality images may lead to lower confidence.")

def show_performance_insights(df):
    """Show performance insights and trends - Day 12 enhancement"""
    st.subheader("🚀 Performance Insights & Trends")
    
    # System performance metrics
    st.subheader("⚡ System Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sessions = df['Session_ID'].nunique()
        st.metric("Total Sessions", total_sessions)
    
    with col2:
        if 'Processing_Time_MS' in df.columns:
            avg_processing = df['Processing_Time_MS'].mean()
            st.metric("Avg Processing Time", f"{avg_processing:.1f} ms")
    
    with col3:
        if 'Liveness_Verified' in df.columns:
            liveness_success = df['Liveness_Verified'].sum()
            liveness_total = len(df)
            liveness_rate = (liveness_success / liveness_total * 100) if liveness_total > 0 else 0
            st.metric("Liveness Success Rate", f"{liveness_rate:.1f}%")
    
    with col4:
        if 'Confidence' in df.columns:
            high_confidence = len(df[df['Confidence'] >= 0.8])
            confidence_rate = (high_confidence / len(df) * 100) if len(df) > 0 else 0
            st.metric("High Confidence Rate", f"{confidence_rate:.1f}%")
    
    # Performance trends
    st.subheader("📈 Performance Trends Over Time")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Processing_Time_MS' in df.columns:
            # Processing time trends
            daily_time = df.groupby(df['Date'].dt.date)['Processing_Time_MS'].agg(['mean', 'std']).reset_index()
            daily_time.columns = ['Date', 'Avg_Time', 'Std_Time']
            
            fig_time_trend = go.Figure()
            fig_time_trend.add_trace(go.Scatter(
                x=daily_time['Date'], 
                y=daily_time['Avg_Time'],
                mode='lines+markers',
                name='Average Processing Time',
                line=dict(color='green', width=3)
            ))
            
            # Add standard deviation bands
            fig_time_trend.add_trace(go.Scatter(
                x=daily_time['Date'],
                y=daily_time['Avg_Time'] + daily_time['Std_Time'],
                mode='lines',
                line=dict(width=0),
                showlegend=False
            ))
            fig_time_trend.add_trace(go.Scatter(
                x=daily_time['Date'],
                y=daily_time['Avg_Time'] - daily_time['Std_Time'],
                mode='lines',
                line=dict(width=0),
                fill='tonexty',
                fillcolor='rgba(0,255,0,0.2)',
                showlegend=False
            ))
            
            fig_time_trend.update_layout(
                title="Daily Processing Time Trends",
                xaxis_title="Date",
                yaxis_title="Processing Time (ms)"
            )
            st.plotly_chart(fig_time_trend, use_container_width=True)
    
    with col2:
        if 'Confidence' in df.columns:
            # Confidence trends
            daily_conf = df.groupby(df['Date'].dt.date)['Confidence'].agg(['mean', 'std']).reset_index()
            daily_conf.columns = ['Date', 'Avg_Confidence', 'Std_Confidence']
            
            fig_conf_trend = go.Figure()
            fig_conf_trend.add_trace(go.Scatter(
                x=daily_conf['Date'], 
                y=daily_conf['Avg_Confidence'],
                mode='lines+markers',
                name='Average Confidence',
                line=dict(color='blue', width=3)
            ))
            
            # Add standard deviation bands
            fig_conf_trend.add_trace(go.Scatter(
                x=daily_conf['Date'],
                y=daily_conf['Avg_Confidence'] + daily_conf['Std_Confidence'],
                mode='lines',
                line=dict(width=0),
                showlegend=False
            ))
            fig_conf_trend.add_trace(go.Scatter(
                x=daily_conf['Date'],
                y=daily_conf['Avg_Confidence'] - daily_conf['Std_Confidence'],
                mode='lines',
                line=dict(width=0),
                fill='tonexty',
                fillcolor='rgba(0,0,255,0.2)',
                showlegend=False
            ))
            
            fig_conf_trend.update_layout(
                title="Daily Confidence Trends",
                xaxis_title="Date",
                yaxis_title="Average Confidence"
            )
            st.plotly_chart(fig_conf_trend, use_container_width=True)
    
    # Monthly summary - Day 12 requirement
    st.subheader("📅 Monthly Performance Summary")
    
    if 'Month' in df.columns and 'Year' in df.columns:
        monthly_summary = df.groupby(['Year', 'Month']).agg({
            'Is_Present': 'sum',
            'Is_Late': 'sum',
            'Is_Absent': 'sum'
        }).reset_index()
        
        monthly_summary['Total'] = monthly_summary['Is_Present'] + monthly_summary['Is_Late'] + monthly_summary['Is_Absent']
        monthly_summary['Present_Percentage'] = (monthly_summary['Is_Present'] / monthly_summary['Total'] * 100).round(1)
        monthly_summary['Late_Percentage'] = (monthly_summary['Is_Late'] / monthly_summary['Total'] * 100).round(1)
        
        # Create monthly summary chart
        fig_monthly = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Monthly Attendance Counts', 'Monthly Attendance Percentages'),
            vertical_spacing=0.1
        )
        
        # Counts subplot
        fig_monthly.add_trace(
            go.Bar(x=monthly_summary['Month'], y=monthly_summary['Is_Present'], name='Present'),
            row=1, col=1
        )
        fig_monthly.add_trace(
            go.Bar(x=monthly_summary['Month'], y=monthly_summary['Is_Late'], name='Late'),
            row=1, col=1
        )
        
        # Percentages subplot
        fig_monthly.add_trace(
            go.Scatter(x=monthly_summary['Month'], y=monthly_summary['Present_Percentage'], 
                      name='Present %', mode='lines+markers'),
            row=2, col=1
        )
        fig_monthly.add_trace(
            go.Scatter(x=monthly_summary['Month'], y=monthly_summary['Late_Percentage'], 
                      name='Late %', mode='lines+markers'),
            row=2, col=1
        )
        
        fig_monthly.update_layout(height=600, title_text="Monthly Attendance Analysis")
        fig_monthly.update_yaxes(title_text="Count", row=1, col=1)
        fig_monthly.update_yaxes(title_text="Percentage (%)", row=2, col=1)
        fig_monthly.update_xaxes(title_text="Month", row=2, col=1)
        
        st.plotly_chart(fig_monthly, use_container_width=True)
        
        # Display monthly summary table
        st.subheader("📊 Monthly Summary Table")
        display_summary = monthly_summary[['Month', 'Total', 'Present_Percentage', 'Late_Percentage']].copy()
        display_summary = display_summary.sort_values('Total', ascending=False)
        st.dataframe(display_summary, use_container_width=True)
    
    # Performance recommendations
    st.subheader("💡 Performance Recommendations")
    
    if 'Processing_Time_MS' in df.columns:
        avg_time = df['Processing_Time_MS'].mean()
        if avg_time > 200:
            st.warning("⚠️ Average processing time is high. Consider optimizing face detection algorithms.")
        elif avg_time > 150:
            st.info("ℹ️ Processing time is moderate. Some optimization may be beneficial.")
        else:
            st.success("✅ Processing time is optimal. System is performing well.")
    
    if 'Face_Quality_Score' in df.columns:
        avg_quality = df['Face_Quality_Score'].mean()
        if avg_quality < 0.6:
            st.warning("⚠️ Average face quality is low. Consider improving lighting conditions or camera quality.")
        elif avg_quality < 0.7:
            st.info("ℹ️ Face quality is acceptable but could be improved.")
        else:
            st.success("✅ Face quality is excellent. System is capturing high-quality images.")
    
    if 'Confidence' in df.columns:
        avg_confidence = df['Confidence'].mean()
        if avg_confidence < 0.7:
            st.warning("⚠️ Average confidence is low. Consider retraining or improving recognition models.")
        elif avg_confidence < 0.8:
            st.info("ℹ️ Confidence is acceptable but could be improved.")
        else:
            st.success("✅ Confidence is high. Recognition system is performing well.")

