"""
Test file for interfaces to ensure they can be imported correctly
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

def test_interface_imports():
    """Test that all interfaces can be imported correctly"""
    try:
        from src.interfaces import (
            FaceDatabaseInterface,
            AttendanceManagerInterface,
            RecognitionInterface,
            LivenessInterface,
            AnalyticsInterface
        )
        print("✅ All interfaces imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import interfaces: {e}")
        return False

def test_interface_abstract_methods():
    """Test that interfaces have the expected abstract methods"""
    try:
        from src.interfaces import (
            FaceDatabaseInterface,
            AttendanceManagerInterface,
            RecognitionInterface,
            LivenessInterface,
            AnalyticsInterface
        )
        
        # Check that interfaces have expected methods
        expected_methods = {
            FaceDatabaseInterface: ['add_user', 'remove_user', 'get_user', 'find_face'],
            AttendanceManagerInterface: ['log_attendance', 'verify_attendance', 'get_attendance_history'],
            RecognitionInterface: ['detect_faces', 'recognize_face', 'extract_embeddings'],
            LivenessInterface: ['detect_blink', 'detect_head_movement', 'run_comprehensive_test'],
            AnalyticsInterface: ['get_attendance_trends', 'get_user_performance', 'get_system_metrics']
        }
        
        for interface_class, methods in expected_methods.items():
            for method in methods:
                if not hasattr(interface_class, method):
                    print(f"❌ {interface_class.__name__} missing method: {method}")
                    return False
        
        print("✅ All interfaces have expected abstract methods")
        return True
        
    except Exception as e:
        print(f"❌ Error testing interface methods: {e}")
        return False

if __name__ == "__main__":
    print("Testing EyeD Project Interfaces...")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_interface_imports()
    
    if imports_ok:
        # Test abstract methods
        methods_ok = test_interface_abstract_methods()
        
        if methods_ok:
            print("\n🎉 All interface tests passed!")
        else:
            print("\n❌ Interface method tests failed!")
    else:
        print("\n❌ Interface import tests failed!")
    
    print("=" * 50)
