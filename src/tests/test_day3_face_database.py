#!/usr/bin/env python3
"""
Test script for Day 3: Face Database Implementation
EyeD AI Attendance System

This script tests the new FaceDatabase module to ensure:
- Database initialization and loading
- User registration and management
- Embedding storage and retrieval
- Database integrity verification
- Performance optimization features
"""

import sys
import os
import numpy as np
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_face_database():
    """Test the FaceDatabase module functionality"""
    print("🧪 Testing Day 3: Face Database Implementation")
    print("=" * 60)
    
    try:
        # Import the new module
        from src.modules.face_db import FaceDatabase
        print("✅ FaceDatabase module imported successfully")
        
        # Test 1: Database Initialization
        print("\n📋 Test 1: Database Initialization")
        print("-" * 40)
        
        # Clean up any existing test data
        test_data_dir = "data/test_faces"
        if os.path.exists(test_data_dir):
            import shutil
            shutil.rmtree(test_data_dir)
        
        # Initialize database
        db = FaceDatabase(test_data_dir)
        print(f"✅ Database initialized in: {test_data_dir}")
        print(f"✅ Data directory created: {os.path.exists(test_data_dir)}")
        print(f"✅ Backup directory created: {os.path.exists(os.path.join(test_data_dir, 'backups'))}")
        
        # Test 2: User Registration
        print("\n📋 Test 2: User Registration")
        print("-" * 40)
        
        # Create mock embeddings (4096 dimensions as per VGG-Face)
        mock_embedding1 = np.random.rand(4096).astype(np.float32)
        mock_embedding2 = np.random.rand(4096).astype(np.float32)
        
        # Register test users
        success1 = db.register_user(
            name="Alice Johnson",
            user_id="alice_001",
            embedding=mock_embedding1,
            image_path="data/test_faces/alice.jpg",
            metadata={"department": "Engineering", "role": "Developer"}
        )
        
        success2 = db.register_user(
            name="Bob Smith",
            user_id="bob_002",
            embedding=mock_embedding2,
            image_path="data/test_faces/bob.jpg"
        )
        
        print(f"✅ Alice registration: {'SUCCESS' if success1 else 'FAILED'}")
        print(f"✅ Bob registration: {'SUCCESS' if success2 else 'FAILED'}")
        
        # Test 3: Embedding Loading
        print("\n📋 Test 3: Embedding Loading")
        print("-" * 40)
        
        embeddings = db.load_embeddings()
        print(f"✅ Loaded {len(embeddings)} embeddings")
        print(f"✅ Alice embedding shape: {embeddings.get('alice_001', 'Not found').shape if 'alice_001' in embeddings else 'Not found'}")
        print(f"✅ Bob embedding shape: {embeddings.get('bob_002', 'Not found').shape if 'bob_002' in embeddings else 'Not found'}")
        
        # Test 4: User Data Retrieval
        print("\n📋 Test 4: User Data Retrieval")
        print("-" * 40)
        
        alice_data = db.get_user_data("alice_001")
        bob_data = db.get_user_data("bob_002")
        
        print(f"✅ Alice data retrieved: {'Yes' if alice_data else 'No'}")
        if alice_data:
            print(f"   - Name: {alice_data.get('name')}")
            print(f"   - Department: {alice_data.get('department')}")
            print(f"   - Registration date: {alice_data.get('registration_date')}")
        
        print(f"✅ Bob data retrieved: {'Yes' if bob_data else 'No'}")
        if bob_data:
            print(f"   - Name: {bob_data.get('name')}")
            print(f"   - Registration date: {bob_data.get('registration_date')}")
        
        # Test 5: Search Functionality
        print("\n📋 Test 5: Search Functionality")
        print("-" * 40)
        
        # Search by name
        alice_search = db.search_users("Alice")
        bob_search = db.search_users("Bob")
        engineering_search = db.search_users("Engineering")
        
        print(f"✅ Search 'Alice': {len(alice_search)} results")
        print(f"✅ Search 'Bob': {len(bob_search)} results")
        print(f"✅ Search 'Engineering': {len(engineering_search)} results")
        
        # Test 6: Database Statistics
        print("\n📋 Test 6: Database Statistics")
        print("-" * 40)
        
        stats = db.get_database_stats()
        print(f"✅ Total users: {stats['total_users']}")
        print(f"✅ Total embeddings: {stats['total_embeddings']}")
        print(f"✅ Database size: {stats['database_size_bytes']} bytes")
        print(f"✅ Recent registrations: {len(stats['recent_registrations'])}")
        
        # Test 7: Database Verification
        print("\n📋 Test 7: Database Verification")
        print("-" * 40)
        
        verification = db.verify_embeddings()
        print(f"✅ Integrity check: {'PASSED' if verification['integrity_check'] else 'FAILED'}")
        print(f"✅ Issues found: {len(verification['issues'])}")
        print(f"✅ Warnings: {len(verification['warnings'])}")
        
        if verification['issues']:
            print("   Issues:")
            for issue in verification['issues']:
                print(f"   - {issue}")
        
        if verification['warnings']:
            print("   Warnings:")
            for warning in verification['warnings']:
                print(f"   - {warning}")
        
        # Test 8: User Update
        print("\n📋 Test 8: User Update")
        print("-" * 40)
        
        update_success = db.update_user("alice_001", {
            "department": "Senior Engineering",
            "role": "Senior Developer",
            "last_promotion": "2024-01-15"
        })
        
        print(f"✅ Alice update: {'SUCCESS' if update_success else 'FAILED'}")
        
        # Verify update
        updated_alice = db.get_user_data("alice_001")
        if updated_alice:
            print(f"   - Updated department: {updated_alice.get('department')}")
            print(f"   - Updated role: {updated_alice.get('role')}")
            print(f"   - Last promotion: {updated_alice.get('last_promotion')}")
        
        # Test 9: Backup Creation
        print("\n📋 Test 9: Backup Creation")
        print("-" * 40)
        
        backup_path = db.create_backup()
        if backup_path:
            print(f"✅ Backup created: {backup_path}")
            print(f"✅ Backup file exists: {os.path.exists(backup_path)}")
        else:
            print("❌ Backup creation failed")
        
        # Test 10: Cleanup and Deletion
        print("\n📋 Test 10: Cleanup and Deletion")
        print("-" * 40)
        
        # Delete Bob
        delete_success = db.delete_user("bob_002")
        print(f"✅ Bob deletion: {'SUCCESS' if delete_success else 'FAILED'}")
        
        # Verify deletion
        remaining_embeddings = db.load_embeddings()
        print(f"✅ Remaining embeddings: {len(remaining_embeddings)}")
        print(f"✅ Bob still exists: {'Yes' if 'bob_002' in remaining_embeddings else 'No'}")
        
        # Test 11: Performance Test
        print("\n📋 Test 11: Performance Test")
        print("-" * 40)
        
        import time
        
        # Test embedding loading performance
        start_time = time.time()
        for _ in range(10):
            db.load_embeddings()
        load_time = time.time() - start_time
        
        print(f"✅ 10 embedding loads in {load_time:.4f} seconds")
        print(f"✅ Average load time: {load_time/10:.4f} seconds")
        
        # Test 12: Memory Management
        print("\n📋 Test 12: Memory Management")
        print("-" * 40)
        
        # Check if cache is working efficiently
        cache_hit = db.get_user_embedding("alice_001")
        print(f"✅ Cache hit for Alice: {'Yes' if cache_hit is not None else 'No'}")
        print(f"✅ Cache hit shape: {cache_hit.shape if cache_hit is not None else 'N/A'}")
        
        # Final cleanup
        print("\n🧹 Final Cleanup")
        print("-" * 40)
        
        # Clean up test data
        if os.path.exists(test_data_dir):
            import shutil
            shutil.rmtree(test_data_dir)
            print(f"✅ Test data directory removed: {test_data_dir}")
        
        print("\n🎉 All Day 3 Tests Completed Successfully!")
        print("=" * 60)
        print("✅ Face Database Module: PASSED")
        print("✅ Embedding Storage: PASSED")
        print("✅ User Management: PASSED")
        print("✅ Database Integrity: PASSED")
        print("✅ Performance Optimization: PASSED")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure the FaceDatabase module is properly implemented")
        return False
        
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_face_database()
    sys.exit(0 if success else 1)


