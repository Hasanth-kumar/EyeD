"""
Dependency injection setup for FastAPI.

This module provides dependency injection functions for use cases and repositories,
following Clean Architecture principles.
"""

import logging
from typing import Protocol
import numpy as np

from use_cases.mark_attendance import MarkAttendanceUseCase
from use_cases.recognize_face import RecognizeFaceUseCase
from use_cases.get_analytics import GetAnalyticsUseCase
from use_cases.generate_leaderboard import GenerateLeaderboardUseCase
from use_cases.get_all_users import GetAllUsersUseCase
from use_cases.register_user import RegisterUserUseCase
from use_cases.get_user_info import GetUserInfoUseCase
from use_cases.get_user_performance import GetUserPerformanceUseCase
from use_cases.update_user_info import UpdateUserInfoUseCase
from use_cases.get_attendance_records import GetAttendanceRecordsUseCase
from use_cases.mark_class_attendance import MarkClassAttendanceUseCase
from domain.services.recognition import FaceRecognitionService
from domain.shared.constants import DEFAULT_CONFIDENCE_THRESHOLD
from core.shared.constants import DEFAULT_EMBEDDING_MODEL
from domain.services.liveness import LivenessService
from domain.services.attendance import AttendanceService
from domain.services.analytics import MetricsCalculator, TimelineAnalyzer
from domain.services.gamification import (
    LeaderboardGenerator,
    StreakCalculator,
    BadgeCalculator,
    BadgeDefinitions
)
from repositories.attendance_repository import AttendanceRepository
from repositories.face_repository import FaceRepository
from repositories.user_repository import UserRepository
from infrastructure.storage.csv_handler import CSVHandler
from infrastructure.storage.file_storage import FileStorage
from core.recognition.detector import FaceDetector
from core.recognition.embedding_extractor import EmbeddingExtractor
from core.recognition.recognizer import FaceRecognizer
from core.recognition.quality_assessor import QualityAssessor
from core.recognition.strategies import MediaPipeDetectionStrategy, YOLODetectionStrategy
from core.liveness.blink_detector import BlinkDetector
from core.liveness.landmark_extractor import LandmarkExtractor
from domain.services.liveness.liveness_verifier import LivenessVerifier
from core.attendance.attendance_logger import AttendanceLogger
from core.attendance.attendance_validator import AttendanceValidator

logger = logging.getLogger(__name__)

# Singleton instances (created once, reused)
_file_storage: FileStorage | None = None
_face_detector: FaceDetector | None = None
_embedding_extractor: EmbeddingExtractor | None = None
_face_recognizer: FaceRecognizer | None = None
_quality_assessor: QualityAssessor | None = None
_quality_assessor_class_attendance: QualityAssessor | None = None
_blink_detector: BlinkDetector | None = None
_landmark_extractor: LandmarkExtractor | None = None
_liveness_verifier: LivenessVerifier | None = None
_attendance_logger: AttendanceLogger | None = None
_attendance_validator: AttendanceValidator | None = None
_csv_handler: CSVHandler | None = None
_attendance_repository: AttendanceRepository | None = None
_face_repository: FaceRepository | None = None
_user_repository: UserRepository | None = None
_face_recognition_service: FaceRecognitionService | None = None
_face_detector_mediapipe: FaceDetector | None = None
_face_detector_yolo: FaceDetector | None = None
_face_recognition_service_mediapipe: FaceRecognitionService | None = None
_face_recognition_service_yolo: FaceRecognitionService | None = None
_face_recognition_service_class_attendance: FaceRecognitionService | None = None
_liveness_service: LivenessService | None = None
_attendance_service: AttendanceService | None = None
_recognize_face_use_case: RecognizeFaceUseCase | None = None
_mark_attendance_use_case: MarkAttendanceUseCase | None = None
_metrics_calculator: MetricsCalculator | None = None
_timeline_analyzer: TimelineAnalyzer | None = None
_badge_definitions: BadgeDefinitions | None = None
_badge_calculator: BadgeCalculator | None = None
_streak_calculator: StreakCalculator | None = None
_leaderboard_generator: LeaderboardGenerator | None = None
_get_analytics_use_case: GetAnalyticsUseCase | None = None
_generate_leaderboard_use_case: GenerateLeaderboardUseCase | None = None
_get_all_users_use_case: GetAllUsersUseCase | None = None
_register_user_use_case: RegisterUserUseCase | None = None
_get_user_info_use_case: GetUserInfoUseCase | None = None
_get_user_performance_use_case: GetUserPerformanceUseCase | None = None
_update_user_info_use_case: UpdateUserInfoUseCase | None = None
_get_attendance_records_use_case: GetAttendanceRecordsUseCase | None = None
_mark_class_attendance_use_case: MarkClassAttendanceUseCase | None = None


def get_file_storage() -> FileStorage:
    """Get or create file storage instance."""
    global _file_storage
    if _file_storage is None:
        _file_storage = FileStorage()
        logger.info("File storage initialized")
    return _file_storage


def get_csv_handler() -> CSVHandler:
    """Get or create CSV handler instance."""
    global _csv_handler
    if _csv_handler is None:
        file_storage = get_file_storage()
        _csv_handler = CSVHandler(file_storage=file_storage)
        logger.info("CSV handler initialized")
    return _csv_handler


def get_face_detector() -> FaceDetector:
    """Get or create face detector instance."""
    global _face_detector
    if _face_detector is None:
        _face_detector = FaceDetector()
        logger.info("Face detector initialized")
    return _face_detector


def get_embedding_extractor() -> EmbeddingExtractor:
    """Get or create embedding extractor instance."""
    global _embedding_extractor
    if _embedding_extractor is None:
        _embedding_extractor = EmbeddingExtractor(model_name=DEFAULT_EMBEDDING_MODEL)
        logger.info(f"Embedding extractor initialized with {DEFAULT_EMBEDDING_MODEL} model")
    return _embedding_extractor


def get_face_recognizer() -> FaceRecognizer:
    """Get or create face recognizer instance."""
    global _face_recognizer
    if _face_recognizer is None:
        _face_recognizer = FaceRecognizer()
        logger.info("Face recognizer initialized")
    return _face_recognizer


def get_quality_assessor() -> QualityAssessor:
    """Get or create quality assessor instance."""
    global _quality_assessor
    if _quality_assessor is None:
        _quality_assessor = QualityAssessor()
        logger.info("Quality assessor initialized")
    return _quality_assessor


def get_quality_assessor_class_attendance() -> QualityAssessor:
    """Get or create quality assessor instance for class attendance with lower threshold."""
    global _quality_assessor_class_attendance
    if _quality_assessor_class_attendance is None:
        # Lower threshold (0.3) for class attendance to allow smaller/distant faces
        _quality_assessor_class_attendance = QualityAssessor(min_quality_threshold=0.3)
        logger.info("Quality assessor for class attendance initialized (threshold=0.3)")
    return _quality_assessor_class_attendance


def get_blink_detector() -> BlinkDetector:
    """Get or create blink detector instance."""
    global _blink_detector
    if _blink_detector is None:
        _blink_detector = BlinkDetector()
        logger.info("Blink detector initialized")
    return _blink_detector


def get_landmark_extractor() -> LandmarkExtractor:
    """Get or create landmark extractor instance."""
    global _landmark_extractor
    if _landmark_extractor is None:
        _landmark_extractor = LandmarkExtractor()
        logger.info("Landmark extractor initialized")
    return _landmark_extractor


def get_liveness_verifier() -> LivenessVerifier:
    """Get or create liveness verifier instance."""
    global _liveness_verifier
    if _liveness_verifier is None:
        blink_detector = get_blink_detector()
        _liveness_verifier = LivenessVerifier(blink_detector=blink_detector)
        logger.info("Liveness verifier initialized")
    return _liveness_verifier


def get_attendance_logger() -> AttendanceLogger:
    """Get or create attendance logger instance."""
    global _attendance_logger
    if _attendance_logger is None:
        _attendance_logger = AttendanceLogger()
        logger.info("Attendance logger initialized")
    return _attendance_logger


def get_attendance_validator() -> AttendanceValidator:
    """Get or create attendance validator instance."""
    global _attendance_validator
    if _attendance_validator is None:
        _attendance_validator = AttendanceValidator()
        logger.info("Attendance validator initialized")
    return _attendance_validator


def get_attendance_repository() -> AttendanceRepository:
    """Get or create attendance repository instance."""
    global _attendance_repository
    if _attendance_repository is None:
        csv_handler = get_csv_handler()
        _attendance_repository = AttendanceRepository(csv_handler=csv_handler)
        logger.info("Attendance repository initialized")
    return _attendance_repository


def get_face_repository() -> FaceRepository:
    """Get or create face repository instance."""
    global _face_repository
    if _face_repository is None:
        file_storage = get_file_storage()
        _face_repository = FaceRepository(file_storage=file_storage)
        logger.info("Face repository initialized")
    return _face_repository


def get_user_repository() -> UserRepository:
    """Get or create user repository instance."""
    global _user_repository
    if _user_repository is None:
        file_storage = get_file_storage()
        _user_repository = UserRepository(storage_handler=file_storage)
        logger.info("User repository initialized")
    return _user_repository


def get_face_recognition_service() -> FaceRecognitionService:
    """Get or create face recognition service instance."""
    global _face_recognition_service
    if _face_recognition_service is None:
        _face_recognition_service = FaceRecognitionService(
            face_detector=get_face_detector(),
            embedding_extractor=get_embedding_extractor(),
            face_recognizer=get_face_recognizer(),
            quality_assessor=get_quality_assessor(),
            confidence_threshold=DEFAULT_CONFIDENCE_THRESHOLD
        )
        logger.info("Face recognition service initialized")
    return _face_recognition_service


def get_face_detector_mediapipe() -> FaceDetector:
    """Get or create face detector instance with MediaPipe as primary strategy."""
    global _face_detector_mediapipe
    if _face_detector_mediapipe is None:
        # Use very low confidence threshold and full-range model for better multi-face detection
        # Lower threshold helps detect faces that are further away or partially occluded
        mediapipe_strategy = MediaPipeDetectionStrategy(
            min_detection_confidence=0.2,  # Lower threshold to catch all faces in group photos
            model_selection=1  # Full-range (0-5m) for group photos
        )
        _face_detector_mediapipe = FaceDetector(detection_strategy=mediapipe_strategy)
        logger.info("Face detector (MediaPipe primary) initialized with confidence=0.2, full-range model")
    return _face_detector_mediapipe


def get_face_detector_yolo() -> FaceDetector:
    """Get or create face detector instance with YOLO as primary strategy."""
    global _face_detector_yolo
    if _face_detector_yolo is None:
        try:
            # Use default model path to trigger fallback logic (tries face models, then falls back to yolov8n.pt)
            model_path = "yolov8n.pt"  # Ultralytics will download this automatically
            conf_threshold = 0.25  # Lower threshold for better multi-face detection in group photos
            yolo_strategy = YOLODetectionStrategy(
                model_path=model_path,
                conf_threshold=conf_threshold
            )
            _face_detector_yolo = FaceDetector(detection_strategy=yolo_strategy)
            logger.info(f"Face detector (YOLO primary) initialized with model={model_path}, conf={conf_threshold}")
        except ImportError as e:
            logger.warning(f"YOLO is not available: {e}")
            raise ImportError("YOLO is not available. Install it with: pip install ultralytics")
    return _face_detector_yolo


def get_face_recognition_service_mediapipe() -> FaceRecognitionService:
    """Get or create face recognition service instance with MediaPipe-based detector."""
    global _face_recognition_service_mediapipe
    if _face_recognition_service_mediapipe is None:
        _face_recognition_service_mediapipe = FaceRecognitionService(
            face_detector=get_face_detector_mediapipe(),
            embedding_extractor=get_embedding_extractor(),
            face_recognizer=get_face_recognizer(),
            quality_assessor=get_quality_assessor(),
            confidence_threshold=DEFAULT_CONFIDENCE_THRESHOLD
        )
        logger.info("Face recognition service (MediaPipe primary) initialized")
    return _face_recognition_service_mediapipe


def get_face_recognition_service_yolo() -> FaceRecognitionService:
    """Get or create face recognition service instance with YOLO-based detector."""
    global _face_recognition_service_yolo
    if _face_recognition_service_yolo is None:
        try:
            _face_recognition_service_yolo = FaceRecognitionService(
                face_detector=get_face_detector_yolo(),
                embedding_extractor=get_embedding_extractor(),
                face_recognizer=get_face_recognizer(),
                quality_assessor=get_quality_assessor(),
                confidence_threshold=DEFAULT_CONFIDENCE_THRESHOLD
            )
            logger.info("Face recognition service (YOLO primary) initialized")
        except ImportError as e:
            logger.error(f"Failed to initialize YOLO-based face recognition service: {e}")
            raise
    return _face_recognition_service_yolo


def get_face_recognition_service_class_attendance() -> FaceRecognitionService:
    """Get or create face recognition service instance for class attendance with lower thresholds."""
    global _face_recognition_service_class_attendance
    if _face_recognition_service_class_attendance is None:
        try:
            # Lower thresholds for class attendance to handle smaller/distant faces:
            # - Confidence threshold: 0.35 (instead of 0.45) for more lenient matching
            # - Quality threshold: 0.3 (instead of 0.5) to allow smaller faces
            _face_recognition_service_class_attendance = FaceRecognitionService(
                face_detector=get_face_detector_yolo(),
                embedding_extractor=get_embedding_extractor(),
                face_recognizer=get_face_recognizer(),
                quality_assessor=get_quality_assessor_class_attendance(),
                confidence_threshold=0.35,  # Lower threshold for class photos
                min_quality_threshold=0.3   # Lower quality threshold for distant faces
            )
            logger.info("Face recognition service for class attendance initialized (confidence=0.35, quality=0.3)")
        except ImportError as e:
            logger.error(f"Failed to initialize class attendance face recognition service: {e}")
            raise
    return _face_recognition_service_class_attendance


def get_liveness_service() -> LivenessService:
    """Get or create liveness service instance."""
    global _liveness_service
    if _liveness_service is None:
        _liveness_service = LivenessService(
            landmark_extractor=get_landmark_extractor(),
            liveness_verifier=get_liveness_verifier()
        )
        logger.info("Liveness service initialized")
    return _liveness_service


def get_attendance_service() -> AttendanceService:
    """Get or create attendance service instance."""
    global _attendance_service
    if _attendance_service is None:
        _attendance_service = AttendanceService(
            attendance_logger=get_attendance_logger(),
            attendance_validator=get_attendance_validator()
        )
        logger.info("Attendance service initialized")
    return _attendance_service


def get_metrics_calculator() -> MetricsCalculator:
    """Get or create metrics calculator instance."""
    global _metrics_calculator
    if _metrics_calculator is None:
        _metrics_calculator = MetricsCalculator()
        logger.info("Metrics calculator initialized")
    return _metrics_calculator


def get_timeline_analyzer() -> TimelineAnalyzer:
    """Get or create timeline analyzer instance."""
    global _timeline_analyzer
    if _timeline_analyzer is None:
        _timeline_analyzer = TimelineAnalyzer()
        logger.info("Timeline analyzer initialized")
    return _timeline_analyzer


def get_badge_definitions() -> BadgeDefinitions:
    """Get or create badge definitions instance."""
    global _badge_definitions
    if _badge_definitions is None:
        _badge_definitions = BadgeDefinitions.default()
        logger.info("Badge definitions initialized")
    return _badge_definitions


def get_badge_calculator() -> BadgeCalculator:
    """Get or create badge calculator instance."""
    global _badge_calculator
    if _badge_calculator is None:
        badge_definitions = get_badge_definitions()
        _badge_calculator = BadgeCalculator(badge_definitions)
        logger.info("Badge calculator initialized")
    return _badge_calculator


def get_streak_calculator() -> StreakCalculator:
    """Get or create streak calculator instance."""
    global _streak_calculator
    if _streak_calculator is None:
        _streak_calculator = StreakCalculator()
        logger.info("Streak calculator initialized")
    return _streak_calculator


def get_leaderboard_generator() -> LeaderboardGenerator:
    """Get or create leaderboard generator instance."""
    global _leaderboard_generator
    if _leaderboard_generator is None:
        _leaderboard_generator = LeaderboardGenerator()
        logger.info("Leaderboard generator initialized")
    return _leaderboard_generator


def get_recognize_face_use_case() -> RecognizeFaceUseCase:
    """Get or create recognize face use case instance."""
    global _recognize_face_use_case
    if _recognize_face_use_case is None:
        _recognize_face_use_case = RecognizeFaceUseCase(
            face_recognition_service=get_face_recognition_service(),
            attendance_repository=get_attendance_repository(),
            face_repository=get_face_repository(),
            user_repository=get_user_repository()
        )
        logger.info("Recognize face use case initialized")
    return _recognize_face_use_case


def get_mark_attendance_use_case() -> MarkAttendanceUseCase:
    """Get or create mark attendance use case instance."""
    global _mark_attendance_use_case
    if _mark_attendance_use_case is None:
        _mark_attendance_use_case = MarkAttendanceUseCase(
            liveness_service=get_liveness_service(),
            attendance_service=get_attendance_service(),
            attendance_repository=get_attendance_repository()
        )
        logger.info("Mark attendance use case initialized")
    return _mark_attendance_use_case


def get_get_analytics_use_case() -> GetAnalyticsUseCase:
    """Get or create get analytics use case instance."""
    global _get_analytics_use_case
    if _get_analytics_use_case is None:
        _get_analytics_use_case = GetAnalyticsUseCase(
            metrics_calculator=get_metrics_calculator(),
            timeline_analyzer=get_timeline_analyzer(),
            attendance_repository=get_attendance_repository()
        )
        logger.info("Get analytics use case initialized")
    return _get_analytics_use_case


def get_generate_leaderboard_use_case() -> GenerateLeaderboardUseCase:
    """Get or create generate leaderboard use case instance."""
    global _generate_leaderboard_use_case
    if _generate_leaderboard_use_case is None:
        _generate_leaderboard_use_case = GenerateLeaderboardUseCase(
            leaderboard_generator=get_leaderboard_generator(),
            metrics_calculator=get_metrics_calculator(),
            streak_calculator=get_streak_calculator(),
            badge_calculator=get_badge_calculator(),
            attendance_repository=get_attendance_repository(),
            user_repository=get_user_repository()
        )
        logger.info("Generate leaderboard use case initialized")
    return _generate_leaderboard_use_case


def get_get_all_users_use_case() -> GetAllUsersUseCase:
    """Get or create get all users use case instance."""
    global _get_all_users_use_case
    if _get_all_users_use_case is None:
        _get_all_users_use_case = GetAllUsersUseCase(
            user_repository=get_user_repository()
        )
        logger.info("Get all users use case initialized")
    return _get_all_users_use_case


def get_register_user_use_case() -> RegisterUserUseCase:
    """Get or create register user use case instance."""
    global _register_user_use_case
    if _register_user_use_case is None:
        from domain.services.recognition import UserRegistrationService
        user_registration_service = UserRegistrationService(
            face_detector=get_face_detector(),
            embedding_extractor=get_embedding_extractor(),
            quality_assessor=get_quality_assessor()
        )
        _register_user_use_case = RegisterUserUseCase(
            registration_service=user_registration_service,
            user_repository=get_user_repository(),
            face_repository=get_face_repository()
        )
        logger.info("Register user use case initialized")
    return _register_user_use_case


def get_get_user_info_use_case() -> GetUserInfoUseCase:
    """Get or create get user info use case instance."""
    global _get_user_info_use_case
    if _get_user_info_use_case is None:
        _get_user_info_use_case = GetUserInfoUseCase(
            user_repository=get_user_repository(),
            attendance_repository=get_attendance_repository(),
            metrics_calculator=get_metrics_calculator()
        )
        logger.info("Get user info use case initialized")
    return _get_user_info_use_case


def get_get_user_performance_use_case() -> GetUserPerformanceUseCase:
    """Get or create get user performance use case instance."""
    global _get_user_performance_use_case
    if _get_user_performance_use_case is None:
        _get_user_performance_use_case = GetUserPerformanceUseCase(
            metrics_calculator=get_metrics_calculator(),
            streak_calculator=get_streak_calculator(),
            attendance_repository=get_attendance_repository()
        )
        logger.info("Get user performance use case initialized")
    return _get_user_performance_use_case


def get_update_user_info_use_case() -> UpdateUserInfoUseCase:
    """Get or create update user info use case instance."""
    global _update_user_info_use_case
    if _update_user_info_use_case is None:
        _update_user_info_use_case = UpdateUserInfoUseCase(
            user_repository=get_user_repository()
        )
        logger.info("Update user info use case initialized")
    return _update_user_info_use_case


def get_get_attendance_records_use_case() -> GetAttendanceRecordsUseCase:
    """Get or create get attendance records use case instance."""
    global _get_attendance_records_use_case
    if _get_attendance_records_use_case is None:
        _get_attendance_records_use_case = GetAttendanceRecordsUseCase(
            attendance_repository=get_attendance_repository()
        )
        logger.info("Get attendance records use case initialized")
    return _get_attendance_records_use_case


def get_mark_class_attendance_use_case() -> MarkClassAttendanceUseCase:
    """Get or create mark class attendance use case instance."""
    global _mark_class_attendance_use_case
    if _mark_class_attendance_use_case is None:
        _mark_class_attendance_use_case = MarkClassAttendanceUseCase(
            face_recognition_service=get_face_recognition_service_class_attendance(),
            attendance_service=get_attendance_service(),
            attendance_repository=get_attendance_repository(),
            face_repository=get_face_repository(),
            user_repository=get_user_repository()
        )
        logger.info("Mark class attendance use case initialized with lower thresholds (confidence=0.35, quality=0.3)")
    return _mark_class_attendance_use_case

