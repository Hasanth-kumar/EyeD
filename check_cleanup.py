#!/usr/bin/env python3
"""
Script to check VGG-Face data that needs cleanup.
Run this to see what data exists before cleanup.
"""

import json
import pickle
import os
from pathlib import Path

def check_faces_json():
    """Check faces.json for VGG-Face embeddings."""
    print("=" * 60)
    print("1. CHECKING faces.json")
    print("=" * 60)
    
    faces_file = Path("data/faces/faces.json")
    if not faces_file.exists():
        print("[ERROR] faces.json not found")
        return []
    
    with open(faces_file, 'r') as f:
        data = json.load(f)
    
    # Check metadata
    metadata = data.get("metadata", {})
    embedding_model = metadata.get("embedding_model", "Unknown")
    total_users = metadata.get("total_users", 0)
    
    print(f"Embedding Model: {embedding_model}")
    print(f"Total Users (metadata): {total_users}")
    
    # Find legacy users
    legacy_users = []
    for key, value in data.items():
        if key in ["users", "metadata"]:
            continue
        if isinstance(value, dict) and "embedding" in value:
            legacy_users.append(key)
            name = value.get("name", "N/A")
            image_path = value.get("image_path", "N/A")
            print(f"  - {key}: {name} (image: {image_path})")
    
    print(f"\n[OK] Found {len(legacy_users)} legacy VGG-Face users")
    return legacy_users

def check_embeddings_cache():
    """Check embeddings_cache.pkl for cached embeddings."""
    print("\n" + "=" * 60)
    print("2. CHECKING embeddings_cache.pkl")
    print("=" * 60)
    
    cache_file = Path("data/faces/embeddings_cache.pkl")
    if not cache_file.exists():
        print("[OK] embeddings_cache.pkl does not exist (nothing to clean)")
        return []
    
    try:
        with open(cache_file, 'rb') as f:
            cache = pickle.load(f)
        
        embeddings = cache.get("embeddings", {})
        metadata = cache.get("metadata", {})
        
        print(f"Total cached embeddings: {len(embeddings)}")
        if embeddings:
            print("User IDs in cache:")
            for user_id in embeddings.keys():
                print(f"  - {user_id}")
        else:
            print("[OK] Cache is empty (nothing to clean)")
        
        return list(embeddings.keys())
    except Exception as e:
        print(f"[WARNING] Error reading cache: {e}")
        return []

def check_face_images(legacy_users):
    """Check which face images exist for legacy users."""
    print("\n" + "=" * 60)
    print("3. CHECKING Face Images")
    print("=" * 60)
    
    faces_dir = Path("data/faces")
    if not faces_dir.exists():
        print("[ERROR] faces directory not found")
        return []
    
    # Get all jpg files
    image_files = list(faces_dir.glob("*.jpg"))
    print(f"Total image files found: {len(image_files)}")
    
    # Check which ones belong to legacy users
    legacy_images = []
    for img_file in image_files:
        img_name = img_file.name
        # Check if image name matches any legacy user
        for user in legacy_users:
            if user.lower() in img_name.lower():
                legacy_images.append(img_name)
                print(f"  - {img_name} (belongs to: {user})")
                break
    
    print(f"\n[OK] Found {len(legacy_images)} images for legacy users")
    return legacy_images

def check_attendance_records(legacy_users):
    """Check attendance.csv for records from legacy users."""
    print("\n" + "=" * 60)
    print("4. CHECKING Attendance Records")
    print("=" * 60)
    
    attendance_file = Path("data/attendance.csv")
    if not attendance_file.exists():
        print("[ERROR] attendance.csv not found")
        return 0, 0
    
    import csv
    with open(attendance_file, 'r') as f:
        reader = csv.DictReader(f)
        records = list(reader)
    
    total_records = len(records)
    
    # Count records for legacy users
    legacy_records = 0
    for record in records:
        name = record.get("Name", "").lower()
        user_id = record.get("ID", "").lower()
        for user in legacy_users:
            if user.lower() in name or user.lower() in user_id:
                legacy_records += 1
                break
    
    print(f"Total attendance records: {total_records}")
    print(f"Records for legacy users: {legacy_records} ({legacy_records/total_records*100:.1f}%)")
    print("[OK] Attendance records should be KEPT (historical data)")
    
    return total_records, legacy_records

def main():
    """Main function to run all checks."""
    print("\n" + "=" * 60)
    print("VGG-FACE CLEANUP CHECKER")
    print("=" * 60)
    print("\nThis script identifies VGG-Face data that can be cleaned up.\n")
    
    # Run all checks
    legacy_users = check_faces_json()
    cached_users = check_embeddings_cache()
    legacy_images = check_face_images(legacy_users)
    total_records, legacy_records = check_attendance_records(legacy_users)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Legacy VGG-Face Users: {len(legacy_users)}")
    print(f"Cached Embeddings: {len(cached_users)}")
    print(f"Legacy Face Images: {len(legacy_images)}")
    print(f"Attendance Records (KEEP): {legacy_records}/{total_records}")
    
    print("\n" + "=" * 60)
    print("RECOMMENDED ACTIONS")
    print("=" * 60)
    print("1. Remove VGG-Face embeddings from faces.json")
    print("2. Reset/delete embeddings_cache.pkl")
    print("3. (Optional) Delete old face images")
    print("4. KEEP attendance records (historical data)")
    print("\nSee CLEANUP_REPORT.md for detailed instructions.\n")

if __name__ == "__main__":
    main()

