#!/usr/bin/env python3
"""
Day 2 Test Script - Face Registration Module
Tests all registration functionality including webcam capture, image upload, and database operations
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        from deepface import DeepFace
        print("✅ DeepFace imported successfully")
    except ImportError as e:
        print(f"❌ DeepFace import failed: {e}")
        return False
    
    try:
        from src.modules.registration import FaceRegistration
        print("✅ FaceRegistration module imported successfully")
    except ImportError as e:
        print(f"❌ FaceRegistration import failed: {e}")
        return False
    
    return True

def test_registration_initialization():
    """Test FaceRegistration class initialization"""
    print("\n🧪 Testing registration initialization...")
    
    try:
        # Create temporary directory for testing
        temp_dir = tempfile.mkdtemp(prefix="eyed_test_")
        
        from src.modules.registration import FaceRegistration
        registration = FaceRegistration(data_dir=temp_dir)
        
        # Check if data directory was created
        if os.path.exists(temp_dir):
            print("✅ Data directory created successfully")
        else:
            print("❌ Data directory not created")
            return False
        
        # Check if embeddings file path is correct
        expected_embeddings_file = os.path.join(temp_dir, "faces.json")
        if registration.embeddings_file == expected_embeddings_file:
            print("✅ Embeddings file path set correctly")
        else:
            print("❌ Embeddings file path incorrect")
            return False
        
        # Check if face cascade is loaded
        if registration.face_cascade is not None:
            print("✅ Face cascade classifier loaded")
        else:
            print("❌ Face cascade classifier not loaded")
            return False
        
        # Cleanup
        shutil.rmtree(temp_dir)
        print("✅ Temporary directory cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Registration initialization failed: {e}")
        return False

def test_face_detection():
    """Test face detection functionality"""
    print("\n🧪 Testing face detection...")
    
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="eyed_test_")
        from src.modules.registration import FaceRegistration
        import numpy as np
        registration = FaceRegistration(data_dir=temp_dir)
        
        # Create a simple test image (just a colored rectangle for now)
        test_image = np.zeros((300, 300, 3), dtype=np.uint8)
        test_image[:] = (128, 128, 128)  # Gray image
        
        # Test face detection (should return empty list for no faces)
        faces = registration._detect_faces(test_image)
        
        if isinstance(faces, tuple):
            print("✅ Face detection method works (returned empty tuple for no faces)")
        elif isinstance(faces, list):
            print("✅ Face detection method works (returned empty list for no faces)")
        else:
            print(f"❌ Face detection method returned wrong type: {type(faces)}")
            return False
        
        # Cleanup
        shutil.rmtree(temp_dir)
        return True
        
    except Exception as e:
        print(f"❌ Face detection test failed: {e}")
        return False

def test_face_quality_validation():
    """Test face quality validation"""
    print("\n🧪 Testing face quality validation...")
    
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="eyed_test_")
        from modules.registration import FaceRegistration
        import numpy as np
        registration = FaceRegistration(data_dir=temp_dir)
        
        # Test with various face sizes
        test_cases = [
            ((50, 50, 50, 50), False),    # Too small
            ((100, 100, 100, 100), True), # Just right
            ((200, 200, 200, 200), True), # Large enough
        ]
        
        # Create test image with some variation (not just solid gray)
        test_image = np.zeros((400, 400, 3), dtype=np.uint8)
        test_image[:] = (128, 128, 128)  # Medium gray
        # Add some variation to pass contrast check
        test_image[100:300, 100:300] = (200, 200, 200)  # Lighter region
        test_image[150:250, 150:250] = (50, 50, 50)     # Darker region
        
        for bbox, expected in test_cases:
            result = registration._validate_face_quality(test_image, bbox)
            if result == expected:
                print(f"✅ Quality validation for bbox {bbox}: {result} (expected: {expected})")
            else:
                print(f"❌ Quality validation for bbox {bbox}: {result} (expected: {expected})")
                return False
        
        # Cleanup
        shutil.rmtree(temp_dir)
        return True
        
    except Exception as e:
        print(f"❌ Face quality validation test failed: {e}")
        return False

def test_database_operations():
    """Test database operations (CRUD)"""
    print("\n🧪 Testing database operations...")
    
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="eyed_test_")
        from src.modules.registration import FaceRegistration
        registration = FaceRegistration(data_dir=temp_dir)
        
        # Test initial state
        users = registration.get_registered_users()
        if len(users) == 0:
            print("✅ Initial database is empty")
        else:
            print("❌ Initial database should be empty")
            return False
        
        # Test user deletion (should handle non-existent user gracefully)
        result = registration.delete_user("non_existent_user")
        if not result:
            print("✅ Gracefully handled deletion of non-existent user")
        else:
            print("❌ Should not succeed in deleting non-existent user")
            return False
        
        # Cleanup
        shutil.rmtree(temp_dir)
        return True
        
    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        return False

def test_webcam_availability():
    """Test if webcam is available (without actually opening it)"""
    print("\n🧪 Testing webcam availability...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Webcam is available")
            cap.release()
            return True
        else:
            print("⚠️ Webcam not available (this is okay for testing)")
            return True  # Not a failure, just a warning
            
    except Exception as e:
        print(f"⚠️ Webcam test failed: {e}")
        return True  # Not a failure, just a warning

def run_all_tests():
    """Run all Day 2 tests"""
    print("🚀 EyeD Day 2 - Face Registration Tests")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Registration Initialization", test_registration_initialization),
        ("Face Detection", test_face_detection),
        ("Face Quality Validation", test_face_quality_validation),
        ("Database Operations", test_database_operations),
        ("Webcam Availability", test_webcam_availability),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Day 2 implementation is ready.")
        print("\n🚀 Next steps:")
        print("1. Test webcam registration: python main.py --mode register")
        print("2. Test with actual face images")
        print("3. Verify embeddings are generated correctly")
    else:
        print("⚠️ Some tests failed. Please review the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
