#!/usr/bin/env python3
"""
Cleanup script for VGG-Face to ArcFace migration - Option 1 (Minimal Cleanup)

This script:
1. Creates backups of files before cleanup
2. Removes VGG-Face embeddings from faces.json
3. Resets embeddings_cache.pkl
4. Keeps face images (for re-registration)
5. Keeps attendance records (historical data)
"""

import json
import pickle
import shutil
import sys
from pathlib import Path
from datetime import datetime
import os

def create_backup():
    """Create backup directory and backup files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"data/backups/vgg-face-cleanup-{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating backup in: {backup_dir}")
    
    # Backup faces.json
    faces_file = Path("data/faces/faces.json")
    if faces_file.exists():
        backup_faces = backup_dir / "faces.json.backup"
        shutil.copy2(faces_file, backup_faces)
        print(f"  [OK] Backed up faces.json")
    
    # Backup embeddings_cache.pkl
    cache_file = Path("data/faces/embeddings_cache.pkl")
    if cache_file.exists():
        backup_cache = backup_dir / "embeddings_cache.pkl.backup"
        shutil.copy2(cache_file, backup_cache)
        print(f"  [OK] Backed up embeddings_cache.pkl")
    
    return backup_dir

def cleanup_faces_json():
    """Remove VGG-Face embeddings from faces.json."""
    print("\n" + "=" * 60)
    print("CLEANING faces.json")
    print("=" * 60)
    
    faces_file = Path("data/faces/faces.json")
    if not faces_file.exists():
        print("[ERROR] faces.json not found")
        return False
    
    # Load current data
    with open(faces_file, 'r') as f:
        data = json.load(f)
    
    # Count legacy users before cleanup
    legacy_users = []
    for key, value in data.items():
        if key in ["users", "metadata"]:
            continue
        if isinstance(value, dict) and "embedding" in value:
            legacy_users.append(key)
    
    print(f"Found {len(legacy_users)} legacy VGG-Face users to remove")
    
    # Create new clean structure
    new_data = {
        "users": {},
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "embedding_model": "ArcFace",
            "total_users": 0,
            "updated_users": 0,
            "description": "ArcFace face database - users need to re-register"
        }
    }
    
    # Save cleaned data
    with open(faces_file, 'w') as f:
        json.dump(new_data, f, indent=2)
    
    print(f"[OK] Removed {len(legacy_users)} legacy users")
    print(f"[OK] Updated metadata: embedding_model = 'ArcFace'")
    print(f"[OK] Reset total_users to 0")
    return True

def cleanup_embeddings_cache():
    """Reset embeddings_cache.pkl to empty state."""
    print("\n" + "=" * 60)
    print("CLEANING embeddings_cache.pkl")
    print("=" * 60)
    
    cache_file = Path("data/faces/embeddings_cache.pkl")
    
    # Create empty cache structure
    empty_cache = {
        "embeddings": {},
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "version": "1.0",
            "total_embeddings": 0
        }
    }
    
    # Write empty cache
    with open(cache_file, 'wb') as f:
        pickle.dump(empty_cache, f)
    
    print("[OK] Reset embeddings_cache.pkl to empty state")
    return True

def verify_cleanup():
    """Verify that cleanup was successful."""
    print("\n" + "=" * 60)
    print("VERIFYING CLEANUP")
    print("=" * 60)
    
    # Check faces.json
    faces_file = Path("data/faces/faces.json")
    if faces_file.exists():
        with open(faces_file, 'r') as f:
            data = json.load(f)
        
        # Count legacy users (should be 0)
        legacy_count = 0
        for key, value in data.items():
            if key in ["users", "metadata"]:
                continue
            if isinstance(value, dict) and "embedding" in value:
                legacy_count += 1
        
        metadata = data.get("metadata", {})
        embedding_model = metadata.get("embedding_model", "Unknown")
        total_users = metadata.get("total_users", -1)
        
        if legacy_count == 0 and embedding_model == "ArcFace" and total_users == 0:
            print("[OK] faces.json is clean")
        else:
            print(f"[WARNING] faces.json may not be fully clean:")
            print(f"  - Legacy users remaining: {legacy_count}")
            print(f"  - Embedding model: {embedding_model}")
            print(f"  - Total users: {total_users}")
    
    # Check embeddings_cache.pkl
    cache_file = Path("data/faces/embeddings_cache.pkl")
    if cache_file.exists():
        with open(cache_file, 'rb') as f:
            cache = pickle.load(f)
        
        embeddings = cache.get("embeddings", {})
        if len(embeddings) == 0:
            print("[OK] embeddings_cache.pkl is empty")
        else:
            print(f"[WARNING] embeddings_cache.pkl has {len(embeddings)} embeddings")
    
    # Check face images (should still exist)
    faces_dir = Path("data/faces")
    image_files = list(faces_dir.glob("*.jpg"))
    print(f"[OK] Face images preserved: {len(image_files)} images")
    
    # Check attendance records (should still exist)
    attendance_file = Path("data/attendance.csv")
    if attendance_file.exists():
        import csv
        with open(attendance_file, 'r') as f:
            reader = csv.DictReader(f)
            records = list(reader)
        print(f"[OK] Attendance records preserved: {len(records)} records")

def main():
    """Main cleanup function."""
    print("=" * 60)
    print("VGG-FACE CLEANUP - OPTION 1 (MINIMAL CLEANUP)")
    print("=" * 60)
    print("\nThis will:")
    print("  - Remove VGG-Face embeddings from faces.json")
    print("  - Reset embeddings_cache.pkl")
    print("  - KEEP face images (for re-registration)")
    print("  - KEEP attendance records (historical data)")
    print("\nA backup will be created before cleanup.\n")
    
    # Check for --yes flag or confirmation
    auto_confirm = '--yes' in sys.argv or '-y' in sys.argv
    if not auto_confirm:
        try:
            response = input("Proceed with cleanup? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("Cleanup cancelled.")
                return
        except EOFError:
            print("[ERROR] Cannot read input. Use --yes flag for non-interactive mode.")
            print("Example: python cleanup_vgg_face.py --yes")
            return
    
    try:
        # Step 1: Create backup
        print("\n" + "=" * 60)
        print("STEP 1: CREATING BACKUP")
        print("=" * 60)
        backup_dir = create_backup()
        print(f"\n[OK] Backup created in: {backup_dir}")
        
        # Step 2: Clean faces.json
        if not cleanup_faces_json():
            print("[ERROR] Failed to clean faces.json")
            return
        
        # Step 3: Clean embeddings_cache.pkl
        if not cleanup_embeddings_cache():
            print("[ERROR] Failed to clean embeddings_cache.pkl")
            return
        
        # Step 4: Verify cleanup
        verify_cleanup()
        
        print("\n" + "=" * 60)
        print("CLEANUP COMPLETE!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Users need to re-register to generate ArcFace embeddings")
        print("  2. Test the system with a new registration")
        print("  3. Backup location: " + str(backup_dir))
        print("\n")
        
    except Exception as e:
        print(f"\n[ERROR] Cleanup failed: {e}")
        print("You can restore from backup if needed.")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

