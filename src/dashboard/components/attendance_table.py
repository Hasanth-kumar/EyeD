"""
Enhanced Attendance Table Component - Phase 4 Implementation
Provides advanced filtering, search, and table view for attendance data
Uses service layer for data access and business logic
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

def load_attendance_data():
    """Load attendance data through the service layer"""
    try:
        # Get attendance service from session state
        if 'attendance_service' not in st.session_state:
            return None, "Services not initialized. Please refresh the page."
        
        attendance_service = st.session_state.attendance_service
        
        # Get attendance history through service
        attendance_data = attendance_service.get_attendance_report_by_type("detailed_history")
        
        if not attendance_data or 'attendance_data' not in attendance_data:
            return None, "No attendance data available yet. Start using the system to see logs."
        
        # Extract the actual attendance data from the report
        actual_data = attendance_data['attendance_data']
        
        if not actual_data or len(actual_data) == 0:
            return None, "No attendance data available yet. Start using the system to see logs."
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(actual_data)
        
        # Ensure required columns exist
        required_columns = ['Date', 'Time', 'Name', 'ID', 'Status', 'Confidence']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return None, f"Missing required columns: {missing_columns}"
        
        # Convert date and time columns
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
        
        # Add derived columns for better analysis
        df['Day_of_Week'] = df['Date'].dt.day_name()
        df['Hour'] = df['Time'].dt.hour
        df['Week_Number'] = df['Date'].dt.isocalendar().week
        
        # Add status emoji markers
        df['Status_Display'] = df['Status'].apply(add_status_emoji)
        
        # Add confidence level categorization
        df['Confidence_Level'] = df['Confidence'].apply(categorize_confidence)
        
        return df, None
        
    except Exception as e:
        return None, f"Error loading attendance data: {e}"

def add_status_emoji(status):
    """Add emoji markers to status"""
    if pd.isna(status):
        return "❓ Unknown"
    elif "present" in str(status).lower():
        return "✅ Present"
    elif "absent" in str(status).lower():
        return "❌ Absent"
    elif "late" in str(status).lower():
        return "🌙 Late"
    else:
        return f"📝 {status}"

def categorize_confidence(confidence):
    """Categorize confidence levels"""
    if pd.isna(confidence):
        return "Unknown"
    elif confidence >= 0.8:
        return "🟢 High"
    elif confidence >= 0.6:
        return "🟡 Medium"
    else:
        return "🔴 Low"

def show_attendance_table():
    """Show enhanced attendance table with advanced filtering and search"""
    st.header("📋 Enhanced Attendance Table - Phase 4")
    st.markdown("**Service Layer Architecture with Advanced Filtering**")
    
    # Architecture info
    st.info("""
    🏗️ **New Architecture**: This component now uses the service layer instead of direct file access.
    - **Service Layer**: Business logic orchestration
    - **Repository Layer**: Data persistence
    - **Clean Separation**: UI components depend on services, not data directly
    """)
    
    # Load data through service layer
    df, error = load_attendance_data()
    if error:
        st.error(error)
        if "Services not initialized" in error:
            st.info("Please refresh the page to initialize services.")
        else:
            st.info("Make sure the attendance data is available through the service layer.")
        return
    
    # Advanced filtering section
    st.subheader("🔍 Advanced Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Date range filter
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Quick date filters
        quick_filters = st.selectbox(
            "Quick Filters",
            ["Custom Range", "Last 7 Days", "Last 30 Days", "This Month", "This Week"]
        )
    
    with col2:
        # User filter
        all_users = ["All Users"] + sorted(df['Name'].unique().tolist())
        user_filter = st.selectbox("Select User", all_users)
        
        # Status filter
        all_statuses = ["All Statuses"] + sorted(df['Status'].unique().tolist())
        status_filter = st.selectbox("Select Status", all_statuses)
        
        # Confidence filter
        confidence_filter = st.selectbox(
            "Confidence Level",
            ["All Levels", "🟢 High", "🟡 Medium", "🔴 Low"]
        )
    
    with col3:
        # Liveness filter
        liveness_filter = st.selectbox(
            "Liveness Verification",
            ["All", "✅ Verified", "❌ Not Verified"]
        )
        
        # Quality score filter
        min_quality = float(df['Face_Quality_Score'].min()) if 'Face_Quality_Score' in df.columns else 0.0
        max_quality = float(df['Face_Quality_Score'].max()) if 'Face_Quality_Score' in df.columns else 1.0
        quality_range = st.slider(
            "Quality Score Range",
            min_value=min_quality,
            max_value=max_quality,
            value=(min_quality, max_quality),
            step=0.01
        )
    
    # Apply quick date filters
    if quick_filters != "Custom Range":
        today = datetime.now().date()
        if quick_filters == "Last 7 Days":
            start_date = today - timedelta(days=7)
            end_date = today
        elif quick_filters == "Last 30 Days":
            start_date = today - timedelta(days=30)
            end_date = today
        elif quick_filters == "This Month":
            start_date = today.replace(day=1)
            end_date = today
        elif quick_filters == "This Week":
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        
        date_range = (start_date, end_date)
    
    # Apply filters
    filtered_df = df.copy()
    
    # Date filter
    if len(date_range) == 2 and date_range[0] and date_range[1]:
        filtered_df = filtered_df[
            (filtered_df['Date'].dt.date >= date_range[0]) & 
            (filtered_df['Date'].dt.date <= date_range[1])
        ]
    
    # User filter
    if user_filter != "All Users":
        filtered_df = filtered_df[filtered_df['Name'] == user_filter]
    
    # Status filter
    if status_filter != "All Statuses":
        filtered_df = filtered_df[filtered_df['Status'] == status_filter]
    
    # Confidence filter
    if confidence_filter != "All Levels":
        filtered_df = filtered_df[filtered_df['Confidence_Level'] == confidence_filter]
    
    # Liveness filter
    if liveness_filter == "✅ Verified":
        filtered_df = filtered_df[filtered_df['Liveness_Verified'] == True]
    elif liveness_filter == "❌ Not Verified":
        filtered_df = filtered_df[filtered_df['Liveness_Verified'] == False]
    
    # Quality filter
    if 'Face_Quality_Score' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['Face_Quality_Score'] >= quality_range[0]) & 
            (filtered_df['Face_Quality_Score'] <= quality_range[1])
        ]
    
    # Search functionality
    st.subheader("🔎 Search & Quick Actions")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input(
            "Search by Name, ID, or Session ID",
            placeholder="Enter search term..."
        )
        
        if search_term:
            search_mask = (
                filtered_df['Name'].str.contains(search_term, case=False, na=False) |
                filtered_df['ID'].str.contains(search_term, case=False, na=False) |
                filtered_df['Session_ID'].str.contains(search_term, case=False, na=False)
            )
            filtered_df = filtered_df[search_mask]
    
    with col2:
        if st.button("🔄 Reset Filters"):
            st.rerun()
    
    with col3:
        # Export functionality
        if st.button("📤 Export Data"):
            export_data(filtered_df)
    
    # Display filtered results
    st.subheader(f"📊 Filtered Results ({len(filtered_df)} entries)")
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_entries = len(filtered_df)
        st.metric("Total Entries", total_entries)
    
    with col2:
        if 'Confidence' in filtered_df.columns:
            avg_confidence = filtered_df['Confidence'].mean()
            st.metric("Avg Confidence", f"{avg_confidence:.1%}" if not pd.isna(avg_confidence) else "N/A")
    
    with col3:
        if 'Liveness_Verified' in filtered_df.columns:
            liveness_rate = filtered_df['Liveness_Verified'].mean()
            st.metric("Liveness Rate", f"{liveness_rate:.1%}" if not pd.isna(liveness_rate) else "N/A")
    
    with col4:
        if 'Face_Quality_Score' in filtered_df.columns:
            avg_quality = filtered_df['Face_Quality_Score'].mean()
            st.metric("Avg Quality", f"{avg_quality:.2f}" if not pd.isna(avg_quality) else "N/A")
    
    # Enhanced data table
    if len(filtered_df) > 0:
        # Select columns to display
        display_columns = [
            'Name', 'ID', 'Date', 'Time', 'Status_Display', 'Confidence_Level',
            'Liveness_Verified', 'Face_Quality_Score', 'Processing_Time_MS'
        ]
        
        # Filter columns that exist in the dataframe
        available_columns = [col for col in display_columns if col in filtered_df.columns]
        
        # Format the display dataframe
        display_df = filtered_df[available_columns].copy()
        
        # Format date and time for better display
        if 'Date' in display_df.columns:
            display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        if 'Time' in display_df.columns:
            display_df['Time'] = display_df['Time'].dt.strftime('%H:%M:%S')
        
        # Add row numbers
        display_df.insert(0, 'Row', range(1, len(display_df) + 1))
        
        # Display the table with better formatting
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Row": st.column_config.NumberColumn("Row", width="small"),
                "Name": st.column_config.TextColumn("Name", width="medium"),
                "ID": st.column_config.TextColumn("ID", width="small"),
                "Date": st.column_config.TextColumn("Date", width="small"),
                "Time": st.column_config.TextColumn("Time", width="small"),
                "Status_Display": st.column_config.TextColumn("Status", width="small"),
                "Confidence_Level": st.column_config.TextColumn("Confidence", width="small"),
                "Liveness_Verified": st.column_config.CheckboxColumn("Liveness", width="small"),
                "Face_Quality_Score": st.column_config.NumberColumn("Quality", format="%.2f", width="small"),
                "Processing_Time_MS": st.column_config.NumberColumn("Time (ms)", format="%.1f", width="small")
            }
        )
        
        # Pagination info
        st.caption(f"Showing {len(filtered_df)} of {len(df)} total entries")
        
    else:
        st.info("No entries match the current filters. Try adjusting your search criteria.")
    
    # Additional insights
    if len(filtered_df) > 0:
        st.subheader("💡 Quick Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Status distribution
            if 'Status' in filtered_df.columns:
                status_counts = filtered_df['Status'].value_counts()
                st.write("**Status Distribution:**")
                for status, count in status_counts.items():
                    emoji = "✅" if "present" in str(status).lower() else "❌" if "absent" in str(status).lower() else "🌙"
                    st.write(f"{emoji} {status}: {count}")
        
        with col2:
            # Top users by attendance
            if 'Name' in filtered_df.columns:
                user_counts = filtered_df['Name'].value_counts().head(5)
                st.write("**Top Users (This Period):**")
                for user, count in user_counts.items():
                    st.write(f"👤 {user}: {count} entries")

def export_data(df):
    """Export filtered data to CSV"""
    if len(df) > 0:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"attendance_export_{timestamp}.csv"
        
        # Prepare export data
        export_df = df.copy()
        
        # Convert datetime objects to strings for CSV export
        if 'Date' in export_df.columns:
            export_df['Date'] = export_df['Date'].dt.strftime('%Y-%m-%d')
        if 'Time' in export_df.columns:
            export_df['Time'] = export_df['Time'].dt.strftime('%H:%M:%S')
        
        # Create download button
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=filename,
            mime="text/csv"
        )
        
        st.success(f"Data exported successfully! {len(df)} entries included.")
    else:
        st.warning("No data to export. Please adjust your filters.")

