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
        try:
            from modules.registration import FaceRegistration
            registration = FaceRegistration()
            
            print("\n🧩 Face Registration System")
            print("=" * 30)
            print("1. Register new user (webcam)")
            print("2. Register from image file")
            print("3. List registered users")
            print("4. Delete user")
            print("5. Exit")
            
            while True:
                choice = input("\nEnter your choice (1-5): ").strip()
                
                if choice == "1":
                    name = input("Enter user name: ").strip()
                    if name:
                        success = registration.capture_face(name)
                        if success:
                            print(f"✅ User {name} registered successfully!")
                        else:
                            print(f"❌ Failed to register user {name}")
                
                elif choice == "2":
                    image_path = input("Enter image file path: ").strip()
                    name = input("Enter user name: ").strip()
                    if image_path and name:
                        success = registration.register_from_image(image_path, name)
                        if success:
                            print(f"✅ User {name} registered successfully from image!")
                        else:
                            print(f"❌ Failed to register user {name} from image")
                
                elif choice == "3":
                    try:
                        users = registration.get_registered_users()
                        if users:
                            print("\nRegistered Users:")
                            for user_id, name in users.items():
                                print(f"  {user_id}: {name}")
                        else:
                            print("No users registered yet.")
                    except Exception as e:
                        print(f"❌ Error listing users: {e}")
                
                elif choice == "4":
                    try:
                        user_id = input("Enter user ID to delete: ").strip()
                        if user_id:
                            success = registration.delete_user(user_id)
                            if success:
                                print(f"✅ User {user_id} deleted successfully!")
                            else:
                                print(f"❌ Failed to delete user {user_id}")
                    except Exception as e:
                        print(f"❌ Error deleting user: {e}")
                
                elif choice == "5":
                    print("👋 Returning to main menu...")
                    break
                
                else:
                    print("Invalid choice. Please try again.")
                    
        except ImportError as e:
            print(f"❌ Failed to import registration module: {e}")
        except Exception as e:
            print(f"❌ Registration error: {e}")
    
    print("\n✅ EyeD system initialized successfully!")
    print("💡 Use --help for more options")

if __name__ == "__main__":
    main()
