"""
Final test script to verify face recognition with correct confidence threshold
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.modules.recognition import FaceRecognition
import cv2
import numpy as np

def test_recognition_final():
    """Test face recognition with correct confidence threshold"""
    
    print("🔍 Final Test: Face Recognition System...")
    
    # Initialize recognition system with correct threshold for VGG-Face
    recognition = FaceRecognition(confidence_threshold=0.1, use_mediapipe=True)
    
    # Load known faces
    print("📚 Loading known faces...")
    if not recognition.load_known_faces("data/faces"):
        print("❌ Failed to load known faces")
        return False
    
    print(f"✅ Loaded {len(recognition.known_faces)} known faces")
    
    # Show loaded faces info
    for user_id, embedding in recognition.known_faces.items():
        user_name = recognition.known_names.get(user_id, "Unknown")
        print(f"  - {user_name}: {embedding.shape} dimensions")
    
    # Test with a sample image if available
    test_image_path = "data/faces/Hasanth.jpg"
    if os.path.exists(test_image_path):
        print(f"\n🧪 Testing recognition with {test_image_path}")
        
        # Load test image
        test_image = cv2.imread(test_image_path)
        if test_image is None:
            print("❌ Failed to load test image")
            return False
        
        # Test recognition
        result = recognition.recognize_face(test_image)
        
        if result:
            print(f"✅ Recognition successful!")
            print(f"  - User: {result.user_name}")
            print(f"  - Confidence: {result.confidence:.3f}")
            print(f"  - Processing time: {result.processing_time_ms:.1f}ms")
            
            # Check if confidence is above threshold
            if result.confidence >= 0.1:
                print(f"🎯 Confidence {result.confidence:.3f} is above threshold 0.1 - Perfect!")
            else:
                print(f"⚠️ Confidence {result.confidence:.3f} is below threshold 0.1")
        else:
            print("❌ Recognition failed")
            
        # Test embedding extraction
        print(f"\n🔍 Testing embedding extraction...")
        embeddings = recognition.extract_embeddings(test_image)
        if embeddings is not None:
            print(f"✅ Embeddings extracted: {embeddings.shape}")
            print(f"  - Range: [{embeddings.min():.4f}, {embeddings.max():.4f}]")
        else:
            print("❌ Failed to extract embeddings")
    
    return True

if __name__ == "__main__":
    test_recognition_final()
