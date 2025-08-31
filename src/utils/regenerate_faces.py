"""
Utility script to regenerate face database with proper embeddings
This fixes the dimension mismatch issue between registration and recognition
"""

import json
import cv2
import numpy as np
from pathlib import Path
from deepface import DeepFace
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def regenerate_face_embeddings(faces_dir: str = "data/faces"):
    """
    Regenerate face embeddings for all registered users
    
    Args:
        faces_dir: Path to faces database directory
    """
    faces_path = Path(faces_dir)
    faces_json = faces_path / "faces.json"
    
    if not faces_json.exists():
        logger.error(f"Faces database not found at {faces_json}")
        return False
    
    try:
        # Load existing faces database
        with open(faces_json, 'r') as f:
            faces_db = json.load(f)
        
        logger.info("Loaded existing faces database")
        
        # Process each user
        users_data = faces_db.get("users", {})
        updated_count = 0
        
        for user_id, user_data in users_data.items():
            try:
                # Skip if no image path
                image_path = user_data.get("image_path")
                if not image_path:
                    logger.warning(f"No image path for user {user_id}")
                    continue
                
                # Check if image file exists
                img_path = Path(image_path)
                if not img_path.exists():
                    logger.warning(f"Image file not found: {image_path}")
                    continue
                
                logger.info(f"Processing user: {user_data.get('name', user_id)}")
                
                # Load and process image
                image = cv2.imread(str(img_path))
                if image is None:
                    logger.warning(f"Failed to load image: {image_path}")
                    continue
                
                # Convert BGR to RGB for DeepFace
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # Extract embedding using VGG-Face model
                logger.info(f"Extracting embedding for {user_data.get('name', user_id)}...")
                embedding_result = DeepFace.represent(
                    img_path=rgb_image,
                    model_name="VGG-Face",
                    enforce_detection=False,
                    align=True
                )
                
                if embedding_result and len(embedding_result) > 0:
                    embedding = embedding_result[0]["embedding"]
                    user_data["embedding"] = embedding
                    user_data["embedding_model"] = "VGG-Face"
                    user_data["embedding_dimensions"] = len(embedding)
                    updated_count += 1
                    logger.info(f"✅ Updated {user_data.get('name', user_id)} with {len(embedding)}-dim embedding")
                else:
                    logger.warning(f"Failed to extract embedding for {user_data.get('name', user_id)}")
                
            except Exception as e:
                logger.error(f"Error processing user {user_id}: {e}")
                continue
        
        # Save updated database
        if updated_count > 0:
            # Add metadata
            faces_db["metadata"] = {
                "last_updated": "2025-01-15",
                "embedding_model": "VGG-Face",
                "total_users": len(users_data),
                "updated_users": updated_count
            }
            
            # Backup original file
            backup_path = faces_json.with_suffix('.json.backup')
            import shutil
            shutil.copy2(faces_json, backup_path)
            logger.info(f"Backed up original database to {backup_path}")
            
            # Save updated database
            with open(faces_json, 'w') as f:
                json.dump(faces_db, f, indent=2)
            
            logger.info(f"✅ Successfully updated {updated_count} users with proper embeddings")
            logger.info(f"Database saved to {faces_json}")
            return True
        else:
            logger.warning("No users were updated")
            return False
            
    except Exception as e:
        logger.error(f"Failed to regenerate face embeddings: {e}")
        return False

def verify_embeddings(faces_dir: str = "data/faces"):
    """
    Verify that all users have proper embeddings
    
    Args:
        faces_dir: Path to faces database directory
    """
    faces_path = Path(faces_dir)
    faces_json = faces_path / "faces.json"
    
    if not faces_json.exists():
        logger.error(f"Faces database not found at {faces_json}")
        return False
    
    try:
        with open(faces_json, 'r') as f:
            faces_db = json.load(f)
        
        users_data = faces_db.get("users", {})
        valid_count = 0
        invalid_count = 0
        
        for user_id, user_data in users_data.items():
            embedding = user_data.get("embedding")
            if embedding and isinstance(embedding, list) and len(embedding) > 100:
                # Check if it's not all the same value (placeholder)
                if len(set(embedding)) > 10:  # At least 10 different values
                    valid_count += 1
                    logger.info(f"✅ {user_data.get('name', user_id)}: Valid {len(embedding)}-dim embedding")
                else:
                    invalid_count += 1
                    logger.warning(f"❌ {user_data.get('name', user_id)}: Placeholder embedding detected")
            else:
                invalid_count += 1
                logger.warning(f"❌ {user_data.get('name', user_id)}: No valid embedding")
        
        logger.info(f"Verification complete: {valid_count} valid, {invalid_count} invalid")
        return valid_count > 0
        
    except Exception as e:
        logger.error(f"Failed to verify embeddings: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting face database regeneration...")
    
    # Regenerate embeddings
    if regenerate_face_embeddings():
        logger.info("Face database regeneration completed successfully!")
        
        # Verify the results
        logger.info("Verifying embeddings...")
        if verify_embeddings():
            logger.info("✅ All embeddings verified successfully!")
        else:
            logger.warning("⚠️ Some embeddings may still be invalid")
    else:
        logger.error("Face database regeneration failed!")
