"""
Daily Attendance Page - EyeD AI Attendance System
Implements real-time face recognition with liveness detection
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time
from datetime import datetime, date
import pandas as pd
from pathlib import Path
import threading
import queue

# Page configuration
st.set_page_config(
    page_title="Daily Attendance - EyeD",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set current page in session state for navigation highlighting
st.session_state.current_page = "daily_attendance"

# Hide the top navigation bar
st.markdown("""
<style>
    /* Hide the top navigation bar completely */
    .stApp > header {
        display: none !important;
    }
    
    /* Hide the hamburger menu button */
    .stApp > div[data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* Professional spacing */
    .stApp > div[data-testid="stAppViewContainer"] {
        padding-top: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

def initialize_systems():
    """Initialize face recognition, liveness detection, and attendance systems"""
    try:
        from src.modules.recognition import FaceRecognition
        from src.modules.liveness import EnhancedLivenessDetection
        from src.modules.attendance import AttendanceManager
        
        # Initialize systems
        recognition = FaceRecognition(confidence_threshold=0.1, use_mediapipe=True)
        liveness = EnhancedLivenessDetection(min_blinks=2, blink_timeout=15.0)
        attendance_manager = AttendanceManager()
        
        # Load known faces
        if not recognition.load_known_faces("data/faces"):
            st.warning("⚠️ No known faces loaded. Please register users first.")
            st.info("Go to the Registration page to add new users.")
            return None, None, None
        
        st.success("✅ Face recognition and liveness detection systems initialized")
        return recognition, liveness, attendance_manager
        
    except Exception as e:
        st.error(f"Failed to initialize systems: {e}")
        return None, None, None

def initialize_session_state():
    """Initialize session state variables for attendance tracking"""
    if 'attendance_logged_today' not in st.session_state:
        st.session_state.attendance_logged_today = set()
    
    if 'current_date' not in st.session_state:
        st.session_state.current_date = date.today().isoformat()
    
    # Check if date changed
    current_date = date.today().isoformat()
    if current_date != st.session_state.current_date:
        st.session_state.attendance_logged_today.clear()
        st.session_state.current_date = current_date

def show_attendance_mode_selection():
    """Show attendance mode selection interface"""
    col1, col2 = st.columns(2)
    
    with col1:
        attendance_mode = st.selectbox(
            "Attendance Mode",
            ["Real-Time Webcam", "Image Upload"],
            help="Choose attendance capture method"
        )
    
    with col2:
        confidence_threshold = st.slider(
            "Recognition Confidence",
            min_value=0.05,
            max_value=0.95,
            value=0.1,
            step=0.05,
            help="Minimum confidence required for face recognition"
        )
    
    return attendance_mode, confidence_threshold

def show_real_time_interface(recognition, liveness, attendance_manager, confidence_threshold):
    """Show real-time webcam attendance interface"""
    st.info("📱 **Real-Time Mode**: Position your face in the camera for attendance")
    
    # Start real-time attendance capture
    if st.button("🚀 Start Real-Time Attendance", key="start_real_time_btn", type="primary"):
        initialize_real_time_session()
        st.session_state.webcam_active = True  # Automatically start camera
        st.rerun()
    
    # Show stop button if session is active
    if st.session_state.get('real_time_session_active', False):
        if st.button("⏹️ Stop Real-Time Session", key="stop_real_time_btn", type="secondary"):
            stop_real_time_session()
            st.rerun()

def show_image_upload_interface(recognition, liveness, attendance_manager, confidence_threshold):
    """Show image upload attendance interface"""
    st.info("📁 **Upload Mode**: Upload a face image for attendance processing")
    
    uploaded_file = st.file_uploader(
        "Upload face image",
        type=['jpg', 'jpeg', 'png'],
        help="Upload a clear face image for attendance"
    )
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        
        if st.button("🚀 Process Attendance", key="process_limited_btn", type="primary"):
            process_uploaded_image(
                face_image=uploaded_file,
                recognition=recognition,
                liveness=liveness,
                attendance_manager=attendance_manager,
                confidence_threshold=confidence_threshold
            )

def initialize_real_time_session():
    """Initialize session state for real-time attendance session"""
    if 'real_time_session_active' not in st.session_state:
        st.session_state.real_time_session_active = False
    if 'webcam_cap' not in st.session_state:
        st.session_state.webcam_cap = None
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = None
    if 'real_time_step' not in st.session_state:
        st.session_state.real_time_step = 'face_detection'
    if 'face_detected' not in st.session_state:
        st.session_state.face_detected = False
    if 'user_recognized' not in st.session_state:
        st.session_state.user_recognized = None
    if 'liveness_result' not in st.session_state:
        st.session_state.liveness_result = None
    if 'attendance_logged' not in st.session_state:
        st.session_state.attendance_logged = False
    if 'captured_frame' not in st.session_state:
        st.session_state.captured_frame = None
    if 'webcam_active' not in st.session_state:
        st.session_state.webcam_active = False
    if 'attendance_logged_today' not in st.session_state:
        st.session_state.attendance_logged_today = set()
    if 'current_date' not in st.session_state:
        st.session_state.current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Start the session
    st.session_state.real_time_session_active = True
    st.session_state.session_start_time = time.time()
    st.session_state.real_time_step = 'face_detection'
    st.session_state.face_detected = False
    st.session_state.user_recognized = None
    st.session_state.liveness_result = None
    st.session_state.attendance_logged = False
    st.session_state.captured_frame = None
    st.session_state.webcam_active = True

def stop_real_time_session():
    """Stop the real-time attendance session"""
    st.session_state.real_time_session_active = False
    if st.session_state.get('webcam_cap'):
        st.session_state.webcam_cap.release()
        st.session_state.webcam_cap = None

def show_daily_attendance():
    """Show daily attendance interface with real-time webcam and liveness detection"""
    st.markdown("**Real-time face recognition for attendance tracking**")
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize systems
    recognition, liveness, attendance_manager = initialize_systems()
    if not all([recognition, liveness, attendance_manager]):
        return
    
    # Show attendance mode selection
    attendance_mode, confidence_threshold = show_attendance_mode_selection()
    
    # Show appropriate interface based on mode
    if attendance_mode == "Real-Time Webcam":
        show_real_time_interface(recognition, liveness, attendance_manager, confidence_threshold)
    else:
        show_image_upload_interface(recognition, liveness, attendance_manager, confidence_threshold)
    
    # Show today's attendance summary
    show_attendance_summary()
    
    # Show recent attendance logs
    show_recent_attendance()
    
    # Show real-time session if active
    if st.session_state.get('real_time_session_active', False):
        show_real_time_session(
            recognition=recognition,
            liveness=liveness,
            attendance_manager=attendance_manager,
            confidence_threshold=confidence_threshold
        )

def initialize_webcam():
    """Initialize webcam for real-time attendance"""
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("❌ Failed to open webcam. Please check camera permissions.")
            return None
        
        # Set webcam properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        st.success("✅ Webcam initialized successfully")
        return cap
        
    except Exception as e:
        st.error(f"❌ Webcam initialization error: {str(e)}")
        return None

def handle_face_detection_step(recognition, confidence_threshold):
    """Handle Step 1: Face Detection - Single Responsibility: Face Detection Only"""
    st.info("🔍 **Step 1**: Face Detection - Position your face in the live camera")
    
    # Show live camera feed
    st.info("📹 **Live Camera Active** - Position your face clearly")
    
    # Create camera placeholder
    camera_placeholder = st.empty()
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("❌ Failed to open webcam")
        st.session_state.webcam_active = False
        return False
    
    try:
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Process live feed
        frame_count = 0
        face_detected_frames = 0  # Count consecutive frames with face
        required_frames = 10  # Need 10 consecutive frames to confirm detection
        
        while st.session_state.webcam_active and st.session_state.real_time_step == 'face_detection':
            ret, frame = cap.read()
            if not ret:
                st.error("❌ Failed to read from camera")
                break
            
            frame_count += 1
            
            # Process every 3rd frame for better responsiveness
            if frame_count % 3 == 0:
                # Perform face detection
                detection_result = recognition.detect_faces(frame)
                
                if detection_result and detection_result.face_locations:
                    # Draw face detection box
                    for (x, y, w, h) in detection_result.face_locations:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(frame, f"Face Detected! ({face_detected_frames}/{required_frames})", (x, y-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    face_detected_frames += 1
                    
                    # Only proceed after stable detection
                    if face_detected_frames >= required_frames:
                        # Show success message
                        st.success("✅ **Face Detected!** Moving to recognition step...")
                        
                        # Store frame and proceed
                        st.session_state.captured_frame = frame.copy()
                        st.session_state.face_detected = True
                        st.session_state.real_time_step = 'face_recognition'
                        
                        # Release camera
                        cap.release()
                        st.session_state.webcam_active = False
                        st.rerun()
                        return True
                else:
                    # Reset face detection counter if no face
                    face_detected_frames = 0
                    
                    # Draw instructions on frame
                    cv2.putText(frame, "Position your face in the camera", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    cv2.putText(frame, "Looking for faces...", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Display frame
            camera_placeholder.image(frame, channels="BGR", use_container_width=True)
            
            # Add delay to slow down detection
            time.sleep(0.1)  # Slower than 30 FPS for better user experience
                
    finally:
        # Release camera if loop ends
        if cap.isOpened():
            cap.release()
    
    return False

def handle_face_recognition_step(recognition, confidence_threshold):
    """Handle Step 2: Face Recognition - Single Responsibility: Recognition Only"""
    st.info("👤 **Step 2**: Face Recognition - Processing detected face...")
    
    # Debug: Show what we have
    st.write("🔍 **Debug Info:**")
    st.write(f"Face Detected: {st.session_state.face_detected}")
    st.write(f"Captured Frame: {st.session_state.captured_frame is not None}")
    
    # Use the detected face for recognition
    if not st.session_state.face_detected or st.session_state.captured_frame is None:
        st.error("❌ No face detected. Please go back to detection step.")
        st.session_state.real_time_step = 'face_detection'
        st.rerun()
        return False
    
    # Show the detected face
    st.image(st.session_state.captured_frame, caption="Detected Face", use_container_width=True)
    
    st.info("🔄 Processing face recognition...")
    
    # Perform recognition on the detected frame
    recognition_results = recognition.recognize_user(st.session_state.captured_frame)
    
    # Debug: Show recognition results
    st.write(f"Recognition Results: {len(recognition_results) if recognition_results else 0}")
    if recognition_results:
        st.write(f"First Result: {recognition_results[0]}")
    
    if not recognition_results:
        st.error("❌ No faces detected. Please try again.")
        st.session_state.real_time_step = 'face_detection'
        st.rerun()
        return False
    
    # Find the best match
    best_match = None
    for result in recognition_results:
        if result['recognized'] and result['confidence'] >= confidence_threshold:
            if best_match is None or result['confidence'] > best_match['confidence']:
                best_match = result
    
    if best_match:
        st.success(f"✅ **Face Recognized**: {best_match['name']} (Confidence: {best_match['confidence']:.1%})")
        st.session_state.user_recognized = best_match
        st.session_state.real_time_step = 'liveness_verification'
        st.rerun()
        return True
    else:
        st.error("❌ Face not recognized. Please try again.")
        st.session_state.real_time_step = 'face_detection'
        st.rerun()
        return False

def handle_liveness_verification_step(liveness):
    """Handle Step 3**: Liveness Verification - Single Responsibility: Liveness Only"""
    st.info("👁️ **Step 3**: Liveness Verification - Blink naturally in live camera")
    
    # Debug: Show what we have
    st.write("🔍 **Debug Info:**")
    st.write(f"User Recognized: {st.session_state.user_recognized}")
    st.write(f"Webcam Active: {st.session_state.webcam_active}")
    
    if not st.session_state.user_recognized:
        st.error("❌ No user recognized. Please go back to recognition step.")
        st.session_state.real_time_step = 'face_recognition'
        st.rerun()
        return False
    
    # Ensure webcam is active for liveness verification
    st.session_state.webcam_active = True
    
    # Show live liveness camera
    st.info("👁️ **Live Liveness Check** - Blink naturally to verify")
    
    # User guidance for liveness verification
    st.info("💡 **Tip**: Look directly at the camera and blink naturally")
    
    # Create camera placeholder
    liveness_placeholder = st.empty()
    
    # Initialize webcam for liveness
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("❌ Failed to open webcam for liveness check")
        st.session_state.webcam_active = False
        return False
    
    try:
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Process live liveness detection
        st.info("🎥 **Starting camera loop for liveness detection...**")
        frame_count = 0
        liveness_start_time = time.time()
        blink_detected_frames = 0
        required_blinks = 3  # Need 3 blinks to confirm liveness
        max_wait_time = 45.0  # Maximum time to wait for liveness verification
        
        while st.session_state.webcam_active and st.session_state.real_time_step == 'liveness_verification':
            ret, frame = cap.read()
            if not ret:
                st.error("❌ Failed to read from camera")
                break
            
            frame_count += 1
            elapsed_time = time.time() - liveness_start_time
            
            # Check timeout - if taking too long, restart the process
            if elapsed_time > max_wait_time:
                st.warning("⏰ **Timeout**: Liveness verification taking too long. Please ensure good lighting and look directly at the camera.")
                st.info("🔄 Restarting liveness verification...")
                time.sleep(2)  # Give user time to read the message
                st.session_state.real_time_step = 'face_recognition'
                cap.release()
                st.session_state.webcam_active = False
                st.rerun()
                return False
            
            # Process every 3rd frame for liveness
            if frame_count % 3 == 0:
                try:
                    # Perform liveness detection
                    liveness_result = liveness.detect_blink_sequence(frame, timeout=10.0)
                    
                    if liveness_result.is_live:
                        blink_detected_frames += 1
                        
                        # Show progress
                        cv2.putText(frame, f"Blink Detected! ({blink_detected_frames}/{required_blinks})", (10, 90), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        # Only proceed after multiple blinks
                        if blink_detected_frames >= required_blinks:
                            # Show success message
                            st.success("✅ **Liveness Verified**: Natural blinking detected!")
                            
                            # Store result and proceed
                            st.session_state.liveness_result = liveness_result
                            st.session_state.real_time_step = 'attendance_logging'
                            
                            # Release camera
                            cap.release()
                            st.session_state.webcam_active = False
                            st.rerun()
                            return True
                    else:
                        # Show liveness status
                        elapsed_time = time.time() - liveness_start_time
                        cv2.putText(frame, f"Liveness Check: {elapsed_time:.1f}s", (10, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                        cv2.putText(frame, "Blink naturally...", (10, 60), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                        cv2.putText(frame, f"Blinks: {blink_detected_frames}/{required_blinks}", (10, 90), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                        
                except Exception as e:
                    st.error(f"❌ Liveness detection error: {e}")
                    cv2.putText(frame, f"Error: {str(e)[:50]}...", (10, 150), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Display frame
            liveness_placeholder.image(frame, channels="BGR", use_container_width=True)
            
            # Add delay for better user experience
            time.sleep(0.1)
                
    finally:
        # Release camera if loop ends
        if cap.isOpened():
            cap.release()
    
    return False

def handle_attendance_logging_step(attendance_manager):
    """Handle Step 4: Attendance Logging - Single Responsibility: Attendance Only"""
    st.info("📝 **Step 4**: Attendance Logging - Finalizing attendance record...")
    
    # Debug: Show what we have
    st.write("🔍 **Debug Info:**")
    st.write(f"User Recognized: {st.session_state.user_recognized}")
    if st.session_state.user_recognized:
        st.write(f"User Name: {st.session_state.user_recognized.get('name', 'N/A')}")
        st.write(f"User Confidence: {st.session_state.user_recognized.get('confidence', 'N/A')}")
        st.write(f"User Recognized: {st.session_state.user_recognized.get('recognized', 'N/A')}")
    st.write(f"Liveness Result: {st.session_state.liveness_result}")
    if st.session_state.liveness_result:
        st.write(f"Liveness is_live: {st.session_state.liveness_result.is_live}")
        st.write(f"Liveness confidence: {st.session_state.liveness_result.confidence}")
        st.write(f"Liveness blink_count: {st.session_state.liveness_result.blink_count}")
    
    if not st.session_state.user_recognized or not st.session_state.liveness_result:
        st.error("❌ Missing recognition or liveness verification data")
        st.session_state.real_time_step = 'face_recognition'
        st.rerun()
        return False
    
    # Get confidence and liveness info
    user_confidence = st.session_state.user_recognized.get('confidence', 0.0)
    liveness_verified = st.session_state.liveness_result.is_live
    face_quality_score = st.session_state.liveness_result.confidence
    
    # Log attendance with all the verification data
    attendance_entry = attendance_manager.log_attendance(
        face_image=st.session_state.captured_frame,
        user_id=st.session_state.user_recognized.get('user_id'),
        device_info="webcam",
        location="office",
        confidence=user_confidence,
        liveness_verified=liveness_verified,
        face_quality_score=face_quality_score,
        verification_stage="completed"
    )
    # Add manual test button for debugging
    if st.button("🧪 Test Attendance Logging", key="test_attendance_btn"):
        st.write("Testing attendance logging...")
        # Create a dummy user for testing
        test_user = {
            'name': 'Test User',
            'confidence': 0.95,
            'id': 'test123'
        }
        test_liveness = type('obj', (object,), {
            'is_live': True,
            'blink_count': 3,
            'face_quality_score': 0.9
        })()
        
        test_result = log_attendance(test_user, test_liveness, attendance_manager, st.empty())
        st.write(f"Test result: {test_result}")
        return False
    
    # Check attendance entry result
    if attendance_entry:
        st.success(f"""🎉 **Attendance Logged Successfully!**
        - User: {st.session_state.user_recognized.get('name', 'N/A')}
        - Confidence: {user_confidence:.2%}
        - Liveness Verified: {'✅' if liveness_verified else '❌'}
        - Face Quality Score: {face_quality_score:.2%}
        """)
        st.session_state.attendance_logged = True
        st.session_state.real_time_step = 'completed'
        st.rerun()
        return True
    else:
        st.error("❌ **Attendance Logging Failed** - Please try again")
        st.session_state.real_time_step = 'face_detection'
        st.rerun()
        return False

def handle_completion_step():
    """Handle Step 5: Completion - Single Responsibility: UI Summary Only"""
    st.success("🎉 **Real-Time Attendance Session Completed Successfully!**")
    
    # Show detailed summary
    if st.session_state.user_recognized and st.session_state.liveness_result:
        user_confidence = st.session_state.user_recognized.get('confidence', 0.0)
        liveness_verified = st.session_state.liveness_result.is_live
        face_quality_score = st.session_state.liveness_result.confidence
        
        st.info(f"""
        **User:** {st.session_state.user_recognized.get('name', 'N/A')}  
        **Confidence:** {user_confidence:.2%}  
        **Liveness:** {'✅ Verified' if liveness_verified else '❌ Not Verified'}  
        **Face Quality:** {face_quality_score:.2%}  
        **Status:** ✅ Present  
        **Time:** {datetime.now().strftime('%I:%M %p')}
        """)
    
    # Reset session
    if st.button("🔄 Start New Session", key="new_session_btn"):
        reset_session_state()
        st.rerun()
    
    # Return to main menu
    if st.button("🏠 Return to Main Menu", key="return_main_btn"):
        st.session_state.real_time_session_active = False
        st.session_state.webcam_active = False
        st.rerun()

def reset_session_state():
    """Reset all session state variables - Single Responsibility: State Management Only"""
    st.session_state.real_time_step = 'face_detection'
    st.session_state.face_detected = False
    st.session_state.user_recognized = None
    st.session_state.liveness_result = None
    st.session_state.attendance_logged = False
    st.session_state.captured_frame = None
    st.session_state.liveness_frame = None
    st.session_state.webcam_active = False

def show_real_time_session(recognition, liveness, attendance_manager, confidence_threshold):
    """Main coordinator function - Single Responsibility: Orchestration Only"""
    st.subheader("🎬 Real-Time Attendance Session")
    
    # Initialize session state for real-time processing
    if 'real_time_step' not in st.session_state:
        st.session_state.real_time_step = 'face_detection'
    if 'face_detected' not in st.session_state:
        st.session_state.face_detected = False
    if 'user_recognized' not in st.session_state:
        st.session_state.user_recognized = None
    if 'liveness_result' not in st.session_state:
        st.session_state.liveness_result = None
    if 'attendance_logged' not in st.session_state:
        st.session_state.attendance_logged = False
    if 'captured_frame' not in st.session_state:
        st.session_state.captured_frame = None
    if 'liveness_frame' not in st.session_state:
        st.session_state.liveness_frame = None
    if 'webcam_active' not in st.session_state:
        st.session_state.webcam_active = False
    
    # Show current step status
    st.info(f"🔄 **Current Step**: {st.session_state.real_time_step.replace('_', ' ').title()}")
    
    # Add stop button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("⏹️ Stop Session", key="stop_session_btn"):
            st.session_state.real_time_session_active = False
            st.session_state.webcam_active = False
            st.rerun()
    
    # Route to appropriate step handler based on current state
    step_handlers = {
        'face_detection': lambda: handle_face_detection_step(recognition, confidence_threshold),
        'face_recognition': lambda: handle_face_recognition_step(recognition, confidence_threshold),
        'liveness_verification': lambda: handle_liveness_verification_step(liveness),
        'attendance_logging': lambda: handle_attendance_logging_step(attendance_manager),
        'completed': lambda: handle_completion_step()
    }
    
    current_step = st.session_state.real_time_step
    if current_step in step_handlers:
        step_handlers[current_step]()
    else:
        st.error(f"❌ Unknown step: {current_step}")
        reset_session_state()
        st.rerun()

def log_attendance(user_recognized, liveness_result, attendance_manager, status_placeholder):
    """Log attendance for recognized user"""
    status_placeholder.info("📝 **Step 4**: Logging attendance...")
    
    # Debug: Show what we're actually logging - Store in session state for persistence
    debug_info = {
        'user_recognized': user_recognized,
        'liveness_result': {
            'is_live': liveness_result.is_live if hasattr(liveness_result, 'is_live') else 'N/A',
            'confidence': liveness_result.confidence if hasattr(liveness_result, 'confidence') else 'N/A',
            'blink_count': liveness_result.blink_count if hasattr(liveness_result, 'blink_count') else 'N/A',
            'blink_duration': liveness_result.blink_duration if hasattr(liveness_result, 'blink_duration') else 'N/A',
            'motion_score': liveness_result.motion_score if hasattr(liveness_result, 'motion_score') else 'N/A'
        },
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Store debug info in session state
    st.session_state.last_debug_info = debug_info
    
    # Also store the step we're in for debugging
    st.session_state.current_attendance_step = "debug_info_captured"
    
    # Display debug info
    st.write("🔍 **Debug - Attendance Logging (Persistent):**")
    st.write(f"**User Recognized:** {user_recognized}")
    st.write(f"**User Name:** {user_recognized.get('name', 'N/A')}")
    st.write(f"**User Confidence:** {user_recognized.get('confidence', 'N/A')}")
    st.write(f"**User ID:** {user_recognized.get('user_id', 'N/A')}")
    st.write(f"**Liveness Result:** {liveness_result}")
    
    # Show detailed liveness info
    if hasattr(liveness_result, 'is_live'):
        st.write(f"**Liveness is_live:** {liveness_result.is_live}")
        st.write(f"**Liveness confidence:** {liveness_result.confidence}")
        st.write(f"**Blink count:** {liveness_result.blink_count}")
        st.write(f"**Motion score:** {liveness_result.motion_score}")
    else:
        st.write("⚠️ **Liveness result object missing expected attributes**")
        st.write(f"**Available attributes:** {dir(liveness_result)}")
    
    # Check if already logged today
    attendance_key = f"{st.session_state.current_date}_{user_recognized['name']}"
    if attendance_key in st.session_state.attendance_logged_today:
        status_placeholder.warning("⚠️ **Already Logged**: You have already logged attendance today")
        st.session_state.current_attendance_step = "already_logged_today"
        return False
    
    st.session_state.current_attendance_step = "checking_duplicate_passed"
    
    # Log attendance
    # Create a dummy image since we don't have the frame here
    import numpy as np
    dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Extract confidence value
    confidence = user_recognized.get('confidence', 0.0)
    st.write(f"Extracted Confidence: {confidence}")
    st.session_state.current_attendance_step = "confidence_extracted"
    
    # Try with new interface first, fallback to old interface if needed
    st.session_state.current_attendance_step = "attempting_attendance_logging"
    st.write("🔄 **Attempting to log attendance...**")
    
    try:
        st.write(f"📝 **Calling attendance_manager.log_attendance with:**")
        st.write(f"- Image: {type(dummy_image)}")
        st.write(f"- Name: {user_recognized['name']}")
        st.write(f"- Device: Real-Time Webcam")
        st.write(f"- Location: Main Office")
        st.write(f"- Confidence: {confidence}")
        st.write(f"- Liveness Verified: {liveness_result.is_live}")
        st.write(f"- Face Quality Score: {liveness_result.confidence}")
        st.write(f"- Verification Stage: completed")
        
        # Use keyword arguments to ensure correct parameter mapping
        success = attendance_manager.log_attendance(
            face_image=dummy_image,
            user_id=user_recognized['name'],
            device_info="Real-Time Webcam",
            location="Main Office",
            confidence=confidence,
            liveness_verified=liveness_result.is_live,
            face_quality_score=liveness_result.confidence,
            verification_stage="completed"
        )
        
        st.write(f"✅ **Attendance logging result:** {success}")
        
    except Exception as e:
        st.write(f"❌ **Error in attendance logging:** {e}")
        st.write(f"**Error type:** {type(e).__name__}")
        st.session_state.current_attendance_step = f"error_in_attendance_logging: {type(e).__name__}"
        success = False
    
    if success:
        # Add to session state
        st.session_state.attendance_logged_today.add(attendance_key)
        st.session_state.current_attendance_step = "attendance_logged_successfully"
        
        # Show success message
        current_time = datetime.now().strftime("%H:%M:%S")
        status_placeholder.success(f"""
        🎉 **Attendance Logged Successfully!**
        
        **User:** {user_recognized['name']}  
        **Time:** {current_time}  
        **Confidence:** {user_recognized['confidence']:.1%}  
        **Liveness:** ✅ Verified (Blink Count: {liveness_result.blink_count})  
        **Security:** ✅ Verified  
        **Status:** Present
        """)
        
        # Show next steps
        st.info("""
        **Next Steps:**
        1. Your attendance has been recorded
        2. Check the Attendance page to view your records
        3. Analytics will be updated automatically
        """)
        
        return True
    else:
        st.session_state.current_attendance_step = "attendance_logging_failed"
        status_placeholder.error("❌ **Attendance Logging Failed**: Could not save attendance record")
        return False

def process_uploaded_image(face_image, recognition, liveness, attendance_manager, confidence_threshold):
    """Process uploaded image for attendance"""
    with st.spinner("🔄 Processing uploaded image..."):
        try:
            # Convert image to numpy array
            if hasattr(face_image, 'read'):
                img = Image.open(face_image)
                face_array = np.array(img)
            else:
                face_array = face_image
            
            # Step 1: Face Recognition
            st.info("🔍 **Step 1**: Performing face recognition...")
            
            recognition_results = recognition.recognize_user(face_array)
            
            if not recognition_results:
                st.error("❌ No faces detected in the image")
                return
            
            # Find the best match
            best_match = None
            for result in recognition_results:
                if result['recognized'] and result['confidence'] >= confidence_threshold:
                    if best_match is None or result['confidence'] > best_match['confidence']:
                        best_match = result
            
            if not best_match:
                st.error("❌ Face not recognized or confidence too low")
                st.info(f"Best confidence: {max([r['confidence'] for r in recognition_results]):.1%}")
                return
            
            username = best_match['name']
            confidence = best_match['confidence']
            
            st.success(f"✅ **Face Recognized**: {username} (Confidence: {confidence:.1%})")
            
            # Step 2: Basic Liveness Check (Limited)
            st.warning("⚠️ **Limited Liveness Check**: Single image analysis has reduced security verification")
            
            # Perform basic liveness detection
            liveness_result = liveness.detect_blink(frame=face_array)
            
            if not liveness_result.is_live:
                st.error("❌ **Basic Liveness Check Failed**")
                st.info("For better security, use the Real-Time Webcam mode")
                return
            
            st.success("✅ **Basic Liveness Verified**: Image appears to be from a real person")
            
            # Step 3: Attendance Logging
            st.info("📝 **Step 3**: Logging attendance...")
            
            # Check if already logged today
            attendance_key = f"{st.session_state.current_date}_{username}"
            if attendance_key in st.session_state.attendance_logged_today:
                st.warning("⚠️ **Already Logged**: You have already logged attendance today")
                return
            
            # Log attendance
            success = attendance_manager.log_attendance(
                face_image=face_array,
                user_id=username,
                device_info="Image Upload (Limited)",
                location="Main Office",
                confidence=confidence,
                liveness_verified=liveness_result.is_live,
                face_quality_score=liveness_result.confidence,
                verification_stage="basic_check"
            )
            
            if success:
                # Add to session state
                st.session_state.attendance_logged_today.add(attendance_key)
                
                # Show success message
                current_time = datetime.now().strftime("%H:%M:%S")
                st.success(f"""
                🎉 **Attendance Logged Successfully!**
                
                **User:** {username}  
                **Time:** {current_time}  
                **Confidence:** {confidence:.1%}  
                **Liveness:** ⚠️ Basic Check Passed  
                **Security:** ⚠️ Limited Protection  
                **Status:** Present
                """)
                
                st.warning("""
                **Security Note**: Image upload mode has limited security verification.
                For maximum security, use the Real-Time Webcam mode.
                """)
                
            else:
                st.error("❌ **Attendance Logging Failed**: Could not save attendance record")
                
        except Exception as e:
            st.error(f"❌ **Processing Error**: {str(e)}")
            st.info("Please try again or contact support if the issue persists")

def show_attendance_summary():
    """Show today's attendance summary"""
    st.subheader("📊 Today's Attendance Summary")
    
    try:
        # Load attendance data
        attendance_file = Path("data/attendance.csv")
        if attendance_file.exists():
            df = pd.read_csv(attendance_file)
            
            # Filter today's attendance
            today = date.today().strftime("%Y-%m-%d")
            today_df = df[df['Date'] == today]
            
            if not today_df.empty:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_today = len(today_df)
                    st.metric("Total Today", total_today)
                
                with col2:
                    present_today = len(today_df[today_df['Status'] == 'Present'])
                    st.metric("Present", present_today)
                
                with col3:
                    late_today = len(today_df[today_df['Status'] == 'Late'])
                    st.metric("Late", late_today)
                
                with col4:
                    attendance_rate = (present_today / total_today * 100) if total_today > 0 else 0
                    st.metric("Attendance Rate", f"{attendance_rate:.1f}%")
                
                # Show today's attendees
                st.subheader("👥 Today's Attendees")
                today_display = today_df[['Name', 'Time', 'Status', 'Confidence', 'Liveness_Verified']].copy()
                today_display['Time'] = pd.to_datetime(today_display['Time']).dt.strftime('%H:%M:%S')
                today_display['Confidence'] = today_display['Confidence'].apply(lambda x: f"{float(x):.1%}" if pd.notna(x) and x is not None else "N/A")
                today_display['Liveness_Verified'] = today_display['Liveness_Verified'].apply(lambda x: "✅" if x == True else "❌" if x == False else "❓")
                
                st.dataframe(today_display, use_container_width=True)
                
            else:
                st.info("No attendance records for today yet.")
        else:
            st.info("No attendance data available.")
            
    except Exception as e:
        st.error(f"Error loading attendance summary: {e}")

def show_recent_attendance():
    """Show recent attendance logs"""
    st.subheader("📋 Recent Attendance Logs")
    
    try:
        # Load attendance data
        attendance_file = Path("data/attendance.csv")
        if attendance_file.exists():
            df = pd.read_csv(attendance_file)
            
            # Show last 10 entries
            recent_df = df.tail(10)[['Name', 'Date', 'Time', 'Status', 'Confidence', 'Liveness_Verified']].copy()
            recent_df['Time'] = pd.to_datetime(recent_df['Time']).dt.strftime('%H:%M:%S')
            recent_df['Confidence'] = recent_df['Confidence'].apply(lambda x: f"{float(x):.1%}" if pd.notna(x) and x is not None else "N/A")
            recent_df['Liveness_Verified'] = recent_df['Liveness_Verified'].apply(lambda x: "✅" if x == True else "❌" if x == False else "❓")
            
            st.dataframe(recent_df, use_container_width=True)
            
            # Download option
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Full Attendance Data",
                data=csv,
                file_name=f"attendance_data_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No attendance data available.")
            
    except Exception as e:
        st.error(f"Error loading recent attendance: {e}")

# Page configuration
st.set_page_config(
    page_title="Daily Attendance - EyeD",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide the top navigation bar
st.markdown("""
<style>
    /* Professional top navigation bar styling */
    .stApp > header {
        background: linear-gradient(90deg, #1f77b4, #17a2b8) !important;
        border-bottom: 2px solid #0d6efd !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    /* Style the hamburger menu button */
    .stApp > div[data-testid="stToolbar"] {
        background: transparent !important;
    }
    
    /* Style the header content */
    .stApp > header > div {
        background: transparent !important;
    }
    
    /* Professional header text */
    .stApp > header h1 {
        color: white !important;
        font-weight: bold !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
    }
    
    /* Style the hamburger menu icon */
    .stApp > div[data-testid="stToolbar"] button {
        color: white !important;
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 6px !important;
    }
    
    /* Hover effects for buttons */
    .stApp > div[data-testid="stToolbar"] button:hover {
        background: rgba(255,255,255,0.2) !important;
        transform: translateY(-1px) !important;
        transition: all 0.2s ease !important;
    }
    
    /* Professional spacing */
    .stApp > div[data-testid="stAppViewContainer"] {
        padding-top: 1rem !important;
    }
    
    /* Add subtle shadow to main content */
    .main .block-container {
        box-shadow: 0 0 10px rgba(0,0,0,0.05) !important;
        border-radius: 8px !important;
        margin-top: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize services if not already done
def initialize_services():
    """Initialize services for this page"""
    if 'services_initialized' not in st.session_state or not st.session_state.services_initialized:
        try:
            from src.services import (
                get_attendance_service,
                get_attendance_repository,
                get_attendance_manager
            )
            
            # Initialize services
            attendance_service = get_attendance_service()
            attendance_repository = get_attendance_repository()
            attendance_manager = get_attendance_manager()
            
            # Store in session state
            st.session_state.attendance_service = attendance_service
            st.session_state.attendance_repository = attendance_repository
            st.session_state.attendance_manager = attendance_manager
            st.session_state.services_initialized = True
            
        except Exception as e:
            st.error(f"Failed to initialize services: {e}")
            return False
    return True

# Initialize services
initialize_services()

# Show navigation sidebar
from src.dashboard.utils.navigation import show_navigation_sidebar
show_navigation_sidebar()

# Page header
from src.dashboard.utils.navigation import show_page_header, show_page_footer
show_page_header(
    title="Daily Attendance",
    description="Real-time face recognition with liveness detection",
    icon="📅"
)

# Persistent Debug Display Section
if 'last_debug_info' in st.session_state:
    with st.expander("🔍 **Last Debug Info (Click to expand)**", expanded=True):
        debug_info = st.session_state.last_debug_info
        st.write("**Last Attendance Logging Debug Information:**")
        st.write(f"**Timestamp:** {debug_info.get('timestamp', 'N/A')}")
        
        # User Recognition Info
        user_info = debug_info.get('user_recognized', {})
        st.write("**User Recognition:**")
        st.write(f"- Name: {user_info.get('name', 'N/A')}")
        st.write(f"- User ID: {user_info.get('user_id', 'N/A')}")
        st.write(f"- Confidence: {user_info.get('confidence', 'N/A')}")
        st.write(f"- Recognized: {user_info.get('recognized', 'N/A')}")
        st.write(f"- Processing Time: {user_info.get('processing_time', 'N/A')} ms")
        
        # Liveness Info
        liveness_info = debug_info.get('liveness_result', {})
        st.write("**Liveness Detection:**")
        st.write(f"- Is Live: {liveness_info.get('is_live', 'N/A')}")
        st.write(f"- Confidence: {liveness_info.get('confidence', 'N/A')}")
        st.write(f"- Blink Count: {liveness_info.get('blink_count', 'N/A')}")
        st.write(f"- Motion Score: {liveness_info.get('motion_score', 'N/A')}")
        
        # Raw data for debugging
        st.write("**Raw Data:**")
        st.json(debug_info)
        
        # Step tracking
        if 'current_attendance_step' in st.session_state:
            st.write("**Current Attendance Step:**")
            st.write(f"- Step: {st.session_state.current_attendance_step}")
        else:
            st.write("**Current Attendance Step:** Not tracked")
else:
    st.info("🔍 **Debug Info:** No attendance logging debug information available yet. Try marking your attendance to see debug details.")

# Show current step if available
if 'current_attendance_step' in st.session_state:
    st.info(f"📍 **Current Step:** {st.session_state.current_attendance_step}")

# Show the daily attendance component
show_daily_attendance()

# Page footer
show_page_footer("Daily Attendance")
