"""
Basic tests for Day 1 setup verification
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

def test_project_structure():
    """Test that the project structure is correctly set up"""
    print("🔍 Testing project structure...")
    
    # Check main directories exist
    required_dirs = [
        "src",
        "src/modules", 
        "src/utils",
        "src/dashboard",
        "src/tests",
        "data",
        "data/faces",
        "docs"
    ]
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path} exists")
        else:
            print(f"❌ {dir_path} missing")
            return False
    
    return True

def test_imports():
    """Test that basic imports work"""
    print("\n🔍 Testing imports...")
    
    try:
        from src.utils.config import PROJECT_ROOT, DATA_DIR, FACES_DIR
        print("✅ Config imports work")
        
        from src.utils.logger import logger
        print("✅ Logger imports work")
        
        from src.utils.database import attendance_db
        print("✅ Database imports work")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_dependencies():
    """Test that all dependencies are available"""
    print("\n🔍 Testing dependencies...")
    
    try:
        import cv2
        print(f"✅ OpenCV: {cv2.__version__}")
        
        import mediapipe as mp
        print(f"✅ MediaPipe: {mp.__version__}")
        
        import deepface
        print(f"✅ DeepFace: {deepface.__version__}")
        
        import numpy as np
        print(f"✅ NumPy: {np.__version__}")
        
        import pandas as pd
        print(f"✅ Pandas: {pd.__version__}")
        
        import streamlit as st
        print(f"✅ Streamlit: {st.__version__}")
        
        import plotly
        print(f"✅ Plotly: {plotly.__version__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Dependency import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Day 1 Setup Verification Tests")
    print("=" * 50)
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Basic Imports", test_imports),
        ("Dependencies", test_dependencies)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Day 1 setup is complete and working!")
        print("✅ Ready to proceed to Day 2: Face Registration")
    else:
        print("⚠️ Some tests failed. Please fix issues before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    main()
