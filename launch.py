#!/usr/bin/env python3
"""
EyeD - Unified Launcher
Simple launcher script for EyeD AI Attendance System
"""

import sys
import subprocess
from pathlib import Path

def show_menu():
    """Display the main menu"""
    print("👁️ EyeD AI Attendance System")
    print("=" * 40)
    print("Choose your mode:")
    print("1. 🎥 Webcam Mode - Real-time face recognition")
    print("2. 📊 Dashboard Mode - Web interface")
    print("3. 👤 Registration Mode - Add new users")
    print("4. 🧪 Recognition Test - Test face recognition")
    print("5. 🔍 Liveness Test - Test liveness detection")
    print("6. 🔗 Integration Test - Test full system")
    print("7. 📋 Attendance Mode - Manage attendance")
    print("8. 🚪 Exit")
    print("=" * 40)

def run_mode(mode, **kwargs):
    """Run a specific mode using main.py"""
    try:
        cmd = [sys.executable, "main.py", "--mode", mode]
        
        # Add additional arguments
        if "camera" in kwargs:
            cmd.extend(["--camera", str(kwargs["camera"])])
        if "debug" in kwargs and kwargs["debug"]:
            cmd.append("--debug")
            
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {mode} mode: {e}")
    except KeyboardInterrupt:
        print(f"\n👋 {mode} mode stopped by user")

def main():
    """Main launcher function"""
    while True:
        show_menu()
        
        try:
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == "1":
                print("\n🎥 Starting Webcam Mode...")
                camera = input("Enter camera ID (default: 0): ").strip() or "0"
                debug = input("Enable debug mode? (y/n, default: n): ").strip().lower() == "y"
                run_mode("webcam", camera=int(camera), debug=debug)
                
            elif choice == "2":
                print("\n📊 Starting Dashboard Mode...")
                run_mode("dashboard")
                
            elif choice == "3":
                print("\n👤 Starting Registration Mode...")
                run_mode("register")
                
            elif choice == "4":
                print("\n🧪 Starting Recognition Test Mode...")
                run_mode("recognition")
                
            elif choice == "5":
                print("\n🔍 Starting Liveness Test Mode...")
                run_mode("liveness")
                
            elif choice == "6":
                print("\n🔗 Starting Integration Test Mode...")
                run_mode("integration")
                
            elif choice == "7":
                print("\n📋 Starting Attendance Mode...")
                run_mode("attendance")
                
            elif choice == "8":
                print("\n👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter a number between 1-8.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        if choice != "8":
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
