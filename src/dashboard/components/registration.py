"""
User Registration Component
Provides clean user registration interface
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
import io
import time
import os
from pathlib import Path

def show_registration():
    """Show user registration interface"""
    # Check if services are available
    if 'attendance_service' not in st.session_state:
        st.error("Services not initialized. Please refresh the page.")
        return
        
    if 'face_database' not in st.session_state:
        st.error("Face database not initialized. Please refresh the page.")
        return
    
    # Get services from session state
    attendance_service = st.session_state.attendance_service
    face_database = st.session_state.face_database
    
    # Initialize face registration module
    try:
        from src.modules.registration import FaceRegistration
        face_registration = FaceRegistration()
        st.session_state.face_registration = face_registration
    except Exception as e:
        st.error(f"Failed to initialize face registration: {e}")
        return
    
    # Registration form
    st.subheader("📝 New User Registration")
    
    with st.form("user_registration"):
        # User information
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username", placeholder="e.g., alice_johnson")
            first_name = st.text_input("First Name", placeholder="John")
            last_name = st.text_input("Last Name", placeholder="Doe")
        
        with col2:
            email = st.text_input("Email", placeholder="john.doe@company.com")
            department = st.selectbox("Department", [
                "Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", "Other"
            ])
            role = st.text_input("Role", placeholder="Software Engineer")
        
        # Face capture
        st.subheader("📸 Face Capture")
        
        # Camera input
        camera_input = st.camera_input("Capture face image for registration")
        
        # Or file upload
        uploaded_file = st.file_uploader(
            "Or upload an image file", 
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear face image for registration"
        )
        
        # Image processing
        face_image = None
        if camera_input is not None:
            face_image = camera_input
            st.success("✅ Face captured via camera")
        elif uploaded_file is not None:
            face_image = uploaded_file
            st.success("✅ Face image uploaded")
        
        # Show status of face capture
        if face_image is None:
            st.warning("⚠️ Please capture a face image using the camera or upload an image file")
        else:
            st.success("✅ Face image ready")
        
        # Display captured image
        if face_image is not None:
            st.image(face_image, caption="Captured Face Image", use_container_width=True)
            
            # Image quality check
            if st.checkbox("🔍 Analyze Image Quality"):
                try:
                    # Convert to PIL Image for analysis
                    if hasattr(face_image, 'read'):
                        img = Image.open(face_image)
                    else:
                        img = face_image
                    
                    # Basic quality metrics
                    width, height = img.size
                    aspect_ratio = width / height
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Image Size", f"{width} × {height}")
                    with col2:
                        st.metric("Aspect Ratio", f"{aspect_ratio:.2f}")
                    with col3:
                        # Simple brightness estimation
                        img_array = np.array(img.convert('L'))
                        brightness = np.mean(img_array)
                        st.metric("Brightness", f"{brightness:.1f}")
                    
                    # Quality recommendations
                    if width < 200 or height < 200:
                        st.warning("⚠️ Image resolution is low. Higher resolution recommended.")
                    elif aspect_ratio < 0.8 or aspect_ratio > 1.2:
                        st.warning("⚠️ Image aspect ratio is not ideal. Square images work best.")
                    elif brightness < 50:
                        st.warning("⚠️ Image is too dark. Better lighting recommended.")
                    elif brightness > 200:
                        st.warning("⚠️ Image is too bright. Reduce lighting or exposure.")
                    else:
                        st.success("✅ Image quality is good for registration.")
                        
                except Exception as e:
                    st.error(f"Error analyzing image: {e}")
        
        # Additional settings
        st.subheader("⚙️ Registration Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            enable_liveness = st.checkbox("Enable Liveness Detection", value=True)
            auto_attendance = st.checkbox("Enable Auto-Attendance", value=True)
        
        with col2:
            notification_email = st.checkbox("Send Welcome Email", value=True)
            create_backup = st.checkbox("Create Face Backup", value=True)
        
        # Submit button
        submitted = st.form_submit_button("🚀 Register User")
        
        if submitted:
            # Log registration attempt
            from src.utils.logger import setup_logger
            from datetime import datetime
            logger = setup_logger("RegistrationComponent")
            logger.info("=" * 60)
            logger.info("STREAMLIT REGISTRATION FORM SUBMITTED")
            logger.info("=" * 60)
            logger.info(f"Username: {username}")
            logger.info(f"First Name: {first_name}")
            logger.info(f"Last Name: {last_name}")
            logger.info(f"Email: {email}")
            logger.info(f"Department: {department}")
            logger.info(f"Role: {role}")
            logger.info(f"Face Image Provided: {'Yes' if face_image else 'No'}")
            logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)
            
            # Check each field individually for better validation
            missing_fields = []
            if not username or username.strip() == "":
                missing_fields.append("Username")
            if not first_name or first_name.strip() == "":
                missing_fields.append("First Name")
            if not last_name or last_name.strip() == "":
                missing_fields.append("Last Name")
            if not email or email.strip() == "":
                missing_fields.append("Email")
            if not face_image:
                missing_fields.append("Face Image")
            
            if missing_fields:
                logger.warning(f"Registration validation failed - Missing fields: {missing_fields}")
                st.error("❌ Please fill in all required fields and capture a face image.")
                st.write("**Missing or empty fields:**")
                for field in missing_fields:
                    st.write(f"- {field}")
                return
            
            logger.info("Registration form validation passed - Proceeding with user registration")
            
            # Show processing
            with st.spinner("🔄 Processing registration..."):
                try:
                    # Prepare user metadata
                    user_metadata = {
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'department': department,
                        'role': role,
                        'enable_liveness': enable_liveness,
                        'auto_attendance': auto_attendance,
                        'notification_email': notification_email,
                        'create_backup': create_backup
                    }
                    
                    # Register user using face registration module
                    # First, save the uploaded image temporarily
                    import tempfile
                    import os
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                        # Convert PIL image to bytes and save
                        if hasattr(face_image, 'read'):
                            # It's an uploaded file
                            tmp_file.write(face_image.read())
                            face_image.seek(0)  # Reset file pointer
                        elif hasattr(face_image, 'save'):
                            # It's a PIL Image (camera)
                            face_image.save(tmp_file.name, 'JPEG')
                        else:
                            st.error("❌ Unsupported image format")
                            return
                        
                        tmp_path = tmp_file.name
                    
                    try:
                        # Register user using the correct method
                        success = face_registration.register_from_image(
                            image_path=tmp_path,
                            user_name=f"{first_name} {last_name}",
                            user_id=username
                        )
                        
                        # Clean up temp file
                        os.unlink(tmp_path)
                        
                        if success:
                            # Log successful registration completion
                            logger.info("=" * 60)
                            logger.info("STREAMLIT REGISTRATION COMPLETED SUCCESSFULLY")
                            logger.info("=" * 60)
                            logger.info(f"Username: {username}")
                            logger.info(f"Full Name: {first_name} {last_name}")
                            logger.info(f"Email: {email}")
                            logger.info(f"Department: {department}")
                            logger.info(f"Role: {role}")
                            logger.info(f"Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            logger.info("=" * 60)
                            
                            st.success("✅ User registered successfully!")
                            
                            # Show registration summary
                            st.subheader("📋 Registration Summary")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Username:** {username}")
                                st.write(f"**Name:** {first_name} {last_name}")
                                st.write(f"**Email:** {email}")
                            
                            with col2:
                                st.write(f"**Department:** {department}")
                                st.write(f"**Role:** {role}")
                                st.write(f"**Registration Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            
                            # Clear form
                            st.rerun()
                        else:
                            logger.error("=" * 60)
                            logger.error("STREAMLIT REGISTRATION FAILED")
                            logger.error("=" * 60)
                            logger.error(f"Username: {username}")
                            logger.error(f"Full Name: {first_name} {last_name}")
                            logger.error(f"Error: Registration process returned False")
                            logger.error("=" * 60)
                            
                            st.error("❌ Failed to register user. Please try again.")
                            
                    except Exception as e:
                        logger.error("=" * 60)
                        logger.error("STREAMLIT REGISTRATION ERROR")
                        logger.error("=" * 60)
                        logger.error(f"Username: {username}")
                        logger.error(f"Full Name: {first_name} {last_name}")
                        logger.error(f"Error: {str(e)}")
                        logger.error(f"Error Type: {type(e).__name__}")
                        logger.error("=" * 60)
                        
                        st.error(f"❌ Registration error: {e}")
                        # Clean up temp file on error
                        if 'tmp_path' in locals():
                            try:
                                os.unlink(tmp_path)
                            except:
                                pass
                        st.info("Please check the system logs for more details.")
                        
                except Exception as e:
                    logger.error("=" * 60)
                    logger.error("STREAMLIT REGISTRATION UNEXPECTED ERROR")
                    logger.error("=" * 60)
                    logger.error(f"Username: {username}")
                    logger.error(f"Full Name: {first_name} {last_name}")
                    logger.error(f"Error: {str(e)}")
                    logger.error(f"Error Type: {type(e).__name__}")
                    logger.error("=" * 60)
                    
                    st.error(f"❌ Unexpected error during registration: {e}")
                    st.info("Please check the system logs for more details.")
    
    # Show existing users
    st.subheader("👥 Registered Users")
    
    try:
        if 'face_registration' in st.session_state:
            # Use list_users for more detailed information
            users = face_registration.list_users()
            
            if users:
                # Convert to DataFrame for display with more details
                user_data = []
                for user in users:
                    # Format registration date
                    reg_date = user.get('registration_date', 'Unknown')
                    if reg_date != 'Unknown':
                        try:
                            # Parse ISO format date and format nicely
                            from datetime import datetime
                            dt = datetime.fromisoformat(reg_date.replace('Z', '+00:00'))
                            reg_date = dt.strftime('%Y-%m-%d %H:%M')
                        except:
                            reg_date = reg_date[:10] if len(reg_date) > 10 else reg_date
                    
                    user_data.append({
                        'User ID': user.get('user_id', 'Unknown'),
                        'Name': user.get('name', 'Unknown'),
                        'Registration Date': reg_date,
                        'Status': 'Active'
                    })
                
                if user_data:
                    import pandas as pd
                    df = pd.DataFrame(user_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # User statistics
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Users", len(users))
                    with col2:
                        st.metric("Active Users", len(users))
                else:
                    st.info("No user data available for display.")
            else:
                st.info("No users registered yet.")
        else:
            st.warning("Face registration system not available.")
            
    except Exception as e:
        st.error(f"Error loading user data: {e}")
