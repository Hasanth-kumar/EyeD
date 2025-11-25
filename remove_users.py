#!/usr/bin/env python3
"""
Remove specific users (Hasanth and Haze) from the system.
This will delete:
- Face images
- Attendance records (optional)
"""

import os
import csv
import shutil
from pathlib import Path
from datetime import datetime

def remove_face_images(user_names):
    """Remove face images for specified users."""
    print("=" * 60)
    print("REMOVING FACE IMAGES")
    print("=" * 60)
    
    faces_dir = Path("data/faces")
    if not faces_dir.exists():
        print("[ERROR] faces directory not found")
        return []
    
    removed_images = []
    user_names_lower = [name.lower() for name in user_names]
    
    # Find and delete images
    for image_file in faces_dir.glob("*.jpg"):
        image_name_lower = image_file.name.lower()
        
        # Check if image belongs to any of the users
        for user_name in user_names_lower:
            if user_name in image_name_lower:
                try:
                    image_file.unlink()
                    removed_images.append(image_file.name)
                    print(f"  [OK] Deleted: {image_file.name}")
                except Exception as e:
                    print(f"  [ERROR] Failed to delete {image_file.name}: {e}")
                break
    
    print(f"\n[OK] Removed {len(removed_images)} face images")
    return removed_images

def remove_attendance_records(user_names):
    """Remove attendance records for specified users."""
    print("\n" + "=" * 60)
    print("REMOVING ATTENDANCE RECORDS")
    print("=" * 60)
    
    attendance_file = Path("data/attendance.csv")
    if not attendance_file.exists():
        print("[OK] attendance.csv not found (nothing to remove)")
        return 0
    
    # Create backup
    backup_file = attendance_file.with_suffix('.csv.backup')
    shutil.copy2(attendance_file, backup_file)
    print(f"[OK] Created backup: {backup_file.name}")
    
    # Read all records
    with open(attendance_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        all_records = list(reader)
    
    # Filter out records for specified users
    user_names_lower = [name.lower() for name in user_names]
    filtered_records = []
    removed_count = 0
    
    for record in all_records:
        name = record.get("Name", "").lower()
        user_id = record.get("ID", "").lower()
        
        # Check if record belongs to any of the users
        should_remove = False
        for user_name in user_names_lower:
            if user_name in name or user_name in user_id:
                should_remove = True
                removed_count += 1
                break
        
        if not should_remove:
            filtered_records.append(record)
    
    # Write filtered records back
    with open(attendance_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_records)
    
    print(f"[OK] Removed {removed_count} attendance records")
    print(f"[OK] Kept {len(filtered_records)} records")
    return removed_count

def main():
    """Main function."""
    user_names = ["hasanth", "haze"]
    
    print("=" * 60)
    print("REMOVE USERS: Hasanth and Haze")
    print("=" * 60)
    print(f"\nThis will remove data for: {', '.join(user_names)}")
    print("\nWill remove:")
    print("  - Face images")
    print("  - Attendance records")
    print("\nA backup of attendance.csv will be created.\n")
    
    # Remove face images
    removed_images = remove_face_images(user_names)
    
    # Remove attendance records
    removed_records = remove_attendance_records(user_names)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Face images removed: {len(removed_images)}")
    print(f"Attendance records removed: {removed_records}")
    print("\n[OK] User removal complete!\n")

if __name__ == "__main__":
    main()


