"""
Face Registration Module for EyeD AI Attendance System
Day 2 Implementation: Face Registration (Selfie Capture)

This module will handle:
- Webcam snapshot capture
- Image upload functionality  
- Face embedding extraction using DeepFace
- Storage of user data and embeddings
"""

import cv2
import os
import json
import numpy as np
from datetime import datetime
from deepface import DeepFace
from typing import Tuple, Optional, Dict, Any, List
from src.utils.logger import setup_logger

# Use centralized logging system
logger = setup_logger("FaceRegistration")

class FaceRegistration:
    """
    Face Registration Module for EyeD AI Attendance System
    
    Features:
    - Webcam capture with real-time face detection
    - Face quality validation
    - DeepFace embedding extraction (MobileNet)
    - User registration with metadata storage
    """
    
    def __init__(self, data_dir: str = "data/faces"):
        """
        Initialize Face Registration system
        
        Args:
            data_dir: Directory to store face images and embeddings
        """
        self.data_dir = data_dir
        self.embeddings_file = os.path.join(data_dir, "faces.json")
        # Try multiple face detection methods
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        if not os.path.exists(cascade_path):
            logger.warning(f"Default cascade not found at {cascade_path}")
            # Try alternative path
            cascade_path = "haarcascade_frontalface_default.xml"
        
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            logger.error("Failed to load face cascade classifier")
            # Try to download or use alternative
            logger.info("Trying to use MediaPipe face detection as fallback")
            self.face_cascade = None
        else:
            logger.info("Face cascade classifier loaded successfully")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing embeddings
        self.embeddings_db = self._load_embeddings()
        
        # Log initialization summary
        logger.info("=" * 60)
        logger.info("FACE REGISTRATION SYSTEM INITIALIZED")
        logger.info("=" * 60)
        logger.info(f"Data Directory: {data_dir}")
        logger.info(f"Embeddings File: {self.embeddings_file}")
        logger.info(f"Total Users Loaded: {len([k for k, v in self.embeddings_db.items() if isinstance(v, dict) and 'name' in v])}")
        logger.info(f"Face Cascade Loaded: {'Yes' if self.face_cascade is not None else 'No'}")
        logger.info("=" * 60)
    
    def _load_embeddings(self) -> Dict[str, Any]:
        """Load existing face embeddings from JSON file"""
        if os.path.exists(self.embeddings_file):
            try:
                logger.info(f"Loading existing embeddings database from: {self.embeddings_file}")
                file_size = os.path.getsize(self.embeddings_file)
                logger.info(f"Database file size: {file_size} bytes")
                
                with open(self.embeddings_file, 'r') as f:
                    data = json.load(f)
                
                user_count = len([k for k, v in data.items() if isinstance(v, dict) and "name" in v])
                logger.info(f"Loaded {user_count} users from existing database")
                
                return data
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.warning(f"Could not load existing embeddings: {e}")
                logger.warning("Starting with fresh database")
                return {}
            except Exception as e:
                logger.error(f"Unexpected error loading embeddings: {e}")
                logger.error("Starting with fresh database")
                return {}
        else:
            logger.info("No existing embeddings database found - starting fresh")
            return {}
    
    def _save_embeddings(self):
        """Save face embeddings to JSON file"""
        try:
            logger.info(f"Saving embeddings database to: {self.embeddings_file}")
            logger.info(f"Total users in database: {len(self.embeddings_db)}")
            
            with open(self.embeddings_file, 'w') as f:
                json.dump(self.embeddings_db, f, indent=2)
            
            logger.info(f"Embeddings database saved successfully to {self.embeddings_file}")
            logger.info(f"Database file size: {os.path.getsize(self.embeddings_file)} bytes")
        except Exception as e:
            logger.error(f"Failed to save embeddings database: {e}")
            logger.error(f"Database file: {self.embeddings_file}")
            logger.error(f"Error type: {type(e).__name__}")
    
    def _detect_faces(self, frame: np.ndarray) -> list:
        """
        Detect faces in the frame using OpenCV or MediaPipe fallback
        
        Args:
            frame: Input image frame
            
        Returns:
            List of face bounding boxes (x, y, w, h)
        """
        try:
            # Validate input frame
            if frame is None:
                logger.warning("Frame is None in _detect_faces")
                return []
            
            if frame.size == 0:
                logger.warning("Frame has zero size in _detect_faces")
                return []
            
            # Try OpenCV face detection first
            if self.face_cascade is not None:
                try:
                    # Convert to grayscale
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Detect faces with OpenCV
                    faces = self.face_cascade.detectMultiScale(
                        gray, 
                        scaleFactor=1.1, 
                        minNeighbors=5, 
                        minSize=(30, 30)
                    )
                    
                    # Ensure we return a list
                    if isinstance(faces, tuple):
                        faces = list(faces)
                    elif not isinstance(faces, list):
                        faces = []
                    
                    if len(faces) > 0:
                        logger.debug(f"OpenCV detected {len(faces)} faces")
                        return faces
                        
                except Exception as e:
                    logger.warning(f"OpenCV face detection failed: {e}")
            
            # Fallback to MediaPipe face detection
            try:
                import mediapipe as mp
                mp_face_detection = mp.solutions.face_detection
                mp_drawing = mp.solutions.drawing_utils
                
                with mp_face_detection.FaceDetection(
                    model_selection=0, min_detection_confidence=0.5) as face_detection:
                    
                    # Convert BGR to RGB
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = face_detection.process(rgb_frame)
                    
                    faces = []
                    if results.detections:
                        for detection in results.detections:
                            bbox = detection.location_data.relative_bounding_box
                            h, w, _ = frame.shape
                            x = int(bbox.xmin * w)
                            y = int(bbox.ymin * h)
                            width = int(bbox.width * w)
                            height = int(bbox.height * h)
                            faces.append([x, y, width, height])
                    
                    logger.debug(f"MediaPipe detected {len(faces)} faces")
                    return faces
                    
            except Exception as e:
                logger.warning(f"MediaPipe face detection failed: {e}")
            
            # If both methods fail, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Error in _detect_faces: {e}")
            return []
    
    def _validate_face_quality(self, frame: np.ndarray, face_bbox: Tuple[int, int, int, int]) -> bool:
        """
        Validate face image quality for registration
        
        Args:
            frame: Input image frame
            face_bbox: Face bounding box (x, y, w, h)
            
        Returns:
            True if face quality is acceptable
        """
        x, y, w, h = face_bbox
        
        # Check minimum size
        if w < 100 or h < 100:
            return False
        
        # Extract face region
        face_region = frame[y:y+h, x:x+w]
        
        # Check if face region is not empty
        if face_region.size == 0:
            return False
        
        # Convert to grayscale for brightness check
        gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        
        # Check brightness (avoid too dark or too bright images)
        mean_brightness = np.mean(gray_face)
        if mean_brightness < 30 or mean_brightness > 220:
            return False
        
        # Check contrast (standard deviation)
        contrast = np.std(gray_face)
        if contrast < 20:
            return False
        
        return True
    
    def _extract_embedding(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face embedding using DeepFace MobileNet
        
        Args:
            face_image: Face image (BGR format)
            
        Returns:
            Face embedding vector or None if extraction fails
        """
        try:
            # Convert BGR to RGB for DeepFace
            rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            
            # Extract embedding using VGG-Face model (more reliable)
            embedding = DeepFace.represent(
                img_path=rgb_image,
                model_name="VGG-Face",
                enforce_detection=False,
                align=True
            )
            
            if embedding and len(embedding) > 0:
                return np.array(embedding[0]["embedding"])
            else:
                logger.warning("No embedding extracted from face image")
                return None
                
        except Exception as e:
            logger.error(f"Failed to extract embedding: {e}")
            return None
    
    def capture_face(self, user_name: str, user_id: str = None) -> bool:
        """
        Capture face image from webcam and register user
        
        Args:
            user_name: Name of the user to register
            user_id: Optional user ID (if not provided, uses timestamp)
            
        Returns:
            True if registration successful, False otherwise
        """
        if not user_id:
            user_id = f"user_{int(datetime.now().timestamp())}"
        
        # Log webcam capture attempt
        logger.info("=" * 60)
        logger.info("STARTING WEBCAM FACE CAPTURE REGISTRATION")
        logger.info("=" * 60)
        logger.info(f"User Name: {user_name}")
        logger.info(f"User ID: {user_id}")
        logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # Initialize webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logger.error("Could not open webcam - Registration failed")
            return False
        
        # Set webcam properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        logger.info("Webcam initialized successfully")
        logger.info(f"Webcam properties: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)} @ {cap.get(cv2.CAP_PROP_FPS)}fps")
        
        # Give webcam time to initialize
        import time
        time.sleep(1)
        
        logger.info(f"Starting face capture for user: {user_name}")
        logger.info("Press 'SPACE' to capture, 'ESC' to cancel")
        
        try:
            frame_count = 0
            while True:
                try:
                    ret, frame = cap.read()
                    frame_count += 1
                    
                    if not ret:
                        logger.error(f"Failed to grab frame {frame_count}")
                        # Try to reinitialize webcam if it fails
                        if frame_count > 10:  # After 10 failed attempts
                            logger.error("Too many failed frame reads, reinitializing webcam")
                            cap.release()
                            cap = cv2.VideoCapture(0)
                            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                            cap.set(cv2.CAP_PROP_FPS, 30)
                            frame_count = 0
                        continue
                    
                    # Check if frame is valid
                    if frame is None:
                        logger.error(f"Frame {frame_count} is None, skipping iteration")
                        continue
                    
                    # Ensure frame has valid dimensions
                    if frame.size == 0:
                        logger.error(f"Frame {frame_count} has zero size, skipping iteration")
                        continue
                    
                    # Log frame info occasionally
                    if frame_count % 30 == 0:  # Every 30 frames
                        logger.info(f"Frame {frame_count}: shape={frame.shape}, dtype={frame.dtype}")
                    
                    # Detect faces in frame
                    try:
                        faces = self._detect_faces(frame)
                    except Exception as e:
                        logger.error(f"Face detection failed on frame {frame_count}: {e}")
                        faces = []
                
                except Exception as e:
                    logger.error(f"Error processing frame {frame_count}: {e}")
                    faces = []
                
                # Draw face detection rectangles
                for (x, y, w, h) in faces:
                    color = (0, 255, 0) if self._validate_face_quality(frame, (x, y, w, h)) else (0, 0, 255)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                
                # Add instructions and status to frame
                cv2.putText(frame, "Press SPACE to capture, ESC to cancel", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"User: {user_name}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Add face detection status
                if len(faces) == 0:
                    status_text = "No face detected"
                    status_color = (0, 0, 255)  # Red
                elif len(faces) == 1:
                    if self._validate_face_quality(frame, faces[0]):
                        status_text = "Face detected - Press SPACE to capture!"
                        status_color = (0, 255, 0)  # Green
                    else:
                        status_text = "Face detected but quality too low"
                        status_color = (0, 165, 255)  # Orange
                else:
                    status_text = f"Multiple faces detected ({len(faces)})"
                    status_color = (0, 0, 255)  # Red
                
                cv2.putText(frame, status_text, 
                           (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
                
                # Show frame
                cv2.imshow('Face Registration - Press SPACE to capture', frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                
                if key == 27:  # ESC key
                    logger.info("=" * 60)
                    logger.info("WEBCAM FACE CAPTURE REGISTRATION CANCELLED BY USER")
                    logger.info("=" * 60)
                    logger.info(f"User: {user_name}")
                    logger.info(f"User ID: {user_id}")
                    logger.info(f"Cancellation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.info("=" * 60)
                    break
                elif key == 32:  # SPACE key
                    logger.info(f"SPACE key pressed! Detected {len(faces)} faces")
                    
                    if len(faces) == 1:
                        # Single face detected, proceed with registration
                        x, y, w, h = faces[0]
                        logger.info(f"Single face detected at position: ({x}, {y}, {w}, {h})")
                        
                        if self._validate_face_quality(frame, (x, y, w, h)):
                            logger.info("Face quality validation passed, proceeding with registration")
                            # Extract face region
                            face_image = frame[y:y+h, x:x+w]
                            
                            # Extract embedding
                            logger.info("Extracting face embedding...")
                            embedding = self._extract_embedding(face_image)
                            
                            if embedding is not None:
                                logger.info(f"Embedding extracted successfully, length: {len(embedding)}")
                                # Save face image
                                image_filename = f"{user_id}_{user_name}.jpg"
                                image_path = os.path.join(self.data_dir, image_filename)
                                cv2.imwrite(image_path, face_image)
                                
                                # Save embedding and metadata
                                self.embeddings_db[user_id] = {
                                    "name": user_name,
                                    "embedding": embedding.tolist(),
                                    "image_path": image_filename,
                                    "registration_date": datetime.now().isoformat(),
                                    "face_bbox": [x, y, w, h]
                                }
                                
                                # Save to file
                                self._save_embeddings()
                                
                                # Log successful registration with comprehensive details
                                logger.info("=" * 60)
                                logger.info("WEBCAM FACE CAPTURE REGISTRATION COMPLETED SUCCESSFULLY")
                                logger.info("=" * 60)
                                logger.info(f"User ID: {user_id}")
                                logger.info(f"User Name: {user_name}")
                                logger.info(f"Registration Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                logger.info(f"Face Image: {image_filename}")
                                logger.info(f"Image Path: {image_path}")
                                logger.info(f"Embedding Vector Length: {len(embedding)}")
                                logger.info(f"Face Bounding Box: x={x}, y={y}, w={w}, h={h}")
                                logger.info(f"Database File: {self.embeddings_file}")
                                logger.info("=" * 60)
                                
                                # Show success message
                                cv2.putText(frame, "Registration Successful!", 
                                           (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                                cv2.imshow('Registration Successful!', frame)
                                cv2.waitKey(2000)  # Show for 2 seconds
                                
                                return True
                            else:
                                logger.error("Failed to extract face embedding")
                                cv2.putText(frame, "Failed to extract embedding", 
                                           (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        else:
                            logger.warning("Face quality validation failed")
                            cv2.putText(frame, "Face quality too low", 
                                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    elif len(faces) == 0:
                        logger.info("SPACE pressed but no face detected")
                        cv2.putText(frame, "No face detected", 
                                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    else:
                        logger.info(f"SPACE pressed but {len(faces)} faces detected (need exactly 1)")
                        cv2.putText(frame, "Multiple faces detected", 
                                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            logger.info("Webcam resources released and windows closed")
        
        logger.info("=" * 60)
        logger.info("WEBCAM FACE CAPTURE REGISTRATION ENDED")
        logger.info("=" * 60)
        logger.info(f"User: {user_name}")
        logger.info(f"User ID: {user_id}")
        logger.info(f"Final Status: {'SUCCESS' if 'success' in locals() else 'FAILED'}")
        logger.info("=" * 60)
        
        return False
    
    def user_exists(self, username: str) -> bool:
        """Check if a user already exists"""
        return username in self.embeddings_db
    
    def _update_cache(self, username: str, embedding: np.ndarray, user_data: Dict[str, Any]):
        """Update in-memory cache with new user data"""
        try:
            # This method would update any in-memory caches
            # For now, we just log the update
            logger.info(f"Cache updated for user: {username}")
        except Exception as e:
            logger.warning(f"Failed to update cache for {username}: {e}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            total_users = len(self.embeddings_db)
            return {
                "total_users": total_users,
                "database_path": str(self.embeddings_file),
                "faces_directory": str(self.data_dir),
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all registered users with their details"""
        try:
            users = []
            for user_id, data in self.embeddings_db.items():
                if isinstance(data, dict) and "name" in data:
                    users.append({
                        "user_id": user_id,
                        "name": data.get("name", "Unknown"),
                        "registration_date": data.get("registration_date", "Unknown"),
                        "image_path": data.get("image_path", "Unknown")
                    })
            return users
        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            return []
    
    def register_from_image(self, image_path: str, user_name: str, user_id: str = None) -> bool:
        """
        Register user from an existing image file
        
        Args:
            image_path: Path to the image file
            user_name: Name of the user
            user_id: Optional user ID
            
        Returns:
            True if registration successful, False otherwise
        """
        if not user_id:
            user_id = f"user_{int(datetime.now().timestamp())}"
        
        # Log registration attempt
        logger.info(f"Starting user registration process - User: {user_name}, ID: {user_id}")
        logger.info(f"Image path: {image_path}")
        
        try:
            # Load image
            frame = cv2.imread(image_path)
            if frame is None:
                logger.error(f"Could not load image: {image_path}")
                return False
            
            # Detect faces
            logger.info("Detecting faces in uploaded image...")
            faces = self._detect_faces(frame)
            
            logger.info(f"Face detection completed - Found {len(faces)} face(s)")
            
            if len(faces) != 1:
                logger.error(f"Expected 1 face, found {len(faces)} - Registration failed")
                return False
            
            x, y, w, h = faces[0]
            logger.info(f"Face detected at position: x={x}, y={y}, w={w}, h={h}")
            
            logger.info("Validating face image quality...")
            if not self._validate_face_quality(frame, (x, y, w, h)):
                logger.error("Face quality validation failed - Image quality too low for registration")
                return False
            
            logger.info("Face quality validation passed")
            
            # Extract face region
            face_image = frame[y:y+h, x:x+w]
            
            # Extract embedding
            logger.info("Extracting face embedding using DeepFace...")
            embedding = self._extract_embedding(face_image)
            
            if embedding is None:
                logger.error("Failed to extract face embedding - Registration cannot proceed")
                return False
            
            logger.info(f"Face embedding extracted successfully - Vector length: {len(embedding)}")
            
            # Save face image
            image_filename = f"{user_id}_{user_name}.jpg"
            save_path = os.path.join(self.data_dir, image_filename)
            logger.info(f"Saving face image to: {save_path}")
            cv2.imwrite(save_path, face_image)
            
            # Prepare user metadata
            registration_date = datetime.now()
            user_metadata = {
                "name": user_name,
                "embedding": embedding.tolist(),
                "image_path": image_filename,
                "registration_date": registration_date.isoformat(),
                "face_bbox": [x, y, w, h]
            }
            
            logger.info(f"User metadata prepared - Name: {user_name}, ID: {user_id}, Date: {registration_date}")
            
            # Save embedding and metadata to database
            self.embeddings_db[user_id] = user_metadata
            logger.info("User data added to in-memory database")
            
            # Save to file
            self._save_embeddings()
            
            # Log successful registration with comprehensive details
            logger.info("=" * 60)
            logger.info("USER REGISTRATION COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            logger.info(f"User ID: {user_id}")
            logger.info(f"User Name: {user_name}")
            logger.info(f"Registration Date: {registration_date.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"Face Image: {image_filename}")
            logger.info(f"Image Path: {save_path}")
            logger.info(f"Embedding Vector Length: {len(embedding)}")
            logger.info(f"Face Bounding Box: x={x}, y={y}, w={w}, h={h}")
            logger.info(f"Database File: {self.embeddings_file}")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error("=" * 60)
            logger.error("USER REGISTRATION FAILED")
            logger.error("=" * 60)
            logger.error(f"User: {user_name}")
            logger.error(f"User ID: {user_id}")
            logger.error(f"Error: {str(e)}")
            logger.error(f"Error Type: {type(e).__name__}")
            logger.error(f"Image Path: {image_path}")
            logger.error("=" * 60)
            return False
    
    def get_registered_users(self) -> Dict[str, str]:
        """
        Get list of registered users
        
        Returns:
            Dictionary mapping user IDs to names
        """
        users = {}
        for user_id, data in self.embeddings_db.items():
            # Process all user entries (not just those starting with "user_")
            if isinstance(data, dict) and "name" in data:
                users[user_id] = data["name"]
        return users
    
    def get_user_embedding(self, user_id: str) -> Optional[np.ndarray]:
        """
        Get embedding for a specific user
        
        Args:
            user_id: User ID to look up
            
        Returns:
            User's face embedding vector or None if not found
        """
        if user_id in self.embeddings_db:
            return np.array(self.embeddings_db[user_id]["embedding"])
        return None
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a registered user
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        if user_id not in self.embeddings_db:
            logger.warning(f"User ID {user_id} not found")
            return False
        
        try:
            # Get image path
            image_filename = self.embeddings_db[user_id]["image_path"]
            image_path = os.path.join(self.data_dir, image_filename)
            
            # Delete image file
            if os.path.exists(image_path):
                os.remove(image_path)
                logger.info(f"Deleted image file: {image_path}")
            
            # Remove from database
            del self.embeddings_db[user_id]
            
            # Save updated database
            self._save_embeddings()
            
            logger.info(f"Successfully deleted user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            return False


def main():
    """Main function for testing the registration module"""
    print("🧩 EyeD Face Registration Module")
    print("=" * 40)
    
    # Initialize registration system
    registration = FaceRegistration()
    
    while True:
        print("\nOptions:")
        print("1. Register new user (webcam)")
        print("2. Register from image file")
        print("3. List registered users")
        print("4. Delete user")
        print("5. Exit")
        
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
            users = registration.get_registered_users()
            if users:
                print("\nRegistered Users:")
                for user_id, name in users.items():
                    print(f"  {user_id}: {name}")
            else:
                print("No users registered yet.")
        
        elif choice == "4":
            user_id = input("Enter user ID to delete: ").strip()
            if user_id:
                success = registration.delete_user(user_id)
                if success:
                    print(f"✅ User {user_id} deleted successfully!")
                else:
                    print(f"❌ Failed to delete user {user_id}")
        
        elif choice == "5":
            print("👋 Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
