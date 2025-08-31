"""
Script to fix the face database by regenerating embeddings from the original image
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

def fix_face_database():
    """Fix the face database by regenerating embeddings from original images"""
    
    faces_dir = Path("data/faces")
    faces_json = faces_dir / "faces.json"
    
    if not faces_json.exists():
        logger.error(f"Faces database not found at {faces_json}")
        return False
    
    try:
        # Load current database
        with open(faces_json, 'r') as f:
            faces_db = json.load(f)
        
        logger.info("Loaded current faces database")
        
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
                    
                    # Verify the embedding dimensions
                    if len(embedding) == 4096:
                        logger.info(f"✅ Generated {len(embedding)}-dimensional embeddings")
                        
                        # Update the database - use 'embeddings' field for consistency
                        user_data["embeddings"] = embedding
                        user_data["embedding_model"] = "VGG-Face"
                        user_data["embedding_dimensions"] = len(embedding)
                        
                        # Remove the old 'embedding' field if it exists
                        if "embedding" in user_data:
                            del user_data["embedding"]
                            logger.info("Removed old 'embedding' field")
                        
                        updated_count += 1
                        logger.info(f"✅ Updated {user_data.get('name', user_id)} with {len(embedding)}-dim embedding")
                    else:
                        logger.warning(f"Unexpected embedding dimensions: {len(embedding)}")
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
                "updated_users": updated_count,
                "description": "Fixed face database with proper 4096-dimensional VGG-Face embeddings"
            }
            
            # Backup current file
            backup_path = faces_json.with_suffix('.json.fixed_backup')
            import shutil
            shutil.copy2(faces_json, backup_path)
            logger.info(f"Backed up current database to {backup_path}")
            
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
        logger.error(f"Failed to fix face database: {e}")
        return False

def verify_fixed_database():
    """Verify that the database has been fixed"""
    
    faces_json = Path("data/faces/faces.json")
    
    if not faces_json.exists():
        logger.error("Faces database not found")
        return False
    
    try:
        with open(faces_json, 'r') as f:
            faces_db = json.load(f)
        
        users_data = faces_db.get("users", {})
        valid_count = 0
        
        for user_id, user_data in users_data.items():
            embeddings = user_data.get("embeddings")
            if embeddings and isinstance(embeddings, list):
                if len(embeddings) == 4096:
                    valid_count += 1
                    user_name = user_data.get('name', user_id)
                    logger.info(f"✅ {user_name}: Valid {len(embeddings)}-dim embeddings")
                else:
                    user_name = user_data.get('name', user_id)
                    logger.warning(f"❌ {user_name}: Invalid {len(embeddings)}-dim embeddings")
            else:
                user_name = user_data.get('name', user_id)
                logger.warning(f"❌ {user_name}: No embeddings found")
        
        logger.info(f"Verification complete: {valid_count} valid users")
        return valid_count > 0
        
    except Exception as e:
        logger.error(f"Failed to verify database: {e}")
        return False

if __name__ == "__main__":
    logger.info("🔧 Starting face database fix...")
    
    # Fix the database
    if fix_face_database():
        logger.info("✅ Face database fix completed successfully!")
        
        # Verify the results
        logger.info("🔍 Verifying fixed database...")
        if verify_fixed_database():
            logger.info("✅ Database verification successful!")
        else:
            logger.warning("⚠️ Database verification failed")
    else:
        logger.error("❌ Face database fix failed!")
