"""
Recognize face use case.

Extracts face recognition logic from attendance marking workflow.
Handles face detection, quality assessment, recognition, and eligibility validation.
"""

from dataclasses import dataclass
from typing import Optional, Protocol, Dict, Any, Tuple, List
from datetime import date, datetime
import logging
import numpy as np

logger = logging.getLogger(__name__)

from domain.entities.user import User
from domain.services.recognition import FaceRecognitionService
from domain.shared.exceptions import (
    FaceDetectionFailedError,
    InsufficientQualityError,
    FaceNotRecognizedError,
    DailyLimitExceededError
)
from domain.shared.constants import (
    MIN_FACE_QUALITY_SCORE,
    MAX_DAILY_ATTENDANCE_ENTRIES
)


@dataclass
class RecognizeFaceRequest:
    """Request for recognizing a face from a single frame."""
    frame: np.ndarray  # Single frame for recognition


@dataclass
class RecognizeFaceResponse:
    """Response from face recognition."""
    success: bool
    user: Optional[User] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    confidence: Optional[float] = None
    error: Optional[str] = None
    daily_limit_reached: bool = False


class AttendanceRepositoryProtocol(Protocol):
    """Protocol for attendance repository operations."""
    
    def get_attendance_history(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List:
        """Get attendance history. Returns list of attendance entries."""
        ...


class FaceRepositoryProtocol(Protocol):
    """Protocol for face repository operations."""
    
    def get_all_face_embeddings(self) -> Dict[str, Any]:
        """Get all face embeddings. Returns dict with 'success' and 'embeddings' keys."""
        ...


class UserRepositoryProtocol(Protocol):
    """Protocol for user repository operations."""
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user by ID. Returns dict with 'success' and 'data' keys."""
        ...


class RecognizeFaceUseCase:
    """
    Use case for recognizing faces from a single frame.
    
    This use case handles:
    1. Face detection and quality assessment
    2. Face recognition against known embeddings
    3. Eligibility validation (daily limit check)
    4. User information retrieval
    
    Following Clean Architecture, this use case orchestrates domain services
    and repositories without containing business logic itself.
    """
    
    def __init__(
        self,
        face_recognition_service: FaceRecognitionService,
        attendance_repository: AttendanceRepositoryProtocol,
        face_repository: FaceRepositoryProtocol,
        user_repository: UserRepositoryProtocol,
        max_daily_entries: int = None
    ):
        """
        Initialize RecognizeFaceUseCase.
        
        Args:
            face_recognition_service: Composite service for face recognition operations.
            attendance_repository: Attendance data persistence repository.
            face_repository: Face embedding persistence repository.
            user_repository: User data persistence repository.
            max_daily_entries: Maximum attendance entries allowed per day.
        """
        self.face_recognition_service = face_recognition_service
        self.attendance_repository = attendance_repository
        self.face_repository = face_repository
        self.user_repository = user_repository
        self.max_daily_entries = (
            max_daily_entries if max_daily_entries is not None
            else MAX_DAILY_ATTENDANCE_ENTRIES
        )
    
    def execute(self, request: RecognizeFaceRequest) -> RecognizeFaceResponse:
        """
        Execute face recognition workflow.
        
        Workflow:
        1. Detect face and assess quality
        2. Recognize face from known embeddings
        3. Validate eligibility (check daily limit)
        4. Get user information
        
        Args:
            request: Recognize face request with single frame.
        
        Returns:
            RecognizeFaceResponse with user info or error.
        """
        try:
            # Step 1: Detect face and assess quality
            face_image, quality_result = self.face_recognition_service.detect_and_assess_face(
                request.frame
            )
            
            # Step 2: Recognize face
            recognition_result = self._recognize_face(face_image)
            
            # Step 3: Validate eligibility (check daily limit)
            daily_limit_reached = self._check_daily_limit(recognition_result.user_id)
            if daily_limit_reached:
                return RecognizeFaceResponse(
                    success=False,
                    error=f"Daily attendance limit reached ({self.max_daily_entries} entries)",
                    daily_limit_reached=True,
                    user_id=recognition_result.user_id,
                    user_name=recognition_result.user_name,
                    confidence=recognition_result.confidence
                )
            
            # Step 4: Get user information
            user = self._get_user(recognition_result)
            
            # Success
            return RecognizeFaceResponse(
                success=True,
                user=user,
                user_id=recognition_result.user_id,
                user_name=recognition_result.user_name,
                confidence=recognition_result.confidence,
                daily_limit_reached=False
            )
            
        except FaceDetectionFailedError as e:
            return RecognizeFaceResponse(
                success=False,
                error=str(e.message) if hasattr(e, 'message') else str(e)
            )
        except InsufficientQualityError as e:
            return RecognizeFaceResponse(
                success=False,
                error=str(e.message) if hasattr(e, 'message') else str(e)
            )
        except FaceNotRecognizedError as e:
            return RecognizeFaceResponse(
                success=False,
                error=str(e.message) if hasattr(e, 'message') else str(e)
            )
        except DailyLimitExceededError as e:
            return RecognizeFaceResponse(
                success=False,
                error=str(e.message) if hasattr(e, 'message') else str(e),
                daily_limit_reached=True
            )
        except Exception as e:
            logger.error(f"Unexpected error during face recognition: {e}", exc_info=True)
            return RecognizeFaceResponse(
                success=False,
                error=f"Unexpected error during face recognition: {str(e)}"
            )
    
    def _recognize_face(
        self,
        face_image: np.ndarray
    ) -> Any:
        """
        Get known embeddings and recognize face.
        
        Args:
            face_image: Cropped face image.
        
        Returns:
            RecognitionResult with user_id, user_name, and confidence.
        
        Raises:
            FaceNotRecognizedError: If recognition fails.
        """
        # Get known embeddings
        embeddings_result = self.face_repository.get_all_face_embeddings()
        
        # Handle both protocol format (dict with 'success' and 'embeddings') 
        # and actual format (Dict[str, FaceEmbedding])
        if isinstance(embeddings_result, dict) and 'success' in embeddings_result:
            # Protocol format
            if not embeddings_result.get('success', False):
                raise FaceNotRecognizedError(message="Failed to retrieve known face embeddings")
            embeddings_data = embeddings_result.get('embeddings', {})
        else:
            # Actual format: Dict[str, FaceEmbedding]
            embeddings_data = embeddings_result
        
        if not embeddings_data:
            raise FaceNotRecognizedError(message="No known faces in database")
        
        logger.info(f"Loaded {len(embeddings_data)} known face embeddings for recognition")
        
        # Prepare known embeddings dictionary for recognition
        known_embeddings, user_names = self._prepare_known_embeddings(embeddings_data)
        
        logger.info(f"Prepared {len(known_embeddings)} known embeddings for recognition")
        if len(known_embeddings) > 0:
            first_user_id = list(known_embeddings.keys())[0]
            first_embedding = known_embeddings[first_user_id]
            logger.info(f"Sample embedding ({first_user_id}): shape={np.array(first_embedding).shape}, dtype={np.array(first_embedding).dtype}, norm={np.linalg.norm(np.array(first_embedding)):.6f}")
        
        # Recognize face using the composite service
        recognition_result = self.face_recognition_service.recognize_face(
            face_image=face_image,
            known_embeddings=known_embeddings,
            user_names=user_names
        )
        
        return recognition_result
    
    def _prepare_known_embeddings(
        self,
        embeddings_data: Dict[str, Any]
    ) -> Tuple[Dict[str, np.ndarray], Dict[str, str]]:
        """
        Prepare known embeddings and user names from repository data.
        
        Handles both formats:
        - Dict[str, FaceEmbedding] (actual repository format)
        - Dict[str, dict] with 'embeddings' key (protocol format)
        
        Args:
            embeddings_data: Raw embeddings data from repository.
        
        Returns:
            Tuple of (known_embeddings, user_names) dictionaries.
        
        Raises:
            FaceNotRecognizedError: If no valid embeddings found.
        """
        from domain.entities.face_embedding import FaceEmbedding
        
        known_embeddings = {}
        user_names = {}
        
        for user_id, embedding_info in embeddings_data.items():
            # Handle FaceEmbedding entity format
            if isinstance(embedding_info, FaceEmbedding):
                known_embeddings[user_id] = embedding_info.embedding
                user_names[user_id] = embedding_info.user_id  # Use user_id as name
            # Handle dict format with 'embeddings' key (protocol format)
            elif isinstance(embedding_info, dict) and 'embeddings' in embedding_info:
                known_embeddings[user_id] = embedding_info['embeddings']
                user_names[user_id] = embedding_info.get('user_name', user_id)
            # Handle dict format with 'embedding' key (direct embedding)
            elif isinstance(embedding_info, dict) and 'embedding' in embedding_info:
                known_embeddings[user_id] = embedding_info['embedding']
                user_names[user_id] = embedding_info.get('user_name', user_id)
            # Handle direct numpy array
            elif isinstance(embedding_info, np.ndarray):
                known_embeddings[user_id] = embedding_info
                user_names[user_id] = user_id
        
        if not known_embeddings:
            raise FaceNotRecognizedError(message="No valid embeddings found in database")
        
        return known_embeddings, user_names
    
    def _check_daily_limit(self, user_id: str) -> bool:
        """
        Check if user has reached daily attendance limit.
        
        Args:
            user_id: ID of the user to check.
        
        Returns:
            True if daily limit reached, False otherwise.
        """
        today = date.today()
        
        # Get existing attendance records for today
        existing_records = self.attendance_repository.get_attendance_history(
            user_id=user_id,
            start_date=today,
            end_date=today
        )
        
        # Check daily limit
        daily_entries_count = len(existing_records)
        return daily_entries_count >= self.max_daily_entries
    
    def _get_user(self, recognition_result: Any) -> User:
        """
        Retrieve or create user from recognition result.
        
        Args:
            recognition_result: Recognition result with user_id and user_name.
        
        Returns:
            User domain entity.
        """
        user_id = recognition_result.user_id
        
        # Get user information
        user_result = self.user_repository.get_user(user_id)
        if user_result.get('success', False) and user_result.get('data'):
            user_data = user_result['data']
            return self._dict_to_user_entity(user_data)
        
        # If user not found in repository, create minimal user from recognition result
        return User(
            user_id=user_id,
            username=recognition_result.user_name,
            first_name=None,
            last_name=None,
            email=None,
            registration_date=datetime.now(),
            status='active'
        )
    
    def _dict_to_user_entity(self, user_data: Dict[str, Any]) -> User:
        """
        Convert user dictionary to User entity.
        
        Args:
            user_data: Dictionary representation of user.
        
        Returns:
            User domain entity.
        """
        # Parse registration date
        registration_date = datetime.now()
        if 'registration_date' in user_data:
            reg_date_str = user_data['registration_date']
            if isinstance(reg_date_str, str):
                try:
                    registration_date = datetime.fromisoformat(reg_date_str)
                except ValueError:
                    registration_date = datetime.now()
            elif isinstance(reg_date_str, datetime):
                registration_date = reg_date_str
        
        return User(
            user_id=user_data.get('user_id', ''),
            username=user_data.get('user_name') or user_data.get('username', ''),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            email=user_data.get('email'),
            registration_date=registration_date,
            status=user_data.get('status', 'active')
        )

