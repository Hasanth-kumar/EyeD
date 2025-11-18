"""
Domain exceptions for EyeD AI Attendance System.

This module contains all domain-specific exceptions used across the system.
These exceptions represent business rule violations and domain errors.

All exceptions are domain-specific and have no infrastructure dependencies.
"""


class DomainException(Exception):
    """
    Base exception for all domain-related errors.
    
    This is the base class for all domain exceptions. It provides a common
    interface for handling domain errors throughout the system.
    """
    
    def __init__(self, message: str, error_code: str = None):
        """
        Initialize domain exception.
        
        Args:
            message: Human-readable error message.
            error_code: Optional error code for programmatic handling.
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class InvalidAttendanceRecordError(DomainException):
    """
    Exception raised when an attendance record is invalid.
    
    This exception is raised when an attendance record fails validation
    against business rules (e.g., missing required fields, invalid data).
    """
    
    def __init__(self, message: str = "Invalid attendance record", error_code: str = "INVALID_ATTENDANCE_RECORD"):
        super().__init__(message, error_code)


class InvalidConfidenceError(DomainException):
    """
    Exception raised when a confidence score is invalid.
    
    This exception is raised when a confidence score is outside the valid
    range (0.0 to 1.0) or below the required threshold.
    """
    
    def __init__(self, message: str = "Invalid confidence score", error_code: str = "INVALID_CONFIDENCE"):
        super().__init__(message, error_code)


class DailyLimitExceededError(DomainException):
    """
    Exception raised when the daily attendance entry limit is exceeded.
    
    This exception is raised when a user attempts to create more attendance
    entries than allowed per day.
    """
    
    def __init__(
        self,
        message: str = "Daily attendance entry limit exceeded",
        error_code: str = "DAILY_LIMIT_EXCEEDED",
        daily_entries: int = None,
        max_entries: int = None
    ):
        """
        Initialize daily limit exceeded error.
        
        Args:
            message: Human-readable error message.
            error_code: Error code for programmatic handling.
            daily_entries: Current number of entries for the day.
            max_entries: Maximum allowed entries per day.
        """
        if daily_entries is not None and max_entries is not None:
            message = f"Daily limit exceeded: {daily_entries}/{max_entries} entries"
        super().__init__(message, error_code)
        self.daily_entries = daily_entries
        self.max_entries = max_entries


class LivenessVerificationFailedError(DomainException):
    """
    Exception raised when liveness verification fails.
    
    This exception is raised when liveness detection fails to verify
    that a live person is present (e.g., spoofing detected, insufficient blinks).
    """
    
    def __init__(self, message: str = "Liveness verification failed", error_code: str = "LIVENESS_VERIFICATION_FAILED"):
        super().__init__(message, error_code)


class UserAlreadyExistsError(DomainException):
    """
    Exception raised when attempting to register a user that already exists.
    
    This exception is raised when a user_id is already registered in the system.
    """
    
    def __init__(self, message: str = "User already exists", error_code: str = "USER_ALREADY_EXISTS", user_id: str = None):
        """
        Initialize user already exists error.
        
        Args:
            message: Human-readable error message.
            error_code: Error code for programmatic handling.
            user_id: ID of the user that already exists.
        """
        if user_id:
            message = f"User with ID '{user_id}' already exists"
        super().__init__(message, error_code)
        self.user_id = user_id


class UserNotFoundError(DomainException):
    """
    Exception raised when a user is not found.
    
    This exception is raised when attempting to retrieve or update a user
    that does not exist in the system.
    """
    
    def __init__(self, message: str = "User not found", error_code: str = "USER_NOT_FOUND", user_id: str = None):
        """
        Initialize user not found error.
        
        Args:
            message: Human-readable error message.
            error_code: Error code for programmatic handling.
            user_id: ID of the user that was not found.
        """
        if user_id:
            message = f"User with ID '{user_id}' not found"
        super().__init__(message, error_code)
        self.user_id = user_id


class FaceDetectionFailedError(DomainException):
    """
    Exception raised when face detection fails.
    
    This exception is raised when no face is detected in the provided image.
    """
    
    def __init__(self, message: str = "Face detection failed - no face detected in image", error_code: str = "FACE_DETECTION_FAILED"):
        super().__init__(message, error_code)


class InsufficientQualityError(DomainException):
    """
    Exception raised when face quality is insufficient.
    
    This exception is raised when the face quality score is below the required threshold.
    """
    
    def __init__(
        self,
        message: str = "Face quality is insufficient",
        error_code: str = "INSUFFICIENT_QUALITY",
        quality_score: float = None,
        threshold: float = None
    ):
        """
        Initialize insufficient quality error.
        
        Args:
            message: Human-readable error message.
            error_code: Error code for programmatic handling.
            quality_score: Actual quality score achieved.
            threshold: Required quality threshold.
        """
        if quality_score is not None and threshold is not None:
            message = f"Face quality score {quality_score:.2f} is below threshold {threshold:.2f}"
        super().__init__(message, error_code)
        self.quality_score = quality_score
        self.threshold = threshold


class EmbeddingExtractionFailedError(DomainException):
    """
    Exception raised when face embedding extraction fails.
    
    This exception is raised when embedding extraction cannot be performed
    on the provided face image.
    """
    
    def __init__(self, message: str = "Face embedding extraction failed", error_code: str = "EMBEDDING_EXTRACTION_FAILED"):
        super().__init__(message, error_code)


class FaceNotRecognizedError(DomainException):
    """
    Exception raised when face recognition fails.
    
    This exception is raised when a face cannot be matched against known
    faces in the database (e.g., confidence below threshold, no match found).
    """
    
    def __init__(
        self,
        message: str = "Face not recognized",
        error_code: str = "FACE_NOT_RECOGNIZED",
        confidence: float = None,
        threshold: float = None
    ):
        """
        Initialize face not recognized error.
        
        Args:
            message: Human-readable error message.
            error_code: Error code for programmatic handling.
            confidence: Actual confidence score achieved.
            threshold: Required confidence threshold.
        """
        if confidence is not None and threshold is not None:
            message = f"Face recognition failed: confidence {confidence:.3f} is below threshold {threshold:.3f}"
        super().__init__(message, error_code)
        self.confidence = confidence
        self.threshold = threshold


