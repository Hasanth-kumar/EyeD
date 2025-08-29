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
import cv2

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

def run_webcam_recognition(camera_id: int = 0, debug: bool = False):
    """Run real-time webcam face recognition"""
    print("🎥 Initializing webcam...")
    
    # Import FaceRecognition here to avoid circular import issues
    from modules.recognition import FaceRecognition
    
    # Initialize face recognition system
    recognition = FaceRecognition(confidence_threshold=0.6, use_mediapipe=True)
    
    # Load known faces
    if not recognition.load_known_faces("data/faces"):
        print("⚠️ No known faces loaded. Please register users first.")
        print("   Use: python main.py --mode register")
        return
    
    # Initialize webcam
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"❌ Failed to open camera {camera_id}")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("✅ Webcam initialized successfully")
    print("📱 Press 'q' to quit, 's' to save frame, 'r' to reload faces")
    print("🎯 Face detection and recognition active...")
    
    frame_count = 0
    fps_start_time = cv2.getTickCount()
    fps = 0.0  # Initialize fps variable
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read frame from webcam")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Process frame for face recognition
            recognition_results = recognition.recognize_user(frame)
            
            # Draw results on frame
            frame = draw_recognition_results(frame, recognition_results, debug)
            
            # Calculate and display FPS
            frame_count += 1
            if frame_count % 30 == 0:  # Update FPS every 30 frames
                current_time = cv2.getTickCount()
                fps = 30.0 / ((current_time - fps_start_time) / cv2.getTickFrequency())
                fps_start_time = current_time
                frame_count = 0
            
            # Display FPS
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display frame
            cv2.imshow("EyeD - Live Face Recognition", frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("👋 Quitting webcam mode...")
                break
            elif key == ord('s'):
                save_frame(frame, recognition_results)
            elif key == ord('r'):
                print("🔄 Reloading known faces...")
                recognition.load_known_faces("data/faces")
                print(f"✅ Reloaded {len(recognition.known_faces)} faces")
    
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"❌ Webcam recognition error: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Webcam mode closed")

def draw_recognition_results(frame, results, debug=False):
    """Draw recognition results on frame"""
    for result in results:
        x, y, w, h = result['bbox']
        name = result['name']
        confidence = result['confidence']
        recognized = result['recognized']
        
        # Choose color based on recognition status
        if recognized:
            color = (0, 255, 0)  # Green for recognized
            thickness = 2
        else:
            color = (0, 0, 255)  # Red for unknown
            thickness = 1
        
        # Draw bounding box
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
        
        # Draw name and confidence
        label = f"{name}: {confidence:.2f}"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        
        # Background rectangle for text
        cv2.rectangle(frame, (x, y - label_size[1] - 10), 
                     (x + label_size[0], y), color, -1)
        
        # Text
        cv2.putText(frame, label, (x, y - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Debug info
        if debug:
            cv2.putText(frame, f"Box: ({x},{y},{w},{h})", (x, y + h + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
    
    return frame

def save_frame(frame, results):
    """Save current frame with recognition results"""
    try:
        # Create data/faces directory if it doesn't exist
        faces_dir = Path("data/faces")
        faces_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp-based filename
        timestamp = cv2.getTickCount()
        filename = faces_dir / f"capture_{timestamp}.jpg"
        
        # Save frame
        cv2.imwrite(str(filename), frame)
        print(f"💾 Frame saved as {filename}")
        
        # Save results to log
        if results:
            print("📊 Recognition results:")
            for result in results:
                print(f"  - {result['name']}: {result['confidence']:.3f}")
        
        # Also save recognition metadata
        metadata_file = faces_dir / f"capture_{timestamp}_metadata.txt"
        with open(metadata_file, 'w') as f:
            f.write(f"Capture Time: {timestamp}\n")
            f.write(f"Frame Size: {frame.shape[1]}x{frame.shape[0]}\n")
            f.write("Recognition Results:\n")
            for result in results:
                f.write(f"  - {result['name']}: {result['confidence']:.3f}\n")
        
        print(f"📝 Metadata saved as {metadata_file}")
        
    except Exception as e:
        print(f"❌ Failed to save frame: {e}")

def main():
    """Main entry point for EyeD application"""
    parser = argparse.ArgumentParser(description="EyeD AI Attendance System")
    parser.add_argument("--mode", choices=["webcam", "dashboard", "register", "test_db", "recognition"], 
                       default="webcam", help="Application mode")
    parser.add_argument("--camera", type=int, default=0, help="Camera device ID")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    print("👁️ EyeD - AI Attendance System")
    print("=" * 40)
    
    if args.mode == "webcam":
        print("🎥 Starting webcam mode...")
        try:
            from modules.recognition import FaceRecognition
            run_webcam_recognition(args.camera, args.debug)
        except ImportError as e:
            print(f"❌ Failed to import recognition module: {e}")
        except Exception as e:
            print(f"❌ Webcam mode failed: {e}")
        
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
    
    elif args.mode == "recognition":
        print("🧠 Testing Face Recognition Module...")
        try:
            from modules.recognition import FaceRecognition
            import numpy as np
            
            print("\n🧩 Face Recognition Test Mode")
            print("=" * 30)
            print("1. Test recognition initialization")
            print("2. Test face detection")
            print("3. Test face recognition from image")
            print("4. Test embedding comparison")
            print("5. Test complete recognition pipeline")
            print("6. Run recognition on test image")
            print("7. Exit")
            
            while True:
                choice = input("\nEnter your choice (1-7): ").strip()
                
                if choice == "1":
                    print("\n📋 Testing Recognition Initialization...")
                    recognition = FaceRecognition(confidence_threshold=0.6)
                    print(f"✅ Recognition system initialized")
                    print(f"✅ Confidence threshold: {recognition.confidence_threshold}")
                    print(f"✅ Face cascade loaded: {recognition.face_cascade is not None}")
                    
                    # Try to load known faces
                    success = recognition.load_known_faces()
                    if success:
                        stats = recognition.get_recognition_stats()
                        print(f"✅ Loaded {stats['known_faces_count']} known faces")
                        print(f"✅ Total known names: {stats['total_known_names']}")
                    else:
                        print("⚠️ No known faces loaded (this is normal if no users registered)")
                
                elif choice == "2":
                    print("\n📋 Testing Face Detection...")
                    recognition = FaceRecognition()
                    
                    # Create a test image with a simple pattern
                    test_image = np.zeros((300, 300, 3), dtype=np.uint8)
                    test_image[:] = (128, 128, 128)  # Gray background
                    
                    # Add a simple "face-like" rectangle
                    cv2.rectangle(test_image, (100, 100), (200, 200), (255, 255, 255), -1)
                    
                    faces = recognition.detect_faces(test_image)
                    print(f"✅ Face detection test completed")
                    print(f"✅ Detected faces: {len(faces)}")
                    
                    if faces:
                        for i, (x, y, w, h) in enumerate(faces):
                            print(f"   - Face {i+1}: ({x}, {y}, {w}, {h})")
                
                elif choice == "3":
                    print("\n📋 Testing Face Recognition from Image...")
                    recognition = FaceRecognition()
                    
                    # Check if there are any registered faces
                    success = recognition.load_known_faces()
                    if not success:
                        print("⚠️ No known faces to test with. Please register some users first.")
                        continue
                    
                    # Ask for test image path
                    image_path = input("Enter path to test image (or press Enter to skip): ").strip()
                    if not image_path:
                        print("Skipping image recognition test.")
                        continue
                    
                    if not os.path.exists(image_path):
                        print(f"❌ Image file not found: {image_path}")
                        continue
                    
                    print(f"🔍 Processing image: {image_path}")
                    results = recognition.recognize_from_image(image_path)
                    
                    if results:
                        print(f"✅ Recognition completed. Found {len(results)} faces:")
                        for i, result in enumerate(results):
                            print(f"   - Face {i+1}: {result['name']} (confidence: {result['confidence']:.3f})")
                            print(f"     Bounding box: {result['bbox']}")
                            print(f"     Recognized: {'✅' if result['recognized'] else '❌'}")
                    else:
                        print("⚠️ No faces detected in the image")
                
                elif choice == "4":
                    print("\n📋 Testing Embedding Comparison...")
                    recognition = FaceRecognition()
                    
                    # Create mock embeddings for testing
                    emb1 = np.random.rand(4096).astype(np.float32)
                    emb2 = np.random.rand(4096).astype(np.float32)
                    emb3 = emb1.copy()  # Identical to emb1
                    
                    # Test different comparisons
                    similarity_12 = recognition.compare_embeddings(emb1, emb2)
                    similarity_13 = recognition.compare_embeddings(emb1, emb3)
                    similarity_11 = recognition.compare_embeddings(emb1, emb1)
                    
                    print(f"✅ Embedding comparison tests completed:")
                    print(f"   - Random vs Random: {similarity_12:.3f}")
                    print(f"   - Random vs Copy: {similarity_13:.3f}")
                    print(f"   - Same vs Same: {similarity_11:.3f}")
                    
                    # Validate results
                    if similarity_11 > 0.99:
                        print("✅ Self-similarity test passed (should be ~1.0)")
                    else:
                        print("⚠️ Self-similarity test may have issues")
                
                elif choice == "5":
                    print("\n📋 Testing Complete Recognition Pipeline...")
                    recognition = FaceRecognition()
                    
                    # Load known faces
                    success = recognition.load_known_faces()
                    if not success:
                        print("⚠️ No known faces to test with. Please register some users first.")
                        continue
                    
                    # Create a test frame
                    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    test_frame[:] = (100, 100, 100)  # Dark gray background
                    
                    # Process the frame
                    results = recognition.recognize_user(test_frame)
                    print(f"✅ Pipeline test completed")
                    print(f"✅ Processed frame with {len(results)} results")
                    
                    if results:
                        for i, result in enumerate(results):
                            print(f"   - Result {i+1}: {result}")
                
                elif choice == "6":
                    print("\n📋 Running Recognition on Test Image...")
                    recognition = FaceRecognition()
                    
                    # Check if there are any registered faces
                    success = recognition.load_known_faces()
                    if not success:
                        print("⚠️ No known faces to test with. Please register some users first.")
                        continue
                    
                    # Look for test images in the faces directory
                    faces_dir = Path("data/faces")
                    if faces_dir.exists():
                        image_files = list(faces_dir.glob("*.jpg")) + list(faces_dir.glob("*.jpeg")) + list(faces_dir.glob("*.png"))
                        
                        if image_files:
                            print(f"Found {len(image_files)} test images:")
                            for i, img_path in enumerate(image_files):
                                print(f"   {i+1}. {img_path.name}")
                            
                            try:
                                choice_idx = int(input(f"Select image (1-{len(image_files)}): ")) - 1
                                if 0 <= choice_idx < len(image_files):
                                    selected_image = image_files[choice_idx]
                                    print(f"🔍 Processing: {selected_image.name}")
                                    
                                    results = recognition.recognize_from_image(str(selected_image))
                                    
                                    if results:
                                        print(f"✅ Recognition completed. Found {len(results)} faces:")
                                        for i, result in enumerate(results):
                                            print(f"   - Face {i+1}: {result['name']} (confidence: {result['confidence']:.3f})")
                                            print(f"     Bounding box: {result['bbox']}")
                                            print(f"     Recognized: {'✅' if result['recognized'] else '❌'}")
                                    else:
                                        print("⚠️ No faces detected in the image")
                                else:
                                    print("❌ Invalid selection")
                            except ValueError:
                                print("❌ Invalid input")
                        else:
                            print("⚠️ No test images found in data/faces/ directory")
                    else:
                        print("⚠️ No faces directory found")
                
                elif choice == "7":
                    print("👋 Returning to main menu...")
                    break
                
                else:
                    print("Invalid choice. Please try again.")
                    
        except ImportError as e:
            print(f"❌ Failed to import recognition module: {e}")
            print("Make sure the FaceRecognition module is properly implemented")
        except Exception as e:
            print(f"❌ Face recognition test error: {e}")
            import traceback
            traceback.print_exc()
    
    elif args.mode == "test_db":
        print("🧪 Testing Face Database Module...")
        try:
            from modules.face_db import FaceDatabase
            import numpy as np
            
            print("\n🧩 Face Database Test Mode")
            print("=" * 30)
            print("1. Test database initialization")
            print("2. Test user registration")
            print("3. Test embedding loading")
            print("4. Test database verification")
            print("5. Test performance")
            print("6. Run full test suite")
            print("7. Exit")
            
            while True:
                choice = input("\nEnter your choice (1-7): ").strip()
                
                if choice == "1":
                    print("\n📋 Testing Database Initialization...")
                    test_dir = "data/test_db"
                    db = FaceDatabase(test_dir)
                    print(f"✅ Database initialized in: {test_dir}")
                    print(f"✅ Data directory: {os.path.exists(test_dir)}")
                    print(f"✅ Backup directory: {os.path.exists(os.path.join(test_dir, 'backups'))}")
                    
                elif choice == "2":
                    print("\n📋 Testing User Registration...")
                    test_dir = "data/test_db"
                    db = FaceDatabase(test_dir)
                    
                    # Create mock embedding
                    mock_embedding = np.random.rand(4096).astype(np.float32)
                    
                    success = db.register_user(
                        name="Test User",
                        user_id="test_001",
                        embedding=mock_embedding,
                        image_path="data/test_db/test_user.jpg",
                        metadata={"test": True, "created": "2024-01-01"}
                    )
                    
                    if success:
                        print("✅ Test user registered successfully!")
                        user_data = db.get_user_data("test_001")
                        print(f"   - Name: {user_data.get('name')}")
                        print(f"   - Test flag: {user_data.get('test')}")
                    else:
                        print("❌ Test user registration failed!")
                
                elif choice == "3":
                    print("\n📋 Testing Embedding Loading...")
                    test_dir = "data/test_db"
                    db = FaceDatabase(test_dir)
                    
                    embeddings = db.load_embeddings()
                    print(f"✅ Loaded {len(embeddings)} embeddings")
                    
                    if embeddings:
                        for user_id, embedding in embeddings.items():
                            print(f"   - {user_id}: {embedding.shape}")
                    else:
                        print("   No embeddings found")
                
                elif choice == "4":
                    print("\n📋 Testing Database Verification...")
                    test_dir = "data/test_db"
                    db = FaceDatabase(test_dir)
                    
                    verification = db.verify_embeddings()
                    print(f"✅ Integrity check: {'PASSED' if verification['integrity_check'] else 'FAILED'}")
                    print(f"✅ Total users: {verification['total_users']}")
                    print(f"✅ Total embeddings: {verification['total_embeddings']}")
                    
                    if verification['issues']:
                        print("   Issues found:")
                        for issue in verification['issues']:
                            print(f"   - {issue}")
                    
                    if verification['warnings']:
                        print("   Warnings:")
                        for warning in verification['warnings']:
                            print(f"   - {warning}")
                
                elif choice == "5":
                    print("\n📋 Testing Performance...")
                    test_dir = "data/test_db"
                    db = FaceDatabase(test_dir)
                    
                    import time
                    start_time = time.time()
                    
                    for _ in range(5):
                        db.load_embeddings()
                    
                    load_time = time.time() - start_time
                    print(f"✅ 5 embedding loads in {load_time:.4f} seconds")
                    print(f"✅ Average load time: {load_time/5:.4f} seconds")
                
                elif choice == "6":
                    print("\n📋 Running Full Test Suite...")
                    print("This will run the comprehensive test script...")
                    confirm = input("Continue? (y/n): ").strip().lower()
                    if confirm == 'y':
                        print("Running test_day3_face_database.py...")
                        os.system("python test_day3_face_database.py")
                    else:
                        print("Test cancelled.")
                
                elif choice == "7":
                    print("👋 Returning to main menu...")
                    break
                
                else:
                    print("Invalid choice. Please try again.")
                    
        except ImportError as e:
            print(f"❌ Failed to import face database module: {e}")
            print("Make sure the FaceDatabase module is properly implemented")
        except Exception as e:
            print(f"❌ Face database test error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n✅ EyeD system initialized successfully!")
    print("💡 Use --help for more options")

if __name__ == "__main__":
    main()
