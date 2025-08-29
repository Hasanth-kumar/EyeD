"""
Day 14 Demo: Gamification Features and User Engagement
EyeD AI Attendance System

This demo showcases:
- Badge system with emoji badges (🏆 100% attendance, 🌙 Late comer)
- Timeline chart showing arrival times per user
- Achievement tracking and leaderboards
- User engagement features
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import os

def create_sample_gamification_data():
    """Create sample data for gamification demo"""
    
    # Sample users
    users = ["Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Eva Brown"]
    
    # Generate sample attendance data over 30 days
    start_date = datetime.now() - timedelta(days=30)
    dates = [start_date + timedelta(days=i) for i in range(30)]
    
    data = []
    
    for user in users:
        for date in dates:
            # Skip weekends
            if date.weekday() >= 5:
                continue
                
            # Generate realistic attendance patterns
            if user == "Alice Johnson":  # Perfect attendance
                status = "Present"
                hour = 8 + np.random.randint(0, 2)  # 8-9 AM
                confidence = 0.9 + np.random.random() * 0.1
            elif user == "Bob Smith":  # Good attendance, sometimes late
                if np.random.random() < 0.85:
                    status = "Present"
                    hour = 8 + np.random.randint(0, 3)  # 8-11 AM
                else:
                    status = "Late"
                    hour = 9 + np.random.randint(0, 2)  # 9-11 AM
                confidence = 0.8 + np.random.random() * 0.15
            elif user == "Carol Davis":  # Consistent but sometimes absent
                if np.random.random() < 0.8:
                    status = "Present"
                    hour = 8 + np.random.randint(0, 2)
                else:
                    status = "Absent"
                    hour = 0
                confidence = 0.85 + np.random.random() * 0.1
            elif user == "David Wilson":  # Late comer
                if np.random.random() < 0.7:
                    status = "Late"
                    hour = 9 + np.random.randint(0, 3)
                else:
                    status = "Present"
                    hour = 8 + np.random.randint(0, 2)
                confidence = 0.75 + np.random.random() * 0.2
            else:  # Eva Brown - Inconsistent
                if np.random.random() < 0.6:
                    status = "Present"
                    hour = 8 + np.random.randint(0, 4)
                elif np.random.random() < 0.8:
                    status = "Late"
                    hour = 9 + np.random.randint(0, 3)
                else:
                    status = "Absent"
                    hour = 0
                confidence = 0.7 + np.random.random() * 0.25
            
            if status != "Absent":
                time_str = f"{hour:02d}:{np.random.randint(0, 60):02d}:00"
                data.append({
                    'Date': date.strftime('%Y-%m-%d'),
                    'Time': time_str,
                    'Name': user,
                    'Status': status,
                    'Confidence': round(confidence, 3),
                    'Quality_Score': round(0.7 + np.random.random() * 0.3, 3),
                    'Session_ID': f"session_{len(data):06d}",
                    'Liveness_Verified': np.random.choice([True, False], p=[0.95, 0.05])
                })
    
    return pd.DataFrame(data)

def calculate_user_achievements(df):
    """Calculate achievements and badges for each user"""
    if df is None or len(df) == 0:
        return {}
    
    achievements = {}
    
    # Group by user
    for user_name in df['Name'].unique():
        user_data = df[df['Name'] == user_name]
        
        # Calculate metrics
        total_days = len(user_data)
        present_days = len(user_data[user_data['Status'] == 'Present'])
        late_days = len(user_data[user_data['Status'] == 'Late'])
        absent_days = len(user_data[user_data['Status'] == 'Absent'])
        
        # Calculate attendance percentage
        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
        
        # Calculate streaks
        user_data_sorted = user_data.sort_values('Date')
        current_streak = 0
        max_streak = 0
        temp_streak = 0
        
        for _, row in user_data_sorted.iterrows():
            if row['Status'] == 'Present':
                temp_streak += 1
                max_streak = max(max_streak, temp_streak)
            else:
                temp_streak = 0
        
        # Current streak (from most recent)
        for _, row in user_data_sorted.iloc[::-1].iterrows():
            if row['Status'] == 'Present':
                current_streak += 1
            else:
                break
        
        # Determine badges
        badges = []
        
        # Attendance badges
        if attendance_percentage == 100:
            badges.append({"name": "🏆 Perfect Attendance", "type": "attendance", "color": "gold"})
        elif attendance_percentage >= 90:
            badges.append({"name": "🥇 Excellent Attendance", "type": "attendance", "color": "silver"})
        elif attendance_percentage >= 80:
            badges.append({"name": "🥈 Good Attendance", "type": "attendance", "color": "bronze"})
        elif attendance_percentage >= 70:
            badges.append({"name": "🎯 Consistent", "type": "attendance", "color": "blue"})
        
        # Streak badges
        if max_streak >= 10:
            badges.append({"name": "🔥 Fire Streak", "type": "streak", "color": "red"})
        elif max_streak >= 7:
            badges.append({"name": "⚡ Week Warrior", "type": "streak", "color": "orange"})
        elif max_streak >= 5:
            badges.append({"name": "💪 Consistent", "type": "streak", "color": "green"})
        
        # Late comer badge (if applicable)
        if late_days > 0:
            badges.append({"name": "🌙 Late Comer", "type": "timing", "color": "purple"})
        
        # Early bird badge
        early_arrivals = len(user_data[(user_data['Status'] == 'Present') & (user_data['Hour'] < 9)])
        if early_arrivals >= 5:
            badges.append({"name": "🐦 Early Bird", "type": "timing", "color": "yellow"})
        
        # Quality badges
        high_quality = len(user_data[user_data['Quality_Score'] >= 0.8]) if 'Quality_Score' in user_data.columns else 0
        if high_quality >= 10:
            badges.append({"name": "📸 Quality Master", "type": "quality", "color": "cyan"})
        
        achievements[user_name] = {
            'total_days': total_days,
            'present_days': present_days,
            'late_days': late_days,
            'absent_days': absent_days,
            'attendance_percentage': attendance_percentage,
            'current_streak': current_streak,
            'max_streak': max_streak,
            'badges': badges,
            'total_badges': len(badges)
        }
    
    return achievements

def show_gamification_demo():
    """Show gamification demo dashboard"""
    st.set_page_config(
        page_title="Day 14: Gamification Demo",
        page_icon="🏆",
        layout="wide"
    )
    
    st.title("🏆 Day 14: Gamification Features Demo")
    st.markdown("**EyeD AI Attendance System - Gamification & User Engagement**")
    
    # Create sample data
    with st.spinner("Generating sample gamification data..."):
        df = create_sample_gamification_data()
        
        # Add hour column for analysis
        df['Hour'] = pd.to_datetime(df['Time']).dt.hour
        df['Day_of_Week'] = pd.to_datetime(df['Date']).dt.day_name()
    
    st.success(f"✅ Generated {len(df)} attendance records for {df['Name'].nunique()} users over 30 days")
    
    # Calculate achievements
    achievements = calculate_user_achievements(df)
    
    # Create tabs for different gamification features
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏅 User Achievements", 
        "📊 Leaderboard", 
        "⏰ Timeline Analysis",
        "🎯 Badge Collection"
    ])
    
    with tab1:
        show_user_achievements_demo(achievements)
    
    with tab2:
        show_leaderboard_demo(achievements)
    
    with tab3:
        show_timeline_analysis_demo(df)
    
    with tab4:
        show_badge_collection_demo(achievements)

def show_user_achievements_demo(achievements):
    """Show individual user achievements and badges"""
    st.subheader("🏅 Individual User Achievements")
    
    # User selector
    selected_user = st.selectbox(
        "Select User to View Achievements",
        list(achievements.keys()),
        index=0
    )
    
    if selected_user:
        user_data = achievements[selected_user]
        
        # Display user stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Days", user_data['total_days'])
        with col2:
            st.metric("Attendance %", f"{user_data['attendance_percentage']:.1f}%")
        with col3:
            st.metric("Current Streak", user_data['current_streak'])
        with col4:
            st.metric("Max Streak", user_data['max_streak'])
        
        # Progress bars
        st.markdown("### 📈 Progress Tracking")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Attendance Progress**")
            attendance_progress = user_data['attendance_percentage'] / 100
            st.progress(attendance_progress)
            st.caption(f"{user_data['present_days']}/{user_data['total_days']} days present")
        
        with col2:
            st.markdown("**Streak Progress**")
            streak_progress = user_data['current_streak'] / max(user_data['max_streak'], 1)
            st.progress(streak_progress)
            st.caption(f"Current: {user_data['current_streak']} | Best: {user_data['max_streak']}")
        
        # Badges display
        st.markdown("### 🏆 Earned Badges")
        
        if user_data['badges']:
            # Group badges by type
            badge_types = {}
            for badge in user_data['badges']:
                badge_type = badge['type']
                if badge_type not in badge_types:
                    badge_types[badge_type] = []
                badge_types[badge_type].append(badge)
            
            # Display badges by category
            for badge_type, badges in badge_types.items():
                st.markdown(f"**{badge_type.title()} Badges:**")
                cols = st.columns(len(badges))
                for i, badge in enumerate(badges):
                    with cols[i]:
                        st.markdown(f"<div style='text-align: center; padding: 10px; border: 2px solid {badge.get('color', 'gray')}; border-radius: 10px;'>", unsafe_allow_html=True)
                        st.markdown(f"<h3>{badge['name']}</h3>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No badges earned yet. Keep attending to earn your first badge!")
        
        # Achievement suggestions
        st.markdown("### 💡 Achievement Suggestions")
        suggestions = []
        
        if user_data['attendance_percentage'] < 100:
            suggestions.append(f"🎯 **Perfect Attendance**: Attend {user_data['total_days'] - user_data['present_days']} more days to reach 100%")
        
        if user_data['max_streak'] < 5:
            suggestions.append(f"🔥 **Streak Builder**: Build a 5-day streak (current best: {user_data['max_streak']})")
        
        if user_data['current_streak'] == 0:
            suggestions.append("💪 **Get Started**: Begin a new attendance streak today!")
        
        for suggestion in suggestions:
            st.markdown(suggestion)

def show_leaderboard_demo(achievements):
    """Show leaderboard based on different metrics"""
    st.subheader("📊 Achievement Leaderboard")
    
    # Convert to DataFrame for easier manipulation
    leaderboard_data = []
    for user, data in achievements.items():
        leaderboard_data.append({
            'User': user,
            'Attendance %': data['attendance_percentage'],
            'Total Badges': data['total_badges'],
            'Max Streak': data['max_streak'],
            'Current Streak': data['current_streak'],
            'Present Days': data['present_days']
        })
    
    leaderboard_df = pd.DataFrame(leaderboard_data)
    
    # Different leaderboard views
    metric_options = ['Attendance %', 'Total Badges', 'Max Streak', 'Present Days']
    selected_metric = st.selectbox("Rank by:", metric_options)
    
    # Sort by selected metric
    if selected_metric in leaderboard_df.columns:
        leaderboard_df_sorted = leaderboard_df.sort_values(selected_metric, ascending=False)
        
        # Display top performers
        st.markdown(f"**🏆 Top Performers by {selected_metric}**")
        
        # Top 3 with special styling
        for i, (_, row) in enumerate(leaderboard_df_sorted.head(3).iterrows()):
            if i == 0:
                st.markdown(f"🥇 **{row['User']}** - {row[selected_metric]:.1f}")
            elif i == 1:
                st.markdown(f"🥈 **{row['User']}** - {row[selected_metric]:.1f}")
            elif i == 2:
                st.markdown(f"🥉 **{row['User']}** - {row[selected_metric]:.1f}")
        
        st.markdown("---")
        
        # Full leaderboard table
        st.markdown("**📋 Complete Leaderboard**")
        st.dataframe(leaderboard_df_sorted, use_container_width=True)
        
        # Leaderboard chart
        st.markdown("**📊 Leaderboard Visualization**")
        fig = px.bar(
            leaderboard_df_sorted.head(10),
            x='User',
            y=selected_metric,
            title=f"Top 10 Users by {selected_metric}",
            color=selected_metric,
            color_continuous_scale='viridis'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

def show_timeline_analysis_demo(df):
    """Show timeline chart of arrival times per user - Day 14 requirement"""
    st.subheader("⏰ Timeline Analysis - Arrival Times per User")
    st.markdown("**This is the key Day 14 requirement: Timeline chart showing arrival times per user**")
    
    if df is None or len(df) == 0:
        st.info("No data available for timeline analysis.")
        return
    
    # Filter for present users only
    present_df = df[df['Status'] == 'Present'].copy()
    
    if len(present_df) == 0:
        st.info("No present attendance data for timeline analysis.")
        return
    
    # User selector for timeline
    user_options = ['All Users'] + list(present_df['Name'].unique())
    selected_user_timeline = st.selectbox("Select User for Timeline:", user_options)
    
    # Filter data based on selection
    if selected_user_timeline == 'All Users':
        timeline_df = present_df
        title_suffix = "All Users"
    else:
        timeline_df = present_df[present_df['Name'] == selected_user_timeline]
        title_suffix = selected_user_timeline
    
    # Create timeline chart
    st.markdown(f"**📅 Arrival Times Timeline - {title_suffix}**")
    
    # Scatter plot of arrival times
    fig = px.scatter(
        timeline_df,
        x='Date',
        y='Hour',
        color='Name',
        title=f"Arrival Times Over Time - {title_suffix}",
        labels={'Hour': 'Hour of Day', 'Date': 'Date'},
        hover_data=['Name', 'Time', 'Status', 'Confidence']
    )
    
    # Add reference lines for typical work hours
    fig.add_hline(y=9, line_dash="dash", line_color="green", annotation_text="9 AM - Work Start")
    fig.add_hline(y=17, line_dash="dash", line_color="red", annotation_text="5 PM - Work End")
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Time distribution analysis
    st.markdown("**📊 Time Distribution Analysis**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly distribution
        hour_counts = timeline_df['Hour'].value_counts().sort_index()
        fig_hour = px.bar(
            x=hour_counts.index,
            y=hour_counts.values,
            title="Arrival Time Distribution by Hour",
            labels={'x': 'Hour of Day', 'y': 'Number of Arrivals'}
        )
        st.plotly_chart(fig_hour, use_container_width=True)
    
    with col2:
        # Day of week distribution
        day_counts = timeline_df['Day_of_Week'].value_counts()
        fig_day = px.pie(
            values=day_counts.values,
            names=day_counts.index,
            title="Arrivals by Day of Week"
        )
        st.plotly_chart(fig_day, use_container_width=True)
    
    # Early bird vs late comer analysis
    st.markdown("**🐦 Early Bird vs 🌙 Late Comer Analysis**")
    
    early_birds = timeline_df[timeline_df['Hour'] < 9]
    late_comers = timeline_df[timeline_df['Hour'] >= 9]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Early Birds (< 9 AM)", len(early_birds))
    with col2:
        st.metric("On Time (9 AM)", len(timeline_df[timeline_df['Hour'] == 9]))
    with col3:
        st.metric("Late Comers (> 9 AM)", len(late_comers))

def show_badge_collection_demo(achievements):
    """Show comprehensive badge collection and statistics"""
    st.subheader("🎯 Badge Collection & Statistics")
    
    # Collect all badges
    all_badges = []
    badge_counts = {}
    
    for user, data in achievements.items():
        for badge in data['badges']:
            badge_name = badge['name']
            all_badges.append({
                'User': user,
                'Badge': badge_name,
                'Type': badge['type'],
                'Color': badge.get('color', 'gray')
            })
            
            if badge_name not in badge_counts:
                badge_counts[badge_name] = 0
            badge_counts[badge_name] += 1
    
    if not all_badges:
        st.info("No badges have been earned yet. Start attending to earn badges!")
        return
    
    # Badge statistics
    st.markdown("**📊 Badge Statistics**")
    
    col1, col2, col3 = st.columns(3)
    
    total_badges_earned = len(all_badges)
    unique_badges = len(badge_counts)
    users_with_badges = len(set([badge['User'] for badge in all_badges]))
    
    with col1:
        st.metric("Total Badges Earned", total_badges_earned)
    with col2:
        st.metric("Unique Badge Types", unique_badges)
    with col3:
        st.metric("Users with Badges", users_with_badges)
    
    # Most common badges
    st.markdown("**🏆 Most Common Badges**")
    
    if badge_counts:
        badge_df = pd.DataFrame([
            {'Badge': badge, 'Count': count}
            for badge, count in badge_counts.items()
        ]).sort_values('Count', ascending=False)
        
        fig = px.bar(
            badge_df,
            x='Badge',
            y='Count',
            title="Badge Popularity",
            color='Count',
            color_continuous_scale='viridis'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Badge type distribution
    st.markdown("**📈 Badge Type Distribution**")
    
    badge_types = {}
    for badge in all_badges:
        badge_type = badge['Type']
        if badge_type not in badge_types:
            badge_types[badge_type] = 0
        badge_types[badge_type] += 1
    
    if badge_types:
        type_df = pd.DataFrame([
            {'Type': badge_type, 'Count': count}
            for badge_type, count in badge_types.items()
        ])
        
        fig = px.pie(
            type_df,
            values='Count',
            names='Type',
            title="Badges by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Individual badge collections
    st.markdown("**👤 Individual Badge Collections**")
    
    user_badges = {}
    for user, data in achievements.items():
        user_badges[user] = data['badges']
    
    # Display each user's badge collection
    for user, badges in user_badges.items():
        if badges:
            st.markdown(f"**{user}** ({len(badges)} badges)")
            
            # Create columns for badges
            cols = st.columns(min(len(badges), 4))
            for i, badge in enumerate(badges):
                with cols[i % 4]:
                    st.markdown(
                        f"<div style='text-align: center; padding: 8px; margin: 2px; border: 2px solid {badge.get('color', 'gray')}; border-radius: 8px; background-color: rgba(0,0,0,0.05);'>",
                        unsafe_allow_html=True
                    )
                    st.markdown(f"<strong>{badge['name']}</strong>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("---")

def main():
    """Main demo function"""
    st.sidebar.title("🏆 Day 14 Demo")
    st.sidebar.markdown("**Gamification Features**")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 Day 14 Requirements")
    st.sidebar.markdown("✅ Emoji badges (🏆 100% attendance, 🌙 Late comer)")
    st.sidebar.markdown("✅ Timeline chart → arrival times per user")
    st.sidebar.markdown("✅ Gamification elements for user engagement")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🚀 Features Implemented")
    st.sidebar.markdown("🏅 **User Achievements**: Individual progress tracking")
    st.sidebar.markdown("📊 **Leaderboards**: Multiple ranking metrics")
    st.sidebar.markdown("⏰ **Timeline Analysis**: Arrival time visualization")
    st.sidebar.markdown("🎯 **Badge Collection**: Comprehensive badge system")
    
    # Show the main demo
    show_gamification_demo()

if __name__ == "__main__":
    main()
