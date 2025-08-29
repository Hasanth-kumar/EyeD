#!/usr/bin/env python3
"""
Test script to verify all dependencies are working correctly
"""

def test_opencv():
    try:
        import cv2
        print("✅ OpenCV version:", cv2.__version__)
        return True
    except ImportError as e:
        print("❌ OpenCV import failed:", e)
        return False

def test_mediapipe():
    try:
        import mediapipe as mp
        print("✅ MediaPipe version:", mp.__version__)
        return True
    except ImportError as e:
        print("❌ MediaPipe import failed:", e)
        return False

def test_deepface():
    try:
        import deepface
        print("✅ DeepFace version:", deepface.__version__)
        return True
    except ImportError as e:
        print("❌ DeepFace import failed:", e)
        return False

def test_numpy():
    try:
        import numpy as np
        print("✅ NumPy version:", np.__version__)
        return True
    except ImportError as e:
        print("❌ NumPy import failed:", e)
        return False

def test_pandas():
    try:
        import pandas as pd
        print("✅ Pandas version:", pd.__version__)
        return True
    except ImportError as e:
        print("❌ Pandas import failed:", e)
        return False

def test_streamlit():
    try:
        import streamlit as st
        print("✅ Streamlit version:", st.__version__)
        return True
    except ImportError as e:
        print("❌ Streamlit import failed:", e)
        return False

def test_plotly():
    try:
        import plotly
        print("✅ Plotly version:", plotly.__version__)
        return True
    except ImportError as e:
        print("❌ Plotly import failed:", e)
        return False

def test_tensorflow():
    try:
        import tensorflow as tf
        print("✅ TensorFlow version:", tf.__version__)
        return True
    except ImportError as e:
        print("❌ TensorFlow import failed:", e)
        return False

def test_webcam_access():
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Webcam access: Available")
            cap.release()
            return True
        else:
            print("⚠️ Webcam access: Not available (no camera found)")
            return False
    except Exception as e:
        print("❌ Webcam access failed:", e)
        return False

def main():
    print("🧪 Testing Dependencies for EyeD AI Attendance System")
    print("=" * 60)
    
    tests = [
        ("OpenCV", test_opencv),
        ("MediaPipe", test_mediapipe),
        ("DeepFace", test_deepface),
        ("NumPy", test_numpy),
        ("Pandas", test_pandas),
        ("Streamlit", test_streamlit),
        ("Plotly", test_plotly),
        ("TensorFlow", test_tensorflow),
        ("Webcam Access", test_webcam_access)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n🔍 Testing {name}...")
        if test_func():
            passed += 1
        print("-" * 40)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All dependencies are working correctly!")
        print("✅ Ready to proceed with Day 1 implementation!")
    else:
        print("⚠️ Some dependencies have issues. Please resolve before proceeding.")
        print("💡 Check the error messages above for guidance.")

if __name__ == "__main__":
    main()
