"""
Register user use case.

Orchestrates user registration workflow with face recognition.
"""

from dataclasses import dataclass
from typing import Optional, Protocol
from datetime import datetime
import logging
import numpy as np

from domain.entities.user import User
from domain.entities.face_embedding import FaceEmbedding
from domain.services.recognition import UserRegistrationService
from domain.shared.exceptions import (
    UserAlreadyExistsError,
    FaceDetectionFailedError,
    InsufficientQualityError,
    EmbeddingExtractionFailedError
)

logger = logging.getLogger(__name__)


@dataclass
class RegisterUserRequest:
    """Request for user registration."""
    user_id: str
    user_name: str
    face_image: np.ndarray
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@dataclass
class RegisterUserResponse:
    """Response from user registration."""
    success: bool
    user: Optional[User] = None
    error: Optional[str] = None
    quality_score: Optional[float] = None


class UserRepositoryProtocol(Protocol):
    """Protocol for user repository operations."""
    
    def get_user(self, user_id: str) -> dict:
        """Get user by ID. Returns dict with 'success' and 'data' keys."""
        ...
    
    def add_user(self, user_data: dict) -> dict:
        """Add user. Returns dict with 'success' key."""
        ...


class FaceRepositoryProtocol(Protocol):
    """Protocol for face repository operations."""
    
    def store_face_embeddings(
        self,
        user_id: str,
        embeddings: np.ndarray,
        embedding_metadata: Optional[dict] = None
    ) -> dict:
        """Store face embeddings. Returns dict with 'success' key."""
        ...


class RegisterUserUseCase:
    """
    Orchestrates user registration workflow.
    
    This use case coordinates face detection, quality assessment, embedding
    extraction, and persistence to register a new user with face recognition.
    
    Uses ArcFace model for embedding extraction, which provides better recognition
    accuracy compared to previous models, especially for smaller/distant faces.
    """
    
    def __init__(
        self,
        registration_service: UserRegistrationService,
        user_repository: UserRepositoryProtocol,
        face_repository: FaceRepositoryProtocol
    ):
        """
        Initialize RegisterUserUseCase.
        
        Args:
            registration_service: Composite service for user registration operations.
            user_repository: User data persistence repository.
            face_repository: Face embedding persistence repository.
        """
        self.registration_service = registration_service
        self.user_repository = user_repository
        self.face_repository = face_repository
    
    def execute(self, request: RegisterUserRequest) -> RegisterUserResponse:
        """
        Execute user registration workflow.
        
        Args:
            request: Registration request with user data and face image.
        
        Returns:
            RegisterUserResponse with registration result.
        
        Raises:
            UserAlreadyExistsError: If user_id already exists.
            FaceDetectionFailedError: If no face detected in image.
            InsufficientQualityError: If face quality below threshold.
            EmbeddingExtractionFailedError: If embedding extraction fails.
        """
        try:
            # Step 1: Validate user_id uniqueness
            self._validate_user_id_uniqueness(request.user_id)
            
            # Step 2: Process registration image (detect, assess quality, extract embedding)
            # We need face_location for face_bbox, so detect first to get location
            detection_result = self.registration_service.face_detector.detect(request.face_image)
            if not detection_result.faces_detected or detection_result.face_count == 0:
                raise FaceDetectionFailedError()
            
            # Get face_location for bbox (will be used later)
            face_location = detection_result.faces[0]
            
            # Process registration image (this will detect again internally, but that's okay)
            # Embeddings extracted using ArcFace model for improved accuracy
            face_image, quality_result, embedding_result = (
                self.registration_service.process_registration_image(request.face_image)
            )
            
            # Step 3: Create User entity
            user = User(
                user_id=request.user_id,
                username=request.user_name,
                first_name=request.first_name,
                last_name=request.last_name,
                email=request.email,
                registration_date=datetime.now(),
                status='active'
            )
            
            # Step 4: Create FaceEmbedding entity
            face_embedding = FaceEmbedding(
                user_id=request.user_id,
                embedding=embedding_result.embedding,
                quality_score=quality_result.overall_score,
                created_at=datetime.now()
            )
            
            # Step 5: Store face image and get image path
            try:
                image_path = self.face_repository.store_face_image(
                    user_id=request.user_id,
                    face_image=face_image
                )
            except Exception as e:
                logger.error(f"Failed to store face image: {e}")
                return RegisterUserResponse(
                    success=False,
                    error=f"Failed to store face image: {str(e)}",
                    quality_score=quality_result.overall_score
                )
            
            # Step 6: Save user (convert entity to dict for repository)
            # This will save in legacy format (top-level key in faces.json)
            user_data = self._user_entity_to_dict(user)
            user_result = self.user_repository.add_user(user_data)
            if not user_result.get('success', False):
                error_msg = user_result.get('error', 'Failed to save user')
                return RegisterUserResponse(
                    success=False,
                    error=error_msg,
                    quality_score=quality_result.overall_score
                )
            
            # Step 7: Save face embedding with all legacy format fields
            # Get full name for legacy format
            full_name = user.get_full_name()
            
            # Extract face_bbox from face_location
            face_bbox = None
            if face_location:
                # Convert face_location to bbox format [x, y, width, height]
                if hasattr(face_location, 'x') and hasattr(face_location, 'y'):
                    face_bbox = [
                        int(face_location.x),
                        int(face_location.y),
                        int(face_location.width) if hasattr(face_location, 'width') else 0,
                        int(face_location.height) if hasattr(face_location, 'height') else 0
                    ]
            
            embedding_metadata = {
                'quality_score': quality_result.overall_score,
                'created_at': face_embedding.created_at.isoformat(),
                'name': full_name,  # Legacy format requires 'name' field
                'image_path': image_path,  # Store image path
                'face_bbox': face_bbox  # Store face bounding box if available
            }
            face_result = self.face_repository.store_face_embeddings(
                user_id=request.user_id,
                embeddings=face_embedding.embedding,
                embedding_metadata=embedding_metadata
            )
            if not face_result.get('success', False):
                error_msg = face_result.get('error', 'Failed to save face embedding')
                return RegisterUserResponse(
                    success=False,
                    error=error_msg,
                    quality_score=quality_result.overall_score
                )
            
            # Success
            return RegisterUserResponse(
                success=True,
                user=user,
                quality_score=quality_result.overall_score
            )
            
        except (UserAlreadyExistsError, FaceDetectionFailedError,
                InsufficientQualityError, EmbeddingExtractionFailedError) as e:
            # Re-raise domain exceptions
            raise
        except Exception as e:
            # Handle unexpected errors
            return RegisterUserResponse(
                success=False,
                error=f"Unexpected error during registration: {str(e)}"
            )
    
    def _validate_user_id_uniqueness(self, user_id: str) -> None:
        """
        Validate that user_id is unique.
        
        Args:
            user_id: User ID to validate.
        
        Raises:
            UserAlreadyExistsError: If user_id already exists.
        """
        result = self.user_repository.get_user(user_id)
        if result.get('success', False) and result.get('data') is not None:
            raise UserAlreadyExistsError(user_id=user_id)
    
    def _user_entity_to_dict(self, user: User) -> dict:
        """
        Convert User entity to dictionary for repository.
        
        Args:
            user: User entity to convert.
        
        Returns:
            Dictionary representation of user.
        """
        return {
            'user_id': user.user_id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'status': user.status,
            'registration_date': user.registration_date.isoformat()
        }

