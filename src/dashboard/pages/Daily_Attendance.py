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
        from src.modules.liveness import LivenessDetection
        from src.modules.attendance import AttendanceManager
        
        # Initialize systems
        recognition = FaceRecognition(confidence_threshold=0.1, use_mediapipe=True)
        liveness = LivenessDetection()  # New modular system doesn't need parameters
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

def run_streamlit_compatible_blink_session(liveness):
    """Run a Streamlit-compatible blink detection session"""
    try:
        # Initialize session state if not already done
        if 'blink_counter_start_time' not in st.session_state:
            st.session_state.blink_counter_start_time = time.time()
        if 'blink_count' not in st.session_state:
            st.session_state.blink_count = 0
        if 'blink_counter_camera_cap' not in st.session_state:
            st.session_state.blink_counter_camera_cap = None
        if 'last_blink_time' not in st.session_state:
            st.session_state.last_blink_time = None
        
        # Initialize camera if not already done
        if st.session_state.blink_counter_camera_cap is None:
            try:
                st.session_state.blink_counter_camera_cap = cv2.VideoCapture(0)
                if not st.session_state.blink_counter_camera_cap.isOpened():
                    st.error("❌ Failed to open camera. Please check camera permissions.")
                    st.session_state.blink_counter_active = False
                    return False
                else:
                    st.success("✅ Camera initialized successfully")
                    # Set camera properties
                    try:
                        st.session_state.blink_counter_camera_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        st.session_state.blink_counter_camera_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        st.session_state.blink_counter_camera_cap.set(cv2.CAP_PROP_FPS, 30)
                    except Exception as prop_error:
                        st.warning(f"⚠️ Some camera properties could not be set: {prop_error}")
            except Exception as e:
                st.error(f"❌ Camera initialization error: {e}")
                st.session_state.blink_counter_active = False
                return False
        
        # Calculate elapsed time
        elapsed_time = time.time() - st.session_state.blink_counter_start_time
        remaining_time = max(0, 30.0 - elapsed_time)  # 30 seconds timer
        progress = min(100.0, (elapsed_time / 30.0) * 100)
        
        # Read frame from camera
        ret, frame = st.session_state.blink_counter_camera_cap.read()
        if not ret:
            st.error("❌ Failed to read from camera")
            st.session_state.blink_counter_active = False
            if st.session_state.blink_counter_camera_cap:
                st.session_state.blink_counter_camera_cap.release()
                st.session_state.blink_counter_camera_cap = None
            return False
    
        # Process frame for blink detection
        current_ear = 0.0
        current_status = "EYES OPEN"
        blink_detected_this_frame = False
        
        try:
            liveness_result = liveness.detect_blink(frame)
            
            # Get EAR value for debugging - try multiple sources
            current_ear = 0.0
            current_status = "EYES OPEN"
            
            # Method 1: Try to get from details
            if hasattr(liveness_result, 'details') and liveness_result.details:
                current_ear = liveness_result.details.get('ear_value', 0.0)
                current_status = "BLINKING" if liveness_result.is_live else "EYES OPEN"
            # Method 2: Try to get from blink history
            elif hasattr(liveness, 'blink_history') and liveness.blink_history:
                current_ear = liveness.blink_history[-1]['ear']
                current_status = "BLINKING" if liveness_result.is_live else "EYES OPEN"
            # Method 3: Calculate EAR directly from the frame
            else:
                # Direct EAR calculation as fallback
                try:
                    import mediapipe as mp
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = liveness.face_mesh.process(rgb_frame)
                    if results.multi_face_landmarks:
                        face_landmarks = results.multi_face_landmarks[0]
                        left_ear = liveness._calculate_eye_aspect_ratio(face_landmarks, liveness.LEFT_EYE)
                        right_ear = liveness._calculate_eye_aspect_ratio(face_landmarks, liveness.RIGHT_EYE)
                        current_ear = (left_ear + right_ear) / 2.0
                        # Use EAR threshold for status determination
                        current_status = "BLINKING" if current_ear < 0.21 else "EYES OPEN"
                    else:
                        current_ear = 0.0
                        current_status = "NO FACE DETECTED"
                except Exception as calc_error:
                    st.warning(f"⚠️ EAR calculation error: {calc_error}")
                    current_ear = 0.0
                    current_status = "ERROR"
            
            # Check if a new blink was detected
            # Use multiple methods to detect blinks
            blink_detected = False
            
            # Method 1: Check liveness_result.is_live (when eyes are closed)
            if liveness_result.is_live:
                blink_detected = True
            
            # Method 2: Check EAR threshold directly
            elif current_ear < 0.21 and current_ear > 0.0:
                blink_detected = True
            
            # Method 3: Check blink history for recent blink detection
            elif (hasattr(liveness, 'blink_history') and liveness.blink_history and 
                  liveness.blink_history[-1].get('blink_detected', False)):
                blink_detected = True
            
            # Update blink count if blink detected
            if blink_detected:
                current_time = time.time()
                # Avoid counting the same blink multiple times (500ms cooldown)
                if (st.session_state.last_blink_time is None or 
                    current_time - st.session_state.last_blink_time > 0.5):
                    st.session_state.blink_count += 1
                    st.session_state.last_blink_time = current_time
                    blink_detected_this_frame = True
                    st.success(f"👁️ Blink {st.session_state.blink_count} detected! Total: {st.session_state.blink_count}")
            
            # Also sync with liveness module blink count
            if liveness_result.blink_count > st.session_state.blink_count:
                st.session_state.blink_count = liveness_result.blink_count
                    
        except Exception as e:
            st.warning(f"⚠️ Blink detection error: {e}")
        
        # Add visual overlays to the frame
        frame_with_overlays = add_enhanced_visual_overlays_to_frame(
            frame, elapsed_time, remaining_time, st.session_state.blink_count, current_ear, current_status
        )
        
        # Display the camera feed with live updates
        st.image(frame_with_overlays, channels="BGR", use_container_width=True, caption=f"LIVE CAMERA - EAR: {current_ear:.3f} - {current_status}")
        
        # Debug information
        with st.expander("🔍 Debug Information", expanded=True):
            st.write(f"**EAR Value**: {current_ear:.3f}")
            st.write(f"**Status**: {current_status}")
            st.write(f"**Liveness Result**: {liveness_result.is_live}")
            st.write(f"**Blink Count (Liveness)**: {liveness_result.blink_count}")
            st.write(f"**Blink Count (Session)**: {st.session_state.blink_count}")
            st.write(f"**Confidence**: {liveness_result.confidence:.3f}")
            st.write(f"**Processing Time**: {liveness_result.processing_time:.3f}s")
            
            # Show which method was used for EAR calculation
            if hasattr(liveness_result, 'details') and liveness_result.details:
                st.write("**EAR Source**: Method 1 (Details)")
                st.write(f"**Details**: {liveness_result.details}")
            elif hasattr(liveness, 'blink_history') and liveness.blink_history:
                st.write("**EAR Source**: Method 2 (Blink History)")
            else:
                st.write("**EAR Source**: Method 3 (Direct Calculation)")
            
            # Show blink detection methods
            st.write("**Blink Detection Methods**:")
            st.write(f"- Method 1 (liveness_result.is_live): {liveness_result.is_live}")
            st.write(f"- Method 2 (EAR < 0.21): {current_ear < 0.21 and current_ear > 0.0}")
            if hasattr(liveness, 'blink_history') and liveness.blink_history:
                latest_blink = liveness.blink_history[-1].get('blink_detected', False)
                st.write(f"- Method 3 (blink_history): {latest_blink}")
            else:
                st.write("- Method 3 (blink_history): Not available")
            
            # Show blink history if available
            if hasattr(liveness, 'blink_history') and liveness.blink_history:
                st.write(f"**Blink History Length**: {len(liveness.blink_history)}")
                if liveness.blink_history:
                    latest = liveness.blink_history[-1]
                    st.write(f"**Latest History**: EAR={latest.get('ear', 0):.3f}, Blink={latest.get('blink_detected', False)}")
            else:
                st.write("**Blink History**: Not available")
            
            # Show face mesh status
            if hasattr(liveness, 'face_mesh'):
                st.write("**Face Mesh**: Available")
            else:
                st.write("**Face Mesh**: Not available")
        
        # Display status
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.metric("⏱️ Time Left", f"{remaining_time:.1f}s")
        
        with col2:
            # Color coding based on progress
            if st.session_state.blink_count >= 3:
                color = "#28a745"  # Green - success
                status_text = "✅ SUCCESS!"
            elif st.session_state.blink_count >= 2:
                color = "#ffc107"  # Yellow - almost there
                status_text = "🟡 Almost there!"
            elif st.session_state.blink_count >= 1:
                color = "#17a2b8"  # Blue - good progress
                status_text = "🔵 Good progress!"
            else:
                color = "#dc3545"  # Red - need blinks
                status_text = "🔴 Blink naturally!"
            
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px; margin: 10px 0;">
                <h1 style="color: {color}; margin: 0;">👁️ BLINKS: {st.session_state.blink_count}</h1>
                <p style="margin: 5px 0; color: #666;">Target: 3 blinks in 30 seconds</p>
                <p style="margin: 5px 0; color: #888; font-size: 12px;">EAR: {current_ear:.3f} | Status: {current_status}</p>
                <p style="margin: 5px 0; color: {color}; font-weight: bold;">{status_text}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.metric("📊 Progress", f"{progress:.1f}%")
        
        # Progress bar
        st.progress(min(1.0, progress / 100))
        
        # Check if we've reached 3 blinks (success condition)
        if st.session_state.blink_count >= 3:
            st.session_state.blink_counter_active = False
            
            st.success(f"""
            ✅ **Liveness Verification Successful!**
            
            **Session Results:**
            - **Blinks Counted**: {st.session_state.blink_count}
            - **Session Duration**: {elapsed_time:.1f} seconds
            - **Success**: ✅ Verified (3 blinks detected)
            """)
            
            # Create a mock liveness result for compatibility
            class MockLivenessResult:
                def __init__(self, blink_count, confidence=0.9):
                    self.is_live = True
                    self.confidence = confidence
                    self.blink_count = blink_count
                    self.details = {'blink_count': blink_count}
            
            st.session_state.liveness_result = MockLivenessResult(st.session_state.blink_count)
            st.session_state.real_time_step = 'attendance_logging'
            
            # Clean up camera
            if st.session_state.blink_counter_camera_cap:
                st.session_state.blink_counter_camera_cap.release()
                st.session_state.blink_counter_camera_cap = None
            
            st.rerun()
            return True
        
        # Check if 30 seconds have passed (timeout condition)
        if elapsed_time >= 30.0:
            st.session_state.blink_counter_active = False
            
            if st.session_state.blink_count >= 3:
                st.success(f"""
                ✅ **Liveness Verification Successful!**
                
                **Session Results:**
                - **Blinks Counted**: {st.session_state.blink_count}
                - **Session Duration**: 30.0 seconds
                - **Success**: ✅ Verified (3+ blinks detected)
                """)
                
                # Create a mock liveness result for compatibility
                class MockLivenessResult:
                    def __init__(self, blink_count, confidence=0.9):
                        self.is_live = True
                        self.confidence = confidence
                        self.blink_count = blink_count
                        self.details = {'blink_count': blink_count}
                
                st.session_state.liveness_result = MockLivenessResult(st.session_state.blink_count)
                st.session_state.real_time_step = 'attendance_logging'
                
            else:
                st.error(f"""
                ❌ **Liveness Verification Failed**
                
                **Session Results:**
                - **Blinks Counted**: {st.session_state.blink_count}
                - **Session Duration**: 30.0 seconds
                - **Error**: Insufficient blinks detected (minimum 3 required)
                
                **Please try again and blink naturally during the countdown.**
                """)
            
            # Clean up camera
            if st.session_state.blink_counter_camera_cap:
                st.session_state.blink_counter_camera_cap.release()
                st.session_state.blink_counter_camera_cap = None
            
            st.rerun()
            return True
        
        # Continue the session by rerunning with a small delay
        time.sleep(0.1)  # 100ms delay for smoother updates
        st.rerun()
        
        return False
        
    except Exception as e:
        st.error(f"❌ Error in Streamlit-compatible blink session: {e}")
        st.session_state.blink_counter_active = False
        if st.session_state.blink_counter_camera_cap:
            st.session_state.blink_counter_camera_cap.release()
            st.session_state.blink_counter_camera_cap = None
        return False
    
def calculate_ear(landmarks, eye_indices):
    """Calculate Eye Aspect Ratio (EAR) for blink detection"""
    try:
        # Extract the 6 key eye landmark coordinates
        eye_points = []
        for idx in eye_indices:
            if idx < len(landmarks.landmark):
                landmark = landmarks.landmark[idx]
                x, y = landmark.x, landmark.y
                eye_points.append((x, y))
        
        if len(eye_points) < 6:
            return 0.0
        
        # Calculate vertical distances (A and B)
        # A = distance between points 1 and 5
        A = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
        # B = distance between points 2 and 4  
        B = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
        
        # Calculate horizontal distance (C)
        # C = distance between points 0 and 3
        C = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
        
        # Calculate EAR: (A + B) / (2.0 * C)
        if C > 0:
            ear = (A + B) / (2.0 * C)
            return ear
        else:
            return 0.0
            
    except Exception as e:
        return 0.0

def add_enhanced_visual_overlays_to_frame(frame, elapsed_time, remaining_time, blink_count, current_ear=0.0, current_status="EYES OPEN"):
    """Add enhanced visual overlays to the camera frame for 30s timer and 3-blink requirement"""
    try:
        # Create a copy of the frame
        frame_with_overlays = frame.copy()
        
        # Add timer overlay
        timer_text = f"Time: {remaining_time:.1f}s"
        cv2.putText(frame_with_overlays, timer_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        
        # Add blink count overlay (larger and more prominent)
        blink_text = f"BLINKS: {blink_count}"
        cv2.putText(frame_with_overlays, blink_text, (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
        
        # Add EAR value and status
        ear_text = f"EAR: {current_ear:.3f} ({current_status})"
        ear_color = (0, 0, 255) if current_status == "BLINKING" else (0, 255, 0)
        cv2.putText(frame_with_overlays, ear_text, (10, 110), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, ear_color, 2)
        
        # Add target requirement (3 blinks)
        target_text = "TARGET: 3 blinks"
        cv2.putText(frame_with_overlays, target_text, (10, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Add progress bar overlay (30 seconds)
        bar_width = 300
        bar_height = 20
        bar_x = 10
        bar_y = 170
        
        # Background bar
        cv2.rectangle(frame_with_overlays, (bar_x, bar_y), 
                     (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
        
        # Progress bar (30 seconds)
        progress_width = int((elapsed_time / 30.0) * bar_width)
        cv2.rectangle(frame_with_overlays, (bar_x, bar_y), 
                     (bar_x + progress_width, bar_y + bar_height), (0, 255, 0), -1)
        
        # Add status indicator with color coding
        if blink_count >= 3:
            status_text = "✅ SUCCESS!"
            color = (0, 255, 0)  # Green
        elif blink_count >= 2:
            status_text = "🟡 Almost there!"
            color = (0, 255, 255)  # Yellow
        elif blink_count >= 1:
            status_text = "🔵 Good progress!"
            color = (255, 255, 0)  # Cyan
        else:
            status_text = "🔴 Blink naturally!"
            color = (0, 165, 255)  # Orange
        
        cv2.putText(frame_with_overlays, status_text, (10, 210), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Add countdown indicator
        if remaining_time <= 5.0:
            countdown_text = f"COUNTDOWN: {remaining_time:.1f}s"
            cv2.putText(frame_with_overlays, countdown_text, (10, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        return frame_with_overlays
        
    except Exception as e:
        st.error(f"Error adding enhanced visual overlays: {e}")
        return frame

def handle_liveness_verification_step(liveness):
    """Handle Step 3**: Liveness Verification - Single Responsibility: Liveness Only"""
    st.info("👁️ **Step 3**: Liveness Verification - Live Blink Counter (30 seconds)")
    st.warning("🎯 **Requirements**: Blink 3 times naturally within 30 seconds. Camera will stop automatically after 3 blinks or 30 seconds!")
    
    # Debug: Show what we have
    st.write("🔍 **Debug Info:**")
    st.write(f"User Recognized: {st.session_state.user_recognized}")
    st.write(f"Webcam Active: {st.session_state.webcam_active}")
    st.write(f"Blink Counter Active: {st.session_state.get('blink_counter_active', False)}")
    st.write(f"Blink Count: {st.session_state.get('blink_count', 0)}")
    
    if not st.session_state.user_recognized:
        st.error("❌ No user recognized. Please go back to recognition step.")
        st.session_state.real_time_step = 'face_recognition'
        st.rerun()
        return False
    
    # Show instructions
    st.info("""
    **🎯 Live Blink Counter Instructions:**
    1. Look directly at the camera
    2. Blink naturally during the 30-second countdown
    3. The system will count your blinks in real-time
    4. Exactly 3 blinks are required for verification
    5. Camera will stop automatically after 3 blinks or 30 seconds
    """)
    
    # Initialize session state
    if 'blink_session_id' not in st.session_state:
        st.session_state.blink_session_id = None
    if 'blink_counter_active' not in st.session_state:
        st.session_state.blink_counter_active = False
    
    # Start button
    if st.button("🚀 Start Live Blink Counter", key="start_blink_counter_btn", type="primary"):
        try:
            # Create unique session ID
            session_id = f"liveness_session_{int(time.time())}"
            st.session_state.blink_session_id = session_id
            
            # Initialize blink counter state
            st.session_state.blink_counter_start_time = time.time()
            st.session_state.blink_count = 0
            st.session_state.blink_counter_camera_cap = None
            st.session_state.last_blink_time = None
            
            st.session_state.blink_counter_active = True
            st.success(f"✅ Live Blink Counter session started: {session_id}")
            
            # Reset liveness detection state
            liveness.reset_state()
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Failed to start live blink counter: {e}")
            return False
    
    # Live camera feed with real-time blink detection using Streamlit-compatible approach
    if st.session_state.blink_counter_active and st.session_state.blink_session_id:
        run_streamlit_compatible_blink_session(liveness)
    
    # Stop button (if session is active)
    if st.session_state.blink_counter_active:
        if st.button("⏹️ Stop Session", key="stop_blink_counter_btn", type="secondary"):
            try:
                # Clean up camera
                if st.session_state.blink_counter_camera_cap:
                    st.session_state.blink_counter_camera_cap.release()
                    st.session_state.blink_counter_camera_cap = None
                
                st.session_state.blink_counter_active = False
                st.session_state.blink_session_id = None
                st.success("✅ Live Blink Counter session stopped")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error stopping session: {e}")
    
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
        if hasattr(st.session_state.liveness_result, 'details'):
            blink_count = st.session_state.liveness_result.details.get('blink_count', 0)
            st.write(f"Liveness blink_count: {blink_count}")
        else:
            st.write(f"Liveness blink_count: {getattr(st.session_state.liveness_result, 'blink_count', 'N/A')}")
    
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
                    # Count all logged entries as present
                    present_today = len(today_df[today_df['Status'] == 'logged'])
                    st.metric("Present", present_today)
                
                with col3:
                    # Count late entries (if any)
                    late_today = len(today_df[today_df['Status'] == 'Late'])
                    st.metric("Late", late_today)
                
                with col4:
                    # Calculate attendance rate based on total entries
                    attendance_rate = (total_today / max(1, total_today) * 100) if total_today > 0 else 0
                    st.metric("Attendance Rate", f"{attendance_rate:.1f}%")
                
                # Show status breakdown
                st.subheader("📈 Status Breakdown")
                status_counts = today_df['Status'].value_counts()
                for status, count in status_counts.items():
                    st.write(f"• **{status.title()}**: {count} entries")
                
                # Show liveness verification stats
                if 'Liveness_Verified' in today_df.columns:
                    liveness_stats = today_df['Liveness_Verified'].value_counts()
                    st.subheader("🔐 Liveness Verification Stats")
                    for status, count in liveness_stats.items():
                        status_text = "✅ Verified" if status == True else "❌ Failed" if status == False else "❓ Unknown"
                        st.write(f"• **{status_text}**: {count} entries")
                
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
