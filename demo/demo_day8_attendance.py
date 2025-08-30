#!/usr/bin/env python3
"""
Demo Script for Day 8: Attendance Logging System
Demonstrates the comprehensive attendance management system with liveness verification

This script showcases:
- Attendance session management
- Liveness verification integration
- Analytics and transparency features
- Performance monitoring
"""

import sys
import time
import cv2
import numpy as np
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from modules.attendance import AttendanceManager
from modules.face_db import FaceDatabase
from utils.logger import logger

def print_banner():
    """Print demo banner"""
    print("=" * 80)
    print("👁️ EyeD - AI Attendance System Demo")
    print("📅 Day 8: Comprehensive Attendance Logging with Liveness Verification")
    print("=" * 80)
    print()

def print_menu():
    """Print demo menu"""
    print("🎯 Available Demo Options:")
    print("1. 📝 Start Attendance Session")
    print("2. 🔍 Process Attendance Frame")
    print("3. 📊 View Attendance Analytics")
    print("4. 🔍 Generate Transparency Report")
    print("5. 📈 View Performance Statistics")
    print("6. ⚙️  Update Configuration")
    print("7. 🧪 Run Test Suite")
    print("8. 🚪 Exit Demo")
    print()

def demo_attendance_session(attendance_manager):
    """Demo attendance session management"""
    print("📝 Attendance Session Management Demo")
    print("-" * 50)
    
    # Start a new session
    print("🔄 Starting new attendance session...")
    session_id = attendance_manager.start_attendance_session(
        user_id="demo_user_001",
        user_name="Demo User",
        device_info="Demo Webcam",
        location="Demo Office"
    )
    print(f"✅ Session started: {session_id}")
    
    # Show session details
    if session_id in attendance_manager.active_sessions:
        session = attendance_manager.active_sessions[session_id]
        print(f"   User: {session.user_name} ({session.user_id})")
        print(f"   Device: {session.device_info}")
        print(f"   Location: {session.location}")
        print(f"   Status: {session.status}")
        print(f"   Start Time: {session.start_time}")
    
    return session_id

def demo_frame_processing(attendance_manager, session_id):
    """Demo frame processing for attendance"""
    print("\n🔍 Frame Processing Demo")
    print("-" * 50)
    
    if session_id not in attendance_manager.active_sessions:
        print("❌ No active session found. Please start a session first.")
        return
    
    # Create a mock frame (in real usage, this would come from webcam)
    print("📷 Creating mock video frame...")
    mock_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    print(f"   Frame shape: {mock_frame.shape}")
    print(f"   Frame data type: {mock_frame.dtype}")
    
    # Process the frame
    print("🔄 Processing frame for attendance verification...")
    result = attendance_manager.process_attendance_frame(mock_frame, session_id)
    
    # Display results
    print("📊 Frame Processing Results:")
    print(f"   Success: {result['success']}")
    if result['success']:
        print(f"   Verification Success: {result.get('verification_success', False)}")
        print(f"   Attendance Logged: {result.get('attendance_logged', False)}")
        print(f"   User Name: {result.get('user_name', 'Unknown')}")
        print(f"   Confidence: {result.get('confidence', 0.0):.3f}")
        print(f"   Liveness Verified: {result.get('liveness_verified', False)}")
        print(f"   Face Quality Score: {result.get('face_quality_score', 0.0):.1f}")
        print(f"   Processing Time: {result.get('processing_time_ms', 0.0):.1f}ms")
        print(f"   Verification Stage: {result.get('verification_stage', 'Unknown')}")
        
        if 'message' in result:
            print(f"   Message: {result['message']}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
        if 'error_message' in result:
            print(f"   Error Details: {result['error_message']}")

def demo_analytics(attendance_manager):
    """Demo attendance analytics"""
    print("\n📊 Attendance Analytics Demo")
    print("-" * 50)
    
    # Get analytics
    analytics = attendance_manager.get_attendance_analytics()
    
    if 'error' in analytics:
        print(f"❌ Analytics Error: {analytics['error']}")
        return
    
    print("📈 Attendance Analytics:")
    print(f"   Total Entries: {analytics['total_entries']}")
    print(f"   Unique Users: {analytics['unique_users']}")
    print(f"   Success Rate: {analytics['success_rate']:.1f}%")
    print(f"   Average Confidence: {analytics['avg_confidence']:.3f}")
    print(f"   Liveness Verification Rate: {analytics['liveness_verification_rate']:.1f}%")
    
    # Quality metrics
    if 'quality_metrics' in analytics and analytics['quality_metrics']:
        quality = analytics['quality_metrics']
        if 'confidence_distribution' in quality:
            dist = quality['confidence_distribution']
            print("\n🎯 Confidence Distribution:")
            print(f"   High (≥0.8): {dist.get('high', 0)}")
            print(f"   Medium (0.6-0.8): {dist.get('medium', 0)}")
            print(f"   Low (<0.6): {dist.get('low', 0)}")
    
    # Performance metrics
    if 'performance_metrics' in analytics:
        perf = analytics['performance_metrics']
        print("\n⚡ Performance Metrics:")
        print(f"   Total Attendance Logs: {perf.get('total_attendance_logs', 0)}")
        print(f"   Successful Logs: {perf.get('successful_logs', 0)}")
        print(f"   Liveness Verifications: {perf.get('liveness_verifications', 0)}")
        print(f"   Average Processing Time: {perf.get('avg_processing_time_ms', 0.0):.1f}ms")
        print(f"   Active Sessions: {perf.get('active_sessions', 0)}")

def demo_transparency_report(attendance_manager, session_id):
    """Demo transparency report generation"""
    print("\n🔍 Transparency Report Demo")
    print("-" * 50)
    
    if session_id not in attendance_manager.active_sessions:
        print("❌ No active session found. Please start a session first.")
        return
    
    # Generate transparency report
    print("📋 Generating transparency report...")
    report = attendance_manager.get_transparency_report(session_id)
    
    if 'error' in report:
        print(f"❌ Report Error: {report['error']}")
        return
    
    print("📊 Transparency Report:")
    
    # Session information
    if 'session_info' in report:
        session_info = report['session_info']
        print("\n📝 Session Information:")
        print(f"   Session ID: {session_info['session_id']}")
        print(f"   User ID: {session_info['user_id']}")
        print(f"   User Name: {session_info['user_name']}")
        print(f"   Start Time: {session_info['start_time']}")
        print(f"   End Time: {session_info['end_time'] or 'Not ended'}")
        print(f"   Status: {session_info['status']}")
        print(f"   Device: {session_info['device_info']}")
        print(f"   Location: {session_info['location']}")
    
    # Verification details
    if 'verification_details' in report:
        verification = report['verification_details']
        print("\n🔐 Verification Details:")
        print(f"   Confidence: {verification['confidence']:.3f}")
        print(f"   Liveness Verified: {verification['liveness_verified']}")
        print(f"   Face Quality Score: {verification['face_quality_score']:.1f}")
        print(f"   Processing Time: {verification['processing_time_ms']:.1f}ms")
        print(f"   Verification Stage: {verification['verification_stage']}")
    
    # Quality assessment
    if 'quality_assessment' in report:
        quality = report['quality_assessment']
        print("\n✅ Quality Assessment:")
        print(f"   Meets Confidence Threshold: {quality['meets_confidence_threshold']}")
        print(f"   Meets Quality Threshold: {quality['meets_quality_threshold']}")
        print(f"   Meets Performance Threshold: {quality['meets_performance_threshold']}")
    
    # System metrics
    if 'system_metrics' in report:
        system = report['system_metrics']
        print("\n🖥️ System Metrics:")
        print(f"   Total Verifications: {system['total_verifications']}")
        print(f"   Success Rate: {system['success_rate']:.1f}%")
        print(f"   Average Processing Time: {system['avg_processing_time']:.1f}ms")

def demo_performance_stats(attendance_manager):
    """Demo performance statistics"""
    print("\n📈 Performance Statistics Demo")
    print("-" * 50)
    
    # Get performance stats
    stats = attendance_manager.get_performance_stats()
    
    print("⚡ Performance Statistics:")
    print(f"   Total Attendance Logs: {stats['total_attendance_logs']}")
    print(f"   Successful Logs: {stats['successful_logs']}")
    print(f"   Success Rate: {stats['success_rate']:.1f}%")
    print(f"   Liveness Verifications: {stats['liveness_verifications']}")
    print(f"   Liveness Rate: {stats['liveness_rate']:.1f}%")
    print(f"   Average Processing Time: {stats['avg_processing_time_ms']:.1f}ms")
    print(f"   Active Sessions: {stats['active_sessions']}")
    print(f"   Total Sessions: {stats['total_sessions']}")

def demo_config_update(attendance_manager):
    """Demo configuration updates"""
    print("\n⚙️ Configuration Update Demo")
    print("-" * 50)
    
    print("Current Configuration:")
    print(f"   Confidence Threshold: {attendance_manager.confidence_threshold}")
    print(f"   Max Daily Entries: {attendance_manager.max_daily_entries}")
    print(f"   Enable Liveness: {attendance_manager.enable_liveness}")
    print(f"   Enable Analytics: {attendance_manager.enable_analytics}")
    print(f"   Enable Transparency: {attendance_manager.enable_transparency}")
    
    # Update configuration
    print("\n🔄 Updating configuration...")
    success = attendance_manager.update_config({
        'confidence_threshold': 0.75,
        'max_daily_entries': 4
    })
    
    if success:
        print("✅ Configuration updated successfully!")
        print("\nUpdated Configuration:")
        print(f"   Confidence Threshold: {attendance_manager.confidence_threshold}")
        print(f"   Max Daily Entries: {attendance_manager.max_daily_entries}")
    else:
        print("❌ Failed to update configuration")

def run_test_suite():
    """Run the test suite"""
    print("\n🧪 Running Test Suite...")
    print("-" * 50)
    
    try:
        # Import and run tests
        from src.tests.test_day8_attendance import run_attendance_tests
        success = run_attendance_tests()
        return success
    except ImportError as e:
        print(f"❌ Could not import test module: {e}")
        print("   Make sure you're running from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        return False

def main():
    """Main demo function"""
    print_banner()
    
    # Initialize attendance manager
    print("🚀 Initializing Attendance Manager...")
    try:
        attendance_manager = AttendanceManager(
            enable_liveness=False,  # Disable for demo to avoid dependency issues
            confidence_threshold=0.6,
            max_daily_entries=3,
            enable_analytics=True,
            enable_transparency=True
        )
        print("✅ Attendance Manager initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize Attendance Manager: {e}")
        print("   This might be due to missing dependencies or configuration issues")
        return
    
    print()
    
    # Demo state
    current_session_id = None
    
    while True:
        print_menu()
        
        try:
            choice = input("🎯 Enter your choice (1-8): ").strip()
            
            if choice == "1":
                current_session_id = demo_attendance_session(attendance_manager)
                
            elif choice == "2":
                if current_session_id:
                    demo_frame_processing(attendance_manager, current_session_id)
                else:
                    print("❌ Please start an attendance session first (option 1)")
                    
            elif choice == "3":
                demo_analytics(attendance_manager)
                
            elif choice == "4":
                if current_session_id:
                    demo_transparency_report(attendance_manager, current_session_id)
                else:
                    print("❌ Please start an attendance session first (option 1)")
                    
            elif choice == "5":
                demo_performance_stats(attendance_manager)
                
            elif choice == "6":
                demo_config_update(attendance_manager)
                
            elif choice == "7":
                success = run_test_suite()
                if success:
                    print("\n✅ All tests passed!")
                else:
                    print("\n❌ Some tests failed!")
                    
            elif choice == "8":
                print("\n👋 Thank you for using the EyeD Attendance System Demo!")
                print("🚀 Phase 3 implementation complete!")
                break
                
            else:
                print("❌ Invalid choice. Please enter a number between 1 and 8.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            logger.error(f"Demo error: {e}")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
