#!/usr/bin/env python3
"""
Test Script for EyeD AI Attendance System
Tests the main components to ensure they work correctly
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_registration_system():
    """Test the face registration system"""
    print("🧪 Testing Face Registration System...")
    
    try:
        from src.modules.registration import FaceRegistration
        
        # Initialize registration system
        registration = FaceRegistration()
        print("✅ FaceRegistration initialized successfully")
        
        # Test database stats
        stats = registration.get_database_stats()
        print(f"📊 Database stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Registration system test failed: {e}")
        return False

def test_recognition_system():
    """Test the face recognition system"""
    print("\n🧪 Testing Face Recognition System...")
    
    try:
        from src.modules.recognition import FaceRecognition
        
        # Initialize recognition system
        recognition = FaceRecognition(confidence_threshold=0.6, use_mediapipe=True)
        print("✅ FaceRecognition initialized successfully")
        
        # Test loading known faces
        success = recognition.load_known_faces("data/faces")
        if success:
            print(f"✅ Loaded {len(recognition.known_faces)} known faces")
        else:
            print("⚠️ No known faces loaded (this is normal for a new system)")
        
        return True
        
    except Exception as e:
        print(f"❌ Recognition system test failed: {e}")
        return False

def test_liveness_system():
    """Test the liveness detection system"""
    print("\n🧪 Testing Liveness Detection System...")
    
    try:
        from src.modules.liveness import LivenessDetection
        
        # Initialize liveness system
        liveness = LivenessDetection()
        print("✅ LivenessDetection initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Liveness system test failed: {e}")
        return False

def test_attendance_system():
    """Test the attendance management system"""
    print("\n🧪 Testing Attendance Management System...")
    
    try:
        from src.modules.attendance import AttendanceManager
        
        # Initialize attendance system
        attendance = AttendanceManager()
        print("✅ AttendanceManager initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Attendance system test failed: {e}")
        return False

def test_database_files():
    """Test if required database files exist"""
    print("\n🧪 Testing Database Files...")
    
    try:
        # Check faces directory
        faces_dir = Path("data/faces")
        if faces_dir.exists():
            print(f"✅ Faces directory exists: {faces_dir}")
            
            # Check faces.json
            faces_json = faces_dir / "faces.json"
            if faces_json.exists():
                print(f"✅ Faces database exists: {faces_json}")
                
                # Try to read it
                import json
                with open(faces_json, 'r') as f:
                    data = json.load(f)
                    user_count = len(data.get('users', {}))
                    print(f"✅ Database readable with {user_count} users")
            else:
                print("⚠️ Faces database doesn't exist yet (normal for new system)")
        else:
            print("⚠️ Faces directory doesn't exist yet (normal for new system)")
        
        # Check attendance file
        attendance_file = Path("data/attendance.csv")
        if attendance_file.exists():
            print(f"✅ Attendance file exists: {attendance_file}")
        else:
            print("⚠️ Attendance file doesn't exist yet (normal for new system)")
        
        return True
        
    except Exception as e:
        print(f"❌ Database files test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 EyeD AI Attendance System - Component Tests")
    print("=" * 50)
    
    tests = [
        test_registration_system,
        test_recognition_system,
        test_liveness_system,
        test_attendance_system,
        test_database_files
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Run: python main.py --mode register")
        print("2. Run: streamlit run src/dashboard/app.py")
        print("3. Use the dashboard to register users and log attendance")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check if data/faces directory exists")
        print("3. Verify DeepFace and MediaPipe are properly installed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
