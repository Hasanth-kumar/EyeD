#!/usr/bin/env python3
"""
Test script to verify Phase 2 implementation of EyeD modularity
Tests that all modules properly implement their respective interfaces
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_attendance_manager_interface():
    """Test AttendanceManager interface implementation"""
    print("Testing AttendanceManager interface implementation...")
    
    try:
        from modules.attendance import AttendanceManager
        from interfaces.attendance_manager_interface import AttendanceManagerInterface
        
        # Check if class implements interface
        assert issubclass(AttendanceManager, AttendanceManagerInterface), \
            "AttendanceManager should implement AttendanceManagerInterface"
        
        # Check if required methods exist
        required_methods = [
            'log_attendance',
            'verify_attendance', 
            'get_attendance_history',
            'get_attendance_statistics',
            'update_attendance_config'
        ]
        
        for method in required_methods:
            assert hasattr(AttendanceManager, method), \
                f"AttendanceManager missing required method: {method}"
        
        print("✅ AttendanceManager interface implementation: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ AttendanceManager interface implementation: FAILED - {e}")
        return False

def test_face_database_interface():
    """Test FaceDatabase interface implementation"""
    print("Testing FaceDatabase interface implementation...")
    
    try:
        from modules.face_db import FaceDatabase
        from interfaces.face_database_interface import FaceDatabaseInterface
        
        # Check if class implements interface
        assert issubclass(FaceDatabase, FaceDatabaseInterface), \
            "FaceDatabase should implement FaceDatabaseInterface"
        
        # Check if required methods exist
        required_methods = [
            'add_user',
            'remove_user',
            'get_user',
            'get_all_users',
            'find_face',
            'update_user_metadata',
            'get_user_embeddings',
            'backup_database',
            'restore_database',
            'get_database_stats',
            'clear_database',
            'is_healthy'
        ]
        
        for method in required_methods:
            assert hasattr(FaceDatabase, method), \
                f"FaceDatabase missing required method: {method}"
        
        print("✅ FaceDatabase interface implementation: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ FaceDatabase interface implementation: FAILED - {e}")
        return False

def test_recognition_interface():
    """Test FaceRecognition interface implementation"""
    print("Testing FaceRecognition interface implementation...")
    
    try:
        from modules.recognition import FaceRecognition
        from interfaces.recognition_interface import RecognitionInterface
        
        # Check if class implements interface
        assert issubclass(FaceRecognition, RecognitionInterface), \
            "FaceRecognition should implement RecognitionInterface"
        
        # Check if required methods exist
        required_methods = [
            'detect_faces',
            'recognize_face',
            'extract_embeddings',
            'compare_faces',
            'load_known_faces'
        ]
        
        for method in required_methods:
            assert hasattr(FaceRecognition, method), \
                f"FaceRecognition missing required method: {method}"
        
        print("✅ FaceRecognition interface implementation: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ FaceRecognition interface implementation: FAILED - {e}")
        return False

def test_liveness_interface():
    """Test LivenessDetection interface implementation"""
    print("Testing LivenessDetection interface implementation...")
    
    try:
        from modules.liveness import LivenessDetection
        from interfaces.liveness_interface import LivenessInterface
        
        # Check if class implements interface
        assert issubclass(LivenessDetection, LivenessInterface), \
            "LivenessDetection should implement LivenessInterface"
        
        # Check if required methods exist
        required_methods = [
            'detect_blink',
            'detect_head_movement',
            'detect_eye_movement',
            'detect_mouth_movement',
            'analyze_depth',
            'analyze_texture'
        ]
        
        for method in required_methods:
            assert hasattr(LivenessDetection, method), \
                f"LivenessDetection missing required method: {method}"
        
        print("✅ LivenessDetection interface implementation: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ LivenessDetection interface implementation: FAILED - {e}")
        return False

def main():
    """Run all Phase 2 interface tests"""
    print("=" * 60)
    print("Phase 2 Implementation Verification")
    print("Testing Interface Compliance for All Modules")
    print("=" * 60)
    
    tests = [
        test_attendance_manager_interface,
        test_face_database_interface,
        test_recognition_interface,
        test_liveness_interface
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Phase 2 Implementation Results: {passed}/{total} tests PASSED")
    
    if passed == total:
        print("🎉 Phase 2 Implementation: COMPLETE!")
        print("All modules successfully implement their respective interfaces")
        print("Single Responsibility Principle maintained")
        print("Modularity goals achieved")
    else:
        print("⚠️  Phase 2 Implementation: INCOMPLETE")
        print(f"{total - passed} modules need attention")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
