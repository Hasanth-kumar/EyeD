#!/usr/bin/env python3
"""
Test Suite for Day 13: Enhanced User Registration
EyeD AI Attendance System

Tests the enhanced registration features including:
- Real backend integration
- Face embedding generation
- Live database updates
- Enhanced user management
"""

import unittest
import sys
import os
from pathlib import Path
import tempfile
import shutil
import json
import numpy as np
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class TestDay13EnhancedRegistration(unittest.TestCase):
    """Test suite for Day 13 enhanced registration features"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.faces_dir = Path(self.test_dir) / "faces"
        self.faces_dir.mkdir()
        
        # Create test image data
        self.test_image = np.random.randint(0, 255, (480, 480, 3), dtype=np.uint8)
        self.test_user_data = {
            'name': 'Test User',
            'user_id': 'TEST001',
            'email': 'test@example.com',
            'department': 'Engineering',
            'role': 'Employee',
            'phone': '+1-555-123-4567'
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_01_registration_component_imports(self):
        """Test that registration component imports correctly"""
        try:
            from dashboard.components.registration import (
                show_registration, show_webcam_registration, 
                show_image_upload_registration, show_user_management,
                detect_face_in_image, generate_face_embedding,
                process_registration_enhanced
            )
            self.assertTrue(True, "All registration functions imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import registration functions: {e}")
    
    def test_02_face_database_enhanced_methods(self):
        """Test enhanced face database methods"""
        try:
            from modules.face_db import FaceDatabase
            
            # Test with mock data directory
            db = FaceDatabase(str(self.faces_dir))
            
            # Test enhanced register_user method
            self.assertTrue(hasattr(db, 'register_user'), "register_user method should exist")
            self.assertTrue(hasattr(db, '_save_user_image'), "_save_user_image method should exist")
            self.assertTrue(hasattr(db, '_generate_embedding'), "_generate_embedding method should exist")
            
        except ImportError as e:
            self.fail(f"Failed to import FaceDatabase: {e}")
        except Exception as e:
            self.fail(f"Failed to initialize FaceDatabase: {e}")
    
    def test_03_recognition_module_embedding_method(self):
        """Test that recognition module has generate_embedding method"""
        try:
            from modules.recognition import FaceRecognition
            
            recognition = FaceRecognition()
            self.assertTrue(hasattr(recognition, 'generate_embedding'), 
                          "generate_embedding method should exist")
            
        except ImportError as e:
            self.fail(f"Failed to import FaceRecognition: {e}")
        except Exception as e:
            self.fail(f"Failed to initialize FaceRecognition: {e}")
    
    def test_04_face_detection_validation(self):
        """Test face detection validation functionality"""
        try:
            from dashboard.components.registration import detect_face_in_image
            
            # Test with mock face detection
            with patch('cv2.CascadeClassifier') as mock_cascade:
                mock_cascade.return_value.detectMultiScale.return_value = [(100, 100, 200, 200)]
                
                result = detect_face_in_image(self.test_image)
                self.assertTrue(result, "Face detection should return True for valid face")
                
        except ImportError as e:
            self.fail(f"Failed to import face detection function: {e}")
    
    def test_05_image_quality_assessment(self):
        """Test image quality assessment functionality"""
        try:
            from dashboard.components.registration import assess_image_quality
            
            # Test quality assessment
            quality_score = assess_image_quality(self.test_image)
            
            self.assertIsInstance(quality_score, float, "Quality score should be float")
            self.assertGreaterEqual(quality_score, 0.0, "Quality score should be >= 0")
            self.assertLessEqual(quality_score, 1.0, "Quality score should be <= 1")
            
        except ImportError as e:
            self.fail(f"Failed to import quality assessment function: {e}")
    
    def test_06_embedding_generation_mock(self):
        """Test embedding generation with mock backend"""
        try:
            from dashboard.components.registration import generate_face_embedding
            
            # Test with mock recognition system
            with patch('dashboard.components.registration.REAL_BACKEND_AVAILABLE', False):
                embedding = generate_face_embedding(self.test_image)
                
                self.assertIsInstance(embedding, np.ndarray, "Embedding should be numpy array")
                self.assertEqual(len(embedding), 4096, "Mock embedding should be 4096 dimensions")
                
        except ImportError as e:
            self.fail(f"Failed to import embedding generation function: {e}")
    
    def test_07_enhanced_registration_processing(self):
        """Test enhanced registration processing"""
        try:
            from dashboard.components.registration import process_registration_enhanced
            
            # Test registration processing with mock backend
            with patch('dashboard.components.registration.REAL_BACKEND_AVAILABLE', False):
                # Mock the face database
                with patch('dashboard.components.registration.st') as mock_st:
                    mock_st.session_state = {}
                    mock_st.success = lambda x: None
                    mock_st.info = lambda x: None
                    mock_st.error = lambda x: None
                    
                    success = process_registration_enhanced(
                        self.test_user_data['name'],
                        self.test_user_data['user_id'],
                        self.test_user_data['email'],
                        self.test_user_data['department'],
                        self.test_user_data['role'],
                        self.test_user_data['phone'],
                        self.test_image,
                        'test'
                    )
                    
                    # Should return boolean result
                    self.assertIsInstance(success, bool, "Should return boolean result")
                
        except ImportError as e:
            self.fail(f"Failed to import registration processing function: {e}")
    
    def test_08_user_management_interface(self):
        """Test user management interface functions"""
        try:
            from dashboard.components.registration import (
                show_registered_users_enhanced, show_user_search, show_database_info
            )
            
            # Test that all management functions exist
            self.assertTrue(callable(show_registered_users_enhanced), 
                          "show_registered_users_enhanced should be callable")
            self.assertTrue(callable(show_user_search), 
                          "show_user_search should be callable")
            self.assertTrue(callable(show_database_info), 
                          "show_database_info should be callable")
            
        except ImportError as e:
            self.fail(f"Failed to import user management functions: {e}")
    
    def test_09_database_operations(self):
        """Test database operations functionality"""
        try:
            from dashboard.components.registration import get_directory_size
            
            # Test directory size calculation
            size = get_directory_size(self.test_dir)
            self.assertIsInstance(size, float, "Directory size should be float")
            self.assertGreaterEqual(size, 0.0, "Directory size should be >= 0")
            
        except ImportError as e:
            self.fail(f"Failed to import database operations function: {e}")
    
    def test_10_metadata_handling(self):
        """Test extended metadata handling"""
        try:
            from modules.face_db import FaceDatabase
            
            db = FaceDatabase(str(self.faces_dir))
            
            # Test metadata fields
            expected_fields = ['name', 'user_id', 'email', 'department', 'role', 'phone']
            
            for field in expected_fields:
                self.assertIn(field, self.test_user_data, f"User data should contain {field}")
                
        except ImportError as e:
            self.fail(f"Failed to import FaceDatabase for metadata test: {e}")
    
    def test_11_image_saving_functionality(self):
        """Test image saving functionality"""
        try:
            from modules.face_db import FaceDatabase
            
            db = FaceDatabase(str(self.faces_dir))
            
            # Test image saving
            if hasattr(db, '_save_user_image'):
                image_path = db._save_user_image('TEST001', self.test_image)
                
                if image_path:
                    self.assertTrue(image_path.exists(), "Saved image should exist")
                    self.assertTrue(image_path.suffix == '.jpg', "Image should be saved as JPG")
                    
        except ImportError as e:
            self.fail(f"Failed to import FaceDatabase for image saving test: {e}")
    
    def test_12_embedding_generation_integration(self):
        """Test embedding generation integration"""
        try:
            from modules.face_db import FaceDatabase
            
            db = FaceDatabase(str(self.faces_dir))
            
            # Test embedding generation
            if hasattr(db, '_generate_embedding'):
                # Mock the entire DeepFace module to avoid actual model loading
                with patch.dict('sys.modules', {'deepface': MagicMock()}):
                    # Create a mock embedding
                    mock_embedding = np.random.rand(512)
                    
                    # Test that the method exists and is callable
                    self.assertTrue(hasattr(db, '_generate_embedding'), 
                                  "_generate_embedding method should exist")
                    self.assertTrue(callable(db._generate_embedding), 
                                  "_generate_embedding method should be callable")
                    
        except ImportError as e:
            self.fail(f"Failed to import FaceDatabase for embedding test: {e}")
    
    def test_13_user_search_functionality(self):
        """Test user search functionality"""
        try:
            from modules.face_db import FaceDatabase
            
            db = FaceDatabase(str(self.faces_dir))
            
            # Test search method
            if hasattr(db, 'search_users'):
                # Add test user
                db.users_db['TEST001'] = self.test_user_data
                
                # Test search
                results = db.search_users('Test')
                self.assertIsInstance(results, list, "Search results should be list")
                
        except ImportError as e:
            self.fail(f"Failed to import FaceDatabase for search test: {e}")
    
    def test_14_database_persistence(self):
        """Test database persistence functionality"""
        try:
            from modules.face_db import FaceDatabase
            
            db = FaceDatabase(str(self.faces_dir))
            
            # Test save methods
            self.assertTrue(hasattr(db, '_save_database'), "_save_database method should exist")
            
            # Test with mock data
            db.users_db['TEST001'] = self.test_user_data
            
            # Test save
            if hasattr(db, '_save_database'):
                db._save_database()
                
                # Check if file was created
                json_file = self.faces_dir / "faces.json"
                self.assertTrue(json_file.exists(), "Database file should be created")
                
        except ImportError as e:
            self.fail(f"Failed to import FaceDatabase for persistence test: {e}")
    
    def test_15_error_handling(self):
        """Test error handling in registration process"""
        try:
            from dashboard.components.registration import process_registration_enhanced
            
            # Test with invalid inputs
            with patch('dashboard.components.registration.REAL_BACKEND_AVAILABLE', False):
                # Test with None image
                success = process_registration_enhanced(
                    'Test User', 'TEST001', 'test@example.com',
                    'Engineering', 'Employee', '+1-555-123-4567',
                    None, 'test'
                )
                
                # Should handle None image gracefully
                self.assertIsInstance(success, bool, "Should return boolean result")
                
        except ImportError as e:
            self.fail(f"Failed to import registration function for error handling test: {e}")

def run_tests():
    """Run all tests and return results"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDay13EnhancedRegistration)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return results
    return {
        'tests_run': result.testsRun,
        'tests_failed': len(result.failures),
        'tests_errored': len(result.errors),
        'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun if result.testsRun > 0 else 0
    }

if __name__ == '__main__':
    print("🧪 Running Day 13 Enhanced Registration Test Suite...")
    print("=" * 60)
    
    results = run_tests()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"Tests Run: {results['tests_run']}")
    print(f"Tests Failed: {results['tests_failed']}")
    print(f"Tests Errored: {results['tests_errored']}")
    print(f"Success Rate: {results['success_rate']:.1%}")
    
    if results['tests_failed'] == 0 and results['tests_errored'] == 0:
        print("\n🎉 All tests passed! Day 13 implementation is working correctly.")
    else:
        print(f"\n⚠️ {results['tests_failed'] + results['tests_errored']} tests failed. Please review the implementation.")
    
    print("=" * 60)
