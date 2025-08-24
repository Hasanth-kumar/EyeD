#!/usr/bin/env python3
"""
EyeD - AI Attendance System with Liveness Detection
Main entry point for the application

Author: EyeD Team
Date: 2025
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

def main():
    """Main entry point for EyeD application"""
    parser = argparse.ArgumentParser(description="EyeD AI Attendance System")
    parser.add_argument("--mode", choices=["webcam", "dashboard", "register"], 
                       default="webcam", help="Application mode")
    parser.add_argument("--camera", type=int, default=0, help="Camera device ID")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    print("👁️ EyeD - AI Attendance System")
    print("=" * 40)
    
    if args.mode == "webcam":
        print("🎥 Starting webcam mode...")
        # TODO: Import and run webcam recognition
        print("⚠️ Webcam mode not yet implemented (Day 5)")
        
    elif args.mode == "dashboard":
        print("📊 Starting Streamlit dashboard...")
        # TODO: Launch Streamlit app
        print("⚠️ Dashboard mode not yet implemented (Day 10)")
        
    elif args.mode == "register":
        print("📝 Starting user registration...")
        # TODO: Import and run registration
        print("⚠️ Registration mode not yet implemented (Day 2)")
    
    print("\n✅ EyeD system initialized successfully!")
    print("💡 Use --help for more options")

if __name__ == "__main__":
    main()
