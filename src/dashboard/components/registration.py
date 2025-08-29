"""
User Registration Component - Day 13 Enhanced
Handles user registration interface with real backend integration and embedding generation
"""

import streamlit as st
import pandas as pd
import cv2
import numpy as np
from PIL import Image
import io
from pathlib import Path
import sys
import time
import json
import hashlib
from datetime import datetime
import os

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from modules.face_db import FaceDatabase
    from modules.recognition import FaceRecognition
    REAL_BACKEND_AVAILABLE = True
except ImportError:
    REAL_BACKEND_AVAILABLE = False
    st.warning("⚠️ Real backend not available. Using mock systems for demonstration.")

def show_registration():
    """Show enhanced user registration interface"""
    st.header("👤 User Registration - Day 13 Enhanced")
    st.markdown("**Register new users with face images, generate embeddings, and update database in real-time**")
    
    # Initialize real backend if available
    if REAL_BACKEND_AVAILABLE and 'face_db' not in st.session_state:
        try:
            st.session_state.face_db = FaceDatabase()
            st.session_state.face_recognition = FaceRecognition()
            st.success("✅ Real backend initialized successfully!")
        except Exception as e:
            st.error(f"❌ Failed to initialize real backend: {e}")
            REAL_BACKEND_AVAILABLE = False
    
    # Registration tabs
    tab1, tab2, tab3 = st.tabs(["📷 Webcam Registration", "📁 Image Upload Registration", "👥 User Management"])
    
    with tab1:
        show_webcam_registration()
    
    with tab2:
        show_image_upload_registration()
    
    with tab3:
        show_user_management()

def show_webcam_registration():
    """Show enhanced webcam-based registration with real backend"""
    st.subheader("📷 Webcam Registration")
    
    # User information form
    with st.form("webcam_registration"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="Enter full name", help="Required field")
            user_id = st.text_input("User ID *", placeholder="Enter unique ID", help="Required field")
            email = st.text_input("Email", placeholder="Enter email address")
        
        with col2:
            department = st.selectbox(
                "Department",
                ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", "Other"]
            )
            role = st.selectbox(
                "Role",
                ["Employee", "Manager", "Director", "Intern", "Contractor"]
            )
            phone = st.text_input("Phone (Optional)", placeholder="Enter phone number")
        
        # Webcam capture
        st.subheader("📸 Face Capture")
        
        # Initialize webcam state
        if 'webcam_captured' not in st.session_state:
            st.session_state.webcam_captured = False
            st.session_state.captured_image = None
            st.session_state.embedding_generated = False
        
        # Webcam interface
        camera_input = st.camera_input("Take a photo", help="Ensure good lighting and clear face visibility")
        
        if camera_input is not None:
            # Convert to PIL Image
            image = Image.open(camera_input)
            st.session_state.captured_image = image
            st.session_state.webcam_captured = True
            
            # Display captured image
            col1, col2 = st.columns([2, 1])
            with col1:
                st.image(image, caption="Captured Image", use_column_width=True)
            
            with col2:
                # Image quality assessment
                quality_score = assess_image_quality(image)
                st.metric("Image Quality Score", f"{quality_score:.2f}/1.0")
                
                if quality_score < 0.5:
                    st.warning("⚠️ Image quality is low. Please try again with better lighting.")
                elif quality_score < 0.7:
                    st.info("ℹ️ Image quality is acceptable but could be improved.")
                else:
                    st.success("✅ Image quality is good!")
                
                # Face detection validation
                if detect_face_in_image(image):
                    st.success("✅ Face detected successfully!")
                else:
                    st.error("❌ No face detected. Please try again.")
                
                # Generate embedding preview
                if st.button("🔍 Generate Embedding Preview", type="secondary"):
                    with st.spinner("Generating embedding..."):
                        embedding = generate_face_embedding(image)
                        if embedding is not None:
                            st.session_state.embedding_generated = True
                            st.success("✅ Embedding generated successfully!")
                            st.info(f"Embedding size: {len(embedding)} dimensions")
                        else:
                            st.error("❌ Failed to generate embedding")
        
        # Submit button
        submitted = st.form_submit_button("🚀 Register User", type="primary")
        
        if submitted:
            if not name or not user_id:
                st.error("Please fill in all required fields (Name and User ID)")
            elif not st.session_state.webcam_captured:
                st.error("Please capture an image using the webcam")
            elif not detect_face_in_image(st.session_state.captured_image):
                st.error("No face detected in the captured image")
            else:
                # Process registration with real backend
                success = process_registration_enhanced(
                    name, user_id, email, department, role, phone,
                    st.session_state.captured_image, "webcam"
                )
                
                if success:
                    st.success(f"✅ User {name} registered successfully!")
                    # Reset form
                    st.session_state.webcam_captured = False
                    st.session_state.captured_image = None
                    st.session_state.embedding_generated = False
                    st.rerun()
                else:
                    st.error("❌ Registration failed. Please try again.")

def show_image_upload_registration():
    """Show enhanced image upload-based registration"""
    st.subheader("📁 Image Upload Registration")
    
    # User information form
    with st.form("upload_registration"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name (Upload) *", placeholder="Enter full name", help="Required field")
            user_id = st.text_input("User ID (Upload) *", placeholder="Enter unique ID", help="Required field")
            email = st.text_input("Email (Upload)", placeholder="Enter email address")
        
        with col2:
            department = st.selectbox(
                "Department (Upload)",
                ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", "Other"]
            )
            role = st.selectbox(
                "Role (Upload)",
                ["Employee", "Manager", "Director", "Intern", "Contractor"]
            )
            phone = st.text_input("Phone (Upload)", placeholder="Enter phone number")
        
        # Image upload
        st.subheader("📁 Image Upload")
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg'],
            help="Upload a clear face image (PNG, JPG, JPEG). Minimum resolution: 480x480"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Image quality assessment
            quality_score = assess_image_quality(image)
            st.metric("Image Quality Score", f"{quality_score:.2f}/1.0")
            
            if quality_score < 0.5:
                st.warning("⚠️ Image quality is low. Please try a different image.")
            elif quality_score < 0.7:
                st.info("ℹ️ Image quality is acceptable but could be improved.")
            else:
                st.success("✅ Image quality is good!")
            
            # Face detection validation
            if detect_face_in_image(image):
                st.success("✅ Face detected successfully!")
            else:
                st.error("❌ No face detected. Please try again.")
        
        # Submit button
        submitted = st.form_submit_button("🚀 Register User (Upload)", type="primary")
        
        if submitted:
            if not name or not user_id:
                st.error("Please fill in all required fields (Name and User ID)")
            elif uploaded_file is None:
                st.error("Please upload an image file")
            elif not detect_face_in_image(image):
                st.error("No face detected in the uploaded image")
            else:
                # Process registration with real backend
                success = process_registration_enhanced(
                    name, user_id, email, department, role, phone,
                    image, "upload"
                )
                
                if success:
                    st.success(f"✅ User {name} registered successfully!")
                    st.rerun()
                else:
                    st.error("❌ Registration failed. Please try again.")

def show_user_management():
    """Show enhanced user management interface"""
    st.subheader("👥 User Management")
    
    # User management tabs
    tab1, tab2, tab3 = st.tabs(["📋 Registered Users", "🔍 Search Users", "⚙️ Database Info"])
    
    with tab1:
        show_registered_users_enhanced()
    
    with tab2:
        show_user_search()
    
    with tab3:
        show_database_info()

def show_registered_users_enhanced():
    """Show enhanced list of registered users"""
    st.subheader("📋 Registered Users")
    
    try:
        # Load faces database
        if hasattr(st.session_state, 'face_db') and st.session_state.face_db:
            users = st.session_state.face_db.users_db
            
            if users:
                # Create enhanced user dataframe
                user_data = []
                for user_id, user_info in users.items():
                    user_data.append({
                        'User ID': user_id,
                        'Name': user_info.get('name', 'Unknown'),
                        'Department': user_info.get('department', 'N/A'),
                        'Role': user_info.get('role', 'N/A'),
                        'Email': user_info.get('email', 'N/A'),
                        'Registration Date': user_info.get('registration_date', 'N/A'),
                        'Image Path': user_info.get('image_path', 'N/A'),
                        'Embedding Status': '✅' if 'embedding' in user_info else '❌'
                    })
                
                df = pd.DataFrame(user_data)
                
                # Add search and filter
                search_term = st.text_input("🔍 Search users by name or ID", placeholder="Type to search...")
                if search_term:
                    df = df[df.apply(lambda x: search_term.lower() in str(x).lower(), axis=1)]
                
                # Display user count
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Users", len(users))
                with col2:
                    active_users = len([u for u in users.values() if u.get('status', 'active') == 'active'])
                    st.metric("Active Users", active_users)
                with col3:
                    st.metric("Departments", len(set(u.get('department', 'Unknown') for u in users.values() if u.get('department'))))
                with col4:
                    embedding_count = len([u for u in users.values() if 'embedding' in u])
                    st.metric("Embeddings", f"{embedding_count}/{len(users)}")
                
                # Display user table
                st.dataframe(df, use_container_width=True)
                
                # Export functionality
                if st.button("📥 Export User Data (CSV)"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv,
                        file_name=f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
            else:
                st.info("No users registered yet.")
                
        else:
            st.info("Face database not initialized.")
            
    except Exception as e:
        st.error(f"Error loading users: {e}")

def show_user_search():
    """Show user search functionality"""
    st.subheader("🔍 Search Users")
    
    search_query = st.text_input("Enter search term", placeholder="Search by name, ID, department, or email...")
    
    if search_query:
        try:
            if hasattr(st.session_state, 'face_db') and st.session_state.face_db:
                users = st.session_state.face_db.users_db
                results = []
                
                for user_id, user_info in users.items():
                    searchable_text = f"{user_id} {user_info.get('name', '')} {user_info.get('department', '')} {user_info.get('email', '')}".lower()
                    if search_query.lower() in searchable_text:
                        results.append((user_id, user_info))
                
                if results:
                    st.success(f"Found {len(results)} matching users:")
                    for user_id, user_info in results:
                        with st.expander(f"👤 {user_info.get('name', 'Unknown')} ({user_id})"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Department:** {user_info.get('department', 'N/A')}")
                                st.write(f"**Role:** {user_info.get('role', 'N/A')}")
                                st.write(f"**Email:** {user_info.get('email', 'N/A')}")
                            with col2:
                                st.write(f"**Registration Date:** {user_info.get('registration_date', 'N/A')}")
                                st.write(f"**Embedding Status:** {'✅ Generated' if 'embedding' in user_info else '❌ Not Generated'}")
                                st.write(f"**Image Path:** {user_info.get('image_path', 'N/A')}")
                else:
                    st.info("No users found matching your search.")
            else:
                st.info("Face database not available.")
        except Exception as e:
            st.error(f"Search error: {e}")

def show_database_info():
    """Show database information and statistics"""
    st.subheader("⚙️ Database Information")
    
    try:
        if hasattr(st.session_state, 'face_db') and st.session_state.face_db:
            db = st.session_state.face_db
            
            # Database statistics
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Database Path", str(db.data_dir))
                st.metric("Users File", db.embeddings_file.name)
                st.metric("Cache File", db.embeddings_cache_file.name)
                st.metric("Backup Directory", db.backup_dir.name)
            
            with col2:
                st.metric("Total Users", len(db.users_db))
                st.metric("Embeddings Cache", len(db.embeddings_cache))
                st.metric("User Embeddings", len(db.user_embeddings))
                st.metric("Database Size", f"{get_directory_size(db.data_dir):.1f} MB")
            
            # Database actions
            st.subheader("🛠️ Database Actions")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Refresh Database"):
                    db._load_database()
                    st.success("Database refreshed!")
                    st.rerun()
            
            with col2:
                if st.button("💾 Create Backup"):
                    backup_path = db.backup_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(backup_path, 'w') as f:
                        json.dump(db.users_db, f, indent=2)
                    st.success(f"Backup created: {backup_path.name}")
            
            with col3:
                if st.button("🧹 Clear Cache"):
                    db.embeddings_cache = {}
                    db.user_embeddings = {}
                    st.success("Cache cleared!")
            
            # Recent activity
            st.subheader("📊 Recent Activity")
            if hasattr(db, 'users_db') and db.users_db:
                recent_users = sorted(
                    [(uid, info) for uid, info in db.users_db.items()],
                    key=lambda x: x[1].get('registration_date', ''),
                    reverse=True
                )[:5]
                
                for user_id, user_info in recent_users:
                    st.write(f"👤 **{user_info.get('name', 'Unknown')}** ({user_id}) - {user_info.get('registration_date', 'N/A')}")
        else:
            st.info("Face database not available.")
            
    except Exception as e:
        st.error(f"Error loading database info: {e}")

def assess_image_quality(image):
    """Assess image quality for face registration"""
    try:
        # Convert PIL to OpenCV format
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Calculate quality metrics
        quality_score = 0.0
        
        # Resolution score (0-0.3)
        height, width = gray.shape
        resolution_score = min(1.0, (height * width) / (480 * 480)) * 0.3
        quality_score += resolution_score
        
        # Brightness score (0-0.3)
        mean_brightness = np.mean(gray)
        if 30 <= mean_brightness <= 250:
            brightness_score = 0.3
        else:
            brightness_score = 0.3 * (1 - abs(mean_brightness - 140) / 140)
        quality_score += max(0, brightness_score)
        
        # Contrast score (0-0.2)
        contrast = np.std(gray)
        contrast_score = min(0.2, contrast / 50 * 0.2)
        quality_score += contrast_score
        
        # Sharpness score (0-0.2)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(0.2, laplacian_var / 500 * 0.2)
        quality_score += sharpness_score
        
        return min(1.0, quality_score)
        
    except Exception as e:
        st.error(f"Error assessing image quality: {e}")
        return 0.0

def detect_face_in_image(image):
    """Detect if a face is present in the image"""
    try:
        # Convert PIL to OpenCV format
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Load face cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        return len(faces) > 0
        
    except Exception as e:
        st.error(f"Face detection error: {e}")
        return False

def generate_face_embedding(image):
    """Generate face embedding using DeepFace"""
    try:
        if REAL_BACKEND_AVAILABLE and hasattr(st.session_state, 'face_recognition'):
            # Convert PIL to numpy array
            img_array = np.array(image)
            
            # Generate embedding
            embedding = st.session_state.face_recognition.generate_embedding(img_array)
            return embedding
        else:
            # Mock embedding for demonstration
            return np.random.rand(4096)
            
    except Exception as e:
        st.error(f"Embedding generation error: {e}")
        return None

def process_registration_enhanced(name, user_id, email, department, role, phone, image, source):
    """Process user registration with enhanced backend integration"""
    try:
        # Create faces directory if it doesn't exist
        faces_dir = Path("data/faces")
        faces_dir.mkdir(exist_ok=True)
        
        # Generate filename with hash for uniqueness
        timestamp = int(time.time())
        image_hash = hashlib.md5(image.tobytes()).hexdigest()[:8]
        filename = f"user_{user_id}_{timestamp}_{image_hash}.jpg"
        filepath = faces_dir / filename
        
        # Save image
        if isinstance(image, Image.Image):
            image.save(filepath, "JPEG", quality=95)
        else:
            # Convert numpy array to PIL and save
            pil_image = Image.fromarray(image)
            pil_image.save(filepath, "JPEG", quality=95)
        
        # Generate embedding
        embedding = generate_face_embedding(image)
        
        # Prepare user data
        user_data = {
            'name': name,
            'user_id': user_id,
            'email': email,
            'department': department,
            'role': role,
            'phone': phone,
            'image_path': str(filepath),
            'registration_date': datetime.now().isoformat(),
            'source': source,
            'status': 'active'
        }
        
        # Add embedding if generated
        if embedding is not None:
            user_data['embedding'] = embedding.tolist()
        
        # Update real backend if available
        if REAL_BACKEND_AVAILABLE and hasattr(st.session_state, 'face_db'):
            # Register user in real database
            st.session_state.face_db.register_user(name, user_id, image, metadata=user_data)
            st.success("✅ User registered in real database!")
        else:
            # Fallback to mock system
            if 'face_db' not in st.session_state:
                from utils.mock_systems import MockFaceDatabase
                st.session_state.face_db = MockFaceDatabase()
            
            st.session_state.face_db.add_user(name, user_id, embedding if embedding is not None else [])
            st.info("ℹ️ User registered in mock system (real backend not available)")
        
        # Log registration
        st.info(f"User {name} ({user_id}) registered via {source}")
        st.info(f"Image saved to: {filepath}")
        
        if embedding is not None:
            st.info(f"Face embedding generated: {len(embedding)} dimensions")
        
        return True
        
    except Exception as e:
        st.error(f"Registration error: {e}")
        return False

def get_directory_size(directory):
    """Get directory size in MB"""
    try:
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size / (1024 * 1024)  # Convert to MB
    except:
        return 0.0

# Show registered users at the bottom
if __name__ == "__main__":
    show_registered_users_enhanced()

