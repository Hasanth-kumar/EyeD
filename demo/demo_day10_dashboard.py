#!/usr/bin/env python3
"""
Demo Script for Day 10: Basic Dashboard Skeleton
EyeD AI Attendance System

This script demonstrates the Day 10 dashboard features:
- Dashboard metrics and performance monitoring
- Attendance logs with filtering
- Analytics and charts
- User registration with quality assessment
- Testing suite for image quality
- Debug tools and logging
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def create_sample_attendance_data():
    """Create sample attendance data for testing the dashboard"""
    print("📊 Creating sample attendance data...")
    
    # Sample users
    users = [
        {"name": "Alice Johnson", "id": "U001"},
        {"name": "Bob Smith", "id": "U002"},
        {"name": "Carol Davis", "id": "U003"},
        {"name": "David Wilson", "id": "U004"},
        {"name": "Eva Brown", "id": "U005"}
    ]
    
    # Generate sample attendance data for the past 7 days
    attendance_data = []
    base_date = datetime.now() - timedelta(days=7)
    
    for day in range(8):  # 8 days including today
        current_date = base_date + timedelta(days=day)
        date_str = current_date.strftime("%Y-%m-%d")
        
        for user in users:
            # Random attendance pattern
            if np.random.random() > 0.1:  # 90% attendance rate
                # Random arrival time between 8 AM and 10 AM
                hour = np.random.randint(8, 11)
                minute = np.random.randint(0, 60)
                time_str = current_date.replace(hour=hour, minute=minute).strftime("%H:%M:%S")
                
                # Random confidence and quality scores
                confidence = np.random.uniform(0.7, 0.95)
                face_quality = np.random.uniform(0.6, 0.9)
                processing_time = np.random.uniform(50, 200)
                
                # Status based on arrival time
                if hour == 8:
                    status = "Present"
                elif hour == 9:
                    status = "Present"
                else:
                    status = "Late"
                
                # Liveness verification (95% success rate)
                liveness_verified = np.random.random() > 0.05
                
                attendance_data.append({
                    "Name": user["name"],
                    "ID": user["id"],
                    "Date": date_str,
                    "Time": time_str,
                    "Status": status,
                    "Confidence": round(confidence, 3),
                    "Liveness_Verified": liveness_verified,
                    "Face_Quality_Score": round(face_quality, 3),
                    "Processing_Time_MS": round(processing_time, 1),
                    "Verification_Stage": "Completed",
                    "Session_ID": f"S{day:03d}_{user['id']}",
                    "Device_Info": "Demo System",
                    "Location": "Demo Office"
                })
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(attendance_data)
    
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Save to CSV
    csv_path = data_dir / "attendance.csv"
    df.to_csv(csv_path, index=False)
    
    print(f"✅ Created {len(df)} attendance records")
    print(f"📁 Saved to: {csv_path}")
    
    return df

def create_sample_face_database():
    """Create sample face database entries"""
    print("👤 Creating sample face database...")
    
    # Sample user data
    sample_users = {
        "user_001": {
            "name": "Alice Johnson",
            "user_id": "U001",
            "registration_date": "2025-01-15",
            "last_updated": "2025-01-15",
            "image_path": "data/faces/user_001.jpg",
            "embedding": [0.1] * 128,  # Placeholder embedding
            "metadata": {
                "age": 28,
                "department": "Engineering",
                "role": "Software Developer"
            }
        },
        "user_002": {
            "name": "Bob Smith",
            "user_id": "U002",
            "registration_date": "2025-01-16",
            "last_updated": "2025-01-16",
            "image_path": "data/faces/user_002.jpg",
            "embedding": [0.2] * 128,  # Placeholder embedding
            "metadata": {
                "age": 32,
                "department": "Marketing",
                "role": "Marketing Manager"
            }
        },
        "user_003": {
            "name": "Carol Davis",
            "user_id": "U003",
            "registration_date": "2025-01-17",
            "last_updated": "2025-01-17",
            "image_path": "data/faces/user_003.jpg",
            "embedding": [0.3] * 128,  # Placeholder embedding
            "metadata": {
                "age": 25,
                "department": "HR",
                "role": "HR Specialist"
            }
        }
    }
    
    # Create faces directory if it doesn't exist
    faces_dir = Path("data/faces")
    faces_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample faces.json
    faces_data = {
        "users": sample_users,
        "embeddings": {},
        "metadata": {
            "created": datetime.now().isoformat(),
            "version": "1.0",
            "total_users": len(sample_users)
        }
    }
    
    # Save faces.json
    faces_json_path = faces_dir / "faces.json"
    with open(faces_json_path, 'w') as f:
        json.dump(faces_data, f, indent=2)
    
    print(f"✅ Created face database with {len(sample_users)} users")
    print(f"📁 Saved to: {faces_json_path}")
    
    return sample_users

def test_dashboard_imports():
    """Test if all dashboard dependencies can be imported"""
    print("🔍 Testing dashboard imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ PIL imported successfully")
    except ImportError as e:
        print(f"❌ PIL import failed: {e}")
        return False
    
    try:
        from src.dashboard.app import main
        print("✅ Dashboard app imported successfully")
    except ImportError as e:
        print(f"❌ Dashboard app import failed: {e}")
        return False
    
    return True

def test_dashboard_functionality():
    """Test basic dashboard functionality"""
    print("🧪 Testing dashboard functionality...")
    
    try:
        # Test dashboard metrics calculation
        from src.dashboard.app import get_dashboard_metrics
        
        # Mock session state
        class MockSessionState:
            def __init__(self):
                self.face_db = None
                self.attendance_manager = None
        
        # Test with empty data
        metrics = get_dashboard_metrics()
        print(f"✅ Dashboard metrics calculated: {metrics}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard functionality test failed: {e}")
        return False

def run_dashboard():
    """Run the Streamlit dashboard"""
    print("🚀 Starting Streamlit dashboard...")
    print("📱 The dashboard will open in your browser")
    print("🔗 If it doesn't open automatically, go to: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the dashboard")
    print()
    
    try:
        import subprocess
        import sys
        
        # Run streamlit app
        cmd = [sys.executable, "-m", "streamlit", "run", "src/dashboard/app.py"]
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")
        print("💡 Try running manually: streamlit run src/dashboard/app.py")

def main():
    """Main demo function"""
    print("👁️ EyeD AI Attendance System - Day 10 Demo")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("src/dashboard/app.py").exists():
        print("❌ Error: Please run this script from the EyeD project root directory")
        return
    
    # Test imports
    if not test_dashboard_imports():
        print("❌ Import tests failed. Please install required dependencies:")
        print("pip install streamlit plotly opencv-python pillow")
        return
    
    # Create sample data
    print("\n📊 Setting up sample data...")
    create_sample_attendance_data()
    create_sample_face_database()
    
    # Test functionality
    print("\n🧪 Testing dashboard functionality...")
    if not test_dashboard_functionality():
        print("❌ Functionality tests failed")
        return
    
    print("\n✅ All tests passed! Dashboard is ready to run.")
    
    # Ask user if they want to run the dashboard
    print("\n" + "=" * 50)
    print("🎯 Day 10 Dashboard Features Implemented:")
    print("✅ Basic Dashboard Skeleton with sidebar menu")
    print("✅ Enhanced testing suite with various image qualities")
    print("✅ Debug logging and visualization tools")
    print("✅ Performance monitoring dashboard")
    print("✅ Quality assessment tools")
    print("✅ Real-time metrics and analytics")
    print("✅ User registration with quality assessment")
    print("✅ Attendance logs with filtering")
    print("✅ Interactive charts and visualizations")
    
    print("\n🚀 Ready to launch dashboard!")
    print("Choose an option:")
    print("1. Run dashboard now")
    print("2. Exit")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
        run_dashboard()
    else:
        print("👋 Goodbye! You can run the dashboard later with:")
        print("streamlit run src/dashboard/app.py")

if __name__ == "__main__":
    main()
