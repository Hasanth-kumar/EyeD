"""
Gamification Component - Enhanced Phase 4.4 Implementation
Handles badges, achievements, leaderboards, and user engagement features
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

def load_gamification_data():
    """Load data for gamification features through the service layer"""
    try:
        # Get attendance service from session state
        if 'attendance_service' not in st.session_state:
            return None, "Services not initialized. Please refresh the page."
        
        attendance_service = st.session_state.attendance_service
        
        # Get attendance data through service layer
        attendance_data = attendance_service.get_attendance_report_by_type("detailed_history")
        
        if not attendance_data or 'attendance_data' not in attendance_data:
            return None, "No attendance data available yet."
        
        # Extract the actual attendance data from the report
        actual_data = attendance_data['attendance_data']
        
        if not actual_data or len(actual_data) == 0:
            return None, "No attendance data available yet."
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(actual_data)
        
        # Filter out test entries
        df = df[~df['Name'].str.startswith('#', na=False)]
        
        if len(df) == 0:
            return None, "No valid attendance data available."
        
        # Convert date and time columns
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
        
        # Add derived columns for gamification
        df['Day_of_Week'] = df['Date'].dt.day_name()
        df['Hour'] = df['Time'].dt.hour
        df['Week_Number'] = df['Date'].dt.isocalendar().week
        df['Month'] = df['Date'].dt.month_name()
        df['Year'] = df['Date'].dt.year
        
        # Add attendance status indicators
        df['Is_Present'] = (df['Status'] == 'Present').astype(int)
        df['Is_Late'] = (df['Status'] == 'Late').astype(int)
        df['Is_Absent'] = (df['Status'] == 'Absent').astype(int)
        
        return df, None
    except Exception as e:
        return None, f"Error loading data: {e}"

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
        
        # Calculate additional metrics
        early_arrivals = len(user_data[(user_data['Status'] == 'Present') & (user_data['Hour'] < 9)])
        on_time_arrivals = len(user_data[(user_data['Status'] == 'Present') & (user_data['Hour'] == 9)])
        late_arrivals = len(user_data[(user_data['Status'] == 'Present') & (user_data['Hour'] > 9)])
        
        # Calculate quality metrics
        avg_confidence = user_data['Confidence'].mean() if 'Confidence' in user_data.columns else 0
        high_quality_days = len(user_data[user_data['Confidence'] >= 0.9]) if 'Confidence' in user_data.columns else 0
        
        # Determine badges with enhanced categories
        badges = []
        
        # 🏆 ATTENDANCE BADGES
        if attendance_percentage == 100:
            badges.append({"name": "🏆 Perfect Attendance", "type": "attendance", "color": "gold", "rarity": "legendary"})
        elif attendance_percentage >= 95:
            badges.append({"name": "🥇 Excellent Attendance", "type": "attendance", "color": "silver", "rarity": "epic"})
        elif attendance_percentage >= 90:
            badges.append({"name": "🥈 Great Attendance", "type": "attendance", "color": "bronze", "rarity": "rare"})
        elif attendance_percentage >= 80:
            badges.append({"name": "🥉 Good Attendance", "type": "attendance", "color": "blue", "rarity": "uncommon"})
        elif attendance_percentage >= 70:
            badges.append({"name": "🎯 Consistent", "type": "attendance", "color": "green", "rarity": "common"})
        
        # 🔥 STREAK BADGES
        if max_streak >= 30:
            badges.append({"name": "🔥 Legendary Streak", "type": "streak", "color": "red", "rarity": "legendary"})
        elif max_streak >= 20:
            badges.append({"name": "⚡ Epic Streak", "type": "streak", "color": "orange", "rarity": "epic"})
        elif max_streak >= 15:
            badges.append({"name": "💪 Heroic Streak", "type": "streak", "color": "purple", "rarity": "rare"})
        elif max_streak >= 10:
            badges.append({"name": "🔥 Fire Streak", "type": "streak", "color": "red", "rarity": "uncommon"})
        elif max_streak >= 7:
            badges.append({"name": "⚡ Week Warrior", "type": "streak", "color": "orange", "rarity": "common"})
        elif max_streak >= 5:
            badges.append({"name": "💪 Consistent", "type": "streak", "color": "green", "rarity": "common"})
        
        # ⏰ TIMING BADGES
        if early_arrivals >= 20:
            badges.append({"name": "🐦 Early Bird Master", "type": "timing", "color": "yellow", "rarity": "epic"})
        elif early_arrivals >= 10:
            badges.append({"name": "🐦 Early Bird", "type": "timing", "color": "yellow", "rarity": "rare"})
        elif early_arrivals >= 5:
            badges.append({"name": "🌅 Morning Person", "type": "timing", "color": "lightblue", "rarity": "uncommon"})
        
        if on_time_arrivals >= 15:
            badges.append({"name": "⏰ Punctuality Master", "type": "timing", "color": "green", "rarity": "epic"})
        elif on_time_arrivals >= 10:
            badges.append({"name": "⏰ Always On Time", "type": "timing", "color": "green", "rarity": "rare"})
        elif on_time_arrivals >= 5:
            badges.append({"name": "⏰ Punctual", "type": "timing", "color": "lightgreen", "rarity": "uncommon"})
        
        if late_arrivals >= 10:
            badges.append({"name": "🌙 Night Owl", "type": "timing", "color": "purple", "rarity": "uncommon"})
        elif late_arrivals >= 5:
            badges.append({"name": "🌙 Late Comer", "type": "timing", "color": "purple", "rarity": "common"})
        
        # 📸 QUALITY BADGES
        if high_quality_days >= 20:
            badges.append({"name": "📸 Quality Master", "type": "quality", "color": "cyan", "rarity": "epic"})
        elif high_quality_days >= 15:
            badges.append({"name": "📸 High Quality", "type": "quality", "color": "cyan", "rarity": "rare"})
        elif high_quality_days >= 10:
            badges.append({"name": "📸 Quality Focused", "type": "quality", "color": "lightcyan", "rarity": "uncommon"})
        
        if avg_confidence >= 0.95:
            badges.append({"name": "🎯 Precision Master", "type": "quality", "color": "gold", "rarity": "legendary"})
        elif avg_confidence >= 0.90:
            badges.append({"name": "🎯 High Precision", "type": "quality", "color": "silver", "rarity": "epic"})
        elif avg_confidence >= 0.85:
            badges.append({"name": "🎯 Accurate", "type": "quality", "color": "bronze", "rarity": "rare"})
        
        # 🏅 MILESTONE BADGES
        if total_days >= 100:
            badges.append({"name": "🏅 Centurion", "type": "milestone", "color": "gold", "rarity": "legendary"})
        elif total_days >= 50:
            badges.append({"name": "🏅 Half Century", "type": "milestone", "color": "silver", "rarity": "epic"})
        elif total_days >= 25:
            badges.append({"name": "🏅 Quarter Century", "type": "milestone", "color": "bronze", "rarity": "rare"})
        elif total_days >= 10:
            badges.append({"name": "🏅 Decade", "type": "milestone", "color": "blue", "rarity": "uncommon"})
        elif total_days >= 5:
            badges.append({"name": "🏅 Starter", "type": "milestone", "color": "green", "rarity": "common"})
        
        # 🎖️ SPECIAL ACHIEVEMENTS
        if current_streak >= 5 and attendance_percentage >= 90:
            badges.append({"name": "🎖️ Streak Master", "type": "special", "color": "rainbow", "rarity": "legendary"})
        
        if early_arrivals >= 5 and on_time_arrivals >= 5:
            badges.append({"name": "🎖️ Time Master", "type": "special", "color": "rainbow", "rarity": "epic"})
        
        if high_quality_days >= 10 and avg_confidence >= 0.9:
            badges.append({"name": "🎖️ Quality Champion", "type": "special", "color": "rainbow", "rarity": "epic"})
        
        achievements[user_name] = {
            'total_days': total_days,
            'present_days': present_days,
            'late_days': late_days,
            'absent_days': absent_days,
            'attendance_percentage': attendance_percentage,
            'current_streak': current_streak,
            'max_streak': max_streak,
            'early_arrivals': early_arrivals,
            'on_time_arrivals': on_time_arrivals,
            'late_arrivals': late_arrivals,
            'avg_confidence': avg_confidence,
            'high_quality_days': high_quality_days,
            'badges': badges,
            'total_badges': len(badges),
            'legendary_badges': len([b for b in badges if b.get('rarity') == 'legendary']),
            'epic_badges': len([b for b in badges if b.get('rarity') == 'epic']),
            'rare_badges': len([b for b in badges if b.get('rarity') == 'rare'])
        }
    
    return achievements

def show_gamification():
    """Show enhanced gamification dashboard with badges and achievements"""
    st.markdown("## 🎮 Gamification Center")
    st.markdown("**Earn badges, track achievements, and stay motivated!**")
    
    # Load data
    df, error = load_gamification_data()
    if error:
        st.error(error)
        st.info("Start using the system to see achievements and badges.")
        return
    
    # Calculate achievements
    achievements = calculate_user_achievements(df)
    
    if not achievements:
        st.info("No user data available for gamification features.")
        return
    
    # Create tabs for different gamification features
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏅 User Achievements", 
        "📊 Leaderboard", 
        "⏰ Timeline Analysis",
        "🎯 Badge Collection",
        "🎖️ Special Features"
    ])
    
    with tab1:
        show_user_achievements(achievements)
    
    with tab2:
        show_leaderboard(achievements)
    
    with tab3:
        show_timeline_analysis(df)
    
    with tab4:
        show_badge_collection(achievements)
    
    with tab5:
        show_special_features(achievements, df)

def show_user_achievements(achievements):
    """Show individual user achievements and badges with enhanced design"""
    st.subheader("🏅 Individual User Achievements")
    
    # User selector
    selected_user = st.selectbox(
        "Select User to View Achievements",
        list(achievements.keys()),
        index=0
    )
    
    if selected_user:
        user_data = achievements[selected_user]
        
        # Display user stats with enhanced metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Days", user_data['total_days'])
        with col2:
            st.metric("Attendance %", f"{user_data['attendance_percentage']:.1f}%")
        with col3:
            st.metric("Current Streak", user_data['current_streak'])
        with col4:
            st.metric("Max Streak", user_data['max_streak'])
        with col5:
            st.metric("Total Badges", user_data['total_badges'])
        
        # Enhanced progress tracking
        st.markdown("### 📈 Progress Tracking")
        
        col1, col2, col3 = st.columns(3)
        
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
        
        with col3:
            st.markdown("**Quality Progress**")
            quality_progress = user_data['avg_confidence']
            st.progress(quality_progress)
            st.caption(f"Avg Confidence: {user_data['avg_confidence']:.1%}")
        
        # Badge rarity display
        st.markdown("### 🏆 Badge Rarity Breakdown")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Legendary", user_data['legendary_badges'], "🏆")
        with col2:
            st.metric("Epic", user_data['epic_badges'], "💎")
        with col3:
            st.metric("Rare", user_data['rare_badges'], "⭐")
        with col4:
            st.metric("Common", user_data['total_badges'] - user_data['legendary_badges'] - user_data['epic_badges'] - user_data['rare_badges'], "🔹")
        
        # Enhanced badges display with rarity colors
        st.markdown("### 🏆 Earned Badges")
        
        if user_data['badges']:
            # Group badges by type
            badge_types = {}
            for badge in user_data['badges']:
                badge_type = badge['type']
                if badge_type not in badge_types:
                    badge_types[badge_type] = []
                badge_types[badge_type].append(badge)
            
            # Display badges by category with enhanced styling
            for badge_type, badges in badge_types.items():
                st.markdown(f"**{badge_type.title()} Badges:**")
                cols = st.columns(len(badges))
                for i, badge in enumerate(badges):
                    with cols[i]:
                        rarity = badge.get('rarity', 'common')
                        color = badge.get('color', 'gray')
                        
                        # Enhanced styling based on rarity
                        if rarity == 'legendary':
                            border_style = "5px solid gold; box-shadow: 0 0 10px gold;"
                        elif rarity == 'epic':
                            border_style = "4px solid purple; box-shadow: 0 0 8px purple;"
                        elif rarity == 'rare':
                            border_style = "3px solid blue; box-shadow: 0 0 6px blue;"
                        else:
                            border_style = f"2px solid {color};"
                        
                        st.markdown(f"""
                        <div style='text-align: center; padding: 15px; margin: 5px; border: {border_style} border-radius: 15px; background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));'>
                            <h4 style='margin: 0; color: {color};'>{badge['name']}</h4>
                            <small style='color: {color}; font-weight: bold;'>{rarity.upper()}</small>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No badges earned yet. Keep attending to earn your first badge!")
        
        # Enhanced achievement suggestions
        st.markdown("### 💡 Achievement Suggestions")
        suggestions = []
        
        if user_data['attendance_percentage'] < 100:
            needed_days = user_data['total_days'] - user_data['present_days']
            suggestions.append(f"🎯 **Perfect Attendance**: Attend {needed_days} more days to reach 100%")
        
        if user_data['max_streak'] < 5:
            suggestions.append(f"🔥 **Streak Builder**: Build a 5-day streak (current best: {user_data['max_streak']})")
        
        if user_data['current_streak'] == 0:
            suggestions.append("💪 **Get Started**: Begin a new attendance streak today!")
        
        if user_data['early_arrivals'] < 5:
            suggestions.append("🐦 **Early Bird**: Try arriving before 9 AM to earn the Early Bird badge!")
        
        if user_data['avg_confidence'] < 0.9:
            suggestions.append("📸 **Quality Focus**: Improve your face recognition quality for better badges!")
        
        for suggestion in suggestions:
            st.markdown(suggestion)

def show_leaderboard(achievements):
    """Show enhanced leaderboard with multiple metrics and visualizations"""
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
            'Present Days': data['present_days'],
            'Legendary Badges': data['legendary_badges'],
            'Epic Badges': data['epic_badges'],
            'Rare Badges': data['rare_badges'],
            'Avg Confidence': data['avg_confidence'],
            'Early Arrivals': data['early_arrivals']
        })
    
    leaderboard_df = pd.DataFrame(leaderboard_data)
    
    # Different leaderboard views
    metric_options = ['Attendance %', 'Total Badges', 'Max Streak', 'Present Days', 'Legendary Badges', 'Epic Badges', 'Avg Confidence']
    selected_metric = st.selectbox("Rank by:", metric_options)
    
    # Sort by selected metric
    if selected_metric in leaderboard_df.columns:
        leaderboard_df_sorted = leaderboard_df.sort_values(selected_metric, ascending=False)
        
        # Display top performers with enhanced styling
        st.markdown(f"**🏆 Top Performers by {selected_metric}**")
        
        # Top 3 with special styling and medals
        for i, (_, row) in enumerate(leaderboard_df_sorted.head(3).iterrows()):
            if i == 0:
                st.markdown(f"🥇 **{row['User']}** - {row[selected_metric]:.1f} 🏆")
            elif i == 1:
                st.markdown(f"🥈 **{row['User']}** - {row[selected_metric]:.1f} 🥈")
            elif i == 2:
                st.markdown(f"🥉 **{row['User']}** - {row[selected_metric]:.1f} 🥉")
        
        st.markdown("---")
        
        # Full leaderboard table
        st.markdown("**📋 Complete Leaderboard**")
        st.dataframe(leaderboard_df_sorted, use_container_width=True)
        
        # Enhanced leaderboard chart
        st.markdown("**📊 Leaderboard Visualization**")
        fig = px.bar(
            leaderboard_df_sorted.head(10),
            x='User',
            y=selected_metric,
            title=f"Top 10 Users by {selected_metric}",
            color=selected_metric,
            color_continuous_scale='viridis'
        )
        fig.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig, use_container_width=True)

def show_timeline_analysis(df):
    """Show timeline chart of arrival times per user"""
    st.subheader("⏰ Timeline Analysis - Arrival Times per User")
    
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

def show_badge_collection(achievements):
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

def show_special_features(achievements, df):
    """Show special gamification features like team challenges and milestones"""
    st.subheader("🎖️ Special Features")
    
    # Team Challenge Section
    st.markdown("### 🏆 Team Challenges")
    
    if len(achievements) >= 2:
        # Calculate team metrics
        total_team_attendance = sum(data['present_days'] for data in achievements.values())
        total_team_days = sum(data['total_days'] for data in achievements.values())
        team_attendance_rate = (total_team_attendance / total_team_days * 100) if total_team_days > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Team Attendance Rate", f"{team_attendance_rate:.1f}%", "👥")
        with col2:
            st.metric("Total Team Badges", sum(data['total_badges'] for data in achievements.values()), "🏆")
        with col3:
            st.metric("Team Members", len(achievements), "👤")
        
        # Team goals
        st.markdown("**🎯 Team Goals**")
        
        if team_attendance_rate >= 95:
            st.success("🏆 **Team Excellence**: Your team has achieved 95%+ attendance rate!")
        elif team_attendance_rate >= 90:
            st.info("🥇 **Team Greatness**: Your team is close to 95% attendance rate!")
        elif team_attendance_rate >= 80:
            st.warning("🥈 **Team Good**: Your team is doing well, aim for 90%!")
        else:
            st.error("🥉 **Team Improvement**: Your team needs to improve attendance!")
        
        # Team streak challenge
        max_team_streak = max(data['max_streak'] for data in achievements.values())
        if max_team_streak >= 10:
            st.success(f"🔥 **Team Streak Champion**: Someone achieved a {max_team_streak}-day streak!")
        elif max_team_streak >= 7:
            st.info(f"⚡ **Team Streak**: Best team streak is {max_team_streak} days!")
        else:
            st.warning(f"💪 **Team Streak Goal**: Best team streak is {max_team_streak} days. Aim for 7+!")
    
    else:
        st.info("Team challenges require at least 2 users. Invite more people to join!")
    
    # Milestone Celebrations
    st.markdown("### 🎉 Milestone Celebrations")
    
    # Find recent milestones
    milestones = []
    for user, data in achievements.items():
        if data['total_days'] >= 100:
            milestones.append(f"🏅 **{user}** reached 100 days! Centurion status achieved!")
        elif data['total_days'] >= 50:
            milestones.append(f"🏅 **{user}** reached 50 days! Half Century milestone!")
        elif data['total_days'] >= 25:
            milestones.append(f"🏅 **{user}** reached 25 days! Quarter Century milestone!")
        elif data['total_days'] >= 10:
            milestones.append(f"🏅 **{user}** reached 10 days! Decade milestone!")
        
        if data['max_streak'] >= 20:
            milestones.append(f"🔥 **{user}** achieved a {data['max_streak']}-day streak! Epic!")
        elif data['max_streak'] >= 10:
            milestones.append(f"🔥 **{user}** achieved a {data['max_streak']}-day streak! Amazing!")
        
        if data['legendary_badges'] > 0:
            milestones.append(f"🏆 **{user}** earned {data['legendary_badges']} legendary badge(s)!")
    
    if milestones:
        st.markdown("**Recent Achievements:**")
        for milestone in milestones:
            st.markdown(f"🎉 {milestone}")
    else:
        st.info("No recent milestones to celebrate. Keep attending to unlock achievements!")
    
    # Fun Statistics
    st.markdown("### 📊 Fun Statistics")
    
    if df is not None and len(df) > 0:
        # Most active day
        most_active_day = df['Day_of_Week'].value_counts().index[0]
        most_active_count = df['Day_of_Week'].value_counts().iloc[0]
        
        # Most active hour
        most_active_hour = df['Hour'].value_counts().index[0]
        most_active_hour_count = df['Hour'].value_counts().iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Most Active Day", most_active_day, f"{most_active_count} check-ins")
        with col2:
            st.metric("Most Active Hour", f"{most_active_hour}:00", f"{most_active_hour_count} check-ins")
        
        # Quality statistics
        if 'Confidence' in df.columns:
            avg_confidence = df['Confidence'].mean()
            high_quality_sessions = len(df[df['Confidence'] >= 0.9])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Average Quality", f"{avg_confidence:.1%}", "📸")
            with col2:
                st.metric("High Quality Sessions", high_quality_sessions, "⭐")
