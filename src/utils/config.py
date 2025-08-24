"""
Configuration settings for EyeD AI Attendance System
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
FACES_DIR = DATA_DIR / "faces"
ATTENDANCE_FILE = DATA_DIR / "attendance.csv"

# Model settings
FACE_RECOGNITION_MODEL = "MobileNet"  # DeepFace model
CONFIDENCE_THRESHOLD = 0.6  # Minimum confidence for recognition
LIVENESS_THRESHOLD = 0.2  # Eye aspect ratio threshold for blink detection

# Camera settings
CAMERA_ID = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30

# Streamlit settings
STREAMLIT_PORT = 8501
STREAMLIT_HOST = "localhost"

# Ensure directories exist
FACES_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
