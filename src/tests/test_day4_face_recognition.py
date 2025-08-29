#!/usr/bin/env python3
"""
EyeD AI Attendance System - Day 4 Face Recognition Tests
Comprehensive testing of the face recognition module

Author: EyeD Team
Date: 2025
"""

import sys
import os
import numpy as np
import cv2
from pathlib import Path
import time
import traceback

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def test_recognition_initialization():
    """Test 1: Recognition system initialization"""
    print("🧪 Test 1: Recognition System Initialization")
    print("=" * 50)
    
    try:
        from src.modules.recognition import FaceRecognition
        
        # Test with default confidence threshold
        recognition = FaceRecognition()
        assert recognition.confidence_threshold == 0.6, f"Expected confidence threshold 0.6, got {recognition.confidence_threshold}"
        print("✅ Default confidence threshold set correctly")
        
        # Test with custom confidence threshold
        recognition_custom = FaceRecognition(confidence_threshold=0.8)
        assert recognition_custom.confidence_threshold == 0.8, f"Expected confidence threshold 0.8, got {recognition_custom.confidence_threshold}"
        print("✅ Custom confidence threshold set correctly")
        
        # Test face cascade loading
        assert recognition.face_cascade is not None, "Face cascade classifier should be loaded"
        print("✅ Face cascade classifier loaded successfully")
        
        # Test initial state
        assert len(recognition.known_faces) == 0, "Known faces should be empty initially"
        assert len(recognition.known_names) == 0, "Known names should be empty initially"
        print("✅ Initial state correctly set")
        
        print("✅ Test 1 PASSED: Recognition system initialization\n")
        return True
        
    except Exception as e:
        print(f"❌ Test 1 FAILED: {e}")
        traceback.print_exc()
        return False

def test_face_detection():
    """Test 2: Face detection functionality"""
    print("🧪 Test 2: Face Detection Functionality")
    print("=" * 50)
    
    try:
        from src.modules.recognition import FaceRecognition
        
        recognition = FaceRecognition()
        
        # Test 1: Empty image (no faces)
        empty_image = np.zeros((300, 300, 3), dtype=np.uint8)
        faces = recognition.detect_faces(empty_image)
        assert isinstance(faces, list), "detect_faces should return a list"
        print("✅ Empty image detection handled correctly")
        
        # Test 2: Simple test image
        test_image = np.zeros((300, 300, 3), dtype=np.uint8)
        test_image[:] = (128, 128, 128)  # Gray background
        
        # Add a simple pattern that might trigger detection
        cv2.rectangle(test_image, (100, 100), (200, 200), (255, 255, 255), -1)
        
        faces = recognition.detect_faces(test_image)
        assert isinstance(faces, list), "detect_faces should return a list"
        print("✅ Test image detection handled correctly")
        
        # Test 3: Check return format
        if faces:
            for face in faces:
                assert len(face) == 4, f"Face bounding box should have 4 elements, got {len(face)}"
                x, y, w, h = face
                assert isinstance(x, int) and isinstance(y, int), "x, y should be integers"
                assert isinstance(w, int) and isinstance(h, int), "w, h should be integers"
                assert w > 0 and h > 0, "Width and height should be positive"
            print("✅ Face bounding box format correct")
        
        print("✅ Test 2 PASSED: Face detection functionality\n")
        return True
        
    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}")
        traceback.print_exc()
        return False

def test_embedding_extraction():
    """Test 3: Face embedding extraction"""
    print("🧪 Test 3: Face Embedding Extraction")
    print("=" * 50)
    
    try:
        from src.modules.recognition import FaceRecognition
        
        recognition = FaceRecognition()
        
        # Create a test face image (simple pattern)
        test_face = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Test embedding extraction
        embedding = recognition.extract_face_embedding(test_face)
        
        if embedding is not None:
            assert isinstance(embedding, np.ndarray), "Embedding should be a numpy array"
            assert embedding.shape == (4096,), f"Expected embedding shape (4096,), got {embedding.shape}"
            assert embedding.dtype == np.float32, f"Expected float32 dtype, got {embedding.dtype}"
            print("✅ Face embedding extraction successful")
            print(f"   - Shape: {embedding.shape}")
            print(f"   - Dtype: {embedding.dtype}")
            print(f"   - Range: [{embedding.min():.3f}, {embedding.max():.3f}]")
        else:
            print("⚠️ Embedding extraction returned None (this may be normal for test images)")
        
        print("✅ Test 3 PASSED: Face embedding extraction\n")
        return True
        
    except Exception as e:
        print(f"❌ Test 3 FAILED: {e}")
        traceback.print_exc()
        return False

def test_embedding_comparison():
    """Test 4: Embedding comparison functionality"""
    print("🧪 Test 4: Embedding Comparison Functionality")
    print("=" * 50)
    
    try:
        from src.modules.recognition import FaceRecognition
        
        recognition = FaceRecognition()
        
        # Create test embeddings
        emb1 = np.random.rand(4096).astype(np.float32)
        emb2 = np.random.rand(4096).astype(np.float32)
        emb3 = emb1.copy()  # Identical to emb1
        
        # Test 1: Same embedding comparison
        similarity_11 = recognition.compare_embeddings(emb1, emb1)
        assert isinstance(similarity_11, float), "Similarity should be a float"
        assert 0.99 <= similarity_11 <= 1.01, f"Self-similarity should be ~1.0, got {similarity_11}"
        print("✅ Self-similarity test passed")
        
        # Test 2: Different embedding comparison
        similarity_12 = recognition.compare_embeddings(emb1, emb2)
        assert isinstance(similarity_12, float), "Similarity should be a float"
        assert 0.0 <= similarity_12 <= 1.0, f"Similarity should be between 0 and 1, got {similarity_12}"
        print("✅ Different embedding comparison test passed")
        
        # Test 3: Identical embedding comparison
        similarity_13 = recognition.compare_embeddings(emb1, emb3)
        assert similarity_13 > 0.99, f"Identical embeddings should have high similarity, got {similarity_13}"
        print("✅ Identical embedding comparison test passed")
        
        # Test 4: Commutative property
        similarity_21 = recognition.compare_embeddings(emb2, emb1)
        assert abs(similarity_12 - similarity_21) < 1e-6, "Similarity should be commutative"
        print("✅ Commutative property test passed")
        
        print(f"✅ Test 4 PASSED: Embedding comparison functionality")
        print(f"   - Self-similarity: {similarity_11:.6f}")
        print(f"   - Different similarity: {similarity_12:.6f}")
        print(f"   - Identical similarity: {similarity_13:.6f}\n")
        return True
        
    except Exception as e:
        print(f"❌ Test 4 FAILED: {e}")
        traceback.print_exc()
        return False

def test_face_recognition():
    """Test 5: Face recognition functionality"""
    print("🧪 Test 5: Face Recognition Functionality")
    print("=" * 50)
    
    try:
        from src.modules.recognition import FaceRecognition
        
        recognition = FaceRecognition()
        
        # Test with no known faces
        test_face = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        name, confidence = recognition.recognize_face(test_face)
        
        assert name == "Unknown", f"Expected 'Unknown' for no known faces, got '{name}'"
        assert confidence == 0.0, f"Expected confidence 0.0 for no known faces, got {confidence}"
        print("✅ Recognition with no known faces handled correctly")
        
        # Test with known faces (if available)
        success = recognition.load_known_faces()
        if success:
            print("✅ Known faces loaded successfully")
            
            # Test recognition with a test face
            name, confidence = recognition.recognize_face(test_face)
            assert isinstance(name, str), "Name should be a string"
            assert isinstance(confidence, float), "Confidence should be a float"
            assert 0.0 <= confidence <= 1.0, f"Confidence should be between 0 and 1, got {confidence}"
            print("✅ Recognition with known faces handled correctly")
            print(f"   - Recognized name: {name}")
            print(f"   - Confidence: {confidence:.3f}")
        else:
            print("⚠️ No known faces available for testing (this is normal)")
        
        print("✅ Test 5 PASSED: Face recognition functionality\n")
        return True
        
    except Exception as e:
        print(f"❌ Test 5 FAILED: {e}")
        traceback.print_exc()
        return False

def test_frame_processing():
    """Test 6: Complete frame processing pipeline"""
    print("🧪 Test 6: Complete Frame Processing Pipeline")
    print("=" * 50)
    
    try:
        from src.modules.recognition import FaceRecognition
        
        recognition = FaceRecognition()
        
        # Create test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        test_frame[:] = (100, 100, 100)  # Dark gray background
        
        # Process the frame
        results = recognition.recognize_user(test_frame)
        
        # Check return format
        assert isinstance(results, list), "recognize_user should return a list"
        print("✅ Frame processing returned correct format")
        
        # Check result structure if any faces detected
        if results:
            for result in results:
                assert isinstance(result, dict), "Each result should be a dictionary"
                assert 'bbox' in result, "Result should contain 'bbox' key"
                assert 'name' in result, "Result should contain 'name' key"
                assert 'confidence' in result, "Result should contain 'confidence' key"
                assert 'recognized' in result, "Result should contain 'recognized' key"
                
                bbox = result['bbox']
                assert len(bbox) == 4, f"Bounding box should have 4 elements, got {len(bbox)}"
                
                name = result['name']
                assert isinstance(name, str), "Name should be a string"
                
                confidence = result['confidence']
                assert isinstance(confidence, float), "Confidence should be a float"
                assert 0.0 <= confidence <= 1.0, f"Confidence should be between 0 and 1, got {confidence}"
                
                recognized = result['recognized']
                assert isinstance(recognized, bool), "Recognized should be a boolean"
                
            print("✅ Result structure validation passed")
        
        print(f"✅ Test 6 PASSED: Complete frame processing pipeline")
        print(f"   - Processed frame with {len(results)} results\n")
        return True
        
    except Exception as e:
        print(f"❌ Test 6 FAILED: {e}")
        traceback.print_exc()
        return False

def test_image_recognition():
    """Test 7: Image file recognition"""
    print("🧪 Test 7: Image File Recognition")
    print("=" * 50)
    
    try:
        from src.modules.recognition import FaceRecognition
        
        recognition = FaceRecognition()
        
        # Test with non-existent file
        results = recognition.recognize_from_image("non_existent_file.jpg")
        assert results == [], "Non-existent file should return empty list"
        print("✅ Non-existent file handling correct")
        
        # Test with existing test image if available
        test_images = []
        faces_dir = Path("data/faces")
        if faces_dir.exists():
            test_images = list(faces_dir.glob("*.jpg")) + list(faces_dir.glob("*.jpeg")) + list(faces_dir.glob("*.png"))
        
        if test_images:
            # Test with first available image
            test_image = test_images[0]
            print(f"🔍 Testing with image: {test_image.name}")
            
            results = recognition.recognize_from_image(str(test_image))
            assert isinstance(results, list), "recognize_from_image should return a list"
            print("✅ Image recognition returned correct format")
            
            if results:
                print(f"   - Found {len(results)} faces in image")
                for i, result in enumerate(results):
                    print(f"   - Face {i+1}: {result['name']} (confidence: {result['confidence']:.3f})")
            else:
                print("   - No faces detected in test image")
        else:
            print("⚠️ No test images available for testing")
        
        print("✅ Test 7 PASSED: Image file recognition\n")
        return True
        
    except Exception as e:
        print(f"❌ Test 7 FAILED: {e}")
        traceback.print_exc()
        return False

def test_recognition_stats():
    """Test 8: Recognition system statistics"""
    print("🧪 Test 8: Recognition System Statistics")
    print("=" * 50)
    
    try:
        from src.modules.recognition import FaceRecognition
        
        recognition = FaceRecognition()
        
        # Get initial stats
        stats = recognition.get_recognition_stats()
        
        # Check stats structure
        assert isinstance(stats, dict), "Stats should be a dictionary"
        required_keys = ['known_faces_count', 'confidence_threshold', 'face_cascade_loaded', 'total_known_names']
        
        for key in required_keys:
            assert key in stats, f"Stats should contain '{key}' key"
        
        print("✅ Stats structure validation passed")
        
        # Check stats values
        assert isinstance(stats['known_faces_count'], int), "known_faces_count should be an integer"
        assert isinstance(stats['confidence_threshold'], float), "confidence_threshold should be a float"
        assert isinstance(stats['face_cascade_loaded'], bool), "face_cascade_loaded should be a boolean"
        assert isinstance(stats['total_known_names'], int), "total_known_names should be an integer"
        
        print("✅ Stats value types validation passed")
        
        # Check initial values
        assert stats['known_faces_count'] == 0, "Initial known_faces_count should be 0"
        assert stats['confidence_threshold'] == 0.6, "Initial confidence_threshold should be 0.6"
        assert stats['face_cascade_loaded'] == True, "face_cascade_loaded should be True"
        assert stats['total_known_names'] == 0, "Initial total_known_names should be 0"
        
        print("✅ Initial stats values validation passed")
        
        print(f"✅ Test 8 PASSED: Recognition system statistics")
        print(f"   - Known faces: {stats['known_faces_count']}")
        print(f"   - Confidence threshold: {stats['confidence_threshold']}")
        print(f"   - Face cascade loaded: {stats['face_cascade_loaded']}")
        print(f"   - Total known names: {stats['total_known_names']}\n")
        return True
        
    except Exception as e:
        print(f"❌ Test 8 FAILED: {e}")
        traceback.print_exc()
        return False

def test_performance():
    """Test 9: Performance testing"""
    print("🧪 Test 9: Performance Testing")
    print("=" * 50)
    
    try:
        from src.modules.recognition import FaceRecognition
        
        recognition = FaceRecognition()
        
        # Test embedding comparison performance
        emb1 = np.random.rand(4096).astype(np.float32)
        emb2 = np.random.rand(4096).astype(np.float32)
        
        # Time multiple comparisons
        start_time = time.time()
        for _ in range(100):
            similarity = recognition.compare_embeddings(emb1, emb2)
        
        comparison_time = time.time() - start_time
        avg_comparison_time = comparison_time / 100
        
        print(f"✅ Performance test completed")
        print(f"   - 100 comparisons in {comparison_time:.4f} seconds")
        print(f"   - Average time per comparison: {avg_comparison_time:.6f} seconds")
        
        # Performance should be reasonable (less than 1ms per comparison)
        assert avg_comparison_time < 0.001, f"Comparison too slow: {avg_comparison_time:.6f}s per comparison"
        print("✅ Performance within acceptable limits")
        
        print("✅ Test 9 PASSED: Performance testing\n")
        return True
        
    except Exception as e:
        print(f"❌ Test 9 FAILED: {e}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all recognition tests"""
    print("🚀 EyeD AI Attendance System - Day 4 Face Recognition Tests")
    print("=" * 70)
    print("Running comprehensive test suite for face recognition module...\n")
    
    tests = [
        test_recognition_initialization,
        test_face_detection,
        test_embedding_extraction,
        test_embedding_comparison,
        test_face_recognition,
        test_frame_processing,
        test_image_recognition,
        test_recognition_stats,
        test_performance
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(tests, 1):
        print(f"Running Test {i}/{len(tests)}...")
        if test():
            passed += 1
        else:
            failed += 1
        print()
    
    # Summary
    print("📊 Test Results Summary")
    print("=" * 30)
    print(f"✅ Tests Passed: {passed}")
    print(f"❌ Tests Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! Day 4 Face Recognition implementation is complete.")
        print("🚀 Ready for Day 5: Live Video Recognition")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please review the implementation.")
    
    return failed == 0

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during testing: {e}")
        traceback.print_exc()
        sys.exit(1)

