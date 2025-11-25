"""
Diagnostic script to debug face recognition issue.
Tests why Hasanth's face is not recognized in the class photo.
"""

import cv2
import numpy as np
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import required modules
from infrastructure.storage.file_storage import FileStorage
from repositories.face_repository import FaceRepository
from core.recognition.detector import FaceDetector
from core.recognition.embedding_extractor import EmbeddingExtractor
from core.recognition.recognizer import FaceRecognizer
from core.recognition.quality_assessor import QualityAssessor
from domain.services.recognition.face_recognition_service import FaceRecognitionService
from core.shared.constants import DEFAULT_CONFIDENCE_THRESHOLD

def main():
    # Initialize services
    file_storage = FileStorage()
    face_repository = FaceRepository(file_storage)
    
    # Initialize face recognition components
    face_detector = FaceDetector()
    embedding_extractor = EmbeddingExtractor()
    face_recognizer = FaceRecognizer()
    quality_assessor = QualityAssessor()
    
    face_recognition_service = FaceRecognitionService(
        face_detector=face_detector,
        embedding_extractor=embedding_extractor,
        face_recognizer=face_recognizer,
        quality_assessor=quality_assessor,
        confidence_threshold=DEFAULT_CONFIDENCE_THRESHOLD
    )
    
    # Load class photo
    class_photo_path = "WhatsApp Image 2025-11-24 at 15.13.40_4f9af74b.jpg"
    logger.info(f"Loading class photo: {class_photo_path}")
    
    if not Path(class_photo_path).exists():
        logger.error(f"Class photo not found: {class_photo_path}")
        return
    
    class_image = cv2.imread(class_photo_path)
    if class_image is None:
        logger.error(f"Failed to load class photo: {class_photo_path}")
        return
    
    logger.info(f"Class photo loaded: shape={class_image.shape}")
    
    # Load reference embedding for Hasanth
    logger.info("Loading reference embedding for Hasanth...")
    hasanth_embedding_entity = face_repository.get_face_embedding("hasanth")
    
    if hasanth_embedding_entity is None:
        logger.error("Hasanth embedding not found in repository")
        return
    
    hasanth_embedding = hasanth_embedding_entity.embedding
    logger.info(f"Hasanth embedding loaded: shape={hasanth_embedding.shape}, dtype={hasanth_embedding.dtype}, norm={np.linalg.norm(hasanth_embedding):.6f}")
    
    # Get all known embeddings
    logger.info("Loading all known embeddings...")
    all_embeddings = face_repository.get_all_face_embeddings()
    logger.info(f"Loaded {len(all_embeddings)} known embeddings")
    
    # Prepare known embeddings dictionary
    known_embeddings = {}
    user_names = {}
    for user_id, embedding_entity in all_embeddings.items():
        known_embeddings[user_id] = embedding_entity.embedding
        user_names[user_id] = user_id
    
    logger.info(f"Prepared {len(known_embeddings)} known embeddings for recognition")
    
    # Detect all faces in class photo
    logger.info("Detecting faces in class photo...")
    detection_result = face_detector.detect(class_image)
    
    if not detection_result.faces_detected or detection_result.face_count == 0:
        logger.error("No faces detected in class photo!")
        return
    
    logger.info(f"Detected {detection_result.face_count} face(s) in class photo")
    
    # Process each detected face
    for idx, face_location in enumerate(detection_result.faces):
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing face {idx + 1}/{detection_result.face_count}")
        logger.info(f"Face location: x={face_location.x}, y={face_location.y}, width={face_location.width}, height={face_location.height}")
        
        # Extract face region
        height, width = class_image.shape[:2]
        x = max(0, face_location.x)
        y = max(0, face_location.y)
        x_end = min(width, x + face_location.width)
        y_end = min(height, y + face_location.height)
        
        face_image = class_image[y:y_end, x:x_end]
        logger.info(f"Face image extracted: shape={face_image.shape}")
        
        # Assess quality
        quality_result = quality_assessor.assess(face_image)
        logger.info(f"Quality assessment: score={quality_result.overall_score:.4f}, is_suitable={quality_result.is_suitable}")
        
        if not quality_result.is_suitable:
            logger.warning(f"Face {idx + 1} quality insufficient: {quality_result.overall_score:.4f} < 0.5")
            continue
        
        # Extract embedding
        embedding_result = embedding_extractor.extract(face_image)
        if embedding_result is None:
            logger.warning(f"Face {idx + 1}: Failed to extract embedding")
            continue
        
        face_embedding = embedding_result.embedding
        logger.info(f"Face {idx + 1} embedding extracted: shape={face_embedding.shape}, dtype={face_embedding.dtype}, norm={np.linalg.norm(face_embedding):.6f}")
        
        # Compare with Hasanth's embedding directly
        similarity = face_recognizer.compare_embeddings(face_embedding, hasanth_embedding)
        logger.info(f"Face {idx + 1} similarity with Hasanth: {similarity:.6f} (threshold: {DEFAULT_CONFIDENCE_THRESHOLD})")
        
        if similarity >= DEFAULT_CONFIDENCE_THRESHOLD:
            logger.info(f"✓ Face {idx + 1} MATCHES Hasanth! (similarity: {similarity:.6f})")
        else:
            logger.warning(f"✗ Face {idx + 1} does NOT match Hasanth (similarity: {similarity:.6f} < {DEFAULT_CONFIDENCE_THRESHOLD})")
        
        # Try recognition against all known embeddings
        recognition_result = face_recognizer.recognize(
            face_embedding=face_embedding,
            known_embeddings=known_embeddings,
            threshold=DEFAULT_CONFIDENCE_THRESHOLD,
            user_names=user_names
        )
        
        if recognition_result:
            logger.info(f"Face {idx + 1} recognized as: {recognition_result.user_name} (user_id: {recognition_result.user_id}, confidence: {recognition_result.confidence:.6f})")
        else:
            logger.warning(f"Face {idx + 1} not recognized (no match above threshold)")
    
    logger.info(f"\n{'='*60}")
    logger.info("Diagnostic complete!")

if __name__ == "__main__":
    main()

