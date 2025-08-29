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
import plotly.graph_objects as go
from pathlib import Path
import sys
import time
from datetime import datetime
import cv2
import numpy as np
import io
from PIL import Image

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Mock classes for demonstration
class MockFaceDatabase:
    def __init__(self):
        self.users_db = {
            "user1": {"name": "Alice Johnson", "image_path": "data/faces/user1.jpg"},
            "user2": {"name": "Bob Smith", "image_path": "data/faces/user2.jpg"},
            "user3": {"name": "Carol Davis", "image_path": "data/faces/user3.jpg"}
        }
    
    def register_user(self, name, user_id, image):
        self.users_db[user_id] = {"name": name, "image_path": f"data/faces/{user_id}.jpg"}
        return True
    
    def get_recognition_accuracy(self):
        return 0.85

class MockAttendanceManager:
    def __init__(self):
        self.attendance_data = []
    
    def get_today_attendance_count(self):
        return 12
    
    def get_recognition_accuracy(self):
        return "85%"

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

def show_attendance_logs():
    """Show attendance logs with filtering and analysis"""
    st.header("📋 Attendance Logs")
    
    # Initialize systems
    if not initialize_systems():
        return
    
    try:
        # Load attendance data
        df = pd.read_csv("data/attendance.csv")
        
        # Remove comment rows
        df = df[~df['Name'].str.startswith('#', na=False)]
        
        if len(df) == 0:
            st.info("No attendance data available yet. Start using the system to see logs.")
            return
        
        # Convert date and time columns
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
        
        # Filtering options
        st.subheader("🔍 Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_filter = st.date_input("Select Date", value=datetime.now().date())
        
        with col2:
            user_filter = st.selectbox("Select User", ["All"] + list(df['Name'].unique()))
        
        with col3:
            status_filter = st.selectbox("Select Status", ["All"] + list(df['Status'].unique()))
        
        # Apply filters
        filtered_df = df.copy()
        
        if date_filter:
            filtered_df = filtered_df[filtered_df['Date'].dt.date == date_filter]
        
        if user_filter != "All":
            filtered_df = filtered_df[filtered_df['Name'] == user_filter]
        
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['Status'] == status_filter]
        
        # Display filtered data
        st.subheader(f"📊 Filtered Results ({len(filtered_df)} entries)")
        
        # Add emoji markers
        def add_status_emoji(status):
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
        
        filtered_df['Status_Display'] = filtered_df['Status'].apply(add_status_emoji)
        
        # Show the filtered data
        st.dataframe(filtered_df[['Name', 'Date', 'Time', 'Status_Display', 'Confidence', 'Liveness_Verified']], 
                     use_container_width=True)
        
        # Summary statistics
        st.subheader("📈 Summary Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_entries = len(filtered_df)
            st.metric("Total Entries", total_entries)
        
        with col2:
            if 'Confidence' in filtered_df.columns:
                avg_confidence = filtered_df['Confidence'].mean()
                st.metric("Avg Confidence", f"{avg_confidence:.2%}" if not pd.isna(avg_confidence) else "N/A")
        
        with col3:
            if 'Liveness_Verified' in filtered_df.columns:
                liveness_rate = filtered_df['Liveness_Verified'].mean()
                st.metric("Liveness Rate", f"{liveness_rate:.1%}" if not pd.isna(liveness_rate) else "N/A")
        
    except Exception as e:
        st.error(f"Error loading attendance data: {e}")
        st.info("Make sure the attendance.csv file exists and has the correct format.")

def show_analytics():
    """Show analytics and charts"""
    st.header("📈 Analytics & Insights")
    
    try:
        # Load attendance data
        df = pd.read_csv("data/attendance.csv")
        
        # Remove comment rows
        df = df[~df['Name'].str.startswith('#', na=False)]
        
        if len(df) == 0:
            st.info("No attendance data available yet. Start using the system to see analytics.")
            return
        
        # Convert date and time columns
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
        
        # Create analytics tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Attendance Overview", "⏰ Time Analysis", "👥 User Performance", "🔍 Quality Metrics"])
        
        with tab1:
            st.subheader("Attendance Overview")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Daily attendance chart
                daily_attendance = df.groupby(df['Date'].dt.date).size().reset_index(name='Count')
                fig_daily = px.bar(daily_attendance, x='Date', y='Count', 
                                  title="Daily Attendance Count")
                st.plotly_chart(fig_daily, use_container_width=True)
            
            with col2:
                # Status distribution pie chart
                status_counts = df['Status'].value_counts()
                fig_status = px.pie(values=status_counts.values, names=status_counts.index, 
                                   title="Attendance Status Distribution")
                st.plotly_chart(fig_status, use_container_width=True)
        
        with tab2:
            st.subheader("Time Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Hourly distribution
                if 'Time' in df.columns:
                    df['Hour'] = df['Time'].dt.hour
                    hourly_counts = df['Hour'].value_counts().sort_index()
                    fig_hourly = px.bar(x=hourly_counts.index, y=hourly_counts.values,
                                       title="Attendance by Hour of Day")
                    st.plotly_chart(fig_hourly, use_container_width=True)
            
            with col2:
                # Weekly pattern
                if 'Date' in df.columns:
                    df['Weekday'] = df['Date'].dt.day_name()
                    weekday_counts = df['Weekday'].value_counts()
                    fig_weekday = px.bar(x=weekday_counts.index, y=weekday_counts.values,
                                        title="Attendance by Day of Week")
                    st.plotly_chart(fig_weekday, use_container_width=True)
        
        with tab3:
            st.subheader("User Performance")
            
            # User attendance summary
            user_summary = df.groupby('Name').agg({
                'Date': 'count',
                'Confidence': 'mean',
                'Liveness_Verified': 'mean'
            }).rename(columns={'Date': 'Attendance_Count', 'Confidence': 'Avg_Confidence'})
            
            st.dataframe(user_summary, use_container_width=True)
            
            # Top performers
            top_performers = user_summary.sort_values('Attendance_Count', ascending=False).head(5)
            
            fig_top = px.bar(top_performers, x=top_performers.index, y='Attendance_Count',
                            title="Top 5 Users by Attendance")
            st.plotly_chart(fig_top, use_container_width=True)
        
        with tab4:
            st.subheader("Quality Metrics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Confidence distribution
                if 'Confidence' in df.columns:
                    fig_conf = px.histogram(df, x='Confidence', nbins=20,
                                          title="Confidence Score Distribution")
                    st.plotly_chart(fig_conf, use_container_width=True)
            
            with col2:
                # Liveness verification rate over time
                if 'Liveness_Verified' in df.columns:
                    liveness_trend = df.groupby(df['Date'].dt.date)['Liveness_Verified'].mean()
                    fig_liveness = px.line(x=liveness_trend.index, y=liveness_trend.values,
                                          title="Liveness Verification Rate Over Time")
                    st.plotly_chart(fig_liveness, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error generating analytics: {e}")

def show_user_registration():
    """Show user registration form with quality assessment"""
    st.header("👤 User Registration")
    
    # Initialize systems
    if not initialize_systems():
        return
    
    # Registration form
    st.subheader("📝 New User Registration")
    
    with st.form("user_registration"):
        user_name = st.text_input("Full Name", placeholder="Enter user's full name")
        user_id = st.text_input("User ID", placeholder="Enter unique user ID")
        
        # Image upload
        uploaded_image = st.file_uploader("Upload User Photo", type=['jpg', 'jpeg', 'png'])
        
        # Webcam capture option
        use_webcam = st.checkbox("Use Webcam Instead")
        
        submitted = st.form_submit_button("Register User")
        
        if submitted:
            if not user_name or not user_id:
                st.error("Please provide both name and user ID.")
                return
            
            # Check if user already exists
            if user_id in st.session_state.face_db.users_db:
                st.error(f"User ID {user_id} already exists. Please use a different ID.")
                return
            
            # Process image
            image_to_process = None
            
            if use_webcam:
                st.info("Webcam capture will be implemented in the next phase.")
                return
            elif uploaded_image:
                try:
                    # Convert uploaded file to image
                    image_bytes = uploaded_image.read()
                    image_to_process = Image.open(io.BytesIO(image_bytes))
                    image_to_process = np.array(image_to_process)
                    
                    # Convert to BGR for OpenCV
                    if len(image_to_process.shape) == 3:
                        image_to_process = cv2.cvtColor(image_to_process, cv2.COLOR_RGB2BGR)
                    
                except Exception as e:
                    st.error(f"Error processing uploaded image: {e}")
                    return
            else:
                st.error("Please either upload an image or select webcam capture.")
                return
            
            # Quality assessment
            st.subheader("🔍 Image Quality Assessment")
            
            try:
                # Basic quality checks
                height, width = image_to_process.shape[:2]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Resolution", f"{width}x{height}")
                
                with col2:
                    brightness = np.mean(image_to_process)
                    st.metric("Brightness", f"{brightness:.1f}")
                
                with col3:
                    contrast = np.std(image_to_process)
                    st.metric("Contrast", f"{contrast:.1f}")
                
                # Quality score calculation
                quality_score = 0
                quality_factors = []
                
                # Resolution score
                if width >= 480 and height >= 480:
                    quality_score += 25
                    quality_factors.append("✅ Good resolution (480x480+)")
                else:
                    quality_factors.append("⚠️ Low resolution")
                
                # Brightness score
                if 50 <= brightness <= 200:
                    quality_score += 25
                    quality_factors.append("✅ Good brightness")
                else:
                    quality_factors.append("⚠️ Poor brightness")
                
                # Contrast score
                if contrast >= 30:
                    quality_score += 25
                    quality_factors.append("✅ Good contrast")
                else:
                    quality_factors.append("⚠️ Low contrast")
                
                # Face detection score
                try:
                    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    gray = cv2.cvtColor(image_to_process, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                    
                    if len(faces) > 0:
                        quality_score += 25
                        quality_factors.append("✅ Face detected")
                    else:
                        quality_factors.append("❌ No face detected")
                except:
                    quality_factors.append("⚠️ Face detection failed")
                
                # Display quality assessment
                st.subheader(f"Quality Score: {quality_score}/100")
                
                for factor in quality_factors:
                    st.write(factor)
                
                if quality_score >= 75:
                    st.success("🎉 Image quality is excellent for registration!")
                elif quality_score >= 50:
                    st.warning("⚠️ Image quality is acceptable but could be improved.")
                else:
                    st.error("❌ Image quality is too poor for registration. Please use a better image.")
                    return
                
                # Proceed with registration if quality is acceptable
                if quality_score >= 50:
                    try:
                        # Register user
                        success = st.session_state.face_db.register_user(
                            name=user_name,
                            user_id=user_id,
                            image=image_to_process
                        )
                        
                        if success:
                            st.success(f"✅ User {user_name} registered successfully!")
                            
                            # Update performance metrics
                            st.session_state.performance_metrics.append({
                                'timestamp': datetime.now(),
                                'processing_time': 0.5,  # Placeholder
                                'operation': 'user_registration',
                                'success': True
                            })
                            
                            # Clear form
                            st.rerun()
                        else:
                            st.error("Failed to register user. Please try again.")
                    
                    except Exception as e:
                        st.error(f"Error during registration: {e}")
                
            except Exception as e:
                st.error(f"Error during quality assessment: {e}")

def show_testing_suite():
    """Show enhanced testing suite with various image qualities"""
    st.header("🧪 Testing Suite")
    
    st.subheader("🔍 Image Quality Testing")
    
    # Test image upload
    test_image = st.file_uploader("Upload Test Image", type=['jpg', 'jpeg', 'png'], key="test_upload")
    
    if test_image:
        try:
            # Process test image
            image_bytes = test_image.read()
            test_img = Image.open(io.BytesIO(image_bytes))
            test_img_array = np.array(test_img)
            
            # Convert to BGR for OpenCV
            if len(test_img_array.shape) == 3:
                test_img_array = cv2.cvtColor(test_img_array, cv2.COLOR_RGB2BGR)
            
            # Display image
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Test Image")
                st.image(test_image, caption="Uploaded Test Image", use_column_width=True)
            
            with col2:
                st.subheader("Quality Analysis")
                
                # Basic metrics
                height, width = test_img_array.shape[:2]
                brightness = np.mean(test_img_array)
                contrast = np.std(test_img_array)
                
                st.metric("Resolution", f"{width}x{height}")
                st.metric("Brightness", f"{brightness:.1f}")
                st.metric("Contrast", f"{contrast:.1f}")
                
                # Advanced analysis
                st.subheader("Advanced Analysis")
                
                # Histogram
                if len(test_img_array.shape) == 3:
                    gray = cv2.cvtColor(test_img_array, cv2.COLOR_BGR2GRAY)
                else:
                    gray = test_img_array
                
                hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
                
                fig_hist = px.line(x=range(256), y=hist.flatten(), 
                                  title="Image Histogram")
                st.plotly_chart(fig_hist, use_container_width=True)
                
                # Face detection test
                st.subheader("Face Detection Test")
                
                try:
                    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                    
                    if len(faces) > 0:
                        st.success(f"✅ {len(faces)} face(s) detected")
                        
                        # Draw bounding boxes
                        test_img_with_boxes = test_img_array.copy()
                        for (x, y, w, h) in faces:
                            cv2.rectangle(test_img_with_boxes, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        
                        # Convert back to RGB for display
                        test_img_with_boxes_rgb = cv2.cvtColor(test_img_with_boxes, cv2.COLOR_BGR2RGB)
                        st.image(test_img_with_boxes_rgb, caption="Image with Face Detection", use_column_width=True)
                    else:
                        st.warning("⚠️ No faces detected in the image")
                
                except Exception as e:
                    st.error(f"Face detection failed: {e}")
        
        except Exception as e:
            st.error(f"Error processing test image: {e}")

def show_debug_tools():
    """Show debug logging and visualization tools"""
    st.header("🐛 Debug Tools")
    
    st.subheader("📊 Performance Metrics")
    
    if st.session_state.performance_metrics:
        df_debug = pd.DataFrame(st.session_state.performance_metrics)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Processing time over time
            fig_time = px.line(df_debug, x='timestamp', y='processing_time',
                              title="Processing Time Trends")
            st.plotly_chart(fig_time, use_container_width=True)
        
        with col2:
            # Success rate
            success_rate = df_debug['success'].mean() * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
            
            # Average processing time
            avg_time = df_debug['processing_time'].mean()
            st.metric("Avg Processing Time", f"{avg_time:.3f}s")
    
    st.subheader("📝 Debug Logs")
    
    # Add test log entry
    if st.button("Add Test Log Entry"):
        st.session_state.debug_logs.append({
            'timestamp': datetime.now(),
            'level': 'INFO',
            'message': 'Test log entry added',
            'module': 'dashboard'
        })
        st.rerun()
    
    # Display logs
    if st.session_state.debug_logs:
        for log in st.session_state.debug_logs[-10:]:  # Show last 10 logs
            timestamp = log['timestamp'].strftime("%H:%M:%S")
            level = log['level']
            message = log['message']
            module = log['module']
            
            if level == 'ERROR':
                st.error(f"[{timestamp}] {level} - {module}: {message}")
            elif level == 'WARNING':
                st.warning(f"[{timestamp}] {level} - {module}: {message}")
            else:
                st.info(f"[{timestamp}] {level} - {module}: {message}")
    else:
        st.info("No debug logs available yet.")

def main():
    """Main Streamlit dashboard"""
    st.title("👁️ EyeD - AI Attendance System")
    st.markdown("### Day 10: Basic Dashboard Skeleton with Enhanced Features")
    st.markdown("---")
    
    # Initialize session state
    if 'face_db' not in st.session_state:
        st.session_state.face_db = None
    if 'attendance_manager' not in st.session_state:
        st.session_state.attendance_manager = None
    if 'performance_metrics' not in st.session_state:
        st.session_state.performance_metrics = []
    if 'debug_logs' not in st.session_state:
        st.session_state.debug_logs = []
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Attendance Logs", "Analytics", "Register User", "Testing Suite", "Debug Tools"]
    )
    
    # Initialize systems
    if not initialize_systems():
        st.error("Failed to initialize required systems. Please check the installation.")
        return
    
    # Page routing
    if page == "Dashboard":
        show_dashboard()
    elif page == "Attendance Logs":
        show_attendance_logs()
    elif page == "Analytics":
        show_analytics()
    elif page == "Register User":
        show_user_registration()
    elif page == "Testing Suite":
        show_testing_suite()
    elif page == "Debug Tools":
        show_debug_tools()
    
    # Footer
    st.markdown("---")
    st.markdown("*EyeD - Making attendance smart, secure, and simple! 🚀*")
    
    # Add performance metric for page load
    if 'page_load_time' not in st.session_state:
        st.session_state.page_load_time = time.time()
        load_time = time.time() - st.session_state.page_load_time
        st.session_state.performance_metrics.append({
            'timestamp': datetime.now(),
            'processing_time': load_time,
            'operation': 'page_load',
            'success': True
        })

if __name__ == "__main__":
    main()
