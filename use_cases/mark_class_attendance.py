"""
Mark class attendance use case.

Orchestrates class attendance marking workflow where a single photo of the entire
class is taken and attendance is marked for all recognized students.
"""

from dataclasses import dataclass
from typing import Optional, List, Protocol, Dict, Any
from datetime import date
import time
import logging
import numpy as np

logger = logging.getLogger(__name__)

from domain.entities.attendance_record import AttendanceRecord
from domain.services.recognition import FaceRecognitionService
from domain.services.attendance import AttendanceService
from core.attendance.value_objects import IndividualAttendanceResult
from domain.shared.exceptions import (
    InvalidAttendanceRecordError,
    FaceNotRecognizedError
)
from domain.shared.constants import MAX_DAILY_ATTENDANCE_ENTRIES


@dataclass
class MarkClassAttendanceRequest:
    """Request for marking class attendance from a single photo."""
    class_image: np.ndarray  # Single photo containing multiple faces
    device_info: str
    location: str


@dataclass
class MarkClassAttendanceResponse:
    """Response from marking class attendance."""
    success: bool
    results: List[IndividualAttendanceResult]
    total_detected: int
    total_recognized: int
    total_marked: int
    error: Optional[str] = None


class AttendanceRepositoryProtocol(Protocol):
    """Protocol for attendance repository operations."""
    
    def add_attendance(self, record: AttendanceRecord) -> bool:
        """Add attendance entry. Returns True if successful."""
        ...
    
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


class MarkClassAttendanceUseCase:
    """
    Orchestrates class attendance marking workflow.
    
    This use case handles:
    - Detecting all faces in a class photo
    - Recognizing each face against known embeddings
    - Checking daily limits per student
    - Creating and saving attendance records for all recognized students
    
    Following Clean Architecture, this use case orchestrates domain services
    and repositories without containing business logic itself.
    """
    
    def __init__(
        self,
        face_recognition_service: FaceRecognitionService,
        attendance_service: AttendanceService,
        attendance_repository: AttendanceRepositoryProtocol,
        face_repository: FaceRepositoryProtocol,
        user_repository: UserRepositoryProtocol,
        max_daily_entries: int = None
    ):
        """
        Initialize MarkClassAttendanceUseCase.
        
        Args:
            face_recognition_service: Composite service for face recognition operations.
            attendance_service: Composite service for attendance operations.
            attendance_repository: Attendance data persistence repository.
            face_repository: Face embedding persistence repository.
            user_repository: User data persistence repository.
            max_daily_entries: Maximum attendance entries allowed per day.
        """
        self.face_recognition_service = face_recognition_service
        self.attendance_service = attendance_service
        self.attendance_repository = attendance_repository
        self.face_repository = face_repository
        self.user_repository = user_repository
        self.max_daily_entries = (
            max_daily_entries if max_daily_entries is not None
            else MAX_DAILY_ATTENDANCE_ENTRIES
        )
    
    def execute(self, request: MarkClassAttendanceRequest) -> MarkClassAttendanceResponse:
        """
        Execute class attendance marking workflow.
        
        Workflow:
        1. Get known embeddings from face_repository
        2. Call recognize_multiple_faces() to recognize all faces
        3. For each recognized face: check daily limit, create attendance record, save
        4. Return response with all results
        
        Args:
            request: Mark class attendance request with class image and metadata.
        
        Returns:
            MarkClassAttendanceResponse with results for all recognized faces.
        """
        start_time = time.time()
        results: List[IndividualAttendanceResult] = []
        
        try:
            # Step 1: Get known embeddings
            known_embeddings, user_names = self._get_known_embeddings()
            if not known_embeddings:
                return MarkClassAttendanceResponse(
                    success=False,
                    results=[],
                    total_detected=0,
                    total_recognized=0,
                    total_marked=0,
                    error="No known faces in database"
                )
            
            # Step 2: Recognize all faces using recognize_multiple_faces
            recognition_results = self.face_recognition_service.recognize_multiple_faces(
                image=request.class_image,
                known_embeddings=known_embeddings,
                user_names=user_names
            )
            
            total_detected = len(recognition_results)
            total_recognized = sum(1 for r in recognition_results if r is not None)
            
            # Step 3: Get face images and process each recognized face
            face_images = self._extract_face_images(request.class_image, len(recognition_results))
            
            # Step 4: Process each recognized face for attendance
            for idx, recognition_result in enumerate(recognition_results):
                if recognition_result is None:
                    continue
                
                face_image = face_images[idx] if idx < len(face_images) else None
                if face_image is None:
                    continue
                
                # Get quality score for this face
                quality_result = self.face_recognition_service.quality_assessor.assess(face_image)
                
                # Process individual face attendance
                result = self._process_individual_attendance(
                    recognition_result=recognition_result,
                    face_image=face_image,
                    quality_score=quality_result.overall_score,
                    device_info=request.device_info,
                    location=request.location,
                    start_time=start_time
                )
                results.append(result)
            
            total_marked = sum(1 for r in results if r.success)
            
            return MarkClassAttendanceResponse(
                success=True,
                results=results,
                total_detected=total_detected,
                total_recognized=total_recognized,
                total_marked=total_marked
            )
            
        except Exception as e:
            logger.exception(f"Unexpected error during class attendance marking: {e}")
            return MarkClassAttendanceResponse(
                success=False,
                results=results,
                total_detected=len(results),
                total_recognized=sum(1 for r in results if r is not None),
                total_marked=sum(1 for r in results if r.success),
                error=f"Unexpected error during class attendance marking: {str(e)}"
            )
    
    def _get_known_embeddings(
        self
    ) -> tuple[Dict[str, np.ndarray], Dict[str, str]]:
        """
        Get known embeddings and user names from repository.
        
        Returns:
            Tuple of (known_embeddings, user_names) dictionaries.
        """
        embeddings_result = self.face_repository.get_all_face_embeddings()
        
        # Handle both protocol format (dict with 'success' and 'embeddings')
        # and actual format (Dict[str, FaceEmbedding])
        if isinstance(embeddings_result, dict) and 'success' in embeddings_result:
            if not embeddings_result.get('success', False):
                return {}, {}
            embeddings_data = embeddings_result.get('embeddings', {})
        else:
            embeddings_data = embeddings_result
        
        if not embeddings_data:
            return {}, {}
        
        known_embeddings = {}
        user_names = {}
        
        from domain.entities.face_embedding import FaceEmbedding
        
        for user_id, embedding_info in embeddings_data.items():
            # Handle FaceEmbedding entity format
            if isinstance(embedding_info, FaceEmbedding):
                known_embeddings[user_id] = embedding_info.embedding
                user_names[user_id] = embedding_info.user_id
            # Handle dict format with 'embeddings' key
            elif isinstance(embedding_info, dict) and 'embeddings' in embedding_info:
                known_embeddings[user_id] = embedding_info['embeddings']
                user_names[user_id] = embedding_info.get('user_name', user_id)
            # Handle dict format with 'embedding' key
            elif isinstance(embedding_info, dict) and 'embedding' in embedding_info:
                known_embeddings[user_id] = embedding_info['embedding']
                user_names[user_id] = embedding_info.get('user_name', user_id)
            # Handle direct numpy array
            elif isinstance(embedding_info, np.ndarray):
                known_embeddings[user_id] = embedding_info
                user_names[user_id] = user_id
        
        return known_embeddings, user_names
    
    def _extract_face_images(
        self,
        image: np.ndarray,
        expected_count: int
    ) -> List[Optional[np.ndarray]]:
        """
        Extract face images from the class image.
        
        Detects faces and extracts face regions. Results are in the same order
        as recognition results from recognize_multiple_faces.
        
        Args:
            image: Full class image containing multiple faces.
            expected_count: Expected number of faces (from recognition results).
        
        Returns:
            List of face images (one per detected face), None for failed extractions.
        """
        detection_result = self.face_recognition_service.face_detector.detect(image)
        if not detection_result.faces_detected or detection_result.face_count == 0:
            return []
        
        face_images = []
        height, width = image.shape[:2]
        
        for face_location in detection_result.faces:
            try:
                # Ensure coordinates are within image bounds
                x = max(0, face_location.x)
                y = max(0, face_location.y)
                x_end = min(width, x + face_location.width)
                y_end = min(height, y + face_location.height)
                
                # Extract face region
                face_image = image[y:y_end, x:x_end]
                face_images.append(face_image)
            except Exception as e:
                logger.warning(f"Error extracting face region: {str(e)}")
                face_images.append(None)
        
        return face_images
    
    def _process_individual_attendance(
        self,
        recognition_result: Any,
        face_image: np.ndarray,
        quality_score: float,
        device_info: str,
        location: str,
        start_time: float
    ) -> IndividualAttendanceResult:
        """
        Process attendance for a single recognized face.
        
        Args:
            recognition_result: Recognition result with user_id, user_name, confidence.
            face_image: Cropped face image for attendance record.
            quality_score: Quality score of the face image.
            device_info: Device information.
            location: Location where attendance was recorded.
            start_time: Start time for processing time calculation.
        
        Returns:
            IndividualAttendanceResult with success status and error message if failed.
        """
        user_id = recognition_result.user_id
        user_name = recognition_result.user_name
        # Convert confidence to Python float (handles numpy scalar types)
        confidence = float(recognition_result.confidence)
        
        try:
            # Check daily limit (reuse logic from RecognizeFaceUseCase)
            daily_limit_reached = self._check_daily_limit(user_id)
            if daily_limit_reached:
                return IndividualAttendanceResult(
                    user_id=user_id,
                    user_name=user_name,
                    confidence=confidence,
                    success=False,
                    error_message=f"Daily attendance limit reached ({self.max_daily_entries} entries)"
                )
            
            # Create attendance record using attendance_service
            attendance_record = self.attendance_service.create_and_validate_record(
                user_id=user_id,
                user_name=user_name,
                face_image=face_image,
                confidence=confidence,
                liveness_verified=True,  # Skip liveness for photo-based attendance
                face_quality_score=quality_score,
                device_info=device_info,
                location=location,
                verification_stage="class_attendance",
                session_id=None,  # Will be generated by logger
                start_time=start_time
            )
            
            # Save attendance record
            save_success = self.attendance_repository.add_attendance(attendance_record)
            if not save_success:
                return IndividualAttendanceResult(
                    user_id=user_id,
                    user_name=user_name,
                    confidence=confidence,
                    success=False,
                    error_message="Failed to save attendance record"
                )
            
            return IndividualAttendanceResult(
                user_id=user_id,
                user_name=user_name,
                confidence=confidence,
                success=True,
                error_message=None
            )
            
        except InvalidAttendanceRecordError as e:
            return IndividualAttendanceResult(
                user_id=user_id,
                user_name=user_name,
                confidence=confidence,
                success=False,
                error_message=str(e.message) if hasattr(e, 'message') else str(e)
            )
        except Exception as e:
            logger.warning(f"Error processing attendance for {user_id}: {str(e)}")
            return IndividualAttendanceResult(
                user_id=user_id,
                user_name=user_name,
                confidence=confidence,
                success=False,
                error_message=f"Error processing attendance: {str(e)}"
            )
    
    def _check_daily_limit(self, user_id: str) -> bool:
        """
        Check if user has reached daily attendance limit.
        
        Reuses logic from RecognizeFaceUseCase._check_daily_limit.
        
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

